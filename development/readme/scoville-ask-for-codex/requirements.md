## What it enforces

- **Independent advice.** Advisers inspect and answer. The calling task owns changes.
- **Traceable answers.** Task IDs, consultation references and scope identify each response. Native chat titles show the model and original task.
- **Visible failures.** Invalid settings, unavailable models and failed consultations are reported without silently replacing the model or route.

Native advisers are instructed to stay read-only. The host provides no separate
write barrier. Claude permits Read, Grep and Glob by default. WebSearch and
WebFetch require `claude.web_tools`. Model communication always needs network access.
