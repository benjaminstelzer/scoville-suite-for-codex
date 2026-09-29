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

The object contains operation=resolve, project_root and optional overrides.
The JSON response config.advisers supplies id, route, model and effort directly.
These are technical settings, not a dispatch prompt. Use model and effort as
create_thread model and thinking. Dispatch questions and adviser answers remain
plain text. No model/list call or output repair is required. A nonzero exit or
ok:false stops the operation with its diagnostic. Existing stdin JSON requests
remain supported, including the unchanged Ask Claude interface.

ask_settings.py, scoville_config.py and ask_claude.py are imported modules, not
separate commands. Use the bundled ask.py from this installed package.

config.pin_threads controls pinning new native adviser chats. Default true;
set ask.pin_threads=false through Setup to disable it. Preserve existing pins.

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
  "pin_threads": true,
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
Request overrides use the fields inside `ask`. Retained follow-up
settings take precedence over new defaults unless explicitly changed.

`resolve` accepts `project_root` and optional unsaved `overrides`. Pass the
selected project's absolute root. When omitted, `cwd` supplies the root, or
the process working directory if neither was supplied. `project_config` is
rejected with migration guidance. Keep settings unchanged during a run.
Native availability is checked by create_thread on the actual host, not by a
separate CLI catalog. Display resolved settings when configuration is requested.

Claude-only prepare takes mode=review|consultation, question, scope, reference,
and an absolute cwd, with overrides selecting only Claude
advisers. It returns entries[].request unchanged for operation=claude. The Claude
adapter, deadlines and follow-up session rules are unchanged. No separate
authorization field is required: the explicit Ask request commissions the call.
Native prepare and followup operations are removed; use native tools directly.
