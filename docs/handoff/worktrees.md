# Worktrees and CodeGraph

Each ModelSpec agent session uses **its own git worktree**. Never `git checkout`
inside `/Users/terbeest/dev/modelspec` or any other session's tree.

## Create a worktree

```bash
git -C /Users/terbeest/dev/modelspec fetch origin main
git -C /Users/terbeest/dev/modelspec worktree add -b <branch> \
  /Users/terbeest/dev/worktrees/<name> origin/main
cd /Users/terbeest/dev/worktrees/<name>
```

Run tests from that tree so imports resolve there:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q
# Parallel (what "Run pytest" CI uses). Serial above still works.
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n auto --dist loadfile
```

Leave other `modelspec-*` worktrees under `/Users/terbeest/dev/worktrees`
alone. They belong to other sessions. Observed 2026-09-14, before this
MODEL-40 tree: ten `modelspec-*` directories. That count is not an inventory
to maintain; it is why this file exists.

## CodeGraph is per checkout

`.codegraph/` is gitignored and local. An index built in checkout A is **not**
current for checkout B, even when both are the same commit: the daemon socket,
file watcher, and absolute paths belong to one tree.

The primary clone `/Users/terbeest/dev/modelspec` may have a `.codegraph/`
directory. Do not query it while working in a worktree, and do not tell a
fresh session that "the repo is indexed."

In **this** worktree, only if you need CodeGraph:

```bash
# once per worktree (non-interactive)
codegraph init -y .

# after you edit files in this tree
codegraph sync .
```

`codegraph explore` must be pointed at this worktree (`projectPath` or cwd).
If there is no `.codegraph/` here, skip CodeGraph and use the files.

Graphify is a separate, bounded documentation+implementation map with its own
allowlist. It does not replace a worktree-local CodeGraph index, and CodeGraph
does not index `models/` or `benchmarks/` as verified facts.
