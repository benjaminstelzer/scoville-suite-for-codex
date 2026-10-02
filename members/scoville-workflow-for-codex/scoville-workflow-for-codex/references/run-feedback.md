# Run feedback

The runner is the exact agent ID supplied in this manager's start assignment.
Send controls and issues only to that runner, never another project's runner or
a chat selected by title. Display questions and the final report in the original
runner chat. Children return messages and results to their spawning manager.

Use the same absolute report path supplied at every manager start. A successor
verifies that its direct handoff names that file. Keep the actual overall scope
as free text through handoffs and steering. No report or display invents scope.

`run_feedback.py` generates every visible status. WORKING_ON has only its status
line; blockers, questions, pauses and completion retain their explanatory body.
The manager copies its returned
`message` exactly into the native send argument. Its first line is a protocol
control, including the key for WORKING_ON. After authenticating the sender, the
runner removes that first line and copies the remaining Markdown (`text`)
exactly into its visible response under the applicable state rules. Preserve
its body, including plain paths; add no backticks, emphasis or rewording. Use
these generated messages without separate startup, handshake or
answer-forwarding status narration.

## Progress

Use the project name supplied at manager start through repairs, stop/resume and
handoff. Retain the actual user scope internally, never infer it from the Plan
Goal or title. Only user steering changes it. After saving and validating Plan
progress, generate before every writing dispatch or resumption:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" progress --project "<project-name>" --project-root "<workspace_root>"
```

Send the returned `message` to the runner with `send_message`. Require successful send output before writing dispatch or
resumption. On failure or uncertain delivery, retain the point and generated
payload, report BLOCKED with the diagnostic and keep that release stopped.
The manager-only mode reads the bundled select_context.py --position projection.
It uses the active in_progress Work Item and its single saved consecutive
in_progress Step/group, or a Step-less legacy item. Missing, unmarked or multiple
start groups fail with a diagnostic; reconcile observed progress and validate
before retrying. It neither selects nor starts work. Assignment labels may cover
a larger range. Display only `Working on: project → PLAN-NNNN → W-NNN/step-N`
as the generated bold line, with no Scope paragraph or other body.
The runner never invokes this mode or reads the Plan.

The runner accepts progress only from its current STARTed manager. Process
received messages in order before waiting again, including batches with issues.
Validate sender and retained project name. Display a changed key's text
before retaining that key as displayed. Keep it across takeover and stop/resume.
The same key prints nothing, including review, repair and scope changes at that point.
Successful delivery permits writer release; it does not confirm visible display.
On project-name drift, request regeneration from the retained value
and keep that key undisplayed until its corrected message arrives. The manager
resends promptly; cosmetic correction changes only the display if work is already
released. A substantive scope conflict stops dependent work until clarified.
Never repair helper output manually. Managers omit `--previous-key` for WORKING_ON:
always send the complete generated text and let the runner deduplicate visible output.

## Targeted issues

The manager promptly sends every necessary user decision or blocking
condition to the runner, whether from a child message/result, its own work,
a helper failure, or takeover. Stop dependent work first. Use `status` with
`--kind decision` for the exact question, reason and waiting work, or `--kind blocked`
for the actual diagnostic, why work cannot continue and the necessary next action.
Report the affected scope when independent authorized work can continue.
Do not wait for final child results, unrelated checks or the next progress key.
Children ask their manager, never the user directly. The runner authenticates
the current or exact pending manager under the takeover rules; it alone presents
the user question. Retain each issue's manager identity for answer routing,
including during takeover. Generate the actual message body in the user's
language using the retained project name and affected unit:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" status --kind decision --project "<project-name>" --plan PLAN-0025 --point W-001/step-2 --text '<actual question, reason and waiting work>'
```

Kinds are `decision`, `blocked`, `paused` and `completed`. Before the canonical
location is known, omit both `--plan` and `--point`; the heading uses Startup.
Use `--text-file` instead of `--text` for an existing UTF-8 body. Direct `--text`
requires no writes and remains available while a pending manager cannot write.
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
STOPPED, generated with `status --kind paused`. While writes are prohibited, retain and relay the unsaved issue with
the reason it cannot yet be saved. A pending successor keeps it unsaved until
TAKEOVER_COMPLETE makes it the current owner. For a report-write failure, retain
and relay the issue with the exact save diagnostic, marking it unsaved.
Keep dependent work stopped until persistence and any necessary answer are
secured; saving the report or Plan must never hide the
condition from the runner. An unknown write outcome requires
reading the existing report before retrying. Never accept partial helper stdout.

If startup fails before a manager can own the report, the runner records the
user-relevant startup problem at `Startup` and generates its blocked display
using the same helper. Otherwise
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
Generate `status --kind completed` with the last accepted unit and actual
completed scope. This does not bypass closure.

On a valid COMPLETED from the current manager, keep the runner completion phase
open until that manager's actual native final and confirmed child/writer
quiescence. A control message alone is not the end of the run. Then read the
retained file with `run_feedback.py read --report-file "<run-report.md>"`. Require success
and nonempty `display_text` before displaying the retained generated completion text.
Then output `Run report: <absolute-path>` and the complete returned `display_text`.
This field preserves all report content except internal issue-marker lines;
`text` retains the stored form for bookkeeping.
A failed or empty read reports the problem and leaves completion unconfirmed.
Only after successful output does the runner role end. Do not replace this
helper operation with a direct file read or start a normal-assistance audit first.
Read only on a requested inspection or completion, never as a progress poll.
The runner's key and report path survive stop/resume. A new completed-run
activation creates a new file and starts with no previous display key.
