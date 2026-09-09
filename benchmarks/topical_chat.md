---
id: topical_chat
name: Topical-Chat
aliases: []
page_kind: benchmark
category: generation
subcategory: open-domain dialogue
status: active
summary: BIG-bench Topical-Chat evaluates open-domain response generation in conversations grounded in topical information.
measures: The task asks a model to generate a response in an open-domain conversation. Its examples contain multi-turn dialogue about topics such as people, science, sports, and culture.
task_format: Dialogue context followed by a generated response.
metric: {name: BLEU, direction: higher_is_better, unit: score, max_score: null, random_baseline: null, human_baseline: null, baseline_note: "The task metadata names BLEU and provides no human baseline."}
dataset: {size: 22295, size_note: "The public BIG-bench task file contains 22,295 examples.", url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/topical_chat, license: "", languages: [English], modalities: [text], splits: "", public_test_set: true}
publisher: {org: Google BIG-bench, authors: [], url: https://github.com/google/BIG-bench}
paper: {title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models", arxiv: "2206.04615", url: https://arxiv.org/abs/2206.04615, year: 2022}
leaderboard_url: ""
repo_url: https://github.com/google/BIG-bench
released: "2022"
last_updated: ""
lineage: {family: bigbench, predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No current task-specific leaderboard was established.}
contamination: {risk: high, note: The public dialogue examples and references may have entered training corpora; actual exposure is unknown.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: topical_chat, other: ""}
tags: [dialogue, generation, open-domain]
sources:
  - url: https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/topical_chat/task.json
    title: BIG-bench Topical-Chat task
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2206.04615
    title: BIG-bench paper
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-001 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-001"}
---

## What it measures

Topical-Chat evaluates open-domain response generation. A model receives a multi-turn English conversation and generates the next response, with the dialogue grounded in topical information.

The public examples span everyday and factual topics. The task measures similarity to reference responses, not unrestricted conversational quality.

## How it is scored

The BIG-bench task metadata (`preferred_score: bleu`) names BLEU as the headline metric, but the task file also computes ROUGE, BLEURT, and log-likelihood for every response. BLEU rewards n-gram overlap with references and does not fully capture relevance, factuality, or naturalness; BLEURT is a learned metric intended to correlate better with human judgment, so the two can disagree on the same response. The task file provides no human baseline.

## Dataset and licence

The public task file contains 22,295 examples. It does not state a separate split or licence in the inspected metadata. Dialogue and reference text are public, creating substantial exposure risk.

## Who publishes it

Topical-Chat is distributed through Google’s BIG-bench collection and covered by the broader BIG-bench paper. No current standalone leaderboard or separate paper was established.

## Lineage

This is a standalone BIG-bench task. The inspected sources do not establish a predecessor, successor, or formal variant.

## Saturation and contamination

Saturation is unknown. Public dialogue references can appear in training corpora, and BLEU can reward memorization. A high overlap score should not be treated as evidence of safe, useful conversation.

## How to run it

Run BIG-bench task `topical_chat` with its generation metric. Preserve conversation order, reference handling, task revision, and decoding settings. Report BLEU implementation details when comparing runs.

## Reading the numbers

A higher BLEU score indicates more lexical overlap with the task’s reference responses. It does not establish engaging dialogue, factual grounding, long-context tracking, or resistance to repetition. Pair automatic scores with human judgments and factuality checks.

The task’s open-domain framing makes topic distribution and reference diversity important. Inspect responses across topics rather than relying only on one corpus-level number.

Reference-based generation metrics can penalize valid responses that use different wording. Human relevance, coherence, and factuality checks are needed to complement BLEU.

Conversation length and topic transitions can also affect results. Preserve the full context and report truncation and decoding settings when comparing systems.

These controls are necessary for fair generation comparisons.
