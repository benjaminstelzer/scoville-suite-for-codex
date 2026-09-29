# Native Ask chats

Start the round in the calling Codex chat. It owns creation, necessary follow-up
messages and collection of the advisers' answers through native task tools.

The Ask request covers these chats and their consultation messages under
SKILL.md. Use that route without a separate approval step.

Resolve the requested advisers once, then use create_thread directly for each.
Preserve the selected saved project and its local checkout. Each adviser gets
fresh context and exactly `SC-ASK-<ADVISER ID>: <calling task title>`.
Example: `SC-ASK-ASTRA: Review the Plan`. Use the resolved adviser ID in uppercase
for the title label. Preserve caller-title casing and the exact technical model
parameter. Do not add a number or project name.
Keep existing chat titles and follow-up identities unchanged.
Use the actual caller ID and title and saved project ID;
titles do not identify tasks.

Put the user's request, necessary raw evidence and explicit limits in a UTF-8
file. Exclude the caller's verdict and unrelated history. Build the assignment:

```text
python "<ask-skill-directory>/scripts/build_adviser_prompt.py" --question-file "<question.txt>" --mode review --scope "<exact scope>" --reference "<consultation reference>" --format create --project-id <saved-id> --adviser-id <resolved-adviser-id> --caller-title "<actual caller title>" --model <resolved-model> --thinking <resolved-effort>
```

Use `--mode consultation` for advice. `CODEX_THREAD_ID`, or the optional
`--caller-thread-id`, adds caller provenance; no callback address is required. The helper includes
the packaged adviser and delivery rules. Parse its successful, complete stdout
as JSON and pass that object unchanged to create_thread. It includes the prompt,
canonical title, project and selected model/effort. A nonzero exit or truncated output stops
dispatch; fix the named input, not the generated prompt. No manual rule assembly.

The host validates availability; report failure without changing the model.

Retain intended adviser/question before creation, then the returned task/host ID.
clientThreadId is pending, not a usable threadId. Resolve pending creation with
host-provided correlation; never retry an unknown creation or match only by title.
When resolved config.pin_threads is true, pin each ready adviser with move_thread_to_sidebar_section using its returned
threadId, hostId and sectionId="pinned". Resolve pending creation before pinning.
If pinning fails, report it and retry only the pin on that existing chat.
When false, omit pinning; do not unpin existing chats. The default is true.

After creation or a follow-up, use wait_threads on the actual task/host IDs
with bounded event waits, normally timeoutMs=30000. Retain each returned cursor
as that target's afterCursor for the next wait. Consume a complete returned
answer directly. If a completed response is missing or truncated, read that
same chat once with read_thread. Match task ID, consultation_reference and
scope, retain the answer or concrete failure, then present it to the user.
Keep reference and scope as separate exact values, including in clarifications.
Do not replace the consultation reference with the reviewed scope.
The adviser replies in its own chat; no callback is required.

A necessary question is an ordinary adviser response. Answer it through
send_message_to_thread in the same chat, using available facts; ask the user
only when the missing fact requires them. Preserve the reference while resolving
that question. Then collect the response normally.

A timeout ends only that wait. Keep the calling turn active and wait again on
unfinished advisers with their latest cursors until answers, questions or real
failures arrive. Independent work may happen between waits. Do not end the turn
with only "review pending" or depend on a future user message or completion
notification. Repeated bounded event waits are expected; rapid status polling,
timers, duplicate creation and requests to resend an existing answer are not.
Keep each completed answer once and remove that adviser from pending targets.
Questions and failures are not completed reviews. Continue other advisers while
preserving those open issues. A user interruption follows the user's direction;
missing facts only the user can supply or an actual tool failure may require
yielding with the exact pending handles. Never claim that partial work is done.

## Follow-ups and archival

For an authorized follow-up, use send_message_to_thread on the same unarchived
chat with a new reference and question.
Keep its model/effort unless explicitly overridden. Retain the intended question
before sending; an unknown send result is reconciled rather than sent again.
Never silently replace or unarchive a missing/archived adviser.

The caller owns the post-review question and closes sessions under SKILL.md's
review-closing rule. After retaining the answer, call set_thread_archived once
with archived=true and the exact adviser threadId and hostId. Never archive the
calling chat or send the adviser another question about archival. No receipt
or archival check follows. Ordinary consultations stay open unless the user
requests closure or cleanup.
Report an explicit tool error if returned, without changing permissions or retrying.
