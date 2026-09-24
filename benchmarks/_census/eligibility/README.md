# Evidence-first benchmark downselection

Current session ownership and startup steps are in [the September 9 ModelSpec/BenchGraph handoff](../../../docs/superpowers/plans/2026-09-09-modelspec-benchgraph-handoff.md).

This directory holds reviewed eligibility evidence, not benchmark articles. The accepted policy is in [the active catalogue specification](../../../docs/superpowers/specs/2026-09-08-benchgraph-active-catalogue.md).

## Current state

Current totals in `current-report.json` are **0 active, 1 alias and 5 unverified records**. No benchmark is catalogue-active: no remaining evidence record has a qualifying, dated, attributable frontier/open result pair. The reference set in `reference-models.json` is empty, which fails closed.

Records whose results came from sources whose terms do not permit this project's use were removed on 2026-09-24 (MODEL-117), together with the reference models that existed only for them. Git history keeps the earlier records.

The pilot assessed on September 8, 2026 left these dispositions:

| Disposition | Count | IDs |
| --- | ---: | --- |
| Active | 0 | |
| Alias | 1 | `obqa` → `openbookqa`; preserve main/fact evaluation configurations |
| Unverified | 5 | `livebench`, `openbookqa`, `openml_benchmark`, `openml_benchmarks`, `swe_together` |

This is not a census-wide acceptance-rate estimate. Unassessed discovery candidates are not included in these records.

See `pilot-research.md` for the provisional source ledger and `pilot-report.json` for the mechanically checked dispositions. `reference-models.json` records current model membership; `evidence/*.json` records results and independent reviews. `source-fingerprints.json` records public response hashes and retrieval times without redistributing full source bodies; retrieval is never the result date. `batch-004-research.md` records unresolved result-date evidence for LiveBench and SWE-bench Pro; it remains provisional and requires independent review before admission.

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

The latter writes `benchmarks/_census/next_batch_eligible.json`, selecting only active IDs and excluding already written pages. Missing or invalid inputs fail closed; expired evidence yields no active selection. There is no census fallback. The original `next_batch.json` and legacy run queues are preserved.

Run focused checks:

```sh
python3 -m pytest tests/test_benchmark_eligibility.py tests/test_eligible_batch.py tests/test_eligible_runner.py -q
```
