# MODEL-450 round-four execution evidence

Round four adds the missing public mirror of the approved private release
coverage workflow. The mirror is byte-identical to data#130. Dedicated pin and
isolation tests cover its existing execution from the engine directory.
The approved SLO implementation is unchanged.

Public PR: https://github.com/turbobeest/modelspec/pull/970.
Private companion: https://github.com/turbobeest/modelspec-data/pull/130.
The public PR was already ready for review; this execution preserves its state.

Base: `b315b0c7b52e6cb74f4178bd301f484d2b347389`.
Merged main: `d7d5082b9ead230782f58533224ac901b55d4e81`.
Merge commit: `451ab6d91faa28776c12bb8098f1238b40e095c8`.
Pulled private branch: `afc3a5b2fce504601af0a3537401c2edd2f231a8`.
Verified implementation: `67cc733c96787426da362643f374741e06aca061`.
The final evidence commit's exact SHA is recorded in `.pr-commit.txt` and
`.pr-body.md`. This file cannot contain its own commit hash.
Prior rounds' evidence remains in this file at the base commit.

## Preparation and red first

Commands ran from `/Users/terbeest/dev/worktrees/model-450`, except the
explicit private pull:

```bash
git fetch origin main
git merge --no-edit origin/main -m 'Merge origin/main for MODEL-450 round 4' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git -C /Users/terbeest/dev/worktrees/data-model-450 pull --ff-only
/Users/terbeest/dev/modelspec/.venv/bin/python /Users/terbeest/dev/worktrees/data-model-450/.github/scripts/check_writer_mirrors.py --mirrors .github/private-writers --workflows /Users/terbeest/dev/worktrees/data-model-450/.github/workflows
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py -k 'release_coverage or release-coverage'
```

Fetch, merge and fast-forward pull exited 0. Before the mirror was added, the
checker exited 1 with `release-coverage.yml: public mirror is missing`.
The new tests exited 1 with **17 failed, 298 deselected**, all because the
public mirror was absent. Red logs are in
`/tmp/model-450-scratch/r4-executor/{mirrors-red,tests-red}.log`.

The red-first tests were:

- `test_release_coverage_verifies_the_pin_before_running_the_engine`: data
  checkout, pin verification, pinned engine checkout, credentials and permissions.
- `test_the_pin_script_accepts_only_a_commit_on_main`, with the new
  `release-coverage` parameter: valid ancestor/tip and 11 invalid or unavailable
  input cases run against a local Git repository.
- `test_a_fetchable_commit_off_main_is_refused_by_ancestry`, with the new writer
  parameter: an available commit outside main still fails ancestry.
- `test_release_coverage_runs_from_engine_with_private_history_only_as_input`,
  for measure and alert: execute the workflow commands against synthetic engine
  and private modules; verify the engine loads and data/output arguments match.

The existing canonical writer tests retain their assertions. This approved
workflow runs from `engine` without linking private paths or using `-I`;
the dedicated tests verify that form without claiming isolated-mode behavior.
The model-week mirror pattern was read from `origin/model-448-mirror`.

## Green verification

```bash
cp /Users/terbeest/dev/worktrees/data-model-450/.github/workflows/release-coverage.yml .github/private-writers/release-coverage.yml
/Users/terbeest/dev/modelspec/.venv/bin/python /Users/terbeest/dev/worktrees/data-model-450/.github/scripts/check_writer_mirrors.py --mirrors .github/private-writers --workflows /Users/terbeest/dev/worktrees/data-model-450/.github/workflows
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py -k 'release_coverage or release-coverage'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_engine_pin.py tests/test_writer_isolation.py tests/test_release_slo.py tests/test_release_slo_history.py tests/test_release_slo_handoff.py tests/test_coverage_slo.py tests/test_data_workflows.py tests/test_removed_sources.py
git diff --check
```

All exited 0. The checker printed **12 public writer mirrors match private
workflows**. Targeted green: **19 passed, 298 deselected in 1.22s**; the extra
two cases are shared cache and secret guards that discover the new mirror.
The broader serial run passed **594 tests, 1 skipped in 68.60s**.
The skip, `test_a_built_dist_carries_no_removed_value`, requires
`MODELSPEC_DIST`. No full local suite ran.

After the evidence update, this final documentation guard also exited 0,
with **1 passed in 31.98s**:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source > /tmp/model-450-scratch/r4-executor/final-doc-guard.log 2>&1
```

`ruff check tests/test_engine_pin.py tests/test_writer_isolation.py` exited 1
with 25 pre-existing E501 findings in the isolation test file. An inline Python
comparison of Ruff JSON results against `451ab6d9` exited 0: all 25 finding
codes, messages and source lines match, with no additions. That exact comparison
is saved as `/tmp/model-450-scratch/r4-executor/lint-comparison.py`.
No unrelated formatting was changed.

Tools: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, Ruff 0.16.6 and Git 2.50.1.
A read-only review found no blockers. Logs are under
`/tmp/model-450-scratch/r4-executor/`.

## Limits

No live workflow, deployment, artifact transfer, issue write, CI result or SLO
attainment was observed. No private content was copied beyond the expressly
authorized workflow mirror. No new private-worktree edit was made after its
requested pull. No Worker exports, production switches or pin were edited;
no Worker memory probe was needed. No vendor calls, source-page retention,
Linear writes, merge to main, force push or PR-state change occurred.
