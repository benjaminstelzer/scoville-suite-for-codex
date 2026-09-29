"""Ask configuration validation shared by Ask and suite Setup."""
from pathlib import Path
import json
import math
import re
from scoville_config import merge, section

REASONING_LEVELS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")
MODEL_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")


def validate_claude_pair(settings):
    if settings['route'] == 'claude-cli':
        require(MODEL_PATTERN.fullmatch(settings['model']),
                'model must use letters, digits, dot, underscore, colon or hyphen for route=claude-cli; correct the model identifier')
        require(settings['effort'] in EFFORT_LEVELS,
                f"effort={type(settings['effort']).__name__} is unsupported for route=claude-cli; choose one of {', '.join(EFFORT_LEVELS)}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()),
            f'{name} must be nonempty text; provide a non-blank string')
    return value


def merge_config_layer(base, overlay):
    result = merge(base, overlay)
    # A newer preset also overrides inline fields inherited from older layers.
    # Inline advisers supplied in this same layer retain their local precedence.
    if 'advisers' not in overlay and isinstance(overlay.get('presets'), dict):
        advisers = result.get('advisers')
        if isinstance(advisers, list):
            for index, adviser in enumerate(advisers):
                if isinstance(adviser, dict):
                    preset = overlay['presets'].get(adviser.get('id'))
                    if isinstance(preset, dict):
                        advisers[index] = merge(adviser, preset)
    return result

def resolve_settings(defaults: Path, request: dict):
    require(isinstance(request, dict), 'request must be a JSON object; provide fields in an object such as {"overrides": {}}')
    config = json.loads(defaults.read_text(encoding='utf-8'))
    require('project_config' not in request,
            'request.project_config is unsupported; use request.project_root for .scoville/config.json or request.overrides for this request')
    config = merge_config_layer(config, section('ask', request.get('project_root', request.get('cwd'))))
    config = merge_config_layer(config, request.get('overrides', {}))
    unknown = sorted(set(config) - {'schema_version', 'advisers', 'presets', 'claude', 'pin_threads'})
    require(not unknown, f'configuration keys {unknown} are unknown; use only schema_version, advisers, presets, claude and pin_threads')
    require(type(config.get('pin_threads')) is bool,
            'ask.pin_threads must be a JSON boolean; use true or false')
    require(type(config.get('schema_version')) is int and config['schema_version'] == 1,
            f"schema_version={type(config.get('schema_version')).__name__} is unsupported; set it to integer 1")
    advisers = config.get('advisers')
    require(isinstance(advisers, list) and advisers, 'advisers must be a nonempty array; select at least one adviser')
    presets = config.get('presets')
    require(isinstance(presets, dict), 'presets must be an object mapping preset ids to settings; use {} when no presets are defined')
    for identifier, preset in presets.items():
        preset_path = f'presets.{identifier}'
        require(re.fullmatch(r'[a-z0-9][a-z0-9-]*', identifier),
                f'{preset_path} is not a valid preset id; use lowercase letters, digits and hyphens, starting with a letter or digit')
        require(isinstance(preset, dict), f'{preset_path} must be an object with name, route, model and effort fields')
        unknown = sorted(set(preset) - {'name', 'route', 'model', 'effort'})
        require(not unknown, f'{preset_path} has unknown fields {unknown}; use only name, route, model and effort')
        require(preset.get('route') in {'native', 'claude-cli'},
                f"{preset_path}.route={type(preset.get('route')).__name__} is unsupported; choose 'native' or 'claude-cli'")
        text(preset.get('model'), f'{preset_path}.model')
        require(preset.get('effort') in REASONING_LEVELS,
                f"{preset_path}.effort={type(preset.get('effort')).__name__} is invalid; choose one of {', '.join(sorted(REASONING_LEVELS))}")
        validate_claude_pair(preset)
        if 'name' in preset:
            text(preset['name'], 'preset name')
    expanded = []
    for item in advisers:
        if isinstance(item, str):
            require(item in presets, f'advisers entry {type(item).__name__} has no matching presets.{item}; add that preset or provide a complete adviser object')
            item = {'id': item}
        require(isinstance(item, dict), f'advisers entry {type(item).__name__} must be a preset id string or an adviser object; use {{"id": "sol"}}')
        preset = presets.get(item.get('id'), {})
        require(isinstance(preset, dict) and set(preset) <= {'name', 'route', 'model', 'effort'},
                f"advisers[].id={type(item.get('id')).__name__} references a preset with unsupported fields; correct presets.{item.get('id')}")
        expanded.append(merge(preset, item))
    advisers = config['advisers'] = expanded
    claude = config.get('claude')
    require(isinstance(claude, dict), 'claude must be an object; provide its Claude CLI settings in an object')
    seen = set()
    for adviser in advisers:
        require(isinstance(adviser, dict), f'advisers[{len(seen)}] must be an object; use fields id, route, model and effort')
        unknown = sorted(set(adviser) - {'id', 'name', 'route', 'model', 'effort'})
        require(not unknown, f'advisers[{len(seen)}] has unknown fields {unknown}; use only id, name, route, model and effort')
        identifier = text(adviser.get('id'), f'advisers[{len(seen)}].id')
        require(re.fullmatch(r'[a-z0-9][a-z0-9-]*', identifier) and identifier not in seen,
                f'advisers[{len(seen)}].id={type(identifier).__name__} is invalid or duplicated; use a unique lowercase id such as sol')
        seen.add(identifier)
        require(adviser.get('route') in {'native', 'claude-cli'},
                f"advisers[{len(seen)-1}].route={type(adviser.get('route')).__name__} is unsupported; choose 'native' or 'claude-cli'")
        text(adviser.get('model'), f'advisers[{len(seen)-1}].model')
        require(adviser.get('effort') in REASONING_LEVELS,
                f"advisers[{len(seen)-1}].effort={type(adviser.get('effort')).__name__} is invalid; choose one of {', '.join(sorted(REASONING_LEVELS))}")
        validate_claude_pair(adviser)
        if 'name' in adviser:
            text(adviser['name'], 'adviser name')
    claude = config.get('claude')
    required_claude = {'max_budget_usd', 'session_persistence', 'customizations', 'timeout_seconds', 'web_tools'}
    missing = sorted(required_claude - set(claude))
    unknown = sorted(set(claude) - required_claude)
    require(not missing and not unknown,
            f'claude settings fields mismatch; missing={missing}, unknown={unknown}; provide exactly {sorted(required_claude)}')
    deadline = claude['timeout_seconds']
    require(type(deadline) in (int, float) and math.isfinite(deadline) and deadline > 0,
            f'claude.timeout_seconds={type(deadline).__name__} must be a positive finite number of seconds; use a value such as 3600')
    budget = claude['max_budget_usd']
    require(type(budget) in (int, float) and math.isfinite(budget) and budget > 0,
            f'claude.max_budget_usd={type(budget).__name__} must be a positive finite USD amount; use a value such as 5')
    for key in ('session_persistence', 'customizations', 'web_tools'):
        require(type(claude[key]) is bool,
                f'claude.{key}={type(claude[key]).__name__} must be a JSON boolean; use true or false')
    return config
