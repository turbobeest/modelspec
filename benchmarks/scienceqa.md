---
id: scienceqa
name: "ScienceQA"
aliases: []
page_kind: benchmark
category: multimodal
subcategory: "multimodal science multiple-choice QA with lecture and explanation annotations"
status: saturated
summary: "21,208 multimodal science multiple-choice questions annotated with lectures and explanations for chain-of-thought training; the leaderboard has sat frozen well above the human baseline since early 2024."
measures: >
  ScienceQA gives a model a science question, drawn from an elementary-through-high-school
  curriculum, together with optional context: an image (a diagram, photo or chart), a short hint,
  and always a multiple-choice answer set of two to five options that varies per question. Roughly
  half the questions include an image the question cannot be answered without; the rest are
  text-only. What sets ScienceQA apart from a plain multiple-choice quiz is that every question is
  also annotated with a "lecture" -- background knowledge relevant to the topic -- and a "solution,"
  a worked explanation of the correct answer. The benchmark's own paper is not really about the
  multiple-choice task alone: it uses these lecture and solution annotations to train and evaluate
  models that generate a chain-of-thought explanation before answering, and shows this measurably
  improves accuracy for both few-shot GPT-3 and fine-tuned smaller models.
task_format: >
  Multiple-choice question answering (two to five options, varying per question) over a science
  question that may include an accompanying image and a short hint; English only. Full evaluation
  runs the ~4,241-question test split, though many papers instead use a fixed, randomly-sampled
  1,000-question "test-mini" subset for cost reasons.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 39.83
  human_baseline: 88.40
  baseline_note: >
    Because the number of options varies by question, there is no fixed random-guess rate; the paper
    instead measured an empirical "Random Chance" baseline of 39.83% by scoring uniform random
    guesses over each question's actual option set, and measured human performance the same way at
    88.40% overall. Both are broken down identically by subject (natural/social/language science),
    context type (text, image, neither) and grade band (grades 1-6 versus 7-12) in the paper and on
    the official leaderboard; the paper's own baselines (zero- and few-shot GPT-3, fine-tuned
    UnifiedQA) all scored well below the human figure at release.
dataset:
  size: 21208
  size_note: >
    21,208 examples total -- 12,726 train, 4,241 validation, 4,241 test -- confirmed directly from
    the current Hugging Face mirror and matching the paper's own "~21k" figure almost exactly. Every
    example carries an image field (empty for text-only questions), question, choice list, answer
    index, optional hint, the lecture/solution annotation pair, and grade/subject/topic/category/
    skill metadata.
  url: "https://huggingface.co/datasets/derek-thomas/ScienceQA"
  license: "CC BY-SA 4.0 (Hugging Face dataset card)"
  languages:
    - en
  modalities:
    - text
    - image
  splits: "train (12,726) / validation (4,241) / test (4,241, answers public); many papers instead score a fixed 1,000-question random 'test-mini' subset"
  public_test_set: true
publisher:
  org: "University of California, Los Angeles (UCLA); Allen Institute for AI (AI2) -- multi-institution collaboration"
  authors:
    - "Pan Lu"
    - "Swaroop Mishra"
    - "Tony Xia"
    - "Liang Qiu"
    - "Kai-Wei Chang"
    - "Song-Chun Zhu"
    - "Oyvind Tafjord"
    - "Peter Clark"
    - "Ashwin Kalyan"
  url: "https://scienceqa.github.io"
paper:
  title: "Learn to Explain: Multimodal Reasoning via Thought Chains for Science Question Answering"
  arxiv: "2209.09513"
  url: "https://arxiv.org/abs/2209.09513"
  year: 2022
leaderboard_url: "https://scienceqa.github.io/leaderboard.html"
repo_url: "https://github.com/lupantech/ScienceQA"
released: "2022-09"
last_updated: "2024-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 96.18
  as_of: "2024-01"
  note: >
    The official leaderboard -- read live for this page, and identical to the copy embedded in the
    GitHub README -- is topped by "Multimodal-T-SciQ_Large" at 96.18% overall (submitted May 2023),
    with the next four entries all above 93%, and dozens of its roughly 80 ranked entries sit above
    the 88.40% human baseline. The leaderboard's own maintainers date its last major update to
    December 2023 and its newest individual entry (KAM-CoT) to January 2024, meaning it has not
    moved in well over two years; this repository's own model-card corpus contains zero mentions of
    "scienceqa." The leaderboard carries its own caveat that entries are collected manually from
    papers rather than independently re-run, so exact rankings should be read with that in mind.
contamination:
  risk: high
  note: >
    The full train, validation and test splits, including answers, lectures and solutions, have been
    public since 2022. The leaderboard's saturation (see above) is itself consistent with heavy
    reuse of this fixed, fully public item set in both training and evaluation across the model
    families that populate it.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "ScienceQA (the current LLM-judge config's reader_cfg passes only the question and choices text fields, with no image field referenced, and grades free-form responses with an LLM judge rather than the paper's own protocol -- so as configured it appears to exercise a text-only rendering of the task, not the image-grounded multimodal one)"
  bigbench: ""
  other: ""
tags:
  - multimodal
  - science-qa
  - chain-of-thought
  - multiple-choice
  - saturated
sources:
  - url: "https://arxiv.org/abs/2209.09513"
    title: "Learn to Explain: Multimodal Reasoning via Thought Chains for Science Question Answering (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://github.com/lupantech/ScienceQA"
    title: "lupantech/ScienceQA GitHub repository (README, embedded leaderboard table, NeurIPS 2022 citation)"
    accessed: "2026-09-08"
  - url: "https://scienceqa.github.io/leaderboard.html"
    title: "ScienceQA official interactive leaderboard"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/derek-thomas/ScienceQA"
    title: "derek-thomas/ScienceQA dataset card, Hugging Face (license, split sizes, feature schema)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/ScienceQA/ScienceQA_llmjudge_gen_f00302.py"
    title: "OpenCompass ScienceQA LLM-judge dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ScienceQA gives a model a science question, drawn from an elementary-through-high-school curriculum, together with optional context: an image (a diagram, photo or chart), a short hint, and always a multiple-choice answer set of two to five options that varies per question. Roughly half the roughly 21,000 questions include an image the question cannot be answered without; the rest are text-only. What sets ScienceQA apart from a plain multiple-choice quiz is that every question is also annotated with a "lecture" -- background knowledge relevant to the topic -- and a "solution," a worked explanation of the correct answer. The benchmark's own paper is not really about the multiple-choice task alone: it uses these lecture and solution annotations to train and evaluate models that generate a chain-of-thought explanation before answering, and shows this measurably improves accuracy for both few-shot GPT-3 and fine-tuned smaller models.

## How it is scored

Scoring is plain accuracy against the single correct option. Because the number of options varies by question, there is no fixed random-guess rate; the paper instead measured an empirical "Random Chance" baseline of 39.83% by scoring uniform random guesses over each question's actual option set, and measured human performance the same way at 88.40% overall. Both figures are broken down identically by subject (natural/social/language science), context type (text, image, neither) and grade band (grades 1-6 versus 7-12) in the paper and on the official leaderboard; the paper's own baselines -- zero- and few-shot GPT-3, and fine-tuned UnifiedQA -- all scored well below the human figure at release.

## Dataset and licence

The current Hugging Face mirror totals 21,208 examples -- 12,726 train, 4,241 validation, 4,241 test -- matching the paper's own "~21k" figure almost exactly, and is released under CC BY-SA 4.0. Every example carries an image field (empty for text-only questions), a question, a choice list, an answer index, an optional hint, the lecture/solution annotation pair described above, and grade, subject, topic, category and skill metadata. Because evaluating the full ~4,241-question test split is expensive against large or proprietary models, many papers instead report on a fixed, randomly-sampled 1,000-question "test-mini" subset; the official leaderboard tracks both.

## Who publishes it

ScienceQA was introduced by Pan Lu, Swaroop Mishra, Tony Xia, Liang Qiu, Kai-Wei Chang, Song-Chun Zhu, Oyvind Tafjord, Peter Clark and Ashwin Kalyan, presented at NeurIPS 2022 under the title "Learn to Explain: Multimodal Reasoning via Thought Chains for Science Question Answering." The lead author, Pan Lu, is at UCLA, and two co-authors, Oyvind Tafjord and Peter Clark, are AI2 researchers also behind this repository's `arc_challenge` page, making this a multi-institution collaboration rather than a single lab's release. The authors continue to maintain the reference GitHub repository and an interactive leaderboard at scienceqa.github.io/leaderboard.html.

## Lineage

No predecessor or successor is tracked in this repository, but ScienceQA's lead author also co-authored MathVista (`mathvista`), a later multimodal reasoning benchmark in the same visual-chain-of-thought tradition, and ScienceQA is a natural point of comparison for this repository's other multimodal science and diagram pages, MMMU (`mmmu`) and AI2D (`ai2d`), even though none of the three formally descends from another. ScienceQA predates all three and is one of the earlier benchmarks to pair multimodal multiple-choice questions with explanation annotations specifically to support and measure chain-of-thought prompting.

## Saturation and contamination

The official leaderboard -- read live for this page, and identical to the copy embedded in the GitHub README -- is topped by "Multimodal-T-SciQ_Large" at 96.18% overall (submitted May 2023), with the next four entries all above 93%, and dozens of its roughly 80 ranked entries sit above the 88.40% human baseline. The leaderboard's own maintainers date its last major update to December 2023 and its newest individual entry (KAM-CoT) to January 2024, meaning it has not moved in well over two years, and this repository's own model-card corpus contains zero mentions of "scienceqa." The leaderboard carries its own caveat that entries are collected manually from papers rather than independently re-run, so exact rankings should be read with that in mind. Contamination risk is high: the full train, validation and test splits, including answers, lectures and solutions, have been public since 2022.

## How to run it

No lm-evaluation-harness, inspect_evals, HELM or BIG-bench task name was confirmed for ScienceQA in the sources checked for this page. OpenCompass ships a `ScienceQA` config, but as currently written its reader configuration passes only the `question` and `choices` text fields into the prompt, with no `image` field referenced, and grades the free-form response with an LLM judge rather than the paper's original protocol -- meaning this specific harness path appears to exercise a text-only rendering of the benchmark rather than the image-grounded multimodal task ScienceQA is designed around. Vision-language-model evaluation toolkits more generally support the original image-plus-text task, though no specific task name for one was confirmed from a source opened for this page.

## Reading the numbers

A high ScienceQA score, on its own, now confirms very little: dozens of models on the official leaderboard already exceed the 88.40% human baseline, the leaderboard has been effectively frozen since early 2024, and no model card in this repository's own corpus currently reports it, all consistent with later multimodal suites (MMMU, MathVista) having displaced it for comparing frontier models. Before trusting any reported number, check whether it covers the full ~4,241-question test split or the smaller 1,000-question test-mini subset, and whether the harness that produced it actually supplied the question's image -- as the current OpenCompass configuration does not -- since a text-only score on an image-dependent question set is not comparable to the benchmark's original, image-grounded protocol.
