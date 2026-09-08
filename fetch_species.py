"""Pull all Pokemon species from PokeAPI (trusted source) and verify completeness."""
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

API = "https://pokeapi.co/api/v2/pokemon-species"
UA  = {"User-Agent": "pokespin-builder/1.0 (one-time dataset build)"}

def get(url, tries=5):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            if a == tries - 1: raise
            time.sleep(1.5 * (a + 1))

index = get(f"{API}?limit=20000")
count = index["count"]
results = index["results"]
print(f"index count={count} rows={len(results)}")
assert count == len(results), "index truncated"

def one(row):
    d = get(row["url"])
    en = [n["name"] for n in d["names"] if n["language"]["name"] == "en"]
    return {"id": d["id"], "slug": d["name"], "name": en[0] if en else None,
            "generation": d["generation"]["name"]}

out = []
with ThreadPoolExecutor(max_workers=12) as ex:
    for i, rec in enumerate(ex.map(one, results), 1):
        out.append(rec)
        if i % 100 == 0: print(f"  {i}/{len(results)}", flush=True)

out.sort(key=lambda r: r["id"])
json.dump(out, open("data/species.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote data/species.json", len(out))
