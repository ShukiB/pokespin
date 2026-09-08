# -*- coding: utf-8 -*-
"""Build data/verbs.json and the self-contained dist/pokespin.py installer."""
import io, json, os
from gerund import gerund

ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5,
         "vi": 6, "vii": 7, "viii": 8, "ix": 9}

species = json.load(io.open("data/species.json", encoding="utf-8"))
assert len(species) == 1025 and [r["id"] for r in species] == list(range(1, 1026))

entries = []
for r in species:
    gen = ROMAN[r["generation"].split("-")[-1]]
    entries.append({"id": r["id"], "gen": gen,
                    "pokemon": r["name"], "verb": gerund(r["name"])})

verbs = [e["verb"] for e in entries]
assert len(set(verbs)) == len(verbs), "duplicate verbs"

# group by generation, preserving pokedex order within each
by_gen = {}
for e in entries:
    by_gen.setdefault(str(e["gen"]), []).append(e["verb"])
assert sorted(int(g) for g in by_gen) == list(range(1, 10)), "expected 9 generations"
assert sum(len(v) for v in by_gen.values()) == 1025

io.open("data/verbs.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(entries, ensure_ascii=False, indent=1))

os.makedirs("dist", exist_ok=True)
tpl = io.open("pokespin_template.py", encoding="utf-8").read()
blob = json.dumps(by_gen, ensure_ascii=True, sort_keys=True)
out = tpl.replace('GEN_VERBS = {"__EMBED__": []}',
                  "GEN_VERBS = json.loads(r'''%s''')" % blob)
assert "__EMBED__" not in out, "embed placeholder not substituted"
io.open("dist/pokespin.py", "w", encoding="utf-8", newline="\n").write(out)

print("verbs: %d across %d gens | dist/pokespin.py bytes: %d"
      % (len(verbs), len(by_gen), os.path.getsize("dist/pokespin.py")))
for g in sorted(by_gen, key=int):
    print("  gen %s: %4d  (%s ...)" % (g, len(by_gen[g]), by_gen[g][0]))
