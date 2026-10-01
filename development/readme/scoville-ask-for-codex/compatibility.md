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
