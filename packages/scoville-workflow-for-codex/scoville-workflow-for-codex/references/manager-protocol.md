# Manager start and takeover

Runner and managers read this contract before their first protocol action.
The runner retains only control metadata; substantive handoffs pass directly
between managers. Authenticate every message by the host sender and retained
exact agent ID, never a claimed ID or title. Only the runner starts managers.
At your permitted reading stage, load the shared [writing rules](writing.md)
before the remaining operations references. They own pre-output sizing and
complete-file transfer.
If agent inventory is needed, query only retained IDs or this run's manager
subtree. A global inventory may contain unrelated agents and earlier reviews;
neither their finals nor their claims are handoff or review evidence for this
run. Match every reused assessment to this run, unit and recorded reviewer ID.

| State / event | Runner action | Manager action and gate |
| --- | --- | --- |
| Initial activation or one SUCCESSOR_REQUEST from the current manager | Build and spawn once; retain one unique ID, canonical name mapping and launched pair. Ignore a handled duplicate request. Never infer a request from elapsed time or context. | A predecessor requests once only after its complete unit and children are quiescent, then stops writes. Include own ID and launched pair. |
| Spawned, awaiting READY | Require READY from the exact new ID within 60 seconds. For a successor, first deliver SUCCESSOR `<new-id>` to the predecessor, then send START to the ready manager. | **First action:** send READY to the supplied runner, then actively wait for its START. Before START, no project reads, handoff requests, writes or children. |
| START delivered | Initial manager becomes current. A successor stays pending. Accept pending startup or takeover controls and issues, but ordinary progress only from the current STARTed manager. | Initial manager loads operations and sends RUNNING after startup checks. Successor's **first action after START:** send HANDOFF_REQUEST directly to the supplied predecessor. |
| Direct handoff | Never read the handoff. | Predecessor accepts the request only from the runner-named successor. Compose the substantive handoff yourself from your retained rollover handoff, keeping pending choices and the necessary next action; omit obsolete diary repetition. Send its text with `collaboration.send_message` directly to that successor, then HANDOFF_DELIVERED to runner. `build_manager_handoff.py` only builds the runner's spawn arguments; never run it for this step. Stay active and write-inactive for direct clarifications and the exact successor's receipt. A wait timeout alone does not end this state. An oversized handoff or confirmed one-way routing rejection uses the file route below. |
| Verification | Retain both IDs; no release yet. | Successor loads operations and compares the compact handoff with the current Plan position and sources needed for the next action. Confirm unchanged report path, child quiescence, completed effects and evidence limits, required review and commit boundaries, scope, permissions, stops and pending issues and answers. Reuse completed checks and accepted review outcomes. Read old results or inspect additional sources only to resolve a specific missing or conflicting fact; do not reconstruct earlier work or rerun accepted checks solely because the manager changed. Resolve material gaps directly. Only then send HANDOFF_ACCEPTED to predecessor and RUNNING to runner. No writes or dispatch. |
| Receipt and predecessor final | Require **both** predecessor's native completion and successor's RUNNING. HANDOFF_DELIVERED alone proves only delivery. Forward queued input in order, then send TAKEOVER_COMPLETE. Successful delivery makes successor current and retires predecessor. | Predecessor ends only after the authenticated receipt, with control-only final HANDOFF_DELIVERED. Successor actively waits for exact runner's TAKEOVER_COMPLETE; a wait timeout alone is no refusal. Apply post-snapshot steering and answers, then resume the retained next action without repeating consumed checkpoints or checks. |
| Retired predecessor | Only for CLARIFICATION_REQUEST from the current manager naming its retained predecessor, use collaboration.followup_task on that exact ID for direct read-only clarification. | Retired manager remains write-inactive. After native completion, send neither routine receipts nor routine closure messages. Do not wake it for cleanup. |

Use bounded `collaboration.wait_agent` calls while waiting for READY, START or takeover.
Do not end the waiting turn. RUNNING asserts completion of the applicable
startup or takeover checks, never pending or qualified takeover; use BLOCKED
for those states.
The affected transition is blocked by any of these conditions:

- A tool error.
- Missing or mismatched confirmation.
- An unresolved conflicting fact.
- An uncertain spawn or writer state.
- STOP.

Retain identities, payloads and delivery state; report the concrete diagnostic
under run-feedback.md.
Never infer delivery, release work, automatically respawn or retry an uncertain
send. On failed startup send STOP to the known new manager. If START might have
arrived, establish quiescence of children and writers under SKILL.md's Stop
rules before resuming. A blocked successor cannot write, including the run report.

If canonical files resolve a discrepancy in recorded evidence, the successor
confirms the correction with the predecessor or an actual user answer. Retain
the inaccurate evidence and any required fresh review as pending work in the
handoff. This resolved discrepancy does not block HANDOFF_ACCEPTED: after
TAKEOVER_COMPLETE, correct and validate the Plan and complete the review before
dispatching the next unit. Do not claim the old review proved a false fact. If
the actual effect, authority, writer state or correction scope remains uncertain,
send BLOCKED to the runner and keep both managers write-inactive until resolved
or stopped. The predecessor remains available for read-only clarification and
receipt during that state; elapsed wait time is not a reason to invent success.

## Complete handoff file

After the authenticated HANDOFF_REQUEST, use this route when the complete
handoff cannot meet the shared pre-output size check without losing required
information, or when its direct send explicitly returns
`live agent path ... not found`. For an oversized handoff, do not attempt the
direct text send. The retiring predecessor may publish this complete temporary
handoff file. Other project and report writes remain stopped. An uncertain send,
capacity error or other failure stays blocked. Do not retry the send or spawn
another manager.

Publish the same retained handoff through `check_text_size.py --publish-full`
under `.scoville/temp/<sha256>.txt`. Send
`HANDOFF_FILE_READY <successor-id> <sha256> <absolute-file-path>` to the runner.
The runner checks the exact predecessor sender and its one pending successor ID,
then forwards `HANDOFF_FILE <predecessor-id> <sha256> <absolute-file-path>` to
that successor with the instruction to verify the hash and read the entire file.
The complete path is the text after the hash, including any spaces. The runner
sees only this metadata and never reads the file. A failed or uncertain forward
blocks takeover with the file and delivery state retained.

The successor accepts the path only from its exact runner after START. Verify
SHA-256 over the complete original bytes. Decode and emit text explicitly as
UTF-8, and read every ordered character-safe portion through prechecked
complete outputs that fit, including labels and combined results. Hash
verification does not replace reading. Missing,
mismatched or incomplete content blocks takeover. Compare the handoff with the
canonical Plan and relevant files under Verification. If a direct copy also
arrives, consume the same handoff only once. Conflicting copies block. Send
HANDOFF_ACCEPTED directly to the predecessor only after verification. The
predecessor then sends HANDOFF_DELIVERED to the runner and ends with its
control-only native final. The runner still requires that final and successor
RUNNING before TAKEOVER_COMPLETE.

## Steering and answers

From accepted successor request through release, queue new steering and answers
to predecessor-owned issues for the successor in received order. Preserve each
issue's original source identity and answer and delivery state. Deliver once to the
authenticated pending successor before TAKEOVER_COMPLETE, never also to the
predecessor. Retain the queue and uncertain deliveries after a failed takeover.
Answers to the pending successor's own issues go directly to that exact ID.
Outside takeover, forward steering to the current manager and each answer once
to its originating manager or verified current successor. Never broadcast.
Use collaboration.followup_task for an idle recipient; collaboration.send_message does not wake it.

The successor applies post-snapshot input before any write or dispatch and
relays resulting decisions and blockers. An unanswered decision remains blocking;
elapsed time is no answer. STOP reaches both managers during incomplete takeover,
including their children, under the runner's stop contract.
