#!/usr/bin/env sh
# Point this checkout at your own GitHub account and push.
#   sh publish.sh <github-username>
#
# Create the empty PUBLIC repo named "pokespin" on GitHub first (no README, no
# .gitignore, no license -- this repo already has them).
#
# Safe to run on a fork at any time: it discovers whichever owner the install
# URLs currently name and rewrites that to yours.
set -eu

NEW="${1:-}"
if [ -z "$NEW" ]; then
  echo "usage: sh publish.sh <github-username>" >&2
  exit 1
fi

# Whoever the install URLs point at right now.
OLD="$(sed -n 's|.*POKESPIN_REPO:-\([A-Za-z0-9_.-]*\)/pokespin.*|\1|p' install.sh | head -1)"
if [ -z "$OLD" ]; then
  echo "publish.sh: could not read the current owner out of install.sh" >&2
  exit 1
fi

if [ "$OLD" = "$NEW" ]; then
  echo "Already pointing at $NEW/pokespin; nothing to rewrite."
else
  for f in install.sh install.ps1 README.md commands/pokespin.md; do
    [ -f "$f" ] || continue
    sed -i "s|$OLD/pokespin|$NEW/pokespin|g" "$f"
  done
  echo "Rewrote install URLs: $OLD/pokespin -> $NEW/pokespin"
fi

if grep -rq "$OLD/pokespin" install.sh install.ps1 2>/dev/null; then
  echo "warning: a reference to $OLD survived:" >&2
  grep -rn "$OLD/pokespin" install.sh install.ps1 >&2
fi

git config user.name  >/dev/null 2>&1 || git config user.name  "$NEW"
git config user.email >/dev/null 2>&1 || git config user.email "$NEW@users.noreply.github.com"

git add -A
git diff --cached --quiet || git commit -q -m "Point install URLs at $NEW/pokespin"

git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$NEW/pokespin.git"

echo "Pushing to https://github.com/$NEW/pokespin ..."
git push -u origin main

cat <<EOF

Done. Share these:

  curl -fsSL https://raw.githubusercontent.com/$NEW/pokespin/main/install.sh | sh
  irm https://raw.githubusercontent.com/$NEW/pokespin/main/install.ps1 | iex

Inside Claude Code:

  /plugin marketplace add $NEW/pokespin
  /plugin install pokespin@pokespin
  /pokespin install
EOF
