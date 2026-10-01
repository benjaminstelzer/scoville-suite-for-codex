## How it works

- Pick advisers, each with its own model, effort and route through Codex or
  the Claude CLI.
- A helper prepares the question, scope and read-only rules. Selected Codex
  advisers start as independent subagents with fresh context and the configured
  model and effort. Claude uses the CLI.
- Your chat keeps each native agent's handle and collects its complete answer.
  Questions and follow-ups use the same agent. A wait timeout leaves the adviser
  pending, and collection continues while it is working.
- A complete answer ends the native turn. Your chat waits for that completion
  and sends no routine receipt afterward. A capacity refusal leaves that adviser
  pending, with its diagnostic and received answers retained.
- You get separate reviews back or, for a general question, one combined
  answer. Failed starts and missing answers remain visible alongside completed
  results. Ask doesn't replace an adviser when capacity or startup is uncertain.
