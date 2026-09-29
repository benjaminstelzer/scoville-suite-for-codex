## Codex limitations

Workflow and native Ask advisers run in separate chats because Codex has no
[`close_agent`](https://github.com/openai/codex/issues/36211). That means
extra sidebar entries that need archiving, and archived chats can
[stay visible](https://github.com/openai/codex/issues/30903) anyway. Chats
created on desktop may also be
[missing from Codex Mobile](https://github.com/openai/codex/issues/24464),
which makes it harder to follow or continue a run from your phone.
