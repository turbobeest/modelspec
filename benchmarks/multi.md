---
id: multi
name: MULTI
page_kind: family
category: multimodal
summary: "MULTI evaluates Chinese multimodal understanding with more than 18,000 authentic examination questions and hard and in-context variants."
measures: "MULTI tests image-text comprehension, complex reasoning, and knowledge recall against real examination standards. MULTI-Elite is a 500-question hard subset, while MULTI-Extend adds more than 4,500 external knowledge context pieces."
task_format: "Chinese image-text multiple-choice questions with optional retrieved context."
metric:
  name: accuracy
  direction: higher_is_better
  unit: percent
  max_score: 100
  human_baseline: 86.1
  baseline_note: "The paper reports human expert baselines of 86.1% on MULTI and 73.1% on MULTI-Elite."
dataset:
  size: 18000
  size_note: "More than 18,000 questions; MULTI-Elite has 500 questions and MULTI-Extend has more than 4,500 context pieces."
  url: https://opendfm.github.io/
  languages: [Chinese]
  modalities: [text, image]
  public_test_set: null
publisher:
  org: "MULTI authors"
  authors: [Zichen Zhu, Yang Xu, Lu Chen, Jingkai Yang, Yichuan Ma, Yiming Sun, Hailin Wen, Jiaqi Liu, Jinyu Cai, Yingzi Ma, Situo Zhang, Zihan Zhao, Liangtai Sun, Kai Yu]
  url: https://arxiv.org/abs/2402.03173
paper:
  title: "MULTI: Multimodal Understanding Leaderboard with Text and Images"
  arxiv: "2402.03173"
  url: https://arxiv.org/abs/2402.03173
  year: 2024
released: "2024-02"
lineage:
  variants: ["multi_bench"]
saturation:
  status: open
  note: "The paper reports a large gap between leading model and human expert accuracy."
contamination:
  risk: medium
  note: "The questions derive from authentic examinations and the release is public; model-specific exposure is not established."
harness:
  other: "Official MULTI evaluation resources."
tags: [Chinese, multimodal, examinations, visual-reasoning]
sources:
  - url: https://arxiv.org/abs/2402.03173
    title: "MULTI paper"
    accessed: "2026-09-08"
  - url: https://opendfm.github.io/
    title: "Official MULTI project page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-008 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

MULTI evaluates Chinese multimodal understanding using authentic examination questions. Items combine images and text and test comprehension, complex reasoning, and knowledge recall. The project also provides MULTI-Elite, a selected 500-question hard subset, and MULTI-Extend, which adds external knowledge context for in-context learning.

## How it is scored

The main metric is multiple-choice accuracy. The paper reports Qwen2-VL-72B at 76.9% on MULTI and 53.1% on MULTI-Elite, compared with human expert baselines of 86.1% and 73.1%. MULTI-Extend evaluates use of supplied context and should be reported separately.

## Dataset and licence

The dataset contains more than 18,000 selected and refined questions, with 500 in MULTI-Elite and more than 4,500 external knowledge context pieces in MULTI-Extend. The consulted sources do not establish a unified licence or answer visibility, so those fields remain unknown.

## Who publishes it

Zichen Zhu and 13 coauthors introduced MULTI in a 2024 arXiv paper, later published in Science China Information Sciences. The authors link the official project page. The project is a leaderboard and dataset rather than a judge-based evaluation.

## Lineage

MULTI is the family page. MULTI-Elite and MULTI-Extend are named variants. MULTI-Bench is a separate spoken-dialogue benchmark despite the shared word, and is listed as a related variant only for catalogue navigation.

## Saturation and contamination

The gap between the leading reported model and human experts shows substantial headroom. The benchmark is open. Because examination material and release resources are public, contamination risk is medium; model-specific exposure is not established.

## How to run it

Use the official questions and multiple-choice extraction protocol. Report MULTI, MULTI-Elite, or MULTI-Extend, language, image handling, context retrieval, and model prompt. Keep context-augmented results separate from the base test.

## Reading the numbers

A high accuracy indicates strong performance on the selected Chinese visual and textual questions. It does not establish broad multimodal reasoning outside examination formats. Compare hard-subset and context-augmented results with human baselines. Inspect image-text and knowledge-recall slices when choosing a model.
