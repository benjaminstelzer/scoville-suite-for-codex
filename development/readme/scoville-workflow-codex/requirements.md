## What it enforces

- **Explicit activation.** Workflow only starts when you ask for it by name.
- **Separate responsibilities.** The coordinator handles Plan updates,
  assignments and any authorized commits. Workers implement. Reviewers look
  but don't edit.
- **One writing worker.** All tasks share the existing checkout. The Plan
  records progress, and messages carry the next action.
- **Bounded context.** A new worker gets the Work Item and its assigned Step
  range. A continuation only gets what's left: remaining work, applicable
  criteria and constraints, completed effects and evidence. It doesn't need to
  reopen the Plan or earlier chats.
- **Configured models.** Risk decides model and effort. If a required pair
  isn't available, Workflow says so instead of substituting another.
- **Independent review.** The project's own review cadence comes first.
  Otherwise, unreviewed product-code changes get an early review after a fix
  to previously completed code, or before dependent work or extensive testing.
  Other required reviews happen when a Work Item is complete and reuse earlier
  assessments of unchanged parts. If the same failure survives two
  corrections, the coordinator looks at its cause again before another
  attempt.
- **Context handoffs.** By default, the coordinator hands over at or above 40%
  context, after a checked group, an accepted Work Item or a worker handoff.
  Workers and reviewers hand over above 60%, at natural stopping points. Both
  thresholds are configurable. If there's no measurement, Workflow doesn't
  guess one.
- **Retained results.** Results are saved before a task is archived. A
  predecessor only retires after its successor has confirmed the takeover.
  Archive errors are reported without confirmation loops. Decision requests
  and the final coordinator stay open.
- **Accepted commits.** If committing is allowed, the commit contains the
  accepted changes and Plan updates, and required hooks and backups run.
- **Defined scope.** Workflow follows the active Plan, or a narrower boundary
  you set, and keeps its stops and open decisions.

[Native Codex operations](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations.md)
covers delivery, permissions and recovery.
