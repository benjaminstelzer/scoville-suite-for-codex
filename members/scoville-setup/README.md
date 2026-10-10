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

Requires Codex with Python 3.11+. Fable, Astra, SOL or Opus (5.0+) are recommended. Luna 6 with High reasoning passed the selected comprehension and functional checks in Codex. Other routes and hosts remain unverified.

## Install

Setup comes with the Codex Suite and isn't available on its own.
Install the complete suite from [its own packages](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/packages).
Partial installations aren't supported: every member has to be installed and
enabled.

## Configuration

Project settings live in `.scoville/config.json`. Ask settings include adviser
models and effort, Claude limits, timeouts, session storage, custom instructions
and web access. Workflow settings choose executor, reviewer and explorer models
and effort. Optional explore fields inherit the effective execute values.
The existing visible chat is the manager; its model comes from the host.

Setup shows effective values including defaults. A one-off choice remains in
the request or Plan unless the user asks to save it. Legacy workflow.manager,
workflow.context and workflow.pin_threads are ignored when reading; an authorized
save removes only those legacy keys while preserving unrelated settings.
New patches cannot set them. Show is read-only.

## Limitations

Setup saves low, medium, high and xhigh reasoning. Other supported levels may
be configured manually and remain unchanged during unrelated saves.

Native advisers, executors, reviewers and explorers have no sidebar chats. Legacy
ask.pin_threads is readable and preserved but has no effect; new pin changes
are rejected. Claude CLI sessions also have no sidebar entry.

## How to use

Ask Scoville Setup to show this project's settings, or tell it which values
to save. Name a one-off choice in the request if it should apply only to the
current task.

## Sources

- Ask and Workflow configuration files define the defaults and supported values.
- [Scoville Suite source](https://github.com/benjaminstelzer/scoville-suite-for-codex).

## Developer links

[Source](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-setup) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-setup/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/members/scoville-setup/development/README.md)

## License

MIT. See [LICENSE](LICENSE).
