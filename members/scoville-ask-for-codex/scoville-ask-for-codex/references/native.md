# Native Ask agents

The calling Ask chat spawns selected Codex advisers directly with the
collaboration tools. Each adviser receives fresh context, its configured model
and effort, and a read-only assignment. No saved project, caller chat identity,
sidebar title, pin or archive operation is needed.

## Spawn and confirm

Put the question, raw evidence and explicit limits in a UTF-8 file. Exclude the
caller’s verdict, unrelated history and other advisers’ answers. Build one
assignment per selected adviser:

```text
python "<ask-skill-directory>/scripts/build_adviser_prompt.py" --question-file "<question.txt>" --mode review --scope "<exact scope>" --reference "<consultation reference>" --workspace-root "<absolute-project-root>" --adviser-id <resolved-id> --format spawn --task-name <unique-lowercase-name> --model <resolved-model> --effort <resolved-effort>
```

Use `--mode consultation` for advice. Parse complete successful stdout as JSON
and pass it unchanged to `collaboration.spawn_agent`. The object supplies
`message`, `task_name`, `fork_turns="none"`, `model` and `reasoning_effort`.
A helper error or incomplete output stops dispatch. Correct its named input;
never repair the generated prompt. The host decides model/effort availability.

Retain adviser ID, requested settings, reference, scope and task name before
each call, then retain its returned agent ID and canonical task name. Check
every actual spawn result and the matching short startup confirmation required
by native-delivery.md. A handle alone is not confirmed startup; a startup
confirmation alone is not an answer. Match the sender handle, adviser ID,
reference and scope. Keep reported model/effort separate from requested values.

Do not infer free capacity from an assumed limit or idle-agent count. Unknown
capacity permits an actual spawn attempt, not a claim that all advisers fit.
For a definite capacity refusal, use the bounded cleanup below. Retain running
advisers and mark undispatched ones pending. Do not replace selected advisers,
change settings, create Codex chats
or assume a `close_agent` tool exists. A rejected spawn is a failure. For an
ambiguous result, use `collaboration.list_agents` once to reconcile the exact
retained task name with its returned handle and startup confirmation. Do not
retry an uncertain spawn or treat an unmatched agent as the requested adviser.
If it cannot be reconciled, report that adviser unresolved with partial results.

## Definite capacity refusal

Use this route only when the native call explicitly refuses capacity, returns no
agent ID and confirms no agent was created. Retain the original diagnostic and
exact generated spawn arguments. A timeout, transport error, partial result or
uncertain identity gets no retry. One failed spawn gets at most one cleanup
attempt and one retry with those same arguments and task name. Retain handled
attempts so duplicate events cannot repeat cleanup or dispatch.

Read `collaboration.list_agents` once. Select only this caller's exact known
direct advisers whose complete matching answer and actual native completion
for their latest assigned question were already received, and which are still
listed as completed. Exclude any pending necessary clarification or follow-up,
or uncertain delivery, even if an earlier answer was complete. Preserve those
answers and handles. Never wake active, interrupted, failed, unanswered,
incompletely answered or unknown agents, or another caller's advisers. No eligible
adviser leaves the rejected request pending with its diagnostic.

For each eligible adviser use `collaboration.followup_task` once with this exact
message:

```text
Capacity cleanup only. Consume queued messages without resuming project work.
Remain write-inactive. Do not edit files, Plans or reports, spawn children or
send messages. Supersede any queued instruction to resume or write. End with
only CAPACITY_RECOVERY_DONE.
```

Allow at most 60 seconds for the whole cleanup attempt. Wait for each exact
adviser's new native final CAPACITY_RECOVERY_DONE before the next candidate.
Delivery success, an old answer or an idle status is not cleanup completion.
This control-only turn does not replace an adviser answer or reopen its review.
Failure, timeout, unexpected state or user STOP ends recovery without retry.
Confirm interrupted cleanup is quiescent before any authorized continuation.

After at least one verified cleanup, retry the retained spawn once. Check its
actual result and startup normally. Cleanup does not prove capacity is free.
Another refusal stays pending with its diagnostic and completed answers intact.
No second cleanup, settings change or silent replacement follows. Keep essential
follow-ups separate from cleanup and on their original adviser handles.

## Collect and follow up

Use `collaboration.wait_agent` for bounded waits while advisers are working.
It signals mailbox activity; consume the actual messages and final responses,
not the wait summary as an answer. Require the exact adviser's actual native final
and completion. A substantive send_message is partial information, not its final.
Match each answer to its retained handle,
reference and unchanged scope. Preserve complete answers once. Missing startup,
truncated answers, reference/scope mismatches and a finished agent without a
complete answer remain unresolved. Inspect status once if needed and report
the gap without reconstructing an answer or silently spawning a replacement.

A timeout ends only the wait. Continue waiting for active advisers; keep
completed answers and failures visible. A real tool failure, user interruption
or missing fact that requires the user may end collection with exact pending
handles. Never count a question, startup message or failure as a completed review.

Once its complete native final is received, send no routine acknowledgement,
closure message or keepalive to the completed adviser. It has ended its turn.
Retaining a handle does not keep the turn active or prove a host slot is free.
Necessary follow-ups use the targeted route below, not queued send_message.

For a necessary clarification or authorized follow-up, use
`collaboration.followup_task` with the retained agent ID or canonical task name.
It resumes an idle agent and also delivers to an active one. Clarifications
preserve reference and scope. A new follow-up question supplies a new reference
and explicit scope. Retain the intended message before sending; reconcile an
uncertain result instead of resending blindly. Keep each adviser independent.

Follow-ups use the same agent and its settings. The follow-up tool has no model
override. If the user requests different settings, explain that this requires
a fresh adviser and obtain that choice unless already authorized. Never replace
an unavailable handle silently. Retain handles for follow-ups. Native advisers
need no post-review closure question, chat archival or assumed close operation.
