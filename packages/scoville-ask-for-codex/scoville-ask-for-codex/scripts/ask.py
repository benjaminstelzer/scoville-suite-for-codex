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
    require(isinstance(value, str) and bool(value.strip()), f'{name} must be nonempty text; provide a non-blank string')
    return value


def resolve(request):
    config = resolve_settings(ROOT / 'config.default.json', request)
    advisers = config['advisers']
    for adviser in advisers:
        if adviser['route'] == 'claude-cli':
            require(ask_claude.MODEL_PATTERN.fullmatch(adviser['model']),
                    f"adviser {type(adviser['id']).__name__}.model must use letters, digits, dot, underscore, colon or hyphen for route=claude-cli")
            require(adviser['effort'] in ask_claude.EFFORT_LEVELS,
                    f"adviser {type(adviser['id']).__name__}.effort={type(adviser['effort']).__name__} is unsupported for route=claude-cli; choose one of {', '.join(ask_claude.EFFORT_LEVELS)}")
    return {'config': config}


def prepare(request):
    require(isinstance(request, dict), 'request must be a JSON object; provide operation, mode, question, scope and reference fields')
    mode = request.get('mode')
    require(mode in {'review', 'consultation'},
            f"request.mode={type(mode).__name__} is missing or unsupported; clarify ambiguous intent as a review or consultation, then use 'review' or 'consultation'")
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
            raise ValueError(f"adviser {type(adviser['id']).__name__}.route='native' cannot use prepare; use build_adviser_prompt.py and collaboration.spawn_agent for this native adviser or select a claude-cli adviser")
        else:
            entry['request'] = {'operation': 'claude', 'adviser': adviser, 'claude': settings['claude'],
                'prompt': prompt, 'reference': ref, 'scope': scope, 'cwd': request.get('cwd')}
        entries.append(entry)
    return {'mode': mode, 'entries': entries}


def claude(request):
    require(isinstance(request, dict), 'request must be a JSON object; provide operation, adviser, claude, cwd and prompt fields')
    missing = [key for key in ('adviser', 'claude') if key not in request]
    require(not missing, f'request is missing required fields {missing}; include adviser and claude settings from a prepared request')
    require(isinstance(request['adviser'], dict), 'request.adviser must be an object; use the adviser object from prepare output')
    require(isinstance(request['claude'], dict), 'request.claude must be an object; use the claude settings from prepare output')
    adviser, config = request['adviser'], request['claude']
    require(adviser.get('route') == 'claude-cli',
            f"request.adviser.route={type(adviser.get('route')).__name__} must be 'claude-cli' for this operation; provide a Claude CLI adviser")
    # Reuse configuration validation without reading unrelated native defaults.
    resolved = resolve({'overrides': {'advisers': [adviser], 'claude': config}})['config']
    config = resolved['claude']
    adviser = resolved['advisers'][0]
    cwd = Path(text(request.get('cwd'), 'cwd'))
    require(cwd.is_absolute() and cwd.is_dir(),
            f"request.cwd={type(str(cwd)).__name__} must be an existing absolute directory; pass the project's absolute path")
    resume = request.get('session_id')
    if resume is not None:
        text(resume, 'session_id')
    timeout = request.get('timeout_seconds', config['timeout_seconds'])
    require(type(timeout) in (int, float) and math.isfinite(timeout) and timeout > 0,
            f'request.timeout_seconds={type(timeout).__name__} must be a positive finite number; use a value such as 3600')
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
        require(not (args.input_file and (args.project_root or args.adviser or args.model or args.effort)),
                '--input-file cannot be combined with --project-root, --adviser, --model or --effort; choose one request input mode')
        if args.input_file:
            try:
                request = json.loads(args.input_file.read_text(encoding='utf-8'))
            except json.JSONDecodeError as error:
                raise ValueError(f'--input-file {args.input_file} has invalid JSON at line {error.lineno}, column {error.colno}; correct the syntax near {error.msg}') from error
        elif args.project_root:
            request = {'operation': 'resolve', 'project_root': str(args.project_root)}
            if args.adviser:
                request['overrides'] = {'advisers': args.adviser}
            if args.model or args.effort:
                require(args.adviser and len(args.adviser) == 1,
                        '--model and --effort require exactly one --adviser; pass one adviser id such as --adviser sol')
                adviser = {'id': args.adviser[0]}
                if args.model:
                    adviser['model'] = args.model
                if args.effort:
                    adviser['effort'] = args.effort
                request['overrides'] = {'advisers': [adviser]}
        else:
            require(not (args.adviser or args.model or args.effort),
                    '--adviser, --model and --effort require --project-root; provide --project-root PATH')
            try:
                request = json.load(sys.stdin)
            except json.JSONDecodeError as error:
                raise ValueError(f'stdin has invalid JSON at line {error.lineno}, column {error.colno}; correct the syntax near {error.msg}') from error
        require(isinstance(request, dict), 'request must be a JSON object; provide an operation field such as {"operation": "resolve"}')
        operation = request.get('operation')
        require(operation in OPERATIONS,
                f'request.operation={type(operation).__name__} is unsupported; choose one of {", ".join(sorted(OPERATIONS))}')
        result = OPERATIONS[operation](request)
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
