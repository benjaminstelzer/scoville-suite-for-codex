# Development

The [member source](../scoville-workflow-for-codex/) is part of
[Scoville Suite](../../../README.md#development-and-builds). Build before you
install. Development files stay in the suite, and current work is tracked in
the suite's root Plan. The Plans in this member are historical.

## Validate

Run the focused contract tests from `members/scoville-workflow-for-codex/`:

```text
python -B -m unittest discover -s development/tests -v
```

Run package validation against a generated build, and validate the planning
profile at the suite root. The contract tests check source rules, not the
live task lifecycle. The [development history](../../../docs/README.md)
explains the runtime problems and the changes they led to.

## Installation identity

Install only the generated package. Before you replace an existing
installation, wait until every workflow using it has finished. Then compare
the complete build and installed file lists and their contents. A copy
command alone doesn't prove the new version is in use.

## Retention

Current tests, Plans, Decisions and this summary are kept. Raw model reviews,
transcripts, screenshots and one-off runtime evidence go to temporary storage,
unless a published artifact depends on them.
