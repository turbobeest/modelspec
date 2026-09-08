---
id: pubmedqa
name: PubMedQA
aliases:
  - PQA-L
page_kind: benchmark
category: domain
subcategory: biomedical literature question answering
status: active
summary: Yes/no/maybe research questions answered from their source PubMed abstract, testing biomedical reading comprehension.
measures: >
  PubMedQA tests whether a model can answer a yes/no/maybe research question using the PubMed abstract
  that the question was derived from. Each item pairs a question phrased from a paper's own title or
  conclusion (for example, "Do preoperative statins reduce atrial fibrillation after coronary artery
  bypass grafting?") with that paper's abstract, and asks the model to decide whether the abstract's
  evidence supports a yes, no, or maybe/inconclusive answer. It is a single-turn, English-language,
  text-only reading-comprehension task grounded in biomedical research literature rather than clinical
  practice or exam questions, which sets it apart from MedQA and MedMCQA.
task_format: >
  Three-way yes/no/maybe classification given a research question and its source PubMed abstract.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: 78.0
  baseline_note: >
    The original paper reports a human performance ceiling of 78.0% and its own simple baseline model
    (driven by the imbalanced "yes" majority class rather than blind guessing) at 55.2%, both higher
    than the 33.3% chance rate for uniform random guessing across three labels.
dataset:
  size: 1000
  size_note: >
    The 1,000-item expert-annotated subset (PQA-L) is the evaluation set used for reported accuracy
    scores. The full release totals 273,518 instances: PQA-L (1,000, expert-labelled) plus two
    non-evaluation subsets intended for training/weak supervision, PQA-U (61,200 unlabelled) and PQA-A
    (211,300 artificially generated, labelled automatically from paper conclusions).
  url: https://huggingface.co/datasets/qiaojin/PubMedQA
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: >
    1,000 expert-labelled questions (PQA-L) used for evaluation, commonly reported via ten-fold
    cross-validation; EleutherAI's lm-evaluation-harness instead evaluates a single fixed fold (fold 0).
    Exact per-fold train/validation/test counts were not established from the sources reviewed for this
    page.
  public_test_set: true
publisher:
  org: University of Pittsburgh
  authors:
    - Qiao Jin
    - Bhuwan Dhingra
    - Zhengping Liu
    - William W. Cohen
    - Xinghua Lu
  url: https://pubmedqa.github.io
paper:
  title: "PubMedQA: A Dataset for Biomedical Research Question Answering"
  arxiv: "1909.06146"
  url: https://arxiv.org/abs/1909.06146
  year: 2019
leaderboard_url: https://pubmedqa.github.io
repo_url: https://github.com/pubmedqa/pubmedqa
released: "2019-09"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 82.0
  as_of: "2023-11"
  note: >
    PubMedQA's own leaderboard shows GPT-4 with Microsoft's Medprompt technique leading at 82.0%
    accuracy in the "reasoning-required" setting as of November 2023, already above the 78.0% human
    performance figure the original 2019 paper reported. Not every later model has kept pace: Google's
    MedGemma Technical Report reported 76.8% (text-only) and 77.2% (multimodal) for its 27B model in
    July 2025, both below the 2023 GPT-4-Medprompt figure and the human baseline.
contamination:
  risk: high
  note: >
    The 1,000-item labelled evaluation set, with answers included, has been public since September
    2019. The larger 211,300-item artificially labelled subset is also commonly used as biomedical
    fine-tuning data in its own right. Neither carries a canary string or gating mechanism, which makes
    clean held-out evaluation increasingly unlikely this many years after release.
harness:
  lm_eval: pubmedqa
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness's pubmedqa task reads the bigbio/pubmed_qa mirror's
    pubmed_qa_labeled_fold0_source configuration and scores three-way (yes/no/maybe) accuracy against
    that single cross-validation fold rather than the authors' own ten-fold protocol.
tags:
  - medical
  - biomedical-literature
  - yes-no-maybe
  - reading-comprehension
sources:
  - url: https://arxiv.org/abs/1909.06146
    title: "PubMedQA: A Dataset for Biomedical Research Question Answering"
    accessed: "2026-09-08"
  - url: https://github.com/pubmedqa/pubmedqa
    title: "pubmedqa/pubmedqa GitHub repository"
    accessed: "2026-09-08"
  - url: https://pubmedqa.github.io
    title: "PubMedQA project site and leaderboard"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/qiaojin/PubMedQA
    title: "qiaojin/PubMedQA dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/pubmedqa/pubmedqa.yaml
    title: "pubmedqa task config, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: https://aclanthology.org/D19-1259/
    title: "PubMedQA: A Dataset for Biomedical Research Question Answering, ACL Anthology (EMNLP-IJCNLP 2019)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2507.05201
    title: "MedGemma Technical Report"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice O"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

PubMedQA tests whether a model can answer a yes/no/maybe research question using the PubMed abstract
that the question was derived from. Each item pairs a question phrased from a paper's own title or
conclusion (for example, "Do preoperative statins reduce atrial fibrillation after coronary artery
bypass grafting?") with that paper's abstract, and asks the model to decide whether the abstract's
evidence supports a yes, no, or maybe/inconclusive answer. It is a single-turn, English-language,
text-only reading-comprehension task grounded in biomedical research literature rather than clinical
practice or exam questions, which sets it apart from MedQA and MedMCQA.

## How it is scored

Models are graded on three-way classification accuracy (yes/no/maybe). A model guessing uniformly at
random across the three labels would score roughly 33%, but the classes are not evenly distributed: the
original paper's own simple baseline, driven by the imbalanced "yes" majority class, already scores
55.2%, against a best-model score of 68.1% and a human performance ceiling of 78.0% reported in the
paper. Most current evaluations use only the 1,000-item expert-labelled subset (PQA-L) as the scored
set, commonly following a ten-fold cross-validation protocol; EleutherAI's lm-evaluation-harness, for
instance, evaluates against a single fixed fold (fold 0) of that split rather than all ten.

## Dataset and licence

The full PubMedQA release totals 273,518 question-answer instances across three subsets: 1,000
expert-annotated instances (PQA-L, the subset used for reported accuracy scores), 61,200 unlabelled
instances (PQA-U) and 211,300 artificially generated instances (PQA-A, labelled automatically from paper
conclusions rather than by human annotators). Only PQA-L functions as an evaluation set; PQA-U and PQA-A
are intended as additional pretraining or weak-supervision data. The dataset and code are released under
the MIT licence and hosted on GitHub and Hugging Face, with answers included in the public PQA-L files.

## Who publishes it

PubMedQA was introduced by Qiao Jin, Bhuwan Dhingra, Zhengping Liu, William W. Cohen and Xinghua Lu,
affiliated with the University of Pittsburgh, Carnegie Mellon University and Google AI, and presented at
EMNLP-IJCNLP 2019. The dataset and an accuracy leaderboard are maintained by the authors at
pubmedqa.github.io, where submissions are still accepted by email; the site records its leaderboard as
last updated in April 2024.

## Lineage

PubMedQA has no formal predecessor or successor of its own. Like MedQA and MedMCQA, both of which have
pages in this repository, it is one of the components Google folded into its "MultiMedQA" evaluation
suite for Med-PaLM and Med-PaLM 2, and the three are commonly reported together by medical-specialist
model developers. It is not a variant of either: all three were built independently, by different
groups, from different source material (licensing exams versus research abstracts).

## Saturation and contamination

PubMedQA's own leaderboard shows GPT-4 with Microsoft's Medprompt technique leading at 82.0% accuracy in
the "reasoning-required" setting as of November 2023, already above the 78.0% human performance figure
the original 2019 paper reported — a rare case among the benchmarks on this site where a widely cited
score has clearly passed the paper's own human baseline. Not every later model has kept pace, though:
Google's MedGemma Technical Report reported 76.8% (text-only) and 77.2% (multimodal) for its 27B model in
July 2025, both below the 2023 GPT-4-Medprompt score. Contamination risk is high: the labelled evaluation
set has been public with answers since September 2019, and the larger artificially labelled subset is
commonly used as biomedical fine-tuning data in its own right, both circumstances that make clean
held-out evaluation increasingly unlikely seven years on.

## How to run it

EleutherAI's lm-evaluation-harness implements the task as `pubmedqa`, reading the bigbio/pubmed_qa
mirror's `pubmed_qa_labeled_fold0_source` configuration and scoring three-way (yes/no/maybe) accuracy
against that single cross-validation fold rather than the authors' own ten-fold protocol. Because the
authors' leaderboard, the ten-fold protocol, and the harness's single-fold shortcut are three different
evaluation setups, and because "reasoning-required" and "reasoning-free" variants exist depending on
whether the model also sees the paper's long-form answer, PubMedQA scores from different sources need
their protocol checked before they are compared.

## Reading the numbers

A high PubMedQA score shows a model can extract a yes/no/maybe verdict from a research abstract the way
the paper's own conclusion does, not that it can appraise biomedical evidence the way a researcher or
clinician would, and certainly not that it is fit for clinical decision-making. Google, which reports
PubMedQA for MedGemma alongside MedQA and MedMCQA, states plainly that model outputs "are not intended to
directly inform clinical diagnosis, patient management decisions, treatment recommendations, or any
other direct clinical practice applications" and require independent clinical verification. Because the
benchmark's top scores already sit at or above its own reported human baseline, treat further gains as
diminishing in significance, and check whether a reported number came from the reasoning-required or
reasoning-free protocol before comparing it to another model's.
