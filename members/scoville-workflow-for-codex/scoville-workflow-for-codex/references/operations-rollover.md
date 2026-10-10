# Automatic context rollover

The checkpoint reads current-task telemetry and configured thresholds.
Coordinator comparison is at-or-above; child comparison is strictly above.
Crossing a threshold schedules rollover. Managers finish their selected Step or
Step group through acceptance and closure. Reviewers finish their review.
Executors, including correction workers, use the safe boundary below.
A broader assignment does not add later unreleased Steps to that unit.
A user stop still takes effect immediately. Missing decisions and helper
failures retain their blocking rules.

## Child rollover

After a bounded work-and-check batch, checkpoint only if assigned work, a
correction or a required check remains. After the last required check, return
the normal role result without another checkpoint, even above the threshold.
The coordinator's later review and Plan closure are not unfinished child work.
Failed checks also end a batch.
Check before a command expected to add substantial context unless just checked
with no material growth. Finish running operations first. Follow the shared
writing rules for complete output capture and exit status before display.
Reviewers do not write captured source output or diffs for their own reading;
The child role contract permits only necessary oversized-result preparation
and publication. Follow the shared complete-file procedure.

`continue` resumes work. Missing telemetry also continues without guessing.
`rollover_pending` records a measured crossing. Retain its measurement across
compaction. A lower later reading does not cancel it.

An executor chooses the next safe boundary: finish the bounded change already
started, the dependent edits needed to leave coherent files, and its focused
checks. Finish running operations and capture their complete results. Start no
new independent task or broad check. A failed check ends a batch without proving
acceptance. Retain its failure and unfinished correction rather than starting
another repair, except stabilization needed to finish the started change.
At a quiescent boundary with work remaining, stop writing and return
context_handoff with completed effects, changed paths, checks and failures,
the retained measurement, remaining work, constraints, evidence limits and next
action. A checked prior-code fix uses review_pending first with those same
continuation facts. Its due review precedes dependent work and successor release.
No remaining work means the normal result, without another checkpoint.

Reviewers finish their current review, including required checks, then return
the normal result and any needed retained measurement. Their threshold alone
does not authorize transfer of an unfinished review.

## Authorized recovery handoff

The continuation interface remains available for an explicitly authorized
transfer of unfinished work, or an executor's retained measured crossing at the
safe boundary above. Neither condition completes the assigned manager unit.
Retain finished parts, changes, checks, unresolved facts, constraints and the next
action, and confirm the predecessor has stopped writing before any successor.

After retaining a child handoff and confirming its work has ended, the manager
runs its checkpoint only at the completed manager-unit boundary below. A recovery
handoff does not complete that unit or authorize manager rollover. Resume its
remaining work first, preserving the pending handoff and exact agent ID.
A context_handoff alone does not trigger review, but a checked product fix in
that handoff follows the review cadence before dependent work continues.

For a crossed review_pending result, retain its complete continuation facts as
the handoff source. Complete due review and corrections first. Supply review
acceptance and correction effects separately to the successor. Obtain a missing
fact without releasing the predecessor's writes or inventing it. The native
result and confirmed quiescence satisfy the predecessor handoff gate below.

The recovery sequence is:

```text
Predecessor native final + writer quiescence
  → manager verifies remaining assignment and spawns successor
  → successor reads complete assignment and sends exact HANDOFF_ACCEPTED
  → manager verifies receipt, authority and quiescence
  → TAKEOVER_COMPLETE → successor finishes remaining assignment
```

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
Do not interrupt or transfer unfinished work within the current unit to turn
over the manager. A broader assignment's accepted progress_pending group ends
that worker's allocation under operations.md; later groups use fresh workers.
Child thresholds remain strictly above their configured value (default 60%). Missing or stale telemetry
means continue without inventing a measured boundary or claiming a switch.
Retain a measured crossing across compaction. A decision or blocker that prevents
the current unit's completion also prevents its threshold-driven handoff.

Retain a compact substantive handoff locally with:

- The exact workspace and Plan path, requested scope and exact project display name.
- The unchanged run-report path and open issue IDs, including each pending user
  question, its source identity and whether its answer has arrived.
- Accepted results the next action depends on: scoped outcome, review identity,
  evidence path and open limits; plus pending reviews and findings.
- Child IDs and whether each child is writing or stopped.
- The next worker number and any recovery context.
- Constraints, coordination authority and the next action.

Do not carry old counts, hash inventories or resolved diagnostics unless the
next action depends on them. Bind each needed
hash to its exact file and field. Never guess a missing original source.

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
