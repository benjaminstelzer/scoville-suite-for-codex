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
| Direct handoff | Never read the handoff. | Apply [Direct handoff](#direct-handoff); await the exact successor's receipt without writes. |
| Verification | Retain both IDs; no release yet. | Apply [Verification](#verification) before HANDOFF_ACCEPTED and RUNNING; no writes or dispatch. |
| Receipt and predecessor final | Require **both** predecessor's native completion and successor's RUNNING. HANDOFF_DELIVERED alone proves only delivery. Forward queued input in order, then send TAKEOVER_COMPLETE. Successful delivery makes successor current and retires predecessor. | Predecessor ends only after the authenticated receipt, with control-only final HANDOFF_DELIVERED. Successor actively waits for exact runner's TAKEOVER_COMPLETE; a wait timeout alone is no refusal. Apply post-snapshot steering and answers, then resume the retained next action without repeating consumed checkpoints or checks. |
| Retired predecessor | Only for CLARIFICATION_REQUEST from the current manager naming its retained predecessor, use collaboration.followup_task on that exact ID for direct read-only clarification. | Retired manager remains write-inactive. After native completion, send neither routine receipts nor routine closure messages. Do not wake it for cleanup. |

## Direct handoff

Predecessor accepts the request only from the runner-named successor. Compose
the substantive handoff yourself from your retained rollover handoff, keeping
pending choices and the necessary next action; omit obsolete diary repetition.
Send its text with `collaboration.send_message` directly to that successor, then
HANDOFF_DELIVERED to runner. `build_manager_handoff.py` only builds the runner's
spawn arguments; never run it for this step. Stay active and write-inactive for
direct clarifications and the exact successor's receipt. A wait timeout alone
does not end this state. An oversized handoff or confirmed one-way routing
rejection uses the file route below.

## Verification

The successor verifies without writes or dispatch:

1. Load operations and compare the handoff with the current Plan position and
   sources needed next. Confirm unchanged report path, child quiescence,
   completed effects, evidence limits, required review and commit boundaries, scope,
   permissions, stops, pending issues and answers.
2. Reuse completed checks and accepted reviews only while reviewed content,
   applicable requirements and supporting conditions remain unchanged. Reassess
   only affected claims under existing check and review rules.
3. Resolve material gaps directly. Read old results or additional sources only
   for specific missing or conflicting facts; neither reconstruct earlier work
   nor rerun accepted checks solely because the manager changed. After complete
   verification, send HANDOFF_ACCEPTED to predecessor and RUNNING to runner.
   Keep writes and dispatch stopped until TAKEOVER_COMPLETE.

## Transition failures

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

| Discrepancy | Required action |
| --- | --- |
| Canonical files resolve inaccurate recorded evidence | Successor confirms with predecessor or an actual user answer. Retain inaccurate evidence and required fresh review as pending handoff work. HANDOFF_ACCEPTED may proceed; after TAKEOVER_COMPLETE, correct and validate the Plan and finish review before next dispatch. Never claim the old review proved the false fact. |
| Actual effect, authority, writer state or correction scope remains uncertain | Send BLOCKED to runner; both managers stay write-inactive until resolved or stopped. Predecessor remains available for read-only clarification and receipt. Elapsed time proves no success. |

## Complete handoff file

```text
Authenticated request → predecessor publishes complete handoff
  → runner forwards metadata → successor verifies and reads
  → HANDOFF_ACCEPTED → predecessor native final + successor RUNNING
  → runner delivers queued input → TAKEOVER_COMPLETE
```

After authenticated HANDOFF_REQUEST, use this route when required handoff
content cannot fit the shared pre-output size check, or its direct send
explicitly returns `live agent path ... not found`. Skip direct text send for
oversized handoffs. The retiring predecessor may publish the complete temporary
handoff; other project and report writes remain stopped. Uncertain sends,
capacity errors and other failures stay blocked. Never retry the send or spawn
another manager.

1. **Predecessor:** Publish the same retained handoff through
   `check_text_size.py --publish-full` under `.scoville/temp/<sha256>.txt`. Send
   `HANDOFF_FILE_READY <successor-id> <sha256> <absolute-file-path>` to runner.
2. **Runner:** Check the exact predecessor sender and one pending successor ID.
   Forward `HANDOFF_FILE <predecessor-id> <sha256> <absolute-file-path>` to that
   successor, instructing it to verify the hash and read the entire file. The
   path is all text after the hash, including spaces. Never read the file.
   Failed or uncertain forwarding blocks takeover; retain file and delivery state.
3. **Successor:** Accept the path only from the exact runner after START. Verify
   SHA-256 over complete original bytes. Decode and emit explicitly as UTF-8;
   read every ordered character-safe portion through prechecked complete outputs
   that fit, including labels and combined results. Hash verification is not
   reading. Missing, mismatched or incomplete content blocks takeover. If a
   direct copy arrives, consume the same handoff only once; conflicting copies
   block. Apply
   [Verification](#verification) against the canonical Plan and relevant files
   before sending HANDOFF_ACCEPTED directly to predecessor.
4. **Predecessor:** After the receipt, send HANDOFF_DELIVERED to runner and end
   with the control-only native final. **Runner:** Require that final and
   successor RUNNING before TAKEOVER_COMPLETE.

## Steering and answers

| Phase or input | Recipient and gate |
| --- | --- |
| Accepted successor request through release: steering and answers to predecessor-owned issues | Queue in received order for the authenticated pending successor. Deliver once before TAKEOVER_COMPLETE, never also to predecessor. |
| Pending successor's own issue | Send the answer directly to that exact ID. |
| Outside takeover | Steering goes to current manager; each answer goes once to its originating manager or verified current successor. Never broadcast. |
| Failed takeover | Retain queue and uncertain deliveries. |

Preserve each issue's original source identity, answer and delivery state.
Use collaboration.followup_task for an idle recipient; collaboration.send_message does not wake it.

The successor applies post-snapshot input before any write or dispatch and
relays resulting decisions and blockers. An unanswered decision remains blocking;
elapsed time is no answer. STOP reaches both managers during incomplete takeover,
including their children, under the runner's stop contract.
