---
id: metabench
name: metabench
aliases:
  - MetaBench
  - metabench-A
page_kind: benchmark
category: composite
subcategory: sparse reconstruction of Open LLM Leaderboard v1 benchmarks
status: active
summary: An 858-item sparse subsample of ARC, GSM8K, HellaSwag, MMLU, TruthfulQA and WinoGrande that reconstructs Open LLM Leaderboard scores from a few percent of the items.
measures: >
  metabench does not add a new skill. It keeps the most informative items from six public
  benchmarks used on Hugging Face's Open LLM Leaderboard v1: ARC, GSM8K, HellaSwag, MMLU,
  TruthfulQA and WinoGrande. The authors fit item-response models on thousands of leaderboard
  submissions, then keep a few hundred items per source so that latent-ability estimates can
  reconstruct the original six scores and their mean. English text. Five of the six sources are
  multiple choice; GSM8K is free-form arithmetic. A secondary 751-item set and choice-permuted
  copies exist for repeat evaluation.
task_format: >
  Mix of multiple-choice log-likelihood (ARC, HellaSwag, MMLU, TruthfulQA, WinoGrande) and
  generate-until exact match (GSM8K). lm-evaluation-harness tasks bake in the original few-shot
  preprompts and set num_fewshot to 0 so those shots are not added twice.
metric:
  name: "accuracy (group mean of per-source acc; GSM8K exact match), plus optional reconstructed Open LLM Leaderboard scores"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The group config averages accuracy with weight_by_size false, so GSM8K's exact-match rate is
    mixed with multiple-choice acc. Chance differs by source and is not a single number. The paper's
    claim is reconstruction error against the original six scores, not a human ceiling.
dataset:
  size: 858
  size_note: >
    Primary split: 145 ARC + 237 GSM8K + 93 HellaSwag + 96 MMLU + 154 TruthfulQA + 133 WinoGrande
    = 858 items, confirmed on Hugging Face config splits named `primary`. Secondary split: 100 +
    249 + 58 + 102 + 136 + 106 = 751 items. The six source benchmarks together had 28,632 items
    before distillation.
  url: https://huggingface.co/datasets/HCAI/metabench
  license: CC-BY-NC-SA-4.0
  languages:
    - en
  modalities:
    - text
  splits: "primary (858) and secondary (751) per source config; no training split"
  public_test_set: true
publisher:
  org: Human-Centered AI, Helmholtz Munich
  authors:
    - Alex Kipnis
    - Konstantinos Voudouris
    - Luca M. Schulze Buschoff
    - Eric Schulz
  url: https://github.com/adkipnis/metabench
paper:
  title: "metabench -- A Sparse Benchmark of Reasoning and Knowledge in Large Language Models"
  arxiv: "2407.12844"
  url: https://arxiv.org/abs/2407.12844
  year: 2025
leaderboard_url: ""
repo_url: https://github.com/adkipnis/metabench
released: "2024-07"
last_updated: "2025-02"
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
    metabench is a compression of already-saturated or near-saturated public sets. No current
    public leaderboard of raw metabench group accuracy was found. The paper reports reconstruction
    RMSE against the original scores, not a ceiling on metabench itself.
contamination:
  risk: high
  note: >
    Every primary item is a public item from ARC, GSM8K, HellaSwag, MMLU, TruthfulQA or WinoGrande.
    The authors ship permuted-choice and secondary-item variants to blunt memorisation; GSM8K has
    no permute variant because it is not multiple choice.
harness:
  lm_eval: metabench
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Groups: `metabench` (858, original order), `metabench_permute`, `metabench_secondary` (751),
    `metabench_secondary_permute`. Dataset path HCAI/metabench. After harness logging, reconstruct.R
    in adkipnis/metabench maps item scores back to estimated original benchmark points.
tags:
  - composite
  - sparse
  - open-llm-leaderboard
  - irt
sources:
  - url: https://arxiv.org/abs/2407.12844
    title: "metabench arXiv abstract (v2, 20 Feb 2025)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2407.12844v2
    title: "metabench HTML full text on ar5iv (v2)"
    accessed: "2026-09-08"
  - url: https://github.com/adkipnis/metabench
    title: "adkipnis/metabench GitHub repository"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/HCAI/metabench
    title: "HCAI/metabench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=HCAI/metabench
    title: "HCAI/metabench datasets-server split counts"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/metabench/README.md
    title: "metabench task README, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/metabench/metabench.yaml
    title: "metabench group config, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch 7 pilot (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, pilot-review"
---

## What it measures

metabench is a short proxy for six English benchmarks from Open LLM Leaderboard v1: [ARC](arc.md),
[GSM8K](gsm8k.md), [HellaSwag](hellaswag.md), [MMLU](mmlu.md), [TruthfulQA](truthfulqa.md) and
[WinoGrande](winogrande.md). The authors took item-level results from more than 5,000 leaderboard
models, dropped uninformative items, fit IRT models, and kept the items that best cover the ability
range. The primary set has 858 items, under 3% of the original 28,632. A disjoint 751-item
secondary set is for a second run. Five sources remain multiple choice; GSM8K stays generate-until.

The intended use is cheap reconstruction of the old six scores and their mean, not a new domain.

## How it is scored

lm-evaluation-harness group `metabench` reports mean accuracy with equal weight per source, mixing
GSM8K exact match with multiple-choice acc. That raw mean is not the paper's headline. The paper
fits GAMs from IRT abilities (and subtest scores) to reconstruct each original normalised score and
the Open LLM Leaderboard mean. v2 of the paper (February 2025, ICLR 2025) reports 1.24% RMSE per
source and 0.58% RMSE on the total, with Spearman r = 0.94 between a single common factor and the
total. The harness README still quotes the older abstract (1.5% / 0.8% / r = 0.93). Use the v2
figures for the paper, and say which reconstruction script produced a reported "metabench" number.

## Dataset and licence

Hugging Face `HCAI/metabench` hosts one config per source with `primary` and `secondary` splits
whose sizes sum to 858 and 751. The dataset card and GitHub LICENSE state CC BY-NC-SA 4.0. Source
benchmarks keep their own licences; this card records metabench's published terms. Answers are
public. The Hugging Face card still warns that running and evaluating models is "not yet fully
supported."

## Who publishes it

Alex Kipnis, Konstantinos Voudouris, Luca M. Schulze Buschoff and Eric Schulz at Helmholtz Munich's
Human-Centered AI group. arXiv v1 appeared 4 July 2024; v2 on 20 February 2025, accepted at ICLR
2025. Code is adkipnis/metabench.

## Lineage

Items are subsets of the six pages named above, not new questions. Related work in the paper
includes tinyBenchmarks, which the authors argue they outperform on reconstruction error. No
successor id exists here. Open LLM Leaderboard v1 is the reconstruction target; later leaderboard
versions are out of scope.

## Saturation and contamination

Because the parent sets are old and public, contamination risk is high. Permuted-choice tasks
shuffle labels on the five multiple-choice sources; GSM8K cannot be shuffled that way. Saturation
of raw metabench accuracy was not established from a public table. Treat reconstructed Open LLM
Leaderboard points as estimates with the paper's RMSE, not as freshly measured full-set scores.

## How to run it

`lm-eval --tasks metabench` (or `_permute`, `_secondary`, `_secondary_permute`). Then
`Rscript reconstruct.R` in the authors' repo if you want reconstructed full-set points. Shot
preprompts are stored in the dataset; harness `num_fewshot` is 0. Do not compare a raw group acc
from one variant with a reconstructed leaderboard mean from another.

## Reading the numbers

A metabench run is a compressed stand-in for six 2023-era English leaderboard tasks. It does not
test coding, long context, tools or multilingual ability. If two papers both say "metabench,"
check primary versus secondary, permute versus original, raw acc versus reconstructed points, and
which paper version's RMSE they cite. Read the six parent pages for what each slice actually asks.
