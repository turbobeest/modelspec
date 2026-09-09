---
id: medmcqa
name: MedMCQA
aliases:
  - Med-MCQA
page_kind: benchmark
category: domain
subcategory: medical entrance exam question answering
status: active
summary: Over 194,000 multiple-choice questions from India's AIIMS and NEET PG medical entrance exams, across 21 subjects.
measures: >
  MedMCQA tests whether a model can answer multiple-choice medical questions drawn from two of India's
  largest postgraduate medical entrance examinations, AIIMS and NEET PG. Each question covers one of 21
  medical subjects (anatomy, pharmacology, surgery, obstetrics, and so on) and asks for the single best
  answer among several options, mirroring the format used to screen doctors applying for postgraduate
  specialty training in India. It is a single-turn, English-language, text-only task; the authors report
  it requires more than ten distinct types of reasoning across the question set, from single-fact recall
  to multi-hop clinical reasoning. Because the exams it draws from are specific to the Indian medical
  curriculum, its subject mix and phrasing differ somewhat from the US-focused MedQA, even though both
  are "medical multiple-choice" benchmarks.
task_format: >
  Four-option multiple-choice medical exam question; the model returns a single letter answer (A-D).
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: >
    No physician or expert human baseline was established from the sources reviewed for this page.
dataset:
  size: 193155
  size_note: >
    182,822 training, 6,150 validation and 4,183 test questions, summing to 193,155; the paper's own
    abstract rounds this to "more than 194k." Only training and validation examples ship with answers;
    the authors withhold test-set ground truth specifically to preserve leaderboard integrity, so most
    automated evaluations (including EleutherAI's lm-evaluation-harness) score against the public
    validation split as a proxy test set instead.
  url: https://github.com/MedMCQA/MedMCQA
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "182,822 train / 6,150 validation / 4,183 test (test-set answers withheld by the authors)"
  public_test_set: false
publisher:
  org: Saama AI Research
  authors:
    - Ankit Pal
    - Logesh Kumar Umapathi
    - Malaikannan Sankarasubbu
  url: https://github.com/MedMCQA/MedMCQA
paper:
  title: "MedMCQA: A Large-scale Multi-Subject Multi-Choice Dataset for Medical domain Question Answering"
  arxiv: "2203.14371"
  url: https://arxiv.org/abs/2203.14371
  year: 2022
leaderboard_url: https://medmcqa.github.io/
repo_url: https://github.com/MedMCQA/MedMCQA
released: "2022-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 74.2
  as_of: "2025-07"
  note: >
    The project's own leaderboard, checked during this research, still shows a top dev-accuracy figure
    around 63%, with no date attached, reflecting BERT-style and early GPT-era submissions rather than
    current frontier models. Google's MedGemma Technical Report reported a materially higher 74.2% for
    its 27B model in July 2025, suggesting the official leaderboard has not kept pace with current
    model reports and should not be read as a live ranking of frontier models.
contamination:
  risk: medium
  note: >
    The authors' withheld test set carries low risk if it is actually used, since its answers are not
    public. But the training and validation splits, including the validation split most automated
    harnesses score against as a proxy test set, have been fully public with answers since March 2022,
    more than four years before this research, long enough for likely inclusion in large training
    corpora.
harness:
  lm_eval: medmcqa
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness's medmcqa task reads the openlifescienceai/medmcqa mirror on Hugging Face and
    sets both its "validation" and "test" split fields to the dataset's public validation split, since
    the authors do not distribute test-set labels; it scores accuracy and normalized accuracy.
tags:
  - medical
  - multiple-choice
  - medical-entrance-exam
  - india
sources:
  - url: https://arxiv.org/abs/2203.14371
    title: "MedMCQA: A Large-scale Multi-Subject Multi-Choice Dataset for Medical domain Question Answering"
    accessed: "2026-09-08"
  - url: https://github.com/MedMCQA/MedMCQA
    title: "MedMCQA/MedMCQA GitHub repository"
    accessed: "2026-09-08"
  - url: https://medmcqa.github.io/
    title: "MedMCQA project site and leaderboard"
    accessed: "2026-09-08"
  - url: https://proceedings.mlr.press/v174/pal22a.html
    title: "MedMCQA: A Large-scale Multi-Subject Multi-Choice Dataset for Medical domain Question Answering, Proceedings of CHIL 2022"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/medmcqa/medmcqa.yaml
    title: "medmcqa task config, EleutherAI lm-evaluation-harness"
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

MedMCQA tests whether a model can answer multiple-choice medical questions drawn from two of India's
largest postgraduate medical entrance examinations, AIIMS and NEET PG. Each question covers one of 21
medical subjects (anatomy, pharmacology, surgery, obstetrics, and so on) and asks for the single best
answer among several options, mirroring the format used to screen doctors applying for postgraduate
specialty training in India. It is a single-turn, English-language, text-only task; the authors report
it requires more than ten distinct types of reasoning across the question set, from single-fact recall
to multi-hop clinical reasoning.

Because the exams it draws from are specific to the Indian medical curriculum, MedMCQA's subject mix and
phrasing differ somewhat from the US-focused MedQA, even though both are "medical multiple-choice"
benchmarks.

## How it is scored

Models are scored on accuracy over four answer options, so random guessing scores 25%. The dataset ships
with a training split, a validation split, and a test split whose ground-truth labels are withheld by the
authors specifically to preserve the leaderboard's integrity; researchers submit predictions through a
form rather than scoring locally against the test set. In practice, most automated evaluations, including
EleutherAI's lm-evaluation-harness, score models against the public validation split instead, using it as
a stand-in test set, so a "MedMCQA" number in a model card is more often a validation-split score than a
true held-out test score.

## Dataset and licence

MedMCQA contains 182,822 training, 6,150 validation and 4,183 test questions, a total of 193,155 (the
paper's abstract rounds this to "more than 194k"), collected from AIIMS and NEET PG exam question banks
covering around 2,400 healthcare topics. The dataset and code are released under the MIT licence, and the
authors distribute both through a GitHub repository and a project site (medmcqa.github.io) that also
hosts the leaderboard and submission form. Only training and validation examples ship with answers;
test-set answers are held by the authors.

## Who publishes it

MedMCQA was introduced by Ankit Pal, Logesh Kumar Umapathi and Malaikannan Sankarasubbu of Saama AI
Research in Chennai, India, and published at the 2022 ACM Conference on Health, Inference, and Learning
(CHIL), with a preprint posted to arXiv in March 2022. The authors maintain the reference dataset, code
and leaderboard themselves; no independent tracker for MedMCQA was found during this research.

## Lineage

MedMCQA has no formal predecessor or successor. It is one of the components Google bundled into its
"MultiMedQA" evaluation suite for Med-PaLM and Med-PaLM 2, alongside MedQA and PubMedQA (both of which
also have pages in this repository), and it is regularly reported together with those two by
medical-specialist model developers such as Google's MedGemma team. It is not a variant of MedQA: the two
were built independently, from different national exam systems, by different research groups.

## Saturation and contamination

The project's own leaderboard, checked during this research, still shows a top dev-accuracy figure
around 63%, with no date attached, reflecting BERT-style and early GPT-era submissions rather than
current frontier models. More recent individual model reports place scores well above that: Google's
MedGemma Technical Report put its 27B model at 74.2% in July 2025. Contamination risk sits at medium:
the authors' withheld test set carries low risk if it is actually used, but the training and validation
splits, including the validation split most automated harnesses score against, have been fully public
with answers since March 2022, more than four years before this research.

## How to run it

EleutherAI's lm-evaluation-harness implements the task as `medmcqa`, reading the
openlifescienceai/medmcqa mirror on Hugging Face and, notably, setting both its validation and test
split fields to the dataset's public validation split, since the authors do not distribute test-set
labels. It scores accuracy and normalized accuracy. Because the harness effectively evaluates against a
different split than the one the authors call "test," and because the authors' own leaderboard requires
an ungated prediction submission rather than local scoring, scores reported as "MedMCQA" can come from
either protocol and are not automatically comparable.

## Reading the numbers

A high MedMCQA score means a model reliably selects the answer intended by Indian postgraduate medical
entrance exam writers, not that it can practise medicine safely. Developers who report it alongside
MedQA and PubMedQA, such as Google's MedGemma team, pair it with an explicit disclaimer that outputs
"are not intended to directly inform clinical diagnosis, patient management decisions, treatment
recommendations, or any other direct clinical practice applications" and require independent clinical
verification. Because most published scores are actually validation-split scores rather than scores
against the authors' withheld test set, treat small differences between models with some caution, and
read MedMCQA alongside MedQA and PubMedQA rather than alone.
