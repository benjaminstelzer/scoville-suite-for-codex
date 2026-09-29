# Scoville Setup

Setup keeps your project's Scoville settings in one file. It shows the values
that actually apply and changes only what you ask it to save.

The heat, in this case, is knowing and controlling which settings your
project actually uses, defaults included.

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

## Compatibility

Requires Codex with Python 3.11+.

A current Fable, Astra, SOL or Opus model is recommended. Luna was also used
in testing.

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
percentages at which coordinators and workers roll over.

Setup shows the values that apply to the project, defaults included. A
one-off choice stays in the request or Plan Step unless you ask Setup to save
it. Setup saves the regular reasoning levels `low`, `medium`, `high` and
`xhigh`. Other supported levels have to be configured by hand, and Setup
leaves them unchanged when it saves other settings.

Ask and Workflow each have a `pin_threads` switch, enabled by default. For
example: "Use Scoville Setup to disable pinning for Workflow but keep it
enabled for Ask." Setup then saves `workflow.pin_threads: false` and
`ask.pin_threads: true` in the project's `.scoville/config.json`. Use the
boolean values true and false, not strings. For Workflow, the switch covers
the starting manager, workers, reviewers and rollover successors. Existing
pins stay as they are, and Claude CLI sessions have no sidebar entry.



## Sources

- Ask and Workflow configuration files define the defaults and supported values.
- [Scoville Suite source](https://github.com/benjaminstelzer/scoville-suite-for-codex).

## License

MIT. See [LICENSE](LICENSE).
