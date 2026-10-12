## Configuration

Use Scoville Setup to show or save `.scoville/config.json` in the project.
`workflow.execute.CLASS`, `review.CLASS` and `explore.CLASS` select role models
and reasoning. Unspecified Explorer fields inherit effective Executor values.
The host chooses the manager model. Reads create no file.

`workflow.context_threshold_percent` is the one threshold for all subagents.
Its bundled default is 50. Reuse an idle associated agent below it; start a new
one at or above it. Check only before assignments. A failed measurement is a
technical problem, not a spawn fallback. There is no manager threshold or rollover.

Legacy `manager`, nested `context` and `pin_threads` settings are ignored on
reads and removed only by an authorized save. They do not configure this new
threshold. Other saved settings are preserved.

The [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
explain model selection, original-text extraction and reuse.
