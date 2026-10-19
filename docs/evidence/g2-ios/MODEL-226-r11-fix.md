# MODEL-226 round 11 executor evidence

Round 11 keeps the round 10 text checks and adds decoded strings.
`decoded_strings` yields every string in a parsed JSON or YAML value,
including dict keys. A key that is not a string is converted with `str`.
The helper does not build a mapping and does not rename keys. Each
yielded string is HTML-unescaped before the publisher predicate.

`publisher_subject` still returns the visible text, the title, every raw
attribute value, and the unescaped file text. For HTML it also returns
each JSON-LD blob and, when that blob parses, the decoded strings.
Owned JSON, YAML, and a genuine leading front-matter block do the same.
A parse error leaves the text checks alone. Markdown prose and the
Markdown body are not parsed. The original blob or file is parsed before
the whole text is unescaped, so a character reference inside a key cannot
collapse two keys into one and drop a value.

The tracked-name guard no longer finds JSON-LD with a regular expression.
It uses `publisher_subject`, which reads `Page.ld`. That parser already
accepts an unquoted type and a type whose plus sign is written as a
character reference. The catalogue walk of cards still exempts the legacy
field key. The page check does not.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-226-platform-drafts`
- Branch: `model-226-platform-drafts`
- Start of this round: `d9ae8ffd0d753c5895c131d1c69bb4ce0fdd3325`
- `git merge origin/main` conflicted in `decision/snapshot.py` on the
  import block. Both sides were kept: the publisher walk imports from
  this branch, and `JSONStreamReader` from `e621e1219aa7702dc1539ef54747f27dbc5f8519`.
  Merge commit: `0f6a3454425487b4bd4d0e423c18c64af18bd68b`.
- Fix: `6fdc85d8f7da6fa5357d98fbe9de91f909f704fc`
- The tip SHA is the commit that adds this file. Resolve it with
  `git rev-parse HEAD`.
- Pin generators left the tree unchanged aside from this round's edits.
  `python -m pipeline.agent_copy write`, `python -m api.worker.openapi`,
  and `python -m qa.contracts` each exited 0. `git status --short`
  afterwards listed only `pipeline/surface_lint.py`,
  `tests/test_removed_sources.py`, and `tests/test_surface_lint.py`.

## Tools

- Python 3.14.4
- pytest 9.1.1
- pytest-xdist 3.8.0
- PyYAML 6.0.3
- ruff 0.16.6
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3.
  npm 10.9.8. The shell function `npm` exits 126. The absolute binary
  was used.
- flock 0.4.0 at `/opt/homebrew/bin/flock`
- gh 2.102.0
- git 2.50.1
- Unicode 16.0.0

## Red

The probe matrix, the decoded-string helper test, and the JSON-LD script
form test ran against the unchanged page check. Log:
`/tmp/model-226-r11/red.txt`.

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=line tests/test_surface_lint.py::test_publisher_probe_matrix tests/test_surface_lint.py::test_decoded_strings_yields_keys_without_a_new_mapping tests/test_removed_sources.py::test_jsonld_script_forms_reach_the_tracked_name_guard
```

Pytest exited 1. `28 failed, 30 passed in 0.49s`. The shell recorded
`EXIT:1`.

The failures were the four collision payloads, Unicode-escaped JSON keys
and values, JSON-LD plain and escaped keys and values, YAML Unicode and
hex keys and values, a front-matter Unicode value, the missing helper,
and the unquoted and character-reference script types. Plain controls,
prose, duplicate attributes, and the quoted script type passed. Paths
outside the owned set stayed unflagged.

## Green

The same command, after the helper landed, printed `58 passed in 0.45s`.
The shell recorded `EXIT:0`. Log: `/tmp/model-226-r11/green-probes.txt`.

Focused suite, exit 0. Log: `/tmp/model-226-r11/focused.txt`.

```text
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -ra -n 4 --dist loadfile -p no:cacheprovider --basetemp /tmp/model-226-r11/focused-temp tests/test_surface_lint.py tests/test_removed_sources.py tests/test_release_blog.py tests/test_release_blog_platforms.py tests/test_release_pipeline.py
```

`383 passed, 1 skipped in 127.58s`. The skip is
`test_a_built_dist_carries_no_removed_value` because `MODELSPEC_DIST`
was unset. The built tree was linted separately.

`ruff check pipeline/surface_lint.py` reported no findings. `ruff check`
on the two test files still reports pre-existing E501 lines. This round
did not reformat those lines. A percent-format finding in the new escape
helper was replaced with a format specifier.

## Site

`python -m pipeline.build --out dist` exited 0. Log:
`/tmp/model-226-r11/build.txt`.

`python -m pipeline.surface_lint --tree dist/modelspec` exited 0:

```text
dist/modelspec: 0 findings; 5362 files checked
```

`(cd web && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci)`
exited 0 and added 346 packages. Log: `/tmp/model-226-r11/npm-ci.txt`.

## Full suite

Started after the fix commit, with the working tree clean. The shell
recorded `FULL:0`.

```text
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Pytest printed `12050 passed, 9 skipped, 11 warnings in 1473.31s`.
The warnings are the existing unsigned-vocabulary `RuntimeWarning` in
`tests/test_cli_snapshot.py` and `tests/test_cli_keyed_origin.py`.
Log: `/tmp/model-226-r11/full.txt`.

The tracked-name guard was re-run after this file was written.
`tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source`
printed `1 passed in 36.59s`. The shell recorded `CENSUS:0`.
Log: `/tmp/model-226-r11/census.txt`. The sentence above was added after
that run. A direct check of this file with the same predicate matched nothing.

## Not observed

No Linear edit. No browser. No `wsl`, `ssh`, `scp`, or `curl`. No
force-push. No merge of the PR. No production switch. No legal text,
ranking floor, or frozen-data edit. Model cards were not rewritten.
The legacy field key stayed on the cards.
