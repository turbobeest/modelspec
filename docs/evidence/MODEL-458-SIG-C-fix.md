# MODEL-458-SIG-C

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`.
Branch: `model-458-sig-c`.
The final commit SHA is in the draft PR body.

Environment: macOS, Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, httpx 0.28.1,
Git 2.50.1. Commands ran from the assigned worktree. In the commands,
`python` is the repository's Python environment and `$SCRATCH` is the ticket
scratch directory.

## AUD-14-F9

A malformed mandatory source now makes `scripts/process_release_signals.py`
exit 2. The diagnostic is one line of at most 500 characters on stderr. The
source URL is shown first, up to 300 characters, so shortening the detail
leaves that shown URL in place. The processor writes no result file, leaves
the pending queue unchanged, and leaves the existing card unchanged. An
uncertain identity is still an identity-review result. A prohibited-source
URL still raises `ValueError`.

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
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k test_bad_required_source_exits_with_controlled_failure --tb=line --basetemp $SCRATCH/red
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k test_bad_required_source_exits_with_controlled_failure --tb=short --basetemp $SCRATCH/green
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py --tb=line --basetemp $SCRATCH/focused
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_watch.py --tb=line --basetemp $SCRATCH/watch
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

`RequiredSourceError` builds one line of at most 500 characters. Line breaks
in the source URL and the detail become spaces. A URL longer than 300
characters is shown as its first 300 characters followed by `...`, and the
detail is what gets shortened after that.

`test_long_date_published_diagnostic_is_bounded` uses a primary
`datePublished` of 100000 characters. Before the bound it reported
`1 failed, 114 deselected in 0.43s`, exit 1, captured output length 100105.
After the bound, that test plus the malformed-source selector reported
`11 passed, 104 deselected in 0.54s`, exit 0.

### Non-object payloads

`test_bad_required_source_exits_with_controlled_failure` now includes a
top-level array and a top-level `null` models.dev body. On the unchanged
type check, `-k "top-level-array or top-level-null"` reported
`2 passed, 115 deselected in 0.45s`, exit 0.

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
file is written, and the pending file is unchanged. On the unchanged code,
`-k test_prohibited_release_url_stays_a_value_error` reported
`1 passed, 117 deselected in 0.45s`, exit 0.

With `main` also catching `ValueError`, the same selector reported
`1 failed, 117 deselected in 0.58s`, exit 1 (`DID NOT RAISE ValueError`).
With `RequiredSourceError` made a subclass of `ValueError`, the same
selector reported
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
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch_filter.py --tb=line --basetemp $SCRATCH/focused
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$SCRATCH:$PWD" python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch_filter.py --tb=line --basetemp $SCRATCH/blocked
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py --tb=line --basetemp $SCRATCH/removed
```

The focused files reported `193 passed in 44.34s`, exit 0. The same files
with `socket.socket.connect` and `socket.create_connection` raising reported
`193 passed in 40.65s`, exit 0, and 0 connect attempts. The removed-source
guard reported `46 passed, 1 skipped in 52.79s`, exit 0.

Not observed: a production source fetch, the full pytest suite, or CI for
the round 2 head. The round 2 head is the draft PR head.

## Round 3

`origin/main` was merged before the other edits. Focused tests on that
merge, before any other change, reported `193 passed in 41.70s`, exit 0.

The same environment as above. Commands ran from the worktree root.

### Bound where the error is built

`test_required_source_error_bounds_the_built_message` builds
`RequiredSourceError` for a normal source URL. A detail of 100000 characters
followed by a line break stays one line of at most 500 characters, starts
with `required source <url> failed: `, and still holds the start of the
detail. A short detail that holds a line break is kept whole, on one line.
The captured-output test from round 2 is unchanged.

On the unchanged constructor,
`-k test_required_source_error_bounds_the_built_message` reported
`1 passed, 125 deselected in 0.50s`, exit 0. The same command, with
`--tb=line`, was used for each temporary edit below:

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k test_required_source_error_bounds_the_built_message --tb=line
```

Each temporary edit was reverted. The same selector then failed:

- Limit raised to 550: `1 failed, 125 deselected in 0.43s`, exit 1
  (length 550).
- Detail cut to 500 and the prefix added after: `1 failed, 125 deselected
  in 0.44s`, exit 1 (length 552).
- Constructor left unbounded, with the 500-character cut where `main`
  prints: `1 failed, 125 deselected in 0.44s`, exit 1 (length 100064).
- Detail dropped: `1 failed, 125 deselected in 0.44s`, exit 1 (the detail
  start was absent).
- Line-break flattening removed: `1 failed, 125 deselected in 0.45s`,
  exit 1 (the short detail kept its line break).

After the reverts the selector reported `1 passed, 125 deselected in 0.42s`,
exit 0.

### Any source URL

Line breaks in the URL are flattened the same way as the detail. A URL
longer than 300 characters is shown as its first 300 characters followed by
`...`. The message is then one line of at most 500 characters, and the
shown URL comes first. The error keeps the URL as given.

Before that change,
`-k "test_required_source_error_bounds_a_long_url or test_required_source_error_flattens_a_url_line_break or test_required_source_error_keeps_a_short_url_message"`
reported `2 failed, 1 passed, 126 deselected in 0.50s`, exit 1. The
100000-character URL produced a message of 100025 characters. The URL that
holds a line break left that break in the message. The URL of 300
characters or fewer, with no line break, passed.

After the change,
`-k "test_required_source_error_bounds_the_built_message or test_required_source_error_bounds_a_long_url or test_required_source_error_flattens_a_url_line_break or test_required_source_error_keeps_a_short_url_message or test_long_date_published_diagnostic_is_bounded or test_bad_required_source_exits_with_controlled_failure or test_required_source_diagnostic_is_on_stderr or test_prohibited_release_url_stays_a_value_error"`
reported `19 passed, 110 deselected in 0.46s`, exit 0.

### Falsy row under the matching provider

`test_falsy_matching_provider_row_has_no_models_map` covers `null`, `0`,
`""`, and `[]` under the key of the matching provider. Each ends in
`RequiredSourceError` because the provider row has no models map. The
round-2 test for a falsy row beside the matching provider is unchanged.

On the unchanged branch,
`-k "test_falsy_matching_provider_row_has_no_models_map or test_falsy_provider_row_is_an_empty_row"`
reported `8 passed, 125 deselected in 0.49s`, exit 0.

With the falsy-row branch skipping the entry, this command reported
`4 failed, 129 deselected in 0.43s`, exit 1 (`IdentityUncertainError`, not
`RequiredSourceError`):

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_signals.py -k test_falsy_matching_provider_row_has_no_models_map --tb=line
```

The edit was reverted. The same selector then reported
`4 passed, 129 deselected in 0.43s`, exit 0.

### Focused runs

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch_filter.py --tb=line --basetemp $SCRATCH/merge
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch_filter.py --tb=line --basetemp $SCRATCH/focused
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$SCRATCH:$PWD" python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch_filter.py --tb=line --basetemp $SCRATCH/blocked
```

The merge run reported `193 passed in 41.70s`, exit 0. The focused files
after these tests reported `201 passed in 42.93s`, exit 0. The same files
with `socket.socket.connect` and `socket.create_connection` raising reported
`201 passed in 41.41s`, exit 0, and 0 connect attempts.

Not observed: a production source fetch, the full pytest suite, or CI for
this head.
