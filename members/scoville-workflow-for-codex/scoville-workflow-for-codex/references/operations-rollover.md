# Automatic context rollover

The checkpoint reads current-task telemetry and configured thresholds.
Coordinator comparison is at-or-above; child comparison is strictly above.
The worker rules apply to worker and reviewer.

## Child rollover

While assigned work remains, run the supplied checkpoint after each bounded
work-and-check batch, including failed checks, before starting the next batch.
Check before a command expected to add substantial context unless just checked
with no material growth. Finish running operations first. Save large outputs to
a file; read the exit status, summary and relevant failures. Completed assignments
return their normal result without another checkpoint.

`continue` resumes work. Missing telemetry also continues without guessing.
`context_handoff` stops project work and returns a short handoff: assignment,
finished parts, relevant changes and checks, unresolved facts, constraints and
next action. Do not perform another correction or check after handing off.

After retaining a worker handoff, the coordinator runs its checkpoint before
creating the successor. If rollover is due, hand over the coordinator first,
including the pending worker handoff and predecessor ID. The new coordinator
then handles any due review or Step split before creating the worker successor.
A context_handoff alone does not trigger review, but a checked product fix in
that handoff still follows the review cadence before dependent work continues.

The coordinator creates the successor with the same role, remaining scope, workspace and
launched model/effort, the complete Work Item and its still-relevant constraints,
the handoff, and predecessor/coordinator chat IDs. The successor sends directly
to the predecessor: "I have the information. You can archive yourself now."
Then it continues the unfinished work and sends its result to the coordinator.
The predecessor self-archives after that message. No coordinator relay or extra
confirmation is needed. The predecessor does no further project work.

## Coordinator rollover

At a checked boundary or retained worker handoff, finish due Plan updates and stop project writes.
Create the successor in the same project with the same launched model/effort.
Its assignment includes the Skill path, Plan/current unit, requested scope,
completed effects, pending review/results, needed chat IDs and worker numbering,
handoffs relevant to a pending Step split, relevant
constraints and next action. Carry the user's existing coordination authority.
Keep this handoff as short as possible and only as long as needed to continue.

The successor reads the handoff and replies directly to the predecessor:
"I have the information. You can archive yourself now." The predecessor calls
set_thread_archived on itself as its last action. The successor continues without
waiting for archival. No cursor file or additional acknowledgement is required.

Failed creation or delivery leaves an unfinished transition recoverable from
the known chats. Use the ordinary stop/resume rule; do not restart completed work.
