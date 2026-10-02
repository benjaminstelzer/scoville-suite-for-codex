### Claude sessions

If Ask reports an expired OAuth session, run `claude auth login` again and
check the result with `claude auth status`. If an outdated CLI rejects a
supported model, run `claude update` and check `claude --version` before retrying.
