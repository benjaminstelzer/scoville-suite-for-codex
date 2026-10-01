## How it was developed

- The native route was exercised with real Astra and SOL subagents, a
  clarification and follow-up on the same handle, and a rejected model request.
  An intentionally incomplete reply checked that partial results remain visible.
- Focused helper and package tests cover spawn arguments, configuration and
  legacy settings. Claude CLI checks use simulated process results. These
  checks do not establish agent capacity limits or recovery from every host failure.
