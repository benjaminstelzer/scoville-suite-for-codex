## How it works

The thread where Workflow starts is the manager. It maintains the Plan and
coordinates Explorer, Executor and Reviewer. It writes no source code.
The helper sends original Plan context and exactly one selected Step; the
manager does not rewrite the assignment. Agents choose relevant Skills themselves.

Each named call continues in the diagram with that title. Agent selection returns
to its caller only when an agent is ready. A measurement error stops dispatch.

### Work Item control

```mermaid
flowchart TD
    G{"Clean Git workspace<br/>before activation writes?"} -->|Yes| S["Manager selects ONE Step"]
    G -->|No or Git unavailable| BP["Manager resolves prerequisite<br/>Dependent work stays stopped"]
    BP -->|Missing Executor result only| REC[["Recover SAME Step<br/>Enter Executor selection<br/>in Step execution and review"]]
    REC -->|Step completed| N
    S --> T[["Call: Step execution and review"]]
    T -->|Step completed| N{"All Steps complete and<br/>required Step reviews passed?"}
    N -->|No| NA{"Next Step authorized?"}
    NA -->|Yes| S
    NA -->|No| STOP["Commit pending Plan if no unreviewed work<br/>Stop with Work Item open"]
    N -->|Yes| C[["Call: Agent selection<br/>Reviewer for current Work Item"]]
    C -->|Agent ready| H["Helper sends full Work Item<br/>Every Step and full Acceptance"]
    H --> P{"Closure result"}
    P -->|blocked| BP
    P -->|changes_requested| K["Select ONE affected Step<br/>Keep Plan and Work Item<br/>Add unchanged review result"]
    K --> T
    P -->|pass| D["Accept Work Item<br/>Next authorized Work Item or finish"]
```

### Step execution and review

```mermaid
flowchart TD
    ST["Manager saves execution<br/>start or resume state"] --> E[["Executor selection<br/>Call: Agent selection<br/>Current Work Item"]]
    E -->|Agent ready| H["Helper validates start<br/>Sends original selected Step"]
    H --> W["Execute Step and required checks<br/>Return complete result"]
    W --> WR{"Executor result"}
    WR -->|blocked| BP["Manager resolves prerequisite<br/>Dependent work stays stopped"]
    BP -->|Missing Executor result only| E
    WR -->|done| MC{"Step complete, required checks met<br/>and effects clear?"}
    MC -->|No or unclear| BP
    MC -->|Yes| CR{"Changes or open Step review?"}
    CR -->|No| SA["Record completed Step and evidence"]
    CR -->|Yes| R[["Call: Agent selection<br/>Reviewer for current Work Item"]]
    R -->|Agent ready| V["Helper sends SAME Step<br/>and complete Executor result"]
    V --> A{"Step review result"}
    A -->|blocked| BP
    A -->|changes_requested| F["Add unchanged review result<br/>Keep the SAME Step"]
    F --> ST
    A -->|pass| CS["Record Step and commit reviewed work<br/>with Plan progress"]
    CS -->|Success or no versionable changes| DONE["Return: Step completed<br/>to Work Item control"]
    CS -->|Commit failed or forbidden| BP
    SA --> DONE
```

### Agent selection

This check serves Executor, Reviewer and Explorer, including closure review.
Measure only after the associated agent has completed its work and is idle.

```mermaid
flowchart TD
    E{"Associated agent exists?"} -->|No| NEW["Spawn and initialize agent once"]
    E -->|Yes| C{"Valid measured context<br/>below threshold?"}
    C -->|Yes| REUSE["Reuse agent<br/>Next task only"]
    C -->|Valid at or above| REPLACE["Replace and initialize agent<br/>Retain model and reasoning pair"]
    C -->|Measurement error| B["Stop dispatch<br/>Report technical problem to Manager"]
    NEW --> READY["Return: agent ready<br/>to the calling diagram"]
    REUSE --> READY
    REPLACE --> READY
```

### Explorer requests

```mermaid
flowchart TD
    Q["Question, idea or planning preparation"] --> X[["Call: Agent selection<br/>Explorer for Manager thread"]]
    X -->|Agent ready| XP["Investigate read-only<br/>Report to Manager"]
    XP --> M["Manager answers the user<br/>and writes authorized Plan changes"]
```

Executor and Reviewer stay associated with one Work Item; Explorer with the
manager thread. One threshold applies before all subagent assignments.
Fresh agents receive role, writing, shell-command and result rules once.
Reuse sends only the next task and its binding context and evidence; it does
not reload those rules or already loaded Skills. Codex supplies project rules.
The Reviewer retains both Step and closure policies from its first assignment.
Establish completion and idle state before measuring an associated agent.
No existing agent means first creation. A valid measurement below threshold means
reuse; at or above means replace with the retained pair. Replacement does not
reset the role's model choice. A missing measurement or execution blocker
returns a problem to manager, not an automatic replacement. An incompatible
newly selected model pair requires a new agent. Ongoing writes are not interrupted
for threshold checks. Host compaction continues the same assignments.

Use complete unchanged native finals for review and correction inputs. Missing
required change attribution blocks review; recover it through the same
Step and agent check, never through a Manager-composed substitute.
Git is required. Activation checks a clean worktree before Plan writes; it
does not automatically clean existing work. Each passed changed Step is committed
with Plan progress before advancing. Reviewers use Git status and diff HEAD;
closure uses the Work Item start commit. Make no empty commits.

Review each Step that changed files, configuration or behavior. A Step without
such changes is checked by the closure review. The manager checks completion,
required checks and clear effects using the complete result and reconciled
retained effects. Missing or unclear results are resolved first; `changes: none`
alone means only no file changes; Git and actual non-file or ignored-output
evidence determine effects. Step review covers changes of the
selected Step, necessary context and open findings. Follow-ups without new
changes do not end an open Step review or its findings; evidence-only follow-ups
continue review of the original change. The separate closure review
checks every Step and the full Acceptance against current implementation.
Corrections repeat one Step, its review when required, then closure when due. If no existing
Step covers a missing already required implementation, manager may add that
Step without changing Acceptance; changed or unclear requirements need the user.
