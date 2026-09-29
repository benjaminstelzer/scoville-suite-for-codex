# Scoville Ask for Codex

Scoville Ask sends your question and the relevant evidence to advisers you
configure separately, then brings their assessments back to the task you
started from. Use it for a second opinion, a patch review or to compare
approaches.

The heat, in this case, is the useful part of the advice, still clear after
independent opinions have been brought together.

## How it works

- Pick advisers, each with its own model, effort and route through Codex or
  the Claude CLI.
- A small helper turns the question, scope and adviser rules into the native
  start arguments, including project, model and title. Those arguments are
  passed on unchanged, and each conversation stays available for follow-up
  questions. Native chats are pinned by default. Setup can turn that off with
  `ask.pin_threads=false`.
- Advisers answer in their own chats. Your chat collects the answers and asks
  any follow-up questions in the same adviser chat. If a native wait times out,
  it keeps waiting and brings the result back without needing another message
  from you.
- You get separate reviews back or, for a general question, one combined
  answer.

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

## What it costs

- Every adviser means another model call and more waiting, on the Codex or
  Claude account it's configured with.
- Native chat and mobile limits are summarized under
  [Codex limitations](https://github.com/benjaminstelzer/scoville-suite-for-codex#codex-limitations).
- You choose the advisers and weigh up disagreements yourself. More opinions
  don't guarantee a better answer.

## How it was developed

- Native Codex chats and the Claude CLI adapters were checked with functional
  tests, Luna comprehension cases and independent reviews.

- Development links: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-ask-for-codex) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-ask-for-codex/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/members/scoville-ask-for-codex/development/README.md)

## Compatibility

Adviser chats need Codex desktop, a saved project and the native tools to
collect their answers. Every adviser needs network access. Python 3.11 or newer
is required for the helper scripts.

Needs a frontier model from the Fable, Astra, SOL or Opus families, version
5.0 or newer. Luna was also used in testing.

When Codex creates the adviser chat, it checks whether the requested model
and reasoning level are available. If not, Ask reports it and doesn't
substitute another model. Third-party models need a provider connection
configured in Codex. The Claude CLI route needs Claude Code installed and
signed in, and Opus 5.5 needs version 2.1.280 or newer. See "How to Ask with
Claude Code" for setup.

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

### Install the complete Scoville suite

The complete suite is in the
[Scoville Suite monorepo](https://github.com/benjaminstelzer/scoville-suite-for-codex).
Install its released Skill packages, not development templates.

## How to use

Ask naturally, for example:

```text
Use scoville-ask-for-codex to review this patch with SOL.
```

```text
Ask Fable and Claude independently how they would approach this problem, then return and compare their answers here.
```

Asking covers creating the adviser chats and the messages that bring their
answers back. You don't have to approve those steps one by one.

After a review, your chat asks whether you still need the review sessions.
Say yes, or ask a follow-up, and they stay. Say no, or move on to another
topic without answering, and it archives the native review chats. Silence
alone does nothing. Claude CLI consultations are closed for further use, but
the saved Claude history is neither archived nor deleted. The advisers never
ask the closing question themselves.

### Configure defaults

The defaults are in `config.default.json` next to the installed `SKILL.md`.
Project choices go under `ask` in `.scoville/config.json` at the project
root. Anything missing falls back to the shipped defaults.
Reading settings creates no file. If you name something explicitly in a
request, it overrides these values for that call only, without saving them.

The `astra`, `sol`, `claude` and `fable` presets are what a named request
resolves to. If you don't name an adviser, the shipped `advisers` list
applies. Model, effort and route are configurable for every preset. Current
defaults:
```json
{
  "schema_version": 1,
  "pin_threads": true,
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
the adviser list, which replaces the default list completely. A model or
reasoning level you name in a request applies only to that call and doesn't
change saved settings. Follow-ups keep their original settings unless you
change them explicitly. For a custom adviser, add an ID, route, exact model
and effort to `advisers`. The installed configuration reference covers helper
inputs and migration.

### How to Ask with Claude Code

1. Install [Claude Code](https://code.claude.com/docs/en/setup) if needed. Open a terminal or PowerShell window.
2. Run `claude --version`. Opus 5.5 needs **2.1.280 or newer**. For an older version, run `claude update`, then check again. Keep running Claude sessions open.
3. Run `claude auth login` and complete sign-in in your browser. Run `claude auth status` to check that you are signed in.
4. In Codex with this Skill installed, ask: **“Ask Claude to review this change.”** The defaults above determine the model and reasoning level. Change the `ask` settings in `.scoville/config.json` or name another model or effort in the request.

If Ask reports an expired OAuth session, repeat step 3 and try again. An
outdated CLI can reject the correct model ID. In that case, repeat step 2
rather than switching to another model.



## Sources

- [Codex App Server and model/list](https://learn.chatgpt.com/docs/app-server#models).
- [Codex Skills](https://learn.chatgpt.com/docs/build-skills).
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference).

## License

MIT. See [LICENSE](LICENSE).
