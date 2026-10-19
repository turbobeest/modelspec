# MODEL-411 execution evidence

Date: 2026-10-19. Worktree: `/Users/terbeest/dev/worktrees/model-411-cite-only`.
Branch: `model-411-cite-only`.

- Base SHA: `bbfa93be5eed392878a2af0d709ca6e774302c5c`.
- Design-first commit: `36b1d65597d3e87aaa06553740fb47cb90d39ead`.
- Main implementation commit: `e529e66932e2a80064447ceb4b06663ee1bb3456`.
- Flat-score citation commit: `0783b9267b9afbf093dcca43492b592f2abc50cd`.
- Generated MCP fixture commit: `eae42d7f22696e155dad5295f9dd58b4c77076a3`.
- Final implementation SHA tested: `f72a2721654c05950c93f19e611bc0bc599d3f66`.
- The subsequent evidence-only commit contains this report. Its SHA is obtained with
  `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-411-fix.md`; the PR and
  executor completion marker record the final branch tip. No code changes follow
  the final implementation SHA above.

The public build configuration `registry/source-retention.json` names `x.ai`,
`docs.x.ai`, and `perplexity.ai`, including matching subdomains and observed
redirect origins. No private-data follow-up is needed for the host list.
Cite-only fetches retain URL, retrieval time, and hash metadata without new page
copies. Verification returns `cited`, and admitted facts carry null verification,
citation provenance, and explicit public warnings. Existing contract states and
versions remain unchanged; citation fields and open warning codes are additive.

## Required gates

| Check | Observed result |
| --- | --- |
| Site build | Exit 0 on the final source revision; `root/site-build-final-code.log` |
| Surface lint | Exit 0: `dist/modelspec: 0 findings; 5366 files checked` |
| Web install/build/test | Exit 0; 900 tests passed, 57 files passed and one skipped |
| MCP install/typecheck/test | Exit 0; 235 tests passed across 12 files |
| Agent-copy generator check | Exit 0; `root/agent-copy-final-code.log` |
| OpenAPI generator check | Exit 0: `api/worker/openapi.yaml matches the implementation` |
| QA contract generator | Exit 0; MCP source digest refresh committed in `eae42d7f` and included at the final tested SHA |
| Evidence/release chart guard | Exit 0: `nothing to check` |
| Data freeze | Exit 0: `data freeze: ok` |
| Full pytest under the shared lock | Exit 0: 12,178 passed, 9 skipped, 11 warnings in 1559.82s (25:59); `root/full-pytest-final.log` |

These commands ran from the worktree, and each return code was captured directly
before printing a log excerpt. The web and MCP commands are recorded with their
red/green evidence below.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m api.worker.openapi
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m api.worker.openapi --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/chart_check_pr.py --base bbfa93be
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base bbfa93be --head HEAD --branch model-411-cite-only
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Tool versions: Python **3.14.4**, pytest **9.1.1**, Node **v22.22.3**, npm
**10.9.8**, git **2.50.1**. Python commands used the repository's shared virtual
environment. Node commands used the pinned binary directory. Version commands:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm --version
git --version
```

## Red/green behavioral evidence

Commands ran from `/Users/terbeest/dev/worktrees/model-411-cite-only` unless a different working directory is stated. Python was 3.14.4 and pytest 9.1.1; web commands used Node v22.22.3 and npm 10.9.8. Tests used synthetic pages and mocked fetchers, without live provider requests. Recorded red runs exited 1 and green runs exited 0. Counts below belong to the named runs, whose test sets overlap; they must not be summed.

### Retention and redirect boundaries

`retention/red.txt` records **10 failed** before implementation. Relevant tests were `test_copy_store_cite_only_keeps_only_citation` (normalized host cases), `test_copy_store_requires_origin_and_preserves_unrestricted_hosts`, `test_copy_store_redirect_is_cite_only_even_with_existing_hash`, `test_fetcher_keeps_redirect_origins_for_retention`, `test_recheck_hash_does_not_reconfirm_a_cited_fact`, `test_price_fetch_cite_only_does_not_write_copy`, `test_benchmark_named_cache_retains_metadata_not_text`, and `test_disk_scraper_refuses_cite_only_before_subprocess`. Failures included the absent origin-aware API, an unchanged hash reconfirming a fact, a fetch returning `ok` instead of `cited`, and a retained body file. The combined source/collector run subsequently recorded **518 passed** in `retention/green.txt`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_decision_sources.py tests/test_fetch.py tests/test_fetch_pricing.py tests/test_model_345_collect.py tests/test_data_trust.py tests/test_licence_coverage.py tests/test_fetch_ranking_leaderboards.py tests/test_leaderboard_refresh.py tests/test_model_160_evidence.py tests/test_model_163_collect.py
```

`surfaces/red-redirects.log` records **6 failed**, of which five reached the intended retention assertions; the sixth was a fixture error described below. `test_hash_cache_does_not_replay_any_restricted_metadata_origin`, `test_hash_cache_citation_marker_blocks_historical_body`, `test_named_cache_checks_all_redirect_origins_before_writing`, and `test_rendered_fetch_preserves_intermediate_redirect_origin` exposed replay or persistence through historical bodies and redirect metadata. `test_firecrawl_preserves_both_reported_origin_fields` covers both rendered origins after fixture correction. `retention/redirects-green.txt` records **77 passed**.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_redirects.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_redirects.py tests/test_cite_only_retention.py tests/test_fetch.py tests/test_fetch_pricing.py tests/test_model_160_evidence.py
```

`test_rendered_replay_carries_only_hash_and_fetch_date` then failed because an old generated `.html` remained beside the metadata manifest: **1 failed, 11 deselected**, `retention/reused-artifact-red.txt`. After cleanup, the source/fallback run recorded **255 passed**, `retention/final-green.txt`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py -k rendered_replay
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py tests/test_cite_only_redirects.py tests/test_price_reread_fallback.py tests/test_decision_sources.py
```

Later output review found two additional leaks. `test_benchmark_cli_emits_only_citation_metadata` exposed copied page text or links on stdout (**3 failed, 12 deselected**, `retention/cli-red.txt`). `test_failed_cite_only_reread_report_omits_old_quoted_value` exposed old quoted content in an unreachable reread report (**1 failed, 15 deselected**, `retention/report-red.txt`). Their combined green run recorded **135 passed**, `retention/output-green.txt`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py -k benchmark_cli
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py -k failed_cite
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py tests/test_cite_only_redirects.py tests/test_price_reread.py tests/test_fetch.py
```

### Verification, admission, and provenance

`verification/red.log` records **9 failed, 6 passed**. `test_cite_source_ref_preserves_fetch_timestamp_without_changing_old_refs` found the timestamp rejected; `test_cite_verifier_returns_cited_without_reading_or_verifying` and `test_cite_run_checks_queue_without_verification_or_recrawl` reached a reader that deliberately raises on access; `test_cite_facts_satisfy_premier_completeness_without_verification` found both blocked admission and retained historical verification. `test_cite_lookup_includes_model_inheritance_and_subscription_facts` found the lookup API absent, while `test_cite_redirect_policy_survives_snapshot_build_without_local_copy_store` found redirect-derived admission missing.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_verification.py > .scratch/model-411/verification/red.log 2>&1
```

Additional admission regressions were red before their fixes: `test_cite_admission_still_validates_facet_value` admitted a nonnumeric context limit, and `test_authored_citation_cannot_relabel_an_ordinary_verified_fact` retained untrusted citation metadata (**2 failed**, `verification/admission-red.log`). `test_cite_redirect_evidence_cannot_enter_as_verified` also failed in `verification/redirect-red.log`; that run contained an earlier cache-dependent test later replaced as described below. The completed verification/model/snapshot/parser run recorded **648 passed**, `verification/focused-green.log`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_verification.py -k 'redirect_evidence or copy_marker' > .scratch/model-411/verification/redirect-red.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_verification.py -k 'validates_facet or authored_citation' > .scratch/model-411/verification/admission-red.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_verification.py tests/test_decision_model.py tests/test_decision_snapshot.py tests/test_decision_verify.py tests/test_xai_matrix_reader.py > .scratch/model-411/verification/focused-green.log 2>&1
```

The final suite also checks mismatch/unreachable quarantine, malformed hashes, ordinary-host unverified rejection, operational identifier exclusion, specialized reader interception, and historical-copy refusal. These are coverage statements, not claims that each test was separately captured red.

`test_cite_lookup_does_not_load_full_provenance` exposed eager provenance loading for both restricted and ordinary hosts (**2 failed**, `verification/lazy-provenance-red.log`). The fix indexes cited record IDs and leaves full provenance packed. The combined warning/memory run recorded **44 passed**, `verification/lazy-provenance-green.log`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_verification.py -k does_not_load_full > .scratch/model-411/verification/lazy-provenance-red.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_verification.py tests/test_cite_only_surfaces.py tests/test_snapshot_successor_memory.py > .scratch/model-411/verification/lazy-provenance-green.log 2>&1
```

### Public responses, pages, and exports

`surfaces/red-pytest.log` records **5 failed**: `test_cited_fact_warns_in_complete_and_bounded_decisions` lacked warnings at `none`, `summary`, and `full`; `test_cited_record_never_passes_as_verified_evidence` raised `TypeError` on null verification; and `test_model_page_names_cited_fact_and_source_without_claiming_verification` found the model citation field absent. Additional comparison/vocabulary tests recorded **2 failed** in `surfaces/red-comparison-vocabulary.log`.

Cross-review extended `test_named_comparison_preserves_citation_metadata` to `not_disclosed` and `requires_contract`, exposing lost citation metadata, and added `test_cited_estate_gain_warns_without_current_cited_hold`, exposing an unwarned recommended subscription. Their red run was **3 failed, 1 passed, 8 deselected**, `surfaces/red-assurance-review.log`; the final public/comparison/estate/contract run was **301 passed**, `surfaces/green-assurance-review.log`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_surfaces.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_surfaces.py -k 'named_comparison or estate_gain'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_surfaces.py tests/test_model_comparison.py tests/test_decision_estate.py tests/test_decision_contract.py
```

`root/red-exports.log` records **3 failed, 1 passed**: `test_model_export_carries_citation_url_hash_and_fetch_date` retained old verification, `test_cited_fact_notice_survives_rank_export_and_worker` lacked model citation metadata, and `test_cited_benchmark_is_not_counted_as_verified` still included the benchmark in the verified set. `root/green-exports.log` records **4 passed** for the same file.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py
```

Cross-review found three more export defects: `test_citation_export_preserves_distinct_facts_with_the_same_facet` lost record identity, `test_benchmark_catalogue_export_separates_citations_from_verified_results` included citations in verified results, and `test_cited_catalogue_result_is_not_presented_as_verified` lacked a benchmark-page notice. `surfaces/red-export-review.log` records **3 failed, 16 deselected**; `surfaces/green-export-review.log` records **81 passed**.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py tests/test_cite_only_surfaces.py -k 'distinct_facts or catalogue_result or catalogue_export'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py tests/test_cite_only_surfaces.py tests/test_pipeline.py
```

The web test `shows citation assurance on the simple answer even when the cited row was trimmed` failed on the missing notice. The detailed-answer test's initial failure was a fixture problem, not a demonstrated missing notice; see caveats. `surfaces/red-web.log` records **2 failed**; `surfaces/green-web.log` records **2 passed**. The web build exited 0, and `surfaces/web-all.log` records **900 passed**, with 57 passing and one skipped test file. These commands ran with working directory `web`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test -- --run src/decide/__tests__/cite-only.test.tsx
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
```

### Accuracy reports and CLI wording

`verification/accuracy-red.log` records **5 failed**. `test_fidelity_cite_only_remains_cited_without_verification_or_private_upgrade` exposed both `KeyError: cited` and an erroneous private-correction upgrade to `public_image_lag`. `test_fidelity_citations_do_not_count_as_assessed_or_dilute_unknown_share` exposed a diluted unknown share; `test_fidelity_fetch_preserves_hash_date_and_redirect_origin` found missing fetch metadata; and `test_verify_cli_does_not_call_a_cited_check_verified` found the misleading “Verified” introduction. Extending the metadata test then exposed missing timestamps and redirect URLs in persisted diagnostic reports (**1 failed**, `verification/accuracy-metadata-red.log`).

The final combined accuracy/verification/public/memory run recorded **125 passed**, `verification/final-focused-green.log`. Cited results remain outside verification accuracy denominators and private-correction upgrades; fetch metadata survives temporary-store closure, and absent optional metadata preserves the existing failure-report shape.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_accuracy.py > .scratch/model-411/verification/accuracy-red.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_accuracy.py -k fetch_preserves > .scratch/model-411/verification/accuracy-metadata-red.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_accuracy.py tests/test_accuracy.py tests/test_accuracy_alert.py tests/test_cite_only_verification.py tests/test_cite_only_surfaces.py tests/test_snapshot_successor_memory.py > .scratch/model-411/verification/final-focused-green.log 2>&1
```

### Setup and fixture caveats

- An early verification test attempt used a raw dictionary for `Claim.target` and tried to mutate frozen `SnapshotInputs`. Those fixture errors were corrected before the saved `verification/red.log`; they are not behavioral red evidence.
- The initial full verification/parser run recorded **59 failed, 580 passed** because historical synthetic xAI parser fixtures now encountered the production retention policy. The parser fixture now disables that policy only within its suite, retaining all existing parser assertions. Separate policy tests exercise the production interception; the corrected combined run passed 648 tests.
- The old redirect `copy_marker` test depended on the operator's local CopyStore during snapshot compilation. It was replaced with a verify-runtime marker test. Final snapshot compilation derives citations only from registered source URLs and persisted source references; old missing retrieval dates remain null.
- `retention/weekly-red.txt` is misleadingly named: it records **12 passed**. An earlier weekly test failed collection because of an incorrect test-module import. `retention/collectors.txt` exited 4 with no tests because `tests/test_refresh_leaderboards.py` did not exist; the corrected command above uses `tests/test_leaderboard_refresh.py`.
- Intermediate retention runs caught a zero-count output-shape change, two synthetic fallback expectations using x.ai as a verified host, and a variable typo. Their failures are preserved in `retention/green-attempt.txt` and `retention/focused.txt`; the final source and collector runs passed.
- The Firecrawl red fixture originally used `openai.com`, outside its existing allowlist. The fixture changed to `chatgpt.com`; production allowlist policy did not change. That initial failure does not establish the intended redirect defect by itself.
- The first web invocation exited 127 because dependencies were absent. After `npm ci`, the simple-answer test reached the missing-notice assertion; the detailed fixture first needed `boardWeights.chat_preference=1` to render its result row. Neither the missing executable nor the detailed fixture exception is counted as behavioral red evidence.
- A public-suite run during edits recorded **429 passed, 2 failed** from stale schema/document artifacts. Regeneration resolved them, and subsequent contract runs passed. One intermediate accuracy run failed an existing exact-output assertion after null/empty optional metadata was added; the fix omits absent metadata rather than weakening that assertion.

Log paths above refer to the original `.scratch/model-411/` run directory; logs were later moved to `tmp/model-411-execution/`. Re-running a red command against the completed implementation should pass; the saved red outputs establish its earlier failure. Root owns final commit identification, required gates, and the complete evidence record.

## Final integration regressions

The standalone rank report omitted the fact citation map even though the site
and Worker exporters supplied it. `test_standalone_rank_report_preserves_fact_citation`
failed with `KeyError: 'warnings'` (**1 failed, 6 deselected**, exit 1). After the
CLI shared the same loader and displayed the notice, the export/ranking run
passed **43 tests** in 123.22 seconds (exit 0).

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py -k standalone
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py tests/test_ranking.py
```

The real site rebuild exposed a second fact-overlay case: legacy frozen records
can lack IDs. The first correction keyed only by ID and failed with
`KeyError: 'id'`. Parameterizing
`test_citation_export_preserves_distinct_facts_with_the_same_facet` to omit IDs
produced **1 failed, 1 passed, 6 deselected** (exit 1). Matching canonical fact
content, excluding only assurance fields, preserved both dated records and
made the combined citation export/surface run pass **21 tests** (exit 0).

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py -k distinct_facts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py tests/test_cite_only_surfaces.py
```

MCP could erase the citation warning when fitting a large complete decision to
its response budget. Both `mcp/test/cite-only.test.ts` cases failed with
`warnings: []` instead of `cite_only_not_machine_verified` (exit 1). The warning
now survives normal pruning and the minimal fallback. The complete MCP suite
passed **235 tests** in 12 files, and type checking passed (exit 0). Commands ran
from `mcp`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test -- --run test/cite-only.test.ts
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run typecheck
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
```

The first MCP attempt exited 127 because dependencies were absent. A later full
run had 234 passing tests and one schema-fixture failure: the standalone
ShownFact test needed the published `$defs` for its new citation reference. It
now uses the same pattern as the existing HardwareEstimate schema test.

A final legacy case used `benchmarks.benchmark_source` for a flat score list.
Those scores were already unverified, but their cite-only origin was undisclosed.
The parameterized `test_flat_score_source_citation_survives_exports_rank_and_model_page` produced
**1 failed, 1 passed, 8 deselected** (exit 1). Candidate, coverage, model export,
and page output now retain that citation, while structured evidence still
overrides the corresponding flat score. The final export/surface/ranking run
passed **59 tests** in 95.11 seconds (exit 0). No hash or date is fabricated for
legacy score records that never stored one.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py -k flat_score_source
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_exports.py tests/test_cite_only_surfaces.py tests/test_ranking.py
```

The final output-boundary commands, with red failures and the **135-test** green
run described above, were:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py -k benchmark_cli
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py -k failed_cite
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cite_only_retention.py tests/test_cite_only_redirects.py tests/test_price_reread.py tests/test_fetch.py
```

## Full-suite integration corrections

The first complete locked run returned exit 1:

```text
20 failed, 12158 passed, 9 skipped, 11 warnings in 1437.78s (0:23:57)
```

The full output is retained in `root/full-pytest.log`. Its failures grouped into
these concrete causes, all corrected without removing existing assertions:

| Red tests | Cause and correction | Green output |
| --- | --- | --- |
| `test_every_module_a_workflow_runs_has_its_imports_installed[chart-check.yml:check-evidence-charts]`; `test_every_imported_repository_module_is_vendored` | Source-registry loading reached the module-level HTTP client import in a data-only workflow. HTTP imports now occur inside Fetcher. The standalone report CLI's `pipeline.load` import is classified alongside its existing build-time imports. | 135 passed with source tests, 22.97s |
| Six tests in `test_snapshot_successor_vendor.py` | `write_rank` mock rejected `cited_facts`; its signature now accepts the explicit keyword and asserts the empty fixture mapping. Signature, successor, cleanup, vocabulary, and determinism assertions remain intact. | 23 passed, 3.38s |
| `test_export_versions_changed_shape_and_keeps_unranked_models`; `test_cli_report_is_explicit_in_json_and_text` | Ranking stubs rejected the added keyword. They now accept `cited_facts` explicitly; the CLI-format test stubs its new model-loader call, restoring its original isolation. | 131 passed, 2 skipped with public/export tests, 5.88s |
| Seven tests in `test_rendered_sources.py`; `test_finance_projection_links_to_its_retained_source_snapshot` | Fake responses omitted real Playwright URL/request-chain fields or urllib `geturl()`. Test doubles now supply those fields; production redirect behavior was not weakened. | 43 passed with retention/redirect tests, 19.38s |
| `test_verified_evidence_renders_apart_from_legacy_scores` | Its frontmatter-only fake omitted the new Model property. It now uses a real Model and keeps every verification-label assertion. | Included in the 131-pass public run |
| `test_each_reference_is_under_the_word_budget[api.md]` | New prose raised the API reference to 940 words. Detailed citation assurance moved to the rank reference; the API reference is 797 words, below its unchanged 800-word limit. | Included in the 131-pass public run |

Focused commands, all exit 0 on the final corrections:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_workflow_dependencies.py tests/test_worker_vendor_imports.py tests/test_decision_sources.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor_vendor.py tests/test_decision_vendors.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_192_research.py tests/test_rendered_sources.py tests/test_cite_only_retention.py tests/test_cite_only_redirects.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py tests/test_incomplete_evidence_ranking.py tests/test_relations.py tests/test_cite_only_exports.py tests/test_cite_only_surfaces.py
```

A compact reproduction of the two dependency guards recorded **2 failed,
44 passed** before correction in `root/red-dependency-guards.log`. One public
repair run started before the final prose edit and recorded **130 passed,
2 skipped, 1 failed** at 815 API words. The subsequent complete focused run
passed all 131 tests with two existing skips. The full-suite rerun uses the same
required four-worker command, without exclusions or changed assertions.

The final full-suite rerun at `f72a2721654c05950c93f19e611bc0bc599d3f66`
completed with exit 0:

```text
12178 passed, 9 skipped, 11 warnings in 1559.82s (0:25:59)
```

The 11 warnings come from unsigned decision-vocabulary fixtures in the CLI
snapshot tests. The full output is retained in `root/full-pytest-final.log`.

## Execution notes and limits

- The initial site build passed; a later integration build caught the ID-less
  export regression above. The final gate records the corrected build.
- `pipeline.agent_copy check` initially reported a stale
  `cli/modelspec/agent-bundle.json`. `pipeline.agent_copy write` regenerated it;
  the subsequent check passed. `python -m decision.schema` and
  `python -m api.worker.openapi` regenerated their checked-in schemas.
- Two full-suite launchers were stopped with exit 143 while waiting for the
  shared lock, with no pytest child running, to finish review fixes. No active
  test run or other session's process was interrupted.
- No live provider request, paid scrape, vendor speed probe, production deploy,
  production switch change, or private-data migration was observed or performed.
  New source tests use synthetic content. This does not establish behavior of a
  live publisher or third-party scraper beyond the simulated HTTP boundaries.
- Historical source copies and preexisting fact text, including old quote
  fields, are intentionally not deleted or reauthored. Their migration remains
  MODEL-409. Existing factual values may still be serialized by existing data
  workflows; no new source quotations are extracted from cite-only fetches.
- Older source references without a recorded retrieval time retain an explicit
  null date. No retrieval timestamp is inferred from verification dates.
- Frozen data, the 718 existing premier facts, ranking floors,
  `neutrality_commitment()`, and legal text were not edited.
- The browser UI was exercised by the web test suite, not a manual browser
  session. Local tests do not establish deployed behavior. The draft PR still
  requires independent review; no merge was performed.
- Full logs were retained locally under `tmp/model-411-execution/`, grouped as
  `root`, `retention`, `verification`, and `surfaces`. The red/green excerpts and
  commands above are the committed review evidence. Individual workers' test
  sets overlap; their counts must not be added together.
