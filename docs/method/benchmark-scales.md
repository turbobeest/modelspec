# Declaring benchmark scales

Benchmark pages declare `metric.unit`, `metric.min_score` and `metric.max_score`.
Card evidence must use the same stored unit and stay within that range. The
writer and snapshot validators enforce it before a row can enter a decision.

Percentage and fraction benchmarks retain their zero floor. Open scales,
such as a money balance, can have negative values when the page allows them.
For a signed metric, declare its floor explicitly on the benchmark page.

FollowIR reports pairwise mean reciprocal rank, or p-MRR. Its raw score runs
from -1 to 1. The [paper's Table 2](https://arxiv.org/html/2403.15246v3#S4.T2)
reports that score times 100, from -100 to 100. Declare the stored scale as:

```yaml
metric:
  name: p-MRR, mean over three tasks
  direction: higher_is_better
  unit: p-MRR (x100)
  min_score: -100
  max_score: 100
```

Use `unit: p-MRR (x100)` on FollowIR evidence rows. A negative score is valid;
zero means the ranking did not respond to the changed instruction. The scale
validator enforces the metric's inherent bounds even if a page omits them or
declares a wider range. A page may declare a narrower range.

The MTEB refresh converts raw FollowIR scores to this stored scale. Its other
boards continue to store percentage scores. Verification compares the retained
board fraction with the stored value using the unit's factor of 0.01.

Fresh benchmark pages, card rows, source registrations and verification records
belong in `turbobeest/modelspec-data`, as required by [the data split](../design/data-split.md).
The public data freeze also covers `benchmarks/AUTHORING.md`; changes to engine
authoring guidance belong under `docs/`.

This adds a benchmark scale to the engine. Evidence units already accept strings
and scores already accept signed finite numbers, so no published contract field
widens and no contract version changes.
