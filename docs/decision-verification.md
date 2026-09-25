# Two-key verification

`decision/verify.py` (MODEL-140; design §5, "Two keys"). The agent that
collects a value never verifies it.

## Flow

1. A collector files a **claim** with `Queue.file`: the target (`fact` or
   `evidence` ID), the subject and the names it is published under, the value,
   unit and conditions (effort, harness, date), the source snapshots it read
   and who collected it (agent, model family, method).
2. Source change detection (`decision/sources.py`) re-queues the claims citing a
   changed region with `Queue.requeue(report)`. The re-check pins each source
   to its new retained copy. `RecheckReport.requeue` refs are `fact:<id>` or
   `evidence:<id>`.
3. `modelspec verify [--changed-only]` (or `verify.run`) re-reads each pending
   claim from the cited regions of its retained copies. It appends one
   `Verification` per value to `verification/log.jsonl` and prints a summary.
   `--changed-only` skips new values and runs only the re-queued ones.

## Extractors

The verifier re-extracts the value. It never reads the collector's value
first. Deterministic extractors always run first:

- `TableExtractor`: tables as `decision.normalise` renders them. It needs a
  model column. The value column is the one whose header is the claim's label,
  or else the only score-like column. A unit in the header, such as
  `Score (%)`, applies to the column.
- `KeyValueExtractor`: `Key: value` lists. The region must name the subject
  under a `Model` or `Name` key.
- `LLMExtractor`: prose. It calls an injected `complete(prompt)` function,
  and its actor records the model: `llm-extract:<model>`. The CLI does not
  configure one yet, so a prose region is reported as `skipped`.

The first extractor that accepts a region and is independent of the collector
reads it. `decision.model.Verification` rejects a verifier whose agent and
model family both match the collector's. A claim that no independent
extractor can read is `skipped`: nothing is logged, and the claim stays queued.

## Checks

- **Identity.** The row must name the subject, after the name is normalised
  (case and punctuation). An effort qualifier in the model cell, such as
  `(max effort)` or `[high]`, is a condition. Any other qualifier, such as
  `(thinking)`, is a different identity. When the claimed value belongs to
  another row, the diff names that sibling.
- **Value and unit.** Both values are converted to the base unit of their
  dimension (`UNITS`: percent/fraction, tokens/K/M, USD per 1M/1K tokens, and
  so on). Tolerance (`TOLERANCE_RULE`): `|a − b| ≤ 0.5 × max(ulp_a, ulp_b)`.
  Here `ulp` is one unit in the last written decimal place, so a value rounded
  to the other value's precision agrees. When the values disagree and the units
  differ, the diff is `unit`. When the units match, the diff is `value`. A
  source that states no unit does not confirm one.
- **Conditions.** Effort and harness must match. If the source states a
  condition that the claim omits, that is a mismatch: a max-effort score filed
  with no effort is not a default score. A date is checked when the claim
  carries one.

## Outcomes and quarantine

- `verified`
- `mismatch`: `diff` is a JSON list of `{field, expected, found}`. The target
  is listed by `Queue.recrawl_requests()` until it is filed again.
- `unreachable`: the retained copy, the source registration or the cited
  region is missing. The target is also listed for re-crawl.

`is_quarantined(target)` is true unless the target's latest logged outcome is
`verified`. A value that has never been verified is quarantined.
`quarantined_values(targets=None)` lists the quarantined targets in the log,
or among `targets` when that list is given.

## Fixture

`tests/fixtures/verification/` seeds these errors: a score copied from a
sibling, a wrong unit (in both directions), a max-effort value filed as default
or with no effort, a stale date, a value absent from the source, a missing copy
and a missing region. `tests/test_decision_verify.py` requires every seeded
error to end as a mismatch or quarantined, and every correct value to end as
verified.
