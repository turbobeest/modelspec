# MODEL-433 Worker memory verification

The final private bundle passes the ticket's 115 MiB steady-memory limit in both
periods. These measurements supersede the earlier pass. This bundle includes the
validated `block_telemetry` recipe step and the three explicit AWS telemetry
endpoints in the private source registry.

| Period | Steady MiB | Peak MiB | Exit code |
| --- | ---: | ---: | ---: |
| Current | 104.59937286376953 | 105.42255401611328 | 0 |
| Successor | 103.72702026367188 | 104.97483825683594 | 0 |

Neither final run emitted a memory warning. The acceptance gate checks steady memory.
Both runs exercised `POST /v1/decide`, `GET /v1/vocabulary`, `POST /v1/rank`,
and `POST /v1/policy-check` using the script's stubbed request boundary. Its
request handler rejects network access.

The worktree base was `bd38d72e326e3d603a45dac6fc758dc8acfeb324`.
The public HEAD at final verification was
`8e2cdd8dd5b8e7d21948d3e5fb4d22e9d3fb9a38`.
The private data HEAD was `a6f8fd798d7d6f40b35ed08320796b773f29df9a`.
The private checkout was read only during this verification.
The measured `decision/model.py` SHA-256 was
`51fe075b1eb7831f461c31c7527ee2c3ec8938bbd974abcd223f5ebb83c1ef42`.
The measured private `registry/sources.yaml` SHA-256 was
`de29dd6a39e9631014b95b777a5092976e623160f0d3873b63e9ebf47a110bbc`.
Both copied files matched their final source files after both measurements.

Tool versions:

- Node v22.22.3, from the executable required by the brief.
- Build Python 3.14.4.
- Build dependencies: pydantic 2.13.5, PyYAML 6.0.3, httpx 0.28.1, cryptography 45.0.7.
- Runtime Pyodide 0.28.3, with pydantic 2.10.6, pydantic_core 2.27.2,
  PyYAML 6.0.2, annotated-types 0.7.0 and typing-extensions 4.14.1.

Commands ran from `/Users/terbeest/dev/worktrees/model-433`.

```sh
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -c "import importlib.metadata,json; print(json.dumps({name: importlib.metadata.version(name) for name in ['pydantic','PyYAML','httpx','cryptography']}))"
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node -p "require('/tmp/model-433-scratch/memory-runtime/node_modules/pyodide/package.json').version"
git -C /tmp/model-433-scratch/modelspec-data rev-parse HEAD
mkdir -p /tmp/model-433-scratch/worker-memory
shasum -a 256 decision/model.py api/worker/vendor.py api/worker/measure_memory.cjs /tmp/model-433-scratch/modelspec-data/registry/sources.yaml
env PYTHONPATH=$PWD MODELSPEC_SNAPSHOT_KEY=model433-worker-memory-throwaway-fixture-key MODELSPEC_REQUIRE_DATA_DIR=1 /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /tmp/model-433-scratch/modelspec-data --out /tmp/model-433-scratch/worker-memory/bundle
cp api/worker/src/*.py /tmp/model-433-scratch/worker-memory/bundle/
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import runpy
from pathlib import Path
bundle=Path('/tmp/model-433-scratch/worker-memory/bundle')
blobs=runpy.run_path(str(bundle/'bundled_data.py'))['BLOBS']
snapshot='/api/decision/snapshot-successor.json.gz' in blobs
vocabulary='/api/decision/vocabulary-successor.json' in blobs
assert snapshot == vocabulary, 'Incomplete successor pair'
print('successor='+str(snapshot).lower())
PY
shasum -a 256 decision/model.py /tmp/model-433-scratch/worker-memory/bundle/decision/model.py /tmp/model-433-scratch/modelspec-data/registry/sources.yaml /tmp/model-433-scratch/worker-memory/bundle/registry/sources.yaml
env NODE_PATH=/tmp/model-433-scratch/memory-runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model433-worker-memory-throwaway-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs /tmp/model-433-scratch/worker-memory/bundle --limit-mib 115 --output /tmp/model-433-scratch/worker-memory/current.json
env NODE_PATH=/tmp/model-433-scratch/memory-runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model433-worker-memory-throwaway-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs /tmp/model-433-scratch/worker-memory/bundle --successor --limit-mib 115 --output /tmp/model-433-scratch/worker-memory/successor.json
```

The vendor command exited 0 and reported 129 files vendored. The copy and
successor-pair check exited 0 and printed `successor=true`. Each measurement
exited 0. Version and identity commands exited 0.

Artifacts:

- `/tmp/model-433-scratch/worker-memory/current.json`
- `/tmp/model-433-scratch/worker-memory/successor.json`
- `/tmp/model-433-scratch/worker-memory/build-metadata.json`

Limitations: this is the repository's local Pyodide probe, not a deployed
Cloudflare measurement. It used a throwaway signing key. Build Python was
3.14.4 rather than CI's 3.13, while the measured Pyodide runtime and dependency
pins match the workflow. No baseline comparison was requested or run. No
production requests, paid calls, deployment, tests or GitHub calls were made.
The earlier pass downloaded its pinned runtime wheels using Pyodide and cached
them under the existing scratch runtime's `node_modules`. Both final runs loaded
those cached packages. The difference from earlier measurements is not a
controlled comparison and does not establish a memory improvement from the code
change.

No tracked files were edited. The public default bundle was not re-vendored.
All started processes exited. The parent must remove the private
`/tmp/model-433-scratch/worker-memory/bundle` with the other private scratch data
after collecting the results.
