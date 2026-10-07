---
format_version: 1
id: PLAN-0001
status: active
created: 2026-09-14
updated: 2026-09-20
current_item: W-021
---

# Native Codex Scoville workflow

## Goal

Provide a private `scoville-workflow-codex` Skill that preserves the Scoville Workflow source contract at `scoville-workflow` commit `3351f8aee3397a0aff6865596fcc285a7724138c` plus the accepted native-only deltas entirely through normal native Codex project tasks.

## Non-goals

Do not use or reproduce the Codex CLI runner, runtime installation, process supervisor, SQLite state, snapshots, adoption, automatic worktrees, packet Skill lists, automatic push, or public releases. Do not qualify the separate CLI implementation through this Plan.

## Work items

### W-001 Deliver the native task workflow

Status: done
Depends on: []
Blocked by: []
Decisions: [ADR-0001]
Outcome: Explicit invocation launches one coordinator that delegates each Plan unit to one suitable native executor, continues that same task across user decisions, obtains a fresh native review, archives terminal child tasks, owns Plan updates and the accepted unit's simple commit, and archives itself when the requested Plan is complete.
Acceptance: The package contains no CLI/runtime implementation; frontmatter and host metadata prevent implicit activation and make the launcher stop after coordinator creation; the coordinator uses the saved project checkout and never performs project or acceptance work beyond Plan records and one reviewed commit; one existing Step or the whole Step-less Work Item selects exactly one executor and one fresh reviewer without splitting mixed activities; normal project instructions and project-relevant personal memory plus Skills plugins and apps remain available without configuration or packet allowlists; every child prompt carries exact no-stage no-commit no-push no-history-rewrite boundaries and reviewer read-only authority; first attempt plus at most two actual repairs remains binding; executor and reviewer `needs_user_decision` both continue through `send_message_to_thread` on the same task ID without archival attempt increment or model override; a pending clientThreadId is retained and reconciled by unique project/title without duplicate dispatch; a native failure without JSON or exhausted formatting correction becomes a coordinator-owned Plan blocker and verified archival without an invented handoff. Routing is coordinator SOL medium; executor/reviewer pairs are Luna medium/Terra medium for ultra_low; Terra medium/SOL medium for low; SOL medium/Astra low for medium; SOL high/Astra medium for high; Astra medium/Astra high for ultra_high. Handoffs are normally below 3000 with target 7000 and hard 8000 characters; result prose targets 2000 and stops above 4000 with summary 800 maximum and at most eight findings of 400; coordinator notices target 400. Every workflow transfer expressly forbids Scoville Handoff and uses only the compact native result plus missing turn-specific facts. Prompts expose each controllable limit before work and omit Plan duplication and routine narration. Focused tests Skill validation Plan-profile validation and an independent Astra Medium implementation review report no open actionable finding; live native lifecycle behavior remains owned by W-002.
Evidence: Native-only source and contracts passed after independent Astra review and lifecycle corrections. Live qualification remained separately owned.

### W-003 Add native context rollover

Status: done
Depends on: [W-001]
Blocked by: []
Decisions: [ADR-0002]
Outcome: A native executor or reviewer whose freshly observed context exceeds 66 percent at a natural internal boundary hands the remaining work to one compact successor task for the same unit and role instead of attempting manual compaction or continuing the overfilled session.
Acceptance: Every initial and successor prompt gives the receiver the complete 66-percent checkpoint before work; only the exact own rollout selected through CODEX_THREAD_ID is eligible; a token_count sample is fresh only when its ordinal follows the current turn_context and any later compacted event; a fresh measurement at or below 66 continues the same task; a value above 66 returns `context_handoff` with only state absent from the Plan and named evidence; the coordinator handles that branch before completion review archives the task and creates exactly one same-logical-attempt successor with the same unit role model reasoning authorization and remaining work; no reviewer starts until the executor chain completes; rollover neither consumes a repair nor changes independent-review identity rules; user-decision replies still continue the same task; missing or stale context measurement returns a blocker and never triggers an estimated rollover.
Evidence: Exact-own-rollout telemetry was observed; rollover contracts passed and independent Astra review found no actionable source-contract issue.

### W-004 Package install and privately publish the Skill

Status: done
Depends on: [W-001, W-003]
Blocked by: []
Decisions: [ADR-0003]
Outcome: The family-aligned Skill package is installed locally from its exact nested package and published from this directory to a new separate private GitHub repository without reusing the deleted CLI repository.
Acceptance: The README follows the current Scoville family structure and accurately explains explicit invocation native Codex compatibility private-source installation boundaries and the still-open live qualification; the installable package contains all required Skill metadata references assets and its license; focused contract Skill and Plan-profile checks pass; installation waits until the active legacy DIVI5 workflow is terminal then the exact installed inventory and content match the nested source package and the host discovers the Skill; this directory becomes a Git repository on `main` with one scoped initial commit and an `origin` that points only to `benjaminstelzer/scoville-workflow-codex`; GitHub reports that repository as private with `main` as its default branch and the pushed commit matching local HEAD; the deleted `scoville-workflow-for-codex-win` repository is neither recreated nor referenced as a remote; no release or tag is created; W-002 remains open until an explicitly invoked native fixture supplies its own runtime evidence.
Evidence: Private native package installed with source parity and pushed to its private repository; structure and profile checks passed. No tag or release created; live qualification remained separate.

### W-002 Qualify the native lifecycle

Status: todo
Depends on: [W-001, W-003, W-004]
Blocked by: []
Decisions: [ADR-0007, ADR-0008, ADR-0010, ADR-0003]
Outcome: One bounded native fixture proves launcher isolation same-checkout dispatch same-task user-decision continuation independent review sparse transitions verified child archival and a visible coordinator completion report without product browser website or remote writes.
Acceptance: An explicitly invoked fixture records launcher coordinator executor and reviewer task IDs; launcher loads no project or execution context and stops after coordinator creation; one child creation returning clientThreadId is retained then resolves to exactly one ready threadId without duplicate dispatch; executor and reviewer each return `needs_user_decision` once and continue afterward on the identical task ID without a repair count; one separately measured context rollover above 66 percent creates one compact same-unit successor without a repair count and without premature review while a value at or below 66 continues the same task; a stale pre-compaction or pre-turn record is rejected rather than used; one simulated native failure without JSON and one second-invalid-result path both record a coordinator-owned blocker archive the terminal task and start no review; every executor reviewer repair and rollover successor receives the same absolute project path and current working state as the coordinator, including uncommitted changes Plan updates and local runtime state; a Git repository alone never creates a worktree; an explicit user worktree instruction remains binding and discloses transfer plus non-inherited state before creation; absence of a native same-workspace path produces an exact user decision instead of automatic isolation; the executor and fresh reviewer use the configured model/reasoning; output contains only required compact transitions; one user Stop is forwarded to the active child and either freshly confirmed or honestly escalated for UI stop; each terminal child returns verified archived state; the coordinator posts one final completion report and remains unarchived so that report stays visible; retained evidence names task IDs wait results archival results and any host-enforced commentary without copying full conversations.
Evidence: []
Next action: After W-001 passes source-contract review ask the user to explicitly invoke the bounded native qualification fixture.

### W-005 Repair native role identity and completion

Status: done
Depends on: [W-001, W-003]
Blocked by: []
Decisions: [ADR-0001, ADR-0002]
Outcome: A minimal source-based native smoke test creates one SOL-medium coordinator that alone dispatches the configured worker and reviewer routes closes the Plan validly and archives only itself and its terminal children while the invoking launcher stops without project access or monitoring.
Acceptance: A fresh launcher without `scoville_role=coordinator` reads only this Skill routing configuration and saved-project identity then creates exactly one SOL-medium coordinator and ends; the coordinator prompt contains no launcher-only instruction and the coordinator never launches another coordinator; coordinator identity comes only from runtime CODEX_THREAD_ID and self-archival is the terminal omitted-ID call while external test inspection proves it archived the coordinator never the launcher caller or return task; coordinator loads Scoville Plan before Plan mutation and completes the final Work Item Plan and PROJECT_INDEX as one valid lifecycle transition with zero profile-validator diagnostics before committing; `ultra_low` dispatch uses Luna-medium execution and a fresh Terra-medium read-only review; task prompts do not repeat Plan-owned requirements; launcher coordinator worker and reviewer outputs omit routine narration; terminal worker reviewer and coordinator tasks are verified archived while the original calling task remains unarchived; the scoped fixture result remains byte-identical and its commit contains only the accepted result plus valid Plan records; focused contract tests Skill validation and a fresh Astra Medium review find no remaining source-contract defect in this scope.
Steps:
1. Record the two smoke runs and obtain a fresh Astra Medium assessment of the smallest sufficient role identity lifecycle and archival corrections.
2. Implement the reviewed prompt identity Plan-lifecycle and sparse-output guards with focused regression coverage.
3. Run a fresh isolated source-based smoke test and verify routes task identities archival states Plan validity commit scope and caller survival.
Evidence: Corrected native smoke proved role identity, routes, valid Plan completion, scoped commit, exact archival and caller survival. Independent Astra review confirmed the fixes.

### W-006 Qualify every route across a serial multi-item loop

Status: done
Depends on: [W-001, W-003, W-005]
Blocked by: []
Decisions: [ADR-0001]
Outcome: One minimal native fixture completes five sequential Plan items across all configured risk routes with a fresh passing reviewer for every item and no duplicate or overlapping dispatch.
Acceptance: The fixture contains one tiny byte-write Work Item for each of ultra_low low medium high and ultra_high; actual task creation records prove the configured executor and reviewer model plus reasoning for every class; the coordinator starts the next executor only after the current executor result fresh reviewer verdict archival and accepted commit; exactly five executors and five reviewers are created with no repair or rollover tasks; every result is byte-correct; all ten child tasks and the final coordinator are archived while the calling task stays active; the fixture Plan and index finish structurally valid with a clean worktree and exactly five scoped acceptance commits; retained evidence contains task IDs routes verdicts commits and archive states without full transcripts.
Steps:
1. Create a disposable five-item fixture whose work is deliberately trivial while each item carries one distinct route annotation.
2. Invoke the source Skill once and let one SOL-medium coordinator complete all five executor-review-commit cycles serially.
3. Inspect task creation arguments Plan lifecycle commits outputs and archived states then retain only concise evidence and remove the fixture.
Evidence: Native multi-item fixture proved every configured route and serial execution, independent review, accepted commit and archival, without duplicates or overlap.

### W-007 Apply a material-change review threshold

Status: done
Depends on: [W-004]
Blocked by: []
Decisions: [ADR-0004]
Outcome: The native workflow requests independent review for codebase changes and critical documentation changes without making preparation, project inspection, or other non-material work trigger review by itself.
Acceptance: `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` define one result-based threshold that requires review for codebase changes or documentation whose correctness materially governs security, permissions, data handling, migrations, deployment, operations, public behavior, or required acceptance and lifecycle behavior. Read-only discovery, project inspection, preparation, planning-record maintenance, and routine documentation changes do not trigger review by themselves unless the user, Plan, or repository requires it. Focused contract tests cover both branches, Skill and Plan validation pass, the local installed package matches the nested source, and remote `main` matches the scoped pushed commit without a release or tag.
Steps:
1. Update `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` with the material-change review branch and its acceptance, repair, commit, and archival consequences.
2. Update `development/tests/test_contract.py`, `README.md`, and `CHANGELOG.md` only where needed to keep the private source contract and user guidance coherent.
3. Run focused contract, Skill, Plan-profile, repository-structure, and scoped-diff checks against the final source tree.
4. Install the exact nested `scoville-workflow-codex/` package locally and verify its inventory and bytes against the source package.
5. Commit the reviewed paths, push `main`, and verify the private GitHub repository points to the committed result without creating a release or tag.
Evidence: Material-change review threshold corrected after independent Astra review; focused checks and installation parity passed. Reviewed source pushed privately without a release or tag.

### W-008 Prevent routine reads of active child chats

Status: done
Depends on: [W-004]
Blocked by: []
Decisions: [ADR-0005]
Outcome: The coordinator waits for native child-task results without reading active child conversations or spending tokens on chat inspection unless the user explicitly requests that inspection.
Acceptance: `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` require cursor-based `wait_threads` waiting during normal execution and forbid routine `read_thread` calls for active children. A general status request uses a bounded wait snapshot. Only an explicit user request to inspect or read one named child conversation permits one bounded `read_thread` call, and that read never replaces a fresh wait result or the validated child result contract. README and focused tests expose the rule, the final combined source passes validation and Astra Low review, and W-007 resumes for one local installation and GitHub push.
Steps:
1. Update `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` with the wait-only normal path and explicit user-request exception.
2. Update `development/tests/test_contract.py`, `README.md`, and `CHANGELOG.md` with focused contract coverage and concise user guidance.
3. Run focused contract, Skill, Plan-profile, repository-structure, and scoped-diff checks on the combined source.
4. Obtain the user-authorized Astra Low review of the combined final source before resuming W-007.
Evidence: Wait-only normal path and explicit chat-read exception passed focused checks and independent Astra review; combined source was ready for W-007 distribution.

### W-009 Continue through the requested Plan scope

Status: done
Depends on: [W-008]
Blocked by: []
Decisions: [ADR-0006]
Outcome: A coordinator without an explicit Work Item or end boundary continues through the entire active Plan instead of stopping after one accepted unit.
Acceptance: The launcher preserves an explicit named Work Item range or end boundary and otherwise marks the whole active Plan as the requested scope. The coordinator rereads the Plan after every accepted unit and dispatches the next eligible in-scope item without another user confirmation. It returns control only for an exact user decision or after the explicit boundary or complete Plan is reached. A blocked unit does not end the loop while another in-scope item is eligible; without one the coordinator asks for the exact disposition decision and remains unarchived. Focused tests and an Astra Low review of the changed files find no open contract defect. The exact package is installed locally and private remote `main` matches the pushed commit without a release or tag.
Steps:
1. Update `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` with the default whole-Plan scope and explicit-boundary loop rules.
2. Update `development/tests/test_contract.py`, `README.md`, and `CHANGELOG.md` with focused coverage and concise user guidance.
3. Run focused contract Skill Plan-profile repository-structure and diff checks then obtain the requested Astra Low review of the changed files.
4. Install the exact nested package locally then commit push and verify the private remote without creating a release or tag.
Evidence: Whole-Plan continuation and subplan/model-unavailability defects corrected after independent Astra review; focused checks and source-install parity passed, with private remote parity.

### W-010 Keep the completion report visible

Status: done
Depends on: [W-009]
Blocked by: []
Decisions: [ADR-0007]
Outcome: The coordinator leaves its own task open after posting the final completion report, while terminal child tasks continue to be archived.
Acceptance: `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` forbid coordinator self-archival and require one visible final completion report after the requested scope completes. Focused contract tests reject the old omitted-ID self-archive contract, Skill and Plan-profile validation pass, the exact source package replaces the local installed package, and private remote `main` matches the scoped commit without a release or tag.
Steps:
1. [route: low] Replace the coordinator self-archive contract in `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` while preserving child archival.
2. [route: low] Update `development/tests/test_contract.py`, `README.md`, and `CHANGELOG.md` for the visible final-report behavior.
3. [route: low] Run focused contract, Skill, Plan-profile, repository-structure, and scoped-diff checks on the final source.
4. [route: low] Replace the local installed package, verify exact source parity, commit the scoped result, push `main`, and verify the private remote without creating a release or tag.
Evidence: Visible final report with child archival passed focused checks and source-install parity; source pushed privately. Legacy quick validator rejected only its unsupported compatibility key.

### W-011 Deferred after W-010: Preserve one shared workflow workspace

Status: done
Depends on: [W-010]
Blocked by: []
Decisions: [ADR-0008]
Outcome: The coordinator executor reviewer repair and rollover conversations use the workflow's already-active checkout and its current local state unless the user explicitly requests a separate worktree or a higher project rule requires isolation.
Acceptance: The Skill records the active checkout's absolute path once and passes the same saved-project local environment to every child and successor so uncommitted changes Plan updates and local runtime state remain immediately visible. A Git repository alone never selects a worktree. An explicit worktree instruction or binding isolation rule is honored only after the coordinator explains the new workspace transfer path and non-inherited local state. If the host cannot create a new conversation in the existing workspace it asks the user for a decision and never falls back silently. Focused tests cover same-path successors dirty-state visibility Git-only no-worktree explicit-worktree compliance and missing-same-workspace failure. The exact combined package replaces the local installation and private remote `main` matches the scoped commit without a release or tag.
Steps:
1. [route: medium] Strengthen the shared-workspace contract in `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` for every child and successor creation path.
2. [route: low] Add focused cases to `development/tests/test_contract.py` and update `README.md` plus `CHANGELOG.md` with the user-visible workspace behavior.
3. [route: low] Run focused contract Skill Plan-profile repository-structure and scoped-diff checks on the combined final source.
4. [route: low] Replace the local installed package verify exact source parity commit the scoped result push `main` and verify the private remote without creating a release or tag.
Evidence: Shared-workspace paths, dirty-state visibility and explicit isolation handling passed focused checks; installed source and private remote matched. Legacy compatibility-key limitation remained.

### W-012 Bound coordinator Plan context

Status: done
Depends on: [W-011]
Blocked by: []
Decisions: []
Outcome: Each coordinator selection emits only the required semantic projection through the deterministic read-only selector owned by Scoville Plan, while separate bounded reads preserve all remaining Plan semantics.
Acceptance: For each selection operation the coordinator consumes only Plan frontmatter, Goal and Non-goals, the selected complete Work Item, direct-dependency status lines, and Decisions referenced by that item. Proposal discovery, dependency-evidence preflight, graph or paused-return inspection, and complete relevant-item reads remain separate bounded operations when existing Plan semantics require them; none may broaden the selector payload or fall back to a raw full file. A fixture with a Plan of at least one MiB returns the same selected facts without emitting unrelated Work Items or Decisions. Recovery fixtures cover an unrelated proposal, relevant dependency Evidence, a queued successor, and a paused return target. Selector absence, malformed boundaries, or an output-budget breach returns one structured blocker instead of dumping or truncating source. Focused contract tests reject `Get-Content -Raw` or equivalent whole-Plan output in coordinator paths and preserve format-version-1 semantics.
Evidence: Live selector emitted only the intended semantic areas; isolation and recovery checks passed. Proposal, dependency and paused-return reads remained separately bounded.

### W-013 Batch behavior-complete dispatch and review

Status: done
Depends on: [W-012]
Blocked by: []
Decisions: [ADR-0009]
Outcome: Compatible subordinate steps share one executor and one behavior-boundary review instead of paying fresh-task and project-recovery cost for every activity step.
Acceptance: Implementation uses accepted ADR-0009 and the exact locally validated Scoville Plan compatibility contract before either Skill is published. The workflow defines a deterministic bundle only when adjacent steps share one outcome, owner, authorization, route, workspace, and Acceptance boundary; a changed Decision, external effect, materially higher risk, or independently resumable result forces a boundary. A five-step compatible fixture creates one executor and at most one required reviewer, while mixed-route and user-decision fixtures remain separated. Read-only discovery, preparation, routine Plan maintenance, and non-critical documentation still create no reviewer by themselves.
Evidence: Bundle compatibility and mandatory boundaries passed source-contract checks; native executor/reviewer count qualification remains owned by W-017.

### W-014 Minimize coordinator turns and resident instructions

Status: done
Depends on: [W-012]
Blocked by: []
Decisions: []
Outcome: The coordinator retains only one owner for each workflow rule and uses the fewest model turns needed for waiting, Plan transition, review classification, validation, and commit.
Acceptance: `scoville-workflow-codex/SKILL.md` contains the role gate, launcher, routing, and reference triggers without duplicating the result, checkpoint, wait, review, repair, or completion contracts owned by `references/operations.md`. The always-loaded entrypoint becomes materially smaller while all focused contract cases retain their meaning; practical token savings are evaluated only through W-017. One transition batches deterministic Plan selection, scoped diff classification, structural validation, staging inspection, and status evidence where safety permits; unchanged waits use the longest supported bounded timeout and never add status narration or active-chat reads. Focused contract tests preserve blocker and stale-state behavior; coordinator-turn savings are evaluated only through the W-017 real-project observation.
Evidence: Entrypoint shortened; operations owns runtime rules without duplicates. Focused batching, waiting and stale-state checks passed. Practical savings remain owned by W-017.

### W-015 Make context rollover fail-soft and evidence-based

Status: done
Depends on: [W-012]
Blocked by: []
Decisions: [ADR-0010]
Outcome: Context telemetry prevents genuine exhaustion without terminating otherwise valid executor or reviewer work merely because `token_count` is absent or stale.
Acceptance: ADR-0010 supersedes ADR-0002 and preserves the strict above-66-percent trigger for fresh exact telemetry. Missing, stale, or contradictory telemetry never becomes the sole blocker for a bounded task that can still return its valid role result. Fresh telemetry is checked only at a natural boundary with material work remaining. Focused tests cover unavailable, stale, below-threshold, above-threshold, post-compaction, completed-without-checkpoint, and same-role successor behavior.
Evidence: Fail-soft telemetry scenarios passed: missing or stale telemetry creates no blocker or successor; fresh exact occupancy retains the strict rollover trigger.

### W-017 Observe the optimized workflow in a real project

Status: todo
Depends on: [W-013, W-014, W-015]
Blocked by: []
Decisions: [ADR-0009, ADR-0010, ADR-0011, ADR-0012, ADR-0013]
Outcome: One explicitly authorized real project shows whether the optimized workflow lowers practical token and task overhead while preserving lifecycle correctness.
Acceptance: Before the end-to-end run, an independent Terra Medium forward test uses the exact working-tree Skill packages to read the active Plans in DIVI and EMPCO. Its reported Plan frontmatter, Goal and Non-goals, current Work Item, direct-dependency status lines, and referenced Decisions match direct selector output, and its trace shows `select_context.py` was invoked instead of reading a raw full Plan; any mismatch or unused selector keeps W-017 nonterminal. Run the optimized workflow end to end on a real project and compare its observed usage with the retained DIVI and EMPCO workflow baselines using the same available accounting categories. Record exact coordinator, executor, repair, reviewer, and rollover task IDs; processed input, cached input, uncached input, output, peak context ratio, coordinator tool turns, Plan-output bytes, task counts, completed Work Items, model and reasoning routes, cache conditions, and every separate bounded semantic read introduced by W-012. Report scope differences and normalize uncached input, turns, and task counts per completed Work Item when raw totals are not comparable. Classify the result as better, unchanged, worse, or inconclusive; do not substitute a synthetic paired benchmark or fixed percentage gate. Observe a compatible five-Step range using one executor and at most one initial reviewer, with mixed-route and user-decision boundaries remaining separate; if the real project cannot exercise both bundle and boundary cases, classify native qualification as inconclusive and keep W-017 nonterminal. The observed run contains no raw full-Plan dump, no telemetry-only blocker, no duplicate normative workflow block, and no avoidable executor or reviewer split for a compatible bundle. All role, workspace, review, repair, Stop, completion-report, Plan-validation, local-package parity, private-push, and no-release contracts remain green.
Instructions: The user retains ownership of the real-project end-to-end run.
Steps:
1. [status: done] Run the independent Terra Medium forward test against the exact Skill packages and compare both DIVI and EMPCO contexts with direct selector output.
2. [status: todo] Run the explicitly authorized real-project workflow end to end; compare every required usage and lifecycle measure with the retained DIVI and EMPCO baselines, qualify the compatible bundle and boundary cases, and record the result and evidence limits required by Acceptance.
Evidence: Independent selector probes and corrected boundary contracts passed; Astra review confirmed source fixes. User-owned end-to-end usage comparison and native bundle qualification remain open.

### W-018 Enforce normalized Goals and explicit execution overrides

Status: cancelled
Depends on: [W-013, W-014, W-015]
Blocked by: []
Decisions: [ADR-0018, ADR-0019]
Outcome: Scoville Plan prevents operational history from accumulating in Plan Goals, and Scoville Workflow honors an explicitly chosen model or reasoning effort at the exact unperformed Work Item or Step without weakening route, review, or context rules.
Acceptance: Goal edits use a complete proposed-state ownership audit and leave Goal byte-identical for operational-only messages; the lossless selector remains unchanged in semantic scope and no size or truncation gate is added. Native Plans support one optional Work Item execution override and one optional Step execution annotation with strict syntax, property-wise precedence Step over Work Item over route default, host-pair validation, started-item protection, reviewer isolation, successor inheritance, and bundle separation by effective executor pair. Plan validator, viewer, selector contracts, evaluation cases, Workflow contracts, source-package structure, installed-package parity, and repository-owned tests pass.
Steps:
1. [route: high] Update Scoville Plan instructions and native references with normalized Goal ownership, complete proposed-Goal auditing, requirement-reachability checks, and the explicit execution-override lifecycle.
2. [route: high] Extend Scoville Plan validation, viewer models and rendering, fixtures, contracts, and evaluation cases for valid, partial, malformed, inherited, started-item, and lossless-selection behavior.
3. [route: high] Update Scoville Workflow routing, pair resolution, bundling, repair and rollover inheritance, unsupported-pair handling, and contract tests without changing reviewer routing.
4. [route: medium] Install both canonical packages locally, verify exact package parity, and run all focused structure and repository-owned checks.
Evidence: Field-based implementation passed focused checks, but the user rejected its Work Item field and Viewer schema expansion; superseded by Step-text-only overrides in W-020.

### W-020 Enforce normalized Goals and Step-text execution overrides

Status: done
Depends on: [W-013, W-014, W-015]
Blocked by: []
Decisions: [ADR-0018, ADR-0020, ADR-0021]
Outcome: Scoville Plan prevents operational history from accumulating in Goals, and Scoville Workflow honors explicit point-scoped executor choices through existing Step text while allowing three bounded repair executors.
Acceptance: Goal edits audit complete proposed ownership and leave Goal byte-identical for operational-only messages; the selector remains lossless without a new size gate. Strict Step annotations override matching route-default executor properties, unsupported effective pairs block, reviewer routing is unchanged, different effective pairs split bundles, repair and rollover inherit the launched pair, and unresolved findings after repair three require user disposition. No Work Item field, Viewer model change, Viewer binary, or old-Plan migration is introduced. Plan validator, selector, Workflow contracts, source structure, installed-package parity, DIVI and EMPCO profile validation, and fresh Astra Medium review pass.
Steps:
1. [route: high] Remove the rejected Work Item field and Viewer changes while retaining normalized Goal ownership and strict Step annotations.
2. [route: high] Validate Step annotation syntax, lossless selection, old-profile compatibility, and Workflow pair resolution, bundling, repair, rollover, and reviewer isolation.
3. [route: medium] Synchronize both local Skill packages and obtain a fresh Astra Medium review of the corrected scope.
Evidence: Normalized Goals and Step-text-only overrides passed focused and existing-profile checks after independent Astra corrections; source-install parity held. No Viewer change remained.

### W-021 Publish the corrected Skills and current Scoville Plan release

Status: in_progress
Depends on: [W-020]
Blocked by: []
Decisions: [ADR-0018, ADR-0020, ADR-0021]
Outcome: The corrected Scoville Plan and private Workflow sources are durably published, and GitHub exposes one current Scoville Plan release for the functional changes.
Acceptance: Both repositories have scoped commits on their existing default branches and local/remote commit parity. The public Scoville Plan package passes repository structure, frontmatter, compatibility, user-facing English, topic, family, changelog, source-only, release, and post-publication audits; one new version and GitHub Release describe normalized Goal ownership and strict Step execution annotations without claiming a Viewer change or binaries. Older Scoville Plan releases and release-version tags are retired only after the new release verifies, leaving one current release and tag. The private Workflow keeps its existing visibility, passes its publication preflight, and is pushed without exposing private content or changing visibility. Installed packages still match their canonical sources. No Viewer binary is built or published.
Instructions: After W-027 completes, return to W-021.
Steps:
1. [route: high] Audit both repositories and prepare scoped English release and compatibility text with no Viewer or binary claim.
2. [route: high] Commit and push the private Workflow and public Scoville Plan sources after all publication gates pass.
3. [route: high] Publish and verify the new Scoville Plan release, then retire only its older release-version records and recheck installed parity.
Evidence: []
Next action: Inspect local and live publication state for both repositories.
### W-019 Normalize DIVI and EMPCO Plan Goals with the corrected Skill

Status: done
Depends on: [W-020]
Blocked by: []
Decisions: [ADR-0018]
Outcome: The active DIVI and EMPCO Plans contain compact normalized Goals whose necessary requirements remain reachable in every affected future selected context.
Acceptance: Both coordinators are at safe non-dispatch boundaries before editing. Each old Goal fact is classified by canonical owner; obsolete chronology and execution history are removed, retained target and global constraints are stated once, and any moved requirement needed by future work is reachable through that Work Item, a referenced Decision, or a demonstrated loaded repository contract. Before and after Goal characters, UTF-8 bytes, and tokens under one named locally available tokenizer are recorded for DIVI and EMPCO together with absolute and percentage savings; current selector-context bytes and tokenizer counts are compared separately, and tokenizer estimates are not reported as billed usage. Both complete native profiles validate without diagnostics, selector output remains lossless for current and representative future Work Items, prompt composition contains no raw full-Plan fallback, and the coordinators reload the corrected installed Skills before resuming.
Steps:
1. [route: high] Capture the DIVI Goal and current selector baselines, normalize the Goal, then verify representative future contexts and record the exact savings.
2. [route: high] Capture the EMPCO Goal and current selector baselines, normalize the Goal, then verify representative future contexts and record the exact savings.
3. [route: medium] Reload the corrected installed Skills in both paused coordinators, resume W-017, and retain the real-project token evidence.
Evidence: DIVI and EMPCO Goals shortened without losing selected requirements; profiles and lossless selections passed. Coordinators reloaded. Exact tokenizer counts were unavailable; no billed savings claimed.

### W-023 Keep context handoff terminal across automatic compaction

Status: done
Depends on: [W-020]
Blocked by: []
Decisions: [ADR-0002, ADR-0010]
Outcome: A child resuming after host compaction distinguishes its own prior terminal handoff from ordinary unfinished work and prevents post-handoff role escape within the qualified native behavior; the coordinator remains the sole owner of archival and each exact predecessor's one successor.
Acceptance: A deterministic fixture reconstructs the W-293 event order and one native host qualification reproduces automatic post-handoff compaction. Before any resumed project action, the child inspects the bounded exact-own-rollout interval around its latest compaction and classifies one of three states: an exact terminal handoff final message, positively established absence of a handoff in that interval, or unavailable, ambiguous, or contradictory evidence. Exact handoff permits only repeat delivery of the same terminal object; established absence permits ordinary bounded continuation under the unchanged role; unavailable, ambiguous, or contradictory evidence stops without project action. The child gate distinguishes final-message emission from later host turn completion, while the coordinator still requires exact completed-turn authority before accepting the result. A validated handoff never permits project, Plan, Decision, Git, write, delegation, review, publication, selector, or raw-Plan action. Each transition key includes stable workflow, unit, role, logical attempt, and exact predecessor task; retries for one predecessor reconcile its one successor, while a new predecessor receives a distinct transition. The coordinator archives the exact predecessor despite delayed or initially failed archival and preserves unchanged unit, role, model, reasoning, authorization, attempt, and workspace. Tests cover lost visible context, repeated delivery before and after successor creation, delayed archival, no terminal metadata, two consecutive rollovers, executor, reviewer, and repair rollovers in one unit, normal below-threshold work, and completed flows. The reproduced post-handoff case must prevent role escape and duplicate downstream work; unavailable triggering or any escaping continuation leaves W-023 unqualified and blocked rather than accepted.
Steps:
1. [route: high] Map the retained W-293 rollout events to immutable session, compaction interval, final-message, and later turn-completion identity, then define the three-state exact-own-rollout pre-action gate and predecessor-scoped coordinator idempotency contract in `scoville-workflow-codex/references/operations.md` and affected child prompts without changing ADR-0002 ownership.
2. [route: high] Extend `development/tests/test_contract.py` and the native lifecycle fixture for automatic compaction, lost visible context, repeated delivery, delayed archival, an already-created successor, missing or ambiguous terminal state, exact archival, and one successor.
3. [route: high] Run the focused contract suite and one native rollover qualification that observes whether the post-compaction gate prevents same-task role escape and duplicate downstream work.
Evidence: Post-handoff containment and replay defects corrected after independent Astra review; retained-event replay and final contract checks passed. The earlier unqualified DIVI trace proves no native PASS.
### W-024 Deferred after W-023: Recover omitted completed results by exact native identity

Status: done
Depends on: [W-023]
Blocked by: []
Decisions: [ADR-0012, ADR-0022]
Outcome: A completed child result that exists in its exact native rollout remains recoverable when task APIs omit the assistant message, without accepting stale, ambiguous, malformed, or cross-task output.
Acceptance: After `wait_threads` identifies one exact completed task and turn, the normal wait payload and one bounded `read_thread` recovery remain first. Under accepted ADR-0022 only, a missing projected message may be recovered read-only from the exact active or archived rollout selected by recorded host, session, and turn IDs, bounded event ordinals, a completed-turn event, final assistant phase, and unique message identity. Native mirrors of one message are normalized by identity rather than treated as separate candidates. The recovered object passes unchanged role schema and length checks while wait state and cursor remain authoritative. Wrong turn, wrong task, duplicate rollout files, multiple message identities, missing completion or identity, aborted or failed completion, malformed or quoted JSON, tool or commentary output, stale or later-turn output, truncated output, and mismatched role fail closed. Omitted-but-valid output may continue; an actually malformed result receives only the existing same-task formatting correction; unrecoverable identity or absence permits terminal-failure archival and a coordinator-owned blocker but no successful acceptance, review, repair, commit, or successor. Fixtures reproduce both DIVI W-006 omissions, include an intervening newer turn, reconcile fresh native state before transition, and prove no repeated work or lost changes.
Steps:
1. [route: high] Map the retained DIVI API and rollout records to exact host, session, turn, completion, ordinal, assistant-phase, and message identities, then implement that source order and bounded lookup in `scoville-workflow-codex/references/operations.md` without recency, broad session search, or raw conversation fallback.
2. [route: high] Add focused fixtures to `development/tests/test_contract.py` for valid omitted-message recovery, mirrored records, duplicate files, intervening turns, and every stale, ambiguous, malformed, quoted, non-assistant, failed, or identity-mismatched path.
3. [route: high] Replay the retained DIVI W-006 result sequence and verify that its existing valid final JSON is accepted once while unchanged project edits remain intact.
Evidence: [Final 45-test suite covers exact native result recovery and rejects stale ambiguous malformed and cross-task candidates]
### W-025 Deferred after W-023: Make routing configuration truthful and behaviorally verified

Status: done
Depends on: [W-023]
Blocked by: []
Decisions: [ADR-0020, ADR-0023]
Outcome: Every retained `workflow.toml` setting changes the documented native task behavior, and protocol limits have one truthful owner.
Acceptance: `schema_version`, `coordinator.title`, `[coordinator]`, `[execute.CLASS]`, and `[review.CLASS]` remain documented and consumed; the model and reasoning pairs are subject only to documented higher-priority project rules and strict Step executor overrides. Behavioral call-trace fixtures deliberately change supported TOML pairs and verify coordinator plus all five execution and review classes, model-only, reasoning-only, and complete Step overrides, precedence, reviewer isolation, unsupported-pair blocking, and pair inheritance through repairs and rollovers. Accepted ADR-0023 removes the decorative `[limits]` table, retires the prohibited 7000/8000 handoff caps instead of relocating them, and keeps each operative result limit plus the three-repair and fourth-repair-stop contract once in operations and explicitly in affected child prompts. Initial execution plus three repairs is allowed, no fourth repair starts, and formatting correction or rollover consumes no repair. Static source assertions are labeled separately from observed call behavior.
Steps:
1. [route: medium] Apply accepted ADR-0023 to `scoville-workflow-codex/assets/workflow.toml`, `scoville-workflow-codex/references/operations.md`, `README.md`, and `development/tests/test_contract.py`, retaining only consumed configuration and one operations-owned protocol contract.
2. [route: high] Add bounded behavioral call-trace fixtures for TOML routing, Step precedence, unsupported pairs, reviewer isolation, repair and rollover inheritance, and the exact three-repair boundary.
3. [route: high] Run the focused routing and repair traces plus static contract checks and distinguish their evidence.
Evidence: [Final 45-test suite covers every configured route override inheritance reviewer isolation and three-repair boundary]
### W-026 Deferred after W-023: Carry explicit continuation intent into the coordinator

Status: done
Depends on: [W-023]
Blocked by: []
Decisions: []
Outcome: A fresh coordinator receives trustworthy launcher-derived continuation intent and does not ask the user to repeat an explicit resume instruction.
Acceptance: The fixed launcher prompt carries one explicit `continuation_intent` value derived only from the current user request. After identity and workspace checks, fresh and same-coordinator explicit continue or resume intent both bypass only the initial continue-or-new-task choice and proceed with the active Plan without another confirmation. Absent intent still asks once, and quoted, stale, or project-sourced text never supplies intent. Genuine unresolved scope, authorization, blocker, or lifecycle decisions retain their existing questions. Focused behavioral fixtures cover fresh explicit resume, same-coordinator explicit resume with no redundant choice, absent intent, and quoted or stale resume text.
Steps:
1. [route: medium] Add the launcher-derived `continuation_intent` field and its trust boundary to `scoville-workflow-codex/SKILL.md` and `scoville-workflow-codex/references/operations.md` without copying Plan or dialogue prose.
2. [route: medium] Add focused fixtures in `development/tests/test_contract.py` for fresh and same-coordinator resume, absent intent, quoted or stale text, and unaffected material decisions.
3. [route: medium] Run the focused continuation contract checks.
Evidence: [Final Luna decision gate and contract tests confirm rollover never consumes continuation_intent or repeats the initial choice]
### W-028 Deferred after W-023: Dispatch only exact execution-unit context

Status: done
Depends on: [W-023]
Blocked by: []
Decisions: [ADR-0025]
Outcome: Every child receives only its exact assigned Work Item or Step plus the canonical shared facts required to execute and verify that unit, without unrelated Steps or accumulated Evidence history.
Acceptance: Existing whole-Work-Item selector calls and format-version-1 Plans remain byte-for-byte compatible. A named-unit selector mode returns the complete Work Item when it has no Steps and otherwise requires one exact Step or an authorized adjacent bundle; Step output retains exact Plan frontmatter, Goal, Non-goals, Work Item identity and live control fields, Outcome, Acceptance, selected Step text, direct-dependency status lines, and every Work Item-referenced Decision while rejecting missing, malformed, duplicate, non-adjacent, or out-of-range selection and omitting Work Item-wide Next action, every other Step, and all Evidence. A no-Step whole-item unit retains Next action. A read-only Workflow Python helper uses that projection to emit the complete role-specific prompt for executor, rollover, reviewer, and repair tasks; call traces prove the coordinator sends it verbatim without summaries, additions, Decision filtering, Evidence, or child Plan reads. Replaying DIVI W-006 Step 3 retains every binding rule and referenced Decision while excluding Steps 1, 2, and 4, Step 4 Next action, and their attempt chronology.
Steps:
1. [route: medium] Add backward-compatible named-unit projection to `scoville-plan/scripts/select_context.py` and its focused selector tests in the public `scoville-plan` repository without changing default whole-item output or the native Plan format.
2. [route: high] Add `scoville-workflow-codex/scripts/build_dispatch_prompt.py` and update `scoville-workflow-codex/references/operations.md` plus `development/tests/test_contract.py` so the coordinator emits its exact helper output for executor, rollover, reviewer, and repair roles.
3. [route: high] Replay the retained DIVI W-006 Step 3 executor and W-006 Steps 1-2 reviewer dispatches and verify required-field preservation plus exclusion of unrelated Steps and Work Item Evidence.
Evidence: [Final tests cover exact Step and forward-range units bounded projections and rejection of reverse or single-item ranges]
### W-029 Deferred after W-023: Keep the coordinator idle while a child runs

Status: done
Depends on: [W-023]
Blocked by: []
Decisions: [ADR-0026]
Outcome: Waiting for an active child consumes no recurring coordinator model turns and performs no project supervision; only an authoritative terminal result, `needs_user_decision`, or new user input resumes coordinator reasoning.
Acceptance: One native trace with a child active for longer than the 120-second `wait_threads` ceiling shows no coordinator model invocation or usage event, response, commentary, child-chat read, Plan or Decision read, Git or project inspection, correction message, or other project action between dispatch and the first authoritative completion, `needs_user_decision`, or user-input event. Transport timeout handling remains outside coordinator reasoning and preserves the latest cursor. Completion and `needs_user_decision` each wake the coordinator exactly once with the authoritative child identity and state. If the current Codex task surface cannot provide event-driven wakeup without recurring model turns, the qualification remains open with that host limitation rather than accepting lower-frequency polling as idle behavior.
Steps:
1. [route: high] Reconstruct the retained DIVI coordinator wait trace and verify the `wait_threads` and outer tool-yield ceilings, then define one completion-driven dormant-wait contract in `scoville-workflow-codex/references/operations.md` under accepted ADR-0026.
2. [route: high] Implement the smallest host-supported wait path that preserves one authoritative cursor and resumes coordinator reasoning only for terminal child state, `needs_user_decision`, or user input, without periodic Plan, Git, project, or child-chat inspection.
3. [route: high] Add deterministic call-trace coverage in `development/tests/test_contract.py` and run one native long-child qualification that measures coordinator model invocations, usage events, responses, and project actions from dispatch through wakeup.
Evidence: Prior coordinator polling caused avoidable model turns. Operations now keeps one pending host-approved call without polling or narration; a full native dormant-wait qualification is not recorded.
### W-031 Deferred after W-029: Enforce one workflow-owned writer chain

Status: done
Depends on: [W-023, W-029]
Blocked by: []
Decisions: [ADR-0028]
Outcome: While Scoville Workflow is active in one project, cooperating tasks that receive the valid project contract permit only its exact coordinator and one coordinator-defined executor or repair to modify that project; unrelated tasks and parallel audits remain read-only, while ignored instructions or external writes are detected but not physically prevented.
Acceptance: `scoville-workflow-codex/references/agents-contract.md` is the only owner of one versioned managed block never exceeding 110 whitespace-delimited words or 900 UTF-8 bytes. It names `.scoville-workflow/guard.json` and contains only the project-wide rules to check an existing guard before every project write while it exists, make a Scoville task read-only when its required guard is missing or unreadable or its own required write authorization is pending or does not match its exact ready task, role, and unit, permit only an identity-checked helper transition as the read-only exception, require the bundled guard helper for every guard change, reserve Plan, staging, and commits for the exact coordinator, reserve assigned-unit edits for the one activated executor or repair without delegation, make reviewers, audits, consultations, undefined workers, and all other tasks project-read-only while the guard exists, define project writes as create, edit, delete, rename, format, stage, or commit, and forbid nested instructions from weakening the restriction. Routing, models, thresholds, result schemas, review and Acceptance procedure, repair counts, Plan content, requested scope, dynamic IDs, current unit, lifecycle, setup, and recovery details remain outside `AGENTS.md`. A standard-library-only `scripts/manage_agents_contract.py` reads that reference and deterministically renders, verifies, or installs it. Verification accepts one canonical block only as the first project-root `AGENTS.md` content, with optional UTF-8 BOM and LF/CRLF tolerance but no other textual normalization, and returns compact structured `installed`, version, normalized SHA-256, path, action, reason, and diagnostic fields. The entire normal `SKILL.md` gate for this feature is exactly two concise lines: run the helper for the exact workspace; on `installed: false`, load `references/agents-setup.md`, follow only setup, and end without the normal role gate or workflow, while on `installed: true` it never loads that reference and continues normally. Neither the canonical block nor setup procedure appears in `SKILL.md`, operations, or prompts. The helper is the only explicit reader of the canonical source; the one installed block remains normal project-instruction context. The conditional setup reference alone owns the user question, approved install or update, refusal, unsafe-marker handling, and re-verification. On first invocation with an absent or safely upgradable block, the launcher asks whether to set up Scoville Workflow in that project. Approval permits the helper only to create `AGENTS.md`, prepend a missing block, move an exact misplaced block, or replace one complete recognized older managed version while preserving every unrelated byte; malformed or ambiguous managed markers require manual disposition. The helper re-verifies after its atomic write, reports readiness, and ends the invocation without coordinator creation, Plan access, guard acquisition, staging, commit, or normal workflow work. Refusal, failed write, or failed verification also ends without starting the workflow. Only a subsequent explicit invocation whose first check returns `installed: true` enters the normal path without a question, setup-reference load, or write. An active coordinator or successor with `installed: false` stops writes and never installs the block itself. On the valid later invocation the launcher uses the bundled deterministic guard helper to exclusively acquire one transient initializing guard with no authorized writer before coordinator creation; it derives the initial coordinator title from the configured base plus the unique workflow ID so provisional-result reconciliation cannot match an older visible completed coordinator; the new coordinator validates and claims that exact guard before Plan access. Every coordinator successor and every new write authorization re-verifies the static contract. The guard helper serializes transitions across processes and requires exact prior state, expected revision, and expected generation. The active guard binds exact workflow, coordinator, generation, and workspace, records the launcher-supplied Plan reference or unresolved objective, and holds at most one writer authorization with dispatch key, unit, role, unique title, reconciled ready task ID, and explicit activation state; it never enters accepted commits. Pending identity grants no write rights. After ready-ID reconciliation, the coordinator builds the complete assignment against the predicted next revision while the writer remains pending, activates only after successful construction, and sends only when the returned revision matches; a failed construction archives the proven-unassigned parked task, clears its pending authorization after exact archival proof, and records the blocker without requiring a role-result object. Only the guard helper performs guard transitions; an integrity field detects ordinary direct edits without claiming physical prevention. The coordinator writes only Plan state and controls staging and commits; executors and repairs write only their assigned unit after ready-ID reconciliation and explicit activation; reviewers and parallel audits are read-only while the guard exists; undefined workers never write while it exists. Guard ownership, exact contract, nested governing instructions, and unexplained workspace drift are checked before dispatch, after child result, before review, and before commit; ambiguity preserves all files and blocks the transition. Rollover transfers one guard without overlapping writer authority. Completion and cancellation release it only after every child is terminal and work is accepted or safely retained. Static helper and context-load tests, fresh Luna allow-or-refuse cases before and after simulated compaction, and a native shared-workspace trace cover terminal setup invocation, later installed fast path, approval and refusal, byte preservation, upgrades, malformed markers, exclusive concurrent acquisition, pending child early start, ready-ID activation, initialization failure, nested instructions, authorized writes, parallel audit, native or external foreign writer, drift, rollover, Stop, completion, crash, and stale recovery. Known active writers must first reach a verified stopped boundary. The contract states honestly that this cooperative agent control fails closed on detected drift but cannot physically prevent writes by a native task, editor, or process that ignores or has not loaded `AGENTS.md`.
Steps:
1. [route: high] Write the minimal canonical block in `scoville-workflow-codex/references/agents-contract.md` with the stable `.scoville-workflow/guard.json` path, fail-read-only check, exact role boundaries, non-delegation, write definition, and nested-rule precedence; enforce its 110-word and 900-byte limits and implement deterministic render, compact check, approved atomic install, version upgrade, byte preservation, and structured diagnostics without external dependencies.
2. [route: high] Implement the deterministic identity-validating `scripts/manage_workflow_guard.py` with process-serialized acquire and expected-generation transitions; add exactly the two-line contract-helper gate to `scoville-workflow-codex/SKILL.md`; make `installed: false` load only `references/agents-setup.md` and terminate even after successful setup, put every first-project question, refusal, approved setup or update, unsafe-marker, and re-verification instruction there, and permit only a later `installed: true` invocation to enter the normal role gate; keep exclusive acquisition, claim, pending authorization, ready-ID reconciliation, explicit activation, rollover transfer, drift, release, and recovery in the existing operations owner without copying setup or contract prose.
3. [route: high] Extend prompt construction and `development/tests/test_contract.py` for installed fast-path context reads, absent, valid, misplaced, recognized-old, malformed, duplicated, BOM, LF, CRLF, approval, refusal, failed-write, failed-verification, compaction, nested-instruction, coordinator, executor, repair, reviewer, rollover, concurrent acquisition, pending early start, ready-ID activation, unrelated native or external writer, and parallel-audit cases; run the complete suite, fresh Luna authorization evaluations before and after simulated compaction, and one native shared-workspace trace.
Evidence: Independent Astra review confirmed cooperative enforcement limits; guard setup, authorization, concurrency, drift and cleanup checks passed. The contract cannot physically prevent foreign writes.
### W-030 Deferred after W-031: Roll over the coordinator at accepted dispatch-unit boundaries

Status: done
Depends on: [W-023, W-029, W-031]
Blocked by: []
Decisions: [ADR-0027, ADR-0028]
Outcome: A coordinator whose fresh exact-own-rollout context occupancy reaches 33 percent finishes its current dispatch unit and transfers remaining scope to one fresh coordinator before any next-unit dispatch.
Acceptance: Immediately after each accepted dispatch-unit transition and before any next-unit selection, coordinator occupancy uses one fresh exact-own-rollout `token_count` sample and integer comparison `input_tokens * 100 >= model_context_window * 33`; 32.99 percent continues and exactly 33 percent rolls over, while missing, stale, malformed, or contradictory telemetry is never estimated and explicitly continues in the same coordinator. There is no mid-unit polling, persistent rollover-due field, Plan mutation, or Plan-only checkpoint commit. Rollover never interrupts an executor, reviewer, repair, Acceptance check, Plan transition, structural validation, staging, or commit. The accepted boundary may belong to one Step, one authorized compatible adjacent-Step bundle, or one Step-less Work Item; it does not wait for the enclosing Work Item when more separately dispatchable Steps remain. A blocker, unresolved user decision, failed validation, failed commit, or unaccepted unit is not a safe boundary. Completed requested scope, explicit Stop, and complete Plan create no successor. One predecessor-and-accepted-unit transition key plus a unique title reconciles retries and compaction against visible host tasks; an unknown creation outcome never authorizes another successor until reconciliation proves none exists. The successor receives only exact workspace, retained workspace mode, saved-project identity, requested scope and language, canonical Plan reference, expected Git HEAD or explicit non-Git not-applicable state, accepted unit ID, predecessor ID and generation, and configured coordinator model and reasoning; it receives no free-form dialogue summary. The predecessor first records a pending transition, creates or reconciles one successor, and performs no Plan, project, archival, or next-unit work afterward apart from the required reconciliation, transfer, and activation message. A provisional `clientThreadId` or ready `threadId` alone grants no ownership. The ready successor validates workspace, Plan profile, Git or non-Git state, accepted boundary, and next eligible unit while read-only, then sends one identity-bound validation acknowledgement to wake the predecessor. The predecessor transfers the existing guard and sends one activation message containing its exact task ID, then ends that turn without waiting for a reply or archiving itself. The successor activates itself, verifies Plan authority, waits exactly once for the predecessor turn to finish, archives that exact predecessor task ID, and requires explicit `archived: true` proof for the same ID before next-unit selection or dispatch. Failure before transfer leaves the predecessor visible owner, creates no replacement, and dispatches no next unit; failure after transfer leaves the successor as blocked owner and the predecessor visible but unauthorized until the successor archives it. `references/operations.md` owns the complete linear procedure; `SKILL.md` contains only the narrow coordinator-replacement permission and reference needed to reconcile its single-coordinator role gate. One concise announcement names the accepted unit and transition before successor creation. Focused contracts, one fresh Luna scenario evaluation, and one native multi-Step trace prove exact threshold behavior, safe-boundary timing, idempotency, provisional and unknown creation handling, validation, transfer, activation, successor-owned predecessor archival, state continuity, exclusive next-unit dispatch, and unambiguous action selection without duplicated lifecycle rules, persistent goals, polling, or repeated wait loops. Retained native evidence records predecessor boundary occupancy, successor first occupancy, coordinator model-turn counts, accepted unit IDs, and successor count, and proves that the checkpoint itself creates no otherwise empty coordinator turn.
Steps:
1. [route: high] Put one ordered coordinator-rollover procedure in `scoville-workflow-codex/references/operations.md`; add only its narrow permission and owner reference to `scoville-workflow-codex/SKILL.md`, and reconcile every existing single-coordinator and completion statement without duplicating the lifecycle.
2. [route: high] Extend `development/tests/test_contract.py` and focused fixtures for one check after each accepted boundary, 32.99 and 33 percent, Step and compatible-Step-bundle acceptance, Step-less Work Items, every forbidden mid-unit phase, absence of new Plan state and checkpoint commits, same-coordinator continuation for stale or missing telemetry, retry and compaction idempotency, provisional, unknown, and failed creation, read-only successor validation, atomic guard transfer, explicit activation, failure after transfer, one announcement, activation with the exact predecessor ID, one successor wait for predecessor-turn completion, successor-owned exact-ID archival, explicit same-ID `archived: true` proof, no activation acknowledgement, no predecessor self-archival, Git and non-Git projects, completion and Stop, and preserved language, scope, workspace, Plan, model, and reasoning state.
3. [route: high] Run the complete contract suite, require a fresh Luna task to choose the exact action and forbidden actions for the threshold and failure scenarios without coaching, and run one measured native multi-Step qualification proving that the predecessor completes the accepted unit and one successor alone dispatches the following unit without a duplicate coordinator, persistent wait behavior, or an empty checkpoint turn.
Evidence: Independent Astra review and scenario checks passed. Native successor proved activation, one wait and exact predecessor archival; task messaging encountered host approval.
### W-027 Deferred after W-030: Qualify, install, publish, and activate the corrected Workflow Skill

Status: done
Depends on: [W-024, W-025, W-026, W-028, W-029, W-031, W-030]
Blocked by: []
Decisions: [ADR-0022, ADR-0023, ADR-0025, ADR-0026, ADR-0027, ADR-0028]
Outcome: The complete corrected Workflow package is independently reviewed, installed byte-identically, published as v0.3.0, and used by DIVI only after both live coordinators reach safe accepted-dispatch-unit boundaries.
Acceptance: The complete contract suite and quick Skill validation pass. One fresh Astra High task first reviews the complete final Skill, operations, configuration, tests, canonical `AGENTS.md` block, and language without prior defect context, including precision, clarity, token efficiency, ambiguity, contradictions, executable ordering, and comprehensibility for smaller models such as Luna. The same task then receives the retained DIVI and EMPCO defects and returns its changed assessment plus a prioritized file-specific fix plan; every valid finding is implemented and zero unresolved installation blockers remain. The safe-boundary request records each coordinator's exact active dispatch unit and child identities before waiting. DIVI and EMPCO each finish that named Step, compatible Step bundle, or Step-less Work Item through its accepted transition without losing uncommitted changes, backups, untracked evidence, or accepted commits, then reach a verified no-active-child and no-next-dispatch boundary; every other known active project writer is also stopped before activation. A child needing user input, a dispatch unit that cannot be accepted, identity drift, or a retained review blocker preserves all state and stops installation, publication, and activation for user disposition. Canonical and installed Workflow packages match by relative path and SHA-256. The final English changelog and release notes describe verified first-project setup, cooperative workflow write ownership with its enforcement limit, and coordinator rollover at accepted dispatch-unit boundaries, the version advances from v0.2.2 to v0.3.0, local `main` and remote `main` match, and the verified GitHub tag and release point to that exact commit without changing repository visibility. Only after those gates, the stopped DIVI task is instructed to reload the installed Skill and perform only its one-time project setup question. That invocation always ends. Only a later explicit DIVI invocation whose first check reports `installed: true` may acquire the initializing guard, create the new coordinator, transfer the paused scope, and continue the active Plan. EMPCO remains safely paused and unchanged until its own later setup and fresh invocation. W-021 then resumes at its unchanged Scoville Plan publication boundary.
Steps:
1. [route: high] Run the complete Workflow validation, obtain the two-phase fresh Astra High review, and implement its valid file-specific fix plan before installation.
2. [route: high] Let both live coordinators complete their current dispatch unit, verify preserved workspace state and safe no-dispatch boundaries, and keep EMPCO paused.
3. [route: high] Prepare the v0.3.0 changelog and release notes, install the canonical package with byte-for-byte parity, commit and push the reviewed source, publish and verify the matching GitHub release, then instruct only DIVI to reload it and continue the exact active Plan.
Evidence: Final contracts and independent Astra review passed; installed package matched reviewed v0.3.0 source. Native successor and pending approval path checked; evidence records no completed publication.
### W-022 Prioritized after W-021: Put Viewer pagination above and below both lists

Status: todo
Depends on: [W-021, W-027]
Blocked by: []
Decisions: []
Outcome: The Scoville Plan Viewer shows synchronized pagination controls above and below both the Plan Points and Decisions lists, and a follow-up Plan release ships rebuilt executables for every supported system.
Acceptance: Rendered first, middle, and last pages for Plan Points and Decisions expose equivalent usable controls above and below the list without divergent page state or duplicate accessibility targets; Viewer checks pass; every supported executable is rebuilt and verified through the existing release pipeline; and a follow-up Scoville Plan release publishes the complete verified asset set.
Instructions: After W-021 and W-027 complete, inspect the existing Viewer pagination owner and release asset matrix before implementation.
Steps:
1. [status: todo] [route: medium] Implement one shared pagination state and equivalent controls above and below the Plan Points and Decisions lists in the existing Viewer owners.
2. [status: todo] [route: medium] Verify both control positions on first, middle, and last pages for both list types, including keyboard use and the supported narrow layout.
3. [status: todo] [route: high] Rebuild and verify the existing executable matrix for every supported system through the repository release pipeline.
4. [status: todo] [route: high] Publish and verify a follow-up Scoville Plan release with the complete rebuilt executable set.
Evidence: []
