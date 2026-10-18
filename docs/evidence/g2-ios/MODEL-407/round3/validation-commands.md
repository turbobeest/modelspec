# MODEL-407 Round 3 validation commands

Run from `/Users/terbeest/dev/worktrees/model-407`. The original Round 3
executable implementation is `f6dbbcd86845e614a00d3bd7ce8dfa4d55c2f618`.
The final main reconciliation is `e7f422751aa49dcb8461863fd7f5cd7983208e82`.
Its reader and snapshot loader match the original fix; fresh public/private
bundles, focused checks, timing and integration checks verify the merged
source. See the main report and `merged-*` artifacts for those results.
The installed host Python is 3.14.4; Node is 22.22.3 and Pyodide is 0.28.3.

```sh
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
export PYTHONPATH=$PWD
export MODEL407_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python

"$MODEL407_PYTHON" -m pytest -q \
  tests/test_snapshot_streaming.py tests/test_decision_snapshot.py \
  tests/test_snapshot_successor.py tests/test_snapshot_successor_memory.py \
  tests/test_snapshot_successor_vendor.py tests/test_snapshot_response_headers.py \
  tests/test_dated_price_snapshot.py tests/test_decide_snapshot_refresh.py \
  tests/test_hardware_fit_memory.py tests/test_hardware_fit_worker.py \
  tests/test_worker_memory.py tests/test_ci_workflows.py tests/test_worker_compression.py \
  tests/test_rank_worker.py tests/test_policy_check.py tests/test_policy_commercial_use.py \
  tests/test_policy_shape.py tests/test_policy_store_state.py
"$MODEL407_PYTHON" -m pytest -q -p no:xdist -m perf
"$MODEL407_PYTHON" -m pytest --collect-only -q -m 'not perf'
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD \
  "$MODEL407_PYTHON" -m pytest -q -n 4 --dist loadfile
```

`npm ci` ran successfully in `web` before the full suite. The serial timing
and collection commands match `.github/workflows/test.yml`. Wait for public
vendor builds to remove their temporary repository overlays before running
unscoped collection. The public reproduction recipe uses a hidden temporary
directory to prevent discovery of those transient links.

The pre-merge full suite completed at branch HEAD
`00a03dbbd837615d90cefee7d32d47e64c266da1`: 11,654 passed, 9 skipped and
11 warnings in 1,306.36 seconds, direct exit 0. The final merged full-suite
result is recorded at the end of this file. The merged checks below also
exit 0; the chart check has nothing to check. The source comparison checks
runtime and test directories against the final measured merge. The
nested-object test correction is in `8a0009d4`.

```sh
"$MODEL407_PYTHON" -m ruff check decision/json_stream.py tests/test_snapshot_streaming.py
"$MODEL407_PYTHON" scripts/data_freeze_guard.py \
  --base 6f45c2a7 --head HEAD --branch model-407-worker-memory
"$MODEL407_PYTHON" scripts/chart_check_pr.py --base 6f45c2a7
git diff --exit-code e7f42275 HEAD -- api decision pipeline schema registry hardware mcp web tests qa cli .github scripts
git diff --check
```

The private run used the ordinary vendor path, with all generated files,
bundles, logs, and probe outputs under the authorized scratch directory:

```sh
git -C /Users/terbeest/dev/modelspec-data worktree add --detach \
  /tmp/model-407-private/data-74947c3 74947c3
mkdir -p /tmp/model-407-private/tmp
export TMPDIR=/tmp/model-407-private/tmp
export TZ=UTC PYTHONDONTWRITEBYTECODE=1 MODELSPEC_REQUIRE_DATA_DIR=1
export MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key
unset MODELSPEC_SNAPSHOT_ED25519_KEY GITHUB_STEP_SUMMARY MODEL407_MEMORY_MODE
export NODE_PATH="$PWD/tmp/model-407/memory_probe/runtime/node_modules"
"$MODEL407_PYTHON" api/worker/vendor.py \
  --data-dir /tmp/model-407-private/data-74947c3 \
  --out /tmp/model-407-private/bundle-round3-final \
  > /tmp/model-407-private/vendor.log 2>&1
```

After the build, tracked top-level `api/worker/src/*.py` modules were copied
into that bundle, matching the CI path and [public recipe](memory-commands.md):

```sh
"$MODEL407_PYTHON" - <<'PY' > /tmp/model-407-private/copy.log 2>&1
from pathlib import Path
import shutil
import subprocess

bundle = Path("/tmp/model-407-private/bundle-round3-final")
for name in subprocess.check_output(
        ["git", "ls-files", "--", "api/worker/src"], text=True).splitlines():
    source = Path(name)
    if source.parent == Path("api/worker/src") and source.suffix == ".py":
        shutil.copyfile(source, bundle / source.name)
PY
```

No generated source was patched. The exact native CI requests and the already
committed warm hook ran as follows, each with its direct process status checked:

```sh
node --expose-gc api/worker/measure_memory.cjs \
  /tmp/model-407-private/bundle-round3-final --limit-mib 115 --attribute \
  --output /tmp/model-407-private/current.json \
  > /tmp/model-407-private/current.log 2>&1
node --expose-gc api/worker/measure_memory.cjs \
  /tmp/model-407-private/bundle-round3-final --successor --limit-mib 115 --attribute \
  --output /tmp/model-407-private/successor.json \
  > /tmp/model-407-private/successor.log 2>&1
MODEL407_MEMORY_MODE=warm node --expose-gc \
  --require ./docs/evidence/g2-ios/MODEL-407/rollover-probe-hook.cjs \
  api/worker/measure_memory.cjs /tmp/model-407-private/bundle-round3-final \
  --limit-mib 115 --attribute --output /tmp/model-407-private/warm.json \
  > /tmp/model-407-private/warm.log 2>&1
```

The native successor mode crosses the period boundary before the CI request
sequence. The warm hook serves the current period first, crosses the boundary,
then serves the successor and remaining CI requests. It asserts predecessor
release before successor bytes are read. Attribution follows the memory
sample; neither mode forces collection between requests.

Only whitelisted memory numbers and engine/data commit SHAs were exported to
`private-memory-numbers.json`. The detached data worktree was removed using
`git worktree remove`, then every remaining scratch child was deleted with a
path-guarded Python cleanup. The scratch directory was verified empty.

The final private run repeated this recipe at merge commit
`e7f422751aa49dcb8461863fd7f5cd7983208e82`, using
`/tmp/model-407-private/bundle-round3-merged` in place of
`bundle-round3-final`. Vendor and all three probes returned direct exit 0.
Only the whitelisted memory fields and engine/data commit identifiers were
exported to `private-merged-memory-numbers.json`; the detached data worktree
and every scratch child were removed afterward. No generated source was
patched in either final run.

The final locked full-suite rerun used the same command above at HEAD
`e7f422751aa49dcb8461863fd7f5cd7983208e82`. It finished with direct process
exit 0: **11,845 passed, 9 skipped, 11 warnings in 1,384.42 seconds
(23 minutes 4 seconds)**. Its complete output is in `merged-full-suite.txt`.
The merged focused command adds `tests/test_model_comparison.py` to the
original list; `merged-validation.json` records that exact command and the
652 passing tests. The exact serial perf and collection commands are unchanged
and pass three performance tests and collection of 11,851 non-performance tests.
