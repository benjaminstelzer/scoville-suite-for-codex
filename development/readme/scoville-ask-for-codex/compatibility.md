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
