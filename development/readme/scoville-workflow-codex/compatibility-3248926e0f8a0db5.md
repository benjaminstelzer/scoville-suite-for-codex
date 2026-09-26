## Compatibility

Requires Codex desktop, a saved local project, native task creation,
messaging and archival controls, access to the task's own `CODEX_THREAD_ID`,
and Scoville Plan v1.8.0 or a compatible source_text selector. Python 3.11+ runs the deterministic helpers.
There is no CLI or Claude Code execution path.

Tasks must share the existing checkout. If the host cannot provide that,
Workflow asks for a decision instead of silently creating another workspace.
Measured rollover uses native `token_count` data when available. Missing or
contradictory measurements do not by themselves block valid bounded work.

Native approval can hold a result message pending. Keep the exact task ID
without duplicate sends. The coordinator takes the complete result directly
from the native message; no parser or routine result read is needed.
Use `read_thread` only for targeted recovery of a known missing result or state.
The host must support authorized child messages that resume the coordinator.
If unavailable, Workflow reports the limitation before dispatch.
