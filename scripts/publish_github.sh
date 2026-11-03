#!/usr/bin/env bash
set -euo pipefail
release_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$release_dir"
gh auth status --hostname github.com
account="$(gh api user --jq .login)"
if [[ "$account" != "Joe05062000" ]]; then
  echo 'Stop: authenticate as Joe05062000 before publishing.' >&2
  exit 1
fi
python3 scripts/check_release.py
if [[ "$(git branch --show-current)" != main ]] || [[ -n "$(git status --porcelain)" ]]; then
  echo 'Stop: publish requires a clean committed main branch.' >&2
  exit 1
fi
if git remote get-url origin >/dev/null 2>&1; then
  echo 'Stop: origin already exists. Inspect the remote and history before pushing.' >&2
  exit 1
fi
if gh repo view Joe05062000/hotel-market-opportunity-explorer --json nameWithOwner >/dev/null 2>&1; then
  echo 'Stop: destination already exists. Inspect it; no history will be overwritten.' >&2
  exit 1
fi
gh repo create Joe05062000/hotel-market-opportunity-explorer --public --source . --remote origin --push --description 'NYC hospitality research metadata, a no-key guided assistant and transparent hotel revenue scenarios'
