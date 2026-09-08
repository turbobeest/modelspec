---
id: codeinsights_student_mistake
name: "CodeInsights Student Mistake"
aliases:
  - "CodeInsightsStudentMistakeScenario"
  - "codeinsights student mistake"
page_kind: benchmark
category: coding
subcategory: "HELM C++ student-mistake generation on a CodeInsight sample"
status: unknown
summary: "HELM scenario that asks a model to introduce a given student's typical C++ mistakes on a new problem, using three prior buggy submissions."
measures: >
  codeinsights_student_mistake is a Stanford HELM run spec on sampled CodeInsight course logs.
  For each retained student it shows a topic pass-rate profile and three earlier buggy C++
  submissions, then asks the model to attempt a fourth problem while inserting mistakes that
  student would likely make. The instruction forbids a fully correct solution. HELM scores the
  generated fragment against the student's actual mistaken response and against that student's
  unit-test pass pattern. It is error-pattern imitation, not generic bug finding, not the
  CodeInsight paper's next-attempt predictor, and not [ci_mcqa](ci_mcqa.md).
task_format: >
  English HELM instruction plus a Vietnamese/English problem prompt; model returns a fenced C++
  fragment for {{ STUDENT_ANSWER }}. Default temperature 0, max_tokens 4000, num_testcases=1.
metric:
  name: "composite: ast_distance, asm_distance, codebert_similarity, unittest_alignment_ratio"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Same comprehensive metric class as codeinsights_student_coding. The AST docstring treats
    1 as maximum difference, but HELM fills ast_distance and asm_distance with Levenshtein.ratio
    (similarity) and still writes 1.0 on parse or compile failure. CodeBERT and unit-test
    alignment are higher-is-better. No schema headline, random baseline or human baseline was
    found. A fully correct program can score poorly on alignment if the student had failed tests.
dataset:
  size: 41
  size_note: >
    Direct count of Kazchoko/my_dataset Scenario3_data.csv: 696 rows, 50 student_id values,
    175 question_unittest_id values. HELM groups by student, sorts by student_id,
    question_unittest_id and timestamp, skips students with fewer than four rows, and uses the
    fourth row as the target, yielding 41 instances at default num_testcases=1. Sample, not the
    full CodeInsight release (paper Table 1: 3,286 students / 3,074,795 submissions). The gated
    Hugging Face card instead describes 781 students in 2023–2024.
  url: "https://huggingface.co/datasets/Kazchoko/my_dataset"
  license: ""
  languages:
    - vi
    - en
  modalities:
    - text
    - code
  splits: "HELM VALID_SPLIT only; one target problem per retained student"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM scenario); CodeInsight dataset from VNU-HCM University of Technology CS"
  authors:
    - "Kazunori Fukuhara"
    - "Sang T. Truong"
    - "Duc Q. Nguyen"
    - "Fagun Patel"
    - "Benjamin W. Domingue"
    - "Sanmi Koyejo"
    - "Nick Haber"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_student_mistake_scenario.py"
paper:
  title: "A Dataset for Modeling Iterative Problem-Solving"
  arxiv: "2609.00940"
  url: "https://arxiv.org/abs/2609.00940"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_student_mistake_scenario.py"
released: "2025-07"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - codeinsights_student_coding
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public HELM CodeInsights leaderboard was found. The HELM sample is 41 items. The HELM
    README states that HELM entered maintenance mode on 2026-06-01. No model card in this
    repository cites this id.
contamination:
  risk: medium
  note: >
    Scenario3_data.csv, including response_mistake and unit tests, is public on
    Kazchoko/my_dataset (created 2025-04-18). The full CodeInsight dump is gated. No measured
    training overlap was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "codeinsights_student_mistake"
  opencompass: ""
  bigbench: ""
  other: "Run spec name is codeinsights_student_mistake:temperature={tpr},num_testcases={n}; default tpr=0.0, num_testcases=1."
tags:
  - coding
  - cplusplus
  - student-code
  - error-imitation
  - helm
  - cs-education
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/codeinsights_student_mistake_scenario.py"
    title: "HELM CodeInsightsStudentMistakeScenario (Scenario3 CSV, mistake prompt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/codeinsights_run_specs.py"
    title: "HELM codeinsights_student_mistake run spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_code_evaluation_metrics.py"
    title: "HELM comprehensive code-evaluation metrics (AST, CodeBERT, unit-test alignment)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/stanford-crfm/helm/pulls/3644"
    title: "HELM PR 3644 (merged 2025-07-15)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Kazchoko/my_dataset"
    title: "Hugging Face Kazchoko/my_dataset API"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2609.00940"
    title: "CodeInsight paper (arXiv:2609.00940)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2609.00940"
    title: "CodeInsight HTML: dataset counts, VNU-HCM, licence wording"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CodeInsightTeam/code_insights_csv"
    title: "Hugging Face CodeInsightTeam/code_insights_csv API (gated, cc-by-4.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-008"
---

## What it measures

HELM's codeinsights_student_mistake run asks a model to fail like a particular student. The prompt gives that student's topic pass rates, three past buggy submissions (`response_mistake`), a new Vietnamese C++ problem, a template, and unit-test text. The instruction says to keep personal style and to insert typical errors such as off-by-one indexing, not to emit a clean solution. The reference string is the student's own mistaken code on the target problem.

This uses the CodeInsight course logs from VNU-HCM University of Technology, but it is not the paper's next-attempt prediction task (arXiv:2609.00940). It is also not [codeinsights_student_coding](codeinsights_student_coding.md), which asks for style-matched attempts without requiring a bug.

## How it is scored

Scoring matches the student-coding run spec: `get_comprehensive_code_evaluation_metric_specs()` plus basic HELM metrics. Reported fields include AST and assembly distances, optional CodeBERT cosine similarity, and unit-test alignment with the student's pass/fail bits. The distance fields use `Levenshtein.ratio` (similarity) while the docstring and the 1.0 failure default treat them as distances. A correct program can look like a miss if the student failed tests. Default `num_testcases=1` scores only the first parsed unit test. The scenario stores `pass` as a digit string and then runs `int(...)` before splitting digits, which drops leading zeros in that pattern; treat alignment as HELM-defined, not as a verbatim reconstruction of every test bit.

## Dataset and licence

HELM reads `Scenario3_data.csv` and `student_performace_by_topic.csv` from `Kazchoko/my_dataset`. A direct parse found 696 rows, 50 students, and 41 HELM instances after the four-row filter. The CSV also has `response_correct` and `response_mistake` columns; HELM's reference is `response_mistake`. Kazchoko has no licence card. The paper calls the full dump departmental IP, educational use, on request; the gated `CodeInsightTeam/code_insights_csv` card instead says `cc-by-4.0` and describes 781 students in 2023–2024 against Table 1's 3,286 unique students. HELM answers are public.

## Who publishes it

Same HELM PR 3644 (15 July 2025) as the student-coding scenario, with the same CodeInsight authors and VNU-HCM CS source. The HELM reviewer marked the code experimental. The dataset paper is dated 1 September 2026 (EMNLP 2026 Findings) and places the logs in the 2022 and 2023 academic years. No public leaderboard URL was found.

## Lineage

Sibling page: [codeinsights_student_coding](codeinsights_student_coding.md). Other HELM CodeInsights run specs without pages yet: `codeinsights_correct_code`, `codeinsights_code_efficiency`, `codeinsights_edge_case`. Do not merge with [ci_mcqa](ci_mcqa.md) or with execution-only coding suites such as [humaneval](humaneval.md).

## Saturation and contamination

Unknown saturation on 41 public items. The mistake CSV has been downloadable since April 2025. Full trajectories are gated. No measured contamination study was found.

## How to run it

HELM run spec `codeinsights_student_mistake` with `temperature` and `num_testcases`. Adapter instruction tells the model to introduce realistic mistakes. Metrics need `g++` and libclang; CodeBERT is optional. The scenario file contains leftover debug `print` calls and an unused nested `evaluate_generation` stub; they do not change the instance list. lm-eval and inspect_evals names were not found.

## Reading the numbers

A high alignment score means the model's tests failed and passed in the same pattern as that student, not that the code is good. A high CodeBERT score against `response_mistake` can reward copying a bug. One unit test and 41 students make ranking unstable. Read this beside [codeinsights_student_coding](codeinsights_student_coding.md): coding measures style-matched solutions, mistake measures style-matched errors. Neither number is a HumanEval-style pass@k.
