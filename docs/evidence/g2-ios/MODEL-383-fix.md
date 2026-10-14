# MODEL-383 execution evidence

Executed on 2026-10-13 local (2026-10-14 UTC) in
`/Users/terbeest/dev/worktrees/model-383`, on
`sparksandsawdust/model-383-landing-date`.

Base SHA: `a333ce7e798972488eac1ab62021065116681567`.
Implementation SHA: `23e78dfd123b55223b58973b547be69378790a53`.
The delivery commit adds this report only.

Tools: Python 3.14.4, pytest 9.1.1, Node v22.22.3.
Interpreter: `/Users/terbeest/dev/modelspec/.venv/bin/python`.

## Change

`tests/test_landing.py` builds the module fixture with `date.today()`, then
two tests rebuilt a snapshot with a second `date.today()` and compared the
results. Both rebuilds now pass `date.fromisoformat(data.as_of)`.

The new test
`test_the_headline_rebuild_uses_the_fixture_date_past_midnight` reuses that
fixture, replaces `date.today` with the next day, and calls the headline test.

## Audit

Other tests that call `date.today()` or `datetime.now()` do not pair a
fixture date with a later computation whose result moves when the calendar
day changes. No other test file was edited.

`tests/test_entity.py`, `tests/test_method.py`, and `tests/test_coverage.py`
call `date.today()` once inside a fixture. Later tests use that object.
`tests/test_llms_txt.py` calls `date.today()` twice in one function.
`llms_txt` does not put `Build.as_of` into the text the test asserts.
`tests/test_social_cards.py`, `tests/test_holding.py`, `tests/test_legal.py`,
and `tests/test_relations.py` pass one `date.today()` into coverage and do
not compare it with a second engine run.

## Red-first observation

Only the new test existed. Both rebuilds still called `date.today()`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py::test_the_headline_rebuild_uses_the_fixture_date_past_midnight --tb=short
```

Exit code **1**. `1 failed in 176.73s`.

| Defect | Red-first test | Observed red output | Green result |
| --- | --- | --- | --- |
| Headline rebuild uses a second `date.today()` | `test_the_headline_rebuild_uses_the_fixture_date_past_midnight` | `AssertionError: assert 0.3905 == 0.3907` on `cheapest_p`. Fixture `as_of` was `2026-10-13`. The monkeypatched rebuild used `2026-10-14`. | The same test passes. Focused file: `33 passed`. |

## Green verification

Playwright was missing and `CI=true`, so the first focused run reported
`21 passed, 12 errors` (browser checks refused to skip). Then, with Node
v22.22.3:

```sh
cd web && npm ci
./node_modules/.bin/playwright install chromium
PYTHONPATH=/Users/terbeest/dev/worktrees/model-383 npm run build
```

Playwright 1.63.0. `npm run build` exited 0.

Focused command, after that install:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py --tb=line
```

Exit code **0**. `33 passed in 175.69s`.

Full suite, one run, four workers. Load average at start was 12.61.

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit code **1**. `1 failed, 10454 passed, 8 skipped, 11 warnings in 1462.78s`.

The failure is `tests/test_agent_ready.py::test_built_tree_passes_surface_lint`.
Sitemap `<lastmod>` values are `2026-10-13` and the lint expects `2026-10-14`.
`pipeline/build.py` stamps pages with `date.today()` (local).
`pipeline/export.py` stamps `built_at` with `datetime.now(UTC)`.
On this Mac those dates were `2026-10-13` and `2026-10-14`.
The diff does not touch that path.

The same test with `TZ=UTC`, so both clocks share one calendar day:

```sh
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_ready.py::test_built_tree_passes_surface_lint --tb=line
```

Exit code **0**. `1 passed in 274.79s`.

## Not observed

The full suite was not run a second time, and it was not run under `TZ=UTC`.
No threshold or expected landing number was edited. Linear was not edited.
The branch was not merged.
