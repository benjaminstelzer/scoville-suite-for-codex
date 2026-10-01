# Scoville Ask for Codex

Scoville Ask sends your question and the relevant evidence to advisers you
configure separately, then brings their assessments back to the task you
started from. Use it for a second opinion, a patch review or to compare
approaches.

## How it works

- Pick advisers, each with its own model, effort and route through Codex or
  the Claude CLI.
- A helper prepares the question, scope and read-only rules. Selected Codex
  advisers start as independent subagents with fresh context and the configured
  model and effort. Claude uses the CLI.
- Your chat checks each native agent's startup and collects its complete answer.
  Questions and follow-ups use the same agent. A wait timeout leaves the adviser
  pending, and collection continues while it is working.
- A complete answer ends the native turn. Your chat waits for that completion
  and sends no routine receipt afterward. If a new adviser is definitely refused
  for capacity, Ask may wake its own completed advisers once to consume queued
  messages, then retry the same start once. This doesn't guarantee a free slot.
- You get separate reviews back or, for a general question, one combined
  answer. Failed starts and missing answers remain visible alongside completed
  results. Ask doesn't replace an adviser when capacity or startup is uncertain.

## What it enforces

- **Independent advice.** Advisers look and answer. Changes stay with the task
  that asked.
- **Traceable answers.** Each response shows which adviser answered which
  question. Native results stay tied to the agent handle, reference and scope.
  Requested settings stay separate from model telemetry the host actually reports.
- **Visible failures.** Invalid settings, unavailable models and failed
  consultations are reported. Ask never quietly switches to another model or
  route.

Native advisers are told to stay read-only, but the host doesn't enforce that
with a separate write barrier. Claude may use Read, Grep and Glob by default.
WebSearch and WebFetch need `claude.web_tools`.

## What it costs

- Every adviser means another model call and more waiting, on the Codex or
  Claude account it's configured with.
- Native advisers occupy agent capacity. Ask retains their handles for follow-ups
  and cannot assume idle agents free a slot or that the host offers a close tool.
- You choose the advisers and weigh up disagreements yourself. More opinions
  don't guarantee a better answer.

## How it was developed

- The native route was exercised with real Astra and SOL subagents, a
  clarification and follow-up on the same handle, and a rejected model request.
  An intentionally incomplete reply checked that partial results remain visible.
- Focused helper and package tests cover spawn arguments, configuration and
  legacy settings. Claude CLI checks use simulated process results. These
  checks do not establish agent capacity limits or recovery from every host failure.

- Development links: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-ask-for-codex) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-ask-for-codex/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/members/scoville-ask-for-codex/development/README.md)

## Compatibility

Native advisers need Codex collaboration tools for spawning agents, receiving
their messages and resuming them. Every adviser needs network access.
Python 3.11 or newer is required for the helper scripts.

Needs a frontier model from the Fable, Astra, SOL or Opus families, version
5.0 or newer. The native agent route was checked with Astra and SOL.

The host checks the requested model and effort when starting an agent. Ask
reports rejection without substituting another model. Available agent capacity
can limit a consultation. Completed answers stay available while unstarted or
unresolved advisers are reported separately.

The Claude CLI route needs Claude Code installed and signed in, and Opus 5.5
needs version 2.1.280 or newer. See "How to Ask with Claude Code" for setup.

Install and enable every Skill in the suite. Each applies to its own task scope.
Start Workflow by asking for it explicitly.

## Install

### Install this Skill

Install this Skill as part of the complete suite from
[the suite's own packages](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/packages).
Every member must be installed and enabled. Do not fetch or substitute packages
from individual Skill repositories. If any member is missing or incompatible,
report the incomplete installation rather than claiming the suite is ready.

The host needs permission to write to its Skills directory. The
[Codex Skills guide](https://learn.chatgpt.com/docs/build-skills) lists where to install it.



## How to use

Ask naturally, for example:

```text
Use scoville-ask-for-codex to review this patch with SOL.
```

```text
Ask Fable and Claude independently how they would approach this problem, then return and compare their answers here.
```

Asking covers starting the selected advisers and exchanging the questions and
answers needed for the consultation. You don't approve those steps one by one.
Native advisers use subagents, and follow-ups keep their handles.

After a Claude CLI review, your chat asks whether you still need those review
sessions. Say yes, or ask a follow-up, and they stay. Say no, or move on to
another topic without answering, and it closes them for further use. Silence
alone does nothing. Saved Claude history is neither archived nor deleted.
Native advisers need no closing question or chat archival.

### How to Ask with Claude Code

1. Install [Claude Code](https://code.claude.com/docs/en/setup) if needed. Open a terminal or PowerShell window.
2. Run `claude --version`. Opus 5.5 needs **2.1.280 or newer**. For an older version, run `claude update`, then check again. Keep running Claude sessions open.
3. Run `claude auth login` and complete sign-in in your browser. Run `claude auth status` to check that you are signed in.
4. In Codex with this Skill installed, ask: **“Ask Claude to review this change.”** The configured defaults determine the model and reasoning level. Change the `ask` settings in `.scoville/config.json` or name another model or effort in the request.

If Ask reports an expired OAuth session, repeat step 3 and try again. An
outdated CLI can reject the correct model ID. In that case, repeat step 2
rather than switching to another model.

### Configure defaults

The defaults are in `config.default.json` next to the installed `SKILL.md`.
Project choices go under `ask` in `.scoville/config.json` at the project
root. Anything missing falls back to the shipped defaults.
Reading settings creates no file. If you name something explicitly in a
request, it overrides these values for that call only, without saving them.

Native advisers have no separate sidebar chats to title, pin or archive.
Existing `ask.pin_threads` values remain readable but have no effect. Scoville
Setup explains this obsolete setting and rejects new changes to it.

The `astra`, `sol`, `claude` and `fable` presets are what a named request
resolves to. If you don't name an adviser, the shipped `advisers` list
applies. Model, effort and route are configurable for every preset. Current
defaults:
```json
{
  "schema_version": 1,
  "advisers": ["astra"],
  "presets": {
    "astra": {"route": "native", "model": "gpt-6-astra", "effort": "high"},
    "sol": {"route": "native", "model": "gpt-5.6-sol", "effort": "high"},
    "claude": {"route": "claude-cli", "model": "claude-opus-5-5", "effort": "high"},
    "fable": {"route": "claude-cli", "model": "claude-fable-5-1", "effort": "medium"}
  },
  "claude": {
    "max_budget_usd": 10,
    "session_persistence": true,
    "customizations": false,
    "timeout_seconds": 3600,
    "web_tools": false
  }
}
```

For example, this `.scoville/config.json` selects SOL and Fable by default and
changes only SOL's effort:

```json
{
  "ask": {
    "advisers": ["sol", "fable"],
    "presets": {"sol": {"effort": "medium"}}
  }
}
```

Project settings override the bundled defaults one field at a time, except
the adviser list, which replaces the default list completely. Native follow-ups
keep the same agent and settings. Changing model or effort requires a fresh
adviser. For a custom adviser, add an ID, route, exact model and effort to
`advisers`. The installed configuration reference covers helper
inputs and migration.

## Sources

- [Codex App Server and model/list](https://learn.chatgpt.com/docs/app-server#models).
- [Codex Skills](https://learn.chatgpt.com/docs/build-skills).
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference).

## License

MIT. See [LICENSE](LICENSE).
