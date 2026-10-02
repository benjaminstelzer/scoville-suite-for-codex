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
from ask_settings import diagnostic_value, resolve_settings

ROOT = Path(__file__).resolve().parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()), f'{name} must be nonempty text; provide a non-blank string')
    return value


def resolve(request):
    return {'config': resolve_settings(ROOT / 'config.default.json', request)}


def prepare(request):
    require(isinstance(request, dict), 'request must be a JSON object; provide operation, mode, question, scope and reference fields')
    mode = request.get('mode')
    require(mode in ('review', 'consultation'),
            f"request.mode={diagnostic_value(mode)} is missing or unsupported; clarify ambiguous intent as a review or consultation, then use 'review' or 'consultation'")
    question = text(request.get('question'), 'question')
    scope = text(request.get('scope'), 'scope')
    reference = text(request.get('reference'), 'reference')
    cwd = Path(text(request.get('cwd'), 'request.cwd'))
    require(cwd.is_absolute() and cwd.is_dir(),
            f"request.cwd={str(cwd)!r} must be an existing absolute directory; pass the project's absolute path")
    settings = resolve(request)['config']
    role = (ROOT / 'references/adviser.md').read_text(encoding='utf-8')
    entries = []
    for adviser in settings['advisers']:
        ref = reference + ':' + adviser['id']
        entry = {'adviser': adviser, 'reference': ref, 'scope': scope, 'context_mode': 'fresh'}
        if adviser['route'] == 'native':
            raise ValueError(f"adviser {adviser['id']!r}.route='native' cannot use prepare; use build_adviser_prompt.py and collaboration.spawn_agent for this native adviser or select a claude-cli adviser")
        else:
            prompt = (role + f'\n\nmode: {mode}\nadviser_id: {adviser["id"]}'
                      + f'\nworkspace_root: {cwd}\nconsultation_reference: {ref}\nscope: {scope}'
                      + '\n\nInspect only the supplied scope in this workspace. Resolve relative evidence paths there.'
                      + '\n\n## User request and evidence\n\n' + question)
            entry['request'] = {'operation': 'claude', 'adviser': adviser, 'claude': settings['claude'],
                'prompt': prompt, 'reference': ref, 'scope': scope, 'cwd': str(cwd)}
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
            f"request.adviser.route={diagnostic_value(adviser.get('route'))} must be 'claude-cli' for this operation; provide a Claude CLI adviser")
    # Reuse configuration validation without reading unrelated native defaults.
    try:
        resolved = resolve({'overrides': {'advisers': [adviser], 'claude': config}})['config']
    except ValueError as error:
        raise ValueError(str(error).replace('request.overrides.advisers[0]', 'request.adviser')
                         .replace('request.overrides.claude', 'request.claude')) from error
    config = resolved['claude']
    adviser = resolved['advisers'][0]
    cwd = Path(text(request.get('cwd'), 'cwd'))
    require(cwd.is_absolute() and cwd.is_dir(),
            f"request.cwd={str(cwd)!r} must be an existing absolute directory; pass the project's absolute path")
    resume = request.get('session_id')
    if resume is not None:
        text(resume, 'session_id')
    timeout = request.get('timeout_seconds', config['timeout_seconds'])
    require(type(timeout) in (int, float) and math.isfinite(timeout) and timeout > 0,
            f'request.timeout_seconds={diagnostic_value(timeout)} must be a positive finite number; use a value such as 3600')
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


def read_utf8(path, argument):
    try:
        return path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        raise ValueError(f'{argument} {path}: {error}; provide a readable UTF-8 file at this path') from error


def read_request(path, argument):
    try:
        return json.loads(read_utf8(path, argument))
    except json.JSONDecodeError as error:
        raise ValueError(f'{argument} {path} has invalid JSON at line {error.lineno}, column {error.colno}; correct the syntax near {error.msg}') from error


def prepare_file(args):
    """Generate one directly executable Claude request, retaining follow-up settings."""
    for name in ('mode', 'scope', 'reference', 'output_file'):
        require(getattr(args, name) is not None,
                f'--question-file requires --{name.replace("_", "-")}; see --help for the complete preparation command')
    require(args.output_file.resolve() != args.question_file.resolve(),
            '--output-file must differ from --question-file; preserve the question in its own UTF-8 file')
    previous = None
    if args.resume_request:
        require(args.project_root is None and args.adviser is None,
                '--resume-request retains its workspace and adviser; omit --project-root and --adviser')
        text(args.session_id, '--session-id for --resume-request')
        previous = read_request(args.resume_request, '--resume-request')
        require(isinstance(previous, dict) and previous.get('operation') == 'claude',
                '--resume-request must contain a generated operation=claude request; use the retained request file')
        for name in ('adviser', 'claude'):
            require(isinstance(previous.get(name), dict),
                    f'--resume-request {args.resume_request}: {name} must be an object; use the intact retained request')
        require(previous['claude'].get('session_persistence') is True,
                '--resume-request has session_persistence=false; continuation is unavailable, request a fresh consultation')
        adviser = dict(previous['adviser'])
        claude_config = dict(previous['claude'])
        cwd = previous.get('cwd')
    else:
        require(args.session_id is None, '--session-id requires --resume-request; use the retained request and exact session ID')
        require(args.project_root is not None and args.adviser and len(args.adviser) == 1,
                '--question-file requires --project-root PATH and exactly one --adviser ID, for example --adviser claude')
        adviser = {'id': args.adviser[0]}
        claude_config = {}
        cwd = str(args.project_root)
    for key in ('model', 'effort'):
        if getattr(args, key) is not None:
            adviser[key] = getattr(args, key)
    if previous is not None and 'timeout_seconds' in previous:
        claude_config['timeout_seconds'] = previous['timeout_seconds']
    for key in ('timeout_seconds', 'max_budget_usd'):
        if getattr(args, key) is not None:
            claude_config[key] = getattr(args, key)
    if args.web_tools is not None:
        claude_config['web_tools'] = args.web_tools == 'true'
    question = read_utf8(args.question_file, '--question-file')
    try:
        prepared = prepare({'mode': args.mode, 'scope': args.scope, 'reference': args.reference,
                            'question': question, 'cwd': cwd,
                            'overrides': {'advisers': [adviser], 'claude': claude_config}})['entries'][0]['request']
    except ValueError as error:
        # Translate only values supplied through this CLI; keep config-source diagnostics intact.
        fields = {'request.cwd': '--project-root' if previous is None else f'--resume-request {args.resume_request}: cwd',
                  'question': '--question-file', 'scope': '--scope', 'reference': '--reference', 'request.mode': '--mode'}
        for key in ('model', 'effort', 'timeout_seconds', 'max_budget_usd', 'web_tools'):
            if getattr(args, key) is not None:
                owner = 'advisers[0]' if key in ('model', 'effort') else 'claude'
                fields[f'request.overrides.{owner}.{key}'] = '--' + key.replace('_', '-')
        message = str(error)
        for field, flag in fields.items():
            if message.startswith(field):
                message = flag + message[len(field):]
                break
        raise ValueError(message) from error
    if previous is not None:
        prepared['session_id'] = args.session_id
    try:
        args.output_file.write_text(json.dumps(prepared, ensure_ascii=False) + '\n', encoding='utf-8')
    except OSError as error:
        raise ValueError(f'--output-file {args.output_file}: {error}; choose a writable file in an existing directory') from error
    return {'request_file': str(args.output_file), 'reference': prepared['reference'],
            'scope': prepared['scope'], 'adviser': prepared['adviser'], 'claude': prepared['claude']}


def main(argv=()):
    request = {}
    try:
        parser = argparse.ArgumentParser(description=__doc__, epilog=(
            'Prepare: --project-root PATH --adviser claude --question-file question.txt '
            '--mode review --scope SCOPE --reference REF --output-file request.json. '
            'Execute: --input-file request.json. Follow-up: replace --project-root/--adviser '
            'with --resume-request previous.json --session-id EXACT_ID.'))
        parser.add_argument('--input-file', type=Path)
        parser.add_argument('--project-root', type=Path)
        parser.add_argument('--adviser', action='append')
        parser.add_argument('--model')
        parser.add_argument('--effort')
        parser.add_argument('--question-file', type=Path)
        parser.add_argument('--mode', choices=('review', 'consultation'))
        parser.add_argument('--scope')
        parser.add_argument('--reference')
        parser.add_argument('--output-file', type=Path)
        parser.add_argument('--resume-request', type=Path)
        parser.add_argument('--session-id')
        parser.add_argument('--web-tools', choices=('true', 'false'))
        parser.add_argument('--timeout-seconds', type=float)
        parser.add_argument('--max-budget-usd', type=float)
        args = parser.parse_args(argv)
        options = {key: value for key, value in vars(args).items() if key != 'input_file' and value is not None}
        require(not (args.input_file and options),
                '--input-file cannot be combined with other flags; execute the generated request unchanged or prepare a new request first')
        if args.question_file:
            result = prepare_file(args)
            print(json.dumps({'ok': True, **result}, ensure_ascii=False))
            return 0
        preparation_flags = ('mode', 'scope', 'reference', 'output_file', 'resume_request', 'session_id',
                             'web_tools', 'timeout_seconds', 'max_budget_usd')
        supplied = ['--' + name.replace('_', '-') for name in preparation_flags if getattr(args, name) is not None]
        require(not supplied, f'{", ".join(supplied)} requires --question-file; see --help for preparation and follow-up examples')
        if args.input_file:
            request = read_request(args.input_file, '--input-file')
        elif args.project_root:
            request = {'operation': 'resolve', 'project_root': str(args.project_root)}
            if args.adviser:
                request['overrides'] = {'advisers': args.adviser}
            if args.model is not None or args.effort is not None:
                require(args.adviser and len(args.adviser) == 1,
                        '--model and --effort require exactly one --adviser; pass one adviser id such as --adviser sol')
                adviser = {'id': args.adviser[0]}
                if args.model is not None:
                    adviser['model'] = args.model
                if args.effort is not None:
                    adviser['effort'] = args.effort
                request['overrides'] = {'advisers': [adviser]}
        else:
            require(not (args.adviser or args.model is not None or args.effort is not None),
                    '--adviser, --model and --effort require --project-root; provide --project-root PATH')
            try:
                request = json.load(sys.stdin)
            except json.JSONDecodeError as error:
                raise ValueError(f'stdin has invalid JSON at line {error.lineno}, column {error.colno}; correct the syntax near {error.msg}') from error
        require(isinstance(request, dict), 'request must be a JSON object; provide an operation field such as {"operation": "resolve"}')
        operation = request.get('operation')
        require(isinstance(operation, str) and operation in OPERATIONS,
                f'request.operation={diagnostic_value(operation)} is unsupported; choose one of {", ".join(sorted(OPERATIONS))}')
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
