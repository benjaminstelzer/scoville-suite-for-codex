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

For direct helper calls in PowerShell, quote the interpreter path and prefix it
with `&`. Run generated commands unchanged in the current tool shell; do not
replace their process or argument handling with a direct call.

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

For a requested one-time Ask override, read Scoville Ask for Codex's
`references/configuration.md` and use its read-only
settings resolution with the selected adviser and requested model or effort.
Keep unrequested saved values. Report the actual returned values; a promise
to use them later is not resolution. This reads settings without starting an
adviser or saving configuration.

For an explicit save request:

1. Include only requested fields in a JSON object. Generate it with a serializer,
   such as Python `json.dumps` or PowerShell `ConvertTo-Json -Depth 10 -Compress`;
   do not hand-write JSON.
2. Use UTF-8 stdin. In PowerShell, set
   `$OutputEncoding = [System.Text.UTF8Encoding]::new($false)` before piping so
   non-ASCII values reach the helper unchanged.
3. Pass the complete serialized object on stdin to `set` below.
4. Read the successful JSON response: it contains saved effective settings.

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

Without an applicable limit, read complete UTF-8 directly; invent no budget.
With an applicable limit:

1. Use the smallest declared or explicitly selected limit of the command and
   every enclosing tool output. Read separately unless the complete combined output,
   including labels and metadata, is measured and fits; combined reads share
   that budget.
2. If the file may exceed that limit, use the verified Python interpreter and
   bundled reader:
   `<verified-python> -X utf8 "<skill-directory>/scripts/check_text_size.py" --file "<document>" --max-output-tokens <limit> --part 1`.
   It validates the complete UTF-8 file and budgets labels too.
   The program is `scripts/check_text_size.py`; the document is its `--file`
   argument. Copy the whole command: change only `--file` for another document
   or `--part` to continue. Keep program, launcher and quoting unchanged.
   Only named `.py` files may be Python program files; SKILL.md, references and
   assignments are documents.
3. For multipart output, follow `part=N bytes=start:end/total next=M` with
   `--part M` through `last`,
   where end equals total. Read every unchanged part in order before dependent
   work. Use one limit for the whole sequence. If an applicable limit changes,
   restart at part 1 with the new smallest limit; never raise a binding limit
   to keep the old sequence.

Reader parts are already bounded. Execute the supplied reader command unchanged;
do not wrap it in `--run`, add `--publish-full`, or save its output.

A reader error leaves the read incomplete, even if its diagnostic cannot fit.
Correct a visible cause and restart at part 1. Do not repeat an unchanged failed
call or raise a binding limit. Otherwise report the unread document and stop
dependent work.
Do not alter or copy the input, truncate it or recover omitted text after an
oversized read.

To check a supplied expected SHA-256, use the same checker with
`--file "<artifact>" --sha256 --max-output-tokens <limit>` and compare its
`sha256` with the supplied value. A mismatch or error stops dependent work.
Then read the same unchanged file from `--part 1` through `last` with the same
limit. Hash verification is not reading; ordinary sources need no extra hash check.

| Condition | Required route |
| --- | --- |
| Python and every named helper are available | Use the bundled helper. |
| Missing Python, script, dependency or helper error | Stop the affected operation; do not substitute manual execution. |

Helpers: `scripts/setup.py`, `scripts/check_text_size.py`.
