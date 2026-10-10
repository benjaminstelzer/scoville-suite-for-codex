# Shell command rules

Run complete commands in the current tool shell. If another shell is necessary,
use its known suitable launcher. Preserve generated commands and argument quoting.
In PowerShell, invoke a quoted executable path with `&`.

Give `rg` existing file or directory paths and select files with `-g`, for example:
`rg -n -g "*.php" -- "search text" "<existing-directory>"`.
The command-capture helper passes arguments unchanged and expands no wildcards.

Use native shell commands for simple inventories. For composed text or more
complex logic, use a literal-safe file or script rather than nested inline code.

PowerShell `Out-String` formats objects; POSIX command substitution removes
trailing newlines. Use complete raw-output capture when byte preservation matters.

For native Codex calls, forward rendered checker output unchanged as text.
Do not JSON-encode it again or add unchecked status lines. Structured helper
results and native tool arguments keep their own interfaces.

Keep the complete `exec_command` result until the command ends, including
`session_id`, every output chunk and the final exit status. A completed outer script does not prove child completion. Use the
template below for checked reads and captures, one per outer call.

This template selects 20000;
use the same smallest applicable limit in the generated command, both tools and
outer directive. Before execution, replace `<command_json>` with one JSON string
literal encoding the complete generated command, including quotes and backslashes.
Replace the whole value; never paste a command inside existing quotes or a
JavaScript template literal. JSON encoding preserves backticks and `${` as data.

```javascript
// @exec: {"max_output_tokens": 20000}
let r = await tools.exec_command({
  cmd: <command_json>,
  max_output_tokens: 20000
});
let output = r.output;
while (r.session_id !== undefined) {
  r = await tools.write_stdin({
    session_id: r.session_id, chars: "", yield_time_ms: 10000,
    max_output_tokens: 20000
  });
  output += r.output;
}
text(output);
```

Check completeness separately from command success:

| Result | Completion condition |
| --- | --- |
| Running `session_id` | Retain its ID and every chunk until completion; never restart the command. |
| `part=` from `--part` | Read all unchanged parts through `last`. |
| `exit=` from `--run` | Both streams are captured; the child exit status determines command success. A nonzero exit can supply valid failure evidence. |
| Complete-file metadata | Read the entire supplied file. |
| Empty output, capture or reader failure, `output_complete=false` | Required input remains unread; stop dependent work. |

Never discard a failure's stdout or stderr.
