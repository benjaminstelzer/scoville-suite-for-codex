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
in operations.md; no overlapping groups. Reuse the available worker for related
groups with the same model/effort when context permits. Build and send its complete
next assignment once, updating its title to the assigned range. Otherwise create
a worker. An inherited context_handoff always uses a successor.
Helper --unit values are W-001/step-5, W-001/steps-1-4, or W-001 for the
whole item. Keep step/steps lowercase in parameters; uppercase STEP/STEPS
belongs only in the displayed task title.
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
For repair use `--role repair --original-model <model> --original-reasoning
<effort> --repair-number <1|2|3>`. Record the actually launched original pair.
An absent pair in the current route table blocks escalation with its diagnostic;
do not invent the cause or build an immutable repair schedule.
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

Build the child assignment once. The helper selects the unit internally; do not
repeat selection to reconstruct its output or print the generated prompt as a
second tool result before sending it:

```text
python "<workflow-skill-directory>/scripts/build_dispatch_prompt.py" --project-root "<workspace_root>" --unit <unit> --role <executor|reviewer|repair>
```

The helper returns the complete assignment as plain text, ready for create_thread.
The bundled selector and Plan root are derived. CODEX_THREAD_ID supplies the
coordinator ID; use `--return-to-thread-id <id>` only when the host does not set it.
Optional arguments name existing UTF-8 plain-text files:

- Review: `--executor-result <result.txt>` with a completed worker result; for a
  whole-item review, add concise references to earlier group results and the
  full relevant diff through supplemental context. Do not omit unreviewed groups.
- Repair: `--reviewer-result <result.txt> --repair-assignment <findings.txt>`.
- Continuation: `--context-handoff <handoff.md>`.
- Necessary facts: `--supplemental-context <facts.md>`.

Pass original text without JSON, escaping or another result schema. The
coordinator validates results before building the next assignment. The helper
reads no stdin. A nonzero exit reports ERROR and stops dispatch; do not repair
its output. The helper includes the complete selected Work Item once, with the
exact assigned unit stated separately. It does not choose Goals, Non-goals or
ADR provisions. Supply those selected facts through --supplemental-context;
reviewers and rollover successors need the same still-relevant constraints.
Supplemental context supplies project facts, not copies of the builder's role,
checkpoint or delivery rules. Reuse an existing selection for scope decisions;
the builder's internal selection needs no separate preview call.

For a new worker, call `create_thread` directly with the generated `prompt`, role-counter `title`,
resolved `model` and `thinking`, and
`target:{type:"project",projectId:<saved-id>,environment:{type:"local"}}`.
Record the intended unit before the call, then retain the
returned task/host ID in the same run record. No lifecycle-helper wrapper,
parking task, fork or shared-history subagent is needed.

A ready task needs its actual `threadId` and `hostId`; `clientThreadId` alone is
not ready. Use host-provided correlation to resolve pending creation. Titles alone do not identify a
task. If creation remains ambiguous, stop before another creation attempt.
No byte, hash or delivery receipt is required.

Build and create within one code cell, using the host's actual tool names.
`buildCommand` is the documented shell command with its paths safely quoted;
`pair`, `title` and `projectId` are already resolved values:

```javascript
const outputLimit = 16000;
const built = await tools.exec_command({cmd: buildCommand, max_output_tokens: outputLimit});
if (built.exit_code !== 0) throw new Error(built.output);
if (built.original_token_count > outputLimit) {
  throw new Error("Assignment output was truncated; do not dispatch it. Reduce the assigned scope or unnecessary context and rebuild.");
}
const created = await tools.mcp__codex_app__create_thread({
  prompt: built.output, title, model: pair.model, thinking: pair.thinking,
  target: {type: "project", projectId, environment: {type: "local"}}
});
text(created); // creation identity only; never print the generated assignment
```

Inspect the native creation response for readiness and retain its actual ID.
Before ending the coordinator turn, satisfy any host-required wait for progress.
Then use result messages, without a polling loop. Do not reconstruct the native
response as a lifecycle-helper payload.

The receiver owns only the assigned project changes. It cannot edit canonical
Plan records, stage/commit, create successors or change configuration. Its final
answer uses the existing `SCOVILLE_RESULT_V1` contract supplied by the builder.
The child sends one completion notification and then its final result, as
specified by the builder. Require this message capability and the user's
ongoing coordination authorization before dispatch. If unavailable, report
that limitation rather than silently starting a polling workflow.
