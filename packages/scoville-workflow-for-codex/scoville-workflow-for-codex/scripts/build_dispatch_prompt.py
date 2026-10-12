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
from native_task_arguments import add_creation_options, creation_arguments, workflow_title, validate_creation_options, single_line, assignment_path, publish_assignment, shell_command, budget_retry
from resolve_model_pair import resolve
from workflow_settings import ROUTES, load_config
from check_agent_context import measure

MAX_NON_GOALS_BYTES = 8192
def communication_rule(language: str) -> str:
    single_line(language, '--communication-language')
    return (
        f"Communication language: {language}. Use it for commentary, messages and natural-language text in result fields. "
        "Your commentary and messages go to the manager. When commentary is needed, use short labelled lines "
        f"such as action: <next action in {language}>. Do not add introductory narration, including before reading this assignment. "
        "Your final uses the required result fields. "
        "Keep required field names, status values, quotes, relay text and technical literals exact."
    )


def select_unit(selector: Path, root: Path, unit: str, max_output_bytes: int | None = None, retry_arguments: list[str] | None = None, plan: str | None = None) -> dict:
    if not re.fullmatch(r"W-[0-9]{3}(?:/step-[1-9][0-9]*)?", unit):
        raise ValueError(f"--unit {unit!r} is invalid; use ONE Step, e.g. W-001/step-2, or W-001 for reviewer closure; no Step ranges")
    command = [sys.executable, "-B", str(selector), "--root", str(root),
               "--unit", unit, "--format", "json"]
    if max_output_bytes is not None:
        command.extend(["--max-output-bytes", str(max_output_bytes)])
    if plan:
        command.extend(['--plan', plan])
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


def work_item_context(item: dict) -> str:
    """Render selected original Steps with binding fields; keep whole items intact."""
    unit = item.get('unit')
    if not isinstance(unit, str) or not re.fullmatch(r'W-[0-9]{3}(?:/step-[1-9][0-9]*)?', unit):
        raise ValueError('SELECTOR_INCOMPATIBLE: Plan must provide a valid unit')
    source = item.get('source_text')
    if not isinstance(source, str) or not source.strip():
        raise ValueError('SELECTOR_INCOMPATIBLE: selected unit must contain source_text')
    if '/' not in unit:
        complete = item.get('context_text')
        if not isinstance(complete, str) or not complete.strip():
            raise ValueError('SELECTOR_INCOMPATIBLE: whole item requires context_text')
        return complete.rstrip()
    fields = []
    for key in ('header', 'status', 'depends_on', 'blocked_by', 'decisions', 'outcome', 'acceptance'):
        value = item.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'SELECTOR_INCOMPATIBLE: selected Steps require {key}')
        fields.append(value)
    if 'instructions' in item:
        value = item['instructions']
        if not isinstance(value, str) or not value.strip():
            raise ValueError('SELECTOR_INCOMPATIBLE: invalid instructions')
        fields.append('Instructions: ' + value)
    return '\n'.join(fields) + '\nSteps:\n' + source


def validate_execution_start(root: Path, context: dict) -> None:
    validator = Path(__file__).with_name('validate_profile.py')
    result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(validator),
                             '--root', str(root), '--format', 'json'],
                            capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise ValueError('Execution start validation failed; correct the saved profile before dispatch.\n'
                         + result.stdout + result.stderr)
    verdict = json.loads(result.stdout)
    if verdict.get('valid') is not True:
        raise ValueError('Execution start validation did not confirm a valid profile; no assignment published.\n'
                         + result.stdout + result.stderr)
    item = context['work_item']
    plan = context['plan']['frontmatter']
    if (not re.search(r'^status: active\r?$', plan, re.M)
            or not re.search(r'^current_item: ' + re.escape(item['unit'].split('/')[0]) + r'\r?$', plan, re.M)
            or item['status'].strip() != 'Status: in_progress'
            or not re.match(r'[1-9][0-9]*\. \[status: in_progress\]', item['source_text'])):
        raise ValueError('EXECUTION_NOT_STARTED: save the Plan as active with this Work Item as current_item; '
                         'save the Work Item and selected Step as in_progress before dispatch; no assignment published.')
    for diagnostic in verdict.get('diagnostics', []):
        if diagnostic.get('severity') == 'warning':
            print(json.dumps(diagnostic, ensure_ascii=False), file=sys.stderr)


def result_contract(role: str) -> list[str]:
    return [
        "Return minimal labelled fields, no narration.",
        ("""Use these fields:
status: pass | changes_requested | blocked
evidence: <decisive sources and check evidence; for closure, concise coverage of every Step and Acceptance criterion>
findings: <none, or each location, effect, smallest correction and affected Step number or none>
blocker: <only for blocked: exact prerequisite or decision>
limits: <material missing evidence, or none>
Return pass only when the assigned review ran with no unresolved defect or required evidence gap. For closure, cover every original Step and full Work Item Acceptance.""" if role == 'reviewer' else
         """Return done when this ONE Step and its required checks finish. A blocker returns blocked; name its cause and effect and stop dependent writes. Use these fields; no recap, work log or Acceptance verdict:
status: done | blocked
changes:
- path: <each changed path to report>
  before: <exact lines or diff hunk before the reported change, or "new file">
  after: <exact lines or diff hunk after the reported change, "current file" for a new file created by this assignment, or "deleted file">
checks: <each decisive command or observation and its actual result>
problems: <cause and effect, or none>
limits: <missing baseline or other evidence limit, or none>
For a new file created by this assignment, use before: "new file" and after: "current file"; do not repeat its content.
A behavior description is not before/after evidence. Normally report only changes made by this assignment. If reviewer_result is blocked only for missing change evidence, this is an evidence-only follow-up: report the original reviewed change completely using executor_result and reviewer_result. Change no files and repeat no unchanged successful checks solely for that evidence. If required original evidence is unavailable, return blocked naming it. Use changes: none when no file changed, except for that evidence-only follow-up. Preserve unrelated changes. Do not claim attribution you cannot prove."""),
        "Return the complete result through your native final only, then stay inactive until the manager gives the next helper assignment. Do not also send a duplicate result.",
    ]


def build_explorer_prompt(workspace: Path, context: dict, role_input: dict, language: str, *, reuse: bool = False) -> str:
    if set(role_input) != {'supplemental_context'} or not role_input['supplemental_context'].strip():
        raise ValueError('exploration requires --supplemental-context with the complete question or change request; no executor or reviewer result flags')
    return role_prompt('explorer', workspace, context, role_input, language, reuse=reuse)


def binding_context(context: dict) -> list[str]:
    if not context:
        return []
    plan = context['plan']
    exclusions = plan.get('non_goals')
    if not isinstance(exclusions, str) or not exclusions.strip():
        raise ValueError('SELECTOR_INCOMPATIBLE: Plan must provide non-empty plan.non_goals; use matching Plan and Workflow packages')
    if len(exclusions.encode('utf-8')) > MAX_NON_GOALS_BYTES:
        raise ValueError(f'NON_GOALS_TOO_LARGE: observed {len(exclusions.encode("utf-8"))} UTF-8 bytes; limit {MAX_NON_GOALS_BYTES}; shorten redundancy while preserving every exclusion before dispatch')
    lines = []
    if plan.get('frontmatter'):
        lines.append('## Plan identity\n' + plan['frontmatter'])
    if plan.get('goal'):
        lines.append(plan['goal'])
    lines.append(exclusions)
    for decision in context.get('decisions', []):
        if re.search(r'^status: accepted\r?$', decision, re.M):
            lines.append('## Binding Decision\n' + decision)
    if context.get('direct_dependencies'):
        lines.append('## Dependency state\n' + json.dumps(context['direct_dependencies'], ensure_ascii=False))
    lines.append('## Work Item context\n' + work_item_context(context['work_item']))
    return lines


def role_prompt(role: str, workspace: Path, context: dict, role_input: dict, language: str, *, reuse: bool = False) -> str:
    single_line(language, '--communication-language')
    if role == 'reviewer':
        mode = 'Step review' if '/' in context['work_item']['unit'] else 'Closure review'
        task = [f'Task: {mode} of the assigned unit.']
    else:
        task = ['Task: investigate the supplied request.' if role == 'explorer' else 'Task: execute the assigned unit.']
    if role != 'explorer':
        task.append('## Assigned unit\n' + context['work_item']['unit'])
    task.extend(binding_context(context))
    task.extend('## ' + key + '\n' + value for key, value in role_input.items())
    if reuse:
        return '\n'.join(task + [f'Communication language: {language}.']) + '\n'
    skill = Path(__file__).resolve().parents[1]
    checker = skill / 'scripts/check_text_size.py'
    shell = skill / 'references/shell-commands.md'
    writing_path = skill / 'references/writing.md'
    for file in (checker, shell, writing_path):
        if not file.is_file():
            raise ValueError(f'bundled dependency missing: {file}; use the intact matching suite package before dispatch')
    writing = writing_path.read_text(encoding='utf-8')
    shell_text = shell.read_text(encoding='utf-8')
    suite = skill.parent.parent if skill.parent.name == skill.name else skill.parent
    lines = [
        f'scoville_role={role}', 'dispatch_contract=SCOVILLE_AGENT_DISPATCH_V1',
        f'workspace_root={workspace}',
        f'python: {sys.executable}', f'text_size_checker: {checker}',
        f'shell_command_rules: {shell}; complete text embedded below.',
        f'suite_directory: {suite}',
        'Choose appropriate Skills yourself. Resolve selected suite Skills from suite_directory in this matching build, preserving explicit user invocations and overrides. Skill selection grants no extra permissions. Load only the references needed for this assignment.',
        'Do not activate Workflow or Handoff or assume manager permissions. The manager owns Plan, Decision and index edits, staging, commits and dispatch. Do not edit those records, change Workflow settings or create agents/chats. Follow repository constraints. A selected Skill grants no extra role permissions.',
        'Use the named interpreter and checker for command capture, size checks and complete result delivery, even outside the workspace. Only necessary oversized-result preparation/publication under .scoville/temp is permitted for read-only roles; no source captures or unrelated external access.',
        "The complete matching writing and shell-command rules below satisfy their required reads.",
        'Retain your role, writing, shell-command and result rules for later tasks; later assignments contain only the next task. Do not reload already read rules or Skills for each message.',
        writing, shell_text,
    ]
    if role == 'explorer':
        lines.extend(['Investigate only the supplied question, change request or planning preparation. Read necessary sources; do not implement, change project files, run tests, edit Plan records, change settings or create agents. Planning preparation returns proposals, scope and open questions; the manager writes the Plan. Mark facts affected by possible concurrent executor writes as provisional.', 'Return minimal labelled fields, no narration:\nstatus: done | blocked\nanswer: <answer, recommendation, or planning proposals with scope and open questions>\nevidence: <decisive source locations>\nblocker: <only for blocked: missing prerequisite or decision>\nlimits: <material limits, or none>\nNo review acceptance.', result_contract(role)[-1]])
    elif role == 'executor':
        lines.append("Perform only the ONE selected original Step and its required checks. Work Item Outcome and Acceptance constrain this Step; they do not authorize additional work. If the Step's action or completion boundary is materially unclear, return blocked before writes, naming the ambiguity. Preserve unrelated changes and completed effects. Do not advance to later Steps or rewrite the assignment. Review findings are additional context for this Step, not new scope. Before each edit, retain the exact original changed lines for your result. Stop writing before your result.")
        lines.extend(result_contract(role))
    else:
        lines.append('The Task line selects Step review or Closure review; apply only that one.')
        lines.extend(['Step review: stay read-only; run no tests. Review the actual changes of the selected Executor assignment against this SAME original Step and affected Acceptance. An evidence-only follow-up continues review of the original change. Use the LAST Executor final as evidence and the supplied review result as open findings. If direct evidence shows an omitted change from that assignment, return blocked naming the path and missing attribution. First check its evidence for each changed path. Missing exact before and after lines, or a new-file or deleted-file fact: return blocked naming the path and missing evidence. For before "new file" with after "current file", read that complete file as its after lines. This applies only to files created by the reported assignment. If that file is missing, unreadable, inconsistent with the reported assignment or not attributable to it, return blocked naming the path and missing evidence. A behavior description is not before/after evidence. Return changes_requested for actual implementation defects. Read unchanged files only for relevant effects or dependencies. Preserve open earlier findings. Do not review unrelated or unattributed changes, other Steps, the whole Plan or cumulative Step diffs. Executor results are reports, not approval; assess whether their reported checks support their claims.', 'Closure review: stay read-only; run no tests.\n1. For EVERY original Step and each criterion of the FULL Work Item Acceptance, inspect the sources and evidence needed to verify it; no unrelated general audit.\n2. Verify required preservation against a baseline matching the Work Item start or equivalent direct evidence. Git status or diff counts only when its base matches that start. Reported passing tests do not prove unchanged test sources.\n3. Missing required evidence prevents pass; return blocked naming it.\nRetained earlier review coverage is evidence, not a current pass. Keep open findings. Executor results are reports, not approval. A missing implementation finding without a matching Step uses affected Step: none.'])
        lines.extend(result_contract(role))
    lines.extend(task)
    lines.append('## Communication\n' + communication_rule(language))
    lines.append('Before acting, check this assignment, role rights, scope, required reads and prerequisites. Before communicating, check language, required result fields and evidence for each claim. Correct a mismatch; stop dependent work on a missing prerequisite. Do not claim an unperformed check or output a checklist transcript.')
    lines.append('On user stop, stop dependent work and return actual retained effects. Host compaction continues this same assignment; preserve completed effects and checks. Do not replace yourself, choose another Step or perform threshold handovers.')
    return '\n'.join(lines) + '\n'


def build_prompt(role: str, workspace: Path, context: dict, role_input: dict, language: str, *, reuse: bool = False) -> str:
    if role == 'explorer':
        return build_explorer_prompt(workspace, context, role_input, language, reuse=reuse)
    unit = context.get('work_item', {}).get('unit', '')
    if not isinstance(unit, str):
        raise ValueError('SELECTOR_INCOMPATIBLE: Plan must provide a valid unit')
    if not re.fullmatch(r'W-[0-9]{3}/step-[1-9][0-9]*', unit):
        if role != 'reviewer' or not re.fullmatch(r'W-[0-9]{3}', unit):
            raise ValueError('executor and Step review require exactly ONE Step: --unit W-001/step-1; only reviewer closure accepts --unit W-001')
    allowed = {'reviewer_result'}
    if role == 'reviewer':
        allowed.add('executor_result')
        if not role_input.get('executor_result', '').strip():
            raise ValueError('review requires the complete executor result; supply --executor-result')
    elif 'executor_result' in role_input:
        if not role_input.get('executor_result', '').strip() or not role_input.get('reviewer_result', '').strip():
            raise ValueError('executor evidence follow-up requires complete --executor-result and --reviewer-result inputs')
        allowed.add('executor_result')
    if set(role_input) - allowed:
        raise ValueError('unknown role input; executor/reviewer accept only complete role results. --supplemental-context is for Explorer requests, not rewritten dispatch text')
    return role_prompt(role, workspace, context, role_input, language, reuse=reuse)


def resolve_creation_pair(args: argparse.Namespace, context: dict | None = None) -> None:
    """Apply configured/Step pairs; verify retained choices without silent overrides."""
    if args.format != 'create':
        if args.route:
            raise ValueError('--route requires --format create; omit it for prompt-only output')
        return
    if args.model is not None:
        single_line(args.model, '--model')
    if args.override_reason:
        single_line(args.override_reason, '--override-reason')
    retained = args.agent_id or args.replacement_of or (args.reviewer_result if args.role == 'executor' else None)
    if retained and (args.model is None or args.thinking is None):
        raise ValueError('reuse or correction requires both --model and --thinking: retain the launched pair or supply an explicitly justified fresh replacement; --route cannot replace it')
    step = context['work_item']['source_text'] if context and '/' in context['work_item']['unit'] else ''
    route_match = re.search(r'\[route: (ultra_low|low|medium|high|ultra_high)\]', step)
    fields = {}
    execution = re.search(r'\[execute: ([^\]]+)\]', step) if args.role == 'executor' else None
    if execution:
        fields = dict(value.split('=', 1) for value in execution[1].split('; '))
    if route_match and (args.route is None or ROUTES.index(route_match[1]) > ROUTES.index(args.route)):
        args.route = route_match[1]
    if args.override_reason and args.model is not None and args.thinking is not None:
        return  # Explicit user role choice, not an inferred or replacement override.
    if retained:
        if route_match:
            config = load_config(Path(__file__).resolve().parents[1] / 'assets/workflow.toml', args.workspace_root)
            expected = resolve(config, args.role, args.route, fields.get('model'), fields.get('reasoning'))
        else:
            expected = {'model': fields.get('model', args.model), 'thinking': fields.get('reasoning', args.thinking)}
        if (args.model, args.thinking) != (expected['model'], expected['thinking']):
            raise ValueError('selected Step requires a different explicit pair; spawn a fresh agent with only --route, or use --override-reason for an explicit user role choice')
        return
    if not args.route:
        if fields.get('model') and fields.get('reasoning'):
            expected = {'model': fields['model'], 'thinking': fields['reasoning']}
        else:
            raise ValueError('--format create requires --route CLASS or both --model and --thinking with --override-reason; normal fresh spawns use only --route')
    else:
        config = load_config(Path(__file__).resolve().parents[1] / 'assets/workflow.toml', args.workspace_root)
        expected = resolve(config, args.role, args.route, fields.get('model'), fields.get('reasoning'))
    for key, current in (('model', args.model), ('thinking', args.thinking)):
        if current is not None and current != expected[key] and not args.override_reason:
            raise ValueError('fresh flags differ from the configured or explicit Step pair; use only --route, or provide --override-reason for an explicit user role choice')
    args.model = args.model if args.model is not None else expected['model']
    args.thinking = args.thinking if args.thinking is not None else expected['thinking']


def main() -> int:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    # Preserve literal selector newlines in prompt-only output, including CRLF.
    sys.stdout.reconfigure(newline='')
    parser = argparse.ArgumentParser(description=__doc__)
    add_creation_options(parser)
    parser.add_argument('--route', choices=ROUTES, help='normal fresh spawn: resolve configured and explicit Step pairs; manual overrides require --override-reason')
    parser.add_argument('--override-reason', help='explicit user role choice only; required to bypass configured or Step pairs')
    parser.add_argument('--replacement-of', help='previous exact handle for a fresh replacement retaining its full pair; never overrides explicit Step annotations')
    parser.add_argument('--agent-id', help='exact existing agent handle for followup_task; omit for spawn_agent')
    parser.add_argument('--plan', help='selected canonical PLAN-NNNN; omitted means active Plan')
    parser.add_argument('--worker-number', type=int, help='next number for a new agent of this role throughout the Manager thread; reuse keeps it')
    parser.add_argument("--selector", type=Path, default=Path(__file__).with_name("select_context.py"))
    parser.add_argument("--max-output-bytes", type=int,
                        help="explicit UTF-8 budget for the complete Plan selector result; omit for its default")
    parser.add_argument("--plan-root", type=Path)
    parser.add_argument("--unit", help='required for executor/reviewer; optional Plan context for explorer')
    parser.add_argument("--role", choices=("executor", "reviewer", "explorer"), required=True)
    parser.add_argument('--communication-language', required=True, help='nonempty single-line language name from the current user message or explicit user choice, e.g. German')
    parser.add_argument("--project-root", "--workspace-root", dest="workspace_root", type=Path, required=True)
    parser.add_argument("--assignment-file", type=Path, help="optional new absolute UTF-8 assignment file for --format create; defaults to an external system temporary path, for every fresh assignment")
    for name in ("executor-result", "reviewer-result", "supplemental-context"):
        parser.add_argument("--" + name, type=Path, help="UTF-8 plain-text file")
    args = parser.parse_args()
    try:
        single_line(args.communication_language, '--communication-language')
        if args.route and (args.agent_id or args.replacement_of):
            raise ValueError('--route cannot combine with --agent-id or --replacement-of; retain both launched pair flags')
        if args.replacement_of is not None:
            single_line(args.replacement_of, '--replacement-of')
            if args.format != 'create' or args.agent_id or args.override_reason is not None:
                raise ValueError('--replacement-of requires fresh create, without --agent-id or --override-reason')
        if args.plan and not args.unit:
            raise ValueError('--plan requires --unit; Explorer Plan context needs both, or omit both for a question without Plan context')
        if args.role != 'explorer' and not args.unit:
            raise ValueError('--unit is required for executor and reviewer')
        if args.agent_id:
            single_line(args.agent_id, '--agent-id')
            if args.format != 'create':
                raise ValueError('--agent-id requires --format create for unchanged followup_task arguments')
        if args.format == 'create' and (args.worker_number is None or args.worker_number < 1):
            raise ValueError('--worker-number must be a positive role agent number; count each role separately and keep its number on reuse')
        if not args.workspace_root.is_absolute() or not args.workspace_root.is_dir():
            raise ValueError(f"--project-root/--workspace-root {str(args.workspace_root)!r} must be an existing absolute project directory; supply the actual checkout path")
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
                               [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]], args.plan) if args.unit else {})
        resolve_creation_pair(args, context)
        validate_creation_options(args)
        if args.agent_id:
            measurement = measure(args.agent_id, args.workspace_root)
            if measurement['action'] != 'reuse':
                raise ValueError('agent context is at or above threshold; spawn a new associated agent instead of followup')
            if (args.model, args.thinking) != (measurement['model'], measurement['reasoning_effort']):
                raise ValueError('followup model/thinking differs from the measured retained pair; use the launched pair or explicitly choose a fresh agent')
        prompt = build_prompt(args.role, args.workspace_root, context, role_input, args.communication_language, reuse=bool(args.agent_id))
        if args.format == 'create':
            if args.role == 'executor':
                validate_execution_start(args.plan_root or args.workspace_root, context)
            title_unit = args.unit
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
                read_only = (' No tests or project-file changes. Only prepare and publish necessary '
                             'oversized results under .scoville/temp using shared complete-file rules.'
                             if args.role in {'reviewer', 'explorer'} else '')
                message = (f'You are the assigned {args.role}.{read_only} '
                           f'{communication_rule(args.communication_language)} Read the complete UTF-8 assignment '
                           f'from {args.assignment_file} before any project work. '
                           'Reading this external assignment file is permitted. Choose your reading method. '
                           'Follow the assignment and '
                           'bundled Skill paths; return its required result.\n'
                           f'Assignment: {title}\n')
            if args.agent_id:
                message = (f'Next task: read the complete UTF-8 file {args.assignment_file} before any project work; reading it is permitted.\n'
                           f'Assignment: {title}\n')
            output = ({'target': args.agent_id, 'message': message} if args.agent_id else
                      creation_arguments(message, task_name, args.model, args.thinking))
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
