#!/bin/bash
set -euo pipefail

# Planned c probe; not executed because c failed its production gate.
# Run only after compare_private.py has successfully evaluated state c.
# No production credentials are read or used.
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
export MODELSPEC_SNAPSHOT_KEY=model437-private-proof-throwaway-key
export MODELSPEC_REQUIRE_DATA_DIR=1
export DATA_SPLIT_ENABLED=false
proof_root=/tmp/model-437-scratch/proof-setup/results
candidate_root=$proof_root/c/code
private_root=/tmp/model-437-scratch/modelspec-data
bundle_root=/tmp/model-437-scratch/proof-setup/memory-bundle-c
runtime_root=/tmp/model-437-scratch/proof-setup/memory-runtime
python_bin=/Users/terbeest/dev/modelspec/.venv/bin/python
export PYTHONPATH=$candidate_root

npm install --prefix "$runtime_root" --no-save pyodide@0.28.3
"$python_bin" "$candidate_root/api/worker/vendor.py" --data-dir "$private_root" --out "$bundle_root"
# The staged code tree contains tracked handwritten top-level modules only.
# vendor.py's generated bundled_data.py and tier_policy.py remain in place.
"$python_bin" - "$candidate_root/api/worker/src" "$bundle_root" <<'PY'
from pathlib import Path
import shutil
import sys
source, output = map(Path, sys.argv[1:])
for path in source.glob('*.py'):
    if path.name not in {'bundled_data.py', 'tier_policy.py'}:
        shutil.copy2(path, output / path.name)
PY
NODE_PATH="$runtime_root/node_modules" node --expose-gc "$candidate_root/api/worker/measure_memory.cjs" "$bundle_root" --limit-mib 115 --output /tmp/model-437-scratch/proof-setup/memory-current.json
NODE_PATH="$runtime_root/node_modules" node --expose-gc "$candidate_root/api/worker/measure_memory.cjs" "$bundle_root" --successor --limit-mib 115 --output /tmp/model-437-scratch/proof-setup/memory-successor.json
