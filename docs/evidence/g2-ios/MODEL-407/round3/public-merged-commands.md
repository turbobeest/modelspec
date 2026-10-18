This public rerun checks merge commit
`e7f422751aa49dcb8461863fd7f5cd7983208e82`, after main added
`decision/model_comparison.py`. It materialized a fresh public fixture and ran
the ordinary vendor command without generated-source patches. The recipe,
probe, 115 MiB limit, and Node 22.22.3/Pyodide 0.28.3 runtime are unchanged.

| Mode | Steady MiB | Peak MiB | Wasm MiB | Direct exit |
| --- | ---: | ---: | ---: | ---: |
| Current | 104.490169 | 104.942264 | 59.875 | 0 |
| Native successor | 104.489985 | 107.502391 | 59.875 | 0 |
| Warm rollover | 104.533630 | 107.603294 | 59.875 | 0 |

Fixture creation and vendor both exited 0. Vendor took 197.491 seconds and
removed its temporary directories. Both periods retained 15 synthetic hardware
workloads and 68 referenced synthetic sources. Their snapshot IDs remain
`snap_4a7d44f0961cb6a6` and `snap_0f8efcaccaa46937`, with the same 2026-10-21
boundary as the earlier final run.

`public-merged-metadata.json` records the full commit, source hashes, exact
commands and environment, direct exit statuses, and retained fixture counts.
It includes the new module's hash and the list of copied handwritten Worker
modules. The generated snapshot loader, JSON reader, and model comparison
module were checked byte-for-byte against the source files.

These commands reproduce the run from the merge commit, using a fresh output
directory. The recorded run used `tmp/model-407/round3/memory-merged`; choose a
new path if it already exists. The hidden temporary directory keeps vendor's
temporary repository links out of pytest discovery.

```sh
export MODEL407_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python
export MODEL407_NODE=/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node
export MODEL407_PUBLIC="$PWD/tmp/model-407/round3/memory-merged"
export NODE_PATH="$PWD/tmp/model-407/memory_probe/runtime/node_modules"
export PYTHONPATH="$PWD" TZ=UTC PYTHONDONTWRITEBYTECODE=1
export MODELSPEC_REQUIRE_DATA_DIR=1
export MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key
unset MODELSPEC_SNAPSHOT_ED25519_KEY GITHUB_STEP_SUMMARY MODEL407_MEMORY_MODE
mkdir -p "$MODEL407_PUBLIC/.tmp"
export TMPDIR="$MODEL407_PUBLIC/.tmp"

"$MODEL407_PYTHON" api/worker/memory_fixture.py \
  --out "$MODEL407_PUBLIC/public-data"
"$MODEL407_PYTHON" api/worker/vendor.py \
  --data-dir "$MODEL407_PUBLIC/public-data" --out "$MODEL407_PUBLIC/bundle"

"$MODEL407_PYTHON" - <<'PY'
import os
from pathlib import Path
import shutil
import subprocess

bundle = Path(os.environ["MODEL407_PUBLIC"]) / "bundle"
for name in subprocess.check_output(
        ["git", "ls-files", "--", "api/worker/src"], text=True).splitlines():
    source = Path(name)
    if source.parent == Path("api/worker/src") and source.suffix == ".py":
        shutil.copyfile(source, bundle / source.name)
PY

"$MODEL407_NODE" --expose-gc api/worker/measure_memory.cjs \
  "$MODEL407_PUBLIC/bundle" --limit-mib 115 --attribute \
  --output "$MODEL407_PUBLIC/public-merged-current.json"
"$MODEL407_NODE" --expose-gc api/worker/measure_memory.cjs \
  "$MODEL407_PUBLIC/bundle" --successor --limit-mib 115 --attribute \
  --output "$MODEL407_PUBLIC/public-merged-successor.json"
MODEL407_MEMORY_MODE=warm "$MODEL407_NODE" --expose-gc \
  --require ./docs/evidence/g2-ios/MODEL-407/rollover-probe-hook.cjs \
  api/worker/measure_memory.cjs "$MODEL407_PUBLIC/bundle" \
  --limit-mib 115 --attribute \
  --output "$MODEL407_PUBLIC/public-merged-warm.json"
```

The source copy selects only tracked top-level modules, leaving generated
`bundled_data.py` and `tier_policy.py` intact. Vendor itself includes
`decision/model_comparison.py`. Each probe runs directly, without a pipe.
The warm hook and the sampling rules are the same as those documented in
`memory-commands.md`. This rerun uses only public data.
