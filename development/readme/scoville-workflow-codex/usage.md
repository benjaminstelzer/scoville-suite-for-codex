## How to use

Activate the workflow explicitly:

```text
Use $scoville-workflow-for-codex to execute the active Scoville Plan in this saved project.
```

Name a Work Item or end boundary to limit the run. Without one, the coordinator
continues through the active Plan.

The calling chat coordinates the run. Use the full Skill name to start it
reliably; `$scw` also works once the Skill is loaded. Ordinary requests such as
“implement the plan” do not activate Workflow.

Task titles identify the work and role:

```text
S-MNGR-#2-PLAN-0011
S-WORK-#3-W-010/STEPS-1-3
S-REVW-#2-W-010/STEPS-1-3
S-FIXR-#1-W-010/STEPS-1-3
```

Manager numbers count coordinators within a run. Worker, reviewer and fixer
numbers each start at 1 for the assigned Work Item and exact Step range.
A successor for that same role and unit gets the next number; continuing the
same chat keeps its number. Rollover preserves the unit and repair attempt.

Titles show the Plan or Work Item and assigned range: `STEP-2` or `STEPS-1-3`.
A whole Work Item shows its full Step range, or no suffix when it has no Steps.
Uppercase applies to titles only.

### Configuration

Use Scoville Setup to inspect or change project settings in
`.scoville/config.json`. Under `workflow`, `execute.CLASS` and `review.CLASS`
select model/reasoning pairs, and `context` sets rollover thresholds. Missing
values use the bundled defaults. Starting a run creates no configuration file.

Default rollover thresholds are 25% for the coordinator and strictly above 75%
for child roles. Progress is saved in `.scoville/workflow.md`. Change settings
between runs and avoid parallel edits to the shared project checkout.

See the [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
for task classification, Step overrides and repair escalation.
