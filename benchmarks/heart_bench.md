---
id: heart_bench
name: HEART-Bench
page_kind: benchmark
category: human-preference
subcategory: personality consistency
summary: "HEART-Bench evaluates whether LLM agents preserve human-like personality and memory-consistent decisions across structured psychological scenarios."
measures: "HEART-Bench constructs 11 character profiles from orthogonal Big Five traits and pairs each with 1,000 autobiographical-style episodic memories. It tests decisions across 64 DIAMONDS scenarios for personality and value consistency."
task_format: "673 human-validated multiple-choice decision questions grounded in character memories."
metric:
  name: decision consistency
  direction: higher_is_better
  unit: percent
  max_score: 100
dataset:
  size: 673
  size_note: "673 multiple-choice questions after human validation and filtering."
  languages: [English]
  modalities: [text]
  public_test_set: null
publisher:
  org: "HEART-Bench authors"
  authors: [Weihan Peng, Chenxu Zhang, Qianao Wang, Yuling Shi, Heng Lian, Qihong Mao, Jiahao Pang, Chunliang Feng, Bowen Li, Xiaodong Gu]
  url: https://arxiv.org/abs/2605.30058
paper:
  title: "HEART-Bench: Do LLM Agents Exhibit Human-like Psychology?"
  arxiv: "2605.30058"
  url: https://arxiv.org/abs/2605.30058
  year: 2026
released: "2026-05"
saturation:
  status: open
  note: "The benchmark proposes a new testbed for personality and memory-consistent decisions."
contamination:
  risk: unknown
  note: "Training-data exposure is not established by the paper."
harness:
  other: "HEART-Bench character-profile and DIAMONDS scenario protocol."
tags: [psychology, personality, memory, agents]
sources:
  - url: https://arxiv.org/abs/2605.30058
    title: "HEART-Bench paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-007 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

HEART-Bench tests whether an LLM agent can simulate a coherent human-like psychology rather than only complete tasks. It constructs 11 characters from orthogonal Big Five personality traits and supplies each with 1,000 structured autobiographical-style episodic memories.

Agents answer 673 human-validated multiple-choice questions across 64 decision-making scenarios. The scenarios follow the DIAMONDS taxonomy: Duty, Intellect, Adversity, Mating, pOsitivity, Negativity, Deception, and Sociality.

## How it is scored

The benchmark measures whether decisions remain consistent with the assigned personality profile, memories, and values. The abstract does not establish a single published metric name beyond decision consistency, nor a human baseline. Report scenario family, character, memory condition, and question-level aggregation with any score.

## Dataset and licence

The paper reports 11 profiles, 1,000 memories per profile, 64 scenarios, and 673 multiple-choice questions after human validation and filtering. It does not state a dataset licence or public test policy in the abstract. Those fields remain unknown.

## Who publishes it

Weihan Peng, Chenxu Zhang, Qianao Wang, Yuling Shi, Heng Lian, Qihong Mao, Jiahao Pang, Chunliang Feng, Bowen Li, and Xiaodong Gu introduced HEART-Bench in a May 2026 arXiv paper. No independent leaderboard is established.

## Lineage

HEART-Bench is a standalone personality-consistency benchmark. Its relationship to HEART is topical rather than a declared lineage: HEART evaluates emotional-support quality, while HEART-Bench evaluates psychological coherence in decisions. The paper names no successor.

## Saturation and contamination

The benchmark is presented as a new testbed for human-like emotions, personality consistency, and value-consistent behavior. No saturation result is established. Training exposure is unknown.

## How to run it

Instantiate each character profile and its episodic memories, then present the 64 scenario families under the released protocol. Report memory access, prompt, character, DIAMONDS dimension, and consistency aggregation. Keep profile and scenario splits separate.

## Reading the numbers

A high consistency score means decisions align with the selected profile and memory context under the benchmark’s questions. It does not prove human psychology, emotional understanding, or safe behavior. Inspect cross-scenario and cross-dimension consistency, since an aggregate can hide a brittle character simulation.
