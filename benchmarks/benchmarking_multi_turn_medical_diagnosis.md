---
id: benchmarking_multi_turn_medical_diagnosis
name: "MINT (Medical Incremental N-Turn Benchmark)"
aliases:
  - "MINT"
  - "Medical Incremental N-Turn Benchmark"
  - "Benchmarking Multi-turn Medical Diagnosis"
page_kind: benchmark
category: domain
subcategory: "multi-turn medical diagnosis (hold, lure, self-correction)"
status: active
summary: "MINT shards 1,035 medical cases into multi-turn evidence to test whether models diagnose too early, self-correct, or get lured by lab results."
measures: >
  MINT (Medical Incremental N-Turn Benchmark) tests diagnostic multiple-choice accuracy when
  clinical evidence arrives in sequence instead of as one vignette. Each of 1,035 cases is split
  into labeled shards (history, exam, labs, imaging, and related categories). The model may hold,
  answer, or revise as shards appear. The authors isolate three behaviours: premature commitment
  (hold), later correction of a wrong answer (self-correction), and early answering triggered by
  salient labs (lure). English clinical text; no images in the released description.
task_format: >
  Multi-turn chat over evidence shards, with a multiple-choice diagnostic question and answer
  options. Main contrast: Ask-Question-First (question shown up front; model may wait or answer
  at any turn) versus Ask-Question-Last (question withheld until the final turn). Also FULL versus
  CONCAT single-turn controls. Turn-count variants fix 4, 8, 12, or 16 turns.
metric:
  name: "diagnostic accuracy (multiple-choice)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single overall headline accuracy is published. Table 1 reports per-source, per-model
    Full / Concat / Q-First initial / Q-First final / Q-Last figures. Commercial models sit near
    ceiling on single-turn FULL (GPT-5-mini 95.5% and Claude Sonnet 4.6 94.1% on the 600 MedQA
    cases) while Q-First initial accuracy is lower (76.5% and 87.7% on the same slice). Q-Last
    beats Q-First initial by 20.1% on average across datasets and models. Random baseline is not
    established: source items mix option counts (MedBullets five-option subset; MedQA typically
    four).
dataset:
  size: 1035
  size_note: >
    Paper Table 5: MedQA 600 (CRAFT-MD vignettes, 50 from each of 12 disease categories, from
    1,804 candidates) + MedMCQA 174 (diagnosis-focused, vignette ≥100 words) + Derm-Public 100
    + Derm-Private 99 (one mislabeled case dropped) + MedBullets 62 (five-option diagnosis
    items from 308). Mean 9.36 turns after clinical-category sharding (median 9). 370 cases
    (35.7%) include a laboratory-result shard. Mean case length 124.63 in Table 5; the table
    does not label the length unit. Code and data "will be released upon publication."
  url: "https://arxiv.org/abs/2604.04325"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "no public train/test split; five source pools listed in Table 5; ClinicalCategoryShard plus FixedTurns (4/8/12/16) variants"
  public_test_set: false
publisher:
  org: "The University of Texas at Austin; New York University; UT Southwestern; UNC Chapel Hill; University of Illinois Urbana-Champaign"
  authors:
    - "Jinrui Fang"
    - "Runhan Chen"
    - "Xu Yang"
    - "Jian Yu"
    - "Jiawei Xu"
    - "Ashwin Vinod"
    - "Wenqi Shi"
    - "Tianlong Chen"
    - "Heng Ji"
    - "ChengXiang Zhai"
    - "Ying Ding"
    - "Yuji Zhang"
  url: "https://arxiv.org/abs/2604.04325"
paper:
  title: "Benchmarking Multi-turn Medical Diagnosis: Hold, Lure, and Self-Correction"
  arxiv: "2604.04325"
  url: "https://arxiv.org/abs/2604.04325"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2026-04"
  note: >
    No overall leaderboard. Single-turn FULL accuracy on MedQA is already high for GPT-5-mini
    (95.5%) and Claude Sonnet 4.6 (94.1%), and Derm-Private Q-Last reaches 100% for Claude
    Sonnet 4.6, so those slices are near ceiling. The multi-turn Q-First initial scores still
    separate models, which is the protocol the paper argues for. Open-source general models
    sit much lower (Qwen2.5-3B MedQA FULL 53.3%, Q-First final 29.8%).
contamination:
  risk: medium
  note: >
    Underlying vignettes come from public exam sets ([MedQA](medqa.md), [MedMCQA](medmcqa.md),
    [Medbullets](medbullets.md)) plus CRAFT-MD public/private dermatology cases. Those texts
    can appear in pretraining. The multi-turn shard sequences, 13-category labels, and hold
    protocol are new and, as of this page, not released as a public test file.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No public harness. Paper Appendix F gives sharding, turn-repartition, FULL/CONCAT, Q-First, and Q-Last prompts. Construction used Qwen3-32B at temperature 0. Authors state data and code will be released upon publication; GitHub and Hugging Face searches on 2026-09-08 found no public dump."
tags:
  - medical
  - diagnosis
  - multi-turn
  - clinical-reasoning
  - mint
sources:
  - url: "https://arxiv.org/abs/2604.04325v1"
    title: "Benchmarking Multi-turn Medical Diagnosis: Hold, Lure, and Self-Correction (arXiv:2604.04325v1)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2604.04325v1"
    title: "MINT paper HTML full text"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-076 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MINT, the Medical Incremental N-Turn Benchmark, asks a model to diagnose from a clinical vignette that arrives in pieces. Instead of one exam-style paragraph, the case is split into shards labeled with a 13-way clinical taxonomy (background, presentation, past history, labs, imaging, and so on). The model sees those shards in order and may refuse to answer, commit, or change its mind.

The point is not another single-turn medical exam score. The authors want to know whether models jump to a diagnosis before the evidence is in, whether they can correct that jump, and whether a lab result lures them into answering early. The census id is the paper title; the benchmark's own name is MINT.

## How it is scored

Items are multiple-choice diagnostic questions. The paper reports accuracy under several protocols on the same cases. FULL is the original single-turn vignette. CONCAT pastes the shards back together; Qwen3-32B matched FULL closely enough that the authors treat sharding as information-preserving. Q-First shows the question and options from the start and tells the model to wait until evidence is enough; the table records initial-commitment accuracy, final accuracy after revisions, and abstention. Q-Last hides the question until the last turn, so the model answers once with all shards in view.

Q-Last is on average 20.1% higher than Q-First initial accuracy across datasets and the 11 evaluated models. Incorrect-to-correct revisions occur at up to 10.6 times the rate of the reverse. Over 55% of first answers in Q-First land in the first two turns. Moving lab shards earlier makes models answer immediately in 75.0% of those cases, versus 13.9% and 8.3% for middle and late placement. There is no hosted leaderboard and no single official overall percentage.

## Dataset and licence

The pool is 1,035 English cases: 600 MedQA vignettes sampled from CRAFT-MD's 1,804 items (50 per 12 disease categories), 174 diagnosis-focused MedMCQA items with vignettes of at least 100 words, 100 public and 99 private dermatology cases from Johri et al. (one mislabeled private case dropped), and 62 five-option MedBullets diagnosis items. After clinical-category sharding, cases average 9.36 turns (median 9); 35.7% contain a lab shard.

A second family, MINT-FixedTurns, re-chunks each case into 4, 8, 12, or 16 turns with Qwen3-32B at temperature 0. The arXiv HTML page marks the article CC BY 4.0. The dataset licence is not stated because the authors say data and code will be released upon publication; no public repository was found on 2026-09-08.

## Who publishes it

The paper is a collaboration among UT Austin, NYU, UT Southwestern, UNC Chapel Hill, and UIUC. Listed authors: Jinrui Fang, Runhan Chen, Xu Yang, Jian Yu, Jiawei Xu, Ashwin Vinod, Wenqi Shi, Tianlong Chen, Heng Ji, ChengXiang Zhai, Ying Ding, and Yuji Zhang. arXiv:2604.04325v1 is dated 6 April 2026. Corresponding emails on the paper are jinrui@utexas.edu, ying.ding@ischool.utexas.edu, and yujiz@illinois.edu. No maintained leaderboard or GitHub org was identified.

## Lineage

This MINT is not the 2023 Princeton tool-use benchmark that [CIBench](cibench.md) cites (586 interactive coding tasks). It is also not a new exam bank: it re-shards [MedQA](medqa.md), [MedMCQA](medmcqa.md), [Medbullets](medbullets.md), and CRAFT-MD dermatology cases. No successor id exists in this repository. CRAFT-MD itself does not yet have a page.

## Saturation and contamination

Single-turn FULL is close to saturated for frontier chat models on MedQA and the dermatology slices (GPT-5-mini 95.5% MedQA FULL; Claude Sonnet 4.6 99.0% Derm-Private FULL and 100% Q-Last). The multi-turn hold setting is not: Q-First initial scores drop, open models drop further, and the paper treats that gap as the result. Source exam text is public and old enough to leak; the unpublished shard files limit direct train-on-test for the multi-turn protocol itself.

## How to run it

There is no released harness, Hugging Face dataset, or lm-eval task. Appendix F prints the prompts for sharding, turn repartition, FULL/CONCAT, Q-First, and Q-Last. Construction used Qwen3-32B with deterministic decoding. Until the promised release, numbers are only comparable if they follow those prompts and the Q-First versus Q-Last contrast. Do not drop MINT scores next to ordinary MedQA accuracy.

## Reading the numbers

A high FULL score on these 1,035 cases mostly restates existing exam skill. The number that matters here is when the model first commits and whether Q-Last recovers the loss. A model that answers in turn two after a lab result can look decisive and still be wrong. Compare Q-First initial, Q-First final, and Q-Last on the same source slice, and keep this MINT separate from the older tool-use project of the same name.
