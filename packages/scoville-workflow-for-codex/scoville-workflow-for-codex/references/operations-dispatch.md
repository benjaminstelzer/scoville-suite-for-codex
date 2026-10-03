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
After completion the agent stays write-inactive. Context thresholds only schedule
rollover after the complete assignment and its required corrections and checks.
An explicitly authorized recovery handoff uses a successor for unfinished work.
Helper --unit values are W-001/step-5, W-001/steps-1-4, or W-001 for the
whole item. Keep step/steps lowercase in parameters; assignment labels preserve the exact unit casing.
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

The builder resolves the selected route internally for executor or reviewer.
Use --model and/or --thinking for explicit overrides on a new route. Keep
conflicting Step choices in separate ordered groups. A complete explicit pair
bypasses configuration. Recovery and correction require both arguments with
the original launched pair; never silently re-resolve them after settings change.
Only a justified, explicitly chosen replacement pair changes a correction's model.
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
results, questions and takeover notices. Reuse it for review, repair and recovery;
a forwarded agent request alone supplies no user permission.
Add only the Goals, Non-goals, current ADR provisions and dependency results
needed for this unit. Omit irrelevant context and ADR history. The manager
selects these facts so the child need not load the Plan.
For fresh assignments, do not duplicate the included Work Item's full Acceptance
in supplemental context. Reviews identify their affected criteria. Recovery
continuations must include applicable criteria because the Work Item is omitted.

Use the actual absolute workspace path for `--project-root`, never `.` or a
relative path. Before a fresh review, retain the original worker result in a
UTF-8 file and supply it through `--executor-result`; supplemental context does
not replace it. A recovery review uses the continuation inputs below.

Build the child assignment once. The helper selects the unit internally; do not
repeat selection to reconstruct its output or print the generated prompt as a
second tool result before sending it:

```text
python "<workflow-skill-directory>/scripts/build_dispatch_prompt.py" --project-root "<absolute-workspace-root>" --unit <unit> --role executor --format create --manager-agent-id <own-agent-id> --project-name "<project name>" --worker-number <number> --route <class> --supplemental-context "<facts.txt>"
```

For a fresh review, use the reviewed worker's number and retained result:

```text
python "<workflow-skill-directory>/scripts/build_dispatch_prompt.py" --project-root "<absolute-workspace-root>" --unit <unit> --role reviewer --format create --manager-agent-id <own-agent-id> --project-name "<project name>" --worker-number <number> --route <class> --executor-result "<worker-result.txt>" --supplemental-context "<review-facts.txt>"
```

The helper returns complete `spawn_agent` arguments as JSON: message, unique
role task name, fork_turns="none", model and reasoning_effort.
Every newly built native assignment has an automatic unique name suffix,
including repeated reviews of the same worker. This changes no role label,
scope or model. Use that generated name without requesting user permission.
Retain the complete arguments; do not repeat a failed or uncertain spawn
automatically. Validate and retain its actual model/reasoning_effort against
the host capabilities before spawning; no separate resolver or copy step is needed.
The message retains the project, canonical Plan ID and complete assigned range.
Provide the next worker number, or the reviewed worker's number for a reviewer.
A recovery continuation's task name includes its predecessor identity digest to avoid
reusing a reviewer task name. The bundled selector and Plan root are derived.
Supply the actual spawning manager ID explicitly with --manager-agent-id;
CODEX_THREAD_ID identifies a rollout and is not assumed to be an agent address.
Recovery/correction also supply --model <launched-model> --thinking <launched-effort>.
Role-specific inputs name existing UTF-8 plain-text files:

- Fresh review requires `--executor-result <result.txt>` with a completed, progress_pending or review_pending worker result. In
  supplemental context name the diff since the last review and affected Acceptance.
  For final review add short references to earlier assessments for unchanged
  parts. Include every still-unreviewed change and relevant interaction.
- Correction worker: `--role executor --reviewer-result <result.txt>`. Put the
  assigned source findings and needed context in supplemental context.
- Authorized recovery continuation: `--context-handoff <handoff.md> --predecessor-agent-id <id>`
  plus `--supplemental-context <facts.md>`. The handoff names remaining work,
  completed effects and next action. The facts contain only applicable acceptance
  criteria, constraints, permissions, evidence limits and required paths.
  Review continuations need no repeated full executor result. Carry relevant
  findings and the remaining review boundary in this compact context.
- Necessary facts: `--supplemental-context <facts.md>`.

Pass original text without JSON, escaping or another result schema. The
manager validates results before building the next assignment. The helper
reads no stdin. A nonzero exit reports ERROR and stops dispatch; do not repair
its output. Handle argument or selector-budget errors only under
[pre-dispatch correction](#pre-dispatch-correction).
For a new assignment the helper includes the complete selected Work
Item once. For a continuation it validates the selected unit but omits the Work
Item body and uses the compact handoff and required supplemental facts instead.
The unit remains an identity, not an instruction to repeat completed Steps.
Written Step progress accompanies the assignment; reviews and assigned
corrections retain their exact scope even when its Steps are marked done.
The helper does not choose applicable acceptance criteria, Goals, Non-goals or
ADR provisions. Supply those selected facts through --supplemental-context;
reviewers and recovery successors need the same still-relevant constraints.
Supplemental context supplies project facts, not copies of the builder's role,
checkpoint or delivery rules. Reuse an existing selection for scope decisions;
the builder's internal selection needs no separate preview call.

### Pre-dispatch correction

One corrected helper call before reporting BLOCKED is allowed for an explicit
invalid-argument diagnostic from `build_dispatch_prompt.py`, or
`OUTPUT_BUDGET_EXCEEDED` from that builder or `run_feedback.py progress`.
No agent start or progress-message send may have been attempted, and the failed
call must have produced no assignment file or other effects.
Use already verified facts, such as the absolute workspace path or retained
original worker result. Correct the input, never failed output. Dispatch only
the corrected call's complete successful output.

For `OUTPUT_BUDGET_EXCEEDED`, pass `--max-output-bytes <required_bytes>` to the
failed helper using the diagnostic's required size, within any caller-imposed budget.
This forwards a bounded budget to the bundled selector and preserves complete
context. Do not replace the selector with an adapter or truncate the result.

If required facts are missing, the correction fails, or effects or agent state
are uncertain, retain the diagnostic and report the blocker under run-feedback.md.
Do not invent a worker result, bypass validation or repeat a spawn. This exception
does not cover other helper failures, capacity refusals or uncertain delivery.

### Native dispatch and results

Call `spawn_agent` directly with the generated arguments. Collaboration tools
are direct tool calls, not tools inside functions.exec. Check the builder's zero
exit and complete output, then copy its JSON fields unchanged into the native
call. For a fresh child on a direct-tool host, use
--assignment-file "<new-absolute-temporary-file>" to avoid retyping a long message. The builder saves the complete
assignment verbatim and returns a short native message that directs the child
to read it. Keep that file through completion and review. The directory must
exist and the file must be new; recovery continuations retain their direct
handoff prompt. Copy the returned fields exactly, including punctuation and
whitespace; never paraphrase supplemental text. Do not print or rebuild another
copy. Stop on truncated output or a helper error; never dispatch a partial prompt.

Retain the exact returned agent ID with its role, unit and launched pair. Require
one unambiguous identity. A failed or uncertain spawn, including capacity refusal,
is BLOCKED. Preserve the diagnostic, retained results and unfinished assignment
under operations.md. Inspect only known identities with `list_agents`; no
automatic retry, completed-agent cleanup or replacement chat. No new writer
starts until prior writes are quiescent.
Native agents have no sidebar pins or archival step.

A fresh child starts its assignment on spawn. A recovery child first completes
the manager receipt/release gate in operations-rollover.md. READY/START belongs
to manager startup, not child dispatch. Wait with `wait_agent` for native completion or user input;
a timeout is not failure or permission to start another child. Match the result's
host sender identity to the assigned agent, retain it once, and apply operations.md.
Do not use chat tools, title matching or repeated result requests for coordination.

The child owns only assigned project changes. It cannot edit canonical Plan
records, stage/commit, dispatch successors or change Workflow/model settings.
Product and test configuration may change only within the assigned scope and
project constraints; reviewers remain read-only. Its complete final answer is
delivered natively to the spawning manager. Require native delegation, completion
and interruption support before dispatch; never fall back to new chats.
