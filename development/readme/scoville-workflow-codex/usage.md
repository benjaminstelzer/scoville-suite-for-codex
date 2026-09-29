## How to use

With the suite installed in Codex, start Workflow in your saved project:

```text
Use $scoville-workflow-for-codex to execute the active Scoville Plan in this saved project.
```

No additional project installation or `AGENTS.md` entry is needed.

Name a Work Item or end boundary to limit the run. Without one, the coordinator
continues through the active Plan.

The calling chat coordinates the run and creates workers for implementation.
You can also explicitly name Workflow in your request:

```text
Führe ausschließlich PLAN-0001 mit dem Scoville Workflow aus.
```

“Starte den Scoville-Workflow” also starts it. “Führe den Plan aus” alone does
not. Mentions, questions and quoted examples do not start a run. `$scw` works
once the Skill is loaded.

Task titles identify the work and role:

```text
SC-MGR-2: My project · PLAN-0011
SC-WRK-3: My project · PLAN-0011/W-010/steps-1-3
SC-REV-3: My project · PLAN-0011/W-010/steps-1-3
```

Manager numbers count coordinators within a run. Every new worker gets the next
worker number, including rollover and correction assignments. Reviewers use the
number of the worker whose final result triggers their review. A reviewer rollover
keeps that number. A grouped review's title shows the full reviewed Step range.

Titles show the Plan, Work Item and assigned range: `step-2` or `steps-1-3`.
A whole Work Item shows its full Step range, or no suffix when it has no Steps.
Only the role prefix is uppercase; project names and inserted content keep their casing.

### Configuration

To change the defaults, use Scoville Setup to inspect or save project settings in
`.scoville/config.json`. Under `workflow`, `execute.CLASS` and `review.CLASS`
select model/reasoning pairs, and `context` sets rollover thresholds. Missing
values use the bundled defaults. Starting a run creates no configuration file.

### Pin chats

Workflow pins the manager, workers, reviewers and rollover successors by default.
Use Scoville Setup before a run to turn this off for the project:

```text
Use Scoville Setup to disable pinning for Workflow in this project.
```

Setup saves `workflow.pin_threads: false` in `.scoville/config.json`. Ask has
its own `ask.pin_threads` switch. Both default to `true` and can be enabled
again through Setup. These settings control new pin operations; existing pins
are not removed. Claude CLI sessions have no Codex sidebar entry.

Default rollover triggers are at or above 40% context usage for the coordinator
and strictly above 60% for workers and reviewers. The Plan records progress;
direct messages carry handoffs. At most one worker writes in the shared checkout.

See the [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
for task classification and explicit model choices.
