# MODEL-437 round 2 commands

Commands ran from `/Users/terbeest/dev/worktrees/model-437` unless the recorded
command specifies its scratch working directory. Pytest ran serially with
`-p no:cacheprovider`. Each tool/process exit code was checked directly.

## Merge and initial red tests

```bash
git fetch origin main
git merge --no-commit origin/main
```

The merge stopped with the five conflicts named in the spec. Main's versions
of `scripts/price_reread.py` and `tests/test_cite_only_caller_isolation.py` were
retained exactly. The other conflicts retained #889's cited-score additions.
The merge commit is `a65a4997692d20abcccc848abf6a8c48448ed727`.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cite_only_caller_isolation.py tests/test_cite_only_verification.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_score_warnings.py tests/test_cite_only_exports.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_score_contract.py::test_human_named_comparison_labels_cited_benchmark_score tests/test_decision_summary.py::test_cited_answer_sentence_covers_facts_scores_and_both
```

The merge check passed 211 tests. The initial P1 red run failed 14 tests and
passed 51. P2/P3 failed 7 and passed 3 before their source changes.

## Final test files against the untouched merged code

The final tests were also replayed against an archive of the merge commit.
Only the three test files were copied from the implementation checkout. This
confirms the final assertions fail against the old implementation after the
fixture corrections described in the main report.

```bash
python3 - <<'PYTHON'
from pathlib import Path
import subprocess, tarfile, shutil
root=Path('/tmp/model-437-scratch/executor/merged-base')
root.mkdir()
archive=root.parent/'merged-base.tar'
with archive.open('wb') as stream:
    subprocess.run(['git','archive','a65a4997'], stdout=stream, check=True)
with tarfile.open(archive) as contents:
    contents.extractall(root, filter='data')
archive.unlink()
for name in ('test_cited_scores.py','test_cited_score_warnings.py','test_cite_only_exports.py'):
    shutil.copy2(Path('tests')/name, root/'tests'/name)
PYTHON
env PYTHONPATH=/tmp/model-437-scratch/executor/merged-base /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider /tmp/model-437-scratch/executor/merged-base/tests/test_cited_scores.py /tmp/model-437-scratch/executor/merged-base/tests/test_cited_score_warnings.py /tmp/model-437-scratch/executor/merged-base/tests/test_cite_only_exports.py
```

Result: exit 1, 18 failed and 81 passed. All failures are assertion failures.

## Green checks

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_scores.py tests/test_cited_score_warnings.py tests/test_cite_only_exports.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_score_contract.py tests/test_decision_summary.py tests/test_cli_compare_models.py tests/test_cite_only_warning_scope.py tests/test_cite_only_surfaces.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_score_contract.py tests/test_decision_summary.py -k 'cited or deserialized_citation'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_scores.py tests/test_cited_score_warnings.py tests/test_cite_only_exports.py tests/test_cited_score_contract.py tests/test_decision_summary.py tests/test_class_fit.py tests/test_legal.py tests/test_removed_sources.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base origin/main --head HEAD --branch model-437-count-cited-scores
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
```

The four green pytest commands passed 99, 154, 17, and 367 tests respectively.
The 17-test selection deselected 58 tests. The final 367-test run skipped only
the optional built-site scan because `MODELSPEC_DIST` was unset. These suites
overlap. Schema, OpenAPI, data freeze and whitespace checks exited 0. The shard
planner estimated 4,111.592 to 4,111.594 seconds per CI shard.

## Tool versions

Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3, cryptography 45.0.7,
pypdf 6.19.0, Node 22.22.3, Pyodide 0.28.3, Git 2.50.1, gh 2.102.0.
Node was `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node`.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PYTHON'
import sys, importlib.metadata
print(sys.version)
for name in ('pytest', 'pydantic', 'PyYAML', 'cryptography', 'pypdf'):
    print(name, importlib.metadata.version(name))
PYTHON
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
git --version
gh --version
```

Private acceptance commands, direct exit codes, timestamps, policies, and pinned
revisions are recorded separately in the public JSON files beside this document.
The main report explains the state labels and the scratch-only data repair.

## Restore the public bundle after private probes

```bash
env -u MODELSPEC_SOURCE_CACHE -u MODELSPEC_SNAPSHOT_KEY -u MODELSPEC_SNAPSHOT_ED25519_KEY -u MODELSPEC_REQUIRE_DATA_DIR PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
```

Exit 0. Rebuilt 129 public files; bundle imports passed with only declared
dependencies. Git reported no tracked bundle changes.

## Final artifact guard and cleanup

After staging all acceptance helpers, public aggregates and red/green logs:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
```

Exit 0, one passed. The scoped cleanup command and verification are in
`cleanup.public.json`. The acceptance helper removed its owned private tree;
the executor removed its own scratch and the completed labels scratch using
`shutil.rmtree` after copying the logs, then removed the empty ticket root.
No task scratch or started background process remains.
