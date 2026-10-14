# MODEL-337 merge evidence

PR #717 conflicted with `origin/main` in `cli/modelspec/agent-bundle.json`. That file is generated. Each merge takes main's copy, then `python -m pipeline.agent_copy write` regenerates it. `cli_version` stays `1.0.0`. The `pyproject.toml` source hash matches that file. Compared with main's bundle, those are the only two differences. The bounded decide behavior in `cli/modelspec/spec.py`, `docs/cli-contract.md`, and the README merged cleanly. `mcp/src/agent-copy.json` still contains the bounded-decide guidance, including `fields:null` and four mentions of bounded decide.

Worktree: `/Users/terbeest/dev/worktrees/model-337`.
Branch: `sparksandsawdust/model-337-bounded-cli`.
Pre-merge HEAD: `a999f257c4e0b6af4e5e70a6ceeb46347ea04fae`.

`origin/main` was `e8eaa9ce870b4ccf21616525ab2f798ced438700` at the first merge. That merge commit is `15f456fce214ccc97b5c6042f3e9a48491753f3f`. Pytest on that tree exited 0: `10006 passed, 8 skipped, 11 warnings in 2075.45s (0:34:35)`. During that run, `main` advanced to `434dd2b0313b941bbe246bfddddf8272a7d89c4a` (MODEL-364, compare named models). The bundle conflicted again. `cli/modelspec/cli.py` and `docs/cli-contract.md` auto-merged. The decide command still calls `bound_decide_request`. The new `compare` command for `POST /v1/compare-models` is present. The second merge commit is `876b4d3a7c663b5277309ccd5053ab95a4495f08`.

The final delivery commit adds only this evidence update. Resolve its SHA with `git log -1 --format=%H`. A report committed to Git cannot contain its own commit hash.

The spec lists no red-first test. The work is the merge. No product test was written for this pass.

## Commands

All commands ran from the worktree. Each pytest exit code is the `EXIT:` line written by `$?` immediately after pytest. The generator commands' exit codes were read from the shell status.

Tools: Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Git 2.50.1, GitHub CLI 2.102.0. The host reported macOS 27.2, arm64.

```bash
git fetch origin main
git merge origin/main --no-edit
git checkout --theirs -- cli/modelspec/agent-bundle.json
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

The same sequence ran twice. The first `write` and `check` exited 0, and the first pytest exited 0 with the count above. After MODEL-364, `write` and `check` exited 0 again. The second pytest exited 0: `10141 passed, 8 skipped, 11 warnings in 1855.52s (0:30:55)`.

Each `write` also refreshed `mcp/src/agent-copy.json`, `docs/agents.md`, `cli/modelspec/spec.schema.json`, `cli/modelspec/feedback.schema.json`, `site/holding/index.html`, and `api/worker/src/agent_guide.py`. Those outputs matched the merged tree, so the merge commits do not change them.

After the second suite, `git fetch origin main` still showed `434dd2b0313b941bbe246bfddddf8272a7d89c4a`, and `git merge-tree --name-only HEAD origin/main` exited 0.

## Not observed

No hand edit of hashes. No force-push. No change to the PR ready state. No Linear write. No call to the live API. No `gh pr edit`, merge, or close. No conflict other than `cli/modelspec/agent-bundle.json`.
