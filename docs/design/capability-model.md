# Capability model

Status: implemented for MODEL-129 on 2026-09-25.

## Decision

The estimate stage uses a hierarchical bifactor item-response model. It turns the
verified evidence items in one snapshot into a capability estimate for each model and
registry domain that the model has actually been measured on. A model with no evidence
tagged to a domain gets `null`, not a cross-domain guess.

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
items and their domain/directness tags from the snapshot inputs. An item tagged `direct`
has loading 1 before normalisation. Proxy loading is selected by deterministic residual
minimisation and is constrained below the direct anchor. The fit also learns an offset
for each non-independent source kind; independent and benchmark-author measurements are
the zero reference. Evidence weight halves every 365 days, with a 0.25 floor. A
percentage item loses Fisher information near its ceiling, so saturation appears as low
information at the frontier rather than a special rule.

Alternating ridge-weighted least squares fits model abilities, item parameters, source
offsets and proxy loading. Inputs, iterations and tie breaks are sorted; there is no
random fit initialisation. The snapshot stores the resulting item parameters, source
offsets, capability estimates and explanation drivers. Identical inputs therefore
produce byte-identical snapshots.

## Uncertainty and decisions

The inverse penalised information matrix gives a Laplace covariance for each model.
Contract intervals are central 80% intervals. A single-domain objective reads the stored
estimate; constraints still filter first and never add score. The engine uses a
snapshot/spec-derived seed to draw the feasible set and returns `p_best` and
`top3_stability`. Overlapping intervals add `not_separable`; the web presents the
overlapping rows as one evidence-indistinguishable group even though a stable sort is
retained for transport.

Full explanations list the measurements that drove the requested estimate. Each item
keeps its source, observation date, learned loading, normalised estimate weight and
recency weight. Contract 1.6 adds those three nullable provenance fields. Older decision
contracts remain accepted.

The fit runs only while a snapshot is built. A summary decision does no fitting. The
premier snapshot validation measured a 25.8 ms median and 37.4 ms maximum across all 12
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
- The report names 43 estimate/single-benchmark leader disagreements and links the dated
  source behind every single-benchmark leader. These are not silently treated as errors:
  the estimate combines all tagged evidence with learned discrimination, source offset,
  directness and recency, while the comparator uses one raw measurement.

The recall specs now name domains where the question names a capability; the approved
expected answers were not changed. The previous report was 1 pass, 14 partial and 5
fail. The estimate-stage report is 2 pass, 4 partial and 14 fail:

| Question | Before | Estimate stage |
|---|---|---|
| Q01 | fail | fail |
| Q02 | fail | pass |
| Q03 | partial | fail |
| Q04 | partial | fail |
| Q05 | partial | fail |
| Q06 | partial | fail |
| Q07 | partial | fail |
| Q08 | partial | fail |
| Q09 | partial | fail |
| Q10 | partial | partial |
| Q11 | partial | partial |
| Q12 | partial | fail |
| Q13 | fail | fail |
| Q14 | partial | fail |
| Q15 | partial | partial |
| Q16 | fail | fail |
| Q17 | partial | partial |
| Q18 | partial | fail |
| Q19 | fail | fail |
| Q20 | pass | pass |

The changed failures are visible rather than tuned away. Most come from combined
evidence naming a top-three model outside the recall file's single-board acceptable set;
some come from newly estimated models that the expected answer requires under
`may_qualify`. Of the ten questions that explicitly expect no unique winner, interval
overlap satisfies that expectation whenever the engine has results except Q07. Q16 has
no complete estimate. The detailed findings are in the generated recall report.

## Floor policy proposal

This change does not alter floors. If Jamie adopts estimate-based floors later, use an
explicit risk rule rather than the point estimate: either require the lower interval
bound to clear the floor, or require a documented posterior probability of clearing it.
The decision contract should state the interval level and probability threshold. Until
then, existing evidence floors keep their present meaning.

Excluded sources are filtered before the fit. Arena evidence in the validation snapshot
comes only from `lmarena-ai/leaderboard-dataset`.
