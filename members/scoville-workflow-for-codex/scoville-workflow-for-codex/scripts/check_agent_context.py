#!/usr/bin/env python3
"""Check this native subagent's active context before continuing work."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys
from workflow_settings import load_config

HEADER_LIMIT = 1024 * 1024
NATIVE_ID = re.compile(r'[A-Za-z0-9._:-]{1,128}')


def bound_identity(path: Path, thread_id: str) -> dict | None:
    """Bind the native environment to its own subagent header, never a Manager."""
    with path.open('rb') as stream:
        header = stream.readline(HEADER_LIMIT + 1)
    if not header or len(header) > HEADER_LIMIT:
        return None
    try:
        event = json.loads(header)
    except (ValueError, UnicodeError):
        return None
    if not isinstance(event, dict) or type(event.get('ordinal')) is not int or event['ordinal'] != 0 or event.get('type') != 'session_meta':
        return None
    payload = event.get('payload')
    if not isinstance(payload, dict):
        return None
    identity, source = payload.get('id'), payload.get('source')
    if identity != thread_id or not isinstance(source, dict):
        return None
    subagent = source.get('subagent')
    spawn = subagent.get('thread_spawn') if isinstance(subagent, dict) else None
    if not isinstance(spawn, dict):
        return None
    parent, agent = spawn.get('parent_thread_id'), spawn.get('agent_path')
    if (not isinstance(parent, str) or not NATIVE_ID.fullmatch(parent) or parent == thread_id
            or not isinstance(agent, str) or not agent.strip() or any(c in agent for c in '\r\n')):
        return None
    return {'thread_id': thread_id, 'parent_thread_id': parent, 'agent_id': agent}


def resolve_session(root: Path, session_path: Path | None = None) -> tuple[Path, dict]:
    identity = os.environ.get('CODEX_THREAD_ID', '')
    if not NATIVE_ID.fullmatch(identity):
        raise ValueError('CODEX_THREAD_ID must identify this native subagent; run in its own environment')
    if session_path is not None:
        binding = bound_identity(session_path, identity) if session_path.is_file() else None
        if binding is None:
            raise ValueError('--session-path does not bind this native subagent; rerun once without --session-path; do no project work')
        return session_path, binding
    if not root.is_dir():
        raise ValueError(f'native sessions directory is missing: {root}; verify CODEX_HOME or --sessions-root')
    matches = []

    def enumeration_error(error):
        raise error

    for directory, _, files in os.walk(root, onerror=enumeration_error):
        for name in files:
            if name.endswith('.jsonl'):
                path = Path(directory) / name
                binding = bound_identity(path, identity)
                if binding is not None:
                    matches.append((path, binding))
    if len(matches) != 1:
        raise ValueError(f'own native subagent session is missing or ambiguous ({len(matches)} matches); do no project work')
    return matches[0]


def snapshot(path: Path) -> list[dict]:
    # Fix the byte boundary before reading a concurrently appended rollout.
    for _ in range(2):
        with path.open('rb') as stream:
            size = os.fstat(stream.fileno()).st_size
            data = stream.read(size)
        if len(data) == size and data.endswith(b'\n'):
            return [json.loads(line) for line in data.splitlines()]
    raise ValueError('native rollout has an incomplete tail; current context cannot be measured')


def inspect(path: Path, binding: dict) -> dict:
    latest = {}
    last_ordinal = -1
    next_parent = None
    seen = set()
    started = False
    thread_id, agent_id = binding['thread_id'], binding['agent_id']
    for event in snapshot(path):
        ordinal = event.get('ordinal')
        if type(ordinal) is not int or ordinal <= last_ordinal:
            raise ValueError('rollout ordinals must be unique and increasing')
        last_ordinal = ordinal
        payload = event.get('payload', {})
        kind = event.get('type')
        if ordinal == 0 and kind != 'session_meta':
            raise ValueError('rollout must start with its bound child session metadata')
        if kind == 'session_meta':
            if started:
                raise ValueError('session metadata after the first task_started is invalid')
            source = payload.get('source')
            if isinstance(source, dict):
                spawn = source.get('subagent', {}).get('thread_spawn')
                if not isinstance(spawn, dict) or not isinstance(spawn.get('parent_thread_id'), str) or not spawn['parent_thread_id'].strip():
                    raise ValueError('subagent session metadata needs its native parent identity')
                parent = spawn['parent_thread_id']
            elif isinstance(source, str) and source.strip():
                spawn, parent = {}, None
            else:
                raise ValueError('session metadata source is malformed')
            identity = payload.get('id')
            if not isinstance(identity, str) or not identity.strip():
                raise ValueError('session metadata id is malformed')
            if 'meta' not in latest:
                if ordinal != 0 or identity != thread_id or spawn.get('agent_path') != agent_id or parent != binding['parent_thread_id']:
                    raise ValueError('first session metadata does not bind the requested child and its parent')
                latest['meta'] = payload
                next_parent = parent
                seen.add(identity)
            elif identity == thread_id:
                original = latest['meta']['source']['subagent']['thread_spawn']
                if spawn.get('agent_path') != agent_id or parent != original['parent_thread_id']:
                    raise ValueError('duplicate child metadata changes its identity or parent')
            else:
                if next_parent is None or identity != next_parent or identity in seen:
                    raise ValueError('inherited metadata is outside the ordered parent chain')
                seen.add(identity)
                if parent in seen:
                    raise ValueError('inherited metadata parent chain contains a loop')
                next_parent = parent
        elif kind == 'compacted' and started:
            latest['compacted'] = ordinal
        elif kind == 'token_usage_record':
            latest['record'] = (ordinal, payload)
        elif kind == 'turn_context':
            latest['context'] = (ordinal, payload)
        elif kind == 'event_msg' and payload.get('type') in ('task_started', 'task_complete', 'task_failed', 'task_aborted'):
            if payload['type'] == 'task_started':
                started = True
            latest[payload['type']] = (ordinal, payload)
    meta = latest.get('meta', {})
    source = meta.get('source', {})
    spawn = source.get('subagent', {}).get('thread_spawn', {}) if isinstance(source, dict) else {}
    if meta.get('id') != thread_id or spawn.get('agent_path') != agent_id:
        raise ValueError('rollout identity does not match this native subagent; stop dependent work')
    required = ('task_started', 'context')
    if any(key not in latest for key in required):
        raise ValueError('active-turn context telemetry is missing; stop dependent work')
    start = latest['task_started']
    context = latest['context']
    turn = start[1].get('turn_id')
    if not start[0] < context[0] or not turn or context[1].get('turn_id') != turn:
        raise ValueError('context telemetry is not from the current active turn')
    for key in ('task_complete', 'task_failed', 'task_aborted'):
        if key in latest and latest[key][0] > start[0]:
            raise ValueError('this turn is complete, failed or interrupted; only an active subagent can measure itself')
    # Compaction itself forbids further work; no numeric claim is needed.
    if 'compacted' in latest:
        return {'turn_id': turn, 'compacted': True}
    if 'record' not in latest or latest['record'][0] < context[0]:
        raise ValueError('current-turn usage is missing; stop dependent work')
    record = latest['record'][1]
    if record.get('turn_id') != turn or record.get('thread_id') != thread_id:
        raise ValueError('context telemetry belongs to another turn or agent')
    used, window = record.get('usage', {}).get('total_tokens'), start[1].get('model_context_window')
    if type(used) is not int or type(window) is not int or not 0 < used <= window:
        raise ValueError('last-call total_tokens or model_context_window is invalid')
    return {'used_tokens': used, 'model_context_window': window, 'turn_id': turn,
            'compacted': False}


def measure(project_root: Path, sessions_root: Path | None = None, session_path: Path | None = None) -> dict:
    root = sessions_root or Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
    path, binding = resolve_session(root, session_path)
    config = load_config(Path(__file__).resolve().parents[1] / 'assets/workflow.toml', project_root)
    result = inspect(path, binding)
    threshold = config['context_threshold_percent']
    reason = ('compaction' if result['compacted'] else 'threshold' if
              result['used_tokens'] * 100 >= result['model_context_window'] * threshold else None)
    result.update(binding, action='handover' if reason else 'continue', reason=reason,
                  threshold_percent=threshold, session_path=str(path.resolve()))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--sessions-root', type=Path, help='native local sessions directory; default CODEX_HOME/sessions')
    parser.add_argument('--session-path', type=Path, help='own session_path returned earlier; skips the session search')
    args = parser.parse_args()
    try:
        result = measure(args.project_root, args.sessions_root, args.session_path)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(json.dumps({'action':'blocked', 'diagnostic':str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='strict')
    raise SystemExit(main())
