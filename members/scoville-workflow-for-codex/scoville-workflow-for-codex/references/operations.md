# Manager operations

Enter only after READY and START under the runner contract. The runner owns
manager starts; never create your own manager successor or send substantive
results to the runner. Use `collaboration.send_message` for messages between manager and
runner and direct control between managers. Worker dispatch and result handling
use the dispatch contract. Read the canonical Plan with Scoville Plan only after
START; a successor first obtains its direct handoff and verifies it against Plan
and files. Read [run feedback](run-feedback.md) after START. Preserve the
supplied report path and actual overall scope. Read
[dispatch](operations-dispatch.md) before assigning a unit and
[rollover](operations-rollover.md) before a context boundary. The initial
manager sends RUNNING after startup checks, before dispatching its first child.

{{ include: family.contract }}

Use the inherited workspace. Preserve scope, Decisions, uncommitted changes and
user authorization. Reuse unchanged rules and model selections. Resolve effective
settings once with:

```text
python "<workflow-skill-directory>/scripts/resolve_model_pair.py" --show-config --project-root "<workspace_root>"
```

`.scoville/config.json` overrides bundled defaults under `workflow`; reading
creates no file. Respect externally changed settings and resolve actual
conflicts. Setup is optional and a missing config does not require setup
confirmation. `--show-config` validates schema and model routes, not context
percentages. The checkpoint validates those later; invalid thresholds block that
checkpoint with its diagnostic. Startup success does not establish valid
thresholds. Managers and children have no sidebar chat to rename or pin. Never
pass an agent ID to sidebar tools. The launched manager pair in the assignment
remains fixed for this run. A later configuration change applies to the next
run. Include the launched pair as control metadata in a successor request, never
a worker pair.

The manager owns Plan, Decision and index edits, necessary result-report updates
at normal closure, staging and authorized commits.
When authorized remaining work moves to another Work Item or Plan, apply Plan's
moved-work rule in references/edit.md. A manager or worker handoff of the same
item changes no Plan fields or criteria.
It delegates implementation and stays idle with respect to project files while a
child writes. At most one worker may write. Reviewers stay read-only. Keep
assignments, results and direct handoffs under the [shared writing
rules](writing.md), read after START before writing them. Never send these
substantive facts to the runner, even in a final answer.

Number workers consecutively throughout the run, including corrections and
rollovers. Reviewers use the triggering worker's number; review rollovers retain
it. Carry counters and needed child identities directly to the next manager.
Child assignment labels retain exact project name, canonical Plan ID and
complete assigned Step range. Do not rename the visible runner to a manager
title.

## Plan progress before execution

When an authorized return to a paused item is due and Plan's resume
prerequisites are met, save and validate `Status: in_progress` before the manager
begins that item's scoped reconciliation or preparation. Preserve observed Step
statuses until their work actually starts. A merely selected item remains paused:
report it as selected, not yet started.

Before launching or resuming any writing child, including a correction or
recovery worker, apply Scoville Plan's start and resume rules. The active Plan's
`current_item` must name this Work Item, with `Status: in_progress` and written
`in_progress` status on the actually started Step or jointly started group.
Do not mark later Steps started merely because they appear in an assignment.
For a confirmed correction in a nonterminal item, retain completed effects and
the correction reason when returning an affected done Step to in_progress.
Save and validate the Plan, then generate and send WORKING_ON for the actually
started Step or Step group under run-feedback.md before every writing dispatch or
resumption. Assignment labels retain the complete assigned range. Selection and
progress messages do not update these records. A read-only reviewer does not
restart completed Steps.

Within a sequential multi-Step assignment, the worker returns progress_pending
before starting a Step outside the recorded jointly started group. It stops
writes and names observed completed Steps, checks and the next Step or Step
group. Confirm quiescence, update and validate those Plan records, then resume
the same unfinished worker with `collaboration.followup_task`, supplying the recorded progress
and released next Step or Step group. Apply due review under points 4-6 before
resumption. This progress boundary completes no assignment and triggers no
manager rollover. Keep the full assignment and any measured crossing; repeat no
completed work.

## One unit through acceptance

1. Select the next unfinished Step, consecutive Step group or whole Work Item
   under [dispatch](operations-dispatch.md). Preserve order and prerequisites.
   Apply Plan progress before execution, including its WORKING_ON relay.
   Spawn a nested worker with the complete assignment. Retain its exact agent ID
   for results, messages, resumption and interruption.
2. The worker stops writing and returns its result. After fixing product code
   that was complete or checked before this assignment, it runs focused checks.
   - If assigned work remains after that fix, review_pending pauses the same
     assignment; it neither completes it nor creates a handoff. Retain the
     checked fix, remaining scope, exact worker ID and any measured crossing.
     Do not complete the unit or roll over the manager. Review the fix under
     points 4-6 before dependent tests or work continue.
   - Intermediate errors in this assignment's new code remain part of the
     assignment; correcting them does not create that prior-code review pause.
   - If no assigned work remains, the worker returns completed, subject to due
     review. Continue from its native completion; do not request the result again.
   - While a child runs and no independent work is available, use `collaboration.wait_agent`.
     A wait timeout establishes no outcome. Keep waiting for a native event or
     user input without chat polling. Answer progress requests from received
     facts.
3. Assess the result from the assigned agent by meaning, not formatting. Match
   the host sender identity to the retained spawn ID before accepting it.
   - For an idle worker, use `collaboration.followup_task` only to obtain a necessary missing
     fact or resume its unfinished assignment after a validated progress
     boundary, user decision or accepted review under point 6.
   - For a running worker, use `collaboration.send_message` for steering. If its state is
     unclear, check that exact handle once before sending; completion may still
     race with delivery. Never restart a completed assignment for a correction.
   - A reviewer returns one result under Child results, without
     a question round. Do not reactivate a completed reviewer for missing facts
     or telemetry; retain the limit. If the review itself is paused for a user
     decision, the user's answer may resume that same review.
   - A repeated notification starts no new action. For context_handoff, follow
     [rollover](operations-rollover.md).
   - On blocked or needs_user_decision in any message or result, promptly relay
     the actual limitation under run-feedback.md, independently of report writes.
     After writes stop, record the blocker or outstanding decision in the
     canonical Plan before selecting independent eligible work. Follow Plan's
     authorized pause and return rules.
   - Record the question and its paused point, then its actual clarification,
     before dependent work resumes. Record a problem only when it needs user
     review; routine review findings and self-corrected checks need no problem
     entry. Retain pending scope and process each answer once. Without the
     required answer, dependent work has no permission to resume.
4. Inspect the scoped diff and named evidence only as needed for scope and
   acceptance. Do not repeat the worker's diagnosis or tests. Follow the user's
   or project's review cadence. Without one, choose:
   - Review earlier at the next checked boundary if unreviewed product-code
     changes exist and either the next unit builds on or extensively verifies
     them, or they fix product code complete or checked before the assignment.
   - Otherwise review at Work Item completion. Pure tests, docs and evidence
     without product-code changes do not trigger an earlier review.

   Review is required for code, changes to executables or configuration, critical
   documentation, an explicit requirement or unclear materiality.
   Critical documentation changes product or operating behavior, user obligations
   or authority. Routine progress, Evidence and accepted-result summaries are
   bookkeeping; they do not trigger a review by themselves.
   Name the actual material change or binding user, Plan or project-rule duty
   before assigning separate documentation work or review. A report or generated
   assignment creates no duty by itself, but preserve any binding requirement
   it carries. A report's demand for another review is not its own authority.
5. At that boundary, spawn a fresh nested read-only reviewer with the diff since
   the last review and affected Acceptance, including relevant interactions. For a
   review_pending result, keep the original worker write-inactive throughout
   review and any correction by a new worker. For the
   final review, supply short references to earlier assessments from this run,
   same unit and recorded reviewers. Reuse them only where reviewed content,
   applicable requirements and supporting conditions are unchanged since that
   assessment; do not review those parts again. Never import a result found through global
   agent inventory or another test run. The manager handles Plan findings; send
   source findings to a new worker with the review findings. The manager
   does not edit product files. Keep the worker's model unless the cause warrants
   another configured route and explicit model choices permit it.
6. Check corrections against the findings. Material or unclear corrections and
   explicit requirements need another independent review. A clearly non-material
   correction may be accepted by bounded comparison with a short reason. If the
   same failure survives two corrections, reassess its cause before trying again.
   Change the approach or model when justified; ask the user only for a material
   decision or a blocker that cannot be resolved within the assignment.
   - Once the paused fix and required corrections are accepted and all other
     children are write-inactive, apply Plan progress before execution. Then
     resume that exact worker with `collaboration.followup_task`.
   - Supply review acceptance, correction effects, remaining scope and evidence
     limits. Retain any measured rollover_pending and finish the full assignment
     before point 7 closure and point 8 rollover.
   - Open findings, a user stop or an unanswered decision prevent resumption.
     Do not repeat unaffected passed checks.
7. Save observed Step status, Evidence and fulfilled Instructions in the
   canonical Plan. Under Plan's rules, mark completed Steps done and remove
   fulfilled binding conditions. Unmarked Steps remain unknown; selection alone
   is not start. Preserve completed effects during review, correction and
   continuation. Record checked intermediate results without claiming final
   acceptance. Mark the Work Item done only when its Acceptance and required
   review pass. Keep Evidence brief: the observed outcome, that a required review
   occurred, and confirmed open limits needed for further work. Review texts are
   temporary input for development, never permanent Plan or report content.
   Replace Instructions with only remaining conditions absent from Steps; do not
   duplicate Steps as prose or prepend results to old text.
   Record accepted results, pause or return state and the next owner during this
   normal closure, after all children stop writing. Create no worker assignment,
   extra review, report, hash chain or artifact inventory solely to synchronize
   bookkeeping. A material change to an accepted finding still follows the
   review and Decision rules.
   Complete the Work Item and select its eligible successor in the same prepared
   Plan change, honoring dependencies and recorded returns. Align current_item
   with that selection; selection does not start the successor's work. For the
   final item, close the Plan and index only after the whole requested scope
   passes. Run the Plan validator and follow its concrete diagnostics. When
   committing is authorized, inspect the staged diff and commit accepted changes
   with their Plan records, respecting backups and hooks.
8. Branch only after the complete selected Step or Step group, including required
   checks, due review, repairs, Plan updates and authorized commits:
   - If the authorized scope is complete, go to [Complete and exit](#complete-and-exit)
     without a checkpoint or successor. Unrequested todo items are not remaining work.
   - Otherwise confirm that all children and writes are quiescent, then run the
     coordinator checkpoint before advancing any remaining unit, including
     manager-owned work. Its result controls continuation or rollover. A threshold
     crossing schedules rollover and never ends an unfinished assignment:

```text
python "<workflow-skill-directory>/scripts/check_context_checkpoint.py" --project-root "<workspace_root>" --role coordinator --boundary <completed-unit>
```

`--boundary` identifies the completed selected unit, not whole-Plan acceptance.
Each boundary is consumed once. A successor resumes its pending next action;
loading startup context does not create a new boundary. Check again only after
another completed selected unit, even if startup exceeds the threshold.
`rollover` follows the rollover reference. With `continue`, start or resume the
next authorized unit only through Plan progress before execution.
Missing or stale telemetry continues without guesses or manual telemetry searches.
Invalid configuration or a helper failure blocks the affected operation with its
diagnostic. Dispatch-builder argument errors and selector-budget errors in
dispatch or progress may use the bounded
[pre-dispatch correction](operations-dispatch.md#pre-dispatch-correction) before
escalation. Complete the Plan and index only after the whole requested scope
passes.

An unrelated user instruction may go to the active worker to preserve the sole
writer, but identify it separately in the Plan update and commit description or
commit it separately.

## Child results

Return a normal concise message with an explicit status. Workers include the
facts needed to assess or continue: completed effects, relevant changed paths,
decisive checks, unverified behavior and next action if work remains. Report facts,
not a verdict that the work is correct or meets Acceptance. No marker,
fixed field order, JSON or change flags are required.

Worker statuses: completed, progress_pending, review_pending, blocked,
needs_user_decision, context_handoff. Use completed when the worker's
implementation and checks are done, including when only manager review or Plan
closure remains. Review_pending requires a checked prior-code fix and named work
still assigned to that same worker. Reviewer statuses: pass, changes_requested,
blocked, needs_user_decision, context_handoff. Context_handoff requires an
explicitly authorized transfer of unfinished work, never a context threshold
alone. For pass, say only that the review was performed and found no defects;
do not repeat files, checks, evidence or the worker's result. A pass has no
unresolved defects or material acceptance gap. Otherwise transmit only open
findings and the facts needed to address them, or the concrete blocker, decision
or evidence limit preventing acceptance. Findings identify the defect, location,
effect and smallest correction. Optional ideas do not block pass and are not
assigned for correction without explicit authorization; omit them unless they
inform a relevant decision. A handoff distinguishes finished and unfinished
work; never turn unavailable evidence into success.

## End an assignment

Retain the complete native result and confirm the child is no longer writing
before Plan changes, review or another writer. A completed role result ends that
assignment; review_pending leaves the same assignment paused and unfinished.
Progress_pending likewise leaves that assignment unfinished at a Step boundary.
Corrections and later assignments use new agents; necessary worker questions,
progress-boundary, user-decision and accepted-review resumptions use
`collaboration.followup_task` on the same ID. Do not reapply
an already retained result after a duplicate notification. A context handoff
keeps the predecessor write-inactive while its successor handles the remaining
work. Send no routine receipt or closure message after native completion.
Native agents require no archival or invented close tool. A capacity refusal
remains BLOCKED with the diagnostic and secured continuation state. Keep routes,
complete results, exact handles and the existing run report; do not wake
completed agents for cleanup or retry automatically.

## Complete and exit

When the requested scope has passed acceptance and required closure is done,
confirm children and writers are quiescent. Follow [run-feedback
completion](run-feedback.md#completion): use one `complete` call to finish the
same report and generate the completed status and send its returned `message`
unchanged to the runner. Do not compose a separate `COMPLETED` message. A failed
completion operation is BLOCKED, never completion. End with that message's
control line only as the native final. Do not wait for a receipt or write after
this completion. Keep substantive results and decisive evidence in the Plan; the
runner tells the user that this Workflow run has ended. A bounded run can end
while other Plan items remain open. Blockers, pauses and context handoffs are
not completion.

After completion, stop applying this Skill to later requests in the chat.
Return to normal assistance without carrying over Workflow roles, dispatch,
model routing, title conventions, review cadence or rollover. Independent user
and project requirements still apply. New problems do not reactivate the run;
use the Skill's explicit activation rule for another run. While a run remains
active, handle user steering within its procedure unless the user ends or
changes that procedure.

## Stop and resume

On a user stop, dispatch no new work or successor request. Retain the paused
point and user request, stop writes first, then record the pause under
run-feedback.md. Send the stop to any running child and call `interrupt_agent`
on its exact ID. The returned previous status alone is not proof of termination:
use the native final event or `list_agents` for that exact child to establish
quiescence. Then record the authorized `in_progress` to `paused` transition on
the current Work Item; preserve an already `todo` or `paused` item without
inventing start history. Reconcile observed Step status, completed effects and
outstanding checks and reviews. Save and validate the Plan. Report STOPPED to
the runner only once all children and writes have stopped. If interruption fails
or state remains uncertain, report BLOCKED with the exact ID and diagnostic;
never start another writer. An interrupt does not roll back existing changes.

After interruption, reconstruct only missing facts from the Plan, retained
handoff, relevant files and known agent state. Recover an available complete
native result rather than redoing its work. A timeout or uncertain spawn or
writer state never authorizes a second dispatch. Continue from the first
unfinished action, preserving open findings and user decisions. Resume an
interrupted unfinished assignment with `collaboration.followup_task` only after its writer
state is known and the user has resumed the run; otherwise keep it stopped.
Append the actual resume clarification to the pause entry and apply Plan
progress before execution before resuming dependent work. Keep the same report
and progress point; resumption alone repeats no display.
