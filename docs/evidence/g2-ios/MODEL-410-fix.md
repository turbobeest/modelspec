# MODEL-410 JSON-LD unescape fix

`publisher_subject` used to parse a JSON-LD blob, and parse `html.unescape(blob)` only when that parse failed. A blob whose Unicode-escape backslashes are written as `&#92;` is already valid JSON. Unescaping the parsed strings then leaves literal `\uXXXX`, so an excluded publisher name in a key or a value was not flagged. The same blob parsed after HTML unescaping contains the name.

The check still appends the raw unescaped blob. It now collects `decoded_strings` from `json.loads(blob)` and from `json.loads(html.unescape(blob))`, each when that parse succeeds. When the two texts are identical, the second parse is skipped because it would add the same strings. The original parse stays first, so a character reference inside a key cannot collapse two keys and drop the earlier value. No mapping is built from decoded keys, and no key exemption was added.

`presence` and `structured_data` still parse the original blob only. They check organization copy and schema.org shape. They do not collect publisher strings. The tracked-name guard does not parse JSON-LD itself. Its HTML path calls `publisher_subject`.

## Revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-410-jsonld`
- Branch: `model-410-jsonld`
- Base: `6a3f00d0ffde1b97245d0c43ef7aa4a33393bf17` (`origin/main` at start)
- Fix: `5579547347fe8ab12b05be645992cebe7b6c326a`
- The tip SHA is the commit that adds this file. Resolve it with `git rev-parse HEAD`.

## Tools

- Python 3.14.4
- Unicode 16.0.0
- pytest 9.1.1
- pytest-xdist 3.8.0
- PyYAML 6.0.3
- markdown-it-py 4.2.0
- pydantic 2.13.5
- ruff 0.16.6
- Node `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node` is v22.22.3
- flock 0.4.0 at `/opt/homebrew/bin/flock`
- gh 2.102.0
- git 2.50.1

## Red

The four cases are both excluded publisher names, each as a JSON-LD value and as a JSON-LD key. The names are built at runtime. The backslash of each `\uXXXX` escape is the character reference `&#92;`.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_surface_lint.py::test_jsonld_entity_encoded_unicode_escapes_are_flagged tests/test_removed_sources.py::test_jsonld_entity_encoded_unicode_escapes_reach_the_tracked_name_guard
```

Pytest exited 1. `8 failed in 0.51s`. The shell recorded `EXIT:1`. Log: `/tmp/model-410/red.txt`.

`Page.ld` still equalled the original blob, so the HTML parser had not decoded `&#92;` first. `lexicon` returned no `lexicon.removed-source` finding for any of the four pages. `_publisher_hit` returned false for the same four pages.

## Green

Same two tests, plus the publisher probe matrix, the decoded-string helper test, and the JSON-LD script-form guard, after the parse change and a format-only edit in the guard test:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=line tests/test_surface_lint.py::test_jsonld_entity_encoded_unicode_escapes_are_flagged tests/test_removed_sources.py::test_jsonld_entity_encoded_unicode_escapes_reach_the_tracked_name_guard tests/test_surface_lint.py::test_publisher_probe_matrix tests/test_surface_lint.py::test_decoded_strings_yields_keys_without_a_new_mapping tests/test_removed_sources.py::test_jsonld_script_forms_reach_the_tracked_name_guard
```

Pytest exited 0. `66 passed in 0.47s`. The shell recorded `EXIT:0`.

The two files together, before that format-only edit:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --tb=line tests/test_surface_lint.py tests/test_removed_sources.py
```

Pytest exited 0. `220 passed, 1 skipped in 114.70s`. The shell recorded `EXIT:0`. Log: `/tmp/model-410/focused.txt`. The command did not use `-ra`, so the skip was not named. The only `skipif` in those files is `MODELSPEC_DIST`.

## Site build and surface lint

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
```

Exit 0. Log: `/tmp/model-410/build.txt`. An earlier invocation wrote the same shape of log, then the shell aborted on zsh's read-only `status` variable before it could record the code. The exit 0 above is from the rerun.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec
```

Exit 0. `dist/modelspec: 0 findings; 5362 files checked`.

## Full suite

This shell has `CI=true`. The worktree had no `web/node_modules` and no `web/dist`.

First run, before that install:

```sh
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit 1. `5 failed, 12041 passed, 9 skipped, 11 warnings, 12 errors in 1472.50s`. The failures and errors were `tests/test_social_cards.py` and `tests/test_landing.py` asking for `npm ci` and Playwright. Log: `/tmp/model-410/full.txt`.

```sh
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci --prefix web
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm run build --prefix web
```

`npm ci` exited 0 and added 346 packages. `npm run build` exited 0 and wrote `web/dist/decide.html`. Landing browser cases then passed: `12 passed in 8.11s`, exit 0.

Second full run, same flock command, with that Node directory on `PATH`:

Exit 0. `12058 passed, 9 skipped, 11 warnings in 1400.11s (0:23:20)`. Log: `/tmp/model-410/full2.txt`. The shell recorded `EXIT:0`. The unsigned-vocabulary warnings are the same eleven warnings as the first run. The `-q` command did not name the 9 skips.

`git status --short` after the web install and build was empty aside from this evidence file.

## Not observed

No GitHub Actions result for this branch. No live deployment, private-data build, paid-provider call, or browser pass against modelspec.dev. The 9 skipped full-suite cases were not named. `MODELSPEC_DIST` was not set, so `test_a_built_dist_carries_no_removed_value` was not run. The built tree was checked with `pipeline.surface_lint` instead. No ranking floor, legal text, production switch, or frozen catalogue file was changed. No Linear write, merge, force-push, ssh, or scp.
