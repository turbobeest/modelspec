The public fixture and probe were run from `/Users/terbeest/dev/worktrees/model-407`.
The Python executable was `/Users/terbeest/dev/modelspec/.venv/bin/python`.
Every Node command used `/Users/terbeest/.nvm/versions/node/v22.22.3/bin` first in PATH.

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_worker_memory.py
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm install --prefix tmp/model-407/memory_probe/runtime --no-save pyodide@0.28.3

# The baseline engine is an archive of immutable public commit b4a7074f.
# Reproduce the public archive without changing branches:
python - <<'PY'
import io, subprocess, tarfile
from pathlib import Path
out = Path('tmp/model-407/memory_probe/.engine-b4a7074f')
out.mkdir(parents=True, exist_ok=True)
archive = subprocess.run(['git', 'archive', 'b4a7074f'], check=True, capture_output=True)
with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as source:
    source.extractall(out, filter='data')
PY
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/memory_fixture.py --out tmp/model-407/memory_probe/public-data-calibrated
MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir tmp/model-407/memory_probe/public-data-calibrated --out tmp/model-407/memory_probe/public-bundle-calibrated
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/memory_fixture.py --public-engine tmp/model-407/memory_probe/.engine-b4a7074f --out tmp/model-407/memory_probe/public-data-b4a7074f
MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python tmp/model-407/memory_probe/.engine-b4a7074f/api/worker/vendor.py --data-dir tmp/model-407/memory_probe/public-data-b4a7074f --out tmp/model-407/memory_probe/public-bundle-b4a7074f

# Copies only tracked handwritten src/*.py, then asserts both snapshot envelopes
# retain all 15 synthetic hardware records and writes bundle-metadata.json.
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-407/inspect-public-bundles.py

env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key node --expose-gc api/worker/measure_memory.cjs tmp/model-407/memory_probe/public-bundle-b4a7074f --measure-only --attribute --output tmp/model-407/memory_probe/b4a7074f-memory.json
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key node --expose-gc api/worker/measure_memory.cjs tmp/model-407/memory_probe/public-bundle-calibrated --limit-mib 115 --baseline tmp/model-407/memory_probe/b4a7074f-memory.json --attribute --output tmp/model-407/memory_probe/candidate-memory.json
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key node --expose-gc api/worker/measure_memory.cjs tmp/model-407/memory_probe/public-bundle-b4a7074f --limit-mib 115 --output tmp/model-407/memory_probe/b4a7074f-gate-red.json
```

The final command intentionally returned 1 at 116.476902 MiB. The first baseline
measurement returned 0 in measurement-only mode at 115.411487 MiB. These show
about 1.07 MiB of run-to-run V8 variation. The Wasm allocation was 71.875 MiB in
both baseline runs. The candidate passed at 104.472095 MiB, with 59.875 MiB Wasm.

The immutable old probe was also run with `--limit-mib 1` on the initial valid
public bundle. It ignored that unimplemented flag and returned 0 at 104.348796
MiB. The new probe on the same bundle returned 1 at 103.363607 MiB. These are a
process-exit regression proof, not the final fixture calibration.

The initial fixture used an excluded model. Its actual built envelope retained
zero hardware rows. The corrected fixture uses `google/gemma-4-31b-it`, and its
admission test now uses the production premier file with `gate=True`.

Private measurements use the authorized `/tmp/model-407-private` directory.
The final memory-only matrix is recorded in `../MODEL-407-fix.md`. Private
bundles, validity dates, raw logs, and probe outputs are kept outside this
repository and deleted after measurement.


Follow-up at executable commit `bb41f0f68cb90c0616263e4c4853c77ee3d916a4`:

The historical engines were extracted with `git archive` and Python's
`tarfile.extractall(..., filter="data")` under the authorized private scratch
directory. Each engine ran its own `api/worker/vendor.py`; the final build ran
the current worktree's script. The data worktrees were created with:

```sh
git -C /Users/terbeest/dev/modelspec-data worktree add --detach /tmp/model-407-private/data-fd3145c fd3145c
git -C /Users/terbeest/dev/modelspec-data worktree add --detach /tmp/model-407-private/data-74947c3 74947c3
```

For each historical `(ENGINE, DATA)` pair in
`(7908f238, fd3145c)`, `(7908f238, 74947c3)`,
`(b4a7074f, fd3145c)`, `(b4a7074f, 74947c3)`, the build command was:

```sh
TMPDIR=/tmp/model-407-private/tmp TZ=UTC PYTHONDONTWRITEBYTECODE=1   PYTHONPATH=/tmp/model-407-private/engine-$ENGINE   MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key   /Users/terbeest/dev/modelspec/.venv/bin/python   /tmp/model-407-private/engine-$ENGINE/api/worker/vendor.py   --data-dir /tmp/model-407-private/data-$DATA   --out /tmp/model-407-private/bundle-$ENGINE-$DATA
```

`MODELSPEC_SNAPSHOT_ED25519_KEY` was removed from the build environment.
Build stdout/stderr went to files in the private scratch directory. After each
build, the engine's tracked, handwritten top-level `api/worker/src/*.py` files
were copied into its output directory, matching the CI bundle assembly.
The probe used the original four requests and default 120 MiB limit for those
four historical cells. The initial implementation used the same process with
`--limit-mib 115`. All direct exit statuses are in the execution evidence.

The final private build and probes used these command arguments, with
stdout/stderr and every JSON output redirected under the private scratch path:

```sh
TMPDIR=/tmp/model-407-private/tmp TZ=UTC PYTHONDONTWRITEBYTECODE=1   PYTHONPATH=$PWD MODELSPEC_REQUIRE_DATA_DIR=1   MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key   /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py   --data-dir /tmp/model-407-private/data-74947c3   --out /tmp/model-407-private/private-bundle-final

# Common environment for all three probes; GITHUB_STEP_SUMMARY was removed.
export TMPDIR=/tmp/model-407-private/tmp TZ=UTC PYTHONDONTWRITEBYTECODE=1
export NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules
export MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key

/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc   api/worker/measure_memory.cjs /tmp/model-407-private/private-bundle-final   --limit-mib 115 --attribute --output /tmp/model-407-private/private-final-current.json
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc   api/worker/measure_memory.cjs /tmp/model-407-private/private-bundle-final   --successor --limit-mib 115 --attribute   --output /tmp/model-407-private/private-final-successor.json
MODEL407_MEMORY_MODE=warm /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node   --expose-gc --require ./docs/evidence/g2-ios/MODEL-407/rollover-probe-hook.cjs   api/worker/measure_memory.cjs /tmp/model-407-private/private-bundle-final   --limit-mib 115 --attribute --output /tmp/model-407-private/private-final-warm.json
```

The final public build used the identical worktree vendor and tracked-file
copy with `tmp/model-407/memory_probe/public-data-calibrated` as `--data-dir`
and `tmp/model-407/root/public-bundle-final` as `--out`. Its three probes used
that bundle and public output paths. The public JSON artifacts are retained;
private raw output is deleted, with only memory numbers and engine/data SHAs
exported to `private-memory-numbers.json`.

The `--successor` run sets the UTC boundary before the original four requests.
The warm hook adds one current-period decide before crossing the boundary and
repeating the same decide. It asserts predecessor release before successor
read, signature verification, and body/header binding. Neither acceptance
path adds garbage collection between requests. Object attribution runs only
after the gate's memory sample.
