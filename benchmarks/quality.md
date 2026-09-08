---
id: quality
name: "QuALITY"
aliases:
  - "QuALITY: Question Answering with Long Input Texts, Yes!"
  - "QUALITY"
page_kind: benchmark
category: long-context
subcategory: "long-document English multiple-choice QA (~5k-token passages, four options)"
status: active
summary: "Multiple-choice QA over English passages averaging about 5,000 tokens; writers read the full article, and a hard subset beats speed-limited annotators."
measures: >
  QuALITY (Question Answering with Long Input Texts, Yes!) gives a model an English article
  of about 5,000 tokens and a four-option question written by a contributor who read the
  whole passage. Untimed validators must agree the item is answerable; a hard subset is the
  slice where speed-limited annotators mostly fail. The skill is long-document comprehension
  that skimming and lexical overlap do not solve. OpenCompass, the census harness for this
  id, runs the HTML-stripped development split as a generation multiple-choice task, not the
  hidden test set used by the NYU leaderboard.
task_format: >
  Four-way multiple choice (A–D) over a long English article plus a question. Official scoring
  is accuracy on the held-out test set. OpenCompass is zero-shot generation with
  first_option_postprocess over ABCD.
metric:
  name: "accuracy (all); easy_acc and hard_acc also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 93.5
  baseline_note: >
    Four options, so chance is 25%. The paper's untimed human accuracy is 93.5% on the full
    set and 89.1% on QuALITY-hard, from a majority of annotators versus gold. The NYU
    leaderboard restates those human figures and also reports SAT-style score. OpenCompass
    reports easy_acc, hard_acc and all_acc on the public dev split.
dataset:
  size: 6737
  size_note: >
    Paper Table 3: 6,737 validated questions over 381 articles (train 2,523 / 150 articles,
    dev 2,086 / 115, test 2,128 / 116). Hard subset 3,360 questions (49.9%). Test labels are
    not public. OpenCompass loads QuALITY.v1.0.1.htmlstripped.dev, so an OpenCompass run is
    the 2,086-question development split. Third-party Hugging Face set emozilla/quality has
    2,523 train and 2,086 validation rows and no test split.
  url: "https://github.com/nyu-mll/quality"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "train 2523 / dev 2086 / test 2128 questions; test answers held out"
  public_test_set: false
publisher:
  org: "New York University (NYU-MLL) and collaborators"
  authors:
    - "Richard Yuanzhe Pang"
    - "Alicia Parrish"
    - "Nitish Joshi"
    - "Nikita Nangia"
    - "Jason Phang"
    - "Angelica Chen"
    - "Vishakh Padmakumar"
    - "Johnny Ma"
    - "Jana Thompson"
    - "He He"
    - "Samuel R. Bowman"
  url: "https://nyu-mll.github.io/quality/"
paper:
  title: "QuALITY: Question Answering with Long Input Texts, Yes!"
  arxiv: "2112.08608"
  url: "https://arxiv.org/abs/2112.08608"
  year: 2022
leaderboard_url: "https://nyu-mll.github.io/quality/"
repo_url: "https://github.com/nyu-mll/quality"
released: "2022-06"
last_updated: "2025-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 88.0
  as_of: "2025-01"
  note: >
    NYU leaderboard (last updated January 2025) ranks by full test-set accuracy. The leading
    entry is 88.0% / 81.9% hard (clustering plus Qwen2.5-7B decomposition, DeepSeek-V3 as
    the chooser, January 2025), still below the 93.5% / 89.1% human figures. RAPTOR+GPT-4
    is 82.6% (June 2023). These retrieval systems are not a single-forward-pass long-context
    score. OpenCompass's Qwen1.5-72B-Chat example is 68.84 all_acc on the public dev split.
contamination:
  risk: medium
  note: >
    Train and development questions and answers are public (v1.0.1 on GitHub, CC BY 4.0).
    Test labels remain on the leaderboard. Articles are drawn from Gutenberg, Slate/OANC and
    other long CC-BY sources, which are common in pretraining. The official test set is held
    out; OpenCompass numbers are not, because they use htmlstripped.dev.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "QuALITY (abbr QuALITY; dataset class QuALITYDataset; config QuALITY_gen_c407cb.py; path ./data/QuALITY/QuALITY.v1.0.1.htmlstripped.dev)"
  bigbench: ""
  other: >
    Official evaluation is the NYU leaderboard test set. L-Eval reuses a 15-row QuALITY
    slice (see leval.md). SCROLLS also reports QuALITY. No lm-eval task name was confirmed
    here. Third-party Hugging Face copy: emozilla/quality (train/validation only; card has
    no licence tag).
tags:
  - long-context
  - multiple-choice
  - reading-comprehension
  - english
sources:
  - url: "https://arxiv.org/abs/2112.08608"
    title: "QuALITY paper abs (arXiv:2112.08608, NAACL 2022)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2112.08608"
    title: "QuALITY paper HTML: 6737 questions, 381 articles, human 93.5%/89.1%"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/nyu-mll/quality/main/README.md"
    title: "nyu-mll/quality README (v1.0.1, hard definition, held-out test)"
    accessed: "2026-09-08"
  - url: "https://nyu-mll.github.io/quality/"
    title: "QuALITY leaderboard: CC BY 4.0, last updated January 2025, top 88.0%"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.naacl-main.391/"
    title: "ACL Anthology NAACL 2022 camera-ready"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/QuALITY/QuALITY.md"
    title: "OpenCompass QuALITY.md (dev-set Qwen1.5 example scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/QuALITY/QuALITY_gen_c407cb.py"
    title: "OpenCompass QuALITY zero-shot gen config on htmlstripped.dev"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/QuALITY.py"
    title: "QuALITYDataset and QuALITYEvaluator (easy/hard/all accuracy)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/emozilla/quality"
    title: "emozilla/quality API: 2523 train + 2086 validation, no licence tag"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-020 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-020"
---

## What it measures

QuALITY is long-document multiple-choice reading in English. Each item is an article of a few thousand tokens, a question, and four answers. Writers read the full text; they do not write from a summary. Speed-limited annotators fail more than half of the hard subset, so keyword search is not enough. Passages come from Project Gutenberg, Slate, and similar long sources. The average context is 5,159 tokens in the paper, far longer than RACE or CosmosQA.

This page is the NYU dataset. It is not [artificial_analysis_quality_index](artificial_analysis_quality_index.md). [L-Eval](leval.md) reuses a 15-example QuALITY slice and is a different suite.

## How it is scored

Official ranking is accuracy on the hidden test set (2,128 questions). The site also reports a SAT-style score that penalises wrong answers. Humans sit at 93.5% full / 89.1% hard. Random choice is 25%. OpenCompass instead scores the public development split: it generates a letter, maps it with `first_option_postprocess`, and reports easy_acc, hard_acc and all_acc. In the OpenCompass evaluator, `hard_acc` is implemented as `sum(hard) / len(easy) * 100`, so the hard number is not a clean hard-subset mean unless the easy and hard counts match. Do not mix an OpenCompass all_acc with a NYU test accuracy.

## Dataset and licence

The paper counts 6,737 validated questions on 381 articles after dropping items that failed untimed checks (88.4% of 7,620 written questions). Splits are train 2,523, dev 2,086, test 2,128. About half are hard. The leaderboard states a CC BY 4.0 licence for the dataset; source articles keep their own licences, listed per line. OpenCompass reads `QuALITY.v1.0.1.htmlstripped.dev`. Test labels are not in the zip.

## Who publishes it

NYU-MLL authors led by Pang, Parrish and Joshi, with Bowman and He among the co-authors. The paper is NAACL 2022 (arXiv 16 December 2021, v2 11 May 2022). Data v1.0.1 is dated June 2022. NYU still hosts the leaderboard (last updated January 2025).

## Lineage

Standalone. SCROLLS and [L-Eval](leval.md) reuse QuALITY items; those pages are not this id. [LongBench](longbench.md) and [InfiniteBench](infinitebench.md) are later long-context suites, not formal successors. No family page.

## Saturation and contamination

The January 2025 leaderboard top is 88.0% test accuracy for a retrieval-and-decomposition stack using DeepSeek-V3, still short of 93.5% human. Raw long-context chat models on the same table sit lower (GPT-3.5-16k 74.7% in January 2024). Train and dev answers have been public since 2022, so contamination of those splits is plausible. The hidden test set is the cleaner number; OpenCompass is not that number.

## How to run it

Download v1.0.1 from nyu-mll/quality and submit test predictions to the NYU site. OpenCompass: `QuALITY_datasets` from `configs/datasets/QuALITY/QuALITY_gen.py`, local path `./data/QuALITY/QuALITY.v1.0.1.htmlstripped.dev`. No lm-eval or inspect_evals task name was confirmed here. A score without split (test vs htmlstripped.dev) is not comparable.

## Reading the numbers

A strong NYU test score means the system can answer writer-authored questions about a ~5k-token story, often with retrieval rather than a single window. It does not measure book-length context, multimodal reading, or open-ended summary quality. Check whether the reporter used test or dev, all or hard, and a full-document prompt versus RAPTOR-style chunks. Place it next to [L-Eval](leval.md) or [LongBench](longbench.md) only after matching protocol.
