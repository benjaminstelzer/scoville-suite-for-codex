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
{{ include: member.defaults }}
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
