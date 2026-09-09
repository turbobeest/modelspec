---
id: svamp
name: SVAMP
aliases:
  - Simple Variations on Arithmetic Math word Problems
page_kind: benchmark
category: math
subcategory: grade-school arithmetic word-problem robustness
status: active
summary: >
  A 1,000-item challenge set of grade-school arithmetic word problems made by
  applying question, reasoning and structure variations to existing MWPs.
measures: >
  SVAMP (Simple Variations on Arithmetic Math word Problems) tests whether a
  solver actually reads a short English word problem, or just matches shallow
  templates. Each item is a one-unknown arithmetic story at about grade four or
  below. The authors built it by taking seeds from ASDiv-A and MAWPS and applying
  three kinds of edit: change the question, change the reasoning, or change the
  surface structure. A model that ignored the question on the old sets still
  scored well; SVAMP is meant to stop that shortcut.
task_format: >
  Free-response English word problem. The model must output a numeric answer.
  OpenCompass concatenates the `Body` and `Question` fields, prompts with four
  hardcoded chain-of-thought examples, and extracts the final number with the
  GSM8K postprocessor.
metric:
  name: accuracy (exact-match final number)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or human baseline is published. The NAACL 2021 paper reports that
    then-SOTA tree and graph decoders drop sharply relative to MAWPS and ASDiv-A.
    OpenCompass reuses Gsm8kEvaluator after casting each gold answer to int.
dataset:
  size: 1000
  size_note: >
    The official `SVAMP.json` in arkilpatel/SVAMP contains 1,000 challenge items
    and is the evaluation set. Hugging Face `ChilleD/SVAMP` is a third-party
    mirror of the same 1,000 rows split 700/300 train/test. OpenCompass's
    `SVAMPDataset` reads a JSONL of Body+Question+Answer with no split filter.
  url: https://github.com/arkilpatel/SVAMP
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "official release is one 1,000-item eval set; ChilleD/SVAMP adds train 700 / test 300"
  public_test_set: true
publisher:
  org: ""
  authors:
    - Arkil Patel
    - Satwik Bhattamishra
    - Navin Goyal
  url: https://github.com/arkilpatel/SVAMP
paper:
  title: "Are NLP Models really able to Solve Simple Math Word Problems?"
  arxiv: "2103.07191"
  url: https://arxiv.org/abs/2103.07191
  year: 2021
leaderboard_url: ""
repo_url: https://github.com/arkilpatel/SVAMP
released: "2021-03"
last_updated: "2021-04"
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
    No current public leaderboard for SVAMP was opened. The 2021 paper showed
    then-SOTA models well below their MAWPS/ASDiv-A scores. Grade-school
    one-unknown arithmetic has since become easy for frontier models, but that
    later ease was not read from a sourced SVAMP table here.
contamination:
  risk: high
  note: >
    The 1,000 items and answers have been public on GitHub since March 2021 and
    mirrored on Hugging Face. They are short template-like stories, so
    memorisation and leakage into pretraining are plausible.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: svamp
  bigbench: ""
  other: >
    OpenCompass config `svamp_gen` (hash `svamp_gen_fb25e4`) uses abbr `svamp`,
    path `opencompass/SVAMP`, four in-prompt CoT examples, `Gsm8kEvaluator`, and
    `gsm8k_postprocess`. No lm-evaluation-harness task directory named svamp was
    found on the harness main branch listing.
tags:
  - math
  - word-problems
  - arithmetic
  - robustness
  - english
sources:
  - url: https://arxiv.org/abs/2103.07191
    title: "Are NLP Models really able to Solve Simple Math Word Problems? (arXiv abs)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2103.07191
    title: SVAMP paper HTML on ar5iv
    accessed: "2026-09-08"
  - url: https://github.com/arkilpatel/SVAMP
    title: arkilpatel/SVAMP repository
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/arkilpatel/SVAMP/main/README.md
    title: SVAMP README (1,000-item challenge set, MIT badge, NAACL 2021)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/arkilpatel/SVAMP/main/LICENSE
    title: SVAMP MIT LICENSE
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/arkilpatel/SVAMP/main/SVAMP.json
    title: Official SVAMP.json (1,000 items counted)
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ChilleD/SVAMP
    title: ChilleD/SVAMP third-party Hub mirror
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=ChilleD/SVAMP
    title: ChilleD/SVAMP split info (700 train / 300 test)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SVAMP/svamp_gen_fb25e4.py
    title: OpenCompass svamp_gen_fb25e4.py (abbr svamp, 4-shot CoT)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/svamp.py
    title: OpenCompass SVAMPDataset loader
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-022 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-022"
---

## What it measures

SVAMP is a stress test for elementary English math word problems. Each item is a short story plus a question about one unknown quantity, using only arithmetic. The authors showed that solvers of MAWPS and ASDiv-A could often ignore the question, or ignore word order, and still look strong. SVAMP applies controlled edits so that those shortcuts fail.

The three edit types are question sensitivity, reasoning ability, and structural invariance. A typical change swaps who received the objects, or rewrites the story without changing the math. The skill under test is reading the actual question, not recalling a template from ASDiv-A.

## How it is scored

The original paper scores equation or value accuracy of classic seq2seq and tree decoders. Current LLM harnesses score the final number. OpenCompass concatenates body and question, prepends four worked examples, and runs `Gsm8kEvaluator` after `gsm8k_postprocess`. Gold answers are cast to `int`, so a non-integer gold would not match that loader.

There is no published human or chance baseline. A 2021 Graph2Tree number is not comparable to a 2026 chain-of-thought LLM run.

## Dataset and licence

The official file `SVAMP.json` holds 1,000 items (`ID`, `Body`, `Question`, `Equation`, `Answer`, `Type`). The README treats that file as the full challenge set. `ChilleD/SVAMP` on Hugging Face is a later mirror that splits the same 1,000 rows into 700 train and 300 test. Both the GitHub repo and the Hub card state MIT. Answers are public.

## Who publishes it

Arkil Patel, Satwik Bhattamishra and Navin Goyal. arXiv 2103.07191 appeared 12 March 2021 (v2 15 April 2021) and was published at NAACL 2021. The code and data remain at arkilpatel/SVAMP. No live official leaderboard was found.

## Lineage

SVAMP is not a split of [GSM8K](gsm8k.md). It is a robustness overlay on ASDiv-A and MAWPS, which have no pages here. Later grade-school sets such as GSM8K ask longer multi-step problems; they do not replace SVAMP's variation tests. [TabMWP](tabmwp.md) adds tables rather than these template edits.

## Saturation and contamination

No current top score was sourced. The set is five years old, fully public, and made of short arithmetic stories, so contamination risk is high. Treat a near-perfect modern score as expected unless the paper used a private variant.

## How to run it

OpenCompass `--datasets svamp_gen` (abbr `svamp`). That config is four-shot in the prompt despite `ZeroRetriever`. The reference data file is GitHub `SVAMP.json`. Do not compare an OpenCompass GSM8K-style number with the 2021 tree-decoder tables, and do not assume the ChilleD 300-item test split is what a paper used.

## Reading the numbers

SVAMP asks whether the model still solves the problem after a small rewrite. It does not measure algebra, contest math, or table reasoning. Pair it with [GSM8K](gsm8k.md) or [MATH](math.md) if you need harder math. If a card reports SVAMP without saying which 1,000-item file or which 300-item slice, the numbers are not comparable.
