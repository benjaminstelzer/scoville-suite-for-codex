#!/usr/bin/env python3
"""Build spawn_agent arguments for a gated manager start or direct takeover."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from inspect_native_context import configure_utf8
from run_feedback import report_path
from native_task_arguments import EFFORTS, single_line


def build_arguments(args: argparse.Namespace) -> dict:
    runner = single_line(args.runner_id, '--runner-id (copy the actual runner agent ID)')
    if args.manager_number < 1:
        raise ValueError('--manager-number must be a positive integer, e.g. --manager-number 1')
    if bool(args.model) != bool(args.thinking):
        raise ValueError('supply both --model and --thinking for an explicit manager pair, or omit both to inherit the runner pair')
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
        context = (f'Workspace: {args.project_root}\n'
                   'After START, read the manager operations and start the authorized scope.\n'
                   f'User activation and scope:\n{request.rstrip()}\n')
    else:
        if args.request_file or args.project_root:
            raise ValueError('--mode successor accepts only --predecessor-id as work context; omit --request-file and --project-root and obtain the handoff directly')
        predecessor = single_line(args.predecessor_id, '--predecessor-id (copy the actual predecessor agent ID)')
        if predecessor == runner:
            raise ValueError('--predecessor-id must identify the old manager, not --runner-id; copy its exact spawn ID')
        context = (f'Predecessor: {predecessor}\n'
                   'After START, send HANDOFF_REQUEST directly to that predecessor with send_message. '
                   'Wait for its substantive handoff; do not ask the runner for it. '
                   'Read the manager operations, compare the handoff with the canonical Plan and actual files, '
                   'and resolve missing or conflicting facts directly before any project write or child dispatch. '
                   'Preserve pending questions, answers, stops, review and commit boundaries. '
                   'Then send HANDOFF_ACCEPTED to the predecessor and RUNNING to the runner. '
                   'Wait actively for TAKEOVER_COMPLETE from the exact runner before writing or dispatching. '
                   'It confirms the predecessor ended after your receipt. Then resume the retained next action '
                   'without repeating the consumed checkpoint.\n')
    if not args.report_file:
        raise ValueError('--report-file is required for every manager; use the existing absolute path returned by run_feedback.py create')
    report = report_path(args.report_file, args.project_root if args.mode == 'start' else None)
    skill = Path(__file__).resolve().parents[1]
    message = (
        f'You are Scoville manager {args.manager_number}. Runner agent: {runner}.\n'
        'FIRST ACTION: send READY to that runner using send_message. The host sender identity '
        'must identify you; never claim another agent ID. Wait for START from that exact runner '
        'using wait_agent; do not end your turn while this handshake is pending. '
        'Before START, do not read project files, request a handoff, dispatch children or write. '
        'A missing or failed message stops startup with its diagnostic.\n'
        f'Manager operations: {skill / "references" / "operations.md"}\n'
        f'Rollover contract: {skill / "references" / "operations-rollover.md"}\n'
        f'Run feedback contract: {skill / "references" / "run-feedback.md"}\n'
        f'Run report (same file for all managers): {report}\n'
        'This continues the user-authorized Workflow. Internal control and direct handoff messages '
        'are within that run; this grants no third-party messaging or extra project scope.\n'
        'The runner receives only short control states: READY, RUNNING, SUCCESSOR_REQUEST, '
        'HANDOFF_DELIVERED, WORKING_ON, CAPACITY_REQUEST, COMPLETED, STOPPED, BLOCKED or NEEDS_USER_DECISION. '
        'RUNNING means startup checks are complete and, for a successor, the direct handoff and '
        'child quiescence are verified. Report rejected or pending takeover as BLOCKED; '
        'never use RUNNING CONTROL or a qualified RUNNING for that state. '
        'WORKING_ON carries only the generated display key, project, Plan point and actual overall scope. '
        'Read run-feedback.md after START; record user-relevant issues and resolutions in the same run report. '
        'Finalize that file only after requested-scope acceptance and closure. '
        'Include only the necessary control ID, error or user question; never send it work results, '
        'diffs, evidence, Plan content or substantive handoffs, including in your final answer. '
        'A successor request includes your exact agent ID and an explicit manager model/effort change '
        'only if one is in force. Only the runner starts managers.\n'
        'Context thresholds only schedule rollover. Complete the selected Step or Step group, '
        'including required checks, due review, repairs, Plan updates and authorized commits, '
        'and confirm all children and writes are quiescent before requesting a successor. '
        'Never transfer unfinished assignments merely because a threshold was crossed. '
        'A user stop remains immediate.\n'
        + context)
    result = {'task_name': f'scoville_manager_{args.manager_number}', 'message': message, 'fork_turns': 'none'}
    if args.model:
        result.update(model=single_line(args.model, '--model'), reasoning_effort=args.thinking)
    return result


def main() -> int:
    configure_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('start', 'successor'), required=True)
    parser.add_argument('--runner-id', required=True)
    parser.add_argument('--manager-number', required=True, type=int)
    parser.add_argument('--project-root', type=Path)
    parser.add_argument('--request-file', type=Path, help='UTF-8 user activation and scope, initial start only')
    parser.add_argument('--report-file', type=Path, help='existing absolute per-run report, control metadata for every manager')
    parser.add_argument('--predecessor-id', help='exact predecessor agent ID, successor only')
    parser.add_argument('--model', help='explicitly selected manager model; otherwise inherit runner')
    parser.add_argument('--thinking', choices=EFFORTS)
    args = parser.parse_args()
    try:
        print(json.dumps(build_arguments(args), ensure_ascii=False))
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
