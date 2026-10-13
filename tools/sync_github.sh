#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
gh auth status >/dev/null 2>&1 || { echo 'GitHub 授权失效。请运行 gh auth login -h github.com'; exit 1; }
if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create dark-fantasy-rpg --private --source=. --remote=origin
fi
visibility=$(gh repo view --json visibility --jq .visibility)
[ "$visibility" = PRIVATE ] || { echo '停止：目标仓库不是私有仓库'; exit 1; }
git push -u origin HEAD
gh repo view --json url --jq .url
