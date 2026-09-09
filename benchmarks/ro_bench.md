---
id: ro_bench
name: RO-Bench
aliases:
  - Ro-Bench
  - "Ro-Bench: Robust Video MLLMs Benchmark"
page_kind: benchmark
category: multimodal
subcategory: "video MLLM robustness under counterfactual edits"
status: proposed
summary: >
  Multiple-choice video questions scored on original clips and on text-edited
  counterfactual versions, so the gap measures robustness rather than raw accuracy.
measures: >
  RO-Bench (also written Ro-Bench) tests whether a video multimodal LLM still answers
  correctly after a text-driven edit of the clip. Source videos come from DAVIS, TGVE,
  MSR-VTT, BalanceCC, and the internet. Captions are rewritten along object, action,
  background, and style, then a video editor renders a new clip. Questions cover action
  recognition, object recognition, object existence, and video captioning. Agents in the
  videos are grouped as human, animal, landscape, or object. The interesting number is
  the drop from original to edited accuracy, not the original score alone.
task_format: >
  A video plus an English multiple-choice question. Object-existence options are yes,
  no, and not sure. Other tasks use a gold option from the caption plus LLM distractors.
metric:
  name: "accuracy (origin, edit, and drop)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Table 1 reports Origin accuracy, Edit accuracy, and Drop = Origin minus Edit.
    Object existence uses three options. Other option counts were not given as a single
    random-guess figure. No human baseline was reported.
dataset:
  size: 8600
  size_note: >
    The paper states 8.6k multiple-choice QA pairs across four tasks, from 2.1k
    filtered video-caption pairs. Exact integers were not printed. A separate fine-tuning
    set has 332 original videos, 1,328 counterfactual videos, and 6,640 QA pairs. That
    training set is not the test set.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - video
    - text
  splits: "original vs edited evaluation; separate counterfactual fine-tuning set"
  public_test_set: false
publisher:
  org: Beijing University of Posts and Telecommunications
  authors:
    - Zixi Yang
    - Jiapeng Li
    - Muxi Diao
    - Yinuo Jing
    - Kongming Liang
  url: "https://arxiv.org/abs/2510.08936"
paper:
  title: "RO-Bench: Large-scale robustness evaluation of MLLMs with text-driven counterfactual videos"
  arxiv: "2510.08936"
  url: "https://arxiv.org/abs/2510.08936"
  year: 2025
leaderboard_url: ""
repo_url: ""
released: "2025-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 60.83
  as_of: "2025-10"
  note: >
    Among the eight off-the-shelf video MLLMs in Table 1, VideoChat2 had the smallest
    overall drop (10.34 points; edited overall 60.83%). Mean drop across those models
    was 17.57 points (origin 70.25%, edited 52.68%). Fine-tuned LLaVA-NextRo reached
    74.23% edited overall with a 4.83-point drop. Action recognition dropped 23.99
    points on average, more than object existence (11.54).
contamination:
  risk: medium
  note: >
    Raw videos include public datasets (DAVIS, TGVE, MSR-VTT, BalanceCC) plus internet
    clips. Questions were generated with GPT-4o. The edited test videos were not found
    in a public release as of this research, which limits scrape risk for the counterfactual
    half, but original clips may already appear in training data.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The October 2025 paper says code and data will be released shortly. No GitHub
    repository, Hugging Face dataset, or harness task was found.
tags:
  - multimodal
  - video
  - robustness
  - counterfactual
  - multiple-choice
sources:
  - url: "https://arxiv.org/abs/2510.08936"
    title: "RO-Bench arXiv abstract (v1, 10 Oct 2025)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2510.08936"
    title: "RO-Bench PDF (dataset pipeline, Table 1–2, release note)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-080 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

RO-Bench gives a video multimodal LLM an English multiple-choice question about a clip, then asks the same question about a counterfactual edit of that clip. Edits change object attributes, actions, background, or style through text-driven video editors. Tasks are action recognition, object recognition, object existence, and captioning.

The original-video score is ordinary video QA. The edited-video score, and the drop between them, is the robustness claim. Object edits hurt more than style or background in the paper's plots. Action recognition dropped more than object existence.

## How it is scored

The reported metrics are Origin accuracy, Edit accuracy, and Drop. Higher Origin and Edit are better; smaller Drop is more robust. Object existence uses yes / no / not sure. Other tasks shuffle a gold option from the caption with LLM distractors. No single random baseline was given for mixed option counts.

Table 1 (2025-10) evaluates eight models plus two LLaVA-Next fine-tunes. Mean Origin was 70.25% and mean Edit 52.68%, a 17.57-point drop. VideoChat2 dropped 10.34 points (Edit 60.83%). LLaVA-Next dropped 26.56 points (Edit 43.41%). LLaVA-NextRo, fine-tuned on the authors' counterfactual set, dropped 4.83 points and reached 74.23% Edit. The abstract's 21.73% Ro-Bench gain is 26.56 minus 4.83, a drop reduction, not an Edit-accuracy delta. On MVBench, LLaVA-NextRo averaged 44.33 versus 31.55 for LLaVA-Next, a 12.78-point gain.

## Dataset and licence

The paper describes 8.6k QA pairs from 2.1k filtered video-caption pairs. Sources are DAVIS, TGVE, MSR-VTT, BalanceCC, and internet video. GPT-4o writes questions. Fine-tuning used 332 original videos, 1,328 edited videos, and 6,640 QA pairs; that set is separate from the robustness test. Dataset licence is not stated. The arXiv page uses the standard non-exclusive distribution licence for the paper, not a data licence. Code and data were promised and were not found.

## Who publishes it

Zixi Yang, Jiapeng Li, Muxi Diao, Yinuo Jing, and Kongming Liang at Beijing University of Posts and Telecommunications submitted the paper on 10 October 2025. Yang, Li, Diao, and Jing are marked equal contribution. Liang is corresponding author. There is no leaderboard URL.

## Lineage

RO-Bench is a video analogue of language-guided counterfactual image tests such as LANCE, which the paper cites. It is not RoTBench (tool-use noise), not RoboBench, and not RoBench-25. MVBench is the related video-understanding suite used to show transfer after counterfactual fine-tuning; this repository has no MVBench page yet.

## Saturation and contamination

Off-the-shelf models still lose more than ten points on edited clips, so the robustness gap is open. LLaVA-NextRo narrows Drop on this set because it trained on the same pipeline. Public source videos can leak into pretraining. Edited clips were not found in a public dump, which currently limits that half.

## How to run it

No repository, dataset card, or harness task was found. Reproducing Table 1 needs the unreleased videos, questions, and the origin-versus-edit protocol. Do not treat an MVBench average as a RO-Bench number. If a later dump appears, record whether scores are Origin, Edit, or Drop, and whether the model was fine-tuned on the 6,640-pair training split.

## Reading the numbers

A high Origin score only says the model can read the unedited clip. A small Drop with a low Edit score is still a weak video model. The 21.73% figure is a reduction in Drop for LLaVA-NextRo versus LLaVA-Next, not a 21.73-point Edit gain. Compare RO-Bench with other video suites only alongside the same four tasks and the same original-versus-edited split.
