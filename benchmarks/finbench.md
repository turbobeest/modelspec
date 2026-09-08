---
id: finbench
name: FinBench
aliases:
  - "FinBench (FinPT)"
page_kind: benchmark
category: domain
subcategory: financial risk classification
status: active
summary: Ten Kaggle-sourced tabular datasets, turned into natural-language customer profiles, that test whether a model flags credit default, fraud or customer-churn risk.
measures: >
  FinBench tests whether a model can predict financial risk — credit-card default, loan default,
  credit-card fraud, or customer churn — from a customer's record. The record starts as a row of
  tabular data (age, income, credit score, loan type, and so on); FinPT, the method the benchmark
  was built to evaluate, first has a language model turn that row into a natural-language "customer
  profile," then fine-tunes a foundation model on the profile text to predict a binary label (risky
  or not). It is a single-turn, text-only, English-language classification task over ten separate
  datasets, each drawn from a different Kaggle source and grouped into three risk categories.
task_format: >
  Binary classification: given a natural-language customer profile (or the underlying tabular row),
  predict whether the customer is financially risky (1) or not (0), separately for each of ten
  datasets across default, fraud and churn.
metric:
  name: F1-score (binary, positive class)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The original paper scores every dataset with F1 rather than accuracy specifically because all
    ten datasets are class-imbalanced (positive/risky rate ranges from 0.67% to 27.8% across
    datasets and splits); the authors state plain accuracy would let a model score well by
    predicting the majority class. No random or human baseline is reported. A single "FinBench"
    number, when one is reported, is an unweighted average of the ten per-dataset F1 scores; the
    paper's own best average (FinPT on Flan-T5-Base, full fine-tuning) is 49.17.
dataset:
  size: 10
  size_note: >
    Ten binary-classification datasets in four sub-categories: credit-card default (cd1, cd2), loan
    default (ld1, ld2, ld3), credit-card fraud (cf1, cf2) and customer churn (cc1, cc2, cc3), all
    collected from Kaggle. About 333,000 labeled instances in total, 9 to 120 features per dataset.
    Each dataset has its own train/validation/test split: test is a fixed 30% of instances, and the
    remaining 70% splits 9:1 into train and validation.
  url: https://huggingface.co/datasets/yuweiyin/FinBench
  license: CC BY-NC 4.0 (dataset, per the Hugging Face dataset card); the accompanying code
    repository is released separately under MIT.
  languages:
    - en
  modalities:
    - text
  splits: per-dataset train/validation/test (70/none-extra/30, with train:validation at 9:1)
  public_test_set: true
publisher:
  org: Department of Computer Science, University of Hong Kong, with DAMO Academy, Alibaba Group
  authors:
    - Yuwei Yin
    - Yazheng Yang
    - Jian Yang
    - Qi Liu
  url: https://github.com/YuweiYin/FinPT
paper:
  title: "FinPT: Financial Risk Prediction with Profile Tuning on Pretrained Foundation Models"
  arxiv: "2308.00065"
  url: https://arxiv.org/abs/2308.00065
  year: 2023
leaderboard_url: ""
repo_url: https://github.com/YuweiYin/FinPT
released: "2023-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    The paper's own baselines leave real headroom: tree-based models (RandomForest, XGBoost,
    CatBoost, LightGBM) average 44-47 F1, small tabular neural networks (DeepFM, STG, VIME, TabNet)
    average 24-40, and the best FinPT configuration (Flan-T5-Base, fully fine-tuned on profile text)
    averages 49.17 — well short of the ceiling. Those runs all fine-tune small-to-mid-size open
    models (up to 13B parameters) on the profile text; the authors separately report that prompting
    LLaMA and Flan-T5 zero/few-shot, without fine-tuning, scores under 10 F1. This repository found
    no independent, current tracker that scores today's frontier chat models against FinBench under
    a stated, comparable protocol, so a present-day saturation read is not established here.
contamination:
  risk: high
  note: >
    All ten source datasets are public Kaggle datasets, several of them long-standing, widely
    reused tabular-ML datasets (for example the Taiwan credit-card default set and the HMEQ home
    equity set) that predate FinBench by years and have been used in countless tutorials and papers.
    Labels are shipped locally with the data rather than held out behind a submission server, and
    the natural-language "profile" text FinPT generates from each row is itself published on
    Hugging Face. A model trained on general web and code data has a real chance of having seen the
    underlying tables, even if not the exact profile-text rendering.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No standard automated harness (lm-evaluation-harness, inspect_evals, HELM, OpenCompass,
    BIG-bench) was confirmed to include FinBench. The authors' own repository (YuweiYin/FinPT)
    is the reference implementation: it builds the customer-profile text via the OpenAI API, then
    fine-tunes a foundation model with a small classification head on top of its hidden states,
    training four times per configuration with different seeds and averaging. This differs
    substantially from a zero-shot or few-shot prompting evaluation of a chat model, so a "FinBench"
    number's method (fine-tuned classifier vs. prompted judgment, and which of the ten datasets were
    averaged) should be checked before comparing two reported scores.
tags:
  - finance
  - tabular-to-text
  - classification
  - imbalanced
  - risk-prediction
sources:
  - url: https://arxiv.org/abs/2308.00065
    title: "FinPT: Financial Risk Prediction with Profile Tuning on Pretrained Foundation Models"
    accessed: "2026-09-08"
  - url: https://github.com/YuweiYin/FinPT
    title: "YuweiYin/FinPT (GitHub repository, README and LICENSE)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/yuweiyin/FinBench
    title: "yuweiyin/FinBench dataset card (Hugging Face)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice P"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

FinBench tests whether a model can predict financial risk — will this customer default on a credit
card or loan, commit credit-card fraud, or churn — from a record of that customer. The starting
point is a row of tabular data: age, income, education, credit score, loan type and similar fields.
FinPT, the method the benchmark was built to evaluate, first prompts a language model to turn that
row into a fluent natural-language "customer profile" paragraph, then fine-tunes a foundation model
on the profile text, with a small classification head, to predict a binary risky/not-risky label.

It is ten separate binary-classification datasets, not one: two on credit-card default, three on
loan default, two on credit-card fraud, and three on customer churn, each sourced from a different
public Kaggle dataset and unified into one loading interface. Every dataset is skewed, with the
positive (risky) class ranging from well under 1% to just over a quarter of instances, so the task
also tests whether a model handles severe class imbalance rather than just predicting the majority.

## How it is scored

Every dataset is scored with F1 on the positive (risky) class, not accuracy — the authors state
plainly that accuracy would let a model do well by defaulting to the majority "not risky" label
given how imbalanced these datasets are. A single "FinBench" number, where one is reported, is an
unweighted average of the ten per-dataset F1 scores. The original paper's own protocol fine-tunes a
foundation model (with all parameters, or just the last decoder block for very large models) on the
LLM-generated profile text, training four times with different random seeds and averaging; a
separate experiment shows that zero-shot or few-shot prompting of the same models, without
fine-tuning, scores under 10 F1 on average. That gap means a "FinBench" score's method — fine-tuned
classifier versus prompted judgment — needs to be known before treating two scores as comparable.

## Dataset and licence

The ten datasets were screened from "hundreds" of Kaggle datasets for quality, popularity and
column meaningfulness, then unified into one structure with roughly 333,000 labeled instances in
total. Each dataset ships its own train, validation and test split: a fixed 30% test set, with the
remaining 70% split 9:1 into train and validation. Alongside the raw tabular rows, the dataset
provides an instruction template and the LLM-generated profile text for each instance, plus
per-table statistics for algorithms that need them. The Hugging Face dataset card lists the licence
as CC BY-NC 4.0; the code repository that builds and loads it is released separately under MIT.

## Who publishes it

FinBench was introduced alongside the FinPT method by Yuwei Yin, Yazheng Yang and Qi Liu at the
University of Hong Kong's Department of Computer Science, with Jian Yang at DAMO Academy, Alibaba
Group, in the paper "FinPT: Financial Risk Prediction with Profile Tuning on Pretrained Foundation
Models," posted to arXiv in July 2023. The paper is marked as a University of Hong Kong preprint;
no separate conference or journal acceptance was found in the sources read. The authors maintain
the reference code at github.com/YuweiYin/FinPT and the dataset on Hugging Face.

## Lineage

No predecessor or successor benchmark, and no variant or subset page, was established for FinBench
in this repository's own materials; this appears to be the only page for this benchmark family here.
The name is easy to confuse with other finance-benchmark efforts that use similar wording — notably
FinBen, a much larger 36-dataset, 24-task holistic financial benchmark, and FinanceBench, a
150-question open-book financial-filings QA set — but those are distinct projects with their own
papers and datasets, not variants of this one. Readers encountering a "finbench" score should
confirm which of these it actually refers to before comparing it across sources.

## Saturation and contamination

The paper's own baselines leave clear room to improve: tree-based models average 44-47 F1, small
tabular neural networks average 24-40, and the strongest FinPT configuration (Flan-T5-Base, fully
fine-tuned) averages 49.17 — under half of the maximum. Those numbers all come from fine-tuning
open, small-to-mid-size models on the ten datasets; this repository found no current, independent
tracker scoring today's frontier chat models against FinBench under one stated protocol, so a
present-day saturation call is not established here. Contamination risk is high: all ten source
tables are public, long-circulating Kaggle datasets — several, like the Taiwan credit-card-default
set, are classic tabular-ML datasets that predate this benchmark by years — and labels sit locally
with the data rather than behind a held-out server, so a model trained on general web data has a
real chance of having seen the underlying tables even without seeing FinPT's specific profile text.

## How to run it

The authors' own repository (YuweiYin/FinPT) is the reference implementation: it constructs
customer-profile text via the OpenAI API from the raw tabular rows, then fine-tunes a foundation
model — the paper tests BERT, FinBERT, GPT-2, T5, Flan-T5 and LLaMA at various sizes — with a small
feed-forward classifier on its hidden states, training four times per configuration with different
seeds and reporting the average. No standard harness (lm-evaluation-harness, inspect_evals, HELM,
OpenCompass, BIG-bench) was confirmed to carry FinBench as a task. Because the original protocol is
fine-tuning, not prompting, any zero-shot or few-shot FinBench number for a chat model reflects a
different evaluation method than the one the benchmark's own paper validates, and it is not
established here which method any given reported score used.

## Reading the numbers

A high FinBench score means a model, after seeing the profile text, separates risky from
non-risky customers well on ten specific, imbalanced Kaggle datasets — it says nothing about
financial reasoning in general, or about how the model would do on a bank's actual, differently
distributed customer base. Because F1 rather than accuracy is the metric, small changes in a score
can reflect the fixed class imbalance rather than genuine skill differences between models. Given
how much the original paper's fine-tuned baselines vary by dataset (F1 on the rarest-fraud dataset,
cf1, tops out near 22 even for the best model), a single averaged number can hide a model that does
well on the easier datasets and badly on the hardest one; check the per-dataset breakdown, and the
evaluation method behind the number, before treating a FinBench score as a settled comparison.
