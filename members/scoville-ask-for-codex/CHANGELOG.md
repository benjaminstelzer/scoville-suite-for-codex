# Changelog

## v1.0.4 - 2026-09-28

- Clarify the README presentation and keep the name explanation once per package.

## v1.0.3 - 2026-09-27

- Explain invalid adviser settings and project configuration with concrete correction guidance.

## v1.0.2 - 2026-09-26

- Carry complete adviser instructions and existing reply authorization in mixed consultations, with task IDs separate from host identifiers.
- Preserve explicitly selected adviser presets when defaults name another adviser.
- Require matching sender, reference and reviewed scope before accepting an answer.
- Keep Claude timeout state separate from native return destinations and require explicit authority to resume.

## v1.0.1 - 2026-09-26

- Make separate adviser chats explicit in the Skill invocation so host task rules do not redirect Ask into subagents.
- Carry existing user authorization into native adviser assignments instead of treating the dispatch as permission to reply.
- Report undelivered answers with their destination and retain the complete answer for recovery; respect host-required progress waits.

## v1.0.0 - 2026-09-25

- Combine adviser selection, native tasks and Claude CLI in Scoville Ask for Codex.
- Use S-ASK titles with the uppercase model ID and exact caller title without changing sidebar placement.
- Create native adviser chats directly and collect their answers through native messages. Keep the Claude CLI route unchanged.
