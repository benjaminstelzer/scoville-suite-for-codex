# Manager start and takeover

Runner and managers read this contract before their first protocol action.
The runner retains only control metadata; substantive handoffs pass directly
between managers. Authenticate every message by the host sender and retained
exact agent ID, never a claimed ID or title. Only the runner starts managers.

| State / event | Runner action | Manager action and gate |
| --- | --- | --- |
| Initial activation or one SUCCESSOR_REQUEST from the current manager | Build and spawn once; retain one unique ID, canonical name mapping and launched pair. Ignore a handled duplicate request. Never infer a request from elapsed time or context. | A predecessor requests once only after its complete unit and children are quiescent, then stops writes. Include own ID and launched pair. |
| Spawned, awaiting READY | Require READY from the exact new ID within 60 seconds. For a successor, first deliver SUCCESSOR `<new-id>` to the predecessor, then send START to the ready manager. | **First action:** send READY to the supplied runner, then actively wait for its START. Before START, no project reads, handoff requests, writes or children. |
| START delivered | Initial manager becomes current. A successor stays pending. Accept pending startup/takeover controls and issues, but ordinary progress only from the current STARTed manager. | Initial manager loads operations and sends RUNNING after startup checks. Successor's **first action after START:** send HANDOFF_REQUEST directly to the supplied predecessor. |
| Direct handoff | Never read the handoff. | Predecessor accepts the request only from the runner-named successor, sends the substantive handoff directly, then HANDOFF_DELIVERED to runner. Stay active and write-inactive for direct clarifications and the exact successor's receipt, at most 60 seconds. |
| Verification | Retain both IDs; no release yet. | Successor loads operations and compares handoff with canonical Plan and relevant files. Verify unchanged report path, child quiescence, completed effects, review/commit boundaries, scope, permissions, stops and pending issues/answers. Resolve missing/conflicting facts directly. Only then send HANDOFF_ACCEPTED to predecessor and RUNNING to runner. No writes or dispatch. |
| Receipt and predecessor final | Require **both** predecessor's native completion and successor's RUNNING. HANDOFF_DELIVERED alone proves only delivery. Forward queued input in order, then send TAKEOVER_COMPLETE. Successful delivery makes successor current and retires predecessor. | Predecessor ends only after the authenticated receipt, with control-only final HANDOFF_DELIVERED. Successor actively waits up to 60 seconds for exact runner's TAKEOVER_COMPLETE, applies post-snapshot steering/answers, then resumes the retained next action without repeating consumed checkpoints or checks. |
| Retired predecessor | Only for CLARIFICATION_REQUEST from the current manager naming its retained predecessor, use followup_task on that exact ID for direct read-only clarification. | Retired manager remains write-inactive. No routine receipt/closure message or cleanup wakeup after native completion. |

Use `wait_agent` during READY/START and takeover waits; do not end the waiting
turn. RUNNING asserts completed startup/verification, never pending or qualified
takeover; use BLOCKED for those states. A tool error, missing/mismatched confirmation, conflicting fact, uncertain
spawn/writer state or STOP blocks the affected transition. Retain identities,
payloads and delivery state; report the concrete diagnostic under run-feedback.md.
Never infer delivery, release work, automatically respawn or retry an uncertain
send. On failed startup send STOP to the known new manager. If START might have
arrived, establish child/writer quiescence under SKILL.md's Stop rules before
resuming. A blocked successor cannot write, including the run report.

## Steering and answers

From accepted successor request through release, queue new steering and answers
to predecessor-owned issues for the successor in received order. Preserve each
issue's original source identity and answer/delivery state. Deliver once to the
authenticated pending successor before TAKEOVER_COMPLETE, never also to the
predecessor. Retain the queue and uncertain deliveries after a failed takeover.
Answers to the pending successor's own issues go directly to that exact ID.
Outside takeover, forward steering to the current manager and each answer once
to its originating manager or verified current successor. Never broadcast.
Use followup_task for an idle recipient; send_message does not wake it.

The successor applies post-snapshot input before any write or dispatch and
relays resulting decisions/blockers. An unanswered decision remains blocking;
elapsed time is no answer. STOP reaches both managers during incomplete takeover,
including their children, under the runner's stop contract.
