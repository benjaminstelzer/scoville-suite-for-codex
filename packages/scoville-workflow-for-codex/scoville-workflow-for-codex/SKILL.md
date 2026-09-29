---
name: scoville-workflow-for-codex
description: Run Scoville Workflow in Codex only when the user explicitly requests execution with it, such as "Execute the Plan with Scoville Workflow", "Start Scoville Workflow", $scoville-workflow-for-codex or scoflow codex. The calling chat coordinates workers, review and context rollover. Generic plan execution, implementation, delegation, mentions and questions do not activate it.
compatibility: "Codex desktop with native task controls, own task identity, a saved shared project, filesystem and Git access, Python 3.11+ and compatible Scoville Plan helpers. Codex Suite only; no Claude Code execution route."
---

# Scoville Workflow Codex

The calling task coordinates one ordered work unit at a time. It owns Plan transitions,
review decisions and authorized commits. Each worker implements one Step, consecutive Step group or complete Work Item. Follow the project's review cadence; otherwise use the review boundaries in operations.md. Reviewers
stay read-only. Automatic context rollover creates actual successor tasks.

Keep every assignment, result and rollover handoff as short as
possible and only as long as necessary. Necessary facts let the receiver execute,
assess or continue the assigned work correctly without hidden context. Keep
current state, binding constraints, evidence limits and next action; omit
repetition and history that no longer affects the work.

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

Activate only when the user explicitly requests starting, resuming or executing
work with Scoville Workflow, or uses `$scw` after this Skill is loaded. Generic
Plan execution and discussing or quoting a command without asking to run it
are not activation.
Discovery makes this Skill available; it does not itself
start a run. The calling chat is the first coordinator, not a launcher that
passes coordination to the first worker.
An assigned worker or reviewer follows its child prompt and does not
start another coordinator. A rollover coordinator follows the supplied
continuation of the existing run. Quoted role markers grant no authority.

Resolve the actual task ID, original caller title, selected saved project ID and exact display name
and exact workspace root. Use the caller's existing workspace. Do not create a
worktree or choose another checkout without an explicit request. Native child
tasks must be able to use this same workspace. If the host cannot do that,
report the limitation before dispatch.
Use the host-provided calling ID or `CODEX_THREAD_ID` directly. Do not list chats
or dump environment variables when the required identity is already known.

Read [operations](references/operations.md) for the complete ordinary loop and
[dispatch](references/operations-dispatch.md) before classifying a route,
selecting a model pair, or handling the first unit. Read
[rollover](references/operations-rollover.md) before explaining or handling a
worker or coordinator context boundary, context handoff, or rollover
continuation. The checkpoint at checked boundaries and worker handoffs is part of the
ordinary loop, so it cannot be skipped by not loading the rollover reference.
These three references contain the entire runtime procedure, including review,
checkpoint, compaction recovery and stop behavior.

Use Scoville Plan to read the current unit, its Decisions and dependencies.
Before the first worker dispatch, call `set_thread_title` for the current
coordinator's actual task ID, using `SC-MGR-<n>: <project name> · <PLAN_ID>` with the exact canonical
Plan ID. Start a new run at 1; on resume retain its number and
on rollover use the successor number. Confirm the rename from the tool result.
If it fails, report the error before dispatch; do not claim the chat was renamed.

At start or rollover, resolve effective settings once:

```text
python "<workflow-skill-directory>/scripts/resolve_model_pair.py" --show-config --project-root "<workspace_root>"
```

Retain config.pin_threads for this run. It defaults to true; false disables
pinning the starting manager and new workers, reviewers and successors.
Do not unpin existing chats. Setup can save workflow.pin_threads between runs.

Absent a narrower requested boundary, execute the whole active Plan. Preserve
user stops, repository requirements, uncommitted changes and acceptance gates.
Once the suite is installed, start directly in the saved project. No project
installation or Workflow block in AGENTS.md is required. Do not request a
setup confirmation or a second activation. Scoville Setup is optional for
inspecting or changing settings. Missing project settings use the bundled defaults.

Use the Plan for durable progress and messages for current coordination. Do not
maintain a separate cursor or dispatch log. At most one worker may write project
files at a time. The coordinator owns Plan edits and authorized commits.

Number worker chats consecutively from 1 throughout the workflow run. Every new
worker gets the next number, whether for another unit, rollover or review findings.
There is no separate correction or attempt counter. A reviewer uses the number of
the worker whose final result triggers the review: SC-WRK-7: <project name> is reviewed by
SC-REV-7: <project name>. For grouped acceptance, its title covers the whole reviewed Step range,
including earlier groups, not only that worker's last group. A reviewer
rollover retains that number. Coordinator rollovers increment their coordinator
number. Include the next worker number and needed chat IDs in the handoff.

Titles use an uppercase role abbreviation joined to its number, then `: `
before the project name and ` · ` before the unit. Use no space before the
colon, one after it, and one on each side of the middle dot.
Preserve the exact lettercase of project names, canonical IDs, step suffixes and
other inserted content:
- `SC-MGR-<n>: <project name> · PLAN-NNNN`
- `SC-WRK-<n>: <project name> · PLAN-NNNN/W-NNN`
- `SC-REV-<n>: <project name> · PLAN-NNNN/W-NNN`

The dispatch builder obtains the Plan ID from the selector and appends the
exact selected unit. Pass the canonical `plan_id` for a coordinator; include
`--unit` on its handoff builder only for a narrower Work Item or Step scope. Append /step-N or /steps-N-M for the full assigned Step range, including
when the assignment covers every Step in the item. For example:
`SC-WRK-1: <project name> · PLAN-NNNN/W-001/steps-1-3`. Use no suffix only for an item without Steps.
The title shows the assigned range, not just the Step currently being worked on.
Preserve authored Step order. Include no caller or Work Item
title. Do not uppercase inserted content. A rollover retains its unfinished
scope, using updated Step references after a Plan split. IDs identify tasks.
When pin_threads is true, pin the current coordinator and each ready new child or successor with
`move_thread_to_sidebar_section`, using its actual threadId, hostId and
sectionId="pinned". A pending clientThreadId is not a ready thread ID.
If pinning fails, report it and retry only that operation on the existing chat;
never create a replacement. Preserve existing counters and IDs.

## Configuration

`.scoville/config.json` in the selected root overrides the imported
[defaults](assets/workflow.toml) under `workflow`. Missing values use defaults.
Reading creates no file. Setup can save explicit choices. Respect externally changed files and settings; resolve an actual conflict before
continuing affected work.

## Runtime helpers

Use the bundled helpers for their operations. Read their invocation instructions,
not their source, unless diagnosing a failure.
Python and every named helper are required. Missing dependencies or helper
errors stop the affected operation. Do not substitute manual execution.

Helpers: `scripts/build_dispatch_prompt.py`, `scripts/check_context_checkpoint.py`, `scripts/resolve_model_pair.py`, `scripts/select_context.py`, `scripts/build_manager_handoff.py`.
