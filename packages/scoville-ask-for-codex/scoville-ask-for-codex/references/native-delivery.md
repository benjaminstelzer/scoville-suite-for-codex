# Native agent delivery

Before inspecting evidence, send the parent a short startup confirmation through
`collaboration.send_message`. Include adviser_id, consultation_reference and
scope exactly as supplied. Use the parent in your assigned agent task path;
do not infer it from a chat title or CODEX_THREAD_ID. This confirms receipt of
the assignment, not model telemetry or a completed answer.

Return the complete answer as your final agent response. The parent receives
it through the collaboration tools. Include adviser_id, consultation_reference,
unchanged scope and material evidence limits. Report actual model and effort
only when exposed by the host; otherwise they are unknown.

End that turn after the native final. Do not wait for an acknowledgement or keep
the agent active. The caller may resume the retained handle for a necessary
follow-up. An explicit capacity-cleanup followup is only message consumption:
do no inspection, writing, delegation or messaging, and end with only
CAPACITY_RECOVERY_DONE. That control turn never revises the completed answer.

If a material fact is missing, return the concrete question instead of guessing.
The caller will resume this same agent with the answer. Follow-ups preserve the
reference and scope unless the caller supplies a new question or changed scope.

Keep the answer within 6000 characters unless more detail was requested. If
essential content does not fit, explicitly mark it incomplete and name what
remains. Do not silently truncate or claim completion. Do not create, pin,
archive or close chats, or ask a session-closure question.
