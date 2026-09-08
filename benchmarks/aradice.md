---
id: aradice
name: AraDiCE
aliases:
- AraDICE
page_kind: benchmark
category: composite
subcategory: Arabic dialect and cultural-knowledge suite (translated BoolQ, OpenBookQA, PIQA,
  TruthfulQA-MC1, Winogrande, ArabicMMLU, plus native cultural QA)
status: active
summary: A suite that re-runs six existing English NLU benchmarks in Egyptian, Levantine and Gulf/MSA Arabic, plus a native cultural-knowledge test across six Arab countries.
measures: >
  AraDiCE (Arabic Dialect and Cultural Evaluation) tests two things existing Arabic benchmarks mostly
  did not separate: whether a model understands specific Arabic dialects, and whether it knows
  region-specific cultural facts. For dialect comprehension, the authors machine-translated six
  established English NLU benchmarks -- BoolQ, OpenBookQA, PIQA, TruthfulQA (MC1), Winogrande, and
  ArabicMMLU -- into Egyptian and Levantine Arabic (and, for some tasks, Gulf-leaning Modern Standard
  Arabic), then had humans post-edit the machine translations for quality. For cultural awareness, they
  built a separate, purpose-written multiple-choice benchmark covering country-specific knowledge for
  Egypt, Jordan, Lebanon, Palestine, Qatar and Syria, which is not a translation of anything but new
  content.
task_format: Mixed by constituent task -- BoolQ is yes/no reading comprehension; PIQA, Winogrande,
  OpenBookQA and TruthfulQA-MC1 are multiple-choice commonsense or truthfulness questions; ArabicMMLU is
  multi-subject multiple-choice exam questions; the cultural-knowledge benchmark is multiple-choice
  questions about country-specific customs, history and facts. Each is presented in a specific Arabic
  dialect (or English, for some tasks' original-language control configs).
metric:
  name: accuracy (acc/acc_norm per constituent task; no single combined AraDiCE score is defined by the
    harness)
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: Random baseline varies by constituent task (roughly 50% for BoolQ's yes/no format,
    roughly 25% for four-option multiple choice, lower for ArabicMMLU's per-subject question sets) and
    is not a single number for the suite as a whole. The lm-evaluation-harness `AraDiCE` group lists all
    28 sub-tasks together but, unlike some other harness groups, does not define an
    `aggregate_metric_list` to roll them up into one score, so running the group yields 28 separate
    per-task numbers.
dataset:
  size: 45000
  size_note: '~45,000 post-edited samples in total across the seven translated task types, per the
    paper''s abstract (an approximate figure, not further broken down there). lm-evaluation-harness
    registers 28 leaf tasks under the `AraDiCE` group: ArabicMMLU in Egyptian and Levantine dialects
    (each further split into dozens of subject-level sub-tasks, e.g. high-school biology, primary-school
    maths, university economics); BoolQ, OpenBookQA, PIQA, TruthfulQA-MC1 and Winogrande each in
    Egyptian, Levantine, MSA and English configs; and 6 country-specific cultural-knowledge tasks
    (Egypt, Jordan, Lebanon, Palestine, Qatar, Syria).'
  url: https://huggingface.co/datasets/QCRI/AraDiCE
  license: CC-BY-NC-SA-4.0
  languages:
  - ar
  - en
  modalities:
  - text
  splits: Varies by constituent task; no single unified split count is reported across all 28 sub-tasks.
  public_test_set: true
publisher:
  org: Qatar Computing Research Institute (QCRI)
  authors:
  - Basel Mousi
  - Nadir Durrani
  - Fatema Ahmad
  - Md. Arid Hasan
  - Maram Hasanain
  - Tameem Kabbani
  - Fahim Dalvi
  - Shammur Absar Chowdhury
  - Firoj Alam
  url: https://huggingface.co/datasets/QCRI/AraDiCE
paper:
  title: 'AraDiCE: Benchmarks for Dialectal and Cultural Capabilities in LLMs'
  arxiv: '2409.11404'
  url: https://arxiv.org/abs/2409.11404
  year: 2024
leaderboard_url: ''
repo_url: https://huggingface.co/datasets/QCRI/AraDiCE
released: '2024-09'
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ''
  note: No dedicated public leaderboard for AraDiCE was found (a Hugging Face Spaces search for the
    name returned nothing). The paper reports that Arabic-specific models (Jais, AceGPT) outperform
    general multilingual models on the dialectal tasks, but a specific top-score figure for the current
    field was not established from the sources reviewed.
contamination:
  risk: medium
  note: The dataset has been public on Hugging Face since September 2024 (about two years before this
    page was written), so broad web-crawl contamination is plausible, but no source consulted
    documents a specific contamination study or the publisher flagging observed leakage.
harness:
  lm_eval: aradice
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- arabic
- dialect
- cultural-knowledge
- composite
- multilingual
sources:
- url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/aradice
  title: lm-evaluation-harness aradice task directory (README, group yaml, all 28 sub-task configs)
  accessed: '2026-09-08'
- url: https://arxiv.org/abs/2409.11404
  title: 'AraDiCE: Benchmarks for Dialectal and Cultural Capabilities in LLMs (arXiv abstract)'
  accessed: '2026-09-08'
- url: https://huggingface.co/datasets/QCRI/AraDiCE
  title: QCRI/AraDiCE dataset card (licence, tags, task categories)
  accessed: '2026-09-08'
- url: https://huggingface.co/api/datasets/QCRI/AraDiCE
  title: QCRI/AraDiCE dataset metadata (Hugging Face API)
  accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: sonnet-5 agent, batch 4, slice D
  reviewed: ''
  reviewed_by: ''
---

## What it measures

AraDiCE (Arabic Dialect and Cultural Evaluation) targets two gaps the authors identify in earlier
Arabic LLM benchmarks: dialect comprehension and cultural awareness. For dialects, the authors took six
established English NLU benchmarks -- [BoolQ](boolq.md), [OpenBookQA](openbookqa.md), [PIQA](piqa.md),
[TruthfulQA](truthfulqa.md) (its MC1 multiple-choice variant), [Winogrande](winogrande.md), and
ArabicMMLU (a dialectal companion to [MMLU](mmlu.md), which has no dedicated page in this repository) --
and machine-translated them into Egyptian and Levantine Arabic, then had humans post-edit the
translations for quality; some tasks also ship Gulf-leaning MSA and English control configs. For
cultural awareness, the authors instead wrote new multiple-choice questions testing country-specific
knowledge across Egypt, Jordan, Lebanon, Palestine, Qatar and Syria -- content that has no English or
MSA original, since it tests knowledge a dialect-region speaker would have rather than a translated
comprehension task.

## How it is scored

Each constituent task keeps its own native scoring: BoolQ is yes/no accuracy, PIQA/Winogrande/
OpenBookQA/TruthfulQA-MC1 are multiple-choice accuracy, ArabicMMLU and the cultural-knowledge tasks are
multiple-choice accuracy over their own subject or country splits. lm-evaluation-harness exposes all 28
of these as separate leaf tasks under one `AraDiCE` group, but that group config does not define an
aggregate metric to roll the 28 numbers into a single AraDiCE score, unlike some other multi-task
harness groups. In practice this means a model's "AraDiCE score" is really a table of per-dialect,
per-task numbers rather than one figure, and any single reported "AraDiCE" number should be checked for
which subset it actually averages.

## Dataset and licence

The paper reports roughly 45,000 post-edited samples in total across the translated tasks. In the
harness, this is organised as 28 tasks: ArabicMMLU in two dialects (each further broken into dozens of
subject-level sub-tasks spanning primary through university level), five NLU benchmarks
(BoolQ, OpenBookQA, PIQA, TruthfulQA-MC1, Winogrande) each in up to four language/dialect configs, and
six country-specific cultural-knowledge tasks. The Hugging Face dataset (`QCRI/AraDiCE`) is released
under a CC BY-NC-SA-4.0 licence, meaning non-commercial use with attribution and share-alike terms;
answers are public.

## Who publishes it

AraDiCE was published by Basel Mousi, Nadir Durrani, Fatema Ahmad, Md. Arid Hasan, Maram Hasanain,
Tameem Kabbani, Fahim Dalvi, Shammur Absar Chowdhury and Firoj Alam, hosted under the Qatar Computing
Research Institute's (QCRI) organisation on Hugging Face and arXiv. The paper was posted to arXiv in
September 2024 and last revised in December 2024. No dedicated public leaderboard for the benchmark was
found.

## Lineage

AraDiCE is built by translating and dialect-adapting six pre-existing benchmarks that each have their
own page in this repository -- [BoolQ](boolq.md), [OpenBookQA](openbookqa.md), [PIQA](piqa.md),
[TruthfulQA](truthfulqa.md), [Winogrande](winogrande.md), and the general-purpose [MMLU](mmlu.md) family
(via its Arabic-specific ArabicMMLU variant, which has no page of its own here) -- and adding a seventh,
wholly new component, the cultural-knowledge benchmark, which has no predecessor. It sits alongside
other dialect- or region-specific Arabic benchmarks tracked in this repository's census queue (for
example `arabic_leaderboard_complete` and `arabic_leaderboard_light`, assigned to a different batch), but
no direct successor to AraDiCE itself was found.

## Saturation and contamination

No dedicated public leaderboard tracks AraDiCE scores, and no source consulted gives a recent,
model-by-model top score across its 28 sub-tasks, so a saturation reading was not established. The paper
itself reports that Arabic-specific fine-tuned models (Jais, AceGPT) outperformed general multilingual
models on the dialectal tasks at publication, while noting that dialect identification, generation and
translation remained challenging across the board. The dataset has been public on Hugging Face since
September 2024, roughly two years before this page was written, so contamination from broad web
pretraining is plausible, though no source consulted documents it being observed.

## How to run it

lm-evaluation-harness implements the full suite under the `AraDiCE` group (task id `aradice` for the
"overall" rollup, though see the scoring note above about the lack of a defined aggregate), with 28
leaf tasks covering every dialect/benchmark combination plus the six cultural tasks. No inspect_evals,
HELM, OpenCompass or BIG-bench integration was confirmed. Because scores are reported per task and per
dialect rather than as one number, comparing two models on "AraDiCE" requires checking that both reports
cover the same subset of the 28 tasks; a report that only ran the cultural-knowledge tasks, for example,
is not comparable to one that only ran the dialectal NLU tasks.

## Reading the numbers

A model that scores well across AraDiCE's dialectal tasks understands Arabic beyond Modern Standard
Arabic, the register most Arabic training data and benchmarks default to, which matters because most
Arabic speakers use a regional dialect day to day. A model that scores well on the cultural-knowledge
component knows region-specific facts that a MSA-only or translation-based evaluation would not surface
at all. Because the two halves test genuinely different things, do not treat a single "AraDiCE" number
as informative without knowing whether it reflects dialect comprehension, cultural knowledge, or an
average across both -- and check which of the six dialects or countries were actually covered before
comparing two models' results.
