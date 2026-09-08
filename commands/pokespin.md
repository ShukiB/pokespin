---
description: Install, remove, or inspect the Pokemon spinner verbs (pick generations 1-9)
allowed-tools: Bash(python:*), Bash(python3:*), Read
---

Run the pokespin installer that ships with this plugin.

The script is at `${CLAUDE_PLUGIN_ROOT}/dist/pokespin.py`. Invoke it with
Python, passing the user's arguments through: `$ARGUMENTS` (default to
`install` when empty).

Subcommands:

- `install` -- writes the verbs. Flags: `--gen SPEC`, `--mode replace|append`,
  `--scope user|project`, `--dry-run`
- `uninstall`, `status`, `gens`, `preview -n N [--gen SPEC]`

`--gen` selects which Pokemon generations to use, and accepts `1` (the
default -- Kanto, 151), a range `1-3`, a list `2,5,9`, or `all` (1025).
Generation sizes: 1 Kanto 151, 2 Johto 100, 3 Hoenn 135, 4 Sinnoh 107,
5 Unova 156, 6 Kalos 72, 7 Alola 88, 8 Galar 96, 9 Paldea 120.

If the user names a region rather than a number ("Johto", "Kanto"), map it to
that generation. If they ask for "everything" or "all Pokemon", use `--gen all`.
When they just say "install", let the default stand -- do not pass `--gen`.

After an install or uninstall, tell the user in one line that Claude Code must
be restarted, since settings are read once at startup. Report the script's own
output rather than paraphrasing it.
