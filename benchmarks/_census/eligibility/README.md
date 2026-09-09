# Evidence-first benchmark downselection

Current session ownership and startup steps are in [the September 9 ModelSpec/BenchGraph handoff](../../../docs/superpowers/plans/2026-09-09-modelspec-benchgraph-handoff.md).

This directory holds reviewed eligibility evidence, not benchmark articles. The accepted policy is in [the active catalogue specification](../../../docs/superpowers/specs/2026-09-08-benchgraph-active-catalogue.md).

## Initial pilot, assessed September 8, 2026

Six purposively selected groups produced nine candidate records:

| Disposition | Count | IDs |
| --- | ---: | --- |
| Active | 1 | `automationbench_aa` |
| Alias | 1 | `obqa` → `openbookqa`; preserve main/fact evaluation configurations |
| Unverified | 7 | `automationbench`, `terminal_bench_v4_0`, `livebench`, `openbookqa`, `openml_benchmark`, `openml_benchmarks`, `swe_together` |
| Historical under the full mechanical gate | 0 | Some inspected evidence is old, but other requirements also remain unverified. |

This is not a census-wide acceptance-rate estimate. Unassessed discovery candidates are not included in these nine records. The model reference set is deliberately a two-model agentic pilot, not an exhaustive list of current models across all domains.

## Reviewed batch 002

The next six profiles passed independent source review using the fixed per-model chart embedded in AA's September 4 v4.2 release. Its dated chart supersedes the initially proposed undated live comparison values. Current totals in `current-report.json` are **7 active, 1 alias and 7 unverified records**. The active IDs are `aa_briefcase`, `aa_lcr`, `automationbench_aa`, `critpt`, `gdp_pdf_aa`, `gdpval_aa` and `scicode`. Reference membership now covers the relevant agentic, coding, long-context and scientific-reasoning domains for the same two models; it remains a limited seed reference set.

AA-Briefcase and GDPval-AA chart values are rounded normalized Elo percentages, not raw Elo. GDP.pdf uses AA's implementation. Exact versions and configurations remain in each result record. The source-derived `eligible-candidates.json` supplies candidate names to batch selection, which still recomputes eligibility rather than treating this list as perpetual approval. The seven pages have now completed source review, including three new pages (`aa_briefcase`, `gdp_pdf_aa`, `gdpval_aa`) and four repaired/reviewed drafts. They await integration; see Operational state below.

AutomationBench-AA qualifies through specifically attributed results published September 7 for GPT-6 Astra (max) and GLM-5.3 (max). Run dates are undisclosed. The record preserves the partial-credit scoring variant, held-out version and comparison configuration. Eligibility approves the profile's inclusion in the active set, not every claim in an existing article; article review remains separate.

See `pilot-research.md` for the corrected provisional source ledger and `pilot-report.json` for the mechanically checked dispositions. `reference-models.json` records current model membership; `evidence/*.json` records results and independent reviews. The coordinator independently opened the qualifying primary sources. The OpenCompass alias mapping received a separate Luna review. `source-fingerprints.json` records public response hashes and retrieval times without redistributing full source bodies; retrieval is never the result date.

## Commands

Recompute the current reviewed evidence at today's assessment date:

```sh
python3 scripts/benchmarks/downselect.py \
  --evidence benchmarks/_census/eligibility/evidence \
  --reference-set benchmarks/_census/eligibility/reference-models.json \
  --as-of "$(date +%F)" \
  --output benchmarks/_census/eligibility/current-report.json
```

Build a candidate authoring batch using today's eligibility, rather than trusting a saved report:

```sh
python3 scripts/benchmarks/next_batch.py eligibility/eligible-candidates.json 40 3
```

The latter writes `benchmarks/_census/next_batch_eligible.json`, selecting only active IDs and excluding already written pages. Missing or invalid inputs fail closed; expired evidence yields no active selection. There is no census fallback. The original `next_batch.json` and legacy run queues are preserved. The original pilot yielded no unwritten P2 selections. The expansion originally yielded three new-page candidates; all seven eligible pages now exist, so selection should not dispatch them again. This is not programme completion.

Run focused checks:

```sh
python3 -m pytest tests/test_benchmark_eligibility.py tests/test_eligible_batch.py tests/test_eligible_runner.py -q
```

## Operational state

**September 9 update:** the first seven-page curated batch has completed writing and source review. The reconciled result is `benchmarks/_census/cache/eligible-20260908/coordinator-status.json`; it verifies current eligibility and exact article hashes across the original Grok reviews and subsequent correction reviews. Three initial rejections were corrected and independently rechecked. SciCode's GLM-5.3 score was corrected from 56% to 59% in both the evidence and article; see [the transparent erratum](2026-09-09-chart-correction.md). AA-LCR's Grok reviewer produced no events during a prolonged startup stall, so its logs were preserved and a full independent Luna source review completed the work. These are reviewed drafts ready for integration, not published pages. The immutable original run status retains its earlier rejections; use the coordinator status for the reconciled outcome.

Verification batches 003 and 004 finished research before ownership transfer. `batch-003-research.md` proposes HLE/AA-Omniscience results; `batch-004-research.md` records unresolved result-date evidence for LiveBench/SWE-bench Pro. Both remain provisional and require independent review before admission. No ModelSpec research agents remain active in the originating DPF session. The new ModelSpec session owns further research and integration.

The legacy production supervisor remains suspended and its continuation controller is blocked by `QUALITY_AUDIT_PAUSE.json`; all twelve former Grok workers finished their current contexts. `SONNET_STOP` remains in place. Do not remove either hold to consume the old all-candidates queue.

The bounded replacement ran through `scripts/benchmarks/run_eligible.py`, with seven Grok slots and only the seven reviewed IDs above. Original run state is at `benchmarks/_census/cache/eligible-20260908/run-001/status.json`; its historical supervisor PID is in `eligible-20260908/supervisor.pid`. Each job records process PID/exit metadata in its `logs/` directory. Confirm live processes rather than treating an old status as current. The shared `cache/eligible-run.lock` prevents competing new runners; existing run directories cannot be replayed.

The new runner rechecks eligibility before writing, before independent review and after review. It snapshots existing pages, records the hash of each approved page, validates structure and leaves results at `ready-for-coordinator` or `needsattention`. No Git checkpoint, push, merge or deployment is automatic. A coordinator must recheck the approved hash and current eligibility before accepting a page, and independently assessed eligibility does not approve the article's full contents. A SIGTERM or SIGINT sent to the supervisor PID alone drains current tasks and prevents subsequent assignments. Do not signal the whole process group when requesting a soft stop.

Verification batch 002 completed source research and independent record review for AA-Briefcase, GDPval-AA v2, GDP.pdf, SciCode, AA-LCR v1.1 and CritPt. An aggregate index result cannot qualify every component; the dated chart supplies the actual per-component pairs.

The bounded dispatcher now enforces eligibility. Coordinator checkpoint admission and serving integration remain to be completed; the old automatic checkpoint controller stays disabled. The serving implementation must consume eligibility for its default active listing. No deployment, merge or publication occurred as part of this pilot. Focused checks including `tests/test_eligible_runner.py` pass 35 cases, covering soft stop, expiry before review, review invalidation after page mutation, concurrency, provenance and input handling.

The [durable review bundle](handoff/2026-09-09/review-bundle.json) preserves the reconciled seven-page status, article hashes, and original/correction review records outside the ignored cache. Recheck hashes and current eligibility before integration.
