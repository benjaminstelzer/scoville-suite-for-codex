## Compatibility

Needs Codex with native agent spawning, messaging, waiting, interruption and
agent-state inspection, Python 3.11+ and the complete Codex Suite. Agents must
share the existing checkout and support the configured model and effort pairs.
It also needs a frontier model from the Fable, Astra, SOL or Opus families,
version 5.0 or newer. Bounded Luna Medium tests also cover the current manager
handoff. They do not establish complete Luna coverage of the agent lifecycle.

The run stops when the host cannot confirm agent identity, deliver a required
message or establish who may write. It does not substitute chats, another model
or an assumed close operation. Queued messages can keep completed agents resident.
Bounded cleanup can help, but available agent capacity can still limit a run.

Context rollover uses fresh Codex measurements tied to the actual agent.
Without usable telemetry, bounded work continues without claiming a measured
switch. Automated tests cover helper validation and controlled telemetry.
Live multi-unit execution, stop handling, child completion after a measured
crossing and manager handoffs need separate evidence.
