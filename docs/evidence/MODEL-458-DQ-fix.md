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

No private pages were changed. No live source reads, provider calls, production
changes, or local full-suite runs were performed.
