# Scoville Workflow for Codex

Scoville Workflow makes sense when there is a substantial Plan to execute and
software you intend to keep maintaining. Coordination, independent reviews and
handoffs take time and tokens. For a small fix or a one-prompt experiment, that
effort rarely pays off. For longer AI-assisted development, it gives the work a
structure that holds across many assignments and conversations.

Start from a Plan with settled requirements, dependencies and acceptance
criteria. Scoville Plan and independent Ask reviews establish that direction
before Workflow carries it through implementation.

Workers implement a defined piece of work, then fresh reviewers inspect the
result. Reviewing at the relevant dependency boundaries helps catch mistakes
before later Plan points build on faulty code. That makes longer sessions easier
to manage. The manager records accepted progress in the Plan, so what is
done, what remains and what was actually checked stay visible.

Automatic context compaction can arrive right in the middle of ongoing work,
without a completed work unit or a prepared handoff. Rollover moves that
transition to a controlled work boundary. Results are checked and completed
Plan points are recorded before the manager changes. The Plan is the
backbone: the next agent knows where to continue, without reconstructing progress
from the whole conversation. Crossing a context threshold schedules rollover.
Workers finish their complete Step or Step group, including required corrections
and checks, then return the normal result. Later assignments use fresh agents.

The complete assignment can still reach automatic compaction before that boundary.
Smaller assignments also keep unrelated history out of worker and reviewer
contexts. Progress stays in the Plan, and each agent loads the relevant
instructions. Rules, Decisions and open Steps have a stable place across
sessions.

Install it through the complete Codex Suite. It requires Codex desktop's native
agent controls.

## How it works

- The visible chat is the runner. It starts a manager after explicit Workflow
  activation or when the current manager requests a successor. One exact agent
  ID and READY from that agent allow the runner to send START. Missing or
  ambiguous confirmation stops the run. An unknown spawn state never causes
  a replacement spawn.
- The manager selects consecutive Plan work, routes model and effort, and starts
  nested workers and read-only reviewers. At most one worker writes to the shared
  checkout. The manager owns Plan updates and authorized commits.
- The manager follows project review rules or the bundled review points below.
  Reviewers reuse assessments of unchanged parts at final review. A new worker
  corrects findings.
- Crossing a measured context threshold schedules rollover. The manager finishes
  the selected Step or Step group, including due review, corrections, checks,
  Plan updates and authorized commits. It requests a successor only after all
  children and writes are quiescent.
- The runner gives the successor only the predecessor's ID as work context.
  After START, the new manager requests the handoff directly, checks the Plan,
  files and child state, and confirms takeover before writing or dispatching a
  child. Substantive results and handoffs stay with managers and their children.
  The runner receives short control states, errors and necessary user questions.
- Children finish their full assignment and return the normal completed or
  review result after crossing the threshold. Later assignments use fresh
  children. Explicitly authorized recovery can transfer unfinished work, checked
  effects, constraints and evidence limits. A recovery child confirms receipt
  to its manager and waits for release. It does not message the completed child.
- A retiring manager waits for the successor's receipt before ending its turn.
  The runner confirms that completion before the successor starts work. This
  avoids sending routine receipt messages to a completed predecessor.
- After a definite capacity refusal, the runner may wake its known retired
  managers once to consume queued messages without writing. The failed spawn
  then gets one retry. Uncertain starts and persistent failures remain blocked.
  Native agents need no new chats or archival.
- The runner shows the current project, Plan point and overall scope when the
  point changes. Managers preserve user questions and problems in one run file,
  adding their resolutions. On accepted completion, the runner outputs it.

```mermaid
flowchart TD
    U["Explicit Workflow activation"] --> R["Runner creates report, shows path<br/>and spawns manager"]
    R --> G["Exact agent sends READY<br/>Runner sends START"]
    G --> M["Manager selects Plan work<br/>and sends display fields"]
    M --> W["One writing worker"]
    W --> V["Required read-only review"]
    V -->|Findings| W
    V -->|Accepted| P["Manager updates Plan<br/>Commits when authorized"]
    P --> B{"Work remains and context boundary reached?"}
    B -->|No boundary| M
    B -->|Requested scope accepted| F["Manager finalizes report"]
    F --> D["COMPLETED and native final<br/>Runner reads report with helper<br/>Then announces completion and outputs it"]
    B -->|Quiescent boundary| S["SUCCESSOR_REQUEST to runner"]
    S --> N["Runner gates new manager with READY / START"]
    N --> H["New manager requests handoff directly<br/>Verifies Plan, files and child state"]
    H --> A["Successor confirms receipt<br/>Predecessor ends without writing"]
    A --> T["Runner confirms completion<br/>and releases successor"]
    T --> M
```

## What it enforces

- **Explicit activation and checked startup.** The runner starts on a named
  Workflow request or a successor request from its current manager. The exact
  spawned manager must send READY and receive START before doing project work.
- **Separate responsibilities.** Managers own Plan transitions and authorized
  commits. Workers implement. Reviewers stay read-only. At most one worker
  writes in the shared checkout.
- **Bounded assignments.** A new child receives its Work Item and assigned
  Step range. A continuation receives remaining work, applicable criteria,
  constraints, checked effects and evidence limits.
- **Configured models.** Risk selects model and effort. Missing support blocks
  dispatch instead of silently substituting a pair.
- **Independent review.** Project review rules come first. Otherwise, review
  follows fixes to previously checked product code and precedes dependent work
  or extensive tests. Final review reuses checked, unchanged parts. Repeated
  failure after two corrections requires reassessing the cause.
- **Measured handoffs.** By default, managers turn over at or above 40% context
  after completing the selected Step or Step group, including required checks,
  due review and corrections. Workers, reviewers and correction workers schedule
  rollover strictly above 60%, finish their complete assignment and return the
  normal result. Later assignments use fresh agents. Thresholds are configurable.
  A handoff requires no active writer. Missing or stale telemetry is never counted
  as a switch.
- **Direct takeover.** The successor manager obtains the handoff from its
  predecessor and verifies Plan, files and child state before writing. Results
  remain retained, and predecessors stay write-inactive after handoff.
- **Retained decisions and stops.** An unanswered question blocks dependent
  work. A stop interrupts children and requires confirmed quiescence before
  STOPPED is reported. Resumption preserves pending findings and decisions.
- **Accepted commits and scope.** Authorized commits include accepted changes
  and Plan updates, with required hooks and backups. Workflow respects the
  requested scope and only reports completion when its acceptance is met.
- **Visible work.** `Working on:` identifies the project, Plan and point.
  `Scope:` gives the actual overall assignment as free text. Repeated events,
  reviews, repairs and manager switches at the same point add no progress message.
- **Targeted run report.** Every run gets its own Markdown file under `.scoville`,
  with the full path shown before startup. User questions, requested pauses and
  problems needing user review stay in it with their clarifications. Normal
  progress and test results stay out. A clean completed run has the sentence
  `No issues occurred during this run.`. Completion includes the report output.

[Native Codex operations](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations.md)
covers delivery, permissions and recovery.

## What it costs

- Worker and reviewer agents, handoffs and Plan updates cost tokens and time.
- Caching can reduce charges for repeated input. Large contexts still take time
  to process, and a controlled handoff adds another exchange.
- Coordination overhead depends on assignment size, reviews and handoffs.
  The retained reports don't establish a typical percentage for the current
  Workflow. Token counts include cached input, so they don't show the price
  of a run on their own.

## How it was developed

- Real project histories shaped assignment size, reviews, communication and
  context handoffs.
- Tests with GPT-6 SOL Medium covered grouped work, review, repair and
  rollover. Targeted Luna tests found places where the instructions weren't
  followed.
- Simulated delivery checks don't show how reliable it is live. Compaction
  right after a handoff and delivery failures at host level haven't been fully
  verified.

- Development links: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-workflow-for-codex) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-workflow-for-codex/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/members/scoville-workflow-for-codex/development/README.md)

## Compatibility

Needs Codex with native agent spawning, messaging, waiting, interruption and
agent-state inspection, Python 3.11+ and the complete Codex Suite. Agents must
share the existing checkout and support the configured model and effort pairs.
It also needs a frontier model from the Fable, Astra, SOL or Opus families,
version 5.0 or newer. Bounded Luna Medium tests also cover the current manager
handoff. They do not establish complete Luna coverage of the agent lifecycle.

The run stops when the host cannot confirm agent identity, deliver a required
message or establish who may write. It does not substitute chats, another model
or an assumed close operation. Queued messages can keep completed agents resident.
Bounded cleanup can help, but available agent capacity can still limit a run.

Context rollover uses fresh Codex measurements tied to the actual agent.
Without usable telemetry, bounded work continues without claiming a measured
switch. Automated tests cover helper validation and controlled telemetry.
Live multi-unit execution, stop handling, child completion after a measured
crossing and manager handoffs need separate evidence.

Install and enable every Skill in the suite. Each applies to its own task scope.
Start Workflow by asking for it explicitly.

## Install

Install and enable the complete
[Scoville Suite for Codex](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/packages).
Workflow only comes with the suite, and every Skill has to come from this
repository's own `packages/<name>/<name>/` directory. Don't swap in packages
from the individual repositories, and don't continue if members are missing.
The suite needs Codex and Python 3.11 or newer. Use the suite's prompt for a
new installation, or its upgrade prompt if you already have one installed.



## How to use

With the suite installed in Codex, start Workflow in your saved project:

```text
Use $scoville-workflow-for-codex to execute the active Scoville Plan in this saved project.
```

You don't need a separate project installation or an `AGENTS.md` entry.

To limit the run, name a Work Item or the point where it should stop.
Otherwise the manager works through the active Plan.

The chat you start it in runs the startup handshake and monitors short control
states. A manager agent coordinates workers and reviewers. You can also just
name Workflow in your request:

```text
Run only PLAN-0001 with Scoville Workflow.
```

"Start Scoville Workflow" also starts it. "Execute the Plan" alone
does not. Mentions, questions and quoted examples don't start a run. `$scw`
works once the Skill is loaded.

Assignment labels identify the work and role:

```text
SC-WRK-3: My project · PLAN-0011/W-010/steps-1-3
SC-REV-3: My project · PLAN-0011/W-010/steps-1-3
```

Managers have numbered agent names such as `scoville_manager_2`. Each new
worker gets the next number, including workers for recovery and corrections. A reviewer
takes the number of the worker whose final result it reviews and keeps it
after a recovery transfer. For a grouped review, the label shows the full range of
Steps reviewed.

Labels show the Plan, the Work Item and the assigned range: `step-2` or
`steps-1-3`. A whole Work Item shows its full Step range, or no suffix if it
has no Steps. Only the role prefix is uppercase. Project names and inserted
content keep their own casing.

### Run feedback

Before the first manager starts, the runner shows the full path of the run's
Markdown file in your project's `.scoville` directory. You can open it manually.

At the first point and each project, Plan or point change, you see:

```text
Working on: My project → PLAN-0024 → W-003/step-4
Scope: Finishing PLAN-0024 from W-003 to W-006.
```

Scope repeats the overall goal you assigned. Reviews, corrections and a manager
change at the same point don't repeat the display.

The report keeps questions, points paused at your request and problems needing
your inspection. Later clarifications stay with the original issue. A stop and
resume use the same file. Routine status messages and normal test results aren't
recorded.

At accepted completion, the runner says the assignment is complete and outputs
the report. If the whole run had no such issues, it contains
`No issues occurred during this run.`. Stops, blockers and unreadable reports
don't produce a completion message.

### Configuration

To change the defaults, use Scoville Setup to view or save the project
settings in `.scoville/config.json`. Under `workflow`, `execute.CLASS` and
`review.CLASS` choose model and reasoning pairs, and `context` sets the
rollover thresholds. Anything missing uses the bundled defaults, and starting
a run doesn't create a configuration file.

By default, 40% context usage or more schedules manager rollover, and
above 60% schedules it for workers, reviewers and correction workers. Each
finishes its complete current assignment, including required corrections and
checks, before a handoff with no active writer. Children return the normal result
and later assignments use fresh agents. The Plan records progress, direct messages
carry the handoffs, and at most one worker writes to the shared checkout at a
time.

The [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
explain how tasks are classified and how explicit model choices work.

### Agent lifecycle

Workflow uses nested agents. They do not create separate sidebar chats, and
`workflow.pin_threads` does not pin them. The setting remains readable for
compatibility. Agents keep their exact IDs for messages and handoffs. If the
host cannot start the next agent, the run reports the limitation and stops.

## Sources

- [Agent Skills specification](https://agentskills.io/specification) for the
  portable package and progressive disclosure model.
- [OpenAI coding-agent best practices](https://developers.openai.com/codex/learn/best-practices)
  for explicit outcomes, constraints, planning, and completion evidence.

## License

MIT. See [LICENSE](LICENSE).
