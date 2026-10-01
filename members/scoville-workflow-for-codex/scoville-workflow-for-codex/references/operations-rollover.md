# Automatic context rollover

The checkpoint reads current-task telemetry and configured thresholds.
Coordinator comparison is at-or-above; child comparison is strictly above.
Crossing a threshold schedules rollover. Finish the complete current assignment,
including its required corrections and checks, before handing over. This applies
to managers, workers, reviewers and repair workers. A user stop still takes effect
immediately. Missing decisions and helper failures retain their blocking rules.

## Child rollover

After a bounded work-and-check batch, checkpoint only if assigned work, a
correction or a required check remains. After the last required check, return
the normal role result without another checkpoint, even above the threshold.
The coordinator's later review and Plan closure are not unfinished child work.
Failed checks also end a batch.
Check before a command expected to add substantial context unless just checked
with no material growth. Finish running operations first. Save large outputs to
a file; read the exit status, summary and relevant failures.

`continue` resumes work. Missing telemetry also continues without guessing.
`rollover_pending` records a measured threshold crossing but does not end or
shorten the assignment. Retain it across compaction and finish the assigned Step
or Step group, review or repair, including required corrections and checks.
Then return the normal completed/pass/changes_requested result and stop writing.
Include the retained measurement when needed for rollover evidence. Do not return
context_handoff with unfinished assigned work merely because of the threshold.

Each later assignment already uses a fresh child. Its predecessor's completed
result is the quiescent boundary, so no separate child context_handoff or
unfinished-work successor is required for a measured threshold crossing.

## Authorized recovery handoff

The continuation interface remains available for an explicitly authorized
transfer of unfinished work. A context threshold alone never authorizes it.
Retain finished parts, changes, checks, unresolved facts, constraints and the next
action, and confirm the predecessor has stopped writing before any successor.

After retaining a child handoff and confirming its work has ended, the manager
runs its checkpoint only at the completed manager-unit boundary below. A recovery
handoff does not complete that unit or authorize manager rollover. Resume its
remaining work first, preserving the pending handoff and exact agent ID.
A context_handoff alone does not trigger review, but a checked product fix in
that handoff follows the review cadence before dependent work continues.

The manager spawns a successor with the same role, remaining scope, workspace
and launched model/effort, the compact handoff, and predecessor/manager agent IDs.
Supply only unfinished work, applicable acceptance, constraints, completed effects
with evidence limits, required paths and next action. Preserve user permissions
and stops. Do not resend the complete Work Item or completed instructions. The
manager checks this selection against the canonical item before dispatch.

The predecessor has already delivered its native final and stopped writing.
The successor retains the supplied information and sends
`HANDOFF_ACCEPTED <predecessor-id>` to its exact spawning manager. Never send a
routine receipt to the completed predecessor. Missing essential facts go to the
manager before project work. Failed delivery blocks takeover with its diagnostic.

The manager accepts this receipt only from the exact newly spawned successor,
with the retained predecessor ID. Require the completed native handoff, confirmed
writer quiescence, applicable authorization and no stop or unanswered decision.
Only then send TAKEOVER_COMPLETE to that successor. Ignore duplicate receipts
already handled. A mismatch or uncertain state blocks without releasing work.
The successor waits actively for this exact manager's release, at most 60 seconds,
before project work. Missing release or STOP is BLOCKED. After release it finishes
the remaining assignment and returns its complete native final to the manager.
The predecessor stays write-inactive. No chat, archival or close tool is needed.

## Manager rollover

The checkpoint's `coordinator` role means the manager. At or above the configured
manager threshold (default 40%), schedule rollover at the next completed unit
boundary. Complete the selected Step or Step group, including required checks,
due reviews, repairs, Plan updates and authorized commits, then stop project
writes. Retain the complete child results and confirm all children are quiescent.
Do not interrupt or transfer unfinished assignments to turn over the manager.
Child thresholds remain strictly above their configured value (default 60%). Missing or stale telemetry
means continue without inventing a measured boundary or claiming a switch.
Retain a measured crossing across compaction. A decision or blocker that prevents
the current unit's completion also prevents its threshold-driven handoff.

Retain a compact substantive handoff locally: exact workspace and Plan path,
requested scope and its display wording, exact project display name and saved
scope-file path, unchanged run-report path and open issue IDs/answer states,
checked effects and evidence limits, pending review/findings,
child IDs and write/stop states, next worker number, recovery context if any,
constraints, coordination authority and next action. Include any pending
user question, answer state and source identity. Keep a received answer; never
repeat a question solely because of takeover. The consumed checkpoint boundary
must be named so the successor resumes its pending action rather than rechecking.
Send the runner only `SUCCESSOR_REQUEST <own-agent-id>` plus the explicit manager
model/effort if one is in force. If the runner needs your launched pair because
its own settings changed, return that pair from known host metadata, never a
worker default. Request once, then stop writing and wait with `wait_agent`. The
runner alone builds and spawns the successor under SKILL.md. Never send the
handoff file, Plan state or worker result to the runner. No new chat, self-spawn,
model guess, assumed agent capacity or invented close tool is permitted.

The runner sends `SUCCESSOR <new-id>`. Accept HANDOFF_REQUEST only from that exact
host sender identity. Send the substantive handoff directly with `send_message`
to the successor. After successful delivery send only `HANDOFF_DELIVERED` to the
runner. Stay active and write-inactive with `wait_agent` until HANDOFF_ACCEPTED
arrives from that exact successor, handling necessary direct clarifications first.
Wait at most 60 seconds for the receipt. Only after that receipt end with the
control-only final `HANDOFF_DELIVERED`. Native completion exposes this response
to the runner. Keep substantive details in the direct handoff. A failed delivery,
missing receipt or user stop blocks the transition with its concrete control
status. Never end successfully before receipt or claim failed delivery as success.

After its matching START, the successor requests this handoff directly. It must
receive it, compare it against the canonical Plan and actual relevant files,
and verify that the handoff report path matches the supplied run-control
path. Preserve issue entries and received clarifications. Resolve missing or
conflicting facts with the predecessor before its first
write or child dispatch. Confirm children are quiescent, preserve review/commit
boundaries, user stops and unanswered questions. Do not redo completed checks.
Only after verification send HANDOFF_ACCEPTED directly to the predecessor and
RUNNING to the runner. Remain active with `wait_agent` until TAKEOVER_COMPLETE
from the exact runner, at most 60 seconds. Do no writes or child dispatch before
that gate. It confirms the predecessor's native completion as well as your
verified receipt. A rejection, missing fact or uncertain child state is BLOCKED,
even if START was received. Retired predecessors stay write-inactive. No archival
or close tool is required, and routine acknowledgements never go to a completed
predecessor. For a later essential question ask the runner to wake that known
predecessor with `followup_task` for direct clarification, preserving these roles.

Tool failure, a missing/mismatched handoff, uncertain writer state or conflicting
facts blocks takeover. Send only the concrete BLOCKED control to the runner and
do no project work. Resolve recoverable missing facts directly, not through the
runner. On stop, both managers stop their children and report their actual state.
No replacement manager starts while a prior spawn or writer state is unknown.
