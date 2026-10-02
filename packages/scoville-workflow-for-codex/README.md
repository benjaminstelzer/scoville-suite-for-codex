# Scoville Workflow for Codex

Scoville Workflow takes a prepared Plan through implementation, independent
review and corrections. A manager assigns bounded work, workers implement it
and reviewers check the result. Progress stays in the Plan across sessions.

Use Plan and Ask to settle requirements and acceptance first, then assign the
whole Plan or a defined part. Workflow suits larger tasks and software you
intend to maintain. For a tiny fix, the coordination is usually more work
than the fix. Install it through the complete Codex Suite in Codex desktop.

Scoville measures chili heat. Workflow keeps the goal sharp as agents take
turns. Adding more cooks is only useful if dinner still arrives.

## How it works

- Start from a prepared Plan and choose the whole Plan or a bounded part.
- Let the manager arrange implementation, checks, review and corrections.
- Follow progress in the chat and Plan. Questions and problems stay in the run
  report, whose location is shown at startup.
- Continue across context handoffs and finish when the requested work meets
  its acceptance criteria.

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 20, 'rankSpacing': 18}}}%%
flowchart TD
    P["Repository Plan"] --> C["Manager selects a bounded piece of work"]
    C --> W["Worker implements and checks the result"]
    W --> B("Review boundary reached?")
    B -->|No| A
    B -->|Yes| G("Review required?")
    G -->|Yes| R["Fresh reviewer checks the result"]
    G -->|No| A["Manager records checked progress<br/>and updates the Plan"]
    R -->|Pass| A
    R -->|Findings| F["Manager corrects Plan findings<br/>New worker corrects project findings"]
    F --> Q("Follow-up review required?")
    Q -->|Yes| R
    Q -->|No| A
    A --> E["Accept when required checks and reviews pass<br/>Commit when authorized"]
    E --> N("Requested work remains?")
    N -->|No| D["Announce completion<br/>Show the run report"]
    N -->|Yes| T("Context boundary reached?")
    T -->|No| C
    T -->|Yes| H["Hand over at the completed work boundary<br/>Next manager continues from the Plan and handoff"]
    H --> C
```

## What it enforces

- **Clear responsibility.** Managers maintain the Plan, workers implement and
  reviewers assess. At most one worker writes in the shared checkout.
- **Bounded work and review.** Assignments carry their scope and acceptance
  criteria. Required reviews and corrections precede accepted completion.
- **Your model choices.** Configured models and reasoning levels are respected.
  Unsupported settings stop the affected operation rather than being replaced.
- **Continuity.** Context handoffs preserve checked progress, open findings and
  decisions. A successor verifies the current state before writing.
- **Visible control.** You see current work, necessary questions and blockers.
  Pauses preserve unfinished work. Completion includes the run report.

Workflow starts only when explicitly requested and commits only when authorized.
The [operations reference](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations.md)
contains the coordination and recovery details.

## What it costs

- Workers, reviews and handoffs add tokens and time. That coordination is useful for substantial, dependent work. There is no established typical overhead or guaranteed saving.

## How it was developed

Real project runs exposed unnecessary coordination and fragile context
handoffs. Native agents and bounded assignments simplified the route. Host
delivery failures and compaction immediately after handoff remain incompletely
verified.

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
Available agent capacity can still limit a run.

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

You can ask questions or pause during the run. The chat shows the current
project, Plan point and started Step. The run report under `.scoville` keeps
questions, requested pauses and problems with their later resolutions.
Completion includes that report. A stop or blocker is not reported as finished.

"Start Scoville Workflow" also activates it. "Execute the Plan" alone does not.

### Configuration

To change the defaults, use Scoville Setup to view or save the project
settings in `.scoville/config.json`. Under `workflow`, `manager` sets the
manager's model and reasoning, `execute.CLASS` and `review.CLASS` set the worker
and reviewer pairs, and `context` sets the
rollover thresholds. Anything missing uses the bundled defaults, and starting
a run doesn't create a configuration file.

The manager defaults to `gpt-6.1-sol` with `medium` reasoning, independently of
the visible chat's model. An explicit manager pair for one run overrides saved
settings. Successors keep the pair that started the run.

By default, managers schedule a context handoff at 40% usage and workers or
reviewers above 60%. They finish the current assignment and required checks
before handing over. Setup can change these thresholds.

The [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
explain how tasks are classified and how explicit model choices work.

## Sources

- [Agent Skills specification](https://agentskills.io/specification) for the
  portable package and progressive disclosure model.
- [OpenAI coding-agent best practices](https://developers.openai.com/codex/learn/best-practices)
  for explicit outcomes, constraints, planning, and completion evidence.

## License

MIT. See [LICENSE](LICENSE).
