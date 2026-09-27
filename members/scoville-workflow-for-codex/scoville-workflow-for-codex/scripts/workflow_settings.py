"""Workflow defaults and project overrides for Workflow and suite Setup."""
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required for Workflow helpers")
from pathlib import Path
import tomllib
from scoville_config import merge, section as config_section


ROUTES = ("ultra_low", "low", "medium", "high", "ultra_high")
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}


def load_config(path: Path, project_root: Path | str | None = None) -> dict:
    with path.open("rb") as stream:
        config = merge(tomllib.load(stream), config_section('workflow', project_root))
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise ValueError(f"workflow.schema_version={type(config.get('schema_version')).__name__} is unsupported; use integer 1 for this configuration format")
    if set(config) - {"schema_version", "context", "execute", "review"}:
        raise ValueError(f"unknown workflow configuration keys: {sorted(set(config) - {'schema_version', 'context', 'execute', 'review'})}; use only schema_version, context, execute and review")
    for section in ("execute", "review"):
        table = config.get(section)
        if not isinstance(table, dict) or set(table) != set(ROUTES):
            raise ValueError(f"{section} must contain exactly the five routes: {', '.join(ROUTES)}; supply an object with those keys, or omit the project override to retain defaults")
        for route, pair in table.items():
            if not isinstance(pair, dict) or set(pair) != {"model", "reasoning"}:
                raise ValueError(f"invalid {section}.{route} pair: {type(pair).__name__}; use an object with exactly model and reasoning, e.g. model='gpt-6-astra', reasoning='medium'")
            if (not isinstance(pair["model"], str) or not pair["model"]
                    or not isinstance(pair["reasoning"], str) or pair["reasoning"] not in EFFORTS):
                raise ValueError(f"invalid {section}.{route} values: {type(pair).__name__}; model must be a nonempty string and reasoning one of {', '.join(sorted(EFFORTS))}")
    return config



def read_thresholds(path: Path, project_root: Path | str | None = None) -> dict:
    with path.open("rb") as stream:
        config = merge(tomllib.load(stream), config_section('workflow', project_root))
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise ValueError(f"workflow.schema_version={type(config.get('schema_version')).__name__} is unsupported; use integer 1 for this configuration format")
    thresholds = config.get("context")
    if not isinstance(thresholds, dict) or set(thresholds) != {"coordinator_percent", "worker_percent"}:
        raise ValueError(f"context={type(thresholds).__name__} requires exactly coordinator_percent and worker_percent; supply both integer percentages or omit context to keep defaults")
    if any(type(value) is not int or not 1 <= value <= 99 for value in thresholds.values()):
        invalid = {key: value for key, value in thresholds.items() if type(value) is not int or not 1 <= value <= 99}
        raise ValueError(f"context percentages must be integers from 1 through 99; invalid fields: {list(invalid)}. Replace only those values with integers, without percent signs or quotes")
    return thresholds
