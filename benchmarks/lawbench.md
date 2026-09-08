---
id: lawbench
name: LawBench
aliases: []
page_kind: benchmark
category: domain
subcategory: "Chinese legal knowledge across three cognitive levels (memorization, understanding, application), 20 tasks"
status: active
summary: "LawBench scores a model's Chinese legal knowledge across 20 tasks grouped into memorization, understanding and application, drawn from real legal databases, exams and court documents."
measures: >
  LawBench tests a model's legal knowledge of the Chinese civil-law system across three cognitive levels:
  memorization (reciting law article text or answering legal-concept questions), understanding (proofreading
  legal documents, extracting named entities or events, identifying the point of dispute in a case, or
  summarizing legal news, among others) and application (predicting which article or charge applies to a
  set of facts, predicting a prison term, answering multiple-choice case-analysis questions in the style of
  China's judicial exam, or drafting a legal consultation answer). Its 20 tasks are drawn from a mix of
  sources: the national legal-article database, the JEC_QA judicial-exam question bank, and several years of
  the CAIL (Chinese AI and Law) shared-task datasets and the LAIC and LEVEN legal NLP datasets, rather than
  from questions written for the benchmark itself.
task_format: >
  Task format varies by task type: single-label or multi-label classification, regression (for example,
  predicting a prison term in months), span extraction, or free-text generation, each read from a Chinese-
  language prompt built from real legal text (a statute, a case summary, a court judgment excerpt, or a
  consultation question).
metric:
  name: "task-specific metric (accuracy, F1, rc-F1, soft-F1, F0.5, ROUGE-L, or normalized log-distance depending on task), averaged across tasks for a headline score"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random or human baseline applies across all 20 tasks, since they use seven different metric
    types; the paper reports zero-shot and one-shot results per task and an overall average rather than one
    baseline figure.
dataset:
  size: 10000
  size_note: >
    The project README states 500 examples per task across 20 tasks, "10,000 total instances," but per-task
    counts in the paper are not perfectly uniform: task 1-1 (article recitation) draws on 152 sub-articles
    across five core laws rather than 500 discrete questions, and task 3-2 (scene-based article prediction)
    uses 252 test examples; most of the remaining tasks report 500. Treat the round 10,000 figure as the
    source's own headline count rather than an exact per-task sum.
  url: "https://github.com/open-compass/LawBench"
  license: >
    LawBench is a mix of created and transformed datasets, and its own README asks users to follow the
    licence of each original source dataset (CAIL2018, CAIL2019, CAIL2021, CAIL2022, JEC_QA, LAIC2021, LEVEN
    and others) rather than stating one combined licence for the benchmark; the LawBench GitHub repository's
    own code is separately licensed Apache-2.0.
  languages: ["zh"]
  modalities: ["text"]
  splits: "20 task-specific test sets, mostly 500 examples each (a few tasks smaller, such as 252 for task 3-2); no shared train/validation split"
  public_test_set: true
publisher:
  org: "Shanghai AI Laboratory, Amazon Alexa AI, Saarland University and Nanjing University"
  authors: ["Zhiwei Fei", "Xiaoyu Shen", "Dawei Zhu", "Fengzhe Zhou", "Zhuo Han", "Songyang Zhang", "Kai Chen", "Zongwen Shen", "Jidong Ge"]
  url: "https://github.com/open-compass/LawBench"
paper:
  title: "LawBench: Benchmarking Legal Knowledge of Large Language Models"
  arxiv: "2309.16289"
  url: "https://arxiv.org/abs/2309.16289"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/open-compass/LawBench"
released: "2023-09"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 52.35
  as_of: "2023-09"
  note: >
    At release, GPT-4 led the zero-shot overall average at 52.35%, ahead of GPT-3.5-turbo (42.15%),
    StableBeluga2 (39.23%), Qwen-7B-Chat (37.00%) and InternLM-Chat-7B-8K (35.73%); the paper adds that
    fine-tuned legal-specific models such as ChatLaw-13B underperformed general-purpose Chinese-oriented
    models of similar size, and that one-shot prompting gave only modest gains over zero-shot. The
    open-compass/LawBench repository's commit history shows no activity since November 2023, and its own
    README still lists this same results table, so current-day standing beyond that reading is not
    established here.
contamination:
  risk: high
  note: >
    LawBench's component datasets (the CAIL shared-task releases, JEC_QA, LAIC2021, LEVEN and others) were
    already public, with answers, from their own original releases -- several years before LawBench itself
    was compiled in September 2023 -- and LawBench republishes them together without additional gating, so
    by this research date (2026-09-08) some components have had close to a decade of potential exposure to
    web crawls and training corpora.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "lawbench"
  bigbench: ""
  other: >
    The authors' own evaluation code and per-task prompt templates live under `evaluation/` in
    open-compass/LawBench; the paper's protocol truncates to 2048 input / 1024 output tokens, decodes
    open-source models greedily and GPT models at temperature 0.7 with top-p 1.0, and evaluates both
    zero-shot and one-shot. OpenCompass registers the benchmark as `lawbench`, with separate
    `lawbench_zero_shot_gen` and `lawbench_one_shot_gen` config files matching that same protocol split.
    Not confirmed in the lm-evaluation-harness, HELM or BIG-bench task lists.
tags: ["legal", "chinese", "domain-knowledge", "classification", "generation"]
sources:
  - url: "https://arxiv.org/abs/2309.16289"
    title: "LawBench: Benchmarking Legal Knowledge of Large Language Models"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2309.16289"
    title: "LawBench, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/LawBench"
    title: "open-compass/LawBench repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/LawBench/main/README_EN.md"
    title: "open-compass/LawBench: README_EN.md"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/lawbench"
    title: "OpenCompass lawbench dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LawBench tests a model's legal knowledge of the Chinese civil-law system across three cognitive levels,
following a framework borrowed from educational assessment: memorization (reciting the text of a law
article given its number, or answering multiple-choice questions about legal concepts), understanding (for
example, proofreading a legal document, pulling named entities or events out of a judgment, identifying the
point of dispute in a civil case, or summarizing legal news) and application (predicting which article or
criminal charge applies to a set of facts, predicting a prison term, answering case-analysis questions in
the style of China's national judicial exam, calculating criminal damages, or drafting a consultation
answer). Its 20 tasks are drawn from real sources rather than written for the benchmark: the national legal
database, the JEC_QA judicial-exam question bank, several years of the CAIL shared-task datasets, and the
LAIC and LEVEN legal NLP datasets.

## How it is scored

Because the 20 tasks span classification, regression, extraction and generation, LawBench uses seven
different metric families depending on task type: accuracy for multiple-choice and single-label tasks, F1
for multi-label classification and article/charge prediction, a reading-comprehension F1 variant, a
tolerant "soft" F1 for phrase-level extraction, F0.5 for proofreading, ROUGE-L for generation and recitation
tasks, and a normalized log-distance for the two prison-term prediction tasks. A model's headline LawBench
number is the average across all 20 per-task scores. The paper evaluates each model zero-shot and one-shot,
in Chinese, with model-specific prompt prefixes and suffixes, truncating inputs to 2048 tokens and outputs
to 1024.

## Dataset and licence

The project README states 500 examples per task across the 20 tasks, "10,000 total instances," though
individual task sizes in the paper are not perfectly uniform -- article recitation draws on 152 sub-articles
across five core laws rather than 500 discrete items, and scene-based article prediction uses 252 test
examples. LawBench is, in its own README's words, "a mix of created and transformed datasets," and asks
users to follow the licence of each original source (the CAIL2018/2019/2021/2022 shared tasks, JEC_QA,
LAIC2021, LEVEN and others) rather than stating one combined data licence; the LawBench repository's own
code is separately Apache-2.0. All data and model predictions are released publicly on GitHub without
gating.

## Who publishes it

LawBench comes from Zhiwei Fei, Xiaoyu Shen, Dawei Zhu, Fengzhe Zhou, Zhuo Han, Songyang Zhang, Kai Chen,
Zongwen Shen and Jidong Ge, working across Shanghai AI Laboratory, Amazon Alexa AI, Saarland University and
Nanjing University, posted to arXiv in September 2023. The paper evaluated 51 models: 20 multilingual
general-purpose models, 22 Chinese-oriented models, and 9 legal-domain fine-tuned models. The authors
maintain the reference data, predictions and evaluation code at github.com/open-compass/LawBench, and the
benchmark is integrated into the OpenCompass evaluation platform from the same organisation.

## Lineage

No predecessor, successor or formal variant of LawBench is catalogued in this repository. It occupies a
similar role for Chinese law that HeadQA occupies for Spanish healthcare exams or LawBench's own JEC_QA
source occupies for the judicial exam specifically: a domain-knowledge benchmark built from real
professional material rather than benchmark-written questions.

## Saturation and contamination

At release, GPT-4 led the zero-shot overall average at 52.35%, ahead of GPT-3.5-turbo (42.15%),
StableBeluga2 (39.23%), Qwen-7B-Chat (37.00%) and InternLM-Chat-7B-8K (35.73%) -- roughly half of the
notional 100-point ceiling, with fine-tuned legal-specific models such as ChatLaw-13B underperforming
general-purpose Chinese-oriented models of similar size. The open-compass/LawBench repository has shown no
commit activity since November 2023 and its README still displays this same table, so this page cannot
establish where current (2025- or 2026-era) models stand. Contamination risk is high: LawBench's component
datasets were already public, with answers, well before LawBench itself compiled them in September 2023,
giving some of the underlying material years of additional exposure to web crawls and model training data
by 2026.

## How to run it

The authors' own evaluation code and per-task prompt templates live under `evaluation/` in
open-compass/LawBench, truncating inputs to 2048 tokens and outputs to 1024, decoding open-source models
greedily and GPT models at temperature 0.7 with top-p 1.0, and evaluating both zero-shot and one-shot.
OpenCompass registers the benchmark as `lawbench`, with separate zero-shot and one-shot config files
matching that protocol. It was not confirmed in the lm-evaluation-harness, HELM or BIG-bench task lists, so
a score from one of those suites should not be assumed without checking a specific implementation.

## Reading the numbers

A high LawBench score shows a model recognizes and can apply Chinese statute and case-law patterns across
memorization, understanding and application tasks -- it is not a substitute for legal training or licensed
legal advice, and the paper itself concludes current models remain "a long way from obtaining usable and
reliable LLMs in legal tasks." Because the headline average blends seven different metric types across
tasks of very different difficulty and format, two similar overall scores can come from very different
per-task profiles, so check the per-cognitive-level or per-task breakdown before treating one number as the
whole picture. Zero-shot and one-shot scores are not interchangeable, and because no current leaderboard was
confirmed for this page, treat any recent LawBench number as being compared to a September 2023 reference
point rather than an actively maintained ranking.
