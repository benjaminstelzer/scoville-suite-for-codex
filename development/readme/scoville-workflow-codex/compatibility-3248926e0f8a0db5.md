## Compatibility

Requires Codex desktop, a saved local project, native task creation, messaging
and archival, access to the task ID, Python 3.11+, and the complete Codex Suite.
A current Fable, Astra, SOL or Opus model is recommended. Luna was also used
in testing.

Tasks must share the existing checkout. Authorized result messages must be able
to resume the coordinator. If the host cannot support either, Workflow reports
the limitation before dispatch.

Context rollover uses native measurements when available. Missing measurements
allow bounded work to continue. If result delivery fails, recovery uses the existing chat and saved result.
Codex may require approval before delivering a message.
