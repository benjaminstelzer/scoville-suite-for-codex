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
