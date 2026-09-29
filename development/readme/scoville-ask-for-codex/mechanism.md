## How it works

- Select advisers with their own model, effort and Codex or Claude CLI route.
- A small helper combines the question, scope and adviser rules into the native start arguments, including project, model and title. Pass those arguments directly and retain each conversation for follow-up. Native chats are pinned by default; Setup can disable this with ask.pin_threads=false.
- Advisers answer in their own chats. The calling chat collects those answers and handles necessary questions in the same adviser chat.
- Return separate reviews or synthesize answers to a general question.
