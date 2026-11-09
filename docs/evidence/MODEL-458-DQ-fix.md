# MODEL-458-DQ verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`, equal to fetched
`origin/main` at execution start. Final branch SHA is reported with the draft
PR and executor completion record; resolve it with `git rev-parse model-458-dq`.

All tests use synthetic fixtures. Private-data results are aggregate counts
from a read-only export of the supplied checkout's `origin/main`.

## AUD-07-F1

Benchmark validation and the audit share a structural-key check. Diagnostics
name known schema parents only. All-file findings survive serving calibration.
Model facts and evidence remain owned by their existing loaders.

Red command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_benchmark_validation.py
```

Result: `8 failed, 2 passed`. The four parameterizations of
`test_benchmark_validator_rejects_unknown_nested_key` returned `[]` instead of
`unknown_benchmark_key`; the four parameterizations of
`test_trust_inventory_reports_unknown_benchmark_key` lacked that finding.
The quoted-string and independent model-field controls passed.

Green command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_benchmark_validation.py tests/test_data_trust.py tests/test_decision_registry.py
```

Result: `164 passed in 19.64s`.

The private offline audit returned exit 1 with 41 structural findings on 32
benchmark pages. Known parent counts: `freshness` 32, `dataset` 3,
`contamination` 3, `saturation` 3. Multiple parents can occur on one page.

## AUD-07-F3

The shared safe YAML loader rejects repeated authored mapping keys before
construction. Diagnostics retain line and column without authored text. Valid
anchors, explicit merge overrides, merge-sequence precedence, Boolean values,
dates, sets and binary tags retain their supported behavior. The audit checks
registry and lineup documents and preserves duplicate diagnostics through
calibration, including collection failure.

Red command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_yaml_loading.py tests/test_benchmark_validation.py
```

Result: `18 failed, 26 passed in 4.02s`. `test_duplicate_aliases_are_rejected`
and `test_nested_duplicate_mapping_is_rejected` did not raise on either loader.
Validator and audit regressions lacked `duplicate_yaml_key`, including after
calibration. The safe-tag and merge controls passed before the change.

Green command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_yaml_loading.py tests/test_benchmark_validation.py tests/test_data_trust.py tests/test_card_yaml_roundtrip.py
```

Result: `115 passed in 15.24s`.

Review added `test_quoted_merge_key_is_distinct_from_merge_directive` on both
loaders. The two controls initially failed, then passed after using a distinct
merge-tag identity. Command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_yaml_loading.py -k quoted_merge
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_yaml_loading.py
```

The private audit returned exit 1 and retained 10 duplicate-key diagnostics,
41 structural diagnostics on 32 pages, and one collection-failure diagnostic.

Broader loader check:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py tests/test_model_191_refinements.py
```

Result: `11 failed, 59 passed in 21.30s`. Each failure reaches the new duplicate
mapping-key boundary in the frozen benchmark data. Existing data remains
unchanged; the ticket does not authorize its correction.

No private pages were changed. No live source reads, provider calls, production
changes, or local full-suite runs were performed.

## AUD-07-F2

The offline inventory checks manifest-attributed retained files against the
existing restrictive source policy. It handles requested and redirect origins,
deduplicates files, and reports missing, unattributed or bounded-out inputs as
coverage limitations. Paths stay within the supplied data root. The composed
audit root uses that original data root for retained-file inventory.

Red command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_trust_retention.py
```

Result: `38 failed, 2 passed in 6.88s`. The reproduction returned zero errors;
`test_audit_reports_retained_copy_from_cite_only_host` lacked the specific
`retained_cite_only_copy` finding. Controls cover retainable origins,
metadata-only records, duplicate manifests, redirects and bounded file handling.
The initial focused green run returned `40 passed in 12.29s`.

Review added regressions for valid parent-relative paths, malformed paths and
JSON-body attribution. No source-body decompression or source fetch is needed.
The private inventory identifies 22 unique retained files under the existing
policy. This is a count-only check; no retained file or policy class changed.

Green command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_trust_retention.py tests/test_data_trust.py tests/test_cite_only_retention.py
```

Result: `151 passed in 19.32s`. Private coverage limitations are 87 unattributed
files, seven missing references and four manifests exceeding the 2 MiB read
bound. The check does not inspect or expand source archives to determine origin.

## AUD-07-F5

Both audit range checks now use admission's effective-range helper. Open scales
have no invented zero minimum. Fraction, percent, explicit bounds and signed
p-MRR retain their existing admission rules. Finite and unit diagnostics remain
separate. No contract field or accepted admission range changes.

Read the MODEL-276 history with:

```sh
git show f60433939ffdbe33b7ca588fb0a2b6ef9b17c07d -- schema/benchmark_values.py tests/test_benchmark_values.py
```

Red command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_trust.py -k 'trust_audit_agrees_with_open_scale or trust_range_classes_agree or trust_range_matches_declared_bounds or trust_open_scale'
```

Result: `12 failed, 18 passed, 69 deselected in 6.19s`. The three
`test_trust_audit_agrees_with_open_scale_admission` cases reported
`benchmark_range`; the separate range-class test reported three errors instead
of none. The explicit and signed controls also exposed disagreement with
admission. The original synthetic reproduction reported `{'balance': 1}` after
admission accepted the value.

Green command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_benchmark_values.py tests/test_data_trust.py
```

Result: `141 passed in 19.15s`. The unchanged 42-test admission suite passes.
The private census identifies two historical score records on two model pages
whose old audit range classification disagreed with admission. This observation
does not establish that serving rejected those records.

## Final verification and limitations

Tool versions: Python 3.14.4, pytest 9.1.1, Pydantic 2.13.5, PyYAML 6.0.3,
Git 2.50.1, Node v22.22.3. Versions were read with Python module attributes,
`git --version`, and `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version`.

Combined focused command:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_benchmark_validation.py tests/test_yaml_loading.py tests/test_card_yaml_roundtrip.py tests/test_benchmark_values.py tests/test_data_trust.py tests/test_data_trust_retention.py tests/test_cite_only_retention.py tests/test_decision_registry.py
```

Result: `9 failed, 347 passed in 39.16s`. All new regressions pass. The nine
registry failures, like the 11 broader pipeline failures above, reach duplicate
mapping keys in frozen benchmark data. No test was weakened and no frozen data
was changed. These failures block readiness.

The supplied private checkout differs from its `origin/main`. This read-only
export used the committed tree, without changing that checkout:

```sh
git -C /Users/terbeest/dev/modelspec-data archive --format=tar --output=/tmp/MODEL-458-DQ-scratch/root/data.tar origin/main
mkdir -p /tmp/MODEL-458-DQ-scratch/root/private-data
tar -xf /tmp/MODEL-458-DQ-scratch/root/data.tar -C /tmp/MODEL-458-DQ-scratch/root/private-data
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.data_trust data --data-dir /tmp/MODEL-458-DQ-scratch/root/private-data --date 2026-11-09 --json > /tmp/MODEL-458-DQ-scratch/root/final-private.json
```

The final audit exits 1. Its 74 errors comprise 41 structural findings on 32
benchmark pages, 10 duplicate-key findings, 22 retained-copy findings and one
snapshot collection failure. Historical range classifications decrease from
144 to 142. This audit does not establish served-fact accuracy: collection stops
at the duplicate-key boundary. It performs no source sampling or network reads.

Private aggregate results can be reproduced without printing private details:

```python
import json
from collections import Counter
from pathlib import Path
r = json.loads(Path('/tmp/MODEL-458-DQ-scratch/root/final-private.json').read_text())['invariants']
print(Counter(f['rule'] for f in r['findings'] if f['severity'] == 'error'))
print(len({f['id'] for f in r['findings'] if f['rule'] == 'unknown_benchmark_key'))
print(sum(r['legacy_provenance']['range_classes'].values()))
```

The deploy-style private memory attempt ran through the machine-wide heavy
command wrapper, with a throwaway signing key. The executed command was:

```sh
/Users/terbeest/.codex-g2/heavy.sh /bin/bash /tmp/MODEL-458-DQ-scratch/root/memory-probe.sh
```

The script starts with `set -eu` and runs these stages from the engine root:

```sh
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
export PYTHONPATH="$PWD"
export TMPDIR=/tmp/MODEL-458-DQ-scratch/root/memory/tmp
export MODELSPEC_REQUIRE_DATA_DIR=1
export MODELSPEC_SNAPSHOT_KEY=model458-dq-memory-fixture-key
/Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --data-dir /tmp/MODEL-458-DQ-scratch/root/private-data --out /tmp/MODEL-458-DQ-scratch/root/memory/bundle
cp api/worker/src/*.py /tmp/MODEL-458-DQ-scratch/root/memory/bundle/
npm install --prefix /tmp/MODEL-458-DQ-scratch/root/memory/runtime --no-save pyodide@0.28.3
export NODE_PATH=/tmp/MODEL-458-DQ-scratch/root/memory/runtime/node_modules
node --expose-gc api/worker/measure_memory.cjs /tmp/MODEL-458-DQ-scratch/root/memory/bundle --limit-mib 115 --output /tmp/MODEL-458-DQ-scratch/root/memory/current.json
node --expose-gc api/worker/measure_memory.cjs /tmp/MODEL-458-DQ-scratch/root/memory/bundle --successor --limit-mib 115 --output /tmp/MODEL-458-DQ-scratch/root/memory/successor.json
```

Both attempts, including the final range-helper version, exited 2 during private
vendoring. Reported categories were `LoadError` from export and `RuntimeError`
from its parent. The later stages did not run. Current steady-state memory:
**unmeasured**. Successor steady-state memory: **unmeasured**. Neither result
establishes compliance with the unchanged 115 MiB limit. No gate was raised and
no data was repaired to obtain a measurement.

The public bundle was re-vendored into scratch and its imports checked:

```sh
env PYTHONPATH=$PWD /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --out /tmp/MODEL-458-DQ-scratch/root/public-bundle --check
```

Exit 0: `vendored 129 files`; `bundle imports cleanly with only declared dependencies`.
This import check is not a private-data memory measurement.

Status: **BLOCKED** pending separate data corrections, passing affected
catalogue suites and successful private current/successor memory measurements.
This ticket changes no private data, frozen data, ranking floors, legal text,
retention policy, production switches, prices, plans or workflows.
