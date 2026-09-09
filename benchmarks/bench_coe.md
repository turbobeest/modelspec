---
id: bench_coe
name: "Bench-CoE"
page_kind: benchmark
category: composite
summary: "Bench-CoE evaluates routing and collaboration among specialist language and multimodal experts using benchmark-derived training data."
measures: "Bench-CoE studies whether a router can assign each query to suitable expert models and improve aggregate performance through collaboration. It covers language and multimodal tasks under query-level and subject-level routing settings."
task_format: "A mixture of language and multimodal benchmark queries routed to specialist experts."
metric:
  name: task performance
  direction: higher_is_better
  unit: score
  baseline_note: "The paper compares the collaborative system with individual experts; a universal maximum is not established."
dataset:
  modalities: [text, image]
  public_test_set: null
publisher:
  org: "Bench-CoE authors"
  authors: [Yuanshuai Wang, Xingjian Zhang, Jinkun Zhao, Siwei Wen, Peilin Feng, Shuhao Liao, Lei Huang, Wenjun Wu]
  url: https://arxiv.org/abs/2412.04167
paper:
  title: "Bench-CoE: a Framework for Collaboration of Experts from Benchmark"
  arxiv: "2412.04167"
  url: https://arxiv.org/abs/2412.04167
  year: 2024
repo_url: https://github.com/ZhangXJ199/Bench-CoE
released: "2024-12"
saturation:
  status: unknown
  note: "The paper proposes a framework and reports experiments; a ceiling is not established."
contamination:
  risk: unknown
  note: "The consulted paper does not establish contamination of its benchmark queries."
harness:
  other: "Official Bench-CoE code and the benchmark datasets named by the paper."
tags: [mixture-of-experts, routing, multimodal]
sources:
  - url: https://arxiv.org/abs/2412.04167
    title: "Bench-CoE paper and abstract"
    accessed: "2026-09-08"
  - url: https://github.com/ZhangXJ199/Bench-CoE
    title: "Official Bench-CoE repository"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-003 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

Bench-CoE is a framework for evaluating collaboration among expert models. A router receives a query and selects an expert or experts suited to the task. The paper studies both query-level routing and subject-level routing.

Its experiments span language and multimodal tasks. The object of measurement is aggregate task performance under routing, compared with the performance of individual experts. It is consequently a composite evaluation framework rather than one fixed skill test.

## How it is scored

The paper compares the collaborative system with single expert models across varied data distributions. The metric is the score of each underlying task and the resulting overall performance; the sources consulted here do not define one universal scale, random baseline, or human baseline. Comparisons must preserve the task mix, expert pool, routing granularity, and modality.

## Dataset and licence

Bench-CoE uses benchmark data to train or evaluate the router and reports language and multimodal experiments. The paper does not establish one dataset size or one licence covering all component benchmarks. The exact split composition and answer visibility are therefore unknown in this record. Consult the official repository before reproducing a reported aggregate.

## Who publishes it

Yuanshuai Wang, Xingjian Zhang, Jinkun Zhao, Siwei Wen, Peilin Feng, Shuhao Liao, Lei Huang, and Wenjun Wu introduced Bench-CoE in a December 2024 arXiv paper. The authors link code from the paper to the ZhangXJ199/Bench-CoE repository. No independent leaderboard is established by the sources consulted.

## Lineage

Bench-CoE is a standalone framework benchmark entry. It draws on existing language and multimodal benchmarks, but the paper does not name a single predecessor or successor benchmark. The underlying component datasets should be cited separately when reporting a result.

## Saturation and contamination

The paper reports that collaboration can outperform any single model in its experiments, but it does not establish that the tasks have reached a ceiling. Saturation is therefore unknown. The component benchmark data are public or externally sourced in varying ways, and the paper does not establish model-training contamination; risk remains unknown.

## How to run it

Start with the official repository. Fix the expert pool, router training data, query-level or subject-level strategy, task mixture, and language or multimodal split. Evaluate each component task with its native scorer, then report the aggregation rule and the single-expert baselines. These choices can materially change the combined score.

## Reading the numbers

A higher aggregate indicates that routing selected useful specialists for the tested mixture. It does not show that the router generalizes to unseen domains, experts, or modalities. Inspect per-task results and routing decisions, because a gain can come from a favorable task mix. Report individual-expert baselines and the exact component datasets with every aggregate.
