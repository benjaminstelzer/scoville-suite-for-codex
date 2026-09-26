# Scoville Ask for Codex

The name comes from the Scoville scale, which originally measured chili heat through dilution.
Here, the heat is the useful findings that remain clear when independent opinions are brought together.

Scoville Ask sends your question and relevant evidence to independently
configured advisers, then returns their assessments to the original task.
Use it for a second opinion, a patch review or a comparison of approaches.

## How it works

- Select advisers with their own model, effort and Codex or Claude CLI route.
- Send independent questions and retain each conversation for follow-up.
- Return separate reviews or synthesize answers to a general question.

## What it enforces

- **Independent advice.** Advisers inspect and answer. The calling task owns changes.
- **Traceable answers.** Task IDs, consultation references and scope identify each response. Native chat titles show the model and original task.
- **Visible failures.** Invalid settings, unavailable models and failed consultations are reported without silently replacing the model or route.

Native advisers are instructed to stay read-only. The host provides no separate
write barrier. Claude permits Read, Grep and Glob by default. WebSearch and
WebFetch require `claude.web_tools`. Model communication always needs network access.

## What it costs

- Each adviser adds a model call and waiting time through its configured Codex or Claude account.
- Native advisers add separate chats and cleanup. Codex lacks
  [`close_agent`](https://github.com/openai/codex/issues/36211), and closed
  threads can [remain visible](https://github.com/openai/codex/issues/30903).
- Desktop-created chats may be [missing from Codex Mobile](https://github.com/openai/codex/issues/24464), limiting mobile follow-up.
- You choose the advisers and assess disagreements. More opinions do not guarantee a better answer.

## How it was developed

- Native Codex chats and Claude CLI adapters were checked through functional tests, Luna comprehension cases and independent reviews.
- Development records distinguish requested settings from observed model telemetry, and simulated consultations from live execution.

- Development links: [Source](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-ask-for-codex) | [Tests](https://github.com/benjaminstelzer/scoville-suite-for-codex/tree/main/members/scoville-ask-for-codex/development/tests) | [Notes](https://github.com/benjaminstelzer/scoville-suite-for-codex/blob/main/members/scoville-ask-for-codex/development/README.md)

## Compatibility

**Codex online.** Native advisers require Codex desktop task controls, a
verified calling task and a saved project. All routes require network access
and Python 3.11 or newer. Use a frontier LLM from the Fable, Astra, SOL or Opus
families, version 5.0 or newer.

The native task host checks the requested model and effort when it creates the adviser chat. A rejected request is reported without substituting another model. Native third-party models require a suitable provider connection, such as EasyCLIProxy where configured. The Claude CLI route requires installed, authenticated Claude Code. Opus 5.5 requires version 2.1.280 or newer. See “How to Ask with Claude Code” for setup.

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

`config.default.json` beside the installed `SKILL.md` owns the shipped defaults.
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

Objects merge by field. The adviser list replaces earlier selections. Shipped
defaults are overridden by project settings, then by request overrides. The
installed configuration reference explains inline-field precedence. An
explicit per-call model or effort wins without changing the saved defaults.
Follow-ups retain their original settings unless explicitly changed. For a
custom adviser, supply an ID, route, exact model and effort in `advisers`.
See the installed configuration reference for helper inputs and migration.

### How to Ask with Claude Code

1. Install [Claude Code](https://code.claude.com/docs/en/setup) if needed. Open a new terminal or PowerShell window. The folder does not matter.
2. Run `claude --version`. Opus 5.5 needs **2.1.280 or newer**. For an older version, run `claude update`, then check again. Keep running Claude sessions open.
3. Run `claude auth login` and complete sign-in in your browser. Run `claude auth status` to check that you are signed in.
4. In Codex with this Skill installed, ask: **“Ask Claude to review this change.”** The imported defaults above determine the model and effort. Change the `ask` settings in `.scoville/config.json` or name another model or effort in the request.

If Ask reports an expired OAuth session, repeat step 3 and retry. An old CLI can reject the correct model ID. Repeat step 2 instead of substituting a model.

## Sources

- [Codex App Server and model/list](https://learn.chatgpt.com/docs/app-server#models).
- [Codex Skills](https://learn.chatgpt.com/docs/build-skills).
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference).

## License

MIT. See [LICENSE](LICENSE).
