## How it works

- Pick advisers, each with its own model, effort and route through Codex or
  the Claude CLI.
- A helper prepares the question, scope and read-only rules. Selected Codex
  advisers start as independent subagents with fresh context and the configured
  model and effort. Claude uses the CLI.
- Your chat checks each native agent's startup and collects its complete answer.
  Questions and follow-ups use the same agent. A wait timeout leaves the adviser
  pending, and collection continues while it is working.
- A complete answer ends the native turn. Your chat waits for that completion
  and sends no routine receipt afterward. If a new adviser is definitely refused
  for capacity, Ask may wake its own completed advisers once to consume queued
  messages, then retry the same start once. This doesn't guarantee a free slot.
- You get separate reviews back or, for a general question, one combined
  answer. Failed starts and missing answers remain visible alongside completed
  results. Ask doesn't replace an adviser when capacity or startup is uncertain.
