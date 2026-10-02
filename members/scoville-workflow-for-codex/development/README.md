# Development

Early coordination put too much effort into passing instructions through
helpers, message records and polling. Using the host's native agent operations
removed layers that did little for the actual work. Context exhaustion and
delivery failures then showed why handoffs need explicit ownership and retained
progress. Simpler coordination helped, but it did not make host failures disappear.

The [source](../scoville-workflow-for-codex/) and tests live in the suite. Install the built package.

From this member directory, run `python -B -m unittest discover -s development/tests`.
