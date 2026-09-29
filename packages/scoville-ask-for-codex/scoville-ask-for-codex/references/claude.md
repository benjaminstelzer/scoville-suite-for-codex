# Claude CLI

Use only `ask.py` operation `claude` with the request returned by `prepare`.
It wraps the bundled Claude adapter, sends the question through stdin and uses
the explicit workspace, model, effort and budget. Claude must already be
available and authenticated. Opus 5.5 requires Claude Code 2.1.280 or newer; check `claude --version` and report an older installation. Use the official `claude update` only within the current setup authorization, then verify the version before retrying. Never replace a failed native route with CLI.

The adapter allows Read, Grep and Glob and uses `dontAsk`. WebSearch and
WebFetch require an explicit `claude.web_tools: true` configuration or request
override. Read the default from the imported settings in configuration.md.
Customizations are disabled by default. Local launch does not mean offline;
Claude and optional web tools communicate with their services. These tool
restrictions do not justify a claim of sandbox isolation.

Read the `claude.timeout_seconds` default from the imported settings in
[configuration.md](configuration.md). A positive finite `timeout_seconds` on the request overrides it for that call. At the
deadline the adapter terminates its process family and returns `ok:false` with
`code:claude_timeout`; it does not retry. Any unconfirmed cleanup is reported.
After timeout, retain any previously confirmed session ID and requested
settings, mark actual metadata unknown when unavailable, and do not claim the
interrupted turn was saved. A status request does not authorize resuming the
timed-out consultation. A failure does not authorize a higher budget or another
provider.

Retain the JSON answer, permission denials, requested/reported settings and
exact session ID. Permission denials are evidence gaps even when an answer is
present. Missing session IDs mean continuation is unavailable, not success at
creating a resumable session. A process error, timeout, malformed JSON or empty
answer is a failed consultation; never reconstruct an answer from logs.

For an explicitly requested follow-up, reuse the retained adviser settings,
working directory and session ID; set `session_id` on the next `claude` request
with a new prompt/reference/scope. Do not use “most recent session”, resume by
display name or silently create a fresh session. No automatic retry after an
uncertain process result. CLI sessions have no Codex sidebar row.
The Claude session ID is the continuation handle; no native task handle or
native return destination applies to this route.

## Review closure

The caller asks the post-review question under SKILL.md only when continuation
is available. If continuation_available is false, report that follow-up would
need a fresh consultation instead of offering to keep this session open.

The adapter runs a print-mode process that exits after its answer. A retained
session ID identifies saved conversation history, not a running background
agent or Codex chat. On review closure, stop treating that ID as an active
follow-up target; preserve it only with the review evidence. Do not resume it
on an unrelated message. There is no native archive operation for this route:
do not call set_thread_archived, claude stop/rm, or delete session files.
Describe it as a closed consultation, not an archived or deleted Claude session.
An explicit later request to continue that saved session may use the retained
ID and original settings. Never use the most recent session implicitly.

If CLI authentication is missing or its OAuth session cannot refresh, report the error and ask the user to run `claude auth login` in a separate terminal, complete browser sign-in and verify with `claude auth status`. Keep running sessions open. Resume the requested check after authentication succeeds; never inspect or copy credential files.
