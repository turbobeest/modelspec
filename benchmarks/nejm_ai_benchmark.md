---
id: nejm_ai_benchmark
name: "NEJMAI / nephSAP nephrology benchmark"
aliases: [Nejmaibench, nephSAP]
page_kind: benchmark
category: domain
subcategory: medical knowledge
status: active
summary: "OpenCompass's NEJMAI wrapper evaluates zero-shot multiple-choice answering on 858 nephSAP nephrology questions."
measures: The OpenCompass configuration identifies a medical question, answer options, subject, and prompt mode. The linked benchmark paper evaluates 858 Nephrology Self-Assessment Program questions, not a general NEJM exam.
task_format: Medical multiple-choice question with options A through E; output one option letter.
metric:
  name: accuracy
  direction: higher_is_better
  unit: percent
  max_score: 100
dataset:
  size: 858
  size_note: "The linked nephSAP paper reports 858 multiple-choice questions; the OpenCompass local CSV revision is not independently counted here."
  url: https://huggingface.co/datasets/opencompass/nejmaibench
  license: ""
  languages: [English]
  modalities: [text]
  splits: ""
  public_test_set: null
publisher:
  org: "Nephrology Self-Assessment Program / OpenCompass"
  authors: [Sean Wu, Michael Koo, Lesley Blum, Andy Black, Liyo Kao, Fabien Scalzo, Ira Kurtz]
  url: https://arxiv.org/abs/2308.04709
paper: {title: "A Comparative Study of Open-Source Large Language Models, GPT-4 and Claude 2: Multiple-Choice Test Taking in Nephrology", arxiv: "2308.04709", url: https://arxiv.org/abs/2308.04709, year: 2023}
leaderboard_url: ""
repo_url: https://github.com/open-compass/opencompass
released: "2023-08"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No authoritative leaderboard was established.}
contamination: {risk: unknown, note: Exposure and contamination were not established.}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: nejmaibench, bigbench: "", other: ""}
tags: [medicine, multiple-choice, zero-shot]
sources:
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/nejm_ai_benchmark/nejmaibench_gen_60c8f5.py
    title: OpenCompass NEJMAI benchmark configuration
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/opencompass/nejmaibench
    title: OpenCompass NEJMAI dataset card
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-017 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: GPT-5.6 Luna independent review, luna-batch-017}
---

## What it measures

The OpenCompass `nejmaibench` configuration is a medical multiple-choice evaluation tied to the nephSAP nephrology study. The configuration exposes a question, answer options, subject, and prompt mode, and uses a medical-assistant system prompt.

The configured zero-shot prompt asks the model to output only the letter corresponding to the correct answer. The linked paper identifies nephrology as the clinical domain and reports 858 Nephrology Self-Assessment Program questions.

## How it is scored

OpenCompass uses `NejmaibenchEvaluator` with generated answers and a zero-shot retriever. The evaluator extracts option letters and reports accuracy. The paper reports historical zero-shot scores, including GPT-4 at 73.3% and Claude 2 at 54.4%; these are paper results rather than a current leaderboard.

## Dataset and licence

The OpenCompass data path is `opencompass/nejmaibench`, backed by a local `NEJM_All_Questions_And_Answers.csv` path in the project data registry. The linked paper reports 858 nephSAP questions. A public dataset licence and exact CSV revision were not established, so answer exposure remains unknown.

## Who publishes it

OpenCompass publishes the runnable configuration. Wu and co-authors published the linked nephSAP study in 2023. No current standalone leaderboard was established.

## Lineage

This page documents the OpenCompass `nejmaibench` wrapper for the nephSAP nephrology question set. It should not be merged with broad medical exams or image-based NEJM benchmarks. No predecessor or successor was established.

## Saturation and contamination

Saturation and contamination risk are unknown. Medical questions may overlap with training data, but the inspected sources provide no exposure analysis. Scores should be interpreted with the prompt and dataset revision recorded.

## How to run it

Run the OpenCompass `nejmaibench` dataset configuration. It uses `NejmaibenchDataset`, `NejmaibenchEvaluator`, `ZeroRetriever`, and `GenInferencer`; it supplies the medical-assistant system prompt and asks for one option letter. Other prompt modes in the repository may produce different results.

## Reading the numbers

A strong score indicates success on these nephrology questions under the exact option format. It does not establish safe clinical decision-making, current medical knowledge, or performance with patient context. Check evaluator normalization, dataset revision, and whether answers were exposed before comparing reports.

Medical multiple-choice performance can also depend on specialty mix and the distinction between recall and clinical reasoning. Those dimensions are not recoverable from the OpenCompass configuration alone, so they should be reported from the dataset release when available.
