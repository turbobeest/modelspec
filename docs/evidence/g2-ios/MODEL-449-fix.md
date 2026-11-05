# MODEL-449 verification

## Round 2: exact price attribution

Round-two base: `489eab5e3124e82e4de96402086068ebce949acb`.
Final implementation: `4a24eda6bb5b65e5c9e2c86322e86982bf5b4c36`.
The evidence-only follow-up is included in the final submitted head recorded in
`.pr-commit.txt` and the executor completion line. This updates existing draft
PR #972; data PR #128 has no round-two changes.

The review's substring match and subject replacement predate this PR:

```sh
git blame 6815544116839f991c10904772e7357f12d5b566 -L 715,719 -- decision/verify.py
```

Exit 0. All five lines belong to `2ad89a4ee8`, dated 2026-09-25.
Direct and grouped pricing rows now require exact normalized membership in the
claim's names and preserve the published subject. Full aliases must be explicit;
qualifiers such as `Global` or marketing descriptions are never inferred.
Existing positive parser fixtures declare their full aliases and retain their
price, tier, and wrong-value assertions. New controls reject undeclared aliases.

An additional full-verifier probe found the same misattribution in Btok/Mtok
tables and cached-price prose. Btok prices now use the adjacent exact model
declaration and MODEL-426 heading checks. Cached prose must name the exact model
before `caching`; free-output statements are limited to the next line of the
owned Btok table. No whole-page substring is used to establish model identity.

### Round-two red and green

Python 3.14.4, pytest 9.1.1, git 2.50.1. Tests used the designated worktree,
serial pytest, and synthetic source bytes; no provider or paid calls.

| Regression | Red, before its fix | Final green |
| --- | --- | --- |
| `test_substring_model_row_leaves_prices_unwritten`, `test_price_table_with_both_models_keeps_only_the_exact_row`, normalized-name controls | 5 failed, 4 passed, exit 1. Sibling-only pages wrote offerings; mixed pages lost the exact price. | All 9 passed |
| `test_offering_price_rows_require_an_exact_registered_name`, `test_offering_price_row_preserves_its_normalized_exact_subject`, explicit-alias controls | 11 failed, 1 passed, exit 1. Wrong subjects were accepted or replaced. | All 12 passed |
| `test_scoped_btok_price_never_verifies_another_models_heading`, `test_cached_price_prose_never_verifies_an_extended_model_name`, exact/alias controls | 9 failed, 5 passed, exit 1. Real `verify()` returned `verified` for sibling prices; normalized cached identity also failed. | All 14 passed |

Exact focused commands, with the first three run before the corresponding fix:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_offering_drafter.py -k 'substring_model or both_models or normalized_exact'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k 'offering_price_rows_require_an_exact_registered_name or offering_price_row_preserves_its_normalized_exact_subject or offering_price_row_uses_an_explicit_alias_without_rewriting_it'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k 'scoped_btok or cached_price_prose'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py tests/test_offering_drafter.py tests/test_metric_price_tables.py tests/test_price_reread.py tests/test_admission_drafter.py
# Final code: exit 0, 684 passed in 7.77s, including the MODEL-426 table-attribution suite.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py
# After staging round-two evidence: exit 0, 46 passed, 1 built-dist skip in 60.01s.
```

Red logs remain in `.scratch/model-449-r2/root/attribution-red.log`,
`.scratch/model-449-r2/review/red.log`, and `review/scoped-red.log`;
the final output is `root/final-focused.log` under the same scratch directory.

### Existing private offering prices

Both runs invoked the real deterministic verifier for every current
`offering.price.*` fact, using current values and references with filed claim
names and collector metadata. The generic, byte-identical reproduction script
is preserved in [MODEL-449-r2-replay.py](MODEL-449-r2-replay.py).
It disables network connections, reads committed archives only into memory,
refuses source writes, and checks tracked file hashes and git status afterward.
Exact executed commands:

```sh
git clone --depth 1 https://github.com/turbobeest/modelspec-data.git /tmp/model-449-scratch/private-data
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r2/private/replay_prices.py --engine $PWD --data /tmp/model-449-scratch/private-data --revision 489eab5e --output /tmp/model-449-scratch/prices-before.json
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-449-r2/private/replay_prices.py --engine $PWD --data /tmp/model-449-scratch/private-data --output /tmp/model-449-scratch/prices-after.json
```

All exited 0. Private main was `c26a2d7b67039dd0ed2490cd740766680c9e454d`.
Final verifier SHA-256 was
`3c1de57ac8dc859d22509a7ffe76c6418bf6292f40d3e2128a2b4dbb7fa9e2d6`.

| Outcome | Before | After |
| --- | ---: | ---: |
| Verified | 71 | 71 |
| Mismatch | 3 | 3 |
| Cited | 30 | 30 |
| Unreachable | 126 | 126 |
| Total | 230 | 230 |

**Every fact whose outcome changed: none.** Methods, reasons, and diffs also
matched for every fact. Forty-five facts exercised `offering-price-table@1`.
Coverage is limited: matching retained bytes exist for 74 facts. The scan
checked all 4,676 tracked files and 407 gzip archives, but only four of 20
non-cited hashes are present. The 126 unreachable facts include 102 known and
24 not-disclosed values. This is not a claim that all 230 prices were reverified.
All tracked private files remained byte-identical; no data file was rewritten.
Full per-fact results remain untracked in the private data worktree at
`.scratch/model-449-r2/`; no private values enter this public evidence.

The verifier is absent from `api/worker/vendor.py:SOURCES`; snapshot/export
consumes recorded receipts and does not run these readers. With no receipts,
rank rows, or exported fields changed, the conditional Worker memory probe and
re-vendor are not triggered. No full local suite, deployment, or remote CI result
was observed. The private scratch clone was deleted after confirming the saved
private reports were byte-identical to the compared files.

## Round 1

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
