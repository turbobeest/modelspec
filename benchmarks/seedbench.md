---
id: seedbench
name: "SeedBench"
aliases:
  - "SeedBench: A Multi-task Benchmark for Evaluating Large Language Models in Seed Science"
page_kind: benchmark
category: domain
subcategory: "seed science and rice breeding decision support"
status: active
summary: "2,264 expert-validated questions across 11 task types simulating gene retrieval, gene-function analysis and variety breeding for rice, scored by accuracy, macro-F1 or ROUGE-L per task."
measures: >
  SeedBench tests whether a model can support the decision-making stages a seed breeder works
  through: retrieving gene information, analysing gene function and regulation, and reasoning
  about variety breeding outcomes. Content is built from a corpus of roughly 308,727 breeding
  publications distilled to about 1.1 billion tokens, initially scoped to rice, with maize,
  soybean and wheat planned as future extensions. Tasks span three families: question answering
  (multiple choice, multiple answer, fill-in-the-blank, open generation), summarisation (plain
  summary and key-information extraction) and reading comprehension (multiple choice, multiple
  answer, fill-in-the-blank, generation and subcategory classification).
task_format: >
  Mixed by task type: single- and multi-answer multiple choice, cloze-style fill-in-the-blank,
  free-text generation, extractive/abstractive summarisation, and classification. OpenCompass
  runs it as the `seedbench_gen` config, reading `instruction` and `question` fields against an
  `answer` field, applying different postprocessors per subcategory (1-1 through 3-5).
metric:
  name: "accuracy / macro-F1 / ROUGE-L (task-dependent)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The GitHub repository states multiple-choice tasks are scored by accuracy, multiple-answer
    tasks by macro-F1, and generation/summarisation tasks by ROUGE-L. The paper's headline
    "overall performance" and "subcategory average" figures combine these different metrics into
    one number per model; no single random-guess baseline applies across that mix.
dataset:
  size: 2264
  size_note: >
    GitHub README gives exact per-task-type counts summing to 2,264: QA multiple choice 200,
    QA multiple answer 187, QA fill-in-the-blank 224, QA generation 242, summarisation (simple)
    225, summarisation (key-information extraction) 225, reading-comprehension multiple choice
    113, multiple answer 108, fill-in-the-blank 221, generation 240, subcategory classification
    279. The paper separately describes a larger pool of 4,336 bilingual (English/Chinese)
    questions used before expert validation narrowed it to the 2,264-question released benchmark;
    that distinction was not independently resolved beyond the paper's abstract-level framing.
  url: "https://github.com/open-sciencelab/SeedBench"
  license: "GPL-3.0 (code repository; a separate data licence was not confirmed)"
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "single evaluation set, distributed via ModelScope"
  public_test_set: true
publisher:
  org: "Shanghai AI Laboratory (InternScience / open-sciencelab)"
  authors:
    - "Jie Ying"
    - "Zihong Chen"
    - "Zhefan Wang"
    - "Wanli Jiang"
    - "Chenyang Wang"
    - "Zhonghang Yuan"
    - "Haoyang Su"
    - "Huanjun Kong"
    - "Fan Yang"
    - "Nanqing Dong"
  url: "https://github.com/open-sciencelab/SeedBench"
paper:
  title: "SeedBench: A Multi-task Benchmark for Evaluating Large Language Models in Seed Science"
  arxiv: "2505.13220"
  url: "https://arxiv.org/abs/2505.13220"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/open-sciencelab/SeedBench"
released: "2025-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 68.37
  as_of: "2025-05"
  note: >
    The paper's headline numbers put DeepSeek-V3 at 68.37% overall (question-type average) ahead
    of GPT-4 at 67.88%, and DeepSeek-V3-671B at 63.30% on the subcategory average versus GPT-4's
    62.06%. All 26 evaluated models sit well below a 100% ceiling, and the authors' stated
    conclusion is that current LLMs are not yet reliable for real seed-science decision support.
contamination:
  risk: unknown
  note: >
    The underlying corpus (308,727 breeding publications) and the released question set are both
    public, and no rotating or held-out variant is described, so leakage into later pretraining
    corpora is plausible. The paper does not report a contamination analysis, and none was found
    independently, so risk is left unknown rather than assumed.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "seedbench"
  bigbench: ""
  other: "OpenCompass config directory datasets/SeedBench (seedbench_gen_5d5ea1.py); dataset downloads automatically from ModelScope on first OpenCompass run."
tags:
  - agriculture
  - seed-science
  - rice-breeding
  - bilingual
  - domain-knowledge
sources:
  - url: "https://arxiv.org/abs/2505.13220"
    title: "SeedBench paper abstract (arXiv:2505.13220), ACL 2025, 2,264 questions, 11 task types, 26 models"
    accessed: "2026-09-08"
  - url: "https://github.com/open-sciencelab/SeedBench"
    title: "open-sciencelab/SeedBench GitHub README (per-task-type counts, GPL-3.0 licence, ModelScope download, ROUGE-L/accuracy/macro-F1 metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SeedBench/README.md"
    title: "OpenCompass SeedBench dataset README (confirms same task breakdown: QA 4 types, summarisation 2 types, reading comprehension 5 types)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SeedBench/seedbench_gen_5d5ea1.py"
    title: "OpenCompass seedbench_gen config (opencompass/seedbench dataset path, category codes 1-1..3-5, AccEvaluator/F1ScoreEvaluator/RougeEvaluator)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-003"
---

## What it measures

SeedBench (this page) tests a model's usefulness in the seed-breeding pipeline, not general knowledge trivia. It simulates three stages a breeder works through in practice: pulling gene information, analysing what a gene does and how it is regulated, and reasoning about the outcome of a variety-breeding decision. The initial release focuses on rice, built from a large corpus of breeding literature distilled by domain experts, with maize, soybean and wheat named as future extensions. Content is bilingual, in English and Chinese.

This name collides with a well-known, unrelated multimodal benchmark, AILab-CVC's "SEED-Bench" for image/video large language models. The OpenCompass configuration directory used for the `seedbench` harness id in this repository's census hint (`opencompass/configs/datasets/SeedBench`) was opened directly for this page and its task categories (four QA types, two summarisation types, five reading-comprehension types, 11 total) match the seed-science benchmark's GitHub README exactly, not the multimodal one. Do not use scores reported under "SEED-Bench" for multimodal models as if they were this benchmark.

## How it is scored

Scoring is task-type dependent: accuracy for multiple-choice questions, macro-F1 for multiple-answer questions, and ROUGE-L for open-ended generation and summarisation tasks. The paper aggregates these into an "overall" question-type average and a separate "subcategory" average; because the underlying per-task metrics are not the same statistic, a single reported percentage should be read as a paper-defined composite rather than a uniform accuracy figure. OpenCompass implements the benchmark as `seedbench_gen`, applying `AccEvaluator`, `F1ScoreEvaluator` or `RougeEvaluator` per category code (1-1 through 3-5 mapping to the QA/summarisation/reading-comprehension task types).

## Dataset and licence

The released benchmark contains 2,264 expert-validated questions, broken down in the GitHub README into 11 task types: four QA formats (200/187/224/242 items), two summarisation formats (225/225 items), and five reading-comprehension formats (113/108/221/240/279 items), which sum to the stated total. The source corpus is described as 308,727 cleaned publications reduced to roughly 1.1 billion tokens, with rice as the current crop focus. The GitHub repository carries a GPL-3.0 licence; that covers the code, and a separate licence specifically for the released question data was not independently confirmed, so treat data licensing as unresolved rather than assuming GPL-3.0 applies to the dataset itself. The dataset downloads automatically from ModelScope rather than shipping as a static file in the repository.

## Who publishes it

The paper is by Jie Ying, Zihong Chen, Zhefan Wang, Wanli Jiang, Chenyang Wang, Zhonghang Yuan, Haoyang Su, Huanjun Kong, Fan Yang and Nanqing Dong, accepted at ACL 2025 and posted to arXiv in May 2025. The GitHub organisation is `open-sciencelab`, associated with Shanghai AI Laboratory's InternScience initiative; the same organisation publishes other domain-science benchmarks under that umbrella.

## Lineage

SeedBench is a new 2025 benchmark with no predecessor or successor tracked in this repository. It should not be treated as a variant or subset of AILab-CVC's multimodal SEED-Bench despite the shared name; the two evaluate unrelated capabilities (agricultural domain reasoning versus multimodal image/video comprehension) and come from different publishers.

## Saturation and contamination

The paper's own results show DeepSeek-V3 leading at 68.37% (question-type average, edging out GPT-4's 67.88%) and DeepSeek-V3-671B leading the subcategory average at 63.30% against GPT-4's 62.06%, across 26 evaluated models. Those scores sit well short of a ceiling, and the authors conclude that current LLMs need substantial further development before they are reliable for real seed-science work, which is consistent with an open, unsaturated benchmark. No contamination analysis was found in the sources opened for this page; because the source corpus and question set are both public with no described refresh mechanism, contamination risk could not be established and is marked unknown rather than assumed low.

## How to run it

OpenCompass provides the `seedbench_gen` configuration (`opencompass/configs/datasets/SeedBench/seedbench_gen_5d5ea1.py`), which downloads the dataset from ModelScope on first run and applies per-category evaluators automatically. The GitHub repository also documents a standalone evaluation path through its own scripts. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found for this benchmark.

## Reading the numbers

A strong SeedBench score suggests a model can retrieve gene information, reason about gene function, and support variety-breeding judgement calls for rice specifically; results should not be assumed to generalise to other crops the benchmark does not yet cover. Because the headline number mixes accuracy, macro-F1 and ROUGE-L across different task types, compare models on the same reported metric or task subset rather than on the single aggregate alone. Given the current leaders sit in the high 60s rather than near 100%, treat any near-ceiling claim on this benchmark with suspicion, and check whether "SeedBench" in a report refers to this seed-science benchmark or the unrelated multimodal SEED-Bench before comparing numbers.
