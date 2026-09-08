---
description: Install, remove, or inspect the Pokemon spinner verbs (1025 Pokemon)
allowed-tools: Bash(python:*), Bash(python3:*), Read
---

Run the pokespin installer that ships with this plugin.

The script is at `${CLAUDE_PLUGIN_ROOT}/dist/pokespin.py`. Invoke it with
Python, passing the user's arguments through: `$ARGUMENTS` (default to
`install` when empty).

Valid subcommands: `install` (flags: `--mode replace|append`,
`--scope user|project`, `--dry-run`), `uninstall`, `status`, `preview -n N`.

After an install or uninstall, tell the user in one line that Claude Code must
be restarted, since settings are read once at startup. Report the script's own
output rather than paraphrasing it.
