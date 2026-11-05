# MODEL-448 public mirror evidence

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
