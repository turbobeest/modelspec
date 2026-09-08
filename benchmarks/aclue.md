---
id: aclue
name: "ACLUE (Ancient Chinese Language Understanding Evaluation)"
aliases:
  - "Ancient Chinese Language Understanding Evaluation"
page_kind: family
category: knowledge
subcategory: "fifteen-task ancient Chinese multiple-choice suite (lexical, syntactic, semantic, inference, knowledge)"
status: active
summary: "Fifteen four-option ancient-Chinese tasks spanning lexicon, syntax, poetry, medicine and culture; 2023 zero-shot scores sat only a little above chance."
measures: >
  ACLUE tests whether a language model can read classical Chinese, not modern Mandarin.
  It bundles 15 four-option multiple-choice tasks that the authors group as lexical
  (polysemy, homographic/通假 characters, named entities), syntactic (sentence
  segmentation), semantic (couplets, poetry context), inference (poetry quality,
  reading comprehension, poetry appreciation, poetry sentiment), and knowledge
  (basic ancient Chinese, traditional culture, medical texts, literature, phonetics).
  Items are drawn from classical corpora and from existing tests, and they span
  roughly 2070 BCE to 1368 CE. The suite is an ancient-language counterpart to
  modern-Chinese exams such as CMMLU, not a clone of CLUE.
task_format: >
  Four-option multiple-choice in ancient or classical Chinese, one correct letter.
  lm-evaluation-harness scores log-likelihood over A/B/C/D. The original paper
  reports zero-shot accuracy averaged across tasks.
metric:
  name: "accuracy (per-task, then mean across the 15 tasks); lm_eval also reports size-weighted acc and acc_norm"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    Every item has four options and one key, so chance is 25%. The GitHub English
    README's zero-shot table lists Random at 25.00 overall. The 2023 paper's best
    model, ChatGLM2, averaged 37.4%, which the authors read as only a little above
    chance. No human baseline is given.
dataset:
  size: 4967
  size_note: >
    Sum of the Hugging Face card's per-task "Total Q." column across all 15 tasks
    (seven generated tasks at 500 items, then 406, 211, 160, 136, 103, 249, 101,
    101). The paper says each task has 100 to 500 questions; 8 tasks are generated
    from corpora, 5 collected from free tests, and 2 sourced from other work
    (reading comprehension from AGIEval; basic ancient Chinese from CMMLU). The
    appendix table labels those last seven as "collected". Each task also has a
    5-question development split used for few-shot prompts. Whether
    those five rows are inside the 4,967 figure is not stated on the card. The HF
    YAML size_categories tag "1M<n<10M" does not match these counts and is ignored.
  url: "https://huggingface.co/datasets/tyouisen/aclue"
  license: CC-BY-NC-SA-4.0
  languages:
    - zh
  modalities:
    - text
  splits: "15 configs, each with a 5-item development split and a test split; lm_eval scores the test split and samples few-shot from dev"
  public_test_set: true
publisher:
  org: "Mohamed bin Zayed University of Artificial Intelligence (MBZUAI)"
  authors:
    - "Yixuan Zhang"
    - "Haonan Li"
  url: "https://github.com/isen-zhang/ACLUE"
paper:
  title: "Can Large Language Model Comprehend Ancient Chinese? A Preliminary Test on ACLUE"
  arxiv: "2310.09550"
  url: "https://arxiv.org/abs/2310.09550"
  year: 2023
leaderboard_url: "https://github.com/isen-zhang/ACLUE"
repo_url: "https://github.com/isen-zhang/ACLUE"
released: "2023-09"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 37.34
  as_of: "2023-09"
  note: >
    The publisher's GitHub zero-shot table, matching the paper's ChatGLM2 figure of
    about 37.4%, tops out at 37.34 for ChatGLM2-6B, with ChatGPT at 36.82. That is
    a 2023 snapshot on then-current models, not a 2026 frontier reading. No later
    official table was found, so current saturation is unknown.
contamination:
  risk: high
  note: >
    Development and test items, including answers, are public on GitHub and Hugging
    Face. Eight tasks are generated from public classical corpora. No contamination
    study was found. The HF card YAML names CC-BY-NC-4.0 while the card body and
    GitHub README name CC BY-NC-SA 4.0 for the dataset; this page follows the
    ShareAlike text.
harness:
  lm_eval: aclue
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - ancient-chinese
  - multiple-choice
  - knowledge
  - chinese
  - family
sources:
  - url: "https://arxiv.org/abs/2310.09550"
    title: "ACLUE paper on arXiv"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2310.09550"
    title: "ACLUE paper full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2023.alp-1.9/"
    title: "ACL Anthology page for the ALP 2023 paper"
    accessed: "2026-09-08"
  - url: "https://github.com/isen-zhang/ACLUE"
    title: "ACLUE GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/isen-zhang/ACLUE/main/README_EN.md"
    title: "ACLUE English README (zero-shot table and licence)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/tyouisen/aclue"
    title: "tyouisen/aclue dataset card"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/aclue/README.md"
    title: "lm-evaluation-harness ACLUE task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/aclue/_aclue.yaml"
    title: "lm_eval group yaml for aclue"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-024 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-024"
---

## What it measures

ACLUE asks whether a model understands ancient Chinese. Each item is a four-option question about classical text: word sense, 通假 characters, named entities, unpunctuated sentence cuts, couplets, poetry, medical prose, literature, phonetics, or general 国学. The time span in the paper and dataset card is the Xia dynasty through the Ming dynasty.

The suite is not CLUE. CLUE is modern Chinese NLU (this repository's `clue` family). It is also not CMMLU, which tests modern Chinese school and professional knowledge. ACLUE is a separate 15-task exam aimed at classical language.

## How it is scored

The original paper reports zero-shot accuracy, averaged over the 15 tasks, with chance at 25%. Table 1 lists ChatGLM2 at 37.4% and ChatGPT at 36.9%. The GitHub English README's zero-shot table instead lists ChatGLM2-6B at 37.34 and ChatGPT at 36.82. lm-evaluation-harness exposes a group `aclue` that runs all 15 subjects as log-likelihood multiple choice and aggregates `acc` and `acc_norm`, weighted by size. Few-shot uses the five-item development split (`sampler: first_n`). A generative letter-picking protocol and this likelihood protocol are not interchangeable.

## Dataset and licence

The Hugging Face mirror `tyouisen/aclue` is the copy lm_eval loads. Its per-task Total Q. column sums to 4,967 items. Generated lexical and poetry tasks sit at 500 items; collected knowledge tasks are smaller (phonetics and reading comprehension 101 each). Each task has a five-question development split. Test labels are in the public files.

The GitHub project is MIT. The dataset is stated as CC BY-NC-SA 4.0 in the GitHub README and in the Hugging Face card body. The Hugging Face YAML header instead says `cc-by-nc-4.0`. This page records CC-BY-NC-SA-4.0 and treats the YAML tag as a conflict, not a second licence.

## Who publishes it

Yixuan Zhang and Haonan Li, with Li's affiliation given as MBZUAI on the paper. The work appeared at the Ancient Language Processing Workshop (Varna, September 2023) and as arXiv:2310.09550. Code and data live at `isen-zhang/ACLUE`. The only leaderboard found is the static zero-shot table in that README.

## Lineage

ACLUE is a standalone ancient-Chinese suite. It is not a subset of `clue`, `cmmlu`, or `ceval`. The authors compare modern-Chinese scores on AGIEval and CMMLU with these ancient-Chinese scores to argue that contemporary Chinese skill does not transfer. lm_eval's group name `aclue` is the runnable id; it is unrelated to CLUE.

## Saturation and contamination

The published 2023 table is close to chance (best 37.34%). Whether current Chinese-capable models have since saturated the set was not established from sources opened here. Contamination risk is high: items and keys are public, and several tasks are generated from public classical corpora. Treat a strong 2026 score as possibly mixed with training-data overlap unless the reporter used a private hold-out, which ACLUE does not provide.

## How to run it

In lm-evaluation-harness, `aclue` runs all 15 subjects; `aclue_<subject>` runs one (for example `aclue_ancient_chinese_culture`). Prompts are Chinese and ask for the option letter after `答案：`. The original repository's `src` and `script` directories hold the authors' own model runners. Do not compare a size-weighted lm_eval mean with an unweighted paper mean without saying so.

## Reading the numbers

A score near 25% means the model is not reading classical Chinese above guessing. A 2023-era 37% meant a small edge, not mastery. A much higher modern score would show some classical-Chinese competence, but not that the model can translate, punctuate, or historically reason outside these 15 templates. Read it beside a modern-Chinese suite (`cmmlu`, `clue`) and do not fold it into a CLUE composite.
