## Configuration

Use Scoville Setup to show or save project settings in `.scoville/config.json`.
Under workflow, execute.CLASS selects an executor pair and review.CLASS its
reviewer pair. Missing fields use bundled defaults. Reading or starting a run
creates no configuration file.
Optional explore.CLASS overrides the Explorer pair. Unspecified fields inherit
the effective execute.CLASS values, including project overrides.

The visible chat is the manager; its model comes from the host. Legacy manager,
context and pin_threads keys are ignored. An authorized Setup save removes
those three keys while preserving unrelated settings. No rollover thresholds
or automatic successor roles remain.

The [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
explain route classification and explicit model choices.
