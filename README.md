# pokespin

Replaces Claude Code's thinking-spinner verbs ("Pondering…", "Noodling…") with
all **1025 Pokémon**, inflected as verbs: *Mewing…*, *Charizarding…*,
*Zubatting…*, *Mr. Miming…*

## Install (any machine)

Requires Python 3.8+ and nothing else. Copy `dist/pokespin.py` anywhere, then:

```bash
python pokespin.py install       # replace the built-in verbs
python pokespin.py install --mode append   # keep the defaults too, 1145 total
python pokespin.py status
python pokespin.py preview -n 20
python pokespin.py uninstall
```

Restart Claude Code afterwards — settings are read once at startup.

Flags: `--scope user|project` (default `user` = `~/.claude/settings.json`;
`project` = `./.claude/settings.json`), `--dry-run`, `--refresh` (re-pull
species live from PokéAPI instead of the embedded list — needs `gerund.py`
beside it; useful when Gen 10 lands).

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
fetch_species.py   one-time pull + integrity check  -> data/species.json
gerund.py          the inflection rules
build.py           species + rules                  -> data/verbs.json, dist/pokespin.py
data/verbs.json    1025 {id, pokemon, verb} records
dist/pokespin.py   the self-contained installer (this is what you ship)
```

Rebuild after editing rules: `python build.py`
