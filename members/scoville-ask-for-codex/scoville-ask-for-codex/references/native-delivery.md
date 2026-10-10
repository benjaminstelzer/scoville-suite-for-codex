# Native agent delivery

Return the complete answer in your final agent response, or use the shared
complete-file route when required content cannot fit. Include adviser_id,
consultation_reference, unchanged scope and material evidence limits in either
form. Report actual model and effort only when exposed by the host; otherwise
they are unknown.

For native Codex Ask advisers, the shared writing rules' temporary-artifact
exception applies to the general adviser write ban. All other adviser
restrictions remain. This delivery route does not apply to Ask Claude.

End that turn after the native final. Do not wait for an acknowledgement or keep
the agent active. The caller may resume the retained handle for a necessary
follow-up.

If a material fact is missing, return the concrete question instead of guessing.
The caller will resume this same agent with the answer. Follow-ups preserve the
reference and scope unless the caller supplies a new question or changed scope.

Use the complete-file route only when necessary content cannot meet a declared or
explicitly selected delivery limit, including an applicable outer tool-output
limit. Compact wording without losing required content. If necessary content
still cannot fit, return the shared complete-file metadata with an instruction to
verify SHA-256 and read the entire file before treating the answer as complete.
If your permissions or host tools prevent that route, follow the shared caller-
capture rule; report any remaining delivery limitation without claiming
completeness.
