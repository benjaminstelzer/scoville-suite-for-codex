# Scoville Ask for Codex

Scoville Ask sends your question and relevant evidence to independently
configured advisers, then returns their assessments to the original task.
Use it for a second opinion, a patch review or a comparison of approaches.

Here, the heat is the useful advice that remains clear when independent opinions are brought together.

## How it works

- Select advisers with their own model, effort and Codex or Claude CLI route.
- Send independent questions and retain each conversation for follow-up.
- Return separate reviews or synthesize answers to a general question.

## What it enforces

- **Independent advice.** Advisers inspect and answer. The calling task owns changes.
- **Traceable answers.** Each response identifies the adviser and question. Codex chat titles show the model and original task.
- **Visible failures.** Invalid settings, unavailable models and failed consultations are reported without silently replacing the model or route.

Native advisers are instructed to stay read-only. The host provides no separate
write barrier. Claude permits Read, Grep and Glob by default. WebSearch and
WebFetch require `claude.web_tools`. Model communication always needs network access.

## What it costs

- Each adviser adds a model call and waiting time through its configured Codex or Claude account.
- Native chat and mobile constraints are summarized in [Codex limitations](https://github.com/benjaminstelzer/scoville-suite-for-codex#codex-limitations).
- You choose the advisers and assess disagreements. More opinions do not guarantee a better answer.

## How it was developed

- Native Codex chats and Claude CLI adapters were checked through functional tests, Luna comprehension cases and independent reviews.

## Compatibility

Adviser chats require Codex desktop and a saved project. Ask must be able to
identify the calling chat to return answers. All advisers require network access
and Python 3.11 or newer.

A current Fable, Astra, SOL or Opus model is recommended. Luna was also used
in testing.

Codex checks whether the requested model and reasoning level are available when it creates the adviser chat. A rejected request is reported without substituting another model. Third-party models need a provider connection configured in Codex. The Claude CLI route requires installed, authenticated Claude Code. Opus 5.5 requires version 2.1.280 or newer. See “How to Ask with Claude Code” for setup.

Install and enable every Skill in the suite. Each applies to its own task scope.
Start Workflow by asking for it explicitly.

## Install

### Install this Skill

Install this Skill as part of the complete suite from
[the suite's own packages](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/packages).
Every member must be installed and enabled. Do not fetch or substitute packages
from individual Skill repositories. If any member is missing or incompatible,
report the incomplete installation rather than claiming the suite is ready.

The host needs permission to write to its Skills directory. See the
[Codex Skills guide](https://learn.chatgpt.com/docs/build-skills)
for host-specific locations.

### Install the complete Scoville suite

Get the complete suite from the
[Scoville Suite monorepo](https://github.com/benjaminstelzer/scoville-suite-for-codex).
Install its released Skill packages, not development templates.

## How to use

Ask naturally, for example:

```text
Use scoville-ask-for-codex to create a separate SOL adviser chat for an independent review of this patch and return its answer here.
```

```text
Ask Fable and Claude independently how they would approach this problem, then return and compare their answers here.
```

### Configure defaults

`config.default.json` beside the installed `SKILL.md` contains the defaults.
Save project choices under `ask` in `.scoville/config.json` at the project root.
Missing values use the shipped defaults. Reading settings creates no file.
Explicit requests override these values for that call without saving them.

The `astra`, `sol`, `claude` and `fable` presets resolve named requests. The
shipped `advisers` list applies when you do not name an adviser. Every preset's
model, effort and route is configurable. Current defaults:

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

Project settings override the bundled defaults field by field. An adviser list
replaces the default list in full. A model or reasoning level named in your
request applies to that call without changing saved settings.
Follow-ups retain their original settings unless explicitly changed. For a
custom adviser, supply an ID, route, exact model and effort in `advisers`.
See the installed configuration reference for helper inputs and migration.

### How to Ask with Claude Code

1. Install [Claude Code](https://code.claude.com/docs/en/setup) if needed. Open a terminal or PowerShell window.
2. Run `claude --version`. Opus 5.5 needs **2.1.280 or newer**. For an older version, run `claude update`, then check again. Keep running Claude sessions open.
3. Run `claude auth login` and complete sign-in in your browser. Run `claude auth status` to check that you are signed in.
4. In Codex with this Skill installed, ask: **“Ask Claude to review this change.”** The defaults above determine the model and reasoning level. Change the `ask` settings in `.scoville/config.json` or name another model or effort in the request.

If Ask reports an expired OAuth session, repeat step 3 and retry. An old CLI can reject the correct model ID. Repeat step 2 instead of substituting a model.



## Sources

- [Codex App Server and model/list](https://learn.chatgpt.com/docs/app-server#models).
- [Codex Skills](https://learn.chatgpt.com/docs/build-skills).
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference).

## License

MIT. See [LICENSE](LICENSE).
