## What it enforces

- **Explicit activation.** Start Workflow by asking for it by name.
- **Separate responsibilities.** The coordinator owns Plan updates, assignments and authorized commits. Workers implement. Reviewers inspect without editing.
- **One active assignment.** Tasks share the existing checkout. The run record retains progress and the next action. Change settings between runs and avoid parallel project edits.
- **Bounded context.** Workers receive the Work Item, assigned Step range and relevant goals, decisions and dependencies. They need not reopen the Plan or earlier chats.
- **Configured models.** Risk determines model and effort. Unavailable required pairs are reported without substitution.
- **Independent review.** Code and critical documentation require a fresh reviewer. Unresolved findings allow up to three repairs before user input.
- **Context handoffs.** Default triggers are at or above 25% for the coordinator after accepted work and strictly above 75% for child roles at natural boundaries. Thresholds are configurable. Missing measurements are not guessed.
- **Retained results.** Save results before archiving a task. Confirm successor takeover before retiring a predecessor. Report archive errors without confirmation loops. Decision requests and the final coordinator remain open.
- **Accepted commits.** Existing commit authority covers accepted changes and accumulated Plan state. Hooks and required backups remain binding.
- **Defined scope.** Follow the active Plan or the user's narrower boundary, preserving stops and open decisions.

See [Native Codex operations](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/packages/scoville-workflow-for-codex/scoville-workflow-for-codex/references/operations.md)
for delivery, permissions and recovery.
