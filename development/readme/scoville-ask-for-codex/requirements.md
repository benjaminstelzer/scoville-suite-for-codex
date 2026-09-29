## What it enforces

- **Independent advice.** Advisers look and answer. Changes stay with the task
  that asked.
- **Traceable answers.** Each response shows which adviser answered which
  question. Codex chat titles show the model and the original task.
- **Visible failures.** Invalid settings, unavailable models and failed
  consultations are reported. Ask never quietly switches to another model or
  route.

Native advisers are told to stay read-only, but the host doesn't enforce that
with a separate write barrier. Claude may use Read, Grep and Glob by default.
WebSearch and WebFetch need `claude.web_tools`. Talking to the model always
needs network access.
