# MODEL-469: old board links assert the redirect at commit and the path and query after load

Branch base: `b374f1ed8be60c8e2d603490a24e882515ca0cd4` (`origin/main`). Round 1 head: `dd76d35be53dce7e0c7cd0590f25b51ccfd03dd0`. Round 2 merged `origin/main` first; that merge was already up to date. This note and the test change are one commit on `model-469`.

Tools: Node `v22.23.2`, npm `10.9.8`, Playwright `1.63.0` (`web/node_modules`), Python `3.12.3` (repo venv), Git `2.43.0`. Web commands ran from `web/` with `PATH` including the repo venv and `PYTHONPATH` set to this worktree, because `vite.config.ts` calls `python -m pipeline.decide_handoff`. Each `npm run build` went through `ops/tools/heavy.sh`. Exit statuses were captured directly, not through a pipe.

## The race

`web/decide.html` replaces the location with `/decide/details/` plus `location.search` and `location.hash` as soon as the old `/decide/` document parses. With both gates off, `gateStatus` starts false (`web/src/decide/App.tsx`), so an undecodable hash takes the opening-board path and `history.replaceState` then writes that board's own `#s=` while keeping the query. That write can finish before the `load` event `page.goto` waits for, or just after it. With either gate on, `gateStatus` stays null until verification, so that rewrite does not run.

Round 1 armed `toHaveURL` in `Promise.all` with `page.goto`. That expectation passes on the redirect's transient URL and says nothing about the URL after load. A details page that strips the query before `load` still passed that form.

## What the test does now

`browser-tests/simple-decide.spec.ts` starts `page.waitForURL(expected, { waitUntil: "commit" })` before `page.goto`. `expected` is still the exact string `origin + /decide/details/ + state` (path, query, and hash). `page.goto` waits for load. After that, every gate build asserts `pathname` is `/decide/details/` and `search` equals the old link's query string.

Both gates off (`VITE_HUMAN_GATE_ENABLED` and `VITE_VISIT_GATE_ENABLED` are not `"true"`): the hash assertion is only that a `#s=` hash is present, together with that same path and query. The board's own `#s=` is legitimate, so the original hash is not required. Either gate on: the redirect's hash is asserted as well, because the rewrite has not run.

No retry wrapper, no timeout change, no skip, and the test is not marked flaky.

## Mutation: the redirect drops the hash

`web/decide.html` was temporarily `location.replace("/decide/details/" + location.search)` (hash omitted). Rebuilt with both gates false through `heavy.sh` (`npm run build`, `VITE_HUMAN_GATE_ENABLED=false`, `VITE_VISIT_GATE_ENABLED=false`, `VITE_TURNSTILE_SITE_KEY=public-browser-test-key`). Then, from `web/`:

```sh
CI=true VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false VITE_TURNSTILE_SITE_KEY=public-browser-test-key \
  ./node_modules/.bin/playwright test --config=playwright.corpus.config.ts \
  browser-tests/simple-decide.spec.ts --grep preserved-state --workers=1
```

Exit 1. 1 failed (30.2s). `page.waitForURL` timed out waiting for `http://127.0.0.1:4173/decide/details/?source=old#s=preserved-state` until `"commit"`. The log showed three navigations: the old `/decide/?source=old#s=preserved-state` URL, then `/decide/details/?source=old` with no hash, then the same path and `?source=old` with the opening board's `#s=` rather than `preserved-state`. The edit was reverted.

## Mutation: the details page strips the query before load

`web/decide-details.html` temporarily ran `history.replaceState(null, "", location.pathname + location.hash)` as the document parsed, so the query was gone before `load` and the redirect's commit URL was unchanged. Same gates-off build command, then:

```sh
CI=true VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false VITE_TURNSTILE_SITE_KEY=public-browser-test-key \
  ./node_modules/.bin/playwright test --config=playwright.corpus.config.ts \
  browser-tests/simple-decide.spec.ts --grep "old board links" --workers=1
```

Exit 1. 2 failed (about 2.4s). Both failed `query after load` in `simple-decide.spec.ts`, after the commit wait had returned. Expected `?template=coding-balanced&source=old`, received `""`. Expected `?source=old`, received `""`. This is the case the commit-only check misses. The edit was reverted. `git diff` for `web/decide.html`, `web/decide-details.html`, and `web/src/decide/App.tsx` was empty afterwards.

## Gates off, 30 times

Clean rebuild, both gates false, same `heavy.sh npm run build` environment. The served `decide.html` again keeps `location.search + location.hash`. Then:

```sh
CI=true VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false VITE_TURNSTILE_SITE_KEY=public-browser-test-key \
  ./node_modules/.bin/playwright test --config=playwright.corpus.config.ts \
  browser-tests/simple-decide.spec.ts --grep "old board links" --repeat-each=30 --workers=1
```

Exit 0. 60 passed (32.0s): 30 for `?template=coding-balanced&source=old` and 30 for `?source=old#s=preserved-state`.

## Full spec, one pass per variant

`browser-tests/simple-decide.spec.ts`, `--workers=4`, after `heavy.sh npm run build` with that cell's `VITE_HUMAN_GATE_ENABLED`, `VITE_VISIT_GATE_ENABLED`, and `VITE_TURNSTILE_SITE_KEY=public-browser-test-key`. The test command is the same `playwright test --config=playwright.corpus.config.ts` line with `CI=true` and those variables. The gates-off pass used the clean build from the 30-run.

| Human gate | Visit gate | Exit | Result |
| --- | --- | --- | --- |
| false | false | 0 | 9 passed, 3 skipped (5.4s) |
| true | false | 0 | 10 passed, 2 skipped (5.4s) |
| false | true | 0 | 11 passed, 1 skipped (6.7s) |
| true | true | 0 | 11 passed, 1 skipped (6.5s) |

Skips are the gate tests that do not apply to that build, plus the opt-in capture test.

## Not observed

The rest of `playwright.corpus.config.ts` (corpus, decide, visit-gate, billing-launch) was not run locally. The Vitest suite was not re-run; this round changes the browser spec only. CI on the draft pull request is the run of those jobs.
