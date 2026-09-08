---
id: codeinsights_correct_code
name: "CodeInsights Correct Code"
aliases:
  - "CodeInsightsCorrectCodeScenario"
  - "codeinsights correct code"
page_kind: benchmark
category: coding
subcategory: "HELM C++ unit-test pass rate on a CodeInsight question sample"
status: unknown
summary: "HELM scenario that asks a model to fill a C++ course template so the generated body passes the problem's unit tests."
measures: >
  codeinsights_correct_code is a Stanford HELM run spec on sampled CodeInsight
  course logs. It groups Kazchoko/my_dataset Scenario1_2_data.csv by
  question_unittest_id, takes the first row of each question, and asks the
  model to write only the C++ that replaces {{ STUDENT_ANSWER }} in the
  course template. Scoring compiles with g++ and measures the fraction of
  parsed unit tests that match expected stdout. It is functional correctness
  on undergraduate C++ assignments, not the CodeInsight paper's next-attempt
  predictor, not student-style imitation, and not [ci_mcqa](ci_mcqa.md).
task_format: >
  English HELM instruction plus a Vietnamese/English problem prompt; model
  returns a fenced C++ fragment. Default temperature 0, max_tokens 4000,
  num_testcases=1 (only the first parsed unit test is kept).
metric:
  name: functional_correctness
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    CodeInsightsFunctionalCorrectnessMetric runs CPPEvaluator: insert the
    extracted body into the template, compile g++ -std=c++11, compare stdout.
    The returned score is mean test-pass rate on the tests attached to that
    instance (default one test), then HELM averages across instances. The
    class docstring also says "passes all provided unit tests"; the
    implementation uses score = passed/len(tests). No published random or
    human baseline. Linux timeout(1) wraps compile and run.
dataset:
  size: 84
  size_note: >
    Direct parse of Kazchoko/my_dataset Scenario1_2_data.csv: 184 rows, 49
    student_id values, 84 question_unittest_id values. HELM groups by
    question, not by student, and keeps one instance per question when
    unittests parse (84/84 at num_testcases=1). Same CSV as
    codeinsights_student_coding, which instead groups by student and yields
    29 instances. Sample, not the full CodeInsight dump (paper Table 1:
    3,286 students / 3,074,795 submissions). Gated Hub API description:
    781 students in 2023–2024; cardData.train is 3,074,799 rows.
  url: "https://huggingface.co/datasets/Kazchoko/my_dataset"
  license: ""
  languages:
    - vi
    - en
  modalities:
    - text
    - code
  splits: "HELM VALID_SPLIT only; one instance per question_unittest_id"
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
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_correct_code_scenario.py"
paper:
  title: "A Dataset for Modeling Iterative Problem-Solving"
  arxiv: "2609.00940"
  url: "https://arxiv.org/abs/2609.00940"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_correct_code_scenario.py"
released: "2025-07"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - codeinsights_student_coding
    - codeinsights_student_mistake
    - codeinsights_code_efficiency
    - codeinsights_edge_case
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public HELM CodeInsights leaderboard was found. Default eval is 84
    items and one unit test. HELM README: maintenance mode from 2026-06-01.
    No model card in this repository cites this id.
contamination:
  risk: medium
  note: >
    Scenario1_2_data.csv, including templates and unit-test text, is public
    on Kazchoko/my_dataset (created 2025-04-18). The full CodeInsight dump is
    gated. No measured training overlap was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "codeinsights_correct_code"
  opencompass: ""
  bigbench: ""
  other: "Run spec name is codeinsights_correct_code:temperature={tpr},num_testcases={n}; default tpr=0.0, num_testcases=1."
tags:
  - coding
  - cplusplus
  - student-code
  - functional-correctness
  - helm
  - cs-education
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/codeinsights_correct_code_scenario.py"
    title: "HELM CodeInsightsCorrectCodeScenario (Scenario1_2 CSV, grouping)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/codeinsights_run_specs.py"
    title: "HELM codeinsights_correct_code run spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_correct_code_metrics.py"
    title: "HELM functional_correctness metric and CPPEvaluator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_metric_specs.py"
    title: "HELM get_functional_correctness_metric_specs"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/stanford-crfm/helm/pulls/3644"
    title: "HELM PR 3644 (merged 2025-07-15)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Kazchoko/my_dataset"
    title: "Hugging Face Kazchoko/my_dataset API"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2609.00940"
    title: "CodeInsight paper (arXiv:2609.00940v1, 1 Sep 2026; no venue on abs)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2609.00940"
    title: "CodeInsight paper HTML (Table 1 3,286 / 3,074,795; departmental licence)"
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
  researched_by: "Grok Build, batch-032 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-032"
---

## What it measures

HELM's codeinsights_correct_code run asks a model to solve one undergraduate C++ assignment. The prompt gives the question name and text, the first parsed unit test, and a template with a `{{ STUDENT_ANSWER }}` hole. The instruction says to emit only the body, not `int main`. Problem stems in the CSV are Vietnamese course text from VNU-HCM University of Technology.

Unlike [codeinsights_student_coding](codeinsights_student_coding.md), there are no prior student submissions and no style instruction. Unlike the CodeInsight paper (arXiv:2609.00940), HELM does not score next-attempt outcome prediction.

## How it is scored

The run spec attaches `get_functional_correctness_metric_specs()` plus basic HELM metrics. `CodeInsightsFunctionalCorrectnessMetric` extracts a ```c++ fence, strips `#include` / `using namespace` / `int main`, compiles with `g++ -std=c++11`, and compares stdout. The per-instance value is passed tests over attached tests. Default `num_testcases=1` means that is a single-test pass bit, not a full suite. The class docstring mixes "passes all tests" with a mean pass-rate formula; the code uses the mean. Compile and run wrap Linux `timeout`. No CodeBERT field on this spec.

## Dataset and licence

HELM reads `Scenario1_2_data.csv` from `Kazchoko/my_dataset` (created 2025-04-18, no dataset-card licence). A direct parse found 184 rows, 49 students, and 84 questions; all 84 questions parsed at least one unit test. The sibling student-coding run uses the same file but groups by student (29 instances). The gated Hub API lists `cc-by-4.0`, 3,074,799 train rows, and a description of 781 students in 2023–2024. Paper Table 1 is 3,286 unique students and 3,074,795 submissions, released under a departmental licence for educational use on request. HELM answers and tests are public. The arXiv HTML footer is CC BY-NC-SA 4.0 for the paper, not the logs.

## Who publishes it

The HELM scenario landed in stanford-crfm/helm PR 3644 on 15 July 2025, authored by Kazunori Fukuhara (GitHub Kazf28). The dataset paper is Patel, Truong, Nguyen, Fukuhara, Domingue, Koyejo and Haber, posted 1 September 2026 (arXiv:2609.00940v1). The abstract lists no conference. Logs are from Programming Fundamentals and Data Structures and Algorithms at VNU-HCM University of Technology (paper: 2022 and 2023 academic years). No public CodeInsights leaderboard URL was found.

## Lineage

Sibling HELM run specs: [codeinsights_student_coding](codeinsights_student_coding.md), [codeinsights_student_mistake](codeinsights_student_mistake.md), [codeinsights_code_efficiency](codeinsights_code_efficiency.md), [codeinsights_edge_case](codeinsights_edge_case.md). Do not merge with [ci_mcqa](ci_mcqa.md) or with [humaneval](humaneval.md).

## Saturation and contamination

Unknown saturation on 84 public items with one unit test. The CSV has been downloadable since April 2025. Full trajectories are gated. Treat public HELM numbers as easy to overfit.

## How to run it

HELM run spec `codeinsights_correct_code` with `temperature` and `num_testcases`. Adapter instruction: skilled C++ programmer, output noun "Your code", 4000 max tokens. Needs `g++` and Linux `timeout`. lm-eval and inspect_evals names were not found.

## Reading the numbers

A 0.8 functional_correctness at the default setting means 80% of questions passed the first parsed unit test, not that the programs handle edge cases. Raising `num_testcases` changes the instance filter and the score. A high score here with a low student-coding CodeBERT score means the model solved the homework without matching that student. Neither number is the paper's next-attempt prediction accuracy.
