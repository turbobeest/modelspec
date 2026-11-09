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
