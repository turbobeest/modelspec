---
id: apps
name: "APPS (Automated Programming Progress Standard)"
aliases: []
page_kind: benchmark
category: coding
subcategory: "competitive programming, test-case graded"
status: superseded
summary: "10,000 Python coding problems scraped from competitive-programming and interview sites across three difficulty tiers, graded by executing generated code against held-out test cases."
measures: >
  APPS gives a model a natural-language description of a programming problem -- for interview- and
  competition-level problems, this includes a formal input/output specification, similar to what a
  competitive-programming judge shows a human contestant -- and the model must write a complete
  Python program that solves it. Problems are pulled from real competitive-programming and
  coding-interview sites rather than authored for the benchmark, and range from problems solvable
  with a few lines of code to substantial algorithmic challenges. The task mirrors how
  software-engineering candidates are screened: read a spec, write correct code, with no partial
  credit for code that merely looks plausible.
task_format: "Free-form Python code generation from a natural-language problem statement (plus a formal input/output spec for interview- and competition-level problems); not code completion."
metric:
  name: "strict accuracy / pass@k (fraction of problems whose generated code passes every held-out test case)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No random or human baseline applies to free-form code generation. The paper shows text-similarity metrics like BLEU are anticorrelated with true correctness on this dataset, so APPS is scored exclusively by executing generated code against test cases, never by comparing code text to a reference solution."
dataset:
  size: 10000
  size_note: "10,000 problems: 5,000 train / 5,000 test, stratified across three tiers -- introductory (3,639 total, 1,000 in test), interview (5,000 total, 3,000 in test) and competition (1,361 total, 1,000 in test). 131,777 test cases in total, about 21 per problem on average."
  url: "https://github.com/hendrycks/apps"
  license: "CC BY-SA 3.0 (dataset, per the paper, following source site Kattis's problem licence); the evaluation code is released separately under MIT, and the community codeparrot/apps mirror on Hugging Face is tagged MIT rather than CC BY-SA -- the two licence statements disagree and no source consulted resolves the conflict."
  languages: ["en"]
  modalities: ["text", "code"]
  splits: "train (5,000, with reference solutions) / test (5,000, test cases public but no reference solutions), each split across introductory/interview/competition tiers"
  public_test_set: true
publisher:
  org: ""
  authors: ["Dan Hendrycks", "Steven Basart", "Saurav Kadavath", "Mantas Mazeika", "Akul Arora", "Ethan Guo", "Collin Burns", "Samir Puranik", "Horace He", "Dawn Song", "Jacob Steinhardt"]
  url: "https://github.com/hendrycks/apps"
paper:
  title: "Measuring Coding Challenge Competence With APPS"
  arxiv: "2105.09938"
  url: "https://arxiv.org/abs/2105.09938"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/hendrycks/apps"
released: "2021-05"
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
  note: "No current top-score figure or actively maintained leaderboard was confirmed from a source opened during this research. The three tiers likely saturate at different rates -- introductory problems are simple enough that strong current code models plausibly solve most of them, while competition-level problems remain a real algorithmic challenge -- so a pooled score can mask a model that is strong on easy problems and weak on hard ones; no source consulted gave a current per-tier breakdown."
contamination:
  risk: high
  note: "All problems, training-set reference solutions, and test cases (for both splits) have been public on GitHub since 2021, and the source competitive-programming sites are themselves widely crawled. The paper's own mitigation was limited to filtering GitHub pretraining repositories matching keywords suggesting overlap with common programming exercises, which addresses only one route of exposure; no dedicated post-hoc APPS contamination study was found in the sources consulted."
harness:
  lm_eval: ""
  inspect_evals: "apps"
  helm: ""
  opencompass: "apps"
  bigbench: ""
  other: ""
tags: ["coding", "competitive-programming", "test-case-grading", "python", "pass-at-k"]
sources:
  - url: "https://arxiv.org/abs/2105.09938"
    title: "Measuring Coding Challenge Competence With APPS"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2105.09938"
    title: "Measuring Coding Challenge Competence With APPS (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/hendrycks/apps"
    title: "hendrycks/apps repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/codeparrot/apps"
    title: "codeparrot/apps dataset metadata (Hugging Face API)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/apps"
    title: "inspect_evals apps task directory"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/apps"
    title: "OpenCompass apps dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

APPS gives a model a natural-language description of a programming problem -- for interview- and competition-level problems, this includes a formal input/output specification, as a competitive-programming judge would show a human contestant -- and the model must write a complete Python program that solves it. Problems are pulled from real competitive-programming and coding-interview sites rather than authored for the benchmark, ranging from a few lines of code to substantial algorithmic challenges. The task mirrors how software-engineering candidates are screened: read a spec, write correct code, with no partial credit for code that merely looks plausible.

## How it is scored

A generated program is graded by executing it against held-out input/output test cases and checking whether every output matches exactly; the paper shows text-similarity metrics like BLEU are anticorrelated with true correctness here, so APPS is scored exclusively by execution, never by comparing generated code text to a reference solution. The headline "strict accuracy" metric is the fraction of problems whose generated solution passes every test case; a separate "pass@k" variant credits a problem as solved if any of k sampled solutions passes, most often at k=1 or via the width-5 beam search the original paper used. Across the 10,000 problems there are 131,777 test cases in total, about 21 per problem on average, though the paper notes this conceals wide variance.

## Dataset and licence

APPS totals 10,000 problems split evenly into 5,000 for training and 5,000 for test, stratified across three difficulty tiers: introductory (3,639 problems total, 1,000 in test), interview (5,000 total, 3,000 in test) and competition (1,361 total, 1,000 in test). Training problems include reference solutions; test problems do not, though their held-out test cases are distributed as part of the public dataset rather than kept server-side. The paper states the dataset itself is licensed CC BY-SA 3.0, following the terms of Kattis, one of its major source sites, while the evaluation code is released separately under the MIT licence; the community `codeparrot/apps` mirror on Hugging Face is tagged MIT rather than CC BY-SA, so the two licence statements disagree and no source consulted resolves the conflict.

## Who publishes it

APPS was published as "Measuring Coding Challenge Competence With APPS" at the NeurIPS 2021 Datasets and Benchmarks Track, by Dan Hendrycks, Steven Basart, Saurav Kadavath, Mantas Mazeika, Akul Arora, Ethan Guo, Collin Burns, Samir Puranik, Horace He, Dawn Song and Jacob Steinhardt; author affiliations were not confirmed from a source opened during this research. The reference dataset, evaluation code and problem sources are maintained in Hendrycks' GitHub repository, github.com/hendrycks/apps.

## Lineage

APPS has no formal predecessor; it appeared alongside a wave of 2021 code-generation benchmarks, most notably OpenAI's HumanEval (`humaneval`, in this repository), which tests function-level code completion rather than full competitive-programming solutions. Neither HumanEval nor MBPP (`mbpp`, also here) formally succeeds APPS, but both are now more commonly reported for general code generation, while agentic and repository-scale evaluation has moved to SWE-bench (`swe_bench`, in this repository) and LiveCodeBench, which has no page here yet. No successor or variant id is formally tracked for APPS.

## Saturation and contamination

No current top-score figure or actively maintained leaderboard was confirmed from a source opened during this research. The three difficulty tiers likely saturate at different rates: introductory problems are simple enough that strong current code models plausibly solve most of them, while competition-level problems remain a real algorithmic challenge, so a single pooled APPS accuracy can mask a model that is strong on easy problems and weak on hard ones. All problems, reference solutions (for training problems) and test cases have been public on GitHub since 2021, and the source competitive-programming sites are themselves widely crawled, so contamination through pretraining on either the benchmark itself or the original web problem pages is plausible; the paper's own mitigation was limited to filtering GitHub pretraining repositories matching keywords suggesting overlap with common programming exercises, which addresses only one route of exposure.

## How to run it

inspect_evals implements it as the `apps` task, defaulting to the interview-level split, extracting Python code from the model's response and assigning a binary correct/incorrect score per problem by executing it against that problem's test cases under a 120-second timeout; a `level` parameter switches between introductory, interview and competition problems. OpenCompass carries generative configurations (`apps_gen`, `apps_mini_gen`) alongside several deprecated variants. Because strict accuracy, pass@1 and pass@k with varying k and sampling temperature are all reported under the name "APPS score" in different papers, and reporters do not always state which difficulty tier or split they used, treat cross-paper APPS comparisons as unsafe unless the sampling method and tier are both stated.

## Reading the numbers

A strong pooled APPS score says a model can turn a competitive-programming problem statement into working, test-passing code more often than not, a meaningfully harder bar than a short function-completion benchmark like HumanEval. Because the three tiers are pooled by default, check the per-tier breakdown when available: competition-level accuracy is more informative for frontier-model comparisons, since introductory problems are close to solved for capable current models. As with most benchmarks public for several years, treat a very high score with some caution absent corroboration from a fresher coding benchmark.
