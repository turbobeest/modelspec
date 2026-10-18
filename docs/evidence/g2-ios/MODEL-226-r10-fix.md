# MODEL-226 round 10 executor evidence

Round 10 simplifies the page publisher check in `pipeline/surface_lint.py`.
That check no longer parses YAML, JSON, or JSON-LD, and it no longer
rebuilds mappings from decoded keys. HTML contributes the visible text,
the title, and every attribute value from the raw pairs, each unescaped.
Markdown and every other file contribute the unescaped file text. A
genuine front-matter block is included again as text, never parsed.

The catalogue guard in `tests/test_removed_sources.py` still parses
structured files and still exempts the legacy field key through
`each_string`. It does not decode keys. The three test files that used
to be allowlisted now build probe strings at runtime, and they are no
longer allowlisted. Two sentences in the round-9 evidence file were
rewritten so that file no longer matches the scanner.

Rounds 7 to 9 still hold. A blocked draft name or lab is still replaced
by "the new model" or "the lab". Model cards were not rewritten. The
legacy field key stayed on the cards. `excluded_in` still exempts that
exact key. Only the page check dropped the exemption.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Start of this round: `b0ea9ec9373b37d586f3f9bd24a553dcc47821fd`
- `git merge origin/main` printed `Already up to date.` Exit 0.
  `origin/main` is `6f45c2a7dc9ce2e771bd1ecea926a1a29fe1ad49`.
- Fix: `fd72671721ec2c31236fe699ffd18977b2414976`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.
- Pin generators left the tree unchanged.
  `python -m pipeline.agent_copy write`, `python -m api.worker.openapi`,
  and `python -m qa.contracts` each exited 0. `git status --short`
  afterwards listed only this round's source edits.

## Tools

- Python 3.14.4
- pytest 9.1.1
- pytest-xdist 3.8.0
- ruff 0.16.6
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  npm 10.9.8. The shell function `npm` exits 126. The absolute binary
  was used.
- flock 0.4.0 (`/opt/homebrew/bin/flock`)
- gh 2.102.0
- git 2.50.1
- Unicode 16.0.0

## Red

The three new page tests ran against the unchanged
`pipeline/surface_lint.py`, before the production edit. Log:
`/tmp/model-226-r10/red.txt`.

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_surface_lint.py
```

Pytest exited 1. `3 failed, 11 passed in 0.46s`. The shell recorded
`EXIT:1`.

- `test_markdown_prose_is_flagged_without_parsing_it_as_yaml` found no
  lexicon hit for the key-shaped prose line. The old path treated that
  line as a mapping.
- `test_a_duplicate_attribute_cannot_hide_a_removed_publisher` found no
  lexicon hit when the same attribute was repeated and the first value
  carried a newline character reference. `dict()` had dropped it.
- `test_surface_lint_never_rebuilds_dicts` failed because
  `publisher_subject` was not a list of strings. The old path rebuilt a
  mapping and collapsed two keys that look the same after decoding.

The 11 passes were HTML body and attribute cases the page parser
already decoded.

The tracked-file failure at the reviewed tip is the r9 verdict: the
round-9 evidence file matched the scanner. This session did not re-run
that test red before editing. The green run below includes it.

## Green

The same surface-lint file, after the production edit, is inside this
focused run. Exit 0. `443 passed, 1 skipped in 533.61s (0:08:53)`.

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_surface_lint.py tests/test_removed_sources.py tests/test_release_blog.py tests/test_release_blog_platforms.py tests/test_release_pipeline.py tests/test_landing.py tests/test_method.py tests/test_pipeline.py tests/test_comparison_pages.py
```

The one skip is `test_a_built_dist_carries_no_removed_value`, because
`MODELSPEC_DIST` was unset. With the built tree set, that test alone
printed `1 passed in 17.62s`. The shell recorded `DIST_EXIT:0`.

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD MODELSPEC_DIST=$PWD/dist /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_a_built_dist_carries_no_removed_value
```

`ruff check` on `pipeline/surface_lint.py` is clean. The guard file's
unused module import of `excluded_in` was removed; `ruff check
tests/test_removed_sources.py --select F401,F811,I001` then exited 0.
Pre-existing E501 lines in that file and in `tests/test_surface_lint.py`
were left. `ruff format --check` already fails on pre-existing layout
in `pipeline/surface_lint.py`. This round did not reformat those lines.
New lines stay within 100 columns.

## Site

`python -m pipeline.build --out dist` exited 0. Hardware-source notices
printed; they are not findings.

`python -m pipeline.surface_lint --tree dist/modelspec --report
/tmp/model-226-r10/surface-lint.json` exited 0:
`dist/modelspec: 0 findings; 5362 files checked`.

`(cd web && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci)`
exited 0 (`added 346 packages`). `npm test` (vitest) exited 0:
`Test Files  52 passed | 1 skipped (53)`, `Tests  843 passed (843)`.
`npm run build` exited 0.

## Full suite

Load at the start of the locked run was `5.99 6.77 5.91`. Worktree
`model-258-guides` held `/tmp/modelspec-fullsuite.lock`. This command
waited, then pytest printed `11860 passed, 9 skipped, 11 warnings in
1401.58s (0:23:21)`. The shell recorded `FULL_EXIT:0`.

```text
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

This is the spec command. It does not set `MODELSPEC_DIST`, so the
built-dist test skips. Skip names were not printed (`-rs` was not
used). Round 9's locked run set the variable and recorded 8 skips.
This run recorded 9. The built-dist test was observed separately, above,
and passed. The warnings are the existing unsigned-vocabulary
`RuntimeWarning` in `tests/test_cli_snapshot.py` and
`tests/test_cli_keyed_origin.py`.

## Not observed

No Linear edit. No network post. No credential. No browser.
No `wsl`, `ssh`, `scp`, or `curl`. No force-push. No merge of the PR.
No production switch. No legal text, ranking floor, or frozen-data
edit. Model cards were not rewritten. The tracked-file test was not
re-run red against the pre-fix tree in this session. An independent
reviewer has not re-run this round. CI on the push was not observed.
