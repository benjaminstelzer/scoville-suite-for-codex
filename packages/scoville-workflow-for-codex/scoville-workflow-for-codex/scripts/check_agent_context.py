#!/usr/bin/env python3
"""Measure a bound, completed native agent before its next assignment."""
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


def bound_identity(path: Path, agent_id: str, parent: str) -> str | None:
    """Return the session ID when this rollout header binds the agent to this Manager."""
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
    if not isinstance(identity, str) or not NATIVE_ID.fullmatch(identity) or not isinstance(source, dict):
        return None
    subagent = source.get('subagent')
    spawn = subagent.get('thread_spawn') if isinstance(subagent, dict) else None
    if isinstance(spawn, dict) and spawn.get('agent_path') == agent_id and spawn.get('parent_thread_id') == parent:
        return identity
    return None


def resolve_session(agent_id: str, root: Path, session_path: Path | None = None) -> tuple[Path, str, str]:
    parent = os.environ.get('CODEX_THREAD_ID', '')
    if not NATIVE_ID.fullmatch(parent):
        raise ValueError('CODEX_THREAD_ID must identify this Manager session; use the native Manager environment')
    if not isinstance(agent_id, str) or not agent_id.strip() or any(c in agent_id for c in '\r\n'):
        raise ValueError('--agent-id must be the exact retained native agent handle')
    if session_path is not None:
        identity = bound_identity(session_path, agent_id, parent) if session_path.is_file() else None
        if identity is None:
            raise ValueError(f'--session-path "{session_path}" is missing or does not bind --agent-id to this Manager; '
                             'rerun once without --session-path to resolve the session again; dispatch nothing')
        return session_path, identity, parent
    if not root.is_dir():
        raise ValueError(f'native sessions directory is missing: {root}; verify CODEX_HOME or --sessions-root')
    matches = []

    def enumeration_error(error):
        raise error

    for directory, _, files in os.walk(root, onerror=enumeration_error):
        for name in files:
            if name.endswith('.jsonl'):
                path = Path(directory) / name
                identity = bound_identity(path, agent_id, parent)
                if identity is not None:
                    matches.append((path, identity))
    if len(matches) != 1:
        raise ValueError(f'exact agent session is missing or ambiguous ({len(matches)} matches); verify the retained handle and native sessions directory; dispatch nothing')
    path, identity = matches[0]
    return path, identity, parent


def inspect(path: Path, agent_id: str, thread_id: str) -> dict:
    latest = {}
    last_ordinal = -1
    next_parent = None
    seen = set()
    started = False
    for line in path.read_text(encoding='utf-8').splitlines():
        event = json.loads(line)
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
                if ordinal != 0 or identity != thread_id or spawn.get('agent_path') != agent_id or not parent or parent == thread_id:
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
        elif kind == 'compacted':
            latest['compacted'] = ordinal
        elif kind == 'token_usage_record':
            latest['record'] = (ordinal, payload)
        elif kind == 'turn_context':
            latest['context'] = (ordinal, payload)
        elif payload.get('type') in ('task_started', 'task_complete', 'task_failed', 'task_aborted', 'token_count'):
            if payload['type'] == 'task_started':
                started = True
            latest[payload['type']] = (ordinal, payload)
    meta = latest.get('meta', {})
    source = meta.get('source', {})
    spawn = source.get('subagent', {}).get('thread_spawn', {}) if isinstance(source, dict) else {}
    if meta.get('id') != thread_id or spawn.get('agent_path') != agent_id:
        raise ValueError('rollout identity does not match the resolved native session and --agent-id; dispatch nothing')
    required = ('task_started', 'task_complete', 'context', 'record', 'token_count')
    if any(key not in latest for key in required):
        raise ValueError('completed-turn context telemetry is missing; establish agent completion and a valid native measurement')
    start, finish = latest['task_started'], latest['task_complete']
    context, record, sample = latest['context'], latest['record'], latest['token_count']
    if not start[0] < context[0] <= record[0] < sample[0] < finish[0]:
        raise ValueError('agent has no measured completed current turn; do not reuse or replace an active or uncertain writer')
    if latest.get('compacted', -1) >= record[0]:
        raise ValueError('context telemetry precedes compaction; obtain a new valid measurement')
    for key in ('task_failed', 'task_aborted'):
        if key in latest and latest[key][0] > start[0]:
            raise ValueError('latest assignment failed or was interrupted; reconcile its effects before dispatch')
    turn = start[1].get('turn_id')
    if not turn or any(p.get('turn_id') != turn for p in (context[1], record[1], finish[1])) or record[1].get('thread_id') != thread_id:
        raise ValueError('context telemetry belongs to another turn or agent')
    info = sample[1].get('info', {})
    usage = info.get('last_token_usage')
    if not isinstance(usage, dict) or usage != record[1].get('usage'):
        raise ValueError('token sample does not match the identity-bearing usage record')
    used, window = usage.get('total_tokens'), info.get('model_context_window')
    if type(used) is not int or type(window) is not int or not 0 < used <= window:
        raise ValueError('last-call total_tokens or model_context_window is invalid')
    model, effort = context[1].get('model'), context[1].get('effort')
    if not isinstance(model, str) or not model.strip() or not isinstance(effort, str) or not effort.strip():
        raise ValueError('completed-turn model and reasoning telemetry is missing')
    return {'used_tokens': used, 'model_context_window': window, 'turn_id': turn,
            'model': model, 'reasoning_effort': effort}


def measure(agent_id: str, project_root: Path, sessions_root: Path | None = None, session_path: Path | None = None) -> dict:
    root = sessions_root or Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
    path, thread_id, parent = resolve_session(agent_id, root, session_path)
    config = load_config(Path(__file__).resolve().parents[1] / 'assets/workflow.toml', project_root)
    result = inspect(path, agent_id, thread_id)
    threshold = config['context_threshold_percent']
    result.update(action='reuse' if result['used_tokens'] * 100 < result['model_context_window'] * threshold else 'spawn',
                  threshold_percent=threshold, agent_id=agent_id, thread_id=thread_id, parent_thread_id=parent,
                  session_path=str(path.resolve()))
    if result['action'] == 'spawn':
        result['replacement_of'] = agent_id
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent-id', required=True, help='exact retained canonical agent handle')
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--sessions-root', type=Path, help='native local sessions directory; default CODEX_HOME/sessions')
    parser.add_argument('--session-path', type=Path, help='session_path returned by an earlier measurement of this agent; skips the session search')
    args = parser.parse_args()
    try:
        result = measure(args.agent_id, args.project_root, args.sessions_root, args.session_path)
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
