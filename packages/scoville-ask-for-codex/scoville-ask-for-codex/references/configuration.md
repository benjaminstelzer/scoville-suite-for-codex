# Settings and helper inputs

Resolve locally with one complete command:

```text
python "<ask-skill-directory>/scripts/ask.py" --project-root "<absolute-project-root>"
```

Optional repeated `--adviser <configured-id>` selects only those advisers.
For one selected adviser, use `--model <id>` and `--effort <level>` for unsaved
overrides. For more complex settings, use a helper-generated or automatically
serialized UTF-8 JSON request; never hand-write transport JSON:

```text
python "<ask-skill-directory>/scripts/ask.py" --input-file "<request.json>"
```

The request object contains:

- `operation=resolve` to select the operation.
- `project_root` for the selected project.
- Optional `overrides` for unsaved settings.

The JSON response's `config.advisers` entries supply these settings directly:

- `id` identifies the adviser.
- `route` selects its transport.
- `model` supplies the `spawn_agent` model.
- `effort` supplies the `spawn_agent` reasoning_effort.

These are technical settings, not a dispatch prompt. Dispatch questions and adviser answers remain
plain text. A nonzero exit or ok:false stops the operation with its diagnostic.
Stdin JSON requests remain supported, including Ask Claude.

ask_settings.py, scoville_config.py and ask_claude.py are imported modules, not
separate commands. Use the bundled ask.py from this installed package.

Legacy ask.pin_threads booleans remain readable and are preserved when other
settings change, but have no effect. Native advisers are subagents without
sidebar chats. Use Scoville Setup for configuration changes.

The selected project root owns `.scoville/config.json`. Its `ask` section
overrides this Skill's defaults. Missing files or fields use those defaults.
Reads never create a file and never search parent directories.
Objects merge by field;
`advisers` replaces the entire list so an explicit selection never adds unwanted
advisers. Select named advisers with strings such as `["sol", "fable"]`, or use
objects with `id` and per-call overrides. A matching ID inherits its configured
preset. Custom IDs need `route` (`native` or `claude-cli`), exact `model` and
`effort`; `name` is optional. One, two and more advisers use the same structure.
Explicit named requests select only those presets. Read the actual config for
current defaults rather than inferring model or effort from a Skill name.

Shipped settings, generated from their canonical file:

```json
{
  "schema_version": 1,
  "advisers": ["astra"],
  "presets": {
    "astra": {"route": "native", "model": "gpt-6-astra", "effort": "high"},
    "sol": {"route": "native", "model": "gpt-5.6-sol", "effort": "high"},
    "claude": {"route": "claude-cli", "model": "claude-opus-5-5", "effort": "high"},
    "fable": {"route": "claude-cli", "model": "claude-fable-5-1", "effort": "medium"}
  },
  "claude": {
    "max_budget_usd": 10,
    "session_persistence": true,
    "customizations": false,
    "timeout_seconds": 3600,
    "web_tools": false
  }
}
```

Save only changed values, for example:
`{"ask":{"advisers":["sol","fable"],"presets":{"sol":{"effort":"medium"}}}}`.
Request overrides use the fields inside `ask`.

`resolve` accepts `project_root` and optional unsaved `overrides`. Pass the
selected project's absolute root. When omitted, `cwd` supplies the root, or
the process working directory if neither was supplied. `project_config` is
rejected with migration guidance. Keep settings unchanged during a run.
Display resolved settings when configuration is requested.

The Claude-only `prepare` request contains:

- `mode=review|consultation` to select the kind of advice.
- `question` for the actual request.
- `scope` for its boundary.
- `reference` for the consultation reference.
- `cwd` for an existing absolute working directory.
- `overrides` selecting only Claude advisers.

The response returns `entries[].request` for `operation=claude`. Use the helper commands
in [Claude operation](claude.md) for fresh requests and follow-ups.
