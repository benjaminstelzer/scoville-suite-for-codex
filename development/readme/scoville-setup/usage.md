## How to use

Ask Scoville Setup to show this project's settings, or tell it which values
to save. For Ask, you can set the advisers, model and effort, Claude spending
limits, timeouts, session storage, custom instructions and web access. For
Workflow, you can set a model and reasoning pair per route and the context
percentages at which manager and child agents schedule rollover. They finish
their complete assigned unit before a context-driven change.

Setup shows the values that apply to the project, defaults included. A
one-off choice stays in the request or Plan Step unless you ask Setup to save
it. Setup saves the regular reasoning levels `low`, `medium`, `high` and
`xhigh`. Other supported levels have to be configured by hand, and Setup
leaves them unchanged when it saves other settings.

Native Ask advisers and Workflow roles are subagents without sidebar chats.
Existing `ask.pin_threads` and `workflow.pin_threads` values remain readable
but have no effect. Setup explains those legacy fields, rejects new pin changes
and preserves them when saving other choices. Claude CLI sessions also have
no sidebar entry.
