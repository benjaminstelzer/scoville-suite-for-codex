#!/usr/bin/env python3
"""Build a complete single-unit assignment without transport receipts."""
from __future__ import annotations
import argparse
import json
import hashlib
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from native_task_arguments import add_creation_options, creation_arguments, workflow_title, validate_creation_options, takeover_instruction, single_line, assignment_path, publish_assignment, shell_command, budget_retry, file_read_instruction
from resolve_model_pair import resolve
from workflow_settings import ROUTES, load_config

MAX_NON_GOALS_BYTES = 8192


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
    statuses = ("pass, changes_requested, blocked, needs_user_decision, context_handoff"
                if role == "reviewer" else "completed, review_pending, blocked, needs_user_decision, context_handoff, progress_pending")
    return [
        "Return a concise normal message with an explicit status: " + statuses + ". No version marker, fixed field syntax, JSON or change flags are required.",
        ("For pass, say only that the review was performed and found no defects; omit the worker recap, changed-file list, check history and repeated evidence. Otherwise report only open findings or the concrete blocker, decision or evidence limit preventing acceptance. For an authorized context_handoff, include only facts needed to continue the unfinished review." if role == "reviewer" else
         "State completed effects, relevant changed paths, decisive checks and unverified behavior. Report facts, not a verdict that the work is correct or meets Acceptance. For an authorized context_handoff, add unfinished work, needed constraints and the next action. Keep only facts needed to assess or continue correctly."),
        *(["Use completed when your assigned implementation and checks are finished, even if manager review or Plan closure remains. Use review_pending only after a checked prior-code fix with specific work still assigned to you after review; name that remaining work."] if role == "executor" else []),
        "Findings name the actual unresolved defect, location, effect and smallest correction. A reviewer pass has no unresolved defects. Optional ideas do not block pass and are not correction assignments; omit them unless they inform a relevant decision. Do not count characters or include a work log.",
    ]


def checkpoint_command(checkpoint: Path, role: str, workspace: Path) -> str:
    arguments = [sys.executable, str(checkpoint), '--role', role, '--project-root', str(workspace)]
    return shell_command(arguments)


def build_prompt(role: str, workspace: Path, coordinator: str, reference: str,
                 context: dict, role_input: dict) -> str:
    single_line(coordinator, '--manager-agent-id')
    allowed = {"context_handoff", "supplemental_context", "predecessor_agent_id"}
    continuation = "context_handoff" in role_input
    if continuation and not role_input["context_handoff"].strip():
        raise ValueError("--context-handoff must describe the unfinished work and completed effects")
    if continuation and not role_input.get("supplemental_context", "").strip():
        raise ValueError("continuation requires --supplemental-context with applicable acceptance criteria, constraints, evidence and required paths")
    if role == "reviewer":
        allowed.add("executor_result")
        result = role_input.get("executor_result")
        if not continuation and (not isinstance(result, str) or not result.strip()):
            raise ValueError("review requires the original worker result; supply it with --executor-result")
        if not continuation and not role_input.get("supplemental_context", "").strip():
            raise ValueError("fresh review requires --supplemental-context <review-facts.txt> with the review boundary, affected Acceptance and applicable earlier assessments")
    if role == "executor":
        allowed.update({"reviewer_result"})
    if set(role_input) - allowed:
        raise ValueError("unknown role input")
    if role_input.get("context_handoff") and not role_input.get("predecessor_agent_id", "").strip():
        raise ValueError("continuation requires --predecessor-agent-id so the successor can confirm receipt directly")
    if role_input.get("predecessor_agent_id"):
        single_line(role_input["predecessor_agent_id"], '--predecessor-agent-id')
        if not continuation:
            raise ValueError('--predecessor-agent-id requires --context-handoff and --supplemental-context')
        if role_input["predecessor_agent_id"] == coordinator:
            raise ValueError('--predecessor-agent-id must identify the prior child, not --manager-agent-id')
    item = context.get("work_item", {})
    if not isinstance(item.get("source_text"), str) or not item["source_text"].strip():
        raise ValueError("selected unit must contain source_text")
    if not continuation and (not isinstance(item.get("context_text"), str) or not item["context_text"].strip()):
        raise ValueError("selected unit must include its complete Work Item as context_text")
    exclusions = context.get('plan', {}).get('non_goals')
    if not isinstance(exclusions, str) or not exclusions.strip():
        raise ValueError('SELECTOR_INCOMPATIBLE: Plan must provide non-empty plan.non_goals; use matching Plan and Workflow packages')
    exclusion_bytes = len(exclusions.encode('utf-8', errors='strict'))
    if exclusion_bytes > MAX_NON_GOALS_BYTES:
        raise ValueError(f'NON_GOALS_TOO_LARGE: plan.non_goals requires {exclusion_bytes} UTF-8 bytes; '
                         f'limit {MAX_NON_GOALS_BYTES}; have the manager shorten redundant wording while preserving every exclusion before dispatch')
    checkpoint = Path(__file__).with_name("check_context_checkpoint.py")
    skill_root = Path(__file__).resolve().parents[1]
    checker = skill_root / 'scripts' / 'check_text_size.py'
    if not checker.is_file():
        raise ValueError(f'bundled text-size checker is missing at {checker}; use the intact matching Workflow package before dispatch')
    writing_path = skill_root / 'references' / 'writing.md'
    try:
        writing = writing_path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        raise ValueError(f'cannot read packaged writing rules at {writing_path}: {error}; use the intact matching suite package before dispatch') from error
    wrapped = skill_root.parent.name == skill_root.name
    suite_root = skill_root.parent.parent if wrapped else skill_root.parent
    code_root = suite_root / "scoville-code"
    code_skill = (code_root / "scoville-code" if wrapped else code_root) / "SKILL.md"
    if not code_skill.is_file():
        raise ValueError(f"bundled Scoville Code is missing at {code_skill}; use the complete matching suite package layout before dispatch")
    lines = [f"scoville_role={role}", "dispatch_contract=SCOVILLE_AGENT_DISPATCH_V1",
             f"workspace_root={workspace}", f"manager_agent_id={coordinator}",
             f"text_size_checker: {checker}", f"python: {sys.executable}",

             "This assignment is your execution contract. Do not load Plan, Workflow or Handoff Skills, selectors, other Plan points, Decision records or predecessor conversations. Load implementation Skills only for the remaining work, not for completed Steps.",
             f"For implementation and review, use Scoville Code at {code_skill} when applicable. Resolve other suite Skills from that same suite directory, preserving any explicit user override. A missing bundled Skill is a blocker, not permission to load a different installed build.",
             "Work only in the named workspace on this assigned unit. The manager owns Plan, Decision and index edits, staging, commits and the run report. Do not write the report or message the runner. Do not create chats or agents, change Workflow or model settings, or dispatch other work. Product and test configuration may change only within the assigned scope and project constraints; reviewers must not change project files or execute tests, apart from the shared writing rules' oversized-result artifact exception.",
             "When work needs a user decision or cannot continue, stop dependent writes and promptly send needs_user_decision or blocked to your actual manager with send_message. Include the assigned point, exact question or diagnostic, why it prevents progress, and what is waiting. Do this during the assignment, without waiting for all unrelated checks or your final result. Do not call user-question tools or wait silently for user input in this child. Once running operations are quiescent, return the complete paused result with the same limitation. Only the manager relays the question to the visible runner and returns the actual user answer. A repeated message and native result describe one pending issue, not two requests.",
             "Perform only the assigned scope. For a continuation, context_handoff defines the remaining work and supplemental_context supplies its applicable acceptance criteria and constraints. Otherwise the Work Item is context for the named Step, consecutive Step range, or whole item. Preserve authored order. Reviewers assess the same assigned scope, not unfinished work outside it. Use supplied supplemental_context only for a necessary constraint or missing fact; Workers request material missing facts instead of expanding scope; reviewers include missing facts and their effect on the verdict in their one complete result. Follow applicable repository instructions and implementation Skills.",
             "Work autonomously. Omit routine progress narration and tool announcements. If the host requires an update, use one short sentence about a material change or blocker.",
             "For size checks before reading potentially large text and for oversized-result delivery, invoke the named Python interpreter and text-size checker even when they are outside the workspace. This exception permits no unrelated external inspection or project writes; delivery artifacts remain governed by the shared writing rules.",
             writing,
             *([] if role == "reviewer" else ["Execute only the Step or jointly started group whose start the manager has recorded and released. Before advancing to another Step or Step group in this same assignment, stop all writes and return progress_pending with observed completed Steps, checks, remaining scope and the proposed next Step or Step group. This ends the turn, not the assignment; do not roll over or edit the Plan. Resume only through followup_task on your exact ID after the manager records and validates progress and releases the next Step or Step group, including any due review acceptance. Preserve completed effects and any measured crossing. A required prior-code review pause uses review_pending instead."]),
             ("Stay read-only for project files and do not execute tests. The shared writing rules permit only necessary oversized-result preparation and publication under .scoville/temp. Independently review the unreviewed diff identified in supplemental_context against the assigned Steps, affected Acceptance, applicable Goals, Non-goals and constraints, including relevant interactions. Treat executor_result as the worker's report, not an approval: use its reported check results as reported evidence, judge whether they cover the claim, and verify its other relevant claims against the scoped diff. Reuse supplied earlier assessments only where reviewed content, applicable requirements and supporting conditions are unchanged since that assessment; do not review those parts again. Report a missing review boundary instead of assuming a whole-tree review." if role == "reviewer" else
              "Implement only the assigned work and its proportionate checks. Preserve unrelated changes. Follow repository instructions, including required backups. After fixing product code that was complete or checked before this assignment, run focused checks. If assigned work remains, stop writing and return review_pending with the checked fix, remaining work and any retained threshold measurement, before further tests or work, including after rollover_pending. This pauses the same assignment for independent review; it does not complete or transfer it. Resume its remaining scope only after the manager confirms review acceptance through followup_task on your exact ID. Preserve completed effects and the retained crossing; finish the full assigned Step or Step group. If no assigned work remains, return completed for the manager's due review. Correct intermediate errors in code you are implementing in this assignment and continue normally."),
             "When reviewer_result is supplied, correct the assigned source defects and verify them. Do not implement optional ideas without explicit authorization. Reviewers give one complete assessment without a question round.",
             "After a bounded implementation-and-check, review, or UI-check batch, checkpoint only if assigned work, a correction or a required check remains. A threshold crossing only schedules rollover: rollover_pending does not stop or shorten your assignment. Retain the measured crossing across compaction and finish the complete assigned Step or Step group, review or repair, including required corrections and checks. After your last required check, return completed for executor or pass or changes_requested for reviewer without another checkpoint, even above the threshold. Include the retained measurement when needed for rollover evidence. The manager's later review and Plan closure are not your unfinished work. Failed checks also end a batch. Finish any running operation first. While work remains, checkpoint before commands expected to add substantial context unless just checked with no material context growth since. Save large output to a file with the exit status; read failures and a summary first, then relevant details as needed. Before displaying potentially large text, apply the shared size-check rule to the complete output or each ordered portion. Never rely on truncation followed by rereading omitted text, and never claim a truncated read is complete.",
             checkpoint_command(checkpoint, role, workspace),
             "Do not return context_handoff with unfinished assigned work merely because a threshold was crossed. It requires an explicitly authorized recovery transfer and a quiescent boundary with no active writer. Each later assignment already uses a fresh child. The manager retains the handoff and confirms quiescence before creating a successor.",
             "On unavailable telemetry, continue without inventing occupancy or claiming rollover. Invalid configuration or a failed helper stops the affected operation and returns blocked with the diagnostic.",
             "After compaction, recover this assignment and compare the actual files and retained checks with completed effects before continuing. Do not repeat completed work or treat compaction as a task handoff.",
             "Treat a user stop as immediate: make no further change, return the exact retained state and stop.",
             "After all work and checks stop, return the complete role result in your final answer, or the shared complete-file metadata if necessary content cannot fit. The file must contain the complete unchanged role result under the contract below. The manager must verify SHA-256 and read the entire file before applying that contract. Native agent completion delivers it to the spawning manager with your agent identity. Do not also send a duplicate result or message the runner. Then stay write-inactive. The manager may use followup_task for a necessary worker question or to continue this same unfinished assignment after a validated progress boundary, user decision or review acceptance; a new correction or completed assignment uses a new agent. No self-archival or close tool is required.",
             *result_contract(role),
             "\n## Assigned unit\n" + item["unit"],
             "\n" + exclusions,
             *([] if continuation else ["\n## Work Item context\n" + item["context_text"].rstrip()]),
             *["\n## " + key + "\n" + value for key, value in role_input.items()]]
    if item.get("step_statuses"):
        progress = "\n".join(f"Step {entry['number']}: {entry['status'] or 'unknown (unmarked)'}"
                             for entry in item["step_statuses"])
        lines.extend([
            "\n## Assigned Step progress\n" + progress,
            "Written status is progress, not permission or acceptance. For ordinary implementation, preserve done or cancelled effects and perform only remaining assigned work. Unmarked status is unknown: use supplied Evidence, Instructions, legacy continuation context and actual scoped results to establish remaining work, never assume todo. An explicitly assigned review or correction still covers its named done Steps; preserve unaffected completed effects. A continuation follows its handoff's remaining scope. Never revive cancelled scope without authorization.",
        ])
    first_action = takeover_instruction(role_input['predecessor_agent_id'], coordinator) if continuation else ''
    return first_action + "\n".join(lines) + "\n"


def resolve_creation_pair(args: argparse.Namespace) -> None:
    """Resolve fresh routes; retained pairs never read changed configuration."""
    if args.format != 'create':
        if args.route:
            raise ValueError('--route requires --format create; omit it for prompt-only output')
        return
    retained = args.context_handoff or args.reviewer_result
    if retained and (args.model is None or args.thinking is None):
        raise ValueError('recovery and correction require both --model and --thinking from the original launched pair; --route cannot replace it')
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
    parser.add_argument('--worker-number', type=int, help='worker number, also for its reviewer')
    parser.add_argument("--selector", type=Path, default=Path(__file__).with_name("select_context.py"))
    parser.add_argument("--max-output-bytes", type=int,
                        help="explicit UTF-8 budget for the complete Plan selector result; omit for its default")
    parser.add_argument("--plan-root", type=Path)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--role", choices=("executor", "reviewer"), required=True)
    parser.add_argument("--project-root", "--workspace-root", dest="workspace_root", type=Path, required=True)
    parser.add_argument("--manager-agent-id", required=True, help="actual spawning manager agent ID; never infer it from CODEX_THREAD_ID")
    parser.add_argument("--predecessor-agent-id")
    parser.add_argument("--assignment-file", type=Path, help="optional new absolute UTF-8 assignment file for --format create; defaults to an external system temporary path, including recovery")
    for name in ("executor-result", "reviewer-result", "context-handoff", "supplemental-context"):
        parser.add_argument("--" + name, type=Path, help="UTF-8 plain-text file")
    args = parser.parse_args()
    try:
        resolve_creation_pair(args)
        validate_creation_options(args)
        if args.format == 'create' and (args.worker_number is None or args.worker_number < 1):
            raise ValueError('--worker-number must be a positive integer; for review use the reviewed worker number')
        if not args.workspace_root.is_absolute() or not args.workspace_root.is_dir():
            raise ValueError(f"--project-root/--workspace-root {str(args.workspace_root)!r} must be an existing absolute project directory; supply the actual checkout path")
        single_line(args.manager_agent_id, '--manager-agent-id')
        if args.assignment_file and args.format != 'create':
            raise ValueError('--assignment-file requires --format create; omit it for direct prompt output')
        if args.format == 'create':
            args.assignment_file = assignment_path(args.assignment_file, args.workspace_root)
        role_input = {}
        if args.predecessor_agent_id:
            role_input["predecessor_agent_id"] = args.predecessor_agent_id
        input_contents = {
            "executor_result": "the complete retained native worker result",
            "reviewer_result": "the complete retained native reviewer result",
            "context_handoff": "the retained handoff with completed effects and remaining work",
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
        context = select_unit(args.selector, args.plan_root or args.workspace_root, args.unit, args.max_output_bytes,
                              [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])
        prompt = build_prompt(args.role, args.workspace_root, args.manager_agent_id,
                              "", context, role_input)
        if args.format == 'create':
            title_unit = args.unit
            # A whole item with Steps must display its complete assigned range.
            if '/' not in title_unit:
                steps = re.findall(r'^([1-9][0-9]*)\. ', context['work_item']['context_text'], re.M)
                if steps:
                    title_unit += f'/steps-{steps[0]}-{steps[-1]}' if len(steps) > 1 else f'/step-{steps[0]}'
            plan_ids = re.findall(r'^id: (PLAN-[0-9]{4})\r?$', context['plan']['frontmatter'], re.M)
            if len(plan_ids) != 1:
                raise ValueError('Plan selector must supply one canonical id in plan.frontmatter; use matching Plan and Workflow packages')
            title = workflow_title(args.project_name, args.role, args.worker_number, plan_ids[0] + '/' + title_unit)
            task_name = f'scoville_{args.role}_{args.worker_number}'
            if args.predecessor_agent_id:
                task_name += '_' + hashlib.sha256(args.predecessor_agent_id.encode('utf-8')).hexdigest()[:12]
            assignment = prompt + '\nAssignment: ' + title + '\n'
            message = assignment
            if args.assignment_file:
                checker = Path(__file__).with_name('check_text_size.py')
                read_check = file_read_instruction(args.assignment_file, checker, sys.executable)
                read_only = ' Stay read-only for project files and do not execute tests. The shared writing rules permit only necessary oversized-result preparation and publication under .scoville/temp.' if args.role == 'reviewer' else ''
                read_gate = ('before any receipt or project work. If the file is inaccessible or your read is incomplete, '
                             'stop and report blocked to your actual manager; do not acknowledge takeover. '
                             'Retain its complete facts, then follow the takeover contract in that assignment. '
                             if args.context_handoff else 'before any project work. ')
                message = (f'You are the assigned {args.role} (manager_agent_id={args.manager_agent_id}).{read_only} Read the complete UTF-8 assignment '
                           f'from {args.assignment_file} {read_gate}'
                           f'{read_check}'
                           'Follow that assignment and its '
                           'bundled Skill paths, then return its required result to the spawning manager.\n'
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
