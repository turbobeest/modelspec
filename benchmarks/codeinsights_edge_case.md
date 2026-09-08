---
id: codeinsights_edge_case
name: "CodeInsights Edge Case"
aliases:
  - "CodeInsightsEdgeCaseScenario"
  - "codeinsights edge case"
page_kind: benchmark
category: coding
subcategory: "HELM prediction of which C++ unit test a CodeInsight student fails"
status: unknown
summary: "HELM scenario that asks a model to name the one unit-test index a given C++ student is most likely to fail."
measures: >
  codeinsights_edge_case is a Stanford HELM run spec on sampled CodeInsight
  logs. For each student it loads a topic pass-rate profile and one target
  C++ problem with parsed unit tests, then asks the model to output a single
  0-based unit-test index the student would fail. Scoring extracts the first
  integer in the completion and checks it against the unique failing bit in
  that student's `pass` pattern. It is failure-index prediction, not code
  generation, and not the CodeInsight paper's next-attempt predictor.
task_format: >
  English HELM instruction plus a Vietnamese/English problem and unit-test
  list; model should return an integer. Default temperature 0, max_tokens
  4000, num_testcases=1 (only the first parsed tests are kept in extra_data).
  The generation adapter still uses output noun "Your code".
metric:
  name: unittest_alignment
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    UnittestAlignmentMetric is 1.0 if the first integer in the completion
    equals the sole index where student_correctness_pattern is 0, else 0.0.
    No output, no integer, or a pattern that does not contain exactly one
    zero all score 0. The scenario stores `pass` then HELM runs int(...)
    before splitting digits, which drops leading zeros. A direct parse of
    the 23 default instances found exactly one failing bit after that int()
    step on 1 instance; the other 22 cannot score 1.0 under the metric as
    written. CodeInsightsUnittestAlignmentMetric wraps that class and does
    not add CodeBERT in evaluate_generation. No random or human baseline.
dataset:
  size: 23
  size_note: >
    Direct parse of Kazchoko/my_dataset Scenario5_data.csv: 541 rows, 50
    student_id values, 93 question_unittest_id values. HELM groups by
    student, sorts by timestamp, uses the first row (no four-row filter),
    and skips targets whose question_unittest_id is missing from
    test_cases_by_qid.json, yielding 23 instances at num_testcases=1.
    question_id in this CSV is a float string (e.g. 175.0); HELM looks up
    question_unittest_id. Sample, not the full CodeInsight release. The
    is_single_failure column is True on all 541 rows; that does not match
    the metric's int() bit test.
  url: "https://huggingface.co/datasets/Kazchoko/my_dataset"
  license: ""
  languages:
    - vi
    - en
  modalities:
    - text
    - code
  splits: "HELM VALID_SPLIT only; one target problem per student with a JSON test list"
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
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_edge_case_scenario.py"
paper:
  title: "A Dataset for Modeling Iterative Problem-Solving"
  arxiv: "2609.00940"
  url: "https://arxiv.org/abs/2609.00940"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_edge_case_scenario.py"
released: "2025-07"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - codeinsights_student_coding
    - codeinsights_student_mistake
    - codeinsights_correct_code
    - codeinsights_code_efficiency
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public HELM CodeInsights leaderboard was found. Default n=23, and the
    metric can return 1.0 on at most the instances with a single remaining
    fail bit after int(). HELM README: maintenance mode from 2026-06-01.
contamination:
  risk: medium
  note: >
    Scenario5_data.csv, including pass patterns and unit-test text, is public
    on Kazchoko/my_dataset (created 2025-04-18). The full dump is gated. No
    measured training overlap was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "codeinsights_edge_case"
  opencompass: ""
  bigbench: ""
  other: "Run spec name is codeinsights_edge_case:temperature={tpr},num_testcases={n}; default tpr=0.0, num_testcases=1."
tags:
  - coding
  - cplusplus
  - student-code
  - unit-tests
  - helm
  - cs-education
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/codeinsights_edge_case_scenario.py"
    title: "HELM CodeInsightsEdgeCaseScenario (Scenario5 CSV, integer prompt)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/codeinsights_run_specs.py"
    title: "HELM codeinsights_edge_case run spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_edge_case_metrics.py"
    title: "HELM unittest_alignment metric"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_metric_specs.py"
    title: "HELM get_edge_case_metric_specs"
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
    title: "CodeInsight paper HTML (Table 1; departmental licence; no EMNLP claim)"
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

HELM's codeinsights_edge_case run asks a model which unit test a particular student would fail. The prompt gives topic-level pass rates, one Vietnamese C++ problem, and the parsed tests. The instruction says to return only a 0-based integer. There is no request for a program body.

The gold index is derived from that student's `pass` bit string, not from executing new code. Default `num_testcases=1` still truncates the test list copied into extra_data, while the alignment metric uses the full stored pass pattern. This is not [codeinsights_student_mistake](codeinsights_student_mistake.md), which generates buggy C++.

## How it is scored

`UnittestAlignmentMetric` reads the first integer in the completion with `-?\d+`. It compares that index to the unique position where the student pattern is 0. Anything else, including two failing tests after `int(pass)`, scores 0. A direct replay of that `int(...)` step on the 23 default instances left exactly one failing bit on 1 instance. The CSV column `is_single_failure` is True for all 541 rows and does not match that filter. The adapter output noun is still "Your code", which fights the integer instruction.

## Dataset and licence

HELM reads `Scenario5_data.csv`, `student_performace_by_topic.csv`, and `test_cases_by_qid.json` from `Kazchoko/my_dataset`. A direct parse found 541 rows, 50 students, and 23 HELM instances after the JSON-key filter. `question_id` values look like `175.0`; lookup uses `question_unittest_id`. Kazchoko has no licence card. The paper versus gated Hub licence split is the same as the sibling pages. Answers and pass bits are public.

## Who publishes it

Same HELM PR 3644 (15 July 2025) and CodeInsight authors as the other scenarios. Dataset paper posted 1 September 2026 (arXiv:2609.00940v1); the abstract lists no conference. Source logs: VNU-HCM University of Technology CS. No public leaderboard URL was found.

## Lineage

Siblings: [codeinsights_student_coding](codeinsights_student_coding.md), [codeinsights_student_mistake](codeinsights_student_mistake.md), [codeinsights_correct_code](codeinsights_correct_code.md), [codeinsights_code_efficiency](codeinsights_code_efficiency.md). Do not merge with [ci_mcqa](ci_mcqa.md).

## Saturation and contamination

Unknown saturation. With the metric's exactly-one-fail rule, most default instances cannot score 1.0. The CSV has been public since April 2025.

## How to run it

HELM run spec `codeinsights_edge_case` with `temperature` and `num_testcases`. Needs the JSON test file. lm-eval and inspect_evals names were not found.

## Reading the numbers

A 0.0 unittest_alignment on this sample is the metric default, not proof the model missed every student. Check how many instances still have exactly one zero after `int(pass)` before ranking models. An integer that names a hard test is not a HumanEval pass@k. Read beside [codeinsights_student_mistake](codeinsights_student_mistake.md) if the question is whether the model can reproduce the bug, not merely point at a test index.
