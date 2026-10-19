# MODEL-226 round 9 executor evidence

Round 9 walks structured values in the shared exclusion guard.
`excluded_in` visits dicts, lists, tuples, strings, and other scalars
converted with `str`. It applies `excluded_publisher` to every string.
A dict key is exempt only when it equals the legacy source field key.
The value of that key is still walked. Text that only looks like the
key is not exempt.

`without_legacy_source_keys` is gone. Snapshot admission walks the
content object. `guard_output` walks an object, or parses a JSON string
that starts with `{` or `[` before the walk. The breakdown and pipeline
paths pass `model_dump` output. Page checks decode HTML entities in
visible text and in every attribute value, then parse JSON-LD before
the walk.

Rounds 7 and 8 still hold. A blocked draft name or lab is still
replaced by "the new model" or "the lab". Model cards were not
rewritten. The legacy field key stayed on the cards.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Base after merging `origin/main` `6f45c2a7dc9ce2e771bd1ecea926a1a29fe1ad49`:
  `1539262d3ea7b29305e7a9209b0966cd837ad604`. The merge was clean. The
  pre-merge tip was `4903155cfd94b4793a96616dfd789fad9a3ea2e7`.
- Fix: `8579b06e9bb599e3c5a953e6e128ed67cf81be40`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.
- The pin generators ran and left the tree unchanged.
  `python -m pipeline.agent_copy write`, `python -m api.worker.openapi`,
  and `python -m qa.contracts` each exited 0. `git status --short` was
  empty afterward.

## Tools

- Python 3.14.4
- pytest 9.1.1
- pytest-xdist 3.8.0
- ruff 0.16.6
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  npm 10.9.8. The shell function `npm` exits 126. The absolute binary
  was used for `npm ci`, `npm test`, and `npm run build`.
- flock 0.4.0 (`/opt/homebrew/bin/flock`)
- gh 2.102.0
- git 2.50.1
- Unicode 16.0.0

## Red

The new walker, snapshot, guard, separator, surface-lint, and
serialized-breakdown tests ran against the previous text exemption,
before the production edit. Log: `/tmp/model-226-r9-red.txt`.

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=line tests/test_removed_sources.py::test_excluded_in_checks_every_string_except_the_legacy_key tests/test_removed_sources.py::test_guard_output_reads_serialized_values tests/test_removed_sources.py::test_every_separator_inside_a_json_value_is_excluded tests/test_removed_sources.py::test_a_snapshot_refuses_a_value_hidden_by_json_escaping tests/test_surface_lint.py::test_surface_lint_rejects_entity_and_key_shaped_publisher_text tests/test_surface_lint.py::test_a_markdown_value_is_not_exempt_because_it_looks_like_the_legacy_key tests/test_surface_lint.py::test_a_json_value_is_not_exempt_because_it_looks_like_the_legacy_key tests/test_release_blog.py::test_a_serialized_breakdown_cannot_hide_a_publisher_value
```

Pytest exited 1. `11 failed, 2 passed in 11.71s`. The two passes were
the HTML body cases whose entities the page parser already decoded.
`excluded_in` could not be imported.
`guard_output` rejected a dict. The separator matrix recorded
`4856 serialized values passed`, starting with `Artificial\tAnalysis`,
`Model Artificial\tAnalysis name`, and `Artificial\nAnalysis`. The
snapshot fact values did not raise `SnapshotBuildError`. Attribute and
key-shaped page text produced no lexicon finding. The serialized
breakdown did not raise `BreakdownError`.

## Green

The same command, after the walker landed, printed `13 passed in 0.71s`.
The shell recorded `EXIT:0`. The HTML cases count as separate parameters.

`tests/test_removed_sources.py`, `tests/test_surface_lint.py`,
`tests/test_landing.py::test_the_positioning_does_not_overclaim`,
`tests/test_method.py`, and the serialized-breakdown test printed
`160 passed, 1 skipped in 270.95s`. The shell recorded `EXIT:0`.

The tracked-file census failed once before the allowlist update, and
only on `tests/test_release_blog.py` and `tests/test_surface_lint.py`.
Those files name the publishers in the new probes. They were added to
`ALLOWED`, the same way `tests/test_release_blog_platforms.py` already
was. The census then passed inside the 160.

Caller suites. Flock waited while worktree `model-407` held
`/tmp/modelspec-fullsuite.lock`. Pytest then printed
`1086 passed, 2 skipped in 253.58s (0:04:13)`. The shell recorded
`EXIT:0`.

```text
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_release_blog.py tests/test_release_blog_platforms.py tests/test_release_pipeline.py tests/test_removed_sources.py tests/test_method.py tests/test_landing.py tests/test_leaderboard_refresh.py tests/test_hardware_review.py tests/test_model_192_research.py tests/test_decision_capability.py tests/test_decide_worker.py tests/test_price_reread.py tests/test_hardware_fit.py tests/test_data_trust.py tests/test_release_watch.py tests/test_speed_measurement.py tests/test_decision_snapshot.py tests/test_surface_lint.py tests/test_pipeline.py tests/test_release_signals.py tests/test_comparison_pages.py tests/test_comparison_probability_grammar.py tests/test_model_comparison.py
```

`ruff check` on `decision/excluded.py`, `release_blog/gates.py`, and
`pipeline/surface_lint.py` exited 0. Other edited files already had
lines over 100 columns. Those lines were left as they were. Lines added
in this round are within 100 columns. `ruff format --check` already
fails on pre-existing layout in `release_blog/gates.py` and
`pipeline/surface_lint.py`. `decision/excluded.py` is formatted. This
round did not reformat unrelated lines.

## False positives

The structural walk ran on `pipeline.data_source.DATA_PATHS`, including
gzip decompression. `data_files_scanned=2842`, `gzip_files=2`,
`unreadable=0`, `publisher_hits=0`, `key_only=1372`. The two gzip files
are `measurements/speed/pilot/runs/speed-v1-2026-09-30T00-f30883892dcc.json.gz`
and `measurements/speed/pilot/superseded/speed-v1-2026-09-29T18-8e19404d5a1f.json.gz`.
The key-only files are the legacy source field key with an empty value.
No other string matched, so the rule was left as specified.

The same walk on the built trees, after `pipeline.build --out dist`
(exit 0) and `npm run build` (exit 0):

- `dist`: 8131 files, 29 unreadable binaries, 0 publisher hits, 1372 key-only
- `web/dist`: 13 files, 0 publisher hits

`pipeline.surface_lint --tree dist/modelspec` exited 0:
`dist/modelspec: 0 findings; 5362 files checked`.

## Site and full suite

`(cd web && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci)`
exited 0 (`added 346 packages`). `npm test` (vitest) exited 0:
`Test Files  52 passed | 1 skipped (53)`, `Tests  843 passed (843)`.
`npm run build` exited 0.

Full suite, started `2026-10-18T11:29:22Z`. This worktree took the lock
immediately:

```text
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD MODELSPEC_DIST=$PWD/dist /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Pytest printed `11853 passed, 8 skipped, 11 warnings in 1444.07s (0:24:04)`.
The shell recorded `EXIT:0`. `MODELSPEC_DIST` pointed at the built
`dist`, so the built-tree scan ran inside this suite. The warnings are
the existing unsigned-vocabulary `RuntimeWarning` in
`tests/test_cli_snapshot.py` and `tests/test_cli_keyed_origin.py`.

## Not observed

No Linear edit. No network post. No credential. No browser.
No `wsl`, `ssh`, `scp`, or `curl`. No force-push. No merge of the PR.
No production switch. No legal text, ranking floor, or frozen-data
edit. Model cards were not rewritten. The legacy field key stayed in
place on the cards.
