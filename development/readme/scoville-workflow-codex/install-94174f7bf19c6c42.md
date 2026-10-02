Use the packages from
[Scoville Suite for Codex]({{ include: suite.repository }}/tree/main/packages).
Workflow only comes with the suite, and every Skill has to come from this
repository's own `packages/<name>/<name>/` directory. Don't swap in packages
from the individual repositories, and don't continue if members are missing.
Use the suite's prompt for a new installation, or its upgrade prompt if you
already have one installed.

### Agent capacity

For longer Workflow runs, we recommend raising the session's agent limit to
256 in `~/.codex/config.toml`. Add or update the setting in its existing
`[agents]` section:

```toml
[agents]
max_concurrent_threads_per_session = 256
```

The limit leaves room for agent threads retained during longer runs. See the [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
for the setting.
