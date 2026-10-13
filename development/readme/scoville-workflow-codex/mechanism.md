## How it works

The thread where Workflow starts is the manager. It maintains the Plan and
coordinates Explorer, Executor and Reviewer. It writes no source code.
The helper sends original Plan context and exactly one selected Step; the
manager does not rewrite the assignment. Agents choose relevant Skills themselves.

```mermaid
flowchart TD
    G{"Activation: Git workspace clean before Plan writes?"} -->|Yes| S
    G -->|No or Git unavailable| BP
    S["Manager selects ONE Step"] --> ST["Manager saves execution start/resume state"]
    ST --> E{"Executor for current Work Item exists?"}
    E -->|No| EN["Spawn and initialize Executor once"]
    E -->|Yes| EC{"Measured context below threshold?"}
    EC -->|Yes| ER["Reuse Executor; next task only"]
    EC -->|Valid at or above| EE["Replace Executor; retain pair"]
    EC -->|Measurement error| B["Stop dispatch; report technical problem"]
    EN --> H["Helper validates start and sends original Step"]
    EE --> H
    ER --> H
    H --> W["Execute Step and checks; return done or problem"]
    W --> WR{"Executor result"}
    WR -->|blocked| BP["Manager resolves prerequisite; stop dependent work"]
    BP -->|missing Executor result: same Step| E
    WR -->|done| MC{"Manager: Step complete, required checks met, effects clear?"}
    MC -->|No or unclear| BP
    MC -->|Yes| CR{"Changes or open Step review?"}
    CR -->|Yes| R{"Reviewer for current Work Item exists?"}
    CR -->|No| SA["Manager records completed Step and evidence"]
    R -->|No| RN["Spawn and initialize Reviewer once"]
    R -->|Yes| RC{"Measured context below threshold?"}
    RC -->|Yes| RR["Reuse Reviewer; next task only"]
    RC -->|Valid at or above| RE["Replace Reviewer; retain pair"]
    RC -->|Measurement error| B
    RN --> V["Helper sends SAME Step and Executor result"]
    RE --> V
    RR --> V
    V --> A{"Step review result"}
    A -->|blocked| BP
    A -->|changes_requested| F["Manager adds unchanged review result; same Step"]
    F --> ST
    A -->|pass| CS["Manager records Step; commits reviewed work and Plan progress"]
    CS -->|success or no versionable changes| N
    CS -->|commit failed or forbidden| BP
    SA --> N{"All Steps complete and required Step reviews passed?"}
    N -->|No| NA{"Next Step authorized?"}
    NA -->|Yes| S
    NA -->|No| STOP["Commit pending Plan if no unreviewed work; stop with Work Item open"]
    N -->|Yes| C["Select Reviewer by same agent check; helper sends full Work Item"]
    C --> P{"Closure result"}
    P -->|blocked| BP
    P -->|changes_requested| K["Manager selects ONE affected Step; keeps Plan and Work Item"]
    K --> F
    P -->|pass| D["Accept Work Item; next authorized Work Item or finish"]
    Q["Question, idea or planning preparation"] --> X{"Explorer for Manager thread exists?"}
    X -->|No| XN["Spawn and initialize Explorer once"]
    X -->|Yes| XC{"Measured context below threshold?"}
    XC -->|Yes| XR["Reuse Explorer; next task only"]
    XC -->|Valid at or above| XE["Replace Explorer; retain pair"]
    XC -->|Measurement error| B
    XR --> XP["Investigate read-only; report to Manager"]
    XN --> XP
    XE --> XP
    XP --> M["Manager answers user and writes authorized Plan changes"]
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
