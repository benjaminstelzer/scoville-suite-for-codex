#!/usr/bin/env python3
"""Show or explicitly save the project's Scoville settings."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

from ask_settings import merge_config_layer, resolve_settings
from scoville_config import merge, read_config
from workflow_settings import load_config, read_thresholds

ROOT = Path(__file__).resolve().parents[1]


def read_patch() -> dict:
    example = '{"workflow": {"context": {"coordinator_percent": 40}}}'
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as error:
        raise ValueError('set expects a UTF-8 JSON object patch on stdin; '
                         f'encode the complete patch as UTF-8 JSON, e.g. {example}. '
                         f'Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}') from error
    except UnicodeError as error:
        raise ValueError('set expects a UTF-8 JSON object patch on stdin; '
                         f'encode the complete patch as UTF-8 JSON, e.g. {example}. Original error: {error}') from error


def effective(project_root: Path) -> dict:
    return {
        "ask": resolve_settings(ROOT / "assets/ask.default.json", {"project_root": project_root}),
        "workflow": load_config(ROOT / "assets/workflow.toml", project_root),
    }


def validate(project_root: Path) -> dict:
    values = effective(project_root)
    read_thresholds(ROOT / "assets/workflow.toml", project_root)
    return values


def validate_setup_choices(value: dict, path: str = "patch") -> None:
    for key, item in value.items():
        field = f"{path}.{key}"
        if key in {"effort", "reasoning"} and item not in ("low", "medium", "high", "xhigh"):
            raise ValueError(
                f"{field}={type(item).__name__} is unsupported by Setup; choose low, medium, high or xhigh, "
                "or edit .scoville/config.json manually when another level is required"
            )
        if isinstance(item, dict):
            validate_setup_choices(item, field)
        elif isinstance(item, list):
            for index, entry in enumerate(item):
                if isinstance(entry, dict):
                    validate_setup_choices(entry, f"{field}[{index}]")


def apply(project_root: Path, patch: dict) -> dict:
    if not isinstance(patch, dict):
        raise ValueError("patch must be a JSON object; for example {\"ask\": {\"claude\": {\"timeout_seconds\": 2400}}}")
    if not patch:
        raise ValueError("patch must contain an ask and/or workflow change; provide a nonempty object")
    unknown = sorted(set(patch) - {"ask", "workflow"})
    if unknown:
        raise ValueError(f"patch has unsupported top-level fields {unknown}; use ask and/or workflow")
    for key in ("ask", "workflow"):
        if key in patch and not isinstance(patch[key], dict):
            raise ValueError(f"patch.{key} must be an object; provide nested settings as a JSON object")
    if "workflow" in patch:
        unknown = sorted(set(patch["workflow"]) - {"manager", "execute", "review", "context", "pin_threads"})
        if unknown:
            raise ValueError(f"patch.workflow has unsupported fields {unknown}; Setup accepts manager, execute, review and context")
    if "pin_threads" in patch.get("ask", {}):
        raise ValueError("patch.ask.pin_threads is obsolete: native Ask advisers are subagents without sidebar chats; omit this field and use ask.advisers or ask.presets for adviser settings")
    if "pin_threads" in patch.get("workflow", {}):
        raise ValueError("patch.workflow.pin_threads is obsolete: Workflow roles are subagents without sidebar chats; omit this field and use workflow.execute, workflow.review or workflow.context for active settings")
    validate_setup_choices(patch)
    current = read_config(project_root)
    proposed = merge(current, patch)
    if "ask" in patch:
        proposed["ask"] = merge_config_layer(current.get("ask", {}), patch["ask"])
    # Reuse the consumers against the proposed file before touching the project.
    with tempfile.TemporaryDirectory(prefix="scoville-setup-") as temporary:
        candidate = Path(temporary)
        (candidate / ".scoville").mkdir()
        (candidate / ".scoville/config.json").write_text(
            json.dumps(proposed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        values = validate(candidate)
    path = project_root / ".scoville/config.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(proposed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return values


def main() -> int:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("show", "set"))
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        values = (apply(args.project_root, read_patch())
                  if args.operation == "set" else validate(args.project_root))
        print(json.dumps({"ok": True, "saved": args.operation == "set",
                          "file": str(args.project_root / ".scoville/config.json"),
                          "effective": values}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "diagnostic": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
