---
id: fld
name: "FLD (Formal Logic Deduction)"
aliases:
  - "Formal Logic Deduction"
  - "FLD.v2"
  - "FLD-star"
  - "FLD★"
page_kind: benchmark
category: reasoning
subcategory: "synthetic multi-step formal-logic deduction (answer classification)"
status: unknown
summary: "Hitachi's synthetic deduction set: given invented facts and a hypothesis, choose proved, disproved, or unknown without using world knowledge."
measures: >
  FLD (Formal Logic Deduction) asks a model to (dis)prove a hypothesis from a
  set of facts that are logically structured but semantically invented, so
  memorised world knowledge should not help. The ICML 2023 paper scores both
  a proof trace and a three-way answer (proved / disproved / unknown).
  EleutherAI lm-eval ships the simplified "answer accuracy" setting only:
  generate the world_assump_label (Hub gold is uppercase PROVED, DISPROVED,
  or UNKNOWN). English natural-language facts, plus parallel logical-formula
  prompts. FLD★ (star / FLD.4) uses deeper trees (up to depth 8 vs up to 3)
  and is harder. Not [logical_deduction](logical_deduction.md)
  and not [formal_fallacies_syllogisms_negation](formal_fallacies_syllogisms_negation.md).
task_format: >
  lm-eval default prompt: "Based on the provided facts ($context$), either
  prove or disprove the hypothesis or state that it is unknown." plus
  prompt_serial. Formula tasks substitute context_formula and
  hypothesis_formula. Target is world_assump_label. Metric is exact_match
  after stripping whitespace and taking the first line.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: null
  baseline_note: >
    Three labels, so uniform chance is 33.3%, matching Table 4 "random guess"
    for answer accuracy. The paper also reports proof accuracy (random 0.0).
    GPT-4 10-shot answer accuracy in Table 4: 52.4 on FLD and 49.4 on FLD★;
    proof accuracy 12.8 and 3.2. Fine-tuned T5 is much higher (91.6 / 72.2
    answer accuracy) and is not a zero-shot LLM baseline. No human-rater
    figure is given.
dataset:
  size: 5000
  size_note: >
    Hugging Face hitachi-nlp/FLD.v2, configs default and star, each has
    train 30,000 / validation 5,000 / test 5,000 (card and dataset-viewer
    agree). lm-eval names training_split, validation_split and test_split;
    the scored split is test (5,000 per task). Formula tasks reuse the same
    rows with formula fields. Corpus README: these are version-2.0 dumps
    of the ICML English corpora (FLD.3 default, FLD.4 star), detailed in
    Appendix H.
  url: "https://huggingface.co/datasets/hitachi-nlp/FLD.v2"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "per config: train 30,000 / validation 5,000 / test 5,000; lm-eval scores test"
  public_test_set: true
publisher:
  org: "Hitachi, Ltd. (hitachi-nlp)"
  authors:
    - "Terufumi Morishita"
    - "Gaku Morio"
    - "Atsuki Yamaguchi"
    - "Yasuhiro Sogawa"
  url: "https://github.com/hitachi-nlp/FLD"
paper:
  title: "Learning Deductive Reasoning from Synthetic Corpus based on Formal Logic"
  arxiv: "2308.07336"
  url: "https://arxiv.org/abs/2308.07336"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/fld"
released: "2023-07"
last_updated: "2023-12"
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
    The paper's own claim is that even GPT-4 solves only about half the
    answer-accuracy items under 10-shot (52.4 / 49.4). That is a 2023 figure
    on the paper's protocol (proof-plus-answer), not a current lm-eval
    leaderboard cell, so top_score is left empty.
contamination:
  risk: medium
  note: >
    Facts are synthetic and counterfactual, so ordinary pretraining knowledge
    should not solve items. The 5,000-row test splits have been public on
    Hugging Face since August 2023, so the strings themselves can still leak
    into later training data.
harness:
  lm_eval: "fld_default"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Runnable YAML task names: fld_default (dataset_name default),
    fld_star (star), fld_logical_formula_default, fld_logical_formula_star.
    The README also says group fld and names fld_logical_formula_fld_star;
    no group: key exists in the YAML files, and the star formula task field
    is fld_logical_formula_star. Official Hitachi eval scripts exist but
    are a different path.
tags:
  - formal-logic
  - deductive-reasoning
  - synthetic
  - exact-match
  - three-way-classification
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/fld/README.md"
    title: "lm-eval fld README (answer-accuracy setting, four task names)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/fld/fld_default.yaml"
    title: "fld_default.yaml (hitachi-nlp/FLD.v2 default, exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/fld/fld_star.yaml"
    title: "fld_star.yaml (dataset_name star)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/fld/fld_logical_formula_default.yaml"
    title: "fld_logical_formula_default.yaml (formula prompt, exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/fld/fld_logical_formula_star.yaml"
    title: "fld_logical_formula_star.yaml (task: fld_logical_formula_star)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hitachi-nlp/FLD.v2"
    title: "Hugging Face FLD.v2 card (30k/5k/5k default and star)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/hitachi-nlp/FLD-corpus/main/README.md"
    title: "FLD-corpus README (PROVED/DISPROVED/UNKNOWN, v2.0, Appendix H)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/hitachi-nlp/FLD-corpus/main/LICENSE"
    title: "FLD-corpus Creative Commons Attribution 4.0 International"
    accessed: "2026-09-08"
  - url: "https://github.com/hitachi-nlp/FLD"
    title: "hitachi-nlp/FLD (Apache-2.0 code; NeurIPS_2024 default branch)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2308.07336"
    title: "ICML 2023 paper HTML (Table 4 GPT-4 10-shot numbers)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2308.07336"
    title: "FLD paper abstract (arXiv:2308.07336)"
    accessed: "2026-09-08"
  - url: "https://proceedings.mlr.press/v202/morishita23a.html"
    title: "PMLR v202 Morishita et al. ICML 2023"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-043 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-043"
---

## What it measures

FLD checks multi-step deduction when the facts are fake. Each item gives a
context of invented statements and a hypothesis. The model must decide
whether the hypothesis is proved, disproved, or unknown from those facts
alone. Because the predicates have no real-world meaning, looking up "who
is whose grandson" cannot help. The paper also asks for a proof sequence;
lm-eval does not.

Two English Hub configs exist. `default` is the basic FLD.v2 dump (FLD.3 in
the paper, trees up to depth 3). `star` is FLD★ / FLD.4 (trees up to depth
8). Formula tasks keep the same labels but write facts as predicate calculus
(`&`, `v`, `¬`, `->`). JFLD is a later Japanese benchmark and is not this id.

## How it is scored

lm-eval uses exact_match on `world_assump_label` after
`remove_whitespace` and `take_first`. Hub gold is uppercase PROVED,
DISPROVED, or UNKNOWN; the prompt asks for prove/disprove/unknown, so case
can fail the match. That is the paper's "answer accuracy" setting, not proof
accuracy. Chance is 33.3% with three labels. Table 4 of the ICML PDF reports
10-shot numbers on a protocol that still asks for proofs: GPT-4 answer
accuracy 52.4 (FLD) and 49.4 (FLD★), proof accuracy 12.8 and 3.2. Those are
not drop-in substitutes for a zero-shot `fld_default` run. Fine-tuned T5 in
the same table (91.6 / 72.2 answer accuracy) is a trained prover.

## Dataset and licence

`hitachi-nlp/FLD.v2` holds 30,000 / 5,000 / 5,000 rows for each of default
and star. This page's size is the 5,000-row test split that lm-eval scores.
The FLD-corpus repository licences the data under CC-BY-4.0. The FLD code
repository is Apache-2.0; that licence does not replace the corpus licence.
The Hub card itself has no licence tag.

## Who publishes it

Hitachi NLP: Terufumi Morishita, Gaku Morio, Atsuki Yamaguchi, and
Yasuhiro Sogawa. The evaluation paper is ICML 2023 (PMLR v202,
arXiv:2308.07336). A NeurIPS 2024 follow-up introduces FLDx2 as a training
corpus; it is not the lm-eval task.

## Lineage

Synthetic deduction relative to RuleTaker-style work, but this page is the
Hitachi FLD.v2 / lm-eval suite. Related in this repository:
[logical_deduction](logical_deduction.md) (object ordering) and
[formal_fallacies_syllogisms_negation](formal_fallacies_syllogisms_negation.md)
(valid vs invalid syllogisms). Neither is a subset of FLD. JFLD and FLDx2
do not yet have pages.

## Saturation and contamination

GPT-4 at about half on answer accuracy in 2023 is not a ceiling, and no
current lm-eval top score was read. Proof accuracy in the paper is much
lower (12.8 / 3.2 for GPT-4). The authors note GPT-4 rarely answers
"unknown". Test strings are public; world knowledge is not the intended
leak path.

## How to run it

`lm_eval --tasks fld_default` (and `fld_star`,
`fld_logical_formula_default`, `fld_logical_formula_star`). Quote the YAML
`task:` name. The README's `fld_logical_formula_fld_star` string does not
match the YAML. Do not mix answer-only exact_match with proof accuracy.

## Reading the numbers

A strong `fld_default` exact_match means the model emitted the Hub gold
string (PROVED, DISPROVED, or UNKNOWN) on 5,000 public test rows. It does
not mean the proof was valid.
`fld_star` is a harder depth setting, not a second shuffle of the same
items. Formula tasks drop English. Compare T5-finetuned numbers only when
the reporter trained on FLD. Read beside other knowledge-free logic tasks,
not beside MMLU formal logic.
