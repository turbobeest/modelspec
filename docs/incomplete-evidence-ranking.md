# Ranking with incomplete benchmark evidence (MODEL-34)

A ranking orders conservative profile scores only for models with measurements covering at least 50% of the profile’s benchmark weight and at least two benchmarks; every other model remains visible as unranked for insufficient evidence.

For a profile containing only one positively weighted benchmark, that one measurement suffices. The benchmark set stays fixed across candidates and filters. The coverage and count thresholds are product defaults, not statistical confidence levels.

## Problem and decision

The requested problem write-up did not exist in this checkout when work began. This document records the reported defect and the implemented design. Previously a missing benchmark added zero to the composite, which treated lack of evidence like poor measured performance. `_basis` examined only present inputs, so a frontier model with one verified result could receive a low numerical rank labeled `verified` despite missing 80% of the profile.

The default now separates observed performance, coverage, and conservative ordering. We retain low-coverage models in a separate, complete unranked list, with null `rank` and `score`. A measured low performer retains a numeric score and rank. This does not promote GPT-6 Astra or assert that the models above it are actually better.

The user-facing explanation is: **We order models by a conservative score only when measurements cover at least half the profile and at least two benchmarks. Models with less evidence remain visible as unranked, alongside their observed results and coverage.**

## Why the simpler fixes fail

- Renormalizing the ordering over present benchmarks turns one lucky result into a full-profile claim and can inflate one evaluator’s capped share. We show that observed average descriptively, but never use it as the sorting score.
- Mean imputation invents average performance for an unmeasured model. We leave the estimate null when nothing is measured and retain a range of possible benchmark contributions.
- Intersecting benchmarks across candidates lets the worst-covered model redefine everyone’s profile. Our profile and weights do not depend on the candidate pool.
- Excluding sparse models from the answer hides frontier models. Our report retains every candidate that passes the caller’s constraints; `limit` applies only to ranked rows.

## Arithmetic and meaning

Let `w_b` be the fixed profile weight and `n_b` a present benchmark normalized to 0–100 by the existing ranges and directions. Let `W` be total positive weight, `A` present positive weight, and `M` missing positive weight.

- Weighted coverage is `A / W`. A measured zero counts as present. Null and non-finite values are absent; zero-weight benchmarks do not count. Negative or non-finite weights are rejected.
- `benchmark_estimate = sum(w_b * n_b) / A`, or null when `A = 0`. This 0–100 observed average is descriptive, not a prediction for the missing benchmarks.
- `benchmark_lower_bound = 0.40 * sum(w_b * n_b)`.
- `benchmark_upper_bound = benchmark_lower_bound + 40 * M`.
- Composite bounds add the existing capability, context, type, optional price, and (in the graph engine) hardware speed components, then clamp to 0–100 as before. These auxiliary components cannot make a model eligible.
- A model is rankable when `W > 0`, coverage is at least 0.50, and its present count is at least `min(2, positive benchmark count)`. Eligible models sort by the composite lower bound. Existing tie breakers remain, with model ID added to stabilize offline ties.

These are deterministic bounds on the effect of missing normalized benchmark inputs, **not statistical confidence intervals or bounds on real-world ability**. They hold other composite inputs fixed and do not quantify noise, evaluation contamination, provenance errors, or uncertainty in capability tiers. Overlapping ranges do not establish which model is better; the ordering is an explicitly conservative selection policy.

The lower-bound arithmetic deliberately equals the old zero-filled arithmetic. The change is the meaning and eligibility of that number: it is no longer presented as a full-profile point estimate, and insufficient evidence produces no rank. This avoids renormalizing Artificial Analysis’s 20% profile share. It also means that rankable legacy models can retain their scores and relative ordering.

`VERIFIED_INDEX_WEIGHT`, `_apply_verified_additions`, normalization ranges, profile weights, and tier values are unchanged. The shared evidence calculation and policy constants live in `api/ranking/engine.py`; `pipeline/ranking.py` imports them.

## Provenance

`evidence_basis` describes benchmark-input provenance, not certification of the composite or model quality:

- `none`: no usable weighted measurements.
- `unverified-legacy`: all usable measurements come from legacy card values.
- `mixed`: both reviewed and legacy measurements contribute.
- `partial-verified`: all present measurements are reviewed, but the profile is incomplete.
- `verified`: every positively weighted benchmark is present and reviewed.

`verified_benchmark_coverage` reports reviewed weight as a fraction of the entire profile, independently of `benchmark_coverage`. Reviewed card evidence continues to override the flat score for the same benchmark. The graph engine lacks this per-score provenance in its current query and does not claim verified provenance.

## Data and compatibility

Both `pipeline.ranking.rank_report(...)` and `RankingEngine.rank_report(...)` return:

- `ranking_status`: `complete`, `partial`, `unavailable`, or `empty`, computed before the ranked limit.
- `policy`: version, conservative ordering, minimum coverage/count, uncertainty meaning, and `limit_applies_to: ranked_only`.
- `ranked_count` and `unranked_count`, before truncation.
- `ranked`: numbered eligible rows ordered by conservative score, limited as requested.
- `unranked`: all insufficient-evidence rows in alphabetical display order, never numbered or sorted as if ranked last.

Rows include `rank_status`, `unranked_reason`, `benchmark_coverage`, benchmark counts, missing benchmark IDs, the observed benchmark estimate, and benchmark/composite bounds. Unranked `score` and `rank` are null; `unranked_reason` is `insufficient_benchmark_evidence`. For eligible rows, `score` is the composite lower bound, and the offline row’s `score_kind` makes this explicit. Existing `benchmark_score` is the lower-bound benchmark component in composite points, not the 0–100 observed estimate.

The list-only `rank(...)` methods return the ranked shortlist. Other models being unrankable is the expected catalogue state, not an error: `rank()` does not raise when `unranked` is non-empty. A caller that only reads the list gets a correct-but-partial ordering — never a fabricated total order, and never an exception on ordinary data. An empty list means either no candidates matched the filters (`ranking_status: empty`) or none of them had enough evidence to order (`unavailable`). Raising on that empty case would still 500 the HTTP surface for any profile with no rankable models; the honest answer is “nothing we can order,” which is a list. `rank_report()` is the companion that distinguishes those statuses and lists every withheld model. Ignoring the companion is allowed; it is how a caller opts into a partial list.

`IncompleteEvidenceError` remains defined and still wraps a full report as `.report`, for callers that want to impose a complete-ordering contract themselves. The library does not raise it from `rank()`.

`write_export` now writes `rankings.json` with `schema_version: 2.0` because each profile is a report rather than a flat list. `profiles.json` also exports the ranking policy. Consumers that can display absence should use the report shape and show ranked/unranked separately. `POST /api/v1/rank` calls `rank_report()`, returns the ranked models, and discloses `unranked_count` and `ranking_status` on `RankResponse`. `total` remains the length of the returned ranked shortlist (after `limit`). The `modelspec offline rank` CLI still calls the list interface and is wired separately.

## CLI

The report interface is available within the allowed files:

```sh
.venv/bin/python -m pipeline.ranking coding --limit 10
.venv/bin/python -m pipeline.ranking reasoning --limit 10 --json
```

It reads the working-tree model cards, performs no network or database calls, prints the ranked shortlist followed by an explicit alphabetical `UNRANKED` section, and emits version 2 report JSON with `--json`. It does not use the old CLI’s cached snapshot or implement its hardware/freshness options; Python callers can use `rank_report` with candidates from the snapshot and its existing filters.

The existing `modelspec offline rank` formatter lives outside the permitted edit scope and still calls list-only `rank()`. After this shim fix that call returns the ranked shortlist instead of raising, so the CLI will print a correct-but-partial ordering until it is wired to `rank_report()`. The separate legacy database CLI in `cli/modelspec/cli.py` computes its own scores without calling either ranking module and is unchanged.

## Before and after on the captured corpus

Both sides below use the same in-memory candidate snapshot from 1,225 working-tree cards, captured before implementation on 2026-09-09. Concurrent card edits therefore cannot explain the differences. No hardware filter or price override was applied. The baseline in this checkout is 230th for Astra in coding and 199th in reasoning, rather than the ticket’s reported 162nd.

### coding

| Position | Before model | Before score | After model | After lower bound | After coverage |
| --- | --- | ---: | --- | ---: | ---: |
| 1 | Claude Opus 4.6 | 73.11 | Claude Opus 4.6 | 73.11 | 80% |
| 2 | GPT-5.4 | 72.28 | GPT-5.4 | 72.28 | 80% |
| 3 | GPT-5.4 Pro | 72.28 | GPT-5.4 Pro | 72.28 | 80% |
| 4 | GPT-5.1 | 71.29 | GPT-5.1 | 71.29 | 80% |
| 5 | GPT-5 | 71.02 | GPT-5 | 71.02 | 80% |
| 6 | GPT-5 Pro | 71.02 | GPT-5 Pro | 71.02 | 80% |
| 7 | GPT-5.2 | 71.02 | GPT-5.2 | 71.02 | 80% |
| 8 | GPT-5.2 Pro | 71.02 | GPT-5.2 Pro | 71.02 | 80% |
| 9 | GPT-5.4 mini | 71.02 | GPT-5.4 mini | 71.02 | 80% |
| 10 | GPT-5.4 nano | 71.02 | GPT-5.4 nano | 71.02 | 80% |

GPT-6 Astra: **#230, score 25.57, basis `verified` → UNRANKED**, score/rank null, coverage 20% (one benchmark), basis `partial-verified`. Observed benchmark average 56.00/100; composite bounds [25.57, 57.57].

The top 10 and their numbers did not change. All ten have `unverified-legacy` benchmark provenance. The report contains 122 eligible models and preserves 1103 unranked models. Astra did not move up; its unsupported numeric position was removed.

### reasoning

| Position | Before model | Before score | After model | After lower bound | After coverage |
| --- | --- | ---: | --- | ---: | ---: |
| 1 | Claude Opus 4.6 | 70.65 | Claude Opus 4.6 | 70.65 | 72% |
| 2 | Gemini 2.5 Pro | 70.28 | Gemini 2.5 Pro | 70.28 | 72% |
| 3 | Gemini 2.5 Pro Preview 05-06 | 68.95 | Gemini 2.5 Pro Preview 05-06 | 68.95 | 72% |
| 4 | Gemini 2.5 Pro Preview 06-05 | 68.95 | Gemini 2.5 Pro Preview 06-05 | 68.95 | 72% |
| 5 | o3-pro | 68.64 | o3-pro | 68.64 | 72% |
| 6 | o3 | 68.48 | o3 | 68.48 | 72% |
| 7 | o3-deep-research | 68.48 | o3-deep-research | 68.48 | 72% |
| 8 | Claude Opus 4 | 68.39 | Claude Opus 4 | 68.39 | 72% |
| 9 | o3-mini | 67.15 | o3-mini | 67.15 | 72% |
| 10 | DeepSeek Reasoner | 66.89 | DeepSeek Reasoner | 66.89 | 80% |

GPT-6 Astra: **#199, score 31.42, basis `verified` → UNRANKED**, score/rank null, coverage 20% (one benchmark), basis `partial-verified`. Observed benchmark average 32.00/100; composite bounds [31.42, 63.42].

The top 10 and their numbers did not change. All ten have `unverified-legacy` benchmark provenance. The report contains 353 eligible models and preserves 872 unranked models. Astra did not move up; its unsupported numeric position was removed.

## Default still owned by the product owner

The owner should decide whether 50% weighted coverage plus two benchmarks is the right eligibility floor, and whether ordering by a conservative bound matches the product’s selection intent. These defaults prioritize avoiding unsupported strong claims; they do not establish that inherited legacy measurements are trustworthy. A provenance threshold, evidence freshness policy, or a different presentation for overlapping bounds is a separate product decision. No exception or manual boost for Astra is built into the algorithm.

## Validation

The regression first failed on a single perfect verified SciCode result receiving a numeric score of 23.0; it now produces null score and explicit unranked status. Tests cover real Astra evidence in coding/reasoning, a lucky sparse model with every auxiliary bonus, measured zero versus missing data, weighted coverage and count boundaries, zero-weight and non-finite inputs, stable profiles across candidate pools, missing-value bounds, the evaluator cap, provenance coverage, filters, both scoring paths, the list interface returning a partial shortlist, versioned exports, and CLI text/JSON behavior.

The exact requested command, `.venv/bin/python -m pytest -q`, stopped before running tests because pytest collected downloaded BIG-bench source from the census cache; that file imports the unavailable `bigbench` package. Exact tail:

```text
=========================== short test summary info ============================
ERROR benchmarks/_census/cache/grok-window-20260908/batch-066/google_BIG-bench_main_bigbench_benchmark_tasks_program_synthesis_test.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
528 warnings, 1 error in 0.49s
```

The failing cache file and pytest’s root discovery configuration are outside the allowed edit scope. This is not reported as a passing full-suite run. The repository-owned tests are also run separately with `.venv/bin/python -m pytest -q tests/`.

That complete `tests/` run passed. Exact final line:

```text
210 passed, 431992 warnings in 158.43s (0:02:38)
```

The warnings are Pydantic `model_fields` instance-access deprecations in `schema/card.py:781`. `git diff --check` also passed. No Git write commands were run, and changes from concurrent hardware/evidence work were left untouched.

The real-card report CLI was run with `.venv/bin/python -m pipeline.ranking coding --limit 10`. It printed the top ten above followed by the unranked section, including:

```text
  UNRANKED  GPT-6 Astra  coverage 20%, observed benchmark average 56.00/100, benchmark basis: partial-verified
```
