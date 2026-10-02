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
scope-file path in the direct manager handoff. After saving and validating Plan
progress, generate before every worker dispatch or resumption:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" progress --project "<project-name>" --plan PLAN-0025 --point W-001/step-2 --scope-file "<scope.txt>"
```

Send `WORKING_ON <key>` followed by the returned `text` to the runner with
`send_message`. Require successful send output before writing dispatch or
resumption. On failure or uncertain delivery, retain the point and generated
payload, report BLOCKED with the diagnostic and keep that release stopped.
Use only these generated display fields. The point is the
actually started Step or jointly started group just recorded and released, such
as W-001/step-2. Never substitute the complete assigned range or a bare Work Item
when it has Steps. A Step-less legacy item uses its Work Item ID. Scope describes
the entire user assignment, such as finishing W-003 through W-006.

The runner accepts progress only from its current STARTed manager. Process each
received progress message in order, including a batch containing a question or
blocker, before waiting again:

1. Validate sender and retained project/scope values.
2. If the key differs from the last visibly displayed key, print exactly the two
   generated display lines, without replacing them with a summary.
3. Only after that visible output, retain the key as displayed. Receiving a
   message alone does not advance it.

Keep that displayed key across takeover and stop/resume. The same key prints
nothing, including
review, repair, repeated notifications and a changed scope at the same point.
The manager retains an authorized scope change for the next point display.
Successful delivery permits writer release; it does not confirm visible display.
On cosmetic project/scope drift, request regeneration from the retained values
and keep that key undisplayed until its corrected message arrives. The manager
resends promptly; cosmetic correction changes only the display if work is already
released. A substantive scope conflict stops dependent work until clarified.
Never repair helper output manually. Managers omit `--previous-key` for WORKING_ON:
always send both generated lines and let the runner deduplicate visible output.

## Targeted issues

The manager promptly sends every necessary user decision or blocking
condition to the runner, whether it arises in a child message/result, its own
work, a helper failure, or takeover. Stop dependent work first. Send
`NEEDS_USER_DECISION` with the canonical Plan ID and affected Step/group, exact
question, why an answer is needed and what is waiting; send `BLOCKED` with that
location, actual diagnostic,
why work cannot continue and the necessary next action. Report the affected
scope, not a whole-run halt when independent authorized work can continue.
Do not wait for final child results, unrelated checks or the next progress key.
Children ask their manager, never the user directly. The runner authenticates
the current or exact pending manager under the takeover rules and visibly states
the Plan ID, affected Step/group, question or diagnostic, reason, and waiting or
blocked state; it alone presents the user question. Startup issues use Startup
until the canonical location is known. Retain each issue's manager identity for
answer routing, including during takeover.
A saved report or manager-only commentary is not a relay. Suppress only an
identical already-visible pending issue, never a new question or changed cause
because WORKING_ON is unchanged. Forward an actual answer once to the manager;
no elapsed time, timeout or unrelated answer resolves the pending issue.

Only record a user question, a point paused for a user request, or a problem
requiring user inspection. Record the affected point and actual question or
needed action. Ordinary reviews, self-corrected checks, progress and successful
results create no entry. Children return needed facts to the manager and do
not write this file. The current manager is its sole writer. Relay immediately,
independently of persistence. Save the issue and any received answer before
dependent work resumes, when the current report owner can safely write.

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
STOPPED. While writes are prohibited, retain and relay the unsaved issue with
the reason it cannot yet be saved. A pending successor keeps it unsaved until
TAKEOVER_COMPLETE makes it the current owner. For a report-write failure, retain
and relay the issue with the exact save diagnostic, marking it unsaved.
Keep dependent work stopped until persistence and any necessary answer are
secured; saving the report or Plan must never hide the
condition from the runner. An unknown write outcome requires
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
