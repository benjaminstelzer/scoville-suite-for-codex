## How to use

With the suite installed in Codex, start Workflow in your saved project:

```text
Use $scoville-workflow-for-codex to execute the active Scoville Plan in this saved project.
```

No additional project installation or `AGENTS.md` entry is needed.

Name a Work Item or end boundary to limit the run. Without one, the coordinator
continues through the active Plan.

The calling chat coordinates the run. Use the full Skill name to start it
reliably. `$scw` also works once the Skill is loaded. Ordinary requests such as
“implement the plan” do not activate Workflow.

Task titles identify the work and role:

```text
SC · MNGR · 2 · PLAN-0011
SC · WORK · 3 · W-010/STEPS-1-3
SC · REVW · 3 · W-010/STEPS-1-3
```

Manager numbers count coordinators within a run. Every new worker gets the next
worker number, including rollover and correction assignments. Reviewers use the
number of the worker whose final result triggers their review. A reviewer rollover
keeps that number. A grouped review's title shows the full reviewed Step range.

Titles show the Plan or Work Item and assigned range: `STEP-2` or `STEPS-1-3`.
A whole Work Item shows its full Step range, or no suffix when it has no Steps.
Uppercase applies to titles only.

### Configuration

To change the defaults, use Scoville Setup to inspect or save project settings in
`.scoville/config.json`. Under `workflow`, `execute.CLASS` and `review.CLASS`
select model/reasoning pairs, and `context` sets rollover thresholds. Missing
values use the bundled defaults. Starting a run creates no configuration file.

Default rollover triggers are at or above 40% context usage for the coordinator
and strictly above 60% for workers and reviewers. The Plan records progress;
direct messages carry handoffs. At most one worker writes in the shared checkout.

See the [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
for task classification and explicit model choices.
