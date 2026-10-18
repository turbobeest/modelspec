# MODEL-226 round 8 executor evidence

Round 8 makes the shared publisher check one predicate.
`excluded_publisher` casefolds the text, keeps letters and digits, and
matches either removed publisher as a substring of that string. A mixed
separator run matches inside surrounding words. A glued product name
matches. The two removed hosts match, because the collapsed form covers
the host.

`REMOVED_TEXT` keeps the owned benchmark names. Publisher names are no
longer alternatives in that expression. Callers that read a document
pass the text through `without_legacy_source_keys` first. That helper
removes the legacy source field key only in key position, before a
colon. The same spelling as a value still matches. Platform drafts
still replace a blocked name or lab with "the new model" or "the lab".

Round 7 still holds. A draft may contain reviewed literals from
`release_blog/platforms.py`, a display name and a lab name that match
`^[A-Za-z][A-Za-z .'-]{0,60}$` and pass the editorial checks, the exact
`post_url` token, and the two fixed disclosure sentences.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Base after merging `origin/main` `6fdc5baef50a1c198a4a0557dbe2299da5f75090`:
  `a7972209b8ba528c7c26f8e5d9b28af82335cdb3`. The merge was clean.
- Fix: `fb20190237a1dda94a1d18547b8b313848dd9fbf`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.
- No schema, OpenAPI, or pin file changed. `api/worker/openapi.py --check`
  exited 0: `api/worker/openapi.yaml matches the implementation`.
  The pin generators were not run.

## Tools

- Python 3.14.4
- pytest 9.1.1
- pytest-xdist 3.8.0
- ruff 0.16.6
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  npm 10.9.8. The shell function `npm` exited 126. The absolute binary
  was used for `npm ci`, `npm run build`, and `npm test`.
- flock 0.4.0 (`/opt/homebrew/bin/flock`)
- gh 2.102.0
- git 2.50.1
- Unicode 16.0.0

## Red

The new separator, glued-name, key, guard, lexicon, and snapshot tests
ran against the unchanged publisher pattern, before the predicate was
rewritten. Log: `/tmp/model-226-r8-red.txt`.

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=line tests/test_release_blog_platforms.py::test_every_separator_run_rejects_both_publishers tests/test_removed_sources.py::test_a_glued_publisher_name_and_its_domains_are_excluded tests/test_removed_sources.py::test_the_legacy_field_key_is_exempt_and_the_same_spelling_as_a_value_is_not tests/test_removed_sources.py::test_guard_output_and_lexicon_reject_collapsed_publishers tests/test_removed_sources.py::test_a_snapshot_refuses_a_fact_value_that_names_a_publisher
```

Pytest exited 1. `8 failed, 2 passed in 51.20s`. The two passes were
the host strings on the guard and lexicon cases. The exhaustive
separator test recorded predicate misses, including the glued product
name. The glued-name test failed on that name. The key test raised
`ImportError` for `without_legacy_source_keys`. Four guard and lexicon
cases did not raise `BreakdownError`. The snapshot fact values did not
raise `SnapshotBuildError`.

## Green

`tests/test_release_blog_platforms.py::test_every_separator_run_rejects_both_publishers`
passed in 41.23s, exit 0. The run covers 1554 separator strings of
length 1–4 drawn from space, tab, newline, hyphen, underscore, and dot,
for both publishers, bare and inside surrounding words, through
`excluded_publisher` and through `generate_from_breakdown` on the model
name, the alias, and the provider. The glued product name and both
hosts are in that test too.

The smaller publisher tests, including the tracked-file scan, were
`29 passed in 9.69s`, exit 0.

Caller suites, after flock waited on another worktree:

```text
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_release_blog.py tests/test_release_blog_platforms.py tests/test_release_pipeline.py tests/test_removed_sources.py tests/test_method.py tests/test_landing.py tests/test_leaderboard_refresh.py tests/test_hardware_review.py tests/test_model_192_research.py tests/test_decision_capability.py tests/test_decide_worker.py tests/test_price_reread.py tests/test_hardware_fit.py tests/test_data_trust.py tests/test_release_watch.py tests/test_speed_measurement.py tests/test_decision_snapshot.py tests/test_surface_lint.py tests/test_pipeline.py tests/test_release_signals.py tests/test_comparison_pages.py tests/test_comparison_probability_grammar.py tests/test_model_comparison.py
```

`1073 passed, 2 skipped in 324.97s`, exit 0.

`ruff check` on `decision/excluded.py`, `release_blog/gates.py`, and
`pipeline/surface_lint.py` exited 0. Other edited files already had
lines over 100 columns. Those lines were left as they were. Lines added
in this round are within 100 columns.

## False positives

The predicate ran on the public data image (`pipeline.data_source.DATA_PATHS`)
after `without_legacy_source_keys`. `data_files_scanned=2840`,
`publisher_hits=0`, `key_only=1372`. The key-only files are the legacy
source field key. No legitimate string collided, so the rule was left
as specified.

The same scan on the built trees, after `pipeline.build --out dist`
(exit 0) and `npm run build` (exit 0):

- `dist`: 8131 files, 0 publisher hits, 1372 key-only
- `web/dist`: 13 files, 0 publisher hits

`pipeline.surface_lint --tree dist/modelspec` exited 0:
`dist/modelspec: 0 findings; 5362 files checked`.

## Site and full suite

`(cd web && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci)`
exited 0 (`added 346 packages`). `npm test` (vitest) exited 0:
`Test Files  52 passed | 1 skipped (53)`, `Tests  843 passed (843)`.

Full suite, started `2026-10-18T09:12:07Z`. Other worktrees held
`/tmp/modelspec-fullsuite.lock`, so flock waited, then:

```text
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD MODELSPEC_DIST=$PWD/dist /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Pytest printed `11715 passed, 8 skipped, 11 warnings in 1420.19s (0:23:40)`.
The shell recorded `EXIT:0`. `MODELSPEC_DIST` pointed at the built
`dist`, so the built-tree scan ran inside this suite. The warnings are
the existing unsigned-vocabulary `RuntimeWarning` in
`tests/test_cli_snapshot.py` and `tests/test_cli_keyed_origin.py`.

## Not observed

No Linear edit. No network post. No credential. No browser. No
`wsl`, `ssh`, `scp`, or `curl`. No force-push. No merge of the PR.
No production switch. No legal text, ranking floor, or frozen-data
edit. Model cards were not rewritten. The legacy field key stayed in
place on the cards.
