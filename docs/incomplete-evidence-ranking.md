# Ranking with incomplete benchmark evidence (MODEL-34)

A ranking orders conservative profile scores only for models with measurements covering at least 50% of the profile’s benchmark weight and at least two benchmarks; every other model remains visible as unranked for insufficient evidence.

For a profile containing only one positively weighted benchmark, that one measurement suffices. The benchmark set stays fixed across candidates and filters. The coverage and count thresholds are product defaults, not statistical confidence levels.

## Problem and decision

Previously a missing benchmark added zero to the composite, which treated lack of evidence like poor measured performance. `_basis` examined only present inputs, so a frontier model with one verified result could receive a low numerical rank labeled `verified` despite missing 80% of the profile.

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

---

# Appendix: the prior analysis, and where the implementation departs from it

The design above was built without sight of the analysis below. The two were
written independently — the analysis on revision `50e1b68`, the implementation
on a branch that did not yet carry it — and they converged on the same core
answer: keep performance, coverage and provenance separate, represent the
unmeasured part of a profile as explicit bounds, and refuse to give a model a
numeric rank its evidence cannot support.

They differ on one substantive point, and it is not resolved.

**The analysis says do not sort by the lower endpoint.** Its words: lower-endpoint
sorting "would largely restore the present coverage penalty". It recommends
instead a strict-dominance partial order — assert that A beats B only when
`L_A > U_B`, and otherwise report "order unresolved" — with no numbered league
table at all.

**The implementation does sort by the composite lower bound**, and produces a
numbered ranking of the models that clear the coverage floor.

The case for what shipped: the eligibility floor changes what the sort means. The
analysis's objection is that a lower-bound sort punishes a model for having gaps.
That is true when everything is sorted together, but only models covering at
least half the profile across at least two benchmarks are ordered at all, so the
sort runs over a set whose coverage is comparable by construction. Models the
objection is really about are not ranked low — they are not ranked.

The case against: "comparable by construction" is doing a lot of work at a floor
of 0.50. Two models at 51% and 99% coverage are ordered against each other, and
the one with more gaps still carries a smaller lower bound for that reason alone.
The analysis's strict-dominance relation would decline to order that pair. What
shipped is a weaker, more usable claim than what was recommended, and the
question of whether it is *too* weak is open.

Also unaddressed by the implementation: the analysis found that **capability
tiers explain 14.18 points of the 34.81-point gap** in the motivating case,
against 20.72 from benchmarks. Capability tiers have no provenance model at all.
Fixing the benchmark component, which is what shipped, leaves a substantial part
of the evidence problem untouched.

The analysis follows in full.

---

## Ranking with incomplete evidence — analysis and recommendation, 2026-09-09

Recommendation, 2026-09-09. Analysis of repository revision `50e1b68`; no ranking behavior is changed by this document. The figures below describe the local catalogue, not a fresh verification of the external benchmark publications.

**Replace the default total leaderboard with an evidence catalogue that supports partial comparisons.** Keep performance, profile coverage, and evidence provenance separate. Represent the unmeasured part of a profile with explicit bounds. State that one model scores higher only when that conclusion survives every allowed value of the unknown results, or when the claim is explicitly confined to a common, compatible measurement set. Otherwise say “order unresolved.” Do not turn coverage or verification into performance points.

GPT-6 Astra and Claude Opus 4.6 should appear in the same searchable catalogue, **but not in the same numbered performance ranking on their current evidence**. Neither should receive a replacement rank. A reader should see what is measured, what remains unknown, and why an overall comparison is unavailable. The purpose is to stop claiming more than the evidence supports, not to make the better-documented model win.

The current implementation makes two separate judgments look like one. In [pipeline/ranking.py](../pipeline/ranking.py), `score` sums weighted normalized benchmark results, skips missing results, then multiplies the sum by 0.40. It also adds capability, cost, context, and type components. `rank` sorts that composite point score. The existing `evidence_basis` and `verified_contributions` fields disclose provenance but do not constrain the ordering. A “verified” label refers to the contributing benchmark records; it does not establish full profile coverage or verification of the other score components.

I reproduced the reported ranks by loading all model cards with `ModelCard.from_yaml_file`, deriving the in-memory graph with `derive_graph`, building candidates with `build_candidates`, and calling `rank(..., "agentic", limit=len(candidates))`, without hardware or open-weight filters and with the default cost weight. This exercise did not write generated rankings.

| Current local result | GPT-6 Astra | Claude Opus 4.6 |
| --- | ---: | ---: |
| Combined distinct benchmark scores on card | 7 | 78 |
| Benchmarks contributing to agentic profile | 3 | 6 |
| Contributing benchmarks with verification records | 3 | 0 |
| Profile weight covered by any recorded scores | 20.01% | 67.99% |
| Profile weight covered by verification records | 20.01% | 0% |
| Benchmark component of current composite | 4.68 | 25.40 |
| Capability component | 5.82 | 20.00 |
| Context component | 11.35 | 11.25 |
| Type bonus | 15.00 | 15.00 |
| Cost component | 0.00 | 0.00 |
| Current composite score and rank | 36.84; 162nd | 71.65; 1st |

Only profile-relevant results affect the benchmark sum; 78 versus 7 is not itself the scoring input. Astra contributes `aa_briefcase`, `automationbench_aa`, and `gdpval_aa`. Opus contributes `swe_bench_agent`, `tau_bench`, `swe_bench_verified`, `arena_elo_overall`, `terminal_bench`, and `ifeval`. These sets have no overlap. The benchmark component explains 20.72 points of the displayed gap, while capability tiers explain another 14.18 points. Fixing missing benchmarks alone would leave a substantial evidence problem in the composite.

The corpus count also needs a precise definition. Of 1,225 cards, 676 have an empty flat `benchmarks.scores` block, but Astra has seven records in `benchmarks.evidence`. After merging both sources as ranking does, 675 candidates have no benchmark scores; 844 have none relevant to agentic. The current `rank` function does not exclude them: other components can still produce a score. Only one card currently carries benchmark verification records. A new product should explicitly show models without usable benchmark evidence rather than suggest that their capabilities are zero, hide them, or call the sole verified model number one.

**The evidence unit must be a result, not a model badge.** An admissible result should identify the exact evaluated model, canonical benchmark and version, metric and unit, evaluation configuration, score, source and source kind, evidence date and date type, and completed review. The policy should distinguish a source-checked provider report from an independent evaluation, and both from independently replicated runs. Checking a published number does not replicate its experiment. Multiple benchmarks from one evaluator are not independent replications either.

This follows the existing [active catalogue evidence contract](superpowers/specs/2026-09-08-benchgraph-active-catalogue.md), including compatible protocols and the separation of publication, evaluation, and verification dates. Benchmark eligibility and model-result eligibility need separate checks: an active benchmark does not make every score on it trustworthy. For a current comparison, apply the contract's freshness rules explicitly; historical results remain available in a dated historical view. A missing date means unknown freshness, not demonstrated staleness. A card-level `benchmark_as_of: 2026-04` is insufficient to date or verify each Opus result.

Admissible source-checked provider reports can be included under the contract, but their source kind must remain visible on every relevant comparison, with a filter for independent evaluations. Unverified legacy numbers remain inspectable as claims awaiting verification. They cannot narrow the default evidence bounds. This is not an assumption that those numbers are false; it is a refusal to use them as established inputs. Adding any number of unverified fields must not improve a performance claim or evidence-qualified coverage.

For each profile, show weighted coverage in three mutually exclusive parts: admissible results, recorded but inadmissible results, and no recorded result. Give reasons for inadmissibility, such as missing provenance, incompatible configuration, or expired evidence. Also show benchmark counts, source kinds, dates, and the named gaps. Deduplicate aliases and repeated runs; several measurements of one benchmark do not earn several shares of its weight. “All three observed results source-checked; 20% of profile covered” is much clearer than “100% verified.”

**Use an evidence range for the full benchmark profile.** Let the profile have nonnegative weights `w_b`, with `W = sum(w_b) > 0`. Let `A_m` contain only admissible, profile-compatible results for model `m`. Under the declared normalization, each benchmark value `x_mb` lies in `[0, 100]`. Then:

```text
admissible coverage C_m = sum(w_b for b in A_m) / W
observed contribution L_m = sum(w_b * x_mb for b in A_m) / W
upper bound U_m = L_m + 100 * (1 - C_m)

Full benchmark-profile score is bounded by [L_m, U_m],
conditional on the accepted measurements and the declared profile.
```

Dividing by the full profile weight `W` defines a common 0–100 scale. It does not divide by the available weight. The current agentic weights actually sum to `1.0001`, due to rounding the three additions to `0.0667`; the illustrative calculation above accounts for that. An implementation must specify weight precision rather than quietly rely on exact equality to 1.0.

These endpoints quantify what the missing results could change. They are not imputed measurements: no missing result is saved as zero or 100, and neither endpoint is presented as the model's estimated score. Do not sort by the lower endpoint, upper endpoint, midpoint, or width. Lower-endpoint sorting would largely restore the present coverage penalty; midpoint sorting would silently assume a value for every gap; upper-endpoint sorting would reward ignorance. A confirmed zero, by contrast, counts as coverage and fixes that benchmark's contribution at zero.

Taking Astra's three agentic records as admissible under the current normalization gives approximately **11.7–91.7 out of 100** for the benchmark profile, with 20.01% coverage. This is a worked illustration conditional on those records and scale choices, not an interval around the current composite score of 36.84. Opus has no admissible result in the current card, so its formal bound is 0–100. The default display should say “No verified agentic evidence; performance unresolved” instead of drawing an apparently informative 0–100 performance bar. The same applies to cards with no relevant scores at all.

These are **bounds due to missing evidence, not statistical confidence intervals**. A frequentist confidence level concerns repeated sampling under a specified procedure, as described by [NIST's explanation of confidence intervals](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm). Seven different benchmarks are not seven interchangeable samples from agentic ability, and 78 unchecked numbers do not justify a smaller standard error. This range makes no claim about sampling error, evaluator bias, contamination, undisclosed scaffolding, or future deployment performance. Source verification alone cannot establish those quantities. If suitable run-level data and methods become available, report measurement uncertainty separately and account for dependence and joint coverage before making statistical aggregate claims; do not manufacture a “95% confidence” label from benchmark counts.

**Ordering should be a supported relation, not a compulsory position.** For the same profile version, evidence policy, assessment date, and compatible evaluation contracts, assert “A scores higher on this benchmark profile” only if `L_A > U_B`. Calculate this before display rounding. Every permitted completion of the missing entries then preserves the ordering. Where ranges overlap or merely touch, report “order unresolved”; overlap does not establish equality. With the same fixed assumptions, this strict relation is transitive, so it can support a partial order without inventing a complete league table.

Do not convert that partial order into numbered tiers, a count of pairwise wins, or a “top models” group. A model with no measurements cannot be ruled out by its 0–100 bounds; calling it undefeated or top tier would reward missingness. Show supported relationships in a selected comparison, and keep catalogue order neutral. More admissible evidence should narrow the feasible range, even when the new measurement is poor. Removing evidence may erase a conclusion, but must not create a stronger superiority claim. Changes to the profile or evidence policy can change conclusions and must be identified as such.

Shared evidence enables a different, narrower question. A comparison view should show benchmark rows only as directly comparable when model identity, benchmark version, unit, and evaluation conditions are compatible. Matching benchmark IDs alone is insufficient. Unknown compatibility produces a reason, not a match. If nothing overlaps, show “No shared compatible evidence” and the missing comparisons. Do not automatically build a score from each pair's intersection: A–B, B–C, and A–C would then answer different questions and could produce contradictory league-table ordering.

If users want a numeric ordering for a narrower task, allow a **named, fixed comparison panel** whose benchmarks, configurations, and weights are chosen before scoring, and shared by all participants. A panel can be a small subset of a full profile, so it does not require catalogue-wide complete coverage. A panel point score requires admissible results for every panel entry; missing participants remain visible as incomplete. Always identify the panel and its share of the parent profile. A one-benchmark panel can establish the ordering on that benchmark only. Changing selected models must not silently change the panel. This is a scoped comparison within the evidence catalogue, not a replacement overall leaderboard.

An absolute ban on comparing models without overlapping measurements is stronger than necessary for full-profile bounds: if valid bounds separate under a fixed common measurement contract, the weighted ordering follows even without a shared observed entry. Permit that mathematical conclusion, while explicitly noting the lack of a head-to-head measurement. Incompatible or undefined contracts cannot support it. In the Astra–Opus case there is neither shared contributing evidence nor separating admissible bounds, so both routes to an ordering are unavailable.

The default user experience should be concrete:

| Agentic catalogue entry | Evidence shown beside model name | Comparison status |
| --- | --- | --- |
| GPT-6 Astra | 3 source-checked independent-evaluator results; about 20% profile coverage; about 80% unmeasured; publications Sep 4–7, checked Sep 8 | Partial evidence; illustrative benchmark range 11.7–91.7; no overall rank |
| Claude Opus 4.6 | 6 relevant legacy scores covering about 68%; 0% verified coverage; per-result dates unavailable; 78 scores across the card | Verification needed; overall performance unresolved; no overall rank |
| Model without benchmark results | No recorded benchmark evidence; coverage 0% | No benchmark comparison available; no overall rank |

Keep all three discoverable using names and known task, hardware, license, and availability facts. Default to alphabetical catalogue order and label any user-selected sort, including coverage, as such. Evidence-state filters can help readers find reviewed results without creating quality tiers. Models measured only outside the selected profile should say that explicitly. Unknown constraint values also need visible treatment; a missing hardware or capability field should not silently become a factual rejection.

Selecting Astra and Opus would open the evidence matrix and say: “No supported overall ordering. No shared compatible agentic results in the current cards.” Readers can inspect the seven dated Astra records and the 78 Opus legacy claims, including their individual source limitations. The empty comparison outcome should suggest the actual research gap: verify compatible results on a fixed agentic panel. It should not fall back to legacy scores. In today's corpus, the global verified comparison view may contain no orderable pair at all. Showing one verified card does not establish a winner.

Do not carry the current composite into the new view as an authoritative “overall fit” score. The initial evidence comparison should concern benchmark performance; show cost, context, type, and capability claims separately with their own provenance and unknowns. This is a real product cost: users lose the present single-number quality-versus-price shortcut. A future overall utility comparison would need explicit user preferences and defensible treatment of every uncertain component, including capability tiers. Adding known-looking context and type points to benchmark bounds would not make undocumented capability assessments reliable. This document proposes that future behavior but implements none of it.

The alternatives make weaker promises. Adding a coverage column while retaining rank 1 and rank 162 leaves the strongest visible claim unchanged. Ranking by available-weight averages rewards selective reporting. Mean imputation and shrinkage estimate missing values through assumptions the catalogue has not established. Verification multipliers confuse the truth of a source attribution with a measured level of performance. Separate verified and unverified leaderboards still manufacture order within each group, and a verified-only list would currently crown a single card. Requiring full coverage of every profile discards useful partial evidence. Bounds plus explicitly scoped comparisons retain that evidence without any of these shortcuts.

The costs are substantial. Ranges will often be broad and comparisons unresolved. A model with one excellent result will remain available but will rarely support a general recommendation. Users accustomed to a best-model answer must choose a narrower panel, gather more evidence, or make their own decision under uncertainty. Review capacity becomes a bottleneck, and coverage will reflect which providers and evaluators the project has researched. Source concentration, correlated benchmarks, and unsuitable profile weights remain design risks even after missingness is represented honestly. More elaborate presentation and machine-readable statuses are required. These are acceptable costs for a project whose claim is evidence quality; a precise unsupported rank is not a substitute for research.

Before implementation, verify the following:

1. **Result admissibility and review lineage.** Audit the seven Astra records against their cited publications and approval ledger, evaluated variants, dates, units, and configurations. Inspect Opus claims individually rather than infer that an undated block is false. In [schema/card.py](../schema/card.py), version and configuration can be empty, and a `verified_at` field does not itself demonstrate reviewer approval. In `build_candidates`, merely appearing in `benchmarks.evidence` marks a result verified and later records overwrite earlier ones by benchmark ID. Establish an explicit admission and conflict-resolution rule; do not choose the best score from incompatible runs.
2. **Normalization and measurement contracts.** Validate bounds, direction, saturation, aliases, and units for every weighted benchmark. `_normalize_benchmark` in [api/ranking/engine.py](../api/ranking/engine.py) clips to declared ranges and guesses a 0–100 scale for unknown IDs. The evidence records describe some AA values as normalized Elo percent; check what that permits us to compare. A numerical bound on this clipped index is not a bound on real-world ability. Verify the model-dependent max-reasoning configurations and disclose the lack of compute matching.
3. **Profile scope and eligibility.** Audit effective weights after `_apply_verified_additions`, their precision, duplicated task families, evaluator concentration, and treatment of benchmarks absent from the active catalogue. Do not remove unavailable benchmarks and renormalize separately for each model. A common profile revision may be needed, but must be named and dated, with results recalculated under that explicit revision. Confirm the rolling freshness policy and historical-view semantics against the accepted contract.
4. **Practical usefulness.** Measure admissible coverage and compatible overlap per profile and model type across the full corpus. Confirm how many pairs are resolvable and which fixed panels would answer useful questions. Do not lower review standards or pick coverage thresholds merely to fill a leaderboard. Present the sparse outcomes to users and check that “unresolved” is understood as uncertainty rather than low performance or a tie.
5. **Every consumer of ranking data.** Inventory the pipeline, graph-backed API, CLI, precomputed top-25 export, and browser scoring. The graph ingestion in [schema/graph.py](../schema/graph.py) currently reads the flat score block, while pipeline candidates merge evidence records; [web3d/downselect.v2.html](../web3d/downselect.v2.html) calculates its own composite. Confirm deployed paths and preserve result provenance through all of them. Existing score-only consumers must not silently sort a bound or truncate away models awaiting evidence.
6. **Behavioral checks for a later implementation.** Check that confirmed zero differs from missing, adding unverified results changes no admissible bound, irrelevant benchmarks change no profile coverage, and removing admissible evidence cannot create a stronger superiority claim. Exercise no-evidence cards, one-benchmark panels, mixed sources, stale and incompatible records, aliases, conflicts, rounding, and disjoint evidence. Check that changing a comparison participant does not change its panel. Review existing tests that require rankings or encode today's evidence distribution; successful migration must permit empty comparative results.

The implementation seam should be one evidence-comparison module shared by callers. Its interface should take a versioned profile, dated evidence policy, and attributable result records, and return coverage, bounds, admissibility reasons, and supported comparison relations. Presentation adapters should render these conclusions rather than independently reconstruct them from flat scores. A later rollout can add those outputs, verify their behavior on frozen snapshots, and then explicitly migrate the default catalogue and its clients. This recommendation authorizes no formula edits, data promotion, regenerated rankings, or deployment.
