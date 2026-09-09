---
id: vitaminc_fact_verification
name: "VitaminC Fact Verification"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "evidence-based fact verification (claim/evidence entailment)"
status: active
summary: >-
  A BIG-bench task built from the VitaminC dataset that asks a model to judge whether a Wikipedia
  passage supports, refutes, or gives no information about a claim.
measures: >
  VitaminC Fact Verification presents a claim together with a short piece of evidence text drawn
  from Wikipedia and asks the model to classify the relationship as "SUPPORTS", "REFUTES", or "NOT
  ENOUGH INFO". The source VitaminC dataset was built to be contrastive: many claim pairs are
  nearly identical in wording but differ in the underlying fact, because the evidence comes from
  real Wikipedia edits that changed a fact, so the task also probes whether a model follows the
  evidence given rather than relying on facts memorised from pretraining, and whether it can do the
  numerical or factual comparison needed when the evidence conflicts with what it may already
  believe.
task_format: >
  Zero-shot, 3-way multiple-choice classification, scored with BIG-bench's multiple_choice_grade
  metric. The task's own convert_to_lm_format.py builds the multiple-choice queries from the
  underlying VitaminC claim-evidence-label triples.
metric:
  name: "Multiple choice grade (accuracy on the SUPPORTS / REFUTES / NOT ENOUGH INFO 3-way choice)"
  direction: higher_is_better
  unit: "accuracy"
  max_score: 1.0
  random_baseline: 0.333
  human_baseline: null
  baseline_note: >
    Three-way balanced choice implies a naive baseline near 1/3, though the exact label balance of
    the 54,668-example BIG-bench subset was not confirmed from the sources read for this page. No
    human baseline figure was found for this page.
dataset:
  size: 54668
  size_note: >
    54,668 multiple-choice queries in the BIG-bench task, per the task's own README/task.json.
    This is a subset of the full VitaminC dataset, which the original paper and its Hugging Face
    dataset card put at roughly 489,000 claim-evidence pairs total (about 371,000 train, 63,100
    validation, 55,200 test), built from over 100,000 real Wikipedia revisions that changed an
    underlying fact plus additional synthetically constructed pairs.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/vitaminc_fact_verification"
  license: "CC-BY-SA-3.0"
  languages:
    - en
  modalities:
    - text
  splits: "Single BIG-bench task file of 54,668 examples; the source VitaminC dataset separately defines train/validation/test splits of about 371,000/63,100/55,200"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration); source dataset by MIT CSAIL (Schuster, Fisch, Barzilay)"
  authors:
    - "Tal Schuster"
    - "Adam Fisch"
    - "Regina Barzilay"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/vitaminc_fact_verification"
paper:
  title: "Get Your Vitamin C! Robust Fact Verification with Contrastive Evidence"
  arxiv: "2103.08541"
  url: "https://arxiv.org/abs/2103.08541"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/vitaminc_fact_verification"
released: "2021"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No maintained leaderboard or per-model score table specific to this BIG-bench task
    (distinct from the original VitaminC paper's own fine-tuned-model results) was found for this
    page, so saturation is not established.
contamination:
  risk: medium
  note: >
    The BIG-bench task file (54,668 examples) has been publicly downloadable since 2021, and the
    full VitaminC dataset is separately and openly hosted on the Hugging Face Hub, so exact
    claim-evidence-label triples could appear in training corpora. No canary-string exclusion
    marker was found for this task in the source read for this page.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "vitaminc_fact_verification"
  other: ""
tags:
  - fact-verification
  - wikipedia
  - contrastive
  - big-bench
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/vitaminc_fact_verification"
    title: "BIG-bench vitaminc_fact_verification task directory (README: task description, 54,668 multiple-choice examples, multiple_choice_grade metric, authors, citation, CC BY-SA 3.0 note)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2103.08541"
    title: "Get Your Vitamin C! Robust Fact Verification with Contrastive Evidence (Schuster, Fisch, Barzilay, NAACL 2021): over 100,000 Wikipedia revisions, 400,000+ claim-evidence pairs, contrastive construction"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/tals/vitaminc"
    title: "tals/vitaminc dataset card on Hugging Face Hub: CC-BY-SA-3.0 licence, SUPPORTS/REFUTES/NOT ENOUGH INFO labels, split sizes (train 371,000 / validation 63,100 / test 55,200)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-008"
---

## What it measures

VitaminC Fact Verification gives a model a claim and a short passage of evidence taken from
Wikipedia, and asks it to classify whether the evidence "SUPPORTS", "REFUTES", or gives "NOT
ENOUGH INFO" about the claim. Because the source dataset was built from real Wikipedia edits that
changed an underlying fact, many claim-evidence pairs are contrastive: nearly identical wording
paired with evidence that differs only in the fact that was edited. That design specifically tests
whether a model follows the evidence in front of it rather than defaulting to facts it may have
memorised elsewhere, in addition to ordinary reading comprehension for entailment.

## How it is scored

The task is a 3-way multiple-choice classification, scored with BIG-bench's
multiple_choice_grade metric (accuracy on the SUPPORTS/REFUTES/NOT ENOUGH INFO choice). A roughly
balanced 3-way choice implies a naive baseline near 1/3, though the exact label balance of the
54,668-example BIG-bench subset specifically was not confirmed from the sources read for this
page. No human baseline figure was found for this page.

## Dataset and licence

The BIG-bench task holds 54,668 multiple-choice examples, built by the task's own conversion
script from the underlying VitaminC dataset. The full VitaminC dataset is considerably larger:
about 489,000 claim-evidence pairs total, drawn from over 100,000 real Wikipedia revisions that
changed a fact plus additional synthetically constructed pairs, split into roughly 371,000 train,
63,100 validation and 55,200 test examples per its Hugging Face dataset card. Both the BIG-bench
task's README and the Hugging Face dataset card give the licence as CC BY-SA 3.0.

## Who publishes it

VitaminC was created by Tal Schuster, Adam Fisch and Regina Barzilay at MIT CSAIL and published as
"Get Your Vitamin C! Robust Fact Verification with Contrastive Evidence" at NAACL 2021. The
BIG-bench task adapting it into a multiple-choice evaluation format was contributed to the broader,
multi-author BIG-bench collaboration coordinated by Google researchers.

## Lineage

VitaminC Fact Verification is a BIG-bench adaptation of the standalone VitaminC dataset; it has no
predecessor or successor benchmark tracked in this repository and is one of several hundred
independent BIG-bench tasks rather than part of a family page here.

## Saturation and contamination

No maintained leaderboard or per-model score table specific to this BIG-bench multiple-choice
task was found for this page, distinct from the original paper's own results training and
evaluating smaller fact-verification models on the full dataset, so saturation for current
general-purpose language models is not established. Contamination risk is medium: the 54,668-item
BIG-bench task file has been public since 2021, and the much larger source VitaminC dataset is
openly hosted on the Hugging Face Hub, increasing the chance that exact claim-evidence-label
triples appear in training data; no canary-string exclusion marker was found for this task.

## How to run it

Run as the `vitaminc_fact_verification` task in the BIG-bench repository
(`bigbench/benchmark_tasks/vitaminc_fact_verification`). No confirmed equivalent task name was
found in lm-evaluation-harness, inspect_evals, HELM or OpenCompass for this page; scores should
not be compared against results computed directly on the full, differently-sized VitaminC dataset
using the original paper's own fine-tuning and evaluation code, since that uses a much larger test
split and a different evaluation setup than this 54,668-example multiple-choice subset.

## Reading the numbers

A high score shows a model can read a short passage and correctly judge whether it supports,
contradicts, or is silent on a claim, including cases specifically constructed to conflict with
commonly known facts. Because the dataset is built around contrastive, near-identical claim pairs
differing only in the edited fact, strong performance is a more meaningful signal of evidence-based
reasoning than performance on fact-verification datasets without that contrastive design, where a
model could do well by pattern-matching claim wording alone. The benchmark does not test whether a
model can locate relevant evidence itself, only whether it can judge evidence that is already
provided.
