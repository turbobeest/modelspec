---
id: medhallu
name: MedHallu
aliases: []
page_kind: benchmark
category: safety
subcategory: medical hallucination detection
status: active
summary: MedHallu classifies whether biomedical answers grounded in PubMed knowledge are factual or hallucinated.
measures: MedHallu presents a biomedical question, a PubMed-derived knowledge snippet, and either a ground-truth answer or a hallucinated answer. The model must classify the answer as factual or hallucinated.
task_format: Knowledge, question, and answer prompt; output 0 for factual or 1 for hallucinated.
metric: {name: exact match, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: 50, human_baseline: null, baseline_note: "The scenario does not provide a human baseline."}
dataset: {size: 1000, size_note: "HELM loads the pqa_labeled train split (1,000 rows per the Hugging Face dataset card) and doubles each row into factual and hallucinated instances, giving 2,000 test instances. The dataset also has a separate pqa_artificial configuration of 9,000 rows, not used by this scenario.", url: https://huggingface.co/datasets/UTAustin-AIHealth/MedHallu, license: MIT, languages: [English], modalities: [text], splits: train, public_test_set: true}
publisher: {org: University of Texas at Austin and collaborators, authors: [Shrey Pandit, Jiawei Xu, Junyuan Hong, Zhangyang Wang, Tianlong Chen, Kaidi Xu, Ying Ding], url: https://medhallu.github.io/}
paper: {title: "MedHallu: A Comprehensive Benchmark for Detecting Medical Hallucinations in Large Language Models", arxiv: "2502.14302", url: https://arxiv.org/abs/2502.14302, year: 2025}
leaderboard_url: ""
repo_url: https://medhallu.github.io/
released: "2025"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: open, top_score: null, as_of: "", note: "The paper reports the best model reaching an F1 of only 0.625 on hard-category hallucinations under its own evaluation protocol, well short of a ceiling; no top score under HELM's exact-match protocol was found."}
contamination: {risk: medium, note: The dataset is publicly loadable; exposure and answer leakage were not established.}
harness: {lm_eval: "", inspect_evals: "", helm: medhallu, opencompass: "", bigbench: "", other: ""}
tags: [medical, hallucination, factuality]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medhallu_scenario.py
    title: HELM MedHallu scenario
    accessed: "2026-09-08"
  - url: https://medhallu.github.io/
    title: MedHallu project page
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/UTAustin-AIHealth/MedHallu
    title: MedHallu dataset
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2502.14302
    title: "MedHallu: A Comprehensive Benchmark for Detecting Medical Hallucinations in Large Language Models"
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-057 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-batch-057"}
---

## What it measures

MedHallu measures factuality classification for medical question answering. Each instance includes a PubMed-derived knowledge passage, a biomedical question, and an answer. One answer is the ground-truth response; the paired answer is deliberately hallucinated.

The task asks whether the answer is factual or contains unsupported information. It is an English text classification task.

## How it is scored

HELM assigns label `0` to the ground-truth answer and label `1` to the hallucinated answer, then uses exact match. With two labels, uniform guessing would give 50 percent, although class construction and prompt details should be checked in the active run.

## Dataset and licence

The scenario loads the `pqa_labeled` configuration of `UTAustin-AIHealth/MedHallu` from the train split at a pinned revision. It reads `Question`, `Ground Truth`, `Knowledge`, and `Hallucinated Answer`. The Hugging Face dataset card lists 1,000 rows in `pqa_labeled` (derived from PubMedQA's labeled split) and a separate `pqa_artificial` configuration of 9,000 rows generated automatically, which this scenario does not use. The dataset card states an MIT licence.

## Who publishes it

MedHallu was introduced by Pandit and colleagues (University of Texas at Austin, UNC Chapel Hill, and Drexel University) in the 2025 paper "MedHallu: A Comprehensive Benchmark for Detecting Medical Hallucinations in Large Language Models" (arXiv:2502.14302). The dataset is hosted under the UTAustin-AIHealth organisation on Hugging Face, with a public project page. HELM maintains the integration. No current standalone leaderboard was established.

## Lineage

MedHallu is a standalone medical factuality benchmark. The sources do not establish a predecessor, successor, or formal variant.

## Saturation and contamination

The paper reports that leading 2025 models, including GPT-4o and Llama-3.1, still struggle with hard-category hallucinations, with the best F1 as low as 0.625 under its own protocol, so the task is open rather than saturated. The dataset is publicly accessible on Hugging Face and the scenario exposes both factual and hallucinated answer construction, creating medium contamination risk for models trained after February 2025. Accuracy can also be affected by artifacts in how paired examples were generated.

## How to run it

Use HELM’s `medhallu` scenario and the pinned Hugging Face revision. It emits two test instances for each dataset row, formats the knowledge, question, and answer, and evaluates exact-match labels. Record the revision and pairing policy.

## Reading the numbers

A strong score indicates that a model distinguishes the benchmark’s factual answers from its hallucinated counterparts. It does not establish open-ended medical factuality or resistance to novel unsupported claims. Review errors by question type and inspect whether models exploit stylistic artifacts.

Because each source row yields a factual and hallucinated pair, report the construction rule and class balance. A model that relies on answer style or length can score well without verifying biomedical claims.
