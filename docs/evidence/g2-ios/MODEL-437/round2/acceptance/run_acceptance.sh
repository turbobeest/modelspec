#!/bin/bash
set -euo pipefail
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
export PYTHONDONTWRITEBYTECODE=1
unset MODELSPEC_SOURCE_CACHE MODELSPEC_SNAPSHOT_ED25519_KEY MODELSPEC_SNAPSHOT_KEY
proof=/tmp/model-437-scratch/acceptance
python=/Users/terbeest/dev/modelspec/.venv/bin/python
candidate=/Users/terbeest/dev/worktrees/model-437
main=$proof/prepared/main
original=$proof/modelspec-data
repaired=$proof/prepared/repaired-data
policy=$proof/prepared/hosts-866.json
results=$proof/results
phase=${1:?phase is baseline, candidate-d, candidate-c, compare, gates-d, gates-c, memory-d, or memory-c}
"$python" - "$proof" "$candidate" "$phase" <<'PY'
from datetime import UTC, datetime
from pathlib import Path
import importlib.metadata,json,subprocess,sys
root,candidate=map(Path,sys.argv[1:3])
def output(command):
    return subprocess.run(command,check=True,capture_output=True,text=True).stdout.strip()
metadata=json.loads((root/'prepared.public.json').read_text())
metadata.update(phase=sys.argv[3],started=datetime.now(UTC).isoformat(),candidate_head=output(['git','-C',str(candidate),'rev-parse','HEAD']),python=sys.version,packages={name:importlib.metadata.version(name) for name in ('pydantic','PyYAML','cryptography','pypdf')},node=output(['/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node','--version']),git=output(['git','--version']),pyodide=json.loads((root/'memory-runtime/node_modules/pyodide/package.json').read_text())['version'])
(root/('provenance-'+sys.argv[3]+'.public.json')).write_text(json.dumps(metadata,indent=2)+'\n')
PY
run() { "$python" "$proof/record_command.py" "$@"; }
case "$phase" in
 baseline)
  run baseline "$python" "$proof/compare_private.py" run --main-root "$main" --candidate-root "$candidate" --host-policy "$policy" --baseline-data-dir "$original" --data-dir "$original" --output "$results" --states a
  ;;
 candidate-d)
  run candidate-main-policy "$python" "$proof/compare_private.py" run --main-root "$main" --candidate-root "$candidate" --host-policy "$policy" --baseline-data-dir "$original" --data-dir "$original" --output "$results" --states d
  ;;
 candidate-c)
  run candidate-repaired-policy "$python" "$proof/compare_private.py" run --main-root "$main" --candidate-root "$candidate" --host-policy "$policy" --baseline-data-dir "$original" --data-dir "$repaired" --output "$results" --states c
  ;;
 compare)
  run compare "$python" "$proof/compare_private.py" compare --output "$results" --states adc
  ;;
 gates-d|gates-c)
  state=${phase#gates-}
  data=$original
  if [ "$state" = c ]; then data=$repaired; fi
  for period in current successor; do
   day=$("$python" - "$results/$state/state.public.json" "$period" <<'CLOCK'
import json,sys
print(json.load(open(sys.argv[1]))[sys.argv[2]]['as_of'])
CLOCK
)
   run "gate-$state-$period" "$python" "$proof/check_completeness.py" --code "$results/$state/code" --data-dir "$data" --output "$proof/gate-$state-$period" --as-of "$day"
  done
  ;;
 memory-d|memory-c)
  state=${phase#memory-}
  data=$original
  if [ "$state" = c ]; then data=$repaired; fi
  run "memory-$state" "$python" "$proof/measure_private.py" --code "$results/$state/code" --data-dir "$data" --output "$proof/memory-$state" --node /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --runtime "$proof/memory-runtime"
  ;;
 *) echo "Unknown phase: $phase" >&2; exit 2 ;;
esac
