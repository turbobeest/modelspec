---
id: tinybenchmarks
name: tinyBenchmarks
aliases:
  - tiny Benchmarks
page_kind: benchmark
category: composite
subcategory: IRT-compressed Open LLM Leaderboard evaluation
status: active
summary: >
  One-hundred-item IRT-selected subsets of Open LLM Leaderboard tasks that
  reconstruct full-benchmark accuracy from a few percent of the original items.
measures: >
  tinyBenchmarks does not add a new skill. It keeps about 100 examples from each
  of several large English benchmarks so that an item-response model can estimate
  the score the model would have got on the full set. The lm-evaluation-harness
  group covers the Open LLM Leaderboard v1 six: ARC, GSM8K, HellaSwag, MMLU,
  TruthfulQA and WinoGrande. The paper also releases tiny AlpacaEval 2.0 and
  sketches HELM Lite; those are not in the harness group. The number to trust
  is the reconstructed parent accuracy, not the raw 100-item hit rate.
task_format: >
  Same formats as the parents: multiple-choice log-likelihood for ARC, HellaSwag,
  MMLU, TruthfulQA and WinoGrande; generate-until exact match for GSM8K.
  Shot counts in the group yaml follow the Open LLM Leaderboard (for example
  tinyArc 25-shot, tinyGSM8k 5-shot, tinyMMLU 0 extra shots with a stored prompt).
metric:
  name: "gp-IRT reconstructed parent accuracy (IRT++ in the harness README)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Harness aggregation calls `tinyBenchmarks.evaluate` and returns the gp-IRT
    estimate of the original benchmark score. Chance differs by parent and is
    not a single number. The paper's claim is estimation error against the full
    sets (about 1-2 points), not a human ceiling on the tiny items.
dataset:
  size: 600
  size_note: >
    Six Open LLM Leaderboard tiny tests of 100 items each (600 scored examples
    in the `tinyBenchmarks` group). Hugging Face confirms tinyMMLU test=100
    (plus 285-dev few-shot pool), tinyGSM8k test=100 (plus the full 7,473-row
    GSM8K train for shots), tinyHellaswag validation=100, tinyWinogrande
    validation=100, tinyTruthfulQA validation=100. tinyArc loads
    `tinyBenchmarks/tinyAI2_arc`. Some configs also ship the original train
    split for few-shot, which is not part of the 100.
  url: https://huggingface.co/tinyBenchmarks
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "100 evaluation items per parent; extra parent train/dev rows for few-shot on some configs"
  public_test_set: true
publisher:
  org: "University of Michigan / IBM Research / Universitat Pompeu Fabra / MIT"
  authors:
    - Felipe Maia Polo
    - Lucas Weber
    - Leshem Choshen
    - Yuekai Sun
    - Gongjun Xu
    - Mikhail Yurochkin
  url: https://github.com/felipemaiapolo/tinyBenchmarks
paper:
  title: "tinyBenchmarks: evaluating LLMs with fewer examples"
  arxiv: "2402.14992"
  url: https://arxiv.org/abs/2402.14992
  year: 2024
leaderboard_url: ""
repo_url: https://github.com/felipemaiapolo/tinyBenchmarks
released: "2024-02"
last_updated: "2024-05"
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
    tinyBenchmarks estimates already-saturated or near-saturated public sets.
    No current leaderboard of raw tiny-group accuracy was found. The paper
    reports reconstruction error, not a ceiling on the 100-item slices.
contamination:
  risk: high
  note: >
    Every tiny item is a public example from ARC, GSM8K, HellaSwag, MMLU,
    TruthfulQA or WinoGrande. Those parents are old and widely trained on.
    A high reconstructed score inherits that leakage; it does not avoid it.
harness:
  lm_eval: tinyBenchmarks
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group `tinyBenchmarks` runs tinyArc, tinyGSM8k, tinyMMLU, tinyWinogrande,
    tinyHellaswag and tinyTruthfulQA. The group yaml names `tinyTruthfulQA`;
    the directory ships `tinyTruthfulQA_mc1.yaml` and `tinyTruthfulQA_mc2.yaml`
    (mc2 include sets task `tinyTruthfulQA`). Metrics require
    `pip install git+https://github.com/felipemaiapolo/tinyBenchmarks`.
    Official IRT++ in the README is the gp-IRT value returned by that package.
tags:
  - composite
  - efficient-eval
  - irt
  - open-llm-leaderboard
  - english
sources:
  - url: https://arxiv.org/abs/2402.14992
    title: tinyBenchmarks paper (arXiv abs, ICML)
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2402.14992
    title: tinyBenchmarks HTML full text on ar5iv
    accessed: "2026-09-08"
  - url: https://github.com/felipemaiapolo/tinyBenchmarks
    title: felipemaiapolo/tinyBenchmarks repository
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/felipemaiapolo/tinyBenchmarks/main/README.md
    title: tinyBenchmarks GitHub README (100 examples, MIT, IRT tables)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/felipemaiapolo/tinyBenchmarks/main/LICENSE
    title: tinyBenchmarks MIT LICENSE
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/tinyBenchmarks/README.md
    title: lm-evaluation-harness tinyBenchmarks task README
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/tinyBenchmarks/tinyBenchmarks.yaml
    title: tinyBenchmarks group yaml
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/tinyBenchmarks/tinyMMLU
    title: tinyMMLU dataset card (100 test items)
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=tinyBenchmarks/tinyMMLU
    title: tinyMMLU split info
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=tinyBenchmarks/tinyGSM8k
    title: tinyGSM8k split info
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/tinyBenchmarks/tinyHellaswag
    title: tinyHellaswag API metadata
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-022 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-022"
---

## What it measures

tinyBenchmarks is a cheaper way to run old English leaderboard tasks. The authors pick about 100 items per parent with item-response models so that a new model's 100-item vector can be mapped back to a full-set score. The harness group covers the six Open LLM Leaderboard v1 tasks: [ARC](arc.md) / [ARC-Challenge](arc_challenge.md), [GSM8K](gsm8k.md), [HellaSwag](hellaswag.md), [MMLU](mmlu.md), [TruthfulQA](truthfulqa.md) and [WinoGrande](winogrande.md).

The paper also ships tiny AlpacaEval 2.0 and discusses HELM Lite. Those are extra. The number this page documents is the reconstructed parent accuracy from the six-task group, not a new capability.

## How it is scored

lm-evaluation-harness does not stop at raw accuracy. Each tiny task's metric aggregation calls `tinyBenchmarks.evaluate` and returns gp-IRT (the README's IRT++). You must install the authors' Python package for that step. Without it, the tasks fail to load.

Shot counts copy the Open LLM Leaderboard. tinyMMLU stores a formatted prompt and sets `num_fewshot` to 0 so shots are not added twice. Estimation error in the paper is about one to two points on held-out models, not zero.

## Dataset and licence

Each Open LLM Leaderboard tiny set has 100 evaluation items. Some Hub configs also include the original train split so few-shot examples exist (tinyGSM8k still has 7,473 train rows). The project LICENSE is MIT. Parent datasets keep their own terms; tinyTruthfulQA's card states Apache-2.0. Answers are public because the parents are public.

## Who publishes it

Felipe Maia Polo, Lucas Weber, Leshem Choshen, Yuekai Sun, Gongjun Xu and Mikhail Yurochkin. arXiv 2402.14992 appeared 22 February 2024; the comment says ICML (the 41st International Conference on Machine Learning). Code is felipemaiapolo/tinyBenchmarks. Data live under the Hugging Face `tinyBenchmarks` org.

## Lineage

Items are subsets of the six pages named above. [metabench](metabench.md) is a later sparse reconstruction of the same six parents; its authors argue they beat tinyBenchmarks on reconstruction error. This page is not metabench. AlpacaEval and HELM Lite tinies are part of the paper, not of the harness group.

## Saturation and contamination

The parents are old and public, so contamination risk is high. Saturation of raw 100-item accuracy was not sourced and would not be the intended metric anyway. Treat a tinyBenchmarks number as an estimate of an Open LLM Leaderboard v1 score, with the paper's error bars.

## How to run it

`lm-eval --tasks tinyBenchmarks` after installing the tinyBenchmarks package. Or name one task (`tinyMMLU`, `tinyGSM8k`, ...). For every IRT method in the paper, dump `--log_samples` and call `tb.evaluate` yourself. Do not compare a raw 100-item accuracy from one paper with a gp-IRT estimate from another.

## Reading the numbers

A tinyBenchmarks score is a compressed stand-in for six 2023-era English leaderboard tasks. It does not test tools, code, long context or other languages. If two papers both say tinyBenchmarks, check whether they reported gp-IRT, p-IRT, or raw accuracy, and whether they ran the six-task group or only tinyMMLU.
