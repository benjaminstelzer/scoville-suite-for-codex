# Scoville Setup

Save the Scoville settings for your project in one file. Setup shows the effective values and changes only what you ask it to save.

## How it works

- Read project settings from `.scoville/config.json`, using defaults for missing values.
- Validate requested changes with the same checks used by Ask and Workflow, then save them.

## What it enforces

- Saves settings only on explicit request and preserves unrelated values.
- Rejects invalid values before writing.
- Changes configuration between runs, without starting or supervising a workflow.

## What it costs

- You choose which settings to save. The helper reads and validates them locally without model calls.

## How it was developed

- Tests exercise settings display, authorized changes, invalid inputs and consumption by Ask and Workflow.

## Compatibility

Codex with Python 3.11+ and a frontier LLM from the Fable, Astra, SOL or Opus families, version 5.0 or newer.

## Install

Setup is included with the Codex Suite. It has no standalone distribution.
Install the complete suite from [its own packages](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/packages).
Partial installation is not supported. Every suite member must be installed
and enabled.

## How to use

Ask Scoville Setup to show the settings for this project, or tell it which values to save. You can configure Ask advisers, model and effort, Claude budget, timeout, persistence, customizations and web tools. Workflow supports model/reasoning pairs for each route and the coordinator/worker context rollover percentages.

The helper returns the effective values. A one-time choice remains in the request or Plan Step unless you ask to save it.
Setup saves the regular reasoning levels `low`, `medium`, `high` and `xhigh`.
Other supported levels require manual configuration and remain unchanged when
Setup saves unrelated settings.

## Sources

- Imported Ask and Workflow defaults and their configuration validators are the settings contract.
- [Scoville Suite source](https://github.com/benjaminstelzer/scoville-suite-for-codex).

## License

MIT. See [LICENSE](LICENSE).
