The final public measurements used engine
`f6dbbcd86845e614a00d3bd7ce8dfa4d55c2f618`, a fresh ordinary
`vendor.py --data-dir` build, and no generated-source patches. Every probe used
Node 22.22.3, Pyodide 0.28.3, the existing request mix, and `--limit-mib 115`.

| Public bundle | Mode | Steady MiB | Wasm MiB | Direct exit |
| --- | --- | ---: | ---: | ---: |
| Whole-content C decoder prototype | Successor | 116.489828 | 71.875 | 1 |
| Whole-content C decoder prototype | Warm rollover | 116.548732 | 71.875 | 1 |
| Bounded-array prototype | Successor | 104.490071 | 59.875 | 0 |
| Bounded-array prototype | Warm rollover | 104.533075 | 59.875 | 0 |
| Final committed source | Current | 104.489331 | 59.875 | 0 |
| Final committed source | Successor | 104.512380 | 59.875 | 0 |
| Final committed source | Warm rollover | 104.533289 | 59.875 | 0 |

The three metadata files preserve the actual commands, direct exit statuses,
engine and source hashes, runtime versions, and snapshot counts. Their original
scratch paths identify the measured inputs and outputs. The corresponding
artifacts are archived here with these names:

| Original label | Archived prefix |
| --- | --- |
| `canonical-c` | `public-prototype-whole-c` |
| `bounded-array` | `public-prototype-bounded-array` |
| `bounded-array-final` | `public-final` |

The fixture recipe is unchanged, with SHA-256
`72c408ea8308f5b2379fb9988a14fc8355361d9d178b3d0340624ca4ae38b963`.
It adds 15 synthetic hardware workloads and 267 registry sources; 68 synthetic
sources are referenced in each built snapshot. Both periods retained all 15
workloads through the ordinary premier selection and completeness gate. The
measured boundary was 2026-10-21. Recreating the fixture uses the current UTC
date plus three days, so later reproductions have different snapshot IDs.

The original working directory was
`/Users/terbeest/dev/worktrees/model-407`. The local builder was Python 3.14.4
with pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1, and cryptography 45.0.7. CI uses
Python 3.13 with the dependency pins in `.github/workflows/rank-api.yml`.
Pyodide resolves its own Python packages from its pinned runtime release.

The following commands reproduce the final build in a new public scratch
directory. Run them from a checkout whose executable files match the final
engine SHA above. Use a fresh `repro` path because the fixture creates its
output directory. The commands reuse the installed Node and Pyodide runtime
from the measurements. If that runtime is absent, install it with
`npm install --prefix tmp/model-407/memory_probe/runtime --no-save pyodide@0.28.3`
using Node 22.22.3.

```sh
export MODEL407_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python
export MODEL407_NODE=/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node
export MODEL407_PUBLIC="$PWD/tmp/model-407/round3/memory/repro"
export NODE_PATH="$PWD/tmp/model-407/memory_probe/runtime/node_modules"
export PYTHONPATH="$PWD" TZ=UTC PYTHONDONTWRITEBYTECODE=1
export MODELSPEC_REQUIRE_DATA_DIR=1
export MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key
unset MODELSPEC_SNAPSHOT_ED25519_KEY GITHUB_STEP_SUMMARY MODEL407_MEMORY_MODE
mkdir -p "$MODEL407_PUBLIC/.tmp"
export TMPDIR="$MODEL407_PUBLIC/.tmp"

"$MODEL407_NODE" --version
"$MODEL407_NODE" -p 'require("pyodide/package.json").version'
"$MODEL407_PYTHON" api/worker/memory_fixture.py \
  --out "$MODEL407_PUBLIC/public-data"
"$MODEL407_PYTHON" api/worker/vendor.py \
  --data-dir "$MODEL407_PUBLIC/public-data" \
  --out "$MODEL407_PUBLIC/bundle-final"

# vendor --out supplies generated packages. Copy tracked handwritten modules.
"$MODEL407_PYTHON" - <<'PY'
import os
from pathlib import Path
import shutil
import subprocess

bundle = Path(os.environ["MODEL407_PUBLIC"]) / "bundle-final"
for name in subprocess.check_output(
        ["git", "ls-files", "--", "api/worker/src"], text=True).splitlines():
    source = Path(name)
    if source.parent == Path("api/worker/src") and source.suffix == ".py":
        shutil.copyfile(source, bundle / source.name)
PY
```

Only tracked top-level source files are copied, so a stale generated
`bundled_data.py` or `tier_policy.py` in the checkout cannot overwrite the fresh
exports. The original run used `round3/memory/tmp`; the replay uses a hidden
`.tmp` directory to keep pytest collection out of vendor's temporary repository
links. Vendor removed both temporary directories after the measured build.

```sh
"$MODEL407_NODE" --expose-gc api/worker/measure_memory.cjs \
  "$MODEL407_PUBLIC/bundle-final" --limit-mib 115 --attribute \
  --output "$MODEL407_PUBLIC/current.json"
"$MODEL407_NODE" --expose-gc api/worker/measure_memory.cjs \
  "$MODEL407_PUBLIC/bundle-final" --successor --limit-mib 115 --attribute \
  --output "$MODEL407_PUBLIC/successor.json"
MODEL407_MEMORY_MODE=warm "$MODEL407_NODE" --expose-gc \
  --require ./docs/evidence/g2-ios/MODEL-407/rollover-probe-hook.cjs \
  api/worker/measure_memory.cjs "$MODEL407_PUBLIC/bundle-final" \
  --limit-mib 115 --attribute --output "$MODEL407_PUBLIC/warm.json"
```

Each Node command is invoked directly, without a pipe. A failed memory gate
returns 1. The native successor mode crosses the boundary before the original
four requests. The warm hook adds one current-period decide before the
successor decide, then runs vocabulary, rank, and policy-check. It checks
predecessor release before successor read and verifies the response bindings.
Neither mode adds garbage collection between requests; attribution follows the
gate's memory sample.

The prototypes ran at engine
`819ba9e1aeb4e5e8a91e305a044224ff061605ed` and used the same signed public
data bundle. The whole-content C decoder failed when the successor decide
grew Wasm from 59.875 to 71.875 MiB. Its retained snapshot index stayed at
3,706,510 bytes. The bounded-array trial restored the original snapshot loader
and changed only the JSON reader. These generated-code trials are separate
from the fresh final build.

Both trial helpers are preserved in this directory. The original metadata's
`tmp/model-407/round3/root/canonical_c_decoder.py` is
`public-prototype-whole-c-helper.py` here. Its
`tmp/model-407/round3/profile/fast_array_reader.py` is
`public-prototype-bounded-array-reader.py` here. The following substitutions
reproduce the measured parser variants on separate copies of a public bundle.
They restore the baseline parser files from immutable git objects and leave
the signed data unchanged.

```sh
"$MODEL407_PYTHON" - <<'PY'
import os
from pathlib import Path
import shutil
import subprocess

out = Path(os.environ["MODEL407_PUBLIC"])
evidence = Path("docs/evidence/g2-ios/MODEL-407/round3")
baseline = "819ba9e1aeb4e5e8a91e305a044224ff061605ed"
snapshot = subprocess.check_output(
    ["git", "show", baseline + ":decision/snapshot.py"], text=True)
reader = subprocess.check_output(
    ["git", "show", baseline + ":decision/json_stream.py"], text=True)
for label in ["whole-c", "bounded-array"]:
    bundle = out / ("bundle-" + label)
    shutil.copytree(out / "bundle-final", bundle)
    (bundle / "decision/snapshot.py").write_text(snapshot)
    (bundle / "decision/json_stream.py").write_text(reader)

helper = (evidence / "public-prototype-whole-c-helper.py").read_text().strip() + "\n\n"
start = snapshot.index("def _stream_canonical_envelope(")
end = snapshot.index("def load_snapshot_bytes(", start)
(out / "bundle-whole-c/decision/snapshot.py").write_text(
    snapshot[:start] + helper + snapshot[end:])
shutil.copyfile(evidence / "public-prototype-bounded-array-reader.py",
                out / "bundle-bounded-array/decision/json_stream.py")
PY
```

Run the successor and warm commands above with `bundle-whole-c` and
`bundle-bounded-array` and distinct output paths. The final bundle's exported
build metadata differs from the historical prototype bundle; the substitutions
replay the parser behavior on the same fixture. For exact historical build
inputs, the prototype metadata records the original engine, source hashes,
ordinary vendor command, signed snapshot IDs, and bundle hash.

No private artifacts were read or copied for this evidence. The parent
executor's final private measurements are recorded separately in
`private-memory-numbers.json`. All final public/private pairs used 59.875 MiB
of Wasm. Their steady-memory differences were approximately 0.084 MiB for
current, 0.061 MiB for successor, and 0.840 MiB for warm rollover. The public
warm run was larger. The remaining difference is outside Wasm and is
consistent with the observed V8 variation; the final pairs are not all within
0.09 MiB.
