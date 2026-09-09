---
id: prost
name: "PROST"
aliases:
  - "PROST"
  - "Physical Reasoning about Objects Through Space and Time"
  - "corypaik/prost"
page_kind: benchmark
category: reasoning
subcategory: "zero-shot four-choice English physical reasoning over 10 object concepts"
status: unknown
summary: "18,736 four-choice English questions from 14 templates that probe physical reasoning about objects in space and time, meant to be used zero-shot."
measures: >
  PROST (Physical Reasoning about Objects Through Space and Time) asks which
  of four everyday objects best fits a short English scene. Concepts are
  direction, mass, height, circumference, stackable, rollable, graspable,
  breakable, slideable, and bounceable. Aroca-Ouellette, Paik, Roncone, and
  Kann wrote 14 templates and expanded them to 18,736 items. The paper and
  the lm-eval README require zero-shot use. It is not [piqa](piqa.md), which
  is two-way how-to commonsense from Instructables.
task_format: >
  Four-option multiple choice. lm-eval task prost loads
  hf://datasets/corypaik/prost/data/default.jsonl, test split. Prompt is
  context, then "Question: {ex_question}", then "Answer:". Choices are fields
  A–D. Target is the integer label. should_decontaminate true. Metrics acc
  and acc_norm. YAML filename corypaik_prost.yaml; runnable name is prost.
metric:
  name: "accuracy (acc); acc_norm also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    Four choices, so uniform chance is 25%. Paper Table 5 macro averages
    (2021 models, some T5/UnifiedQA rows omit Slide): GPT 26.1, GPT-2 XL 30.1,
    RoBERTa-L 31.3, ALBERT-xlarge 31.8, UnifiedQA-3B 46.7 (starred). No
    human-accuracy figure is in the paper HTML opened here. Nine validators
    checked object order and affordance groups, not question accuracy.
dataset:
  size: 18736
  size_note: >
    Paper, Hub card, datasets-server, and lm-eval README all give 18,736 test
    questions from 14 templates covering 10 concepts. No train split by design.
  url: "https://huggingface.co/datasets/corypaik/prost"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "test only (18,736 rows)"
  public_test_set: true
publisher:
  org: "University of Colorado Boulder (NaLa lab)"
  authors:
    - "Stéphane Aroca-Ouellette"
    - "Cory Paik"
    - "Alessandro Roncone"
    - "Katharina Kann"
  url: "https://github.com/nala-cub/prost"
paper:
  title: "PROST: Physical Reasoning about Objects through Space and Time"
  arxiv: "2106.03634"
  url: "https://arxiv.org/abs/2106.03634"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/nala-cub/prost"
released: "2021-06"
last_updated: "2022-10"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 46.7
  as_of: "2021-08"
  note: >
    Highest paper Table 5 macro average opened here is UnifiedQA-3B at 46.7
    (starred; Slide omitted). That is a 2021 checkpoint, not a 2026 frontier
    figure. No later public leaderboard cell was read. Four-choice chance is 25.
contamination:
  risk: medium
  note: >
    Templates were written for this set and answers are public on Hugging Face
    (Apache-2.0). The paper argues zero-shot use so models are not trained on
    these templates. Everyday object facts may still appear in pretraining.
    lm-eval sets should_decontaminate on context plus question.
harness:
  lm_eval: "prost"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "YAML file corypaik_prost.yaml; task name prost; dataset json from corypaik/prost"
tags:
  - physical-reasoning
  - commonsense
  - multiple-choice
  - zero-shot
sources:
  - url: "https://arxiv.org/abs/2106.03634"
    title: "PROST arXiv abs (18,736 items, 14 templates, 10 concepts, 2021-06-07)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2106.03634"
    title: "ar5iv HTML (Table 5 macro averages, UnifiedQA-3B 46.7)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2021.findings-acl.404/"
    title: "ACL Anthology Findings ACL-IJCNLP 2021 landing page"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/corypaik/prost"
    title: "Hub card (18,736 test, Apache-2.0, cloze vs ex_question)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=corypaik/prost"
    title: "datasets-server: 18,736 test rows"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/nala-cub/prost/main/README.md"
    title: "nala-cub/prost README (Hub recommended; Apache-2.0; posterity repo)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/prost/README.md"
    title: "lm-eval PROST README (zero-shot only, task name prost)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/prost/corypaik_prost.yaml"
    title: "lm-eval prost YAML (acc, acc_norm, ex_question, decontaminate)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-066 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-066"
---

## What it measures

PROST is a zero-shot English physical-reasoning quiz. Each item sets a tiny scene ("a person drops a glass, a pillow, a coin, and a ball") and asks which object is most likely to break, roll, or otherwise behave as named. Ten concepts and fourteen hand-written templates expand to 18,736 four-choice questions. Objects were chosen as single tokens for masked LMs. The authors' point is that this knowledge should come from pretraining, not from a PROST training split — there is none.

## How it is scored

lm-eval reports accuracy and length-normalised accuracy over A–D. The paper's Table 5 is a macro average over the ten concepts, with some T5 and UnifiedQA rows dropping Slide because of tokenisation. Those two summaries are not the same number. Few-shot PROST would violate the paper's stated protocol (section 7 in the lm-eval README's words). Chance is 25% if labels are balanced; this page did not re-count label balance in the JSONL.

## Dataset and licence

18,736 test rows on `corypaik/prost`, Apache-2.0 on the Hub card, the nala-cub README, and the dataset_info licence field. Each row has cloze `question` and multiple-choice `ex_question`; lm-eval uses the latter. Answers are public.

## Who publishes it

Stéphane Aroca-Ouellette, Cory Paik, Alessandro Roncone, and Katharina Kann at the University of Colorado Boulder. Findings of ACL-IJCNLP 2021; arXiv:2106.03634 (2021-06-07). The GitHub repo is unmaintained and points to the Hub copy.

## Lineage

The paper contrasts PROST with [piqa](piqa.md): PIQA covers many how-to situations, PROST covers a small set of objective physical concepts. Bangla PIQA is a translation of PIQA, not of PROST. No successor page is in this repository.

## Saturation and contamination

Unknown for current models. The 2021 table tops out at 46.7% macro for UnifiedQA-3B, well above 25% and well below 100%. Templates are public. Zero-shot intent does not stop a later corpus from including the JSONL.

## How to run it

`lm_eval --tasks prost`. Keep zero-shot. Do not train on the test file. Compare acc to acc_norm before mixing papers. There is no inspect_evals, HELM, OpenCompass, or BIG-bench task with this name in the paths checked.

## Reading the numbers

A 40% score means the model beats chance on these templated object questions, not that it has a physics engine. Superlative flips (most vs least) and option order are known failure modes in the paper. PIQA numbers are a different task. Treat any few-shot PROST figure as off-protocol unless the reporter says why.
