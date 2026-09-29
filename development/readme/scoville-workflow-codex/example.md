### One recorded workflow sequence

This is a shortened sequence from a real project run on 21 September 2026.
The chat titles are the original ones, minus the coordinator IDs. It covers
one real Step, not a made-up group of several.

```text
Scoville-Workflow-Codex G6 selects W-015/step-1.
W-015-step-1 executor attempt-1 implements the assignment and reports checks.
W-015-step-1 reviewer attempt-1 finds a broken help-navigation anchor.
W-015-step-1 repair attempt-1 corrects the anchor and checks fragment navigation.
W-015-step-1 reviewer attempt-2 passes the correction, retaining wider test gaps.
Scoville-Workflow-Codex G6 records the accepted Step in a local commit.
G6's boundary checkpoint requests a coordinator handoff.
Scoville-Workflow-Codex G7 takes over W-015/step-2.
```

It shows review, correction and continuation. The focused review passing did
not mean that every live interface check had passed.
