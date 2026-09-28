# Execute the requested scope

The calling chat coordinates. Read the canonical Plan and, on continuation, the
supplied handoff. Reuse unchanged rules and model selections. Announce the Plan,
selected consecutive Step groups and why they belong together in one or two
sentences before first dispatch. Later announce only a dispatch, accepted result
or blocker, once and briefly. Do not relay worker progress or inspect changing files.

For messages to another chat, call `send_message_to_thread` with that chat's ID
as `threadId` and the message as `prompt`. This includes questions, results,
stop instructions and archival requests. Text in your own chat is not delivery.

## One unit through acceptance

1. Select the next unfinished Step, consecutive Step group or whole Work Item
   under [dispatch](operations-dispatch.md). Preserve order and prerequisites.
   Create a worker with the complete assignment. Use the
   returned exact task/host ID for subsequent messages.
2. The worker stops its project work and sends its result. Fixing product code
   that was complete or checked before this assignment ends the assignment after
   focused checks, even inside a larger test Step; retain remaining tests as
   unfinished work. Correcting intermediate errors in this assignment's new code
   stays within the assignment. Continue from that
   message; do not poll, remind or request the same result again. Follow any
   host-required progress wait once after creation.
3. Assess the result from the assigned chat by meaning, not formatting. Ask in
   a worker only for a missing fact needed to continue or accept. A reviewer
   returns one complete assessment, including anything it could not verify;
   do not start a reviewer question round. A repeated
   notification does not start another action. For context_handoff follow
   [rollover](operations-rollover.md). For blocked or needs_user_decision, retain
   the actual limitation and continue only independent eligible work.
4. Inspect the scoped diff and named evidence only as needed for scope and
   acceptance. Do not repeat the worker's diagnosis or tests. Follow the user's
   or project's review cadence. Otherwise review earlier, at the next checked
   boundary, when unreviewed product-code changes exist and either the next unit
   builds on or extensively verifies them, or they fix product code that was
   complete or checked before the fixing assignment. Otherwise review at Work Item completion. Pure tests, docs and
   evidence without product-code changes do not trigger an earlier review.
   Review is required for code, executable/configuration changes, critical
   documentation, an explicit requirement or unclear materiality.
5. At that boundary, create a fresh read-only reviewer with the diff since the
   last review and affected Acceptance, including relevant interactions. For the
   final review, supply short references to earlier assessments and reuse them
   for unchanged parts rather than reviewing those parts again. The coordinator handles Plan findings; send source
   findings to a new worker with the review findings. The coordinator
   does not edit product files. Keep the worker's model unless the cause warrants
   another configured route and explicit model choices permit it.
6. Check corrections against the findings. Material or unclear corrections and
   explicit requirements need another independent review. A clearly non-material
   correction may be accepted by bounded comparison with a short reason. If the
   same failure survives two corrections, reassess its cause before trying again.
   Change the approach or model when justified; ask the user only for a material
   decision or a blocker that cannot be resolved within the assignment.
7. Record checked intermediate results without claiming final acceptance. Mark
   the Work Item done only when its Acceptance and required review pass. Evidence
   contains the outcome and decisive report reference, not chat IDs or attempts.
   Run the Plan validator and follow its concrete diagnostics. When committing
   is authorized, inspect the staged diff and commit accepted changes with their
   Plan records, respecting backups and hooks.
8. With work remaining, run the coordinator checkpoint after a checked group,
   accepted Work Item or retained worker context_handoff, before creating the
   next worker. At a worker handoff nobody is writing, even if the unit is unfinished:

```text
python "<workflow-skill-directory>/scripts/check_context_checkpoint.py" --project-root "<workspace_root>" --role coordinator --boundary <unit-or-handoff>
```

`--boundary` identifies the checked unit or retained handoff, not final acceptance.
`rollover` follows the rollover reference; `continue` allows the next unit.
Missing or stale telemetry continues without guesses or manual telemetry searches.
Invalid configuration or a helper failure blocks the affected operation with its
diagnostic. Complete the Plan/index only after the whole requested scope passes.

On the third context_handoff of the same Step or group, use Scoville Plan to split
the handoff's remaining work into consecutive Steps in that Work Item, preserving
Goal, Acceptance, authored order and Evidence of finished parts. Use the worker
handoffs in the coordinator chat, not a counter file, then resume normal grouping
and review.

An unrelated user instruction may go to the active worker to preserve the sole
writer, but identify it separately in the Plan update and commit description or
commit it separately.

## Results

Return a normal concise message with an explicit status and the facts needed to
assess or continue: completed effects, relevant changed paths, decisive checks,
unverified behavior and next action if work remains. No marker, fixed field order,
JSON or change flags are required.

Worker statuses: completed, blocked, needs_user_decision, context_handoff.
Reviewer statuses: pass, changes_requested, blocked, needs_user_decision,
context_handoff. A pass has no unresolved findings. Findings identify the defect,
location, effect and smallest correction. A handoff distinguishes finished and
unfinished work; never turn unavailable evidence into success.

## Archive

After receiving a completed worker result, the coordinator calls
`send_message_to_thread` for that worker with "Job done. Archive yourself. Call set_thread_archived with archived=true for your own chat as your last action."
as `prompt`. Each completed assignment ends that chat; later
work or another correction uses a new worker chat. After receiving the reviewer's
complete assessment, send it the same archival message without a question round.
For rollover, the successor instead confirms receipt and releases the predecessor.
The recipient calls set_thread_archived on itself as its last action. No further
reply, status check or archival audit is needed. Report a returned tool error;
an open sidebar entry alone does not block accepted work. The final coordinator
stays visible.

## Stop and resume

On a user stop, dispatch no new work. Forward the stop to the active child and
establish whether it actually stopped. If the host cannot interrupt it, tell the
user which chat needs stopping. Archiving is not stopping project work.

After an interruption, reconstruct only missing current facts from the Plan,
handoff, relevant files and known chats. A final answer may contain a result whose
delivery failed. Recover that result rather than redoing its work. If creation
or writer state is uncertain, inspect that known task before starting another
writer. Do not turn a timeout into a second dispatch. Continue from the first
unfinished action, preserving open findings and user decisions.
