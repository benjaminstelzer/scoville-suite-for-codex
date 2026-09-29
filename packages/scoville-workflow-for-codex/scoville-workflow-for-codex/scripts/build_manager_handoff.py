#!/usr/bin/env python3
"""Build a manager successor from its predecessor's own native settings."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from uuid import UUID

from inspect_native_context import configure_utf8, event_payload, load_events, resolve_rollout
from native_task_arguments import EFFORTS, creation_arguments, workflow_title, takeover_instruction


def manager_pair(events: list[dict], thread_id: str) -> tuple[str, str]:
    metas = [event_payload(e) for e in events if e.get('type') == 'session_meta']
    if len(metas) != 1 or metas[0].get('session_id', metas[0].get('id')) != thread_id:
        raise ValueError('native rollout does not identify this manager')
    contexts = [event_payload(e) for e in events if e.get('type') == 'turn_context']
    if not contexts:
        raise ValueError('manager model/effort unavailable; recover its native settings before rollover')
    current = contexts[-1]
    model, effort = current.get('model'), current.get('effort')
    if not model or not effort:
        raise ValueError('manager model/effort unavailable; do not use worker or project defaults')
    return model, effort


def main() -> int:
    configure_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-id', required=True)
    parser.add_argument('--project-name', required=True)
    parser.add_argument('--plan-id', required=True)
    parser.add_argument('--unit', help='only when the manager is scoped to a Work Item or Steps')
    parser.add_argument('--manager-number', required=True, type=int, help='successor number')
    parser.add_argument('--handoff-file', required=True, type=Path)
    parser.add_argument('--report-to-thread-id', help='verified original caller UUID, when a final report is required')
    parser.add_argument('--thread-id', default=os.environ.get('CODEX_THREAD_ID'))
    parser.add_argument('--sessions-root', type=Path)
    parser.add_argument('--rollout', type=Path, help='known native rollout for this predecessor')
    parser.add_argument('--override-model', help='only for an explicit user model change')
    parser.add_argument('--override-thinking', choices=EFFORTS)
    args = parser.parse_args()
    try:
        try:
            predecessor = str(UUID(args.thread_id or ''))
        except ValueError:
            raise ValueError('set CODEX_THREAD_ID or --thread-id to this predecessor manager’s actual UUID') from None
        if args.manager_number < 1:
            raise ValueError('--manager-number must be the positive successor manager number')
        report_to = None
        if args.report_to_thread_id:
            try:
                report_to = str(UUID(args.report_to_thread_id))
            except ValueError:
                raise ValueError('--report-to-thread-id must be the verified original caller UUID; copy it unchanged') from None
        model, thinking = manager_pair(load_events(resolve_rollout(args)), predecessor)
        if bool(args.override_model) != bool(args.override_thinking):
            raise ValueError('an explicit user change requires both override arguments')
        if args.override_model:
            model, thinking = args.override_model, args.override_thinking
        handoff = args.handoff_file.read_text(encoding='utf-8')
        if not handoff.strip():
            raise ValueError('--handoff-file must contain scope, state, constraints and next action')
        identity = args.plan_id + ('/' + args.unit if args.unit else '')
        title = workflow_title(args.project_name, 'coordinator', args.manager_number, identity)
        skill = Path(__file__).resolve().parents[1] / 'SKILL.md'
        prompt = (takeover_instruction(predecessor)
                  + f'Continue the explicitly requested Scoville Workflow using {skill}.\n'
                  f'You are manager {args.manager_number} for {args.plan_id}. '
                  f'Your inherited manager model/effort is {model}/{thinking}.\n'
                  f'Predecessor chat: {predecessor}.\n'
                  'Continue from the retained state. '
                  'Preserve completed work, pending results, user stops and pending questions. '
                  'Process an existing answer; do not repeat an unanswered question solely because of rollover.\n\n'
                  'Use the supplied exact Plan path or the Plan selector to locate the active Plan. '
                  'Do not guess Plan/Decision filenames or search unrelated test artifacts.\n\n'
                  'The predecessor already consumed the checkpoint boundary that caused this rollover. '
                  'Resume the pending next action, not another startup checkpoint or manager creation. '
                  'Run the next coordinator checkpoint only after new checked work or a newly retained worker handoff.\n\n'
                  + (f'Final report destination: {report_to}. Preserve this exact ID in --report-to-thread-id at later rollovers.\n\n' if report_to else '')
                  + handoff)
        print(json.dumps(creation_arguments(prompt, title, args.project_id, model, thinking), ensure_ascii=False))
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
