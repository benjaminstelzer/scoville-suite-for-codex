# Scoville Ask for Codex

Scoville Ask gets independent advice from the advisers you choose and returns
it to your current task. Use it for a patch review, a second opinion or a
comparison of approaches. Each adviser gets the question and relevant evidence
with fresh context.

Scoville measures chili heat. Ask adds a little heat to your assumptions.
Unanimous agreement is pleasant, but finding the missed problem is more useful.

## How it works

- Select configured advisers using native Codex agents or the Claude CLI.
- Give each the same question, scope and relevant evidence independently.
- Collect separate reviews or combine answers to a general question. Follow-up
  questions continue with the same adviser and context.
- Show missing answers and failed starts alongside completed results.

## What it enforces

- **Independent advice.** Advisers assess the work. Changes remain with the
  calling task. Native read-only behavior is instructed, not sandbox-enforced.
- **Traceable answers.** Results stay attached to their adviser and question.
- **Explicit failures.** Unavailable models, invalid settings and failed calls
  are reported. Ask does not quietly choose a different adviser.

Claude uses read tools by default. Web access requires `claude.web_tools`.

## What it costs

- Each adviser adds model usage, waiting and agent capacity. Use extra opinions for decisions worth checking. You still have to weigh disagreements.

## How it was developed

Real consultations shaped independent advice and follow-ups. Configuration
and delivery tests cover the helpers, while simulated host results cannot
establish reliability across every live Codex or Claude failure.

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

Ask handles the consultation and necessary follow-ups without asking you to
approve each exchange. Request a follow-up when you need one. Native agents
keep their context, and Claude can resume its saved session.

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

Use Scoville Setup to inspect or save adviser choices. A model or effort named
in one request applies to that call without changing saved defaults.

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

- [Codex Skills](https://learn.chatgpt.com/docs/build-skills).
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference).

## License

MIT. See [LICENSE](LICENSE).
