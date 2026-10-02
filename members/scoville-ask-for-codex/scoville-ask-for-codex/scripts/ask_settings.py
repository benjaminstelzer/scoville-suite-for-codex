"""Ask configuration validation shared by Ask and suite Setup."""
from pathlib import Path
import json
import math
import re
from scoville_config import merge, section

REASONING_LEVELS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")
MODEL_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")


def diagnostic_value(value):
    """Show small scalar settings, never dump nested configuration or evidence."""
    if isinstance(value, (dict, list)):
        return type(value).__name__
    result = repr(value)
    return result if len(result) <= 80 else result[:77] + '...'


def validate_claude_pair(settings, field=lambda key: key):
    if settings['route'] == 'claude-cli':
        require(MODEL_PATTERN.fullmatch(settings['model']),
                f"{field('model')}={diagnostic_value(settings['model'])} must use letters, digits, dot, underscore, colon or hyphen for route=claude-cli; correct the model identifier")
        require(settings['effort'] in EFFORT_LEVELS,
                f"{field('effort')}={diagnostic_value(settings['effort'])} is unsupported for route=claude-cli; choose one of {', '.join(EFFORT_LEVELS)}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()),
            f'{name}={diagnostic_value(value)} must be nonempty text; provide a non-blank string')
    return value


def model(value, name):
    text(value, name)
    require(not any(c.isspace() for c in value),
            f'{name}={diagnostic_value(value)} must be a model ID without whitespace; pass the exact model identifier')


def merge_config_layer(base, overlay):
    result = merge(base, overlay)
    # A newer preset also overrides inline fields inherited from older layers.
    # Inline advisers supplied in this same layer retain their local precedence.
    if 'advisers' not in overlay and isinstance(overlay.get('presets'), dict):
        advisers = result.get('advisers')
        if isinstance(advisers, list):
            for index, adviser in enumerate(advisers):
                if isinstance(adviser, dict):
                    identifier = adviser.get('id')
                    preset = overlay['presets'].get(identifier) if isinstance(identifier, str) else None
                    if isinstance(preset, dict):
                        advisers[index] = merge(adviser, preset)
    return result

def resolve_settings(defaults: Path, request: dict):
    require(isinstance(request, dict), 'request must be a JSON object; provide fields in an object such as {"overrides": {}}')
    config = json.loads(defaults.read_text(encoding='utf-8'))
    require('project_config' not in request,
            'request.project_config is unsupported; use request.project_root for .scoville/config.json or request.overrides for this request')
    root_field = 'project_root' if 'project_root' in request else 'cwd'
    root_value = request.get(root_field)
    require(root_value is None or isinstance(root_value, (str, Path)),
            f'request.{root_field}={diagnostic_value(root_value)} must be a directory path string; pass the selected project path')
    if isinstance(root_value, str):
        text(root_value, f'request.{root_field}')
    project_root = Path(root_value) if root_value is not None else Path.cwd()
    project = section('ask', project_root)
    overrides = request.get('overrides', {})
    require(isinstance(overrides, dict), 'request.overrides must be an object; supply settings by field')
    layers = [(str(defaults), config),
              (str(project_root / '.scoville/config.json') + ': ask', project),
              ('request.overrides', overrides)]

    def field(path):
        parts = path.replace('[', '.').replace(']', '').split('.')
        for label, layer in reversed(layers):
            value = layer
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                    value = value[int(part)]
                else:
                    break
            else:
                return f'{label}.{path}'
        return path

    def adviser_field(index, identifier, key):
        # A later preset can replace an inline field from an older adviser list.
        for _, layer in reversed(layers):
            if 'advisers' in layer:
                item = layer['advisers'][index]
                if isinstance(item, dict) and key in item:
                    return field(f'advisers[{index}].{key}')
                break
            preset = layer.get('presets', {}).get(identifier, {})
            if isinstance(preset, dict) and key in preset:
                return field(f'presets.{identifier}.{key}')
        if key in config['presets'].get(identifier, {}):
            return field(f'presets.{identifier}.{key}')
        return field(f'advisers[{index}]') + '.' + key

    config = merge_config_layer(config, project)
    config = merge_config_layer(config, overrides)
    unknown = sorted(set(config) - {'schema_version', 'advisers', 'presets', 'claude', 'pin_threads'})
    require(not unknown, f'configuration fields {[field(key) for key in unknown]} are unknown; remove them or use only schema_version, advisers, presets, claude and pin_threads')
    require('pin_threads' not in config or type(config['pin_threads']) is bool,
            f"{field('pin_threads')}={diagnostic_value(config.get('pin_threads'))} must be a JSON boolean; use true or false")
    require(type(config.get('schema_version')) is int and config['schema_version'] == 1,
            f"{field('schema_version')}={diagnostic_value(config.get('schema_version'))} is unsupported; set it to integer 1")
    advisers = config.get('advisers')
    require(isinstance(advisers, list) and advisers, f"{field('advisers')}={diagnostic_value(advisers)} must be a nonempty array; select at least one adviser")
    presets = config.get('presets')
    require(isinstance(presets, dict), f"{field('presets')}={diagnostic_value(presets)} must be an object mapping preset ids to settings; use {{}} when no presets are defined")
    for identifier, preset in presets.items():
        preset_path = field(f'presets.{identifier}')
        preset_field = lambda key: field(f'presets.{identifier}.{key}')
        require(re.fullmatch(r'[a-z0-9][a-z0-9-]*', identifier),
                f'{preset_path} is not a valid preset id; use lowercase letters, digits and hyphens, starting with a letter or digit')
        require(isinstance(preset, dict), f'{preset_path} must be an object with name, route, model and effort fields')
        unknown = sorted(set(preset) - {'name', 'route', 'model', 'effort'})
        require(not unknown, f'{preset_path} has unknown fields {unknown}; use only name, route, model and effort')
        require(preset.get('route') in ('native', 'claude-cli'),
                f"{preset_field('route')}={diagnostic_value(preset.get('route'))} is unsupported; choose 'native' or 'claude-cli'")
        model(preset.get('model'), preset_field('model'))
        require(isinstance(preset.get('effort'), str) and preset['effort'] in REASONING_LEVELS,
                f"{preset_field('effort')}={diagnostic_value(preset.get('effort'))} is invalid; choose one of {', '.join(sorted(REASONING_LEVELS))}")
        validate_claude_pair(preset, preset_field)
        if 'name' in preset:
            text(preset['name'], preset_field('name'))
    expanded = []
    for index, item in enumerate(advisers):
        if isinstance(item, str):
            require(item in presets, f'{field(f"advisers[{index}]")}={diagnostic_value(item)} has no matching preset; choose one of {", ".join(presets)} or add a complete preset')
            item = {'id': item}
        require(isinstance(item, dict), f'{field(f"advisers[{index}]")}={diagnostic_value(item)} must be a preset id string or an adviser object; use {{"id": "sol"}}')
        identifier = text(item.get('id'), field(f'advisers[{index}].id'))
        preset = presets.get(identifier, {})
        require(isinstance(preset, dict) and set(preset) <= {'name', 'route', 'model', 'effort'},
                f"{field(f'advisers[{index}].id')}={diagnostic_value(item.get('id'))} references a preset with unsupported fields; correct presets.{item.get('id')}")
        expanded.append(merge(preset, item))
    advisers = config['advisers'] = expanded
    claude = config.get('claude')
    require(isinstance(claude, dict), f"{field('claude')}={diagnostic_value(claude)} must be an object; provide its Claude CLI settings in an object")
    seen = set()
    for adviser in advisers:
        require(isinstance(adviser, dict), f'advisers[{len(seen)}] must be an object; use fields id, route, model and effort')
        unknown = sorted(set(adviser) - {'id', 'name', 'route', 'model', 'effort'})
        require(not unknown, f'{field(f"advisers[{len(seen)}]")} has unknown fields {unknown}; remove them or use only id, name, route, model and effort')
        index = len(seen)
        identifier = text(adviser.get('id'), field(f'advisers[{index}].id'))
        require(re.fullmatch(r'[a-z0-9][a-z0-9-]*', identifier) and identifier not in seen,
                f'{field(f"advisers[{index}].id")}={diagnostic_value(identifier)} is invalid or duplicated; use a unique lowercase id such as sol')
        seen.add(identifier)
        selected_field = lambda key: adviser_field(index, identifier, key) + f' (adviser {identifier})'
        require(adviser.get('route') in ('native', 'claude-cli'),
                f"{selected_field('route')}={diagnostic_value(adviser.get('route'))} is unsupported; choose 'native' or 'claude-cli'")
        model(adviser.get('model'), selected_field('model'))
        require(isinstance(adviser.get('effort'), str) and adviser['effort'] in REASONING_LEVELS,
                f"{selected_field('effort')}={diagnostic_value(adviser.get('effort'))} is invalid; choose one of {', '.join(sorted(REASONING_LEVELS))}")
        validate_claude_pair(adviser, selected_field)
        if 'name' in adviser:
            text(adviser['name'], selected_field('name'))
    claude = config.get('claude')
    required_claude = {'max_budget_usd', 'session_persistence', 'customizations', 'timeout_seconds', 'web_tools'}
    missing = sorted(required_claude - set(claude))
    unknown = sorted(set(claude) - required_claude)
    require(not missing and not unknown,
            f"{field('claude')} settings fields mismatch; missing={missing}, unknown={unknown}; provide exactly {sorted(required_claude)}")
    deadline = claude['timeout_seconds']
    require(type(deadline) in (int, float) and math.isfinite(deadline) and deadline > 0,
            f"{field('claude.timeout_seconds')}={diagnostic_value(deadline)} must be a positive finite number of seconds; use a value such as 3600")
    budget = claude['max_budget_usd']
    require(type(budget) in (int, float) and math.isfinite(budget) and budget > 0,
            f"{field('claude.max_budget_usd')}={diagnostic_value(budget)} must be a positive finite USD amount; use a value such as 5")
    for key in ('session_persistence', 'customizations', 'web_tools'):
        require(type(claude[key]) is bool,
                f"{field(f'claude.{key}')}={diagnostic_value(claude[key])} must be a JSON boolean; use true or false")
    return config
