---
id: synthetic_efficiency
name: "Synthetic efficiency (HELM)"
aliases:
  - "HELM synthetic efficiency"
page_kind: benchmark
category: generation
subcategory: "controlled inference-runtime probe over prompt length, output length and tokenizer"
status: unknown
summary: "HELM runtime probe: generate from fixed public-domain prompts while varying prompt length, output length and tokenizer."
measures: >
  synthetic_efficiency is not a quality ranking. HELM feeds short public-domain prompts of a
  chosen token length and asks the model to generate a chosen number of tokens so that runtime
  can be compared across providers. The scenario docstring lists four questions: how runtime
  scales with prompt and output length and with the number of completions; how much variance
  each query shows; how providers differ; and whether hardware can be reverse-engineered.
  Prompts are stored on a CodaLab bundle and sliced per tokenizer. English-script public-domain
  text used as filler, not as a comprehension test.
task_format: >
  Completion generation. Run spec synthetic_efficiency with num_prompt_tokens, num_output_tokens,
  tokenizer and optional random. Each run loads 10 instances. References are empty strings tagged
  correct. HELM also attaches exact_match and generative-harms metrics even though the gold
  continuation is empty.
metric:
  name: "inference runtime (denoised and idealized); run spec also attaches exact_match"
  direction: lower_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_classic.yaml puts the group under efficiency_detailed and sets main_split to test
    with no main_name. ScenarioMetadata.main_metric is the string "unknown". The HELM paper
    defines denoised inference runtime (provider stack, noise removed) and idealized inference
    runtime (A100 + Megatron). exact_match on empty references is not the reason to run this
    scenario. Direction here follows runtime (lower is better).
dataset:
  size: 10
  size_note: >
    The classic run spec hard-codes num_instances=10 per configuration. Prompt lengths in the
    scenario file are 1, 16, 32, 64, 256, 512, 768, 1024, 1536 and 1920 tokens. Output lengths
    are 1, 2, 4, 8, 16, 32 and 64. Tokenizers listed include huggingface/gpt2, ai21/j1,
    cohere/cohere, meta/opt, yandex/yalm, bigscience/bloom, bigscience/t0pp, google/t5,
    google/ul2, tsinghua/glm, eleutherai/gptj and eleutherai/gptneox. Files are named
    num_prompt_tokens=…,tokenizer=…,id=….txt on CodaLab bundle
    0x17a361bc066b4b0e87d968069759d361. A full cartesian total was not counted from a
    downloaded dump.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_efficiency_scenario.py"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "test only (HELM TEST_SPLIT); 10 instances per (prompt length, tokenizer) run"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM)"
  authors:
    - "Keshav Santhanam"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_efficiency_scenario.py"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_efficiency_scenario.py"
released: "2022-11"
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
    Runtime is hardware- and stack-specific, so there is no saturation ceiling in the quality
    sense. No numeric cell was read from the JavaScript classic leaderboard. HELM entered
    maintenance mode on 2026-06-01.
contamination:
  risk: medium
  note: >
    Prompt files are public on CodaLab and the scenario says they come from fixed public-domain
    sources. Gold continuations are empty, so answer leakage is not the failure mode. Repeated
    public prompts can still be cached by a provider.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "synthetic_efficiency"
  opencompass: ""
  bigbench: ""
  other: "Run spec synthetic_efficiency:random=<seed> with num_prompt_tokens, num_output_tokens, tokenizer; 10 instances; completion adapter."
tags:
  - efficiency
  - runtime
  - helm
  - synthetic
  - generation
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/synthetic_efficiency_scenario.py"
    title: "synthetic_efficiency_scenario.py (token grids, 12 tokenizers, CodaLab bundle, metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py get_synthetic_efficiency_spec (10 instances, exact_match + generic + harms)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml Synthetic efficiency group (efficiency_detailed, main_split test)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (Liang et al., 2022)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.09110"
    title: "HELM paper HTML (denoised vs idealized runtime; Santhanam credited for this scenario)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (classic leaderboard; maintenance mode 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness code; prompt-file licence not stated)"
    accessed: "2026-09-08"
  - url: "https://worksheets.codalab.org/rest/bundles/0x17a361bc066b4b0e87d968069759d361/contents/blob/num_prompt_tokens=16,tokenizer=huggingface_gpt2,id=0.txt"
    title: "CodaLab prompt sample (16 GPT-2 tokens; Alice in Wonderland public-domain English)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-015 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-015"
---

## What it measures

synthetic_efficiency measures how long a model takes to read a prompt and emit tokens, not whether the tokens are right. HELM loads a public-domain string of a requested token length and asks for a requested number of new tokens. The authors want scaling curves against prompt length, output length and completion count, plus provider variance. The text is filler. A CodaLab sample for 16 GPT-2 tokens is an Alice in Wonderland sentence, consistent with the scenario's public-domain claim. Files are re-tokenized per vendor tokenizer. It is a HELM classic efficiency scenario, not [synthetic_reasoning](synthetic_reasoning.md).

## How it is scored

The HELM paper defines two runtime metrics. Denoised inference runtime uses the provider's own stack with measurement noise removed. Idealized inference runtime re-runs the same queries on NVIDIA A100 GPUs with Megatron so architectures can be compared. schema_classic.yaml does not name a main_metric. The scenario's own metadata string is "unknown". The run spec still attaches exact_match, generic metrics and generative-harms scores even though each reference is an empty string. Quote the runtime column, the tokenizer, and the token lengths. Lower runtime is better.

## Dataset and licence

Each classic run uses 10 test instances. The scenario lists ten prompt lengths and seven output lengths and twelve tokenizer names. Files come from CodaLab bundle `0x17a361bc066b4b0e87d968069759d361`. A downloaded total across every tokenizer and length was not counted here, so `size` is the 10-instance run, not a cartesian product. The scenario says the text is public domain; no SPDX string appears on the bundle in the sources opened, so `license` is empty. HELM's code is Apache-2.0.

## Who publishes it

Stanford CRFM released the scenario with HELM (arXiv 2211.09110, 16 November 2022). The paper's author contributions credit Keshav Santhanam for the synthetic efficiency scenario and its metrics. schema_classic.yaml still includes the Synthetic efficiency group. HELM entered maintenance mode on 1 June 2026.

## Lineage

There is no predecessor page in this repository. It is not a quality sibling of [synthetic_reasoning](synthetic_reasoning.md), which uses the same "synthetic" HELM tag for LIME-style symbolic tasks. No inspect_evals, lm-eval or OpenCompass task with this name was found. No successor replaced it; HELM simply stopped active development in June 2026.

## Saturation and contamination

Saturation does not apply in the usual score-ceiling sense. A faster stack can always move the number. Prompts are public, gold strings are empty, and the interesting quantity is wall-clock time, which is not memorized from a test file. Provider-side caching of repeated prompts is a more realistic confound than training-set leakage.

## How to run it

HELM classic run spec `synthetic_efficiency` takes `num_prompt_tokens`, `num_output_tokens`, `tokenizer` and optional `random`. The scenario asserts the tokenizer is one of the twelve names above. Adapter is completion; `max_tokens` follows `num_output_tokens` when set. Compare only runs that share tokenizer, length pair, hardware notes and HELM version. Do not read the attached exact_match column as a capability score.

## Reading the numbers

A useful plot is runtime against prompt or output length on one stack, or idealized runtime across open models on the same A100 recipe. A single millisecond figure without those knobs is not comparable. Exact_match near zero is expected because the reference is empty. For quality, use a different HELM scenario. For efficiency of a chat API, this 2022 probe is a controlled slice, not a production load test.
