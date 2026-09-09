---
id: interactive_qa_mmlu
name: "InteractiveQA MMLU"
aliases:
  - "interactive_qa_mmlu"
  - "HELM InteractiveQA MMLU"
page_kind: benchmark
category: knowledge
subcategory: "HELM five-subject MMLU slice with a CodaLab InteractiveQA test subset"
status: unknown
summary: "HELM scenario that scores a small InteractiveQA subset of five MMLU subjects as four-choice exact match, not the full 57-subject test."
measures: >
  InteractiveQA MMLU is still four-choice academic questions from Hendrycks
  et al.'s MMLU, but HELM does not score the full 14k-item test. The scenario
  class InteractiveQAMMLUScenario subclasses MMLUScenario and keeps only
  college_chemistry, global_facts, miscellaneous, nutrition and
  us_foreign_policy. Test CSVs are unpacked from a CodaLab bundle labeled
  InteractiveQA, not from the ordinary MMLU test folder. Dev CSVs still come
  from the standard MMLU download and are used as the HELM train split.
task_format: >
  Four-option multiple choice. HELM Classic run spec interactive_qa_mmlu uses
  adapter multiple_choice_joint, instructions "The following are multiple
  choice questions (with answers) about {subject}", input noun Question,
  output noun Answer, and exact-match metrics. get_multiple_choice_adapter_spec
  defaults to max_train_instances=5 and max_tokens=1. The run name is
  interactive_qa_mmlu:subject={subject}; groups include mmlu.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    Four options, so uniform chance is 25%. Hendrycks et al. estimate expert-
    level accuracy on the full 57-subject MMLU test at about 89.8%; that
    figure does not apply to this five-subject InteractiveQA slice. No human
    figure was read for the CodaLab subset.
dataset:
  size: null
  size_note: >
    Item count for the CodaLab InteractiveQA test unpack was not established.
    The scenario comment says "a small subset of the original test set."
    The live nlp.stanford.edu InteractiveQA MMLU page did not yield a row
    count or a max_eval_instances figure in this review. Dev/train still uses
    the standard MMLU per-subject dev CSV.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/interactive_qa_mmlu_scenario.py"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "HELM train from MMLU dev CSV; HELM test from CodaLab InteractiveQA unpack"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM)"
  authors: []
  url: "https://crfm.stanford.edu/helm/classic/"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://nlp.stanford.edu/helm/interactive_qa_mmlu/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/interactive_qa_mmlu_scenario.py"
released: "2022-11"
last_updated: ""
lineage:
  family: ""
  predecessor: mmlu
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No dated top exact-match for this five-subject InteractiveQA slice was
    read. Full-MMLU saturation is tracked on the [mmlu](mmlu.md) page, not here.
    HELM entered maintenance mode on 1 June 2026 per the HELM README.
contamination:
  risk: high
  note: >
    The questions are public MMLU items (MIT-licensed, on GitHub and Hugging
    Face since 2020). Using a smaller CodaLab slice does not hold out answers
    from pretraining. This is from publicity and age, not a measured leakage
    study of the CodaLab files.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "interactive_qa_mmlu"
  opencompass: ""
  bigbench: ""
  other: >
    helm-run --run-entries interactive_qa_mmlu:subject=<one of five>,model=<id>.
    Valid subjects are hardcoded. Do not pass an ordinary MMLU subject.
tags:
  - helm
  - mmlu
  - multiple-choice
  - knowledge
  - interactive-qa
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/interactive_qa_mmlu_scenario.py"
    title: "InteractiveQAMMLUScenario (five subjects, CodaLab test unpack)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM Classic get_interactive_qa_mmlu_spec (joint MC, exact match, groups=mmlu)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "get_multiple_choice_adapter_spec defaults (5-shot, max_tokens=1)"
    accessed: "2026-09-08"
  - url: "https://nlp.stanford.edu/helm/interactive_qa_mmlu/?runs=1&runSpec=interactive_qa_mmlu%3Asubject%3Dmiscellaneous%2Cmodel%3Dopenai_text-babbage-001"
    title: "Historic InteractiveQA MMLU run page (JS UI; no instance count recovered here)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/hendrycks/test/master/LICENSE"
    title: "hendrycks/test MIT License (MMLU questions, copyright 2020 Dan Hendrycks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode 1 June 2026; Classic leaderboard)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness; MMLU data remain MIT)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (arXiv:2211.09110)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2009.03300"
    title: "MMLU paper (arXiv:2009.03300)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-050 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-050"
---

## What it measures

InteractiveQA MMLU still asks four-choice academic questions, but only on five MMLU subjects: college chemistry, global facts, miscellaneous, nutrition and US foreign policy. HELM loads ordinary MMLU dev items as in-context examples and a CodaLab "InteractiveQA" unpack as the test set. The scenario comment calls that unpack a small subset of the original test. This is not the 57-subject [MMLU](mmlu.md) mean, and it is not the per-subject pages [mmlu_college_chemistry](mmlu_college_chemistry.md), [mmlu_global_facts](mmlu_global_facts.md), [mmlu_miscellaneous](mmlu_miscellaneous.md), [mmlu_nutrition](mmlu_nutrition.md) or [mmlu_us_foreign_policy](mmlu_us_foreign_policy.md) when those score the full Hendrycks test CSV.

The name InteractiveQA is the HELM suite label. The Python scenario still grades static multiple choice. No multi-turn human dialogue is implemented in the file opened for this page.

## How it is scored

HELM Classic uses joint multiple-choice prompting and exact match. Default few-shot is five dev items. Chance is 25% on four options. A `helm-run --max-eval-instances` cap is a runner setting, not a property of the CSVs. Do not compare a truncated InteractiveQA cell to a full-subject MMLU number.

## Dataset and licence

MMLU is MIT. HELM's harness is Apache-2.0. This page records MIT for the questions. How many test rows sit in the CodaLab tarball was not counted here. Answers in that tarball are still the public MMLU keys.

## Who publishes it

Stanford CRFM ships the scenario in HELM Classic (`classic_run_specs.py`). The HELM paper is Liang et al., arXiv:2211.09110 (November 2022). A historic results UI remains at nlp.stanford.edu/helm/interactive_qa_mmlu/. The HELM README states the project entered maintenance mode on 1 June 2026.

## Lineage

Predecessor: [MMLU](mmlu.md). This is a HELM protocol and a five-subject slice, not a new item set. It is not MMLU-Pro, MMLU-Redux or a language transfer. Do not treat `interactive_qa_mmlu` as a harness spelling of `mmlu`.

## Saturation and contamination

Full MMLU is saturated at the frontier; this slice has no confirmed top score. The questions have been public since 2020. A smaller test file does not make them private.

## How to run it

```
helm-run --run-entries interactive_qa_mmlu:subject=nutrition,model=<id> --suite <suite>
```

Subject must be one of the five names above. Passing `anatomy` or another MMLU subject raises an assertion in the scenario. Quote subject, shot count and `max_eval_instances` when comparing.

## Reading the numbers

A high exact-match here means the model picked the labeled letter on HELM's InteractiveQA rows for that subject. It does not stand in for 57-subject MMLU, MMLU-Pro or a human-in-the-loop study. Short runner caps bounce. Read it beside the matching `mmlu_*` subject page, which uses the full Hendrycks test CSV, and treat disagreement as a protocol difference rather than a model ranking.
