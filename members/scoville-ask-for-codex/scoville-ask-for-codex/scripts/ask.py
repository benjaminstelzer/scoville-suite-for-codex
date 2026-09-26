#!/usr/bin/env python3
"""Resolve advisers locally; prepare and execute only explicit Claude CLI requests."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import sys

import ask_claude
from ask_settings import resolve_settings

ROOT = Path(__file__).resolve().parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()), f'{name} must be nonempty text')
    return value


def resolve(request):
    config = resolve_settings(ROOT / 'config.default.json', request)
    advisers = config['advisers']
    for adviser in advisers:
        if adviser['route'] == 'claude-cli':
            require(ask_claude.MODEL_PATTERN.fullmatch(adviser['model']), 'invalid Claude model')
            require(adviser['effort'] in ask_claude.EFFORT_LEVELS, 'unsupported Claude CLI effort')
    return {'config': config}


def prepare(request):
    mode = request.get('mode')
    require(mode in {'review', 'consultation'}, 'clarify ambiguous intent before preparing advisers')
    question = text(request.get('question'), 'question')
    scope = text(request.get('scope'), 'scope')
    reference = text(request.get('reference'), 'reference')
    settings = resolve(request)['config']
    role = (ROOT / 'references/adviser.md').read_text(encoding='utf-8')
    prompt = role + '\n\n' + json.dumps({'mode': mode, 'scope': scope, 'question': question}, ensure_ascii=False)
    entries = []
    for adviser in settings['advisers']:
        ref = reference + ':' + adviser['id']
        entry = {'adviser': adviser, 'reference': ref, 'scope': scope, 'context_mode': 'fresh'}
        if adviser['route'] == 'native':
            raise ValueError('Native advisers use create_thread directly; prepare is only for Claude CLI')
        else:
            entry['request'] = {'operation': 'claude', 'adviser': adviser, 'claude': settings['claude'],
                'prompt': prompt, 'reference': ref, 'scope': scope, 'cwd': request.get('cwd'), 'authorized': request.get('creation_authorized')}
        entries.append(entry)
    return {'mode': mode, 'entries': entries}


def claude(request):
    require(request.get('authorized') is True, 'Claude consultation requires authorization')
    adviser, config = request['adviser'], request['claude']
    require(adviser.get('route') == 'claude-cli', 'Claude route required')
    # Reuse configuration validation without reading unrelated native defaults.
    resolved = resolve({'overrides': {'advisers': [adviser], 'claude': config}})['config']
    config = resolved['claude']
    adviser = resolved['advisers'][0]
    cwd = Path(text(request.get('cwd'), 'cwd'))
    require(cwd.is_absolute() and cwd.is_dir(), 'cwd must be an existing absolute directory')
    resume = request.get('session_id')
    if resume is not None:
        text(resume, 'session_id')
    timeout = request.get('timeout_seconds', config['timeout_seconds'])
    require(type(timeout) in (int, float) and math.isfinite(timeout) and timeout > 0, 'invalid Claude deadline')
    args = argparse.Namespace(model=adviser['model'], effort=adviser['effort'],
        max_budget_usd=config['max_budget_usd'], fresh=False, persistent=False,
        resume=resume, continue_session=False, session_name=None,
        session_persistence_default=config['session_persistence'], customizations_enabled=config['customizations'], web_tools=config['web_tools'])
    command = ask_claude.build_command(args, ask_claude.resolve_claude_command())
    result = ask_claude.run_command(command, cwd, text(request.get('prompt'), 'prompt'), timeout)
    if result.returncode != 0:
        detail = result.stderr.strip()
        if not detail and result.stdout.strip():
            detail = ask_claude.claude_error_details(ask_claude.parse_claude_result(result.stdout)) or 'no error details in response'
        raise ValueError(f'Claude exited {result.returncode}: {detail or "no error details"}')
    payload = ask_claude.parse_claude_result(result.stdout)
    require(ask_claude.claude_error_details(payload) is None, 'Claude failed: ' + str(ask_claude.claude_error_details(payload)))
    answer = text(payload.get('result'), 'Claude answer')
    session = payload.get('session_id')
    return {'reference': request.get('reference'), 'scope': request.get('scope'), 'answer': answer,
        'session_id': session, 'continuation_available': bool(session) and config['session_persistence'],
        'context_mode': 'continued' if resume else 'fresh',
        'requested_model': adviser['model'], 'requested_effort': adviser['effort'],
        'reported_model': payload.get('model'), 'reported_effort': payload.get('effort'),
        'permission_denials': payload.get('permission_denials') or []}


OPERATIONS = {'resolve': resolve, 'prepare': prepare, 'claude': claude}


def main(argv=()):
    request = {}
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--input-file', type=Path)
        parser.add_argument('--project-root', type=Path)
        parser.add_argument('--adviser', action='append')
        parser.add_argument('--model')
        parser.add_argument('--effort')
        args = parser.parse_args(argv)
        require(not (args.input_file and (args.project_root or args.adviser or args.model or args.effort)), 'input-file cannot be combined with resolve flags')
        if args.input_file:
            request = json.loads(args.input_file.read_text(encoding='utf-8'))
        elif args.project_root:
            request = {'operation': 'resolve', 'project_root': str(args.project_root)}
            if args.adviser:
                request['overrides'] = {'advisers': args.adviser}
            if args.model or args.effort:
                require(args.adviser and len(args.adviser) == 1, 'model/effort overrides require exactly one adviser')
                adviser = {'id': args.adviser[0]}
                if args.model:
                    adviser['model'] = args.model
                if args.effort:
                    adviser['effort'] = args.effort
                request['overrides'] = {'advisers': [adviser]}
        else:
            require(not (args.adviser or args.model or args.effort), 'resolve flags require project-root')
            request = json.load(sys.stdin)
        require(isinstance(request, dict) and request.get('operation') in OPERATIONS, 'unknown operation')
        result = OPERATIONS[request['operation']](request)
        print(json.dumps({'ok': True, **result}, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        failure = {'ok': False, 'error': str(error)}
        if isinstance(error, ask_claude.ClaudeTimeout):
            failure['code'] = 'claude_timeout'
        print(json.dumps(failure, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    ask_claude.configure_standard_streams()
    raise SystemExit(main(sys.argv[1:]))
