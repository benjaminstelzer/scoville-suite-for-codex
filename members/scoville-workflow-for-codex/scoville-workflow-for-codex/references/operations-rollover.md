# Automatic context rollover

The checkpoint reads fresh telemetry for the current runtime task ID. Its
thresholds come from `.scoville/config.json` or imported Skill defaults.
Coordinator comparison is at-or-above; worker comparison is strictly above.
Worker rules also apply to reviewer and repair roles. Native compaction and a
saved record do not replace creation and continuation in a new task.

## Worker, reviewer or repair

While assigned work remains, run the supplied checkpoint after each bounded
implementation-and-check, review, or UI-check batch, before starting another
correction or check batch. Failed checks also end a batch. Finish any running
operation first. Checkpoint before commands expected to add substantial context unless
just checked with no material context growth since. Save large output to a file with the exit
status; read failures and a summary first, then relevant details as needed. When assigned work and checks are complete, return the normal
role result without another checkpoint. Pending coordinator review and
acceptance are not unfinished child work.

A `continue` outcome resumes the remaining bounded work. Unavailable telemetry
also continues bounded work without estimating occupancy or searching manually
for telemetry. A `context_handoff` outcome returns the normal role result with
that status and ends the task. Run no further test, correction or checkpoint
after that outcome; put the next action in the handoff for the successor.

`context_handoff` means: retain completed effects, current state,
checks, unresolved facts and a concrete remaining assignment, return that status
and end. Identify finished Steps or parts and the next unfinished action.
A longer handoff may be a Markdown file named in the result.

The context_handoff message reports that project work has stopped. The
coordinator retains it and creates one successor without waiting for a native
turn-end event: same role, unit, workspace,
launched model/effort and logical attempt, with the complete Work Item, its relevant supplied constraints
and the short handoff. Do not restart completed work or consume a repair
attempt. Use the next counter for that role in its title while keeping the
unit. Save the new task handle. The successor reads the handoff, checks the relevant current files and sends
one short takeover notice to the coordinator before continuing the remaining work. Match its actual sender
to the retained successor, then archive the predecessor through the ordinary
archival rule. No takeover polling. Pending creation alone is not takeover.
Reconcile an unresolved creation, never recreate it. The predecessor performs
no further project work after handing off.

## Coordinator

At an accepted-unit boundary with work remaining:

1. Save accepted Plan state and the continuation in `.scoville/workflow.md`:
   same run, Plan, scope, project, role counters, predecessor task/host ID,
   retained results, next unit/action and unresolved handles. Assign the next
   coordinator counter and mark successor creation pending. Finish all project
   writes before creating the successor.
2. Create the successor in the same saved project with the same launched
   model/effort and next coordinator title. Its short prompt gives the exact
   installed Skill path, run-record path, predecessor task/host ID and next unit.
   Tell it to resume that record and request the predecessor's self-archival
   after takeover. Carry the user's existing internal-message authorization
   with the continuation, preserving its scope. Do not repeat Plan history or
   carry the predecessor chat.
3. After create_thread, the predecessor makes no project writes and dispatches
   no work. Keep the returned identity in the native tool result, satisfy any
   host-required wait for progress and end the turn. An uncertain creation is
   reconciled on recovery, never recreated.
4. The successor checks the saved run, workspace and predecessor against its
   assignment, records its own actual task/host ID and continues the saved run.
   Send one short takeover message to that predecessor: identify this run and
   request self-archival. No additional archival wait, status check, predecessor
   read or end-of-turn handshake is needed: the predecessor stopped project writes
   before creation. Never repeat completed work.
5. The predecessor accepts the request only from the actual created successor
   for this run. Call set_thread_archived once on its own exact task/host ID as
   its last action. Make no project writes and never resume coordination.
   No confirmation message or archival check follows. The successor continues
   without waiting, checking or making an additional archive call.

These native messages are part of the authorized Workflow coordination. The
final coordinator stays visible. A failed creation or delivery remains an
explicit incomplete handoff; targeted recovery of a known task is allowed.
Do not present compaction or a saved record as a completed rollover.
