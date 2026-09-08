---
id: bbeh
name: "BIG-Bench Extra Hard (BBEH)"
aliases:
  - "BBEH"
page_kind: benchmark
category: reasoning
subcategory: "extra-hard multi-step reasoning suite, BBH successor"
status: active
summary: "Replaces each of BBH's 23 tasks with a substantially harder variant of the same reasoning skill, calibrated so two strong 2025 reference models both scored under 70%."
measures: >
  BIG-Bench Extra Hard (BBEH) takes the same 23 task categories BIG-Bench Hard (BBH) uses --
  logical deduction, causal judgement, object tracking and counting, spatial and temporal
  reasoning, disambiguation, and several more -- and replaces every one of BBH's individual tasks
  with a new, harder task designed to probe the same underlying reasoning skill. The authors built
  each replacement task iteratively, testing candidate items against two Google reference models
  (Gemini 1.5 Flash and a Gemini "Thinking Experimental" model) and refining until both scored
  below 70% accuracy, so difficulty is calibrated against contemporary models rather than guessed.
  The result targets the same reasoning categories as BBH while addressing the saturation BBH
  itself had started to show against increasingly strong models.
task_format: "A mix of multiple-choice and free-response prompts across 23 tasks, mirroring BBH's task categories but with harder instances; most are answered directly or via chain-of-thought prompting before a final extracted answer."
metric:
  name: "harmonic mean accuracy across the 23 tasks (classic micro-average accuracy recommended for the smaller Mini split)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 8.4
  human_baseline: null
  baseline_note: "Random guessing scores 8.4% harmonic mean accuracy across the suite. The authors use harmonic mean (adjusted by adding 1 to each task's accuracy to handle zero scores) specifically to penalize a model that does well on easy tasks while failing others completely, rather than letting a plain average smooth over that failure."
dataset:
  size: 4520
  size_note: "4,520 examples across 23 tasks: 200 examples per task, except Disambiguation QA at 120. A separate BBEH Mini split provides 460 examples (20 per task) for cheaper evaluation runs."
  url: "https://github.com/google-deepmind/bbeh"
  license: "Apache-2.0 (evaluation code); CC BY 4.0 International (other materials)"
  languages: ["en"]
  modalities: ["text"]
  splits: "no train/test split; each task is a single fixed evaluation set (full: 200/task, 120 for Disambiguation QA; Mini: 20/task)"
  public_test_set: true
publisher:
  org: "Google DeepMind"
  authors: ["Mehran Kazemi", "Bahare Fatemi", "Hritik Bansal", "John Palowitch", "Chrysovalantis Anastasiou", "and 15 other authors (20 total)"]
  url: "https://github.com/google-deepmind/bbeh"
paper:
  title: "BIG-Bench Extra Hard"
  arxiv: "2502.19187"
  url: "https://arxiv.org/abs/2502.19187"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/google-deepmind/bbeh"
released: "2025-02"
last_updated: ""
lineage:
  family: ""
  predecessor: "bbh"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 44.8
  as_of: "2025-02"
  note: "BBEH is far from saturated by design: a random-guess baseline scores 8.4% harmonic mean accuracy, the best general-purpose model the authors tested reached only 9.8%, and the best reasoning-specialized model they tested reached 44.8% -- all well below any ceiling, which is the point, since each task was calibrated so that two strong 2025 reference models scored under 70%."
contamination:
  risk: low
  note: "Released in February 2025, so unlikely to appear in the pretraining data of models trained and released before that date; no dedicated contamination study was found in the sources consulted. The calibration methodology (hardening any candidate item two strong reference models could already solve) also works against simple memorization mattering much, since items were selected specifically to resist the strategies available to strong contemporary models."
harness:
  lm_eval: ""
  inspect_evals: "bbeh"
  helm: ""
  opencompass: "bbeh"
  bigbench: ""
  other: "No lm-evaluation-harness task was found for BBEH as of this research (the lm_eval/tasks/bbeh path returned 404)."
tags: ["reasoning", "multi-task", "chain-of-thought", "bbh-successor", "hard"]
sources:
  - url: "https://arxiv.org/abs/2502.19187"
    title: "BIG-Bench Extra Hard"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.19187"
    title: "BIG-Bench Extra Hard (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/google-deepmind/bbeh"
    title: "google-deepmind/bbeh repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/bbeh/main/README.md"
    title: "google-deepmind/bbeh README"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/bbeh"
    title: "inspect_evals bbeh task directory"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/bbeh"
    title: "OpenCompass bbeh dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BIG-Bench Extra Hard (BBEH) takes the same 23 task categories BIG-Bench Hard (BBH) uses -- logical deduction, causal judgement, object tracking and counting, spatial and temporal reasoning, disambiguation, and several more -- and replaces every one of BBH's individual tasks with a new, harder task designed to probe the same underlying reasoning skill. The authors built each replacement task iteratively, testing candidate items against two Google reference models (Gemini 1.5 Flash and a Gemini "Thinking Experimental" model) and refining until both scored below 70% accuracy, so difficulty is calibrated against contemporary models rather than guessed. The result targets the same reasoning categories as BBH while addressing the saturation BBH itself had started to show against increasingly strong models.

## How it is scored

Each of the 23 tasks contributes 200 examples (Disambiguation QA contributes 120), for 4,520 examples in total; the recommended headline metric is the harmonic mean of per-task accuracy, adjusted by adding 1 to each task's accuracy before averaging to handle tasks where a model scores zero, which the authors chose specifically to penalize models that do well on easy tasks in the suite while failing others completely, rather than letting an average smooth over that failure. A smaller BBEH Mini split (20 examples per task, 460 total) is intended for cheaper evaluation runs, and the authors recommend a plain micro-average (classic accuracy) for it instead of the harmonic mean. Reported context lengths and expected output lengths both run several times longer than BBH's on average, so BBEH is also a meaningfully more expensive benchmark to run per example.

## Dataset and licence

BBEH totals 4,520 examples in its full form (200 per task for 22 of the 23 tasks, 120 for Disambiguation QA) plus a 460-example Mini subset (20 per task). There is no train/test split; every example exists only to be evaluated once. The repository states dual licensing: Apache License 2.0 for the evaluation code, and Creative Commons Attribution 4.0 International (CC BY 4.0) for other materials, alongside a disclaimer that the release "is not an official Google product."

## Who publishes it

BBEH comes from a 20-author Google DeepMind team led by Mehran Kazemi, Bahare Fatemi, Hritik Bansal, John Palowitch and Chrysovalantis Anastasiou, published as "BIG-Bench Extra Hard" (arXiv, February 2025). The dataset and evaluation code are maintained at github.com/google-deepmind/bbeh rather than through a dedicated hosted leaderboard.

## Lineage

BBEH is a direct, task-for-task successor to [BIG-Bench Hard](bbh.md) (`bbh`): the paper's own framing is that it "replaces each task in BBH with a novel task that probes a similar reasoning capability but exhibits significantly increased difficulty," rather than introducing new reasoning categories. Both BBH and BBEH ultimately trace back to the much larger [BIG-bench](big_bench.md) collection, from which BBH was originally curated; BBEH's own tasks were purpose-built rather than pulled from BIG-bench directly. No successor or variant id is tracked for BBEH in this repository yet.

## Saturation and contamination

BBEH is far from saturated by design: a random-guess baseline scores 8.4% harmonic mean accuracy, the best general-purpose model the authors tested reached only 9.8%, and the best reasoning-specialized model they tested reached 44.8% -- all well below any ceiling, which is the point, since each task was calibrated so that two strong 2025 reference models scored under 70%. Because the benchmark was released in February 2025, it is unlikely to appear in the pretraining data of models trained and released before that date, and no dedicated contamination study was found in the sources consulted; the calibration methodology (discarding or hardening any candidate item both reference models could already solve) also works against simple memorization mattering much, since the tasks were selected specifically to resist the reasoning strategies available to strong contemporary models.

## How to run it

inspect_evals implements it as the `bbeh` task, and OpenCompass carries a generative configuration (`bbeh_gen`) alongside LLM-judge variants (`bbeh_llmjudge_gen`, `bbeh_llmjudge_rawprompt_gen`) for tasks whose free-form answers are hard to grade by exact match; no lm-evaluation-harness task was found for BBEH as of this research. Because the authors specifically recommend harmonic mean for the full split and micro-average for Mini, and because both LLM-judge and exact-match scoring variants exist in at least one harness, confirm which metric and which split a reported BBEH score used before comparing it across papers.

## Reading the numbers

Given how far even specialized reasoning models sit below the ceiling, any non-trivial BBEH score is a meaningful reasoning signal, and the gap between a "general-purpose" and a "reasoning-specialized" model's score (9.8% vs 44.8% for the authors' own best examples) is itself informative about whether extended reasoning or search at inference time helps on this kind of task. Because the suite pools 23 very different task types into one harmonic-mean number, a model's aggregate BBEH score can still hide large per-task gaps, so check the per-task table when it is available rather than trusting the aggregate alone. As a benchmark released in 2025 and explicitly calibrated against contemporary models, expect BBEH's ceiling to keep moving for some time yet.
