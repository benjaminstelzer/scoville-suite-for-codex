## What it costs

- Separate worker and reviewer tasks, context handoffs and Plan updates use additional tokens and time.
- **Known issue.** Some Codex clients do not expose
  [`close_agent`](https://github.com/openai/codex/issues/36211). Worker and
  reviewer roles therefore use separate Codex chats that can be archived,
  adding visible task entries and cleanup. Even closed child threads can
  [remain visible](https://github.com/openai/codex/issues/30903).
- **Known issue.** Desktop-created threads can be
  [missing from Codex Mobile](https://github.com/openai/codex/issues/24464).
  Mobile monitoring and follow-up can therefore be unreliable for these roles.
