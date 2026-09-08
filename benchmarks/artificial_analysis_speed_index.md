---
id: artificial_analysis_speed_index
name: "Artificial Analysis Output Speed"
aliases:
  - "Artificial Analysis Speed Index"
  - "AA Output Speed"
  - "Output Tokens per Second"
page_kind: benchmark
category: composite
subcategory: "inference throughput / output speed"
status: active
summary: "Artificial Analysis's live-measured output speed for a model's API: tokens generated per second, a performance measure, not a correctness or quality score."
measures: >
  This page documents Artificial Analysis's Output Speed metric — the throughput figure the
  publisher headlines under "Speed" on its own site — as this repository's
  artificial_analysis_speed_index. It is a pure performance measurement, not a capability or
  correctness score: Artificial Analysis sends a live prompt to a model's public API and times how
  many tokens per second stream back after the first token arrives. Unlike the Intelligence Index,
  Artificial Analysis does not publish a single blended "Speed Index" combining multiple timing
  metrics into one number; Output Speed is reported alongside, not merged with, separate metrics
  for time to first token and end-to-end response time. Workloads vary by input length (about
  1,000, 10,000 or 100,000 input tokens, plus a vision workload of one megapixel image and roughly
  1,000 text tokens) because both time-to-first-token and output speed itself shift with prompt
  length and technique such as speculative decoding.
task_format: >
  Live API calls: Artificial Analysis sends standardized, freshly generated prompts of a fixed
  input-token length to a model's public endpoint and streams the response, timing token arrivals
  to derive tokens-per-second and latency figures.
metric:
  name: "Output Speed (output tokens/second)"
  direction: higher_is_better
  unit: "tokens/second"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No fixed maximum or baseline: output speed is an uncapped, provider- and hardware-dependent
    throughput measurement, not a score against a fixed answer key. Higher is better because it
    means faster generation, in contrast with Artificial Analysis's latency metrics (time to first
    token, end-to-end response time), which are lower-is-better.
dataset:
  size: null
  size_note: >
    Not a fixed dataset: prompts are freshly generated for each test run from a mix of long-form
    source content (such as articles) paired with a task — summarization, question generation,
    comparative analysis, translation or visual-artifact generation — sized to hit the target
    input-token budget for that workload (about 1k, 10k or 100k tokens, or a vision workload).
  url: "https://artificialanalysis.ai/downloads/methodology/performance-prompts.xlsx"
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
  status: open
  top_score: null
  as_of: ""
  note: >
    An uncapped throughput measurement has no fixed ceiling; specialised inference hardware
    providers continue to post materially higher output speeds than typical general-purpose API
    hosting, so the field keeps separating rather than converging. No single current top-speed
    figure was captured in numeric form from a source read for this page.
contamination:
  risk: low
  note: >
    Not applicable in the train/test sense: this measures live infrastructure performance rather
    than a model's response to a knowable question set, so there is nothing for a model to have
    memorized in advance. The comparable integrity risk is a provider serving Artificial
    Analysis's own traffic differently from ordinary traffic, which Artificial Analysis addresses
    through published Integrity Terms rather than dataset controls.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No independent harness. Artificial Analysis tests each endpoint itself, roughly every 3 hours
    for standard workloads (once daily for a 10-parallel-prompt load test, once weekly for the
    100k-token workload), using the official OpenAI Python client for OpenAI-compatible APIs and
    each provider's own recommended client otherwise, from a primary server in Google Cloud's
    us-central1-a zone.
tags:
  - composite
  - performance
  - throughput
  - artificial-analysis
sources:
  - url: "https://artificialanalysis.ai/methodology/performance-benchmarking"
    title: "Artificial Analysis Language Model API Performance Benchmarking Methodology"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/"
    title: "Artificial Analysis (homepage, Speed & Latency section)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice J"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

This page documents Artificial Analysis's Output Speed metric — the throughput figure the
publisher headlines under "Speed" on its own site — as this repository's
`artificial_analysis_speed_index`. It is a pure performance measurement, not a capability or
correctness score: Artificial Analysis sends a live prompt to a model's public API and times how
many tokens per second stream back after the first token arrives. Unlike the Intelligence Index,
Artificial Analysis does not publish a single blended "Speed Index" combining multiple timing
metrics into one number; Output Speed is reported alongside, not merged with, separate metrics for
time to first token and end-to-end response time. Workloads vary by input length — about 1,000,
10,000 or 100,000 input tokens, plus a vision workload of one megapixel image and roughly 1,000
text tokens — because both time-to-first-token and output speed itself shift with prompt length
and technique such as speculative decoding.

## How it is scored

Output Speed is the average number of tokens received per second, counted from after the first
streamed chunk arrives to the last: total tokens minus first-chunk tokens, divided by the elapsed
time between the first and last chunk. Standard workloads are tested roughly every three hours; a
10-concurrent-request parallel-load workload runs once a day, and the 100k-input-token workload
runs once a week. Reported figures are the median (P50) across the trailing 72 hours, except the
100k workload, which uses a trailing 14-day median. Tokens are counted with OpenAI's `o200k_base`
tokenizer for every model, specifically so speeds are comparable across models with different
native tokenizers. Figures represent a model's first-party API where one exists, or the median
across providers when it does not.

## Dataset and licence

There is no fixed benchmark dataset: every test run uses a freshly generated prompt built from
long-form source content paired with a task — summarization, question generation, comparative
analysis, translation or visual-artifact generation — sized to hit the target input-token budget
for that workload. Artificial Analysis publishes its prompt-generation approach and a downloadable
set of reasoning-token-estimation prompts on its methodology page. No formal licence for this
prompt set or for Artificial Analysis's own speed measurements was established from a source read
for this page.

## Who publishes it

Artificial Analysis, the same independent benchmarking company behind the Intelligence Index,
designs and runs this measurement itself against providers' public endpoints; no third-party or
academic co-author was credited on the methodology page read for this page.

## Lineage

Output Speed has no separate predecessor or successor of its own; it is one of several performance
metrics — alongside time to first token, total response time for 100 output tokens, and
end-to-end response time — documented on the same Performance Benchmarking methodology page and
revised together, most recently in a March 2026 update that changed the default workload from
1,000 to 10,000 input tokens and refreshed the prompt set. It belongs to the `artificial_analysis`
family alongside `artificial_analysis_quality_index`. Artificial Analysis's related Endpoint
Accuracy Index, which scores how much of a model's accuracy a specific provider endpoint
preserves, is a distinct, accuracy-focused metric with no page in this repository yet.

## Saturation and contamination

An uncapped throughput measurement does not saturate the way an accuracy score does: there is no
maximum tokens-per-second ceiling, and specialised inference hardware providers continue to post
materially higher output speeds than typical general-purpose API hosting, so the field keeps
separating rather than converging. Contamination in the train/test sense does not apply, since
this measures live infrastructure performance rather than a model's response to a knowable
question set. The comparable integrity risk is a provider serving Artificial Analysis's own
traffic differently from ordinary customer traffic; Artificial Analysis addresses this with
published Integrity Terms that bar detecting and special-casing its traffic, and it reserves the
right to re-test from independent accounts, withhold results, or delist a provider that fails
compliance checks.

## How to run it

There is no independent harness a third party runs; Artificial Analysis tests every endpoint
itself from a primary server in Google Cloud's `us-central1-a` zone, using the official OpenAI
Python library for OpenAI-compatible APIs and each provider's recommended client otherwise.
Because time-to-first-token specifically is sensitive to network distance from that single test
location, Artificial Analysis's own methodology page names server location as a known limitation
of the comparison.

## Reading the numbers

A high Output Speed number means a model's API streams answer tokens quickly once it starts
responding — it says nothing about whether those tokens are correct, so read it alongside a
capability figure such as `artificial_analysis_quality_index` rather than in isolation. Speed for
the same model can vary a great deal by provider and hosting configuration, which is why
Artificial Analysis reports it per endpoint rather than once per model; check time to first token
separately, since a model can stream quickly once started but still feel slow to a user if it
takes a long time to begin. Prefer figures measured at the input-token length closest to your own
real workload, since both speed and time-to-first-token shift with prompt length.
