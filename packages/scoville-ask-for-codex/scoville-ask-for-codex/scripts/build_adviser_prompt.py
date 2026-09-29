#!/usr/bin/env python3
"""Compose a native Ask assignment from its packaged instructions."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from uuid import UUID
from native_task_arguments import add_creation_options, creation_arguments, single_line, validate_creation_options


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    add_creation_options(parser, project_name=False)
    parser.add_argument('--caller-title')
    parser.add_argument('--adviser-id', help='resolved adviser ID from ask.py resolve, used as the short title label')
    parser.add_argument("--question-file", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("review", "consultation"))
    parser.add_argument("--scope", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--caller-thread-id", default=os.environ.get("CODEX_THREAD_ID"), help='optional caller identity for provenance, not a callback address')
    args = parser.parse_args()
    try:
        validate_creation_options(args)
        if args.format == 'create':
            single_line(args.caller_title, '--caller-title')
            single_line(args.adviser_id, '--adviser-id')
    except ValueError as error:
        parser.error(str(error))
    try:
        caller = str(UUID(args.caller_thread_id)) if args.caller_thread_id else None
    except ValueError:
        parser.error("CODEX_THREAD_ID or --caller-thread-id must contain the calling chat's UUID; omit it if unavailable")
    for name in ("scope", "reference"):
        value = getattr(args, name)
        if not value.strip() or "\n" in value or "\r" in value:
            parser.error(f"--{name} must be nonempty single-line text")
    try:
        question = args.question_file.read_text(encoding="utf-8")
        if not question.strip():
            parser.error("--question-file must contain the request and necessary evidence")
        rules = [
            (ROOT / "references" / name).read_text(encoding="utf-8")
            for name in ("adviser.md", "native-delivery.md")
        ]
    except (OSError, UnicodeError) as error:
        parser.error(f"cannot read required UTF-8 input: {error}")
    prompt = ("\n\n".join(rules)
          + f"\n\nmode: {args.mode}" + (f"\ncalling_thread_id: {caller}" if caller else "")
          + f"\nconsultation_reference: {args.reference}\nscope: {args.scope}"
          + "\n\n## User request and evidence\n\n" + question)
    try:
        if args.format == 'create':
            title = f'SC-ASK-{args.adviser_id.upper()}: {single_line(args.caller_title, "caller title")}'
            print(json.dumps(creation_arguments(prompt, title, args.project_id, args.model, args.thinking), ensure_ascii=False))
        else:
            print(prompt)
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
