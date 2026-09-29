## How it works

- Pick advisers, each with its own model, effort and route through Codex or
  the Claude CLI.
- A small helper turns the question, scope and adviser rules into the native
  start arguments, including project, model and title. Those arguments are
  passed on unchanged, and each conversation stays available for follow-up
  questions. Native chats are pinned by default. Setup can turn that off with
  `ask.pin_threads=false`.
- Advisers answer in their own chats. Your chat collects the answers and asks
  any follow-up questions in the same adviser chat. If a native wait times out,
  it keeps waiting and brings the result back without needing another message
  from you.
- You get separate reviews back or, for a general question, one combined
  answer.
