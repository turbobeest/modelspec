---
id: multi_bench
name: MULTI-Bench
page_kind: benchmark
category: human-preference
subcategory: spoken emotional intelligence
summary: "MULTI-Bench evaluates spoken dialogue models on multi-turn emotional intelligence through basic understanding and advanced support tracks."
measures: "MULTI-Bench tests whether spoken dialogue models sustain interactive conversations with emotional awareness. Its basic track covers emotion understanding and reasoning; its advanced track covers emotion support and application."
task_format: "Multi-turn spoken dialogue across five tasks and eight subsets."
metric:
  name: task performance
  direction: higher_is_better
  unit: score
dataset:
  size: 3200
  size_note: "About 3.2K samples across five tasks and eight subsets."
  languages: [English]
  modalities: [audio, text]
  public_test_set: null
publisher:
  org: "MULTI-Bench authors"
  authors: [Yayue Deng, Guoqiang Hu, Haiyang Sun, Xiangyu Zhang, Haoyang Zhang, Fei Tian, Xuerui Yang, Gang Yu, Eng Siong Chng]
  url: https://arxiv.org/abs/2511.00850
paper:
  title: "MULTI-Bench: A Multi-Turn Interactive Benchmark for Assessing Emotional Intelligence ability of Spoken Dialogue Models"
  arxiv: "2511.00850"
  url: https://arxiv.org/abs/2511.00850
  year: 2025
released: "2025-11"
saturation:
  status: open
  note: "The paper reports remaining gaps in advanced interactive dialogue and emotional reasoning."
contamination:
  risk: unknown
  note: "Training exposure is not established by the paper abstract."
harness:
  other: "Reproducible MULTI-Bench evaluation framework."
tags: [speech, emotion, multi-turn, dialogue]
sources:
  - url: https://arxiv.org/abs/2511.00850
    title: "MULTI-Bench paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-008 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

MULTI-Bench evaluates spoken dialogue models in genuinely interactive multi-turn conversations. It emphasizes emotional intelligence rather than isolated speech recognition or single-turn response quality.

The basic track tests emotion understanding and reasoning. The advanced track tests emotion support and application. The benchmark contains five tasks and about 3.2K samples across eight subsets.

## How it is scored

The paper reports task performance for six spoken dialogue models across the eight subsets. It finds good basic understanding but remaining gaps in advanced multi-turn interaction and emotion-related reasoning. The abstract does not establish one universal metric name or maximum; report task and track separately.

## Dataset and licence

The paper establishes about 3.2K samples, five tasks, and eight subsets. It does not state a licence or public test policy in the abstract. Reproductions should record audio source, transcript, turn count, and evaluation framework version.

## Who publishes it

Yayue Deng and eight coauthors introduced MULTI-Bench in a November 2025 arXiv submission to ICASSP 2026. No independent leaderboard is established.

## Lineage

MULTI-Bench is a standalone spoken emotional-intelligence benchmark. It is distinct from the Chinese multimodal MULTI family despite the shared name. The paper names no successor.

## Saturation and contamination

The reported advanced-track gaps indicate an open benchmark. Training exposure is unknown.

## How to run it

Use the reproducible evaluation framework and preserve track, task, subset, audio input, and multi-turn interaction settings. Report model speech interface and whether transcripts are available. Do not collapse basic and advanced tracks without showing both.

## Reading the numbers

A strong result indicates emotional dialogue performance under the selected spoken interaction. It does not prove robust empathy in unseen languages, cultures, or high-stakes support. Compare basic and advanced tracks and inspect multi-turn failures. Audio and transcript conditions materially affect comparability.

Because the benchmark is interactive, a model may perform well on recognition while failing to sustain an emotionally appropriate response over several turns. The advanced track is therefore a more demanding deployment signal than a single emotion-label score. Report latency, interruption handling, and the availability of conversation history when those factors are part of the evaluation setup.
