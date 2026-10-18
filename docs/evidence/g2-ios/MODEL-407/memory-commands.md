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
