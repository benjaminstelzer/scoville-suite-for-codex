# Run feedback

Manager: send controls and issues only to the exact runner ID in your start
assignment, never another project's runner or a chat selected by title.
Children: return messages and results to your spawning manager.
Runner: display user feedback in the original runner chat.

Use the same absolute report path supplied at every manager start. A successor
verifies that its direct handoff names that file. Keep the actual overall scope
as free text through handoffs and steering. No report or display invents scope.

`run_feedback.py` generates every visible status. WORKING_ON has only its status
line; blockers, questions, pauses and completion retain their explanatory body.
The manager copies its returned `message` exactly into the native send argument.
Its first line is a protocol control, including the key for WORKING_ON. After
authenticating the sender, the runner removes that first line. For progress,
blockers, questions and pauses, copy the remaining Markdown (`text`) exactly
under the applicable state rules, including plain paths; add no backticks,
emphasis or rewording. Completion follows its section below. Use these messages
without separate startup, handshake or answer-forwarding status narration.

## Progress

Use the project name supplied at manager start through repairs, stops,
resumptions and handoffs. Retain the actual user scope internally, never infer
it from the Plan Goal or title. Only user steering changes it. After saving and
validating Plan progress, generate before every writing dispatch or resumption:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" progress --project "<project-name>" --project-root "<workspace_root>"
```

Send the returned `message` to the runner with `collaboration.send_message`. Require
successful send output before writing dispatch or resumption. On failure or
uncertain delivery, retain the point and generated payload, report BLOCKED with
the diagnostic and keep that release stopped. The manager-only mode reads the
bundled select_context.py --position projection. It uses the active in_progress
Work Item and its single saved consecutive in_progress Step or Step group, or a
Step-less legacy item. When several groups remain in_progress, add `--point
W-NNN/step-N` or `--point W-NNN/steps-N-M` for the actually worked section. This
may be part of a saved group; every named Step must already be in_progress in
the current item. Preserve other historical Step statuses. Do not reset them or
use display-only `--plan/--point` to bypass this check. Missing or unmarked
progress fails with a diagnostic; reconcile observed progress and validate
before retrying. The helper neither selects nor starts work. Assignment labels
may cover a larger range. Display only `Working on: project → PLAN-NNNN →
W-NNN/step-N` as the generated bold line, with no Scope paragraph or other body.
The runner never invokes this mode or reads the Plan.

The runner accepts progress only from its current STARTed manager. Process
received messages in order before waiting again, including batches with issues.
Validate sender and retained project name. Display a changed key's text before
retaining that key as displayed. Keep it across takeover, stops and resumptions.
The same key prints nothing, including review, repair and scope changes at that
point. Successful delivery permits writer release; it does not confirm visible
display. On project-name drift, request regeneration from the retained value and
keep that key undisplayed until its corrected message arrives. The manager
resends promptly; cosmetic correction changes only the display if work is
already released. A substantive scope conflict stops dependent work until
clarified. Never repair helper output manually. Managers omit `--previous-key`
for WORKING_ON: always send the complete generated text and let the runner
deduplicate visible output.
For effect-free input correction after confirmed progress, follow
[pre-dispatch correction](operations-dispatch.md#pre-dispatch-correction).

## Targeted issues

Before a Plan location is known, use Startup by omitting both location options:

```text
python -X utf8 "<workflow-skill-directory>/scripts/run_feedback.py" status --kind blocked --project "<project-name>" --text-file "<blocked.txt>"
```

Once known, add both `--plan PLAN-NNNN` and `--point W-NNN/step-N` or its
consecutive Step range. Capture the helper's complete output before display.

For a dispatch-builder argument error or a selector-budget error in dispatch or
progress, first apply the bounded [pre-dispatch
correction](operations-dispatch.md#pre-dispatch-correction). A successful
correction needs no visible blocker or report entry. All unresolved failures
follow the immediate relay rule below.

For every necessary decision or blocker from a child, manager work, helper or takeover:

1. Stop dependent work. Name affected scope if independent authorized work can continue.
2. Generate `status --kind decision` with the exact question, reason and waiting
   work, or `--kind blocked` with the diagnostic, blocked work and necessary action.
3. Send promptly to the runner; wait neither for final child results, unrelated
   checks nor a changed progress key.
4. Retain the originating manager ID for answer routing, including during takeover.
5. Save the issue and actual answer when the current report owner can safely
   write; dependent work resumes only after necessary answer and persistence.

Children ask only their manager. The runner authenticates the current or exact
pending manager under takeover rules and alone presents the user question.
Generate the body in the user's language with retained project name and unit:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" status --kind decision --project "<project-name>" --plan <plan-id> --point <point> --text-file "<question.txt>"
```

Use `decision`, `blocked` or `paused`. Completion uses `complete` below;
`status --kind completed` is legacy display only and does not finish the report.
Use `--text-file` for message bodies prepared under the shared writing rules
when the role may write. While writes are prohibited, use this standard
ECMAScript function in the available Codex code runtime to encode the complete
body as UTF-8 and standard Base64. It requires no Node, Buffer or file writes.
Use an existing runtime string value, or a single- or double-quoted JavaScript
string literal with standard escapes. Never insert the body into a template literal.
Pass its generated value unchanged as one `status --text-base64 <value>`
argument. Never hand-encode, discard characters or interpolate the body into
shell code. An encoding error stops the call. `--text` remains compatible for
already argument-preserving callers. This grants no pending-manager write permission.

```javascript
function statusBodyBase64(text) {
  const bytes = Array.from(encodeURIComponent(text).matchAll(/%([0-9A-F]{2})|([^%])/g),
    ([, hex, char]) => hex ? parseInt(hex, 16) : char.charCodeAt(0));
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let result = '';
  for (let i = 0; i < bytes.length; i += 3) {
    const n = (bytes[i] << 16) | ((bytes[i + 1] ?? 0) << 8) | (bytes[i + 2] ?? 0);
    result += alphabet[n >>> 18] + alphabet[(n >>> 12) & 63]
      + (i + 1 < bytes.length ? alphabet[(n >>> 6) & 63] : '=')
      + (i + 2 < bytes.length ? alphabet[n & 63] : '=');
  }
  return result;
}
```
A saved report or manager-only commentary is not a relay. Suppress only an
identical already-visible pending issue, never a new question or changed cause
because WORKING_ON is unchanged. Forward an actual answer once to the manager;
no elapsed time, timeout or unrelated answer resolves the pending issue.

Only record a user question, a point paused for a user request, or a problem
requiring user inspection. Record the affected point and actual question or
needed action. Ordinary reviews, self-corrected checks, progress and successful
results create no entry. Children return needed facts to the manager and do
not write this file. The current manager is its sole writer. Relay immediately,
independently of persistence. Save the issue and any received answer before
dependent work resumes, when the current report owner can safely write.

Save the relevant free text in a UTF-8 temporary file and run:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" add --report-file "<run-report.md>" --kind question --location "<plan-id> / <point>" --text-file "<question.txt>"
```

Kinds are `question`, `pause` and `problem`. Retain the returned `issue_id` with
the pending question or pause. `--issue-id <retained-id>` permits an identical
retry without another entry; a different issue under that ID is rejected.
After the actual answer, resume or resolution is received, append it:

```text
python "<workflow-skill-directory>/scripts/run_feedback.py" resolve --report-file "<run-report.md>" --issue-id <retained-id> --text-file "<clarification.txt>"
```

The original issue stays, its status becomes Resolved and the clarification is
appended. Repeating the same clarification changes nothing. A clarification
does not authorize work beyond the user's actual answer. Dependent work remains
paused while a necessary answer is absent. Preserve entries and IDs in the
direct manager handoff. Never erase resolved issues to make a run look clean.

| State | Persistence and relay |
| --- | --- |
| User stop | Establish child and writer quiescence, record pause, then generate STOPPED with `status --kind paused`. |
| Writes prohibited | Retain and relay the unsaved issue and why it cannot yet be saved. |
| Pending successor | Keep issue unsaved until TAKEOVER_COMPLETE makes it current owner. |
| Report-write failure | Retain and relay the issue with exact save diagnostic; mark unsaved. |
| Unknown write outcome | Read existing report before retrying. |

Keep dependent work stopped until persistence and any necessary answer are secured.
Saving report or Plan must never hide the condition. Never accept partial helper stdout.

If startup fails before a manager can own the report, the runner records the
user-relevant startup problem at `Startup` and generates its blocked display
using the same helper. Otherwise managers own report edits. No uncertain writer
state permits a second writer.

## Completion

Only after the requested scope passes acceptance and required closure, use
one call with the actual retained Plan, last accepted point and completed scope:

```text
<verified-python> -X utf8 "<workflow-skill-directory>/scripts/check_text_size.py" --max-output-tokens <limit> --publish-full --project-root "<workspace_root>" --run -- <verified-python> -X utf8 "<workflow-skill-directory>/scripts/run_feedback.py" complete --report-file "<run-report.md>" --completed --project "<project-name>" --plan <plan-id> --point <point> --text-file "<completion.txt>"
```

Manager completion:

1. Prepare the complete UTF-8 body under the shared writing rules before the call.
   Use the same smallest applicable output limit in checker and both host tools.
2. Capture the complete result. Verify the capture hash and read all parts through
   `last` before using file-delivered output. `complete` returns only `report_file`,
   `text` and `message`; the report stays in its file.
3. Send returned `message` unchanged; finish with its control-only native final
   after children and writers are quiescent, under operations.md.

The helper validates the message and
report before saving. An empty report becomes exactly `No issues occurred
during this run.`. Existing issues and resolutions stay unchanged. Repeating
completion preserves the report and returns the same completion semantics.
A failure emits no Completed message. Treat file failure as BLOCKED.

The helper checks mechanics, not Plan acceptance. The manager owns acceptance
and closure. Open questions blocking acceptance, stops, blockers and handoffs
never use `complete` or send COMPLETED. The retained `finish` and `status`
commands remain compatible with older callers. `status --kind completed` only
renders a message; this Workflow's completion route is `complete`.

On a valid COMPLETED from the current manager, keep the runner completion phase
open until that manager's actual native final and confirmed quiescence of
children and writers. A control message alone is not the end of the run. Then
read the retained file with a complete capture:

```text
<verified-python> -X utf8 "<workflow-skill-directory>/scripts/check_text_size.py" --max-output-tokens <limit> --publish-full --project-root "<workspace_root>" --run -- <verified-python> -X utf8 "<workflow-skill-directory>/scripts/run_feedback.py" read --report-file "<run-report.md>"
```

Apply the same limit and complete-file reading rules as above. After a successful
read with nonempty `display_text`, give only a brief summary of the completed
scope and any remaining user-relevant issues, with a clickable link to the full
report. Then end the runner role.

A failed or empty read reports the problem and leaves completion unconfirmed.
Do not replace this helper operation with a direct file read or start a
normal-assistance audit first. Read only on a requested inspection or
completion, never as a progress poll. The runner's key and report path survive
stops and resumptions. A new completed-run activation creates a new file and
starts with no previous display key.
