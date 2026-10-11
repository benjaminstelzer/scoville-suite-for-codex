## How it works

The existing visible chat manages a prepared Plan or its authorized part.
Agents select relevant Skills themselves. Questions go directly to the user;
concise progress and evidence stay in the Plan. Host compaction continues the
same chat without automatic transfers or context thresholds.
User questions, change requests and planning preparation go to a read-only Explorer.
The manager answers the user, writes the Plan and decides authorized next work.

```mermaid
flowchart TD
    P["Visible manager selects authorized Step/group"] --> W["Executor implements and checks"]
    Q["Question, change request or planning preparation"] --> E["Explorer investigates and proposes read-only"]
    E --> M["Manager answers and writes authorized Plan changes"]
    M --> P
    W --> R["Fresh independent reviewer"]
    R -->|Findings| F["Fresh executor corrects source findings<br/>Manager handles Plan findings"]
    F --> R
    R -->|Pass| A["Manager accepts and updates Plan<br/>Commits when authorized"]
    A --> N{"Requested work remains?"}
    N -->|Yes| P
    N -->|No| D["Verify closure and writer quiescence<br/>Report completion"]
```

Review cadence may require an earlier checked boundary. Each finished unit
and correction that changed files gets independent review of those files
unless an explicit cadence says otherwise. Bookkeeping creates no separate
review phase.
