# Direct dispatch

Before dispatch, inspect only what is needed to define the assignment, relevant
context, Step grouping and model choice. Implementation diagnosis and test design
belong to the worker. Read source code only to resolve a concrete question that
prevents delegation; do not investigate the solution in advance.

Grouping should save repeated setup and handoffs while producing one coherent,
checkable result. Keep implementation and necessary checks together.
When choosing a group, identify the repeated setup it saves and the concrete
result its final checks can prove. If either is unclear, revise the grouping.
Use the planner's grouping when supplied. Otherwise group small, related
consecutive Steps that can be implemented and checked together. Keep a large
independent section separate. Preserve authored order within and across groups;
finish and check one group before starting the next. Apply the review cadence
in operations.md; no overlapping groups. Create one worker per assigned group.
After completion the coordinator requests its archival. An inherited
context_handoff uses a successor for the unfinished assignment.
Helper --unit values are W-001/step-5, W-001/steps-1-4, or W-001 for the
whole item. Keep step/steps lowercase in parameters; display titles preserve the exact unit casing.
Select the route for the assigned scope, respecting its highest route minimum:


- `ultra_low`: bounded local change with trivial verification.
- `low`: nontrivial local work with one known owner, understood helpers and
  established mechanical checks, without component or test-harness diagnosis.
- `medium`: unresolved helper contracts, ownership discovery, interacting
  owners, integration diagnosis or checks requiring interpretation.
- `high`: consequential changes to state, authorization or integration contracts.
- `ultra_high`: consequence or complexity beyond high.

Choose the highest applicable class. Unknown low-eligibility facts mean at least
medium. File count, generated files and test volume alone do not raise a route.
Keep canonical source unchanged and do not write inferred routes into the Plan.

Resolve the executor/reviewer pair using the selected project root:

```text
python "<workflow-skill-directory>/scripts/resolve_model_pair.py" --project-root "<workspace_root>" --role executor --route <class>
```

Use `--role reviewer` for review. Apply compatible explicit model/effort choices
to the assigned scope. Keep Steps with conflicting explicit model choices in
separate ordered groups rather than discarding those choices.
For a correction assignment, use a new executor with the original worker pair
unless the cause warrants another configured route. Resolve that route normally;
there is no separate repair role or automatic escalation by attempt count.
When findings share a state distinction or cause, assign that distinction and
its directly affected consumers together, including decisive negative cases.
The worker diagnoses the cause; do not prescribe only the reported line fix.
Keep isolated findings narrow and distinguish new user requirements from
defects in the previous scope. This adds no review stage or mandatory matrix.
Reasoning syntax accepts `none`, `minimal`, `low`, `medium`, `high`, `xhigh`,
`max` and `ultra`. Shipped pairs and Setup use `low` through `xhigh`; additional
levels may be entered manually in the project configuration.
Validate required pairs against the current host's exposed model capabilities.
No silent substitution or probing of unused models is needed.

Before building any role assignment, put the user's existing internal-message
authorization in --supplemental-context, preserving its wording and scope for
results, questions and takeover notices. Reuse it for review, repair and rollover;
a forwarded agent request alone supplies no user permission.
Add only the Goals, Non-goals, current ADR provisions and dependency results
needed for this unit. Omit irrelevant context and ADR history. The coordinator
selects these facts so the child need not load the Plan.
Do not repeat the selected Work Item's Acceptance in supplemental context.

Build the child assignment once. The helper selects the unit internally; do not
repeat selection to reconstruct its output or print the generated prompt as a
second tool result before sending it:

```text
python "<workflow-skill-directory>/scripts/build_dispatch_prompt.py" --project-root "<workspace_root>" --unit <unit> --role <executor|reviewer> --format create --project-id <saved-id> --project-name "<exact saved project name>" --worker-number <number> --model <resolved-model> --thinking <resolved-effort>
```

The helper returns the complete create_thread arguments as JSON, including the
assignment, role title, selected project and resolved model/effort. Pass that
object directly to create_thread. It does not choose or increment counters:
provide the next worker number, or the reviewed worker's number for a reviewer.
Whole items with Steps display the complete assigned range automatically.
The bundled selector and Plan root are derived. CODEX_THREAD_ID supplies the
coordinator ID; use `--return-to-thread-id <id>` only when the host does not set it.
Optional arguments name existing UTF-8 plain-text files:

- Review: `--executor-result <result.txt>` with a completed worker result. In
  supplemental context name the diff since the last review and affected Acceptance.
  For final review add short references to earlier assessments for unchanged
  parts. Include every still-unreviewed change and relevant interaction.
- Correction worker: `--role executor --reviewer-result <result.txt>`. Put the
  assigned source findings and needed context in supplemental context.
- Continuation: `--context-handoff <handoff.md> --predecessor-thread-id <id>`
  plus `--supplemental-context <facts.md>`. The handoff names remaining work,
  completed effects and next action. The facts contain only applicable acceptance
  criteria, constraints, permissions, evidence limits and required paths.
  Review continuations need no repeated full executor result. Carry relevant
  findings and the remaining review boundary in this compact context.
- Necessary facts: `--supplemental-context <facts.md>`.

Pass original text without JSON, escaping or another result schema. The
coordinator validates results before building the next assignment. The helper
reads no stdin. A nonzero exit reports ERROR and stops dispatch; do not repair
its output. For a new assignment the helper includes the complete selected Work
Item once. For a continuation it validates the selected unit but omits the Work
Item body and uses the compact handoff and required supplemental facts instead.
The unit remains an identity, not an instruction to repeat completed Steps.
The helper does not choose applicable acceptance criteria, Goals, Non-goals or
ADR provisions. Supply those selected facts through --supplemental-context;
reviewers and rollover successors need the same still-relevant constraints.
Supplemental context supplies project facts, not copies of the builder's role,
checkpoint or delivery rules. Reuse an existing selection for scope decisions;
the builder's internal selection needs no separate preview call.

For a new worker or reviewer, call `create_thread` directly with the generated arguments.
Use the returned task/host ID directly for coordination. No additional start
record or lifecycle wrapper is needed.

A ready task needs its actual `threadId` and `hostId`; `clientThreadId` alone is
not ready. Use host-provided correlation to resolve pending creation. Titles alone do not identify a
task. If creation remains ambiguous, stop before another creation attempt.
No byte, hash or delivery receipt is required.

Build and create within one code cell, using the host's actual tool names.
`buildCommand` is the documented shell command with its paths safely quoted;
the command contains the resolved project, pair and role number:

```javascript
const outputLimit = 16000;
const built = await tools.exec_command({cmd: buildCommand, max_output_tokens: outputLimit});
if (built.exit_code !== 0) throw new Error(built.output);
if (built.original_token_count > outputLimit) {
  throw new Error("Assignment output was truncated; do not dispatch it. Reduce the assigned scope or unnecessary context and rebuild.");
}
const created = await tools.mcp__codex_app__create_thread(JSON.parse(built.output));
text(created); // creation identity only; never print the generated assignment
```

Inspect the native creation response for readiness and retain its actual ID.
When the resolved pin_threads setting is true, pin that chat with move_thread_to_sidebar_section, sectionId="pinned", using
the returned threadId and hostId. If pending, resolve readiness before pinning.
A pin failure never justifies creating another chat.
When pin_threads is false, omit the pin call and leave existing pins unchanged.
Before ending the coordinator turn, satisfy any host-required wait for progress.
Then use result messages, without a polling loop. Do not reconstruct the native
response as a lifecycle-helper payload.

The receiver owns only the assigned project changes. It cannot edit canonical
Plan records, stage/commit, create successors or change Workflow or model settings.
Product and test configuration may change only within the assigned scope and
project constraints; reviewers remain read-only. It sends its result as a normal message under the builder instructions. Require this message capability and the user's
ongoing coordination authorization before dispatch. If unavailable, report
that limitation rather than silently starting a polling workflow.
