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
Then return the normal `completed`, `pass` or `changes_requested` result and stop writing.
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
and launched model and reasoning effort, the compact handoff, and agent IDs of predecessor and manager.
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
If a mismatch, uncertain state, user stop or unanswered decision prevents
release, the manager sends STOP for a stop, or BLOCKED otherwise, to that exact
successor. The successor accepts either signal only from that exact manager,
remains write-inactive and returns a blocked result with the signal and reason
to the manager. It does not keep waiting after that signal.
The successor uses bounded `collaboration.wait_agent` calls until this exact manager releases
it. A wait timeout alone does not end the wait or authorize project work.
Only TAKEOVER_COMPLETE permits work; STOP or BLOCKED halts the transition.
After release it finishes the remaining assignment and returns its complete
native final to the manager.
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

Retain a compact substantive handoff locally with:

- The exact workspace and Plan path, requested scope and exact project display name.
- The unchanged run-report path and open issue IDs, including each pending user
  question, its source identity and whether its answer has arrived.
- Checked effects and evidence limits, plus pending reviews and findings.
- Child IDs and whether each child is writing or stopped.
- The next worker number and any recovery context.
- Constraints, coordination authority and the next action.

Keep a received answer; never
repeat a question solely because of takeover. The consumed checkpoint boundary
must be named so the successor resumes its pending action rather than rechecking.
Follow [manager protocol](manager-protocol.md) for the successor request,
direct handoff, verification, receipt and release. Read it before requesting
rollover; the successor reads it at entry. The predecessor's first action is
SUCCESSOR_REQUEST with its own ID and launched pair, then an active write-inactive
wait. The successor requests the direct handoff only after authenticated START.
Keep substantive facts out of the runner. The shared protocol owns all gates,
post-snapshot input and later read-only predecessor clarification.
