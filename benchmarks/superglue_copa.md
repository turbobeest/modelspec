---
id: superglue_copa
name: "SuperGLUE COPA (Choice of Plausible Alternatives)"
aliases:
  - "COPA"
  - "Choice of Plausible Alternatives"
  - "SuperGLUE_COPA"
page_kind: benchmark
category: reasoning
subcategory: "binary causal commonsense: cause or effect of a premise (SuperGLUE)"
status: saturated
summary: "SuperGLUE packaging of COPA: pick the more plausible cause or effect of a one-sentence English premise from two alternatives."
measures: >
  SuperGLUE COPA is a two-choice causal commonsense task. The model reads one English
  premise sentence and a question that is either cause or effect, then picks which of two
  alternatives is more plausible. Items are hand-authored, not mined from exams. The original
  COPA paper (Roemmele, Bejan, and Gordon, 2011) wrote 1,000 such questions and split them
  500/500 into development and test. SuperGLUE uses 400 train, 100 validation, and 500 test,
  matching the original test set and splitting the original development set. The language is
  English; the format is forced choice, not free-text explanation.
task_format: "Two-choice classification: premise plus cause/effect cue and two alternatives; English."
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: 100
  baseline_note: >
    Binary choice gives a 50% random-guess rate. SuperGLUE Table 3 estimates human accuracy
    at 100.0 on the hidden test set. BERT++ in that table scored 73.8. The original 2011
    paper reported statistical NLP baselines well below that; those baselines are not HELM
    or OpenCompass numbers.
dataset:
  size: 1000
  size_note: >
    Official SuperGLUE v2 COPA.zip, counted from the jsonl files: 400 train (labels public),
    100 validation (labels public), 500 test (labels omitted). Hugging Face `super_glue`
    config `copa` matches 400/100/500. The 2011 paper authored 1,000 questions and split
    them equally into development and test (500 each). SuperGLUE's 400/100 split of the
    original development portion is the usual train/val cut in modern harnesses.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: "other"
  languages:
    - en
  modalities:
    - text
  splits: "train 400 / validation 100 / test 500 (test labels withheld in the public files)"
  public_test_set: false
publisher:
  org: "USC Institute for Creative Technologies and Indiana University (original COPA); SuperGLUE from New York University and collaborators"
  authors:
    - "Melissa Roemmele"
    - "Cosmin Adrian Bejan"
    - "Andrew S. Gordon"
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
  title: "Choice of Plausible Alternatives: An Evaluation of Commonsense Causal Reasoning"
  arxiv: ""
  url: "https://cdn.aaai.org/ocs/2418/2418-10878-1-PB.pdf"
  year: 2011
leaderboard_url: "https://super.gluebenchmark.com/"
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/SuperGLUE_COPA"
released: "2019-05"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: "glue"
  successors:
    - xcopa
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    SuperGLUE's 2019 human estimate is 100% on the hidden test set, and the public
    validation split is 100 binary items. No current leaderboard table was recovered from
    the JavaScript SuperGLUE site, so no present-day machine top score is recorded. The
    combination of a perfect human ceiling, a tiny scored split, and 2011-era items is why
    COPA is treated as saturated inside SuperGLUE rather than as a ranking task.
contamination:
  risk: high
  note: >
    Train and validation labels have been public since SuperGLUE's 2019 release; the 2011
    development questions are older still. Harnesses score the 100-row labelled validation
    split, not the hidden 500-row test file. Membership of these short, memorable sentences
    in pretraining data is plausible.
harness:
  lm_eval: "copa"
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_COPA"
  bigbench: ""
  other: "lm-eval also ships super_glue-copa-t5-prompt; OpenCompass dataset abbr is COPA"
tags:
  - causal-reasoning
  - commonsense
  - superglue
  - classification
  - saturated
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://cdn.aaai.org/ocs/2418/2418-10878-1-PB.pdf"
    title: "Roemmele, Bejan, Gordon, AAAI Spring Symposium 2011 (COPA)"
    accessed: "2026-09-08"
  - url: "https://dl.fbaipublicfiles.com/glue/superglue/data/v2/COPA.zip"
    title: "Official SuperGLUE v2 COPA.zip (400/100/500 jsonl)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/super_glue/resolve/main/README.md"
    title: "Hugging Face super_glue dataset card (redirects to aps/super_glue)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/super_glue"
    title: "Hugging Face dataset API: super_glue renamed to aps/super_glue; copa splits 400/100/500"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/super_glue/copa/default.yaml"
    title: "lm-evaluation-harness copa task YAML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/super_glue/README.md"
    title: "lm-evaluation-harness SuperGLUE README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SuperGLUE_COPA/SuperGLUE_COPA_gen_91ca53.py"
    title: "OpenCompass SuperGLUE_COPA generation config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/copa.py"
    title: "OpenCompass COPADatasetV2 loader"
    accessed: "2026-09-08"
  - url: "https://super.gluebenchmark.com/"
    title: "SuperGLUE homepage (JavaScript app; scores not recovered as static text)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-002 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-002"
---

## What it measures

SuperGLUE COPA asks a model which of two English alternatives is the more plausible cause or effect of a one-sentence premise. The question field is the word `cause` or `effect`. Items were written by hand for breadth and rater agreement, using photographic subject terms among other prompts, not harvested from tests. The original 2011 evaluation had 1,000 questions. SuperGLUE keeps that pool and reports it as one of eight suite tasks.

This is binary causal preference, not multi-hop explanation. A correct pick can come from shallow association as well as from a causal model.

## How it is scored

The official SuperGLUE metric is accuracy. Random guessing is 50%. SuperGLUE Table 3 puts human accuracy at 100.0 on the hidden test set and BERT++ at 73.8. OpenCompass `SuperGLUE_COPA` generation configs use AccEvaluator and A/B postprocessing on `./data/SuperGLUE/COPA/val.jsonl` (100 labelled items). lm-evaluation-harness task `copa` uses the validation split of `aps/super_glue`/`copa`. Those harness scores are not the SuperGLUE test-server number. The original 2011 paper asked authors to publish both development and test accuracy; SuperGLUE hid the 500 test labels behind its server.

## Dataset and licence

Official SuperGLUE v2 files contain 400 train, 100 validation, and 500 test examples. Test jsonl omits `label`. Hugging Face `aps/super_glue` config `copa` matches those counts. Train labels in the zip are nearly balanced (195 vs 205) and mix cause and effect. The 2011 AAAI paper split the 1,000 questions equally into development and test (500 each) and asked authors to report both. SuperGLUE's 400/100 cut is that development half. The Hugging Face SuperGLUE card lists licence `other` and defers to original task licences. The 2011 AAAI paper carries a standard AAAI copyright line; no SPDX id was found on the SuperGLUE dump.

## Who publishes it

Melissa Roemmele, Cosmin Adrian Bejan, and Andrew S. Gordon introduced COPA at the 2011 AAAI Spring Symposium. SuperGLUE (Wang et al., arXiv:1905.00537, NeurIPS 2019) defined the 400/100/500 split and the leaderboard at super.gluebenchmark.com. OpenCompass's config directory `SuperGLUE_COPA` is the census spelling of that SuperGLUE task. The original ICT project page was not serving at the URL tried for this page; the AAAI PDF is the original-paper source used here.

## Lineage

`glue.md` is the predecessor suite. This repository already has `xcopa.md`, which translates and re-annotates English COPA validation and test items into 11 languages and is a different evaluation. Do not fold SuperGLUE COPA into XCOPA or the reverse. No standalone `copa.md` page exists here; this id is the SuperGLUE/OpenCompass spelling of English COPA. SuperGLUE's other tasks in this batch are `superglue_cb` and `superglue_multirc`; BoolQ is already `boolq.md`.

## Saturation and contamination

A 100% human ceiling on 500 hidden items, and a 100-item public validation file that harnesses score, leave little ranking room among current models. Contamination risk is high: the sentences have been public since 2011/2019 and are short enough to memorise. A 90% OpenCompass COPA number is not evidence of remaining causal-reasoning headroom.

## How to run it

OpenCompass: `opencompass/configs/datasets/SuperGLUE_COPA/` (generation and several PPL templates). Dataset abbr `COPA`; loader `COPADatasetV2`. lm-evaluation-harness: `--tasks copa` or `super_glue-copa-t5-prompt`. Official test accuracy needs the SuperGLUE server. inspect_evals and HELM had no COPA scenario in the sources opened here. Prompt templates differ (which may be the cause/effect vs T5 prefixes), so match configs before comparing.

## Reading the numbers

A strong SuperGLUE COPA score means the model usually picks the intended alternative on this small, old, binary set. It does not mean the model can explain the causal link, handle XCOPA's other languages, or beat chance on a hidden 500-item draw unless the reporter used the official test server. Prefer XCOPA or a newer commonsense suite when the claim is about causal reasoning rather than SuperGLUE completeness.
