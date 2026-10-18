# Browser and gate evidence

These tests run offline. Browser requests for vocabulary, decisions and Turnstile use fixtures. The billing admission cases run the real local Python Worker service and SQLite admission through `tests/replay_billing_launch.py`; they do not call Cloudflare or a provider.

The latest verification used the resolved merge working tree, committed as `e0053beaa0515892667dfcbb3225422560ea43d5`. The recorded HEAD when installation began was `ea1643cc935a78cedd9f242d5eed6a181961618b`; main’s changes were already present in the working tree. Fresh sequential `npm ci`, `npm run build`, `npm test` and `npm run test:browser -- --workers=2 --reporter=line` commands each returned exit 0. The unit run passed 872 tests in 55 files, with one opt-in corpus file skipped. The four gate combinations and screenshot capture were then rerun. [results.txt](results.txt) records the commands and direct exit codes. Playwright artifacts use separate paths under `.generated/` so they cannot delete the main executor's corpus artifacts.

The browser tests first failed before the simple page implementation existed. The tracked [results.txt](results.txt) contains the missing labelled example assertion, all six initial behavior failures, the normalization regression, and final green output summaries. Routing had already changed when the initial run began. Full `.log` files are local artifacts ignored by Git; the PR evidence does not depend on them.

[matrix-results.json](matrix-results.json) records the exit status for all four human-gate and visit-gate combinations. [results.txt](results.txt) preserves their output summaries; the JSON's log filenames identify only the local source artifacts. Each run uses Node v22.22.3, npm 10.9.8, Playwright 1.63.0 and Python 3.14.4. From the repository root, use this command for each `false`/`true` value of the two gate variables:

| Human gate | Visit gate | Passed | Skipped | Exit |
| --- | --- | ---: | ---: | ---: |
| false | false | 35 | 10 | 0 |
| true | false | 37 | 8 | 0 |
| false | true | 44 | 1 | 0 |
| true | true | 44 | 1 | 0 |

These are the fresh reruns after main integration, retaining the 44-pixel home-link target fix and route recovery changes. The previous matrices had the same counts. All four commands exited 0 directly, as did the preceding broad browser run and subsequent screenshot capture. The browser runs were sequential.

```bash
cd web
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false \
VITE_TURNSTILE_SITE_KEY=public-browser-test-key \
MODELSPEC_TEST_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python \
MODELSPEC_BROWSER_OUTPUT=/Users/terbeest/dev/worktrees/model-404/docs/evidence/g2-ios/MODEL-404/gates/.generated/fresh-matrix-false-false \
npm exec playwright -- test browser-tests/simple-decide.spec.ts \
  browser-tests/decide.spec.ts browser-tests/visit-gate.spec.ts \
  browser-tests/billing-launch.spec.ts --workers=2 --reporter=line
```

The broader `npm run test:browser -- --workers=2 --reporter=line` run also exited 0 with 37 passed and 16 skipped. Its environment used both gate flags set to false and the same Node/Python paths. Skips were gate-specific cases, the opt-in capture, absent generated corpus, and deployed-site/pricing checks without explicit URLs. Its command, output summary and exit status are in [results.txt](results.txt). The separate built-corpus run belongs to the main executor's evidence.

The suite verifies the labelled example, alphabetical equal-emphasis ties, keyboard choice and verdict focus, exact detailed-page question transfer, legacy redirects, separate EU and training limits, route selection, response mutations, no-fit and undetermined answers, and the 390 by 844 viewport in both themes. The mobile check measures every job and priority button, the home link, theme button, Change button and primary evidence link at least 44 pixels in both width and height. It also checks all six tied rows and the evidence action inside the viewport, no horizontal overflow, and visible main-content text contrast of at least 4.5:1 in the initial example. The final target check first failed on the 28-pixel home link; adding a 44-pixel minimum height made it pass without losing the mobile fit. The red and green output is recorded in [results.txt](results.txt).

The managed gate test observes zero vocabulary and decision requests before verification. It checks token reuse, one intent per choice and one renewal after an expired-token refusal. The manual gate test observes zero decision requests before a verified lookup. The real Worker case confirms direct machine requests without a key still receive HTTP 401.

After the replay helper's module-cleanup fix, `billing-launch.spec.ts` was rerun under all four flag combinations. Human off/visit off and human on/visit off each passed two tests and skipped the two visit-specific cases; both visit-enabled combinations passed all four tests. Every command exited 0. This follow-up used separate artifact directories and changed no browser source. Its exact command, environment and output summaries are in the distinct billing-cleanup section of [results.txt](results.txt), with machine-readable exits in [billing-cleanup-results.json](billing-cleanup-results.json).

An initial browser run exposed a real request normalization mismatch: the controls loaded while the answer stayed at "Checking the evidence…". The implementation now compares normalized question state. Other interrupted runs saw React hot-reload errors while source files were being edited. Final matrix runs use stable source. A pre-existing detailed-page scroll test also intercepted its initial request too early; it now waits for the first answer before holding the request caused by the tested facet click. Its original scroll-position assertion remains.

The recorded assistant example and six-way tie use `live-assistant-balanced-full.json`, snapshot `snap_483dd2fb6c5915b5`. Coding and no-fit screenshots use exact questions calculated by the offline engine against frozen repository data at `snap_e9c30eaacfa8f2f2`, with the same incomplete-catalogue gate setting used by the existing corpus and prototype. `screenshot-decisions.json` records those questions, response IDs and conclusions. The capture test compares the actual request with the saved question before serving either response.

Screenshot vocabulary remains the unmodified captured live vocabulary. That fixture has no `coverage.as_of`, so its header honestly says "Data date unavailable". Ordinary browser tests separately add coverage from another fixture to verify date rendering. That merged test metadata is never used in screenshots. These captures demonstrate layout and interactions; they do not establish a current model recommendation or evidence freshness.

The fresh capture test passed and regenerated eleven images after main integration; [results.txt](results.txt) includes the generation and capture output. The local engine regenerated the coding and no-fit responses with unchanged snapshot and decision IDs. Desktop simple pages include their full height; mobile examples, coding, tie and no-fit pages include the 390 by 844 viewport. `simple-mobile-example-full.png` also shows the source, cost basis and agent copy below that viewport. Both detailed-page screenshots preserve its existing first screen. All eleven regenerated images were opened and inspected. They are byte-identical to the earlier captures.

| Capture | Desktop | Mobile |
| --- | --- | --- |
| Labelled example | [Image](simple-desktop-example.png) | [Viewport](simple-mobile-example.png), [full page](simple-mobile-example-full.png) |
| Coding | [Image](simple-desktop-coding.png) | [Image](simple-mobile-coding.png) |
| Six-way tie | [Image](simple-desktop-tie.png) | [Image](simple-mobile-tie.png) |
| No fit | [Image](simple-desktop-no-fit.png) | [Image](simple-mobile-no-fit.png) |
| Detailed board | [Image](details-desktop.png) | [Image](details-mobile.png) |

Regenerate the ignored decision files and screenshots from the repository root:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python \
  docs/evidence/g2-ios/MODEL-404/gates/generate-screenshot-decisions.py
cd web
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false \
MODELSPEC_CAPTURE_SIMPLE=1 \
MODELSPEC_BROWSER_OUTPUT=/Users/terbeest/dev/worktrees/model-404/docs/evidence/g2-ios/MODEL-404/gates/.generated/fresh-capture-playwright \
npm exec playwright -- test browser-tests/simple-decide.spec.ts \
  --grep 'capture simple' --workers=1 --reporter=line
```

No live production decision, paid-provider call, recruited usability session, assistive-technology session, Firefox or Safari run was observed. The live smoke test was adapted to check both URLs but was not run against a deployed site. All browser servers started by these runs are stopped by Playwright when each command exits.
