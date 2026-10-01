## Codex limitations

Workflow and native Ask advisers use subagents within the calling chat. They
retain exact handles for messages and follow-ups, without separate sidebar chats.
Host capacity can prevent another agent from starting. An idle agent does not
prove a slot is free, and a run cannot assume that a close tool is available.
If you run several Scoville Workflows in different Codex chats, check the
per-session subagent limit in `~/.codex/config.toml`. For multiple Workflows,
set it to 256 so longer runs have room for their retained agent threads:

```toml
[agents]
max_concurrent_threads_per_session = 256
```

`agents.max_threads` is the legacy alias for this setting. The limit caps open
subagent threads within each session, not the number of agents a Workflow
should launch at once. It does not guarantee available host capacity.

A capacity refusal stops the affected start with its actual diagnostic,
results and continuation state retained. Workflow and Ask do not wake completed
agents for cleanup or retry automatically. Necessary message failures and
identity uncertainty also stop the affected operation.
