# MODEL-458-SIG-C

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`.
Branch: `model-458-sig-c`.
The final commit SHA is in the draft PR body.

Environment: macOS, Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, httpx 0.28.1,
Git 2.50.1. Commands ran from the assigned worktree.

## AUD-14-F9

A malformed mandatory source now makes `scripts/process_release_signals.py`
exit 2. The diagnostic is one line of at most 500 characters on stderr. The
source URL comes first, so shortening the detail leaves the URL in place. The
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

## Round 2

`origin/main` was merged before the other edits. The merge commit is
`dda287a047a39becb10e45ec52e46d542b165f43`. Focused tests on that merge,
before any other change, reported `180 passed in 41.45s`, exit 0.

The same environment as above. Commands ran from the worktree root.

### Decode failures

`_load_required_json` now turns every `ValueError` and every `RecursionError`
from the mandatory JSON decode into `RequiredSourceError`. The same test
gained a 5000-digit integer body and a body of 200000 nested open brackets.

Before the loader change the selector reported `2 failed, 112 deselected in
0.52s`, exit 1. The failures were `ValueError` (integer digit limit) and
`RecursionError` (nested array). After the change the original selector
reported `10 passed, 104 deselected in 0.46s`, exit 0.

### Diagnostic bound

`RequiredSourceError` builds one line of at most 500 characters. The source
URL is the prefix, and the detail is what gets shortened. Newlines in the
detail become spaces.

`test_long_date_published_diagnostic_is_bounded` uses a primary
`datePublished` of 100000 characters. Before the bound it reported
`1 failed, 114 deselected in 0.43s`, exit 1, captured output length 100105.
After the bound, that test plus the malformed-source selector reported
`11 passed, 104 deselected in 0.54s`, exit 0.

### Non-object payloads

`test_bad_required_source_exits_with_controlled_failure` now includes a
top-level array and a top-level `null` models.dev body. On the unchanged
type check the selector reported `2 passed, 115 deselected in 0.45s`, exit 0.

With the top-level type check removed, the same selector reported
`2 failed, 115 deselected in 0.50s`, exit 1 (`AttributeError` on `list` and
`NoneType`). With that check raising the identity-uncertain error instead,
it reported `2 failed, 115 deselected in 0.47s`, exit 1 (`main` returned 0).
Both edits were reverted. The selector then reported `2 passed, 115
deselected in 0.43s`, exit 0.

### Prohibited-source refusal

`test_prohibited_release_url_stays_a_value_error` points the listing
`release_url` at an excluded host built from split string literals. `main`
raises `ValueError`, the error is not a `RequiredSourceError`, no result
file is written, and the pending file is unchanged. On the unchanged code
the selector reported `1 passed, 117 deselected in 0.45s`, exit 0.

With `main` also catching `ValueError`, it reported `1 failed, 117
deselected in 0.58s`, exit 1 (`DID NOT RAISE ValueError`). With
`RequiredSourceError` made a subclass of `ValueError`, it reported
`1 failed, 117 deselected in 0.48s`, exit 1 (`issubclass` was true). Both
edits were reverted. The selector then reported `1 passed, 117 deselected
in 0.50s`, exit 0.

### Stream and listing rows

`test_required_source_diagnostic_is_on_stderr` asserts the diagnostic is on
stderr and stdout has none. `test_falsy_provider_row_is_an_empty_row` covers
`null`, `0`, `""`, and `[]` at `_models_dev_listing`.
`test_provider_matches_by_key_alone` and `test_provider_matches_by_name_alone`
cover those two matches at the same function. On the unchanged code the four
selectors reported `7 passed, 118 deselected in 0.51s`, exit 0.

Printing the diagnostic to stdout: `1 failed, 124 deselected in 0.53s`,
exit 1 (the URL was absent from stderr). Rejecting every falsy row:
`4 failed, 121 deselected in 1.46s`, exit 1. Tolerating only `null`:
`3 failed, 1 passed, 121 deselected in 0.50s`, exit 1. Key match removed:
`1 failed, 1 passed, 123 deselected in 0.56s`, exit 1
(`IdentityUncertainError` on the key test). Name match removed:
`1 failed, 1 passed, 123 deselected in 0.43s`, exit 1
(`IdentityUncertainError` on the name test). All five edits were reverted.
The four selectors then reported `7 passed, 118 deselected in 0.46s`, exit 0.

### Focused runs

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch_filter.py --tb=line --basetemp /tmp/MODEL-458-SIG-C-scratch/focused
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/tmp/MODEL-458-SIG-C-scratch:$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch_filter.py --tb=line --basetemp /tmp/MODEL-458-SIG-C-scratch/blocked
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py --tb=line --basetemp /tmp/MODEL-458-SIG-C-scratch/removed
```

The focused files reported `193 passed in 44.34s`, exit 0. The same files
with `socket.socket.connect` and `socket.create_connection` raising reported
`193 passed in 40.65s`, exit 0, and 0 connect attempts. The removed-source
guard reported `46 passed, 1 skipped in 52.79s`, exit 0.

Not observed: a production source fetch, the full pytest suite, or CI for
the round 2 head. The round 2 head is the draft PR head.
