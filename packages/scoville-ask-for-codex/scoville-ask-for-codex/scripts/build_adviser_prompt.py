#!/usr/bin/env python3
"""Compose a read-only Ask assignment or direct collaboration.spawn_agent arguments."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
EFFORTS = ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra')


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--format', choices=('prompt', 'spawn'), default='prompt')
    parser.add_argument('--task-name', help='unique agent task name: lowercase letters, digits and underscores')
    parser.add_argument('--model')
    parser.add_argument('--effort', choices=EFFORTS)
    parser.add_argument('--adviser-id', required=True, help='resolved adviser ID from ask.py')
    parser.add_argument('--workspace-root', required=True, type=Path)
    parser.add_argument('--question-file', required=True, type=Path)
    parser.add_argument('--mode', required=True, choices=('review', 'consultation'))
    parser.add_argument('--scope', required=True)
    parser.add_argument('--reference', required=True)
    args = parser.parse_args()
    for name in ('scope', 'reference', 'adviser_id'):
        value = getattr(args, name)
        if not value.strip() or any(ord(c) < 32 for c in value):
            parser.error(f"--{name.replace('_', '-')} must be nonempty single-line text without control characters")
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', args.adviser_id):
        parser.error('--adviser-id must be a resolved lowercase adviser ID, for example astra')
    if not args.workspace_root.is_absolute() or not args.workspace_root.is_dir():
        parser.error('--workspace-root must be an existing absolute directory; pass the selected project root')
    if args.format == 'spawn':
        if not args.task_name or not re.fullmatch(r'[a-z0-9_]+', args.task_name):
            parser.error('--task-name is required for --format spawn; use a unique name such as ask_astra_1')
        if args.model is None:
            parser.error('--model is required for --format spawn; pass the resolved model ID such as gpt-6-astra')
        if not args.model.strip() or any(c.isspace() for c in args.model):
            parser.error(f'--model={args.model!r} must be a nonempty model ID without whitespace; pass the resolved identifier such as gpt-6-astra')
        if args.effort is None:
            parser.error('--effort is required for --format spawn; pass the resolved effort, for example high')
    elif any(value is not None for value in (args.task_name, args.model, args.effort)):
        parser.error('--task-name, --model and --effort require --format spawn; omit them for prompt output')
    try:
        question = args.question_file.read_text(encoding='utf-8')
        if not question.strip():
            parser.error('--question-file must contain the request and necessary evidence')
        rules = [(ROOT / 'references' / name).read_text(encoding='utf-8')
                 for name in ('adviser.md', 'native-delivery.md')]
    except (OSError, UnicodeError) as error:
        parser.error(f'cannot read required UTF-8 input: {error}; provide a readable --question-file and intact packaged references')
    prompt = ('\n\n'.join(rules)
              + f'\n\nmode: {args.mode}\nadviser_id: {args.adviser_id}'
              + f'\nworkspace_root: {args.workspace_root}'
              + f'\nconsultation_reference: {args.reference}\nscope: {args.scope}'
              + '\n\nInspect only the supplied scope in this workspace. Resolve relative evidence paths there.'
              + '\n\n## User request and evidence\n\n' + question)
    if args.format == 'spawn':
        print(json.dumps({'task_name': args.task_name, 'message': prompt,
                          'fork_turns': 'none', 'model': args.model,
                          'reasoning_effort': args.effort}, ensure_ascii=False))
    else:
        print(prompt)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
