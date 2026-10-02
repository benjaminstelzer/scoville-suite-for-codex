# Dispatch argument recovery

GPT-6 Luna with medium reasoning handled the revised manager instructions in
four isolated cases: a relative project path, an omitted but available worker
result, an unavailable original result, and a timed-out agent start with unknown
outcome. The first two produced usable review assignments. The latter two
remained blocked, without invented evidence or a repeated start.

The previous instructions and a simple no-Skill prompt reached the same safe
outcomes in their single comparison runs. The previous instructions also omitted
a visible blocker for the corrected calls despite their stricter relay wording.
The plain prompt needed an additional correction for its own wrong script path.
This supports the explicit recovery contract, not a measured reliability gain.

Each condition used one fresh native Codex subagent with the same model and
effort, identical fixture scenarios and the real packaged builder. The evaluator
received raw call results and state, without the suspected defect or expected
answers. Actual assignment files and returned native arguments were inspected.
Agent starts and user messages were represented as intended next actions only.
The test did not measure activation, live host delivery, long-run adherence or
other models. It did not restart or change the running empco workflow.

The comparison baseline is source commit
`bfd99102c68d98ce275ca36cb09ed2e8c664ac93`. The candidate changes the three manager
references under ADR-0145. Local evaluation inputs, outputs and agent handles are
retained in the task evidence; they are not part of the installed Skill.

Separate helper checks reproduced both invalid calls without assignment output
and consumed their corrected native arguments. The existing native-creation
tests passed. These technical checks establish helper behavior and argument
shape, not model effectiveness.
