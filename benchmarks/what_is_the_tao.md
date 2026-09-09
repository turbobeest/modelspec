---
id: what_is_the_tao
name: What Is the Tao?
aliases: []
page_kind: benchmark
category: knowledge
subcategory: philosophy and translation
status: active
summary: BIG-bench What Is the Tao compares stylistic elements of translations of a philosophical text.
measures: The task asks a model to compare translations of a complex philosophical text and select the stylistically appropriate option. It is an English multiple-choice interpretation task.
task_format: Question comparing translation styles with answer choices.
metric: {name: multiple_choice_grade, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: ""}
dataset: {size: 36, size_note: "The task README and auto-generated header both state 36 multiple-choice queries; translated passages are excerpted from Vít Brunner's Tao Te Ching comparison website (ttc.tasuki.org).", url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/what_is_the_tao, license: "", languages: [English], modalities: [text], splits: "", public_test_set: true}
publisher: {org: Google BIG-bench, authors: [Alice Xiang, Ekin Dogus Cubuk], url: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/what_is_the_tao}
paper: {title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models", arxiv: "2206.04615", url: https://arxiv.org/abs/2206.04615, year: 2022}
leaderboard_url: ""
repo_url: https://github.com/google/BIG-bench
released: "2022"
last_updated: ""
lineage: {family: bigbench, predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No leaderboard was established.}
contamination: {risk: medium, note: Public examples may be in training data.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: what_is_the_tao, other: ""}
tags: [philosophy, translation, multiple-choice]
sources:
  - url: https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/what_is_the_tao/task.json
    title: BIG-bench task definition
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/what_is_the_tao/README.md
    title: "what_is_the_tao README (36 questions, authors, data source, limitations)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2206.04615
    title: BIG-bench paper
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-stream-a-001 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-a-001"}
---

## What it measures

What Is the Tao? compares stylistic elements of translations of a complex philosophical text. The task asks a model to select the best answer among alternatives.

## How it is scored

BIG-bench uses multiple-choice grading. The task file contains 36 examples and does not state a human baseline.

## Dataset and licence

The 36 examples are embedded in the public BIG-bench task file. The translated passages are excerpted from Vít Brunner's Tao Te Ching comparison website (ttc.tasuki.org). No separate split or licence is stated.

## Who publishes it

The task was contributed to BIG-bench by Alice Xiang and Ekin Dogus Cubuk. No separate paper or leaderboard was established.

## Lineage

This is a standalone BIG-bench task with no established predecessor or successor.

## Saturation and contamination

Saturation is unknown. The tiny public set makes memorization and uncertainty material. The task's own README reports that on one of its four question types (reading comprehension about the nature of the Tao), the largest models tested answered consistently correctly even when the translated passages were removed from the prompt, suggesting pre-training knowledge rather than in-context analysis drove that subset's score.

## How to run it

Run BIG-bench task `what_is_the_tao`; preserve task revision and answer choices.

## Reading the numbers

A high score indicates agreement with the task’s translation-style distinctions. It does not establish broad translation quality, philosophical understanding, or cultural competence. Item-level review is essential because 36 examples are too few for precise ranking.

Interpret the result as a narrow literary judgment probe, not a general language metric.

Translation style is inherently sensitive to source edition and evaluator framing. The task’s small public example set cannot support stable model rankings, and no claim about philosophical expertise should be inferred from its accuracy. Preserve the exact task revision and choices when reproducing a result.

The benchmark can probe sensitivity to wording and literary register, but those are narrower constructs than translation quality in general. Human interpretation remains necessary for claims about meaning or philosophical fidelity.

Different translations may be defensible for reasons the multiple-choice key does not capture. Error analysis should retain the full alternatives and explain which stylistic feature determined the reference answer. This matters when comparing models with different prompts or language backgrounds.

The task should therefore be cited with its exact examples and choice key.

Its narrow scope is still useful for checking whether a model distinguishes register and stylistic framing in philosophical translation prompts. It should not be used as a standalone measure of translation competence.
