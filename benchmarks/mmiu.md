---
id: mmiu
name: "MMIU"
aliases:
  - "Multimodal Multi-image Understanding"
  - "MMIU-Benchmark"
page_kind: benchmark
category: multimodal
subcategory: "multi-image multiple-choice understanding"
status: active
summary: "A 11,698-question multi-image multiple-choice benchmark spanning 52 tasks and 7 image-relationship types, scored by accuracy."
measures: >
  MMIU tests whether a vision-language model can answer a multiple-choice question
  about several images at once. Items cover seven relationship types, from low-level
  forensic detection through semantic correspondence, temporal ordering, and 2D/3D
  spatial tasks. Each sample is a question, an option list, a list of image paths,
  and a letter answer. Table 1 of arXiv:2408.02718 names five modalities (image,
  text, video, point cloud, depth). Language of the questions is English.
task_format: >
  Multiple-choice with images. inspect_evals builds a user message from the
  question field plus the image list, uses Inspect's multiple_choice solver, and
  scores with choice() plus per-task accuracy. Shuffle defaults to true. A task_name
  filter can run one of the inspect task keys. Authors recommend VLMEvalKit as
  another runner.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 27.4
  human_baseline: null
  baseline_note: >
    The paper and inspect_evals score overall accuracy, plus per-task accuracy.
    The official GitHub README lists Random Guess 27.4 and Frequency Guess 31.5.
    No human baseline was stated in the opened paper abstract, GitHub README, or
    dataset card. inspect_evals README reports gpt-4o at 60% on 1.5k samples; the
    paper reports GPT-4o at 55.7% on the full set.
dataset:
  size: 11698
  size_note: >
    Paper Table 2 and Hugging Face datasets-server both report 11,698 test
    samples and 77,659 images, 52 tasks, 7 image relationships, mean 6.64 images
    per item (range 2-32). inspect_evals eval.yaml dataset_samples is 11698.
    inspect_evals task_names.py lists 60 task keys because of naming splits; the
    README says a map back to the paper's 52 tasks is not implemented.
  url: https://huggingface.co/datasets/FanqingM/MMIU-Benchmark
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - image
    - text
  splits: "test (11,698); inspect_evals pins Hugging Face revision 03bf7d143d920e97a757f606b6b7baee161b019b"
  public_test_set: true
publisher:
  org: "OpenGVLab (Shanghai AI Laboratory and collaborators)"
  authors:
    - "Fanqing Meng"
    - "Jin Wang"
    - "Chuanhao Li"
    - "Quanfeng Lu"
    - "Hao Tian"
    - "Jiaqi Liao"
    - "Xizhou Zhu"
    - "Jifeng Dai"
    - "Yu Qiao"
    - "Ping Luo"
    - "Kaipeng Zhang"
    - "Wenqi Shao"
  url: https://mmiu-bench.github.io/
paper:
  title: "MMIU: Multimodal Multi-image Understanding for Evaluating Large Vision-Language Models"
  arxiv: "2408.02718"
  url: https://arxiv.org/abs/2408.02718
  year: 2024
leaderboard_url: https://github.com/OpenGVLab/MMIU
repo_url: https://github.com/OpenGVLab/MMIU
released: "2024-08"
last_updated: "2024-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 55.72
  as_of: "2024-08"
  note: >
    OpenGVLab README table ranks GPT4o at 55.72, Gemini 53.41, Claude3 53.38,
    InternVL2 50.30 among 24 models, matching the paper's 55.7% GPT-4o figure.
    That is well below 100. Later inspect_evals notes 60% for gpt-4o on 1.5k
    samples, which is not the full-set number.
contamination:
  risk: medium
  note: >
    Questions, options, answers and image archives have been public on Hugging
    Face since 8 August 2024. Many tasks reuse existing public sources (the card
    names BLINK among others), so older single-image sets may already be in
    training data even when this packaging is recent.
harness:
  lm_eval: ""
  inspect_evals: "mmiu"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Authors recommend VLMEvalKit. inspect eval inspect_evals/mmiu; optional -T task_name=..."
tags:
  - multimodal
  - multi-image
  - multiple-choice
  - vision
  - inspect-evals
sources:
  - url: https://arxiv.org/abs/2408.02718
    title: "MMIU paper (arXiv:2408.02718)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2408.02718
    title: "MMIU paper HTML (Table 2: 11698 samples, 77659 images, 52 tasks)"
    accessed: "2026-09-08"
  - url: https://github.com/OpenGVLab/MMIU
    title: "OpenGVLab/MMIU repository and README leaderboard"
    accessed: "2026-09-08"
  - url: https://api.github.com/repos/OpenGVLab/MMIU
    title: "OpenGVLab/MMIU GitHub API (description ICLR2025; license null; pushed 2024-09-14)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/OpenGVLab/MMIU/main/README.md
    title: "MMIU GitHub README (GPT4o 55.72; random 27.4; frequency 31.5)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/FanqingM/MMIU-Benchmark
    title: "FanqingM/MMIU-Benchmark dataset card (CC BY 4.0)"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=FanqingM/MMIU-Benchmark
    title: "MMIU-Benchmark datasets-server (test 11698)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/mmiu/README.md
    title: "inspect_evals mmiu README"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/mmiu/mmiu.py
    title: "inspect_evals mmiu.py"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/mmiu/eval.yaml
    title: "inspect_evals mmiu eval.yaml (dataset_samples 11698)"
    accessed: "2026-09-08"
  - url: https://mmiu-bench.github.io/
    title: "MMIU project page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-058 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-058"
---

## What it measures

MMIU is a multi-image multiple-choice test for vision-language models. Each item gives two to 32 images and an English question with lettered options. The model must pick the labelled answer. Tasks span seven relationship types used in both the paper and inspect_evals' data files: low-level semantic, high-level subject semantic, high-level object semantic, continuous temporal, discrete temporal, 2D spatial and 3D spatial. Table 1 also counts five modalities: image, text, video, point cloud and depth map. It is not a single-image VQA set and not a video benchmark with a timeline API.

## How it is scored

The headline is accuracy over the 11,698 test questions. inspect_evals also reports per-task accuracy. The GitHub README gives random guess 27.4 and frequency guess 31.5. The paper's 24-model table is led by GPT-4o at 55.7% (README 55.72). inspect_evals' README figure of 60% for gpt-4o uses 1.5k samples, not the full set. No human baseline was found in the opened sources.

## Dataset and licence

Hugging Face `FanqingM/MMIU-Benchmark` has a 11,698-row `test` parquet plus image zips. Paper Table 2 matches: 77,659 images, 52 tasks, mean 6.64 images per question. The dataset card states CC BY 4.0. The GitHub repository API reports no licence file. Answers are public. inspect_evals pins revision `03bf7d1`.

## Who publishes it

Fanqing Meng, Jin Wang and Chuanhao Li are joint first authors. Wenqi Shao and Kaipeng Zhang are corresponding authors on the GitHub README. The work is released through OpenGVLab. arXiv:2408.02718 appeared 5 August 2024; the dataset followed on 8 August 2024. The GitHub API description is "[ICLR2025] MMIU…"; the opened arXiv HTML does not carry a venue line, and OpenReview was not independently confirmed here. The project page is mmiu-bench.github.io.

## Lineage

MMIU is a multi-image suite, not a relabel of MMMU or a single BLINK split. Some tasks reuse public sources (the card's example names BLINK). There is no MMIU family page. Do not confuse the acronym with MMLU. inspect_evals contributed by Esther-Guo wraps the Hugging Face release; that wrap is this repository's harness spelling.

## Saturation and contamination

Saturation status is open: the 2024-08 leaderboard top is 55.72, far from 100. Contamination risk is medium. The packaged test is public, and several source image tasks predate MMIU.

## How to run it

```
inspect eval inspect_evals/mmiu
```

Optional `-T task_name=forensic_detection_blink` (keys in `task_names.py`). Default shuffle is on. BMP images are converted to PNG base64 for APIs that reject BMP. Authors recommend VLMEvalKit for the original table. Prompt field choice matters: inspect_evals sends `question` plus images, not the longer `context` string. Per-task names in inspect (60 keys) are not mapped back to the paper's 52 tasks.

## Reading the numbers

A 55% overall score means the model beat frequency guess on a broad mix of multi-image items, not that it can track 3D scenes or long videos. Spatial and temporal slices in the paper are harder than semantic ones. Compare full-set accuracy, not the 1.5k inspect subsample, and look at relationship-type breakdowns before claiming multi-image competence.
