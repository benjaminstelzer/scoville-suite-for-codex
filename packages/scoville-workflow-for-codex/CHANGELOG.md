# Changelog

## v0.9.1 - 2026-10-02

- Correct a known dispatch-argument mistake once before interrupting the user, provided no agent start or other effect occurred. Missing facts and uncertain starts remain blockers.
- Require the absolute project path and original worker result explicitly when preparing a fresh review.

## v0.9.0 - 2026-10-02

- Choose the manager through Setup or project settings. The default is GPT-6.1 SOL with medium reasoning, retained across manager handoffs.
- Keep questions and progress in the original visible chat, with a clear heading for the active project, Plan and Step.
- Show the run report without its internal issue markers.

## v0.8.3 - 2026-10-02

- Relay necessary user questions and blockers promptly to the visible runner, including their Plan, Step, reason and waiting work. A report-save failure keeps the issue visible.
- Show the actually started Step before dispatch or resumption, including within sequential assignments.
- Preserve steering and decision answers during manager takeover, with explicit current and pending manager ownership.

## v0.8.2 - 2026-10-01

- Remove automatic capacity cleanup and retry. Retain the actual diagnostic and continuation state. Preserve necessary follow-ups and verified handoffs.
- Keep the current Plan point and Step progress clear through pause and continuation, while distinguishing a display mismatch from a changed assignment.

## v0.8.1 - 2026-10-01

- Save active Work Item and Step progress before worker execution, including corrections and recovery.
- Keep sequential assignments current through short write-inactive Step boundaries, resuming the same unfinished worker after Plan updates and due review.
- Record authorized pauses without inventing progress on unstarted work, and select successors with accepted Plan progress.
- Name the visible Workflow chat `SC-WFL PLAN-NNNN` at startup, preserving its title through manager changes and pauses.
- Give new managers, workers and reviewers unique native names automatically. Repeated reviews no longer need permission to repair a name collision.

## v0.8.0 - 2026-09-29

- Build native assignments and manager handoffs with consistent project titles, inherited manager settings and a validated report destination.
- Confirm takeover before reading, consume rollover boundaries once and return completed assignments without another checkpoint.
- Deliver the full result once to the coordinator and keep the child's final confirmation short.
- Let Scoville Setup disable automatic pinning while keeping it enabled by default.

## v0.7.3 - 2026-09-28

- Keep continuation assignments focused on remaining work and its acceptance criteria, constraints and evidence. Completed implementation instructions are no longer inserted automatically.

## v0.7.2 - 2026-09-28

- Send rollover confirmations, archival requests and other coordination messages to the intended chat instead of displaying them locally.

## v0.7.1 - 2026-09-28

- Start Workflow directly in a saved project after installing the suite, without a project setup step or an AGENTS.md block.
- Check coordinator context after worker handoffs and split remaining work after the third handoff of a Step or group.
- Review fixes to previously completed product code before continuing dependent work, while keeping ordinary implementation corrections in their assignment.
- Review only unreviewed changes and reuse earlier assessments for unchanged parts.

## v0.7.0 - 2026-09-27

- Use direct handoffs with receipt messages, without a separate run cursor.
- Handle review findings as new worker assignments. Number workers consecutively and give reviewers the number of the reviewed worker.
- Accept ordinary result messages and explicit reviewer model choices. Completed workers and reviewers archive on the coordinator's message.

## v0.6.5 - 2026-09-27

- Review completed Work Items by default and honor explicit project review boundaries. Checked Step groups can continue until that boundary.
- Reuse available workers for corrections and keep transient infrastructure attempts in local run records.

## v0.6.4 - 2026-09-27

- Set Codex Workflow rollover defaults to 40% for coordinators and 60% for workers, reviewers and fixers.
- Check context before commands expected to add substantial context, keep full logs and exit status, and read large output selectively.
- Group related coordinator state updates while preserving dispatch and rollover recovery.

## v0.6.3 - 2026-09-27

- Archive blocked Workflow workers when they are replaced. Keep a worker open when it will continue after clarification.

## v0.6.2 - 2026-09-26

- Start worker, reviewer and fixer numbering at 1 for each assigned Step range. Keep those counters through rollovers.
- Stop checks after a context handoff and start its successor without waiting for a native turn-end event.
- Preserve existing message authorization in every role assignment and keep helper unit parameters distinct from display titles.

- Keep the live cursor current, reuse loaded contracts, and delegate product-file repairs without repeating dispatch context.
- Load dispatch and rollover contracts before route or context-boundary advice.
- Continue bounded work when telemetry is unavailable and return worker handoffs through the normal role result.

## v0.6.1 - 2026-09-26

- Preserve existing user authorization for internal messages across worker dispatches and coordinator rollovers.
- Identify undelivered results explicitly and respect host-required progress waits without adding polling or archival checks.

## v0.6.0 - 2026-09-25

- Use the calling task as coordinator and dispatch one Step, consecutive Step group or whole Work Item at a time, preserving authored order.
- Keep automatic context rollover at 25 percent for coordinators and above 75 percent for child roles, with project overrides.
- Use separate role counters in S-MNGR, S-WORK, S-REVW and S-FIXR titles.
- Receive complete results directly through native messages and stop child checkpoints after their own work and checks finish.
- Pass the full Work Item once with the assigned range and only relevant constraints. Stop dispatch if the tool truncates the assignment.
- Resume remaining work with compact handoffs and archive predecessors through native takeover messages without polling or archival verification.
- Replace guard generations and transport receipts with a local Markdown run record. Retain results before archiving completed tasks.
- Read project configuration over imported defaults. Setup offers low, medium, high and xhigh. Manually written configuration may use the other Plan reasoning values when the selected model supports them.

## v0.5.0 - 2026-09-24

- Apply configurable writing depth to additional coordinator, worker and reviewer instructions while preserving canonical plan text.
- Bind profile rules and separate supplemental context into dispatch verification.
- Require Scoville Plan v1.8.0 or a selector with the same source_text contract. Report incompatible selectors before dispatch.

## v0.4.7 - 2026-09-24

- Clarify operation routing and required helper use for the coordinator.

## v0.4.6 - 2026-09-23

- Resolve task pairs from the configured routes and raise the second and third repair attempts along the WORK rows.
- Bundle project-contract and coordinator-guard verification with bounded Work Item selection in one read-only preflight call.
- Stop an affected operation when Python or a required helper cannot run instead of reconstructing its result manually.

## v0.4.5 - 2026-09-23

- Route new high-class execution to SOL 6 XHigh with Astra 6 High review, and raise ultra-high execution and review to Astra 6 High and XHigh.

## v0.4.4 - 2026-09-23

- Update route defaults for new workers and reviewers from SOL 6 Low through Astra 6 High.

## v0.4.3 - 2026-09-23

- Route new low-class execution to Luna 6 High and its review to SOL 6 Low.

## v0.4.2 - 2026-09-23

- Use Luna 6, SOL 6, and Astra 6 for new coordinators, workers, and reviewers according to the configured route. Remove Terra from the defaults.
- Verify builder assignments after the native task envelope escapes HTML characters or removes the final newline.

## v0.4.1 - 2026-09-23

- Stop agent-created workers before project access when their native task does
  not contain the complete builder-generated dispatch contract. The gate now
  checks the role, execution unit, Plan lockout, required inputs, delivery
  identity and exact reconstructed prompt bytes.

## v0.4.0 - 2026-09-22

- Ship as `scoville-workflow-for-codex`, a Codex-only Beta inside Scoville Suite.
- Configure context handover thresholds and generate SCW task titles through
  bundled helpers.
- Generate dispatch payloads once and load coordinator rules by phase, with
  retained recovery state for interrupted dispatches.
- Allow exact active-successor evidence to resolve a missing normal-list entry.
  Archive only verified predecessors after guard transfer and turn completion.
- Recover outstanding predecessor chains in order. Verify each archival reply
  and retain its receipt before continuing. Failed or unverified replies stop
  the chain without archiving the current coordinator.

## v0.3.6 - 2026-09-21

- Reserve low-risk routing for fully understood work. Discovery, integration uncertainty and checks needing interpretation use at least medium reasoning.

## v0.3.5 - 2026-09-21

- Keep coordinator-only settings and diagnostic output out of worker and reviewer prompts.

## v0.3.4 - 2026-09-21

- Treat planned routing as a minimum and reassess the full assignment before dispatch. Preserve launched models during repairs and handoffs.
- Require an accepted decision before grouping adjacent Steps.

## v0.3.3 - 2026-09-21

- Keep the active coordinator in the normal task list during rollover. The
  successor proves its unarchived visibility without pinning itself, then alone
  archives its predecessor after that predecessor turn completes.

## v0.3.1 - 2026-09-20

- Separated the initial launcher from active coordinator transitions and fixed
  the parking and ready-task handoff fields.

## v0.3.2 - 2026-09-21

- Check inherited permissions during installation and report actual access failures.
- Keep the coordinator visible while work runs, preserve undelivered answers and require verified successor takeover before retiring a predecessor.

## v0.3.0 - 2026-09-20

- Add explicit first-project setup and separate it from Workflow activation.
- Keep one coordinator and one writer active, with reviewers read-only. This is cooperative coordination, not filesystem enforcement.
- Hand over at accepted work boundaries once measured context reaches 33%, retaining ownership on uncertain starts or delivery.

## v0.2.2 - 2026-09-20

- Keep Workflow continuation event-driven instead of starting recurring turns through persistent Codex goals. Pausing an older goal does not cancel active project work.

## v0.2.1 - 2026-09-20

- Show the active Plan unit when implementation, review, repair or acceptance begins. Keep unchanged waits quiet.

## v0.2.0 - 2026-09-20

- Recover context handoffs after host compaction without duplicate successors or repeated completed work. Conflicting evidence stops continuation.
- Preserve undelivered results and avoid recurring polling while children work.
- Keep Windows prompts UTF-8, preserve Git authorization limits and assign repairs only to unresolved findings.

## v0.1.0 - 2026-09-20

- Add explicit Codex Workflow activation with a coordinator, bounded workers, independent review and model routing.
- Continue the active Plan by default, honoring requested boundaries and unresolved decisions. Use the same checkout unless isolation is explicitly chosen.
- Hand over before context exhaustion, preserve results across compaction and avoid repeated no-progress transfers.
- Keep assignments focused on their Steps and relevant Decisions. Review product changes without requiring a separate reviewer for every routine record edit.
- Keep the coordinator visible through completion so its report reaches the user.
