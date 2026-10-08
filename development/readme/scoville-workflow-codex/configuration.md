## Configuration

To change the defaults, use Scoville Setup to view or save the project
settings in `.scoville/config.json`. Under `workflow`:

| Key | Controls |
| --- | --- |
| `manager` | Manager model and reasoning. |
| `execute.CLASS` | Worker pair for that route. |
| `review.CLASS` | Reviewer pair for that route. |
| `context` | Rollover thresholds. |

Missing values use bundled defaults. Starting a run creates no configuration file.

The manager defaults to `gpt-6.1-sol` with `medium` reasoning, independently of
the visible chat's model. An explicit manager pair for one run overrides saved
settings. Successors keep the pair that started the run.

By default, managers schedule a context handoff at 40% usage and workers or
reviewers above 60%. They finish the current assignment and required checks
before handing over. Setup can change these thresholds.

The [dispatch rules](scoville-workflow-for-codex/references/operations-dispatch.md)
explain how tasks are classified and how explicit model choices work.
