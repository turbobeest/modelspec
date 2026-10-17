# MODEL-271 round 2 execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-271-about`.
Branch: `model-271-about`.
Base SHA for this round: `b806ec6065bb5d2025f92e0d271e9a4669973cf9`.
Implementation SHA: `510c1fabf9e6cf74abe1a38d1dd8e6cbad0ee5b3`.
This file is a later commit. Resolve the delivered branch SHA with `git rev-parse HEAD`.

## Defect

REV-810, finding 1. `pipeline/pricing.py` put the access claim and all three call lines inside `<h2>What stays free</h2><ul class="free-list">`. That presented the hosted API and the MCP server as free. Only human lookup on the site is free. Machine access is keyed.

## Red, then green

Test: `tests/test_about.py::test_machine_call_lines_require_a_key_and_stay_out_of_free_lists`.

Red, against `b806ec60`, before the registry and pricing change. Log: `/tmp/model-271-r2/red.txt`. Pytest: `1 failed in 0.51s`. Exit code 1.

The failure list started with `registry MACHINE_KEY is None, not 'with a key'`. The API call, the MCP call, and the access claim lacked `with a key`. `/about/` and both pricing renders (`access_enforced` on, and access off) showed those lines without the phrase. Both pricing renders had the lines inside the free list. `/method/` had no machine call line, so it added no failure.

Green, same test, after the change: included in `9 passed in 0.84s` (this test, the rest of `tests/test_about.py`, and `tests/test_entity.py::test_claims_say_only_what_the_service_does_today`). Exit code 0.

Focused green:

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_about.py tests/test_entity.py tests/test_pricing_page.py tests/test_method.py tests/test_surface_lint.py tests/test_agent_copy.py tests/test_structured_data.py tests/test_crawler_access.py --tb=line
```

`206 passed in 33.73s`. Exit code 0. Log: `/tmp/model-271-r2/green-focused.txt`.

## What changed

`pipeline/entity.py` defines `MACHINE_KEY = "with a key"`. The access claim and the API and MCP call lines include that phrase. Pricing renders those registry sentences under "How to call it" (`entity.CALL_HEADING`), in a `call-list`, not in `free-list`.

The free list still contains the three items that were already there: the board for people, the public repository, and the sandbox. REV-810 did not treat those as the defect. The tie wording, the method additions, and the About link are unchanged.

`cli/modelspec/agent-bundle.json` changed only the `source_hashes` of `pipeline/entity.py` and `pipeline/pricing.py`. `python -m pipeline.agent_copy write` also rewrote the other generated artifacts. Their contents matched what was already committed, so they are not in the diff.

## Commands and versions

- Python 3.14.4, pytest 9.1.1, from `/Users/terbeest/dev/modelspec/.venv`.
- Node v22.22.3, npm 10.9.8, Vite 8.0.3, Vitest 5.0.1 (`npm ls vitest vite` in `web/`).
- GitHub CLI 2.102.0.
- `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist`. Exit code 0. Log: `/tmp/model-271-r2/build-python.txt`.
- Built `dist/modelspec/pricing/index.html` has one free list. Its text is the board, the public repository, and the sandbox. The page contains `with a key` three times. `dist/modelspec/about/index.html` has no free list and contains `with a key` three times. `dist/modelspec/method/index.html` has no free list and does not contain `with a key`.
- First `npm ci` in `web/` exited 126. The shell's `npm` is a zsh function, and the log was only `compdef:153: _comps: assignment to invalid subscript range`. Rerun: `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci`. Exit code 0.
- `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm run build` in `web/`. Exit code 0. Vite 8.0.3.
- `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm test` in `web/`. Exit code 0. Vitest: 52 files passed, 1 file skipped, 843 tests passed. The log did not name the skipped file.
- `/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile`. Exit code 0. `11245 passed, 9 skipped, 11 warnings in 1115.35s (0:18:35)`. Log: `/tmp/model-271-r2/pytest-full.txt`. The warnings are the existing unsigned-vocabulary warnings in the CLI snapshot tests. The command did not request `-rs`, so the summary does not name the nine skipped tests. The pass count is one higher than the round-1 full suite (11244), matching the one new test.

Chrome, against `http://127.0.0.1:8766/` serving `dist/modelspec`:

- `/pricing/`: "How to call it" shows the access claim and the three call lines. The API and MCP lines say `with a key`. "What stays free" is the next heading, and its list is the board, the repository, and the sandbox. At a 390px-wide viewport the two cost columns stack, each 350px wide.
- `/about/`: the five claims, the three call lines, the tier prices, and the neutrality link are in the main text. The API and MCP lines say `with a key`.
- `/method/`: the About link points at `/about/`. The tie paragraph still contains `kind: "tied"`, `tie_breakers`, and "does not return the cheapest model as the answer". The page has no "Machines call the hosted API" line.

## What was not observed

- No production deploy. No paid-provider call. Linear was not edited. The pull request was not merged and was left a draft.
- `npm run test:browser` was not run. The `npm test` script does not include it.
- The nine pytest skips were not listed by name. Their count matches the round-1 full suite.
- The flock command's wall clock was longer than pytest's 1115.35s. This file does not record a separate measurement of how long the lock wait was.
