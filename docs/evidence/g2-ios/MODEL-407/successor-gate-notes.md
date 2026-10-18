# MODEL-407 successor memory gate

Added `--successor` to the actual memory probe. It selects the current
snapshot's exclusive UTC boundary before issuing the original four requests.
The probe does not read or parse successor bytes itself. It asserts a changed
snapshot identity, verified signature, decision body/header binding, and
matching vocabulary. This works with the eager `b4a7074f` implementation and
the lazy implementation. A missing usable successor fails the process.

The JSON result labels `period` as `current` or `successor`. Baseline comparison
rejects a different period. Old JSON with no period remains a current result.
The public workflow and manual private-workflow patch now measure both main
periods and gate both candidate periods at 115 MiB with the matching baseline.
The separate five-request warm-handover hook remains independent.

Red-first commands, before implementation:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_worker_memory.py -k 'matching_periods or public_memory_workflow'
# 2 failed, 4 deselected in 0.10s; exit 1. successor-gate-red.txt.

NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs tmp/model-407/memory_probe/public-bundle-calibrated --successor --measure-only --output tmp/model-407/hardware/successor-flag-red.json
# Unknown flag, Memory probe failed: TypeError; exit 1. successor-flag-red.log.
```

Green verification:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_ci_workflows.py tests/test_worker_memory.py
# 59 passed in 42.30s; exit 0. successor-workflow-green.txt.

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_worker_memory.py -k 'not builds_admitted'
# After adding private-patch regression: 6 passed, 1 deselected in 0.28s; exit 0.

/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --check api/worker/measure_memory.cjs
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH actionlint -shellcheck= .github/workflows/rank-api.yml
git diff --check -- api/worker/measure_memory.cjs tests/test_worker_memory.py .github/workflows/rank-api.yml docs/model-407-recall-private.patch
git apply --numstat docs/model-407-recall-private.patch
/Users/terbeest/dev/modelspec/.venv/bin/ruff check tests/test_worker_memory.py
# Each separate process exited 0.
```

Actual Pyodide 0.28.3 process verification, public artifacts only:

```sh
NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs tmp/model-407/memory_probe/public-bundle-b4a7074f --successor --measure-only --output tmp/model-407/hardware/successor-baseline.json
# Exit 0, successor, 116.482418 MiB. Demonstrates compatibility with eager baseline.

NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs tmp/model-407/memory_probe/public-bundle-calibrated --successor --limit-mib 115 --baseline tmp/model-407/hardware/successor-baseline.json --output tmp/model-407/hardware/successor-candidate.json
# Exit 1, successor, 115.584469 MiB. This intentionally uses the old candidate
# bundle before successor memory optimization, proving the new gate catches it.
```

Both result files report the original four request names. No private artifacts
were accessed or generated for this work. Root owns optimized-bundle and
private measurements. No commits or external writes made.
