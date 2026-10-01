## How it works

- At the start, you see the path of the run report so you can open it at any time.
- Workflow carries out the assigned work, arranges independent reviews and
  corrects findings. Accepted progress and checks stay recorded in the Plan,
  so work can continue across sessions.
- The chat shows the current project, Plan point and your assigned Scope when
  the position changes.
- You can ask questions or pause work during the run. Open questions, requested
  pauses and problems needing your attention stay in the report, with later
  resolutions added.
- Once the requested work is complete and checked, Workflow says so and shows
  the report. A run without issues ends with an explicit confirmation.

```mermaid
flowchart TD
    P["Repository Plan"] --> C["Manager selects a bounded piece of work"]
    C --> W["Worker implements and checks the result"]
    W --> B{"Review boundary reached?"}
    B -->|No| A
    B -->|Yes| G{"Review required?"}
    G -->|Yes| R["Fresh reviewer checks the result"]
    G -->|No| A["Manager records checked progress<br/>and updates the Plan"]
    R -->|Pass| A
    R -->|Findings| F["Manager corrects Plan findings<br/>New worker corrects project findings"]
    F --> Q{"Follow-up review required?"}
    Q -->|Yes| R
    Q -->|No| A
    A --> E["Accept when required checks and reviews pass<br/>Commit when authorized"]
    E --> N{"Requested work remains?"}
    N -->|No| D["Announce completion<br/>Show the run report"]
    N -->|Yes| T{"Context boundary reached?"}
    T -->|No| C
    T -->|Yes| H["Hand over at the completed work boundary<br/>Next manager continues from the Plan and handoff"]
    H --> C
```
