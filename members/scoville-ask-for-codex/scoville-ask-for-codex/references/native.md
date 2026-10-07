# Native Ask agents

The calling Ask chat spawns selected Codex advisers directly with the
collaboration tools. Each adviser receives fresh context, its configured model
and effort, and a read-only assignment.

## Spawn and collect

Put the question, raw evidence and explicit limits in a UTF-8 file outside the
reviewed working tree, using the workspace temporary area or system temporary
directory. Exclude the caller’s verdict, unrelated history and other advisers’ answers. Build one
assignment per selected adviser:

```text
python "<ask-skill-directory>/scripts/build_adviser_prompt.py" --question-file "<question.txt>" --mode review --scope "<exact scope>" --reference "<consultation reference>" --workspace-root "<absolute-project-root>" --adviser-id <resolved-id> --format spawn --task-name <unique-lowercase-name> --model <resolved-model> --effort <resolved-effort>
```

Use `--mode consultation` for advice. Parse complete successful stdout as JSON
and pass it unchanged to `collaboration.spawn_agent`. The object supplies
`message`, `task_name`, `fork_turns="none"`, `model` and `reasoning_effort`.
A helper error or incomplete output stops dispatch. Correct its named input;
never repair the generated prompt. The host decides model/effort availability.

Retain adviser ID, requested settings, reference, scope and generated task name,
then the returned exact native handle. The host identifies the final's sender;
no startup callback is required. A handle is not a complete answer. Actual model
telemetry stays separate from requested settings.

Do not infer free capacity from an assumed limit or idle-agent count. Unknown
capacity permits an actual spawn attempt, not a claim that all advisers fit.
For a capacity refusal, retain its diagnostic and running advisers; mark
undispatched ones pending. Do not wake completed advisers for cleanup or retry
automatically. Do not replace selected advisers,
change settings, create Codex chats
or assume a `close_agent` tool exists. A rejected spawn is a failure. For an
ambiguous result, use `collaboration.list_agents` once to reconcile the exact
retained task name with its returned handle. Do not
retry an uncertain spawn or treat an unmatched agent as the requested adviser.
If it cannot be reconciled, report that adviser unresolved with partial results.

## Collect and follow up

Use `collaboration.wait_agent` for bounded waits while advisers are working.
It signals mailbox activity; consume the actual messages and final responses,
not the wait summary as an answer. For an inline or complete-file answer, require
the exact adviser's actual native final and completion. Match its host sender
to the retained handle and its answer to the latest question, adviser identity,
reference and scope. For complete-file delivery, verify SHA-256 and read the
entire file before accepting or using the answer; metadata alone is insufficient.
A substantive send_message is partial information, not the native final.
Missing or incomplete answers remain unresolved. Retain complete answers once.
If only a label repeats, use the retained assignment to identify the answer;
a different reference or scope needs clarification. Never accept an earlier
answer as the result of a later same-handle follow-up.

A timeout ends only the wait. Continue waiting for active advisers; keep
completed answers and failures visible. A real tool failure, user interruption
or missing fact that requires the user may end collection with exact pending
handles. Never count a question or failure as a completed review.

Once its complete native final is received, send no routine acknowledgement,
closure message or keepalive to the completed adviser. It has ended its turn.
Retaining a handle does not keep the turn active or prove a host slot is free.
Necessary follow-ups use the targeted route below, not queued send_message.
If a necessary message targets an agent whose state is unclear, check its exact
handle with `collaboration.list_agents` once first. A completion race remains
possible; add no polling loop.

For a necessary clarification or authorized follow-up, use
`collaboration.followup_task` with the retained agent ID or canonical task name.
It resumes an idle agent and also delivers to an active one. Clarifications
preserve reference and scope. A new follow-up question supplies a new reference
and explicit scope. Retain the intended message before sending; reconcile an
uncertain result instead of resending blindly. Keep each adviser independent.

Follow-ups use the same agent and its settings. The follow-up tool has no model
override. If the user requests different settings, explain that this requires
a fresh adviser and obtain that choice unless already authorized. Never replace
an unavailable handle silently.
