---
id: medec
name: MEDEC
aliases: []
page_kind: benchmark
category: domain
subcategory: medical error detection and correction
status: active
summary: MEDEC evaluates detection and correction of medical errors in clinical narratives.
measures: MEDEC presents a clinical narrative that is either correct or contains an error. A model must identify the error status, locate the erroneous sentence, and provide a correction when applicable.
task_format: Clinical text; output an error sentence identifier and correction, or CORRECT.
metric: {name: medec_error_flag_accuracy, direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "The scenario mentions doctors outperforming recent systems but gives no numeric human baseline."}
dataset: {size: 3848, size_note: "The scenario describes 2,189 MS training, 734 validation (574 MS and 160 UW), and 925 test (597 MS and 328 UW) texts.", url: https://github.com/abachaa/MEDEC, license: "", languages: [English], modalities: [text], splits: train, validation, test, public_test_set: true}
publisher: {org: MEDIQA-CORR / MEDEC authors, authors: [Asma Ben Abacha, et al.], url: https://github.com/abachaa/MEDEC}
paper: {title: "MEDEC: A Benchmark for Medical Error Detection and Correction in Clinical Notes", arxiv: "2412.19260", url: https://arxiv.org/abs/2412.19260, year: 2024}
leaderboard_url: ""
repo_url: https://github.com/abachaa/MEDEC
released: "2024"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: open, top_score: null, as_of: "", note: The scenario reports remaining gaps versus doctors but no current top score.}
contamination: {risk: medium, note: The repository exposes benchmark files; model exposure was not quantitatively established.}
harness: {lm_eval: "", inspect_evals: "", helm: medec, opencompass: "", bigbench: "", other: MEDIQA-CORR}
tags: [medical, error-detection, correction]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medec_scenario.py
    title: HELM MEDEC scenario
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2412.19260
    title: MEDEC paper
    accessed: "2026-09-08"
  - url: https://github.com/abachaa/MEDEC
    title: MEDEC repository
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-057 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-batch-057"}
---

## What it measures

MEDEC measures medical error detection and correction in clinical notes. Each narrative is either correct or contains an error. Error types in the scenario include diagnosis, management, treatment, pharmacotherapy, and causal organism.

For an erroneous note, the intended output identifies the sentence and supplies corrected wording. For a correct note, the expected output is `CORRECT`.

## How it is scored

HELM’s main metric is `medec_error_flag_accuracy`, focused on whether the error flag is correct. The scenario encodes a corrected reference as the sentence identifier followed by corrected text. Detection, localization, and correction should be reported separately when possible.

## Dataset and licence

The scenario describes 3,848 texts: 2,189 MS training, 574 MS plus 160 UW validation, and 597 MS plus 328 UW test. It downloads the MS test CSV at a pinned repository commit for HELM’s test run. A dataset licence was not established from the inspected sources.

## Who publishes it

MEDEC was introduced by Ben Abacha and colleagues and used in the MEDIQA-CORR shared task. The paper is arXiv:2412.19260. The authors maintain the GitHub repository; no current standalone leaderboard was established.

## Lineage

MEDEC is a standalone medical error benchmark associated with MEDIQA-CORR. The inspected sources do not establish a predecessor or successor.

## Saturation and contamination

The scenario describes recent systems as still trailing medical doctors on error tasks, supporting an open status. Public repository files create medium exposure risk, but no quantitative contamination study was found.

## How to run it

Use HELM’s `medec` scenario. It downloads the pinned MS test CSV, ignores the training file, and emits zero-shot test instances. Record the pinned commit, output format, and whether scores cover only detection or all correction stages.

## Reading the numbers

A high detection score means the model can classify the presence of errors in these narratives. It does not prove that corrections are clinically valid or safe for deployment. Inspect localization, correction fidelity, error type, and MS-versus-UW composition alongside the headline score.

The expected output couples a sentence identifier with corrected text. Exact matching can penalize clinically equivalent rewrites, so component-level evaluation is needed to separate medical correctness from formatting.
