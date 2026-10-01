---
name: scoville-ask-for-codex
description: Ask one or more configured advisers for independent read-only advice or reviews from Codex, through fresh Codex subagents or Claude CLI. Use when the user requests an Ask consultation, a second opinion, or a review by specified advisers. Ordinary questions to the current assistant do not trigger a consultation.
compatibility: "Codex desktop online, Python 3.11+, filesystem access and bundled helpers. Native advisers require collaboration agent tools. Claude advisers require authenticated Claude Code CLI; Opus 5.5 requires CLI 2.1.280+. No manual helper fallback."
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
display names do not identify agent handles. An explicitly named adviser
selects that preset even when the default adviser list contains another
adviser. The default adviser list applies only when no adviser is named; it is
not an allowlist. For multiple advisers, resolve and report each selected
preset separately. Read
[configuration and helper inputs](references/configuration.md) for resolution,
migration or the first helper invocation.

Reuse an already verified Python 3.11+ interpreter. Otherwise check `py -3`
on Windows or `python3` elsewhere; try `python` if needed. Choose it locally,
without asking the user. Use that executable for the `python` examples.
Report a missing runtime only when no suitable installed interpreter is found.

Python 3.11+, the bundled configuration helper and Codex online are required.
Resolve settings once; native spawn_agent validates the requested model and
effort on the actual host. No model-catalog subprocess is required. Report a
host rejection without substituting another model or route.

An explicit Ask request commissions the full consultation: create the needed
adviser subagents, exchange necessary questions and answers, and return results.
Do not ask for separate agent or message approval or require authorization fields.
Respect explicit user limits and host requirements. Native Ask uses direct
collaboration tools in the calling chat.

Native advisers end their turn with the complete answer. Do not acknowledge an
already completed adviser. A definite capacity refusal permits only the bounded
cleanup and unchanged retry under [native operation](references/native.md).

## Ask and collect

1. Prepare a self-contained question, expected scope, requirements and raw
   evidence. Include paths and working-tree scope only when relevant. Exclude
   the caller's verdict, intermediate reasoning, previous adviser answers,
   unrelated history and secrets from fresh consultations.
2. Read [native agent operation](references/native.md) for Codex advisers,
   or [Claude operation](references/claude.md) for CLI advisers.
3. For native advisers, build the assignment and call collaboration.spawn_agent
   directly under native operation. Use fresh context and the selected settings.
   For Claude, use the existing prepare/claude route. Dispatch only selected advisers.
4. Retain each adviser’s handle, settings, reference and scope. Check startup and
   collect complete matching answers under its route’s rules. Necessary questions
   and follow-ups use that same handle. Keep partial answers and failures visible;
   do not silently replace an adviser. A receipt alone is not an answer.
5. Present answers with material evidence and limits. For a consultation,
   synthesize agreement, differences and useful conclusions without inventing
   consensus. No mandatory second exchange round. For reviews, distinguish
   findings from untested concerns and verify findings before authorized fixes.

Retain requested and actually reported model/effort separately; unavailable
telemetry is unknown. Keep adviser handles for follow-ups; Claude review closure follows below.
Resume exact retained handles with their previous settings unless explicitly
overridden; identify a newly authorized fresh consultation as fresh.

## After a completed Claude review

For Claude sessions with continuation available, the calling chat presents the
review and asks once whether those Claude sessions are still needed. The advisers
do not ask this question. Keep the exact Claude session IDs and pending question in conversation
context; no separate state file is needed. Ask only after the requested review
round is complete, not while an adviser or requested follow-up is still working.

- Yes, or a request using the review session: retain it and handle the follow-up.
- No: close the sessions that are no longer needed.
- The next user message addresses something else without answering: close the
  pending review sessions first, then handle that message. Do not ask again.
- No new user message: leave the question pending; no timer or automatic action.

Apply an explicit choice per adviser when the user distinguishes sessions.
Close the Claude consultation as described in Claude operation; do not claim
native archival. Native agent handles remain available under native operation.
Preserve review results and evidence.
An explicit later request may retain/reopen a session under its route's rules.
This closing rule applies to reviews, not ordinary consultations.

{{ include: family.contract }}

Native advisers receive a read-only instruction. Spawning a native agent does
not add a technical write barrier or a separate sandbox. Claude tool restrictions
and opt-in web access are described in references/claude.md.

{{ include: helper.policy }}
