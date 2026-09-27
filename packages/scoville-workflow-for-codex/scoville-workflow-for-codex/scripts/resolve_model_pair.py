#!/usr/bin/env python3
"""Resolve Workflow task model and thinking from the installed route table."""
from __future__ import annotations

import argparse
import json
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required for Workflow helpers")
import tomllib
from pathlib import Path


from workflow_settings import ROUTES, EFFORTS, load_config


def resolve(config: dict, role: str, route: str | None = None,
            override_model: str | None = None, override_reasoning: str | None = None) -> dict:
    if role not in {"executor", "reviewer"} or route not in ROUTES:
        raise ValueError(f"role={role!r}, route={route!r}: use --role executor or reviewer and --route with one of {', '.join(ROUTES)}; example: --role executor --route medium")
    pair = dict(config["review" if role == "reviewer" else "execute"][route])
    if override_model is not None:
        pair["model"] = override_model
    if override_reasoning is not None:
        pair["reasoning"] = override_reasoning
    if not pair["model"] or pair["reasoning"] not in EFFORTS:
        raise ValueError(f"model={pair['model']!r}, reasoning={pair['reasoning']!r}: --override-model must be nonempty and --override-reasoning must be one of {', '.join(sorted(EFFORTS))}; correct the override or omit it to use the configured pair")
    return {"model": pair["model"], "thinking": pair["reasoning"], "route": route}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=("executor", "reviewer"), required=True)
    parser.add_argument("--route", choices=ROUTES)
    parser.add_argument("--override-model")
    parser.add_argument("--override-reasoning")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        config = load_config(Path(__file__).resolve().parents[1] / "assets" / "workflow.toml", args.project_root)
        result = resolve(config, args.role, args.route, args.override_model,
                         args.override_reasoning)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        print(json.dumps({"valid": False, "diagnostic": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"valid": True, **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    raise SystemExit(main())
