---
id: self_instruct
name: "Self Instruct (HELM)"
aliases:
  - "Self-Instruct"
  - "self-instruct"
  - "user_oriented_instructions"
page_kind: benchmark
category: instruction-following
subcategory: "HELM Instruct critique of 252 user-oriented Self-Instruct instructions"
status: unknown
summary: "HELM Instruct scenario that scores 252 expert-written Self-Instruct tasks with a 1-5 Helpfulness critique, not the 52k generated training set."
measures: >
  HELM's self_instruct scenario loads the 252 expert-written, user-oriented instructions released
  for human evaluation in Wang et al.'s Self-Instruct paper. The model sees the instruction plus
  any instance input and must write a free-form English response. The scenario docstring states
  HELM is not running the Self-Instruct bootstrapping method and is not using the 52k model-written
  training instructions. The skill is following a novel user-style request (rewrite, tone, planning,
  and similar), not a closed NLP label set.
task_format: >
  Zero-shot generation. HELM concatenates `instruction`, a newline, and `instances[].input`.
  Adapter defaults from `get_instruct_adapter_spec`: max_tokens 512, temperature 0.7, empty
  instruction prefix, `max_train_instances` 0. Scenario class `.name` is `self-instruct`; run spec
  and metadata name are `self_instruct`. All instances are tagged TEST_SPLIT.
metric:
  name: Helpfulness
  direction: higher_is_better
  unit: "1-5"
  max_score: 5.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM InstructionFollowingCritiqueMetric asks annotators (count = `num_respondents`) five 1-5
    multiple-choice axes: Helpfulness, Understandability, Completeness, Conciseness, Harmlessness.
    Metadata `main_metric` is Helpfulness ("Does the model appear to do what it is instructed to?").
    If fewer than `num_respondents` critiques return, the metric emits no stats. Wang et al.'s paper
    instead used a four-level human rating on the same 252 tasks; that scale is not HELM's 1-5.
dataset:
  size: 252
  size_note: >
    `human_eval/user_oriented_instructions.jsonl` counted directly: 252 lines, 252 instances (one
    per instruction), 44 of them with empty `input`. Matches the human_eval README ("252 instructions
    with 1 instance per instruction") and the paper's "252 user-oriented instructions". HELM downloads
    that raw GitHub URL and emits one Instance per inner instance.
  url: "https://github.com/yizhongw/self-instruct/blob/main/human_eval/user_oriented_instructions.jsonl"
  license: Apache-2.0
  languages:
    - en
  modalities:
    - text
  splits: "HELM maps every row to TEST_SPLIT; no train split in this scenario"
  public_test_set: true
publisher:
  org: "University of Washington and collaborators (dataset); Stanford CRFM (HELM scenario)"
  authors:
    - "Yizhong Wang"
    - "Yeganeh Kordi"
    - "Swaroop Mishra"
    - "Alisa Liu"
    - "Noah A. Smith"
    - "Daniel Khashabi"
    - "Hannaneh Hajishirzi"
  url: "https://github.com/yizhongw/self-instruct"
paper:
  title: "Self-Instruct: Aligning Language Models with Self-Generated Instructions"
  arxiv: "2212.10560"
  url: "https://arxiv.org/abs/2212.10560"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/instruct/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/self_instruct_scenario.py"
released: "2022-12"
last_updated: "2023-05"
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
    Wang et al. report that GPT-3 tuned with Self-Instruct data outperforms models trained on
    existing public instruction datasets on these 252 tasks, leaving a 5% absolute gap behind
    InstructGPT-001 on four-level human ratings (abstract and §4.4). No numeric HELM Instruct
    leaderboard cell was read (the public page is a JavaScript app, not fetched as a table).
contamination:
  risk: medium
  note: >
    The 252 instructions and gold example outputs have been public on GitHub since the paper (v1
    20 Dec 2022). The human_eval README asks users not to train on this file. HELM still ships the
    answers as CORRECT_TAG references even though scoring is a critique of the generation, not
    exact match to those references.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "self_instruct"
  opencompass: ""
  bigbench: ""
  other: "Run spec in instruction_following_run_specs.py; group self_instruct; HELM Instruct site"
tags:
  - instruction-following
  - helm
  - critique
  - open-ended
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/self_instruct_scenario.py"
    title: "HELM SelfInstructScenario (252-file URL, TEST_SPLIT, main_metric Helpfulness)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/instruction_following_run_specs.py"
    title: "HELM @run_spec_function self_instruct (critique metrics, helm/instruct site)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/instruction_following_critique_metrics.py"
    title: "InstructionFollowingCritiqueMetric (1-5 Helpfulness and four other axes)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "get_instruct_adapter_spec (zero-shot, max_tokens 512, temperature 0.7)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/yizhongw/self-instruct/main/human_eval/user_oriented_instructions.jsonl"
    title: "user_oriented_instructions.jsonl counted (252 tasks, 252 instances)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/yizhongw/self-instruct/main/human_eval/README.md"
    title: "Self-Instruct human_eval README (252 instructions, do not train on this set)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/yizhongw/self-instruct/main/LICENSE"
    title: "self-instruct repository Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2212.10560"
    title: "Self-Instruct paper (v1 2022-12-20, v2 2023-05-25)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-014 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-014"
---

## What it measures

self_instruct, as this id, is HELM's wrapper around Wang et al.'s 252 user-oriented evaluation instructions. The model must follow an English request that looks like a product or writing task, not SuperGLUE. HELM's scenario comment is explicit: it does not run the Self-Instruct generation loop and does not score the 52k GPT-3-written training pairs. If a reporter says "Self-Instruct" they may mean that training set instead; this page is only the 252-task eval.

## How it is scored

The run spec attaches `InstructionFollowingCritiqueMetric` with a caller-chosen `num_respondents`. Annotators rate Helpfulness, Understandability, Completeness, Conciseness, and Harmlessness on 1-5 maps. HELM metadata treats Helpfulness as the main number. No automatic exact-match to the file's `output` field is used for that main metric. Wang et al.'s own human study used four rating levels on the same items; do not mix those percentages with HELM's 1-5 means.

## Dataset and licence

252 JSONL rows, one instance each, counted from the GitHub file HELM downloads. 44 instances have an empty input, so the prompt is the instruction alone. Licence on yizhongw/self-instruct is Apache-2.0. Gold `output` strings are in the JSONL and copied into HELM references.

## Who publishes it

Dataset: Yizhong Wang, Yeganeh Kordi, Swaroop Mishra, Alisa Liu, Noah A. Smith, Daniel Khashabi, Hannaneh Hajishirzi. Paper v1 20 December 2022, v2 25 May 2023 (ACL 2023). HELM packaging: Stanford CRFM, run spec `self_instruct` under HELM Instruct (`https://crfm.stanford.edu/helm/instruct/`).

## Lineage

The method paper also releases 175 seed tasks and 52k generated instructions for tuning. Those are training data, not this eval. HELM Instruct groups this scenario with Vicuna, Koala, Open Assistant, grammar, and Anthropic HH RLHF run specs that share the same critique metric. No sibling pages for those names were in this repository when checked.

## Saturation and contamination

No HELM Instruct numeric top was read. The 252 tasks have been public since late 2022 with answers in-file, so instruction-tuned models may have seen them. The authors asked that the file not be used for training.

## How to run it

HELM run spec name `self_instruct` (hyphenated scenario class name `self-instruct`). Needs a working critique backend and `num_respondents`. Generation: 512 tokens, temperature 0.7, zero-shot. Without enough critiques the metric returns an empty list, so a missing Helpfulness cell is not a zero.

## Reading the numbers

A high Helpfulness mean means annotators thought the model did what the instruction asked, on a 1-5 rubric. It is not BLEU against the JSONL output, not the paper's four-level study, and not a score on the 52k generated set. Compare HELM numbers only with the same respondent count, judge pool, and temperature. For closed-form instruction constraints, look at IFEval-style checks instead of this critique.
