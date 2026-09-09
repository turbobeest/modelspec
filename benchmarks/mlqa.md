---
id: mlqa
name: MLQA
aliases:
  - MultiLingual Question Answering
  - MLQA (MultiLingual Question Answering)
page_kind: benchmark
category: knowledge
subcategory: multilingual extractive question answering
status: active
summary: Parallel extractive question answering in seven languages, testing whether a model can recover an answer span from Wikipedia even when the question is in a different language.
measures: >
  MLQA (MultiLingual Question Answering) is an evaluation-only extractive QA set. The model
  receives a Wikipedia paragraph and a question, and must return the answer as a span in the
  paragraph's language. Seven languages are covered: English, Arabic, German, Spanish, Hindi,
  Vietnamese and Simplified Chinese. Instances are multi-way parallel, on average across four
  languages, so the same question can be asked against a context in another language. That is the
  generalised transfer setup. It is a reading-span task in SQuAD format, not a translation
  benchmark, and not the medical acronyms MEDIQA or MedQA.
task_format: >
  Extractive span selection in SQuAD JSON. lm-evaluation-harness instead generates the answer
  string from a "Context / Question / Answer" prompt and scores it with the official MLQA
  normalisation (language-specific article stripping and Chinese mixed segmentation).
metric:
  name: "token F1 and exact match, using the official MLQA evaluation script"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No human baseline is reported in the paper or the official README. The paper's English
    BERT-Large in-language result is 80.2 F1 / 67.4 EM on the XLT test, which is a 2019-2020 model
    result, not a human ceiling. XLM was the strongest zero-shot transfer model in that table.
dataset:
  size: 12738
  size_note: >
    The paper and official README give 12,738 English instances (1,148 dev / 11,590 test) and
    5,029-6,006 instances per target language. Hugging Face `facebook/mlqa` config `mlqa.en.en`
    matches 1,148 validation / 11,590 test. Same-language test sizes: de 4,517, es 5,253, ar 5,335,
    zh 5,137, vi 5,495, hi 4,918. The GitHub README table prints Spanish test as 5,254; the paper
    Table 2 and the Hugging Face card both have 5,253. Cross-language configs reuse those instance
    counts where question and context languages differ.
  url: https://github.com/facebookresearch/MLQA
  license: CC-BY-SA-3.0
  languages:
    - en
    - ar
    - de
    - es
    - hi
    - vi
    - zh
  modalities:
    - text
  splits: "Development and test only; no MLQA training split. English 1,148 / 11,590. Target-language counts in the size note."
  public_test_set: true
publisher:
  org: Facebook AI Research
  authors:
    - Patrick Lewis
    - Barlas Oğuz
    - Ruty Rinott
    - Sebastian Riedel
    - Holger Schwenk
  url: https://github.com/facebookresearch/MLQA
paper:
  title: "MLQA: Evaluating Cross-lingual Extractive Question Answering"
  arxiv: "1910.07475"
  url: https://arxiv.org/abs/1910.07475
  year: 2020
leaderboard_url: ""
repo_url: https://github.com/facebookresearch/MLQA
released: "2019-10"
last_updated: ""
lineage:
  family: ""
  predecessor: squad
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The original XLT table tops out at 80.2 F1 for English BERT-Large and 68.0 F1 for the best
    non-English XLM transfer (Spanish). No later official MLQA leaderboard was found during this
    research, so current saturation is unknown. XTREME and XGLUE later bundled MLQA as one task.
contamination:
  risk: high
  note: >
    Contexts are Wikipedia, questions and answers have been downloadable since 2019, and the
    authors themselves warn that the test set should be touched as little as possible. The
    development split is the intended tuning set.
harness:
  lm_eval: mlqa
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness has no group; tag `mlqa` runs all 49 tasks named
    `mlqa_<context-lang>_<question-lang>` (for example `mlqa_en_en`, `mlqa_ar_es`). Dataset path
    facebook/mlqa, config `mlqa.<ctx>.<q>`. Metrics are exact_match and f1 via a port of
    mlqa_evaluation_v1.py (Arabic article stripping was fixed in harness v0.1).
tags:
  - multilingual
  - extractive-qa
  - wikipedia
  - cross-lingual
sources:
  - url: https://arxiv.org/abs/1910.07475
    title: "MLQA: Evaluating Cross-lingual Extractive Question Answering"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/1910.07475
    title: "MLQA HTML full text on ar5iv"
    accessed: "2026-09-08"
  - url: https://github.com/facebookresearch/MLQA
    title: "facebookresearch/MLQA GitHub repository"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/facebook/mlqa
    title: "facebook/mlqa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/facebook/mlqa
    title: "facebook/mlqa Hugging Face API"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mlqa/README.md
    title: "mlqa task README, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mlqa/mlqa_common_yaml
    title: "mlqa common task template, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/facebookresearch/MLQA/main/mlqa_evaluation_v1.py
    title: "Official MLQA evaluation script"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch 7 pilot (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, pilot-review"
---

## What it measures

MLQA is a seven-language extractive QA eval. Given a Wikipedia paragraph and a question, the model
must return the answering span in the paragraph. Languages are English, Arabic, German, Spanish,
Hindi, Vietnamese and Simplified Chinese. Many items are parallel, so you can keep the English
question and swap in an Arabic paragraph, or the reverse. That is the paper's generalised
cross-lingual transfer (G-XLT) setup. Same-language pairs are the simpler XLT setup.

Questions were written in English on aligned sentences, then professionally translated. Contexts
were not translated for the main set; they are naturally occurring Wikipedia. It is SQuAD-format
span finding, not open-ended generation and not machine translation as a task.

## How it is scored

The official script reports token F1 and exact match after language-specific normalisation: strip
articles where the language has them, strip Unicode punctuation, and use mixed segmentation for
Chinese. English BERT-Large in the paper reaches 80.2 F1 / 67.4 EM. XLM leads most transfer
columns in that table (for example 68.0 F1 Spanish). lm-evaluation-harness generates the answer
string and applies a port of that script; a 2023-era harness changelog fixes Arabic article
stripping, which affects all `mlqa_ar_*` scores. No human baseline is in the paper.

## Dataset and licence

English has 12,738 instances (1,148 / 11,590). Each other language has about 5-6k. There is no
MLQA training split; the paper trains on SQuAD 1.1 and uses MLQA-en as development for zero-shot
work. The official README licences the dataset as CC BY-SA 3.0 because it comes from Wikipedia.
The repo LICENSE file is CC BY-NC 4.0 and applies to the code, per that README. Hugging Face
`facebook/mlqa` lists CC-BY-SA-3.0 for the data. Answers are public. The GitHub README's Spanish
test count is 5,254; the paper and Hugging Face card say 5,253.

## Who publishes it

Patrick Lewis, Barlas Oğuz, Ruty Rinott, Sebastian Riedel and Holger Schwenk at Facebook AI
Research, with Lewis also tied to UCL NLP on the project page. arXiv v1 is 16 October 2019; the
ACL 2020 camera-ready is v3 (May 2020). Data and the eval script are in facebookresearch/MLQA.

## Lineage

Built as a cross-lingual companion to [squad](squad.md). [tydiqa](tydiqa.md) is a later
typologically diverse QA set that was collected in-language rather than translated from English;
the TyDi QA page in this repository already contrasts that choice with MLQA. XQuAD, released
around the same time, translates 1,190 SQuAD items into ten languages and is not this id.

## Saturation and contamination

Current top scores were not established from a live leaderboard. The 2020 table already showed a
large English-versus-transfer gap. Contamination risk is high: Wikipedia plus a public 2019 test
set. The authors ask people to tune on development data and leave the test set alone.

## How to run it

Official: `mlqa_evaluation_v1.py gold.json predictions.json <answer-lang>`. In lm-evaluation-harness,
tag `mlqa` or a pair such as `mlqa_hi_en` (context Hindi, question English in the harness naming).
State the language pair, whether the setup is XLT or G-XLT, and whether SQuAD-style span scoring
or harness generation was used.

## Reading the numbers

A high `mlqa_en_en` F1 is close to SQuAD-style English reading. A high `mlqa_ar_ar` or
`mlqa_hi_en` F1 is the actual cross-lingual claim. Macro-averaging pairs that include English with
pairs that do not will hide that gap. This is not MedQA, not MEDIQA, and not a licence to claim
open-domain multilingual search.
