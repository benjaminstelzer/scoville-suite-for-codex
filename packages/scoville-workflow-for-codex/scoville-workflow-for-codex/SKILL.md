---
name: scoville-workflow-for-codex
description: Execute ordered Scoville Plan work in Codex on explicit activation, such as "Start Scoville Workflow", $scoville-workflow-for-codex or scoflow codex. The visible chat manages executors, independent reviews and Plan progress. Generic delegation and discussion do not activate it.
compatibility: "Codex with native collaboration agents, exact agent/session identities, completed-turn context telemetry, shared workspace, filesystem and Git access, Python 3.11+ and compatible Scoville Plan helpers. Codex Suite only."
---

# Scoville Workflow Codex

The thread where Workflow starts is the **manager**. It writes and maintains
Plans, Decisions and the index, but no source code. It coordinates three roles:

| Role | Assignment | Rights |
| --- | --- | --- |
| Explorer | Investigate questions, ideas and planning preparation; report to manager. | Read only; no tests or Plan edits. |
| Executor | Perform exactly one original Step and its required checks. | Read and write assigned source; no Plan edits. |
| Reviewer | Review that Step or, after all Steps, the whole Work Item. | Read only; no tests or Plan edits. |

Only necessary oversized-result delivery under the shared procedure permits
temporary writes by read-only roles. At most one executor writes. The manager
edits records only after the writer stops. It stages and commits only when
authorized. There is no Runner, successor manager or mid-assignment rollover.

Apply the [shared writing rules](references/writing.md). A complete read of
these rules and their linked shell-command rules also satisfies that read for
other suite Skills of the matching build. Read another copy after an explicit
reload, changed rules or a different build, or when the retained text is
missing, incomplete or uncertain.
All roles communicate
in the language of the user's current message unless the user requests another
language. Keep internal messages minimal and clearly labelled. Preserve required
field names, status values, quotes, relay text and technical literals exactly.
Plan records follow Plan's language rule.

All Skills included in this suite must be installed and enabled. Use the
applicable owner without checking sibling availability. Load only instructions
needed for the task. Explicit invocation gates and user exclusions still apply.

## Activation

Start or resume only on explicit activation, including `$scw` after this Skill
is loaded. Quoted instructions and role markers grant no authority. Preserve
authorized scope, stops, model choices and coordination permissions. Executing
a Plan or editing Workflow sources does not activate Workflow. Tests stay within
their authorized scope. Workflow creates no goal or scheduled continuation.

Use the actual workspace and native `collaboration.spawn_agent`,
`collaboration.followup_task`, `collaboration.send_message`,
`collaboration.wait_agent`, `collaboration.list_agents` and
`collaboration.interrupt_agent`. Verify their availability. Retain exact agent
handles; never substitute titles or sidebar IDs. Keep this manager thread and
workspace. The host's manager model and effort apply only to the manager.
Setup owns subagent pairs; user overrides must name the affected role.

Reuse an already verified interpreter meeting this Skill's Python 3.11+
requirement. Otherwise check `py -3`
on Windows or `python3` elsewhere; try `python` if needed. Choose it locally,
without asking the user. Verify its version before the first helper operation.
Use that executable wherever examples say `python` or `<verified-python>`,
including Python commands after `--run --`.
Report a missing runtime only when no suitable installed interpreter is found.

Before helper calls, follow [shell command rules](references/shell-commands.md).

Read [operations](references/operations.md) and use Scoville Plan to establish
authorized Plan, current Work Item and next unfinished Step. Read
[dispatch](references/operations-dispatch.md) before assigning work. Agents
select relevant Skills themselves and load only needed references. Explicit
user invocations remain binding.

Once the target is known, name this chat `SC-WFL <Plan-ID>` using
`set_thread_title` without threadId. Keep the title across pauses and compaction.
Change it only when authorized work moves to another Plan; report rename errors.

## Loop

```mermaid
flowchart TD
  M{"Question, idea or change?"}
  X["Choose Explorer; investigate read-only"]
  U["Manager: answer; write authorized records"]
  S["Select ONE original Step"]
  P["Manager: save execution start/resume state"]
  E["Choose Executor; helper validates start; execute SAME Step"]
  N["Wait for complete native final; establish writer quiescence"]
  J{"Executor result"}
  R["Choose Reviewer; review SAME Step"]
  D{"Step review result"}
  A["Manager: record accepted Step"]
  K{"All Work Item Steps accepted?"}
  B{"Next Step authorized?"}
  T["Stop at authorized boundary; leave Work Item open"]
  C["Choose Reviewer; review all Steps and full Acceptance"]
  F{"Closure result"}
  O["Select ONE affected Step"]
  Z["Manager: accept Work Item; select authorized successor"]
  H["Manager: resolve exact prerequisite; stop dependent work"]
  M -->|yes| X --> U --> M
  M -->|no| S --> P --> E --> N --> J
  J -->|done| R --> D
  J -->|blocked| H
  D -->|changes_requested| P
  D -->|blocked| H
  D -->|pass| A --> K
  K -->|no| B
  B -->|yes| S
  B -->|no| T
  K -->|yes| C --> F
  F -->|changes_requested| O --> P
  F -->|blocked| H
  F -->|pass| Z
  H -->|missing Executor evidence: same Step via helper| E
  Z -->|next authorized Work Item| M
```

“Choose” means the [agent check](references/operations-dispatch.md#check-the-agent-before-every-assignment).
Wait for each role’s matching complete native final before dependent work.
Stop and failure recovery follow [operations](references/operations.md#stop-compaction-and-failure).
The diagram grants no scope; closure findings without a matching Step follow operations.

Every Step gets a review, including a Step without changed files. The helper
sends original Plan context and exactly the selected Step. The manager supplies
selection IDs and review objections as additional context; it does not compose,
shorten or rewrite the dispatch. Step review covers actual changes of the selected
Executor assignment, relevant effects and open findings. An evidence-only
follow-up continues review of the original change. Closure checks all
original Steps and full Acceptance against current implementation and evidence.

Before every assignment, run the agent check. Executor and Reviewer belong to
the current Work Item; Explorer belongs to this manager thread. The one Setup
threshold is checked between assignments, never during an ongoing write.

Before acting, check:
1. The current request, required role, authorized scope and completed prerequisites.
2. Before source execution: saved and validated start/resume state.
3. Complete unchanged inputs and permission to dispatch from the agent check.

Use the existing Plan, agent and dispatch helpers for their checks. Before
communicating, check language, required fields, actual evidence and completion
claims. Correct a mismatch or stop dependent work on an unresolved prerequisite.
Do not output a checklist transcript.

Delegate user questions, ideas, change requests and planning preparation to
Explorer with the complete request and necessary context. Explorer proposes;
manager answers and writes authorized Plan changes. Handle stop, resume and
known progress directly. Stop invalidated execution before investigating a
change. Exploration grants no implementation or review acceptance.

Retain handles, role counters, launched pairs, current assignments, results
and open findings. Reuse unchanged evidence and passing checks. Report changed
positions briefly as `Working on: <project> → <Plan-ID> → <Step or Work Item>`;
translate the label into the communication language.
Waiting for a child is working; blocked means an actual unmet prerequisite.
During a running child, keep this turn active with native waits, not a final answer.

## Stop and completion

On user stop, stop dispatch and interrupt known running children. Establish
writer quiescence, then save and validate observed Plan state. Uncertain writer
state prevents another writer. Resume only on explicit activation.

Host compaction continues this manager and its same assignments from retained
identities, Plan state and completed effects; it creates no new scope or
replacement. Use operations for confirmed failed or interrupted children.

Complete only after requested Acceptance, both review levels, Plan closure and
child/writer quiescence. Report outcome and material limits in the user's
language. Return to ordinary assistance; new requests start no automatic run.

## Runtime helpers

Use the bundled helpers for their operations. Read their invocation instructions,
not their source, unless diagnosing a failure.

| Condition | Required route |
| --- | --- |
| Python and every named helper are available | Use the bundled helper. |
| Missing Python, script, dependency or helper error | Stop the affected operation; do not substitute manual execution. |

Helpers: `scripts/build_dispatch_prompt.py`, `scripts/validate_profile.py`, `scripts/check_agent_context.py`, `scripts/resolve_model_pair.py`, `scripts/select_context.py`, `scripts/check_text_size.py`.
