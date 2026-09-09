---
id: superglue_ax_b
name: "SuperGLUE AX-b (Broad Coverage Diagnostics)"
aliases:
  - "AX-b"
  - "AXb"
  - "SuperGLUE_AX_b"
  - "AX_b"
page_kind: benchmark
category: reasoning
subcategory: "two-way English diagnostic NLI recast from the GLUE broad-coverage diagnostic"
status: unknown
summary: "SuperGLUE diagnostic: 1,104 English sentence pairs recast from the GLUE diagnostic as two-way entailment, scored with Matthews correlation."
measures: >
  AX-b asks whether sentence2 is entailed by sentence1, as two-class English textual entailment
  (entailment versus not_entailment). SuperGLUE keeps the GLUE expert diagnostic set but collapses
  contradiction and neutral into not_entailment, because MultiNLI is not a SuperGLUE task.
  Submissions are asked to run the RTE model on this set. Items are tagged with logic phenomena
  (negation, monotone, conjunction, and others) for analysis. The set is a diagnostic, not one of
  the eight SuperGLUE score tasks. English text, sentence pairs.
task_format: >
  Binary sentence-pair classification. Official SuperGLUE scoring is Matthews correlation (MCC) on
  the 1,104 labelled pairs, scaled by 100 in Table 3. OpenCompass generation asks A/B ("Is the
  sentence below entailed by the sentence above?") and scores accuracy; perplexity configs compare
  Yes/No or entailment/not_entailment continuations.
metric:
  name: "Matthews correlation (MCC); OpenCompass reports accuracy instead"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0.0
  human_baseline: 77.0
  baseline_note: >
    SuperGLUE Table 3 (PDF p.8, values scaled by 100): most-frequent MCC 0.0, CBoW -0.4, BERT 23.0,
    BERT++ 38.0, human 77.0. Prose human accuracy 88% with MCC 0.77. Official zip labels:
    460 entailment / 644 not_entailment (majority accuracy 58.3% if used as a classification
    baseline). OpenCompass AccEvaluator does not compute MCC.
dataset:
  size: 1104
  size_note: >
    SuperGLUE v2 AX-b.zip AX-b.jsonl: 1,104 lines, counted directly. Hugging Face `aps/super_glue`
    config `axb` test split 1,104 (datasets-server). Labels are present in the public jsonl
    (entailment 460, not_entailment 644). logic tags: 30 distinct values including empty; 740 rows
    have a null logic field. GLUE's family page records the same 1,104 diagnostic rows as three-class
    R3, which is not this two-class recast.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: other
  languages:
    - en
  modalities:
    - text
  splits: "test-only 1,104 labelled pairs in the SuperGLUE v2 zip and in Hugging Face axb"
  public_test_set: true
publisher:
  org: "New York University (SuperGLUE packaging); diagnostic items from the GLUE authors"
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
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/SuperGLUE_AX_b"
released: "2019-05"
last_updated: ""
lineage:
  family: ""
  predecessor: glue
  successors: []
  variants:
    - superglue_ax_g
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    2019 BERT++ MCC is 38.0 against a 77.0 human estimate. The SuperGLUE leaderboard did not render
    as static HTML, so no later official MCC is recorded. OpenCompass accuracy on the public file is
    a different metric.
contamination:
  risk: high
  note: >
    The 1,104 pairs and labels have been public since the GLUE diagnostic (2018) and SuperGLUE v2
    zip (2019). Hugging Face `axb` serves the labelled test split. Linguistic templates (negation
    flips, monotone substitutions) are easy to memorise.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_AX_b (abbr AX_b; gen SuperGLUE_AX_b_gen_4dfefa.py and ppl configs on ./data/SuperGLUE/AX-b/AX-b.jsonl)"
  bigbench: ""
  other: "lm-evaluation-harness lm_eval/tasks/super_glue listing opened here has no axb task (boolq, cb, copa, multirc, record, rte, wic, wsc only)."
tags:
  - nli
  - diagnostic
  - superglue
  - glue
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE (Wang et al., arXiv:1905.00537)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE HTML (diagnostic recast, human 88% / 0.77 MCC)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/1905.00537.pdf"
    title: "SuperGLUE PDF Table 3 (AXb MCC: majority 0.0, CBoW -0.4, BERT 23.0, BERT++ 38.0, human 77.0)"
    accessed: "2026-09-08"
  - url: "https://dl.fbaipublicfiles.com/glue/superglue/data/v2/AX-b.zip"
    title: "Official SuperGLUE v2 AX-b.zip (1,104 labelled jsonl rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/aps/super_glue"
    title: "aps/super_glue dataset card (axb 1,104 test rows, licence other)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=aps/super_glue&config=axb"
    title: "datasets-server size for axb (1,104 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SuperGLUE_AX_b/SuperGLUE_AX_b_gen_4dfefa.py"
    title: "OpenCompass SuperGLUE_AX_b generation config (AXDatasetV2, AccEvaluator, A/B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SuperGLUE_AX_b/SuperGLUE_AX_b_ppl_6db806.py"
    title: "OpenCompass SuperGLUE_AX_b perplexity config (Yes/No)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/super_glue"
    title: "lm-eval super_glue task list (no axb)"
    accessed: "2026-09-08"
  - url: "https://super.gluebenchmark.com/"
    title: "SuperGLUE homepage"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-007 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-007"
---

## What it measures

AX-b is SuperGLUE's broad-coverage linguistic diagnostic, not a scored SuperGLUE task. The model sees two English sentences and must say whether the second is entailed by the first. SuperGLUE took the GLUE diagnostic, which was three-way entailment with phenomenon tags, and folded contradiction and neutral into not_entailment so that an RTE classifier can label it. The point is to see which constructions (negation, monotone, disjunction, and the rest) still fail after the eight-task score looks strong. It is not [superglue_rte](superglue_rte.md), and it is not the three-class GLUE AX average described on [glue](glue.md).

## How it is scored

The SuperGLUE paper scores AX-b with Matthews correlation, printed ×100 in Table 3. BERT++ reached 38.0 against a human 77.0 (prose: 88% accuracy, 0.77 MCC). Most-frequent class has MCC 0.0 even though 644 of 1,104 labels are not_entailment. OpenCompass `SuperGLUE_AX_b` does not compute MCC: generation uses A/B and `AccEvaluator`; perplexity configs score Yes/No or `?entailment` continuations. Those accuracies are not the official diagnostic number. AX-b is excluded from the SuperGLUE average.

## Dataset and licence

The SuperGLUE v2 zip `AX-b/AX-b.jsonl` has 1,104 labelled pairs (460 entailment, 644 not_entailment), matching Hugging Face `aps/super_glue` config `axb`. A `logic` field names phenomena on some rows; 740 rows have it empty. Hugging Face licence is "other"; SuperGLUE does not give a single SPDX id. Labels are in the public file. This is the opposite of BoolQ or RTE test labels, which stay on the evaluation server.

## Who publishes it

Alex Wang, Yada Pruksachatkun, Nikita Nangia, Amanpreet Singh, Julian Michael, Felix Hill, Omer Levy and Samuel R. Bowman (SuperGLUE, arXiv:1905.00537, May 2019, NeurIPS 2019). The sentence pairs come from the GLUE diagnostic of the same group. Site: super.gluebenchmark.com. The leaderboard did not return scores as static HTML.

## Lineage

GLUE introduced the 1,104-pair diagnostic and scored it with three-class R3 beside the nine-task average ([glue](glue.md)). SuperGLUE kept the pairs, collapsed the labels, and asked for RTE-model predictions. This repository has no `glue_ax` page. Sibling SuperGLUE pages include [boolq](boolq.md), [superglue_cb](superglue_cb.md), [superglue_copa](superglue_copa.md), [superglue_multirc](superglue_multirc.md), [superglue_record](superglue_record.md), [superglue_rte](superglue_rte.md), [superglue_wic](superglue_wic.md), [superglue_wsc](superglue_wsc.md) and [superglue_ax_g](superglue_ax_g.md). There is no SuperGLUE family page.

## Saturation and contamination

2019 machine MCC (38.0) sat far below the 77.0 human estimate, so the diagnostic was open then. No later official MCC was readable. Contamination risk is high: the labelled file has been public since 2018–2019 and the constructions are templatic. An OpenCompass accuracy in the 90s on this jsonl is not evidence that linguistic NLI is solved.

## How to run it

Official path: download SuperGLUE v2 `AX-b.zip` and score MCC with the RTE classifier, as the paper specifies. OpenCompass directory `SuperGLUE_AX_b`, abbreviation `AX_b`, file `./data/SuperGLUE/AX-b/AX-b.jsonl`, generation (`SuperGLUE_AX_b_gen_4dfefa.py`) and two perplexity configs. lm-evaluation-harness `super_glue` has no `axb` task in the listing opened here. Name MCC versus accuracy before comparing two AX-b numbers.

## Reading the numbers

A high MCC means the RTE model tracks labelled entailment on these constructed pairs, including the tagged phenomena. It does not enter the SuperGLUE score. It does not measure Winogender bias ([superglue_ax_g](superglue_ax_g.md)). Because labels are public, a modern LLM accuracy on the jsonl can be memorisation. Prefer phenomenon breakdowns over a single MCC if you need to know what still breaks.
