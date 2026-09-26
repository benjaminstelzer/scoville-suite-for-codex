## What it costs

- Worker and reviewer chats, handoffs and Plan updates consume tokens and time.
- Native subagents would be the cleaner option, but Codex lacks
  [`close_agent`](https://github.com/openai/codex/issues/36211).
  Workflow and Ask therefore use separate chats, which add sidebar entries and
  require archiving. Archived chats can still
  [remain visible](https://github.com/openai/codex/issues/30903).
- Desktop-created threads may be [missing from Codex Mobile](https://github.com/openai/codex/issues/24464), limiting mobile monitoring and follow-up.
