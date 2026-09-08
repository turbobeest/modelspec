---
id: thai_exam
name: ThaiExam
aliases:
  - Thai Exam
  - thai-exam
page_kind: benchmark
category: knowledge
subcategory: Thai national and professional multiple-choice exams
status: active
summary: >
  A suite of Thai multiple-choice exams (ONET, IC, TGAT, TPAT-1, A-Level) used
  to test Thai knowledge in Typhoon and later as a HELM scenario.
measures: >
  ThaiExam asks a model to answer real Thai exam items by choosing among four
  or five lettered options. The suite mixes grade-12 academic tests (ONET,
  TGAT, TPAT-1, A-Level) with the Stock Exchange of Thailand's Investment
  Consultant licence exam (IC). Language is mostly Thai; HELM's metadata marks
  some slices as Thai and English. The Typhoon report built the set to measure
  Thai knowledge after continual pretraining, not as a general multilingual MMLU.
task_format: >
  Multiple-choice question with options A-E (some items omit E). HELM's
  `ThaiExamScenario` builds a joint multiple-choice prompt with up to five
  in-context train items and scores exact match on the chosen letter.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Chance is not one number: ONET, TPAT-1 and many A-Level items have five
    options; IC and TGAT have four. Typhoon paper Table 3 lists average-human
    accuracies for three exams only (ONET 0.318, TGAT 0.472, TPAT-1 0.406) and
    leaves IC and A-Level blank, so there is no single suite-wide human figure.
    HELM's main metric is exact_match on the test split.
dataset:
  size: 590
  size_note: >
    Hugging Face datasets-server on typhoon-ai/thai_exam (current files): ONET
    5 train + 162 test, IC 5+95, TGAT 5+65, TPAT-1 5+116, A-Level 5+127, totalling
    25 train + 565 test = 590. The v1.0 card's exam totals (167, 100, 70, 121,
    132) match those sums. The Typhoon paper and the HELM scenario docstring
    instead quote 170, 95, 90, 116 and 175 (646). HELM pins revision
    `d78aef04ea3cc5095545e6951cb39e17c64e26a1`, which the card calls v1.0.
  url: https://huggingface.co/datasets/typhoon-ai/thai_exam
  license: Apache-2.0
  languages:
    - th
  modalities:
    - text
  splits: "five exam configs, each with 5-shot train and a test split"
  public_test_set: true
publisher:
  org: "Typhoon / SCB 10X (typhoon-ai)"
  authors:
    - Kunat Pipatanakul
    - Phatrasek Jirabovonvisut
    - Potsawee Manakul
    - Sittipong Sripaisarnmongkol
    - Ruangsak Patomwong
    - Pathomporn Chokchainant
    - Kasima Tharnpipitchai
  url: https://huggingface.co/datasets/typhoon-ai/thai_exam
paper:
  title: "Typhoon: Thai Large Language Models"
  arxiv: "2312.13951"
  url: https://arxiv.org/abs/2312.13951
  year: 2023
leaderboard_url: ""
repo_url: https://github.com/stanford-crfm/helm
released: "2023-12"
last_updated: "2024-07"
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
    The Typhoon paper reports Typhoon-7B averages (ONET 0.379, IC 0.393, TGAT
    0.700, TPAT-1 0.414, A-Level 0.324, mean 0.442) on its own tables. Those
    2023 figures are not a current HELM top. The dataset card's HELM Thai
    leaderboard URL did not resolve when opened.
contamination:
  risk: high
  note: >
    Items come from published Thai exams and a public Hub dump with answers.
    The Typhoon paper even names the 2021 ONET example as a source. Any model
    trained on Thai web text may have seen the questions.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: thai_exam
  opencompass: ""
  bigbench: ""
  other: >
    HELM run spec `thai_exam` in classic_run_specs.py. Runnable name
    `thai_exam:exam={onet|ic|tgat|tpat1|a_level},method=...` with groups
    `thai_exam` and `thai_exam_{exam}`. Scenario class `ThaiExamScenario`.
    Default method is multiple-choice joint, max_train_instances=5. No
    lm-evaluation-harness task of this name was found.
tags:
  - knowledge
  - multiple-choice
  - thai
  - exams
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/thai_exam_scenario.py
    title: HELM ThaiExamScenario (scenario name thai_exam)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py
    title: HELM get_thai_exam_spec run spec
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/typhoon-ai/thai_exam
    title: typhoon-ai/thai_exam dataset card (Apache-2.0, v1.0)
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/typhoon-ai/thai_exam
    title: typhoon-ai/thai_exam Hugging Face API
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=typhoon-ai/thai_exam
    title: thai_exam split counts on datasets-server
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2312.13951
    title: "Typhoon: Thai Large Language Models (arXiv abs)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2312.13951
    title: Typhoon paper HTML (ThaiExam section and table)
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-022 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-022"
---

## What it measures

ThaiExam is a bundle of Thai multiple-choice exams. The model reads a question, usually in Thai, and picks A-D or A-E. ONET is the grade-12 national test. TGAT is a general aptitude test. TPAT-1 is the medical-school professional aptitude paper. A-Level covers school subjects applied to daily life. IC is the SET investment-consultant licence exam.

The Typhoon authors built the set to see whether a Thai continual-pretrained model actually knew Thai school and professional content. It is not M3Exam, which the same paper uses as a separate Thai ONET-from-another-source comparison.

## How it is scored

HELM scores exact match on the test split after a joint multiple-choice prompt. Each exam config has five labelled train rows for few-shot. The scenario fills missing fifth options when a subject only has four choices. The Typhoon paper reports per-exam accuracy, a simple average, and average-human marks for ONET (0.318), TGAT (0.472) and TPAT-1 (0.406) only.

Do not treat the 2023 Typhoon-7B table as a HELM run. HELM's adapter and the authors' original script need not agree.

## Dataset and licence

The Hub dataset `typhoon-ai/thai_exam` (also resolved from the older `scb10x/thai_exam` id) is Apache-2.0. Current split counts sum to 590 rows: 25 few-shot train items and 565 test items. The v1.0 card's per-exam totals match that sum. The paper and the HELM docstring still quote the larger 2023 counts (170 ONET, 90 TGAT, 175 A-Level, and so on). HELM downloads tarball revision `d78aef04...`, which the card labels v1.0. Answers are public.

The card also disagrees with the paper on ONET subject count (four versus five, English dropped in v1.0). Prefer the Hub files when stating size.

## Who publishes it

The Typhoon team at SCB 10X: Kunat Pipatanakul and co-authors. The technical report is arXiv 2312.13951 (21 December 2023). HELM later wrapped the Hub dump as scenario `thai_exam`. Hugging Face last listed a 8 July 2024 revision (`cccc569b…`). The card's link to a CRFM Thai HELM leaderboard did not resolve when opened.

## Lineage

ThaiExam is not [Arabic EXAMS](arabic_exams.md) and not [Hungarian Exam](hungarian_exam.md). Those are other national-exam pages. The Typhoon paper compares it with M3Exam's Thai ONET slice; M3Exam has no page here. SeaExam on Hugging Face is a different SeaLLMs product.

## Saturation and contamination

No current HELM top was sourced. Public exam items with answers, including a named 2021 ONET example, make contamination risk high. A strong Thai score today may mean the model saw the paper, not that it sat the exam.

## How to run it

HELM run spec `thai_exam` with `exam` in `{onet, ic, tgat, tpat1, a_level}`. The scenario name is `thai_exam`; per-exam groups are `thai_exam_onet` and so on. Use the pinned Hub revision if you want HELM's v1.0 dump. No OpenCompass or lm-evaluation-harness task of this name was found.

## Reading the numbers

A ThaiExam score is Thai exam literacy, not general reasoning. IC is finance licensing; TPAT-1 is medical ethics and reasoning. Average across the five exams hides those differences. Check whether the paper used the 2023 counts or the 590-row v1.0 dump, and whether English ONET items were included.
