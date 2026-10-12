"""Workflow defaults and project overrides for Workflow and suite Setup."""
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required for Workflow helpers")
from pathlib import Path
import tomllib
from scoville_config import merge, section as config_section


ROUTES = ("ultra_low", "low", "medium", "high", "ultra_high")
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
LEGACY_KEYS = ("context", "manager", "pin_threads")
CONFIG_KEYS = {"schema_version", "execute", "review", "explore", "context_threshold_percent"}


def validate_pair(pair: dict, field: str) -> None:
    if not isinstance(pair, dict) or set(pair) != {"model", "reasoning"}:
        raise ValueError(f"invalid {field} pair: {type(pair).__name__}; use an object with exactly model and reasoning, e.g. model='gpt-6.1-sol', reasoning='medium'")
    if (not isinstance(pair["model"], str) or not pair["model"].strip()
            or '\n' in pair["model"] or '\r' in pair["model"]
            or not isinstance(pair["reasoning"], str) or pair["reasoning"] not in EFFORTS):
        raise ValueError(f"invalid {field} values: {type(pair).__name__}; model must be a nonempty single-line string and reasoning one of {', '.join(sorted(EFFORTS))}")


def load_config(path: Path, project_root: Path | str | None = None) -> dict:
    with path.open("rb") as stream:
        config = merge(tomllib.load(stream), config_section('workflow', project_root))
    for key in LEGACY_KEYS:
        config.pop(key, None)
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise ValueError(f"workflow.schema_version={type(config.get('schema_version')).__name__} is unsupported; use integer 1 for this configuration format")
    if set(config) - CONFIG_KEYS:
        raise ValueError(f"unknown workflow configuration keys: {sorted(set(config) - CONFIG_KEYS)}; use schema_version, execute, review, explore and context_threshold_percent")
    threshold = config.get("context_threshold_percent")
    if type(threshold) is not int or not 1 <= threshold <= 100:
        raise ValueError("workflow.context_threshold_percent must be an integer from 1 to 100; e.g. 50 for all subagents")
    # Resolve after execute overrides so unspecified Explorer fields follow them.
    config["explore"] = merge(config.get("execute", {}), config.get("explore", {}))
    for section in ("execute", "review", "explore"):
        table = config.get(section)
        if not isinstance(table, dict) or set(table) != set(ROUTES):
            raise ValueError(f"{section} must contain exactly the five routes: {', '.join(ROUTES)}; supply an object with those keys, or omit the project override to retain defaults")
        for route, pair in table.items():
            validate_pair(pair, f'{section}.{route}')
    return config
