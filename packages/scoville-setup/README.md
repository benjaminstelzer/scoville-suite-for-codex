# Scoville Setup

Setup shows the Scoville settings your project actually uses and saves the
changes you request. Models, reasoning levels and Workflow settings stay in
one project file, with defaults filling the gaps.

Scoville measures chili heat. Setup lets you choose the seasoning instead of
discovering it halfway through the meal.

## How it works

- Read project settings from `.scoville/config.json`, using defaults for missing values.
- Validate requested changes with the same checks used by Ask and Workflow, then save them.

## What it enforces

- Saves settings only when you ask and leaves unrelated values alone.
- Rejects invalid values before writing.
- Changes configuration between runs. It doesn't start or supervise a
  workflow.

## What it costs

- Viewing or changing settings takes an agent interaction. Saved project settings spare you from repeating the same choices in later runs.

## How it was developed

Setup reuses Ask and Workflow validation. Tests follow saved settings into
those consumers, because a successful save alone says little about the next run.

## Compatibility

Requires Codex with Python 3.11+. Use a Fable, Astra, SOL or Opus model (5.0+).

## Install

Setup comes with the Codex Suite and isn't available on its own.
Install the complete suite from [its own packages](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/packages).
Partial installations aren't supported: every member has to be installed and
enabled.

## How to use

Ask Scoville Setup to show this project's settings, or tell it which values
to save. For Ask, you can set the advisers, model and effort, Claude spending
limits, timeouts, session storage, custom instructions and web access. For
Workflow, you can set the manager's model and reasoning, the worker and review
pairs per route, and the context
percentages at which manager and child agents schedule rollover. They finish
their complete assigned unit before a context-driven change.

The manager defaults to `gpt-6.1-sol` with `medium` reasoning. Save another pair
under `workflow.manager.model` and `workflow.manager.reasoning`, through Setup
or directly in `.scoville/config.json`. An explicit pair for one run takes
precedence. Manager successors keep the pair that started the run.

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
