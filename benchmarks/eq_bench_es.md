---
id: eq_bench_es
name: "EQ-Bench (Spanish)"
aliases:
  - "EQ-bench_es"
page_kind: subset
category: reasoning
subcategory: "emotional and social intelligence (dialogue emotion-intensity prediction), Spanish translation"
status: active
summary: "Spanish translation and cultural adaptation of EQ-Bench version 2's 168-171 question emotion-intensity rating task, released by the Barcelona Supercomputing Center."
measures: >
  eq_bench_es shows a model a short dialogue translated and culturally adapted into Spanish, then
  asks it to rate the intensity (0-10) of four named emotions one character is likely feeling at the
  end of the scene -- the same task format as English EQ-Bench. The Barcelona Supercomputing
  Center's Language Technologies Unit produced the adaptation: converting adjectival emotion labels
  to nominal forms to avoid Spanish grammatical-gender ambiguity (e.g. "proud" to "orgullo"),
  replacing Anglo-Saxon character names with Spanish ones, and unifying emotion labels that were
  equivalent but differently inflected in the English original.
task_format: >
  Given a Spanish dialogue and four named emotions, output an intensity rating from 0 to 10 for each
  in a fixed format; scored by the same distance-from-reference formula as EQ-Bench v2 (see the
  family page). lm-evaluation-harness runs it as task `eqbench_es`, generating greedily at
  temperature 0.
metric:
  name: "EQ-Bench score (distance from reference ratings)"
  direction: higher_is_better
  unit: "points"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    Uses EQ-Bench v2's unnormalized scoring: small per-emotion differences from the reference are
    scaled down on an S-shaped curve, larger differences count 1:1, and the total is inverted and
    rescaled so 0 corresponds to a random answer and 100 to matching the reference exactly. The
    lm-evaluation-harness `calculate_score_fullscale` function for this task is, line for line, the
    same scoring function the English `eq_bench` v2 task uses -- confirmed by reading both utils.py
    files directly -- which is the basis for calling this a v2-based translation rather than v1.
dataset:
  size: 168
  size_note: >
    168 rows in a single Hugging Face "test" split (confirmed via the datasets-server size API).
    That is close to, but not exactly, the 171-question English v2 set the dataset card names as its
    source; a handful of items were evidently dropped, merged or failed adaptation during
    translation. No separate train split exists.
  url: "https://huggingface.co/datasets/BSC-LT/EQ-bench_es"
  license: "CC BY 4.0"
  languages:
    - es
  modalities:
    - text
  splits: "single 168-row test split; no train split"
  public_test_set: true
publisher:
  org: "Barcelona Supercomputing Center (BSC), Language Technologies Unit"
  authors: []
  url: "https://huggingface.co/BSC-LT"
paper:
  title: "EQ-Bench: An Emotional Intelligence Benchmark for Large Language Models"
  arxiv: "2312.06281"
  url: "https://arxiv.org/abs/2312.06281"
  year: 2023
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/BSC-LT/EQ-bench_es"
released: "2025-06"
last_updated: ""
lineage:
  family: eq_bench
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "Not established from a source read for this page; no dedicated Spanish EQ-Bench leaderboard was found, and this repository's model cards were not checked for reported eqbench_es scores."
contamination:
  risk: medium
  note: >
    Public on Hugging Face since June 2025 under a permissive licence, with no held-out portion or
    canary string found in the dataset card. No source read for this page documents actual
    memorization by any model.
harness:
  lm_eval: "eqbench_es"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >-
    Confirmed directly in lm-evaluation-harness:
    lm_eval/tasks/eq_bench/multilingual/eqbench_es.yaml sets task: eqbench_es (metadata version
    1.0), reads dataset_path: BSC-LT/EQ-bench_es, and reuses the shared multilingual utils.py's
    calculate_score_fullscale scorer -- the same function the English v2 eq_bench task uses.
tags:
  - emotional-intelligence
  - social-cognition
  - spanish
  - subset
  - translation
sources:
  - url: "https://huggingface.co/datasets/BSC-LT/EQ-bench_es"
    title: "BSC-LT/EQ-bench_es dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/BSC-LT/EQ-bench_es"
    title: "BSC-LT/EQ-bench_es, Hugging Face Hub API (licence tag, arxiv tag)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=BSC-LT/EQ-bench_es"
    title: "BSC-LT/EQ-bench_es row count, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/eq_bench/multilingual/eqbench_es.yaml"
    title: "lm-evaluation-harness: eqbench_es task config"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/eq_bench/multilingual/utils.py"
    title: "lm-evaluation-harness: eq_bench multilingual utils.py (calculate_score_fullscale)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice E"
  reviewed: ""
  reviewed_by: ""
---

Part of the [EQ-Bench](eq_bench.md) family.

## What it measures

eq_bench_es is a Spanish translation and cultural adaptation of EQ-Bench, built by the Barcelona Supercomputing Center's Language Technologies Unit from the same dialogue-rating format as the English original. A model reads a short scene of interpersonal conflict and rates the intensity of four named emotions one character is likely feeling. The adapters reworked emotion labels to sidestep Spanish grammatical gender, swapped in Spanish character names, and merged labels that were duplicates of each other once inflection was normalized. The scoring function bundled with the lm-evaluation-harness task is identical to the one the English `eq_bench` v2 task uses, which is the clearest evidence this translation targets EQ-Bench version 2 (171 questions) rather than the smaller version 1 (60 questions) described in the original paper.

## Reading the numbers

A score here measures the same narrow, reference-matching skill as English EQ-Bench v2, applied to Spanish text -- not general Spanish fluency and not the publisher's newer, unrelated EQ-Bench 3/4 roleplay methodology, which has no Spanish port found for this page. Because the item count (168) does not exactly match the 171-question English source, treat this as a distinct, separately-scored artifact rather than a strict translation with guaranteed comparability to English eq_bench numbers.
