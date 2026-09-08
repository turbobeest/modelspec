---
id: supergpqa
name: SuperGPQA
aliases:
  - Super-GPQA
  - Super GPQA
page_kind: benchmark
category: knowledge
subcategory: graduate-level multidisciplinary multiple-choice QA
status: active
summary: >
  Graduate-level multiple-choice questions across 13 disciplines, 72 fields and 285
  subfields, filtered with a human-LLM pipeline to drop trivial and ambiguous items.
measures: >
  SuperGPQA asks a model to answer a graduate-level question in English by choosing
  among labelled options. Items span far beyond the three sciences in GPQA: the
  authors' taxonomy has 13 disciplines, 72 fields and 285 subfields, with Science,
  Engineering and Medicine holding most of the mass. Annotators rewrite source
  material into multiple-choice form, add distractors, and drop items that experts
  or models mark as trivial or ambiguous. A high score is meant to show graduate
  knowledge and reasoning in long-tail fields, not only in math, physics and CS.
task_format: >
  Single-turn English multiple-choice generation. OpenCompass formats the stem plus
  lettered options (A, B, C, ...) and scores the extracted answer letter against
  `answer_letter`. Default config is zero-shot; a five-shot template also ships.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper reports an average of 9.67 options per question, so chance is far
    below four-option GPQA. No single random-guess or human baseline figure was
    published. The official table reports overall accuracy at sample, subfield,
    field and discipline grain, plus easy/middle/hard splits.
dataset:
  size: 26529
  size_note: >
    Hugging Face datasets-server lists 26,529 rows on the Hub `train` split of
    `m-a-p/SuperGPQA` (file SuperGPQA-all.jsonl). That split is the evaluation
    set, not a training corpus. The GitHub README's per-discipline table sums to
    the same 26,529 (Science 9,838, Engineering 7,892, Medicine 2,755, and ten
    smaller disciplines). The paper title and abstract say "285 Graduate
    Disciplines"; the statistics section instead says 13 disciplines, 72 fields
    and 285 subfields.
  url: https://huggingface.co/datasets/m-a-p/SuperGPQA
  license: ODC-By
  languages:
    - en
  modalities:
    - text
  splits: "single Hub split named train (26,529 evaluation items); no held-out test split"
  public_test_set: true
publisher:
  org: "M-A-P Team, with ByteDance Seed and 2077.AI"
  authors:
    - M-A-P Team
    - Xinrun Du
    - Yifan Yao
    - Kaijing Ma
    - Bingli Wang
    - Tianyu Zheng
    - King Zhu
    - Minghao Liu
  url: https://github.com/SuperGPQA/SuperGPQA
paper:
  title: "SuperGPQA: Scaling LLM Evaluation across 285 Graduate Disciplines"
  arxiv: "2502.14739"
  url: https://arxiv.org/abs/2502.14739
  year: 2025
leaderboard_url: https://huggingface.co/spaces/m-a-p/SuperGPQA
repo_url: https://github.com/SuperGPQA/SuperGPQA
released: "2025-02"
last_updated: "2025-04"
lineage:
  family: ""
  predecessor: gpqa
  successors: []
  variants: []
saturation:
  status: open
  top_score: 61.82
  as_of: "2025-03"
  note: >
    The paper and GitHub README both list DeepSeek-R1 at 61.82% overall sample
    accuracy, with o1-2024-12-17 at 60.24%. Those figures are from the 2025-02/03
    release tables, not a later live scrape of the Hugging Face space.
contamination:
  risk: medium
  note: >
    Questions and answers are public on Hugging Face. The card says the set is
    mostly new but includes transformed items from LawBench, MedMCQA, MedQA,
    MMLU-Pro, MMLU-CF and other named sources, so those fragments may already
    sit in training data. The 2025-02 release is recent relative to GPQA (2023),
    which is why this is not labelled high solely on age.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: supergpqa
  bigbench: ""
  other: >
    OpenCompass loads `m-a-p/SuperGPQA` split `train`. Runnable configs include
    `supergpqa_gen` (zero-shot, abbr `supergpqa`), `supergpqa_cascade_gen_1545c1`
    (per-field cascade), and LLM-judge variants. Official code also supports
    zero-shot and five-shot via `infer/infer.py`. No lm-evaluation-harness or
    HELM task was found under this name.
tags:
  - knowledge
  - multiple-choice
  - graduate-level
  - multidisciplinary
  - english
sources:
  - url: https://arxiv.org/abs/2502.14739
    title: "SuperGPQA: Scaling LLM Evaluation across 285 Graduate Disciplines (arXiv abs)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2502.14739
    title: SuperGPQA HTML full text on ar5iv
    accessed: "2026-09-08"
  - url: https://github.com/SuperGPQA/SuperGPQA
    title: SuperGPQA official GitHub repository
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/SuperGPQA/SuperGPQA/main/README.md
    title: SuperGPQA GitHub README (stats table, DeepSeek-R1 61.82%, ODC-By)
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/m-a-p/SuperGPQA
    title: m-a-p/SuperGPQA dataset card
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/m-a-p/SuperGPQA
    title: m-a-p/SuperGPQA Hugging Face API metadata
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=m-a-p/SuperGPQA
    title: m-a-p/SuperGPQA split info (26,529 train rows)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/supergpqa/supergpqa_gen.py
    title: OpenCompass supergpqa_gen.py (abbr supergpqa, path m-a-p/SuperGPQA)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/supergpqa/supergpqa.py
    title: OpenCompass SuperGPQADataset loader
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/supergpqa/supergpqa_eval.py
    title: OpenCompass SuperGPQA option-letter extractor (A-J)
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-022 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-022"
---

## What it measures

SuperGPQA is an English multiple-choice exam of graduate-level knowledge. The model sees a stem and a list of lettered options, then must pick the correct letter. Coverage is the point: the authors built a taxonomy of 13 disciplines, 72 fields and 285 subfields so that light industry, agriculture, military science and other long-tail areas sit beside math and computer science.

The construction pipeline is a human-LLM filter, not a dump of web quizzes. Crowd annotators rewrite source questions, add distractors, and estimate difficulty. Expert annotators and model failures then drop items that are too easy or too vague. The skill under test is specialised knowledge plus the reasoning needed to use it, not web lookup of a four-option science item.

## How it is scored

The headline metric is accuracy of the predicted option letter. The official tables also average at subfield, field and discipline grain, and they split items into easy, middle and hard. OpenCompass's `SuperGPQAEvaluator` parses a generated completion for a letter in A-J and compares it with `answer_letter`.

There is no published human ceiling. Chance is not 25%: the paper's statistics section gives an average of 9.67 options per question. Default OpenCompass inference is zero-shot generation; the authors' repo also ships a five-shot mode. Cascade and LLM-judge configs exist and will not match the simple letter-match number.

## Dataset and licence

Hugging Face `m-a-p/SuperGPQA` hosts 26,529 items in a split named `train`. That is the evaluation pool. The GitHub per-discipline counts sum to the same total, with Science, Engineering and Medicine about 77% of the set. Answers are public.

The dataset card and GitHub README release the collection under Open Data Commons Attribution (ODC-By). They warn that a minority of items are transformed from other named datasets and that those original licences still apply.

## Who publishes it

The paper is credited to the M-A-P Team, with ByteDance Seed and 2077.AI on the HTML header. arXiv 2502.14739 appeared 20 February 2025; v4 is dated 28 March 2025. Hugging Face `m-a-p/SuperGPQA` last listed a 30 April 2025 revision. Code and inference scripts live at SuperGPQA/SuperGPQA. The authors point to a Hugging Face space as the official leaderboard.

## Lineage

This is a scale-out of [GPQA](gpqa.md), not a GPQA subset. GPQA stays three sciences and a few hundred items; SuperGPQA is tens of thousands of items across a much wider taxonomy. Some SuperGPQA items are rewritten from [MMLU-Pro](mmlu_pro.md) and other public sets named on the card. No successor page exists here.

## Saturation and contamination

The 2025-03 tables still sit near 62% for the best reasoning models they ran, so the set is open on that evidence. The Hugging Face space was not scraped for a later number. Answers are public, and the card admits borrowed fragments from older exams, so contamination risk is medium rather than low.

## How to run it

OpenCompass: `--datasets supergpqa_gen` (task abbr `supergpqa`), loading `m-a-p/SuperGPQA`. Field-cascade and LLM-judge configs live beside it. The authors' `infer/infer.py` is the reference path for the paper tables. No lm-evaluation-harness or HELM task of this name was found. Do not mix zero-shot letter match with cascade or judge scores.

## Reading the numbers

A SuperGPQA score is a wide graduate-knowledge average, not a GPQA Diamond substitute. STEM-heavy mass means a model that is only strong in math can still look decent. Compare it with [GPQA](gpqa.md) and [MMLU-Pro](mmlu_pro.md) rather than treating the three as one number. If two papers both say SuperGPQA, check shot count and whether they used letter match, cascade, or an LLM judge.
