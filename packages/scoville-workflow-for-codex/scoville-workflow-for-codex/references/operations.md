# Manager operations

Enter only after READY and START under the runner contract. The runner owns
manager starts; never create your own manager successor or send substantive
results to the runner. Use `send_message` for manager/runner and direct
manager/manager control. Worker dispatch and result handling use the dispatch
contract. Read the canonical Plan with Scoville Plan only after START; a
successor first obtains its direct handoff and verifies it against Plan and files.
Read [run feedback](run-feedback.md) after START. Preserve the supplied report
path and actual overall scope. Read [dispatch](operations-dispatch.md) before assigning a unit and
[rollover](operations-rollover.md) before a context boundary. The initial manager
sends RUNNING after startup checks, before dispatching its first child.

All Skills included in this suite must be installed and enabled. Use the
applicable owner without checking sibling availability. Load only instructions
needed for the task. Explicit invocation gates and user exclusions still apply.

Use the inherited workspace. Preserve scope, Decisions, uncommitted changes and
user authorization. Reuse unchanged rules and model selections. Resolve effective
settings once with:

```text
python "<workflow-skill-directory>/scripts/resolve_model_pair.py" --show-config --project-root "<workspace_root>"
```

`.scoville/config.json` overrides bundled defaults under `workflow`; reading
creates no file. Respect externally changed settings and resolve actual conflicts.
Setup is optional and a missing config does not require setup confirmation.
`pin_threads` remains compatible saved configuration but has no effect on native
agents. Managers and children have no sidebar chat to rename or pin. Never pass an agent ID
to sidebar tools. Preserve any existing explicit manager model/effort and include
it as control metadata in a successor request; never substitute a worker pair.

The manager owns Plan, Decision and index edits, staging and authorized commits.
It delegates implementation and stays idle with respect to project files while
a child writes. At most one worker may write. Reviewers stay read-only. Keep
assignments, results and direct handoffs concise but sufficient to continue
without hidden context: current state, constraints, evidence limits, next action.
Never send these substantive facts to the runner, even in a final answer.

Number workers consecutively throughout the run, including corrections and
rollovers. Reviewers use the triggering worker's number; review rollovers retain
it. Carry counters and needed child identities directly to the next manager.
Child assignment labels retain exact project name, canonical Plan ID and complete assigned
Step range. Do not rename the visible runner to a manager title.

## Plan progress before execution

Before launching or resuming any writing child, including a correction or
recovery worker, apply Scoville Plan's start/resume rules. The active Plan's
`current_item` must name this Work Item, with `Status: in_progress` and written
`in_progress` status on the actually started Step or jointly started group.
Do not mark later Steps started merely because they appear in an assignment.
For a confirmed correction in a nonterminal item, retain completed effects and
the correction reason when returning an affected done Step to in_progress.
Save and validate the Plan before building the assignment, sending WORKING_ON
or releasing the child to write. Selection and progress messages do not update
these records. A read-only reviewer does not restart completed Steps.

Within a sequential multi-Step assignment, the worker returns progress_pending
before starting a Step outside the recorded jointly started group. It stops
writes and names observed completed Steps, checks and the next Step/group.
Confirm quiescence, update and validate those Plan records, then resume the same
unfinished worker with `followup_task`, supplying the recorded progress and
released next Step/group. Apply due review under points 4-6 before resumption.
This progress boundary completes no assignment and triggers no manager rollover.
Keep the full assignment and any measured crossing; repeat no completed work.

## One unit through acceptance

1. Select the next unfinished Step, consecutive Step group or whole Work Item
   under [dispatch](operations-dispatch.md). Preserve order and prerequisites.
   Apply Plan progress before execution, then send WORKING_ON for the selected
   project, Plan and assigned
   point/range under run-feedback.md. Its Scope is the actual overall assignment,
   not this child's narrower task. Spawn a nested worker with the complete assignment. Retain its exact agent ID
   for results, messages, resumption and interruption.
2. The worker stops writing and returns its result. After fixing product code
   that was complete or checked before this assignment, it runs focused checks.
   If assigned work remains, review_pending is a pause, not assignment completion
   or a handoff. Retain the checked fix, remaining scope, exact worker ID and any
   measured crossing. Do not mark the unit complete or roll over the manager at this pause.
   Review the fix before dependent tests or work continue under points 4-6.
   Correcting intermediate errors in this assignment's new code stays within
   the assignment. If no assigned work remains, the worker returns completed,
   still subject to due review. Continue from that
   native completion; do not request the same result again. Use `wait_agent`
   while a child runs and there is no independent work. Wait timeouts carry no
   outcome; keep waiting for a native event or user input without chat polling.
   Report requested progress from received facts.
3. Assess the result from the assigned agent by meaning, not formatting. Match
   the host sender identity to the retained spawn ID before accepting it. Use
   `followup_task` on an idle worker only for a necessary missing fact or to
   resume the same unfinished assignment after a validated progress boundary,
   user decision or accepted review
   under point 6. Use `send_message`
   for steering a running worker. Never restart a completed assignment for a
   correction. A reviewer returns one complete assessment with evidence limits;
   no reviewer question round. Do not reactivate a completed reviewer for
   missing facts or telemetry; retain that evidence limit. A pending reviewer decision may resume the same
   review with the user's answer. A repeated
   notification does not start another action. For context_handoff follow
   [rollover](operations-rollover.md). For blocked or needs_user_decision, retain
   the actual limitation. After writes stop, record the blocker or outstanding
   decision in the canonical Plan before selecting independent eligible work;
   follow Plan's authorized pause and return rules. Send the
   runner only BLOCKED with the concrete limitation or NEEDS_USER_DECISION with
   the exact necessary question. Record a question and its paused point in the
   run report before relay, and append the actual clarification before dependent
   work resumes. Record a problem only if it needs user review, not routine
   review findings or self-corrected checks. Retain its pending scope and process an answer
   once; no answer means no permission for dependent work.
4. Inspect the scoped diff and named evidence only as needed for scope and
   acceptance. Do not repeat the worker's diagnosis or tests. Follow the user's
   or project's review cadence. Otherwise review earlier, at the next checked
   boundary, when unreviewed product-code changes exist and either the next unit
   builds on or extensively verifies them, or they fix product code that was
   complete or checked before the fixing assignment. Otherwise review at Work Item completion. Pure tests, docs and
   evidence without product-code changes do not trigger an earlier review.
   Review is required for code, executable/configuration changes, critical
   documentation, an explicit requirement or unclear materiality.
5. At that boundary, spawn a fresh nested read-only reviewer with the diff since the
   last review and affected Acceptance, including relevant interactions. For a
   review_pending result, keep the original worker write-inactive throughout
   review and any correction by a new worker. For the
   final review, supply short references to earlier assessments and reuse them
   for unchanged parts rather than reviewing those parts again. The manager handles Plan findings; send source
   findings to a new worker with the review findings. The manager
   does not edit product files. Keep the worker's model unless the cause warrants
   another configured route and explicit model choices permit it.
6. Check corrections against the findings. Material or unclear corrections and
   explicit requirements need another independent review. A clearly non-material
   correction may be accepted by bounded comparison with a short reason. If the
   same failure survives two corrections, reassess its cause before trying again.
   Change the approach or model when justified; ask the user only for a material
   decision or a blocker that cannot be resolved within the assignment.
   Once the paused fix and required corrections are accepted and all other
   children are write-inactive, apply Plan progress before execution, then
   resume that exact worker with `followup_task`.
   Supply the review acceptance, correction effects, remaining scope and evidence
   limits. Retain any measured rollover_pending and finish the same full assignment
   before point 7 closure and point 8 rollover. Open findings, a user stop or an
   unanswered decision prevent resumption. Do not repeat unaffected passed checks.
7. Update observed Step status, Evidence and any fulfilled Instructions in the canonical Plan
   before the next dispatch or checkpoint. Follow Plan's Step-progress rules:
   unmarked is unknown; selection alone is not start. Preserve completed effects
   during review, correction and continuation. Record checked intermediate results without claiming final acceptance. Mark
   the Work Item done only when its Acceptance and required review pass. Evidence
   contains the outcome and decisive report reference, not agent IDs or attempts.
   Complete the Work Item and select its eligible successor in the same prepared
   Plan change under Scoville Plan, honoring dependencies and recorded returns.
   Keep `current_item` aligned with that selection; start the successor only
   through Plan progress before execution. Use Plan/index closure for the final item.
   Run the Plan validator and follow its concrete diagnostics. When committing
   is authorized, inspect the staged diff and commit accepted changes with their
   Plan records, respecting backups and hooks.
8. With work remaining, run the coordinator checkpoint after the complete selected
   Step or Step group, including required checks, due review, repairs, Plan updates
   and authorized commits, before creating the next worker. Confirm all children
   and writes are quiescent. A threshold crossing only schedules rollover and
   never ends an unfinished assignment:

```text
python "<workflow-skill-directory>/scripts/check_context_checkpoint.py" --project-root "<workspace_root>" --role coordinator --boundary <completed-unit>
```

`--boundary` identifies the completed selected unit, not whole-Plan acceptance.
Each boundary is consumed once. A successor resumes its pending next action;
loading startup context does not create a new boundary. Check again only after
another completed selected unit, even if startup exceeds the threshold.
`rollover` follows the rollover reference; `continue` allows the next unit.
Missing or stale telemetry continues without guesses or manual telemetry searches.
Invalid configuration or a helper failure blocks the affected operation with its
diagnostic. Complete the Plan/index only after the whole requested scope passes.

An unrelated user instruction may go to the active worker to preserve the sole
writer, but identify it separately in the Plan update and commit description or
commit it separately.

## Results

Return a normal concise message with an explicit status and the facts needed to
assess or continue: completed effects, relevant changed paths, decisive checks,
unverified behavior and next action if work remains. No marker, fixed field order,
JSON or change flags are required.

Worker statuses: completed, progress_pending, review_pending, blocked, needs_user_decision, context_handoff.
Use completed when the worker's implementation and checks are done, including
when only manager review or Plan closure remains. Review_pending requires a
checked prior-code fix and named work still assigned to that same worker.
Reviewer statuses: pass, changes_requested, blocked, needs_user_decision,
context_handoff. Context_handoff requires an explicitly authorized transfer of
unfinished work, never a context threshold alone. A pass has no unresolved findings.
Findings identify the defect, location, effect and smallest correction. A handoff distinguishes finished and
unfinished work; never turn unavailable evidence into success.

## End an assignment

Retain the complete native result and confirm the child is no longer writing
before Plan changes, review or another writer. A completed role result ends that
assignment; review_pending leaves the same assignment paused and unfinished.
Progress_pending likewise leaves that assignment unfinished at a Step boundary.
Corrections and later assignments use new agents; necessary worker questions,
progress-boundary, user-decision and accepted-review resumptions use
`followup_task` on the same ID. Do not reapply
an already retained result after a duplicate notification. A context handoff
keeps the predecessor write-inactive while its successor handles the remaining
work. Native agents require no archival or invented close tool. If host capacity
prevents a spawn, use the bounded recovery in [agent capacity](agent-capacity.md).
Unresolved capacity remains BLOCKED. Keep routes and the existing run report.

## Complete and exit

When the requested scope has passed acceptance and required closure is done,
confirm children and writers are quiescent. Finalize the same run report with
run_feedback.py finish --completed and verify
its successful output. Only then send `COMPLETED` with the requested scope
identifier to the runner. A failed report operation is BLOCKED, never completion.
End the turn with the same control-only native final. Do not wait for a receipt
or write after this completion.
Keep substantive results and decisive evidence in the Plan; the runner tells
the user that this Workflow run has ended. A bounded run can end while other
Plan items remain open. Blockers,
pauses and context handoffs are not completion.

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
run-feedback.md. Send the stop to
any running child and call `interrupt_agent` on its exact ID. The returned
previous status alone is not proof of termination: use the native final event
or `list_agents` for that exact child to establish quiescence. Then record the
authorized `in_progress` to `paused` transition on the current Work Item;
preserve an already `todo` or `paused` item without inventing start history.
Reconcile observed Step status,
completed effects and outstanding checks/reviews. Save and validate the Plan.
Report STOPPED to
the runner only once all children and writes have stopped. If interruption fails
or state remains uncertain, report BLOCKED with the exact ID and diagnostic;
never start another writer. An interrupt does not roll back existing changes.

After interruption, reconstruct only missing facts from the Plan, retained
handoff, relevant files and known agent state. Recover an available complete
native result rather than redoing its work. A timeout or uncertain spawn/writer
state never authorizes a second dispatch. Continue from the first unfinished
action, preserving open findings and user decisions. Resume an interrupted
unfinished assignment with `followup_task` only after its writer state is known
and the user has resumed the run; otherwise keep it stopped. Append the
actual resume clarification to the pause entry and apply Plan progress before
execution before resuming dependent work.
Keep the same report and progress point; resumption alone repeats no display.
