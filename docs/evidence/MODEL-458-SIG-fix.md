# MODEL-458-SIG verification

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`, also the fetched
`origin/main` before implementation. The assigned branch is `model-458-sig`.

Environment: Python 3.14.4, pytest 9.1.1, httpx 0.28.1, PyYAML 6.0.3,
Git 2.50.1, GitHub CLI 2.103.3. Tests use offline fixtures and run serially.

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

## AUD-14-F10

Optional Hugging Face search accepts a list of repository objects. Invalid
response shapes produce a gather diagnostic while provider-verified cards
still draft. Empty searches and exact repository ownership/name matching
retain their behavior.

The retained reproduction returned `3 failed, 11 deselected`, exit 1.
The permanent regressions returned `6 failed, 4 passed, 73 deselected`, exit 1,
before the fix. Non-object rows raised `AttributeError`; invalid top-level
shapes lacked a failure diagnostic. The focused suites returned `89 passed`,
exit 0, after the fix.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider --tb=short --basetemp /tmp/MODEL-458-SIG-scratch/executor/repro-f10 /tmp/MODEL-458-SIG-scratch/executor/test_repro_F10.py -k test_malformed_optional_hf_does_not_block_card
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short --basetemp /tmp/MODEL-458-SIG-scratch/executor/red-f10 tests/test_release_signals.py -k 'test_malformed_optional_hf_does_not_block_card or test_valid_optional_hf'
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/MODEL-458-SIG-scratch/executor/green-f10 tests/test_release_signals.py tests/test_release_signal_prices.py
```

## AUD-14-F2

Hugging Face repository owners must match the configured feed author before
mapping to the registry's provider. Mismatches hold the source with a
`parse_failed` diagnostic. Matching ignores author case and preserves explicit
author-to-provider aliases.

The retained reproduction returned `1 failed, 7 deselected`, exit 1.
Permanent regressions returned `2 failed, 2 passed, 31 deselected`, exit 1,
because the filter emitted signals from mismatched feeds. After the fix,
the existing watcher, precision and filter suites returned `173 passed`, exit 0.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider --tb=short --basetemp /tmp/MODEL-458-SIG-scratch/executor/repro-f2 /tmp/MODEL-458-SIG-scratch/executor/test_repro_F2.py -k test_huggingface_foreign_owner_cannot_be_credited_to_requested_lab
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short --basetemp /tmp/MODEL-458-SIG-scratch/executor/red-f2 tests/test_release_watch.py -k 'test_huggingface_foreign_owner or test_huggingface_configured_author'
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/MODEL-458-SIG-scratch/executor/green-f2 tests/test_release_watch.py tests/test_release_watch_precision.py tests/test_release_watch_filter.py
```

## AUD-14-F3

Page extraction requires valid UTF-8. A decoding failure reports
`parse_failed` for that source while later healthy sources continue.
Valid UTF-8 retains the complete model ID.

The retained reproduction returned `1 failed, 7 deselected`, exit 1.
Permanent regression `test_invalid_utf8_cannot_create_truncated_model_identity`
returned `1 failed, 1 passed, 35 deselected`, exit 1: the malformed input
incorrectly reported `ok`. The focused watcher suites returned `175 passed`,
exit 0, after the fix.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider --tb=short --basetemp /tmp/MODEL-458-SIG-scratch/executor/repro-f3 /tmp/MODEL-458-SIG-scratch/executor/test_repro_F3.py -k test_invalid_utf8_cannot_create_truncated_model_identity
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short --basetemp /tmp/MODEL-458-SIG-scratch/executor/red-f3 tests/test_release_watch.py -k test_invalid_utf8_cannot_create_truncated_model_identity
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/MODEL-458-SIG-scratch/executor/green-f3 tests/test_release_watch.py tests/test_release_watch_precision.py tests/test_release_watch_filter.py
```

## AUD-14-F8

OpenRouter timestamps must be finite numeric values within the platform's
supported conversion range. Invalid supplied values report `parse_failed`
for that source; they do not become undated discoveries. Later healthy
sources continue. Valid timestamps retain their precision and recency
filtering. The existing null/missing-date behavior remains unchanged.

The retained reproduction returned `1 failed, 7 deselected`, exit 1, with
`OverflowError: timestamp out of range for platform time_t`. Permanent
regressions returned `11 failed, 6 passed, 37 deselected`, exit 1, before the
fix. They cover numeric overflow, nonfinite values, invalid value types,
simulated platform conversion failures, valid dates and recency filtering.
After the fix, `17 passed, 37 deselected`, exit 0.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider --tb=short --basetemp /tmp/MODEL-458-SIG-scratch/executor/repro-f8 /tmp/MODEL-458-SIG-scratch/executor/test_repro_F8.py -k test_out_of_range_created_is_one_source_outage
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short --basetemp /tmp/MODEL-458-SIG-scratch/executor/red-f8 tests/test_release_watch.py -k 'test_out_of_range_created or test_timestamp_platform_failure or test_valid_created_timestamp'
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/MODEL-458-SIG-scratch/executor/green-f8-focused tests/test_release_watch.py -k 'test_out_of_range_created or test_timestamp_platform_failure or test_valid_created_timestamp'
```

## Final verification

The combined focused run returned `327 passed, 1 skipped`, exit 0. The skipped
check requires a built site via `MODELSPEC_DIST`; this ticket does not build
or change the site. All nine selected cases from the retained reproductions
also passed on the fixed implementation, exit 0. The local reproduction
files and detailed logs remained outside the repository.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/MODEL-458-SIG-scratch/executor/green-final tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch.py tests/test_release_watch_precision.py tests/test_release_watch_filter.py tests/test_removed_sources.py
git diff --check
```

The final diff changes only the two release-signal implementation modules,
their two focused test files and this evidence file. A read-only second-agent
review found no actionable issues. Independent review remains pending.

## Observation limits

No live provider responses, production behavior, deployment or publication
were observed. No paid services were called. The local full suite was not
run; CI owns that gate. No contract range, frozen data, source-terms class,
production switch, price, ranking floor or legal text changed.
