# MODEL-469: old board links wait for the redirect URL

Base: `b374f1ed8be60c8e2d603490a24e882515ca0cd4` (`origin/main` at the start of this branch).
Branch: `model-469`. The fix and this note are one commit; the draft PR head is that SHA.

Tools: Node `v22.23.2`, npm `10.9.8`, Playwright `1.63.0` (`web/node_modules`), Vitest `5.0.1`, Python `3.12.3` (repo venv), Git `2.43.0`.
Web commands ran from `web/` with `PATH` including the repo venv, because `vite.config.ts` calls `python -m pipeline.decide_handoff`. Heavy installs and builds used `ops/tools/heavy.sh`. Each command's exit status was captured directly, not through a pipe.

```sh
/home/turbobeest/dev/04-modelspec/modelspec-business/ops/tools/heavy.sh npm ci
/home/turbobeest/dev/04-modelspec/modelspec-business/ops/tools/heavy.sh npx playwright install chromium
```

`npm ci` exit 0 (348 packages). Playwright `1.63.0` installed Chromium `153.0.8010.12` (build v1243). `npm run build` used the same environment as CI's "Test decide page" job: `VITE_HUMAN_GATE_ENABLED`, `VITE_VISIT_GATE_ENABLED`, and `VITE_TURNSTILE_SITE_KEY=public-browser-test-key`. The failing variant is both gates `false`.

## The race

`web/decide.html` lines 7–9 replace the location with `/decide/details/` plus `location.search` and `location.hash` as soon as the old `/decide/` document parses. That navigation still has `?source=old#s=preserved-state`. With both gates off, `gateStatus` starts false (`web/src/decide/App.tsx` line 103), so an undecodable hash takes the opening-board path (lines 683–709) and `history.replaceState` (lines 810–825) then writes that board's own `#s=` while keeping the query. `page.goto` waits for `load`. When the board's `replaceState` finishes first, `toHaveURL` starts after `#s=preserved-state` is already gone and waits out its 5s timeout. With either gate on, `gateStatus` stays null until verification, so that rewrite does not run and the same assertion passes.

The redirect is doing the right thing. The board publishing the state it actually opened is also the right thing. The test was reading the URL after `load`, which is not the URL the redirect produced. `web/src/decide/simple/main.tsx` lines 7–8 repeat the same redirect; on the built page the inline script navigates first and that module line does not run.

## Red, before the test change

Build: both gates false. Command:

```sh
CI=true VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false VITE_TURNSTILE_SITE_KEY=public-browser-test-key \
  ./node_modules/.bin/playwright test --config=playwright.corpus.config.ts \
  browser-tests/simple-decide.spec.ts --grep preserved-state --repeat-each=15 --workers=4
```

Exit 1. 1 failed, 14 passed (7.9s). The failure was `expect(page).toHaveURL(expected)` at `simple-decide.spec.ts:66`. Expected `http://127.0.0.1:4173/decide/details/?source=old#s=preserved-state`. Received the same origin, path, and `?source=old`, with a different `#s=` (the opening board's encoding). All 12 polls in the 5s timeout saw that rewritten URL.

## Fix

`browser-tests/simple-decide.spec.ts` arms `toHaveURL` before `page.goto`, in the same `Promise.all`, for both old-link cases. The expected URL is still `origin + /decide/details/ + state` (path, query, and hash). The example-text assertion is unchanged. No retry wrapper, no timeout change, no skip, and the test is not marked flaky.

## Green

Same failing variant, after the test change, against the unmodified page build:

```sh
CI=true VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false VITE_TURNSTILE_SITE_KEY=public-browser-test-key \
  ./node_modules/.bin/playwright test --config=playwright.corpus.config.ts \
  browser-tests/simple-decide.spec.ts --grep preserved-state --repeat-each=30 --workers=4
```

Exit 0. 30 passed (7.4s). Repeated with eight `python3 -c 'while True: pass'` processes: exit 0, 30 passed (8.1s).

Full `browser-tests/simple-decide.spec.ts`, `--workers=4`, one run per CI matrix cell, each after `npm run build` with that cell's `VITE_*` values:

| Human gate | Visit gate | Exit | Result |
| --- | --- | --- | --- |
| false | false | 0 | 9 passed, 3 skipped |
| true | false | 0 | 10 passed, 2 skipped |
| false | true | 0 | 11 passed, 1 skipped |
| true | true | 0 | 11 passed, 1 skipped |

Skips are the gate tests that do not apply to that build, plus the opt-in capture test.

## Mutation

`web/decide.html` line 8 was temporarily `location.replace("/decide/details/" + location.search)` (hash omitted). Rebuilt with both gates false and ran the preserved-state test once, `--workers=1`. Exit 1. Expected `http://127.0.0.1:4173/decide/details/?source=old#s=preserved-state`. Received `/decide/details/?source=old` with the opening-board `#s=`, not `preserved-state`. The edit was reverted. `git diff` for `web/decide.html` and `web/src/decide/simple/main.tsx` was empty afterwards.

## Unit suite

```sh
/home/turbobeest/dev/04-modelspec/modelspec-business/ops/tools/heavy.sh npm test -- src/decide/__tests__/simple-decide.test.tsx --maxWorkers=1
```

Exit 0. 12 passed.

```sh
/home/turbobeest/dev/04-modelspec/modelspec-business/ops/tools/heavy.sh npm test -- --maxWorkers=1
```

Exit 0. 64 files passed, 1 skipped, 937 tests passed.

## Not observed

The rest of `playwright.corpus.config.ts` (corpus, decide, visit-gate, billing-launch) was not run locally. CI on the draft PR is the run of those jobs. No second copy of the suite was started: `vite preview --strictPort` binds `127.0.0.1:4173`, so two configs cannot share it. The eight busy processes were the contention check instead.
