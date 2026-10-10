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
