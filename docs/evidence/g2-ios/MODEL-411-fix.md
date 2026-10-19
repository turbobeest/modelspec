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


## Round 2 — REV-840 changes

Review baseline: `3b2745368523dfe64f1ead318e1376876b406b9f` (PR #840).
Original feature base: `bbfa93be5eed392878a2af0d709ca6e774302c5c`.
All round-1 results above describe that round only. This section supersedes its
writer inventory and decision-warning scope. Work stays on
`model-411-cite-only`; PR #840 remains a draft.

### Defects and regressions

The watcher now applies the same host policy as CopyStore to direct URLs and
all observed redirect origins. Restricted responses bypass normalization and
classification. State contains only URL, redirect URLs, hash and fetch time;
there is no source `.txt`, report export, extracted change snippet or drafter
input. Reused known cite-only state/export/report/manifest artifacts cannot
revive retained text. Cleanup is limited to URL-keyed generated artifacts.
Ordinary output and unmapped historical artifacts are preserved.

The URL matrix covers x.ai, docs.x.ai, sub.docs.x.ai, www.perplexity.ai,
uppercase, trailing dot, port, redirect to x.ai, and an ordinary control. Real
urllib redirect handling is exercised with a synthetic HTTPS transport,
including ordinary → restricted → ordinary. Firecrawl origins and HTTP-to-
Firecrawl fallback histories are covered. All network fixtures are offline.

The decision warning now follows cited facts actually used by this answer:
shown facts, ranking inputs, and filter operands affecting admission or
elimination. Whole-catalog scans and promotion of broad row warnings are gone.
Row warnings retain their previous scope. The citation notice in the summary
and must-mention list starts “This answer uses cited facts.” Tests cover none/summary/full, bounded answers,
short-circuit predicates, provider/class exclusions, retired candidates,
computed prices, soft penalties, hidden returned facts and ranking inputs
outside the displayed limit.

The reviewer's exact `lab/plain` probe has a contradictory expectation in the
round-2 request: it removes `lab/cited` using that model's cited context limit.
That meets the explicit rule requiring a warning for cited eliminations. The
implementation follows that rule. The exact probe still warns; the no-warning
regression selects the ordinary class/provider before any cited predicate can
affect a candidate. An optional clarification was requested; no contrary
direction was received during execution. This is an explicit interpretation,
not a claim that the exact original filter probe now has no warning.

Ordinary-host scope is restored: `docs/api.md` is byte-identical to the original
base; comparison provenance is emitted for known facts, with a narrow explicit
citation exception; the contract again says “known provenance”; and benchmark
provider failures again use `str(payload)[:300]`. Pricing again invokes the
Firecrawl CLI with the existing wait/main-content options and credential/credit
behavior. Direct restricted hosts fail before subprocess invocation. The single
CLI call returns JSON to memory so all reported origins can be checked before
writing its exact markdown. There is no second scrape, HTTP preflight, Python
key resolver, credit guard or benchmark hash-cache write.

The CLI output-routing flag was checked against installed firecrawl-cli 1.23.3:
`--json` formats stdout and is not the billable JSON extraction format. With no
output path, the output helper writes no page file. Its interaction metadata
contains only scrape ID, URL and creation time. No live scrape was run.

The repo-wide audit found additional source-to-write gaps. Census search caches
now discard restricted titles, descriptions and markdown; replay uses the same
guard. Census excerpt and licence readers refuse restricted content before
parsing or writing. Board and local-memory collectors no longer lose redirect
provenance before creating quoted projections. Legacy urllib excerpt readers
now share a retention-aware opener that refuses direct, intermediate and final
restricted origins. The benchmark HTTP cache instead follows the chain in
memory, retains its origins and writes only citation metadata. Its ordinary
cache and transient body behavior remain intact.

### Red-first and focused evidence

Python: 3.14.4; pytest: 9.1.1; Node: v22.22.3; npm: 10.9.8.
All commands run from `/Users/terbeest/dev/worktrees/model-411-cite-only` unless
a subdirectory is stated. Test commands below use the exact prefix:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q
```

Each table argument list follows that prefix. Output is redirected as
`> tmp/model-411-r2/<log> 2>&1`; exit codes come directly from the process
result, never from a pipe. Counts from overlapping suites must not be added.

| Arguments | Log | Exit | Result |
|---|---|---:|---|
| `tests/test_curation_cite_only.py` | `watcher/red-matrix.log` | 1 | 8 failed, 1 passed |
| `tests/test_curation_cite_only.py -k 'http_fetch or firecrawl'` | `watcher/red-fetch-origins.log` | 1 | 5 failed, 8 passed, 9 deselected |
| `tests/test_curation_cite_only.py -k 'stale or repeat or preserves_prior'` | `watcher/red-reuse.log` | 1 | 5 failed, 1 passed, 22 deselected |
| `tests/test_curation_cite_only.py -k draft` | `watcher/red-drafts.log` | 1 | 12 failed, 1 passed, 28 deselected |
| `tests/test_curation_cite_only.py -k proposal_gate` | `watcher/red-proposals.log` | 1 | 2 failed, 1 passed, 41 deselected |
| `tests/test_curation_cite_only.py -k preserves_prior` | `watcher/red-unrelated-state.log` | 1 | 1 failed, 43 deselected |
| `tests/test_curation_cite_only.py -k prior_manifest` | `watcher/red-prior-manifest.log` | 1 | 1 failed, 44 deselected |
| `tests/test_curation_cite_only.py tests/test_curation_loop.py tests/test_workflow_dependencies.py tests/test_writer_artifacts.py tests/test_cite_only_retention.py tests/test_cite_only_redirects.py` | `watcher/green-final.log` | 0 | 168 passed |
| `tests/test_cite_only_warning_scope.py` | `warnings/red-scope.log` | 1 | 11 failed, 4 passed |
| `tests/test_cite_only_warning_scope.py -k unused_hidden_citation_on_returned_row` | `warnings/red-hidden-returned.log` | 1 | 3 failed, 20 deselected |
| `tests/test_cite_only_warning_scope.py` | `warnings/green-scope-final.log` | 0 | 23 passed |
| `tests/test_cite_only_warning_scope.py tests/test_decision_filter.py tests/test_decision_optimise.py tests/test_decision_explain.py tests/test_decision_summary.py tests/test_decide_bounded.py tests/test_cite_only_surfaces.py` | `warnings/green-focused.log` | 0 | 247 passed; before final hidden-returned correction |
| `tests/test_cite_only_warning_scope.py tests/test_decision_explain.py tests/test_decision_summary.py tests/test_decide_bounded.py tests/test_cite_only_surfaces.py` | `warnings/green-final-consumers.log` | 0 | 163 passed on final warning implementation |
| `tests/test_cite_only_scope.py` | `scope/red.log` | 1 | 7 failed, 1 passed |
| `tests/test_cite_only_scope.py tests/test_cite_only_retention.py tests/test_fetch_pricing.py tests/test_fetch.py tests/test_model_comparison.py tests/test_cite_only_surfaces.py tests/test_api_docs.py tests/test_decision_contract.py` | `scope/green.log` | 0 | 389 passed, 2 skipped |
| `tests/test_cite_only_writer_audit.py` | `root/writer-audit-red.log` | 1 | 6 failed, 1 passed |
| `tests/test_cite_only_writer_audit.py -k provider` | `root/provider-licence-red.log` | 1 | 2 failed, 1 passed, 7 deselected |
| `tests/test_cite_only_writer_audit.py` | `root/writer-audit-final.log` | 0 | 10 passed, before intermediate-hop follow-up |
| `tests/test_cite_only_http_cache.py` | `root/http-cache-red.log` | 1 | 4 failed, 1 passed |
| `tests/test_cite_only_http_cache.py tests/test_fetch.py tests/test_cite_only_retention.py tests/test_cite_only_redirects.py` | `root/http-cache-green.log` | 0 | 52 passed |

The exact reviewer scope command also passed (1 test, exit 0):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider /tmp/rev840/test_probe_scope.py > tmp/model-411-r2/warnings/reviewer-probe.log 2>&1
```

It confirms old verification is null, citation status is cited, and the only
result `lab/plain` has no row warning; the decision warning reflects the cited
filter elimination described above. The original reviewer writer probes were
read, not blindly rerun: their pricing mock targets the former Python scraper
and could launch the restored real CLI. Equivalent assertions use safe local
fixtures in the committed tests.

Key defect-to-test mapping (names are in the command files above/below):

- Watcher retention and redirect provenance: `test_watch_retains_only_citation_metadata_for_restricted_origins`, `test_http_fetch_records_real_urllib_redirect_chain`, `test_firecrawl_watch_uses_every_reported_origin`.
- Reused state, exports and drafts: `test_export_independently_refuses_stale_cite_only_text_and_report`, `test_watch_repeat_preserves_cite_only_policy_and_removes_its_stale_exports`, `test_draft_page_refuses_cite_only_sources_before_prompt_or_file_write`, `test_proposal_gate_refuses_restored_cite_only_accepted_manifests`, `test_draft_cli_does_not_rewrite_cite_only_snippets_from_prior_manifest`, `test_state_guard_preserves_alias_origins_for_later_watch`.
- Warning scope: `test_unrelated_cited_candidate_excluded_by_class_does_not_warn`, `test_unused_hidden_citation_on_returned_row_keeps_only_row_warning`, `test_cited_filter_elimination_warns_even_when_only_plain_result_remains`.
- Ordinary-host scope: `test_ordinary_comparison_preserves_known_only_provenance`, `test_ordinary_pricing_scrape_uses_cli_without_python_credit_or_cache`, `test_ordinary_benchmark_scrape_preserves_provider_failure_message`.
- Census/licence writers: `test_census_search_retains_citation_without_restricted_snippets`, `test_census_aggregator_does_not_write_leads_from_cite_only_redirect`, `test_licence_download_refuses_cite_only_redirect_before_document_write`, `test_provider_licence_audit_does_not_derive_notes_from_cite_only_documents`.
- Projection and hop escapes: `test_board_redirect_cannot_retain_a_new_projection_hash`, `test_rendered_board_redirect_cannot_retain_projection_text`, `test_local_memory_redirect_cannot_retain_quoted_table`, `test_intermediate_cite_only_hop_is_refused_before_following`, `test_named_http_cache_respects_every_redirect`.

The remaining red-first cases and final focused follow-ups use the same prefix
and direct-exit convention:

| Arguments | Log | Exit | Result |
|---|---|---:|---|
| `tests/test_cite_only_collector_writers.py` | `scope/collector-red.log` | 1 | 10 failed, 1 passed; four sentinel writes in projections |
| `tests/test_cite_only_collector_writers.py -k 'intermediate_cite_only or ordinary_redirect_chain'` | `scope/collector-hops-red.log` | 1 | 11 failed, 11 passed, 11 deselected |
| `tests/test_cite_only_collector_writers.py -k 'rendered and (intermediate_cite_only or ordinary_redirect_chain)'` | `scope/collector-rendered-hops-red.log` | 1 | 1 failed, 1 passed, 33 deselected |
| `tests/test_cite_only_collector_writers.py tests/test_model_160_evidence.py tests/test_model_163_lineup_data.py tests/test_model_174_hardware_private.py tests/test_model_191_refinements.py tests/test_model_192_research.py tests/test_leaderboard_refresh.py tests/test_oll_leftovers.py tests/test_oll_v2_keys.py tests/test_cite_only_redirects.py tests/test_cite_only_retention.py tests/test_cite_only_writer_audit.py` | `scope/collector-hops-green.log` | 0 | 366 passed; before final rendered case |
| `tests/test_cite_only_collector_writers.py` | `scope/collector-final-green.log` | 0 | 35 passed on final collector implementation |
| `tests/test_cite_only_writer_audit.py` | `watcher/red-shared-urllib.log` | 1 | 3 failed, 10 passed |
| `tests/test_curation_cite_only.py -k alias_origins` | `watcher/red-alias-origins.log` | 1 | 2 failed, 45 deselected |
| `tests/test_cite_only_writer_audit.py -k standalone_cli` | `watcher/red-licence-cli.log` | 1 | 1 failed, 16 deselected |
| `tests/test_cite_only_writer_audit.py tests/test_curation_cite_only.py tests/test_curation_loop.py tests/test_cite_only_retention.py tests/test_cite_only_redirects.py tests/test_workflow_dependencies.py tests/test_worker_vendor_imports.py tmp/model-411-r2/watcher/test_secondary_redirects.py` | `watcher/green-shared-final-cli.log` | 0 | 185 passed |

The intermediate-hop reds reported `DID NOT RAISE ValueError` or found retained
source text; their ordinary redirect controls passed. The watcher alias red
showed sourceURL/final_url provenance disappearing from state before a later
read; all origin aliases now persist in resolved_urls. The standalone licence
red was `ModuleNotFoundError: decision.retention` without PYTHONPATH; repo-root
import setup restores its documented direct invocation. The test uses empty
stdin and a temporary working directory, with no fetch.

The final collector controls preserve HTTP headers, timeouts, payloads, ordinary
redirects and memo/rendered/OLL cache reuse. Existing Finance Benchmark result
assertions are unchanged; its mock now targets the shared reader boundary.
An early collector test setup omitted the synthetic Firecrawl key and raised
KeyError; it was corrected before the saved red run and production changes.

### Whole-repository writer audit

The [writer audit](MODEL-411-writer-audit.md) records the exact search, all 187
initial non-test writer hits, and path-by-path dispositions for shared readers,
curation state/reports/drafts, collectors, licence/census writers, enrichment,
copy/upload workflows, and metadata-only helpers. Every newly confirmed
programmatic source-to-cache/excerpt bypass was reproduced and guarded.

The audit does not claim that arbitrary external agent CLIs cannot persist
page text. `scripts/benchmarks/run_eligible.py` and agent-test harnesses save
external CLI transcripts; that runtime was not executed or certified. These
are explicitly listed as observation limits, not silently counted as guarded
source readers. Likewise, scraper checks can inspect only origin metadata the
service reports. No live service/browser cache was observed.

Known reused curation artifacts and restricted search rows are sanitized.
Historical CopyStore files, supplied local snapshots, authored quotations,
preexisting ordinary caches without origin metadata, and the 718 existing
premier facts remain the separate MODEL-409 migration. No frozen data, ranking
floors, neutrality terms, legal text, production switches or private data were
changed. Private workflows require a later engine-pin update before these
changes affect their runs; no private workflow/cache/artifact was run or
inspected live here.

### Round-2 complete gates

Final implementation SHA: `44f8ca7623edbc7ae4f4d2ad51205d43d3e6065b`.
The final evidence-only commit is reported in the executor's final marker;
no production or test changes follow this implementation SHA unless recorded
in a subsequent repair section below.

The generator and site/web checks below ran on the completed decision and
surface implementation; the later source-writer-only fixes do not alter their
inputs. The full suite runs on the implementation SHA above. Each process exit
was read directly. Tool versions were checked with `python --version`,
`python -m pytest --version`, `node --version`, and `npm --version` using the
pinned binaries noted above.

| Exact command | Exit | Result / log |
|---|---:|---|
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check` | 0 | Generated bundle current; no rewrite |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m api.worker.openapi --check` | 0 | OpenAPI matches implementation |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts` | 0 | No tracked generated changes |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist` | 0 | `root/site-build.log` |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec` | 0 | 0 findings; 5,366 files; `root/surface-lint.log` |
| `cd web` then `export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH` and `npm ci` | 0 | `root/web-ci.log` |
| Same web directory/PATH, `npm run build` | 0 | `root/web-build.log` |
| Same web directory/PATH, `npm test` | 0 | 57 files passed, 1 skipped; 900 tests passed; `root/web-test.log` |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/chart_check_pr.py --base bbfa93be` | 0 | nothing to check |
| `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base bbfa93be --head HEAD --branch model-411-cite-only` | 0 | data freeze: ok |
| `git diff --exit-code bbfa93be -- docs/api.md api/ranking/engine.py docs/legal tests/test_class_fit.py docs/cli-contract.md docs/policy-check-api.md` | 0 | Named protected/ordinary files unchanged |

Full suite command, with Node 22.22.3 first on PATH:

```sh
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > tmp/model-411-r2/root/full-pytest.log 2>&1
```

The full suite completed with direct exit **0** at the implementation SHA above:

```text
12317 passed, 9 skipped, 11 warnings in 2033.61s (0:33:53)
```

The 11 warnings concern unsigned vocabulary fixtures in the CLI snapshot tests.
The final active worker was observed using CPU while the parent waited; no test
was interrupted or excluded. Every started generator/build/test process has
exited. `git diff --check` passed. No source or test edits followed the tested
implementation commit; the remaining changes are this evidence and the writer
audit. The draft PR head is checked again after pushing the evidence commit.

Round-2 local logs are under `tmp/model-411-r2/{root,watcher,warnings,scope}`.
No live provider call, paid scrape, deployment, private-data edit, production
switch change, merge, or historical-source migration was performed. This work
is ready for renewed independent review, with PR #840 kept as a draft.
