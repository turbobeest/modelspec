# MODEL-458-CI-A verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Branch: `model-458-ci-a`.
The final commit SHA is recorded in the draft PR body after committing this file.

Environment: macOS 27.2 arm64, Python 3.14.4, pytest 9.1.1, Git 2.50.1,
GitHub CLI 2.103.3,
PyYAML 6.0.3, pydantic 2.13.5. Commands ran from the assigned worktree.

## AUD-08-F1

Both required checks preserve filenames from NUL-delimited Git output.
Frozen-path classification and chart reader requirements apply consistently
to added, modified, deleted and renamed paths.

Regression tests: `test_collect_preserves_frozen_paths`,
`test_fixture_changes_preserve_paths`, and `test_card_changes_preserve_paths`.
Before the change, the new cases reported 24 failed and 12 passed, exit 1.
An additional filename preservation check reported 8 failed and 1 passed,
exit 1, before explicit output decoding was added.
After the change, the affected suites reported 80 passed in 16.50 seconds,
exit 0. Detailed local probe output is excluded from this public record.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_freeze_guard.py tests/test_chart_check_pr.py --basetemp /tmp/MODEL-458-CI-A-scratch/root/f1-green-final
git diff --check
```

## AUD-08-F9

The root pytest configuration and shard splitter share the generated-cache
exclusion. Tests beside the cache and in other top-level directories remain
discoverable. Explicit discovery roots inside the excluded cache are omitted.

The supplied scratch probe initially reported default collection exit 0 and
explicit shard collection exit 2. The supplied scratch assertion exited 1.
After the fix, both collection modes exited 0 and selected only the genuine
test. No claim is made that a clean CI checkout contained this local cache.

Permanent regressions are
`test_file_splitter_matches_default_collection_with_cache_ignore` and the
three `test_file_splitter_excludes_cache_from_configured_testpaths` cases.
The red run reported `4 failed, 68 deselected in 0.55s`, exit 1. The collection
comparison reported `RuntimeError: downloaded tests must remain ignored`;
the other cases reported unexpected cache paths in the selected file list.
The complete focused suite then reported `72 passed in 2.91s`, exit 0.
Existing discovery-pattern and shard-assignment assertions remain intact.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-CI-A-scratch/root/repro/F9/probe_ignored_cache.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-A-scratch/root/repro/F9/test_repro.py --basetemp /tmp/MODEL-458-CI-A-scratch/root/repro/F9/pytest
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k 'cache' --basetemp /tmp/MODEL-458-CI-A-scratch/root/f9-red
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py --basetemp /tmp/MODEL-458-CI-A-scratch/root/f9-green
```

## AUD-08-F10

The policy tests load raw card YAML through a module-scoped fixture when a
catalogue-dependent test executes. The six existing consumers retain their
assertions and complete catalogue iterations. The separate schema-validation
test remains unchanged.

`test_policy_shape_collection_does_not_parse_catalogue` failed before the fix
with `AssertionError: catalogue parsed while importing test definitions`.
The focused run reported `1 failed, 72 deselected in 0.17s`, exit 1; after
the fix it reported `1 passed, 72 deselected in 0.12s`, exit 0. The supplied
scratch reproduction independently exited 1 with the same assertion.

`test_catalogue_fixture_contains_every_card` initially reported
`fixture 'cards' not found`, exit 1. It passes with the module fixture and
checks that the result is nonempty and contains every card. This checkout
contains 1,372 card paths. The full serial policy and CI workflow run reported
`108 passed in 33.40s`, exit 0. Wall time was 33.59 seconds. The setup trace
contains exactly one `SETUP M cards` and one `TEARDOWN M cards`.

Fresh-process collection of the same 35 policy cases measured:

| Measurement | Before | After |
| --- | ---: | ---: |
| pytest collection | 43.38 s | 0.09 s |
| Process wall time | 43.83 s | 0.28 s |
| Process user CPU time | 41.51 s | 0.24 s |
| Process system CPU time | 0.85 s | 0.03 s |

These are single local macOS measurements, not CI measurements or summed
testcase times. The measured local wall-time reduction is 43.55 seconds.
The after measurement uses the real fixture implementation; no empty-list
prototype was used.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-A-scratch/root/repro/F10/test_repro.py --basetemp /tmp/MODEL-458-CI-A-scratch/root/repro/F10/pytest
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k policy_shape_collection --basetemp /tmp/MODEL-458-CI-A-scratch/root/f10-red
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_policy_shape.py -k catalogue_fixture --basetemp /tmp/MODEL-458-CI-A-scratch/root/f10-fixture-red
# Run in separate fresh processes before and after the fixture change.
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /usr/bin/time -p /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider tests/test_policy_shape.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k policy_shape_collection --basetemp /tmp/MODEL-458-CI-A-scratch/root/f10-import-green
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /usr/bin/time -p /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --setup-show tests/test_policy_shape.py tests/test_ci_workflows.py --basetemp /tmp/MODEL-458-CI-A-scratch/root/f10-green
```

An AST comparison against the base confirmed that all 28 pre-existing
function bodies in `tests/test_policy_shape.py` are unchanged except for
renaming `CARDS` to `cards` in the six consumers. The shard summary command
exited 0 and assigned all 362 modules across eight shards. Its estimates are
summed historical testcase seconds, not measured wall time.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import ast
import subprocess
from pathlib import Path
base = subprocess.run(['git', 'show', '5dd0eb5a:tests/test_policy_shape.py'], capture_output=True, text=True, check=True).stdout
current = Path('tests/test_policy_shape.py').read_text()
class FixtureName(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == 'CARDS':
            node.id = 'cards'
        return node
old = {n.name:n for n in ast.parse(base).body if isinstance(n, ast.FunctionDef)}
new = {n.name:n for n in ast.parse(current).body if isinstance(n, ast.FunctionDef)}
for name, function in old.items():
    expected = FixtureName().visit(ast.Module(body=function.body, type_ignores=[]))
    actual = ast.Module(body=new[name].body, type_ignores=[])
    assert ast.dump(expected) == ast.dump(actual), name
print(f'All {len(old)} existing function bodies preserved, allowing only CARDS -> cards.')
print('Catalogue paths:', len([p for p in Path('models').glob('**/*.md') if p.name != 'LICENSE.md']))
PY
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 8 --isolate tests/test_private_serving.py --isolate tests/test_social_cards.py --isolate tests/test_agent_ready.py --isolate tests/test_landing.py --summary
git diff --check
```

## Scope of observation

Tests use local fixtures and temporary repositories. No production request,
deployment, paid provider call, private data change or workflow edit was made.
The local full suite was not run; CI remains the full gate. No CI wall-time
improvement has been measured.
