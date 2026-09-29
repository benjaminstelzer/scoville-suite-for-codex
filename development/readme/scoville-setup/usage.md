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
