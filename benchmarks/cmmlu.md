---
id: cmmlu
name: "CMMLU (Chinese Massive Multitask Language Understanding)"
aliases:
  - "Chinese Massive Multitask Language Understanding"
page_kind: benchmark
category: knowledge
subcategory: "Chinese multitask knowledge and reasoning exam suite"
status: active
summary: "11,528 multiple-choice questions across 67 subjects, natively authored in Chinese rather than translated, including China-specific subjects such as driving rules and Chinese civil-service topics."
measures: >
  CMMLU tests broad academic, professional and everyday knowledge in a Chinese-language context,
  positioned as a Chinese-native counterpart to MMLU. Each item is a four-option multiple-choice
  question drawn from one of 67 subjects spanning STEM (subjects requiring calculation and formal
  reasoning), humanities and social sciences (subjects requiring recall and applied knowledge), and
  a distinct category of China-specific content -- such as Chinese driving regulations, Chinese food
  culture and Chinese civil-service exam topics -- that a direct translation of MMLU could not cover
  because the underlying facts do not exist in an English-language source.
task_format: >
  Four-option multiple-choice question answering in Chinese, evaluated zero-shot and five-shot;
  answers are scored by parsing a generated answer letter or by comparing option likelihoods.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    25% is the four-option random-guess rate. The paper reports no general human baseline. At
    publication (2023), the authors found "most existing LLMs struggle to achieve an average
    accuracy of 50%," with the random baseline at 25%, evidence the authors read as considerable
    headroom for 2023-era models.
dataset:
  size: 11528
  size_note: >
    11,528 multiple-choice questions across 67 subjects (confirmed from the paper's full text): a
    five-question-per-subject development set (335 questions total) for few-shot prompting, and a
    test set making up the remainder (11,193 questions, "more than 100" per subject as the paper
    states). Over 80% of questions were manually collected from freely available PDF sources via
    OCR, specifically to reduce overlap with material already circulating in plain-text form online.
  url: "https://huggingface.co/datasets/haonan-li/cmmlu"
  license: "Stated two ways: the GitHub repository's README gives CC BY-NC-SA 4.0, while the current Hugging Face dataset card (now hosted under lmlmcat/cmmlu after a rename from haonan-li/cmmlu) states CC BY-NC 4.0, dropping the ShareAlike clause"
  languages:
    - zh
  modalities:
    - text
  splits: "dev (335, 5/subject) / test (11,193)"
  public_test_set: true
publisher:
  org: "Mohamed bin Zayed University of AI (MBZUAI), with co-authors at Shanghai Jiao Tong University and Microsoft Research Asia"
  authors:
    - "Haonan Li"
    - "Yixuan Zhang"
    - "Fajri Koto"
    - "Yifei Yang"
    - "Hai Zhao"
    - "Yeyun Gong"
    - "Nan Duan"
    - "Timothy Baldwin"
  url: "https://github.com/haonan-li/CMMLU"
paper:
  title: "CMMLU: Measuring massive multitask language understanding in Chinese"
  arxiv: "2306.09212"
  url: "https://arxiv.org/abs/2306.09212"
  year: 2023
leaderboard_url: "https://github.com/haonan-li/CMMLU"
repo_url: "https://github.com/haonan-li/CMMLU"
released: "2023-06"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    The GitHub repository's own leaderboard was not read closely enough during this research to cite
    a specific current top score, but the paper's headline finding at release -- that most 2023
    models could not clear 50% average accuracy against a 25% random baseline -- has plausibly been
    surpassed by later frontier and Chinese-focused models; this repository's C-Eval page records
    that a closely related Chinese exam suite reached the low 90s by 2024 among self-submitted
    leaderboard entries, which is offered here as context rather than as a CMMLU-specific figure.
contamination:
  risk: medium
  note: >
    The test set has been fully public with answers since the June 2023 release, with no held-out
    or refreshed portion described by the authors, so any model trained since then could have seen
    it. The authors' own contamination mitigation was applied only at construction time -- sourcing
    most questions from OCR'd PDFs rather than plain text already circulating online, to reduce the
    chance the exact text was already in 2023-era pretraining corpora -- not as an ongoing measure
    against later training runs.
harness:
  lm_eval: "cmmlu"
  inspect_evals: ""
  helm: ""
  opencompass: "cmmlu"
  bigbench: ""
  other: ""
tags:
  - knowledge
  - multiple-choice
  - chinese
  - multitask
  - exam
sources:
  - url: "https://arxiv.org/abs/2306.09212"
    title: "CMMLU: Measuring massive multitask language understanding in Chinese"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/abs/2306.09212"
    title: "CMMLU paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/haonan-li/CMMLU"
    title: "haonan-li/CMMLU GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/haonan-li/cmmlu"
    title: "cmmlu dataset metadata (redirects to lmlmcat/cmmlu), Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/cmmlu"
    title: "lm-evaluation-harness cmmlu tasks directory"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/cmmlu"
    title: "OpenCompass cmmlu dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
---

## What it measures

CMMLU tests broad academic, professional and everyday knowledge in a Chinese-language context, positioned by its authors as a Chinese-native counterpart to MMLU rather than a translation of it. Each item is a four-option multiple-choice question drawn from one of 67 subjects spanning STEM subjects that require calculation and formal reasoning, humanities and social-science subjects that require recall and applied knowledge, and a distinct set of China-specific subjects -- Chinese driving regulations, Chinese food culture and Chinese civil-service exam topics among them -- that an English-to-Chinese translation of an existing benchmark could not produce, because the underlying facts and conventions do not exist in an English-language source to translate from.

## How it is scored

Every item is four-option multiple choice, so random guessing scores 25%. The authors report zero-shot and five-shot accuracy and found that, at release in 2023, most evaluated models could not average 50% accuracy even with additional prompting techniques, against the 25% floor -- evidence they read as a wide gap still to close. Answers are scored either by parsing a generated answer letter or by comparing the model's likelihood across the four options, matching the approach MMLU and C-Eval both use.

## Dataset and licence

CMMLU totals 11,528 multiple-choice questions across 67 subjects: a five-question-per-subject development set (335 questions) for few-shot prompting, and a test set of the remainder (11,193 questions, more than 100 per subject on average). The authors report that over 80% of questions were manually collected from freely available PDF sources via OCR rather than from plain text, specifically to reduce the chance the exact wording was already circulating in a form easy for a model to have memorised. Quality checks sampled 5% of questions per subject for verification against online sources, from which the authors estimate roughly 2% label noise. The licence is stated two different ways across the project's own pages: the GitHub repository's README gives CC BY-NC-SA 4.0, while the current Hugging Face dataset card, now hosted under `lmlmcat/cmmlu` after the original `haonan-li/cmmlu` repository was renamed, states CC BY-NC 4.0 without the ShareAlike clause. This page records both readings rather than picking one.

## Who publishes it

CMMLU comes from Haonan Li, Yixuan Zhang and Fajri Koto (MBZUAI), Yifei Yang and Hai Zhao (Shanghai Jiao Tong University), Yeyun Gong and Nan Duan (Microsoft Research Asia), and Timothy Baldwin (MBZUAI and the University of Melbourne), published on arXiv in June 2023 and revised in January 2024. The reference repository sits under `haonan-li` on GitHub, and the dataset is mirrored on Hugging Face (now under the `lmlmcat` organisation). The repository's own README hosts a leaderboard of more than 40 evaluated models rather than a separately hosted site.

## Lineage

CMMLU has no predecessor or successor tracked in this repository. It belongs to the same cluster of 2023-era Chinese evaluation suites as C-Eval, also in this repository -- C-Eval's page notes CMMLU as a related, contemporaneous benchmark -- and CMB, a domain-specific medical benchmark in this same family of native-Chinese suites. C-Eval's test set was held out via a submission portal until its full public release in July 2025, a contamination-management approach CMMLU's authors did not adopt: CMMLU published its test set with answers from the start in 2023.

## Saturation and contamination

This page could not confirm a specific current top score for CMMLU from a maintained leaderboard, so saturation status is recorded as "watch" rather than asserted. Context from this repository's C-Eval page is relevant without being a CMMLU-specific finding: C-Eval, a closely related Chinese exam suite from the same period, reached leaderboard scores in the low 90s by late 2024 among self-submitted entries, suggesting the broader family of Chinese multi-subject exam benchmarks is under real pressure from newer models even where CMMLU-specific numbers were not available here. Contamination risk sits at medium to high: the test set has been fully public with answers since June 2023, with no held-out portion or refresh described by the authors, so models trained since then could have encountered it directly.

## How to run it

lm-evaluation-harness implements CMMLU as a 67-subject task group named `cmmlu` (one YAML file per subject, aggregated), following MMLU's original evaluation methodology. OpenCompass ships several `cmmlu` configuration variants, including perplexity-based scoring (`cmmlu_ppl` and revisions), generation-based scoring (`cmmlu_gen` and revisions), zero-shot chain-of-thought variants, and an LLM-judge variant, none of which are directly comparable to one another because they differ in prompt format and scoring method. Check which specific configuration a reported number used before comparing it to another paper's CMMLU score.

## Reading the numbers

A high CMMLU score indicates strong performance on Chinese-language, exam-style knowledge questions across a very broad subject range, including China-specific civic and cultural content that general multilingual benchmarks skip entirely -- but it says little about open-ended Chinese generation, dialogue quality or reasoning outside multiple-choice format. Because the test set has been public with answers since 2023, treat an unusually high score from a model with an unclear training cutoff with some caution, and corroborate it against a second Chinese benchmark, such as C-Eval or CMB, before trusting it as a general signal of Chinese-language capability. Also check which harness configuration produced the number, since OpenCompass alone ships perplexity-based, generation-based and LLM-judge variants that are not interchangeable.
