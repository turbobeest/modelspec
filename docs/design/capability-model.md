# Capability model

Status: implemented for MODEL-129 on 2026-09-25.

## Decision

The estimate stage fits a hierarchical bifactor item-response model, then projects each
domain from only the evidence tagged to that domain. The factor fit learns item
discrimination, source-kind offsets and a proxy loading for held-out prediction. The
domain projection produces the capability estimate used by decisions. A model with no
evidence tagged to a domain gets `null`, not a cross-domain guess.

This model was chosen over two alternatives:

- A fixed weighted average cannot admit a new benchmark without code or weights. That
  conflicts with ADR 0002.
- An unconstrained low-rank factorisation has rotating, unnamed factors. Its factors do
  not remain the registry domains. A Bradley–Terry fit would suit raw Arena battles, but
  the verified snapshot retains published aggregate Arena measurements, not pairwise
  ballots.

The fit has one general factor and one deviation for each tagged domain. Every benchmark
version is an item with a learned positive discrimination, intercept and residual
variance. Percentage measurements use a logistic item link after accounting for a
published random baseline. Other numeric measurements use a standardised linear link.
Higher latent capability always means better; lower-is-better measurements are inverted
at the item boundary.

There is no benchmark allowlist or benchmark-specific hand weight. The model reads the
items and their domain/directness tags from the snapshot inputs. For each item, the
projection orients higher capability upward and standardises the admitted measurements.
A direct measurement has loading 1. A proxy has loading 0.35, so it adds 0.1225 of the
precision of a direct measurement. Evidence precision halves every 365 days, with a
0.25 floor. These rules depend on directness and age, not on a benchmark ID. The factor
fit still learns its proxy loading and source-kind offsets for prediction, but those
cross-domain parameters cannot reorder a domain estimate.

The projection has positive, score-independent weights. Raising one model's measurement
cannot lower that model's estimate or rank. This also fixes the identification problem
for items such as `arena_sc_medicine`, which is direct evidence for chat preference and
proxy evidence for medical capability. The old estimate combined a general factor with
a medical deviation even though the item was fitted mostly through chat preference.
Unrelated evidence could therefore reverse the medical measurement.

Alternating ridge-weighted least squares fits model abilities, item parameters, source
offsets and proxy loading. Inputs, iterations and tie breaks are sorted; there is no
random fit initialisation. The snapshot stores the resulting item parameters, source
offsets, capability estimates and explanation drivers. Identical inputs therefore
produce byte-identical snapshots.

## Uncertainty and decisions

The projection starts with 0.25 prior precision and adds the directness- and age-adjusted
precision of each tagged measurement. Contract intervals are central 80% intervals.
Proxy-only domains therefore keep wide intervals. Their results add
`proxy_evidence_only`, and their contribution formula says that the estimate is
proxy-only. A single-domain objective reads the stored estimate; constraints still
filter first and never add score. The engine uses a snapshot/spec-derived seed to draw
the feasible set and returns `p_best` and `top3_stability`. Overlapping intervals add
`not_separable`; the web presents the overlapping rows as one evidence-indistinguishable
group even though a stable sort is retained for transport.

Full explanations list the measurements that drove the requested estimate. Each item
keeps its source, observation date, directness loading, normalised estimate weight and
recency weight. Contract 1.6 adds those three nullable provenance fields. Older decision
contracts remain accepted.

The fit runs only while a snapshot is built. A summary decision does no fitting. The
premier snapshot validation measured a 13.9 ms median and 19.4 ms maximum across all 12
domain objectives on the local Worker-equivalent Python path, below the 1 s budget. This
is a compute-path measurement, not deployed network latency.

## Validation

The reproducible report is [capability-model.md](../validation/capability-model.md). On
the 2026-09-25 premier snapshot, 462 observations produced 35 learned items across 32
models and 12 domains.

- Five deterministic benchmark-cell holdouts produced 345 predictions: scaled RMSE
  0.7060, versus 1.1049 for the benchmark-mean baseline.
- Holding out each model's newest eligible score produced 20 predictions: scaled RMSE
  0.8326, versus 1.2245 for the same baseline.
- The report finds 3 separable estimate/single-benchmark leader disagreements and 34
  point-order differences whose intervals overlap. Every separable disagreement names
  other fitted direct evidence for the estimate leader and links the dated source behind
  the single-benchmark leader.

The approved recall specs remain byte-identical to main. The generated recall report
compares those same benchmark objectives before and after this change; domain objectives
are not substituted into the approved questions. Main reports 1 pass, 6 partial and 13
fail; this branch reports 4 pass, 6 partial and 10 fail. Q01, Q02 and Q06 move from fail
to pass, with no question moving backward.

## Floor policy proposal

This change does not alter floors. If Jamie adopts estimate-based floors later, use an
explicit risk rule rather than the point estimate: either require the lower interval
bound to clear the floor, or require a documented posterior probability of clearing it.
The decision contract should state the interval level and probability threshold. Until
then, existing evidence floors keep their present meaning.

Excluded sources are filtered before the fit. Arena evidence in the validation snapshot
comes only from `lmarena-ai/leaderboard-dataset`.
