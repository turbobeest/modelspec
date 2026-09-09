---
id: opinions_qa
name: OpinionQA
aliases:
  - OpinionsQA
  - opinions_qa
  - Opinion QA
page_kind: benchmark
category: safety
subcategory: alignment of model opinion distributions with US survey groups
status: active
summary: >
  1,498 Pew American Trends Panel multiple-choice opinion questions used to compare
  a model's answer distribution with 60 US demographic groups, not to score accuracy.
measures: >
  OpinionQA asks a model the same multiple-choice public-opinion questions Pew
  Research asked US adults, covering topics such as guns, abortion, privacy, and
  science. There is no gold answer. The object is the distribution over choices,
  compared with the weighted distribution of all respondents or of a named group
  (for example Democrats, age 65+, or high income). A second mode prepends group
  context to test whether the model can be steered toward that group's views.
task_format: >
  Multiple-choice question with ordinal options plus an optional Refused choice.
  Representativeness uses the question alone. Steerability prepends steer-qa,
  steer-bio, or steer-portray context. Scoring uses next-token log probabilities
  over choice letters, not generated prose.
metric:
  name: representativeness / alignment (1 minus normalized 1-Wasserstein distance)
  direction: higher_is_better
  unit: "0-1 alignment"
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper's alignment score is 1 minus 1-Wasserstein distance between model and
    human opinion distributions, scaled by N-1 choices, averaged over questions.
    Refusal is scored separately. The authors treat the metric as a probe, not a
    target to maximise. HELM's opinions_qa run spec registers no metric_specs.
dataset:
  size: 1498
  size_note: >
    The paper and the tatsu-lab/opinions_qa README both say 1,498 multiple-choice
    questions from 15 Pew American Trends Panel waves, mapped onto 23 coarse and
    40 fine topics, with human answers for 60 US demographic groups. HELM's
    OpinionsQAScenario docstring says 1,484 questions. HELM also ships a
    disagreement_500 file used when max-eval-instances is 500. This page uses
    1,498 from the dataset authors and records HELM's 1,484 as a disagreement.
  url: https://github.com/tatsu-lab/opinions_qa
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "survey waves rather than train/test; HELM treats Pew CSVs as test and uses steer-qa items as train only when context is steer-qa"
  public_test_set: true
publisher:
  org: "Stanford University and Columbia University"
  authors:
    - Shibani Santurkar
    - Esin Durmus
    - Faisal Ladhak
    - Cinoo Lee
    - Percy Liang
    - Tatsunori Hashimoto
  url: https://github.com/tatsu-lab/opinions_qa
paper:
  title: "Whose Opinions Do Language Models Reflect?"
  arxiv: "2303.17548"
  url: https://arxiv.org/abs/2303.17548
  year: 2023
leaderboard_url: ""
repo_url: https://github.com/tatsu-lab/opinions_qa
released: "2023-03"
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
    Alignment is not a skill ceiling. The 2023 paper found every tested model less
    representative of the US populace than the least representative human demographic
    group they computed. No later multi-model tracker was confirmed here.
contamination:
  risk: medium
  note: >
    Pew ATP questions and toplines are public, and the packaged 1,498 prompts have
    been on GitHub and CodaLab since 2023. There is no hidden test key. The risk is
    that models see the survey wording, not that they can memorise a single correct
    letter.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: opinions_qa
  opencompass: ""
  bigbench: ""
  other: >
    HELM scenario name is opinions_qa (OpinionsQAScenario). The run-spec function
    is also opinions_qa; run names look like
    opinions_qa:survey={survey_type},num_logprobs={n},context={default|steer-qa|steer-bio|steer-portray}.
    Official README still calls helm-run with
    run_specs_opinions_qa_openai_default.conf and related steer configs.
    Pew CSVs are pulled from a CodaLab bundle listed in the scenario file.
    No lm-eval, OpenCompass, inspect_evals, or BIG-bench task was confirmed.
tags:
  - opinion-alignment
  - pew
  - multiple-choice
  - demographics
  - steerability
sources:
  - url: https://arxiv.org/abs/2303.17548
    title: "Whose Opinions Do Language Models Reflect? (arXiv:2303.17548)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2303.17548
    title: "OpinionQA paper HTML (1,498 questions, 60 groups, Wasserstein metric)"
    accessed: "2026-09-08"
  - url: https://github.com/tatsu-lab/opinions_qa
    title: "tatsu-lab/opinions_qa repository (dataset README, 1,498 questions)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/tatsu-lab/opinions_qa/master/README.md
    title: "opinions_qa README (CodaLab data, HELM run commands)"
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/opinions_qa_scenario.py
    title: "HELM OpinionsQAScenario (name opinions_qa; docstring 1,484 questions)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py
    title: "HELM get_opinions_qa_spec run-spec function"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-018 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-018"
---

## What it measures

OpinionQA feeds a model a Pew Research multiple-choice opinion question and records the probability it assigns to each listed view. Questions come from 15 American Trends Panel waves and span US political and social topics. The model is not asked for a fact. The comparison is between its choice distribution and the survey's human distribution, overall or within a demographic group. Steering prompts try to make the model answer as a named group.

## How it is scored

The paper maps ordinal choices to integers, drops Refused, and computes 1-Wasserstein distance between model and human distributions. Alignment is 1 minus that distance divided by N-1, averaged over questions. Representativeness uses no extra context. Steerability tries three context styles and keeps the best. Consistency asks whether the best-matching group stays the same across topics. HELM implements the scenario and logprobs adapter but sets `metric_specs` to an empty list, so a HELM run does not by itself reproduce the paper's alignment number.

## Dataset and licence

The authors and README state 1,498 questions; HELM's scenario docstring states 1,484. Human microdata and group aggregates come from Pew ATP. The GitHub repository has no LICENSE file. Pew's own terms for ATP files were not opened here, so `dataset.license` is left empty.

## Who publishes it

Shibani Santurkar, Esin Durmus, Cinoo Lee, Percy Liang, and Tatsunori Hashimoto (Stanford) with Faisal Ladhak (Columbia) posted arXiv:2303.17548 on 30 March 2023. Code and pointers to CodaLab data live at tatsu-lab/opinions_qa. HELM maintains the `opinions_qa` scenario independently.

## Lineage

The work is a survey-based opinion probe, not a QA accuracy set. It is not part of [helm_safety](helm_safety.md), which averages other safety datasets. No predecessor or successor page in this repository shares this item pool.

## Saturation and contamination

There is no accuracy ceiling to saturate. The 2023 result was broad misalignment with US groups, including after steering. Pew wording is public and old enough to appear in pretraining, but that does not yield a single memorisable key.

## How to run it

Use tatsu-lab/opinions_qa with HELM, or `helm-run` with an `opinions_qa` run spec. You must name `survey_type` and `context` (`default`, `steer-qa`, `steer-bio`, `steer-portray`). Data files come from the CodaLab bundle referenced in the scenario. Compare numbers only when survey subset, context mode, and metric (Wasserstein alignment versus raw logprobs) match.

## Reading the numbers

A high representativeness score means the model's mix of answers looks like that group's mix, not that the answers are "right." Matching one group can move the model away from another. Steering gains in the paper were small and did not close group gaps. RLHF models in the paper often collapsed onto a single modal option, which inflates agreement with a group's plurality while erasing that group's internal spread. Read OpinionQA next to the prompt context, not as a standalone accuracy.
