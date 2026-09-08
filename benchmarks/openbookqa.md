---
id: openbookqa
name: "OpenBookQA"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "open-book elementary-science multiple-choice QA"
status: saturated
summary: "5,957 four-way elementary-science questions built around a small fact book; human accuracy is near 92%, and no current model card or live leaderboard still reports it."
measures: >
  OpenBookQA asks a model to answer an elementary-school-level science question by combining one
  "open book" fact with broad common knowledge, the way an open-book exam works: knowing where to
  look up the fact is not enough, because the missing piece is background knowledge no book states
  outright. The open book itself is a set of roughly 1,326-1,329 core science facts (sources read
  for this page give slightly different counts; see Dataset and licence) covering topics such as
  conductivity, states of matter and food chains. Around 6,000 four-way multiple-choice questions
  were then written against those facts so that each one also requires an additional, unstated piece
  of common knowledge to connect the fact to the question -- for example, the fact "metal is a
  thermal conductor" only answers a question about which object conducts the most heat if the model
  also knows a steel spoon is made of metal. That two-hop structure sets it apart from earlier
  reading-comprehension datasets, which typically expect an answer extractable from one supplied
  passage.
task_format: >
  Four-way multiple-choice question answering, typically zero- or few-shot, over a fixed set of
  roughly 6,000 English-language elementary-science questions; no passage or fact is supplied at
  inference time, so the model must supply both the fact and the connecting common-knowledge step
  itself.
metric:
  name: "accuracy (acc and length-normalised acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: 91.7
  baseline_note: >
    The paper measured human accuracy at 89.3% on the Dev split and 91.7% on the Test split, a
    conservative estimate computed from crowd-worker agreement rates; a smaller spot-check of fresh
    annotations landed at 88.6/90.2/91.6% on Train/Dev/Test, consistent with the abstract's rounder
    "close to 92%" claim. Against a 25.0% four-way random baseline, contemporary pretrained QA
    systems performed surprisingly poorly: the paper's strongest non-oracle neural baseline (an
    "Odd-one-out Solver") reached only 50.2% on Test, and the paper explicitly notes several
    state-of-the-art QA models of the time scored worse than its own simple neural baselines. Only
    "oracle" variants fed the gold fact directly approached human performance, reaching up to 76.9%,
    which the authors use to argue the real bottleneck was retrieving the right fact, not reasoning
    once it is in hand.
dataset:
  size: 5957
  size_note: >
    5,957 questions total (4,957 train / 500 validation / 500 test), identical across the Hugging
    Face "main" and "additional" configs; "additional" adds the gold supporting fact plus two
    human-rating fields (humanScore, clarity) that "main" omits. The size of the underlying "open
    book" of facts is reported inconsistently between sources read for this page: the current arXiv
    abstract states 1,329 facts, while the paper's own body text (read via ar5iv) states 1,326; both
    describe the same collection, and this page records both readings rather than picking one.
  url: "https://huggingface.co/datasets/allenai/openbookqa"
  license: >
    Marked "unknown" on the Hugging Face dataset card. The reference code repository
    (allenai/OpenBookQA on GitHub) is Apache-2.0 licensed, but that licence covers the baseline
    modelling code, not a separately stated licence for the question-and-fact text itself.
  languages:
    - en
  modalities:
    - text
  splits: "train (4,957) / validation (500) / test (500); test-split answers are public, unlike several sibling AI2 benchmarks from the same period"
  public_test_set: true
publisher:
  org: "Allen Institute for Artificial Intelligence (AI2)"
  authors:
    - "Todor Mihaylov"
    - "Peter Clark"
    - "Tushar Khot"
    - "Ashish Sabharwal"
  url: "https://allenai.org"
paper:
  title: "Can a Suit of Armor Conduct Electricity? A New Dataset for Open Book Question Answering"
  arxiv: "1809.02789"
  url: "https://arxiv.org/abs/1809.02789"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/allenai/OpenBookQA"
released: "2018-09"
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
  note: >
    No current top score could be confirmed for this page: AI2's own leaderboard subdomain
    (leaderboard.allenai.org) fails to resolve at all (confirmed by a direct DNS lookup failure
    during this research), and paperswithcode.com's listing now redirects to Hugging Face's papers
    hub rather than showing leaderboard data. Combined with a human ceiling already at 91.7% in the
    original 2018 paper and zero mentions of "openbookqa" anywhere across this repository's own
    model-card corpus (checked by grep), the benchmark is treated here as saturated and effectively
    retired from current frontier-model reporting rather than actively tracked.
contamination:
  risk: high
  note: >
    Both the questions and their answer keys, including the test split, have been fully public since
    2018. lm-evaluation-harness's task config enables a decontamination check comparing the question
    stem against a reference corpus, itself a signal the community still treats leakage as a live
    concern for any benchmark still run against this data.
harness:
  lm_eval: "openbookqa (dataset_path allenai/openbookqa, config main, output_type multiple_choice, scores the public test split with acc and acc_norm, should_decontaminate on question_stem)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - multiple-choice
  - elementary-science
  - commonsense
  - retired-leaderboard
sources:
  - url: "https://arxiv.org/abs/1809.02789"
    title: "Can a Suit of Armor Conduct Electricity? A New Dataset for Open Book Question Answering (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.org/abs/1809.02789"
    title: "Can a Suit of Armor Conduct Electricity? (ar5iv full text, incl. Table 4 baseline scores and Section 3.2 human performance)"
    accessed: "2026-09-08"
  - url: "https://github.com/allenai/OpenBookQA"
    title: "allenai/OpenBookQA GitHub repository (README, licence, EMNLP-2018 citation)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/openbookqa"
    title: "allenai/openbookqa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/splits?dataset=allenai/openbookqa"
    title: "allenai/openbookqa configs and splits, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/openbookqa/openbookqa.yaml"
    title: "lm-evaluation-harness openbookqa task config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

OpenBookQA asks a model to answer an elementary-school-level science question by combining one "open book" fact with broad common knowledge, the way an open-book exam works: knowing where to look up the fact is not enough, because the missing piece is background knowledge no book states outright. The open book itself is a set of roughly 1,326-1,329 core science facts (sources read for this page give slightly different counts) covering topics such as conductivity, states of matter and food chains. Around 6,000 four-way multiple-choice questions were then written against those facts so that each one also requires an additional, unstated piece of common knowledge to connect the fact to the question -- for example, the fact "metal is a thermal conductor" only answers a question about which object conducts the most heat if the model also knows a steel spoon is made of metal.

## How it is scored

Systems pick one of four answer choices per question, scored by plain accuracy; lm-evaluation-harness additionally reports length-normalised accuracy (acc_norm) alongside raw accuracy. The paper measured human accuracy at 89.3% on Dev and 91.7% on Test (a conservative estimate from crowd-worker agreement, with a smaller spot-check landing at 88.6/90.2/91.6% on Train/Dev/Test), against a 25.0% four-way random baseline. Contemporary pretrained QA models performed surprisingly poorly against that gap: the paper's strongest non-oracle neural baseline, an "Odd-one-out Solver," reached only 50.2% on Test, and the paper explicitly notes several state-of-the-art QA systems of the time scored worse than its own simple neural baselines. Only "oracle" variants given the gold fact directly approached human performance, reaching up to 76.9%, which the authors use to argue the real bottleneck was retrieving the right fact rather than reasoning once it is in hand.

## Dataset and licence

The Hugging Face "main" and "additional" configs both total 5,957 questions -- 4,957 train, 500 validation, 500 test -- with test-split answers public, unlike several sibling AI2 benchmarks from the same period. The "additional" config adds the gold supporting fact and two human-rating fields (humanScore, clarity) that "main" omits. The open book's own size is reported inconsistently between the sources read for this page: the current arXiv abstract states 1,329 facts, while the paper's body text (read via ar5iv) states 1,326; both describe the same collection, and this page records both readings rather than picking one. The Hugging Face dataset card marks the licence "unknown"; the reference GitHub repository is Apache-2.0 licensed, but that covers the baseline modelling code, not a separately stated licence for the question-and-fact text itself.

## Who publishes it

OpenBookQA comes from Todor Mihaylov, Peter Clark, Tushar Khot and Ashish Sabharwal at the Allen Institute for Artificial Intelligence (AI2), presented at EMNLP 2018 under the title "Can a Suit of Armor Conduct Electricity? A New Dataset for Open Book Question Answering." AI2 originally hosted a dedicated project page and leaderboard at leaderboard.allenai.org; that subdomain no longer resolves at all (confirmed by a direct DNS lookup failure during this research), and allenai.org's own dataset page now redirects straight to the Hugging Face dataset card, which is the closest thing to an official current home for the data.

## Lineage

OpenBookQA has no predecessor or successor tracked in this repository, but it was released the same era as, and is routinely evaluated alongside, ARC-Challenge (`arc_challenge`) and CommonsenseQA (`commonsense_qa`) as one of a cohort of AI2-adjacent four- or five-way multiple-choice science and commonsense benchmarks from 2018-2019. Social IQa (`siqa`), covered elsewhere in this same research batch, is a same-era sibling from an overlapping author community aimed at social rather than physical-science commonsense. None of these formally supersedes another; they are best read as parallel efforts from the same period rather than a lineage.

## Saturation and contamination

No current top score could be confirmed for this page: AI2's own leaderboard subdomain fails to resolve at all, and paperswithcode.com's listing now redirects to Hugging Face's papers hub rather than showing leaderboard data. Combined with a human ceiling already at 91.7% in the original 2018 paper and zero mentions of "openbookqa" anywhere across this repository's own model-card corpus, the benchmark is treated here as saturated and effectively retired from current frontier-model reporting rather than actively tracked. Contamination risk is high: both the questions and their answer keys, including the test split, have been fully public since 2018, and lm-evaluation-harness's task config enables a decontamination check against the question stem, itself a signal the community still treats leakage as a live concern for any benchmark still run against this data.

## How to run it

lm-evaluation-harness implements `openbookqa`, reading the "main" Hugging Face config, evaluating the public test split with both accuracy and length-normalised accuracy, and enabling decontamination against the question stem. No inspect_evals, HELM, OpenCompass or BIG-bench task name was confirmed for OpenBookQA in the sources checked for this page.

## Reading the numbers

A strong OpenBookQA score today says very little on its own: the benchmark's own human ceiling was only a few points above where a well-tuned system landed within a couple of years of release, its answer keys have been public for close to a decade, and it has effectively dropped out of frontier-model reporting, this repository's own model cards included. It is best read as a floor check inherited from older evaluation suites rather than a differentiator between current models. Treat any single high score as expected rather than impressive, and corroborate it against a harder, less-exposed reasoning or knowledge benchmark before drawing conclusions from it alone.
