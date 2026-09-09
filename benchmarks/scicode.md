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
  subfields across five natural-science domains — physics, mathematics, materials science, biology
  and chemistry — contributed and reviewed by working scientists rather than adapted from textbooks
  or competitive-programming sites. Each of the 80 main problems is broken into a sequence of smaller
  subproblems (a median of 3, up to 15), mirroring how a scientist would actually decompose a research
  task: implement one function, then another, then integrate them into a full solution. Every
  subproblem and main problem ships with an optional block of scientist-written background knowledge
  and a docstring specifying the required input/output behaviour, plus gold-standard reference code
  and test cases. Later subproblems typically depend on earlier ones within the same main problem, so
  a model's own earlier mistakes can cascade forward.
task_format: >
  Code generation, zero-shot: for each subproblem the model is given a docstring (and, in the
  with-background setting, scientist-written background text) plus code for that main problem's
  earlier subproblems, and must write the next Python function. A subproblem is judged correct if the
  generated function passes its held-out test cases. A main problem is judged correct only if every
  one of its subproblems is correct and the fully integrated solution also passes. Artificial
  Analysis reports only subproblem pass@1 and always includes the scientist-annotated background.
metric:
  name: "pass@1 on test-set subproblems (Artificial Analysis); publisher also reports main-problem resolve rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No human-performance figure was found. Under the paper's standard setting (no background,
    carrying the model's own earlier subproblem code), Claude 3.5 Sonnet solved 4.6% of main
    problems; with scientist-written background the best main-problem result in that paper is 12.3%.
    The publisher leaderboard (last news 2025-02-01) lists OpenAI o3-mini-low at 10.8% main-problem
    / 33.3% subproblem in the standard setting. Artificial Analysis's dated Intelligence Index v4.2
    chart (2026-09-04) reports GPT-6 Astra (max) at 56% and GLM-5.3 (max) at 59% subproblem pass@1
    under AA's implementation (background on, three repeats, 288 test subproblems). There is no
    meaningful random baseline for free-form code generation.
dataset:
  size: 338
  size_note: >
    338 subproblems decomposed from 80 main problems, confirmed from the paper, the project site,
    and the GitHub README. Hugging Face datasets-server reports 80 rows (validation 15, test 65),
    matching the paper's 15-main / 50-subproblem development split and 65-main / 288-subproblem
    test split. Each main problem has a median of 3 subproblems and a maximum of 15. Full local
    evaluation additionally requires a numeric test-data file (test_data.h5) distributed via Google
    Drive rather than through the Hugging Face dataset or GitHub repository directly.
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
  org: "University of Illinois Urbana-Champaign, Argonne National Laboratory, Carnegie Mellon University, and a multi-institution scientist collaboration"
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
  top_score: null
  as_of: "2026-09"
  note: >
    The dated Artificial Analysis Intelligence Index v4.2 chart (published 2026-09-04) reports
    GPT-6 Astra (max) at 56% and GLM-5.3 (max) at 59% subproblem pass@1 under AA's implementation.
    Those two values are the accepted current pair; they are chart precision, not live-table
    figures, and they are not a claim that 56% is the highest bar on that figure. 56% is well
    below 100%, so the evaluation still has headroom. The publisher's own leaderboard (read
    2026-09-08; last GitHub news 2025-02-01) lists OpenAI o3-mini-low at 10.8% main-problem resolve
    and 33.3% subproblem resolve in the standard no-background setting. That grain is stricter
    than AA's with-background subproblem pass@1 and must not be mixed with it. Execution dates
    and hidden prompt pins for the AA runs are not disclosed.
contamination:
  risk: medium
  note: >
    Problems were newly authored and reviewed by scientist contributors, and the paper states they
    were curated to have zero overlap with then-public datasets. Against that, gold-standard
    reference solutions and test cases are fully public on GitHub and Hugging Face (Hub card
    Apache-2.0; the Hub viewer shows a public general_solution field). inspect_evals warns that
    the 15-problem development split was released with solution code and is easier. Exposure of
    the exact problems and solutions in later training is a realistic risk that grows over time.
harness:
  lm_eval: ""
  inspect_evals: "scicode"
  helm: ""
  opencompass: "SciCode"
  bigbench: ""
  other: >
    inspect_evals' scicode task defaults to provide_scientific_background=False (the paper's harder
    standard setting), timeout=300, include_dev_set=False (65 test main problems), Docker sandbox,
    and reports percentage_main_problems_solved and percentage_subproblems_solved. OpenCompass
    config SciCodeDataset/SciCodeEvaluator defaults to with_bg=False. The project's own
    inspect_ai runner (eval/inspect_ai/scicode.py) is the repository's recommended path and is not
    identical to the community inspect_evals package. Artificial Analysis uses a different profile:
    dataset v1.0.1, 288 test subproblems, three repeats, pass@1 subproblem scoring, scientist-annotated
    background always on, isolated executors, 300-second timeout, no tools. Index v4.2 raised that
    timeout from 60s and isolated script execution so slow-but-correct code is no longer scored as
    failed, then regraded.
tags:
  - coding
  - science
  - multi-step
  - subproblem-decomposition
  - pass-at-1
  - sandboxed-execution
sources:
  - url: "https://arxiv.org/abs/2407.13168"
    title: "SciCode: A Research Coding Benchmark Curated by Scientists (arXiv abstract: 338/80 figures, 4.6% headline, 18 Jul 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2407.13168"
    title: "SciCode paper HTML (dev/test split, median 3 / max 15 subproblems, standard vs with-background pass@1 tables)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/scicode-bench/SciCode/main/README.md"
    title: "scicode-bench/SciCode GitHub README (NeurIPS D&B 2024, official table, inspect_ai, Google Drive test_data.h5)"
    accessed: "2026-09-08"
  - url: "https://scicode-bench.github.io/"
    title: "SciCode project site (30-author affiliations, 16 subfields, five named domains in Table 1)"
    accessed: "2026-09-08"
  - url: "https://scicode-bench.github.io/leaderboard/"
    title: "Official SciCode leaderboard (o3-mini-low 10.8% main / 33.3% subproblem, standard setting)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/SciCode1/SciCode"
    title: "SciCode1/SciCode dataset API (apache-2.0, problems_dev.jsonl / problems_test.jsonl, 19655 downloads)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=SciCode1/SciCode"
    title: "datasets-server size (80 rows; validation 15, test 65)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/SciCode1/SciCode"
    title: "SciCode1/SciCode Hub card and viewer (gold general_solution field is public)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2"
    title: "Artificial Analysis Intelligence Index v4.2 (4 Sep 2026; SciCode sandbox/timeout regrade; dated per-model chart)"
    accessed: "2026-09-08"
  - url: "https://cdn.sanity.io/images/6vfeftx9/articles/971805b0a4b0877da6653842f240267721a56498-2256x4032.png?auto=format&w=1200"
    title: "AA v4.2 Intelligence Evaluations chart (SciCode panel: GPT-6 Astra (max) 56%, GLM-5.3 (max) 59%)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/methodology/intelligence-benchmarking#scicode"
    title: "AA Intelligence Benchmarking methodology (SciCode: 288 test subproblems, 3 repeats, background on, 300s, v1.0.1)"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/evaluations/scicode"
    title: "AA SciCode evaluation page (independent evaluator; 288 test subproblems from 80 problems; not used for live scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/scicode/scicode.py"
    title: "inspect_evals scicode.py (provide_scientific_background default False, timeout 300, include_dev_set False)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/scicode/scorer.py"
    title: "inspect_evals scicode scorer.py (percentage_main_problems_solved and percentage_subproblems_solved)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/scicode/README.md"
    title: "inspect_evals scicode README (65 test problems; gold on the 15-problem dev split)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/scicode/scicode_gen_085b98.py"
    title: "OpenCompass scicode_gen_085b98.py (abbr SciCode, with_bg=False default)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build eligible run, scicode"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SciCode asks a model to write Python that solves research coding problems drawn from 16 subfields across physics, mathematics, materials science, biology, and chemistry. Working scientists wrote and reviewed the items; they are not contest problems or textbook recitations. Each of the 80 main problems splits into ordered subproblems (median 3, at most 15). The model implements one function per step, then integrates the pieces. Every step ships with a docstring, optional scientist-written background, gold reference code, and tests. Later steps usually depend on earlier ones, so errors cascade. That gap between subproblem and main-problem scores is the point of the design.

## How it is scored

A subproblem is pass@1 if its function passes every test case. A main problem is pass@1 only if every subproblem is correct and the integrated solution also passes. The paper's standard setting is zero-shot, without background, carrying the model's own earlier code into later steps. In that setting Claude 3.5 Sonnet solved 4.6% of main problems (26.0% of subproblems). Adding scientist-written background raised the paper's best main-problem result to 12.3%. The publisher leaderboard, last updated in its GitHub news on 2025-02-01, lists OpenAI o3-mini-low at 10.8% main-problem and 33.3% subproblem in the standard setting. The README introduction still calls o1-preview (7.7% main) the best model tested; the table is the ranking to use.

Artificial Analysis reports a different profile. It always includes scientist-annotated background, scores pass@1 on the 288 test subproblems only, runs three repeats, uses isolated executors with a 300-second timeout, and pins dataset v1.0.1. Index v4.2 raised that timeout from 60 seconds and isolated script execution so slow-but-correct code is no longer marked failed, then regraded. The dated v4.2 chart (4 September 2026) shows GPT-6 Astra (max) at 56% and GLM-5.3 (max) at 59%. Those runs are not compute-matched. Execution dates and hidden pins are not disclosed. Do not substitute later live-table values for that chart.

## Dataset and licence

The set is 338 subproblems from 80 main problems. Hugging Face `SciCode1/SciCode` is Apache-2.0, with datasets-server reporting 15 validation rows and 65 test rows, matching the paper's 50 / 288 subproblem split. Problem text is English; solutions are Python. Gold `general_solution` code is visible on the Hub. A full local run also needs `test_data.h5` from Google Drive, which is not in the GitHub tree or the Hub files.

## Who publishes it

SciCode is a 30-author collaboration led by Minyang Tian and Luyu Gao, with corresponding authors Tian, Hao Peng (Illinois), and Eliu Huerta (Argonne / Chicago). The paper is arXiv:2407.13168, posted 18 July 2024, and was accepted at the NeurIPS 2024 Datasets and Benchmarks Track. The project site and GitHub remain the publisher surfaces. Artificial Analysis is an independent evaluator, not the author.

## Lineage

No predecessor or successor id is established. The authors present SciCode as a response to coding benchmarks that capable models had already saturated, using unpublished research workflows instead of existing solved corpora. Related pages here that are not this item pool include [HumanEval](humaneval.md), [SWE-bench](swe_bench.md), [SciBench](scibench.md), and [SciKnowEval](sciknoweval.md). No SciCode subset (by domain or background flag) has a separate page.

## Saturation and contamination

AA's dated v4.2 pair is 56% for GPT-6 Astra (max) and 59% for GLM-5.3 (max), on subproblem pass@1 with background on. That is well below 100%, so status is open. The publisher board's 10.8% main-problem figure is a different, harder grain and is also far from a ceiling; its newest named models date to February 2025. Contamination risk is medium: items were newly written, but gold solutions and tests have been public since the 2024–2025 releases, and inspect_evals flags the 15-problem development split as gold-released and easier.

## How to run it

`inspect eval inspect_evals/scicode` defaults to no background, 300-second Docker timeout, and the 65-problem test set. inspect_evals treats a main problem as solved when every subproblem passes; the paper also requires the integrated main solution to pass. OpenCompass `SciCode` defaults to `with_bg=False`. The upstream repo's `inspect eval scicode.py` runner is a third path. Artificial Analysis's Index numbers use background on, three repeats, and the v1.0.1 sandbox. Compare scores only when the background flag, grain (main vs subproblem), timeout, and split match. No lm-evaluation-harness, HELM, or BIG-bench task was found.

## Reading the numbers

A "SciCode score" is at least four publisher numbers (background on or off, crossed with subproblem or main-problem pass@1) plus AA's separate with-background subproblem pass@1. 56% on AA v4.2 is not 56% of main problems, and it is not the paper's standard setting. A high subproblem score means the model often implements one specified function; a high main-problem score means it chained every step without a single failure. Read the official 10.8% next to the AA 56% only as two protocols, not as a jump on one scale. Look at [SciBench](scibench.md) or [HLE](hle.md) if the claim is scientific knowledge rather than scientific code.
