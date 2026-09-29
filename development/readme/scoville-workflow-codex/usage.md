## How to use

With the suite installed in Codex, start Workflow in your saved project:

```text
Use $scoville-workflow-for-codex to execute the active Scoville Plan in this saved project.
```

You don't need a separate project installation or an `AGENTS.md` entry.

To limit the run, name a Work Item or the point where it should stop.
Otherwise the coordinator works through the active Plan.

The chat you start it in coordinates the run and creates workers for the
implementation. You can also just name Workflow in your request:

```text
Run only PLAN-0001 with Scoville Workflow.
```

"Start Scoville Workflow" also starts it. "Execute the Plan" alone
does not. Mentions, questions and quoted examples don't start a run. `$scw`
works once the Skill is loaded.

Task titles identify the work and role:

```text
SC-MGR-2: My project · PLAN-0011
SC-WRK-3: My project · PLAN-0011/W-010/steps-1-3
SC-REV-3: My project · PLAN-0011/W-010/steps-1-3
```

Manager numbers count the coordinators within one run. Every new worker gets
the next number, including workers for rollovers and corrections. A reviewer
takes the number of the worker whose final result it reviews and keeps it
after a rollover. For a grouped review, the title shows the full range of
Steps reviewed.

Titles show the Plan, the Work Item and the assigned range: `step-2` or
`steps-1-3`. A whole Work Item shows its full Step range, or no suffix if it
has no Steps. Only the role prefix is uppercase. Project names and inserted
content keep their own casing.

### Configuration

To change the defaults, use Scoville Setup to view or save the project
settings in `.scoville/config.json`. Under `workflow`, `execute.CLASS` and
`review.CLASS` choose model and reasoning pairs, and `context` sets the
rollover thresholds. Anything missing uses the bundled defaults, and starting
a run doesn't create a configuration file.

### Pin chats

Workflow pins the manager, workers, reviewers and rollover successors by
default. To turn this off for the project, use Scoville Setup before a run:

```text
Use Scoville Setup to disable pinning for Workflow in this project.
```

Setup saves `workflow.pin_threads: false` in `.scoville/config.json`. Ask has
its own `ask.pin_threads` switch. Both are `true` by default and can be turned
back on through Setup. The switches only affect new pins. Existing pins stay.
Claude CLI sessions don't appear in the Codex sidebar.

By default, the coordinator hands over at 40% context usage or more, and
workers and reviewers above 60%. The Plan records progress, direct messages
carry the handoffs, and at most one worker writes to the shared checkout at a
time.

The [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
explain how tasks are classified and how explicit model choices work.
