---
id: swe_bench_agent
name: "SWE-bench Agent"
aliases: []
page_kind: subset
category: coding
subcategory: "internal repository label for an agent-harness SWE-bench score"
status: unknown
summary: "An internal model-card key for an agentic (not single-shot patch) SWE-bench score; no publisher, paper or dataset for it under this name was found."
measures: >
  `swe_bench_agent` is a scoring key used by this repository's own model-card template, not a benchmark
  published anywhere under that name. The template comments it as "agentic SWE-bench (not just patch
  gen)," grouped with other agentic-environment benchmarks (tau_bench, web_arena, os_world) rather than
  with the SWE-bench family's other named variants. What exact dataset, instance count, harness or
  scaffold produces the number is not documented anywhere this research could find.
task_format: >
  Not documented under this name. If the template comment is accurate, it denotes SWE-bench evaluated by
  an agent that reads, runs and edits a repository over multiple steps, as opposed to a single-shot patch
  generated from one prompt — but no source specific to `swe_bench_agent` describes its dataset, instance
  count or grading protocol.
metric:
  name: ""
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No published baseline exists under this name. Values observed across this repository's own model
    cards run from about 32 to 63 (up to 81 for the newest models catalogued), always below the same
    card's swe_bench_verified value.
dataset:
  size: null
  size_note: ""
  url: ""
  license: ""
  languages: []
  modalities: []
  splits: ""
  public_test_set: null
publisher:
  org: ""
  authors: []
  url: ""
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: ""
released: ""
last_updated: ""
lineage:
  family: swe_bench
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: ""
contamination:
  risk: unknown
  note: "Would inherit the SWE-bench family's high structural contamination risk if it is in fact a SWE-bench evaluation, but that could not be confirmed, so risk is recorded as unknown rather than assumed."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: [coding, agentic, swe-bench, undocumented]
sources:
  - url: "https://arxiv.org/abs/2310.06770"
    title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
    accessed: "2026-09-08"
  - url: "https://www.swebench.com/"
    title: "SWE-bench project overview"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice M"
  reviewed: ""
  reviewed_by: ""
---

Part of the [SWE-bench](swe_bench.md) family.

## What it measures

`swe_bench_agent` is a benchmark key that appears in 61 of this repository's model cards, always next to a
`swe_bench_verified` score for the same model, but it is not a benchmark published anywhere under that
name by SWE-bench's authors or anyone else this research could find. The only definition located is a
code comment in this repository's own model-card template: "agentic SWE-bench (not just patch gen),"
filed under an "Agentic" section alongside `tau_bench`, `web_arena` and `os_world`. Across all 61 cards,
the `swe_bench_agent` score is lower than the same card's `swe_bench_verified` score every time, by
roughly 6 to 18 points (about 76-90% of the Verified value) — too consistent to be noise — but no card's
`benchmark_notes` explains the protocol, and `benchmark_source` lists only generic aggregator tags, not a
citable origin.

## Reading the numbers

Treat a `swe_bench_agent` number as internally consistent but externally undocumented: useful for ranking
models against each other within this repository, since it behaves the same way (always below Verified)
for every model that reports it, but not a figure to quote outside this repository as though it named a
publicly specified SWE-bench variant. Whether it denotes an agentic harness run on Verified's 500 tasks, a
different instance set entirely, or something else again was not established; the direction of the gap is
the only well-supported fact here, not its cause.
