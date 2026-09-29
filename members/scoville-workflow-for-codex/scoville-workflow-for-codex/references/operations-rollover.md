# Automatic context rollover

The checkpoint reads current-task telemetry and configured thresholds.
Coordinator comparison is at-or-above; child comparison is strictly above.
The worker rules apply to worker and reviewer.

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
launched model/effort, the compact handoff, and predecessor/coordinator chat IDs.
Supply only the remaining task, applicable acceptance criteria and constraints,
completed effects with evidence limits, required paths and next action. Preserve
user permissions and stops. Do not resend the complete Work Item, completed
implementation instructions or superseded requests. The coordinator checks this
selection against the canonical item before dispatch. Once the supplied handoff
contains the needed continuation information, the successor's first action is
the takeover message below, before ordinary reading or work. If an essential
fact is missing, recover only that fact first. The successor
calls `send_message_to_thread` with the predecessor's chat ID as `threadId` and
"I have the information. You can archive yourself now. Call set_thread_archived with archived=true for your own chat as your last action." as `prompt`.
Only after successful sending does it read referenced material and continue the
unfinished work. A forbidden or failed send stops takeover with its diagnostic;
do not silently skip it. It sends its eventual result to the coordinator.
The predecessor self-archives after that message. No coordinator relay or extra
confirmation is needed. The predecessor does no further project work.

## Coordinator rollover

At a checked boundary or retained worker handoff, finish due Plan updates and stop project writes.
Create the successor in the same project with the same launched model/effort.
Use the manager builder below. It reads this coordinator's own latest native
model/effort and sets both creation parameters, independent of worker/reviewer
routes and project defaults. An explicit user change overrides the inherited
pair through the builder's paired override arguments. If metadata is unavailable,
recover the known native rollout or stop with the diagnostic; do not guess.
Its assignment includes the Skill path, Plan/current unit, requested scope,
completed effects, pending review/results, needed chat IDs and worker numbering,
handoffs relevant to a pending Step split, relevant
constraints and next action. Carry the user's existing coordination authority.
Keep this handoff as short as possible and only as long as needed to continue.
Carry any pending user question, its scope, answer state and source chat ID.
Process an existing answer; do not repeat an unanswered question merely because
of rollover. If its state is unclear, inspect only that known question/answer.

Save those retained facts in a UTF-8 handoff file, then run:

```text
python "<workflow-skill-directory>/scripts/build_manager_handoff.py" --project-id <same-saved-id> --project-name "<exact saved project name>" --plan-id PLAN-NNNN --manager-number <next-number> --handoff-file "<handoff.md>"
```

For a manager scoped to one Work Item or Step range, add `--unit <exact-unit>`
so its title retains Plan, Work Item and Steps.
If the run owes a final report to another caller, copy its verified ID unchanged
into `--report-to-thread-id`; keep that destination out of free-form handoff text.
Describe the successor's next project action, not the predecessor's completed
manager-creation action. The rollover boundary is already consumed; the successor
does not recheck it after startup reading.
CODEX_THREAD_ID identifies the predecessor. Only if absent, supply its verified
ID with `--thread-id`. A known native log may be supplied with `--rollout`.
For an explicit user model change only, pass both `--override-model` and
`--override-thinking`. Never copy a worker/reviewer pair into those arguments.
Parse complete successful stdout as JSON and pass it unchanged to create_thread,
as in the dispatch reference, pinning the ready successor only when pin_threads is true. A failed or truncated output stops creation.
When false, omit the pin call and leave existing pins unchanged.
The builder includes the Skill path, manager title, own pair, predecessor ID and
takeover message at the very start, before any reading instruction. It preserves the supplied handoff verbatim;
the coordinator still selects and verifies its substantive facts.
The predecessor calls
set_thread_archived on itself as its last action. The successor continues without
waiting for archival. No cursor file or additional acknowledgement is required.

Failed creation or delivery leaves an unfinished transition recoverable from
the known chats. Use the ordinary stop/resume rule; do not restart completed work.
