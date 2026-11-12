# MODEL-467-ENG2

Base `1bdea96ff6ee0a6dc1400f16260d88fdb6fb5a93` on `model-467-eng2`.
The head SHA is the single commit on that branch that adds this file.

Environment: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3. Tests are serial and offline.

## Red, then green

`test_weekly_workflow_keeps_the_arena_revision_pinned` and `test_every_private_writer_refresh_reads_the_arena_revision_variable` ran against the unchanged workflows.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_arena_revision.py::test_weekly_workflow_keeps_the_arena_revision_pinned tests/test_arena_revision.py::test_every_private_writer_refresh_reads_the_arena_revision_variable
```

Exit 1. 2 failed.

The weekly file still contained `MODELSPEC_ARENA_REVISION: pinned`. The release-signal step "Process one isolated work item" had no `MODELSPEC_ARENA_REVISION`. The scan found those two steps and no others.

After both steps set `MODELSPEC_ARENA_REVISION: ${{ vars.MODELSPEC_ARENA_REVISION || 'pinned' }}`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_arena_revision.py
```

Exit 0. 50 passed.

The same two tests, run from `/tmp`:

Exit 0. 2 passed.

## Census

Steps in `.github/private-writers/*.yml` whose `run` starts `scripts.refresh_leaderboards` or `scripts.process_release_signals`:

- `leaderboard-refresh.yml`, "Re-read every covered board once"
- `release-signals.yml`, "Process one isolated work item"

The weekly step "Prove the generated diff is score-only" imports `check_score_only` from `scripts.refresh_leaderboards`. It does not start the module. `scripts/model_233_evidence.py` calls `refresh_leaderboards.run()`. No private-writer workflow runs that script.

## Not observed

The full pytest suite, a live run of either workflow, and the current value of the repository variable `MODELSPEC_ARENA_REVISION`. This commit leaves `modelspec-data` unchanged.
