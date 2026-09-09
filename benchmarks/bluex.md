---
id: bluex
name: "BLUEX (Brazilian Leading Universities Entrance eXams)"
aliases:
  - "Brazilian Leading Universities Entrance eXams"
page_kind: benchmark
category: knowledge
subcategory: "Brazilian university-entrance multiple-choice exams (Portuguese)"
status: active
summary: "Portuguese multiple-choice questions from Unicamp (Convest) and USP (Fuvest) entrance exams, including image-linked items that most text-only harnesses drop."
measures: >
  BLUEX tests whether a model can answer official Brazilian vestibular questions
  written in Portuguese. Items come from Unicamp’s Convest and USP’s Fuvest
  papers. Subjects span high-school fields such as mathematics, history, and
  languages. Many questions need an accompanying figure. Metadata flags image
  use, mathematical reasoning, and Brazil-specific knowledge. HELM’s scenario
  is text-only: it skips any item marked has_associated_images.
task_format: >
  Multiple-choice. HELM uses joint letter answering with a Portuguese
  instruction and one worked example, scored by exact match. The 2023 paper
  also used few-shot prompts drawn from a different year of the same university.
metric:
  name: exact_match (HELM); accuracy in the original paper
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 22.0
  human_baseline: 52.1
  baseline_note: >
    Paper Table 3, text-only subset of 638 questions: random 0.220, mean
    exam-taker score 0.521, mean medicine cutoff 0.863. GPT-4 scored 0.748 on
    that subset in 2023. HELM does not reuse those human or cutoff figures.
dataset:
  size: 1422
  size_note: >
    Hugging Face portuguese-benchmark-datasets/BLUEX default split `questions`
    has 1,422 rows (API and card, accessed 2026-09-08); the viewer includes
    ids such as USP_2025_55, so the live dump is not limited to 2018–2024.
    The project README currently says 1,260 questions from 2018–2024, 724
    without images. Paper Table 1 lists 1,095 questions from 2018–2023
    (638 without images). HELM pins revision
    d99cf6d05b50db7c42a605e5e2924cbd46f076c7 and drops image items. These
    counts are not the same evaluation set.
  url: "https://huggingface.co/datasets/portuguese-benchmark-datasets/BLUEX"
  license: ""
  languages:
    - pt
  modalities:
    - text
    - image
  splits: "single `questions` split on Hugging Face; HELM maps surviving items to test"
  public_test_set: true
publisher:
  org: "University of Campinas (UNICAMP) / Portuguese-Benchmark-Datasets"
  authors:
    - "Thales Sales Almeida"
    - "Thiago Laitz"
    - "Giovana K. Bonás"
    - "Rodrigo Nogueira"
  url: "https://github.com/Portuguese-Benchmark-Datasets/BLUEX"
paper:
  title: "BLUEX: A benchmark based on Brazilian Leading Universities Entrance eXams"
  arxiv: "2307.05410"
  url: "https://arxiv.org/abs/2307.05410"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/Portuguese-Benchmark-Datasets/BLUEX"
released: "2023-07"
last_updated: "2025-08"
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
    On the paper’s 638-item text-only slice, GPT-4 reached 74.8% in 2023,
    below the 86.3% medicine cutoff reported in the same table. No current
    leaderboard top score for the 1,422-row Hugging Face dump or for HELM’s
    filtered run was confirmed here.
contamination:
  risk: high
  note: >
    Official vestibular questions and answer keys are published after each
    sitting. The 2018–2023 exams were already public when the paper appeared.
    The authors argued 2023 papers were then unlikely to be in many training
    sets; that claim does not hold for later models. Answers are public.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: bluex
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec `bluex` (bluex_run_specs.py): ADAPT_MULTIPLE_CHOICE_JOINT,
    Portuguese instructions, exact_match metrics. Scenario loads Hugging Face
    portuguese-benchmark-datasets/BLUEX at a pinned commit and skips image
    items. No licence file was present on the GitHub default branch when
    fetched; the Hugging Face card also omits a licence field.
tags:
  - portuguese
  - multiple-choice
  - exams
  - brazil
  - knowledge
sources:
  - url: "https://arxiv.org/abs/2307.05410"
    title: "BLUEX paper (arXiv:2307.05410)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2307.05410"
    title: "BLUEX full text (ar5iv); Table 3 human, random, GPT-4"
    accessed: "2026-09-08"
  - url: "https://github.com/Portuguese-Benchmark-Datasets/BLUEX"
    title: "Portuguese-Benchmark-Datasets/BLUEX README (1,260 / 724 counts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/portuguese-benchmark-datasets/BLUEX"
    title: "Hugging Face BLUEX dataset card (1,422 questions split)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/portuguese-benchmark-datasets/BLUEX"
    title: "Hugging Face API metadata for BLUEX"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/bluex_scenario.py"
    title: "HELM BLUEXScenario (image filter, pinned revision)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/bluex_run_specs.py"
    title: "HELM bluex run spec (Portuguese joint multiple choice)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-029 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-029"
---

## What it measures

BLUEX is a Portuguese exam benchmark built from Unicamp (Convest) and USP (Fuvest) entrance tests. Each item is a real multiple-choice question from those papers, with subject tags and flags for prior knowledge, text understanding, image use, and mathematical reasoning. The skill is high-school academic QA in Brazilian Portuguese, including items that only make sense with a figure.

HELM’s `bluex` scenario is narrower. It downloads the Hugging Face dump and discards every row with `has_associated_images`. A HELM number is therefore not a full multimodal BLUEX score.

## How it is scored

The 2023 paper reports accuracy on 638 text-only questions. Random guessing was 22.0% on that mix of four- and five-option items. Mean student scores were 52.1%, and the medicine cutoff was 86.3%. GPT-4 reached 74.8% in that table, still below the cutoff. HELM instead scores letter answers with exact match after a Portuguese instruction and one in-context example. Paper accuracy and HELM exact match on a later, image-filtered dump are not the same protocol.

## Dataset and licence

Sources disagree on size. Hugging Face currently lists 1,422 rows in split `questions` (card last updated 2025-08-08). The Hub preview includes 2025 Fuvest ids such as `USP_2025_55`. The GitHub README says 1,260 questions from 2018–2024, 724 without images. Paper Table 1 counts 1,095 questions from 2018–2023 and 638 without images (about 58% of that table; the results text says about 60%). HELM pins commit `d99cf6d…`, which is not the live Hugging Face SHA. No licence statement appears on the Hugging Face card or on a LICENSE file at the GitHub default branch; licence is left empty. The arXiv HTML page marks the *paper* CC BY 4.0; that is not a dataset licence.

## Who publishes it

Thales Sales Almeida, Thiago Laitz, Giovana K. Bonás and Rodrigo Nogueira, affiliated with UNICAMP (and, in the paper, Maritaca AI and NeuralMind), released the dataset in July 2023 (arXiv:2307.05410). Code and data live at Portuguese-Benchmark-Datasets/BLUEX. There is no dedicated live leaderboard confirmed here.

## Lineage

BLUEX is not a variant of [ENEM Challenge](enem_challenge.md). ENEM is the national secondary exam; BLUEX uses Unicamp and USP vestibulares. The ENEM Challenge page already names BLUEX as a related but separate Brazilian-exam benchmark. No successor page exists in this repository.

## Saturation and contamination

On the paper’s 638-item slice, GPT-4 was 74.8% in 2023 and had not reached the medicine cutoff. Whether later models close that gap on the current 1,422-row dump was not confirmed here. Contamination risk is high: official keys are public, older years date to 2018, and nothing is held out.

## How to run it

HELM: `bluex`. The scenario skips image questions, answers with a joint multiple-choice adapter, and scores exact match. Reproducing the paper requires the authors’ text-only filter and their year-matched few-shot rule, not HELM’s later pin. Do not mix a GitHub 1,260 count, a Hugging Face 1,422 count, and the paper’s 638-item table.

## Reading the numbers

A strong BLUEX score means the model can do Portuguese vestibular items that survive the chosen image filter. It does not measure Brazilian law, ENEM, or figure-heavy science. Always state whether images were kept, which year range was used, and whether the metric is paper accuracy or HELM exact match. Read the MR (mathematical reasoning) slice separately; the paper found that subset much harder than the headline mix.
