## What it enforces

- **Explicit activation.** Start Workflow by asking for it by name.
- **Separate responsibilities.** The coordinator owns Plan updates, assignments and authorized commits. Workers implement. Reviewers inspect without editing.
- **One writing worker.** Tasks share the existing checkout. The Plan records progress and messages carry the next action.
- **Bounded context.** New workers receive the Work Item and assigned Step range. Continuations receive only remaining work, applicable criteria and constraints, completed effects and evidence. They need not reopen the Plan or earlier chats.
- **Configured models.** Risk determines model and effort. Unavailable required pairs are reported without substitution.
- **Independent review.** Project review cadence takes priority. Otherwise unreviewed product-code changes receive an earlier review after a fix to previously completed code or before dependent work or extensive testing. Other required reviews happen at Work Item completion, reusing earlier assessments of unchanged parts. If the same failure survives two corrections, the coordinator reassesses its cause before another attempt.
- **Context handoffs.** Default triggers are at or above 40% for the coordinator after a checked group, accepted Work Item or worker handoff and strictly above 60% for workers and reviewers at natural stopping points. Thresholds are configurable. Missing measurements are not guessed.
- **Retained results.** Save results before archiving a task. Confirm successor takeover before retiring a predecessor. Report archive errors without confirmation loops. Decision requests and the final coordinator remain open.
- **Accepted commits.** When committing is authorized, include accepted changes and Plan updates. Run required hooks and backups.
- **Defined scope.** Follow the active Plan or the user's narrower boundary, preserving stops and open decisions.

See [Native Codex operations](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations.md)
for delivery, permissions and recovery.
