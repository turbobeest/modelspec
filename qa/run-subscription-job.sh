#!/bin/zsh
# Run the merged public engine from a fresh detached worktree. No login or API fallback.
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
public_repo="$(cd "$(dirname "$0")/.." && pwd)"
job_directory="$(mktemp -d "${TMPDIR:-/tmp}/modelspec-subscription.XXXXXX")"
cleanup() {
  git -C "$public_repo" worktree remove --force "$job_directory/engine" 2>/dev/null || true
  rmdir "$job_directory" 2>/dev/null || true
}
trap cleanup EXIT
git -C "$public_repo" fetch -q origin main
git -C "$public_repo" worktree add -q --detach "$job_directory/engine" origin/main
cd "$job_directory/engine"
PYTHONPATH="$PWD" "$public_repo/.venv/bin/python" -m qa.subscription_jobs "$@"
