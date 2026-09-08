---
id: chinese_simpleqa
name: "Chinese SimpleQA"
aliases:
  - "Chinese-SimpleQA"
page_kind: benchmark
category: knowledge
subcategory: "short-answer factuality, LLM-graded (Chinese-language counterpart to OpenAI's SimpleQA)"
status: active
summary: The Chinese counterpart to OpenAI's SimpleQA -- 3,000 short fact-seeking questions across 6 topics and 99 subtopics, from Alibaba's Taobao & Tmall Group, LLM-graded following SimpleQA's approach.
measures: >
  Chinese SimpleQA measures short-form factuality in Chinese: whether a model gives a correct, brief
  answer to a fact-seeking question with one static, indisputable answer. The paper positions the
  benchmark explicitly as a Chinese counterpart to OpenAI's SimpleQA (documented in this repository
  as `simpleqa`), built to address the same gap OpenAI identified -- that short, open-ended
  fact-seeking evaluation was missing -- but for Chinese, where the authors say the
  widely-used knowledge sets (CommonSenseQA, CMMLU, C-Eval) are multiple-choice rather than
  open-ended. Questions span six major topics -- Chinese Culture, Humanities, Engineering/
  Technology/Applied Sciences, Life/Art/Culture, Society, and Natural Science -- covering 99
  finer-grained subtopics, and the authors state they applied "a comprehensive and rigorous quality
  control process" to keep reference answers static (unchanging over time) and unambiguous. It is a
  single-turn, Chinese-language, text-only task, independently constructed for Chinese rather than
  translated from OpenAI's English question set.
task_format: >
  Short free-form answer generation to a single fact-seeking Chinese-language question, with no
  supporting passage supplied; graded by a separate LLM grader (the repository recommends the
  OpenAI API) against a reference answer, following SimpleQA's grading approach, rather than scored
  by exact string match.
metric:
  name: "LLM-grader-classified correctness, following SimpleQA's grading approach"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper states its grading process "follows SimpleQA" and recommends running the grader
    through the OpenAI API, but this page could not directly confirm from the sources read whether
    Chinese SimpleQA reuses OpenAI SimpleQA's exact three-way CORRECT/INCORRECT/NOT_ATTEMPTED rubric
    and derived accuracy / accuracy-given-attempted / F-score formulas, or a rubric of its own: the
    grading prompt is not exposed in the public dataset (columns are `id`, `primary_category`,
    `secondary_category`, `question`, `answer`, `urls`) or in OpenCompass's integration script, which
    instead pulls a `system_prompt` and `prompt_template` from its own internal pipeline. No random
    or human baseline applies to this open-ended, single-reference-answer format.
dataset:
  size: 3000
  size_note: >
    3,000 question-answer pairs, confirmed directly against the live Hugging Face parquet files,
    matching the paper's stated count exactly. Each item carries an id, a primary_category (one of
    6), a secondary_category (one of 99 across the corpus), the answer, and supporting source urls;
    there is no separate train/validation split.
  url: "https://huggingface.co/datasets/OpenStellarTeam/Chinese-SimpleQA"
  license: "CC-BY-NC-SA-4.0, per the Hugging Face dataset card; the OpenStellarTeam/ChineseSimpleQA GitHub repository carries no separate LICENSE file for its code."
  languages:
    - zh
  modalities:
    - text
  splits: "single 3,000-question set (no train/validation split); reference answers are public"
  public_test_set: true
publisher:
  org: "Taobao & Tmall Group, Alibaba"
  authors:
    - Yancheng He
    - Shilong Li
    - Jiaheng Liu
    - Yingshui Tan
    - Weixun Wang
    - Hui Huang
    - Xingyuan Bu
    - Hangyu Guo
    - Chengwei Hu
    - Boren Zheng
    - Zhuoran Lin
    - Xuepeng Liu
    - Dekai Sun
    - Shirong Lin
    - Zhicheng Zheng
    - Xiaoyong Zhu
    - Wenbo Su
    - Bo Zheng
  url: "https://openstellarteam.github.io/ChineseSimpleQA/"
paper:
  title: "Chinese SimpleQA: A Chinese Factuality Evaluation for Large Language Models"
  arxiv: "2411.07140"
  url: "https://arxiv.org/abs/2411.07140"
  year: 2024
leaderboard_url: "http://47.109.32.164/"
repo_url: "https://github.com/OpenStellarTeam/ChineseSimpleQA"
released: "2024-11"
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
    The repository names a bare-IP leaderboard (http://47.109.32.164/) that did not respond when
    checked for this page (connection timed out), so this page could not read current standings from
    it. No independently maintained, reachable leaderboard or current top-model score was confirmed
    from the sources read, so a saturation read beyond "unknown" is not established.
contamination:
  risk: medium
  note: >
    All 3,000 questions and their reference answers have been public on GitHub and Hugging Face
    since around the paper's November 2024 posting, under a licence that permits redistribution, so
    a model trained since then could plausibly have seen them. No publisher statement or independent
    study demonstrating actual leakage into a specific model's training data was found, so this page
    does not go beyond "medium."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "chinese_simpleqa"
  bigbench: ""
  other: ""
tags:
  - knowledge
  - factuality
  - chinese
  - question-answering
  - llm-judge
sources:
  - url: "https://arxiv.org/abs/2411.07140"
    title: "Chinese SimpleQA: A Chinese Factuality Evaluation for Large Language Models (He et al., arXiv:2411.07140)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2411.07140"
    title: "Chinese SimpleQA: A Chinese Factuality Evaluation for Large Language Models (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/OpenStellarTeam/ChineseSimpleQA"
    title: "OpenStellarTeam/ChineseSimpleQA GitHub repository (README)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OpenStellarTeam/Chinese-SimpleQA"
    title: "OpenStellarTeam/Chinese-SimpleQA dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/chinese_simpleqa/README.md"
    title: "OpenCompass chinese_simpleqa dataset README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Chinese SimpleQA measures short-form factuality in Chinese: whether a model gives a correct, brief answer to a fact-seeking question that has one static, indisputable answer. The paper positions it explicitly as a Chinese counterpart to OpenAI's SimpleQA (`simpleqa` in this repository), built to fill the same gap OpenAI identified for English -- that short, open-ended fact-seeking evaluation was missing -- but for Chinese, where the authors argue the most widely used knowledge benchmarks (CommonSenseQA, CMMLU, C-Eval) are multiple-choice rather than open-ended and so test something different.

Questions span six major topics -- Chinese Culture, Humanities, Engineering/Technology/Applied Sciences, Life/Art/Culture, Society, and Natural Science -- covering 99 finer-grained subtopics, with each item tagged by both. The authors state they applied "a comprehensive and rigorous quality control process" to keep reference answers static, so they do not change over time, and unambiguous. It is a single-turn, Chinese-language, text-only task, independently constructed for Chinese rather than translated from OpenAI's English question set.

## How it is scored

A model's short free-text answer is graded against a reference answer by a separate LLM grader rather than by exact string match, with the paper stating its grading process "follows SimpleQA" and the repository recommending the grader be run through the OpenAI API. This page could not directly confirm whether Chinese SimpleQA reuses OpenAI SimpleQA's exact three-way CORRECT / INCORRECT / NOT_ATTEMPTED rubric and its derived accuracy, accuracy-given-attempted and F-score figures, or applies a rubric of its own: the public Hugging Face dataset carries only `id`, `primary_category`, `secondary_category`, `question`, `answer` and `urls` columns, with no grading prompt included, and OpenCompass's integration pulls a `system_prompt` and `prompt_template` from its own pipeline rather than the config file itself. No random or human baseline applies to this open-ended, single-reference-answer format.

## Dataset and licence

The dataset totals 3,000 question-answer pairs, confirmed directly against the live Hugging Face parquet files and matching the paper's stated count exactly -- noticeably smaller than SimpleQA's 4,326 English questions. Each item carries a primary category (one of 6), a secondary category (one of 99 across the corpus), and supporting source URLs, with no train/validation split. The data is released under a CC-BY-NC-SA-4.0 licence per the Hugging Face card -- a clearer licence statement than SimpleQA's own data has, where this repository's `simpleqa` page found no authoritative licence statement from OpenAI itself. The GitHub code repository carries no separate LICENSE file.

## Who publishes it

Chinese SimpleQA was published in November 2024 by Yancheng He, Shilong Li and Jiaheng Liu (the paper states these three contributed equally) together with fourteen further co-authors, all affiliated with the Taobao & Tmall Group of Alibaba; Jiaheng Liu is the paper's corresponding author. The `OpenStellarTeam` GitHub organisation maintains the reference repository and dataset, and the authors state they maintain a leaderboard, though the linked address (a bare IP) did not respond when checked for this page.

## Lineage

Chinese SimpleQA has no predecessor or successor tracked in this repository, but it is explicitly modelled on `simpleqa` (OpenAI's "Measuring short-form factuality in large language models," 2024): both test single-turn, short, fact-seeking recall with one indisputable reference answer, graded by an LLM rather than by exact match, and both were built specifically to give frontier models a factuality test harder than older, largely-saturated open-domain QA sets. They differ in scope rather than method: Chinese SimpleQA is Chinese-only, about a third smaller (3,000 versus 4,326 questions), organised around an explicit six-topic/99-subtopic taxonomy not present in the same form in the English original, published by a different organisation (Alibaba's Taobao & Tmall Group rather than OpenAI) under a clearer public licence (CC-BY-NC-SA-4.0 versus SimpleQA's own unestablished data licence), and this page could not confirm whether it reuses SimpleQA's exact adversarial-collection-against-a-model methodology or its precise three-category grading rubric, only that the authors state they followed SimpleQA's general approach. The two are siblings built independently by different organisations, not versions of one shared benchmark.

## Saturation and contamination

The repository names a leaderboard at a bare IP address that did not respond when checked for this page, so no current standings could be read from it, and no other independently maintained, reachable leaderboard was found. A saturation read beyond "unknown" is not established from the sources reviewed.

Contamination risk sits at medium: all 3,000 questions and their reference answers have been public on GitHub and Hugging Face since around the paper's November 2024 posting date, under a licence that permits redistribution, so a model trained since then could plausibly have seen them. No publisher statement or independent study demonstrating actual leakage was found.

## How to run it

The reference dataset and grading scripts live in the `OpenStellarTeam/ChineseSimpleQA` GitHub repository, with three evaluation paths documented: a `simple-evals`-based script, a from-scratch single-evaluation script (both requiring an OpenAI API key for grading), and an OpenCompass integration (`chinese_simpleqa`, using OpenCompass's `LMEvaluator`), which the authors state they maintain in their own fork of OpenCompass. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found. Because grading depends on an LLM judge rather than a fixed rule, and the exact grading prompt was not directly inspected for this page, two reported Chinese SimpleQA scores are only safely comparable if both used the same judge model and prompt.

## Reading the numbers

A high Chinese SimpleQA score indicates a model reliably recalls specific, verifiable Chinese-language facts across a broad topic spread and, importantly, avoids confidently guessing when it does not know an answer, since LLM-based SimpleQA-style grading rewards accurate abstention over confident wrong answers. It is not a general Chinese-language capability test: like its English counterpart, a model can score well by attempting only the questions it is confident about. Because this benchmark's precise grading rubric was not independently confirmed against OpenAI SimpleQA's own published categories, and because both benchmarks depend on a judge model that can itself vary between reporters, treat cross-language comparisons between a "SimpleQA" and a "Chinese SimpleQA" score as directional at best, not a controlled measurement of the same underlying skill.
