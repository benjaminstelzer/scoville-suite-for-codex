# Changelog


## v2.3.11 - 2026-10-03

- Allow Context Cleanup with the tested Luna 6 Medium baseline instead of requiring a recommended frontier model.

- Let Workflow dispatch and report progress for large Plan contexts with an explicit output budget. Report the required size and allow one corrected call before starting an agent or sending progress, without truncating context.
- Validate an explicitly named current section while preserving other historically started Plan Steps.

## v2.3.10 - 2026-10-03

- Resume a paused Plan point before Workflow begins its authorized reconciliation or preparation. Distinguish selection from actual work and preserve existing Step progress.

## v2.3.9 - 2026-10-03

- Keep configuration and workarounds in the right place when building Skill READMEs. Preserve shared fragments needed by the suite so filtered exports build on their own.

## v2.3.8 - 2026-10-02

- Let Workflow correct a known dispatch-argument mistake once before raising a blocker. Missing evidence and uncertain agent starts still stop the operation.
- Make review inputs explicit so a missing worker result does not derail the next handoff.

## v2.3.7 - 2026-10-02

- Configure Workflow's manager and reasoning through Setup, retaining the chosen pair across handoffs. Keep progress and questions clear in the original chat.
- Prepare Claude questions and follow-ups from text files with retained settings and clearer input errors.
- Improve Code, Plan, UI, Handoff and project-rule cleanup with the same changes as the general edition.

## v2.3.6 - 2026-10-02

- Show necessary Workflow questions and blockers in the visible chat with the affected Plan, Step, reason and waiting state.
- Display the actually started Step when work advances within a larger assignment. Preserve steering and decision answers during manager takeover.

## v2.3.5 - 2026-10-01

- Keep Workflow progress and verified manager handoffs tied to the actual Plan state.
- Remove automatic capacity cleanup and retry from Workflow and Ask. Preserve diagnostics, results and continuation. Recommend a Codex per-session limit of 256 for multiple Workflows.
- Accept complete Ask adviser finals without startup acknowledgements and keep incomplete answers available for exact-handle follow-up.
- Show Plan Viewer 1.4.2 progress and current work in a compact, collapsible overview. Clarify Code, Cleanup and UI checks at their existing owners.

## v2.3.4 - 2026-10-01

- Record active Work Items and Steps before worker execution, and keep progress current inside sequential assignments.
- Preserve unstarted work on stop, record authorized pauses and resume from the actual remaining work.
- Filter paused and cancelled Plan points directly in Plan Viewer 1.4.1.
- Name the Workflow chat `SC-WFL PLAN-NNNN` at startup, using its actual Plan ID.
- Give each new native agent a unique name automatically, including repeated reviews of one worker.



## v2.3.1 - 2026-10-01

Known limit: a targeted Handoff test promoted a preference to a requirement.
Check that distinction when resuming from a generated prompt.

## v2.3.0 - 2026-10-01

- Add Project Context Cleanup for requested edits to project rules and index text, preserving their meaning and record ownership.
- Record Step progress and additional instructions in Plan. Select the written position without guessing unknown progress, and repair proven progress from Evidence and actual results.
- Ship Plan Viewer 1.4.0 for all four platforms with matching Step progress, active groups, Instructions and open Decisions.

- Run Workflow and Ask through native agents, retaining exact handles for necessary follow-ups and ending completed turns without routine messages.
- Show Workflow position only when it changes, preserve the assigned Scope and finish with the run report. The report retains user questions and problems needing attention, with an explicit clean-run result when none occurred.
- Allow one bounded cleanup and unchanged retry after a definite native capacity refusal. Other errors and uncertain starts keep their existing blocked or pending state.
- Update configured routing pairs and keep the runner within its coordination role.


## v2.2.1 - 2026-09-29

- Check runtime and memory costs before and after code changes. Prefer simpler algorithms, use suitable existing caches correctly and obtain the user's decision before adding a new cache unless already authorized.

- Continue waiting for native Ask reviews after a wait timeout and return the complete result in the calling chat. Keep consultation references distinct from reviewed scopes during follow-up.


## v2.2.0 - 2026-09-29

- Keep manual no-Python procedures separately loadable in the general edition. Codex requires the packaged helpers, with concrete diagnostics for invalid calls.
- Continue explicitly requested Plan execution through eligible work while preserving recorded stops and unresolved Decisions.

- Build Workflow assignments and rollover prompts with consistent project titles, the manager's own model settings and an exact report destination. Successors take over before reading and do not repeat an inherited checkpoint boundary.
- Keep complete worker and reviewer results in the message to the manager, with a short delivery confirmation in the child chat. Finished assignments return without another checkpoint.
- Keep Ask advisers available for follow-up. The caller collects native answers and owns the closing question, while Claude follow-ups retain the same session.
- Add separate Setup switches for Ask and Workflow chat pinning, both enabled by default.



## v2.1.9 - 2026-09-28

- Recognize explicit requests to run Scoville Workflow without requiring the dollar-prefixed Skill name. Generic plan execution, mentions and questions still do not start it.
- Keep coordination in the calling chat from the first dispatch, with its manager title set before a worker starts.



## v2.1.8 - 2026-09-28

- Explicitly end Workflow when its requested scope is complete. Later requests return to normal assistance until Workflow is explicitly activated again.



## v2.1.7 - 2026-09-28

- Continue unfinished Workflow tasks with only the remaining work, relevant constraints and retained evidence, instead of resending the complete Work Item.



## v2.1.6 - 2026-09-28

- Rename the Workflow coordinator before its first worker starts and use clear chat titles such as SC · MNGR · 1 · PLAN-0001.
- Use the same middle-dot separators in worker, reviewer and Ask chat titles, without hash signs before counters.



## v2.1.5 - 2026-09-28

- Start Workflow from its Skill entry prompt in the current chat, without a setup gate or a separate launcher coordinator. Setup remains optional for inspecting or changing settings.


## v2.1.3 - 2026-09-28

- Keep Code safeguards proportionate to actual consequences and preserve useful output when a later step fails.
- Give UI ownership of interface wording, terminology and unsettled task structure.
- Check the affected composition and responsive behavior after UI changes.


## v2.1.2 - 2026-09-28

- Deliver rollover confirmations and coordination requests to their intended chats through native messages.


## v2.1.1 - 2026-09-28


- Start Workflow directly in a saved project after installing the suite, without a project setup step or an AGENTS.md block.
- Check coordinator context at worker handoffs and split oversized unfinished Steps without changing their acceptance criteria.
- Review completed product fixes before dependent work and reuse earlier reviews for unchanged code.

- Split unfinished Plan Steps without changing scope, acceptance criteria or completed evidence.
- Keep pure visual concepts outside the WordPress implementation adapter.

## v2.1.0 - 2026-09-27

- Run Workflow through direct handoffs and ordinary worker results. Review findings start a new worker, and chat numbers identify the reviewed work.
- Explain invalid helper inputs with the expected value and a concrete correction.
- Keep Plans and handoffs focused on the facts needed to execute, verify or continue.

## v2.0.6 - 2026-09-27

- Review completed Workflow Work Items at the project-defined boundary and reuse available workers for corrections.
- Keep formal Plan updates and related test repairs within their existing Work Item, with concise evidence and retained history.

## v2.0.4 - 2026-09-27

- Set Codex Workflow rollover defaults to 40% for coordinators and 60% for workers, reviewers and fixers.
- Check context before commands expected to add substantial context, keep full logs and exit status, and read large output selectively.
- Group related coordinator state updates while preserving dispatch and rollover recovery.

## v2.0.3 - 2026-09-27

- Archive blocked Workflow workers when they are replaced. Keep a worker open when it will continue after clarification.

## v2.0.2 - 2026-09-26

- Keep per-unit Workflow role numbering, stop work at context handoff, and preserve message authorization and exact return identities.
- Separate Handoff preferences from requirements and name blocking Plan decisions before the action they prevent.
- Preserve existing file encoding and line endings, report individual check failures, and keep Workflow cursors and delegated ownership current.
- Clarify Handoff recovery, final Plan completion, UI evidence ownership and Workflow context boundaries.
- Resolve explicit Ask adviser presets and retain precise mismatch and Claude-timeout recovery state.
- Reuse the unchanged Plan Viewer v1.3.3 binaries and checksums for the compatible Plan package.

## v2.0.1 - 2026-09-26

- Preserve existing user authorization through native Workflow and Ask handoffs, and report answers that could not be delivered.
- Respect host-required progress waits while keeping internal coordination free of extra polling and archival checks.

## v2.0.0 - 2026-09-25

- Group related consecutive Workflow Steps, receive results through native messages and continue unfinished work through compact context handoffs.
- Keep native Ask advisers in separate chats with S-ASK model titles, without a lifecycle helper between Codex and its task tools.
- Bundle Plan Viewer v1.3.3 and build its Windows, Linux and macOS assets with one checksum manifest from the suite workflow.
- Replace the old Code and UI package names, combine Ask variants, add Setup and simplify Plan and Workflow configuration.
- Install General and Codex suites through short migration prompts that remove only listed old Skills before a fresh complete installation.

## v1.1.0 - 2026-09-24

- Build general and Codex suites from one manifest. Keep Python replacement procedures only in the general edition.
- Require complete suite installations from their own packages. Standalone Skills remain independent.
- Add shared writing profiles with independent Plan and Workflow configuration.
- Preserve exact plan-point text and bind additional context and writing rules into Workflow dispatches.
- Bundle the compatible Plan v1.8.0 and Workflow v0.5.0 pair. Plan Viewer v1.3.2 remains unchanged.

## v1.0.10 - 2026-09-24

- Keep High risk classification for concrete planning or risk review of high-impact operations, even when execution is deferred.
- Make Workflow operation routing and helper use explicit for the coordinator.

## v1.0.9 - 2026-09-23

- Resolve WORK and REVIEW pairs from the configurable route table and raise the second and third repair attempts along its WORK rows.
- Bundle project-contract and coordinator-guard verification with bounded Work Item selection in one preflight helper.
- Require Python 3.11+ during suite installation; Workflow stops an affected operation when a required helper cannot run.
- Document Plan's no-Python dispatch-unit selection and Decision-batch hashing routes.

## v1.0.7 - 2026-09-23

- Route new high-class Workflow work to SOL 6 XHigh with Astra 6 High review, and raise ultra-high work and review to Astra 6 High and XHigh.

## v1.0.6 - 2026-09-23

- Route new Workflow work through SOL 6 and Astra 6 with the updated reasoning levels for every class.

## v1.0.5 - 2026-09-23

- Route new low-class Workflow execution to Luna 6 High and its review to SOL 6 Low.

## v1.0.4 - 2026-09-23

- Recognize a verified parking prompt and the complete writer assignment when Codex delivers both in one native turn, while blocking duplicate or conflicting assignments.

## v1.0.3 - 2026-09-23

- Keep Workflow's dispatch binding stable when the writer moves from pending to active, while retaining the separate target and guard checks.

## v1.0.2 - 2026-09-23

- Route new Workflow tasks through Luna 6, SOL 6, and Astra 6. Remove Terra from the default routing table.
- Verify builder assignments after the native task envelope escapes HTML characters or removes the final newline.

## v1.0.1 - 2026-09-23

- Stop Workflow workers before project access unless their native task carries
  the complete builder-generated dispatch contract for the assigned role and
  execution unit.
- Let established codebases keep their local conventions. For Greenfield work,
  start with the smallest coherent responsibility-based layout without
  prescribing an architecture or directory tree.

## v1.0.0 - 2026-09-22

- Install the Scoville Skills together from one suite or use individual
  distributions for the concerns you need.
- Include Scoville Workflow as a Codex-only Beta, available only in the suite.
  It coordinates Plan execution, reviews, repairs and context handovers.
- Include the renamed WordPress UI Backend specialist. Replace an existing
  `wordpress-backend-ui` installation with
  `scoville-wordpress-ui-backend-anti-ai-slop`.
- Bundle runtime helpers inside each Skill so installed packages need neither
  the suite source tree nor a shared directory.
