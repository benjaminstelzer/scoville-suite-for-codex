# Scoville Setup

Save the Scoville settings for your project in one file. Setup shows the effective values and changes only what you ask it to save.

Here, the heat is control over the settings your project actually uses, including defaults and saved choices.

## How it works

- Read project settings from `.scoville/config.json`, using defaults for missing values.
- Validate requested changes with the same checks used by Ask and Workflow, then save them.

## What it enforces

- Saves settings only on explicit request and preserves unrelated values.
- Rejects invalid values before writing.
- Changes configuration between runs, without starting or supervising a workflow.

## What it costs

- Inspecting and changing settings takes an additional interaction with your agent.

## How it was developed

- Tests cover displaying and saving settings, rejecting invalid inputs, and using the saved values in Ask and Workflow.

## Compatibility

Requires Codex with Python 3.11+.

A current Fable, Astra, SOL or Opus model is recommended. Luna was also used
in testing.

## Install

Setup is included with the Codex Suite. It has no standalone distribution.
Install the complete suite from [its own packages](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/packages).
Partial installation is not supported. Every suite member must be installed
and enabled.

## How to use

Ask Scoville Setup to show the settings for this project, or tell it which values to save. You can configure Ask advisers, model and effort, Claude spending limits, timeouts, session storage, custom instructions and web access. Workflow supports model/reasoning pairs for each route and the coordinator/worker context rollover percentages.

Setup shows the values that apply to the project, including defaults. A one-time choice remains in the request or Plan Step unless you ask to save it.
Setup saves the regular reasoning levels `low`, `medium`, `high` and `xhigh`.
Other supported levels require manual configuration and remain unchanged when
Setup saves unrelated settings.

Ask and Workflow each have a `pin_threads` switch, enabled by default.
For example: “Use Scoville Setup to disable pinning for Workflow but keep it
enabled for Ask.” Setup saves `workflow.pin_threads: false` and
`ask.pin_threads: true` in the project's `.scoville/config.json`.
Use true/false boolean values, not strings. Workflow includes its starting
manager, workers, reviewers and rollover successors. Existing pins stay as
they are. Claude CLI sessions have no sidebar entry.



## Sources

- Ask and Workflow configuration files define the defaults and supported values.
- [Scoville Suite source](https://github.com/benjaminstelzer/scoville-suite-for-codex).

## License

MIT. See [LICENSE](LICENSE).
