## Configuration

Project settings live in `.scoville/config.json`. For Ask, Setup can save adviser
choices, model and effort, Claude spending limits, timeouts, session storage,
custom instructions and web access. For Workflow, it can save the manager,
worker and reviewer models and reasoning, plus context handoff thresholds.
Agents finish their assigned unit before a context-driven handoff.

The manager defaults to `gpt-6.1-sol` with `medium` reasoning. Save another pair
under `workflow.manager.model` and `workflow.manager.reasoning`, through Setup
or directly in `.scoville/config.json`. An explicit pair for one run takes
precedence. Manager successors keep the pair that started the run.

Setup shows the values that apply to the project, defaults included. A
one-off choice stays in the request or Plan Step unless you ask Setup to save
it.
