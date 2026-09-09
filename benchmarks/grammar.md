---
id: grammar
name: "Grammar / Best ChatGPT Prompts (HELM Instruct)"
aliases:
  - "Best ChatGPT Prompts"
  - "HELM grammar"
  - "grammar:path"
  - "best_chatgpt_prompts"
page_kind: benchmark
category: instruction-following
subcategory: "HELM Instruct CFG expansion of Gridfiti ChatGPT prompts, scored by Helpfulness"
status: unknown
summary: "HELM Instruct scenario that expands a CFG of Gridfiti ChatGPT prompts and scores free-form replies with a 1-5 Helpfulness critique."
measures: >
  grammar, as this id, is not linguistic acceptability and not [glue_cola](glue_cola.md)
  or [blimp](blimp.md). It is Stanford HELM Instruct's GrammarScenario: a context-free
  grammar expands into English user prompts, the model writes a free-form reply,
  and a critique metric rates Helpfulness. The checked-in grammar
  best_chatgpt_prompts.yaml restates GRIDFITI's 2023 "best ChatGPT prompts"
  list, with slots such as language, city, and event. The HELM schema file
  says the group should have been named best_chatgpt_prompts, but results
  use grammar.
task_format: >
  Zero-shot generation via get_instruct_adapter_spec (max_tokens 512,
  temperature 0.7, max_train_instances 0). References are empty. Run spec
  grammar:path=<yaml>,tags=<csv> keeps only derivations whose collected tags
  include every requested tag. Scoring is InstructionFollowingCritiqueMetric.
metric:
  name: Helpfulness
  direction: higher_is_better
  unit: "1-5"
  max_score: 5.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Annotators also rate Understandability, Completeness, Conciseness, and
    Harmlessness on the same 1-5 maps. Helpfulness is "Does the model appear
    to do what it is instructed to?" (1 = not relevant, 5 = brilliant ideas).
    schema_instruction_following.yaml sets main_name Helpfulness and
    main_split test. If fewer than num_respondents critiques return, the
    metric emits no stats. This is not CoLA MCC and not a parse-accuracy
    score on the CFG.
dataset:
  size: 320
  size_note: >
    Counted from best_chatgpt_prompts.yaml: 289 Root templates expand through
    nonterminals (Language 5, City 2, Event 4, and others) to 320 strings
    when no tag filter is applied. Tag totals include real 31, personal 29,
    content 21. The scenario puts every kept derivation on TEST_SPLIT with
    empty references. A tags= argument can shrink the set. Instance count
    was not re-run through HELM itself.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/grammar_scenario.py"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "all instances TEST_SPLIT; no train split"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM Instruct); prompt list attributed to Gridfiti Staff"
  authors: []
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/grammar_scenario.py"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://crfm.stanford.edu/helm/instruct/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/grammar_scenario.py"
released: "2023"
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
    No numeric HELM Instruct leaderboard cell was read. The critique is 1-5
    Helpfulness from a small prompt list, so ceiling behaviour is not
    established.
contamination:
  risk: medium
  note: >
    Prompt templates are public in HELM and restated from a 2023 web article
    about ChatGPT prompts. There are no gold completions to leak. Models
    trained on prompt-library crawls may have seen similar instructions.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "grammar"
  opencompass: ""
  bigbench: ""
  other: "Runnable spec is grammar:path=<yaml>,tags=<csv> in instruction_following_run_specs.py; default YAML is best_chatgpt_prompts.yaml."
tags:
  - helm
  - instruction-following
  - llm-as-judge
  - prompts
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/grammar_scenario.py"
    title: "HELM GrammarScenario (name grammar; metadata Best ChatGPT Prompts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/grammar.py"
    title: "HELM grammar expansion engine"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/best_chatgpt_prompts.yaml"
    title: "best_chatgpt_prompts.yaml (289 Root templates; 320 derivations unfiltered)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/instruction_following_run_specs.py"
    title: "HELM Instruct run spec grammar"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/instruction_following_critique_metrics.py"
    title: "InstructionFollowingCritiqueMetric (Helpfulness 1-5)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_instruction_following.yaml"
    title: "HELM Instruct schema (group grammar, display Best ChatGPT Prompts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-046 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-046"
---

## What it measures

grammar in HELM is a prompt generator, not a test of English syntax. A YAML grammar lists ChatGPT-style instructions with slots. The harness expands those slots into full user messages. The model must follow the message. Judges then score Helpfulness on a 1–5 map. The default grammar is HELM's rendering of GRIDFITI's 2023 "best ChatGPT prompts" list, covering personal, student, marketing, and similar tags.

This id collides with everyday use of "grammar." It is not CoLA, BLiMP, or grammatical-error correction. HELM's own schema comments that the group should have been called `best_chatgpt_prompts`.

## How it is scored

Runs use `get_instruct_adapter_spec`: zero shots, 512 tokens, temperature 0.7. There is no reference completion. `InstructionFollowingCritiqueMetric` asks `num_respondents` judges (human or configured critique model) five 1–5 questions. The main reported number is Helpfulness. Understandability, Completeness, Conciseness, and Harmlessness are extra. If too few critiques return, HELM emits no stats. Two numbers are comparable only with the same judge, the same `path`, and the same `tags` filter.

## Dataset and licence

`best_chatgpt_prompts.yaml` has 289 Root templates. Expanding nonterminals yields 320 strings with no tag filter, counted from that file. Examples include acting as a chef, writing a resignation letter, and listing bars in a named city. Every instance is test; references are empty. HELM code is Apache-2.0. A separate licence for the Gridfiti prompt wording was not stated in the files opened here.

## Who publishes it

Stanford CRFM ships GrammarScenario inside HELM Instruct (`https://crfm.stanford.edu/helm/instruct/`). Scenario metadata names Gridfiti Staff as the 2023 source of the prompt list. No separate academic paper for this scenario was opened. The Instruct site is the intended leaderboard; no numeric cell from that JavaScript app was read.

## Lineage

The engine in `grammar.py` can load any YAML grammar. The metadata and schema pin this harness id to the ChatGPT-prompt list. HELM Instruct siblings in this repository include [anthropic_hh_rlhf](anthropic_hh_rlhf.md), which uses the same critique metric on a different prompt source. Do not treat this page as [glue_cola](glue_cola.md).

## Saturation and contamination

A 1–5 Helpfulness mean on a few hundred short prompts does not have a published ceiling. Prompt libraries are widely copied, so instruction wording may be familiar even when completions are not. There is no gold answer to memorise.

## How to run it

HELM run spec `grammar` takes `num_respondents`, `path`, and `tags`. Point `path` at `best_chatgpt_prompts.yaml` unless you supply another grammar. Empty `tags` keeps all 320 strings; a tag such as `personal` keeps that slice. lm-evaluation-harness has no task named `grammar` that matches this scenario.

## Reading the numbers

A high Helpfulness score means judges thought the model did what those ChatGPT-style prompts asked. It does not measure syntax, parsing, or grammaticality. Judge identity and `num_respondents` dominate the number. Compare it with other HELM Instruct groups, not with CoLA MCC. If a model card says "grammar" without HELM Instruct, it is probably a different task.
