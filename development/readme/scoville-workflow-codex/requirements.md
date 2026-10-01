## What it enforces

- **Explicit activation and checked startup.** The runner starts on a named
  Workflow request or a successor request from its current manager. The exact
  spawned manager must send READY and receive START before doing project work.
- **Separate responsibilities.** Managers own Plan transitions and authorized
  commits. Workers implement. Reviewers stay read-only. At most one worker
  writes in the shared checkout.
- **Bounded assignments.** A new child receives its Work Item and assigned
  Step range. A continuation receives remaining work, applicable criteria,
  constraints, checked effects and evidence limits.
- **Configured models.** Risk selects model and effort. Missing support blocks
  dispatch instead of silently substituting a pair.
- **Independent review.** Project review rules come first. Otherwise, review
  follows fixes to previously checked product code and precedes dependent work
  or extensive tests. Final review reuses checked, unchanged parts. Repeated
  failure after two corrections requires reassessing the cause.
- **Measured handoffs.** By default, managers turn over at or above 40% context
  after completing the selected Step or Step group, including required checks,
  due review and corrections. Workers, reviewers and correction workers schedule
  rollover strictly above 60%, finish their complete assignment and return the
  normal result. Later assignments use fresh agents. Thresholds are configurable.
  A handoff requires no active writer. Missing or stale telemetry is never counted
  as a switch.
- **Direct takeover.** The successor manager obtains the handoff from its
  predecessor and verifies Plan, files and child state before writing. Results
  remain retained, and predecessors stay write-inactive after handoff.
- **Retained decisions and stops.** An unanswered question blocks dependent
  work. A stop interrupts children and requires confirmed quiescence before
  STOPPED is reported. Resumption preserves pending findings and decisions.
- **Accepted commits and scope.** Authorized commits include accepted changes
  and Plan updates, with required hooks and backups. Workflow respects the
  requested scope and only reports completion when its acceptance is met.
- **Visible work.** `Working on:` identifies the project, Plan and point.
  `Scope:` gives the actual overall assignment as free text. Repeated events,
  reviews, repairs and manager switches at the same point add no progress message.
- **Targeted run report.** Every run gets its own Markdown file under `.scoville`,
  with the full path shown before startup. User questions, requested pauses and
  problems needing user review stay in it with their clarifications. Normal
  progress and test results stay out. A clean completed run has the sentence
  `No issues occurred during this run.`. Completion includes the report output.

[Native Codex operations](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations.md)
covers delivery, permissions and recovery.
