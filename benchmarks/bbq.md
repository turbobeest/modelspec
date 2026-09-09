---
id: bbq
name: BBQ (Bias Benchmark for QA)
aliases:
  - Bias Benchmark for Question Answering
page_kind: benchmark
category: safety
subcategory: social bias in question answering
status: active
summary: Multiple-choice QA benchmark testing whether models default to social stereotypes under ambiguous context and can override them once context disambiguates the answer.
measures: "BBQ tests whether a language model falls back on social stereotypes when it lacks the information to answer a question, and whether it can set that stereotype aside once the missing fact is supplied. Each item gives the model a short context and a question about two people or groups mentioned in it, with three answer choices: one social group, the other, or \"unknown\". The nine bias categories are age, disability status, gender identity, nationality, physical appearance, race or ethnicity, religion, socio-economic status, and sexual orientation, plus two intersectional categories combining race with gender and race with socio-economic status. Every item comes in an ambiguous version, which gives no information that would let a careful reader pick a group over \"unknown\", and a disambiguated version that adds one sentence resolving the question in favour of one of the two groups."
task_format: "Three-way multiple-choice QA (two named social groups plus \"unknown\"), zero- or few-shot, US English"
metric:
  name: accuracy (plus a separate bias score)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The paper also computes a signed bias score alongside accuracy, separately for the ambiguous and disambiguated subsets; a bias score of 0 means errors are not skewed toward the stereotyped answer."
dataset:
  size: 58492
  size_note: "58,492 examples from hand-written templates, at least 25 per category, across 9 bias categories plus 2 intersectional subsets"
  url: https://github.com/nyu-mll/BBQ
  license: CC BY 4.0
  languages:
    - en
  modalities:
    - text
  splits: ""
  public_test_set: true
publisher:
  org: New York University, Machine Learning for Language group
  authors:
    - Alicia Parrish
    - Angelica Chen
    - Nikita Nangia
    - Vishakh Padmakumar
    - Jason Phang
    - Jana Thompson
    - Phu Mon Htut
    - Samuel R. Bowman
  url: https://github.com/nyu-mll/BBQ
paper:
  title: "BBQ: A Hand-Built Bias Benchmark for Question Answering"
  arxiv: "2110.08193"
  url: https://arxiv.org/abs/2110.08193
  year: 2022
leaderboard_url: ""
repo_url: https://github.com/nyu-mll/BBQ
released: "2022"
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
  note: "No maintained leaderboard tracks a current ceiling. Accuracy alone is not the headline number in any case, since the bias score is designed to stay informative even as accuracy approaches 100%."
contamination:
  risk: unknown
  note: "Fully public with no held-out answers since 2021, which makes memorisation plausible for a small hand-built set, but no publisher statement or independent study confirming that was found during this research."
harness:
  lm_eval: bbq
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - bias
  - social-bias
  - safety
  - question-answering
sources:
  - url: https://arxiv.org/abs/2110.08193
    title: "BBQ: A Hand-Built Bias Benchmark for Question Answering"
    accessed: "2026-09-07"
  - url: https://github.com/nyu-mll/BBQ
    title: "nyu-mll/BBQ (GitHub repository)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BBQ tests whether a language model falls back on social stereotypes when it lacks the information to answer a question, and whether it can set that stereotype aside once the missing fact is supplied. Each item gives the model a short context and a question about two people or groups mentioned in it, with three answer choices: one named group, the other, or "unknown". The nine bias categories are age, disability status, gender identity, nationality, physical appearance, race or ethnicity, religion, socio-economic status, and sexual orientation, plus two intersectional categories combining race with gender and race with socio-economic status.

Every item comes in two versions. The ambiguous version gives no information that would let a careful reader pick a group over "unknown". The disambiguated version adds one sentence that resolves the question in favour of one of the two groups. Comparing a model's answers across both versions shows whether it guesses a stereotype when it should say "unknown", and whether it still gets the disambiguated version right once both stereotype-consistent and stereotype-inconsistent framings are tested.

## How it is scored

BBQ is a three-way multiple-choice task, graded on accuracy. The paper additionally computes a bias score: a signed statistic measuring how often the model's errors on ambiguous items land on the stereotyped answer rather than spreading evenly across the two named groups, computed again for the disambiguated set conditioned on getting the answer wrong. A bias score of zero means errors are not skewed toward the stereotype; positive and negative values point toward or against it. Runs typically go through the questions zero-shot or few-shot, one item at a time. Reporters vary in prompt template and in whether they average bias scores across all categories or report intersectional and non-intersectional subsets separately, which makes cross-source comparison imprecise.

## Dataset and licence

The dataset holds 58,492 examples drawn from hand-written templates, at least 25 per category, each instantiated across name and group substitutions and both context types. It is released on GitHub under a CC BY 4.0 licence, with all questions, contexts and gold answers public and no held-out test split. Content is US-English and grounded in stereotypes the authors sourced from published social-science literature for each bias category.

## Who publishes it

BBQ comes from a team at New York University's Machine Learning for Language group: Alicia Parrish, Angelica Chen, Nikita Nangia, Vishakh Padmakumar, Jason Phang, Jana Thompson, Phu Mon Htut and Samuel R. Bowman. The paper appeared in Findings of the Association for Computational Linguistics: ACL 2022. NYU's nyu-mll GitHub organisation maintains the repository and data files; there is no separately maintained leaderboard, so scores mostly come from individual model or lab evaluations rather than one canonical source.

## Lineage

BBQ does not sit inside a family in this repository's taxonomy; it is a standalone social-bias probe with no predecessor or successor tracked here. It has inspired several language- and region-specific adaptations documented in later papers, including CBBQ for Chinese, PakBBQ for Pakistani-English contexts and GG-BBQ for German, none of which are yet pages in this repository.

## Saturation and contamination

No publisher or independent leaderboard tracks a current ceiling for BBQ, so saturation status is not established here. Accuracy alone would not settle the question in any case, since the bias score is designed to stay informative even as accuracy approaches 100%. Contamination risk is likewise not established: the dataset has been fully public since 2021 with no held-out answers, which makes memorisation plausible for a small, hand-built set, but no publisher statement or community study confirming that specific finding turned up during this research.

## How to run it

EleutherAI's lm-evaluation-harness ships a `bbq` task family, including per-category variants, scored from the log-likelihood the model assigns each answer choice. The reference implementation is the data loaders and `analysis_scripts` in the nyu-mll/BBQ repository, which also documents how to reproduce the paper's bias-score computation. Numbers are hard to compare across reporters when they do not state whether they scored plain accuracy, the bias score, or an average of bias scores taken unevenly across the 11 categories.

## Reading the numbers

A high plain accuracy score on BBQ does not by itself mean a model is unbiased: the number that matters most is the bias score on the ambiguous subset, which isolates whether errors skew toward stereotypes rather than scattering randomly. A low bias score alongside high disambiguated-context accuracy is the strongest signal of a model that says "unknown" when it should and updates on new information rather than guessing. Because BBQ is US-English and grounded in US social categories, a good score says little about bias behaviour in other languages or cultural contexts. Check which categories and which context type, ambiguous or disambiguated, a reported number covers before comparing it across models.
