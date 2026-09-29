## Compatibility

Needs Codex desktop, a saved local project, native task creation, messaging
and archiving, access to the task ID, Python 3.11+ and the complete Codex
Suite. It also needs a frontier model from the Fable, Astra, SOL or Opus
families, version 5.0 or newer. Luna was also used in testing.

All tasks have to share the existing checkout, and authorized result messages
have to be able to resume the coordinator. If the host can't do either,
Workflow says so before dispatching anything.

Context rollover uses Codex's own measurements when they're available.
Without them, bounded work simply continues. If a result can't be delivered,
recovery uses the existing chat and the saved result. Codex may ask for
approval before it delivers a message.

Install and enable every Skill in the suite. Each one covers its own kind of
task. To start Workflow, ask for it explicitly.
