## Limitations

Setup saves the regular reasoning levels `low`, `medium`, `high` and
`xhigh`. Other supported levels have to be configured by hand, and Setup
leaves them unchanged when it saves other settings.

Native Ask advisers and Workflow roles are subagents without sidebar chats.
Existing `ask.pin_threads` and `workflow.pin_threads` values remain readable
but have no effect. Setup explains those legacy fields, rejects new pin changes
and preserves them when saving other choices. Claude CLI sessions also have
no sidebar entry.
