---
id: coqa
name: "CoQA (Conversational Question Answering Challenge)"
aliases:
  - "CoQA"
page_kind: benchmark
category: reasoning
subcategory: "conversational reading comprehension"
status: saturated
summary: "Free-form question answering over a passage, where the questions form a real conversation and each answer needs the prior turns to be understood."
measures: >
  CoQA tests whether a model can answer a series of interconnected questions about a passage, the
  way a person would in conversation, rather than one isolated question at a time. Passages are
  drawn from seven domains (children's stories, literature, middle and high school exams, news,
  Wikipedia, science and Reddit); each was given to two paired crowd-workers who chatted about it
  in questions and answers. Because later questions depend on earlier turns, CoQA requires
  coreference resolution (understanding what "it" or "she" refers to from prior turns) and
  pragmatic reasoning that single-turn reading-comprehension datasets do not exercise.
task_format: >
  Free-form text answers to a sequence of conversational questions grounded in a single passage;
  each answer also comes with an evidence span highlighted in the passage. Systems are evaluated
  on an in-domain test set (domains seen in training) and an out-of-domain test set (domains held
  out entirely), scored against the official evaluation script.
metric:
  name: F1
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 88.8
  baseline_note: >
    F1 is computed as word overlap against the gold answer, following the SQuAD-style evaluation
    the authors adapted. The paper reports human performance at 88.8% overall (89.4% in-domain,
    87.4% out-of-domain) and its best contemporary system at 65.4%, a 23.4-point gap the authors
    used to argue the task was far from solved at release. There is no meaningful random baseline
    for a free-form span/answer-generation task.
dataset:
  size: null
  size_note: >
    The official project page and the paper both state "127,000+" questions from "8,000+"
    conversations -- rounded figures given by the source itself, not an exact count found in the
    sources read for this page. The current Hugging Face mirror (stanfordnlp/coqa) contains only
    the public train (7,199 passage/conversation pairs) and validation (500 pairs) splits, 7,699
    total, close to but under the "8,000+" figure; there is no test split in the mirror, since the
    in-domain and out-of-domain held-out test sets are not publicly released.
  url: "https://huggingface.co/datasets/stanfordnlp/coqa"
  license: >
    Mixed by source domain, as published on the CoQA website: CC BY-SA 4.0 (literature and
    Wikipedia passages), the MSR-LA licence (children's stories, from MCTest), RACE's own licence
    (middle/high school exam passages), and the Apache License (news passages, from the CNN/Daily
    Mail dataset). Two of the seven source domains (the paper's science and Reddit portions) are
    not released publicly at all. The Hugging Face dataset card tags the licence simply as "other."
  languages:
    - en
  modalities:
    - text
  splits: "train (7,199 passages) / validation (500 passages); in-domain and out-of-domain held-out test sets are not publicly released"
  public_test_set: false
publisher:
  org: "Stanford University"
  authors:
    - "Siva Reddy"
    - "Danqi Chen"
    - "Christopher D. Manning"
  url: "https://stanfordnlp.github.io/coqa/"
paper:
  title: "CoQA: A Conversational Question Answering Challenge"
  arxiv: "1808.07042"
  url: "https://arxiv.org/abs/1808.07042"
  year: 2019
leaderboard_url: "https://stanfordnlp.github.io/coqa/"
repo_url: "https://stanfordnlp.github.io/coqa/"
released: "2018-08"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 90.7
  as_of: "2020-04"
  note: >
    The official leaderboard, read directly for this page, is topped by two ensembles that both
    reach 90.7% overall F1: "RoBERTa + AT + KD" (Zhuiyi Technology, submitted September 2019) and
    "TR-MT" (WeChatAI, submitted April 2020) -- both above the paper's own 88.8% human-performance
    figure. No leaderboard entry newer than April 2020 was visible in the portion of the table read
    for this page, suggesting the leaderboard stopped attracting frontier submissions once
    transformer ensembles passed the human baseline rather than being formally closed like some
    contemporaries' leaderboards.
contamination:
  risk: medium
  note: >
    The train and validation passages and answers have been public since 2018. The in-domain and
    out-of-domain test sets are not publicly released, which is why lm-evaluation-harness's `coqa`
    task scores the validation split rather than a hidden test set and ships a built-in
    decontamination check comparing each story-and-question pair against a reference corpus. Even
    so, several of CoQA's source domains (Wikipedia, CNN/Daily Mail news, RACE exam passages) are
    separately public in their original form, so a model could plausibly learn to answer
    CoQA-style questions about that underlying text without ever seeing CoQA's own held-out labels.
harness:
  lm_eval: "coqa (scores the validation split via the EleutherAI/coqa mirror; output type generate_until; metrics exact-match and F1; should_decontaminate is set in the task config)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - reading-comprehension
  - conversational
  - question-answering
  - coreference
sources:
  - url: "https://arxiv.org/abs/1808.07042"
    title: "CoQA: A Conversational Question Answering Challenge"
    accessed: "2026-09-08"
  - url: "https://stanfordnlp.github.io/coqa/"
    title: "CoQA project homepage (data, evaluation script, licence and leaderboard)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/stanfordnlp/coqa"
    title: "stanfordnlp/coqa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/coqa/default.yaml"
    title: "lm-evaluation-harness coqa task config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice E"
---

## What it measures

CoQA tests whether a model can answer a series of interconnected questions about a passage the way a person would in conversation, rather than one isolated question at a time. Passages are drawn from seven domains -- children's stories, literature, middle and high school exams, news, Wikipedia, science and Reddit -- and each was given to two paired crowd-workers who chatted about it in a natural sequence of questions and answers. Because later questions depend on earlier turns (a question might use "it" or "she" to refer to something established several turns earlier), CoQA requires coreference resolution and pragmatic reasoning that single-turn reading-comprehension datasets do not exercise.

## How it is scored

Answers are free-form text, evaluated by word-overlap F1 against the gold answer, following the SQuAD-style evaluation the authors adapted; each gold answer also comes with a highlighted evidence span in the passage. The paper reports human performance at 88.8% overall (89.4% in-domain, 87.4% out-of-domain) against 65.4% for its strongest system at release, a 23.4-point gap used to argue the task was far from solved at the time. There is no meaningful random baseline for a free-form generation task. Systems are scored separately on an in-domain test set (domains also seen in training) and an out-of-domain test set (entirely unseen domains), and the two do not always move together.

## Dataset and licence

The official project page and the paper both describe the dataset as "127,000+" questions from "8,000+" conversations, rounded figures from the source itself rather than an exact count. The public Hugging Face mirror contains only the train (7,199 passages) and validation (500 passages) splits, 7,699 conversations in total; the in-domain and out-of-domain held-out test sets are not publicly released. Licensing is mixed by source domain rather than one blanket licence: literature and Wikipedia passages carry CC BY-SA 4.0, children's stories (from MCTest) carry the MSR-LA licence, exam passages (from RACE) carry RACE's own licence, and news passages (from the CNN/Daily Mail dataset) carry the Apache License; two of the seven domains, science and Reddit, are not released publicly at all.

## Who publishes it

CoQA comes from Siva Reddy, Danqi Chen and Christopher D. Manning at Stanford University, first posted to arXiv in August 2018 and later published in Transactions of the Association for Computational Linguistics, with the work presented at NAACL 2019. The authors continue to host the reference data, evaluation script and leaderboard at the project's Stanford-hosted website.

## Lineage

CoQA has no predecessor or successor tracked in this repository. The authors built its evaluation site and scripts on the SQuAD team's own template and thank them directly, and CoQA is best understood as extending SQuAD-style extractive reading comprehension into a conversational, multi-turn setting rather than replacing it; SQuAD itself does not have a page in this repository yet either.

## Saturation and contamination

The official leaderboard, read directly for this page, is topped by two ensembles that both reach 90.7% overall F1 -- "RoBERTa + AT + KD" from Zhuiyi Technology (September 2019) and "TR-MT" from WeChatAI (April 2020) -- both above the paper's own 88.8% human-performance figure. No leaderboard entry newer than April 2020 was visible in the portion of the table read for this page, suggesting submissions dried up once ensembles passed the human baseline rather than the leaderboard being formally retired the way some contemporaries' have been. Contamination risk sits at medium: train and validation data have been public since 2018, and while the held-out test sets are not public, several of CoQA's source domains (Wikipedia, CNN/Daily Mail news, RACE exam passages) are separately available in their original form, so a model could learn to answer CoQA-style questions about that text without ever seeing CoQA's own labels.

## How to run it

lm-evaluation-harness implements a `coqa` task that scores the public validation split (via a mirrored `EleutherAI/coqa` dataset) rather than the held-out test sets, generating free text and computing exact-match and F1 against the reference answers; its task config also wires in a decontamination check that compares each story-and-question pair against a reference corpus. Because the true held-out test sets are not available outside the original leaderboard process, essentially all contemporary harness-based CoQA numbers are validation-split scores, not the numbers that made the official leaderboard.

## Reading the numbers

A high CoQA F1 score indicates a model can track a multi-turn conversation about a passage and resolve references across turns, not just answer isolated questions -- a meaningfully different skill from single-turn extractive QA. Because the official leaderboard's ensembles passed the human baseline back in 2019-2020 and newer harness-reported numbers almost always come from the public validation split rather than the harder held-out test sets, do not assume a validation-split score and a leaderboard score are directly comparable. As with any answer-span or free-form F1 metric, also check whether a source scored exact spans or allowed paraphrase credit, since small scoring-protocol differences move F1 by several points.
