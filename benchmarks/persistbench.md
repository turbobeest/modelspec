---
id: persistbench
name: PersistBench
aliases:
  - PersistBench
  - persistbench_cross_domain
  - persistbench_sycophancy
  - persistbench_beneficial_memory
page_kind: benchmark
category: safety
subcategory: long-term memory leakage, sycophancy, and useful recall
status: active
summary: >
  500 memory-and-query samples that score whether a model leaks, sycophantically
  agrees with, or correctly uses injected long-term user memories.
measures: >
  PersistBench prepends a synthetic long-term memory block to a new user query
  and asks whether the model uses those memories appropriately. Cross-domain
  items plant memories from one life domain next to a query from another.
  Sycophancy items plant user beliefs next to a query that should stay
  objective. Beneficial-memory items plant facts the model should actually use.
  The benchmark targets assistants that inject persistent user notes into the
  system prompt, not retrieval accuracy on a long dialogue log.
task_format: >
  Single-turn chat: system prompt contains a memory list, user message is the
  query. Cross-domain and sycophancy default to three generations per sample
  (max-score reducer). Beneficial memory defaults to one generation. An LLM
  judge scores the response; inspect_evals reports failure_rate.
metric:
  name: failure_rate (percent of samples over a judge threshold)
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Higher failure_rate is worse. Paper abstract medians across 18 models: 53%
    cross-domain leakage and 97% sycophancy. Sorting Table 2's beneficial column
    yields a 16.5% median under the paper's scoring. inspect_evals replication
    (version 2-A, February 2026) for Llama-3.3-70B: 25.0 / 85.0 / 54.0 versus
    paper 17.5 / 82.0 / 55.0; for gpt-oss-120b: 53.0 / 99.0 / 22.0 versus
    59.5 / 96.5 / 20.0.
dataset:
  size: 500
  size_note: >
    200 cross-domain, 200 sycophancy, and 100 beneficial-memory samples, all
    human-reviewed. Memories per sample range from 4 to 16 after expansion.
    inspect_evals ships the same three JSONL files. The authors' GitHub also
    has benchmark_samples/full_benchmark.jsonl.
  url: https://github.com/ivaxi0s/PersistBench
  license: "Paper CC BY 4.0; inspect_evals tree MIT; the authors' GitHub pyproject states no dataset licence"
  languages:
    - en
  modalities:
    - text
  splits: "three fixed task files; no train/test split"
  public_test_set: true
publisher:
  org: "Supervised Program for Alignment Research (SPAR), University of Cambridge, and CISPA Helmholtz Center for Information Security"
  authors:
    - Sidharth Pulipaka
    - Oliver Chen
    - Manas Sharma
    - Taaha S Bajwa
    - Vyas Raina
    - Ivaxi Sheth
  url: https://github.com/ivaxi0s/PersistBench
paper:
  title: "PersistBench: When Should Long-Term Memories Be Forgotten by LLMs?"
  arxiv: "2602.01146"
  url: https://arxiv.org/abs/2602.01146
  year: 2026
leaderboard_url: ""
repo_url: https://github.com/ivaxi0s/PersistBench
released: "2026-02"
last_updated: "2026-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2026-06"
  note: >
    Sycophancy failure is near ceiling for most of the 18 models (median 97%).
    Cross-domain leakage still spreads (paper range 4.0% GPT-5.2 to 91.0%
    Qwen3-235B-A22B-thinking). Beneficial memory is a different axis and does
    not track the two safety rates. No single aggregate top score is defined.
contamination:
  risk: medium
  note: >
    Items are synthetic, generated with MCTS and human review, not scraped
    exams. The JSONL has been public since 2026, so later training runs can
    see the exact memories and queries. There is no hidden label file; the
    judge is the labeler.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No single inspect task named persistbench. Runnable names are
    inspect_evals/persistbench_cross_domain,
    persistbench_sycophancy, and persistbench_beneficial_memory. Default judge
    is openrouter/moonshotai/kimi-k2-thinking at temperature 0. The authors
    recommend the inspect_evals port over ivaxi0s/PersistBench for new runs.
    Cross-domain and sycophancy judge 1-5 (higher = worse). inspect beneficial
    1-3 treats higher as better use and defines failure as 100% minus share
    with score >= 3. The paper describes beneficial 1=full use, 2=partial,
    3=none and treats scores >= 2 as failures. Those two beneficial encodings
    are not the same; compare inspect numbers to the paper only per task.
tags:
  - long-term-memory
  - sycophancy
  - privacy-adjacent
  - llm-judge
  - safety
sources:
  - url: https://arxiv.org/abs/2602.01146
    title: "PersistBench paper abstract (arXiv:2602.01146, ICML 2026)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2602.01146
    title: "PersistBench paper HTML (500 samples, medians, judge protocol)"
    accessed: "2026-09-08"
  - url: https://github.com/ivaxi0s/PersistBench
    title: "Official PersistBench repository README"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/persistbench/README.md
    title: "inspect_evals PersistBench README (task names, failure_rate, replication table)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/persistbench/eval.yaml
    title: "inspect_evals persistbench eval.yaml"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE
    title: "inspect_evals MIT licence"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-018 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-018"
---

## What it measures

PersistBench tests a model that has been given a block of long-term user memories in the system prompt. Cross-domain items check whether memories from one domain leak into an unrelated query. Sycophancy items check whether stored beliefs pull the model off an objective answer. Beneficial-memory items check that the model still uses memories when they are actually needed. The authors generated candidates with MCTS, validated them on held-out models, expanded memory lists, and had humans review every sample.

## How it is scored

An LLM judge (Kimi K2 Thinking in both the paper and inspect_evals) marks each response. Cross-domain and sycophancy use a 1-5 severity scale; a sample fails if any of three generations is at least 3. inspect_evals reports that rate as `failure_rate` (higher is worse). Beneficial memory uses a 1-3 use scale. The paper and inspect_evals do not encode that 1-3 scale the same way; see harness notes. Reasoning traces must not be in the judged text.

## Dataset and licence

Five hundred English samples: 200 / 200 / 100. The arXiv HTML carries a CC BY 4.0 badge. inspect_evals is MIT. The authors' GitHub pyproject does not declare a dataset licence.

## Who publishes it

Sidharth Pulipaka, Oliver Chen, Manas Sharma, and Taaha S Bajwa led the work under SPAR, with Vyas Raina (Cambridge) and Ivaxi Sheth (CISPA). arXiv:2602.01146 appeared 1 February 2026 (v2 2 June 2026) and is marked ICML 2026. Code is at ivaxi0s/PersistBench; the authors point new users to the inspect_evals port.

## Lineage

The paper contrasts PersistBench with LoCoMo and LongMemEval (recall/personalization) and with CIMemories (contextual integrity of stored attributes). None of those have pages in this repository. It is not a subset of [helm_safety](helm_safety.md).

## Saturation and contamination

Sycophancy is already near 100% failure for many models, so it barely ranks them. Cross-domain leakage still ranks. Samples are public synthetic JSONL from 2026, so later pretraining can see them, but they are not old exam items.

## How to run it

Preferred: `inspect eval inspect_evals/persistbench_cross_domain` (and the two sibling tasks), or `inspect eval-set` on all three. The authors' CLI is `benchmark generate` / `benchmark run`. Always name the task; there is no combined persistbench score in inspect_evals. Keep the judge model fixed if you compare to the paper.

## Reading the numbers

A low cross-domain failure rate means the model ignored off-topic memories, not that it has no memory. A low sycophancy failure rate is rare in the paper's 18-model table. Beneficial-memory success can coexist with terrible safety rates; the paper finds those axes only weakly correlated. Do not average the three tasks into one number unless you state the mix. Compare inspect `failure_rate` to the paper only per task, and watch the beneficial 1-3 encoding.
