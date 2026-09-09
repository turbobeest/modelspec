---
id: suicide_risk
name: "Estimating Risk of Suicide"
aliases:
  - "suicide_risk (BIG-bench)"
page_kind: benchmark
category: safety
subcategory: "clinical-style risk triage from short first-person text (BIG-bench task)"
status: active
summary: "A 50-item BIG-bench task asking a model to grade suicide risk in short Reddit-derived posts on a four-level scale against expert labels."
measures: >
  This task gives a model a short, first-person piece of text -- style and typos preserved -- and asks
  it to classify the author's suicide risk into one of four expert-defined levels: no risk, low risk,
  moderate risk, or severe risk. The texts were manually pulled from a public Reddit submission corpus
  and de-identified; some "no risk" items deliberately include emotionally charged or clinically
  sensitive keywords so that a model cannot pass by keyword-matching alone and must weigh context. The
  task's own documentation is explicit that it is a research probe of language understanding, not a
  validated screening tool, and that suicide-risk assessment "deserves careful and thoughtful research."
task_format: "Four-way multiple choice: given a short first-person text, classify author suicide risk as no/low/moderate/severe, scored zero-shot, one-shot, and many-shot."
metric:
  name: "multiple_choice_grade (accuracy against expert-assigned risk level)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four-way random guessing scores 25%. The task's own README reports that, as of its July 2021
    evaluation, tested models topped out around 30% accuracy (roughly GPT2-large in the one-shot
    setting) across zero-, one- and many-shot prompting, barely above chance, and that zero-shot
    performance was at or below chance for every model tested. No separate human-expert accuracy
    figure was found in the sources opened for this page, so `human_baseline` is left empty; the
    task's labels are themselves the expert assessments being matched, rather than a benchmarked
    human score on the same items.
dataset:
  size: 50
  size_note: >
    The task's live `task.json` file contains 50 labelled examples, distributed across the four risk
    levels (roughly 12-16 per level in the categories read from the file). This disagrees with the
    task's own README/documentation text, which describes "40 total (10 per risk level)"; this page
    read the actual data file rather than the prose description and records 50, flagging the
    discrepancy rather than picking one silently. With only 50 items, the task is designed for
    zero-/few-shot probing, not for training or for statistically robust ranking.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/suicide_risk"
  license: "Apache License 2.0 (BIG-bench repository licence; applies to the task code and data as distributed)"
  languages:
    - en
  modalities:
    - text
  splits: "single 50-example evaluation set; no train/validation/test split"
  public_test_set: true
publisher:
  org: "BIG-bench collaboration (Google-led); task authored by named contributors below"
  authors:
    - "Jekaterina Novikova"
    - "Ksenia Shkaruta"
  url: "https://github.com/google/BIG-bench"
paper:
  title: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/suicide_risk"
released: "2021-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The only performance data found in the sources opened for this page is the task's own July 2021
    note that models reached at most about 30% accuracy, close to the 25% random baseline. No later or
    frontier-model result was found, so this page cannot say whether current models have moved past
    that near-chance region; status is left `unknown` rather than guessed.
contamination:
  risk: unknown
  note: >
    The 50 items and their labels have been publicly hosted in the BIG-bench GitHub repository since
    2021, so simple memorisation of this exact file is possible for models trained on public GitHub
    data. No contamination study specific to this task was found in the sources consulted, so risk is
    left `unknown` rather than asserted from the public-hosting fact alone; the extremely small item
    count also limits how much a single memorised set would move a many-shot or held-out score either
    way.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "suicide_risk"
  other: ""
tags:
  - safety
  - mental-health
  - multiple-choice
  - bigbench
  - clinical
  - sensitive
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/suicide_risk"
    title: "BIG-bench: suicide_risk task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/suicide_risk/README.md"
    title: "BIG-bench suicide_risk task README (raw)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/suicide_risk/task.json"
    title: "BIG-bench suicide_risk task.json (raw data file, 50 examples)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench"
    title: "google/BIG-bench repository (Apache-2.0 licence)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-006"
---

## What it measures

This BIG-bench task gives a model a short piece of first-person text and asks it to classify the author's suicide risk into one of four expert-defined levels: no risk, low risk, moderate risk, or severe risk. The texts were manually extracted from a public Reddit submission corpus and de-identified, preserving original writing style, length variation, and typos rather than normalising the language. Several "no risk" items are deliberately written to include emotionally charged or clinically loaded keywords, so a model cannot pass by matching surface vocabulary alone -- it has to weigh the whole context of what the author is describing.

The task's authors are explicit that it is a research probe into whether a language model's judgment tracks expert human assessment, not a validated clinical screening instrument, and they frame suicide-risk work generally as deserving careful, cautious research rather than deployment.

## How it is scored

Each item is scored as four-way multiple choice against the expert-assigned label, using BIG-bench's standard `multiple_choice_grade` (accuracy), so random guessing scores 25%. The task supports zero-shot, one-shot, and many-shot prompting. As of the task's own July 2021 write-up, tested models performed close to chance across all three regimes -- the best result recorded was roughly 30% accuracy (one-shot), and zero-shot accuracy was at or below the 25% random baseline for every model tested, indicating the task was unsolved by the language models available at that time.

## Dataset and licence

The task's live data file (`task.json`) contains 50 labelled examples spread across the four risk categories. This is inconsistent with the task's own README, which describes the dataset as 40 items total, 10 per risk level; this page read the actual data file rather than repeating the prose description, and records 50 as the size while flagging the mismatch rather than silently resolving it. The BIG-bench repository as a whole is released under the Apache License 2.0, which covers this task's code and bundled data as distributed. With only 50 items and no train/validation/test split, the task is built for lightweight zero- and few-shot probing, not for training or for a statistically robust leaderboard-style comparison.

## Who publishes it

The task is credited to Jekaterina Novikova and Ksenia Shkaruta as part of BIG-bench (the Beyond the Imitation Game Benchmark), a large multi-task collaboration led by Google Research and described in "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (2022). BIG-bench as a whole has over 400 contributors across many institutions; this page did not find a narrower institutional affiliation for the two named task authors in the sources opened.

## Lineage

No predecessor, successor, or variant of this specific task was found in the sources opened for this page, and it has no family page in this repository. It sits within BIG-bench's broader cluster of tasks probing emotional and social understanding, several of which are catalogued separately in this repository, but none was confirmed as a direct lineage relative of `suicide_risk` itself.

## Saturation and contamination

The only performance evidence found is the task's own note that, as of July 2021, models reached at most about 30% accuracy against a 25% random baseline -- essentially unsolved at that point, not saturated. No later evaluation of frontier models against this specific task was found in the sources consulted, so this page cannot say whether current models have moved meaningfully past that near-chance region, and `saturation.status` is left `unknown` rather than assumed. Contamination risk is also left `unknown`: the 50 items and their labels have been publicly hosted on GitHub since 2021, which makes memorisation possible for models trained on public code-hosting data, but no dedicated contamination study for this task was found, and the tiny item count limits how much a single memorised set could move scores either way.

## How to run it

BIG-bench runs the task under its own name, `suicide_risk`, using the standard BIG-bench JSON task format and the `multiple_choice_grade` scoring function; no separate configuration in lm-evaluation-harness, HELM, OpenCompass, or inspect_evals was found in the sources opened for this page. Because the task ships as a single 50-example file rather than a maintained leaderboard, reproducing a reported number requires running the exact BIG-bench task version and shot count (zero/one/many) that the reporter used, since the task's own results already show large swings across those three settings.

## Reading the numbers

A model's score on this task says whether its risk judgments on 50 short, hand-picked texts track the two authors' expert labels -- nothing more, and nothing about real-world screening safety. The task was unsolved (near chance) as of its own 2021 evaluation; a much higher score from a modern model would be a meaningful signal of improved contextual judgment on this narrow slice, but with only 50 items the number is noisy and easy to move with a handful of items either way. Do not read a high score here as evidence a model is safe or reliable to use for actual suicide-risk assessment: the task's own authors built it as a research probe and explicitly warn against that use, and no source opened for this page describes any validation of the task against real clinical outcomes.
