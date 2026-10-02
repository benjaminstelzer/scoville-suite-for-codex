## Configuration

The defaults are in `config.default.json` next to the installed `SKILL.md`.
Project choices go under `ask` in `.scoville/config.json` at the project
root. Anything missing falls back to the shipped defaults.
Reading settings creates no file. If you name something explicitly in a
request, it overrides these values for that call only, without saving them.

Use Scoville Setup to inspect or save adviser choices.

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
