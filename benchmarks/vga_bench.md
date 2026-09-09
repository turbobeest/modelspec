---
id: vga_bench
name: VGA-Bench
aliases: []
page_kind: benchmark
category: generation
subcategory: text-to-video aesthetics and generation quality
status: active
summary: "VGA-Bench scores text-to-video models on aesthetic quality, aesthetic tags, and generation quality using 1,016 prompts and 52 sub-dimensions."
measures: >
  VGA-Bench evaluates generated videos, not language-model answers. Given a text prompt
  that names the target aesthetic or quality attribute, a generator produces a clip, and
  dedicated assessors score aesthetic quality (composition, lighting, colour, and related
  attributes), classify aesthetic tags, and rate generation quality (prompt alignment,
  physical plausibility, and basic visual stability). The skill is whether the clip is
  both technically faithful and photographically controlled, not whether a chatbot can
  describe video.
task_format: >
  Text-to-video generation from an official prompt; videos are scored by VAQA-Net,
  VTag-Net, and VGQA-Net (or by human labels on the annotated subset).
metric:
  name: "dimension-averaged aesthetic score, tag accuracy, and generation level"
  direction: higher_is_better
  unit: score
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no single 0–100 headline. Aesthetic quality uses 0–10 human scores (three
    annotators averaged) and automated 5-class accuracy or later SROCC against humans.
    Tags are multi-label with majority vote. Generation quality uses per-dimension ordinal
    options, including −1 for inapplicable prompts. Paper Table 5 reports normalised
    averages; Sora2's aesthetic score was 0.50 in that table. The official toolkit
    requires five videos per prompt (5,080 clips) before aggregation.
dataset:
  size: 1016
  size_note: >
    1,016 bilingual Chinese–English prompts (200 aesthetic, 220 tag, 596 generation:
    120 basic plus 476 fine-grained in the public files). The paper generated over 60,000
    videos from 12 models. Hugging Face currently ships 8,349 videos with annotations,
    including 13,440 generation-quality labels over 6,793 videos, and says the rest will
    follow. Human training labels in the first paper include 1,300 generated videos for
    aesthetic nets and 12,000 for VGQA-Net.
  url: https://huggingface.co/datasets/BestiVictoryLab/VGA-Bench
  license: CC-BY-NC-4.0
  languages:
    - en
    - zh
  modalities:
    - video
    - text
  splits: prompt suite plus a held-out generated-video evaluation set; Hugging Face currently exposes a single train-named dump of the public subset
  public_test_set: true
publisher:
  org: "Ant Group, Beijing Film Academy, and Beijing Institute for General Artificial Intelligence (BIGAI)"
  authors:
    - Longteng Jiang
    - DanDan Zheng
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
  title: "VGA-Bench: A Unified Benchmark and Multi-Model Framework for Video Aesthetics and Generation Quality Evaluation"
  arxiv: "2604.10127"
  url: https://arxiv.org/abs/2604.10127
  year: 2026
leaderboard_url: https://blackrice2001.github.io/VGAbench/
repo_url: https://github.com/BestiVictory/VGA-Bench
released: "2026-04"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors:
    - vga_benchv2
  variants: []
saturation:
  status: open
  top_score: 0.50
  as_of: "2026-04"
  note: >
    In the first paper's Table 5, Sora2 led aesthetic score at 0.50 while tag
    classification stayed low (0.18 in that table). Later VGA-BenchV2 reruns the
    same prompt suite with stronger evaluators; those numbers are not drop-in
    replacements.
contamination:
  risk: medium
  note: >
    Prompts and a growing public video subset are on Hugging Face. Generated clips
    are less likely to sit in language-model pretraining than web photos, but a
    generator could still overfit the prompt suite if it is used as training text.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "BestiVictory/VGA-Bench official toolkit (VAQA, VGQA, VTAG)"
tags:
  - video-generation
  - aesthetics
  - text-to-video
  - human-preference
sources:
  - url: https://arxiv.org/abs/2604.10127
    title: "VGA-Bench paper (arXiv abs, 2604.10127)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2604.10127
    title: "VGA-Bench HTML full text (ar5iv)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/BestiVictoryLab/VGA-Bench
    title: "BestiVictoryLab/VGA-Bench dataset card"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/BestiVictoryLab/VGA-Bench
    title: "Hugging Face dataset API (license cc-by-nc-4.0)"
    accessed: "2026-09-08"
  - url: https://github.com/BestiVictory/VGA-Bench
    title: "BestiVictory/VGA-Bench evaluation toolkit"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-084 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

VGA-Bench measures text-to-video generators on three tracks. Aesthetic quality scores overall appeal plus composition, shot size, lighting, visual tone, colour, depth of field, expression, costume, and makeup. Aesthetic tagging classifies photographic attributes such as composition type, light position, and contrast. Generation quality covers 31 attributes for prompt alignment, physical plausibility, and basic clarity or stability.

Each prompt is written so the target dimension is explicit. A clip is scored only on attributes the prompt actually requests. Prompts are bilingual English and Chinese.

## How it is scored

Humans rate aesthetic dimensions 0–10 (mean of three raters) and tag labels by majority vote. Generation quality uses per-question ordinal options, with −1 meaning the question does not apply. Automated judges are VAQA-Net, VTag-Net, and VGQA-Net. The official toolkit asks for five videos per prompt (5,080 clips), then aggregates VAQA, VTAG, and VGQA overall scores. Table 5 of the first paper reports normalised averages, not a universal percentage. Do not mix those numbers with VGA-BenchV2 table 5, which uses the expanded judges.

## Dataset and licence

The prompt suite has 1,016 items. The paper generated more than 60,000 videos from 12 models, including SVD, AnimateDiff-v2, LaVie, Show-1, ModelScope, CogVideoX, Latte-1, Mochi, LTXVideo, HunyuanVideo, Wan2.1, and Sora2. Hugging Face currently releases 8,349 videos and says further clips will follow. The dataset card is CC-BY-NC-4.0. The evaluation code is Apache-2.0. The arXiv article is CC BY 4.0. Those three licences are not the same.

## Who publishes it

Longteng Jiang, DanDan Zheng, Qianqian Qiao, Heng Huang, Huaye Wang, Jingdong Chen, and Jun Zhou (Ant Group), Yihang Bo and Bao Peng (Beijing Film Academy), and Xin Jin (BIGAI) submitted the paper on 11 April 2026 (CVPR 2026). Hugging Face created the dataset dump on 15 May 2026. The toolkit README points to a community leaderboard at blackrice2001.github.io/VGAbench/.

## Lineage

VGA-Bench refines V-Bench-style video evaluation by splitting aesthetics into many attributes instead of one MUSIQ-like score. V-Bench does not have a page in this repository. [VGA-BenchV2](vga_benchv2.md) keeps the same 1,016 prompts and 52 sub-dimensions, adds much more human supervision, and introduces an optional reward-model loop. This page is the original CVPR protocol, not the V2 evaluator.

## Saturation and contamination

Table 5 still spreads models: Sora2 led aesthetics (0.50) while older diffusion systems sat near 0.20. Tag accuracy was low even for strong generators in that table. The public prompt list is a contamination path for prompt memorisation; the generated videos themselves are a weaker language-model leak.

## How to run it

Generate five videos for every official prompt, write the mapping CSVs under `test/`, and run `BestiVictory/VGA-Bench` (`run_all.sh`). VGQA and VTAG need Qwen3-VL-32B plus the authors' LoRA adapters. Report which evaluator weights you used. First-paper VAQA-Net is not the V2 hybrid stack. No lm-eval task name exists.

## Reading the numbers

An aesthetic score near 0.5 is the top of the first paper's 12-model table, not a 50% exam mark. Tag accuracy measures whether prompted photographic attributes appear, not overall beauty. Generation level averages heterogeneous ordinal scales. Always name VGA-Bench versus VGA-BenchV2, the judge version, and whether humans or nets scored the clips.
