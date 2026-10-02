## How to use

With the suite installed in Codex, start Workflow in your saved project:

```text
Use $scoville-workflow-for-codex to execute the active Scoville Plan in this saved project.
```

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
