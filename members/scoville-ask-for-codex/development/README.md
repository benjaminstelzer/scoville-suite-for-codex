# Scoville Ask development

Canonical sources are in the nested `scoville-ask-for-codex/` directory. README
fragments live in `development/readme/scoville-ask-for-codex/` at the suite root.
Shared configuration code is generated from `shared/runtime/`. Edit its source,
then regenerate the bundled copy.

Run `python -m unittest discover -s members/scoville-ask-for-codex/development/tests` from the suite root. Provider and host simulations are not live consultation evidence.

## Native agent capacity

[Releasing agents without close_agent](../../../development/native-agent-capacity.md)
explains native turn completion, queued-message cleanup, the one-retry boundary
and the recorded host-test limits for Workflow and Ask.
