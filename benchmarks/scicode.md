---
id: scicode
name: "SciCode"
aliases:
  - "SciCode: A Research Coding Benchmark Curated by Scientists"
page_kind: benchmark
category: coding
subcategory: "scientific research code generation, decomposed into ordered subproblems"
status: active
summary: >-
  SciCode decomposes 80 scientist-authored research coding problems into 338 subproblems; a main
  problem counts solved only when every subproblem and the full integration are correct.
measures: >
  SciCode asks a model to write Python code that solves real research problems drawn from 16
  subfields across five natural-science domains -- physics, math, materials science, biology and
  chemistry -- contributed and reviewed by working scientists rather than adapted from textbooks or
  competitive-programming sites. Each of the 80 "main problems" is broken into a sequence of smaller
  subproblems (a median of 3, up to 15), mirroring how a scientist would actually decompose a research
  task: implement one function, then another, then integrate them into a full solution. Every
  subproblem and main problem ships with an optional block of scientist-written background knowledge
  and a docstring specifying the required input/output behaviour, plus gold-standard reference code
  and test cases. Because later subproblems typically depend on earlier ones within the same main
  problem, a model's own earlier mistakes can cascade forward, which is central to why SciCode's
  headline scores are so much lower than its subproblem-level scores (see Reading the numbers).
task_format: >
  Code generation, zero-shot: for each subproblem the model is given a docstring (and, in the
  "with background" setting, scientist-written background text) plus the previously-generated code
  for that main problem's earlier subproblems, and must write the next Python function. A subproblem
  is judged correct if the generated function passes its held-out test cases; a main problem is judged
  correct only if every one of its subproblems is correct and the fully integrated solution also passes.
metric:
  name: "Pass@1, reported at two granularities: subproblem resolve rate and (stricter) main problem resolve rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    No human-performance figure was found; SciCode is scored purely against scientist-written
    reference solutions and test cases, with no reported human baseline run under exam-like
    conditions. The paper's headline number, in its "standard" (no background, without gold subproblem
    context) evaluation setting, is that the best model tested -- Claude 3.5 Sonnet -- solved only
    4.6% of main problems; providing scientist-written background knowledge raises the best main-problem
    result to 12.3%, still far from a ceiling. There is no meaningful random baseline for free-form
    code generation.
dataset:
  size: 338
  size_note: >
    338 subproblems decomposed from 80 main problems, confirmed from both the paper and the maintained
    GitHub repository. The repository reserves 15 main problems (50 subproblems) as a development split
    and the remaining 65 main problems (288 subproblems) as the test split, matching the Hugging Face
    dataset's two files (problems_dev.jsonl, problems_test.jsonl). Each main problem has a median of 3
    subproblems and a maximum of 15. Full local evaluation additionally requires a separate numeric
    test-data file (test_data.h5) distributed via Google Drive rather than through the Hugging Face
    dataset or GitHub repository directly, which some reproduction attempts may miss.
  url: "https://huggingface.co/datasets/SciCode1/SciCode"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "dev: 15 main problems / 50 subproblems; test: 65 main problems / 288 subproblems"
  public_test_set: true
publisher:
  org: "University of Illinois Urbana-Champaign, Carnegie Mellon University and a multi-institution scientist collaboration"
  authors:
    - "Minyang Tian"
    - "Luyu Gao"
    - "Shizhuo Dylan Zhang"
    - "Xinan Chen"
    - "Ofir Press"
    - "Jamie Callan"
    - "Eliu Huerta"
    - "Hao Peng"
  url: "https://scicode-bench.github.io/"
paper:
  title: "SciCode: A Research Coding Benchmark Curated by Scientists"
  arxiv: "2407.13168"
  url: "https://arxiv.org/abs/2407.13168"
  year: 2024
leaderboard_url: "https://scicode-bench.github.io/leaderboard/"
repo_url: "https://github.com/scicode-bench/SciCode"
released: "2024-07"
last_updated: "2025-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 10.8
  as_of: "2025-02"
  note: >
    Read directly from the project's live leaderboard (scicode-bench.github.io/leaderboard/, which
    matches the table in the GitHub README): the top-ranked model, OpenAI o3-mini-low, solves 10.8% of
    main problems (33.3% of subproblems) in the standard, no-background setting, with most other
    tested models well below that -- several score 0% on main problems despite solving a number of
    subproblems correctly. This is far from any ceiling. The most recent models on that table date to
    the repository's 2025-02-01 news entry (adding DeepSeek-R1, DeepSeek-V3 and OpenAI o3-mini); no
    newer frontier models appear on the leaderboard as of this research, so it may understate current
    frontier performance rather than reflecting a settled ceiling.
contamination:
  risk: medium
  note: >
    Problems were newly authored and reviewed by scientist contributors specifically for this
    benchmark rather than scraped from an existing solved-problem corpus, which limits direct
    memorisation risk relative to older, web-mined benchmarks. Against that, the dataset -- including
    its gold-standard reference solutions and test cases -- has been fully public on GitHub and
    Hugging Face since mid-2024 (19,000+ downloads recorded on the Hugging Face copy at the time of
    this research), and SciCode has become a common target for evaluating and, plausibly, for
    fine-tuning coding-oriented models, so exposure to its exact problems and solutions during later
    training is a realistic risk that grows over time.
harness:
  lm_eval: ""
  inspect_evals: "scicode"
  helm: ""
  opencompass: "SciCode"
  bigbench: ""
  other: >
    inspect_evals' `scicode` task takes a `provide_scientific_background` flag (default False, matching
    the paper's harder "standard" setting), runs generated code inside a Docker sandbox with a
    configurable timeout (default 300s), and reports both `percentage_main_problems_solved` and
    `percentage_subproblems_solved` as separate metrics, matching the paper's own two granularities.
    OpenCompass's config (`SciCodeDataset`/`SciCodeEvaluator`) also defaults to `with_bg=False`. The
    benchmark's own GitHub repository additionally ships its own, separate `inspect_ai`-based runner
    (`eval/inspect_ai/scicode.py`) as its currently recommended way to evaluate a new model, which
    predates and is not identical to the inspect_evals community package.
tags:
  - coding
  - science
  - multi-step
  - subproblem-decomposition
  - pass-at-1
  - sandboxed-execution
sources:
  - url: "https://arxiv.org/abs/2407.13168"
    title: "SciCode: A Research Coding Benchmark Curated by Scientists (arXiv abstract: authors, 338/80 figures, 4.6% headline result)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/abs/2407.13168"
    title: "SciCode paper (ar5iv full text: dev/test split sizes, standard vs. with-background setup, all pass@1 figures cited on this page)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/scicode-bench/SciCode/main/README.md"
    title: "scicode-bench/SciCode GitHub README (NeurIPS D&B Track 2024 acceptance note, leaderboard table, inspect_ai/OpenCompass integration notes, Google-Drive-hosted test data)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/SciCode1/SciCode"
    title: "SciCode1/SciCode dataset API record (apache-2.0 licence; problems_dev.jsonl / problems_test.jsonl files)"
    accessed: "2026-09-08"
  - url: "https://scicode-bench.github.io/leaderboard/"
    title: "Official SciCode leaderboard (rendered): current top score (o3-mini-low, 10.8% main / 33.3% subproblem) and full model ranking"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/scicode/scicode.py"
    title: "inspect_evals scicode.py task source (provide_scientific_background flag, Docker sandbox, timeout)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/scicode/scorer.py"
    title: "inspect_evals scicode scorer.py (percentage_main_problems_solved and percentage_subproblems_solved as separate metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/scicode/scicode_gen_085b98.py"
    title: "OpenCompass scicode_gen_085b98.py config (SciCodeDataset/SciCodeEvaluator, with_bg=False default)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SciCode asks a model to write Python code solving real research problems drawn from 16 subfields across five natural-science domains -- physics, math, materials science, biology and chemistry -- contributed and reviewed by working scientists rather than adapted from textbooks or competitive-programming sites. Each of the 80 "main problems" is broken into a sequence of smaller subproblems (median 3, up to 15), mirroring how a scientist decomposes a research task: implement one function, then another, then integrate the pieces into a full solution. Every subproblem and main problem ships with a docstring, an optional block of scientist-written background knowledge, and gold-standard reference code and test cases. Later subproblems typically depend on earlier ones, so a model's own earlier mistakes cascade forward -- central to reading a score correctly (see Reading the numbers).

## How it is scored

Grading happens at two granularities that produce very different numbers from the same run. A subproblem is scored correct (pass@1) if the generated function passes its held-out test cases in isolation. A main problem is scored correct only if every subproblem is correct and the fully integrated solution also passes -- a much stricter bar. The paper's headline "standard" setting evaluates zero-shot without background knowledge, carrying forward the model's own previously generated subproblem code as context for later steps -- the closest match, the authors say, to how a scientist would actually use the model. Under that setting, the best model tested, Claude 3.5 Sonnet, solved only 4.6% of main problems; adding background knowledge raises that best result to 12.3%. No human-performance figure was found.

## Dataset and licence

The dataset holds 338 subproblems decomposed from 80 main problems, split into a 15-problem (50-subproblem) development set and a 65-problem (288-subproblem) test set, released on Hugging Face under Apache-2.0 as two JSONL files matching that split. Problem text is English; solutions are Python. A full local evaluation additionally requires a separate numeric test-data file distributed via Google Drive rather than bundled with the dataset or repository -- a reproducibility detail worth knowing before assuming a from-source run works out of the box.

## Who publishes it

SciCode comes from a 30-author collaboration led by Minyang Tian, Luyu Gao and Shizhuo Dylan Zhang, with scientist co-authors across many institutions plus Ofir Press, Jamie Callan and Eliu Huerta, posted to arXiv in July 2024 and accepted at the NeurIPS 2024 Datasets and Benchmarks Track. The project maintains an active GitHub repository and a public leaderboard at scicode-bench.github.io, last updated per its own change log in February 2025 to add DeepSeek-R1, DeepSeek-V3 and OpenAI o3-mini results.

## Lineage

No predecessor or successor benchmark id was confirmed for SciCode; its authors position it as a response to earlier coding benchmarks becoming easy for capable models, staying hard by drawing problems from genuine research workflows rather than existing solved-problem corpora. No SciCode subset (by domain or background setting) has a separate page here; this page covers the benchmark as a whole.

## Saturation and contamination

Read directly from the project's live leaderboard, the top model (OpenAI o3-mini-low) solves 10.8% of main problems and 33.3% of subproblems in the standard setting, with most other tested models well below that and several at exactly 0% on main problems despite solving some subproblems -- clear headroom, so status is open. The most recent entries date to a February 2025 update; no newer frontier models appear as of this research, so the board may understate current performance. Contamination risk is medium: problems were newly authored rather than scraped from an existing corpus, limiting direct memorisation, but the dataset -- gold solutions and test cases included -- has been fully public since mid-2024, has accumulated substantial downloads, and is a natural fine-tuning target, so exposure risk grows over time.

## How to run it

inspect_evals' `scicode` task takes a `provide_scientific_background` flag (default False, the paper's harder standard setting), executes generated code inside a Docker sandbox with a configurable timeout (300s default), and reports both `percentage_main_problems_solved` and `percentage_subproblems_solved`, matching the paper's two granularities. OpenCompass's configuration also defaults to no background. The project's own GitHub repository additionally maintains a separate, currently-recommended `inspect_ai`-based runner bundled inside itself, which predates and is not identical to the community inspect_evals package -- worth checking which one a given score used. No lm-evaluation-harness, HELM or BIG-bench implementation was found.

## Reading the numbers

A "SciCode score" is really at least four different numbers, depending on two independent settings: with or without background knowledge, and subproblem- or main-problem-level pass@1. Subproblem scores are always much higher than main-problem scores from the same run -- solving roughly a third of subproblems with background knowledge translated to only about an eighth of full main problems -- because a main problem demands every subproblem plus their integration correct simultaneously, so error compounds. A high subproblem score shows a model can often implement one well-specified function correctly; a high main-problem score is the stronger claim that it can chain several together into a working pipeline without a single failure. Always check which of the four settings produced a reported number; with the current best result still around one main problem in ten, no version of this benchmark is close to saturated.
