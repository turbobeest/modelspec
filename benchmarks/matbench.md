---
id: matbench
name: "Matbench"
aliases: []
page_kind: benchmark
category: domain
subcategory: "materials property prediction from composition and/or crystal structure"
status: active
summary: >-
  A 13-task materials-property-prediction suite built for classical ML; OpenCompass's LLM harness
  adapts its 4 composition-only tasks into text prompts graded by regex or an LLM judge.
measures: >
  Matbench asks a model to predict a physical property of an inorganic bulk material -- for example
  a formation energy, a band gap, an elastic modulus, whether a composition is a metal, whether a
  composition forms a glass, or the yield strength of a steel -- given either the material's
  chemical composition alone or its full crystal structure. It was built for classical and
  graph-based machine learning models (random forests, descriptor-based pipelines, crystal graph
  neural networks), not for language models: 9 of its 13 tasks require a crystal structure as
  input, which has no natural plain-text encoding. OpenCompass's LLM evaluation harness sidesteps
  this by running only the 4 tasks that take a composition string alone -- matbench_steels,
  matbench_expt_gap, matbench_expt_is_metal and matbench_glass -- as free-text prompts, which is
  why an LLM's "Matbench" score, where one exists, covers less than a third of the full suite.
task_format: >
  Originally a structured regression or classification problem over composition/structure features.
  OpenCompass's LLM adaptation turns each of the 4 composition-only tasks into a free-text prompt
  asking for a predicted number (matbench_steels, matbench_expt_gap) or a yes/no classification
  (matbench_expt_is_metal, matbench_glass), extracted from the model's response either by regex or
  by a separate LLM-judge call.
metric:
  name: >-
    task-specific: mean absolute error (MAE) for the regression tasks (matbench_steels,
    matbench_expt_gap); accuracy, precision, recall and F1 for the classification tasks
    (matbench_expt_is_metal, matbench_glass). The full 13-task suite also reports RMSE, MAPE,
    max error, balanced accuracy and ROC-AUC depending on task.
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Metrics are not uniform across the 4 LLM-relevant tasks, so no single direction or unit applies:
    MAE is lower-is-better while accuracy/F1 are higher-is-better. The maintainers publish each
    regression task's mean absolute deviation (MAD) as a naive "always predict the training mean"
    baseline -- 229.4 MPa for matbench_steels, 1.143 eV for matbench_expt_gap -- and each
    classification task's positive-class fraction as a base rate: 49.8% for matbench_expt_is_metal,
    71.0% for matbench_glass. No baseline specific to LLM text-prompt evaluation was found.
dataset:
  size: null
  size_note: >
    The full suite spans 13 tasks ranging from 312 to 132,752 samples each (summed from the
    maintainers' own matbench_v0.1_dataset_metadata.json): 9 take a crystal structure as input
    (636-132,752 samples) and 4 take only a composition string (matbench_steels 312,
    matbench_expt_gap 4,604, matbench_expt_is_metal 4,921, matbench_glass 5,680). Those 4
    composition-only tasks are the ones OpenCompass's LLM harness runs. Every task is organised as
    5-fold cross-validation (fold_0 through fold_4, confirmed from the maintainers'
    matbench_v0.1_validation.json); OpenCompass's loader reads only fold_0's test split per task,
    not the 5-fold mean the official leaderboard reports.
  url: "https://github.com/materialsproject/matbench"
  license: "MIT"
  languages: ["en"]
  modalities: ["text", "tabular"]
  splits: "5-fold cross-validation per task (fold_0-fold_4); OpenCompass's LLM harness uses only fold_0's test split"
  public_test_set: true
publisher:
  org: "Hacking Materials Research Group (Lawrence Berkeley National Laboratory); part of the Materials Project"
  authors: ["Alexander Dunn", "Qi Wang", "Alex Ganose", "Daniel Dopp", "Anubhav Jain"]
  url: "https://matbench.materialsproject.org"
paper:
  title: "Benchmarking Materials Property Prediction Methods: The Matbench Test Set and Automatminer Reference Algorithm"
  arxiv: "2005.00707"
  url: "https://arxiv.org/abs/2005.00707"
  year: 2020
leaderboard_url: "https://matbench.materialsproject.org"
repo_url: "https://github.com/materialsproject/matbench"
released: "2020-05"
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
    The official matbench.materialsproject.org leaderboard tracks classical and graph-based ML
    algorithms (Automatminer, CGCNN, MODNet, coNGN and similar), not language models, so it says
    nothing about LLM saturation. No source opened for this page reported current LLM scores on
    OpenCompass's 4-task text adaptation, so a saturation call for LLMs specifically is not
    established here.
contamination:
  risk: medium
  note: >
    Matbench's compositions, structures, property values and fold assignments have all been public
    since 2020, several years before the LLM benchmark era, and much of the underlying property data
    overlaps with the broader Materials Project database that circulates widely in the materials
    science literature. That makes exact memorisation of specific numeric answers plausible for very
    common compounds, though this is closer to general domain-knowledge overlap than to the kind of
    targeted benchmark leakage seen in exam-style datasets. No contamination study specific to LLM
    use of Matbench was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >-
    matbench (4 tasks: matbench_steels, matbench_expt_gap, matbench_expt_is_metal, matbench_glass;
    both a regex/rule-based eval_cfg and an LLM-judge eval_cfg exist for the same tasks)
  bigbench: ""
  other: >
    The reference implementation for the original suite is the pip-installable `matbench` Python
    package (materialsproject/matbench), which runs the full 5-fold protocol against classical ML
    pipelines via the MatbenchBenchmark class. No LLM-oriented reference harness was found outside
    OpenCompass's adaptation.
tags:
  - domain
  - materials-science
  - regression
  - classification
  - tabular
  - cross-validation
sources:
  - url: "https://arxiv.org/abs/2005.00707"
    title: "Benchmarking Materials Property Prediction Methods: The Matbench Test Set and Automatminer Reference Algorithm"
    accessed: "2026-09-08"
  - url: "https://github.com/materialsproject/matbench"
    title: "materialsproject/matbench repository (README, LICENSE)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/materialsproject/matbench/main/matbench/matbench_v0.1_dataset_metadata.json"
    title: "matbench_v0.1_dataset_metadata.json (per-task size, input type, MAD, target, unit)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/materialsproject/matbench/main/matbench/matbench_v0.1_validation.json"
    title: "matbench_v0.1_validation.json (5-fold split assignments per task)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/materialsproject/matbench/main/matbench/constants.py"
    title: "matbench/constants.py (package version 0.6, regression/classification metric lists)"
    accessed: "2026-09-08"
  - url: "https://matbench.materialsproject.org"
    title: "Matbench leaderboard and documentation site"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/matbench/matbench_llm_judge_gen_0e9276.py"
    title: "OpenCompass matbench_llm_judge_gen_0e9276.py (4-task LLM adaptation, judge templates)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/matbench/matbench.py"
    title: "OpenCompass MatbenchDataset loader and regex-based evaluators"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Matbench asks a model to predict a physical property of an inorganic bulk material -- a formation
energy, a band gap, an elastic modulus, whether a composition is a metal, whether it forms a glass,
or the yield strength of a steel -- from either its chemical composition alone or its full crystal
structure. It was built for classical and graph-based machine learning models, not language models:
9 of its 13 tasks require a crystal structure as input, which has no natural plain-text encoding.
OpenCompass's LLM evaluation harness works around this by running only the 4 tasks that take a
composition string alone (matbench_steels, matbench_expt_gap, matbench_expt_is_metal,
matbench_glass) as free-text prompts, so an LLM's "Matbench" score, where one exists at all, covers
under a third of the full suite and none of its structure-dependent tasks.

## How it is scored

Metrics are task-specific and not uniform: the two composition-only regression tasks
(matbench_steels, predicting yield strength in MPa; matbench_expt_gap, predicting an experimental
band gap in eV) are scored by mean absolute error, while the two composition-only classification
tasks (matbench_expt_is_metal, matbench_glass) are scored by accuracy, precision, recall and F1. The
maintainers publish each regression task's mean absolute deviation as a naive baseline -- 229.4 MPa
for matbench_steels, 1.143 eV for matbench_expt_gap -- and each classification task's positive-class
rate as a base rate (49.8% and 71.0% respectively). OpenCompass ships two different ways to grade an
LLM's free-text answer for the same 4 tasks: a regex-based extractor, or a second LLM call acting as
judge, so two "Matbench" numbers are not comparable unless both used the same grading path.

## Dataset and licence

The full suite is 13 tasks ranging from 312 to 132,752 samples, drawn from 10 density-functional-theory
and experimental sources. Every task is organised as 5-fold cross-validation (fold_0 through
fold_4), confirmed from the maintainers' own validation-split file, rather than a single train/test
partition. OpenCompass's LLM harness reads only fold_0's test split for each of its 4 tasks, not the
5-fold mean the official leaderboard reports -- a material difference in protocol, not just in task
count. The reference repository (materialsproject/matbench) is MIT licensed; composition, structure
and target values are public for all tasks.

## Who publishes it

Matbench comes from Alexander Dunn, Qi Wang, Alex Ganose, Daniel Dopp and Anubhav Jain at the
Hacking Materials Research Group, part of the Materials Project at Lawrence Berkeley National
Laboratory, published in npj Computational Materials in 2020. The group maintains the `matbench`
Python package, the reference `Automatminer` algorithm, and the public leaderboard at
matbench.materialsproject.org, which tracks classical and graph-based ML submissions, not LLMs.

## Lineage

Matbench has no predecessor or successor tracked in this repository; it predates the LLM benchmark
era by several years and was not originally designed as one. Its relevance to LLM evaluation is
entirely downstream, through OpenCompass's own text-prompt adaptation of 4 of its 13 tasks -- a
repurposing, not an official variant, and not maintained by Matbench's own authors. No other
harness's adaptation of Matbench for language models was found in sources opened for this page.

## Saturation and contamination

The official leaderboard ranks classical and graph-neural-network algorithms against each other, not
language models, so it gives no signal about LLM saturation. No source opened for this page reported
current LLM scores on OpenCompass's 4-task adaptation, so an LLM-specific saturation call is not
established here. Contamination risk sits at medium: composition, structure and property data have
been public since 2020 and much of it overlaps with the broader Materials Project database that
circulates widely in materials-science literature and code, making memorisation of common compounds'
properties plausible, though this looks more like general domain-knowledge overlap than benchmark-
specific leakage. No contamination study targeting LLM use of Matbench was found.

## How to run it

The original 13-task, 5-fold protocol runs through the pip-installable `matbench` package
(`pip install matbench`), using the `MatbenchBenchmark` class to iterate folds and record
predictions per task. For LLMs, OpenCompass registers the 4 composition-only tasks under the
`matbench` config directory, with both a regex-based evaluator (`MatbenchEvaluator_regression`,
`MatbenchEvaluator_classification`) and an LLM-judge evaluator (`GenericLLMEvaluator` with separate
correctness and numeric-extraction prompt templates) available for the same 4 tasks. A score is only
comparable to another if both used the same task subset, the same fold, and the same grading path.

## Reading the numbers

Because OpenCompass's LLM adaptation covers only 4 of 13 tasks, all composition-only, a "Matbench"
figure attached to a language model says nothing about the 9 structure-dependent tasks that make up
most of the original suite. Because it reads a single fold rather than the 5-fold mean the official
classical-ML leaderboard reports, it is not directly comparable to a matbench.materialsproject.org
ranking even on the same 4 tasks. Treat any LLM "Matbench" score as a narrow, non-standard read on a
benchmark built for a different kind of model, and check which grading path (regex or LLM judge)
produced it before comparing two such scores.
