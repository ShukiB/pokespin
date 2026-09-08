#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pokespin - replace Claude Code's thinking-spinner verbs with all 1025 Pokemon.

Claude Code (>= 2.1.x) supports a `spinnerVerbs` setting:

    "spinnerVerbs": { "mode": "replace" | "append", "verbs": [...] }

It samples one verb uniformly at random each turn, so this tool just installs
the list. Standard library only; no dependencies.

    python pokespin.py install       # replace the default verbs
    python pokespin.py install --mode append
    python pokespin.py status
    python pokespin.py preview -n 15
    python pokespin.py uninstall
    python pokespin.py install --refresh   # re-pull live from PokeAPI

Restart Claude Code after installing; settings are read at startup.

`autoinstall` is the guarded variant the plugin's SessionStart hook calls: it
runs at most once per machine, never overwrites an existing spinnerVerbs, and
swallows every error so it cannot break a session.
"""
import argparse, io, json, os, random, shutil, sys, time

__version__ = "1.1.0"
VERBS = ["__EMBED__"]


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

def fetch_live():
    """Re-derive the list from PokeAPI, so new generations can be picked up."""
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor
    try:
        from gerund import gerund
    except ImportError:
        sys.exit("error: --refresh needs gerund.py (the rule engine) beside this file.")

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
        return d["id"], (en[0] if en else d["name"].title())

    with ThreadPoolExecutor(max_workers=12) as ex:
        pairs = sorted(ex.map(one, rows))
    return [gerund(name) for _, name in pairs]


def get_verbs(refresh):
    verbs = fetch_live() if refresh else list(VERBS)
    if not verbs:
        sys.exit("error: empty verb list.")
    return verbs


# ---------------------------------------------------------------- commands

def cmd_install(a):
    verbs = get_verbs(a.refresh)
    path = settings_path(a.scope)
    data = load_settings(path)
    prev = data.get("spinnerVerbs")
    data["spinnerVerbs"] = {"mode": a.mode, "verbs": verbs}

    if a.dry_run:
        print("[dry-run] would write %s" % path)
        print("[dry-run] mode=%s verbs=%d" % (a.mode, len(verbs)))
        return
    b = backup(path)
    save_settings(path, data)
    print("Installed %d Pokemon verbs (mode=%s)" % (len(verbs), a.mode))
    print("  settings: %s" % path)
    if b:
        print("  backup:   %s" % b)
    if prev:
        print("  note: replaced an existing spinnerVerbs setting.")
    print("  sample:   %s" % ", ".join(random.sample(verbs, min(6, len(verbs)))))
    print("\nRestart Claude Code to see it.")


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
    print("Restart Claude Code to restore the default verbs.")


MARKER = os.path.join(os.path.expanduser("~"), ".claude", ".pokespin-autoinstall")


def cmd_autoinstall(a):
    """One-shot install used by the SessionStart hook.

    Deliberately conservative: it runs at most once per machine, never
    overwrites a spinnerVerbs you already set, and can never break a session --
    any failure exits 0 silently.
    """
    try:
        if os.path.exists(MARKER):
            return                      # already ran once; an uninstall stays uninstalled
        path = settings_path("user")
        data = load_settings(path)
        if "spinnerVerbs" not in data:  # never clobber the user's own choice
            data["spinnerVerbs"] = {"mode": "replace", "verbs": list(VERBS)}
            backup(path)
            save_settings(path, data)
        os.makedirs(os.path.dirname(MARKER), exist_ok=True)
        with io.open(MARKER, "w", encoding="utf-8") as f:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write("pokespin " + __version__ + " installed at " + stamp)
    except (Exception, SystemExit):
        pass       # SystemExit too: load_settings() exits on a corrupt file, and
                   # a cosmetic plugin must never break session startup


def cmd_status(a):
    path = settings_path(a.scope)
    print("settings: %s%s" % (path, "" if os.path.exists(path) else "  (missing)"))
    cfg = load_settings(path).get("spinnerVerbs")
    if not cfg:
        print("status:   not installed (Claude Code is using its default verbs)")
        return
    verbs = cfg.get("verbs", [])
    mine = sum(1 for v in verbs if v in set(VERBS))
    print("status:   installed")
    print("mode:     %s" % cfg.get("mode"))
    print("verbs:    %d  (%d from this pokedex of %d)" % (len(verbs), mine, len(VERBS)))
    if verbs:
        print("sample:   %s" % ", ".join(random.sample(verbs, min(6, len(verbs)))))


def cmd_preview(a):
    verbs = get_verbs(a.refresh)
    for v in random.sample(verbs, min(a.number, len(verbs))):
        print(v)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="pokespin",
        description="Replace Claude Code's spinner verbs with 1025 Pokemon.")
    p.add_argument("--version", action="version", version="pokespin " + __version__)
    sub = p.add_subparsers(dest="cmd")

    def common(sp, scope=True):
        if scope:
            sp.add_argument("--scope", choices=["user", "project"], default="user",
                            help="user = ~/.claude/settings.json (default); "
                                 "project = ./.claude/settings.json")
        sp.add_argument("--refresh", action="store_true",
                        help="re-pull species live from PokeAPI instead of the "
                             "embedded list")
        sp.add_argument("--dry-run", action="store_true",
                        help="show what would change, write nothing")

    sp = sub.add_parser("install", help="write the verbs into settings.json")
    sp.add_argument("--mode", choices=["replace", "append"], default="replace",
                    help="replace the built-in verbs (default) or add to them")
    common(sp)
    sp.set_defaults(func=cmd_install)

    sp = sub.add_parser("uninstall", help="remove the setting again")
    common(sp)
    sp.set_defaults(func=cmd_uninstall)

    sp = sub.add_parser("autoinstall",
                        help="internal: one-shot install used by the SessionStart hook")
    sp.set_defaults(func=cmd_autoinstall, refresh=False, dry_run=False, scope="user")

    sp = sub.add_parser("status", help="show what is currently installed")
    common(sp)
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("preview", help="print a random sample of verbs")
    sp.add_argument("-n", "--number", type=int, default=10)
    common(sp, scope=False)
    sp.set_defaults(func=cmd_preview)

    a = p.parse_args(argv)
    if not getattr(a, "func", None):
        p.print_help()
        return 0
    a.func(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
