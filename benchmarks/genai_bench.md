---
id: genai_bench
name: GenAI-Bench
page_kind: benchmark
category: multimodal
summary: "GenAI-Bench evaluates compositional text-to-image and text-to-video generation with human ratings and automated metric comparisons."
measures: "GenAI-Bench tests whether generated visuals follow compositional prompts involving attributes, relationships, logic, and comparison. It evaluates image and video generation and studies whether VQAScore agrees with human judgments."
task_format: "Text prompts paired with generated images or videos and human preference ratings."
metric:
  name: human alignment rating
  direction: higher_is_better
  unit: rating
  baseline_note: "The paper compares VQAScore with other automated metrics; no universal maximum is established."
dataset:
  size: 40000
  size_note: "GenAI-Rank contains over 40,000 human ratings; the paper also says over 80,000 ratings will be released."
  url: https://linzhiqiu.github.io/
  languages: [English]
  modalities: [text, image, video]
  public_test_set: true
publisher:
  org: "GenAI-Bench authors"
  authors: [Baiqi Li, Zhiqiu Lin, Deepak Pathak, Jiayao Li, Yixin Fei, Kewen Wu, Tiffany Ling, Xide Xia, Pengchuan Zhang, Graham Neubig, Deva Ramanan]
  url: https://arxiv.org/abs/2406.13743
paper:
  title: "GenAI-Bench: Evaluating and Improving Compositional Text-to-Visual Generation"
  arxiv: "2406.13743"
  url: https://arxiv.org/abs/2406.13743
  year: 2024
repo_url: https://linzhiqiu.github.io/
released: "2024-06"
lineage:
  successors: ["genai_rank"]
saturation:
  status: open
  note: "The paper reports meaningful gaps among metrics and generation systems."
contamination:
  risk: medium
  note: "Human ratings and prompts are released or planned for release, so later training exposure is possible."
harness:
  other: "Official GenAI-Bench and GenAI-Rank code and rating protocol."
tags: [text-to-image, text-to-video, compositionality, human-evaluation]
sources:
  - url: https://arxiv.org/abs/2406.13743
    title: "GenAI-Bench paper"
    accessed: "2026-09-08"
  - url: https://linzhiqiu.github.io/
    title: "Official GenAI-Bench project page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-004 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

GenAI-Bench evaluates text-to-visual generation on compositional prompts. Prompts require models to place attributes, relations, and higher-order concepts such as logic and comparison into an image or video. The benchmark therefore tests whether a model follows the meaning of a prompt, not only whether it produces a realistic picture.

The project also evaluates automated metrics against human ratings. GenAI-Rank extends the work to ranking images generated from the same prompt.

## How it is scored

The primary evidence is human alignment ratings. The paper compares VQAScore, which measures whether a VQA model sees an image as depicting the prompt, with CLIPScore, PickScore, HPSv2, and ImageReward. It reports that VQAScore improves ranking and can select among three to nine candidate images. Exact rating scales and video-specific aggregation are not established in the abstract.

## Dataset and licence

The paper says GenAI-Rank contains over 40,000 human ratings and that over 80,000 human ratings will be released. The project page and code are public. The consulted sources do not establish one consolidated licence for prompts, generated media, and ratings, so licensing should be checked in the release.

## Who publishes it

Baiqi Li and ten coauthors introduced GenAI-Bench in a 2024 arXiv paper. The authors link the official project page and open-source dataset, model, and code. No single current leaderboard is identified.

## Lineage

GenAI-Bench extends an earlier introduction cited by the paper. GenAI-Rank is its ranking-focused successor or variant, using human ratings to evaluate metrics on same-prompt image comparisons. The two should not be conflated.

## Saturation and contamination

The paper finds substantial differences among automated metrics and reports that VQAScore better tracks human judgments on compositional prompts. This indicates an open measurement problem. Public release of prompts and ratings creates medium contamination risk for future generators.

## How to run it

Use the official prompts, generation settings, candidate-selection protocol, and human-rating rubric. Report image versus video, prompt subset, number of candidates, and whether VQAScore or human ratings are used. Metric comparisons require identical generated candidates.

## Reading the numbers

A high human alignment score means the output follows the tested prompt to human raters. It does not establish broad visual quality, originality, or temporal coherence. Automated metric scores are proxies whose agreement can vary by prompt type. Inspect attribute and relation failures alongside aggregate ratings.
