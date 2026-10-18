At a UTC dated-price boundary, the Worker selects a verified bundled successor from the same checkout without waiting for deployment. It verifies both bundled signatures before either snapshot can serve, refuses exhausted coverage with `503 no_snapshot`, and keeps each response's snapshot header equal to its body reference. Matching vocabulary follows the same handover.

Health adds optional `decision_snapshot` metadata for the serving ID and expiry, successor presence, and successor start. Decision 2.18, bounded 1.5, and health 1.0 stay unchanged. The design was the first commit of this draft. No ranking, workflow, frozen-data, legal, or production-switch change is included.

The orchestrator granted the QA capture scope exception. `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts` regenerated `qa/fixtures/mcp-tools.json`. Exactly one value changed, `source_hashes["api/worker/openapi.yaml"]`:

- Before: `29294163e44dd60f3f8d686edc92f0a5e22e191e2f0600dc2e2a6f2e17a6ef05`.
- After: `0a95c8ebbf3273b1578cfa049e74d306b435aedfcf8768735e87333688d1812b`.

Every other capture byte, all nine tool definitions, and the six other source hashes are unchanged. No health-derived tool schema or QA helper changed. The existing gate-off test now explicitly asserts the additive snapshot header against the response body before comparing the unchanged historical response fixture.

Validation at `4b0c8cea`:

- Successor, dated-price, refresh, and gate-off focused suites: 61 passed, exit 0.
- QA harness and gaps suites: 123 passed, exit 0.
- Repeated `web/npm ci` and the browser prerequisite build: exit 0.
- Complete pytest suite: queued under the required shared lock; result pending.
- Decide browser matrix: four human/visit gate configurations running against isolated builds; results pending.
- Public-fixture Worker upload: 10,304,997 bytes against the 64 MiB limit. Cached memory probe passed at 116.3302 MiB steady. The retained cold-download observation exceeded the repository's 120 MiB safety threshold. Private production catalogue size and a production rollout were not measured.

The first full attempt's failures and the subsequent corrections are preserved in [the execution evidence](docs/evidence/g2-ios/MODEL-402-fix.md), alongside red-first output, exact commands, generated-capture verification, and reproducible bundle measurements. This PR remains a draft pending independent review.

Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Opus pending.
