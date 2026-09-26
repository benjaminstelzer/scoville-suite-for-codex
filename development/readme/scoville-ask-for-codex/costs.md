## What it costs

- Each adviser adds a separate model call and waiting time. Native tasks use the connected Codex account, and Claude CLI uses its own configured account.
- **Known issue.** Some Codex clients do not expose
  [`close_agent`](https://github.com/openai/codex/issues/36211). Native advisers
  therefore use separate Codex chats that can be archived, adding visible task
  entries and cleanup. Even closed child threads can
  [remain visible](https://github.com/openai/codex/issues/30903).
- **Known issue.** Desktop-created threads can be
  [missing from Codex Mobile](https://github.com/openai/codex/issues/24464).
  Mobile monitoring and follow-up can therefore be unreliable for native advisers.
- You maintain the adviser configuration and review disagreements. More advisers do not guarantee a better answer.
