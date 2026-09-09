---
id: med_paragraph_simplification
name: Paragraph-level Simplification of Medical Texts
aliases: [MedParaSimplification]
page_kind: benchmark
category: generation
subcategory: medical text simplification
status: active
summary: This benchmark maps technical medical abstracts to lay-language summaries across clinical topics.
measures: The task asks a model to rewrite a technical abstract as a plain-language summary while preserving its important clinical content. The corpus pairs abstracts with human-written or author-provided lay summaries.
task_format: Medical abstract input and plain-language summary target.
metric: {name: "", direction: higher_is_better, unit: "", max_score: null, random_baseline: null, human_baseline: null, baseline_note: "HELM does not specify a main metric in this scenario."}
dataset: {size: null, size_note: "The source code downloads data-1024 train, val, and test source/target files but does not state counts.", url: https://github.com/AshOlogn/Paragraph-level-Simplification-of-Medical-Texts, license: CC-BY-4.0, languages: [English], modalities: [text], splits: train, validation, test, public_test_set: true}
publisher: {org: Association for Computational Linguistics / Ashwin Devaraj and colleagues, authors: [Ashwin Devaraj, Iain Marshall, Byron Wallace, Junyi Jessy Li], url: https://aclanthology.org/2021.naacl-main.395/}
paper: {title: "Paragraph-level Simplification of Medical Texts", arxiv: "2104.05767", url: https://arxiv.org/abs/2104.05767, year: 2021}
leaderboard_url: ""
repo_url: https://github.com/AshOlogn/Paragraph-level-Simplification-of-Medical-Texts
released: "2021"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No current authoritative leaderboard was established.}
contamination: {risk: medium, note: The corpus is public through the repository; model exposure was not established.}
harness: {lm_eval: "", inspect_evals: "", helm: med_paragraph_simplification, opencompass: "", bigbench: "", other: ""}
tags: [medical, simplification, summarization]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/med_paragraph_simplification_scenario.py
    title: HELM medical paragraph simplification scenario
    accessed: "2026-09-08"
  - url: https://aclanthology.org/2021.naacl-main.395/
    title: NAACL paper
    accessed: "2026-09-08"
  - url: https://github.com/AshOlogn/Paragraph-level-Simplification-of-Medical-Texts
    title: Official repository
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/AshOlogn/Paragraph-level-Simplification-of-Medical-Texts/main/LICENSE.md
    title: Repository LICENSE.md (CC BY 4.0)
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-057 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-batch-057"}
---

## What it measures

This benchmark measures paragraph-level simplification of medical text. A technical clinical abstract is provided, and the model must produce a plain-language summary that remains faithful to the evidence and conclusions.

The corpus covers clinical topics and stores aligned abstract and plain-language-summary files. The source describes `pls` as “plain-language summary.”

## How it is scored

HELM creates one reference summary for each source-target pair. The scenario does not declare a main metric or evaluator. Any reported ROUGE, BLEU, readability, or semantic score must therefore include its own implementation and normalization details.

## Dataset and licence

The scenario downloads `train.source`, `val.source`, and `test.source`, paired with target files from the official repository’s `data/data-1024` directory, including the test split, so the reference summaries are publicly visible rather than held out. It does not state item counts. The repository’s root `LICENSE.md` is the Creative Commons Attribution 4.0 International licence (CC BY 4.0); the examples include DOI-linked clinical-review abstracts, but the source does not establish rights for every underlying text beyond that repository licence.

## Who publishes it

Devaraj, Marshall, Wallace, and Li introduced the corpus in the 2021 NAACL paper “Paragraph-level Simplification of Medical Texts.” The authors maintain the linked repository. HELM provides the runnable scenario; no current leaderboard was established.

## Lineage

This is a standalone medical simplification corpus. The sources do not identify a predecessor, successor, or formal variant.

## Saturation and contamination

Saturation is unknown. The repository makes data accessible, creating some exposure risk, but no contamination study was located. Medical simplification quality can also depend on factual preservation and reading level, which a single automatic score may miss.

## How to run it

Use HELM’s `med_paragraph_simplification` scenario. It downloads aligned source and target files for train, validation, and test, then emits abstract-to-summary generation instances. Record the evaluator and any readability constraints because the scenario itself does not choose a metric.

## Reading the numbers

A good result suggests that a model can shorten technical medical prose for a general reader. It does not prove that the output is clinically safe, factually complete, or understandable to a specific patient population. Inspect omissions, dosage claims, uncertainty, and readability alongside aggregate scores.

The source and target are aligned line by line, which makes evaluation sensitive to segmentation and whitespace handling. Reproducible runs should preserve the repository files and document preprocessing before scoring.
