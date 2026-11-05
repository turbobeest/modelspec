# MODEL-449 verification

Public base: `6815544116839f991c10904772e7357f12d5b566`.
Final implementation: `d28057f2aeddcc64bd0186918b40303909933b79`.
The subsequent evidence-only commit is included in the submitted head recorded
in the untracked `.pr-commit.txt` handoff and executor completion line.
Private workflow base: `c26a2d7b67039dd0ed2490cd740766680c9e454d`;
final: `2e98ae0cfd010dee0a87d20cf97958afeb95381b`.

The standalone `scripts.offering_drafter` writes a new offering and independent
receipts without premier admission. It shares the admission drafter's typed
candidate reader and real verifier. `decision/model.py:independent_families`
explicitly accepts a deterministic verifier as the second key; collector and
verifier actors must also differ. No second model family or paid model was used.

The release-card path calls this mode. Its draft PR includes the offering,
source registrations, verification receipts, and price gaps. Allowed source
copies remain outside git, in a 35-day private workflow artifact. Existing
offerings and source copies are preserved. Source registrations and verification
records are appended. The private workflow still requires a later engine pin
containing this implementation on public main; its existing pin was not changed.

## Red and green

All commands below used the designated public worktree unless stated otherwise.
Python was 3.14.4, pytest 9.1.1, git 2.50.1, gh 2.102.0, and Node 22.22.3.
Actual browser checks used Playwright 1.63.0 and Chromium 153.0.8010.12.

| Defect and regression | Observed red output | Observed green output |
| --- | --- | --- |
| `test_offering_writes_before_model_admission_with_independent_receipts` and five initial drafter cases | 6 failed, missing standalone module, exit 1 | All 9 final drafter tests passed |
| Budget, ownership, and retention cases in `test_offering_fetch.py` | 22 failed, missing module, exit 1 | 23 passed with real Chromium, exit 0 |
| `test_new_release_card_carries_verified_offering_without_full_admission`, `test_new_release_without_verifiable_prices_records_reasons` | Offering absent; result lacked price gaps, 2 failed, exit 1 | Both passed |
| `test_release_workflow_stages_offering_sources_and_receipts`, `test_release_workflow_retains_price_sources_and_installs_local_chromium` | Offering/source registry not staged; source artifact absent, 2 failed, exit 1 in both repositories | Both passed against both final workflows |
| `test_signal_process_persists_offering_and_price_report_with_production_fetcher` | Returned tuples differed from persisted JSON arrays, 1 failed, exit 1 | All 5 integration tests passed |
| `test_existing_citation_receipt_is_not_rewritten`, `test_corrupt_existing_copy_is_not_replaced` | Existing bytes changed, 2 failed, exit 1 | Both passed |
| `test_chromium_refuses_redirect_before_restricted_response` | Server observed `['/start', '/restricted']`, exit 1 | Server observed only `['/start']`, exit 0 |
| Two `nonpremier` cases in `test_slice1_offerings.py` | Premier-only assertion applied to draft; absent retention claim raised `StopIteration`, 2 failed, exit 1 | 19 passed; controls still reject incomplete premier offerings and unconditional retention claims |

The browser regression used only a local synthetic server. Chromium redirects
now fail closed before fulfillment because routing does not intercept each hop.
The real-browser test closes its server and browser in `finally`/context managers.

Exact public test commands, with red invocations using the relevant named file
or `-k 'existing_citation or corrupt_existing_copy or disagreeing'`,
`-k release_workflow`, `-k nonpremier`, and `-k chromium`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_offering_drafter.py tests/test_offering_fetch.py tests/test_release_signal_prices.py tests/test_release_signals.py tests/test_admission_drafter.py tests/test_admission_fallback.py tests/test_slice1_offerings.py tests/test_removed_sources.py
# Exit 0: 222 passed, 1 skipped in 92.28s. The skip requires a built MODELSPEC_DIST.
env PYTHONPATH="$PWD/.scratch/model-449/price_fetch/venv/lib/python3.14/site-packages:$PWD" PLAYWRIGHT_BROWSERS_PATH="$PWD/.scratch/model-449/price_fetch/browsers" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_offering_drafter.py tests/test_offering_fetch.py tests/test_release_signal_prices.py
# Final code, exit 0: 37 passed in 2.98s, including actual Chromium.
env MODEL449_RELEASE_WORKFLOW=/Users/terbeest/dev/worktrees/data-model-449/.github/workflows/release-signals.yml PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signal_prices.py -k release_workflow
# Exit 0: 2 passed, 3 deselected.
git diff --check
# Exit 0.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
# After staging the evidence, exit 0: 46 passed, 1 built-dist skip in 53.41s.
```

## Five releases

The authorized private scratch clone was created with
`git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/private-data`.
Each command below exited 0. None wrote an unverified price. All five produced
explicit gaps; these replays did not produce five successfully priced offerings.

```sh
for model in openai/gpt-6-1-sol stepfun/step-5-preview qwen/qwen3-8-omni-flash xai/grok-imagine-video-1-5-lite mistral/mistral-large-4; do
  env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.offering_drafter --data-dir /tmp/model-449-scratch/private-data --model "$model" --write --cache-dir /tmp/model-449-scratch/replay/copies --report "/tmp/model-449-scratch/replay/${model//\//-}.json" > /tmp/model-449-scratch/replay/last-command.json
  result=$?
  echo "$model exit=$result"
  if test "$result" -ne 0; then exit "$result"; fi
done
```

| Release | Observed reason |
| --- | --- |
| GPT-6.1 Sol | Own documentation is cite-only. URL, hash and retrieval metadata retained; no source bytes or machine-verified price. |
| Step 5 Preview | No registered first-party provider mapping for `stepfun`. |
| Qwen3.8 Omni Flash | No registered first-party provider mapping for `qwen`. |
| Grok Imagine Video Lite | Non-token pricing has no applicable deterministic price reader. |
| Mistral Large 4 | First-party sources are under the MODEL-409 terms hold. |

Discovery catalogue prices were never accepted as evidence. Firecrawl credits
actually used: **0**. Paid calls are disabled by default. An explicit restored
ledger is required; locked durable reservations cap the run at 5 and the current
UTC calendar month at 100. Missing/corrupt accounting refuses work. The inherited
paid-host allowlist currently overlaps cite-only policy, so those hosts remain
blocked. Limits and interruption/concurrency behavior were tested with a mocked
HTTP transport; no live paid scrape was tested.

## Private data verification

The linked-data guard passed all 14 configured paths. Engine composition used:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-449-scratch/private-data/.github/scripts/check_linked_data.py --engine /Users/terbeest/dev/worktrees/model-449 --data /tmp/model-449-scratch/private-data
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/prepare_data_writer.py --engine /Users/terbeest/dev/worktrees/model-449 --data /tmp/model-449-scratch/private-data
```

Both exited 0. Composition temporarily replaced eight tracked scratch documentation
files. Their exact HEAD bytes were restored before testing. No source copy,
manifest, or receipt was replaced. The private workflow PR contains only its
workflow change, with no curated data or pin changes.

The exact synthetic setup is preserved in [MODEL-449-fixture.py](MODEL-449-fixture.py).
It used `release_catalogue(..., prices=True)` from
`tests/test_release_signal_prices.py`, then real `draft_signal` against the
scratch private catalogue with socket connections prohibited. It validated the
new card and offering, asserted input 2/output 8, and requeued exactly their two
claims with `Queue.requeue`. From that scratch checkout:

```sh
env PYTHONPATH=$PWD MODELSPEC_SOURCE_CACHE=/tmp/model-449-scratch/audit/source-copies /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-449-scratch/audit/prepare_fixture.py
env PYTHONPATH=$PWD MODELSPEC_SOURCE_CACHE=/tmp/model-449-scratch/audit/source-copies /Users/terbeest/dev/modelspec/.venv/bin/python -m cli.modelspec.legacy verify --root /tmp/model-449-scratch/private-data --only google-gemini-api/google/fixture-model/ --json
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.validate_pr --all
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_source_terms.py .github/scripts/tests/test_source_retention_guard.py tests/test_slice1_offerings.py tests/test_decision_model.py
```

All exited 0. The real verifier reported **2 verified, 0 mismatch, 0 unreachable,
0 skipped**, using `offering-price-table@1`. All **1,386 cards validated**;
the focused private CI subset reported **97 passed in 8.70s**. Existing registry,
verification log, and queue bytes were confirmed as unchanged prefixes.

No full local suite, site build, live vendor API, deployment, or remote CI result
was observed. No engine/export fields or Worker-vendored module changed:
`api/worker/vendor.py` vendors only `release_signals/__init__.py` and `contract.py`,
not the changed pipeline. The conditional Worker memory probe and re-vendor were
therefore not run. Independent review, CI, human merges, and subsequent private
engine-pin adoption remain pending. Private scratch data is removed after this
evidence is captured; no private catalogue contents enter the public commit.
