At a UTC dated-price boundary, the Worker selects a verified bundled successor from the same checkout without deployment. Both signatures must verify before either snapshot serves. Exhausted coverage returns `503 no_snapshot`, and matching vocabulary follows the handover.

Round 3 addresses Grok's blocking hardware-fit finding. Hardware-fit now shares the body-bound snapshot-header helper with decide and both compare routes. Real ledger settlement and release tests cross 2026-12-01 while another request advances the holder. The route audit found no other unprotected ID-header write. Historical compare also reselects current after awaited history I/O, preventing an expiry exception.

Health adds optional `decision_snapshot` metadata. Decision 2.18, bounded 1.5, and health 1.0 remain unchanged. The design was the draft PR's first commit.

The repository's `python -m qa.contracts` regenerated `qa/fixtures/mcp-tools.json`. Exactly one value changed, `source_hashes["api/worker/openapi.yaml"]`:

- Before: `29294163e44dd60f3f8d686edc92f0a5e22e191e2f0600dc2e2a6f2e17a6ef05`.
- After: `0a95c8ebbf3273b1578cfa049e74d306b435aedfcf8768735e87333688d1812b`.

Every other capture byte, all nine tool definitions, and six other source hashes are unchanged. No health-derived tool schema or QA helper changed. Round 3 requires no further capture change.

Validation of implementation `7f04d05f`, followed only by evidence commits:

- Red first: six hardware-fit failures and twelve passing route controls; historical compare separately reproduced the uncaught expiry exception.
- Affected Worker suites: 248 passed, one skipped. Final billing, compare-boundary, refresh, and dated-price run: 53 passed.
- After `web/npm ci` and the browser prerequisite build, the exact locked full suite exited **0**: **11,514 passed, 9 skipped, 11 warnings in 1174.82s**.
- All four browser configurations passed: 1,242 Vitest tests each and 429 Playwright passes total, with 11 expected skips. Shared build files stayed unchanged.
- Source CI: 18 checks passed, six skipped, none failed or pending.

The fresh public-fixture dry run measured 10,305,456 bytes against the 64 MiB Worker limit. Cached memory passed at 116.3546 MiB retained and 116.5819 MiB peak under the unchanged 120 MiB gate. The earlier cold-download failure remains recorded. Private production data and live isolate memory were not measured.

[Execution evidence](https://github.com/turbobeest/modelspec/blob/model-402-snapshot-successor/docs/evidence/g2-ios/MODEL-402-fix.md) contains exact commands, red and green output, the route audit, capture verification, and reproducible measurements. This PR remains a draft pending independent review.

Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Opus pending.
