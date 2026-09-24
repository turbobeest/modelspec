# Ranking v2: a benchmark-agnostic capability model (MODEL-129)

*Design spike, phase 1. Written 2026-09-24. No production change: the scorer,
the profiles, the floors and every contract are untouched. The prototype and
its backtests are in [`research/ranking_v2/`](../../research/ranking_v2/).*

> Jamie: "from a pure data science perspective, our algorithm doesn't play. We
> should never lock in specific benchmarks for weighting anything. Lesson
> learned. We need a better algorithm."

This document proposes that algorithm, fits it to our real data, and tests it
against four gates: held-out prediction, a release-week replay of every 2026
flagship, face validity, and the independent audit's twenty questions. It ends
with what it would change in the contracts, where it runs, the plan for phases
2–3 and the decisions that are Jamie's.

**Result, in one paragraph.** A hierarchical item-response model — a general
ability plus one factor per *tagged domain*, a per-benchmark link that
saturates, learned noise, learned source offsets and empirical-Bayes priors —
fits our purged, sourced evidence plus the Arena dataset in about 3 seconds of
pure Python. It predicts held-out scores better than every baseline in both
data views (RMSE 0.26 item-sd against 0.40 for the best low-rank baseline on
sourced data; 0.40 against 0.43 with the flat block), with 80% intervals that
cover 92–96% of held-out values. Replayed at release + 7 days, it places 30 of
32 2026 flagships in coding (v1: 0 of 32), and for flagships with a month of
later evidence its release-week position is within three places of today's
for 18 of 23. Its September coding top 5 is Opus 5.5, Mythos 5.1
(provisional, one provider number), GPT-6 Astra, Fable 5.1 and Opus 5; chat is
Fable 5, Opus 4.6, Fable 5.1, Opus 4.7, Gemini 3.8 Flash. On the independent
audit's 20 questions its top three share 18 of 57 reference models against
v1's 6, it puts a reference model first 7 times in 19 (v1: 4), and it abstains
with a named evidence gap where the audit's references rest on data we do not
hold (MTEB v2, speech). **Recommendation: adopt it, fitted at build time on
sourced evidence, and treat the flat block as legacy.** The weakest part is
not the model but the data: after the MODEL-117 purge, independent reasoning
evidence nearly disappears, so reasoning answers are honest but mostly
`provisional` until MODEL-113 ingests independent boards.

---

## 1. Why v1 fails

v1 (`api/ranking/engine.py`, `pipeline/ranking.py`) scores a model against a
*profile*: a hand-written list of benchmarks with hand-set weights, normalised
through hand-set `BENCHMARK_RANGES`. A model is ranked only if it holds at least
0.50 of the profile's weight (`MIN_BENCHMARK_COVERAGE`) and two of its
benchmarks, and ranked models are ordered by a conservative lower bound in
which a missing benchmark counts as zero. Up to 60 more points come from things
that are not measurements of the task: capability tiers (20), a type-position
bonus (15), context length and price.

Every part of that fails in the same direction once labs move to new
benchmarks, and they have:

| Mechanism | What happens (MODEL-108 audit; independent audit, 2026-09-24) |
|---|---|
| Fixed benchmark lists | Coding still asks for HumanEval, Aider, LiveCodeBench and Terminal-Bench 1.0; nobody runs them on new models. Opus 5.5 holds SWE-bench Pro, Terminal-Bench 4.0 and HLE and has **0%** coding coverage. None of ten recent releases is ranked in any of 51 profiles. |
| Coverage floor | A perfect backfill clears 0.50 in 1 of 51 profiles. |
| Lower-bound ordering | Missing = zero, so field density wins: Gemini 2.5 Pro (March 2025) is coding #1 on a *lower* observed benchmark estimate than Opus 4.6. |
| Fixed normalisation bounds | GPQA 81 and 96 both map to 100; Arena 1401 and 1508 both map to 100. |
| Non-benchmark points | New flagship cards earn 4.5 of 20 capability points against 20 for old leaders (High 4). |
| No class filter | `rag` returns embedders for a generator question (Critical 3). |
| Flat legacy block | Sibling copies: GPT-4.1 nano carries GPT-4.1's SWE-bench score (Critical 2). |
| Flattened evidence | The answer cannot say which number, version, harness, source or date drove it (High 5). |

The root cause is one design choice: **the benchmark set is an input**. Every
fix inside v1 (new lists, new weights, new bounds) re-commits to a set that
will be stale by the next launch cycle. v2 removes the set.

## 2. Options compared

Benchmarks are noisy, partial measurements of a small number of latent
capabilities. Every candidate below takes that view; they differ in what they
assume about the latent structure and the measurement.

| Model | What it assumes | For | Against | Verdict |
|---|---|---|---|---|
| v1 weighted composite | Fixed lists, fixed weights, fixed bounds | Transparent arithmetic | Everything in §1 | Retire |
| Unidimensional IRT (2PL/3PL), one ability *g* | One latent ability; each benchmark has a difficulty and a discrimination; bounded scores saturate through a logistic link | Learns weights; handles missing data; saturation is built in | Cannot say "better at coding than at chat" | The backbone of v2 (`v2_general_only` in §9) |
| Low-rank matrix factorisation / PCA ("observational scaling laws", Ruan et al. 2024) | Z ≈ U V′ with K free factors on per-item standardised scores | Strong predictor; learns loadings freely | Factors are unnamed and rotate between builds; linear in logits, so a saturated benchmark keeps full weight; no uncertainty, no source model | Baseline (`lowrank_k1..3`) |
| Exploratory multidimensional IRT | K free factors with IRT links | Flexible | Unidentified with this sparsity (most models have < 10 observations); factors still unnamed | Rejected |
| Bradley–Terry on Arena battles | Pairwise preference → strength | Principled for Arena | Only one source; the battles are not published per snapshot; Arena ratings *are* BT fits already | Used as a measurement: an Arena rating enters as a Gaussian observation of BT strength with its published interval |
| Full hierarchical Bayes (MCMC) | Everything below, sampled | Exact posteriors | Needs numpy/Stan; minutes to hours; not reproducible in a Pyodide Worker | Deferred; the MAP + Laplace fit below is its tractable version |
| **Chosen: hierarchical bifactor IRT** | g plus one factor per *tagged domain*, testlets for same-run subtask families, per-benchmark links, learned noise and source offsets, empirical-Bayes priors, MAP + Laplace | Named, stable factors (from tags, not rotation); learns every weight; saturation, staleness, source kind and missingness are all in the likelihood; pure Python, 3–15 s fit | Tag quality matters; the Laplace intervals are conditional approximations | **Proposed** |

## 3. The model

### 3.1 Latent structure

Each model *m* has a general ability g_m and a deviation s_{m,d} for each
domain d. Each benchmark (an *item*) b carries one or two domain tags T_b and
measures the blend

    θ_{m,b} = g_m + (1/|T_b|) Σ_{d∈T_b} s_{m,d}  [+ u_{m,f(b)} if b is in a testlet family f]

Testlet factors u_{m,f} absorb what the 57 MMLU subjects (or MultiPL-E's
languages, or MTEB's task groups) share *because they were one run*: the
harness, the prompt format, the answer extraction. Without them one run of 57
correlated items would count as 57 independent pieces of evidence.

A **use case** is a mix π over domains, and its score is

    U_m = g_m + Σ_d π_d s_{m,d}

### 3.2 Measurement: one link per kind of score

* **Bounded percentages** (SWE-bench, GPQA, HLE, …) — a 3PL item on the
  aggregate score:

      E[y_{m,b}] = c_b + (1 − c_b) · σ(λ_b θ_{m,b} + β_b + δ_k)

  c_b is the page's `random_baseline` (GPQA 25%), λ_b the discrimination, β_b
  the easiness, δ_k the offset of the source kind k. The fit is on the
  probability scale, with variance

      Var[y] = τ_b² + y(1−y)/N_b + κ_k² + slope² · Var(λ_b θ + β_b)

  τ_b² is the item's learned residual noise (how well it agrees with everything
  else), y(1−y)/N_b the binomial sampling noise of an N_b-question benchmark,
  κ_k² the learned extra scatter of the source kind, and the last term
  propagates the item's own parameter uncertainty so a benchmark seen on three
  models cannot pin anyone tightly.
* **Ratings** (Arena Elo, the Arena agent score) — linear on the item's
  standardised scale, E[y] = λ_b θ + β_b, with the published 95% interval as
  measurement error.
* **Durations** (METR time horizon) — linear in log minutes.

### 3.3 What sets a benchmark's weight

Nothing is configured. A benchmark's influence on a model is its Fisher
information,

    I_b(θ) = (λ_b · slope_b(θ))² / Var[y]

times a recency factor and a design effect. It is large when the benchmark
discriminates (λ), agrees with the rest of the evidence (small τ), has many
questions (large N), comes from a source that scatters little (small κ), and —
the saturation property — when the model is *on the steep part of the curve*.
At the frontier of a saturated benchmark the slope (1−c)σ(1−σ) → 0, and so
does its weight (§5.1).

### 3.4 Priors and fitting

g ~ N(0, 1); s_{m,d} ~ N(0, σ_d²) and u_{m,f} ~ N(0, σ_f²), with σ learned by
empirical Bayes; λ_b ~ N(family mean, 0.5²) (0.2² for thinly anchored items,
§4.3); β_b weak; δ_k ~ N(0, 0.5²).

The fit is MAP by alternating Gauss–Newton with backtracking over models (each
a vector of at most ~14 numbers), items (λ, β) and source offsets, in two
stages: 30 sweeps with moment (empirical-Bayes) updates of τ_b, κ_k and σ_d,
then with every variance frozen so the objective is fixed and the iteration
converges (tolerance 10⁻³ on every model parameter). Each sweep also solves
exactly for the two directions the likelihood cannot see — a common shift and
a common scale of all abilities — which block updates otherwise crawl along;
without that step the first prototype had not converged after 400 sweeps.
The result is then published on a fixed unit: g has mean 0 and sd 1 over the
models with at least three observations. Uncertainty is the Laplace
approximation per model: Cov_m = (Jᵀ W J + P)⁻¹. A domain in the mix with no
evidence for this model adds its prior variance (π_d σ_d)² to Var[U_m]: missing
evidence widens the interval; it never scores zero.

An item's residual noise τ_b has a prior of 4 percentage points worth ten
models: a model-by-benchmark interaction of a few points is normal among
frontier benchmarks, and an item observed on seven models cannot show it is
smaller. Without that prior, one provider number on a thin benchmark pinned a
model to ±0.15.

Everything is pure Python (`research/ranking_v2/model.py`, no numpy): small
dense Cholesky solves only.

## 4. Domains by tag

### 4.1 The tag

Proposal: benchmark pages gain a `domains:` field, one or two values, the first
primary, from a closed vocabulary:

`coding`, `agentic`, `reasoning`, `math`, `knowledge`, `chat`, `vision`,
`long_context`, `retrieval`, `speech`, `safety`, `multilingual`.

A tag says what a benchmark measures, never how much it matters. The prototype
derives tags without touching any page (`research/ranking_v2/domains.py`): a
page's own `domains:` if present (none yet), then a short override table (e.g.
SWE-bench → coding + agentic, Terminal-Bench → agentic + coding, GPQA →
reasoning + knowledge, MathVista → vision + math), then the page's existing
`category`. The Arena *text* boards are tagged `chat` plus their prompt slice
(coding, math, hard prompts → reasoning, expert → knowledge), so "people like
talking to it" enters the coding factor only where coding-specific evidence
agrees. The WebDev, vision, agent, search and document boards are preference
about a task's *output* and are tagged with the task alone. An earlier
prototype tagged WebDev `coding` + `chat`; WebDev's tight intervals then
carried most of the chat estimate, and the chat top 10 filled with coding
models that have no text-Arena rating at all. Tags are where a design like this
goes wrong quietly, which is why §14 asks who reviews them.

### 4.2 Use cases are domain mixes

| Use case | Mix | Hard filters |
|---|---|---|
| coding | coding .6, agentic .3, reasoning .1 | text-generator |
| agentic | agentic .6, coding .25, reasoning .15 | text-generator or actor |
| reasoning | reasoning .6, math .25, knowledge .15 | text-generator |
| math | math .8, reasoning .2 | text-generator |
| chat | chat .8, knowledge .1, reasoning .1 | text-generator |
| general | chat .3, reasoning .2, coding .2, knowledge .15, agentic .15 | text-generator |
| vision | vision .8, reasoning .2 | text-generator with image input |
| rag_generator | long_context .4, knowledge .3, chat .3 | text-generator, context ≥ 128k (request can raise it) |
| research_assistant | reasoning .4, agentic .3, knowledge .3 | text-generator |
| embedding | retrieval 1.0 | vectoriser |

The mixes are proposals of the same standing as today's floors: Jamie's. The
51 v1 profiles collapse into mixes plus filters; a language-specific coding
profile, for example, is the coding mix plus a filter on published language
support, not a separate benchmark list.

### 4.3 When a new benchmark joins: the minimum-overlap rule

A benchmark enters the fit as soon as it is tagged and at least
**`MIN_OVERLAP` = 3 anchored models** have a score on it — a model is anchored
if it also has at least two observations on *other* benchmarks, so its ability
is pinned independently of the new item. With fewer than **8** anchored models
its discrimination is held near its family's (`lineage.family` on the page:
Terminal-Bench 4.0 borrows from the Terminal-Bench family, SWE-bench Pro from
SWE-bench) and only its difficulty is free. Below 3 it is listed as
`awaiting_overlap` and shown, not used. No list is edited: SWE-bench Pro is in
today's fit on three models (Opus 5.5, Fable 5.1, Mythos Preview), with its
discrimination borrowed from SWE-bench Verified; Terminal-Bench 4.0 on seven.
In the sourced view 39 of 120 tagged benchmarks are in the fit, 65 are
awaiting overlap (mostly single-run MMLU subjects on two or three models) and
16 are seen on one model only.

Versions are distinct items. Terminal-Bench 1.0, 2.0, 2.1 and 4.0 are four
items in one family; SWE-bench Verified and Pro are two. They share a prior on
discrimination and nothing else, because they are different tests: an old
score is never relabelled as a new one.

## 5. Saturation, staleness, live versus static

### 5.1 Saturation is a property of the fit, not a list

The Fisher information of an observation at ability θ is
(λ · (1−c)σ(1−σ))² / Var. At the frontier of a saturated benchmark σ → 1 and
the information collapses, whatever λ is. Measured on today's fit
(`results/saturation.md`), per observation, at the 97th percentile of ability
relative to the median model:

| Benchmark (flat view) | Best observed | Information at frontier ÷ at median |
|---|---:|---:|
| MATH-500 | 97.3% | 0.00 |
| GSM8K | 97.3% | 0.01 |
| IFEval | 92.0% | 0.04 |
| HumanEval | 93.5% | 0.09 |
| GPQA Diamond | 96.0% | 0.46 |
| HLE | 64.4% | **3.33** |

MATH-500 is among the most informative items in the catalogue *at the
median* (information 427, the highest of any item) and worth nothing at the
frontier; HLE is the reverse. Nobody wrote that down. The v1 profiles weighted
MATH-500 and HumanEval by hand in 13 profiles each and IFEval in 26. In
v2 they keep separating mid-range models and stop voting at the top, and when
a benchmark saturates further, its weight falls with no edit.

### 5.2 Recency

* **Static publications** (papers, system cards, one-off evaluations) keep their
  value but lose precision: a precision multiplier 0.5^(age/365 days), floored
  at 0.25. A model's weights do not change, but harnesses, prompts and
  API-served snapshots do, and an old number is a weaker claim about what a
  customer calls today.
* **Live boards** (Arena; later tbench.ai, Scale, Epoch runs) are dated by the
  observation. Per board, only the **newest snapshot on or before the as-of
  date** is read, at full precision. A model missing from it falls back to its
  newest older snapshot, shifted by the median rating difference between the
  two snapshots over the models they share (Elo scales drift as the pool
  changes), with precision halving every 90 days, floored at 0.1.
* An evidence row is used only on or after its `evidence_date`, which is what
  makes the replay in §9.2 honest.

### 5.3 Source kinds, effort and variants

* **Source kind** enters twice: an offset δ_k (does this kind report higher?)
  and a scatter κ_k (how far do its numbers stray?), both learned from
  model–benchmark pairs measured by more than one kind of source.
  Today's fit, sourced view: a provider's own number sits **+0.35 ± 0.04**
  latent units above what independent evaluators report for the same model
  and benchmark (+0.40 ± 0.04 in the flat view, where the flat block itself
  sits at −0.00 ± 0.01). The extra scatter κ stays at its prior floor (1.5
  points for providers, 3 for flat values): too few pairs overlap to learn
  more.
  The offset is subtracted before a provider number informs ability, so a
  launch table is used, but at a discount the data sets. It is one number for
  all providers; per-provider offsets are not identified yet (§10).
* **Effort**: when one source reports several effort settings for one product,
  the max-effort row is the product row (Jamie's rule), for card evidence and
  for Arena names alike (`claude-opus-4-6-high`, `GPT 6 Astra (Max)`).
* **Same run, one signal.** Card rows copied from Arena are replaced by the
  Arena dataset; METR's 80% horizon is dropped beside the 50% one; the nine
  Arena text categories (same voters) carry a design effect
  1/(1 + 0.7 (n − 1)).
* **Quarantine** (independent audit, Critical 2): a flat block sharing ≥ 4
  identical `(key, value)` pairs, making up ≥ 80% of the smaller block, with
  another card is quarantined on both cards unless one declares itself a
  re-host of the other. 65 cards and 2,022 flat values are quarantined today.
  Evidence rows carry `model_id_as_evaluated` and are never quarantined this
  way.
* **MODEL-117 purge**: every row from artificialanalysis.ai or zapier.com, every
  `aa_*`, `*_aa`, `artificial_analysis_*` key and `automationbench*` is dropped
  before anything else — 1,052 evidence rows today (70% of all evidence).

## 6. From a fit to an answer: filters, states, ordering

The independent audit's bar is "within one day, know the model exists, archive
what its lab claims, and show a **dated provisional comparison or a clear
evidence gap**", and it warns against claiming one universal winner. v2's
output is built for that bar.

1. **Hard filters first.** The task fixes the class (`api/classes.py`: a RAG
   generator is a `text-generator`, an embedder a `vectoriser`), then
   feasibility: image input, minimum context, open weights, price cap, device
   fit. Capability tiers, context length and type position are **not** added to
   any score (High 4): they filter, or they are shown beside the answer.
2. **Score** every remaining candidate: posterior mean and sd of U.
3. **State**, from the evidence (proposed thresholds; floors are Jamie's):
   * `ranked` — at least one independent measurement whose *primary* tag is
     the use case's primary domain, and sd(U) ≤ 0.35;
   * `provisional` — at least one measurement, from any source, tagged with
     the primary domain, and sd(U) ≤ 0.75. A provider's own launch numbers are
     enough: this is the dated provisional comparison, and it is labelled as
     such;
   * `insufficient` — no measurement tagged with the primary domain. An
     evidence gap, named with the domains that *are* measured, never a low
     score.
4. **Order** by posterior mean; publish the 80% interval and a `leading_set`:
   every candidate with at least a 20% chance of beating the leader. When the
   evidence cannot separate the top, the answer says so.

The model's estimate is still shown for a model in an evidence gap, as a
transfer estimate from g, because it is useful to a reader deciding what to
test ("strong general evidence, no chat evidence yet") — but it is never
ordered among ranked rows.

How each finding of the independent audit is answered:

| Audit finding | v2 |
|---|---|
| Critical 1 — frontier invisible | No benchmark list; any tagged benchmark with 3 anchored models counts (§4.3). 30 of 32 flagships placed within a week (§9.2). |
| Critical 2 — sibling scores inherited | The data layer drops the flat value wherever a sourced row exists, quarantines sibling-copied flat blocks (65 cards), and the recommended product view fits no flat data at all (§5.3, §8). |
| Critical 3 — embedders answer a generator question | Class and feasibility are hard filters before scoring; `rag_generator` admits text generators with ≥ 128k context (§4.2). Q08 now returns three generators. |
| High 4 — metadata bonuses reward documentation density | Capability tiers, context and type position are filters or displayed tradeoffs, never score. `score` is evidence only. |
| High 5 — evidence flattened | Every contribution carries raw value, version, harness/effort, source kind, URL and date (§7). |
| The realistic bar — a dated provisional comparison or a clear evidence gap, no universal winner | `provisional` and `insufficient` states, the leading set, 80% intervals (§6). |

## 7. Explanation

Linearised at the fit, each observation *i* implies an ability on its own
domain blend,

    implied_i = θ̂_i + (y_i − ŷ_i) / (slope_i λ_b),   precision p_i = w_i (slope_i λ_b)² / Var_i

and the use-case estimate is a weighted sum of them, U = Σ_i ω_i · implied_i
with ω_i = πᵀ Cov a_i p_i. Every row of an answer can therefore carry the
measurements that drove it, each with **raw value, benchmark version, harness
or effort, source kind, source URL and date** (High 5), the ability it implies
on its own, and its weight share. Negative shares occur and are correct: a
very high agentic score, once g is known from elsewhere, is attributed to the
agentic factor and slightly *lowers* the estimate of g that a chat answer
leans on.

Real output, coding, sourced view (`results/face_validity.md`):

> **anthropic/claude-opus-5-5** — U 2.13 ± 0.11, `ranked` (independent evidence
> in the primary domain):
>
> | measurement | source | implies | weight |
> |---|---|---:|---:|
> | Arena WebDev 1818 (`claude-opus-5.5-max`, snapshot 2026-09-23) | independent, [lmarena-ai/leaderboard-dataset](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset) | +2.05 ± 0.06 | 56% |
> | HLE with tools 67.7% | provider, [system card](https://www.anthropic.com/claude-opus-5-5-system-card), 2026-09-22 | +2.00 ± 0.41 | 11% |
> | Terminal-Bench 4.0 66.4% (`xhigh`) | provider, system card, 2026-09-22 | +2.59 ± 0.42 | 9% |
> | Terminal-Bench-Science 0.1 58.7% | provider, system card, 2026-09-22 | +1.82 ± 0.55 | 6% |
> | HLE (no tools) 64.4% | provider, system card, 2026-09-22 | +2.29 ± 0.30 | 6% |
>
> **anthropic/claude-mythos-5-1** — U 2.12 ± 0.42, `provisional` (no
> independent measurement in coding): Terminal-Bench 4.0 60.9%, provider,
> [Fable 5.1 system card](https://www.anthropic.com/claude-fable-5-1-system-card),
> 2026-09-01 → +2.28 ± 0.43, weight 100%.

The second row is the case the audit asked for: a model known for three weeks,
one lab claim archived, shown in the leading set with an interval four times
as wide as its neighbour's and a label that says why.

## 8. Data views

The ticket asks for two runs.

* **sourced** — evidence rows after the purge, plus the Arena dataset
  (`lmarena-ai/leaderboard-dataset`, CC BY 4.0, read over plain HTTP by
  `research/ranking_v2/fetch_arena.py` and committed as a 1–2 MB gzip). Arena
  is sourced evidence: every row has a URL, a publish date and an interval.
* **flat** — the same plus the undated flat `benchmarks.scores` blocks, dated by
  `benchmark_as_of`, with sibling copies quarantined, as their own source kind
  (`flat_unsourced`) with a learned offset and scatter.

| | sourced | flat |
|---|---:|---:|
| Observations | 2,324 | 7,132 |
| Models with any | 240 | 492 |
| Benchmarks (items) in the fit | 39 of 120 | 155 of 174 |
| Items awaiting overlap / seen on one model | 65 / 16 | 6 / 13 |
| Evidence rows purged (MODEL-117) | 1,052 | 1,052 (+61 flat keys) |
| Flat values quarantined as sibling copies | — | 2,022 on 65 cards |
| Flat values dropped beside a sourced row for the same benchmark | — | 257 |
| Fit time | 3.0 s (86 sweeps) | 13.5 s (133 sweeps) |

**Recommendation: the product should fit the sourced view.** The flat block
adds 4,808 values, but they sit almost entirely on models released before
mid-2026 and on benchmarks that no longer separate the frontier (§5.1); it
changes no top-5 in coding, chat, agentic or vision and moves the reasoning
list only within its interval. It helps held-out prediction on legacy items
(the flat-view RMSE is computed on 1,065 cells, mostly MMLU subjects and MTEB),
but it makes the replay *less* stable (median coding displacement 4.0 places
against 1.0; 11 of 23 within three places against 18), because undated April
values arrive in bulk. And it carries the
defects the independent audit found: 65 cards are quarantined as sibling
copies, and nothing else in the block can be attributed. Keep it only as a
labelled transition for models with no sourced evidence, never beside sourced
evidence on the same benchmark, and retire it as MODEL-113 backfills.

## 9. Validation

All four gates, both views. Full tables in `research/ranking_v2/results/`.

### 9.1 Held-out prediction

15% of observed (model, benchmark) cells masked, five seeds, predicted from
the rest. Error is RMSE in units of each item's training sd (percentage items
scaled by at least 5 points so a three-model item cannot dominate); cells whose
item keeps fewer than 5 training models are not scored.

| RMSE (item-sd) | benchmark mean | model mean | low-rank k=1 | k=2 | k=3 | v2, g only | **v2** |
|---|---:|---:|---:|---:|---:|---:|---:|
| sourced, all (344 cells/seed) | 0.997 | 0.483 | 0.417 | 0.412 | 0.398 | 0.283 | **0.261** |
| sourced, Arena cells | 0.990 | 0.429 | 0.359 | 0.347 | 0.333 | 0.254 | **0.225** |
| sourced, benchmark cells (13/seed) | 1.173 | 1.221 | 1.158 | 1.198 | 1.176 | **0.692** | 0.721 |
| flat, all (1,065 cells/seed) | 0.999 | 0.636 | 0.592 | 0.497 | 0.434 | 0.421 | **0.398** |
| flat, benchmark cells (755) | 1.013 | 0.646 | 0.629 | 0.553 | 0.479 | 0.465 | **0.446** |

Per domain (flat view), v2 against the best baseline: coding 0.41 vs 0.57,
knowledge 0.34 vs 0.37, math 0.52 vs 0.59, vision 0.55 vs 0.61, reasoning 0.72
vs 0.78; low-rank k=3 wins on chat (0.24 vs 0.28) and retrieval (0.26 vs 0.29),
the two domains where a free third factor has most data to find. Mean absolute
error on percentage cells: 9.1 points against 16.6 for the benchmark mean
(sourced), 3.7 against 11.2 (flat). The 80% predictive intervals cover 96% of
held-out sourced cells and 92% of flat cells — slightly conservative overall, but only 67% on the 13
sourced benchmark cells, where the intervals are too narrow (§10).

Reading it honestly: v2 beats every baseline overall in both views, most of
the gain over low-rank factorisation comes from the measurement model (the
saturating link, the learned noise, the source offsets, the Arena intervals —
compare "v2, g only" with "low-rank k=1"), and the domain factors add a
further 5–8%. The sourced benchmark-cell comparison rests on 13 cells per seed
and should not be over-read: it is the data's thinness, not a model result.

### 9.2 Historical replay

For each of 32 2026 flagships, a fit using only evidence dated on or before
release + 7 days (Arena from the newest weekly snapshot on or before it),
ranked among models released by then. v1 is the repository's own
`rank_report` at the CLI floor on the same dated, purged data.

| Sourced view | coding | reasoning | chat |
|---|---|---|---|
| v2 placed at +7 days | **30/32** (25 ranked) | 27/32 (1 ranked) | 23/32 (23 ranked) |
| v1 ranked at +7 days | 0/32 | 0/32 | 0/32 |
| Within 3 places of today's position (flagships with 30+ days of later evidence) | 18/23 | 15/22 | 17/21 |
| Median displacement | 1.0 | 2.5 | 1.0 |

Examples: Opus 4.6 at 2026-02-12 is coding #1 of 146 and still #1 of that
pool today; GPT-6 Astra at 2026-09-11 is coding #2 of 215 (today #2); Fable 5.1
at 2026-09-08 is #3 (today #3). The misses are informative: GPT-5.5 and
Qwen3.7-Max had no dated evidence of any kind by release + 7 days (an
ingestion gap, not a model gap), and chat placement waits for a model's
text-Arena listing, which usually takes one to three weeks — correctly shown
as an evidence gap rather than a guess. v1 ranks none of the 32 at release,
in any view, at any use case.

### 9.3 Face validity (sourced view, as of 2026-09-24)

`P` = provisional; **bold** = in the leading set. The v1 row is the
repository's scorer on today's unpurged data, as production serves it; with
the purge applied v1 ranks nothing at all in coding, reasoning, chat or
agentic on sourced evidence, and the same old models on the flat block.

| # | coding | reasoning | chat | agentic | vision |
|---:|---|---|---|---|---|
| 1 | **Opus 5.5** | **Opus 5.5** P | **Fable 5** | **Opus 5.5** P | **Opus 5.5** P |
| 2 | **Mythos 5.1** P | Mythos Preview P | **Opus 4.6** | **Mythos 5.1** P | Mythos Preview P |
| 3 | GPT-6 Astra | Fable 5 P | **Fable 5.1** | Fable 5.1 | Fable 5 |
| 4 | Fable 5.1 | Gemini 3.8 Flash | **Opus 4.7** | GPT-6 Astra | Opus 4.7 |
| 5 | Opus 5 | Fable 5.1 P | **Gemini 3.8 Flash** | Opus 5 | Opus 4.6 |
| 6 | Mythos Preview P | Opus 5 P | **Opus 5** | Mythos Preview | Qwen3.8 Max |
| 7 | GPT-6 Sol | Opus 4.6 P | GPT-5.6 Sol | Fable 5 | Fable 5.1 |
| 8 | Fable 5 | GPT-5.6 Sol P | Kimi K3 | GPT-5.6 Sol | Opus 5 |
| 9 | Kimi K3 | GPT-6 Astra P | Opus 4.8 | Kimi K3 | GPT-5.6 Sol |
| 10 | Qwen3.8 Max | Opus 4.7 P | Gemini 3.7 Flash | Opus 4.8 | GPT-6 Astra |
| v1 #1–3 | Gemini 2.5 Pro, Sonnet 4.5, Opus 4.6 | Opus 4.6, Gemini 2.5 Pro, Gemini 2.5 Pro 05-06 | GPT-4.1, Opus 4.6, Gemini 2.5 Pro | Opus 4.6, Gemini 2.5 Pro, Opus 4 | GPT-4.1, GPT-4.1 mini, Llama 4 Maverick |

Would a knowledgeable engineer defend these in September 2026?

* **Coding, agentic, vision: yes.** The coding and agentic lists match the
  audit's provisional shortlist (Opus 5.5, Astra, Fable 5.1) and the MODEL-108
  Terminal-Bench 4.0 board; vision matches the Arena vision top 10 the
  MODEL-108 audit cites (Fable 5, Qwen3.8 Max, Opus 4.7, Opus 4.6, Opus 5).
  The one objection is Mythos 5.1 at #2 on a single provider number; it is
  labelled provisional with a ±0.42 sd and would fall below Astra under the
  lower-bound ordering (§14, decision 4).
* **Chat: yes.** It is the text-Arena style-control top 6 in a slightly
  different order, which is what the evidence is.
* **Reasoning: defensible but weak, and it says so.** Opus 5.5 leads on its
  own HLE 64.4% and HLE-with-tools 67.7% — the highest reported — but only 7
  models are `ranked`, because after the purge almost no independent reasoning
  measurement exists (of 327 GPQA Diamond evidence rows, 312 came from AA). The
  independent audit's reasoning reference (Astra, Gemini 3.8 Flash, 3.7 Flash)
  comes from Epoch's GPQA runs, which we do not hold; Gemini 3.8 Flash is the
  only `ranked` model in v2's top 10 for the same reason. This is the case for
  ingesting Epoch and Scale (MODEL-113), not for a different model.

### 9.4 Ground truth: the independent audit's 20 questions

The audit (2026-09-24) graded v1's live answers — 15 wrong, 5 defensible — and
gave a dated reference top three for 19 of the 20 questions. v2 answers each
with the use case, hard filters (class, open weights, price cap, context,
device fit) and state rules of §6:

| | v1 (live, audited) | v2 sourced | v2 flat |
|---|---:|---:|---:|
| Reference models in the top three (of 57) | 6 | **18** | 17 |
| Reference model ranked first (of 19) | 4 | **7** | 6 |
| Wrong-class answers | 1 (RAG → embedders) | 0 | 0 |
| Honest abstentions (evidence gap named) | 1 (speech) | 3 (both embedding questions, speech) | 1 (speech) |

Per question (sourced): coding, code review and agents (Q01–Q03) put two of
the three reference models in the top three; general assistant (Q04) and
research assistant (Q19) one and two; chat (Q05) now returns the text-Arena
leaders; competition maths (Q07) two of three (Fable 5.1, Fable 5 — the
reference uses FrontierMath, which we do not hold); the RAG generator (Q08) is
three generators with ≥ 200k context, where v1 returned three embedders;
local coding on an RTX 4090 (Q17) and local chat on an M4 (Q18) now answer
with Qwen3.5-27B, Muse Glimmer 30B and Gemma 4 models instead of Gemma 3; the embedding questions
(Q15–Q16) abstain because no sourced MTEB evidence exists (the audit's
references are MTEB v2 leaders, most without a card). Reasoning (Q06) and the
cheap-model questions (Q10–Q11: GPT-6 Luna has no measurement at all) miss.
Full table: `results/ground_truth.md`.

## 10. Failure modes

1. **Thin frontier overlap.** The provider-reported frontier benchmarks
   (SWE-bench Pro on 3 models, Terminal-Bench 4.0 on 7) connect to the bulk of
   the data through a handful of models. One mis-reported number moves several
   models. Mitigations in the design: item-parameter uncertainty in every
   row's variance, the τ prior, `provisional` for provider-only evidence.
   The real fix is more independent boards (MODEL-113).
2. **One number extrapolates through g.** A model with a single measurement
   (Mythos 5.1) is placed in the whole mix by the general factor. The interval
   is wide and the label says provisional, but it still sorts near the top by
   mean. Decision 4 (ordering) is the lever.
3. **Tags carry the weight the profiles used to.** A mis-tag moves evidence to
   the wrong factor; the WebDev episode in §4.1 moved the whole chat list.
   Tags must be reviewed data with a coverage test.
4. **Intervals are conditional.** The Laplace approximation conditions on item
   parameters (partly repaired by propagating their variance) and on the
   hyperparameters. Held-out coverage is good overall (92–96%) but low on the
   13 sourced benchmark cells (67%). Phase 2 should calibrate against a
   parametric bootstrap before thresholds are finalised.
5. **Reasoning after the purge.** 7 ranked models in the sourced view.
   Correct, and not useful until independent reasoning boards are ingested.
6. **Provider offsets are global.** One δ for every lab. Per-provider offsets
   are not identified with today's overlap and would be the first extension.
7. **Contamination is not modelled.** A benchmark whose test set leaked shows
   up as an easy item (β) or as disagreement (τ), not as a flag. Recency decay
   and saturation partly cover it.
8. **Live-board alignment assumes a uniform drift.** A model missing from the
   newest Arena snapshot is shifted by the median offset between snapshots.
9. **Scale is per build.** g is standardised to sd 1 per fit, so a model's
   score moves when the population does. Phase 2 should anchor the scale to a
   fixed reference set so `score` is comparable across builds.
10. **Effort labels are uneven.** "Max effort" is parsed from names and
    configurations; a source that does not say which effort it ran is taken
    as the product row.

## 11. Contract impact

`score` (the ticket's `rank_score`) changes meaning: from a 0–100 composite of
bounded benchmark points plus metadata bonuses, to the posterior mean of a
latent capability on a scale where the sd of g across well-measured models is
1. Its range widens (it is unbounded and can be negative), `rank_status` gains
a value (`provisional`), and several fields v1 publishes lose their meaning
(`benchmark_coverage`, `score_lower_bound`/`score_upper_bound` as
missing-weight bounds, `capability_score`, `type_bonus`, `context_score`).
Under MODEL-59 that is a major bump for every document that carries a ranked
row:

| Document | Today | v2 | Why |
|---|---|---|---|
| `rankings.json` `schema_version` | 2.0 | **3.0** | `score` semantics and range; new state; removed components |
| `POST /v1/rank` envelope (`rank_service.SCHEMA_VERSION`, OpenAPI `info.version`) | 1.0 | **2.0** | same rows |
| CLI `--json` envelope (`cli.modelspec.offline.SCHEMA_VERSION`) | 1.0 | **2.0** | `offline rank` rows are the same rows |
| `build.export_schema_version` | 3.0 | **4.0** | `candidates.json` stops carrying a flat `benchmark_scores` map per model and carries observations plus fitted parameters (below); `profiles.json` carries mixes, not benchmark weights |

Proposed row shape (additions in bold): `model_id`, `score` (posterior mean),
**`score_sd`**, **`interval_80`**, `rank` (null unless ranked or provisional),
**`rank_status`** ∈ {`ranked`, `provisional`, `insufficient`},
**`status_reason`**, **`leading_set`**, **`p_beats_leader`**,
**`explanation`** (list of {item, value, unit, version, configuration,
as_evaluated, source_kind, source_url, date, implied_ability, weight_share}),
`evidence_basis` (kept; its labels still describe input provenance), and the
filter results that made the model a candidate. The `policy` block gains
`method: "capability-model-v2"`, the thresholds of §6 and the as-of date;
`neutrality` is untouched.

Pre-v2 CLIs are refused by the existing export-version check, as the 2.0→3.0
bump was. A one-release overlap in which the export carries both
`rankings.json` (v1, 2.0) and `rankings-v2.json` (3.0) lets DPF switch on its
own schedule.

## 12. Performance: build time, not request time

The fit is a build step. On this machine, in pure Python:

| | sourced | flat |
|---|---:|---:|
| Observations / models / items | 2,324 / 240 / 39 | 7,132 / 492 / 155 |
| Fit (pure CPython 3.14, one core) | 3.0 s | 13.5 s |
| Score every candidate for one use case | 1–5 ms | 2–5 ms |
| Whole replay (64 fits + v1 at every cutoff) | 384 s | (same run) |

The Worker should not fit per request: a fit is seconds of CPU on every cold
isolate, and two requests a few seconds apart would disagree whenever the
export changed under them. Instead the build fits once and ships the
parameters: per model its dimension list, posterior mean vector and covariance
(at most ~14 × 14, typically 6–9 dims), per domain its σ_d, and the
per-observation explanation terms. For ~500 models that is well under 1 MB of
JSON beside `candidates.json`.

At request time the Worker then does, per candidate, a dot product and a
quadratic form — U = wᵀv, Var = wᵀΣw + Σ_{missing d} (π_d σ_d)² — plus the
hard filters and the state rule. Scoring every candidate for one use case
takes 1–5 ms in CPython, and it works for **any** mix a caller sends, not just
the published ones, so custom use cases cost nothing extra. The arithmetic is
the same file in the CLI and the Worker (vendored byte for byte, as today), so
the byte-identical guarantee of `docs/rank-api.md` survives.

## 13. Implementation plan

**Phase 2 — the data layer and the fit, shadowed (≈ 2 weeks).**

1. `domains:` on benchmark pages: add the field to the page schema, backfill it
   for every benchmark with scores (≈ 170 today) from `domains.py`, and add a
   test that every benchmark with a card observation is tagged.
2. Move `evidence.py` into `pipeline/` as the observation layer: the purge, the
   quarantine, the effort rule, live-snapshot selection, dating. Carry
   observations (not a score map) through `candidates.json` (High 5).
3. Move the Arena fetcher into the scheduled leaderboard refresh the MODEL-108
   audit proposed, writing dated evidence rows rather than a side file.
4. `pipeline/capability.py`: the fit (`model.py`), run by `pipeline/build.py`,
   writing `rank/capability.json` (parameters) and a fit report (items and
   their status, offsets, σ, convergence). Fail the build if it does not
   converge or if any published use case loses more than a set share of its
   ranked models between builds.
5. Publish v2 answers beside v1 (`rankings-v2.json`, `/v1/rank?method=v2`)
   without changing v1. Tests: fit determinism, the Worker/CLI byte-identity
   test extended to v2, the held-out and replay backtests as CI jobs with
   thresholds taken from §9.

**Phase 3 — cut over (≈ 1 week after Jamie signs off the decisions in §14).**

1. Hard class and feasibility filters in `/v1/rank` (class from
   `api/classes.py`, min context, image input, device fit) — independent of the
   scorer and worth shipping first.
2. Switch `rankings.json` and `/v1/rank` to v2 with the version bumps of §11;
   keep v1 answers for one release under their old names.
3. Retire `USE_CASE_PROFILES` benchmark weights, `BENCHMARK_RANGES`,
   `VERIFIED_ADDITIONS`, the coverage floors and the metadata bonuses; profiles
   become mixes plus filters.
4. Update `docs/cli-contract.md`, `docs/rank-api.md`, the wizard (which reads
   `rankings.json`) and `docs/api.md`.

## 14. Decisions for Jamie

Everything below is proposed, not decided. The prototype's values are the
starting point.

1. **Adopt the capability model as the ranking method** (§3), retiring fixed
   benchmark lists, weights, bounds and coverage floors.
2. **Which data the product fits.** Recommendation in §8: sourced evidence
   plus the Arena dataset; the flat block only as quarantined, down-weighted
   `flat_unsourced` evidence during a transition, and never for a model that
   has sourced evidence on the same benchmark.
3. **The state thresholds that replace the floors** (§6): `ranked` needs
   independent evidence whose primary tag is the use case's primary domain and
   sd(U) ≤ 0.35; `provisional` needs any measurement in the primary domain and
   sd(U) ≤ 0.75; the leading set is P(beats leader) ≥ 0.20.
4. **Ordering.** Posterior mean (the prototype), or the lower end of the 80%
   interval, which ranks a single provider number below a well-measured model
   with the same mean. The mean is the better estimate; the lower bound is the
   more conservative shortlist. The coding answer in §9.3 is where the two
   differ.
5. **The use-case mixes** of §4.2, and whether `chat` should mean "predicted
   human preference" (weighting the chat factor more) or "capability in
   conversation" (the prototype).
6. **Provider self-reports count toward `provisional` but not `ranked`.** The
   fitted offset (§5.3) says providers report higher than independent
   evaluators on the same benchmark; confirm that such a number may still
   place a model provisionally within a day of launch (the audit's bar).
7. **Recency**: a 365-day precision half-life for static evidence, and
   newest-snapshot-only for live boards.
8. **Minimum overlap**: 3 anchored models to enter, 8 to learn a
   discrimination freely.
9. **Contract**: the version bumps of §11, and the one-release overlap.
10. **The `domains:` vocabulary** and who reviews tags (tags now carry the
    weight that the profiles used to).

## Reproduce

```bash
# from the repository (or worktree) root, with the repo venv
PY=/Users/terbeest/dev/modelspec/.venv/bin/python
$PY -m research.ranking_v2.backtest all          # every gate, both views (~12 min)
$PY -m research.ranking_v2.backtest truth --report <independent-audit dir>
# optional: refresh the committed Arena snapshot (the JSON API rate-limits;
# the parquet path is what wrote the committed file)
uv run --no-project --with pyarrow python -m research.ranking_v2.fetch_arena --parquet
```

Results are written to `research/ranking_v2/results/` (Markdown and JSON). The
fits are deterministic: fixed seeds, fixed as-of date (2026-09-24), committed
Arena snapshot. Setting `RANKING_V2_CARD_CACHE=<file>` caches the parsed cards
between runs.
