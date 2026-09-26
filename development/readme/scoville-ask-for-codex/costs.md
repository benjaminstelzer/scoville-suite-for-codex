## What it costs

- Each adviser adds a model call and waiting time through its configured Codex or Claude account.
- Native subagents would be the cleaner option, but Codex lacks
  [`close_agent`](https://github.com/openai/codex/issues/36211).
  Ask therefore uses separate chats, which add sidebar entries and
  require archiving. Archived chats can still
  [remain visible](https://github.com/openai/codex/issues/30903).
- Desktop-created chats may be [missing from Codex Mobile](https://github.com/openai/codex/issues/24464), limiting mobile follow-up.
- You choose the advisers and assess disagreements. More opinions do not guarantee a better answer.
