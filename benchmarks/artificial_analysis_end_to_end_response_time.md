---
id: artificial_analysis_end_to_end_response_time
name: "Artificial Analysis end-to-end response time"
aliases:
  - "AA End-to-End Response Time"
page_kind: subset
category: composite
subcategory: "API response latency, single request, no tools (latency stand-in)"
status: active
summary: "Artificial Analysis's time to receive one complete API response to a single request, with no tools. Not a tool-calling loop, and not your hardware."
measures: >
  Part of the [Artificial Analysis](artificial_analysis.md) family. Artificial Analysis defines
  End-to-End Response Time as "the total time to receive a complete response, including input
  processing time, model reasoning time, and answer generation time." It is measured per model
  and API endpoint, for one request with no tools.
task_format: >
  Live API calls to a provider endpoint with synthetic prompts. Workloads are about 1k, 10k
  (site default) or 100k input tokens, plus vision; load is single prompt or 10 parallel prompts.
metric:
  name: "End-to-End Response Time"
  direction: lower_is_better
  unit: "seconds"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "No maximum or baseline; an uncapped latency measurement."
dataset:
  size: null
  size_note: "No fixed dataset; prompts are generated per workload, per the methodology page."
  url: ""
  license: ""
  languages: []
  modalities:
    - text
    - image
  splits: ""
  public_test_set: null
publisher:
  org: "Artificial Analysis"
  authors: []
  url: "https://artificialanalysis.ai"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://artificialanalysis.ai/"
repo_url: ""
released: ""
last_updated: "2026-03"
lineage:
  family: artificial_analysis
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "Uncapped latency measurement. No per-model figure is recorded on this page."
contamination:
  risk: low
  note: "Live infrastructure measurement; there is no answer set to memorize."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Run by Artificial Analysis from a virtual machine in Google Cloud's us-central1-a zone.
tags:
  - latency
  - latency-stand-in
  - artificial-analysis
  - subset
sources:
  - url: "https://artificialanalysis.ai/methodology/performance-benchmarking"
    title: "Artificial Analysis API performance benchmarking methodology (definitions, location, frequency, P50 windows, v2.2.0 of 2 March 2026)"
    accessed: "2026-09-15"
  - url: "https://github.com/turbobeest/modelspec/blob/main/docs/agentic-latency-benchmark.md"
    title: "ModelSpec MODEL-57 spec for a measured agentic latency benchmark"
    accessed: "2026-09-15"
freshness:
  researched: "2026-09-15"
  researched_by: "Claude Opus 5, MODEL-62"
  reviewed: ""
  reviewed_by: ""
---

Part of the [Artificial Analysis](artificial_analysis.md) family.

## What it measures

Time to receive one complete API response, including input processing, reasoning and answer
generation. It covers one request to one endpoint, with no tools. The methodology page gives these
conditions. The primary test server is a virtual machine in Google Cloud's us-central1-a zone.
The 1k, 10k and vision workloads run 8 times per day, about every 3 hours. Results are the median
(P50) over the past 72 hours. The 100k workload runs weekly and uses a 14-day median. (The MODEL-57
survey recorded a 14-day window generally; the page read today limits that to the 100k workload.)

It is not a tool-calling loop. It excludes tool execution and repeated turns, and it does not
reflect your hardware or network location.

## Reading the numbers

A lower time means one full response arrives sooner from that endpoint, measured from
us-central1-a. Figures vary by provider and workload size. This is the model-side term of an agent
loop only. Never multiply it by SWE-bench step counts, or combine the two, to build a "loop
latency" number. No per-model scores are recorded in ModelSpec yet. This page is descriptive until
a measured benchmark meeting the [MODEL-57 spec](../docs/agentic-latency-benchmark.md) exists.
