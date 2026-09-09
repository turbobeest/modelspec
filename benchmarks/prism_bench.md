---
id: prism_bench
name: "PRISM-Bench"
aliases: []
page_kind: benchmark
category: multimodal
subcategory: "audio-centric text-to-audio-video generation"
status: active
summary: >
  900 human-checked clips that score text-to-audio-video models on audio type
  and on-screen vs off-screen sound with an MLLM judge.
measures: >
  PRISM-Bench tests the soundtrack of a generated video, not just the picture.
  Each item is a text prompt plus a human-verified reference clip. A T2AV
  system must emit audio and video together. Scoring factorises along audio
  type (speech, music, sound) and whether the source is on screen or off
  screen, then grades four perceptual axes: audio-visual coherence, audio
  quality, audio expressiveness, and prompt following, using 35 fine-grained
  criteria. The judge is a multimodal LLM in a blind side-by-side comparison
  against the reference, not a human rater on every run.
task_format: >
  Text prompt in; audio+video out. MLLM-as-a-judge, pairwise vs ground truth.
  Subsets: On-screen, Off-screen, and Mixed. Speech / Music / Sound cells.
metric:
  name: "MLLM pairwise dimension totals"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper does not publish a single official maximum. In the Mixed table,
    Seedance 2.0's four dimension totals sum to 99.88, ahead of Kling v3 Omni
    at 94.61 and Veo 3.1 at 88.04. Human agreement with the judge is reported
    as over 70% mean; a case study gives 91% (LTX-2), 93% (Ovi), 68% (Sora 2).
dataset:
  size: 900
  size_note: >
    900 human-verified samples after scene detection and manual checks.
    Underlying audiovisual assets are commercially licensed and not
    redistributed. The public artifact is the leaderboard space, not the
    raw clips.
  url: "https://huggingface.co/spaces/prismbench/prismbench-leaderboard"
  license: ""
  languages:
    - en
  modalities:
    - audio
    - video
    - text
  splits: "On-screen, Off-screen, and Mixed evaluation subsets"
  public_test_set: false
publisher:
  org: "Shanghai Artificial Intelligence Laboratory and Meituan"
  authors:
    - "Yuchen Sun"
    - "Qian Yang"
    - "Jun Wang"
    - "Detai Xin"
    - "Guoqiao Yu"
    - "Guanglu Wan"
    - "Qi Jia"
  url: "https://huggingface.co/spaces/prismbench/prismbench-leaderboard"
paper:
  title: "PRISM-Bench: An Audio-Centric Diagnostic Benchmark for Text-to-Audio-Video Generation"
  arxiv: "2609.04867"
  url: "https://arxiv.org/abs/2609.04867"
  year: 2026
leaderboard_url: "https://huggingface.co/spaces/prismbench/prismbench-leaderboard"
repo_url: ""
released: "2026-09"
last_updated: "2026-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 99.88
  as_of: "2026-09"
  note: >
    Paper table Mixed aggregate: Seedance 2.0 99.88, Kling v3 Omni 94.61,
    Veo 3.1 88.04. Open-source systems trail frontier APIs (the paper's
    On-screen open-source totals include LTX-2 at 49.50). Residual gaps on
    on-screen music and AV coherence remain even for the leader. 99.88 is a
    summed Mixed total, not a documented maximum of 100.
contamination:
  risk: low
  note: >
    Source clips are restricted and not on the Hub. Prompts may leak if
    published on the space; the paper says redistribution rights block a
    public audiovisual dump. Judge models could still be biased toward
    familiar generators.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Authors point at huggingface.co/spaces/prismbench/prismbench-leaderboard
    for comparison code. No lm-eval task was found. Official GitHub URL for
    the suite is not established from the paper footnotes (those point at
    generator repos such as LTX-2, Ovi, MOVA).
tags:
  - video
  - audio
  - t2av
  - mllm-judge
  - multimodal
sources:
  - url: "https://arxiv.org/abs/2609.04867"
    title: "PRISM-Bench arXiv abs (submitted 4 Sep 2026; ACM MM 2026)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2609.04867v1"
    title: "PRISM-Bench HTML (900 samples, 35 criteria, Seedance table)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/prismbench/prismbench-leaderboard"
    title: "PRISM-Bench Hugging Face leaderboard space (URL from paper)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-079 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

PRISM-Bench is an audio-first test of text-to-audio-video generators. The model gets a text prompt and must produce a clip whose sound matches both the prompt and the picture. Existing video boards often treat audio as a side score or grade it without the picture. This suite splits items by audio type (speech, music, environmental sound) and by whether the sounding object is on screen or off screen.

Four perceptual axes are scored: audio-visual coherence, audio quality, audio expressiveness, and prompt following, broken into 35 criteria. A multimodal LLM judge compares the candidate to a human-verified reference in a blind pair, then the paper aggregates those votes.

## How it is scored

The protocol is MLLM-as-a-judge, not compiler pass/fail and not a public human panel on every model. The authors claim mean agreement with humans above 70%. A case study on three systems reports 91% (LTX-2), 93% (Ovi), and 68% (Sora 2). Tables print per-dimension numbers and subset totals for On-screen, Off-screen, and Mixed. The Mixed row for Seedance 2.0 sums four dimension totals to 99.88. That figure is the paper's strongest aggregate, not a documented maximum of 100.

Evaluated systems include Seedance 2.0, Kling v3 Omni, Veo 3.0/3.1, Sora 2, LTX-2, Ovi, and MOVA. Frontier APIs lead; open local models trail, especially on on-screen music and coherence.

## Dataset and licence

The paper states 900 human-verified samples after scene cuts and manual checks. The arXiv licence is CC BY-NC-ND 4.0 for the article. The clips themselves are commercially licensed to the authors' labs and are not released. The public pointer is a Hugging Face space. No SPDX id for the audio/video dump was found. Answers (references) are held back.

## Who publishes it

Yuchen Sun and Qian Yang (equal contribution), with Jun Wang, Detai Xin, Guoqiao Yu, Guanglu Wan, and Qi Jia. Affiliations: Shanghai Artificial Intelligence Laboratory and Meituan. arXiv 2609.04867, submitted 4 September 2026, accepted at ACM Multimedia 2026 (MM '26), Rio de Janeiro, 10–14 November 2026. Related ACM DOI 10.1145/3767308.3836100.

## Lineage

This is not [PRiSM](prism.md) (phone recognition, arXiv 2601.14046). It is not the PRISM peer-review scorer (arXiv 2605.26730). Name overlap only. It does not replace general video quality boards; it adds an audio-centric slice of T2AV.

## Saturation and contamination

Open-source totals in the paper sit far below Seedance 2.0 (for example LTX-2 Mixed 47.96 vs 99.88). On-screen music and AV coherence still lag fidelity even at the top, so the diagnostic axes remain open. Restricted clips lower leakage risk. Judge-model bias is a separate issue: the same MLLM family may prefer a familiar generator.

## How to run it

The paper sends comparison code to `huggingface.co/spaces/prismbench/prismbench-leaderboard`. Generator footnotes point at LTX-2, Ovi, and MOVA repos, not at a PRISM-Bench GitHub that this session could confirm. Do not treat a video-only FVD as a substitute. Match judge model, pairwise protocol, and subset. No lm-eval task was found.

## Reading the numbers

A high Mixed total means the judge preferred that system's audio against the reference on those four axes, not that a human would ship the clip. Coherence can lag quality: the paper flags that pattern for the leader. Compare On-screen vs Off-screen and Speech vs Music before quoting one number. Open-source rows are a different operating point from API systems with extra post-processing.
