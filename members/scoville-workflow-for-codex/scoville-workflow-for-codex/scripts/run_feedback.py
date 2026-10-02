#!/usr/bin/env python3
"""Render changed work and maintain only user-relevant Workflow run issues."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from inspect_native_context import configure_utf8
from native_task_arguments import single_line

CLEAN = 'No issues occurred during this run.\n'
KINDS = {'question': 'User question', 'pause': 'Paused for user request', 'problem': 'Needs user review'}
NAME = re.compile(r'workflow-run-\d{8}T\d{6}Z-[a-f0-9]{32}\.md')
ISSUE_ID = re.compile(r'[A-Za-z0-9_-]{1,80}')
STATUS_LABELS = {'working': 'Working on', 'decision': 'Decision needed',
                 'blocked': 'Blocked', 'paused': 'Paused', 'completed': 'Completed'}
STATUS_CONTROLS = {'working': 'WORKING_ON', 'decision': 'NEEDS_USER_DECISION',
                   'blocked': 'BLOCKED', 'paused': 'STOPPED', 'completed': 'COMPLETED'}


def is_redirect(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def report_directory(project_root: Path) -> Path:
    root = project_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('--project-root must be an existing project directory')
    folder = root / '.scoville'
    if is_redirect(folder):
        raise ValueError('project .scoville must be a direct directory, not a redirected path')
    if folder.exists() and not folder.is_dir():
        raise ValueError('project .scoville must be a directory; move the conflicting file before retrying')
    return folder


def report_path(path: Path, project_root: Path | None = None) -> Path:
    if not path.is_absolute() or not NAME.fullmatch(path.name):
        raise ValueError('--report-file must be the absolute workflow-run-...md path returned by create')
    if is_redirect(path):
        raise ValueError('--report-file must not redirect to another file')
    folder = report_directory(project_root or path.parent.parent)
    if path.parent != folder or not path.is_file():
        raise ValueError('--report-file must be an existing run Markdown file directly in this project .scoville directory')
    return path


def create_report(project_root: Path) -> dict:
    folder = report_directory(project_root)
    folder.mkdir(exist_ok=True)
    name = 'workflow-run-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex + '.md'
    path = folder / name
    with path.open('x', encoding='utf-8', newline='\n'):
        pass
    return {'report_file': str(path)}


def quote(text: str) -> str:
    if not text.strip():
        raise ValueError('--text-file must contain the actual nonempty question, issue or clarification')
    return '\n'.join('> ' + line for line in text.rstrip().splitlines())


def issue_bounds(text: str, issue_id: str) -> tuple[int, int] | None:
    if not ISSUE_ID.fullmatch(issue_id):
        raise ValueError('--issue-id must contain 1-80 letters, digits, underscores or hyphens')
    pattern = rf'^<!-- scoville-issue: {re.escape(issue_id)} -->\n.*?^<!-- /scoville-issue: {re.escape(issue_id)} -->\n?'
    matches = list(re.finditer(pattern, text, re.M | re.S))
    if len(matches) > 1:
        raise ValueError('--report-file contains duplicate issue markers; resolve the duplicate without discarding the issue')
    if not matches:
        return None
    return matches[0].span()


def save(path: Path, before: str, after: str) -> None:
    """One manager owns report writes; preserve a detected concurrent edit."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=path.parent, prefix='.workflow-report-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(after)
        if path.read_text(encoding='utf-8') != before:
            raise ValueError('--report-file changed during this write; reread it and reconcile the intended entry before retrying')
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def add_issue(path: Path, kind: str, location: str, text: str, issue_id: str | None = None) -> dict:
    path = report_path(path)
    location = single_line(location, '--location, e.g. PLAN-0025 / W-001/step-2 or Startup')
    body = quote(text)
    issue_id = issue_id or uuid4().hex
    before = path.read_text(encoding='utf-8')
    bounds = issue_bounds(before, issue_id)
    block = (f'<!-- scoville-issue: {issue_id} -->\n'
             f'## {location} · {KINDS[kind]}\n\nStatus: Open\n\n{body}\n'
             f'<!-- /scoville-issue: {issue_id} -->\n')
    if before == CLEAN:
        raise ValueError('--report-file is a completed clean run; create a new run instead of adding later work')
    if bounds:
        existing = before[bounds[0]:bounds[1]]
        original = existing.split('\n### Resolution\n', 1)[0].replace('Status: Resolved', 'Status: Open', 1)
        if original.rstrip().removesuffix(f'<!-- /scoville-issue: {issue_id} -->').rstrip() != block.rstrip().removesuffix(f'<!-- /scoville-issue: {issue_id} -->').rstrip():
            raise ValueError('--issue-id already belongs to a different issue; reuse it only for the identical entry or choose a new ID')
        return {'report_file': str(path), 'issue_id': issue_id, 'changed': False}
    after = before.rstrip() + ('\n\n' if before.strip() else '') + block
    save(path, before, after)
    return {'report_file': str(path), 'issue_id': issue_id, 'changed': True}


def resolve_issue(path: Path, issue_id: str, text: str) -> dict:
    path = report_path(path)
    body = quote(text)
    before = path.read_text(encoding='utf-8')
    bounds = issue_bounds(before, issue_id)
    if not bounds:
        raise ValueError('--issue-id is absent from this report; use the ID returned by add for this run')
    block = before[bounds[0]:bounds[1]]
    resolution = '\n### Resolution\n\n' + body + '\n'
    if resolution in block:
        return {'report_file': str(path), 'issue_id': issue_id, 'changed': False}
    if 'Status: Open\n' not in block and 'Status: Resolved\n' not in block:
        raise ValueError('--report-file issue has no valid Open/Resolved status; inspect the edited entry before resolving it')
    updated = block.replace('Status: Open\n', 'Status: Resolved\n', 1)
    updated = updated.replace(f'<!-- /scoville-issue: {issue_id} -->', resolution + f'<!-- /scoville-issue: {issue_id} -->', 1)
    save(path, before, before[:bounds[0]] + updated + before[bounds[1]:])
    return {'report_file': str(path), 'issue_id': issue_id, 'changed': True}


def read_report(path: Path) -> dict:
    path = report_path(path)
    text = path.read_text(encoding='utf-8')
    display = re.sub(r'^<!-- /?scoville-issue: [A-Za-z0-9_-]{1,80} -->\n?', '', text, flags=re.M)
    return {'report_file': str(path), 'text': text, 'display_text': display}


def finish_report(path: Path) -> dict:
    path = report_path(path)
    before = path.read_text(encoding='utf-8')
    if not before.strip():
        save(path, before, CLEAN)
    return read_report(path)


def validate_location(plan: str, point: str) -> None:
    if not re.fullmatch(r'PLAN-\d{4}', plan):
        raise ValueError('--plan must be the actual PLAN-NNNN ID, e.g. PLAN-0025')
    if not re.fullmatch(r'W-\d{3}(?:/step-[1-9]\d*|/steps-[1-9]\d*-[1-9]\d*)?', point):
        raise ValueError('--point must be W-NNN, W-NNN/step-N or W-NNN/steps-N-M')
    if '/steps-' in point:
        first, last = map(int, point.split('/steps-')[1].split('-'))
        if first >= last:
            raise ValueError('--point Step range must be ascending and contain at least two Steps, e.g. W-001/steps-1-3')


def status(kind: str, project: str, plan: str | None, point: str | None, body: str) -> dict:
    project = single_line(project, '--project (the actual project name)')
    if plan is None and point is None:
        if kind in ('working', 'completed'):
            raise ValueError('--plan and --point are required for working/completed; use the actual PLAN-NNNN and W-NNN/step-N')
        location = 'Startup'
    elif plan is None or point is None:
        raise ValueError('--plan and --point must be supplied together, e.g. --plan PLAN-0025 --point W-001/step-2; omit both only before startup location is known')
    else:
        validate_location(plan, point)
        location = f'{plan} → {point}'
    if not body.strip():
        raise ValueError('--text or --text-file must supply the actual question, reason, waiting work or completion scope as nonempty text')
    # Project names are literal text inside a Markdown status heading.
    escaped = re.sub(r'([\\`*_\[\]<>])', r'\\\1', project)
    text = f'**{STATUS_LABELS[kind]}: {escaped} → {location}**\n\n{body.strip()}'
    return {'text': text, 'message': f'{STATUS_CONTROLS[kind]}\n{text}'}


def progress(project: str, plan: str, point: str, previous_key: str | None = None) -> dict:
    project = single_line(project, '--project (the actual project name)')
    validate_location(plan, point)
    if previous_key is not None and not re.fullmatch('[a-f0-9]{64}', previous_key):
        raise ValueError('--previous-key must be the exact key returned by the preceding progress call')
    key = hashlib.sha256(json.dumps([project, plan, point], ensure_ascii=False).encode('utf-8')).hexdigest()
    changed = previous_key != key
    escaped = re.sub(r'([\\`*_\[\]<>])', r'\\\1', project)
    text = f'**Working on: {escaped} → {plan} → {point}**' if changed else ''
    return {'key': key, 'changed': changed, 'text': text,
            'message': f'WORKING_ON {key}\n{text}' if changed else ''}


def recorded_progress(project_root: Path, selector: Path) -> tuple[str, str]:
    """Project saved position only. Never select or start work."""
    if not selector.is_file():
        raise ValueError(f'Plan position helper missing: {selector}; install the complete matching Workflow package')
    result = subprocess.run([sys.executable, '-B', str(selector), '--root', str(project_root),
                             '--position', '--format', 'json'],
                            capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise ValueError('Plan position failed; correct its diagnostic before progress: ' + result.stdout + result.stderr)
    position = json.loads(result.stdout)
    if position.get('plan_status') != 'active' or position.get('work_status') != 'in_progress':
        raise ValueError('Plan position has no started current Work Item; save and validate Status: in_progress before progress --project-root PATH')
    units = position.get('current_units', [])
    if position.get('untracked_steps'):
        raise ValueError('Plan position contains unmarked Steps with unknown start state; establish their observed status and save/validate before progress --project-root PATH')
    if len(units) == 1:
        point = units[0]
    elif not units and position.get('reason') == 'whole_work_item':
        point = position['work_item']
    else:
        raise ValueError(f'Plan position needs exactly one saved in_progress Step/group; found {len(units)}: {units}. Record the actually started consecutive group, validate, then rerun progress --project-root PATH; do not start work from this projection')
    return position['plan'], point


def main() -> int:
    configure_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('create').add_argument('--project-root', required=True, type=Path)
    for command in ('add', 'resolve', 'read', 'finish'):
        child = sub.add_parser(command)
        child.add_argument('--report-file', required=True, type=Path)
        if command in ('add', 'resolve'):
            child.add_argument('--text-file', required=True, type=Path, help='UTF-8 actual issue or resolution, never routine status')
            child.add_argument('--issue-id', required=command == 'resolve')
        if command == 'add':
            child.add_argument('--kind', choices=KINDS, required=True)
            child.add_argument('--location', required=True)
        if command == 'finish':
            child.add_argument('--completed', action='store_true', required=True, help='only after requested scope passes acceptance and closure')
    child = sub.add_parser('progress')
    child.add_argument('--project', required=True)
    source = child.add_mutually_exclusive_group(required=True)
    source.add_argument('--project-root', type=Path, help='manager only: derive progress from saved Plan position')
    source.add_argument('--plan', help='explicit display-only Plan ID; requires --point')
    child.add_argument('--point')
    child.add_argument('--selector', type=Path, default=Path(__file__).with_name('select_context.py'))
    child.add_argument('--scope-file', type=Path, help='legacy argument, ignored; progress displays only project and Plan point')
    child.add_argument('--previous-key')
    child = sub.add_parser('status', help='render one status heading and its unchanged explanatory text')
    child.add_argument('--kind', choices=('decision', 'blocked', 'paused', 'completed'), required=True)
    child.add_argument('--project', required=True)
    child.add_argument('--plan')
    child.add_argument('--point')
    text_input = child.add_mutually_exclusive_group(required=True)
    text_input.add_argument('--text-file', type=Path, help='UTF-8 message body')
    text_input.add_argument('--text', help='plain message body; usable without file writes')
    args = parser.parse_args()
    try:
        if args.command == 'create':
            result = create_report(args.project_root)
        elif args.command == 'progress':
            if args.project_root:
                if args.point:
                    raise ValueError('--point cannot override saved progress; omit it with --project-root')
                plan, point = recorded_progress(args.project_root, args.selector)
            else:
                if not args.point:
                    raise ValueError('--plan requires --point W-NNN/step-N; managers use --project-root PATH instead')
                plan, point = args.plan, args.point
            result = progress(args.project, plan, point, args.previous_key)
        elif args.command == 'status':
            body = args.text_file.read_text(encoding='utf-8') if args.text_file is not None else args.text
            result = status(args.kind, args.project, args.plan, args.point, body)
        elif args.command == 'add':
            result = add_issue(args.report_file, args.kind, args.location, args.text_file.read_text(encoding='utf-8'), args.issue_id)
        elif args.command == 'resolve':
            result = resolve_issue(args.report_file, args.issue_id, args.text_file.read_text(encoding='utf-8'))
        else:
            result = (finish_report if args.command == 'finish' else read_report)(args.report_file)
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
