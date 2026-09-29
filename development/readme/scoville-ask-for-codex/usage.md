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
