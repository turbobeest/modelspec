# MODEL-448 public mirror evidence

## Round 2: union merge after the lineup mirror landed

Requested base: `f5f44f9a24aab0980bcea70c2fb639d97f3aa679`.
The remote ticket branch had already advanced to
`8c4c5824efbba379ebc22aade41d62b40b07508d`; fast-forwarding preserved those
intervening changes. Merged public main
`d55250c2e8fd5577639cd64afe2421332bc85b6e`, including the lineup mirror.
Final merge implementation SHA: `aefaeb1c5e456a26507f7e5ec9bae6769413964a`.
The final pushed SHA including this evidence update is in `.pr-commit.txt`.

Read `REV-976.verdict.md`: APPROVE, no defects, reviewing the original public
and private heads. This round changes only the integration with newer main.

Commands from `/Users/terbeest/dev/worktrees/model-448`, unless noted:

```sh
git fetch origin
git merge --ff-only origin/model-448-mirror
git -C /Users/terbeest/dev/worktrees/data-model-448 pull --ff-only
git merge --no-commit origin/main
```

The first three exited 0; private pull reported `Already up to date.`
The merge exited 1 with conflicts in `tests/test_engine_pin.py` and
`tests/test_writer_isolation.py`.

Before resolving the conflicts:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_model_week.py
```

Exit 2: `2 errors in 0.17s`. Both conflicting files failed pytest collection
with `SyntaxError` from the conflict markers. No new behavior was introduced,
so the regression check is the existing suite across the actual union merge.

Resolution retains both `model-week` and `lineup-proposer` in `NAMES` and
`ENGINE_JOBS`, and both complete isolation test functions. All functions and
classes in the three requested test files were compared as Python ASTs with
both parents: the resulting name set is their union, and every parent node
is unchanged. Both workflow files match their corresponding parent bytes.
The same pytest command then exited 0: `358 passed in 16.58s`.

Source guard after staging this evidence:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_removed_sources.py
```

Exit 0: `46 passed, 1 skipped in 51.50s`. The skipped built-site check
requires `MODELSPEC_DIST`; this merge does not build or change a site export.

Actual private-worktree mirror check:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -I /Users/terbeest/dev/worktrees/data-model-448/.github/scripts/check_writer_mirrors.py --mirrors .github/private-writers --workflows /Users/terbeest/dev/worktrees/data-model-448/.github/workflows
```

Exit 1: `::error::lineup-proposer.yml: private workflow is missing`.
The pulled private ticket branch is still
`82a2a61ee05c01870e46e807ccbc16173ce350b9`; its fetched main is
`7409030687c87e1ed05b87b0c126ad0273b3dfb9`. Neither contains the lineup
workflow. The incoming public lineup mirror matches
`origin/model-447-proposer:.github/workflows/lineup-proposer.yml` in the
private repository byte-for-byte. That separate workflow has not reached the
designated private worktree. No private workflow was added, removed or edited
in this round. This dependency blocks a successful all-writer mirror check.

`git diff --check` and `git diff --cached --check` exited 0. The merge was
committed with the required co-author trailer. Push uses
`CI_LOCAL_SKIP=1 git push -u origin model-448-mirror` after focused checks.
Tools: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, Git 2.50.1, Bash 5.3.9.
Zero `gh` calls. No PR state change, hosted CI check, live dispatch, full suite,
site build, provider call or Worker export was performed. Temporary logs were
removed; no background processes remain.

## Round 1 evidence

Public base: `468dd44ceb8600f661479f2f595dac617aff312b`.
Final implementation SHA: `2926cd377dc98fc1b36ed75002c8828c946290b3`.
The final pushed SHA, including this evidence-only commit, is in the untracked
`.pr-commit.txt` hand-off and can be read with `git rev-parse HEAD`.

This adds the byte-identical Model Week workflow under `.github/private-writers/`
and extends engine-pin and isolation checks. It does not change the generator
or add a public Actions workflow. The private companion PR owns execution.

Before copying the mirror, this command exited 1 with `2 failed in 0.15s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider 'tests/test_engine_pin.py::test_the_pin_is_verified_before_the_engine_checkout[model-week]' tests/test_writer_isolation.py::test_model_week_imports_only_the_engine_with_private_history_as_input
```

Both tests failed because `model-week.yml` was absent. Both pass in the final
focused run. Additional tests execute the history-completion shell against
shallow, full and unreachable fixture repositories and verify pinned HEAD stays
unchanged. The isolation test executes the generator command with hostile
private code and `PYTHONPATH` and proves only the engine module is imported.

## Verification

Tools: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, Git 2.50.1,
Bash 5.3.9, actionlint 1.7.12, ShellCheck 0.11.0, GitHub CLI 2.102.0.
All pytest runs used the specified interpreter, ran serially, and had their
exit codes checked directly. No full local suite was run.

From the data worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_model_week_workflow.py .github/scripts/tests/test_writer_mirrors.py
```

Exit 0: `27 passed in 0.94s`. Covers Monday/manual scheduling, one fixed draft
branch, no merge command, exact generator flags, error propagation, ISO year
boundaries, invalid inputs, repeated staging and working appendix links.

From the public mirror worktree:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_model_week.py tests/test_removed_sources.py
```

Exit 0: `400 passed, 1 skipped in 70.95s`. Covers main ancestry, canonical
pin checks, complete history without moving engine HEAD, import isolation
against hostile private files, and the unchanged generator's privacy checks.

After staging the new public mirror:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_removed_sources.py
```

Exit 0: `46 passed, 1 skipped in 52.93s`. The skip needs `MODELSPEC_DIST`;
this workflow change does not build or change a site export.

From the data worktree:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -I .github/scripts/check_writer_mirrors.py --mirrors /Users/terbeest/dev/worktrees/model-448/.github/private-writers --workflows .github/workflows
actionlint .github/workflows/model-week.yml
git diff --check
```

Each exits 0. Mirror check: `12 public writer mirror(s) match private workflows.`
The public mirror is byte-identical, including the canonical pin verification,
checkout and confirmation steps. The checker identifies this workflow as a
writer because it checks out `turbobeest/modelspec` into `engine`.

The private scratch run for `2026-W44` produced the digest and preserved its
appendices using engine pin `6815544116839f991c10904772e7357f12d5b566`.
Detailed reproduction is in the private companion PR's evidence file. No
private report content is included here. Scratch checkouts were deleted.

No live dispatch, hosted CI or scheduled PR update was observed. No full local
suite, site build, provider call, source fetch or Worker export was run.
Human merges must coordinate this mirror with the private workflow because
private recall compares against public main. Both PRs remain drafts.
