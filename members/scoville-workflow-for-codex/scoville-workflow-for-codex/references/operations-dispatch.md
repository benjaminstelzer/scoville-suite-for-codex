# Helper dispatch

Assign exactly ONE original Step. No ranges or whole-Work-Item execution.
`--unit W-001/step-2` selects execution or Step review; `--unit W-001` is only
reviewer closure. `--plan PLAN-NNNN` selects the canonical Plan; omission uses
the active Plan. Explorer Plan context needs a unit; omit both for inquiries
that need no Plan context.

## Choose models and retain agents

Resolve effective settings once; reading writes no configuration:

```text
python "<workflow>/scripts/resolve_model_pair.py" --show-config --project-root "<workspace>"
```

Re-resolve after relevant settings changes. Apply explicit user overrides only
to their named roles, and preserve explicit Step choices. The manager's host
pair never overrides subagent settings. Otherwise choose the configured route for the actual
assignment: ultra_low for trivial bounded work; low for a known mechanical
change; medium for unknown ownership, interacting contracts or interpreted
checks; high for consequential state or authorization/integration contracts;
ultra_high beyond high. File count alone does not raise a route. Unknown low
eligibility means at least medium. Do not write inferred routes into the Plan.
Validate the selected pair against exposed host capabilities without probing
unused models. Explorer's own route inherits executor fields unless overridden.
The pair belongs to the role within its owner: the Work Item for Executor and
Reviewer, this manager thread for Explorer. Reuse and every threshold or failure
replacement keep that pair. A later inferred route does not reset it.
An explicit user or Step override, or a required capability the retained pair
lacks, justifies a fresh agent; state the reason.

## Check the agent before every assignment

Retain each role's exact handle and launched pair. Executor
and Reviewer belong to the current Work Item; Explorer belongs to this manager
thread. Apply this agent check to execution, review, closure, corrections and
missing-result questions:

1. Find the owner's associated role agent.
   - None: first creation. Continue at step 5.
   - Confirmed failed or interrupted: complete [failure recovery](operations.md#stop-compaction-and-failure). End this agent check; recovery performs the redispatch. Do not measure it.
   - Otherwise continue. An ordinary completed `blocked` result is not a failed child.
2. Establish actual completion and idle state from the matching complete native
   final and native state. A status word alone proves neither. Running or
   uncertain: wait or reconcile; dispatch nothing. Never interrupt an active
   agent for the threshold.
3. Measure the bound agent's last completed turn:

   ```text
   python "<workflow>/scripts/check_agent_context.py" --project-root "<workspace>" --agent-id "<exact-handle>"
   ```

4. Act on the helper's returned `action`:

   | Result | Dispatch arguments |
   | --- | --- |
   | `reuse`: strictly below Setup threshold | Same agent: `--agent-id`, both retained `--model` and `--thinking`. If Workflow rules or the build changed since spawn, use fresh `--replacement-of` with that pair instead. |
   | `spawn`: at or above threshold | Fresh agent: `--replacement-of` from `replacement_of`, `--model` from `model`, `--thinking` from `reasoning_effort`. Keep the old agent idle. |
   | `blocked` or nonzero exit | No dispatch: report the technical problem. Neither reuse nor replacement is permitted, including a fresh pair-change route. |

5. Apply the pair choices above. First creation normally uses `--route`;
   explicit Step annotations remain binding. An authorized user role choice
   uses its pair flags and `--override-reason`. An explicit Step change uses
   fresh `--route`; a required exposed capability may justify a fresh pair.
   State the reason. A later inferred route never changes the retained pair.
6. Build the original assignment below and copy the returned arguments unchanged.

The context helper resolves exactly one native session from the retained handle
and this Manager's CODEX_THREAD_ID. Missing or ambiguous identity blocks dispatch;
never copy session IDs or search for similar names. It reads completed-turn last-call total_tokens and
model_context_window, never cumulative usage or live writing telemetry.
followup_task cannot change model or reasoning. Reuse omits `--route`;
`--route` combines with neither `--agent-id` nor `--replacement-of`.
`--replacement-of` combines with neither `--agent-id` nor `--override-reason`.
For reuse, the builder re-measures and verifies the retained pair before
publication. Fresh replacements retain pair checks but are not re-measured:
the manager must establish a `spawn` result, a `reuse` result with such a standing-rule/build change, or complete confirmed-failure recovery steps 1–3 first.
A mismatch or failed reuse measurement publishes nothing.

## Build the assignment

The manager supplies selection IDs, role and selected pair; the helper extracts
original Plan identity, Goal, Non-goals, binding Work Item fields, Instructions
and accepted linked Decisions. Only the selected Step body is included in a
Step assignment. Other Step bodies, accumulated Evidence and Work Item-wide
Next action are excluded. Closure includes the full original Work Item.
Do not compose, shorten, translate or rewrite those texts.

A fresh spawn or replacement receives role, writing, shell-command and result
rules once. Codex supplies applicable project instructions; do not add a second
AGENTS.md loader. A fresh Reviewer receives both Step and closure policies. Reuse through
`--agent-id` sends only the next task, original binding context, complete role
inputs and communication language. Do not reload project or role rules, already
loaded Skills or shared rules on reuse. Read current sources and newly needed
specialized references for the task. Never add rules to a reused assignment.

```text
python "<workflow>/scripts/build_dispatch_prompt.py" --project-root "<absolute-workspace>" --plan PLAN-NNNN --unit W-001/step-2 --role executor --communication-language "<language>" --format create --project-name "<project>" --worker-number <number> --route <class>
```

For every role, fresh or reused, supply `--communication-language` with the
language of the current user message, such as `German`, or the user's explicit
language choice. Do not infer it from Plan text, locale or child history.

The helper returns exact `target` and `message` for collaboration.followup_task
when the agent check selects reuse; otherwise it returns fresh spawn arguments
for collaboration.spawn_agent. Copy them unchanged into the named direct tool;
never call it through exec. Count new agents separately for each role throughout
this Manager thread. Fresh creation uses the next number; reuse keeps its number.
Keep counters across Work Items, pauses and compaction. Clearing a role association
does not reset its counter.

For Step review, use the SAME `--unit`, `--role reviewer` and
`--executor-result "<complete-native-result.txt>"`. For closure use `--unit W-001`
and the latest complete Executor final. Save native finals unchanged for both
levels; never compose a substitute result. Earlier results and coverage remain
in Work Item Evidence. Missing required change attribution prevents pass;
Git is not required when actual reported before/after lines are supplied.
Unchanged files provide relevant context only. Steps without file changes
still receive a review of their action and result.

Corrections and open review findings use `--reviewer-result "<complete-review.txt>"`
as additional context, never rewritten Step text. A missing-evidence follow-up
also passes the reviewed complete Executor final as `--executor-result`.
Its next review checks the original change with the completed evidence.
Correction executors retain
both launched model and thinking unless an explicitly justified selected pair
requires a new agent. Optional ideas do not become correction scope.

Explorer uses `--role explorer --supplemental-context "<complete-request.txt>"`;
quote the user's exact wording and add investigation constraints and source paths.
Preserve the requested reply format in Explorer context. Add a unit only when
needed. Other roles accept complete role results, not freely composed
supplemental dispatch text. Explorer investigates read-only and returns to
manager; no Plan writing, implementation, tests or acceptance.

## Delivery and failures

Prepare complete UTF-8 input files with literal-safe writes before calling the
builder. It reads no stdin. Require zero exit and complete successful output.
An input, selector, publication, spawn or capacity failure stops that operation;
an uncertain effect permits no retry or replacement. No automatic close or
sidebar workaround. Never repair or truncate failed helper output.

The builder publishes each assignment atomically to a unique system temporary
file only after an Executor's saved profile is valid and its active Plan,
current Work Item and selected Step are started. It performs this validation;
do not repeat it separately for dispatch. Review and Explorer assignments need
no execution start.
The assignment is outside the project. `--assignment-file` may select a new absolute readable
path. Keep it through execution/review; the child reads it completely before
work. `--format prompt` only returns text. Inaccessible or incomplete input
blocks dependent work; preserve host sandbox restrictions.

One effect-free corrected call is allowed only for an explicit invalid argument
or builder output-budget error before publication or dispatch. Use verified
inputs. A binding output cap needs its actual decision; never truncate context.
Missing helpers or other failures leave the operation blocked.

Wait on exact native handles; timeout is not completion. For oversized results,
require actual native completion, verify SHA-256 and read the whole supplied
file under the shared delivery procedure. Metadata and partial messages are
not results. Children may use the named external Python/checker only for command capture, size checks
and necessary result delivery; no unrelated access. They neither edit
Plan records, stage, commit, change Workflow settings nor create other agents.
