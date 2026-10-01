# Run feedback

Use the same absolute report path supplied at every manager start. A successor
verifies that its direct handoff names that file. Keep the actual overall scope
as free text through handoffs and steering. No report or display invents scope.

## Progress

After startup checks, choose the actual project display name once and save the
actual overall user assignment as UTF-8 free text in the workspace temporary
area. Reuse that exact project name and scope file for each selected unit,
including repairs, stop/resume and manager changes. Only an actual user change
may replace these values. On recovery, reread the saved scope, not the Plan Goal,
directory name or Plan title. Carry the exact project name, overall scope and
scope-file path in the direct manager handoff. Generate before dispatch:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" progress --project "<project-name>" --plan PLAN-0025 --point W-001/step-2 --scope-file "<scope.txt>"
```

Send `WORKING_ON <key>` followed by the returned `text` to the runner with
`send_message`. Use only these generated display fields. The point is the
selected Step/range or whole Work Item, not an invented counter. Scope describes
the entire currently assigned goal, such as finishing W-003 through W-006.

The runner accepts messages only from its current STARTed manager. It keeps the
last displayed key, including across takeover and stop/resume. A different key
prints exactly the two display lines. The same key prints nothing, including
review, repair, repeated notifications and a changed scope at the same point.
The manager retains an authorized scope change for the next point display.
Regenerate cosmetic display drift from retained project/scope values; clarify
a substantive conflict before dependent work.
The progress helper also supports `--previous-key <last-key>` and returns
`changed: false` with empty `text` for the same project/Plan/point.

## Targeted issues

Only record a user question, a point paused for a user request, or a problem
requiring user inspection. Record the affected point and actual question or
needed action. Ordinary reviews, self-corrected checks, progress and successful
results create no entry. Children return needed facts to the manager and do
not write this file. The current manager is its sole writer.

Save the relevant free text in a UTF-8 temporary file and run:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" add --report-file "<run-report.md>" --kind question --location "PLAN-0025 / W-001/step-2" --text-file "<question.txt>"
```

Kinds are `question`, `pause` and `problem`. Retain the returned `issue_id` with
the pending question or pause. `--issue-id <retained-id>` permits an identical
retry without another entry; a different issue under that ID is rejected.
After the actual answer, resume or resolution is received, append it:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" resolve --report-file "<run-report.md>" --issue-id <retained-id> --text-file "<clarification.txt>"
```

The original issue stays, its status becomes Resolved and the clarification is
appended. Repeating the same clarification changes nothing. A clarification
does not authorize work beyond the user's actual answer. Dependent work remains
paused while a necessary answer is absent. Preserve entries and IDs in the
direct manager handoff. Never erase resolved issues to make a run look clean.

For a stop, establish child/writer quiescence first, then record the pause before
STOPPED. For a report-write failure, retain the unsaved issue, report the exact
diagnostic and halt the affected operation. Show a necessary question even if
its report save failed, marking it unsaved. An unknown write outcome requires
reading the existing report before retrying. Never accept partial helper stdout.

If startup fails before a manager can own the report, the runner records the
user-relevant startup problem at `Startup` using the same helper. Otherwise
managers own report edits. No uncertain writer state permits a second writer.

## Completion

Only after the requested scope passes acceptance and required closure:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" finish --report-file "<run-report.md>" --completed
```

An empty report becomes exactly `No issues occurred during this run.`. Existing
issues and resolutions stay unchanged. Open questions blocking acceptance,
stops, blockers and handoffs never use finish or send COMPLETED. File failure
is BLOCKED and cannot acknowledge completion. Finish itself checks the file,
not Plan acceptance. The manager owns that decision.

On a valid COMPLETED from the current manager, keep the runner completion phase
open until that manager's actual native final and confirmed child/writer
quiescence. A control message alone is not the end of the run. Then read the
retained file with `run_feedback.py read --report-file "<run-report.md>"`. Require success
and a nonempty report before announcing `Completed: <actual assigned scope>`.
Then output `Run report: <absolute-path>` and the complete returned `text`.
A failed or empty read reports the problem and leaves completion unconfirmed.
Only after successful output does the runner role end. Do not replace this
helper operation with a direct file read or start a normal-assistance audit first.
Read only on a requested inspection or completion, never as a progress poll.
The runner's key and report path survive stop/resume. A new completed-run
activation creates a new file and starts with no previous display key.
