---
id: synthetic_reasoning
name: "Synthetic reasoning (HELM, abstract symbols)"
aliases:
  - "HELM synthetic reasoning"
  - "synthetic_reasoning (symbolic)"
  - "Synthetic reasoning (abstract symbols)"
page_kind: benchmark
category: reasoning
subcategory: "LIME-style pattern match, variable substitution and rule induction over abstract symbols"
status: unknown
summary: "HELM LIME-style synthetic tasks: match a pattern, substitute variables, or induce a rule over abstract symbols."
measures: >
  synthetic_reasoning is HELM's abstract-symbol reasoning scenario, inspired by LIME (Wu et al.,
  2021). Each item is built from a shuffled pattern of rule symbols X/Y/Z and math symbols
  +,-,*,=, a substitution dictionary into animal and fruit words, and the string after
  substitution. Three modes exist in code: pattern_match (pick the matching rule from four
  candidates), variable_substitution (apply a dictionary to a rule), and induction (recover
  the rule from two substituted results). English words appear only as substitution fillers.
  The symbols are synthetic.
task_format: >
  Open generation. Run spec synthetic_reasoning:mode={variable_substitution, pattern_match,
  induction}. Instruction "Please solve the following problem.", output noun Target, 5 in-context
  examples, stop at newline, max_tokens 50. HELM main_split is test.
metric:
  name: "quasi_exact_match (schema); run spec attaches exact-match metrics"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_classic.yaml names quasi_exact_match on test. get_synthetic_reasoning_spec uses
    get_exact_match_metric_specs() plus generative-harms metrics. The paper discusses accuracy.
    Report which column you read. Pattern-match items have four candidate rules, but no official
    random baseline is stated. No human baseline is given.
dataset:
  size: 5000
  size_note: >
    SyntheticReasoningScenario generates 1,000 train, 5,000 validation and 5,000 test instances
    per mode with numpy RandomState(42). size is the 5,000-item test split HELM scores. Three
    modes exist, so a full three-mode run scores 15,000 test items. There is no downloaded
    corpus; items are created at runtime from ANIMALS, FRUITS, RULE_SYMBOLS and MATH_SYMBOLS.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_reasoning_scenario.py"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "train 1,000 / valid 5,000 / test 5,000 per mode"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM)"
  authors:
    - "Eric Zelikman"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_reasoning_scenario.py"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/synthetic_reasoning_scenario.py"
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
    The HELM paper reports 2022-era figures: no model above 40% on abstract symbols except
    text-davinci-002 at 47.3% and code-davinci-002 at 55.0%. Those are not a current top.
    No numeric cell was read from the JavaScript classic leaderboard.
contamination:
  risk: medium
  note: >
    Items are generated at runtime from public code and seed 42, so the test set is
    reproducible from the repository. There is no separately held-out file. The canary
    practice used in BIG-bench is not used here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "synthetic_reasoning"
  opencompass: ""
  bigbench: ""
  other: "Run spec synthetic_reasoning:mode={variable_substitution|pattern_match|induction}; 5-shot generation; exact-match metrics."
tags:
  - reasoning
  - synthetic
  - helm
  - pattern-matching
  - induction
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/synthetic_reasoning_scenario.py"
    title: "synthetic_reasoning_scenario.py (three modes, 1000/5000/5000 splits, LIME citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "classic_run_specs.py get_synthetic_reasoning_spec (5-shot, max_tokens 50, exact match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "schema_classic.yaml (display name abstract symbols; quasi_exact_match; test split)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (Liang et al., 2022)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.09110"
    title: "HELM paper HTML (LIME primitives; 47.3%/55.0% 2022-era abstract-symbol scores; Zelikman credit)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2101.06223"
    title: "LIME: Learning Inductive Bias for Primitives of Mathematical Reasoning (Wu et al., 2021)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode 2026-06-01)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-015 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-015"
---

## What it measures

synthetic_reasoning asks a model to manipulate a tiny symbolic language. A pattern is a shuffled mix of rule letters X, Y, Z and operators +, -, *, =. A dictionary replaces those letters with one- or two-word animal or fruit strings. In `pattern_match` the model sees four candidate patterns and one substituted result and must name the matching pattern. In `variable_substitution` it sees a pattern and a dictionary and must emit the result. In `induction` it sees two results from the same pattern and must emit the pattern. Fillers are English words; the skill is copy, replace and induce, not world knowledge.

## How it is scored

The default HELM run is five-shot generation with instruction "Please solve the following problem.", output noun Target, stop at newline, and at most 50 tokens. schema_classic.yaml headlines `quasi_exact_match` on the test split. The run spec attaches `get_exact_match_metric_specs()` and generative-harms metrics. The paper talks about accuracy. Those names are close but not identical. Pattern-match chance is not published; there are four listed rules in the generator. Always name the `mode`.

## Dataset and licence

The scenario builds 1,000 train, 5,000 validation and 5,000 test items per mode with `RandomState(42)`. HELM scores test, so the headline count is 5,000 per mode. A three-mode suite is 15,000 scored items. There is no static download. HELM's repository is Apache-2.0; the strings are generated from lists in the scenario file. The paper appendix for this scenario describes pattern matching and variable substitution, while the same paper's reasoning chapter describes a separate `rule_induct` induction task. The shipped code exposes all three as `mode` values of this scenario.

## Who publishes it

Stanford CRFM released it with HELM (arXiv 2211.09110, submitted 16 November 2022). Author contributions credit Eric Zelikman for implementing the synthetic reasoning scenarios. The design follows LIME (Wu et al., 2021, arXiv 2101.06223). schema_classic.yaml still uses the display name "Synthetic reasoning (abstract symbols)". HELM entered maintenance mode on 1 June 2026.

## Lineage

This id is the abstract-symbol scenario, not HELM `synthetic_reasoning_natural` (natural-language templates; no page in this repository) and not [melt_srn](melt_srn.md), which is a Vietnamese MELT variant of the natural-language task. It is also not [synthetic_efficiency](synthetic_efficiency.md). Dyck languages and bAbI appear beside it in HELM's reasoning chapter as other synthetic probes; they have their own pages where they exist. No successor replaced it.

## Saturation and contamination

The only dated scores opened here are 2022-era: the paper says only text-davinci-002 (47.3%) and code-davinci-002 (55.0%) exceeded 40% on abstract symbols. That is not a current ceiling. Items can be regenerated from public code and seed 42, so a trainer who runs the scenario can put the test strings in a corpus. There is no hidden split.

## How to run it

HELM run spec `synthetic_reasoning:mode=` one of `variable_substitution`, `pattern_match`, `induction`. Do not average modes unless the report says so. Five-shot and a 50-token cap are the classic defaults; changing either moves exact match. lm-eval, inspect_evals and OpenCompass were not found for this name.

## Reading the numbers

A high score means the model can copy and replace in a tiny closed language, or recover a shuffled template from two examples. It does not mean algebraic word-problem skill, legal reasoning, or natural-language deduction. Compare only the same `mode` and the same metric column. For Vietnamese natural-language synthetic rules see [melt_srn](melt_srn.md), which is a different task.
