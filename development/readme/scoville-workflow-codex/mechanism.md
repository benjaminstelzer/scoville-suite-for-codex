## How it works

The thread where Workflow starts is the manager. It maintains the Plan and
coordinates Explorer, Executor and Reviewer. It writes no source code.
The helper sends original Plan context and exactly one selected Step; the
manager does not rewrite the assignment. Agents choose relevant Skills themselves.

```mermaid
flowchart TD
    S["Manager selects ONE Step"] --> ST["Manager saves execution start/resume state"]
    ST --> E{"Executor for current Work Item exists?"}
    E -->|No| EN["Spawn selected Executor"]
    E -->|Yes| EC{"Measured context below threshold?"}
    EC -->|Yes| ER["Reuse Executor"]
    EC -->|Valid at or above| EE["Replace Executor; retain pair"]
    EC -->|Measurement error| B["Stop dispatch; report technical problem"]
    EN --> H["Helper validates start and sends original Step"]
    EE --> H
    ER --> H
    H --> W["Execute Step and checks; return done or problem"]
    W --> WR{"Executor result"}
    WR -->|blocked| BP["Manager resolves prerequisite; stop dependent work"]
    WR -->|done| R{"Reviewer for current Work Item exists?"}
    R -->|No| RN["Spawn selected Reviewer"]
    R -->|Yes| RC{"Measured context below threshold?"}
    RC -->|Yes| RR["Reuse Reviewer"]
    RC -->|Valid at or above| RE["Replace Reviewer; retain pair"]
    RC -->|Measurement error| B
    RN --> V["Helper sends SAME Step and Executor result"]
    RE --> V
    RR --> V
    V --> A{"Step review result"}
    A -->|blocked| BP
    A -->|changes_requested| F["Manager adds unchanged review result; same Step"]
    F --> ST
    A -->|pass| N{"All Steps accepted?"}
    N -->|No| NA{"Next Step authorized?"}
    NA -->|Yes| S
    NA -->|No| STOP["Stop; Work Item stays open"]
    N -->|Yes| C["Select Reviewer by same agent check; helper sends full Work Item"]
    C --> P{"Closure result"}
    P -->|blocked| BP
    P -->|changes_requested| K["Manager selects ONE affected Step; keeps Plan and Work Item"]
    K --> F
    P -->|pass| D["Accept Work Item; next authorized Work Item or finish"]
    Q["Question, idea or planning preparation"] --> X{"Explorer for Manager thread exists?"}
    X -->|No| XN["Spawn selected Explorer"]
    X -->|Yes| XC{"Measured context below threshold?"}
    XC -->|Yes| XR["Reuse Explorer"]
    XC -->|Valid at or above| XE["Replace Explorer; retain pair"]
    XC -->|Measurement error| B
    XR --> XP["Investigate read-only; report to Manager"]
    XN --> XP
    XE --> XP
    XP --> M["Manager answers user and writes authorized Plan changes"]
```

Executor and Reviewer stay associated with one Work Item; Explorer with the
manager thread. One threshold applies before all subagent assignments.
Establish completion and idle state before measuring an associated agent.
No existing agent means first creation. A valid measurement below threshold means
reuse; at or above means replace with the retained pair. Replacement does not
reset the role's model choice. A missing measurement or execution blocker
returns a problem to manager, not an automatic replacement. An incompatible
newly selected model pair requires a new agent. Ongoing writes are not interrupted
for threshold checks. Host compaction continues the same assignments.

Use complete unchanged native finals for review and correction inputs. Missing
required before/after attribution blocks review; recover it through the same
Step and agent check, never through a Manager-composed substitute.

Every Step gets independent review. It covers actual changes of the selected
Executor assignment, necessary context and open findings. An evidence-only
follow-up continues review of the original change. The separate closure review
checks every Step and the full Acceptance against current implementation.
Corrections repeat one Step and its review, then closure when due. If no existing
Step covers a missing already required implementation, manager may add that
Step without changing Acceptance; changed or unclear requirements need the user.
