# MODEL-458-SIGSVC verification

Base SHA: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
The PR body and executor completion line record the final head SHA. Resolve it
from this checkout with `git rev-parse HEAD`.

## AUD-14-F6

Signal IDs retain their canonical payload after acknowledgement. Identical
payloads remain duplicates within the intake window; conflicting payloads
retain the existing conflict response. Acknowledgement also retains the
canonical payload for previously queued rows. Response shapes are unchanged.

The permanent regression is `test_replay_after_ack_is_still_duplicate` in
`tests/test_release_signals.py`, with four cases. Before the implementation
change, pytest reported `4 failed, 57 deselected`, exit 1. Afterward, it
reported `4 passed, 57 deselected`, exit 0. The isolated specification check
also changed from `1 failed, 27 deselected`, exit 1, to
`1 passed, 27 deselected`, exit 0. Detailed local fixtures and output are
excluded from this public evidence.

Commands, run from the assigned worktree:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k test_replay_after_ack_is_still_duplicate
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_watch.py
git diff --check
```

The focused suites reported `92 passed in 24.61s`, exit 0. Existing assertions
were preserved. The documentation clarification is in `docs/grok-bot-signals.md`.
The OpenAPI description remains unchanged because its generator is outside
the specified edit paths.

## AUD-14-F7

Unsupported credentials return the existing authentication error. Invalid
signal fields return the existing input error before KV access. Both intake
paths and all three bearer endpoints retain their response shapes and status
vocabulary. No contract field range is widened.

The permanent regressions in `tests/test_release_signals.py` are
`test_invalid_input_returns_client_error`,
`test_non_ascii_read_key_returns_401` and
`test_invalid_discovery_returns_400`. Before the implementation change,
pytest reported `10 failed, 1 passed, 61 deselected`, exit 1. Afterward it
reported `11 passed, 61 deselected`, exit 0. The isolated specification check
reported `10 failed, 1 passed, 17 deselected`, exit 1, before the fix. All 28
retained specification checks passed afterward, including the existing
authentication, freshness, body-size, feature-off and queue controls.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k 'test_invalid_input_returns_client_error or test_non_ascii_read_key_returns_401 or test_invalid_discovery_returns_400'
```

## Combined focused checks

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_watch.py tests/test_rank_worker.py::test_the_vendored_bundle_is_the_repositorys_own_files tests/test_rank_worker.py::test_the_bundle_needs_nothing_the_isolate_does_not_have tests/test_worker_vendor_imports.py tests/test_worker_bundle.py tests/test_api_docs.py tests/test_removed_sources.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
```

The combined run reported `214 passed, 3 skipped in 90.36s`, exit 0. Two
opt-in live API tests and one built-site test were skipped. Public
re-vendoring copied 129 files and passed its isolated dependency check,
exit 0. Generated package copies are ignored and are not part of the commit.
The tracked-source guard was repeated after the evidence update and reported
`1 passed in 41.19s`, exit 0. The final `git diff --check` passed.

## Private Worker memory

The deploy-equivalent bundle used a fresh shallow private-data clone and a
throwaway signing key. All private exports stayed in ticket scratch. Heavy
commands used the shared serialization wrapper. The commands were:

```sh
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/MODEL-458-SIGSVC-scratch/modelspec-data
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm install --prefix /tmp/MODEL-458-SIGSVC-scratch/memory --no-save pyodide@0.28.3
mkdir -p /tmp/MODEL-458-SIGSVC-scratch/tmp
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD TMPDIR=/tmp/MODEL-458-SIGSVC-scratch/tmp MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_SNAPSHOT_KEY=model458-sigsvc-local-fixture-key /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /tmp/MODEL-458-SIGSVC-scratch/modelspec-data --out /tmp/MODEL-458-SIGSVC-scratch/private-bundle --check
env PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import shutil
import subprocess
import runpy
root = Path('/tmp/MODEL-458-SIGSVC-scratch/private-bundle')
files = subprocess.check_output(['git', 'ls-files', '-z', 'api/worker/src/*.py']).decode().split('\0')
for name in filter(None, files):
    source = Path(name)
    if source.parent == Path('api/worker/src'):
        shutil.copyfile(source, root / source.name)
blobs = runpy.run_path(str(root / 'bundled_data.py'))['BLOBS']
snapshot = '/api/decision/snapshot-successor.json.gz' in blobs
vocabulary = '/api/decision/vocabulary-successor.json' in blobs
assert snapshot == vocabulary, 'incomplete successor pair'
print(f'successor={str(snapshot).lower()}')
PY
env NODE_PATH=/tmp/MODEL-458-SIGSVC-scratch/memory/node_modules MODELSPEC_SNAPSHOT_KEY=model458-sigsvc-local-fixture-key /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs /tmp/MODEL-458-SIGSVC-scratch/private-bundle --limit-mib 115 --output /tmp/MODEL-458-SIGSVC-scratch/private-current-memory.json
env NODE_PATH=/tmp/MODEL-458-SIGSVC-scratch/memory/node_modules MODELSPEC_SNAPSHOT_KEY=model458-sigsvc-local-fixture-key /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs /tmp/MODEL-458-SIGSVC-scratch/private-bundle --successor --limit-mib 115 --output /tmp/MODEL-458-SIGSVC-scratch/private-successor-memory.json
```

The private bundle copied 129 files, passed its isolated dependency check
and contained both snapshot periods. The memory probe exercises decide,
vocabulary, rank and policy-check under Pyodide 0.28.3. It does not exercise
signals HTTP requests; the service regressions cover signals separately.

Both measurements exited 0 against the unchanged 115 MiB steady limit:

| Period | Steady bytes | Steady MiB | Peak MiB |
| --- | ---: | ---: | ---: |
| Current | 114339970 | 109.04 | 112.56 |
| Successor | 108783410 | 103.74 | 105.72 |

The current-period run emitted the existing advisory for a noisy peak above
112 MiB. Its steady usage passed. No memory or timing gate was changed.

## Environment and limits

Python 3.14.4, pytest 9.1.1, httpx 0.28.1, PyYAML 6.0.3,
cryptography 45.0.7, Node v22.22.3, git 2.50.1, gh 2.103.3. The memory runtime used
Pyodide 0.28.3 with pydantic 2.10.6 and PyYAML 6.0.2.

Verification used local service calls with an in-memory KV. Production HTTP,
distributed KV consistency, injected KV failures and concurrent requests
were not observed. No production switch, secret, frozen data, ranking policy
or legal text changed.
No deployment, paid-provider call or local full-suite run was performed.
