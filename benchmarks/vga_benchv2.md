---
id: vga_benchv2
name: VGA-BenchV2
aliases:
  - VGA-Bench V2
page_kind: benchmark
category: generation
subcategory: text-to-video aesthetics, generation quality, and reward-model optimization
status: active
summary: "VGA-BenchV2 keeps VGA-Bench's 52-dimension prompt suite and adds larger human labels, hybrid judges, and aesthetic reward-model fine-tuning."
measures: >
  VGA-BenchV2 evaluates the same text-to-video task as VGA-Bench: a model generates a
  clip from a dimension-aligned prompt, then judges score aesthetic quality, aesthetic
  tags, and generation quality. The V2 contribution is supervision and judges, not a
  new prompt list. Human labels grow by 36,000 task-level annotations. VAQA-Net still
  predicts continuous aesthetic scores; VTag-Net and VGQA-Net become Qwen-based
  vision-language evaluators. An optional loop uses VAQA-Net as a reward model for
  generator fine-tuning.
task_format: >
  Text-to-video generation from the VGA-Bench prompt suite; clips are scored by the
  V2 hybrid evaluators, with an optional reinforcement-learning fine-tune using
  VAQA-Net reward.
metric:
  name: "dimension-averaged aesthetic score, tag classification accuracy, and generation level"
  direction: higher_is_better
  unit: score
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Same three-track reporting as VGA-Bench. VAQA-Net is validated with SROCC (87.6%
    on overall score in Table 3). VTag-Net reports classification accuracy (Top-1 or
    Top-2 by label cardinality). VGQA-Net reports accuracy across 31 dimensions
    (paper average about 71.3%). Table 5 ranks 12 generators; Sora2 reached 0.50
    aesthetic score and 0.80 generation level. Wan2.1 fine-tuning with Flow-GRPO
    moved mean aesthetic score from 0.49 to 0.52 on a held-out set.
dataset:
  size: 1016
  size_note: >
    Prompt suite unchanged: 1,016 prompts and over 60,000 videos from 12 models.
    New V2 annotations: 16,200 aesthetic quality, 13,200 tagging, 6,600 generation
    quality (36,000 added; totals 17,500 / 14,500 / 18,600). VAQA-Net fine-tunes on
    8,366 generated videos and tests on 1,186 held-out clips. VTag-Net uses 11,100
    generated videos plus VADB real videos. VGQA-Net uses 7,054 generated videos.
    Hugging Face currently hosts the shared VGA-Bench dump (8,349 videos), not a
    separate V2-only archive.
  url: https://huggingface.co/datasets/BestiVictoryLab/VGA-Bench
  license: CC-BY-NC-4.0
  languages:
    - en
    - zh
  modalities:
    - video
    - text
  splits: same prompt suite as VGA-Bench; evaluator training uses held-out generated videos
  public_test_set: true
publisher:
  org: "Ant Group, Beijing Film Academy, and Beijing Institute for General Artificial Intelligence (BIGAI)"
  authors:
    - Longteng Jiang
    - Dandan Zheng
    - Qianqian Qiao
    - Heng Huang
    - Huaye Wang
    - Yihang Bo
    - Bao Peng
    - Jingdong Chen
    - Jun Zhou
    - Xin Jin
  url: https://github.com/BestiVictory/VGA-Bench
paper:
  title: "VGA-BenchV2: An Expanded Unified Benchmark and Multi-Model Framework for Evaluating Video Aesthetics and Generation Quality"
  arxiv: "2608.25452"
  url: https://arxiv.org/abs/2608.25452
  year: 2026
leaderboard_url: https://blackrice2001.github.io/VGAbench/
repo_url: https://github.com/BestiVictory/VGA-Bench
released: "2026-08"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: vga_bench
  successors: []
  variants: []
saturation:
  status: open
  top_score: 0.50
  as_of: "2026-08"
  note: >
    Sora2 led Table 5 aesthetic score at 0.50 and generation level at 0.80. Tag
    accuracy remains well below a solved classification task. Reward-model
    fine-tuning of Wan2.1 only moved aesthetics 0.49 to 0.52.
contamination:
  risk: medium
  note: >
    Same public prompt suite as VGA-Bench. Extra human labels are training data
    for judges, not extra test prompts. A generator that trains on the prompt
    list can still overfit the suite.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "BestiVictory/VGA-Bench toolkit with V2 evaluator weights"
tags:
  - video-generation
  - aesthetics
  - text-to-video
  - reward-model
  - human-preference
sources:
  - url: https://arxiv.org/abs/2608.25452
    title: "VGA-BenchV2 paper (arXiv abs, 2608.25452)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/html/2608.25452v1
    title: "VGA-BenchV2 HTML full text (arXiv html)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/BestiVictoryLab/VGA-Bench
    title: "Shared VGA-Bench Hugging Face dataset card"
    accessed: "2026-09-08"
  - url: https://github.com/BestiVictory/VGA-Bench
    title: "Official evaluation toolkit covering VGA-Bench and VGA-BenchV2"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-084 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

VGA-BenchV2 scores the same generated-video skills as [VGA-Bench](vga_bench.md): aesthetic quality, aesthetic tagging, and generation quality over 52 sub-dimensions. Prompts still name the attribute being tested. The V2 paper does not add a new prompt list. It adds human labels, replaces two of the three judges with Qwen3-VL-32B instruction-tuned evaluators, and shows that VAQA-Net can serve as a reward for Flow-GRPO fine-tuning.

The input remains a Chinese or English prompt and a generated clip. The output is a set of dimension scores, not a language-model answer.

## How it is scored

Aesthetic quality is a continuous score from VAQA-Net, validated with Spearman rank correlation against humans (87.6% SROCC on overall score). Tags are discrete labels from VTag-Net. Generation quality is VGQA-Net accuracy on 31 questions (about 71.3% mean in the paper). Table 5 averages those tracks to rank 12 generators. The toolkit still expects five videos per prompt. Reward-model runs report a change in VAQA overall score, not a new test set.

## Dataset and licence

Prompts and the 60,000-clip generation pool are inherited. New labels add 36,000 annotations on top of VGA-Bench's 14,600, for 50,600 task-level human labels. Hugging Face still hosts `BestiVictoryLab/VGA-Bench` (CC-BY-NC-4.0, 8,349 videos as of this research). Code is Apache-2.0. The V2 article is CC BY 4.0. The GitHub README still says V2 "has not yet been published" even though arXiv 2608.25452 exists; treat that as documentation lag.

## Who publishes it

The same Ant Group, Beijing Film Academy, and BIGAI authors as VGA-Bench posted the V2 paper on 26 August 2026 (comments mark IJCAI 2026). The shared toolkit and leaderboard URL are those of VGA-Bench.

## Lineage

This page is the expanded successor of [VGA-Bench](vga_bench.md). It is not a different prompt benchmark and should not be averaged with the first paper's Table 5. Related video suites cited in the paper (V-Bench, V-Bench2, T2V-CompBench, ChronoMagic-Bench, StoryEval) do not have pages here.

## Saturation and contamination

Sora2 remains the aesthetic leader at 0.50 in Table 5, with HunyuanVideo and Wan2.2 close behind. Generation level reaches 0.80 for Sora2, which is high on that normalised scale but is not a solved suite: tag classification and several realism dimensions stay weak. Prompt-suite leakage is the main contamination path.

## How to run it

Use `BestiVictory/VGA-Bench` with the V2 evaluator weights (VAQA checkpoints plus VGQA/VTAG LoRAs on Qwen3-VL-32B). Do not report V1 net scores as V2. Name the weight snapshot. Reward-model experiments are optional and are not the default leaderboard protocol.

## Reading the numbers

V2 aesthetic scores use a different judge than V1, so a 0.50 in V2 is not proof of gain over a 0.50 in V1. Tag accuracy measures controllability of prompted photographic attributes. A 0.03 reward-model bump is a fine-tune result on Wan2.1, not a new generator ranking. Always pair the three tracks; a high generation level with a weak aesthetic score is a different failure than the reverse.
