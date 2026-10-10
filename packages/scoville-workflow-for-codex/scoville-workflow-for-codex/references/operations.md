# Manager operations

The visible chat manages this run. Use Scoville Plan for records and
[dispatch](operations-dispatch.md) for child assignments. Preserve scope,
Decisions, uncommitted changes and user authorization. Resolve effective
executor, reviewer and explorer settings once:

```text
python "<workflow-skill-directory>/scripts/resolve_model_pair.py" --show-config --project-root "<workspace_root>"
```

Reading creates no configuration. Re-resolve after relevant settings changes;
existing assignments retain their launched pairs. Setup is optional. Reuse
complete reads and successful results while relevant inputs remain unchanged.
Inspect context needed to assign or assess work, not the executor's whole
implementation diagnosis. Concrete evidence of an active or uncertain competing
writer blocks writing; missing historical identities alone do not.

All Skills included in this suite must be installed and enabled. Use the
applicable owner without checking sibling availability. Load only instructions
needed for the task. Explicit invocation gates and user exclusions still apply.

The manager owns Plan, Decision and index edits, staging and authorized commits.
Delegate product changes. At most one executor writes; the manager makes no
project edits while it runs. Reviewers stay read-only except necessary complete
result publication under `.scoville/temp` using the shared delivery procedure.
Explorers have the same read-only permissions, investigate user requests and prepare planning,
returning concise answers, source evidence and material limits, not acceptance.
Apply [writing rules](writing.md). Number executors consecutively, including
corrections; reviewers use the reviewed executor's number. Retain exact handles
and launched pairs.

## Execute and accept one unit

1. Select the next authorized unfinished Step or coherent consecutive group.
   Preserve order, prerequisites and supplied grouping. Apply Plan's start or
   resume rules: active current_item and Work Item must be in_progress; start
   only the released Step/group. Preserve completed effects when reopening a
   confirmed correction and record its reason. Save and validate before writing
   dispatch. Report a changed position briefly.
2. Spawn one executor with that released unit. The whole Work Item is context,
   not additional scope. The executor finishes its coherent change, dependent
   edits and proportionate checks, stops writing and returns its native result.
   Wait on retained handles when no independent work is available. A timeout
   establishes no outcome and permits no replacement.
3. Match the host sender to the retained handle. Retain the complete result once
   and establish writer quiescence before review, Plan edits or another writer.
   Assess meaning, not formatting. Necessary missing executor facts and unfinished
   work paused for a decision or early review may use followup_task on the same
   handle. Completed assignments and corrections use fresh executors. Do not
   reactivate completed reviewers for questions; retain their evidence limits.
   Duplicate notifications create no work.
4. Follow user or project review cadence. Otherwise review the finished unit
   before acceptance. Earlier review is needed only before a separate product
   change depends on unreviewed changes or a named costly or consequential gate
   requires acceptance first. Dependent edits and focused checks of the same
   change stay together. Checked code alone, routine tests and Plan maintenance
   create no extra review phase.
5. Spawn a fresh independent read-only reviewer for the unreviewed scoped diff,
   affected Acceptance and relevant interactions. Review is required for code,
   executables, configuration, critical documentation, explicit requirements or
   unclear materiality. Critical documentation changes operating behavior,
   obligations or authority. Routine Plan status and Evidence require no extra
   review. Supply complete executor results and necessary sources without defending
   implementation or suggesting a verdict. Reuse earlier assessments only where
   reviewed content, requirements and supporting conditions remain unchanged.
6. Assign source findings to a fresh correction executor; handle Plan findings
   as manager. Preserve explicit model choices and retain the executor pair
   unless the cause warrants a justified configured replacement. Check corrections
   against findings. Material or unclear corrections and explicit requirements
   need independent review; accept clearly nonmaterial corrections by bounded
   comparison with a short reason. After two failed corrections, reassess cause.
   Do not repeat unaffected passed checks. After accepted early review, resume
   the same unfinished executor with acceptance, correction effects, remaining
   scope and evidence limits. Open findings, unanswered decisions and stops
   prevent dependent resumption.
7. After children stop writing, save observed Step statuses and decisive Evidence.
   Mark completed Steps done; selection is not start and unmarked status is
   unknown. Evidence contains outcome, required review occurrence and open limits,
   not full review prose. Remove fulfilled Instructions. Mark Work Item done only
   after Acceptance and required review pass. Validate the coherent Plan update.
   If authorized, inspect staged changes and commit accepted changes with Plan
   records, respecting hooks and backups. Create no agent, review or report solely
   for bookkeeping.
8. Finish this group's checks, due reviews, corrections and closure before
   assigning a later group to a fresh executor. Continue the next eligible authorized unit,
   honoring dependencies and Plan's pause/return rules. Close Plan and index only
   after the whole requested scope passes.

Do not repeat executor diagnosis or tests merely to assess a result. Check claims
against decisive evidence and investigate named gaps or contradictions. Moving
work to another item or Plan follows Plan's moved-work rule; replacing a child
within a unit creates no new scope.

## Results and decisions

Return minimal labelled facts and an explicit status; no fixed order or JSON.

| Status | Meaning and next action |
| --- | --- |
| completed | Executor implementation and checks finished; due review and closure follow. Explorer answer is ready; it grants no acceptance. |
| review_pending | Binding early review pauses unfinished work; name trigger and remaining scope. Resume after acceptance. |
| pass | Independent review found no unresolved defect or material acceptance gap. Return only pass. |
| changes_requested | Return open findings: location, defect, effect and smallest correction. |
| blocked / needs_user_decision | Name unmet prerequisite, diagnostic or question and affected work. Stop dependent work. |

Executors report completed effects, relevant paths, decisive checks, unverified
behavior and necessary next action, not an Acceptance verdict or work log.
Optional ideas neither block pass nor authorize correction.

Present blockers and decisions directly to the user without waiting for unrelated
checks. Record the question and paused point, then the actual answer before
resuming dependent work. Once writes stop, save necessary continuation state
before selecting independent eligible work. An unanswered question grants no
permission. Active execution or review is working, not blocked.

## Stop and resume

On user stop, dispatch no new work. Stop and interrupt running children by exact
handle. Confirm quiescence through native final or current list_agents state;
an interrupt's previous status alone proves no termination. Uncertain state
requires reporting the exact handle and diagnostic and prevents another writer.
Interruption does not undo changes.

Save and validate the observed Plan pause, preserving completed effects,
unfinished checks, open reviews and decisions. Pause an actually started item;
preserve todo or paused items without invented history. Resume only on explicit
user activation after writer state is known. Recover complete results and
continue the first unfinished action rather than repeating completed work.

## Compaction and child failure

Continue this same manager chat after host compaction from concise Plan state,
exact handles, complete results and pending decisions. Reconcile only missing
facts with relevant files and known child state. Compaction creates no successor,
context check or permission to repeat dispatch.

For a confirmed failed child, establish writer quiescence and completed effects
first. Assign known remaining work through an ordinary fresh scoped assignment
with retained evidence and constraints. An uncertain spawn, result or writer
prevents another dispatch until reconciled.

## Complete and exit

Confirm requested Acceptance, due review and Plan closure, then child and writer
quiescence. Report outcome and material limits directly. A bounded run can finish
with unrequested Plan work open; blockers and pauses are not completion. Return
to ordinary assistance afterward. New problems do not activate another run;
independent user and project requirements still apply.
