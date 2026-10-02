# Changelog

## v1.3.0 - 2026-10-02

- Prepare Claude questions and follow-ups directly from text files, retaining saved settings and explicit overrides.
- Catch invalid workspaces and adviser settings before starting a consultation, with the bad value and its source in the diagnostic.
- Check native adviser availability through the host. The unused model-catalog helper has been removed.

## v1.2.1 - 2026-10-01

- Accept a complete native adviser final without a separate startup acknowledgement. Keep incomplete results open and route necessary follow-ups to the same exact handle.
- Remove automatic capacity cleanup and retry. Keep completed answers, pending advisers and the actual failure diagnostic.
- Keep Claude consultations available for an explicitly requested follow-up without an automatic closing question.

## v1.2.0 - 2026-10-01

- Use native Codex agents for independent advisers and collect their complete final answers in the caller. Separate sidebar chats are no longer required.
- Retain the same adviser handle for necessary follow-ups. End completed turns without queued routine acknowledgements.
- After a definite capacity refusal with no agent created, allow one bounded cleanup of eligible completed advisers and one unchanged retry. Preserve answers, pending questions and actual failure diagnostics.
- Build directly usable native dispatch arguments and prompts with the packaged helpers. Claude CLI keeps its existing session route.

## v1.1.1 - 2026-09-29

- Keep the calling chat waiting after native wait timeouts so completed reviews are collected without another user message.
- Preserve consultation references separately from reviewed scopes in clarifications and result matching.

## v1.1.0 - 2026-09-29

- Build adviser requests with consistent SC-ASK-MODEL titles and collect native answers in the calling chat.
- Keep follow-up questions in the same native chat or Claude session. The caller asks whether the consultation should remain open and handles closure.
- Configure automatic adviser pinning through Scoville Setup, enabled by default.
- Remove obsolete separate authorization fields from Claude requests.

## v1.0.5 - 2026-09-28

- Name adviser chats SC · ASK · MODEL · Caller title, keeping technical model IDs and follow-up identities unchanged.

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
- Report undelivered answers with their destination and retain the complete answer for recovery. Respect host-required progress waits.

## v1.0.0 - 2026-09-25

- Combine adviser selection, native tasks and Claude CLI in Scoville Ask for Codex.
- Use S-ASK titles with the uppercase model ID and exact caller title without changing sidebar placement.
- Create native adviser chats directly and collect their answers through native messages. Keep the Claude CLI route unchanged.
