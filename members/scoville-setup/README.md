# Scoville Setup

Setup keeps your project's Scoville settings in one file. It shows the values
that actually apply and changes only what you ask it to save.

## How it works

- Read project settings from `.scoville/config.json`, using defaults for missing values.
- Validate requested changes with the same checks used by Ask and Workflow, then save them.

## What it enforces

- Saves settings only when you ask and leaves unrelated values alone.
- Rejects invalid values before writing.
- Changes configuration between runs. It doesn't start or supervise a
  workflow.

## What it costs

- Inspecting and changing settings takes an additional interaction with your agent.

## How it was developed

- Tests cover displaying and saving settings, rejecting invalid inputs, and using the saved values in Ask and Workflow.

- Development links: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-setup) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-setup/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/members/scoville-setup/development/README.md)

## Compatibility

Requires Codex with Python 3.11+.

Requires a frontier model from the Fable, Astra, SOL or Opus families,
version 5.0 or newer. Luna was also used in testing.

## Install

Setup comes with the Codex Suite and isn't available on its own.
Install the complete suite from [its own packages](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/packages).
Partial installations aren't supported: every member has to be installed and
enabled.

## How to use

Ask Scoville Setup to show this project's settings, or tell it which values
to save. For Ask, you can set the advisers, model and effort, Claude spending
limits, timeouts, session storage, custom instructions and web access. For
Workflow, you can set a model and reasoning pair per route and the context
percentages at which manager and child agents schedule rollover. They finish
their complete assigned unit before a context-driven change.

Setup shows the values that apply to the project, defaults included. A
one-off choice stays in the request or Plan Step unless you ask Setup to save
it. Setup saves the regular reasoning levels `low`, `medium`, `high` and
`xhigh`. Other supported levels have to be configured by hand, and Setup
leaves them unchanged when it saves other settings.

Native Ask advisers and Workflow roles are subagents without sidebar chats.
Existing `ask.pin_threads` and `workflow.pin_threads` values remain readable
but have no effect. Setup explains those legacy fields, rejects new pin changes
and preserves them when saving other choices. Claude CLI sessions also have
no sidebar entry.

## Sources

- Ask and Workflow configuration files define the defaults and supported values.
- [Scoville Suite source](https://github.com/benjaminstelzer/scoville-suite-for-codex).

## License

MIT. See [LICENSE](LICENSE).
