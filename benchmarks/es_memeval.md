---
id: es_memeval
name: ES-MemEval
page_kind: benchmark
category: long-context
subcategory: emotional support dialogue
summary: "ES-MemEval evaluates long-term conversational memory for personalized emotional support across extraction, temporal reasoning, conflict detection, abstention, and user modeling."
measures: "ES-MemEval tests whether conversational agents use fragmented, implicit, and changing user information over long interactions. It covers question answering, summarization, and dialogue generation through the EvoEmo multi-session dataset."
task_format: "Multi-session personalized dialogue with memory-sensitive QA, summarization, and generation."
metric:
  name: memory capability score
  direction: higher_is_better
  unit: score
dataset:
  url: https://arxiv.org/abs/2602.01885
  languages: [English]
  modalities: [text]
  public_test_set: null
publisher:
  org: "ES-MemEval authors"
  authors: [Tiantian Chen, Jiaqi Lu, Ying Shen, Lin Zhang]
  url: https://arxiv.org/abs/2602.01885
paper:
  title: "ES-MemEval: Benchmarking Conversational Agents on Personalized Long-Term Emotional Support"
  arxiv: "2602.01885"
  url: https://arxiv.org/abs/2602.01885
  year: 2026
released: "2026-02"
saturation:
  status: open
  note: "The paper reports continuing limitations in long-term memory and evolving user-state handling."
contamination:
  risk: unknown
  note: "The paper abstract does not establish training-data exposure."
harness:
  other: "ES-MemEval and EvoEmo evaluation protocol described by the paper."
tags: [memory, dialogue, personalization, emotional-support]
sources:
  - url: https://arxiv.org/abs/2602.01885
    title: "ES-MemEval paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-006 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

ES-MemEval evaluates long-term conversational memory in personalized emotional support. User information is fragmented, implicit, and continuously changing across sessions, so an agent must retrieve more than explicit facts from the latest turn.

The benchmark covers information extraction, temporal reasoning, conflict detection, abstention, and user modeling. Tasks include question answering, summarization, and dialogue generation through the EvoEmo multi-session dataset.

## How it is scored

The paper reports benchmark results across open-source long-context models, commercial models, and retrieval-augmented systems. It finds that explicit long-term memory reduces hallucinations and improves personalization, while RAG improves factual consistency but struggles with temporal dynamics and evolving states. The abstract does not establish one universal metric name or maximum; report task type and memory capability with each score.

## Dataset and licence

The paper names EvoEmo as a multi-session dataset capturing fragmented disclosures and evolving user states. The abstract does not provide an item count, complete split description, or licence. Those fields remain unknown until the official release is inspected.

## Who publishes it

Tiantian Chen, Jiaqi Lu, Ying Shen, and Lin Zhang introduced ES-MemEval in a February 2026 arXiv paper accepted to The Web Conference 2026. No independent leaderboard is identified.

## Lineage

ES-MemEval addresses limitations of long-term dialogue benchmarks that focus on static explicit fact retrieval. EvoEmo is its associated dataset and should not be treated as a separate benchmark page. The paper does not name a successor.

## Saturation and contamination

The reported memory, temporal, and retrieval limitations indicate an open benchmark. The paper does not establish model training exposure or whether evaluation conversations are public, so contamination risk is unknown.

## How to run it

Use the multi-session conversations and the paper’s memory-sensitive task prompts when released. Report session count, memory mechanism, retrieval policy, prompt, language, and task type. Compare direct long-context and RAG systems under matched context budgets.

## Reading the numbers

A strong score indicates effective memory for the selected task and conversation history. It does not establish safe or clinically appropriate emotional support. Inspect temporal conflicts, abstentions, and personalization separately. Retrieval gains should be read alongside evidence faithfulness and readability.
