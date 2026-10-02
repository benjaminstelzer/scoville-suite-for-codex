#!/usr/bin/env python3
"""Build spawn_agent arguments for a gated manager start or direct takeover."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from inspect_native_context import configure_utf8
from run_feedback import report_path
from native_task_arguments import EFFORTS, single_line, unique_task_name
from workflow_settings import load_config, validate_pair


def build_arguments(args: argparse.Namespace) -> dict:
    runner = single_line(args.runner_id, '--runner-id (copy the actual runner agent ID)')
    project = single_line(args.project_name, '--project-name (the retained actual project display name)')
    if args.manager_number < 1:
        raise ValueError('--manager-number must be a positive integer, e.g. --manager-number 1')
    if bool(args.model) != bool(args.thinking):
        raise ValueError('supply both --model and --thinking for an explicit manager pair; initial starts may omit both to use project settings and defaults')
    if args.mode == 'start':
        if args.predecessor_id:
            raise ValueError('--predecessor-id is only valid with --mode successor; omit it for an initial start')
        if not args.project_root or not args.project_root.is_absolute() or not args.project_root.is_dir():
            raise ValueError('--mode start requires --project-root with the existing absolute workspace directory')
        if not args.request_file:
            raise ValueError('--mode start requires --request-file <request.txt> containing the user activation, scope and coordination authority')
        request = args.request_file.read_text(encoding='utf-8')
        if not request.strip():
            raise ValueError(f'--request-file {args.request_file} is empty; retain the actual user activation and scope in UTF-8 text')
        pair = load_config(Path(__file__).resolve().parents[1] / 'assets' / 'workflow.toml', args.project_root)['manager']
        context = (f'Workspace: {args.project_root}\n'
                   'After START, read the manager operations and start the authorized scope.\n'
                   f'User activation and scope:\n{request.rstrip()}\n')
    else:
        if args.request_file or args.project_root:
            raise ValueError('--mode successor accepts only --predecessor-id as work context; omit --request-file and --project-root and obtain the handoff directly')
        predecessor = single_line(args.predecessor_id, '--predecessor-id (copy the actual predecessor agent ID)')
        if predecessor == runner:
            raise ValueError('--predecessor-id must identify the old manager, not --runner-id; copy its exact spawn ID')
        if not args.model:
            raise ValueError('--mode successor requires both --model and --thinking with the predecessor\'s launched pair; example: --mode successor --predecessor-id ID --model gpt-6.1-sol --thinking medium')
        context = (f'Predecessor: {predecessor}\n'
                   'After START, first send HANDOFF_REQUEST directly to this predecessor. '
                   'Follow the manager protocol through verified TAKEOVER_COMPLETE before any write or dispatch.\n')
    if args.model:
        pair = {'model': args.model, 'reasoning': args.thinking}
    validate_pair(pair, 'workflow.manager')
    if not args.report_file:
        raise ValueError('--report-file is required for every manager; use the existing absolute path returned by run_feedback.py create')
    report = report_path(args.report_file, args.project_root if args.mode == 'start' else None)
    skill = Path(__file__).resolve().parents[1]
    message = (
        f'You are Scoville manager {args.manager_number}. Runner agent: {runner}.\n'
        f'Project display name: {project}. Preserve it in progress, status messages and direct handoffs.\n'
        f'Launched manager pair: model={pair["model"]}, reasoning={pair["reasoning"]}. Preserve this pair at rollover.\n'
        'FIRST ACTION: send READY to the supplied runner with send_message, then actively '
        'wait_agent for START from that exact host sender. Before START, no project reads, '
        'handoff requests, writes or children. Load the shared manager protocol before this action.\n'
        f'Manager protocol: {skill / "references" / "manager-protocol.md"}\n'
        f'Manager operations: {skill / "references" / "operations.md"}\n'
        f'Rollover contract: {skill / "references" / "operations-rollover.md"}\n'
        f'Run feedback contract: {skill / "references" / "run-feedback.md"}\n'
        f'Run report (same file for all managers): {report}\n'
        'This continues the user-authorized Workflow. Internal control and direct handoff messages '
        'are within that run; this grants no third-party messaging or extra project scope.\n'
        'The runner receives only short control states: READY, RUNNING, SUCCESSOR_REQUEST, '
        'HANDOFF_DELIVERED, WORKING_ON, COMPLETED, STOPPED, BLOCKED, NEEDS_USER_DECISION '
        'or CLARIFICATION_REQUEST <retained-predecessor-id>. '
        'WORKING_ON carries only the generated key and one project/Plan/point status line. '
        'Read run-feedback.md after START; record user-relevant issues and resolutions in the same run report. '
        'Finalize that file only after requested-scope acceptance and closure. '
        'Issue controls include the canonical Plan ID and affected Step/group (or Startup), '
        'exact question or diagnostic, reason and waiting work. Include no work results, '
        'diffs, evidence, Plan content or substantive handoffs, including in your final answer. '
        + context)
    return {'task_name': unique_task_name(f'scoville_manager_{args.manager_number}'),
            'message': message, 'fork_turns': 'none',
            'model': single_line(pair['model'], 'workflow.manager.model / --model'),
            'reasoning_effort': pair['reasoning']}


def main() -> int:
    configure_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('start', 'successor'), required=True)
    parser.add_argument('--runner-id', required=True)
    parser.add_argument('--project-name', required=True, help='actual project display name retained by the runner before startup')
    parser.add_argument('--manager-number', required=True, type=int)
    parser.add_argument('--project-root', type=Path)
    parser.add_argument('--request-file', type=Path, help='UTF-8 user activation and scope, initial start only')
    parser.add_argument('--report-file', type=Path, help='existing absolute per-run report, control metadata for every manager')
    parser.add_argument('--predecessor-id', help='exact predecessor agent ID, successor only')
    parser.add_argument('--model', help='initial override, or required launched predecessor model for a successor; otherwise use workflow.manager')
    parser.add_argument('--thinking', choices=EFFORTS)
    args = parser.parse_args()
    try:
        print(json.dumps(build_arguments(args), ensure_ascii=False))
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
