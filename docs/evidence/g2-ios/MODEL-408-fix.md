# MODEL-408 execution evidence

Engine base: `badf4be5fdff0a0803fd69387b165307f4190909`.
Design-only first commit: `581833f1`.
Final implementation and private engine pin:
`a22355bf9c3d9511ff563494791dd99282411898`.
Private data base: `92f1f227dcd64394a362e827dfedb306a99beead`.
Final private data commit: `9cb9260f394e8d6b0c0300c5c5091c502ee482bb`,
draft [data PR #96](https://github.com/turbobeest/modelspec-data/pull/96).
The final engine evidence commit is reproducible with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-408-fix.md`.

## Result and limits

The new exact template supports seven current xAI plan identities: Free,
Plus, Premium, Super, Ultra, Teams and Enterprise. It admits five exact USD
monthly prices and seven Build/Bot product-inclusion readings. Free's Build
cell remains limited. Teams' starting per-seat amount and Enterprise's custom
price remain unknown under the scalar subscription-price contract.

The current matrix contains no versioned Grok model rows. All seven new
`models_covered` facts remain unknown. Product names cannot establish
canonical model IDs. Lite and Heavy keep their historical IDs, unknown or
quarantined facts, and a dated explanatory note. No retirement or successor
is inferred. The optional availability facet already exists at the base;
this change adds no schema field and widens no contract range.

All 17 known private facts pass `xai-exact-template@1` before filing. The
snapshot admits exactly those facts and excludes unsupported new coverage,
new usage allowances and the eight previously unsupported Lite/Heavy facts.
Existing Business Grok 4.7 coverage remains intact. No surfaces or
own-software routing changes were made.

## Retrieval and exact binding

Full headed Chromium 153.0.8010.12 retrieved https://x.ai/pricing on
2026-10-18 with HTTP 200. The 554,565 retained bytes have raw SHA-256
`bdf1848f0fe27294ccc7497f2016650cb32406e7252ccf191ab5d3b21d16ab21`.
The normalized document hash is
`c6fac83303fe97d19fd186eaf53ba0b828074e67b4bd7d626ba5431f81113bd7`,
and the complete comparison-region DOM hash is
`a881126da00c7280c4a9b38810f75ee5e1db2c54cffc587034d2f204caee5708`.
The template also binds literal headers, selected row labels, explicit
column/cell paths and approved check/minus SVG hashes.

The source copies, screenshot, complete DOM bindings and fresh reuse review
remain in private `research/model-408/capture/` and `reuse/`. The public
fixtures are synthetic. The current consumer terms, Enterprise Terms, AUP,
X-subscription terms and robots directives were checked and retained with
hashes. Robots preferences do not establish redistribution rights. The
private review records the copying/access restrictions without claiming
legal clearance. All six retained documents passed independent byte-count
and hash checks. Both browser processes exited 0 and closed their browsers.

The exact capture commands, run from this engine worktree, were:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node docs/evidence/g2-ios/MODEL-367/capture.mjs /Users/terbeest/dev/worktrees/data-model-408/research/model-408/capture pricing=https://x.ai/pricing
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node docs/evidence/g2-ios/MODEL-367/capture.mjs /Users/terbeest/dev/worktrees/data-model-408/research/model-408/reuse consumer-terms=https://x.ai/legal/terms-of-service robots=https://x.ai/robots.txt enterprise-terms=https://x.ai/legal/terms-of-service-enterprise acceptable-use-policy=https://x.ai/legal/acceptable-use-policy x-subscription-terms=https://x.ai/legal/x-subscription-terms-of-service
```

## Red-first results

The initial unmodified engine admitted current-plan claims through generic
fallback dispatch. These tests produced 48 failures, exit 1:

- `test_current_plan_cannot_verify_an_unapproved_document_or_null`, 42 cases
  covering seven current plans and six scoped facets.
- `test_current_matrix_mutation_cannot_fall_back`, six cases covering a
  reordered column, extra column, swapped glyph, renamed plan, changed row
  and moved cell.

`MODEL-408/dispatch-red.txt.gz` retains the failing assertions. After exclusive
dispatch was added, all 48 passed, exit 0, in `dispatch-green.txt.gz`.

Before price and Limited-cell support, the 17 positive cases in
`test_current_plan_reads_its_exact_monthly_price` and
`test_current_plan_preserves_product_cell_meanings` failed. The reader
reported that the Limited cell was not exactly one SVG glyph. That run
ended with 17 failed and 85 passed, exit 1, in `reader-red.txt.gz`.
After the minimal reader extension, both reader suites passed all 163 cases,
exit 0, in `reader-green.txt.gz`.

`test_approved_current_template_rejects_mutation` repeats all six attacks
against the same approved synthetic template used by the positive controls,
for price, billing period, products and null model coverage. It never
reapproves a mutated hash. Additional cases reject wrong-column prices,
annual billing, starting/custom prices, invented API permission, invented
model IDs, and empty or null coverage. No existing test was weakened.

An internal reviewer independently replayed the production templates through
CopyStore and `verify.verify`. All 85 cases passed: 18 verified and 67
expected mismatches. A fallback trap was never called. The cases include
the retained Business page, cross-plan/source ownership, all current-plan
null claims, legacy subjects and changed bytes. Its report and receipts are
private under `research/model-408/capture/internal-review*`. This is not the
external cross-model review required before merging.

## Validation

The focused suite passed 760 tests, exit 0, in `focused-green.txt.gz`.
Web dependency installation, the web build and all 843 web tests exited 0.
The test runner reported one skipped test file. Logs are in `web-build.txt.gz`
and `web-tests.txt.gz`.

The required full engine suite is queued under the shared lock. Its final
result will be recorded here before executor completion.
The static-site build exited 0. Its retained log includes existing frozen-data
source-registration warnings and the generated manifest, in `site-build.txt.gz`.

The evidence/chart check exited 0 with `nothing to check`. The data-freeze
guard exited 0 with `data freeze: ok`. Ruff passed the reader and new test
file. Checking the large existing `decision/verify.py` also reported eight
pre-existing E501 findings; `lint-baseline.json` proves the findings match
the base exactly. `git diff --check` passed.

The private suite passed 1,129 tests with 17 skips, exit 0. Its report records
the red private filing check, green replay, snapshot assertions, append-only
verification history, and linked-data guards. The engine pin descends from
the previous pin. Staging and cleanup left no copied engine files or Python
under linked data paths. Private tests and receipt commands are in the
private `docs/evidence/g2-ios/MODEL-408-fix.md`.

The private snapshot grew by 1,045 gzip bytes and 12,442 JSON bytes. A separate
probe built the complete Worker bundle from the curated private data and
ran the existing Pyodide memory gate with a synthetic signing key. Steady
memory was 113,608,520 bytes, 108.35 MiB, below the 125,829,120-byte limit.
Peak memory was 115,465,192 bytes, 110.12 MiB, below the warning threshold.
Both vendoring and the probe exited 0. Its bundle used an isolated output
directory and did not modify shared generated Worker files. Exact commands,
input hashes and byte-only results are private in
`research/model-408/memory/`. This was a local runtime measurement, not a
deployed Worker measurement.

Validation commands ran from this engine worktree unless stated:

```bash
# In web/:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
# Back in the engine:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_xai_consumer_lineup.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_xai_matrix_reader.py tests/test_xai_consumer_lineup.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_xai_matrix_reader.py tests/test_xai_consumer_lineup.py tests/test_decision_verify.py tests/test_decision_sources.py tests/test_model380_subscription_types.py tests/test_model380_subscription_quotes.py tests/test_subscription_availability_reader.py tests/test_model_396_readers.py tests/test_worker_vendor_imports.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out tmp/model-408/sites
# In web/:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
# Back in the engine:
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/chart_check_pr.py --base badf4be5fdff0a0803fd69387b165307f4190909
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base badf4be5fdff0a0803fd69387b165307f4190909 --head HEAD --branch model-408-xai-consumer
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check decision/xai_matrix.py tests/test_xai_consumer_lineup.py
git diff --check
```

Tool versions were Python 3.14.4, pytest 9.1.1, Node 22.22.3, npm 10.9.8,
Playwright 1.63.0, Chromium 153.0.8010.12, Pyodide 0.28.3, Git 2.50.1,
GitHub CLI 2.102.0 and flock 0.4.0. Test exit codes were checked directly. Gzip logs preserve the original output
bytes, including whitespace in failing assertions and test-runner output.

## Unobserved outcomes

No versioned current consumer model coverage, exact Teams or Enterprise plan
amount, or Lite/Heavy retirement statement was observed. No paid subscription,
raw API entitlement, production deployment, merge, Linear write, workflow
dispatch, Firecrawl credit or paid-provider call was exercised. The data
pin's main-ancestry gate remains a merge-order dependency until the engine
implementation reaches main. Both PRs are drafts for human review.
