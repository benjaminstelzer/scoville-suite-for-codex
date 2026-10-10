#!/usr/bin/env python3
"""Build a complete single-unit assignment without transport receipts."""
from __future__ import annotations
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from native_task_arguments import add_creation_options, creation_arguments, workflow_title, validate_creation_options, single_line, assignment_path, publish_assignment, shell_command, budget_retry, file_read_instruction
from resolve_model_pair import resolve
from workflow_settings import ROUTES, load_config

MAX_NON_GOALS_BYTES = 8192
INTERNAL_COMMUNICATION = (
    "Use English for internal commentary, messages and results. Use minimal fields; "
    "keep quotes, relay text and literals exact."
)


def select_unit(selector: Path, root: Path, unit: str, max_output_bytes: int | None = None, retry_arguments: list[str] | None = None) -> dict:
    if not re.fullmatch(r"W-[0-9]{3}(?:/step-[1-9][0-9]*|/steps-[1-9][0-9]*-[1-9][0-9]*)?", unit):
        raise ValueError(f"--unit {unit!r} is invalid; use an existing Work Item, Step or consecutive range, e.g. W-001, W-001/step-2 or W-001/steps-1-3 (lowercase step or steps)")
    command = [sys.executable, "-B", str(selector), "--root", str(root),
               "--unit", unit, "--format", "json"]
    if max_output_bytes is not None:
        command.extend(["--max-output-bytes", str(max_output_bytes)])
    result = subprocess.run(command,
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise ValueError("Plan selection failed: " + result.stdout + result.stderr
                         + budget_retry(result.stdout, retry_arguments or command))
    data = json.loads(result.stdout)
    if not isinstance(data, dict) or set(data) != {"plan", "work_item", "direct_dependencies", "decisions"}:
        raise ValueError("Plan selector returned an unsupported projection")
    item = data.get("work_item")
    if not isinstance(item, dict) or item.get("unit") != unit:
        raise ValueError("Plan selector returned another unit")
    if not isinstance(item.get("source_text"), str) or not item["source_text"]:
        raise ValueError("SELECTOR_INCOMPATIBLE: Plan must provide source_text")
    return data


def result_contract(role: str) -> list[str]:
    statuses = ("pass, changes_requested, blocked, needs_user_decision"
                if role == "reviewer" else "completed, review_pending, blocked, needs_user_decision")
    return [
        "Return a minimal labelled result with an explicit status: " + statuses + ". No version marker, fixed field syntax, JSON or change flags are required.",
        ("For pass, return only the status; pass means the review ran and found no defects. Omit the executor recap, changed-file list, check history and repeated evidence. Otherwise report only open findings or the concrete blocker, decision or evidence limit preventing acceptance." if role == "reviewer" else
         "State completed effects, relevant changed paths, decisive checks and unverified behavior. Report facts, not a verdict that the work is correct or meets Acceptance. When work remains, name remaining scope, constraints, evidence limits and next action. Keep only facts needed to assess or continue correctly."),
        *(["Use completed when your assigned execution unit and checks are finished, even if manager review or Plan closure remains. Use review_pending at a checked boundary only when a binding review cadence, a separate dependent product change or a named costly or consequential gate requires review before the unit is finished; state its review trigger."] if role == "executor" else []),
        "Findings name the actual unresolved defect, location, effect and smallest correction. A reviewer pass has no unresolved defects. Optional ideas do not block pass and are not correction assignments; omit them unless they inform a relevant decision. Do not count characters or include a work log.",
    ]


def build_explorer_prompt(workspace: Path, manager: str, context: dict, role_input: dict) -> str:
    """Read-only inquiry; no execution or review assignment is required."""
    single_line(manager, '--manager-agent-id')
    if set(role_input) != {"supplemental_context"} or not role_input["supplemental_context"].strip():
        raise ValueError('exploration requires --supplemental-context with the complete question or change request and necessary constraints; no executor or reviewer result flags')
    skill = Path(__file__).resolve().parents[1]
    checker = skill / 'scripts/check_text_size.py'
    shell = skill / 'references/shell-commands.md'
    if not checker.is_file() or not shell.is_file():
        raise ValueError('use the intact matching Workflow package before exploration')
    writing = (skill / 'references/writing.md').read_text(encoding='utf-8')
    suite = skill.parent.parent if skill.parent.name == skill.name else skill.parent
    lines = [
        'scoville_role=explorer', f'workspace_root={workspace}', f'manager_agent_id={manager}',
        f'python: {sys.executable}', f'text_size_checker: {checker}', f'shell_command_rules: {shell}',
        'Read the named shell rules before shell calls, complete-file preparation or output that may exceed an applicable limit. Use the named interpreter and checker for bounded reads and complete-file delivery.',
        f'suite_directory: {suite}',
        'Choose appropriate Skills yourself. Resolve selected suite Skills from suite_directory in this matching build, preserving explicit user invocations and overrides. Skill selection grants no extra permissions.',
        'Do not activate Workflow or Handoff or assume manager permissions. Use Plan only read-only; necessary source inspection remains allowed. Mark file facts affected by possible executor writes as provisional.',
        'Investigate only the supplied question, change request or planning preparation. Read necessary sources; do not implement, change project files, run tests, edit Plan records, change settings or create agents. Planning preparation returns proposals, scope and open questions; the manager writes the Plan. A change request authorizes investigation only.',
        'Only necessary oversized-result preparation and publication under .scoville/temp is permitted by the shared delivery rules. No source captures or unrelated external access.',
        INTERNAL_COMMUNICATION,
        'Return completed with the answer or recommendation, decisive source locations, material limits and any necessary decision; otherwise blocked or needs_user_decision with the exact missing prerequisite or question. Do not claim review acceptance. The manager owns user answers, Plan changes and implementation dispatch.',
        'On stop, end investigation and return retained facts. After compaction, continue the same inquiry. Return the complete result only in your native final answer; do not also send it with send_message. Then stay inactive.',
        'The complete matching writing rules below satisfy selected suite Skills\' writing read. Read another copy only for an explicit reload, changed rules or a different required build.',
        writing,
        '\n## Question and constraints\n' + role_input['supplemental_context'],
    ]
    if context:
        exclusions = context['plan'].get('non_goals')
        if not isinstance(exclusions, str) or not exclusions.strip():
            raise ValueError('SELECTOR_INCOMPATIBLE: Plan must provide non-empty plan.non_goals')
        if len(exclusions.encode('utf-8', errors='strict')) > MAX_NON_GOALS_BYTES:
            raise ValueError('NON_GOALS_TOO_LARGE: shorten redundancy while preserving every exclusion before exploration')
        lines.extend(['\n' + context['plan']['non_goals'],
                      '\n## Work Item context\n' + context['work_item']['context_text']])
    return '\n'.join(lines) + '\n'


def build_prompt(role: str, workspace: Path, coordinator: str, reference: str,
                 context: dict, role_input: dict) -> str:
    if role == 'explorer':
        return build_explorer_prompt(workspace, coordinator, context, role_input)
    single_line(coordinator, '--manager-agent-id')
    allowed = {"supplemental_context"}
    if role == "reviewer":
        allowed.add("executor_result")
        result = role_input.get("executor_result")
        if not isinstance(result, str) or not result.strip():
            raise ValueError("review requires the complete executor result; supply --executor-result")
        if not role_input.get("supplemental_context", "").strip():
            raise ValueError("review requires --supplemental-context with review boundary and affected Acceptance")
    else:
        allowed.add("reviewer_result")
    if set(role_input) - allowed:
        raise ValueError("unknown role input")
    item = context.get("work_item", {})
    if not isinstance(item.get("source_text"), str) or not item["source_text"].strip():
        raise ValueError("selected unit must contain source_text")
    if not isinstance(item.get("context_text"), str) or not item["context_text"].strip():
        raise ValueError("selected unit must include its complete Work Item as context_text")
    exclusions = context.get('plan', {}).get('non_goals')
    if not isinstance(exclusions, str) or not exclusions.strip():
        raise ValueError('SELECTOR_INCOMPATIBLE: Plan must provide non-empty plan.non_goals; use matching Plan and Workflow packages')
    exclusion_bytes = len(exclusions.encode('utf-8', errors='strict'))
    if exclusion_bytes > MAX_NON_GOALS_BYTES:
        raise ValueError(f'NON_GOALS_TOO_LARGE: plan.non_goals requires {exclusion_bytes} UTF-8 bytes; '
                         f'limit {MAX_NON_GOALS_BYTES}; have the manager shorten redundant wording while preserving every exclusion before dispatch')
    skill_root = Path(__file__).resolve().parents[1]
    checker = skill_root / 'scripts' / 'check_text_size.py'
    if not checker.is_file():
        raise ValueError(f'bundled text-size checker is missing at {checker}; use the intact matching Workflow package before dispatch')
    writing_path = skill_root / 'references' / 'writing.md'
    try:
        writing = writing_path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        raise ValueError(f'cannot read packaged writing rules at {writing_path}: {error}; use the intact matching suite package before dispatch') from error
    shell_rules = skill_root / 'references' / 'shell-commands.md'
    if not shell_rules.is_file():
        raise ValueError(f'packaged shell rules missing at {shell_rules}; use the intact matching suite package before dispatch')
    wrapped = skill_root.parent.name == skill_root.name
    suite_root = skill_root.parent.parent if wrapped else skill_root.parent
    lines = [f"scoville_role={role}", "dispatch_contract=SCOVILLE_AGENT_DISPATCH_V1",
             f"workspace_root={workspace}", f"manager_agent_id={coordinator}",
             f"text_size_checker: {checker}", f"python: {sys.executable}",
             f"shell_command_rules: {shell_rules}; read before shell commands, complete-file preparation or output that may exceed an applicable limit.",

             ("This assignment is your review contract. Do not load Plan, Workflow or Handoff Skills, selectors, unrelated Plan points, Decision records or predecessor conversations, except the matching Plan Skill's read-only route and applicable field rules for an assigned native Plan- or Decision-field review. You may read only Plan/Decision source paths and sections explicitly named in supplemental_context as review evidence. This grants no maintenance, tests or free context search." if role == "reviewer" else
              "This assignment is your execution contract. Do not load Plan, Workflow or Handoff Skills, selectors, other Plan points, Decision records or predecessor conversations. Load implementation Skills only for the remaining work, not for completed Steps."),
             f"suite_directory: {suite_root}",
             "Choose Skills appropriate to the assigned work yourself. Explicit user Skill invocations supplied in supplemental_context remain binding. Resolve selected suite Skills from suite_directory in this matching build, preserving any explicit user override. A missing needed Skill or reference blocks its dependent work; an unselected Skill does not block dispatch. Skill selection grants no additional role permissions.",
             "Work only in the named workspace on this assigned unit. The manager owns Plan, Decision and index edits, staging and commits. Do not create chats or agents, change Workflow or model settings, or dispatch other work. Product and test configuration may change only within the assigned scope and project constraints; reviewers must not change project files or execute tests, apart from the necessary delivery exception in this role contract.",
             "1. When work needs a user decision or cannot continue, stop dependent writes and promptly send needs_user_decision or blocked to your actual manager with send_message. Include the assigned point, exact question or diagnostic, why it prevents progress, and what is waiting. Do this during the assignment, without waiting for all unrelated checks or your final result. Do not call user-question tools or wait silently for user input in this child. \n2. Once running operations are quiescent, return the complete paused result with the same limitation. The visible manager asks the user directly and returns the actual answer. A repeated message and native result describe one pending issue, not two requests.\n",
             "Perform only the assigned scope. The Work Item is context for the named assigned range. Supplemental context identifies any retained effects and necessary remaining work after a confirmed child failure. The recorded and released Step or group within that range is the current execution unit; later unreleased Steps add no work to it. Preserve authored order. Reviewers assess the same assigned scope, not unfinished work outside it. Use supplied supplemental_context only for a necessary constraint or missing fact; Executors request material missing facts instead of expanding scope; reviewers include missing facts and their effect on the verdict in their one complete result. Follow applicable repository instructions and implementation Skills.",
             "Work autonomously. " + INTERNAL_COMMUNICATION,
              "For bounded UTF-8 reads, command capture, size checks and oversized-result delivery, invoke the named Python interpreter and text-size checker even when they are outside the workspace. This exception permits no unrelated external inspection, commands or project writes; delivery follows this role contract and the shared complete-file procedure.",
             "Program: the named check_text_size.py. Document: only its --file value. Copy the entire reader command; change only --part for continuation. Start only named .py files as Python program files; never start a Skill, reference or assignment as a program.",
             "The named python and text_size_checker replace <verified-python> and <skill-directory>/scripts/check_text_size.py in the shared writing and shell rules.",
             "The complete matching writing rules below satisfy selected suite Skills' writing read. Read another copy only for an explicit reload, changed rules or a different required build.",
             "For necessary oversized-result delivery only, you may prepare and publish complete temporary artifacts under the project's .scoville/temp. Reviewers may not run tests or change the reviewed subject. This exception grants no other writes and preserves host restrictions, write ownership.",
             writing,
             *([] if role == "reviewer" else ["Execute only the selected Step or jointly started group recorded and released by the manager, within the assigned range. Later unreleased Steps are not remaining work for this execution unit. After its implementation and required checks finish, return completed. Stop writing and do not advance to or resume later unreleased Steps. Do not edit the Plan. Preserve completed effects.\n"]),
             ("Stay read-only for project files and do not execute tests. This role permits only necessary oversized-result preparation and publication under .scoville/temp. Follow the shared complete-file procedure. Independently review the unreviewed diff identified in supplemental_context against the assigned Steps, affected Acceptance, applicable Goals, Non-goals and constraints, including relevant interactions. Treat executor_result as the executor's report, not an approval: use its reported check results as reported evidence, judge whether they cover the claim, and verify its other relevant claims against the scoped diff. Reuse supplied earlier assessments only where reviewed content, applicable requirements and supporting conditions are unchanged since that assessment; do not review those parts again. Report a missing review boundary instead of assuming a whole-tree review." if role == "reviewer" else
              "Implement only the assigned work and its proportionate checks. Preserve unrelated changes. Follow repository instructions, including required backups. Finish the coherent change, including dependent edits and focused checks. Follow any binding user or project review cadence. Otherwise pause at a checked boundary only before a separate product change depends on unreviewed changes or a named costly or consequential gate requires acceptance first. Return review_pending under the result contract below. Previously checked code alone does not trigger a pause. A failed focused check is unfinished work. This pauses the same assignment for independent review. Resume only after the manager confirms review acceptance through followup_task on your exact ID. Later unreleased Steps do not require this review pause. If no work remains in the unit, return completed for the manager's due review. Correct intermediate errors in code you are implementing in this assignment before returning the result."),
             "When reviewer_result is supplied, correct the assigned source defects and verify them. Do not implement optional ideas without explicit authorization. Reviewers give one complete assessment without a question round.",
             "After compaction, recover this assignment and compare the actual files and retained checks with completed effects before continuing. Do not repeat completed work or treat compaction as a task handoff.",
             "Treat a user stop as immediate: make no further change, return the exact retained state and stop.",
             "1. After all work and checks stop, return the complete role result in your final answer, or the shared complete-file metadata if necessary content cannot fit. The file must contain the complete unchanged role result under the contract below. The manager must verify SHA-256 and read the entire file before applying that contract. \n2. Native agent completion delivers it to the spawning manager with your agent identity. Do not also send a duplicate result. \n3. Then stay write-inactive. The manager may use followup_task for a necessary executor question or to continue unfinished work within the current execution unit after a user decision or review acceptance; later groups, new corrections and completed assignments use new agents. No self-archival or close tool is required.\n",
             *result_contract(role),
             "\n## Assigned unit\n" + item["unit"],
             "\n" + exclusions,
             "\n## Work Item context\n" + item["context_text"].rstrip(),
             *["\n## " + key + "\n" + value for key, value in role_input.items()]]
    if item.get("step_statuses"):
        progress = "\n".join(f"Step {entry['number']}: {entry['status'] or 'unknown (unmarked)'}"
                             for entry in item["step_statuses"])
        lines.extend([
            "\n## Assigned Step progress\n" + progress,
            "Written status is progress, not permission or acceptance. For ordinary implementation, preserve done or cancelled effects and perform only remaining assigned work. Unmarked status is unknown: use supplied Evidence, Instructions, supplied context and actual scoped results to establish remaining work, never assume todo. An explicitly assigned review or correction still covers its named done Steps; preserve unaffected completed effects. Never revive cancelled scope without authorization.",
        ])
    return "\n".join(lines) + "\n"


def resolve_creation_pair(args: argparse.Namespace) -> None:
    """Resolve fresh routes; retained pairs never read changed configuration."""
    if args.format != 'create':
        if args.route:
            raise ValueError('--route requires --format create; omit it for prompt-only output')
        return
    retained = args.reviewer_result
    if retained and (args.model is None or args.thinking is None):
        raise ValueError('correction requires both --model and --thinking: retain the launched pair or supply an explicitly justified replacement for remaining work; --route cannot replace it')
    if args.model is not None and args.thinking is not None:
        return
    if not args.route:
        raise ValueError('--format create requires --route CLASS or both --model and --thinking; e.g. --route medium (optional --model or --thinking override)')
    config = load_config(Path(__file__).resolve().parents[1] / 'assets' / 'workflow.toml', args.workspace_root)
    pair = resolve(config, args.role, args.route, args.model, args.thinking)
    args.model, args.thinking = pair['model'], pair['thinking']


def main() -> int:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    # Preserve literal selector newlines in prompt-only output, including CRLF.
    sys.stdout.reconfigure(newline='')
    parser = argparse.ArgumentParser(description=__doc__)
    add_creation_options(parser)
    parser.add_argument('--route', choices=ROUTES, help='resolve the role pair internally; --model and --thinking override its fields')
    parser.add_argument('--worker-number', type=int, help='executor number, also for its reviewer')
    parser.add_argument("--selector", type=Path, default=Path(__file__).with_name("select_context.py"))
    parser.add_argument("--max-output-bytes", type=int,
                        help="explicit UTF-8 budget for the complete Plan selector result; omit for its default")
    parser.add_argument("--plan-root", type=Path)
    parser.add_argument("--unit", help='required for executor/reviewer; optional Plan context for explorer')
    parser.add_argument("--role", choices=("executor", "reviewer", "explorer"), required=True)
    parser.add_argument("--project-root", "--workspace-root", dest="workspace_root", type=Path, required=True)
    parser.add_argument("--manager-agent-id", required=True, help="actual spawning manager agent ID; never infer it from CODEX_THREAD_ID")
    parser.add_argument("--assignment-file", type=Path, help="optional new absolute UTF-8 assignment file for --format create; defaults to an external system temporary path, for every fresh assignment")
    for name in ("executor-result", "reviewer-result", "supplemental-context"):
        parser.add_argument("--" + name, type=Path, help="UTF-8 plain-text file")
    args = parser.parse_args()
    try:
        if args.role != 'explorer' and not args.unit:
            raise ValueError('--unit is required for executor and reviewer')
        resolve_creation_pair(args)
        validate_creation_options(args)
        if args.format == 'create' and (args.worker_number is None or args.worker_number < 1):
            raise ValueError('--worker-number must be a positive integer; for review use the reviewed executor number')
        if not args.workspace_root.is_absolute() or not args.workspace_root.is_dir():
            raise ValueError(f"--project-root/--workspace-root {str(args.workspace_root)!r} must be an existing absolute project directory; supply the actual checkout path")
        single_line(args.manager_agent_id, '--manager-agent-id')
        if args.assignment_file and args.format != 'create':
            raise ValueError('--assignment-file requires --format create; omit it for direct prompt output')
        if args.format == 'create':
            args.assignment_file = assignment_path(args.assignment_file, args.workspace_root)
        role_input = {}
        input_contents = {
            "executor_result": "the complete retained native executor result",
            "reviewer_result": "the complete retained native reviewer result",
            "supplemental_context": "the applicable scope, acceptance criteria and constraints",
        }
        for key, expected in input_contents.items():
            path = getattr(args, key)
            if path:
                try:
                    role_input[key] = path.read_text(encoding="utf-8")
                except (OSError, UnicodeError) as error:
                    flag = "--" + key.replace("_", "-")
                    raise ValueError(
                        f'Invalid argument {flag} "{path}": expected an existing readable UTF-8 file '
                        f"containing {expected}. Prepare and verify the retained content with a literal-safe "
                        f"file-write tool, or correct the path, then rerun with {flag} \"<existing-input-file>\". "
                        f"Do not change access controls or invent missing content. Original error: {error}"
                    ) from error
        context = (select_unit(args.selector, args.plan_root or args.workspace_root, args.unit, args.max_output_bytes,
                               [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]) if args.unit else {})
        prompt = build_prompt(args.role, args.workspace_root, args.manager_agent_id,
                              "", context, role_input)
        if args.format == 'create':
            title_unit = args.unit
            # A whole item with Steps must display its complete assigned range.
            if title_unit and '/' not in title_unit:
                steps = re.findall(r'^([1-9][0-9]*)\. ', context['work_item']['context_text'], re.M)
                if steps:
                    title_unit += f'/steps-{steps[0]}-{steps[-1]}' if len(steps) > 1 else f'/step-{steps[0]}'
            identity = 'question'
            if context:
                plan_ids = re.findall(r'^id: (PLAN-[0-9]{4})\r?$', context['plan']['frontmatter'], re.M)
                if len(plan_ids) != 1:
                    raise ValueError('Plan selector must supply one canonical id in plan.frontmatter; use matching Plan and Workflow packages')
                identity = plan_ids[0] + '/' + title_unit
            title = workflow_title(args.project_name, args.role, args.worker_number, identity)
            task_name = f'scoville_{args.role}_{args.worker_number}'
            assignment = prompt + '\nAssignment: ' + title + '\n'
            message = assignment
            if args.assignment_file:
                checker = Path(__file__).with_name('check_text_size.py')
                read_check = file_read_instruction(args.assignment_file, checker, sys.executable)
                read_only = (' No tests or project-file changes. Only prepare and publish necessary '
                             'oversized results under .scoville/temp using shared complete-file rules.'
                             if args.role in {'reviewer', 'explorer'} else '')
                read_gate = 'before any project work. '
                message = (f'You are the assigned {args.role} (manager_agent_id={args.manager_agent_id}).{read_only} '
                           f'{INTERNAL_COMMUNICATION} Read the complete UTF-8 assignment '
                           f'from {args.assignment_file} {read_gate}'
                           f'{read_check}'
                           'Follow the assignment and '
                           'bundled Skill paths; return its required result.\n'
                           f'Assignment: {title}\n')
            output = creation_arguments(message, task_name, args.model, args.thinking)
            payload = json.dumps(output, ensure_ascii=False) + '\n'
            payload.encode('utf-8', errors='strict')
            if args.assignment_file:
                publish_assignment(args.assignment_file, assignment)
            sys.stdout.write(payload)
        else:
            sys.stdout.write(prompt)
        return 0
    except (OSError, ValueError, TypeError, AttributeError) as error:
        parser.print_usage(file=sys.stderr)
        print("ERROR: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
