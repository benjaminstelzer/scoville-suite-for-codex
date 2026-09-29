---
name: scoville-ask-for-codex
description: Ask one or more configured advisers for independent read-only advice or reviews from Codex, through separate native Codex chats or Claude CLI. Use when the user requests an Ask consultation, a second opinion, or a review by specified advisers. Ordinary questions to the current assistant do not trigger a consultation.
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
display names never change native task titles. An explicitly named adviser
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
Resolve settings once; native create_thread validates the requested model and
effort on the actual host. No model-catalog subprocess is required. Report a
host rejection without substituting another model or route.

An explicit Ask request commissions the full consultation: create the needed
adviser chats, exchange necessary questions and answers, and return the results.
Do not ask for separate chat or message approval or require authorization fields.
Respect explicit user limits and host requirements. Native Ask uses one separate
Codex chat per adviser; do not substitute subagents.

## Ask and collect

1. Prepare a self-contained question, expected scope, requirements and raw
   evidence. Include paths and working-tree scope only when relevant. Exclude
   the caller's verdict, intermediate reasoning, previous adviser answers,
   unrelated history and secrets from fresh consultations.
2. For native advisers, resolve the verified calling task ID, exact current
   title and saved project. Never infer identity from title or recency.
   Read [native task operation](references/native.md) for
   native advisers, or [Claude operation](references/claude.md) for CLI advisers.
3. For native advisers, call create_thread directly with the question and
   adviser role under [native operation](references/native.md). Its title is
   exactly `SC-ASK-<ADVISER ID>: <exact calling task title>`.
   For Claude,
   use the existing prepare/claude route. Invoke each selected adviser once.
4. Retain each native task ID, adviser settings and current question. Follow
   native operation to wait for and collect the answer in that chat. A necessary
   question is answered in the same adviser chat. Accept a complete answer only when task ID, consultation reference
   and reviewed scope or revision match the retained request. A receipt,
   truncated answer or mismatch remains unresolved; use the relevant route's
   recovery rules. For a known native task, that is one targeted native status
   query or `read_thread` call for only the missing answer or state. Continue
   pending native work through the bounded event waits in native operation,
   not repeated status reads. Keep partial answers and failures visible and
   collect remaining answers without automatic replacement. A receipt alone
   is not an answer.
5. Present answers with material evidence and limits. For a consultation,
   synthesize agreement, differences and useful conclusions without inventing
   consensus. No mandatory second exchange round. For reviews, distinguish
   findings from untested concerns and verify findings before authorized fixes.

Retain requested and actually reported model/effort separately; unavailable
telemetry is unknown. Keep adviser handles for follow-ups until review closure below.
Resume exact retained handles with their previous settings unless explicitly
overridden; identify a newly authorized fresh consultation as fresh.

## After a completed review

The calling chat presents the review and asks once whether its review sessions
are still needed. The advisers do not ask this question. Keep the exact native
task/host IDs or Claude session IDs and the pending question in conversation
context; no separate state file is needed. Ask only after the requested review
round is complete, not while an adviser or requested follow-up is still working.

- Yes, or a request using the review session: retain it and handle the follow-up.
- No: close the sessions that are no longer needed.
- The next user message addresses something else without answering: close the
  pending review sessions first, then handle that message. Do not ask again.
- No new user message: leave the question pending; no timer or automatic action.

Apply an explicit choice per adviser when the user distinguishes sessions.
For native sessions, the caller archives the retained review chat through
native operation. For Claude CLI, close the consultation as described in Claude
operation; do not claim native archival. Preserve review results and evidence.
An explicit later request may retain/reopen a session under its route's rules.
This closing rule applies to reviews, not ordinary consultations.

{{ include: family.contract }}

Native advisers receive a read-only instruction. Creating a native task does
not add a technical write barrier or a separate sandbox. Claude tool restrictions
and opt-in web access are described in references/claude.md.

{{ include: helper.policy }}
