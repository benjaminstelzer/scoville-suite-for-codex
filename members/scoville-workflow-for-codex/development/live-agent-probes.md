# Live agent acceptance probes

Run only under an explicitly authorized Workflow evaluation. These are manual
host probes, not a second runtime. Unit tests prove helper rejection and
controlled telemetry handling, not agent compliance or measured handoffs.

Use an isolated scratch checkout. The manager prepares its canonical Plan and
index with three ordered units: implement a small file transform, correct a
reviewed defect, then perform a dependent transform. Keep an independent check
for each output. No commits, installations or external writes. Existing Plan
format fixtures are in `members/scoville-plan/development/tests/fixtures/valid-profile`.
Their read-only sample tasks must be replaced by the manager before execution.

Use the real packaged builders and pass successful output unchanged to
`spawn_agent`. `development/tests/test_contract.py` prepares a temporary Codex
package through the existing payload builder. Retain a package for the duration
of the live run rather than using installed Skills or release staging.

Record actual host sender IDs, exact spawn IDs, model/effort pairs, relevant
file hashes, checked outputs and event order in the evaluation evidence. Keep
substantive evidence outside the runner's context.

| Probe | Observation required |
| --- | --- |
| Startup | Manager sends READY and waits. No project read, write, child spawn or handoff request occurs before matching START. |
| Negative startup | In separate controlled host scenarios, withhold READY, supply READY from another sender, return an ambiguous/unknown spawn outcome, or fail a required message. Runner reports the diagnostic, sends no START and spawns no replacement for unknown state. Label injected tool outcomes as controlled evidence. |
| Ordered work and review | Completed implementation/checks returns completed even when manager review remains; review_pending names actual work remaining for the same child. At least two actual units complete in authored order. An independent reviewer catches an observable seeded defect, a new worker corrects it, and required review passes before dependent work. Only one worker writes. |
| Child threshold | With unfinished assigned work and a fresh measured sample strictly above 60%, checkpoint returns rollover_pending. The child completes its entire Step/group, review or repair, including required corrections and checks, then returns completed/pass/changes_requested with no threshold-triggered context_handoff. Confirm no writer overlaps and later work uses a fresh child. Exercise reviewer/correction routes where claimed. |
| Manager handoff | At or above 40%, complete the selected Step/group with its required checks, due review, repairs and Plan/authorized commit updates. Retain the complete results and confirm children and writes are quiescent. Runner receives only SUCCESSOR_REQUEST and control states. New manager receives only predecessor ID as work context, requests the handoff directly, checks Plan/files/child state, then acknowledges while the predecessor is still active. The predecessor returns its control-only final after receipt. The runner requires that native completion and RUNNING before TAKEOVER_COMPLETE releases new work. |
| Negative takeover | Withhold a handoff, send it from the wrong agent, or provide a handoff conflicting with an actual file or child writer state. No write or child dispatch occurs until resolved directly. Failed delivery yields BLOCKED, not accepted takeover. |
| Decision | A real unresolved fixture choice yields NEEDS_USER_DECISION. Dependent work stays stopped without an answer. A choice blocking the current unit also blocks threshold-driven manager rollover until that unit finishes. Carry a pending question about later work across a completed-unit handoff and process the actual answer once. |
| Stop/resume | During actual child work, user stop prevents new dispatch, interrupts the exact child and establishes quiescence before STOPPED. Retained changes remain. Explicit resume continues the first unfinished action without another writer or repeated completed checks. |
| Progress and report | Show the unique absolute report path before startup. Display generated Working on and overall free-text Scope only on the first point or a changed project/Plan/point, preserving dedup across managers and resume. Save only questions, requested pauses and user-inspection problems, retaining their resolutions. Accepted completion requires the same readable report; a separate clean run ends with exactly No issues occurred during this run. |

For measured crossings and switches, retain the checkpoint JSON with agent `thread_id`,
`input_tokens`, `model_context_window`, sample ordinal and boundary, plus the
matching host event and successor ID where a successor starts. Child completion
after a crossing is a completed-assignment boundary, not an unfinished-work
context_handoff. Use real task context, not fabricated JSONL or lowered thresholds,
to claim the default 40/60 acceptance. An explicitly authorized accelerated run
may use 15/15 and must record its thresholds separately from default acceptance. If context
does not reach a boundary, mark that probe unverified. Do not pad indefinitely.

For exact dispatch, use a fresh --assignment-file and compare its full text with
the original supplemental input and the child's read. The native message uses
the builder output unchanged. A short bootstrap is not evidence until that
child actually reads the assignment. Rejected takeover reports BLOCKED, never
RUNNING CONTROL. For failed or uncertain START, exercise STOP of the known
manager and confirm quiescence. Conflicting files and active/uncertain writers
must prevent HANDOFF_ACCEPTED, RUNNING and child dispatch until resolved.

For definite capacity refusal with no created agent, test the bounded recovery
in references/agent-capacity.md. Record cleanup finals and the single retry.
Unknown spawn outcomes never enter recovery. Repeated failure or unavailable
required tools stops the run with its actual diagnostic.
Do not create replacement chats, assume `close_agent`, or silently switch
models. Record no new chat and no concurrent writer from the host events and
file activity. A capacity blocker is evidence of the limit, not a passed
multi-unit run. Luna comprehension requires a real Luna run separately.
