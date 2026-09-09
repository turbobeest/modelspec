---
id: simple_safety_tests
name: "SimpleSafetyTests"
aliases:
  - "SST"
  - "Simple Safety Tests"
  - "simple_safety_tests"
page_kind: benchmark
category: safety
subcategory: "100-prompt English refusal suite across five high-severity harm areas"
status: active
summary: "A 100-prompt English suite of requests that models should refuse, covering five high-severity harm areas."
measures: >
  SimpleSafetyTests (SST) gives a model a single-turn English prompt that, for
  almost all applications, should be refused. The 100 handcrafted items cover
  five harm areas: suicide, self-harm and eating disorders; physical harm;
  illegal and highly regulated items; scams and fraud; and child abuse. Half
  the prompts seek information or advice; half ask for instructions or actions.
  The original paper grades whether the response is unsafe. HELM grades refusal
  with two LLM judges and reports a 0-1 safety_score.
task_format: >
  Single-turn generation. HELM uses adapter generation, max_tokens 512,
  temperature 0, zero in-context examples, then SimpleSafetyTestsAnnotator
  (GPT and Llama judges). Paper protocol: trained human annotators, with and
  without a safety system prompt.
metric:
  name: "unsafe-response rate (paper); HELM safety_score is the near-complement on 0-1"
  direction: lower_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper's headline figure is the share of unsafe responses (lower is
    better). Across 15 models and two system-prompt setups, 20% of 3,000
    labelled responses were unsafe. Llama 2 13B and Claude 2.1 had no unsafe
    responses. Dolly v2 12B reached 69% without a safety prompt and 73% with
    one. A safety system prompt moved the overall rate from 25% to 16%. HELM
    instead reports safety_score, the mean
    of GPT-4o and Llama 3.1 judge ratings (1 safe, 0.5 maybe unsafe, 0 unsafe),
    so higher is better on that column.
dataset:
  size: 100
  size_note: >
    100 prompts. Hugging Face datasets-server: 100 test rows, five columns.
    CSV count: 20 prompts in each of five harm_area values, and 50/50 split
    of category "Information and advice seeking" vs "Instructions and actions".
    CSV harm_area "Physical Harm and Violence" is named "Physical Harm" on the
    dataset card and in the paper.
  url: "https://huggingface.co/datasets/Bertievidgen/SimpleSafetyTests"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "single test split; no train split"
  public_test_set: true
publisher:
  org: "Patronus AI, University of Oxford, Bocconi University"
  authors:
    - "Bertie Vidgen"
    - "Nino Scherrer"
    - "Hannah Rose Kirk"
    - "Rebecca Qian"
    - "Anand Kannappan"
    - "Scott A. Hale"
    - "Paul Rottger"
  url: "https://github.com/bertiev/SimpleSafetyTests"
paper:
  title: "SimpleSafetyTests: a Test Suite for Identifying Critical Safety Risks in Large Language Models"
  arxiv: "2311.08370"
  url: "https://arxiv.org/abs/2311.08370"
  year: 2023
leaderboard_url: "https://crfm.stanford.edu/helm/safety/latest/"
repo_url: "https://github.com/bertiev/SimpleSafetyTests"
released: "2023-11"
last_updated: "2024-03"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 0.0
  as_of: "2024-02"
  note: >
    Paper: Llama 2 13B and Claude 2.1 had 0% unsafe responses on these 100
    prompts, so the original unsafe-rate metric already hit the floor for some
    2023-2024 models. HELM still reports a 0-1 safety_score as one of five
    [helm_safety](helm_safety.md) scenarios; that aggregate is separately
    described as potentially saturated among leading models.
contamination:
  risk: medium
  note: >
    All 100 prompts are public on Hugging Face (created 2024-02-07) and GitHub.
    Providers may safety-tune against similar refusal items. Scoring depends on
    the response, not a fixed answer key, so prompt memorisation alone does not
    guarantee a safe score.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "simple_safety_tests"
  opencompass: ""
  bigbench: ""
  other: "HELM loads Bertievidgen/SimpleSafetyTests revision 98223c5d8c4059c8f4d8fe2fec8720ee8a20d3c5; run_entries_safety.conf lists it with bbq, harm_bench, anthropic_red_team, and xstest."
tags:
  - safety
  - refusal
  - llm-judge
  - helm
sources:
  - url: "https://arxiv.org/abs/2311.08370"
    title: "SimpleSafetyTests paper (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2311.08370"
    title: "SimpleSafetyTests paper full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Bertievidgen/SimpleSafetyTests/raw/main/README.md"
    title: "Hugging Face dataset card (100 prompts, five harm areas, cc-by-2.0 tag)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Bertievidgen/SimpleSafetyTests"
    title: "Hugging Face dataset API (created 2024-02-07, sha 98223c5d)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Bertievidgen/SimpleSafetyTests"
    title: "datasets-server size (100 test rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Bertievidgen/SimpleSafetyTests/resolve/main/sst_test_cases.csv"
    title: "sst_test_cases.csv (100 rows, 20 per harm area, 50/50 categories)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/bertiev/SimpleSafetyTests/main/README.md"
    title: "bertiev/SimpleSafetyTests README (CC-BY, five harm areas)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/bertiev/SimpleSafetyTests/main/LICENSE"
    title: "GitHub LICENSE (Creative Commons Attribution 4.0 International)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/simple_safety_tests_scenario.py"
    title: "HELM SimpleSafetyTestsScenario"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/simple_safety_tests_annotator.py"
    title: "HELM SimpleSafetyTestsAnnotator (GPT and Llama judges)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/safety_run_specs.py"
    title: "HELM simple_safety_tests run spec (max_tokens 512, temperature 0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/safety_metrics.py"
    title: "HELM SafetyScoreMetric (mean of judge scores, 0-1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_safety.conf"
    title: "HELM run_entries_safety.conf"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/safety/latest/"
    title: "HELM Safety leaderboard (JS shell; per-model cells not in static HTML)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/2024/11/08/helm-safety.html"
    title: "HELM Safety CRFM write-up (100 unsafe prompts; paper unsafe-rate protocol)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-072 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-072"
---

## What it measures

SimpleSafetyTests is a 100-prompt English refusal suite. Each prompt is a request that, for almost all applications, a model should refuse. The items are handcrafted and split across five high-severity harm areas: suicide, self-harm and eating disorders; physical harm; illegal and highly regulated items; scams and fraud; and child abuse. Fifty prompts ask for information or advice. Fifty ask for instructions or actions.

The paper tests 11 open models and four closed models, with and without a safety-emphasising system prompt. HELM reuses the same 100 prompts as the `simple_safety_tests` scenario inside [helm_safety](helm_safety.md). This page is that 100-prompt suite, not the five-scenario HELM mean. It is not [xstest](xstest.md), which tests over-refusal on safe-looking prompts, and it is not [harm_bench](harm_bench.md), which scores attack success on a larger behaviour list.

## How it is scored

The paper's metric is the share of responses labelled unsafe by trained annotators (lower is better). Annotators labelled 3,000 responses: 15 models, two system-prompt setups, 100 prompts. Overall, 20% were unsafe. Llama 2 13B and Claude 2.1 had none. Dolly v2 (12B) reached 69% without a safety prompt and 73% with one. Adding a safety system prompt cut the overall rate from 25% to 16% and did not zero it.

The authors also scored five automatic safety filters against those human labels. Perspective API reached 72% accuracy. A zero-shot GPT-4 prompt reached 89%. Those filter accuracies are not model safety scores.

HELM does not use the paper's human labels. `SimpleSafetyTestsAnnotator` sends the transcript to GPT and Llama judges with a 0 / 0.5 / 1 template (unsafe / maybe unsafe / safe). `SafetyScoreMetric` averages the judge scores into `safety_score` on 0-1, where higher is better. HELM generation uses max_tokens 512 and temperature 0. A HELM safety_score is not the paper's unsafe rate.

## Dataset and licence

The public set is 100 English prompts. The Hugging Face dataset `Bertievidgen/SimpleSafetyTests` has 100 test rows. The CSV has 20 prompts in each harm area and a 50/50 split of the two prompt categories. The CSV names one area "Physical Harm and Violence"; the paper and dataset card say "Physical Harm".

Licence is not recorded as a single SPDX id here. The Hub card tags `cc-by-2.0`. The GitHub `LICENSE` file is Creative Commons Attribution 4.0. The GitHub README says only "Licence is CC-BY". Prompts are public; there is no held-out answer key.

## Who publishes it

Bertie Vidgen, Nino Scherrer, Hannah Rose Kirk, Rebecca Qian, Anand Kannappan, Scott A. Hale, and Paul Röttger introduced the suite in arXiv 2311.08370 (14 November 2023; v2 16 February 2024). The ar5iv author line lists Patronus AI, University of Oxford, and Bocconi University. The reference GitHub repository is `bertiev/SimpleSafetyTests`. Stanford CRFM runs the prompts as one HELM Safety scenario and shows per-scenario numbers on the HELM Safety leaderboard.

## Lineage

SST has no family page. It sits beside [xstest](xstest.md), [harm_bench](harm_bench.md), and [anthropic_red_team](anthropic_red_team.md) on the HELM Safety run list, and those four plus BBQ are averaged in [helm_safety](helm_safety.md). XSTest is the over-refusal counterpart, not a successor. No replacement suite from the same authors was confirmed.

## Saturation and contamination

On the paper metric, some 2023-2024 models already scored 0% unsafe on these 100 items, so the original rate no longer separates every strong model. HELM's 0-1 judge score can still move when judges or decoding change. Contamination risk is medium: the prompts have been public since early 2024 and are short enough to appear in later safety-tuning data. Scoring still depends on the completion, not on matching a target string.

## How to run it

HELM's run spec name is `simple_safety_tests`. It loads `Bertievidgen/SimpleSafetyTests` at revision `98223c5d8c4059c8f4d8fe2fec8720ee8a20d3c5`. Matching HELM Safety also requires the two judge models named in `SafetyScoreMetric` metadata. The paper's human protocol is a different number. No lm-eval, inspect_evals, OpenCompass, or BIG-bench task name was confirmed. The prompts include child-abuse and self-harm content; treat the files as sensitive.

## Reading the numbers

A 0% unsafe rate on SST means the model refused or otherwise avoided unsafe completions on these 100 single-turn prompts under that grader. It does not mean the model is safe under jailbreaks, multi-turn pressure, or harm types SST does not cover. A high HELM `safety_score` can also come from blanket refusal; check [xstest](xstest.md) for that failure. Do not compare a paper unsafe rate with a HELM safety_score, and do not treat SST as the HELM Safety mean.
