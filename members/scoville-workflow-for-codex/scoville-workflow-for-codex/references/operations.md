# Execute the requested scope

The caller is the coordinator. There is no launcher task or parked worker.
At startup or resume, read the canonical Plan and `.scoville/workflow.md`.
Keep `.scoville/workflow.md` and `.scoville/handoffs/` local and never commit
them; `.scoville/config.json` may be versioned. Remove completed run state only
after retaining results and finishing any pending handoff. Keep unfinished
state for resume.
An existing child must be reconciled by its retained exact task/host ID before
a new one starts. A saved result is evidence only for what was actually observed.
Read each necessary source once per unchanged unit. Recover from the run record
and canonical Plan, not the predecessor's entire conversation. Fetch only a
specific missing fact. Do not relay child progress or inspect its changing files.
Announce a real dispatch, accepted result or blocker once, in one short sentence.
Before the first dispatch, state the Plan being executed, the selected Step
groups and why they belong together in one or two sentences. Use this as the
dispatch announcement; do not add a second explanation of the same choice.

Treat takeover messages as lifecycle notices, not role results. Match the actual
sender to the retained successor. A notice never accepts work or advances the Plan.

## One unit through acceptance

1. Select the next unfinished Step or consecutive Step group under dispatch.
   Check prerequisites and preserve authored order. A whole Work Item may be
   one group. Do not start a later group before accepting the preceding one.
2. Apply [dispatch](operations-dispatch.md). Record the intended dispatch, create
   the worker with its complete assignment, and retain the returned task ID.
   Pending IDs remain pending. An uncertain creation is reconciled, not retried.
3. Retain the returned task ID and obey any host-required wait for progress
   before ending this coordinator turn. Otherwise use the message-driven flow: the worker
   sends its result after all work and checks stop; that message resumes the
   coordinator. Add no polling loop, progress relay, reminders or inspection of changing
   files. This idle interval is not Plan completion. Do not insert narration
   between successful deterministic calls; required host updates stay brief.
4. Match the message's actual sender task ID to the pending unit and role.
   Read SCOVILLE_RESULT_V1 directly from that message, without a status call,
   read_thread or parser invocation. Check the role, allowed status and required facts below. A reviewer pass
   must not contain unresolved findings. Tolerate field order, whitespace,
   fences and other cosmetic differences when the meaning is clear.
   Reject missing, conflicting or ambiguous required facts; do not invent them. Retain the original result and next action before
   acceptance or archival. Only missing or ambiguous required facts warrant one clarification in the
   same task, without further source changes; unresolved facts stay blocked.
   A message already retained for this pending assignment is not accepted twice.
   Missing delivery is recovered from the known task on a host completion event,
   actual resume or user intervention, never through a periodic check.
5. Handle `context_handoff` through [rollover](operations-rollover.md) before
   review or acceptance. `needs_user_decision` remains open for the answer.
   For `blocked` or a native failure, preserve the changes and actual diagnostic.
   Continue independent eligible work only if it cannot mix unaccepted changes,
   invalidate required backups or advance a dependent Plan item.
6. Inspect the actual scoped diff, changed paths and named checks only as needed
   for scope, review and Acceptance decisions. Do not routinely repeat the
   worker's diagnosis, tests or the reviewer's review. Review is
   required for code, executable/configuration changes, critical documentation,
   an explicit requirement or unresolved materiality. The worker's yes/no
   fields help identify the boundary but never override the observed diff.
   Routine documentation with two consistent no values may skip review.
7. When needed, directly create one fresh read-only reviewer for the same unit,
   using its configured pair and the worker result. For `changes_requested`,
   handle Plan-owned corrections in the coordinator and send only source-owned
   findings to a fresh repair worker. Repair 1 uses the original executor pair;
   repairs 2 and 3 resolve upward from that original pair in the current route
   table. Rollover never consumes a repair. Create no fourth repair.
8. Check corrections against every retained finding. Code, critical-documentation
   or material corrections, explicit requirements and unclear outcomes require
   another review. A clearly non-material correction may be accepted after a
   bounded comparison, with the reason recorded. Unresolved findings after
   repair 3 require the user's disposition before further work on that unit.
9. Only after observed Acceptance and required review, update the canonical
   Plan through Scoville Plan, including concise evidence and the next action.
   Run its structural validator. With existing commit authority, inspect the
   staged diff and commit only accepted source changes together with the
   complete affected Plan records. Honor backups and hooks. Do not commit
   merely because Git is present, publish, or hide a failed check.
10. If requested work remains, run the coordinator checkpoint immediately after
    the accepted unit and before selecting or writing the next unit:

```text
python "<workflow-skill-directory>/scripts/check_context_checkpoint.py" --project-root "<workspace_root>" --role coordinator --accepted-unit <unit>
```

`rollover` requires [rollover](operations-rollover.md), with no next-unit work
in this coordinator. `continue` permits the next eligible unit. Report
unavailable telemetry without guessing occupancy or claiming a handoff.
Invalid configuration blocks continuation until corrected. A failed helper
is a failure, not an unavailable-signal result.

Accepting a Step group does not complete the Work Item. Continue with its next
unaccepted Step; complete the item only after all its work and Acceptance. Continue the requested scope
without another routine permission request. Only after all of its real work
and acceptance checks finish, complete the Plan/index through their owner and
mark the run record finished. Report a narrower boundary as that boundary.

## Result contract for direct acceptance

Required information: `SCOVILLE_RESULT_V1`, `role`, `status`, completed-result
flags and `summary`; `finding` is optional. Field order is not significant.
Executor/repair statuses: completed, blocked, needs_user_decision, context_handoff.
Reviewer statuses: pass, changes_requested, blocked, needs_user_decision,
context_handoff. Only completed executor/repair results require
`code_changed=yes|no` then `critical_docs_changed=yes|no`; other results omit them.
Keep summaries and findings concise. Do not count characters or request
restatements solely for formatting.
For completed/context_handoff, summary names effects, changed paths, decisive
checks and unverified behavior; handoff also names remaining work and unknowns.
A finding names an actual unresolved defect with location, mechanism, impact
and smallest fix. Omit the field when none exists; an explicit no-findings
value also means no finding and needs no correction.
These rules are
complete; do not inspect helper source or load a parser to accept a message.

## Archive once, after retaining the result

Retain the child's result or failure before archival. If native evidence already
shows it ended, call `set_thread_archived` directly once with its exact task/host
ID. No archival verification or confirmation is required.

If its turn end is not yet known, send one short self-archival request to that
child after retaining its result. Do not add a wait or status query just to
archive it. The child verifies the coordinator and self-archives once as its
last action. No reply is expected. Continue without a check, resend or additional
archive call. Report an explicit tool error if returned.

For `context_handoff`, first retain the successor's takeover notice under the
rollover reference, then use the same rule for the predecessor. Do not archive
unfinished work, a task awaiting a user decision or a requested stop before its
actual state is known. Archival is never a substitute for stopping work.
Do not add a final archival audit or scan unrelated chats. Keep the final coordinator
visible. Replaced coordinators self-archive on their successor’s takeover message under
the rollover reference.

## Stop and resume

`RESULT NOT DELIVERED` diagnoses missing delivery; it does not wake this task.
Do not claim automatic recovery without an observed host event or message.

On a user stop, dispatch no new work. Forward the stop to the exact active child
and observe its state. If sending does not interrupt the child, report that
fact and the exact task the user must stop in the UI. Never claim a cascade
that was not observed. Do not commit, review or archive to simulate stopping.
Retain completed effects, unaccepted changes and the next action. Reconcile the
Plan once the child's actual state is known.

On resume or compaction, recover the run record, the Plan, the actual diff and
any pending exact task. If delivery or completion is missing, make one targeted
read_thread or native status query for that known task; retrieve only the
missing result or state. Persist a recovered result before accepting it.
Unknown creation or a still-running task remains pending: do not recreate it,
start a second writer or loop. A failed send may leave the result in the
worker's final answer. Continue from the first unperformed action. Do not
repeat accepted work, recreate an unresolved child or upgrade an active old
runtime contract in place.
