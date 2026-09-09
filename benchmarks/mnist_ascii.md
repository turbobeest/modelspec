---
id: mnist_ascii
name: "ASCII MNIST"
aliases:
  - "BIG-bench mnist_ascii"
page_kind: subset
category: multimodal
subcategory: "ASCII-art digit recognition"
status: unknown
summary: "A BIG-bench task that asks a model to identify MNIST digits rendered as ASCII art."
measures: >
  The task converts MNIST digit images into ASCII art and asks which digit is shown.
  The input is text arranged as a visual pattern, so the task probes whether a
  language model can switch from language processing to simple visual layout reading.
task_format: "Ten-way multiple choice over digit labels 0 through 9; BIG-bench preferred metric is multiple_choice_grade."
metric:
  name: "multiple_choice_grade"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 10.0
  human_baseline: null
  baseline_note: "Ten digit labels imply 10% uniform-choice chance; no human score was published in the task README."
dataset:
  size: 69984
  size_note: "The BIG-bench task README header reports 69,984 multiple-choice queries."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/mnist_ascii"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "Single fixed task set; no train/test split"
  public_test_set: true
publisher:
  org: "Google BIG-bench"
  authors:
    - "Ethan Dyer"
    - "Adam R. Brown"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/mnist_ascii"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/mnist_ascii"
released: "2021"
last_updated: ""
lineage:
  family: "big_bench"
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "The task README says Google-internal models failed, but no current leaderboard cell was established."
contamination:
  risk: medium
  note: "The task is public and contains fixed ASCII renderings. BIG-bench embeds a canary string, but no measured contamination study was opened."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "mnist_ascii"
  other: ""
tags:
  - big-bench
  - subset
  - ascii
  - mnist
  - visual-reasoning
sources:
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/mnist_ascii/README.md"
    title: "BIG-bench mnist_ascii README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/LICENSE"
    title: "BIG-bench Apache License"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "BIG-bench paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-batch-059 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, luna-batch-059"
---

Part of the [BIG-bench](big_bench.md) family.

## What it measures

mnist_ascii renders MNIST digit images as ASCII art and asks the model to identify the digit. The pattern is text on a page, but success requires reading its spatial shape. It is a fixed BIG-bench task rather than a conventional image-input benchmark.

## Reading the numbers

There are ten digit choices, so chance is 10%. A high score means the model recognized the rendered digit under this font and formatting. It does not establish general image recognition or robustness to another ASCII renderer. The task README reports that Google-internal models failed, but no current frontier score was established here.

Formatting is part of the task definition: changing the font, spacing, or line width can change the visual signal. Scores should therefore be compared only when the renderer and prompt wrapper are held constant. The benchmark also says little about recognizing natural images because the input contains no pixels.
