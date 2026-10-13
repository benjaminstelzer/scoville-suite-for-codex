# Manager operations

Use Plan for records and [dispatch](operations-dispatch.md) for assignments.
Preserve authorized scope, Decisions, stops and unrelated changes. The manager
writes records, not source. One executor writes at a time; stop its writes before
record edits, review or another writer. Read only the context needed to select
and assess work; implementation diagnosis belongs to the executor.

All Skills included in this suite must be installed and enabled. Use the
applicable owner without checking sibling availability. Load only instructions
needed for the task. Explicit invocation gates and user exclusions still apply.

## Execute one Step

On each explicit Workflow activation, before Plan writes, require a Git worktree
with empty `git status --porcelain --untracked-files=all`. A failed command or
listed path blocks activation: report the prerequisite or paths; start no
Executor. Do not discard, stash, stage or commit existing work to get clean.
Host continuation, compaction and rule reload are not new activation; do not
interrupt an active writer.
Before leaving Workflow, commit pending owned Plan records when no unreviewed
implementation changes remain; otherwise report the dirty paths.

1. Select the authorized Plan, current Work Item and exactly one Step. Preserve
   order and dependencies. At Work Item start, note HEAD in its existing Evidence
   for closure. Save actual start/resume state through Plan;
   selecting a Step alone is not a start. The dispatch helper validates the
   saved profile and started state before publishing an Executor assignment.
2. Choose Executor with the [agent check](operations-dispatch.md#check-the-agent-before-every-assignment).
   Build the unchanged assignment through the helper and call its returned
   native tool arguments.
3. Wait for the matching complete native result. Retain it once and establish
   writer quiescence. A timeout is not failure or permission to replace a writer.
   A blocking problem returns to manager; ask only a necessary user decision.
   Check Step completion, required checks and clear effects against the complete
   result, Git status/diff HEAD and reported non-file or ignored-output effects.
   Resolve missing or unclear results
   through the same-Step helper before advancing or deciding on review. For
   continuation of this same Step, supply its available complete prior Executor final unchanged as
   `--executor-result`; keep required review inputs. If the current final cannot
   provide required non-Git evidence, report the exact prerequisite;
   do not loop, invent evidence or classify the Step as unchanged.
   Read supporting artifacts only when needed for these manager decisions;
   the reviewer inspects their technical details. Read the complete native final
   or its complete externalized text in either case.
4. Review each Step that changed files, configuration or behavior. A Step without
   such changes is checked by the closure review. Use Git for file changes and
   reported effects for configuration, behavior and ignored outputs. If no changes remain to
   review and no Step review is open, go to item 6. Otherwise choose Reviewer
   with the agent check. Dispatch the SAME original Step and complete unchanged
   Executor final. Review its reported changes, relevant effects and open
   findings. Follow-ups without new changes do not end an open Step review or
   its findings; evidence-only follow-ups continue review of the original change.
5. For changes_requested, pass the review objections unchanged as additional
   context to the executor helper for this same Step. Return to Step 2, then
   review the correction. Do not rewrite the original Step, widen scope or
   implement optional ideas. Reuse unaffected successful checks and coverage;
   retain unresolved findings and limits. Earlier coverage is not a current pass.
6. Once the Step is complete and any required Step review has passed, save
   Step status and concise evidence. Commit the reviewed Step changes with Plan
   progress before selecting the next Step. Foreign or unreviewed work prevents
   this boundary; report its paths, never stage it. A failed or forbidden commit stops
   advancement; report the obstacle. Confirm clean Git status after the commit.
   Make no empty commits. A truly unchanged
   Step needs no Step review or Step commit; retain its Plan progress.
   Record no unperformed review pass. Routine Plan edits create no extra review.

## Close the Work Item

After all Steps are complete and all required Step reviews pass, choose this
Work Item's Reviewer with the agent check.
The helper sends the whole original Work Item, all Steps and full Acceptance.
The reviewer compares current implementation and retained
evidence with those requirements; this is a closure check, not a general audit.

On findings, keep the same Plan and Work Item. Select ONE affected Step, pass
the objections as additional context, execute it, review it when item 4 requires, then repeat the
closure review. If an existing Step covers the defect, use it. If none does,
manager may add one implementation Step for a named, already binding unchanged
Acceptance criterion or Work Item requirement. Run that original new Step
through the normal loop. Changed scope, Acceptance, contradictory requirements
or materially unclear meaning need the user; do not invent a Step to bypass them.

Mark the Work Item done only after its Acceptance and closure review pass.
Validate and commit the coherent Plan update,
respecting repository checks and backups. Clear Executor/Reviewer associations
when moving to the next Work Item; retain Explorer for this manager thread.
Finish only the authorized scope. A bounded run can leave unrequested work open.

## User requests and results

Questions, ideas, change requests and planning preparation go to Explorer.
Choose it with the agent check. Its own configured
pair defaults to the executor pair. It reads and returns a minimal answer,
source evidence and limits. It does not write the Plan or accept implementation.
Answer the user from the Explorer's findings in the communication language.
Preserve evidence limits, quotes and technical literals.

| Result | Meaning |
| --- | --- |
| done | Assigned execution/checks or exploration finished; not review acceptance. |
| pass | Assigned review ran; no unresolved defect or required evidence gap. |
| changes_requested | Open defect, location, effect, smallest correction and affected Step, or none. |
| blocked | Actual prerequisite or required decision prevents dependent work. |

1. Match the complete native final and actual completion to the retained handle
   and assignment. Do not infer identity from titles or partial messages.
2. Save the complete native final unchanged and compare its saved text with
   the complete native final once before dependent dispatch. Concise Plan evidence is separate; never replace a
   child result with Manager-composed evidence.
3. Missing required Executor evidence: choose that Executor through the agent
   check, rebuild the SAME Step with the complete blocked Reviewer final as
   `--reviewer-result` and the complete Executor final it reviewed as
   `--executor-result`. For the next review, supply the complete returned native
   final as `--executor-result` and the original blocked Reviewer final as
   `--reviewer-result`, both unchanged.
   Replacement alone proves no missing baseline; report an actual unavailable
   baseline or unresolved prerequisite. Other necessary missing-result questions
   also use the exact child's agent check and helper assignment.

Report necessary blockers and decisions directly. Stop dependent work; preserve
completed effects and the actual answer before continuing. Nonblocking problems
may continue to review. Waiting for active work is working, not blocked.

## Stop, compaction and failure

On user stop:

1. Dispatch nothing new.
2. Interrupt running children by exact handle.
3. Confirm quiescence through native final or current list_agents state. An
   interrupt's previous status proves no termination. Report an uncertain handle
   and diagnostic; start no competing writer.
4. Save and validate observed Plan pause, unfinished checks, open reviews and
   decisions. Resume only on explicit activation.

After compaction, recover the same assignments and actual results; repeat no
completed work merely to rebuild history.

For a confirmed failed or interrupted child:

1. Establish termination.
2. Reconcile retained effects and checks.
3. Clear its association; do not measure or reuse it.
4. Re-dispatch the same unit and role with unchanged role inputs (Executor
   result, open review findings) and any explicit user role choice. Use the
   helper, next role number and `--replacement-of` with the retained pair,
   unless an explicit Step or user choice changes it.

An ordinary completed `blocked` result is not a failed child. This recovery
never bypasses a failed measurement of an eligible idle agent. Uncertain spawn
or result prevents duplicate dispatch.

Completion requires requested Acceptance, required Step reviews, closure review and
quiescent writers. Report the result and limits, then leave Workflow. Blockers
and pauses are not completion; new requests activate no automatic successor.
