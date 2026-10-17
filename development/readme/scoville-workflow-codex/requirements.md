## What it enforces

- **Responsibility.** The visible chat maintains the Plan; executors implement
  and reviewers assess. At most one executor writes in the shared checkout.
- **Bounded work.** Exactly one original Step is executed and reviewed before
  the next. Every Work Item also receives a full Step/Acceptance closure review.
- **Git.** Git and a clean worktree are required before activation Plan writes.
  The manager commits each passed changed Step with Plan progress before advancing.
- **Reuse.** Executor and Reviewer belong to the current Work Item; Explorer to
  the manager thread. Each subagent checks its own context on every assignment
  and before substantial work chains, then returns safely when replacement is due.
- **Model choices.** Configured executor, reviewer and explorer models and effort are respected.
  Unsupported settings stop dependent work rather than being substituted.
- **Continuity.** The same chat continues after compaction from concise Plan
  state, known child identities, completed effects and open decisions.
- **Visible decisions.** The manager asks necessary questions directly. Stops
  preserve unfinished work; completion requires accepted scope and quiescent writers.

Workflow activation includes accepted-Step commits, subject to explicit user
and project restrictions. It never cleans or commits preexisting work to start.
The [operations reference](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations.md)
contains execution, review and stop behavior.
