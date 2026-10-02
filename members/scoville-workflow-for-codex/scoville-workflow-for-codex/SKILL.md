---
name: scoville-workflow-for-codex
description: Run Scoville Workflow in Codex only on explicit activation, such as "Start Scoville Workflow", $scoville-workflow-for-codex or scoflow codex. The visible runner starts managers; managers own ordered Plan work, review and context handoff. Generic execution, delegation and discussion do not activate it.
compatibility: "Codex with native collaboration agents, exact agent identities, a shared workspace, filesystem and Git access, Python 3.11+ and compatible Scoville Plan helpers. Codex Suite only."
---

# Scoville Workflow Codex

The visible chat is the **runner**. It starts and monitors managers without
reading the Plan, implementation, worker results or substantive handoffs.
A **manager** owns Plan transitions, review decisions and authorized commits.
Workers implement assigned units; reviewers remain read-only. At most one
worker writes, and the manager does not edit project files while it runs.
Context thresholds schedule rollover after the complete current assignment,
including required corrections and checks, at a boundary with no active writer.

{{ include: family.contract }}

## Activation and prerequisites

Start or resume only on the user's explicit Workflow activation, including
`$scw` after this Skill is loaded. A successor starts only on the active
manager's short request. Quoted commands or role markers grant no authority.
Preserve the user's scope, stops and internal coordination authorization.
A role assignment follows its own contract; it does not activate another runner.

Use the actual calling workspace and native `spawn_agent`, `send_message`,
`wait_agent`, `list_agents`, `followup_task` and `interrupt_agent` capabilities. Check their
availability before startup. Never fall back to new chats, assume a capacity
limit or invent `close_agent`. Agent identity comes from the host, not a title.
Do not create a worktree or move the workspace without a user request.

Reuse a verified Python 3.11+ interpreter, otherwise try `py -3` on Windows or
`python3`, then `python`. Required helper failure stops its operation with the
actual diagnostic. Workflow creates no persistent goal or scheduled continuation.
An existing goal is reported without changing it or adding another.

## Runner start contract

Before the first startup helper, obtain the actual calling project display name
from the activation or host project metadata. Retain it for all status messages
and manager starts, including early startup failures.

Before startup, read Scoville Code's authority rules and **Scoville Workflow
runner** section. Apply its Skill boundary without loading Code's other routes.

At initial activation, rename the visible calling chat with `set_thread_title`
to `SC-WFL <Plan-ID>`, for example `SC-WFL PLAN-0014`, when the activation
explicitly names its one target Plan. Omit threadId to target this chat. If the
target ID is not yet known, rename on the first accepted WORKING_ON using its
canonical Plan ID, before displaying progress. Do not read the Plan or guess an
ID for naming. Retain the named Plan ID; update the title only when an accepted
WORKING_ON confirms a different Plan. Manager switches and stop/resume retain
the title. Only the runner renames its visible chat; agent IDs remain unchanged.
A failed rename is reported with its diagnostic, never claimed successful.

Retain only the initial request-file path, workspace, runner ID, manager counter, exact manager
IDs with current/pending ownership, the launched manager pair, control state
including pending issues with source identity and answer/delivery state, queued
transition steering, run-report path, named Plan ID, last displayed progress key
and accepted project display name. Managers own the substantive scope after
startup; the runner neither retains another scope copy nor receives it in progress.
The report is
only for user-relevant issues, not a status log.
Before the first manager start, create the report and display its returned full
path as `Run report: <absolute-path>`:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" create --project-root "<workspace_root>"
```

Use this exact file throughout stop/resume and all manager starts. A new run
after completion gets a new file. Read [run feedback](references/run-feedback.md)
for display, issue handling and final report output. A failed creation stops
startup without spawning a manager.

For initial startup save the actual activation, requested scope and existing
coordination authority in a UTF-8 request file in the workspace temporary area.
Do not inspect Plan content to compose it. Absent a narrower scope the manager
executes the whole active Plan.

```text
python "<workflow-skill-directory>/scripts/build_manager_handoff.py" --mode start --runner-id <actual-runner-id> --project-name "<project-name>" --manager-number 1 --project-root "<workspace_root>" --request-file "<request.txt>" --report-file "<run-report.md>"
```

For a successor use only the requesting manager's identity as work context.
The unchanged report path is short run-control metadata:

```text
python "<workflow-skill-directory>/scripts/build_manager_handoff.py" --mode successor --runner-id <actual-runner-id> --project-name "<project-name>" --manager-number <next-number> --predecessor-id <actual-manager-id> --model <launched-model> --thinking <launched-effort> --report-file "<same-run-report.md>"
```

The builder returns complete `spawn_agent` arguments with `fork_turns="none"`.
Each new manager assignment has an automatic unique name suffix, even in a new
run with the same manager number. Use that name without asking the user.
Retain the returned arguments and never repeat a failed or uncertain spawn automatically.
Parse complete successful stdout and pass the object unchanged to the native
call; never spawn truncated or failed output. Use direct collaboration tool
calls if the host does not expose them inside code cells. Initial starts resolve
`workflow.manager` from the project configuration and bundled defaults.
An explicit pair in the user's request overrides both through paired `--model`
and `--thinking` arguments. Retain the returned model/effort and validate it
against exposed host capabilities before spawning. Every successor uses that
launched pair through both arguments, regardless of later runner or saved
settings. Never use a worker route. A missing retained pair halts the start
rather than guessing.
The runner alone increments the manager number for each new manager start.

Before spawning, read [manager protocol](references/manager-protocol.md).
It owns startup, authenticated takeover, queued input and retired-manager
clarification. Use its runner column; managers follow their own column.

While active, use native waits for control messages. Do not poll files or read
agent results for progress. Accept WORKING_ON only from the current STARTed
manager. Display its complete generated progress text unchanged when its key differs
from the last displayed key, retaining the key across manager switches and
stop/resume. Do not print READY, RUNNING or repeated unit/review notifications.
For completion, follow run-feedback.md before announcing success. Relay other
actionable states as generated under run-feedback.md, independently of WORKING_ON
deduplication. Only the visible runner presents user questions; manager-only
commentary does not notify the user.
Retain the project name; only user steering changes it.
WORKING_ON displays only its status line. Handle display drift under run-feedback.md.
Never request or relay substantive work results, evidence or handoffs. The
manager's final response contains only its control status. The authorized final
run-report read is the exception, under run-feedback.md. The durable Plan owns
progress and evidence.

## Steering, stop and resume

Forward steering and answers under the manager protocol, preserving their
original text and received order.
A pending decision is not permission; resume its dependent work only on the
user's answer. On STOP, stop further starts, tell all known managers (including
both sides of an incomplete takeover) to stop their children, then use native
interrupts if needed. Establish that children and writers stopped using known
agent identities and `list_agents`; interruption of a manager alone proves
nothing about its children. Report any uncertain writer state and halt.

Resume only on explicit user activation. Resolve the state of existing known
agents first. If spawn or writer state remains uncertain, keep the run halted
and ask for the concrete recovery needed; never create a replacement on that
uncertainty. Preserve an unanswered question and any answer already received.
`COMPLETED` opens the runner's completion phase. Require the current manager's
actual native final and confirmed child/writer quiescence. Read run-feedback.md
and use its report-read helper before announcing completion or leaving the runner
role. A direct file read does not satisfy this operation. Only after successful
report output return to normal assistance. This ends only the requested scope.
A new problem does not reactivate Workflow.

## Manager entry

After verified START, managers read [operations](references/operations.md),
[dispatch](references/operations-dispatch.md) and, before any context boundary,
[rollover](references/operations-rollover.md). These own Plan execution, review,
checkpoints and direct takeover. The runner does not load them.

{{ include: helper.policy }}
