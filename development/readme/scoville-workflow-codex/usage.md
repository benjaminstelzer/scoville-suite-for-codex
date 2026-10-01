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

