# Browser and gate evidence

These tests run offline. Browser requests for vocabulary, decisions and Turnstile use fixtures. The billing admission cases run the real local Python Worker service and SQLite admission through `tests/replay_billing_launch.py`; they do not call Cloudflare or a provider.

The latest verification covers the REV-814 fixes at `2488fbc3c92a271d002dc1179b0c6b87345d1c96`. The browser suite serves the genuine generated display vocabulary directly, with no borrowed coverage fields. It asserts the snapshot date and verifies that reordering the same answer's results, evidence and contributions does not change its objective source. [round3/results.txt](round3/results.txt) records exact commands, direct exits, red and green observations, and screenshot provenance.

Both browser regressions failed against the preserved pre-review built JavaScript: the header showed “Data date unavailable” despite the real trim's date, and moving Gemini 3.8 Flash to the front changed the source to “Arena Elo — Coding, 2026-09-13.” The fixed browser passed both checks and the existing response-mutation check. The vocabulary producer's own missing-date red and green are recorded in [the routing evidence](../routing/round3/trim-red.txt).

Fresh sequential `npm ci` and `npm run build` exited 0. The first unit run exposed five historical-fixture provenance assertions that assumed the captured answers shared the regenerated vocabulary's snapshot. The fixture owner corrected those assertions while preserving the original responses. Final `npm test` passed **898 tests**, with one opt-in corpus rendering file skipped. `npm run test:browser -- --workers=2 --reporter=line` passed **38 tests**, with 16 expected skips. The skips cover gate-specific cases, opt-in capture, absent generated corpus and deployed-site/pricing checks without explicit URLs.

All four full gate combinations passed. [round3/matrix.json](round3/matrix.json) records direct exits; [round3/results.txt](round3/results.txt) preserves their summaries. The new source-order test adds one pass to each previous matrix count.

| Human gate | Visit gate | Passed | Skipped | Exit |
| --- | --- | ---: | ---: | ---: |
| false | false | 36 | 10 | 0 |
| true | false | 38 | 8 | 0 |
| false | true | 45 | 1 | 0 |
| true | true | 45 | 1 | 0 |

From the repository root, repeat the following with each combination of flags:

```bash
cd web
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false \
VITE_TURNSTILE_SITE_KEY=public-browser-test-key \
MODELSPEC_TEST_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python \
MODELSPEC_BROWSER_OUTPUT=/Users/terbeest/dev/worktrees/model-404/docs/evidence/g2-ios/MODEL-404/gates/round3/.generated/matrix-false-false \
npm exec playwright -- test browser-tests/simple-decide.spec.ts \
  browser-tests/decide.spec.ts browser-tests/visit-gate.spec.ts \
  browser-tests/billing-launch.spec.ts --workers=2 --reporter=line
```

The suite verifies the labelled example, alphabetical equal-emphasis ties, keyboard choice and verdict focus, exact detailed-page question transfer, legacy redirects, separate EU and training limits, route selection, response mutations, no-fit and undetermined answers, and the 390 by 844 viewport in both themes. The mobile check measures every job and priority button, the home link, theme button, Change button and primary evidence link at least 44 pixels in both dimensions. It checks all six tied rows and the evidence action inside the viewport, no horizontal overflow, and visible main-content text contrast of at least 4.5:1 in the initial example.

The managed gate test observes zero vocabulary and decision requests before verification. It checks token reuse, one intent per choice and one renewal after an expired-token refusal. The manual gate test observes zero decision requests before a verified lookup. The real Worker case confirms direct machine requests without a key still receive HTTP 401.

The vocabulary fixture now comes from the real full-vocabulary producer followed by `display_vocabulary.trim()`, using the frozen public repository at snapshot `snap_e9c30eaacfa8f2f2`, dated `2026-10-04`. It retains `as_of` and omits catalogue coverage counts. Its [generator](../routing/round3/generate-display-vocabulary.py) and [provenance](../routing/round3/display-vocabulary-provenance.json) record the recipe, source hashes and output hash. It contains 40 templates, of which 28 are available. Older captured answers remain historical regression fixtures; they are not used for the refreshed screenshots.

Every screenshot answer now comes from that same frozen snapshot. The local generator produces the exact example, coding, no-fit and detailed plot questions, derives the date from the vocabulary, and rejects a snapshot mismatch. The capture test checks every request before returning its generated answer; it supplies the full answer to both display phases and normalizes only `explain` for this comparison. [screenshot-decisions.json](screenshot-decisions.json) records the questions, dates and decision IDs. No historical answer fallback remains in the capture path.

All eleven images were regenerated and opened individually. The simple headers show “Data as of 2026-10-04.” The example still has six tied models and fits the complete evidence action within 390 by 844. Coding has two tied models and shows “Source: CursorBench 4.0, 2026-09-28.” The example and tie show “Source: Arena WebDev (Code Arena), 2026-09-23.” The no-fit answer shows the exact fallback “Sources and dates: see the full evidence.” Ten PNGs changed from the review base; the detailed mobile first screen remains byte-identical. [round3/screenshots.json](round3/screenshots.json) records hashes. These are frozen-data demonstrations, not a current recommendation or a claim of production freshness.

| Capture | Desktop | Mobile |
| --- | --- | --- |
| Labelled example | [Image](simple-desktop-example.png) | [Viewport](simple-mobile-example.png), [full page](simple-mobile-example-full.png) |
| Coding | [Image](simple-desktop-coding.png) | [Image](simple-mobile-coding.png) |
| Six-way tie | [Image](simple-desktop-tie.png) | [Image](simple-mobile-tie.png) |
| No fit | [Image](simple-desktop-no-fit.png) | [Image](simple-mobile-no-fit.png) |
| Detailed board | [Image](details-desktop.png) | [Image](details-mobile.png) |

Regenerate the ignored answer files and screenshots from the repository root after generating the vocabulary fixture with its linked producer:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python \
  docs/evidence/g2-ios/MODEL-404/gates/generate-screenshot-decisions.py
cd web
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH \
VITE_HUMAN_GATE_ENABLED=false VITE_VISIT_GATE_ENABLED=false \
MODELSPEC_CAPTURE_SIMPLE=1 \
MODELSPEC_BROWSER_OUTPUT=/Users/terbeest/dev/worktrees/model-404/docs/evidence/g2-ios/MODEL-404/gates/round3/.generated/capture \
npm exec playwright -- test browser-tests/simple-decide.spec.ts \
  --grep 'capture simple' --workers=1 --reporter=line
```

Earlier evidence remains reviewable: [results.txt](results.txt) contains the initial six browser failures, the request-normalization regression, the 28-pixel home-link red and 44-pixel fix, first integration checks, and billing-helper cleanup checks. [late-merge-results.txt](late-merge-results.txt) and [late-merge-matrix.json](late-merge-matrix.json) cover the second main integration before REV-814. [focus-race-results.txt](focus-race-results.txt) distinguishes the Coding-focus CI red from local pre-fix greens, records the test-only eventual-focus fix and its negative control, and proves runtime code was unchanged for that correction. Those prior screenshot descriptions refer to the earlier image revisions; the images linked above are the round-three replacements.

Raw `.log` files are ignored local artifacts; the tracked summaries contain the relevant results. No deployed production decision, paid-provider call, recruited usability session, assistive-technology session, Firefox or Safari run was observed. The live smoke test supports both URLs but was not run against a deployed site. Full Python, site composition, surface lint and the built corpus belong to the main executor's evidence. All browser servers started by these runs have stopped.
