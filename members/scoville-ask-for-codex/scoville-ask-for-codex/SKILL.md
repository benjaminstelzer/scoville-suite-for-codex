---
name: scoville-ask-for-codex
description: Ask one or more configured advisers for independent read-only advice or reviews from Codex, through native Codex tasks or Claude CLI. Use when the user requests an Ask consultation, a second opinion, or a review by specified advisers. Ordinary questions to the current assistant do not trigger a consultation.
compatibility: "Codex desktop online, Python 3.11+, filesystem access and bundled helpers. Native advisers require task controls, caller identity and a saved project. Claude advisers require authenticated Claude Code CLI; Opus 5.5 requires CLI 2.1.280+. No manual helper fallback."
---

# Scoville Ask for Codex

Collect independent answers in the calling task. A review asks each adviser to
assess the same evidence; a general consultation combines independent answers
into a synthesis. The caller owns any subsequent changes. Advisers never repair
the subject or delegate the consultation.

## Choose the consultation

Infer `review` or `consultation` from the actual question; an explicit mode wins.
“Could this patch lose data?” is a review even without “for review”. If the
intended outcome is ambiguous, clarify before dispatch. Do not ask again when
the request already establishes the mode, advisers or permission.

Resolve settings with `scripts/ask.py`, using unsaved request overrides above
the selected project's `.scoville/config.json` (`ask` section), then
[config.default.json](config.default.json). Select exactly the requested
advisers, routes, models and efforts. Adviser IDs identify results; optional
display names never change native task titles. Read
[configuration and helper inputs](references/configuration.md) for resolution,
migration or the first helper invocation.

Reuse an already verified Python 3.11+ interpreter. Otherwise check `py -3`
on Windows or `python3` elsewhere; try `python` if needed. Choose it locally,
without asking the user. Use that executable for the `python` examples.
Report a missing runtime only when no suitable installed interpreter is found.

Python 3.11+, the bundled configuration helper and Codex online are required.
Resolve settings once; native create_thread validates the requested model and
effort on the actual host. No model-catalog subprocess is required. Report a
host rejection without substituting another model or route.

Native Ask uses a separate Codex chat per adviser, never a subagent. If the
host requires an explicit new-chat request and none was given, name that
specific missing authorization before dispatch. Do not silently change routes.

## Ask and collect

1. Prepare a self-contained question, expected scope, requirements and raw
   evidence. Include paths and working-tree scope only when relevant. Exclude
   the caller's verdict, intermediate reasoning, previous adviser answers,
   unrelated history and secrets from fresh consultations.
2. Resolve the verified calling task ID and its exact current title, plus the
   saved project for native advisers. Never infer identity from title or
   recency. Read [native task operation](references/native.md) for native
   advisers, or [Claude operation](references/claude.md) for CLI advisers.
3. For native advisers, call create_thread directly with the question and
   adviser role under [native operation](references/native.md). For Claude,
   use the existing prepare/claude route. Invoke each selected adviser once.
4. Retain each native task ID, adviser settings and current question. Follow
   native operation's host requirements before ending the caller turn;
   authorized adviser messages
   resume it. Accept each complete answer once, by actual sender and question.
   Keep partial answers and failures visible and collect remaining answers
   without polling or automatic replacement. A receipt alone is not an answer.
5. Present answers with material evidence and limits. For a consultation,
   synthesize agreement, differences and useful conclusions without inventing
   consensus. No mandatory second exchange round. For reviews, distinguish
   findings from untested concerns and verify findings before authorized fixes.

Retain requested and actually reported model/effort separately; unavailable
telemetry is unknown. Keep successful native adviser tasks open for follow-ups.
Resume exact retained handles with their previous settings unless explicitly
overridden; identify a newly authorized fresh consultation as fresh.

{{ include: family.contract }}

Native advisers receive a read-only instruction. Creating a native task does
not add a technical write barrier or a separate sandbox. Claude tool restrictions
and opt-in web access are described in references/claude.md.
