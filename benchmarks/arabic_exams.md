---
id: arabic_exams
name: Arabic EXAMS
aliases:
- aexams
- AEXAMS
- EXAMS (Arabic)
page_kind: benchmark
category: knowledge
subcategory: Arabic high-school exam multiple-choice QA (5 subjects)
status: active
summary: Multiple-choice Arabic high-school exam questions across five subjects, run under two different harness names (arabic_exams, aexams) over the same 562-item set.
measures: Arabic EXAMS gives a model a high-school-level exam question written in Arabic, with four
  labelled answer options, and asks it to pick the correct one. The questions are drawn from real
  school examinations rather than written for the benchmark, and cover five subjects -- Islamic
  Studies, Biology, Physics, Science, and Social (Studies) -- so a score on this benchmark reflects a
  mix of Arabic reading comprehension and subject-matter recall rather than any single skill. It is the
  Arabic-language slice of EXAMS, a multilingual high-school-exam question answering dataset (Hardalov
  et al., 2020), later re-packaged for LLM evaluation by the AceGPT project.
task_format: 'Multiple-choice exam question with four labelled options (A-D), single correct answer,
  in Arabic; scored either by log-likelihood ranking over the options or by exact match on a generated
  letter, depending on harness.'
metric:
  name: accuracy (lm-evaluation-harness also reports acc_norm; HELM's main metric is exact_match)
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: 25.0
  human_baseline: null
  baseline_note: Random baseline assumes four roughly balanced options. lm-evaluation-harness scores
    each of the five subject tasks with loglikelihood-based multiple-choice accuracy (acc and
    acc_norm, size-weighted mean across subjects), while HELM's ArabicEXAMSScenario instead asks the
    model to generate an answer and scores exact_match; the two protocols are not guaranteed to agree
    for the same model.
dataset:
  size: 562
  size_note: 562 questions total, confirmed independently from three sources -- the original EXAMS-QA
    repository's own per-language table (Arabic, 562), the lm-evaluation-harness mirror Hennara/aexams
    (25 dev + 537 test, unzipped and counted directly), and the HELM mirror OALL/Arabic_EXAMS (25
    validation + 537 test, per its Hugging Face dataset card). Split by subject in the test set 35
    Biology, 73 Islamic Studies, 42 Physics, 115 Science, 272 Social; 5 per subject in dev/validation.
  url: https://huggingface.co/datasets/OALL/Arabic_EXAMS
  license: ''
  languages:
  - ar
  modalities:
  - text
  splits: 'lm-evaluation-harness (Hennara/aexams): test (537) / dev (25). HELM (OALL/Arabic_EXAMS):
    test (537) / validation (25). Same 562 items under different split names.'
  public_test_set: true
publisher:
  org: ''
  authors:
  - Momchil Hardalov
  - Todor Mihaylov
  - Dimitrina Zlatkova
  - Yoan Dinkov
  - Ivan Koychev
  - Preslav Nakov
  url: https://github.com/mhardalov/exams-qa
paper:
  title: 'EXAMS: A Multi-subject High School Examinations Dataset for Cross-lingual and Multilingual
    Question Answering'
  arxiv: ''
  url: https://aclanthology.org/2020.emnlp-main.438/
  year: 2020
leaderboard_url: https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard
repo_url: https://github.com/FreedomIntelligence/AceGPT/tree/main/eval/benchmark_eval/benchmarks/EXAMS_Arabic
released: '2023'
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
  note: No dated leaderboard reading for this specific task was found in the sources reviewed; the
    Open Arabic LLM Leaderboard (OALL) space that hosts scores for it was still active as of its last
    Hugging Face update (October 2025), but a specific top score for arabic_exams/aexams was not
    confirmed from a source opened for this page.
contamination:
  risk: medium
  note: The underlying EXAMS question set has been publicly downloadable since 2020, and both Hugging
    Face mirrors used by the two harnesses have been public since February 2024, so a model trained on
    a broad web or Arabic-web crawl since then has plausibly seen these exact questions and answers.
harness:
  lm_eval: aexams
  inspect_evals: ''
  helm: arabic_exams
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- arabic
- knowledge
- multiple-choice
- multilingual-subset
- exam-qa
sources:
- url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/aexams
  title: lm-evaluation-harness aexams task directory (README, group and per-subject yaml configs)
  accessed: '2026-09-08'
- url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/arabic_exams_scenario.py
  title: HELM ArabicEXAMSScenario source
  accessed: '2026-09-08'
- url: https://huggingface.co/datasets/Hennara/aexams
  title: Hennara/aexams dataset (used by lm-evaluation-harness's aexams task)
  accessed: '2026-09-08'
- url: https://huggingface.co/datasets/OALL/Arabic_EXAMS
  title: OALL/Arabic_EXAMS dataset card and split counts (used by HELM's arabic_exams scenario)
  accessed: '2026-09-08'
- url: https://github.com/mhardalov/exams-qa
  title: mhardalov/exams-qa, the original EXAMS dataset repository (README with per-language item counts;
    CC-BY-SA-4.0 licence on the repository itself)
  accessed: '2026-09-08'
- url: https://aclanthology.org/2020.emnlp-main.438/
  title: 'EXAMS: A Multi-subject High School Examinations Dataset for Cross-lingual and Multilingual
    Question Answering (ACL Anthology)'
  accessed: '2026-09-08'
- url: https://arxiv.org/abs/2309.12053
  title: 'AceGPT, Localizing Large Language Models in Arabic (curated this Arabic subset for LLM eval)'
  accessed: '2026-09-08'
- url: https://github.com/FreedomIntelligence/AceGPT/tree/main/eval/benchmark_eval/benchmarks/EXAMS_Arabic
  title: AceGPT eval benchmark EXAMS_Arabic directory (immediate source both HF mirrors cite)
  accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: sonnet-5 agent, batch 4, slice D
  reviewed: ''
  reviewed_by: ''
---

## What it measures

Arabic EXAMS tests whether a model can answer real high-school exam questions written in Arabic. Each
item is a multiple-choice question with four labelled options, drawn from actual school examinations
across five subjects: Islamic Studies, Biology, Physics, Science, and Social (Studies). Because the
questions were written for human students rather than generated for the benchmark, answering them
correctly requires genuine Arabic reading comprehension combined with subject-matter knowledge, rather
than any single narrow skill.

This is the Arabic-language slice of EXAMS, a multilingual and cross-lingual high-school-exam
question-answering dataset introduced by Hardalov et al. (2020). The Arabic subset was later selected,
split by subject, and re-packaged for LLM evaluation as part of the AceGPT project's Arabic evaluation
suite, and it is this AceGPT-derived packaging -- not the full multilingual release -- that both harnesses
in this repository's scope actually load.

## What both harness names load

This id absorbs two harness entries that turned out to be the same benchmark under different names.
`aexams` in lm-evaluation-harness loads the dataset `Hennara/aexams` (five per-subject tasks:
`aexams_Biology`, `aexams_IslamicStudies`, `aexams_Physics`, `aexams_Science`, `aexams_Social`, grouped
under `aexams`); its own loading script names its homepage as the AceGPT project's `EXAMS_Arabic`
evaluation directory. `arabic_exams` in HELM loads `OALL/Arabic_EXAMS`, a mirror the scenario's own
docstring describes as "the Open Arabic LLM Leaderboard (OALL) version mirror of the Arabic subset of
EXAMS, which is in turn based on the AceGPT version." Both therefore trace to the same AceGPT-curated
source. This page confirmed the two are identical by unzipping `Hennara/aexams`'s underlying data file
and counting items directly: 537 test-split questions (35 Biology, 73 Islamic Studies, 42 Physics, 115
Science, 272 Social) plus 25 dev-split questions (5 per subject) -- 562 total -- which match
`OALL/Arabic_EXAMS`'s reported 537 test plus 25 validation exactly, and match the original EXAMS-QA
repository's own per-language table, which lists 562 total Arabic items. `aexams` is recorded as an
alias on this page rather than getting a separate page.

## How it is scored

lm-evaluation-harness treats each subject as a loglikelihood-based multiple-choice task and reports
accuracy and length-normalised accuracy (acc_norm), aggregated as a size-weighted mean across the five
subjects under the `aexams` group. HELM instead prompts the model to generate an answer and scores it
by exact string match (`exact_match`) against the reference letter or text. These are different
protocols -- ranking four fixed continuations by likelihood versus scoring a free-form generation -- so a
model's `aexams` score and its `arabic_exams` score are not guaranteed to match even though they
evaluate the same 562 items. Random guessing among four options scores 25%.

## Dataset and licence

562 questions in total: 537 in the harnesses' test split and 25 in a small dev/validation split, spread
across five subjects (Biology, Islamic Studies, Physics, Science, Social). Neither Hugging Face mirror
used by the two harnesses (`Hennara/aexams`, `OALL/Arabic_EXAMS`) states its own licence on its dataset
card. The original EXAMS-QA repository that the questions ultimately come from is released under
CC BY-SA 4.0, which this subset plausibly inherits, but that has not been confirmed to apply to either
re-hosted mirror specifically. Both mirrors are text-only and Arabic-only; answers are public in both.

## Who publishes it

The underlying question set comes from EXAMS, published by Momchil Hardalov, Todor Mihaylov, Dimitrina
Zlatkova, Yoan Dinkov, Ivan Koychev and Preslav Nakov at EMNLP 2020. The specific Arabic, five-subject
slice used by both harnesses in this repository was selected and split for LLM evaluation by the AceGPT
project (Huang et al., "AceGPT, Localizing Large Language Models in Arabic," 2023), whose GitHub
evaluation directory both Hugging Face mirrors cite as their source. `Hennara/aexams` and
`OALL/Arabic_EXAMS` are two independent Hugging Face re-hosts of that same AceGPT-curated data, created
ten days apart in February 2024; scores are tracked today on the Open Arabic LLM Leaderboard (OALL)
space, which was still receiving updates as of October 2025.

## Lineage

Arabic EXAMS is one language slice of the larger multilingual EXAMS corpus (2020), which spans high
school exam questions in more languages -- sources reviewed here disagree on the exact count, one giving
16 languages and another giving 26, a discrepancy not resolved from the sources opened for this page.
Neither the full multilingual EXAMS benchmark nor any other language slice of it has a page in this
repository yet. Within this repository, `aexams` and `arabic_exams` are recorded as the same benchmark
under two harness names, per this page's front-matter `aliases`; the fold is also logged in
`benchmarks/_census/DATA-QUALITY.md`.

## Saturation and contamination

No dated top-score reading specific to `aexams` or `arabic_exams` was found in the sources reviewed for
this page; establishing one would mean pulling per-model results from the OALL leaderboard space, which
was not done here. The underlying question-and-answer text has been publicly downloadable since the
original EXAMS release in 2020, and both re-hosted mirrors used by today's harnesses have been public
since February 2024, so contamination from broad or Arabic-focused web pretraining is plausible for
models trained since then; no source consulted describes a specific mitigation for this benchmark.

## How to run it

lm-evaluation-harness registers it as the `aexams` group (five tasks: `aexams_Biology`,
`aexams_IslamicStudies`, `aexams_Physics`, `aexams_Science`, `aexams_Social`), loading
`Hennara/aexams` with 5-shot loglikelihood scoring by default (`fewshot_split: dev`). HELM registers it
as the `arabic_exams` scenario, loading `OALL/Arabic_EXAMS` and remapping its `validation` split to
HELM's train role for in-context examples. Because the two harnesses use different prompt formats,
few-shot sources and scoring rules (ranking vs. generation), do not treat an `aexams` score and an
`arabic_exams` score for the same model as directly comparable without checking which harness produced
each one.

## Reading the numbers

A high score here says a model can read Arabic well enough to parse a real exam question and recall or
infer the right fact among five school subjects; it says little beyond that, since the item count is
small (562) and concentrated in a few subjects, with Social Studies alone making up roughly half the
test split. Because this benchmark exists under two names with two different scoring protocols, always
check which harness produced a given number before comparing it across model reports, and treat a bare
"Arabic EXAMS" score with no harness named as unverified until you confirm the source.
