# Native agent capacity

Completed agents can still occupy a host slot when messages remain queued.
`send_message` does not wake them. A bounded `followup_task` can consume those
messages and end the turn. This does not prove a slot is free or guarantee recovery.
The host owns capacity. Keep model pairs, settings and the current run unchanged.

## Failed spawn owner

Use this route only when the native call explicitly refuses capacity, returns no
agent ID and confirms no agent was created. A timeout, transport error, partial
result, ambiguous identity or unknown writer state blocks without retry.
Retain the exact generated arguments and the original diagnostic. One failed
spawn gets at most one cleanup attempt and one retry. Never rebuild an assignment
or start replacement work while the original spawn's outcome is uncertain.

A manager sends `CAPACITY_REQUEST <own-id> <attempt-number>` to the runner.
Number spawn attempts monotonically in that manager and retain the token. Stay
active with `wait_agent`, without writes or new dispatch. Accept CAPACITY_RETRY
only from the exact runner with that token. CAPACITY_BLOCKED with the same
token ends this wait, retaining its diagnostic and recording the unresolved
problem under run-feedback.md. Retry the same arguments once, then
process its actual result normally. A repeated refusal is BLOCKED, with no second
cleanup. STOP, an unanswered decision or uncertain writes prevent retry.
Resolve a recorded capacity problem only after the required spawn succeeds.

The runner uses the same route for its own definite failed manager spawn.
Its one retry reuses the generated arguments and attempted manager number.

## Runner owns cleanup

Read `list_agents` once. Select only exact known, retired managers directly
spawned by this runner, with completed handoffs and confirmed native completion.
Exclude a manager with a pending essential clarification or uncertain follow-up
delivery, even if its earlier handoff was completed.
Never wake an active manager, unfinished worker, completed reviewer, unknown
agent or another agent's child for cleanup. The current manager remains active
and owns its assignment. No eligible retired manager means BLOCKED. On a
failed cleanup, send CAPACITY_BLOCKED with the original token and concrete
diagnostic to the requester so it can end its wait and retain the problem.
On STOP, use the stop contract instead of sending retry permission.

For each eligible manager still listed as completed, use `followup_task` once
with this exact message:

```text
Capacity cleanup only. Consume queued messages without resuming project work.
Remain write-inactive. Do not edit files, Plans or reports, spawn children or
send messages. Supersede any queued instruction to resume or write. End with
only CAPACITY_RECOVERY_DONE.
```

Wait for that exact manager's native final CAPACITY_RECOVERY_DONE before moving
to the next candidate. Allow at most 60 seconds for the whole cleanup attempt.
Failure, timeout, unexpected status or user STOP ends recovery without a retry.
An interrupted cleanup must be confirmed quiescent before any resume.
Do not infer completion from successful followup delivery or an old final.

After at least one verified cleanup, send `CAPACITY_RETRY <attempt-number>` to
the requesting current manager, or retry the runner's own failed spawn once.
This permits a new attempt after an actual state change, not a claim of available
capacity. Retain handled request tokens so duplicates cannot restart cleanup or
dispatch. On another failure, show the actual BLOCKED diagnostic and let the
manager record the unresolved problem under run-feedback.md. Successful internal
cleanup produces no routine report entry or user progress message.
