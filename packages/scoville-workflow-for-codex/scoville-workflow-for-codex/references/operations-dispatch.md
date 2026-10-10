# Direct dispatch

Inspect only facts needed for scope, grouping and model choice; implementation
diagnosis and test design belong to the executor. Use supplied Step groups.
Otherwise group consecutive related Steps with one coherent, checkable result;
keep implementation and necessary checks together. Preserve order and finish
one group, including due review and corrections, before releasing the next.
Each released group gets one fresh executor. Work Item context grants no later
Steps. Use `--unit W-001/step-5`, `W-001/steps-1-4` or `W-001` only when the
whole item is actually released as one coherent group. Keep step/steps lowercase.

## Model choice

Choose the highest applicable route for the released work and its checks:

| Route | Minimum context |
| --- | --- |
| ultra_low | Bounded local change, trivial verification. |
| low | Known owner and helpers, established mechanical checks; no ownership or test-harness diagnosis. |
| medium | Unknown contracts or ownership, interacting owners, integration diagnosis or interpreted checks. |
| high | Consequential state, authorization or integration contracts. |
| ultra_high | Consequence or complexity beyond high. |

Unknown low eligibility means at least medium. File count, generated files and
test volume alone do not raise the route. Do not write inferred routes into the
Plan. Preserve explicit user choices and route minimums. The builder resolves
executor, reviewer and explorer routes; `--model`, `--thinking` or both override new routes.
Correction requires both retained launched fields or an explicitly justified
replacement for its actual work. Do not replace a child merely to lower its model.
Validate selected pairs against exposed host capabilities without probing unused
models. Reasoning accepts none, minimal, low, medium, high, xhigh, max and ultra;
shipped routes use low through xhigh.

## Prepare assignment

Supply exact existing UTF-8 paths. Discover unknown names from inventories.
Supplemental context contains existing user coordination authorization with its
wording and scope, explicit Skill invocations, and necessary Goals, Non-goals,
ADR provisions, permissions and dependency results. Agents independently select
Skills. Do not prescribe a fixed Skill list or duplicate the included Work Item's
full Acceptance. Preserve model conflicts by separate ordered groups.

Use the actual absolute workspace path. Retain the complete native executor final
and save all its substantive facts for `--executor-result`: status, literals,
changed effects, checks, findings, constraints and evidence limits. Preserve
relevant earlier results when multiple executors affected the reviewed unit.
Formatting may change, meaning may not. Supplemental context does not replace
this result.

```text
python "<workflow-skill-directory>/scripts/build_dispatch_prompt.py" --project-root "<absolute-workspace-root>" --unit <unit> --role executor --format create --manager-agent-id <own-agent-id> --project-name "<project name>" --worker-number <number> --route <class> --supplemental-context "<facts.txt>"
```

Fresh independent review uses the reviewed executor's number:

```text
python "<workflow-skill-directory>/scripts/build_dispatch_prompt.py" --project-root "<absolute-workspace-root>" --unit <unit> --role reviewer --format create --manager-agent-id <own-agent-id> --project-name "<project name>" --worker-number <number> --route <class> --executor-result "<worker-result.txt>" --supplemental-context "<review-facts.txt>"
```

For a user question, change request or planning preparation, assign one fresh read-only Explorer.
Classify the investigation, not a hypothetical implementation. Its `explore`
route inherits the effective `execute` pair except explicitly configured fields.
Number Explorers separately. Supply the complete request and necessary scope,
constraints and source paths in `--supplemental-context`. Add `--unit` only when
the Work Item is needed; otherwise no Plan selection runs. No executor result is
required. Mark facts affected by concurrent writes as provisional.

```text
python "<workflow-skill-directory>/scripts/build_dispatch_prompt.py" --project-root "<absolute-workspace-root>" --role explorer --format create --manager-agent-id <own-agent-id> --project-name "<project name>" --worker-number <explorer-number> --route <class> --supplemental-context "<question-and-facts.txt>"
```

An Explorer answer informs the manager; it does not write the Plan, accept work or
authorize implementation. The manager writes authorized Plan changes. Continue
the normal executor/reviewer cycle for approved changes.

Correction uses `--role executor --reviewer-result <result.txt>` and both
`--model <launched-model> --thinking <launched-effort>`. Supply assigned defects
and necessary context, not optional ideas. After a confirmed failed child and
writer quiescence, ordinary fresh assignment facts identify retained effects,
known remaining work and constraints; no transfer handshake is needed.

Review facts name the unreviewed diff, affected Acceptance and relevant
interactions. Supply exact Plan/Decision paths and sections only when needed as
review evidence. This grants reviewers no maintenance, tests or unrestricted
search. For tracked files, `git diff --output="<diff-file>" <base> -- <paths>`
prepares the complete scoped diff without displaying it. Reviewers read untracked
sources directly from supplied paths through bounded reads. Do not stage solely
for review or ask reviewers to capture source files. Reuse unchanged accepted
assessments with their identity and limits; reopen only for a new claim, gap or
contradiction. Supply facts without defending implementation or suggesting verdict.

Finish and verify input files under shared writing rules before invoking the
builder. It reads no stdin. Require zero exit and complete successful output;
never repair failed or truncated output. The builder includes complete Work Item
context once and literal plan.non_goals under its own heading. Exclusions have
an 8192-byte UTF-8 cap, including heading and newlines. Overflow prevents dispatch;
shorten redundancy while preserving every exclusion. Goal and Decision sections
are selected by the manager, not automatically inserted. Reuse internal
selection; do not call a separate preview merely to reconstruct the prompt.

## Publication and native creation

For `--format create`, the helper atomically publishes the complete assignment
to a unique system temporary path outside the project without overwriting.
Optional `--assignment-file <new-absolute-file>` selects a readable path.
Retain the file through execution and review. A child reads it completely before
work; inaccessible or incomplete input blocks dependent work. Respect its actual
sandbox; do not bypass it or silently copy an assignment. `--format prompt`
returns inline content and accepts no assignment file.

The builder returns all native spawn arguments: task_name, message,
fork_turns="none", model and reasoning_effort. Copy them unchanged into direct
`collaboration.spawn_agent`; never call collaboration through functions.exec.
The unique name preserves project, canonical Plan ID and full assigned range.
Use the actual manager agent identity, not an inferred CODEX_THREAD_ID. Retain
exact returned child identity, unit, role and launched pair. Do not rebuild,
reprint or paraphrase assignments before dispatch.

A failed or uncertain spawn, including capacity refusal, blocks that operation.
Retain the diagnostic and continuation state. Inspect known identities only;
no automatic retry, replacement sidebar chat or completed-agent cleanup.
No new writer starts until prior writes are quiescent. Children need no sidebar
pins, archival or invented close tool.

## Bounded pre-dispatch correction

One corrected call is allowed for an explicit invalid argument,
OUTPUT_BUDGET_EXCEEDED from the builder, or complete
PYTHON_INTERPRETER_REQUIRED child_started=false before the authorized call.
No spawn may have been attempted and no assignment or other effect produced.
Use verified facts; correct inputs, never failed output. Another failure, missing
facts or uncertain effects stops the operation with its actual diagnostic.

A selector-budget error supplies a complete corrected invocation with explicit
--max-output-bytes. An agent-selected internal cap may be raised to required size;
a binding user, Plan or host cap needs the actual decision first. Preserve all
context and actual tool-output limits. Never replace or truncate the selector.
Other helper failures, capacity refusals and uncertain delivery grant no retry.

## Results and permissions

Wait using native events and retained handles. Timeouts prove neither failure
nor permission for another writer. Match native sender to assigned identity;
retain results once and apply operations.md. For complete-file result delivery,
require actual child completion, verify SHA-256 and read the entire file before
accepting its contents. Metadata alone is not a result. Do not coordinate through
sidebar chats, title matching or repeated result requests.

Children may use the named Python and checker for bounded UTF-8 reads, capture
and size checks even outside the workspace. Only necessary oversized-result
preparation/publication permits writes under `.scoville/temp`; reviewers still
cannot run tests or change the reviewed subject. Host restrictions apply.

Children own only their assigned changes. They cannot edit Plan, Decision or
index records, stage or commit, create agents/chats or change Workflow/model
settings. Product/test configuration changes require assigned scope. Complete
native finals deliver results directly to this visible manager.
