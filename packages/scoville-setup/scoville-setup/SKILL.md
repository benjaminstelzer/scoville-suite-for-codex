---
name: scoville-setup
description: Show or change the selected project's Scoville Ask and Workflow settings. Use for saved models, effort, Claude limits and context rollover thresholds. Excludes running workflows, installations, updates and monitoring.
compatibility: "Codex Suite with Python 3.11+, bundled configuration helpers and filesystem access to the selected project. Configuration changes are local; this Skill starts no host tasks."
---

# Scoville Setup

All Skills included in this suite must be installed and enabled. Use the
applicable owner without checking sibling availability. Load only instructions
needed for the task. Explicit invocation gates and user exclusions still apply.

Manage `.scoville/config.json` in the selected project root. Its values override
the imported Skill defaults per field. There is no personal settings layer or
parent-directory search. This Skill is supplied only in the Codex Suite.

When explaining settings or reporting changes, read and apply the
[shared writing rules](references/writing.md).

Use the project's known absolute root. Ask for the root only if it is unknown.
Reuse an already verified interpreter meeting this Skill's Python 3.11+
requirement. Otherwise check `py -3`
on Windows or `python3` elsewhere; try `python` if needed. Choose it locally,
without asking the user. Verify its version before the first helper operation.
Use that executable wherever examples say `python` or `<verified-python>`,
including Python commands after `--run --`.
Report a missing runtime only when no suitable installed interpreter is found.

Run the bundled helper with Python 3.11+:

```text
python "<setup-skill-directory>/scripts/setup.py" show --project-root "<project-root>"
```

Show reads and validates settings without creating a file. Explain the relevant
effective values returned by the helper. `saved: false` means this operation
performed no save; it does not mean the project has no saved overrides.
Defaults are imported from Ask's
[defaults](assets/ask.default.json) and Workflow's [defaults](assets/workflow.toml).
Never maintain another copy of their values in these instructions.

For a requested one-time Ask override, read Scoville Ask's
`<ask-skill-directory>/references/configuration.md` and use its read-only
settings resolution with the selected adviser and requested model or effort.
Keep unrequested saved values. Report the actual returned values; a promise
to use them later is not resolution. This reads settings without starting an
adviser or saving configuration.

For an explicit request to save settings, pass only the requested fields as a
JSON object on stdin to the command below. Generate that object with a serializer
(such as Python `json.dumps` or PowerShell `ConvertTo-Json -Depth 10 -Compress`); do not hand-write
JSON text. Use UTF-8 for stdin. In PowerShell, set
`$OutputEncoding = [System.Text.UTF8Encoding]::new($false)` before piping the
serialized object so non-ASCII values reach the helper unchanged.
The successful JSON response contains the saved
effective settings and can be read directly:

```text
python "<setup-skill-directory>/scripts/setup.py" set --project-root "<project-root>"
```

The object contains `ask`, `workflow` or both sections. The `ask` section supports:

- `advisers` for the selected advisers.
- `presets` for model, effort, route and optional name.
- `claude` for `max_budget_usd`, `session_persistence`, `customizations`,
  `timeout_seconds` and `web_tools`.

The `workflow` section supports:

- `manager` for the manager's model and reasoning level.
- `execute` and `review` for each route's model and reasoning level.
- `context.coordinator_percent` for the manager threshold.
- `context.worker_percent` for the child threshold.

`workflow.manager` sets the manager independently of the runner. Missing fields use the bundled
defaults. A one-time manager pair overrides saved settings for that run;
successors retain the launched pair.
Legacy `ask.pin_threads` and `workflow.pin_threads` remain readable but have
no effect: native advisers and Workflow roles are subagents without sidebar rows.
Explain this when showing those fields; do not offer to save pin settings.
Preserve them when saving other choices. Claude CLI has no sidebar row.
Percentages are integers from 1 through 99. An adviser list replaces the old
selection. Ask or Workflow checks model and effort availability when used.

The helper reuses consumer validation, preserves unrelated saved fields and
writes only after validation succeeds. Report a failed operation's diagnostic
without claiming it was saved. Do not silently substitute values.

Change settings between runs. A one-time model choice stays in the request or
Plan Step unless the user explicitly asks to save it. Do not start advisers,
Workflow agents, an installer, an update, a monitor or a second configuration system.

Offer and save only `low`, `medium`, `high` and `xhigh` reasoning levels.
Other supported levels require a manual entry in `.scoville/config.json`.
Show and preserve such entries when changing unrelated settings; never silently
map them to another level. Actual model support still determines execution.

## Runtime helpers

Use the bundled helpers for their operations. Read their invocation instructions,
not their source, unless diagnosing a failure.

Before a potentially large read, use the verified Python interpreter and the
bundled reader:
`<verified-python> -X utf8 "<skill-directory>/scripts/check_text_size.py" --file "<document>" --max-output-tokens <limit> --part 1`.
The program is `scripts/check_text_size.py`; the document is only the `--file`
value. Start only named `.py` files as Python program files. SKILL.md, references
and assignments are documents, never programs.

Use the smallest declared or explicitly selected command and outer output limit.
The reader validates the complete UTF-8 file and budgets its labels too.
Follow `part=N bytes=start:end/total next=M` with `--part M` through `last`,
where end equals total. Read every unchanged part in order before dependent
work. Keep the same budget throughout; if it changes, restart at part 1.
Use separate outer calls unless their complete combined output, including
labels and metadata, has been measured and fits. Multiple reads or `text()`
calls in one outer call share its budget. A reader error leaves the read
incomplete, even if the budget cannot fit its diagnostic. Do not alter or copy
the input, truncate it or recover omitted text after an oversized read.
Without an applicable limit, read complete UTF-8 directly; invent no budget.
Python and every named helper are required. Missing dependencies or helper
errors stop the affected operation. Do not substitute manual execution.

Helpers: `scripts/setup.py`, `scripts/check_text_size.py`.
