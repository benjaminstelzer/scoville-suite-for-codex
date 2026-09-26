# Native Ask chats

Start the round in a normal Codex caller chat. Desktop multi-agent v2 subagents
cannot receive send_message_to_thread deliveries; return the request to their
parent instead of creating an adviser from that unsupported caller.

Resolve the requested advisers once, then use create_thread directly for each.
Preserve the selected saved project and its local checkout. Each adviser gets
fresh context and exactly `S-ASK <UPPERCASE selected model ID> - <calling task title>`.
Example: `S-ASK GPT-6-SOL - Plan überprüfen`. Uppercase only the displayed model
ID; preserve the caller title and technical model parameter. Keep existing
chat titles and follow-up identities unchanged.
Use the actual caller ID and title; titles do not identify tasks.

The prompt contains references/adviser.md, references/native-delivery.md,
return_to_thread_id, a short consultation_reference, mode, scope and the user's
question with necessary raw evidence. Exclude the caller's verdict and unrelated
history. Native parameters are model=<resolved model>, thinking=<resolved effort>
and target={type:project,projectId:<saved-id>,environment:{type:local}}.
The host validates availability; report failure without changing the model.

Before dispatch, use the user's existing authorization for messages within
this consultation and carry its actual wording and scope in the assignment.
Do not ask again when it already covers the adviser and caller. An agent's
dispatch alone grants no permission. If a required authorization is missing,
resolve it before creating the adviser rather than leaving an undeliverable answer.

Retain intended adviser/question before creation, then the returned task/host ID.
clientThreadId is pending, not a usable threadId. Resolve pending creation with
host-provided correlation; never retry an unknown creation or match only by title.
No lifecycle helper or intermediate payload is required.

After dispatch, satisfy any host-required wait for progress before ending the
caller turn. Otherwise use adviser messages to resume it. Match the actual
sender ID and consultation_reference to the current question. Retain complete
answers or individual failures before reporting the round. Multiple advisers may
reply in any order, including while the caller is already active; retain each
once and end the turn again if another answer remains pending and the host
permits it. Add no polling loop.

On a host completion event, resume or reported missing delivery, make one targeted native status query
or read_thread call for the known task and only the missing answer/state. An
unresolved task remains pending; do not create a replacement or loop.
`RESULT NOT DELIVERED` is a diagnostic in the adviser chat, not a wake-up event.
Do not claim automatic recovery without an observed host event or message.

## Follow-ups and archival

For an authorized follow-up, use send_message_to_thread on the same unarchived
chat with a new reference and question. Include the unchanged delivery destination.
Keep its model/effort unless explicitly overridden. Retain the intended question
before sending; an unknown send result is reconciled rather than sent again.
Never silently replace or unarchive a missing/archived adviser.

Leave successful advisers open. Explicit archival consent in that adviser chat,
an authorized cleanup, or an observed access/permission failure may archive the
exact task after its answer/failure is retained. Call set_thread_archived directly
once for that exact ID. No confirmation message or archival check follows.
Report an explicit tool error if returned, without changing permissions or retrying.
