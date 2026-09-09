---
id: heart
name: HEART
page_kind: benchmark
category: human-preference
subcategory: emotional-support dialogue
summary: "HEART compares human and LLM responses on the same multi-turn emotional-support conversations using blinded ratings and five interpersonal dimensions."
measures: "HEART evaluates emotional-support dialogue beyond fluency. Human raters and LLM judges assess responses for human alignment, empathic responsiveness, attunement, resonance, and task-following on shared dialogue histories."
task_format: "Multi-turn emotional-support conversations with pairwise human and model response evaluation."
metric:
  name: pairwise preference
  direction: higher_is_better
  unit: preference
  baseline_note: "The benchmark directly compares humans and models; no universal maximum is established."
dataset:
  modalities: [text]
  languages: [English]
  public_test_set: null
publisher:
  org: "HEART authors"
  authors: [Laya Iyer, Kriti Aggarwal, Sanmi Koyejo, Gail Heyman, Desmond C. Ong, Subhabrata Mukherjee]
  url: https://arxiv.org/abs/2601.19922
paper:
  title: "HEART: A Unified Benchmark for Assessing Humans and LLMs in Emotional Support Dialogue"
  arxiv: "2601.19922"
  url: https://arxiv.org/abs/2601.19922
  year: 2026
released: "2026-01"
saturation:
  status: open
  note: "The paper reports differences between model and human strengths, especially on adversarial turns."
contamination:
  risk: unknown
  note: "The paper abstract does not establish training-data exposure."
harness:
  other: "HEART blinded human-rating and ensemble LLM-judge protocol."
tags: [empathy, emotional-support, human-evaluation, dialogue]
sources:
  - url: https://arxiv.org/abs/2601.19922
    title: "HEART paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-007 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

HEART evaluates emotional-support dialogue as an interpersonal capability. It places humans and language models on the same multi-turn conversation histories, then compares their responses. The benchmark focuses on reading emotion, adapting tone, and handling resistance, frustration, and distress.

Its rubric has five dimensions: Human Alignment, Empathic Responsiveness, Attunement, Resonance, and Task-Following. These dimensions separate supportive quality from general language fluency.

## How it is scored

Responses are evaluated by blinded human raters and an ensemble of LLM judges. The paper reports pairwise preferences and judge-human agreement. It finds about 80% alignment between LLM-judge and human pairwise preferences, while humans retain advantages in adaptive reframing and nuanced tone shifts. Exact aggregation and scale are not established in the abstract.

## Dataset and licence

The paper describes multi-turn emotional-support conversations but does not state a total item count, licence, or public test policy in the abstract. Those fields remain unknown. Because the evaluation concerns sensitive dialogue, reproductions should document privacy and consent handling.

## Who publishes it

Laya Iyer, Kriti Aggarwal, Sanmi Koyejo, Gail Heyman, Desmond C. Ong, and Subhabrata Mukherjee introduced HEART in a 2026 arXiv paper. No public leaderboard is established.

## Lineage

HEART is a standalone emotional-support dialogue benchmark. It is related in subject to ES-MemEval but differs by directly comparing humans and models on shared conversations rather than testing long-term memory. The paper names no successor.

## Saturation and contamination

Several frontier models approach or surpass average human responses on perceived empathy and consistency, but humans remain stronger on nuanced adaptive behaviors. This indicates an open capability axis. Training exposure is unknown.

## How to run it

Use the same dialogue histories, blinded comparison design, rubric, and judge ensemble. Report human versus model comparison, judge model, turn type, and each HEART dimension separately. Avoid treating judge scores as human ratings without reporting their agreement.

## Reading the numbers

A favorable preference means raters judged the response more supportive under the selected rubric. It does not establish clinical effectiveness or safe crisis handling. Examine adversarial turns and dimension-level results, especially reframing and tone. Human baselines are central to interpretation because the benchmark is explicitly comparative.
