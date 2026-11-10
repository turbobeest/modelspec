# MODEL-458-SIG-C

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`.
Branch: `model-458-sig-c`.
The final commit SHA is in the draft PR body.

Environment: macOS, Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, httpx 0.28.1,
Git 2.50.1. Commands ran from the assigned worktree.

## AUD-14-F9

A malformed mandatory source now makes `scripts/process_release_signals.py`
exit 2. The diagnostic is one line on stderr and names the source URL. The
processor writes no result file, leaves the pending queue unchanged, and
leaves the existing card unchanged. An uncertain identity is still an
identity-review result. A prohibited-source URL still raises `ValueError`.

The permanent regression is
`test_bad_required_source_exits_with_controlled_failure`, eight cases covering
an empty body, truncated JSON, an HTML body, a non-UTF-8 body, a provider map
that is not an object, a models map that is not an object, and two unusable
JSON-LD dates.

Before the change the selector reported `8 failed, 87 deselected in 0.42s`,
exit 1. The failures were `JSONDecodeError`, `UnicodeDecodeError`,
`AttributeError`, and `ValueError`.

After the change the selector reported `8 passed, 87 deselected in 0.42s`,
exit 0. The focused release-signal files reported `101 passed in 2.85s`,
exit 0. `tests/test_release_watch.py` reported `54 passed in 16.37s`, exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k test_bad_required_source_exits_with_controlled_failure --tb=line --basetemp /tmp/MODEL-458-SIG-C-scratch/red
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k test_bad_required_source_exits_with_controlled_failure --tb=short --basetemp /tmp/MODEL-458-SIG-C-scratch/green
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py --tb=line --basetemp /tmp/MODEL-458-SIG-C-scratch/focused
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch.py --tb=line --basetemp /tmp/MODEL-458-SIG-C-scratch/watch
```

Not observed: a production source fetch, the full pytest suite, or CI for
this commit.
