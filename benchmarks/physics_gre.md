---
id: physics_gre
name: "Physics GRE (Inflection-Benchmarks)"
aliases:
  - "physics_gre_multiple_choice"
  - "GR8677"
  - "Inflection Physics GRE"
page_kind: benchmark
category: knowledge
subcategory: "five-way multiple-choice graduate Physics GRE items, image-free subset"
status: unknown
summary: "Processed Physics GRE exams scored as five-way multiple choice; lm-eval reports accuracy on image-free items, not Inflection's GRE percentile."
measures: >
  Physics GRE, in this id, is Inflection AI's processed copy of released Physics GRE forms, a
  graduate-school subject exam. Each item is a five-way (A-E) English physics question. Fields are
  `input` (stem with options inlined), `target_scores` (the correct letter scored 1), and `has_image`.
  Inflection scores only items without a diagram. The skill is whatever those released graduate
  entrance forms ask, as text-only multiple choice, not open-ended derivation and not high-school
  word problems.
task_format: >
  Multiple choice over letters A-E. Inflection sampled generations and took majority vote (maj@8 /
  maj@32), then mapped a GRE-style raw score to a percentile. lm-evaluation-harness instead ranks the
  five option letters by loglikelihood (`output_type: multiple_choice`) and reports mean `acc`. There
  is no `_generate_until` variant in that harness directory.
metric:
  name: "acc (lm-eval loglikelihood multiple-choice)"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: 0.2
  human_baseline: null
  baseline_note: >
    Five options give a 0.2 random-guess accuracy if every item is answered. Inflection does not
    publish an accuracy human baseline. It maps a GRE-style raw score ( +1 correct, -0.25 incorrect,
    no omit heuristic) on image-free items to an ETS-style percentile table (raw 81-100 maps to the
    98th percentile). Those percentiles are not interchangeable with lm-eval `acc`.
dataset:
  size: 75
  size_note: >
    Hugging Face `shayekh/physics_gre` test splits, counted via datasets-server and by reading the
    JSONL: `physics_gre` (GR8677, the scored exam) 100 rows; `physics_gre_additional` (GR9277,
    GR9677, GR0177) 300 rows; `physics_gre_all` 400 rows. In GR8677, 24 of 100 have `has_image` true
    and one image-free row has no option scored 1, so lm-eval `utils.process_docs` keeps 75. The
    additional file has 212 image-free rows, all with a gold letter. Inflection's README describes
    dropping images only; the extra gold-key filter is the harness.
  url: "https://huggingface.co/datasets/shayekh/physics_gre"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "HF configs physics_gre / physics_gre_additional / physics_gre_all, each with a test split only"
  public_test_set: true
publisher:
  org: "Inflection AI (processed exam files); Hugging Face mirror by shayekh; lm-eval task packaging by EleutherAI"
  authors: []
  url: "https://github.com/InflectionAI/Inflection-Benchmarks"
paper:
  title: "Inflection-Benchmarks"
  arxiv: ""
  url: "https://github.com/InflectionAI/Inflection-Benchmarks"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/InflectionAI/Inflection-Benchmarks"
released: "2024-03"
last_updated: "2024-04"
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
    Inflection's README table (opened 2026-09-08) reports GRE-style percentiles on image-free GR8677,
    not accuracy: Inflection-2.5 maj@8 85th, maj@32 95th, GPT-4 maj@8 97th. No lm-eval `acc` figure
    was read. Those percentiles sit near the top of Inflection's own raw-to-percentile map, but they
    are not a current-model `acc` ceiling and are not recorded as `top_score`. The data repo was
    archived on 2025-03-16; that is a repository status, not an `acc` result.
contamination:
  risk: high
  note: >
    The four processed forms, including answers, have been downloadable from Inflection-Benchmarks
    (repo created 2024-03-05) and from `shayekh/physics_gre` (HF created 2024-04-01). Released Physics
    GRE practice forms have circulated as exam prep for years. Inflection does not hold out answers.
harness:
  lm_eval: "physics_gre_multiple_choice"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Also physics_gre_additional_multiple_choice and physics_gre_all_multiple_choice; no lm-eval group named physics_gre"
tags:
  - physics
  - multiple-choice
  - graduate-exam
  - lm-eval
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/physics_gre/README.md"
    title: "lm-evaluation-harness physics_gre README (tasks, image-free scoring, acc vs maj@k)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/physics_gre/_physics_gre_template_yaml"
    title: "lm-eval physics_gre template YAML (multiple_choice, acc, shayekh/physics_gre)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/physics_gre/utils.py"
    title: "lm-eval physics_gre process_docs (drop has_image and missing gold)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/InflectionAI/Inflection-Benchmarks/main/README.md"
    title: "Inflection-Benchmarks README (four exams, maj@k percentiles, GRE raw-score formula)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/InflectionAI/Inflection-Benchmarks/main/LICENSE"
    title: "Inflection-Benchmarks MIT License (copyright 2024 Inflection AI)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/shayekh/physics_gre/raw/main/README.md"
    title: "Hugging Face shayekh/physics_gre dataset card (MIT, three configs)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=shayekh/physics_gre"
    title: "Hugging Face datasets-server split sizes (100 / 300 / 400 test rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/shayekh/physics_gre/resolve/main/physics_gre_scored.jsonl"
    title: "physics_gre_scored.jsonl counted directly (100 rows; 75 scorable image-free)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/shayekh/physics_gre/resolve/main/physics_gre.jsonl"
    title: "physics_gre.jsonl additional exams counted directly (300 rows; 212 image-free)"
    accessed: "2026-09-08"
  - url: "https://github.com/InflectionAI/Inflection-Benchmarks"
    title: "Inflection-Benchmarks GitHub (archived 2025-03-16; public archive banner)"
    accessed: "2026-09-08"
  - url: "https://github.com/InflectionAI/Inflection-Benchmarks/commits/main"
    title: "Inflection-Benchmarks commits (single commit listed 2024-03-06)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-014 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-014"
---

## What it measures

This id is Inflection AI's processed Physics GRE, not the 2025 Yale [PHYSICS](physics.md) set and not BIG-bench [physics_questions](physics_questions.md). The model sees an English five-option item from a released Physics GRE form (GR8677 on the main split; GR9277, GR9677, and GR0177 on the extra split). It must pick A-E. Diagram items are dropped before scoring, so the reported number is text-only exam physics, not figure reading.

## How it is scored

Inflection samples completions, takes majority vote at 8 or 32 draws, then converts accuracy on image-free items into a GRE-style raw score: plus one for a hit, minus 0.25 for a miss, with no "leave blank" path. That raw score is looked up in the percentile table in the Inflection-Benchmarks README. lm-evaluation-harness does none of that. It scores loglikelihood over the five letters and reports mean `acc` on the rows that survive `process_docs`. Do not compare an `acc` to those percentiles.

## Dataset and licence

The Hugging Face mirror `shayekh/physics_gre` (MIT, matching Inflection's MIT LICENSE, copyright 2024) holds 100 + 300 + 400 test rows across three configs. Direct JSONL counts: GR8677 has 24 image items and 75 scorable image-free rows; the three extra forms contribute 212 image-free rows. Answers are in the files. The GitHub commits page lists a single commit on 2024-03-06. The Hub dataset was created 2024-04-01.

## Who publishes it

Inflection AI released the processed JSONL in Inflection-Benchmarks. No named paper authors appear on the README opened here. GitHub shows the repository archived on 2025-03-16 (read-only). EleutherAI's lm-eval task loads the `shayekh` Hub mirror, which that task README says matches the Inflection files on `input`, `target_scores`, and `has_image`.

## Lineage

Not part of MMLU physics, not [physics](physics.md), and not BIG-bench physics word problems. The three lm-eval YAML tasks share one template: `physics_gre_multiple_choice` (GR8677, Inflection's reporting split), `physics_gre_additional_multiple_choice`, and `physics_gre_all_multiple_choice`. There is no lm-eval group named `physics_gre`.

## Saturation and contamination

On Inflection's own percentile protocol, GPT-4 maj@8 already sits at 97, next to the 98th-percentile band. That is not an `acc` ceiling and is not entered as `top_score`. The items and keys have been public since March 2024, and the underlying GRE forms are old, widely copied exam papers, so leakage risk is high.

## How to run it

In lm-eval the runnable names are `physics_gre_multiple_choice`, `physics_gre_additional_multiple_choice`, and `physics_gre_all_multiple_choice`. Prompt: `{{input}}\nAnswer:` with choices from `target_scores` keys. Filter: drop `has_image` and drop rows with no letter scored 1. Inflection's maj@k plus GRE penalty is not implemented there.

## Reading the numbers

A high lm-eval `acc` means the model ranks the right letter above the other four on image-free stems. It does not mean a GRE percentile, does not credit figure items, and does not apply the minus-0.25 penalty. Compare two scores only if they used the same split (GR8677 vs union) and the same protocol (loglikelihood `acc` vs maj@k percentile). For derivation-heavy physics see [physics](physics.md); for numerical high-school word problems see [physics_questions](physics_questions.md).
