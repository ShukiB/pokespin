#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pokespin - replace Claude Code's thinking-spinner verbs with Pokemon.

Claude Code (>= 2.1.x) supports a `spinnerVerbs` setting:

    "spinnerVerbs": { "mode": "replace" | "append", "verbs": [...] }

It samples one verb uniformly at random each turn, so this tool just installs
the list. Standard library only; no dependencies.

    python pokespin.py install               # gen 1 (Kanto, 151) -- the default
    python pokespin.py install --gen all     # all 9 gens, 1025 verbs
    python pokespin.py install --gen 1-3     # ranges and lists: 1-3, or 2,5,9
    python pokespin.py install --mode append
    python pokespin.py gens                  # list the generations
    python pokespin.py status
    python pokespin.py preview -n 15 --gen 2
    python pokespin.py uninstall
    python pokespin.py install --refresh     # re-pull live from PokeAPI

Claude Code re-reads the setting live, so the new verbs show up on the next
spinner -- no restart needed (restart anyway if you don't see them).
Nothing is written unless you ask for it: there are no hooks and no background
work, and `uninstall` puts Claude Code's own verbs back.
"""
import argparse, io, json, os, random, shutil, sys, time

__version__ = "1.2.0"

# Generation -> verbs. Keys are strings so the embedded JSON round-trips.
GEN_VERBS = {"__EMBED__": []}

GEN_NAMES = {1: "Kanto", 2: "Johto", 3: "Hoenn", 4: "Sinnoh", 5: "Unova",
             6: "Kalos", 7: "Alola", 8: "Galar", 9: "Paldea"}

ALL_GENS = sorted(int(g) for g in GEN_VERBS)
DEFAULT_GENS = [1]                      # Kanto only, unless asked otherwise
VERBS = [v for g in ALL_GENS for v in GEN_VERBS[str(g)]]


# ---------------------------------------------------------------- generations

def parse_gens(spec):
    """Turn a --gen spec into a sorted list of ints.

    Accepts: 1 | 1,3 | 1-3 | 2,5-7 | all
    """
    if spec is None:
        return list(DEFAULT_GENS)
    spec = str(spec).strip().lower()
    if spec in ("all", "*"):
        return list(ALL_GENS)
    out = set()
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        try:
            if "-" in part:
                lo, hi = part.split("-", 1)
                lo, hi = int(lo), int(hi)
                if lo > hi:
                    lo, hi = hi, lo
                out.update(range(lo, hi + 1))
            else:
                out.add(int(part))
        except ValueError:
            sys.exit("error: could not read --gen %r. Use 1, 1-3, 2,5,9, or all."
                     % spec)
    bad = sorted(g for g in out if g not in ALL_GENS)
    if bad:
        sys.exit("error: no such generation: %s (valid: 1-%d, or 'all')."
                 % (", ".join(str(b) for b in bad), max(ALL_GENS)))
    if not out:
        sys.exit("error: --gen selected nothing.")
    return sorted(out)


def verbs_for(gens):
    return [v for g in gens for v in GEN_VERBS[str(g)]]


def describe_gens(gens):
    if gens == list(ALL_GENS):
        return "all %d generations" % len(ALL_GENS)
    return ", ".join("gen %d (%s)" % (g, GEN_NAMES.get(g, "?")) for g in gens)


# ---------------------------------------------------------------- settings io

def settings_path(scope):
    if scope == "project":
        return os.path.join(os.getcwd(), ".claude", "settings.json")
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def load_settings(path):
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
    except ValueError as e:
        sys.exit("error: %s is not valid JSON (%s).\nFix or move it, then retry."
                 % (path, e))
    if not isinstance(data, dict):
        sys.exit("error: %s must contain a JSON object." % path)
    return data


def save_settings(path, data):
    """Write atomically so a crash can never leave settings.json truncated."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".pokespin.tmp"
    # ensure_ascii keeps accented names (Flabebe) safe on any console codepage.
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=True, indent=2) + "\n")
    os.replace(tmp, path)


def backup(path):
    if not os.path.exists(path):
        return None
    dest = "%s.bak-%s" % (path, time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, dest)
    return dest


# ---------------------------------------------------------------- verb source

def fetch_live(gens):
    """Re-derive the list from PokeAPI, so new generations can be picked up."""
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor
    try:
        from gerund import gerund
    except ImportError:
        sys.exit("error: --refresh needs gerund.py (the rule engine) beside this file.")

    roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5,
             "vi": 6, "vii": 7, "viii": 8, "ix": 9}
    ua = {"User-Agent": "pokespin/%s" % __version__}

    def get(url, tries=4):
        for a in range(tries):
            try:
                req = urllib.request.Request(url, headers=ua)
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.load(r)
            except Exception:
                if a == tries - 1:
                    raise
                time.sleep(1.5 * (a + 1))

    index = get("https://pokeapi.co/api/v2/pokemon-species?limit=20000")
    rows = index["results"]
    print("PokeAPI reports %d species; fetching names..." % index["count"])

    def one(row):
        d = get(row["url"])
        en = [n["name"] for n in d["names"] if n["language"]["name"] == "en"]
        gen = roman.get(d["generation"]["name"].split("-")[-1], 0)
        return d["id"], gen, (en[0] if en else d["name"].title())

    with ThreadPoolExecutor(max_workers=12) as ex:
        rec = sorted(ex.map(one, rows))
    want = set(gens)
    return [gerund(name) for _, gen, name in rec if gen in want]


def get_verbs(a):
    gens = parse_gens(getattr(a, "gen", None))
    verbs = fetch_live(gens) if getattr(a, "refresh", False) else verbs_for(gens)
    if not verbs:
        sys.exit("error: empty verb list.")
    return gens, verbs


# ---------------------------------------------------------------- commands

def cmd_install(a):
    gens, verbs = get_verbs(a)
    path = settings_path(a.scope)
    data = load_settings(path)
    prev = data.get("spinnerVerbs")
    data["spinnerVerbs"] = {"mode": a.mode, "verbs": verbs}

    if a.dry_run:
        print("[dry-run] would write %s" % path)
        print("[dry-run] mode=%s gens=%s verbs=%d"
              % (a.mode, ",".join(str(g) for g in gens), len(verbs)))
        return
    b = backup(path)
    save_settings(path, data)
    print("Installed %d Pokemon verbs from %s (mode=%s)"
          % (len(verbs), describe_gens(gens), a.mode))
    print("  settings: %s" % path)
    if b:
        print("  backup:   %s" % b)
    if prev:
        print("  note: replaced an existing spinnerVerbs setting.")
    print("  sample:   %s" % ", ".join(random.sample(verbs, min(6, len(verbs)))))
    print("\nClaude Code picks this up live -- watch the next spinner.")


def cmd_uninstall(a):
    path = settings_path(a.scope)
    data = load_settings(path)
    if "spinnerVerbs" not in data:
        print("Nothing to remove; spinnerVerbs is not set in %s" % path)
        return
    if a.dry_run:
        print("[dry-run] would remove spinnerVerbs from %s" % path)
        return
    b = backup(path)
    del data["spinnerVerbs"]
    save_settings(path, data)
    print("Removed spinnerVerbs from %s" % path)
    if b:
        print("  backup: %s" % b)
    print("Claude Code's own verbs are back on the next spinner.")


def cmd_status(a):
    path = settings_path(a.scope)
    print("settings: %s%s" % (path, "" if os.path.exists(path) else "  (missing)"))
    cfg = load_settings(path).get("spinnerVerbs")
    if not cfg:
        print("status:   not installed (Claude Code is using its default verbs)")
        return
    verbs = cfg.get("verbs", [])
    have = set(verbs)
    print("status:   installed")
    print("mode:     %s" % cfg.get("mode"))
    mine = sum(1 for v in verbs if v in set(VERBS))
    print("verbs:    %d  (%d from this pokedex of %d)" % (len(verbs), mine, len(VERBS)))

    present = []
    for g in ALL_GENS:
        pool = GEN_VERBS[str(g)]
        n = sum(1 for v in pool if v in have)
        if n:
            present.append("%d/%d gen %d (%s)" % (n, len(pool), g, GEN_NAMES[g]))
    print("gens:     %s" % ("; ".join(present) if present else "none recognised"))
    if verbs:
        print("sample:   %s" % ", ".join(random.sample(verbs, min(6, len(verbs)))))


def cmd_preview(a):
    _, verbs = get_verbs(a)
    for v in random.sample(verbs, min(a.number, len(verbs))):
        print(v)


def cmd_gens(a):
    print("gen  region    count  example")
    for g in ALL_GENS:
        pool = GEN_VERBS[str(g)]
        mark = " *" if g in DEFAULT_GENS else "  "
        print("%2d%s %-9s %5d  %s"
              % (g, mark, GEN_NAMES.get(g, "?"), len(pool), pool[0]))
    print("")
    print("%d total. '*' is the default." % len(VERBS))
    print("Select with --gen 1 / --gen 1-3 / --gen 2,5,9 / --gen all")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="pokespin",
        description="Replace Claude Code's spinner verbs with Pokemon "
                    "(generation 1 by default).")
    p.add_argument("--version", action="version", version="pokespin " + __version__)
    sub = p.add_subparsers(dest="cmd")

    def common(sp, scope=True, gen=True, refresh=True, dry_run=True):
        # Only the flags a command actually honours: argparse would happily
        # accept --refresh on `status` and silently do nothing with it.
        if scope:
            sp.add_argument("--scope", choices=["user", "project"], default="user",
                            help="user = ~/.claude/settings.json (default); "
                                 "project = ./.claude/settings.json")
        if gen:
            sp.add_argument("--gen", "-g", default=None, metavar="SPEC",
                            help="which generations: 1 (default), 1-3, 2,5,9, or all")
        if refresh:
            sp.add_argument("--refresh", action="store_true",
                            help="re-pull species live from PokeAPI instead of the "
                                 "embedded list")
        if dry_run:
            sp.add_argument("--dry-run", action="store_true",
                            help="show what would change, write nothing")

    sp = sub.add_parser("install", help="write the verbs into settings.json")
    sp.add_argument("--mode", choices=["replace", "append"], default="replace",
                    help="replace the built-in verbs (default) or add to them")
    common(sp)
    sp.set_defaults(func=cmd_install)

    sp = sub.add_parser("uninstall", help="remove the setting again")
    common(sp, gen=False, refresh=False)
    sp.set_defaults(func=cmd_uninstall, refresh=False)

    sp = sub.add_parser("status", help="show what is currently installed")
    common(sp, gen=False, refresh=False, dry_run=False)
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("preview", help="print a random sample of verbs")
    sp.add_argument("-n", "--number", type=int, default=10)
    common(sp, scope=False, dry_run=False)
    sp.set_defaults(func=cmd_preview)

    sp = sub.add_parser("gens", help="list the generations and their sizes")
    sp.set_defaults(func=cmd_gens)

    a = p.parse_args(argv)
    if not getattr(a, "func", None):
        p.print_help()
        return 0
    a.func(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
