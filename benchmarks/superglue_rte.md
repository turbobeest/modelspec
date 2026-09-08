---
id: superglue_rte
name: "SuperGLUE RTE (Recognizing Textual Entailment)"
aliases:
  - "SuperGLUE_RTE"
  - "sglue_rte"
page_kind: benchmark
category: reasoning
subcategory: "two-way English textual entailment (premise/hypothesis)"
status: saturated
summary: "SuperGLUE's two-way textual-entailment task, reused from GLUE RTE: decide whether a hypothesis is entailed by a premise, scored by accuracy."
measures: >
  RTE asks whether a short hypothesis is entailed by a short premise, as two-class English sentence-pair
  classification (entailment versus not_entailment). SuperGLUE uses the same data and format as GLUE RTE:
  the PASCAL RTE1, RTE2, RTE3 and RTE5 challenge sets, merged and collapsed to two labels. The SuperGLUE
  paper kept RTE because, even after transfer learning lifted GLUE RTE from near chance to the mid-80s,
  a gap to human accuracy remained. The items are news and Wikipedia sentences, not long documents.
task_format: >
  Binary sentence-pair classification. Harnesses prompt the pair and score accuracy of entailment versus
  not-entailment. OpenCompass has both generation (A/B) and perplexity (Yes/No) configs; lm-evaluation-harness
  uses a True/False multiple-choice prompt on the SuperGLUE validation split.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.3
  human_baseline: 93.6
  baseline_note: >
    SuperGLUE Table 2 (test): most-frequent class 50.3, BERT 71.6, BERT++ 79.0, human estimate 93.6.
    The paper also cites ~56% as near-chance at GLUE's launch and 86.3% as the then-current GLUE RTE
    transfer result (Liu et al. 2019d; Yang et al. 2019), still below that human estimate.
dataset:
  size: 277
  size_note: >
    Hugging Face `aps/super_glue` config `rte` has 2,490 train, 277 validation, and 3,000 test rows
    (datasets-server size endpoint, 2026-09-08). SuperGLUE Table 1 prints 2,500 / 278 / 300, which
    disagrees with both this mirror and the long-standing GLUE RTE test size of 3,000; this page uses
    the Hugging Face counts and treats Table 1's "300" test figure as unresolved typesetting. Official
    SuperGLUE scoring uses hidden test labels; harnesses score the 277-row validation split.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: >
    Hugging Face card licence is "other". SuperGLUE refers users to the original PASCAL RTE dataset
    licences rather than stating one suite licence.
  languages:
    - en
  modalities:
    - text
  splits: "train 2,490 / validation 277 (public labels) / test 3,000 (official labels held out)"
  public_test_set: false
publisher:
  org: "New York University (SuperGLUE packaging); original RTE challenges from the PASCAL RTE organisers"
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
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/super_glue/rte"
released: "2019-05"
last_updated: ""
lineage:
  family: ""
  predecessor: glue
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    SuperGLUE's 2019 BERT++ test accuracy is 79.0 against a 93.6 human estimate; the paper already cited
    86.3 on the GLUE packaging of the same data. The SuperGLUE leaderboard did not render as static HTML,
    so no later official top score is recorded. The task is a small, public, 2018-era NLI set and is
    treated as saturated for frontier models.
contamination:
  risk: high
  note: >
    SuperGLUE reuses GLUE RTE, itself merged from PASCAL RTE sets that have been public since the
    mid-2000s. Train and validation labels have been public through GLUE (2018) and SuperGLUE (2019).
    lm-evaluation-harness and OpenCompass score the 277-row validation split, not the hidden test set.
harness:
  lm_eval: "sglue_rte (tag super-glue-lm-eval-v1; dataset aps/super_glue config rte). Distinct from glue's rte task."
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_RTE (abbr RTE; gen and ppl configs on ./data/SuperGLUE/RTE/val.jsonl)"
  bigbench: ""
  other: "lm-evaluation-harness also ships super_glue-rte-t5-prompt under tag super-glue-t5-prompt."
tags:
  - nli
  - entailment
  - classification
  - superglue
  - glue
  - saturated
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE (Wang et al., arXiv:1905.00537)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/aps/super_glue"
    title: "aps/super_glue dataset card"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=aps/super_glue&config=rte"
    title: "aps/super_glue rte split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/super_glue/rte/default.yaml"
    title: "lm-evaluation-harness sglue_rte task config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/SuperGLUE_RTE/SuperGLUE_RTE_gen_68aac7.py"
    title: "OpenCompass SuperGLUE_RTE generation config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/SuperGLUE_RTE/SuperGLUE_RTE_ppl_66caf3.py"
    title: "OpenCompass SuperGLUE_RTE perplexity config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-003"
---

## What it measures

RTE is two-way English textual entailment: given a premise and a hypothesis, say whether the hypothesis is entailed. SuperGLUE keeps the GLUE packaging of four PASCAL RTE challenge sets (RTE1, RTE2, RTE3, RTE5), with labels collapsed to entailment versus not_entailment. The SuperGLUE paper states that this is the same data and format as GLUE RTE. Sentences are short news and Wikipedia pairs. The skill is sentence-level inference, not retrieval or long-context reading.

## How it is scored

The metric is accuracy. SuperGLUE Table 2 (test) gives most-frequent 50.3, BERT 71.6, BERT++ 79.0, and human 93.6. The paper also notes GLUE-era transfer results at 86.3% still below that human figure. Official SuperGLUE scoring is a leaderboard submission on hidden test labels. lm-evaluation-harness task `sglue_rte` scores the 277-row validation split with a True/False prompt. OpenCompass `SuperGLUE_RTE` has a generation config (A/B, `first_option_postprocess`) and a perplexity config (Yes/No log-likelihood), both pointed at `val.jsonl`. Those two OpenCompass modes are not interchangeable with each other or with `sglue_rte` without a protocol note.

## Dataset and licence

Hugging Face `aps/super_glue` config `rte` has 2,490 / 277 / 3,000 rows for train / validation / test. SuperGLUE Table 1 prints 2,500 / 278 / 300. The 3,000-row test split matches GLUE RTE; Table 1's "300" is treated here as an unresolved mismatch, not as a third split. The card licence is "other", with SuperGLUE pointing at the original RTE licences. Test labels are hidden for official scoring. Common LLM harnesses use the public 277-row validation set.

## Who publishes it

SuperGLUE's authors at NYU, Facebook AI Research, the University of Washington and DeepMind packaged RTE in May 2019 (arXiv:1905.00537; NeurIPS 2019). The underlying items come from the PASCAL RTE challenges (Dagan, Bar-Haim, Giampiccolo, Bentivogli and colleagues, 2006–2009). The SuperGLUE site is super.gluebenchmark.com; it did not return scores as static HTML during this pass. GLUE's own site still lists RTE as one of nine GLUE tasks.

## Lineage

This is SuperGLUE's copy of GLUE RTE, not a new item set. The [GLUE](glue.md) family page already describes RTE as one of nine tasks; this repository has no `glue_rte` page, so `superglue_rte` is the first RTE page. Do not fold this id into GLUE's composite `glue` score: a SuperGLUE RTE accuracy is one SuperGLUE task, not the GLUE average. BoolQ (`boolq`) is a related SuperGLUE inference task with its own page. No successor page is recorded.

## Saturation and contamination

By 2019 the paper already reported mid-80s machine accuracy against a 93.6 human estimate on a few thousand public pairs. Later SuperGLUE-test scores were not readable here. For current LLMs the 277-row public validation set is a saturated, leakable NLI quiz, not a ranking instrument. Contamination risk is high: PASCAL RTE text has been public for about two decades, and GLUE/SuperGLUE mirrors have been public since 2018–2019.

## How to run it

lm-evaluation-harness: `sglue_rte` (not `rte`; `rte` is the GLUE task). Dataset `aps/super_glue` config `rte`, validation split, accuracy. T5-prompt alias: `super_glue-rte-t5-prompt`. OpenCompass: directory `SuperGLUE_RTE`, abbreviation `RTE`, generation and perplexity configs on `./data/SuperGLUE/RTE/val.jsonl`. Not confirmed in HELM, inspect_evals, or BIG-bench lists opened for this page. Always name the harness and the split before comparing two "RTE" numbers, because GLUE and SuperGLUE share the data but not the prompt or the suite average.

## Reading the numbers

A high SuperGLUE RTE accuracy means the model can do short English premise/hypothesis classification on a tiny, old set. It does not mean the model handles three-way NLI, adversarial NLI, or document-level entailment. Because GLUE's `rte` and SuperGLUE's `sglue_rte` share items, a pair of similar scores is expected and is not independent evidence. Prefer a harder entailment set when ranking current models; use this number only as a dated floor check, and only when the reporter names validation versus hidden test.
