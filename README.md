# pokespin

Replaces Claude Code's thinking-spinner verbs ("Pondering…", "Noodling…") with
Pokémon, inflected as verbs: *Mewing…*, *Charizarding…*, *Zubatting…*,
*Mr. Miming…*

Ships all **1025 species across 9 generations**, and installs **generation 1
(Kanto, 151)** by default -- a short, recognisable list. Pick any others with
`--gen`.

## Install

**Requires:** Python 3.8+ and Claude Code >= 2.1.x. Nothing else.

### One-liner (recommended)

macOS / Linux / Git Bash:

```bash
curl -fsSL https://raw.githubusercontent.com/ShukiB/pokespin/main/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/ShukiB/pokespin/main/install.ps1 | iex
```

Passing arguments through the pipe:

```bash
curl -fsSL .../install.sh | sh -s -- install --mode append
```
```powershell
$env:POKESPIN_ARGS = "install --mode append"; irm .../install.ps1 | iex
```

### As a Claude Code plugin

Adds a `/pokespin` command inside Claude Code:

```
/plugin marketplace add ShukiB/pokespin
/plugin install pokespin@pokespin
/pokespin install
```

### Manual

Copy `dist/pokespin.py` anywhere (it is fully self-contained) and run it:

```bash
python pokespin.py install                 # gen 1 (Kanto, 151) -- the default
python pokespin.py install --gen all       # all 9 gens, 1025 verbs
python pokespin.py install --gen 1-3       # a range
python pokespin.py install --gen 2,5,9     # a list
python pokespin.py install --mode append   # keep Claude Code's own verbs too
python pokespin.py gens                    # list generations and sizes
python pokespin.py status                  # shows which gens are installed
python pokespin.py preview -n 20 --gen 4
python pokespin.py uninstall
```

## Generations

| gen | region | count | | gen | region | count |
|----|--------|------:|-|----|--------|------:|
| **1** | **Kanto** *(default)* | **151** | | 6 | Kalos | 72 |
| 2 | Johto | 100 | | 7 | Alola | 88 |
| 3 | Hoenn | 135 | | 8 | Galar | 96 |
| 4 | Sinnoh | 107 | | 9 | Paldea | 120 |
| 5 | Unova | 156 | | | **all** | **1025** |

`--gen` takes `1`, a range `1-3`, a list `2,5,9`, or `all`. Invalid input is
rejected with a clear message rather than silently installing something else.

### For a whole team, without anyone installing anything

`spinnerVerbs` is honored from project settings, so commit it once:

```bash
python pokespin.py install --scope project   # writes ./.claude/settings.json
git commit -am "Pokemon spinner for everyone on this repo"
```

Everyone who works in that repo gets it; nothing to install per machine.

Restart Claude Code after any of these — settings are read once at startup.

Flags: `--scope user|project` (default `user` = `~/.claude/settings.json`),
`--gen`, `--dry-run`, `autoinstall` (the guarded one-shot the hook calls, which
installs generation 1), `--refresh` (re-pull species live from PokeAPI instead of the
embedded list -- needs `gerund.py` beside it; useful when Gen 10 lands).

The installer timestamps a backup of `settings.json` before every write, writes
atomically via a temp file + rename, and preserves all your other settings keys.

## How it works

Claude Code ≥ 2.1.x exposes a first-class setting — no patching, no forked binary:

```json
"spinnerVerbs": { "mode": "replace", "verbs": ["Mewing", "..."] }
```

Claude Code samples one verb uniformly at random per turn, so randomness is its
job; this tool only supplies the list.

## Data

Names come from **PokéAPI** (`/api/v2/pokemon-species`), the community-standard
Pokémon dataset. Verified at build time: count is exactly 1025, IDs contiguous
1–1025, every English name present, no duplicates, 9 generations.

## Inflection

`gerund.py` applies real English present-participle rules to the *head word*,
not a blind `+ing`:

| rule | example |
|---|---|
| default `+ing` | Mew → Mewing |
| drop silent `e` | Kricketune → Kricketuning, Blastoise → Blastoising |
| `-ie` → `-ying` | Caterpie → Caterpying, Alcremie → Alcremying |
| double final consonant after a stressed CVC | Zubat → Zubatting, Mudkip → Mudkipping |
| `-c` after a vowel → `+king` | Togetic → Togeticking, Lycanroc → Lycanrocking |
| unstressed tails never double | Aggron → Aggroning, Kyurem → Kyureming |
| multi-word: inflect the last word | Great Tusk → Great Tusking, Iron Hands → Iron Handsing |

Eight genuinely irregular names use a hand-written override table
(`Mr. Mime → Mr. Miming`, `Mime Jr. → Miming Jr.`, `Type: Null → Type-Nulling`,
`Porygon-Z → Porygon-Zing`, `Nidoran♀ → Nidoran-Fing`, …) rather than pretending
the rules cover them. All 1025 outputs are unique.

Settings are written with `ensure_ascii`, so accented names (Flabébé) are safe
on any console codepage.

## Repo layout

```
.claude-plugin/     plugin + marketplace manifests (validated)
commands/           the /pokespin slash command
hooks/hooks.json    SessionStart hook -> `pokespin autoinstall` (once, guarded)
install.sh          curl | sh one-liner
install.ps1         irm | iex one-liner
fetch_species.py   one-time pull + integrity check  -> data/species.json
gerund.py          the inflection rules
build.py           species + rules                  -> data/verbs.json, dist/pokespin.py
data/verbs.json    1025 {id, gen, pokemon, verb} records
dist/pokespin.py   the self-contained installer (this is what you ship)
```

Rebuild after editing rules: `python build.py`

## Hosting your own copy

Everything is a static file, so any host that serves raw text works. For GitHub:

1. Create an empty **public** repo named `pokespin` (no README, no license --
   this repo already has them).
2. Run:
   ```bash
   sh publish.sh <your-github-username>
   ```
   That rewrites the install URLs, commits, and pushes.

The one-liners and `/plugin marketplace add <your-username>/pokespin` then work
for anyone, with no release step and no build artifacts to publish.

Users can pin a fork or branch without editing anything:
`POKESPIN_REPO=someone/pokespin POKESPIN_REF=v1.0.0 sh install.sh`
