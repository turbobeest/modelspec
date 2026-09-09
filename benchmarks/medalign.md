---
id: medalign
name: MedAlign
aliases: []
page_kind: benchmark
category: instruction-following
subcategory: electronic health records
status: active
summary: MedAlign tests instruction following grounded in longitudinal electronic health records and clinician responses.
measures: MedAlign gives a model an instruction or question grounded in an event-stream style patient record. It evaluates whether the model can read the record and produce the clinician-generated completion.
task_format: EHR-grounded natural-language instruction and generated clinical response.
metric: {name: COMET and BERTScore, direction: higher_is_better, unit: "", max_score: null, random_baseline: null, human_baseline: null, baseline_note: "The HELM scenario names these metrics; their active calibration is not stated there."}
dataset: {size: 303, size_note: "The paper reports 983 natural-language instructions in total, of which 303 have clinician-written reference responses grounded in 276 longitudinal EHRs; the HELM scenario itself does not restate these counts.", url: https://arxiv.org/abs/2308.14089, license: "", languages: [English], modalities: [text], splits: test, public_test_set: false}
publisher: {org: Stanford Medicine and collaborators, authors: [Scott L. Fleming, Alejandro Lozano, William J. Haberkorn, Jenelle A. Jindal, Eduardo P. Reis, Rahul Thapa, Louis Blankemeier, Julian Z. Genkins, Ethan Steinberg, Ashwin Nayak, Birju S. Patel, Chia-Chun Chiang, Alison Callahan, Zepeng Huo, Sergios Gatidis, Scott J. Adams, Oluseyi Fayanju, Shreya J. Shah, Thomas Savage, Ethan Goh, Akshay S. Chaudhari, Nima Aghaeepour, Christopher Sharp, Michael A. Pfeffer, Percy Liang, Jonathan H. Chen, Keith E. Morse, Emma P. Brunskill, Jason A. Fries, Nigam H. Shah], url: https://arxiv.org/abs/2308.14089}
paper: {title: "MedAlign: A Clinician-Generated Dataset for Instruction Following with Electronic Medical Records", arxiv: "2308.14089", url: https://arxiv.org/abs/2308.14089, year: 2023}
leaderboard_url: ""
repo_url: https://arxiv.org/abs/2308.14089
released: "2023"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No current authoritative leaderboard was established.}
contamination: {risk: low, note: "The paper distributes MedAlign under a research data use agreement rather than an open download, which limits how the records could enter public training corpora; actual training exposure and a formal contamination analysis were not established."}
harness: {lm_eval: "", inspect_evals: "", helm: medalign, opencompass: "", bigbench: "", other: ""}
tags: [medical, ehr, instruction-following]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medalign_scenario.py
    title: HELM MedAlign scenario
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2308.14089
    title: MedAlign paper
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-057 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-batch-057"}
---

## What it measures

MedAlign evaluates instruction following grounded in longitudinal electronic health records. Each example contains a clinician-authored instruction or question and a patient record represented as an event stream. The expected response is a clinician-generated completion.

The task exercises medical reading comprehension, record grounding, and clinically informed reasoning in English.

## How it is scored

The scenario documentation names COMET and BERTScore. HELM’s metadata calls the main metric `medalign_accuracy`, but the scenario does not specify the exact metric aggregation or calibration. Reports should identify the active evaluator and model version.

## Dataset and licence

HELM loads a dataframe through a helper and emits test instances; the scenario code itself does not state row counts. The paper reports 983 natural-language instructions curated by 15 clinicians across 7 specialties, of which 303 have clinician-written reference responses grounded in 276 longitudinal EHRs. The authors distribute MedAlign under a research data use agreement rather than as an open download, so access requires a qualified-researcher request; a redistribution licence was not established.

## Who publishes it

Fleming and collaborators introduced MedAlign in the paper “MedAlign: A Clinician-Generated Dataset for Instruction Following with Electronic Medical Records” (arXiv:2308.14089). HELM maintains an integration scenario. No current standalone leaderboard was established.

## Lineage

MedAlign is a standalone EHR-grounded benchmark. The sources read do not establish a predecessor, successor, or formal variant.

## Saturation and contamination

Saturation is unknown. Contamination risk is assessed as low because the authors distribute MedAlign under a research data use agreement rather than an open download, limiting how the records could reach public training corpora; the inspected sources do not otherwise establish training exposure. A high similarity score can also reward wording overlap without validating clinical safety.

## How to run it

Use HELM’s `medalign` scenario with its configured `max_length` and data path. It wraps each prompt and clinician response as a test instance. Record truncation, record serialization, and whether protected data access was authorized.

## Reading the numbers

A strong score suggests that a model can follow the tested instructions while using supplied longitudinal context. It does not establish diagnostic correctness, safe treatment advice, or robustness to missing or contradictory records. Review factual grounding and clinician assessment alongside automated metrics.

Longitudinal records can contain repeated events, temporal ordering, and irrelevant details. Truncation or serialization changes may alter the available evidence, so those choices should be treated as part of the protocol.
