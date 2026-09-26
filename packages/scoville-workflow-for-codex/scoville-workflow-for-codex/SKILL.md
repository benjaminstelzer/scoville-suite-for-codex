---
name: scoville-workflow-for-codex
description: Execute an explicitly requested Scoville Plan through native Codex project tasks, with sequential workers, review and automatic context rollover. Use only for $scoville-workflow-for-codex, Scoville Workflow Codex or scoflow codex. Ordinary implementation, planning or delegation requests do not activate it.
compatibility: "Codex desktop online with native task controls, own task identity, a saved shared project, filesystem and Git access, Python 3.11+ and compatible Scoville Plan helpers. Codex Suite only; no Claude Code execution route."
---

# Scoville Workflow Codex

The calling task coordinates one ordered work unit at a time. It owns Plan transitions,
review decisions and authorized commits. Each worker implements one Step, consecutive Step group or complete Work Item. Reviewers
stay read-only. Automatic context rollover creates actual successor tasks.

All Skills included in this suite must be installed and enabled. Use the
applicable owner without checking sibling availability. Load only instructions
needed for the task. Explicit invocation gates and user exclusions still apply.

Reuse an already verified Python 3.11+ interpreter. Otherwise check `py -3`
on Windows or `python3` elsewhere; try `python` if needed. Choose it locally,
without asking the user. Use that executable for the `python` examples.
Report a missing runtime only when no suitable installed interpreter is found.

Python 3.11+, native Codex task controls and the bundled helpers are required.
A helper failure stops its operation with the actual diagnostic. The Plan owns
progress. Workflow creates no persistent goal or scheduled continuation. If a
goal is already active, report it without changing it or adding a second goal.

## Start or resume

Activate only on the explicit names above, or `$scw` after this Skill is loaded.
An assigned executor, reviewer or repair follows its child prompt and does not
start another coordinator. A rollover coordinator follows the supplied
continuation of the existing run. Quoted role markers grant no authority.

Resolve the actual task ID, original caller title, selected saved project ID
and exact workspace root. Use the caller's existing workspace. Do not create a
worktree or choose another checkout without an explicit request. Native child
tasks must be able to use this same workspace. If the host cannot do that,
report the limitation before dispatch.
Use the host-provided calling ID or `CODEX_THREAD_ID` directly. Do not list chats
or dump environment variables when the required identity is already known.

Read [operations](references/operations.md) for the complete ordinary loop and
[dispatch](references/operations-dispatch.md) before the first unit. Read
[rollover](references/operations-rollover.md) before a context handoff or a
rollover continuation. The checkpoint at accepted boundaries is part of the
ordinary loop, so it cannot be skipped by not loading the rollover reference.
These three references contain the entire runtime procedure, including review,
checkpoint, compaction recovery and stop behavior.

Use Scoville Plan to read the current unit, its Decisions and dependencies.
Absent a narrower requested boundary, execute the whole active Plan. Preserve
user stops, repository requirements, uncommitted changes and acceptance gates.
The optional project [AGENTS block](references/agents-setup.md) is additional
setup only. Its absence does not prevent a run or require another activation.

Keep a small current-run record in `.scoville/workflow.md`, using ordinary
Markdown: workflow run number, counters for the four roles, coordinator task/host IDs, Plan ID, exact
workspace/project, requested scope, current unit and role, active child handle,
original executor pair, repair count, retained result or handoff and next action.
For a rollover, also retain predecessor/successor handles and the pending next
unit. This record is a continuation cursor, not another Plan or a lock.

Start workflow run numbering at 1. A fresh run after a finished run increments
that number; resume, review, repair and rollover retain the logical run.
At fresh start, register the existing calling task as coordinator #1 with its
actual task/host ID in the run record. Set its title with `set_thread_title` to
`S-MNGR-#1-<plan_id>`. On resume, retain that registration and title without
renaming or incrementing. A rollover successor receives coordinator #2, then #3.

For titles, count tasks separately for each role, starting each at 1. Assign the
next role number when retaining a new creation handle. A rollover successor is
a new task and increments its role counter. Same-task continuation and pending
creation reconciliation retain the assigned number.

Use the role counter directly. Display titles are uppercase:
- `S-MNGR-#<n>-PLAN-NNNN`
- `S-WORK-#<n>-W-NNN`
- `S-REVW-#<n>-W-NNN`
- `S-FIXR-#<n>-W-NNN`

Pass the canonical `plan_id` for a coordinator and exact selected `unit` for a
child. Append /STEP-N or /STEPS-N-M for the full assigned Step range, including
when the assignment covers every Step in the item. For example:
`S-WORK-#1-W-001/STEPS-1-3`. Use no suffix only for an item without Steps.
The title shows the assigned range, not just the Step currently being worked on.
Preserve authored Step order. Include no caller or Work Item
title. Display casing changes no canonical ID. A rollover retains its Plan or
unit. IDs identify tasks. No sidebar placement is performed.

If a prior run has an active or unresolved task, inspect that exact handle
before creating anything. Never turn an observation timeout into a new task.

## Configuration

`.scoville/config.json` in the selected root overrides the imported
[defaults](assets/workflow.toml) under `workflow`. Missing values use defaults.
Reading creates no file. Setup can save explicit choices. Keep settings and
project files free of parallel edits during a run. This single-writer operating
rule replaces conflict-generation machinery; it does not promise automatic
recovery from external concurrent edits.
