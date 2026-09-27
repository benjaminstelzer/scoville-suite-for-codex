# Execute the requested scope

The caller is the coordinator. There is no launcher task or parked worker.
At startup or resume, read the canonical Plan and `.scoville/workflow.md`.
Keep `.scoville/workflow.md` and `.scoville/handoffs/` local and never commit
them; `.scoville/config.json` may be versioned. Remove completed run state only
after retaining results and finishing any pending handoff. Keep unfinished
state for resume.
An existing child must be reconciled by its retained exact task/host ID before
a new one starts. A saved result is evidence only for what was actually observed.
Reuse loaded, unchanged rules and selections across roles. Recover from the
run record and canonical Plan; read a predecessor chat only for a named missing
fact that the handoff and current files cannot supply. Do not relay child
progress or inspect its changing files.
Announce a real dispatch, accepted result or blocker once, in one short sentence.
Before the first dispatch, state the Plan being executed, the selected Step
groups and why they belong together in one or two sentences. Use this as the
dispatch announcement; do not add a second explanation of the same choice.

Treat takeover messages as lifecycle notices, not role results. Match the actual
sender to the retained successor. A notice never accepts work or advances the Plan.

Keep the run record current, not chronological. When retaining a transition,
replace the affected role counter, unit state, active handle and next action
together. Write related cursor changes and any due Plan updates together where possible.
For child creation, keep the required pre-dispatch intent and returned handle
as separate writes; omit other intermediate progress writes. Keep past results in their retained files or Plan evidence, with only
still-needed references in the cursor. Do not add a separate consistency check.
At run completion, mark the unit and run finished and clear the active role and
child; leave no executing role in the finished cursor.

## One unit through acceptance

Follow the user's or project's review cadence. Otherwise review the complete
Work Item at its completion boundary. A Step group is an execution boundary,
not automatically a review boundary. Keep checks with each group; retain its
result and continue in order while final review remains pending. Review newly
unreviewed changes, their interaction and outstanding Acceptance. Reuse accepted
evidence for unchanged parts. An explicitly required intermediate review still
applies. Do not mark the Work Item done or commit unreviewed source changes.

1. Select the next unfinished Step or consecutive Step group under dispatch.
   Check prerequisites and preserve authored order. A whole Work Item may be
   one group. Do not start a later group before its prerequisites and the
   preceding group's checks pass. This permits continuation, not final acceptance.
2. Apply [dispatch](operations-dispatch.md). Record the intended dispatch, send
   the complete assignment to the eligible existing worker or create one, and
   retain its exact task ID. Keep a reusable source-worker handle while review runs.
   Pending IDs remain pending. An uncertain creation is reconciled, not retried.
3. After dispatch, use the message-driven flow: the worker
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
   Keep transient diagnostics in the local run record; Plan Evidence needs only
   their unresolved blocker or effect on Acceptance. Retry a known failed start
   only when its cause permits it; never retry an uncertain creation or delivery.
   When replacing that child, archive it through the rule below as part of the
   replacement. Keep it open if the same child will continue after clarification.
   Continue independent eligible work only if it cannot mix unaccepted changes,
   invalidate required backups or advance a dependent Plan item.
6. Inspect the actual scoped diff, changed paths and named checks only as needed
   for scope, review and Acceptance decisions. Do not routinely repeat the
   worker's diagnosis, tests or the reviewer's review. At the applicable review
   boundary, review is required for code, executable/configuration changes, critical documentation,
   an explicit requirement or unresolved materiality. The worker's yes/no
   fields help identify the boundary but never override the observed diff.
   Routine documentation with two consistent no values may skip review.
   The coordinator never edits product files, including mechanical formatting
   fixes. Send source defects through the existing review/repair path; do not
   accept or commit them as corrected until that role returns the correction.
7. When review is due, create one fresh read-only reviewer for its complete
   scope, using its configured pair and the retained worker results. For `changes_requested`,
   handle Plan-owned corrections in the coordinator and send only source-owned
   findings back to the available worker when its configured pair matches the
   required repair pair and context permits. Send the complete repair assignment
   to that exact chat, retain its handle under the repair role, and leave no
   other source writer active. Otherwise create a repair worker. Repair 1 uses the original executor pair;
   repairs 2 and 3 resolve upward from that original pair in the current route
   table. Rollover never consumes a repair. Create no fourth repair.
8. Check corrections against every retained finding. Code, critical-documentation
   or material corrections, explicit requirements and unclear outcomes require
   another review. A clearly non-material correction may be accepted after a
   bounded comparison, with the reason recorded. Unresolved findings after
   repair 3 require the user's disposition before further work on that unit.
9. Record checked intermediate results and the next action through Scoville Plan
   without claiming final Acceptance. Only after observed Acceptance and required
   review accept the complete Work Item. Keep evidence concise with a report link,
   not task IDs or attempt histories.
   Run its structural validator. With existing commit authority, inspect the
   staged diff and commit only accepted source changes together with the
   complete affected Plan records. Honor backups and hooks. Do not commit
   merely because Git is present, publish, or hide a failed check.
10. If requested work remains, run the coordinator checkpoint after a checked
    group or accepted Work Item and before selecting or writing the next unit.
    The existing --accepted-unit argument identifies that boundary; it does not
    declare final acceptance. Retain pending review in the cursor:

```text
python "<workflow-skill-directory>/scripts/check_context_checkpoint.py" --project-root "<workspace_root>" --role coordinator --accepted-unit <unit>
```

`rollover` requires [rollover](operations-rollover.md), with no next-unit work
in this coordinator. `continue` permits the next eligible unit. Unavailable or
stale telemetry returns `continue`: retain this coordinator and select the next
eligible unit without estimating occupancy or searching manually for telemetry.
Invalid configuration blocks continuation until corrected. A failed helper is
a failure, not an unavailable-signal result.

Finishing a Step group does not complete the Work Item. Continue with its next
unfinished Step; complete the item only after all its work, review and Acceptance. Continue the requested scope
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
shows that a source worker can perform the next related group or pending repair,
keep it available and reuse it with the complete new assignment. Archive it when
it is replaced or no longer needed; pending final review may still need it.
For a child that is no longer needed, if native evidence already
shows it ended, call `set_thread_archived` directly once with its exact task/host
ID. No archival verification or confirmation is required.

If its turn end is not yet known, send one short self-archival request to that
child after retaining its result. Do not add a wait or status query just to
archive it. The child verifies the coordinator and self-archives once as its
last action. No reply is expected. Continue without a check, resend or additional
archive call. Report an explicit tool error if returned.

For `context_handoff`, first retain the successor's takeover notice under the
rollover reference, then use the same rule for the predecessor. Do not archive
a child still working, awaiting a user decision, or whose state after a requested
stop is unknown. An unfinished Work Item does not keep a replaced child open.
Archival is never a substitute for stopping work.
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
any pending exact task. If delivery or completion is missing, recover only the existing result/state
from the known task. Prefer one read_thread or native status query to avoid
an extra turn. A scoped message requesting that same result uses the existing
run authorization too; it must not restart work or change the assignment.
Persist the recovered result before accepting it.
Unknown creation or a still-running task remains pending: do not recreate it,
start a second writer or loop. A failed send may leave the result in the
worker's final answer. Continue from the first unperformed action. Do not
repeat accepted work, recreate an unresolved child or upgrade an active old
runtime contract in place.
