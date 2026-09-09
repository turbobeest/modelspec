---
id: stereoset
name: "StereoSet"
aliases: []
page_kind: benchmark
category: safety
subcategory: "stereotypical bias"
status: active
summary: "Crowdsourced test of whether a language model prefers stereotypical over anti-stereotypical associations across gender, race, religion and profession, while staying fluent."
measures: "StereoSet gives a model a context sentence about a person or group (a gender, race, religion or profession target) and asks it to choose among three completions: one that reflects a common stereotype about the target, one that reflects an anti-stereotype, and one that is unrelated or meaningless. The intrasentence variant fills in a blank within a single sentence with a stereotype, anti-stereotype or unrelated word; the intersentence variant picks the most plausible of three follow-on sentences. The design deliberately separates two things a language model could get wrong: producing fluent, on-topic language at all, and doing so by leaning on a stereotype rather than a neutral or counter-stereotypical association."
task_format: "Three-way forced choice per item (stereotype / anti-stereotype / unrelated), either filling a blank within a sentence (intrasentence) or selecting a following sentence (intersentence)."
metric:
  name: "Idealized CAT Score (ICAT)"
  direction: higher_is_better
  unit: "points"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: "ICAT combines two component scores from the paper: the Language Modeling Score (LMS), the percentage of instances where the model prefers a meaningful (stereotype or anti-stereotype) association over the meaningless one, ideal value 100; and the Stereotype Score (SS), the percentage of meaningful choices that are stereotypical, ideal value 50 (unbiased). ICAT = LMS * min(SS, 100-SS) / 50, so an ideal, unbiased, fluent model scores 100, a fully biased model scores 0, and a model that answers randomly scores 50."
dataset:
  size: 16995
  size_note: "16,995 triplet instances (context + stereotype/anti-stereotype/unrelated options) over 321 target terms: 40 gender, 120 profession, 149 race, 12 religion. Split roughly evenly between the intrasentence (8,498) and intersentence (8,497) formats. The paper reserves 25% of target terms for a published development set and 75% for a hidden test set, with disjoint terms between the two so a model cannot have memorized dev answers for test terms. The Hugging Face mirror (McGill-NLP/stereoset) publishes only the development split: 2,120 intersentence and 2,110 intrasentence examples (4,229 total, some duplicated across configs); the hidden test set is not publicly distributed."
  url: "https://huggingface.co/datasets/McGill-NLP/stereoset"
  license: "CC BY-SA 4.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "development (published, ~25% of terms) / test (hidden, ~75% of terms)"
  public_test_set: false
publisher:
  org: "MIT (Nadeem, Bethke) and McGill University / Mila (Reddy)"
  authors: ["Moin Nadeem", "Anna Bethke", "Siva Reddy"]
  url: "https://stereoset.mit.edu"
paper:
  title: "StereoSet: Measuring stereotypical bias in pretrained language models"
  arxiv: "2004.09456"
  url: "https://arxiv.org/abs/2004.09456"
  year: 2021
leaderboard_url: "https://stereoset.mit.edu"
repo_url: "https://github.com/moinnadeem/StereoSet"
released: "2020-04"
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
  note: "No source consulted here gives a current leaderboard snapshot with recent frontier-model scores; the original repository notes it is no longer actively maintained and points users to the Bias Bench successor project for updated code, but that project's own results were not reviewed for this page."
contamination:
  risk: medium
  note: "The full 16,995-instance set with labels has circulated publicly (via the paper, GitHub mirrors and Hugging Face) since 2020, though the original design held out 75% of target terms as a nominally hidden test set on a leaderboard. Because most public copies and harness integrations (including inspect_evals) use only the published development split, and that split's labels have been public for years, contamination is plausible for any model trained on general web/GitHub/HF data."
harness:
  lm_eval: ""
  inspect_evals: "stereoset"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["bias", "stereotype", "fairness", "crowdsourced"]
sources:
  - url: "https://arxiv.org/abs/2004.09456"
    title: "StereoSet: Measuring stereotypical bias in pretrained language models"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2004.09456"
    title: "StereoSet (ar5iv HTML)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2021.acl-long.416/"
    title: "StereoSet, ACL Anthology entry"
    accessed: "2026-09-08"
  - url: "https://github.com/moinnadeem/StereoSet"
    title: "StereoSet GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/McGill-NLP/stereoset"
    title: "StereoSet dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/stereoset"
    title: "inspect_evals stereoset task"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-005"
---

## What it measures

StereoSet probes whether a pretrained language model's associations lean on common social stereotypes about gender, race, religion and profession, rather than measuring task competence directly. Each item gives a short English context about a target group or role and three candidate completions: a stereotypical one, an anti-stereotypical one, and an unrelated or meaningless one. The intrasentence format fills a blank inside one sentence; the intersentence format picks the best of three follow-on sentences.

The benchmark is explicitly two-dimensional: it wants to know both whether a model produces fluent, on-topic language (choosing a meaningful option over the meaningless one) and, separately, whether its meaningful choices skew toward stereotype or away from it. A model that always answers "unrelated" to seem neutral is penalized for poor language modeling, not rewarded for fairness.

## How it is scored

Three scores come out of an evaluation run. The Language Modeling Score (LMS) is the percentage of instances where the model prefers a meaningful (stereotype or anti-stereotype) completion over the meaningless one; an ideal model scores 100. The Stereotype Score (SS) is the percentage of meaningful choices that are stereotypical; an unbiased model scores 50, a fully stereotyped model 100, a fully anti-stereotyped model 0. The Idealized CAT Score (ICAT) combines them as `LMS * min(SS, 100-SS) / 50`, so ICAT rewards fluency and penalizes bias in either direction: an ideal, unbiased, fluent model scores 100; a model that is fluent but fully biased scores 0; a model that answers at random scores 50.

The original protocol scores masked-language-model or next-token likelihoods over the candidate completions (no generation). The inspect_evals harness instead frames each item as a multiple-choice question posed to the model, with `task_type` selecting the intrasentence or intersentence variant; this is a different elicitation method than the paper's likelihood scoring and can shift results.

## Dataset and licence

The full StereoSet set has 16,995 triplet instances (context plus stereotype, anti-stereotype and unrelated options) built around 321 target terms: 40 gender terms, 120 professions, 149 race/ethnicity terms and 12 religions. Items split almost evenly between the intrasentence (8,498) and intersentence (8,497) formats. Contexts and candidate completions were written by crowdworkers on Amazon Mechanical Turk (475 workers for intrasentence items, 803 for intersentence) and then filtered by further crowdworker validation rounds.

The authors held out 75% of target terms as a hidden test set for a public leaderboard and released the remaining 25% as a development set, with disjoint terms so dev performance cannot leak test answers. In practice most public mirrors, including the Hugging Face dataset used by common harness integrations, distribute only the development split (2,120 intersentence and 2,110 intrasentence examples); the hidden test set is not broadly available. The dataset is licensed CC BY-SA 4.0.

## Who publishes it

StereoSet was introduced by Moin Nadeem and Anna Bethke (both then at MIT/industry-affiliated work) and Siva Reddy (McGill University / Mila), published at ACL-IJCNLP 2021 after first appearing on arXiv in April 2020. The original leaderboard lived at stereoset.mit.edu. The reference GitHub repository (moinnadeem/StereoSet) notes it is no longer actively maintained and points to the Bias Bench project at McGill NLP as a successor codebase.

## Lineage

StereoSet has no family page in this repository and no confirmed predecessor or successor benchmark reviewed here; it is commonly discussed alongside other crowdsourced bias-in-LM tests such as CrowS-Pairs, but that relationship was not verified from a primary source for this page.

## Saturation and contamination

No source consulted here documents a recent leaderboard snapshot or a specific frontier-model ICAT score, so saturation status is not established. Because the full dataset (or at minimum its development split) has been publicly downloadable since 2020, and general fluency/bias benchmarks of this type are frequently included in training-data mixes, there is a real risk that models have seen these items; this assessment is based on the dataset's public availability rather than a measured leakage study.

## How to run it

The inspect_evals harness ships the task as `inspect_evals/stereoset`, configurable with `task_type` (`intersentence`, the default, or `intrasentence`) and a `shuffle` flag; it poses each item as a multiple-choice question rather than replicating the original likelihood-scoring protocol. The original repository provides its own evaluation scripts that score masked/causal LM probabilities directly over candidate completions and compute LMS, SS and ICAT. No lm-evaluation-harness, HELM or OpenCompass task name for StereoSet was confirmed from a primary source for this page.

## Reading the numbers

A high ICAT score suggests a model both stays on-topic (high LMS) and does not systematically prefer stereotypical completions (SS near 50). But ICAT alone does not say which direction any residual bias runs, and a model can score well by refusing to commit to any social claim, which is not the same as an accurate or fair one. Because different harnesses score the task differently (likelihood-based versus multiple-choice generation) and because the widely used data is limited to the development split, scores are not directly comparable across papers unless the protocol and split are stated. Treat StereoSet scores as one narrow signal about associative bias, not a general safety or fairness certification.
