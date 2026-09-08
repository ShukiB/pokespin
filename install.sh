#!/usr/bin/env sh
# pokespin one-line installer (macOS / Linux / Git Bash)
#   curl -fsSL https://raw.githubusercontent.com/OWNER/pokespin/main/install.sh | sh
# Pass args:
#   curl -fsSL .../install.sh | sh -s -- install --mode append
set -eu

REPO="${POKESPIN_REPO:-OWNER/pokespin}"
REF="${POKESPIN_REF:-main}"
URL="https://raw.githubusercontent.com/${REPO}/${REF}/dist/pokespin.py"

PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "pokespin: needs Python 3.8+ on PATH" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TMP/pokespin.py"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TMP/pokespin.py" "$URL"
else
  echo "pokespin: needs curl or wget" >&2; exit 1
fi

[ $# -eq 0 ] && set -- install
exec "$PY" "$TMP/pokespin.py" "$@"
