---
name: scoville-ask-for-codex
description: Ask one or more configured advisers for independent read-only advice or reviews from Codex, through fresh Codex subagents or Claude CLI. Use when the user requests an Ask consultation, a second opinion, or a review by specified advisers. Ordinary questions to the current assistant do not trigger a consultation.
compatibility: "Codex desktop online, Python 3.11+ and filesystem access. Native advisers require collaboration agent tools. Claude advisers require authenticated Claude Code CLI; Opus 5.5 requires CLI 2.1.280+."
---

# Scoville Ask for Codex

Collect independent answers in the calling task. A review asks each adviser to
assess the same evidence; a general consultation combines independent answers
into a synthesis. The caller owns any subsequent changes. Advisers never repair
the subject or delegate the consultation.

When writing adviser framing or reporting results, read and apply the
[shared writing rules](references/writing.md). The helpers include those rules
for adviser answers while preserving the literal user question.

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
not an allowlist. Resolve all selected presets in one call and report the
settings for each adviser. Read
[configuration and helper inputs](references/configuration.md) for resolution,
migration or the first helper invocation.

Reuse an already verified Python 3.11+ interpreter. Otherwise check `py -3`
on Windows or `python3` elsewhere; try `python` if needed. Choose it locally,
without asking the user. Use that executable for the `python` examples.
Report a missing runtime only when no suitable installed interpreter is found.

Native spawn_agent validates the requested model and effort on the actual host.
Report a host rejection without substituting another model or route.

An explicit Ask request commissions the full consultation: create the needed
adviser subagents, exchange necessary questions and answers, and return results.
Do not ask for separate agent or message approval or require authorization fields.
Respect explicit user limits and host requirements. Native Ask uses direct
collaboration tools in the calling chat.

## Ask and collect

1. Prepare a self-contained question, expected scope, requirements and raw
   evidence. Include paths and working-tree scope only when relevant. Exclude
   the caller's verdict, intermediate reasoning, previous adviser answers,
   unrelated history and secrets from fresh consultations.
2. Read [native agent operation](references/native.md) for Codex advisers,
   or [Claude operation](references/claude.md) for CLI advisers.
3. For native advisers, build the assignment and call collaboration.spawn_agent
   directly under native operation. Use fresh context and the selected settings.
   For Claude, use the preparation and execution commands in its reference. Start
   selected native advisers before launching Claude processes; independent Claude
   advisers may run concurrently within host limits. Dispatch only selected advisers.
4. Retain each adviser’s handle, settings, reference and scope. Collect complete
   matching answers under its route’s rules. Necessary questions
   and follow-ups use that same handle. Keep partial answers and failures visible;
   do not silently replace an adviser. A returned handle alone is not an answer.
5. Present answers with material evidence and limits. For a consultation,
   synthesize agreement, differences and useful conclusions without inventing
   consensus. No mandatory second exchange round. For reviews, distinguish
   findings from untested concerns and verify findings before authorized fixes.

Retain requested and actually reported model/effort separately; unavailable
telemetry is unknown.

## Follow-up after completion

Retain the answer, evidence, exact native handle or Claude session ID and
settings. Resume only for an explicitly requested follow-up. Native follow-ups
keep the same settings; a requested change needs a fresh adviser as described
in native.md. Claude follow-ups retain settings unless explicitly overridden.
Do not ask whether a completed review should stay open or close it when the user
changes topic.
Claude print-mode exits after its answer; a retained ID is saved history,
not a running agent. Follow the original route and never select the most recent
session implicitly.

All Skills included in this suite must be installed and enabled. Use the
applicable owner without checking sibling availability. Load only instructions
needed for the task. Explicit invocation gates and user exclusions still apply.

Native advisers receive a read-only instruction. Spawning a native agent does
not add a technical write barrier or a separate sandbox. Claude tool restrictions
and opt-in web access are described in references/claude.md.

## Runtime helpers

Use the bundled helpers for their operations. Read their invocation instructions,
not their source, unless diagnosing a failure.
Python and every named helper are required. Missing dependencies or helper
errors stop the affected operation. Do not substitute manual execution.

Helpers: `scripts/ask.py`, `scripts/build_adviser_prompt.py`, `scripts/check_text_size.py`.
