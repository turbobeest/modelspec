# MODEL-405 validation

Executed on 2026-10-19 in `/Users/terbeest/dev/worktrees/model-405-details`, branch `model-405-details`.

- Base SHA: `bbfa93be5eed392878a2af0d709ca6e774302c5c`.
- Red-test commit: `b343c396`.
- Final implementation SHA: `7891b1f6b7e8e45c99648738dfdc0ab703e51f61`.
- This report follows the tested implementation as an evidence-only commit. The PR body and executor completion line record that final commit's SHA.

The detailed board now renders tied models without a winner headline, star, row numbers, automatic chart ring or automatic table highlight. The tie-order sentence sits directly beneath the heading. A selected model's detail retains its labelled chance of being best. Explicit selections still highlight the corresponding model.

The single agent block follows the human answer and is titled "Ask this from your agent". Its price and credit count come from the existing generated handoff data, with text explaining that the price buys a ModelSpec answer. The header displays the matching snapshot metadata's date, or explicitly reports an unavailable date. Hover and keyboard focus expose the hash; Share retains its raw hash. On mobile, Feedback is in the header flow. The answer includes the existing neutrality sentence and a dated link from the response's evidence.

The simple `/decide/` page's components, source-selection helper and generated pricing data were not changed. Its existing unit and browser tests pass. No decision contract, engine, ranking floor, legal text, frozen data or production switch changed.

## Red before implementation

The five required browser regressions were added to [decide.spec.ts](../../../web/browser-tests/decide.spec.ts) and run against the unchanged implementation. Exit status was **1**, with **5 failed**. The test-only commit preserves that reproducible state.

| Defect and browser test | Red output | Green output |
| --- | --- | --- |
| `MODEL-405: a tied answer has no winner styling and keeps probabilities in detail` | Expected `Order within the tied group is not evidence that one is better.`; received `Ordered by chance of being best.` | Passed. Also checks the full member count, absent star/headline/rank column/automatic highlights, labelled probability in detail and explicit chart selection. |
| `MODEL-405: agent copy and sourced pricing follow the human answer` | Region `Ask this from your agent` was not found. | Passed. One copy button, generated price/credits, clarification text and measured placement below the answer. |
| `MODEL-405: the header labels the snapshot date and keeps its hash on focus` | Expected `Data as of 2026-10-16`; received `snap_483dd2fb6c5915b5`. | Passed. Checks the fixture metadata date, focus tooltip hash and date visibility at 390 px. |
| `MODEL-405: Feedback never covers the private assistant card at 390px` | Expected rectangle intersection `false`; received `true`. | Passed. No intersection before or after scrolling; Feedback opens its dialog. |
| `MODEL-405: the answer pairs neutrality with a dated engine source` | The neutrality link was not found beside the answer. | Passed. The citation URL and date match response evidence. |

Additional red/green checks found during verification:

- The new answer citation initially used default link blue. `answer evidence source links meet AA in both themes` failed at **1.791437530728425**, below **4.5**. Applying the existing theme link color made both theme checks pass.
- The table initially retained an automatic first-row highlight. The tie browser test failed with `.decision-table tr.selected`, expected **0**, received **1**. Passing only an explicit selection for tied answers made it pass.
- Missing and mismatched date metadata both render `Data date unavailable`. A changed response URL/date changes the citation. Removing all evidence from an estimated answer produces the existing explicit invalid-answer state and no invented citation.
- The broad unit run exposed the Share component's use of `SnapshotId` and an old test that required numbered tied rows. Share's existing hash behavior was restored. The table test now exercises both cases, retaining consecutive engine ranks for a separated answer and requiring no rank column for a tie.
- The first full Python run exited 1 with **12,090 passed, 9 skipped, 12 errors** in **1,786.30 seconds**. All 12 errors came from the shared landing-browser setup: `locator.waitFor: Timeout 30000ms exceeded`, waiting for `getByRole('region', { name: 'Give this to my agent' })`. The harness still expected the previous agent title and neutrality wording. Those locators, and the equivalent visit-gate locators, now match the requested copy. The 12 landing checks and the gate-enabled browser suite pass.

## Commands and results

Commands ran from the worktree root unless marked `web/`. Each command's exit status was captured directly before printing its log, without a pipeline. Logs remain in `output/playwright/model-405-executor/`; CTA worker logs are in the separate `output/playwright/model-405-cta/` directory. Playwright Chromium was already installed in the local browser cache; `npm ci` does not install that browser binary, and no browser-install command was run for this ticket.

Node commands used the following environment. The first full Python run accidentally inherited Node 22.23.1; the focused landing rerun and final locked suite explicitly use the required Node 22.22.3 path.

```sh
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH
export MODELSPEC_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python
```

| Command | Result |
| --- | --- |
| `cd web && npm ci` | Exit 0. |
| `cd web && npx playwright test browser-tests/decide.spec.ts --grep MODEL-405 --workers=1` | Original implementation: exit 1, 5 failed. Initial fixes, rerun with `--workers=2`: exit 0, 7 passed. All later MODEL-405 cases also pass in the final full browser run. |
| `cd web && npx playwright test browser-tests/decide.spec.ts --grep 'answer evidence source links'` | Exit 1 before the color fix; passes in the final browser run. |
| `cd web && npx playwright test browser-tests/decide.spec.ts --grep 'MODEL-405: a tied answer'` | Exit 1 before removing the table highlight; passes in the final browser run. |
| `cd web && npm test -- src/decide/__tests__/best-now.test.tsx src/decide/__tests__/tie-aware-answer.test.tsx src/decide/__tests__/decision-table.test.tsx src/decide/__tests__/canvas-axes.test.tsx src/decide/__tests__/field.test.tsx src/decide/__tests__/ranked-answer.test.tsx` | Exit 0, 41 tests in 6 files. |
| `cd web && npm test -- src/decide/__tests__/agent-handoff.test.tsx` | Exit 0, 10 tests. |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out web/src/decide/__corpus__` | Exit 0, generated 319 decisions and 5 vocabularies. |
| `cd web && npm run build` | Exit 0, TypeScript and Vite production build passed. |
| `cd web && MODELSPEC_CORPUS_REQUIRED=1 npm test` | Exit 0, **1,299 passed in 57 files**. |
| `cd web && CI=true npx playwright test --config=playwright.corpus.config.ts` | Exit 0, **122 passed, 10 skipped**. Includes the built detailed page, simple page and generated corpus. |
| `cd web && VITE_HUMAN_GATE_ENABLED=true VITE_VISIT_GATE_ENABLED=true VITE_TURNSTILE_SITE_KEY=public-browser-test-key npm run build` followed by `CI=true VITE_HUMAN_GATE_ENABLED=true VITE_VISIT_GATE_ENABLED=true VITE_TURNSTILE_SITE_KEY=public-browser-test-key npx playwright test --config=playwright.corpus.config.ts` | Both exit 0, **131 passed, 1 skipped**. Exercises manual verification and managed visit-token flows. |
| `cd web && npm run build` after the gate-enabled run | Exit 0; default build restored before the landing and full Python checks. |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py -k behaviour_in_browser` | Exit 0, **12 passed, 21 deselected**. |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist` | Exit 0. |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec` | Exit 0, **0 findings; 5,366 files checked**. |
| `/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile` | Pending completion. |
| `git diff --check` | Exit 0. |

Versions observed: Node **22.22.3**, npm **10.9.8**, Python **3.14.4**, pytest **9.1.1**, Vitest **5.0.1**, Vite **8.0.3**, Playwright **1.63.0**, TypeScript **5.9.3**, Git **2.50.1**, GitHub CLI **2.102.0**.

The full browser command above runs `the board and its explanation fit a 320px viewport in light and dark mode`, `the board fits a 390px viewport in light and dark mode`, and the layout cases at 1000–1440 px. The MODEL-405 checks measure the mobile Feedback/card rectangles and the agent block's position below the answer. Both answer and detail source-link contrast checks pass in both themes.

## Limits of observation

Browser requests used recorded fixtures or the locally generated engine corpus. No deployed-site behavior, live Worker response, vendor API, paid-provider run, production switch, external gate, or CI outcome is claimed. Nine flag-dependent browser scenarios were skipped in the default build and passed in the gate-enabled build. One screenshot-capture scenario was opt-in and skipped in both. Other browser behavior, including the simple page's approved flow, was exercised by the enabled suites.

The site and corpus generators reported existing unregistered hardware-source warnings. Those frozen records were left unchanged. Snapshot dates are not inferred from those warnings, source publication dates, a hash or the current time.

No Linear write, merge, force-push, SSH, SCP, curl, device call or real tmux session was used. The PR remains a draft for the independent review.
