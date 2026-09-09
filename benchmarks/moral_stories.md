---
id: moral_stories
name: "Moral Stories"
aliases:
  - "MoralStories"
page_kind: benchmark
category: safety
subcategory: "binary ranking of a moral versus immoral action given a social norm and context"
status: unknown
summary: "lm-eval ranks a crowd-written moral action against an immoral one, given a social norm, situation and intention from the 12k-story Moral Stories corpus."
measures: >
  This id is EleutherAI lm-evaluation-harness task moral_stories, not the paper's original
  generation suite and not BIG-bench moral_permissibility. Each item is an English seven-part
  story. The harness concatenates the norm, situation and intention, then asks which of two
  action sentences is more likely: the crowd-written moral action or the immoral action.
  The labelled target is always the moral action. The original EMNLP 2021 work instead asked
  models to generate actions, consequences or norms under those constraints.
task_format: >
  Two-way multiple_choice over moral_action versus immoral_action. Context is the capitalised
  norm, situation and intention. Zero extra few-shot examples in the YAML. English text.
metric:
  name: "accuracy (acc); length-normalised accuracy (acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Two choices, so chance is 50%. The harness always places the moral action first and sets
    label 0, so the score is the share of items where the moral action has higher likelihood.
    The paper reports classification accuracy for several grounded action-classification
    settings on RoBERTa-large, not this likelihood ranking, so those figures are not copied
    in as this page's human or model baseline.
dataset:
  size: 12000
  size_note: >
    LabHC/moral_stories (the harness dataset_path) is the "full" 12,000-story subset with a
    single train split of 12,000 rows, confirmed from the Hugging Face dataset card and API.
    The original paper and demelin/moral_stories also state 12k structured narratives after
    validation of about 14k collected stories. lm-eval sets test_split to train, so all 12,000
    stories are scored. The official Hugging Face dump also ships many classification and
    generation splits (norm-distance, lexical-bias, minimal-pairs) that this task does not use.
  url: "https://huggingface.co/datasets/LabHC/moral_stories"
  license: "MIT (demelin/moral_stories card and GitHub LICENSE; LabHC card states no licence field)"
  languages:
    - en
  modalities:
    - text
  splits: "LabHC dump: train only (12,000). lm-eval evaluates that train split."
  public_test_set: true
publisher:
  org: "Allen Institute for AI; University of Edinburgh; University of Washington"
  authors:
    - "Denis Emelin"
    - "Ronan Le Bras"
    - "Jena D. Hwang"
    - "Maxwell Forbes"
    - "Yejin Choi"
  url: "https://github.com/demelin/moral_stories"
paper:
  title: "Moral Stories: Situated Reasoning about Norms, Intents, Actions, and their Consequences"
  arxiv: "2012.15738"
  url: "https://aclanthology.org/2021.emnlp-main.54/"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/demelin/moral_stories"
released: "2021"
last_updated: ""
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
    No current public LLM leaderboard for the lm-eval likelihood task was opened. The 2021
    paper's RoBERTa action-classification numbers are a different protocol.
contamination:
  risk: high
  note: >
    The full 12k stories have been public since 2021 (GitHub, TinyURL dump, Hugging Face).
    lm-eval scores the public train split. The LabHC copy was published to sit beside the
    French Histoires Morales translation of the same stories.
harness:
  lm_eval: "moral_stories"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Task YAML version 1.0. dataset_path LabHC/moral_stories. process_docs in
    lm_eval/tasks/moral_stories/utils.py. The harness README says the implementation follows
    the Histoires Morales work (LabHC/histoires_morales).
tags:
  - social-reasoning
  - morality
  - multiple-choice
  - lm-eval
  - english
sources:
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/moral_stories/moral_stories.yaml"
    title: "lm-evaluation-harness moral_stories.yaml (task name, LabHC path, acc / acc_norm)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/moral_stories/utils.py"
    title: "lm-eval moral_stories utils.process_docs (moral action always label 0)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/moral_stories/README.md"
    title: "lm-eval Moral Stories README (seven-part schema; Histoires Morales note)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/LabHC/moral_stories"
    title: "LabHC/moral_stories card (12,000 train rows; full subset)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/LabHC/moral_stories"
    title: "LabHC/moral_stories Hugging Face API (num_examples 12000)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/demelin/moral_stories"
    title: "demelin/moral_stories card (MIT; original dump and splits)"
    accessed: "2026-09-08"
  - url: "https://github.com/demelin/moral_stories"
    title: "demelin/moral_stories repository and MIT LICENSE"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2021.emnlp-main.54/"
    title: "EMNLP 2021 Moral Stories paper"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2012.15738"
    title: "arXiv 2012.15738 HTML (12k stories; classification versus generation tasks)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-013 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-013"
---

## What it measures

lm-eval `moral_stories` is a two-way choice over English social actions. The model
sees a short norm, a situation, and an intention. It must assign higher likelihood
to the crowd-written moral action than to the matching immoral action. Both actions
are written to satisfy the same intention. Only one of them follows the norm.

This is not a free-text ethics essay, and it is not BIG-bench
[Moral Permissibility](moral_permissibility.md). The 2021 paper used the same
stories for generation and several classification splits. The harness scores one
fixed likelihood comparison on the full 12k set.

## How it is scored

The YAML sets `output_type: multiple_choice` and reports mean `acc` and `acc_norm`.
`utils.process_docs` always lists `[moral_action, immoral_action]` and `label: 0`.
A correct item is one where the moral action has the higher (or length-normalised
higher) log-likelihood. Chance is 50%. No few-shot pool is declared. Do not treat
the paper's RoBERTa action-classification table as this score.

## Dataset and licence

Emelin et al. collected about 14k Mechanical Turk stories from Social-Chem-101
norms and kept 12k after validation. Each story has seven sentences: norm,
situation, intention, moral action, moral consequence, immoral action, immoral
consequence. The GitHub LICENSE and the `demelin/moral_stories` card are MIT.
The LabHC copy used by lm-eval is the same 12,000 rows and does not restate a
licence on its card. Answers are public.

## Who publishes it

The dataset is Emelin, Le Bras, Hwang, Forbes and Choi (EMNLP 2021; arXiv
2012.15738), with authors at Edinburgh, AI2 and the University of Washington.
The ranking task is maintained in EleutherAI lm-evaluation-harness. LabHC
republished the full English subset next to Histoires Morales.

## Lineage

No predecessor page. [Moral Permissibility](moral_permissibility.md) is a different
BIG-bench trolley-style yes/no set. Histoires Morales is a French translation of
these 12k stories; it has no page here. The paper's generation and split-specific
classification tasks are not this harness id.

## Saturation and contamination

No current top score for the likelihood task was read. Contamination is high:
public stories and both actions since 2021, and lm-eval evaluates the public
train split.

## How to run it

`lm_eval --tasks moral_stories`. Confirm you are scoring likelihood, not a
generated action. The Histoires Morales French dump is a different dataset path.

## Reading the numbers

A high score means the model prefers the labelled moral action under this
crowd-written US-centric code of conduct. It does not mean the model can state
a new norm, predict a consequence, or refuse harm in an open prompt. Compare
only to other `moral_stories` likelihood runs, and read the original paper when
the claim is generation quality.
