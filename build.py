# -*- coding: utf-8 -*-
"""Build data/verbs.json and the self-contained dist/pokespin.py installer."""
import io, json, os
from gerund import gerund

species = json.load(io.open("data/species.json", encoding="utf-8"))
assert len(species) == 1025 and [r["id"] for r in species] == list(range(1, 1026))

entries = [{"id": r["id"], "pokemon": r["name"], "verb": gerund(r["name"])} for r in species]
verbs = [e["verb"] for e in entries]
assert len(set(verbs)) == len(verbs), "duplicate verbs"

io.open("data/verbs.json", "w", encoding="utf-8").write(
    json.dumps(entries, ensure_ascii=False, indent=1))

os.makedirs("dist", exist_ok=True)
tpl = io.open("pokespin_template.py", encoding="utf-8").read()
blob = json.dumps(verbs, ensure_ascii=True, indent=0).replace("\n", "")
out = tpl.replace('VERBS = ["__EMBED__"]', "VERBS = json.loads(r'''%s''')" % blob)
io.open("dist/pokespin.py", "w", encoding="utf-8", newline="\n").write(out)
print("verbs:", len(verbs), "| dist/pokespin.py bytes:", os.path.getsize("dist/pokespin.py"))
