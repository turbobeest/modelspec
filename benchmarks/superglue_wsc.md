---
id: superglue_wsc
name: "SuperGLUE WSC (Winograd Schema Challenge, SuperGLUE recast)"
aliases:
  - "SuperGLUE_WSC"
  - "wsc"
  - "wsc.fixed"
page_kind: benchmark
category: reasoning
subcategory: "binary pronoun coreference on Winograd schemas"
status: saturated
summary: "SuperGLUE's recast Winograd Schema Challenge: decide whether a marked pronoun refers to a marked noun in one English sentence, scored by accuracy."
measures: >
  SuperGLUE WSC is a binary coreference task, not the original fill-in-the-blank Winograd Schema
  Challenge. Each item is one English sentence with a marked pronoun and a marked noun. The model
  must say whether the pronoun refers to that noun. SuperGLUE built this recast from the original WSC
  items plus Commonsense Reasoning affiliated data, with a disjoint train/validation/test split so
  that GLUE WNLI's adversarial overlap cannot be memorised. The schemas are written to need everyday
  commonsense rather than syntax.
task_format: >
  Binary yes/no classification on a sentence with two highlighted spans. lm-evaluation-harness loads
  Hugging Face config `wsc.fixed` and scores accuracy. OpenCompass has generation (A/B) and perplexity
  (Yes/No) configs on `val.jsonl`.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 100.0
  baseline_note: >
    SuperGLUE Table 2 (test): most-frequent class 65.1, BERT and BERT++ 64.3 (below the majority
    baseline), human estimate 100.0. The SuperGLUE prose also cites ~96% human on the older
    multiple-choice WSC framing and 90.4% machine accuracy from then-recent data-augmentation work
    (Kocijan et al. 2019; Liu et al. 2019d) on that framing, which is not this binary recast.
dataset:
  size: 104
  size_note: >
    Hugging Face `aps/super_glue` configs `wsc` and `wsc.fixed` both have 554 train, 104 validation
    and 146 test examples. SuperGLUE Table 1 matches those counts. The test items are described as
    coming from fiction books and shared by the original WSC authors. Official SuperGLUE scoring uses
    hidden test labels; harnesses score the 104-row validation split. `wsc.fixed` is the config
    lm-evaluation-harness loads; this page did not open a separate explanation of how `fixed` edits
    the span strings.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: >
    Hugging Face card licence is "other". SuperGLUE refers users to original dataset licences; a
    WSC-specific SPDX id was not stated on the card opened here.
  languages:
    - en
  modalities:
    - text
  splits: "train 554 / validation 104 (public labels) / test 146 (official labels held out)"
  public_test_set: false
publisher:
  org: "New York University (SuperGLUE recast); original Winograd Schema Challenge from Levesque, Davis and Morgenstern"
  authors:
    - "Alex Wang"
    - "Yada Pruksachatkun"
    - "Nikita Nangia"
    - "Amanpreet Singh"
    - "Julian Michael"
    - "Felix Hill"
    - "Omer Levy"
    - "Samuel R. Bowman"
  url: "https://super.gluebenchmark.com/"
paper:
  title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems"
  arxiv: "1905.00537"
  url: "https://arxiv.org/abs/1905.00537"
  year: 2019
leaderboard_url: "https://super.gluebenchmark.com/"
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/super_glue/wsc"
released: "2019-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - winogrande
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    SuperGLUE's 2019 BERT run scored 64.3, below the 65.1 majority baseline, with human 100.0 on 146
    test items. The SuperGLUE leaderboard did not render as static HTML. The validation set has 104
    labelled rows and has been public since 2019, so later LLM accuracies on that split are not treated
    as open headroom.
contamination:
  risk: high
  note: >
    Original Winograd schemas have been public since 2011–2012. SuperGLUE's train and validation labels
    have been public since 2019. The 104-row validation split is what OpenCompass and lm-evaluation-harness
    score. WinoGrande was later built specifically because small WSC-style sets are easy to overfit.
harness:
  lm_eval: "wsc (tag super-glue-lm-eval-v1; dataset aps/super_glue config wsc.fixed; yes/no on validation)"
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_WSC (abbr WSC; gen and ppl configs on ./data/SuperGLUE/WSC/val.jsonl)"
  bigbench: ""
  other: "lm-evaluation-harness also ships super_glue-wsc-t5-prompt under tag super-glue-t5-prompt."
tags:
  - coreference
  - commonsense
  - winograd
  - superglue
  - saturated
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE (Wang et al., arXiv:1905.00537)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/aps/super_glue"
    title: "aps/super_glue dataset card (wsc and wsc.fixed configs)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/super_glue/wsc/default.yaml"
    title: "lm-evaluation-harness wsc task config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/SuperGLUE_WSC/SuperGLUE_WSC_gen_7902a7.py"
    title: "OpenCompass SuperGLUE_WSC generation config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/SuperGLUE_WSC/SuperGLUE_WSC_ppl_d0f531.py"
    title: "OpenCompass SuperGLUE_WSC perplexity config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-003"
---

## What it measures

SuperGLUE WSC is a yes/no coreference problem on one English sentence. A pronoun and a noun are marked, and the model must say whether the pronoun refers to that noun. SuperGLUE recast the Winograd Schema Challenge this way, rather than asking the model to choose among several candidate fillers. Training and validation items come from the original WSC (Levesque, Davis and Morgenstern) and from data distributed by Commonsense Reasoning; test items are fiction-book schemas shared by the original authors. SuperGLUE removed GLUE WNLI's overlapping-sentence trap by keeping the three splits disjoint.

## How it is scored

The metric is accuracy. SuperGLUE Table 2 (test) is the important baseline table: majority class 65.1, BERT 64.3, human 100.0. BERT below majority is the paper's own warning that the binary set is small and skewed. Official SuperGLUE scoring uses 146 hidden test items. lm-evaluation-harness task `wsc` loads `wsc.fixed` and scores the 104-row validation split with a yes/no prompt. OpenCompass `SuperGLUE_WSC` generation asks A/B ("Is '{span1}' and '{span2}' refers to the same entity") and scores accuracy; its perplexity configs compare Yes versus No continuations. Those protocols are not identical.

## Dataset and licence

`aps/super_glue` configs `wsc` and `wsc.fixed` each have 554 / 104 / 146 examples, matching SuperGLUE Table 1. The Hugging Face card licence is "other". Test labels are withheld for the official board. Harnesses opened here use the public 104-row validation split. How `wsc.fixed` differs from `wsc` was not stated on the card text opened for this page; lm-evaluation-harness's runnable task uses `wsc.fixed`.

## Who publishes it

SuperGLUE's authors packaged this recast in May 2019 (arXiv:1905.00537; NeurIPS 2019). The underlying schemas are the Winograd Schema Challenge of Levesque, Davis and Morgenstern (AAAI Spring Symposium, 2011/2012 in SuperGLUE's citation). The SuperGLUE site is super.gluebenchmark.com; it did not return scores as static HTML.

## Lineage

This is not GLUE WNLI. SuperGLUE replaced WNLI's NLI recast with this binary span recast and a non-adversarial split. It is also not [WinoGrande](winogrande.md): WinoGrande is a 44k-problem, adversarially filtered successor to the original WSC, with its own page here. CLUE WSC (`fewclue_cluewsc`) is a Chinese CLUE task, not this English SuperGLUE set. This repository has no SuperGLUE family page. BoolQ (`boolq`) is a sibling SuperGLUE task.

## Saturation and contamination

A 104-row public validation set with a 65% majority baseline cannot separate current models. SuperGLUE's 2019 BERT run did not beat majority. Human accuracy on the SuperGLUE recast is 100.0, so any remaining errors on validation are as likely to be prompt artefacts as genuine schema failures. Contamination risk is high: the schemas are old, famous, and tiny. WinoGrande exists because this style of set stopped being a fair commonsense test.

## How to run it

lm-evaluation-harness: `wsc` (tag `super-glue-lm-eval-v1`), dataset `aps/super_glue` config `wsc.fixed`, validation accuracy. T5-prompt alias: `super_glue-wsc-t5-prompt`. OpenCompass: directory `SuperGLUE_WSC`, abbreviation `WSC`, generation and several perplexity configs on `./data/SuperGLUE/WSC/val.jsonl`. Not confirmed in HELM, inspect_evals, or BIG-bench lists opened for this page. Do not compare a SuperGLUE WSC accuracy to WinoGrande or to GLUE WNLI.

## Reading the numbers

A high SuperGLUE WSC accuracy on 104 validation rows mostly shows the model can answer a famous pronoun puzzle in the prompt format the harness used. It does not show robust coreference or commonsense. Majority is already 65.1, so scores should be read against that floor and against the 100 human ceiling. Prefer [WinoGrande](winogrande.md) when you want a Winograd-style number that still has a large, filtered item set. Treat SuperGLUE WSC as a dated SuperGLUE line, not as independent evidence.
