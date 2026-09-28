## How it works

- The coordinator selects a Step, related consecutive Steps or a whole Work Item. Grouping shares setup and produces a checkable result while preserving the Plan's order.
- Risk determines the worker's model and effort. The worker implements in the existing checkout and returns its result by message.
- Reviews follow the project's cadence, otherwise product-code changes receive an earlier review after a defect fix or before dependent work or extensive testing, and the final review reuses earlier assessments of unchanged parts.
- The coordinator corrects Plan findings and assigns project findings to a new worker. Material or unclear corrections receive another review.
- Accepted changes and Plan updates enter one commit when committing is authorized.
- At a configured context threshold, a successor continues the unfinished work in the same checkout. The coordinator checks after completed groups and worker handoffs, retaining pending work and review.
- Handoffs use direct messages. The successor confirms receipt and asks the predecessor to archive itself, then continues. Archive errors are reported without blocking accepted work.
- After receiving a worker or reviewer result, the coordinator asks that chat to archive itself. Reviewers report their findings and anything they could not verify in one complete response.

```mermaid
flowchart TD
    P["Repository Plan"] --> C["Coordinator selects a bounded unit<br/>and routes model and effort"]
    C --> W["Worker implements and validates"]
    W -->|Checked result| B{"Review boundary reached?"}
    W -->|Context handoff| T
    B -->|No| A
    B -->|Yes| G{"Review required?"}
    G -->|Yes| R["Fresh reviewer checks the result"]
    G -->|No| A["Coordinator records checked result<br/>and updates the Plan"]
    R -->|Pass| A
    R -->|Findings| F["Coordinator fixes Plan findings<br/>New worker corrects project findings"]
    F --> Q{"Follow-up review required?"}
    Q -->|Yes| R
    Q -->|No| A
    A --> E["Accept only when due Acceptance and review pass<br/>Commit accepted changes when authorized"]
    E --> N{"Requested work remains?"}
    N -->|No| D["Finish"]
    N -->|Yes| T{"Context threshold reached?"}
    T -->|No| C
    T -->|Yes| H["Hand over the coordinator with pending work<br/>Successor confirms receipt; predecessor self-archives"]
    H --> C
```
