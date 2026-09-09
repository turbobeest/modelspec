---
id: hellaswag
name: "HellaSwag"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "commonsense natural language inference"
status: saturated
summary: "Four-way multiple-choice test of commonsense sentence continuation, built by adversarial filtering to defeat models of its era."
measures: "HellaSwag tests commonsense inference: given a short description of an everyday situation, a model must pick which of four possible continuations is the most plausible next step. Contexts are drawn from ActivityNet video captions and WikiHow how-to articles, covering ordinary physical activities such as cooking, repairs or sports. The task looks trivial to a person but was built specifically to be hard for the language models of its time, isolating whether a model has a working sense of how everyday situations unfold rather than just fluent language generation."
task_format: "Four-way multiple choice; given a short context, the model selects the most plausible of four candidate continuations."
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: 95.6
  baseline_note: "Random guessing scores 25% on this four-way multiple-choice task; the paper measured human accuracy at 95.6% overall (95.6% in-domain, 95.7% zero-shot)."
dataset:
  size: 59950
  size_note: "39,905 train (14,740 ActivityNet-sourced, 25,165 WikiHow-sourced) + 10,042 validation + 10,003 test; each split further divides into in-domain and zero-shot halves. The paper's own methodology narrative describes a larger pre-filtering candidate pool of roughly 70,000 problems (about 25,000 ActivityNet, 45,000 WikiHow) before adversarial filtering and deduplication produced the released splits."
  url: "https://github.com/rowanz/hellaswag/tree/master/data"
  license: "MIT"
  languages: ["en"]
  modalities: ["text"]
  splits: "train (39,905) / validation (10,042) / test (10,003)"
  public_test_set: false
publisher:
  org: "Paul G. Allen School of Computer Science & Engineering, University of Washington"
  authors: ["Rowan Zellers", "Ari Holtzman", "Yonatan Bisk", "Ali Farhadi", "Yejin Choi"]
  url: "https://rowanzellers.com/hellaswag/"
paper:
  title: "HellaSwag: Can a Machine Really Finish Your Sentence?"
  arxiv: "1905.07830"
  url: "https://arxiv.org/abs/1905.07830"
  year: 2019
leaderboard_url: "https://rowanzellers.com/hellaswag/"
repo_url: "https://github.com/rowanz/hellaswag"
released: "2019-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: "The dataset's own authors closed their public leaderboard to new submissions as of November 2024, and reported human accuracy is 95.6% overall -- both signal the benchmark's practical retirement for separating current frontier models, though no source consulted here gives a specific recent top score."
contamination:
  risk: high
  note: "Most published scores use the validation split, whose labels have been public since 2019. Even where true test-set labels are withheld, the underlying ActivityNet captions and WikiHow articles are separately available across the open web, so memorization is plausible either way. No dedicated HellaSwag contamination study was found in the sources consulted; this assessment rests on the dataset's public/held-out mechanics rather than a measured leakage rate."
harness:
  lm_eval: "hellaswag"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["commonsense", "multiple-choice", "sentence-completion", "adversarial-filtering", "nli"]
sources:
  - url: "https://arxiv.org/abs/1905.07830"
    title: "HellaSwag: Can a Machine Really Finish Your Sentence?"
    accessed: "2026-09-07"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.07830"
    title: "HellaSwag (full text, ar5iv)"
    accessed: "2026-09-07"
  - url: "https://aclanthology.org/P19-1472/"
    title: "HellaSwag - ACL Anthology"
    accessed: "2026-09-07"
  - url: "https://github.com/rowanz/hellaswag"
    title: "rowanz/hellaswag repository"
    accessed: "2026-09-07"
  - url: "https://rowanzellers.com/hellaswag/"
    title: "HellaSwag leaderboard"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/Rowan/hellaswag"
    title: "Rowan/hellaswag dataset card"
    accessed: "2026-09-07"
  - url: "https://www.tensorflow.org/datasets/catalog/hellaswag"
    title: "hellaswag | TensorFlow Datasets catalog"
    accessed: "2026-09-07"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness"
    title: "EleutherAI lm-evaluation-harness (hellaswag task)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HellaSwag tests commonsense inference: given a short description of an everyday situation, a model must pick which of four possible continuations is the most plausible next step. Contexts come from two sources -- ActivityNet video captions and WikiHow how-to articles -- covering ordinary physical activities like cooking, repairs or sports. The task looks trivial to a person but was built specifically to be hard for the language models of its time, isolating whether a model has a working sense of how everyday situations unfold rather than just fluent language generation.

## How it is scored

Each item is four-way multiple choice: one human-written correct ending and three machine-generated wrong ones, so random guessing scores 25%. The authors reported human accuracy at 95.6% on the released test set (95.6% in-domain, 95.7% zero-shot), against well under 50% for the strongest models available in 2019. Most published results use the validation split, since the official test-set labels are held out and were originally scored only through the authors' own leaderboard.

## Dataset and licence

The released dataset totals 59,950 examples: 39,905 for training (14,740 from ActivityNet, 25,165 from WikiHow), 10,042 for validation and 10,003 for test, with each split further divided into "in-domain" (activity categories seen in training) and "zero-shot" (held-out categories) halves. The paper's own methodology narrative separately describes a larger candidate pool of roughly 70,000 problems (about 25,000 ActivityNet-derived, 45,000 WikiHow-derived) before adversarial filtering and deduplication produced the released splits. The GitHub repository states an MIT licence; validation-set labels are public, test-set labels are withheld.

## Who publishes it

HellaSwag comes from Rowan Zellers, Ari Holtzman, Yonatan Bisk, Ali Farhadi and Yejin Choi at the Paul G. Allen School of Computer Science & Engineering, University of Washington, published as "HellaSwag: Can a Machine Really Finish Your Sentence?" at ACL 2019. The authors continue to host the reference repository and a submission leaderboard at rowanzellers.com/hellaswag.

## Lineage

HellaSwag is the direct successor to SWAG (Situations With Adversarial Generations), an earlier commonsense-inference dataset by an overlapping author group that language models caught up to faster than the authors expected. HellaSwag reran the same adversarial-filtering idea with a stronger generator and discriminator to restore a difficulty gap. SWAG does not have a page in this repository, and no successor or variant id is tracked here either.

## Saturation and contamination

The dataset's own authors closed their public leaderboard to new submissions as of November 2024, and their reported human accuracy of 95.6% leaves little headroom above where current frontier models are commonly described as sitting; both point to a benchmark that no longer separates leading models. No source consulted here gives a specific recent top score. Contamination is plausible from two directions: most published scores use the validation split, whose labels have been public since 2019, and even where true test labels are withheld, the underlying ActivityNet captions and WikiHow articles are separately available across the open web, so a model could learn to favor plausible continuations without ever seeing HellaSwag's own label file. No dedicated HellaSwag contamination study was found in the sources consulted, so this assessment rests on the dataset's public/held-out mechanics rather than a measured leakage rate.

## How to run it

lm-evaluation-harness implements it as the `hellaswag` task, scoring by length-normalized log-likelihood over the four candidate endings rather than free generation, which is the most common way it is reported. The authors' own repository at github.com/rowanz/hellaswag provides the adversarial-filtering code and the reference data files. Because scoring can be done either by likelihood ranking or by prompting a model to output a choice letter, and because reporters mix validation-set and leaderboard test-set numbers, comparing HellaSwag scores across papers is only safe when the scoring method and split match.

## Reading the numbers

A HellaSwag score close to the mid-90s tells you a model handles ordinary, physically grounded commonsense about as well as this dataset can distinguish, which by 2026 describes most current models, so it mainly separates weak or very small models from everything else. A low score is still a real signal of trouble with grounded situational reasoning. Because most reporters score the validation split rather than the held-out test set, and because likelihood-based and generation-based scoring can disagree, treat small differences between reported HellaSwag numbers as noise rather than a genuine capability gap.
