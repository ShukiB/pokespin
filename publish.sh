#!/usr/bin/env sh
# One-shot: bake your GitHub username into the install URLs and push.
#   sh publish.sh <github-username>
# Create the empty PUBLIC repo named "pokespin" on GitHub first (no README,
# no .gitignore, no license -- this repo already has them).
set -eu

USER="${1:-}"
if [ -z "$USER" ]; then
  echo "usage: sh publish.sh <github-username>" >&2
  exit 1
fi

# Only the URL placeholders, so prose is left alone.
sed -i "s#githubusercontent.com/OWNER/#githubusercontent.com/$USER/#g; s#POKESPIN_REPO:-OWNER/#POKESPIN_REPO:-$USER/#g" install.sh README.md
sed -i "s#githubusercontent.com/OWNER/#githubusercontent.com/$USER/#g; s#\"OWNER/pokespin\"#\"$USER/pokespin\"#g" install.ps1
sed -i "s#marketplace add OWNER/#marketplace add $USER/#g; s#github.com/OWNER/#github.com/$USER/#g" README.md

if ! grep -rq "OWNER" install.sh install.ps1; then
  echo "URLs baked for $USER"
else
  echo "warning: an OWNER placeholder survived:" >&2
  grep -rn "OWNER" install.sh install.ps1 >&2
fi

git config user.name  >/dev/null 2>&1 || git config user.name  "$USER"
git config user.email >/dev/null 2>&1 || git config user.email "$USER@users.noreply.github.com"

git add -A
git diff --cached --quiet || git commit -q -m "Point install URLs at $USER/pokespin"

git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$USER/pokespin.git"

echo "Pushing to https://github.com/$USER/pokespin ..."
git push -u origin main

cat <<EOF

Done. Share these:

  curl -fsSL https://raw.githubusercontent.com/$USER/pokespin/main/install.sh | sh
  irm https://raw.githubusercontent.com/$USER/pokespin/main/install.ps1 | iex

Inside Claude Code:

  /plugin marketplace add $USER/pokespin
  /plugin install pokespin@pokespin
EOF
