---
id: medqa
name: MedQA
aliases:
  - MedQA-USMLE
  - MedQA-USMLE-4-options
page_kind: benchmark
category: domain
subcategory: medical licensing exam question answering
status: active
summary: Four-option USMLE-style clinical multiple-choice questions, the most widely reported medical exam benchmark for LLMs.
measures: >
  MedQA tests whether a model can pick the correct answer to a clinical multiple-choice question
  written in the style of the United States Medical Licensing Examination. Most questions present a
  short patient vignette (age, presenting symptoms, exam findings, sometimes lab values) and ask for a
  diagnosis, a next step in management, or an underlying mechanism, then offer several candidate
  answers. It is a single-turn, English-language, text-only task built from real practice-exam question
  banks rather than written for the benchmark, so it leans on applied clinical reasoning more than
  isolated fact recall.
task_format: >
  Four-option multiple-choice clinical vignette question; the model returns a single letter answer
  (A-D), usually zero-shot or few-shot.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: >
    A numeric USMLE passing threshold and a physician baseline score were not established from the
    sources reviewed for this page, so neither is reported here.
dataset:
  size: 12723
  size_note: >
    12,723 English-language USMLE-style questions, matching both the original paper's reported count
    and the train/validation/test split sizes on the commonly used four-option Hugging Face mirror
    (10,178 / 1,272 / 1,273). The original release also contains 34,251 Simplified Chinese questions
    (from Mainland Chinese licensing exams) and 14,123 Traditional Chinese questions (from Taiwanese
    exams); those are separate subsets not covered by this page's id. Source questions were originally
    released with up to five options; the four-option variant used by lm-evaluation-harness and most
    model reports was produced by randomly deleting one wrong option per question.
  url: https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options-hf
  license: "Not stated by the paper; the authors' GitHub repository is MIT-licensed; the accompanying textbook corpus is released under a research-use-only agreement"
  languages:
    - en
  modalities:
    - text
  splits: "10,178 train / 1,272 validation / 1,273 test (four-option English mirror)"
  public_test_set: true
publisher:
  org: "MIT Computer Science and Artificial Intelligence Laboratory (CSAIL)"
  authors:
    - Di Jin
    - Eileen Pan
    - Nassim Oufattole
    - Wei-Hung Weng
    - Hanyi Fang
    - Peter Szolovits
  url: https://github.com/jind11/MedQA
paper:
  title: "What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams"
  arxiv: "2009.13081"
  url: https://arxiv.org/abs/2009.13081
  year: 2020
leaderboard_url: ""
repo_url: https://github.com/jind11/MedQA
released: "2020-09"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 89.8
  as_of: "2025-07"
  note: >
    Google's Med-PaLM 2 reported 86.5% on MedQA in May 2023. Google's MedGemma Technical Report put
    MedGemma 27B at 87.7% zero-shot and 89.8% with best-of-5 test-time scaling in July 2025. No
    continuously updated public leaderboard was found during this research; recent scores mostly
    surface inside individual model papers and system cards rather than one standing tracker, so a
    single current global top score could not be confirmed beyond these two dated data points.
contamination:
  risk: high
  note: >
    The English question-and-answer set, including test-split answers, has been publicly downloadable
    from GitHub without gating since September 2020, giving it about six years of exposure to web
    crawls and model training corpora as of this research. No canary string or access agreement covers
    the question set itself, only the separately licensed textbook corpus.
harness:
  lm_eval: medqa_4options
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness's medqa_4options task reads the GBaker/MedQA-USMLE-4-options-hf mirror and
    scores multiple_choice accuracy and normalized accuracy over the 1,273-question test split.
tags:
  - medical
  - multiple-choice
  - usmle
  - clinical-vignette
sources:
  - url: https://arxiv.org/abs/2009.13081
    title: "What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams"
    accessed: "2026-09-08"
  - url: https://github.com/jind11/MedQA
    title: "jind11/MedQA GitHub repository"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options-hf
    title: "GBaker/MedQA-USMLE-4-options-hf dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/bigbio/med_qa
    title: "bigbio/med_qa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/medqa/medqa.yaml
    title: "medqa_4options task config, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2507.05201
    title: "MedGemma Technical Report"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2305.09617
    title: "Towards Expert-Level Medical Question Answering with Large Language Models (Med-PaLM 2)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/google/medgemma-27b-it
    title: "google/medgemma-27b-it model card, Hugging Face"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice O"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MedQA tests whether a model can pick the correct answer to a clinical multiple-choice question written
in the style of the United States Medical Licensing Examination. Most questions present a short patient
vignette (age, presenting symptoms, exam findings, sometimes lab values) and ask for a diagnosis, a next
step in management, or an underlying mechanism, then offer several candidate answers. It is a
single-turn, English-language, text-only task built from real practice-exam question banks rather than
written for the benchmark, so it leans on applied clinical reasoning more than isolated fact recall.

The id on this page covers only the English/USMLE-style subset. The original 2020 release also published
much larger Simplified Chinese (34,251 questions, from Mainland Chinese licensing exams) and Traditional
Chinese (14,123 questions, from Taiwanese exams) subsets; those are rarely reported in model cards and
are not covered by this id.

## How it is scored

Models are graded on accuracy: the share of questions answered with the correct letter. Most reported
scores use the four-option variant, where random guessing scores 25%. The source questions originally
shipped with up to five options; the widely used four-option version was produced by randomly deleting
one incorrect option per question, so "MedQA" and "MedQA 4-options" scores are not always directly
comparable to older five-option numbers. Most evaluations run the model zero-shot or few-shot and
compare its selected letter against the labelled answer; some system cards instead report a best-of-N
or self-consistency variant that samples several completions and takes a majority vote, which raises
scores relative to a single greedy pass.

## Dataset and licence

The evaluation subset most models report is the English-language question bank: 12,723 questions, split
10,178/1,272/1,273 across train, validation and test on the commonly used four-option Hugging Face
mirror. Questions were collected from professional medical board exam question banks rather than written
for the benchmark. The GitHub repository carries an MIT licence badge, but the paper states the
accompanying medical-textbook corpus (included to support retrieval-based baselines) is released only
under a research-use-only agreement, so the textbooks' licensing differs from that on the question
pairs. Hugging Face's listing for the multilingual mirror records the licence as unspecified. Test-split
answers are included in the public files; there is no gating.

## Who publishes it

MedQA was introduced by Di Jin, Eileen Pan, Nassim Oufattole, Wei-Hung Weng, Hanyi Fang and Peter
Szolovits, affiliated with MIT's Computer Science and Artificial Intelligence Laboratory, the MIT-IBM
Watson AI Lab, and Dialectic Inc., and posted to arXiv in September 2020. The authors maintain the
reference dataset and baseline code at github.com/jind11/MedQA. No single organisation runs an actively
updated public leaderboard for it today; current scores mostly surface inside individual model papers
and system cards, including Google's Med-PaLM, Med-PaLM 2 and MedGemma reports.

## Lineage

MedQA has no formal predecessor or successor of its own, but Google bundled it into the "MultiMedQA"
evaluation suite for Med-PaLM and Med-PaLM 2, alongside MedMCQA and PubMedQA (both of which also have
pages in this repository). It sits in the same broad space as MedMCQA (Indian medical entrance exams)
and the newer, harder MedXpertQA (2025). None of these is a formal variant of MedQA: each was built
independently, with its own question sources and methodology.

## Saturation and contamination

Reported scores have risen substantially since 2020. Google's Med-PaLM 2 reported 86.5% in May 2023;
Google's MedGemma Technical Report reported 87.7% zero-shot and 89.8% with best-of-5 test-time scaling
for its 27B model in July 2025. That is a narrowing gap to a perfect score in just over two years, though
no confirmed physician or passing-score baseline exists in the sources reviewed here to weigh it against.
Contamination risk is high: the English question-and-answer set, including test-split answers, has been
downloadable from GitHub without any gating or canary string since September 2020, giving it roughly six
years of exposure to web crawls and model training corpora.

## How to run it

EleutherAI's lm-evaluation-harness implements the standard four-option task as `medqa_4options`, reading
the GBaker/MedQA-USMLE-4-options-hf mirror and scoring accuracy and normalized accuracy over the
1,273-question test split. Because the four-option filtering step was done independently of the paper's
original authors, and because system cards vary in whether they report zero-shot, few-shot or best-of-N
sampling, MedQA scores from different sources are not always computed the same way.

## Reading the numbers

A high MedQA score shows a model is good at picking the textbook-favoured answer to an exam-style
clinical vignette under exam conditions, not that it is safe or competent to use in real patient care.
Google draws exactly that line for MedGemma, which reports MedQA among its headline numbers: its model
card states that outputs "are not intended to directly inform clinical diagnosis, patient management
decisions, treatment recommendations, or any other direct clinical practice applications," and that all
outputs require independent clinical verification. Read a MedQA number alongside MedMCQA and PubMedQA,
which test differently structured medical knowledge, and treat scores from different harnesses, shot
counts or sampling strategies as only roughly comparable.
