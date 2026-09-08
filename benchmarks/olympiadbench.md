---
id: olympiadbench
name: OlympiadBench
aliases:
  - OlympiadBench
  - Olympiad Bench
page_kind: benchmark
category: multimodal
subcategory: bilingual olympiad math and physics, text and figures
status: active
summary: >
  8,476 olympiad-level bilingual math and physics problems, many with figures, from
  contests and the Chinese gaokao; GPT-4V scored 17.97% on the full set at release.
measures: >
  OlympiadBench asks a model to solve contest mathematics or physics problems at
  Olympiad and Chinese college-entrance (gaokao) difficulty, in English or Chinese,
  with or without accompanying figures. Items are open-ended questions or theorem
  proofs. Each record carries expert annotations: subject, language, answer type,
  subfield, and a step-by-step solution. The benchmark is meant to be harder than
  saturated school-math sets and to test scientific reasoning in two languages and
  two modalities, not only English text.
task_format: >
  Zero-shot free response. Open-ended items ask for a numeric, expression, or
  tuple answer that an automated judge compares to a gold final_answer. Proof items
  are sampled by humans in the original paper, not auto-scored. OpenCompass ships
  only five text-only open-ended category files, not the full multimodal set.
metric:
  name: accuracy (open-ended items; automated answer match)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Open-ended contest problems have no chance rate. The paper reports no single
    human baseline. On the full benchmark the README table lists GPT-4o at 25.89%
    average (32.48% math, 13.10% physics) and GPT-4V at 17.97% (21.70% math,
    10.74% physics). Text-only GPT-4o is 39.72% average.
dataset:
  size: 8476
  size_note: >
    8,476 problems on Hugging Face datasets-server across 18 configs, matching the
    paper. Open-ended text-only slices that OpenCompass actually runs sum to 2,673
    (OE_TO_maths_en_COMP 674, OE_TO_maths_zh_COMP 408, OE_TO_maths_zh_CEE 1,240,
    OE_TO_physics_en_COMP 236, OE_TO_physics_zh_CEE 115). Remaining configs are
    multimodal and/or theorem-proof splits.
  url: https://huggingface.co/datasets/Hothan/OlympiadBench
  license: "MIT on the GitHub LICENSE file; Apache-2.0 on the Hugging Face dataset card (both opened; not reconciled)"
  languages:
    - en
    - zh
  modalities:
    - text
    - image
  splits: "18 named category files (OE/TP × MM/TO × maths/physics × en/zh × COMP/CEE); Hugging Face exposes each as a 'train' split of evaluation items"
  public_test_set: true
publisher:
  org: "OpenBMB / Tsinghua University"
  authors:
    - Chaoqun He
    - Renjie Luo
    - Yuzhuo Bai
    - Shengding Hu
    - Zhen Leng Thai
    - Junhao Shen
    - Jinyi Hu
    - Xu Han
    - Yujie Huang
    - Yuxiang Zhang
    - Jie Liu
    - Lei Qi
    - Zhiyuan Liu
    - Maosong Sun
  url: https://github.com/OpenBMB/OlympiadBench
paper:
  title: "OlympiadBench: A Challenging Benchmark for Promoting AGI with Olympiad-Level Bilingual Multimodal Scientific Problems"
  arxiv: "2402.14008"
  url: https://arxiv.org/abs/2402.14008
  year: 2024
leaderboard_url: https://github.com/OpenBMB/OlympiadBench
repo_url: https://github.com/OpenBMB/OlympiadBench
released: "2024-02"
last_updated: "2025-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 25.89
  as_of: "2024-07"
  note: >
    Official README full-benchmark table, GPT-4o at 25.89% average. Physics is
    much lower than math. No later multi-model tracker for 2025–2026 frontier
    models was confirmed on the sources opened here.
contamination:
  risk: high
  note: >
    Items come from International and Chinese Olympiads and the Chinese gaokao,
    which circulate as PDFs and solution books. The packaged JSON, images, and
    gold answers have been public since February 2024 (dataset updates through
    July 2024 / June 2025 on Hugging Face). The authors cleaned OCR and deduped,
    but they did not hold out answers.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: OlympiadBench
  bigbench: ""
  other: >
    OpenCompass dataset type OlympiadBenchDataset, path opencompass/OlympiadBench.
    Default category list in OlympiadBench_categories.py is five text-only
    open-ended files; abbr OlympiadBench_{category}. Other configs add LLM-verify,
    cascade eval, raw prompt, and a math-only file. Official scoring is
    eval/auto_scoring_judge.py in OpenBMB/OlympiadBench. No lm-eval, HELM,
    inspect_evals, or BIG-bench task was confirmed.
tags:
  - olympiad
  - math
  - physics
  - bilingual
  - multimodal
  - free-response
sources:
  - url: https://arxiv.org/abs/2402.14008
    title: "OlympiadBench paper abstract (arXiv:2402.14008, ACL 2024)"
    accessed: "2026-09-08"
  - url: https://github.com/OpenBMB/OlympiadBench
    title: "OpenBMB/OlympiadBench README (8,476 items, leaderboard tables, category codes)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/OpenBMB/OlympiadBench/main/LICENSE
    title: "OlympiadBench GitHub MIT licence"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/Hothan/OlympiadBench
    title: "Hugging Face dataset card Hothan/OlympiadBench"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/Hothan/OlympiadBench
    title: "Hugging Face API metadata (license apache-2.0, 18 configs)"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/size?dataset=Hothan/OlympiadBench
    title: "datasets-server row counts (8,476 total; per-config sizes)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/OlympiadBench/OlympiadBench_categories.py
    title: "OpenCompass OlympiadBench category list (five text-only OE splits)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/OlympiadBench/OlympiadBench_0shot_gen_be8b13.py
    title: "OpenCompass OlympiadBench 0-shot gen config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-018 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-018"
---

## What it measures

OlympiadBench gives a model a contest mathematics or physics problem in English or Chinese. Many items include a figure. The model must produce a final answer, or a proof on theorem-proof splits. Sources are International Olympiads, Chinese Olympiads, and the Chinese gaokao. The authors parsed official PDFs, then cleaned, revised, and labelled each item. The skill under test is olympiad-level scientific problem solving across language and modality, not short multiple-choice recall.

## How it is scored

Open-ended items use an automated judge that compares the extracted final answer to gold `final_answer`, including numeric tolerance when `error` is set. Proof items were only sample-graded in the paper. Reporting is usually accuracy, sometimes split by math versus physics or by text-only versus multimodal. OpenCompass wraps `OlympiadBenchEvaluator` version v2 and, in other configs, an LLM verifier. Those OpenCompass runs cover five text-only open-ended category files, not the 8,476-item full set. A full-set GPT-4V number and an OpenCompass text-only number are different measurements.

## Dataset and licence

Hugging Face datasets-server counts 8,476 rows across 18 category configs, matching the paper. Category codes encode question type (OE or TP), modality (MM or TO), subject, language, and source (COMP or CEE). Gold solutions and images are public. The GitHub LICENSE file is MIT (copyright OpenBMB, 2024). The Hugging Face card states Apache-2.0. Both readings are recorded; this page does not pick one.

## Who publishes it

Chaoqun He, Renjie Luo, Yuzhuo Bai, and colleagues at OpenBMB and Tsinghua posted arXiv:2402.14008 on 21 February 2024. ACL 2024 accepted the paper in May 2024. They maintain GitHub OpenBMB/OlympiadBench and the Hothan/OlympiadBench Hub mirror. The README table is the only official scoreboard opened here. Hugging Face last updated the dataset in June 2025 to fix English physics images.

## Lineage

The paper is a harder bilingual multimodal successor in spirit to school-math sets, not a fork of one parent. This repository's [olymmath](olymmath.md) and [omni_math](omni_math.md) are later math-only text sets that cite OlympiadBench as a comparison. [physics](physics.md) and [cmphysbench](cmphysbench.md) name OlympiadBench as related physics evaluation, not as a parent. OpenCompass's five-file slice is a harness subset of this benchmark, not a separate evaluation id.

## Saturation and contamination

The official full-set table still sits well below 30% for GPT-4o. Physics lags math. That is not a current 2026 ceiling; it is the last table on the project README. Contamination risk is high: contest and gaokao items were already public, and this release ships answers.

## How to run it

Reference code is OpenBMB/OlympiadBench (`inference/` and `eval/auto_scoring_judge.py`). OpenCompass dataset name OlympiadBench loads `opencompass/OlympiadBench` with abbr `OlympiadBench_{category}`. Name the category files, modality, and judge (rule versus LLM) when you compare scores. No lm-eval, HELM, or inspect_evals task was confirmed.

## Reading the numbers

A high full-set score would mean the model can handle contest math and physics in two languages, including figures. Most published OpenCompass numbers omit figures and proofs, so they run high relative to the paper's GPT-4V 17.97%. Physics and non-English text are the harder slices in the authors' own analysis. Do not treat an OlympiadBench score as a pure math score, and do not mix it with [olymmath](olymmath.md), which is a different 200-problem numeric set.
