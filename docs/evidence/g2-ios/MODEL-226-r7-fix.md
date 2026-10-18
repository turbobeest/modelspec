# MODEL-226 round 7 executor evidence

Round 7 stops copying free text from a release breakdown into platform
drafts. Each draft is still one string. `render_drafts` and
`generate_from_breakdown` return those strings. Nothing is posted.

A draft may contain only reviewed literals from `release_blog/platforms.py`,
a display name and a lab name that match `^[A-Za-z][A-Za-z .'-]{0,60}$`
and pass the editorial checks, the exact `post_url` token, and two
fixed sentences chosen by whether `disclosures.supplier` and
`disclosures.early_access` are present. The headline is not read.
The class, the benchmark rows, and the neutrality field are not read.
The neutrality sentence in the draft is the reviewed literal, which
matches the signed fixture's pledge. A name or lab that fails the
charset, a percent word, a superlative, a bracket, or the publisher
check is replaced by "the new model" or "the lab". The bad value is
not copied.

The shared publisher pattern matches either publisher across a run of
spaces, hyphens, underscores, or dots, as a whole token. A second
pass drops those separators and checks again, so a mixed run such as
space-hyphen-dot still matches. The match does not swallow the empty
legacy source field key on a card. That
key is still rejected as a benchmark id by `REMOVED_ID`. The second
alternative of the pattern stays the bare second publisher name so
the surface-lint witness, `pattern.split("|")[1]`, is unchanged.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Base: `dd9f3da4c7fdde71f1324878b4ac9598c71ee5a0`
- Merge of `origin/main`: `245ea965de900d71bf5d238f5b206e6503ad4fc0`
  (brings `b4a7074f`, MODEL-402). No schema, OpenAPI, or pin file
  changed in this round, so the pin generators were not run.
- Fix: `ed47a53765a6d1288f5b51897d74ad5f4977266c`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.

## Tools

- Python 3.14.4
- pytest 9.1.1
- pytest-xdist (the suites used `-n 4 --dist loadfile`)
- ruff 0.16.6
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  npm 10.9.8. In the suite shell, `node --version` was swallowed by a
  zsh `compdef` warning. The absolute binary printed `v22.22.3`.
- flock 0.4.0 (`/opt/homebrew/bin/flock`)
- gh 2.102.0
- git 2.50.1

## Red

The new allowlist tests and the separator tests were run against the
round-6 renderer and the old publisher pattern, before either file
was rewritten.

```text
/Users/terbeest/dev/modelspec/.venv/bin/ruff check release_blog/platforms.py tests/test_release_blog_platforms.py decision/excluded.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_blog_platforms.py tests/test_removed_sources.py::test_excluded_publishers_match_across_separators tests/test_removed_sources.py::test_a_sentence_about_lighting_is_not_an_excluded_publisher tests/test_removed_sources.py::test_mixed_separators_collapse_before_the_publisher_check --tb=line
```

`ruff check` exited 0. Pytest exited 1. `76 failed, 39 passed in 1.67s`.

The signed-fixture oracle failed because the draft still opened on
the breakdown headline (`On swe_bench_pro...`) and still contained
`text generator`. The hook, `from lab`, and the fixed disclosure
sentences were absent. Digit, percent, and superlative inputs raised
`ValueError` from the old input rejector (`contains a digit`,
`contains a percent`, `contains a superlative`) instead of being
omitted. The round-6 scheme-relative supplier text
`See [source](//example.org/).` was present in `x.txt`. The
double-space publisher headline and `The number-one coding model.`
were present. Unsafe names and labs were copied into
`The breakdown covers ...`. `Special Class` and a replacement
neutrality sentence were copied. `excluded_publisher` raised
`ImportError`. Separator forms with a double space, `--`, `_`, `.`,
a spaced hyphen, `...`, and the split second publisher name did not
match the old pattern, which allowed only one space or hyphen between the two words.

## Green

After the allowlist rewrite, `tests/test_release_blog_platforms.py`
was `115 passed` once digit marks were checked before the glued
percent word. The order is superlative, then a number mark, then
the percent word, so a digit still reports `digit`.

`tests/test_removed_sources.py`, `tests/test_release_blog_platforms.py`,
and `tests/test_surface_lint.py::test_removed_sources_reuse_the_catalogue_rule`:
`122 passed, 1 skipped in 109.06s`, exit 0.

Release-blog tests plus the modules that import `decision.excluded`:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_release_blog.py tests/test_release_blog_platforms.py tests/test_release_pipeline.py tests/test_removed_sources.py tests/test_method.py tests/test_landing.py tests/test_leaderboard_refresh.py tests/test_hardware_review.py tests/test_model_192_research.py tests/test_decision_capability.py tests/test_decide_worker.py tests/test_price_reread.py tests/test_hardware_fit.py tests/test_data_trust.py tests/test_release_watch.py tests/test_speed_measurement.py tests/test_decision_snapshot.py tests/test_surface_lint.py tests/test_pipeline.py tests/test_release_signals.py
```

`1038 passed, 2 skipped in 389.72s`, exit 0. An earlier run of this
command, before the token boundary, exited 1: `2 failed, 1035 passed,
2 skipped in 335.82s`. Both failures were `REMOVED_TEXT` matching
inside the legacy source field key (`test_no_tracked_file_names_a_removed_source`
and `test_the_export_carries_no_removed_value`). The pattern now
requires the publisher name to be a whole token. One sentence in
`docs/evidence/g2-ios/MODEL-226-r6-fix.md` also named both publishers
in prose. The old pattern already matched that sentence. The sentence
now says "the two removed publisher names".

`(cd web && npm ci)` with Node v22.22.3 on `PATH` exited 0
(`NPM_CI_EXIT:0`, 346 packages). npm 10.9.8.

Full suite, started `2026-10-18T06:53:55Z`. Another worktree held
`/tmp/modelspec-fullsuite.lock`, so flock waited, then:

```text
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Pytest printed `11686 passed, 9 skipped, 11 warnings in 1367.17s (0:22:47)`.
The wrapper's next line was `status=$?`. In this zsh, `status` is
read-only, so the shell printed `(eval):5: read-only variable: status`
and exited 1 after pytest had already printed the pass line. The
warnings are the existing unsigned-vocabulary `RuntimeWarning` in
`tests/test_cli_snapshot.py` and `tests/test_cli_keyed_origin.py`.

`ruff check` on `decision/excluded.py`, `release_blog/platforms.py`,
and `tests/test_release_blog_platforms.py` exited 0. `ruff format`
was applied to `release_blog/platforms.py` only. `tests/test_removed_sources.py`
already had lines over 100 columns. Those lines were not reformatted.

## Not observed

No Linear edit. No network post. No credential. No browser. No
`wsl`, `ssh`, `scp`, or `curl`. No force-push. No merge of the PR.
No production switch. No legal text, ranking floor, or frozen-data
edit. Model cards were not rewritten. Pin generators were not run.
