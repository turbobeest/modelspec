---
id: srbench
name: "SRBench"
aliases:
  - "SRBench: A Living Benchmark for Symbolic Regression"
  - "Symbolic Regression Benchmark"
page_kind: benchmark
category: math
subcategory: "symbolic regression from numeric data (LLM equation-discovery adaptation)"
status: active
summary: "OpenCompass's LLM adaptation of the SRBench symbolic-regression project: given numeric input-output samples, a model must output a closed-form formula, scored by fit quality and symbolic equivalence."
measures: >
  SRBench (as run by OpenCompass) gives a model a table of numeric input-output samples drawn
  from a known physics equation and asks it to infer a closed-form symbolic formula using a
  restricted operator set (+, -, *, /, exp, sqrt, sin, arcsin and constants). This adapts the
  Feynman Symbolic Regression Database, the ground-truth physics-equation portion of the original
  SRBench project, into a prompted LLM task: the model sees example (x, y) pairs and must recover
  the underlying formula well enough to predict held-out points, rather than being told the
  equation's functional form.
task_format: >
  Free-form text generation: the model reads two prompts describing the input variables and
  sample values, then must output only the inferred formula string. OpenCompass's config draws
  300 random samples per problem and splits them roughly 97%/3% for the model to fit against and
  be evaluated on. No retrieval or tool use is part of the default config (ZeroRetriever,
  GenInferencer).
metric:
  name: "RMSE / NMSE / R² plus symbolic-equivalence match"
  direction: lower_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    OpenCompass's SRbenchDatasetEvaluator parses the model's output formula with SymPy, evaluates
    it against held-out numeric samples to compute RMSE, NMSE and R², and separately checks
    symbolic equivalence to the ground-truth formula. Invalid or non-finite predictions fall back
    to a mesh-grid sampling check. No random or human baseline was read from a source opened for
    this page; direction is lower-is-better for the error metrics (RMSE/NMSE) and higher-is-better
    for R² and the equivalence match, so a single "direction" here should not be read as covering
    every reported number.
dataset:
  size: null
  size_note: >
    The original SRBench (v2.0, La Cava et al. 2021) project spans 252 PMLB regression problems,
    split between 130 datasets with a known ground-truth model (Feynman physics equations and
    ODE-Strogatz systems) and 122 real-world "black-box" datasets without one. OpenCompass's
    integration (added via GitHub PR #2105, June 2025) specifically loads
    `Feynman/FeynmanEquations.csv`, i.e. the Feynman ground-truth subset, not the full 252-problem
    set or the black-box datasets; an exact count of Feynman equations used by the OpenCompass
    config was not independently confirmed from a source opened for this page.
  url: "https://github.com/cavalab/srbench"
  license: "GPL-3.0"
  languages:
    - en
  modalities:
    - text
  splits: "OpenCompass draws 300 samples per equation and splits roughly 97% fit / 3% held-out per problem; this is an OpenCompass-defined split, not one from the original SRBench release."
  public_test_set: true
publisher:
  org: "University of Pennsylvania (Cava Lab) and collaborators; OpenCompass LLM adaptation by Shanghai AI Laboratory / open-compass"
  authors:
    - "William La Cava"
    - "Patryk Orzechowski"
    - "Bogdan Burlacu"
    - "Fabrício Olivetti de França"
    - "Marco Virgolin"
    - "Ying Jin"
    - "Michael Kommenda"
    - "Jason H. Moore"
  url: "https://github.com/cavalab/srbench"
paper:
  title: "Contemporary Symbolic Regression Methods and their Relative Performance"
  arxiv: "2107.14351"
  url: "https://arxiv.org/abs/2107.14351"
  year: 2021
leaderboard_url: "http://cavalab.org/srbench/"
repo_url: "https://github.com/cavalab/srbench"
released: "2021-07"
last_updated: "2025-06"
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
    No LLM leaderboard score on OpenCompass's srbench adaptation was read from a source opened
    for this page. The original SRBench project itself is a "living benchmark" that has been
    updated since 2021 (a 2025 GECCO-companion follow-up paper, arXiv:2505.03977, calls for a
    next-generation version), which is a different question from whether the specific
    LLM-prompted OpenCompass adaptation is saturated; that was not established here.
contamination:
  risk: medium
  note: >
    The Feynman equation set is a long-public physics formula collection (the AI Feynman project
    and SRBench have both republished it since around 2020), so the closed-form equations
    themselves are almost certainly in LLM pretraining corpora. Because OpenCompass presents the
    task as numeric curve-fitting from sampled points rather than asking the model to name a
    known formula directly, memorised knowledge of "the Feynman equations" could still let a
    model shortcut the intended data-driven inference, which the original protocol was not
    designed to guard against the way newer LLM-specific symbolic-regression benchmarks are.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "srbench"
  bigbench: ""
  other: "OpenCompass configs: srbench_gen.py and srbench_rawprompt_gen.py in configs/datasets/srbench; dataset loader opencompass/datasets/srbench.py reads formula_data.json derived from Feynman/FeynmanEquations.csv, added in PR #2105 (June 2025) and updated in PR #2154 and PR #2407."
tags:
  - symbolic-regression
  - math
  - equation-discovery
  - physics
  - numeric-reasoning
sources:
  - url: "https://arxiv.org/abs/2107.14351"
    title: "Contemporary Symbolic Regression Methods and their Relative Performance (arXiv:2107.14351), NeurIPS 2021 Datasets and Benchmarks track, 252 PMLB problems, 14 SR methods"
    accessed: "2026-09-08"
  - url: "https://github.com/cavalab/srbench"
    title: "cavalab/srbench GitHub repository (GPL-3.0 licence, v2.0 vs 2025 edition citations, PMLB-based dataset composition)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/srbench"
    title: "OpenCompass srbench config directory listing (srbench_gen.py, srbench_rawprompt_gen.py)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/srbench/srbench_gen.py"
    title: "OpenCompass srbench_gen config (opencompass/srbench dataset path, prompt1/prompt2/formula fields, SRbenchDatasetEvaluator, restricted operator set)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/srbench.py"
    title: "OpenCompass SRbenchDataset/SRbenchDatasetEvaluator source (300-sample draw, 97/3 split, RMSE/NMSE/R2, SymPy symbolic-equivalence check)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/pull/2105"
    title: "OpenCompass PR #2105 \"SRbench\" (confirms Feynman/FeynmanEquations.csv as the loaded data source, merged June 2025)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-003"
---

## What it measures

SRBench as run through OpenCompass tests symbolic regression: recovering a closed-form mathematical formula from numeric data alone. The model is shown sample input-output pairs generated from a real physics equation drawn from the Feynman Symbolic Regression Database and must output a formula, built only from a restricted operator set (addition, subtraction, multiplication, division, exp, sqrt, sin, arcsin and numeric constants), that fits the pattern. This is a genuinely different skill from most math benchmarks on this page's schema: the model is not solving a stated problem but performing inductive curve-fitting from raw numbers, closer to a scientist's equation-discovery task than to arithmetic or word-problem solving.

The name and Feynman-equation dataset trace back to the original SRBench project (La Cava et al., NeurIPS 2021 Datasets and Benchmarks track), which was built to benchmark dedicated symbolic-regression algorithms, not LLMs. OpenCompass's integration repurposes only the Feynman ground-truth subset of that project into an LLM-prompted task; it does not use SRBench's real-world "black-box" datasets or its original algorithm-comparison protocol.

## How it is scored

OpenCompass draws 300 numeric samples per equation and splits them roughly 97% for the model to see and 3% held out. The model's output formula string is parsed with SymPy and evaluated against the held-out points to compute RMSE, NMSE and R²; predictions that fail to parse or produce non-finite values fall back to a mesh-grid sampling check rather than an automatic zero score. A separate symbolic-equivalence check compares the parsed formula to the known ground truth. This differs sharply from the original SRBench protocol, which ran dedicated symbolic-regression algorithms (genetic programming and related methods) directly on the full sample set and compared fit quality and model simplicity across methods, not LLMs prompted with a fixed sample/prediction split.

## Dataset and licence

The upstream `cavalab/srbench` project (v2.0, 2021) spans 252 PMLB-hosted regression problems: 130 with a known ground-truth model (drawn from the Feynman physics-equation database and the ODE-Strogatz repository) and 122 real-world "black-box" datasets without one. OpenCompass's PR #2105 specifically loads `Feynman/FeynmanEquations.csv`, i.e. only the Feynman ground-truth subset, not the full 252-problem collection or the black-box half. An exact count of equations used in the OpenCompass config was not confirmed from a source opened for this page. The `cavalab/srbench` GitHub repository is licensed GPL-3.0.

## Who publishes it

The original SRBench paper is by William La Cava, Patryk Orzechowski, Bogdan Burlacu, Fabrício Olivetti de França, Marco Virgolin, Ying Jin, Michael Kommenda and Jason H. Moore, published at the NeurIPS 2021 Track on Datasets and Benchmarks (arXiv:2107.14351). The project describes itself as a "living benchmark," with a 2025 GECCO-companion follow-up (arXiv:2505.03977) proposing a next-generation edition. The LLM-prompted adaptation used by OpenCompass was contributed separately by OpenCompass community members (GitHub users soki123, Myhs-phz and MaiziXiao) via PR #2105 in June 2025, and is maintained by the OpenCompass project (Shanghai AI Laboratory), not by the original SRBench authors.

## Lineage

This page documents OpenCompass's `srbench` LLM adaptation of the original SRBench symbolic-regression project; no other id in this repository derives from it. It should not be confused with the newer, LLM-native "LLM-SRBench" (ICML 2025, deep-symbolic-mathematics/llm-srbench), a differently constructed 239-problem benchmark specifically designed to resist LLM memorisation of canonical formulas; that is a separate project with a similar name and no page in this repository yet.

## Saturation and contamination

No specific LLM leaderboard score for OpenCompass's srbench adaptation was found in a source opened for this page, so saturation status is left unknown. The original SRBench project remains actively maintained and has itself been revised since 2021, which speaks to the algorithm-benchmarking side, not to how saturated the OpenCompass LLM-prompt version is. Contamination risk is medium: the Feynman equations are long-public, well-known physics formulas that have circulated since around 2020 via the AI Feynman project and SRBench itself, so a model could plausibly recognise the equation from its numeric pattern (or even guess a canonical formula) using memorised physics knowledge rather than by performing genuine data-driven symbolic regression, which the original benchmark protocol was not built to detect.

## How to run it

OpenCompass provides two configs, `srbench_gen.py` and the newer `srbench_rawprompt_gen.py` (added March 2026 per commit history), both reading from the `opencompass/srbench` Hugging Face dataset and applying `SRbenchDatasetEvaluator`. Running the original SRBench project directly requires the `cavalab/srbench` repository and its PMLB-based experiment pipeline, which benchmarks dedicated SR algorithms rather than prompted LLMs and is a substantially different setup from OpenCompass's adaptation. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation of either version was found.

## Reading the numbers

A strong score on OpenCompass's srbench means a model proposed a formula that fits held-out numeric samples well and, ideally, is symbolically equivalent to the true underlying equation, not just numerically close on the observed range. Because the operator set is restricted and the source equations are well-known physics formulas, treat a high score with some caution: it may reflect the model recalling a canonical formula rather than performing genuine inductive regression from the sampled points, especially for shorter, famous equations. This adaptation is not the same benchmark as the original algorithm-focused SRBench leaderboard at cavalab.org/srbench, and scores are not comparable between the two; always check whether a reported "SRBench" number describes classic SR-algorithm methods or this LLM-prompted variant.
