# MODEL-458-SIG verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`, also the fetched
`origin/main` before implementation. The assigned branch is `model-458-sig`.

Environment: Python 3.14.4, pytest 9.1.1, httpx 0.28.1, PyYAML 6.0.3,
Git 2.50.1. Tests use offline fixtures and run serially.

## AUD-14-F1

Visible primary-source relationships must establish the complete model and
provider identities. Conflicting publishers remain uncertain. Exact visible
announcements, model versions, catalogue aliases and structured metadata
retain their existing behavior.

The retained reproduction failed before the change. Permanent regression
`test_similar_name_is_not_identity` and exact-identity controls ran before
implementation: `6 failed, 10 passed, 57 deselected`, exit 1. Detailed red
output was kept only in the designated local scratch directory.

The focused package tests then passed: `79 passed`, exit 0.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/MODEL-458-SIG-scratch/executor/green-f1 tests/test_release_signals.py tests/test_release_signal_prices.py
```

## Observation limits

No live provider responses, production behavior, deployment or publication
were observed. No paid services were called. The local full suite was not
run; CI owns that gate. No contract range, frozen data, source-terms class,
production switch, price, ranking floor or legal text changed.
