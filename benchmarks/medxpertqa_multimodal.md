---
id: medxpertqa_multimodal
name: MedXpertQA MM
aliases:
  - MedXpertQA Multimodal
  - MedXpertQA-MM
page_kind: benchmark
category: domain
subcategory: expert-level multimodal clinical reasoning
status: active
summary: The multimodal split of MedXpertQA, pairing expert-level clinical questions with medical images and up to ten answer options.
measures: >
  This page covers MedXpertQA MM, the multimodal split of the MedXpertQA benchmark. Each item pairs an
  expert-level clinical question, drawn from and modelled on specialty board exam material across 17
  medical specialties and 11 body systems, with one or more medical images (for example a radiograph,
  histopathology slide, or ECG trace) and supporting clinical documentation such as history and exam
  findings. The model must integrate the image and the text to answer. Example questions on the
  project's own site show as many as ten lettered answer options, noticeably more than the four or five
  typical of MedQA or MedMCQA. Questions are also labelled by type, "Understanding" (applying known
  medical knowledge) or "Reasoning" (multi-step clinical inference). MedXpertQA's other half, a
  text-only split called MedXpertQA Text, does not have a separate page in this repository; be careful
  to check which split a reported "MedXpertQA" score refers to.
task_format: >
  Multiple-choice clinical question paired with one or more medical images and supporting exam
  findings; the model returns a single letter from as many as ten options.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    Answer-option counts vary by question and can run as high as ten (observed directly in example
    questions on the project's site), so a single fixed random-guessing percentage does not apply
    across the whole set the way it does for a fixed four-option benchmark; no human baseline was
    established from the sources reviewed for this page.
dataset:
  size: 2005
  size_note: >
    The MM (multimodal) split contains 2,005 questions: 5 development examples and 2,000 test
    examples. It sits alongside a separate Text split of 2,455 questions (5 dev, 2,450 test) from the
    same release, not covered by this id; combined, the two splits total the 4,460 questions the paper
    reports.
  url: https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA
  license: MIT
  languages:
    - en
  modalities:
    - text
    - image
  splits: "5 dev / 2,000 test (MM configuration only)"
  public_test_set: true
publisher:
  org: Tsinghua University
  authors:
    - Yuxin Zuo
    - Shang Qu
    - Yifei Li
    - Zhangren Chen
    - Xuekai Zhu
    - Ermo Hua
    - Kaiyan Zhang
    - Ning Ding
    - Bowen Zhou
  url: https://github.com/TsinghuaC3I/MedXpertQA
paper:
  title: "MedXpertQA: Benchmarking Expert-Level Medical Reasoning and Understanding"
  arxiv: "2501.18362"
  url: https://arxiv.org/abs/2501.18362
  year: 2025
leaderboard_url: https://medxpertqa.github.io
repo_url: https://github.com/TsinghuaC3I/MedXpertQA
released: "2025-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 56.28
  as_of: "2025-02"
  note: >
    As of the leaderboard's most recent recorded update (20 February 2025), OpenAI's o1 (a December
    2024 model) leads the MM track with a 56.28% average, well clear of the next-best model, Qwen's
    QVQ-72B-Preview, at 33.55%, and both are well short of the 100% ceiling. The project's news feed
    shows no leaderboard update after that date through its most recent entry (an ICML acceptance
    announcement in May 2025), so this snapshot may not reflect models released since.
contamination:
  risk: medium
  note: >
    The authors state they used data synthesis specifically "to mitigate data leakage risk," but the
    dataset has been publicly hosted on GitHub and Hugging Face, ungated and without a canary string,
    since February 2025, which is enough time for some exposure even with that stated mitigation.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No MedXpertQA task exists in EleutherAI's lm-evaluation-harness as of this research (its GitHub
    tasks directory returns a 404 for "medxpertqa"). The authors' own GitHub repository ships the
    reference evaluation code, and the project's changelog states it was integrated into OpenCompass in
    April 2025 (tracked as pull request #2002 on open-compass/opencompass), though the exact registered
    OpenCompass task name could not be confirmed from the sources reviewed.
tags:
  - medical
  - multimodal
  - clinical-reasoning
  - multiple-choice
  - expert-level
sources:
  - url: https://arxiv.org/abs/2501.18362
    title: "MedXpertQA: Benchmarking Expert-Level Medical Reasoning and Understanding"
    accessed: "2026-09-08"
  - url: https://github.com/TsinghuaC3I/MedXpertQA
    title: "TsinghuaC3I/MedXpertQA GitHub repository"
    accessed: "2026-09-08"
  - url: https://medxpertqa.github.io
    title: "MedXpertQA project site and leaderboard"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA
    title: "TsinghuaC3I/MedXpertQA dataset card, Hugging Face"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice O"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

This page covers MedXpertQA MM, the multimodal split of the MedXpertQA benchmark. Each item pairs an
expert-level clinical question, drawn from and modelled on specialty board exam material across 17
medical specialties and 11 body systems, with one or more medical images (for example a radiograph,
histopathology slide, or ECG trace) and supporting clinical documentation such as history and exam
findings. The model must integrate the image and the text to answer. Example questions on the project's
site show as many as ten lettered answer options, more than the four or five typical of MedQA or
MedMCQA. Questions are also labelled by type, "Understanding" (applying known medical knowledge) or
"Reasoning" (multi-step clinical inference), so scores can be broken down by skill.

MedXpertQA's other half, a text-only split called MedXpertQA Text, does not have a separate page in this
repository; check which split a reported "MedXpertQA" score refers to, since this page covers only the
multimodal (MM) split.

## How it is scored

Models are graded on accuracy over lettered multiple-choice options, whose count varies by question and
can run as high as ten, so a single fixed random-guessing baseline does not apply across the whole set
the way it does for a fixed four-option benchmark. The official leaderboard reports separate averages for
"Reasoning" and "Understanding" question types within the MM split, plus an overall MM average, and
separately tracks models as large multimodal models (evaluated with the images) versus text-only models
(evaluated on the same questions as text), letting the site show how much a model's score depends on
actually using the image.

## Dataset and licence

The MM split contains 2,005 questions: 5 development examples and 2,000 test examples, both public with
answers. It sits alongside a separate Text split of 2,455 questions (5 dev, 2,450 test) from the same
release; combined, the two splits total the 4,460 questions the paper reports. The dataset and code are
released under the MIT licence and hosted on GitHub and Hugging Face; English only.

## Who publishes it

MedXpertQA was introduced by Yuxin Zuo, Shang Qu, Yifei Li, Zhangren Chen, Xuekai Zhu, Ermo Hua, Kaiyan
Zhang, Ning Ding and Bowen Zhou, affiliated with Tsinghua University and the Shanghai Artificial
Intelligence Laboratory. The paper first appeared on arXiv in January 2025, the dataset was released in
February 2025, and the work was accepted to ICML 2025. The authors maintain a standing leaderboard at
medxpertqa.github.io, which accepts community submissions.

## Lineage

MedXpertQA has no family page in this repository and no formal predecessor of its own. It shares a
domain with the other medical benchmarks in this batch (MedQA, MedMCQA, PubMedQA), all of which have
pages here, but was built independently by a different group and is not a variant of any of them. Its
own Text-only sibling split, MedXpertQA Text, does not yet have a page in this repository.

## Saturation and contamination

As of the leaderboard's most recent recorded update (20 February 2025), OpenAI's o1 (a December 2024
model) leads the MM track with a 56.28% average, well clear of the next-best model, Qwen's
QVQ-72B-Preview, at 33.55%, and both are well short of the 100% ceiling. The project's own news feed
shows no leaderboard update after that date through its most recent entry (an ICML acceptance
announcement in May 2025), so this snapshot may not reflect models released since. That wide gap between
the top model and the rest, plus the distance from the ceiling, points to an open benchmark rather than
a saturated one. Contamination risk sits at medium: the authors state they used data synthesis
specifically "to mitigate data leakage risk," but the dataset has been publicly hosted, ungated and
without a canary string since February 2025, which is enough time for some exposure even with that
mitigation.

## How to run it

The authors' GitHub repository ships the reference evaluation code and was, per the project's changelog,
integrated into OpenCompass in April 2025 (pull request #2002 on open-compass/opencompass); the exact
registered OpenCompass task name could not be confirmed. No MedXpertQA task exists in EleutherAI's
lm-evaluation-harness as of this research. Because the benchmark separately reports large-multimodal-model
and text-only tracks plus a Reasoning/Understanding breakdown, check which track and subtype a reported
score covers before comparing it across models.

## Reading the numbers

A high MedXpertQA MM score shows a model can combine a medical image with clinical text to pick the
intended answer to an expert-level exam-style question, not that it is ready for real diagnostic or
clinical use. The project's own site states plainly that "MedXpertQA is for research purposes only" and
that "models evaluated on MedXpertQA can produce unexpected results." Because the top score is still well
below the ceiling and well ahead of the next-best model, treat current results as showing meaningful
separation between reasoning-focused and vanilla models rather than a benchmark that has stopped
discriminating, and always confirm whether a score comes from the MM track, the Text track, or a
text-only evaluation of MM's questions.
