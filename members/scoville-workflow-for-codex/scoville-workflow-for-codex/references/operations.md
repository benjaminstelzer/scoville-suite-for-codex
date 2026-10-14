# Manager operations

Use Plan for records and [dispatch](operations-dispatch.md) for assignments.
Preserve authorized scope, Decisions, stops and unrelated changes. The manager
writes records, never source. Only one executor writes; stop its writes before
record edits, review or another writer. Read only what manager decisions need;
the executor diagnoses implementation and the reviewer inspects technical details.

{{ include: family.contract }}

## Runtime and communication

Use the same manager thread and actual workspace. Verify native collaboration
spawn_agent, followup_task, send_message, wait_agent, list_agents and interrupt_agent
are available. Retain exact handles, never titles or sidebar IDs. The host pair
belongs only to the manager; Setup owns subagent pairs and user overrides name a role.

Load output-delivery.md only under shell-rule triggers. Reuse needed
Skills, unchanged evidence and passing checks. Retain role counters, launched pairs,
assignments, complete results and open findings across pauses and compaction.

Use the current user message's language unless explicitly overridden; Plan owns
record language. Internal messages are short labelled fields. Preserve required
fields/statuses, quotes, user wording and technical literals. Before acting, check
request, role, scope, prerequisites and complete unchanged inputs. Before sending,
check language, required fields and evidence for completion claims. Correct a
mismatch or stop dependent work; do not output a checklist transcript.

When the target is known, set this chat's title to `SC-WFL <Plan-ID>` with
set_thread_title and no threadId. Change it only for authorized work in another
Plan, not pauses/compaction; report rename errors. Report changed positions as
`Working on: <project> → <Plan-ID> → <Step or Work Item>`, translating the label.
Waiting for a child is working; blocked means an actual unmet prerequisite.
Keep this turn active with native waits while a child runs, never a final answer.

## Execute one Step

On explicit activation, before Plan writes, require a Git worktree and empty
`git status --porcelain --untracked-files=all`. A failed command or listed path
blocks activation: report it, start no Executor, and never discard, stash, stage
or commit existing work to become clean. Exception: if every listed path is under
`.scoville/temp` and it has no `.gitignore`, create
`.scoville/temp/.gitignore` containing `*` and check again. These are earlier temporary results, not project work.
Continuation, compaction and rule reload do not repeat activation or interrupt a writer.

Follow the entrypoint's loop with these boundary rules:

| Boundary | Required action |
| --- | --- |
| Work Item start | Select authorized Plan/item and one original Step, preserving order/dependencies. Record HEAD in existing Evidence for closure. Save actual start/resume through Plan; selection alone starts nothing. The builder validates saved profile and started state. |
| Dispatch | Apply the agent check, build the unchanged assignment and copy its returned native arguments. |
| Executor completion | Wait for the matching complete native final and writer quiescence; timeout permits neither failure recovery nor replacement. Assess completion, required checks and clear effects as below. |
| Changed Step | Review every Step changing files, configuration or behavior. A truly unchanged Step needs no Step review or Step commit; closure checks it. An open review remains open after evidence-only follow-ups. |
| Correction | Pass changes_requested objections unchanged to the same original Step; execute and review the correction. Never rewrite the Step, expand scope or implement optional ideas. Reuse unaffected checks/coverage, retain open findings/limits; earlier coverage is not a current pass. |
| Accepted changed Step | Only after completion and required review pass, record status/evidence and commit reviewed changes with Plan progress before selecting the next Step. Foreign/unreviewed work blocks this boundary; name its paths, never stage it. Failed/forbidden commit stops advancement. Confirm clean Git; no empty commit. |
| Completed unchanged Step | Record progress; invent no review pass. Routine Plan edits create no extra review. |

Assess a complete Executor result against `git status` and `git diff --stat HEAD`,
including reported paths. Check configuration, behavior and ignored-output effects
Git cannot show. Read supporting artifacts only when necessary for these manager
decisions; always read the complete native final or complete externalized result.
For a missing/unclear result, use the same-Step helper before advancing or deciding
review; supply its available complete prior final as --executor-result and preserve
required review inputs. If it cannot supply required non-Git evidence, report the
exact prerequisite: no loop, invented evidence or false unchanged classification.
A blocker returns to manager; ask only for a necessary user decision.

A Step review receives the same original Step and unchanged complete Executor final.
It covers actual changes, relevant effects and open findings at depth proportionate
to risk, without wider scope or skipped required review. Use Git and reported effects
to decide whether changes exist.

## Close the Work Item

After every Step is complete and required Step reviews pass, choose the Work Item's
Reviewer through the agent check. Closure receives the whole original Work Item,
all Steps and full Acceptance, comparing current implementation and retained evidence.
This checks closure, not unrelated general quality.

Findings keep the same Plan/item: select one affected original Step, pass unchanged
objections, execute it, review when required above, then repeat closure. If no existing
Step covers an omitted implementation, append one Step only for a named already
binding, unchanged Acceptance criterion or Work Item requirement. Run the normal loop.
Changed scope/Acceptance, contradictions or materially unclear meaning need the user;
never invent a Step to bypass them. Preserve original Steps, order and completed effects.

Mark done only after Acceptance and closure pass. Validate and commit the coherent
Plan update under repository checks/backups. Clear Executor/Reviewer associations
for the next Work Item; retain Explorer for this manager thread. Complete only the
authorized scope; bounded runs can leave unrequested work open.

## User requests and results

Send questions, ideas, change requests and planning preparation to Explorer through
the agent check, with the complete request and necessary context. Its own configured
pair defaults to executor fields. It returns minimal findings, source evidence and
limits, never Plan writes or implementation acceptance. Answer in the communication
language, preserving quotes, literals and evidence limits. Handle stop, resume and
known progress directly. Stop invalidated execution before exploring the change.

| Result | Meaning |
| --- | --- |
| done | Assigned execution/checks or exploration finished; not review acceptance. |
| pass | Assigned review ran with no unresolved defect or required evidence gap. |
| changes_requested | Open defect, location, effect, smallest correction and affected Step, or none. |
| blocked | Actual prerequisite or required decision prevents dependent work. |

Match actual completion and complete final to the retained handle and assignment,
never titles or partial messages. Save the final unchanged with a literal-safe write
before dependent dispatch. Concise Plan evidence never substitutes for a child result.

For required missing Executor evidence after a blocked review, apply the agent check
and rebuild that same Step with complete unchanged finals:

| Dispatch | --executor-result | --reviewer-result |
| --- | --- | --- |
| Executor supplies evidence | Final the blocked review checked | Blocked Reviewer final |
| Next review | Returned Executor final | Same blocked Reviewer final |

This evidence-only follow-up makes no new changes or repeats unchanged successful
checks merely to supply evidence; review continues the original change. Replacement
proves no missing baseline. Report unavailable baseline or prerequisite; other
missing-result questions also use the exact child's agent check and helper.
Report blockers/decisions directly, stop dependent work, and preserve completed
effects and the actual answer before continuing. Nonblocking problems may reach review.

## Stop, compaction and failure

On user stop, dispatch nothing new and interrupt running children by exact handle.
Confirm termination through native finals or current list_agents state; an interrupt's
previous status proves no termination. Report uncertain handles/diagnostics and start
no competing writer. Then save and validate observed pause, unfinished checks, open
reviews and decisions. Resume only on explicit activation.

After compaction, normally recover Plan state through its scoped selection route.
Read a specific Plan or Decision directly when authoring, resolving a conflict
or independently checking facts requires it. Recover the same assignments,
actual results and completed effects; repeat no completed work to rebuild history.
For a confirmed failed/interrupted
child: establish termination, reconcile effects/checks, clear its association without
measurement/reuse, then redispatch the same unit/role with unchanged role inputs and
open findings. Use the helper, next role number and --replacement-of with the retained
pair unless explicit Step/user choice changes it. Completed blocked is not failed.
Never bypass failed idle-agent measurement. Uncertain spawn/result forbids duplicate dispatch.

Before leaving, commit pending owned Plan records only when no unreviewed implementation
remains; otherwise report dirty paths. Completion requires requested Acceptance,
required Step reviews, closure review, Plan closure and quiescent children/writers.
Report outcome and limits in the user's language and return to ordinary assistance.
Blockers/pauses are not completion; new requests start no automatic successor.
