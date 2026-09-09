---
id: superglue_wic
name: "SuperGLUE WiC (Word-in-Context)"
aliases:
  - "WiC"
  - "SuperGLUE_WiC"
  - "wic"
page_kind: benchmark
category: knowledge
subcategory: "binary word-sense disambiguation over sentence pairs"
status: saturated
summary: "SuperGLUE's word-sense task: decide whether a polysemous word has the same sense in two short sentences, scored by accuracy."
measures: >
  WiC is word-sense disambiguation recast as a yes/no pair. The model sees two short English snippets
  and a target word that appears in both, then says whether that word is used with the same sense.
  Sentences come from WordNet, VerbNet and Wiktionary. SuperGLUE follows the original WiC paper and
  scores accuracy. The original authors stressed that most target words in the test split do not overlap
  the training vocabulary, so lexical memorisation is a weak strategy.
task_format: >
  Binary classification over a sentence pair plus a marked word. lm-evaluation-harness uses a yes/no
  multiple-choice prompt. OpenCompass has a generation A/B config and several perplexity templates.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 80.0
  baseline_note: >
    SuperGLUE Table 2 (test): most-frequent 50.0, BERT and BERT++ 69.5, human estimate 80.0. The original
    WiC paper (Pilehvar and Camacho-Collados, NAACL 2019) reports contextualised-embedding baselines in
    the high 50s to mid 60s on its own split, with BERT-large thresholding at 65.5, well below that
    SuperGLUE human figure.
dataset:
  size: 638
  size_note: >
    The original WiC paper Table 2 and Hugging Face `aps/super_glue` config `wic` agree on 5,428 train,
    638 validation and 1,400 test instances. SuperGLUE Table 1 rounds train to 6,000 and keeps 638 / 1,400.
    This page uses the exact 5,428 / 638 / 1,400 counts. Official SuperGLUE scoring uses hidden test
    labels; harnesses score the 638-row validation split. The WiC paper states that only 36% of test
    target words overlap training, with no overlapping context sentences across splits.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: >
    Hugging Face card licence is "other". SuperGLUE refers users to original dataset licences; a
    WiC-specific SPDX id was not stated on the SuperGLUE card or in the WiC paper HTML opened here.
  languages:
    - en
  modalities:
    - text
  splits: "train 5,428 / validation 638 (public labels) / test 1,400 (official labels held out)"
  public_test_set: false
publisher:
  org: "University of Cambridge / Tehran Institute for Advanced Studies and Cardiff University (original); SuperGLUE packaging at New York University"
  authors:
    - "Mohammad Taher Pilehvar"
    - "Jose Camacho-Collados"
  url: "https://super.gluebenchmark.com/"
paper:
  title: "WiC: the Word-in-Context Dataset for Evaluating Context-Sensitive Meaning Representations"
  arxiv: "1808.09121"
  url: "https://arxiv.org/abs/1808.09121"
  year: 2019
leaderboard_url: "https://super.gluebenchmark.com/"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/super_glue/wic"
released: "2019"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    SuperGLUE's own human estimate is only 80.0 accuracy, with BERT already at 69.5 in 2019. The
    SuperGLUE leaderboard did not render as static HTML, so no later official top score is recorded.
    The ceiling is low and the validation items have been public since 2019, so the task is treated as
    saturated for frontier models.
contamination:
  risk: high
  note: >
    Train and validation labels have been public since the 2019 WiC and SuperGLUE releases. Source
    sentences are drawn from WordNet, VerbNet and Wiktionary, all widely copied into pretraining
    corpora. Harnesses reviewed here score the 638-row public validation split.
harness:
  lm_eval: "wic (tag super-glue-lm-eval-v1; dataset aps/super_glue config wic; yes/no multiple choice on validation)"
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_WiC (abbr WiC; gen and several ppl configs on ./data/SuperGLUE/WiC/val.jsonl)"
  bigbench: ""
  other: "lm-evaluation-harness also ships super_glue-wic-t5-prompt under tag super-glue-t5-prompt."
tags:
  - word-sense
  - classification
  - superglue
  - saturated
sources:
  - url: "https://arxiv.org/abs/1808.09121"
    title: "WiC: the Word-in-Context Dataset (Pilehvar and Camacho-Collados, arXiv:1808.09121)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1808.09121"
    title: "WiC full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE (Wang et al., arXiv:1905.00537)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/aps/super_glue"
    title: "aps/super_glue dataset card"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/super_glue/wic/default.yaml"
    title: "lm-evaluation-harness wic task config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/SuperGLUE_WiC/SuperGLUE_WiC_gen_d06864.py"
    title: "OpenCompass SuperGLUE_WiC generation config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/SuperGLUE_WiC/SuperGLUE_WiC_ppl_312de9.py"
    title: "OpenCompass SuperGLUE_WiC perplexity config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-003"
---

## What it measures

WiC asks whether a polysemous English word has the same sense in two short sentences. The model is given both sentences and the target word, and it answers yes or no. SuperGLUE describes this as word-sense disambiguation cast as binary classification. Sentences are drawn from WordNet, VerbNet and Wiktionary. The original paper (Pilehvar and Camacho-Collados, NAACL 2019) reports 5,428 / 638 / 1,400 train / dev / test instances, with no shared context sentences across splits and only 36% overlap of test target words with training.

## How it is scored

The metric is accuracy. SuperGLUE Table 2 (test) gives most-frequent 50.0, BERT 69.5, and human 80.0. That human number is low relative to other SuperGLUE tasks: even annotators disagree on some sense pairs. Official SuperGLUE scoring uses hidden test labels. lm-evaluation-harness task `wic` scores the 638-row validation split with a yes/no multiple-choice prompt. OpenCompass `SuperGLUE_WiC` generation asks A/B ("Are '{word}' in the above two sentenses the same?") and scores accuracy after a first-capital postprocess; its perplexity configs compare "same" versus "different" continuations. Generation and perplexity numbers from that harness are not the same protocol.

## Dataset and licence

Counts used here are 5,428 / 638 / 1,400 from the WiC paper and from `aps/super_glue` config `wic`. SuperGLUE Table 1 rounds train to 6,000. The Hugging Face card licence is "other"; SuperGLUE does not publish a single SPDX id for WiC. Test labels are withheld for the official board. Harnesses opened for this page use the public validation split.

## Who publishes it

Mohammad Taher Pilehvar and Jose Camacho-Collados introduced WiC (arXiv:1808.09121, 28 August 2018; NAACL 2019). SuperGLUE (Wang et al., May 2019, NeurIPS 2019) added it as one of eight tasks. The SuperGLUE site is super.gluebenchmark.com; it did not return scores as static HTML. The original GitHub README for WiC was not fetched (404 on the path tried).

## Lineage

WiC is not a GLUE task. SuperGLUE added it as a lexical-semantics check that GLUE lacked. This repository has no SuperGLUE family page. BoolQ (`boolq`) is a sibling SuperGLUE task with its own page. No WiC successor page is recorded here. The id is SuperGLUE's WiC, not an unrelated "WIC" acronym.

## Saturation and contamination

Human accuracy on SuperGLUE WiC is 80.0, so a score in the high 70s is already near the published ceiling. BERT sat at 69.5 in the SuperGLUE paper. Later official tops were not readable. Combined with a public 638-row validation set from 2019, the task is treated as saturated. Contamination risk is high because the labelled validation items and the WordNet/Wiktionary sources have been easy to crawl for years.

## How to run it

lm-evaluation-harness: `wic` (tag `super-glue-lm-eval-v1`), dataset `aps/super_glue` config `wic`, validation accuracy. T5-prompt alias: `super_glue-wic-t5-prompt`. OpenCompass: directory `SuperGLUE_WiC`, abbreviation `WiC`, generation (`SuperGLUE_WiC_gen_d06864.py`) and several perplexity configs on `./data/SuperGLUE/WiC/val.jsonl`. Not confirmed in HELM, inspect_evals, or BIG-bench lists opened for this page. Name the prompt style (yes/no versus A/B versus ppl) before comparing two WiC accuracies.

## Reading the numbers

A high WiC accuracy means the model can often tell whether two short contexts share a sense of one English word. It does not measure multilingual WSD, token-level sense tagging, or definition generation. Because the published human number is 80, a model at 85 is past that estimate and may be fitting public items rather than solving a harder sense task. Use a newer lexical or multilingual sense benchmark if you need headroom among current models.
