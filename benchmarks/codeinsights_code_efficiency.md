---
id: codeinsights_code_efficiency
name: "CodeInsights Code Efficiency"
aliases:
  - "CodeInsightsCodeEfficiencyScenario"
  - "codeinsights code efficiency"
page_kind: benchmark
category: coding
subcategory: "HELM C++ runtime alignment against a CodeInsight student sample"
status: unknown
summary: "HELM scenario that asks a model to write C++ matching one student's runtime style, then compares wall-clock times on unit tests."
measures: >
  codeinsights_code_efficiency is a Stanford HELM run spec on sampled
  CodeInsight logs. For each retained student it shows three earlier C++
  submissions and a fourth Vietnamese problem, and asks the model to solve
  that problem in the same personal style, including the student's
  inefficiency when the examples are slow. Scoring compiles both the model
  body and the student's target response, then compares mean runtime on
  tests that pass. It is runtime imitation, not generic Big-O ranking, and
  not the CodeInsight paper's next-attempt predictor.
task_format: >
  English HELM instruction plus a Vietnamese/English problem prompt; model
  returns a fenced C++ fragment for {{ STUDENT_ANSWER }}. Default temperature
  0, max_tokens 4000, num_testcases=1. Efficiency metric uses 5 timed runs
  and a 10 s timeout.
metric:
  name: "composite: functional_correctness, runtime_efficiency_ratio, efficiency_alignment_score"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    CodeInsightsCodeEfficiencyMetric extends the functional-correctness
    evaluator. functional_correctness is the model's unit-test pass rate.
    runtime_efficiency_ratio is mean LLM seconds per passing test divided by
    the student's; values >1 mean the LLM is slower. efficiency_alignment_score
    is min(ratio, 1/ratio), so 1.0 is matched speed. If only one side runs,
    alignment is 0.0 and the ratio is 0 or inf. Timed loops skip runs with
    zero passing tests. The spec also attaches CodeInsightsCodeEvaluationMetric
    (AST / optional CodeBERT). No schema headline, random baseline, or human
    baseline was found. Direction is mixed: a large ratio is not "better".
dataset:
  size: 19
  size_note: >
    Direct parse of Kazchoko/my_dataset Scenario4_data.csv: 696 rows, 50
    student_id values, 175 question_unittest_id values. HELM groups by
    student, sorts by timestamp, skips students with fewer than four rows
    (9), then skips targets whose question_unittest_id is missing from
    test_cases_by_qid.json (22), yielding 19 instances at num_testcases=1.
    JSON has 101 keys. Sample, not the full CodeInsight release.
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
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_code_efficiency_scenario.py"
paper:
  title: "A Dataset for Modeling Iterative Problem-Solving"
  arxiv: "2609.00940"
  url: "https://arxiv.org/abs/2609.00940"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_code_efficiency_scenario.py"
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
    - codeinsights_edge_case
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public HELM CodeInsights leaderboard was found. The default sample is
    19 items. HELM README: maintenance mode from 2026-06-01.
contamination:
  risk: medium
  note: >
    Scenario4_data.csv, student responses, and test_cases_by_qid.json are
    public on Kazchoko/my_dataset (created 2025-04-18). The full dump is
    gated. No measured training overlap was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "codeinsights_code_efficiency"
  opencompass: ""
  bigbench: ""
  other: "Run spec name is codeinsights_code_efficiency:temperature={tpr},num_testcases={n}; default tpr=0.0, num_testcases=1. Metric args num_runtime_runs=5, timeout_seconds=10."
tags:
  - coding
  - cplusplus
  - student-code
  - runtime
  - helm
  - cs-education
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/codeinsights_code_efficiency_scenario.py"
    title: "HELM CodeInsightsCodeEfficiencyScenario (Scenario4 CSV, test JSON)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/codeinsights_run_specs.py"
    title: "HELM codeinsights_code_efficiency run spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_code_efficiency_metrics.py"
    title: "HELM runtime ratio and alignment metric"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_metric_specs.py"
    title: "HELM get_code_efficiency_metric_specs"
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

HELM's codeinsights_code_efficiency run asks a model to impersonate one C++ student on speed as well as style. The prompt shows three earlier submissions, then a fourth Vietnamese problem and template. The instruction says not to over-optimize: copy inefficiency when the examples are slow, and copy speed when they are fast.

The reference is that student's later `response`. The extra lookup file `test_cases_by_qid.json` must contain the target `question_unittest_id` or HELM drops the student. This is not a compiler-benchmark leaderboard and not the CodeInsight paper's next-attempt task.

## How it is scored

The run spec attaches `CodeInsightsCodeEfficiencyMetric` (5 timed runs, 10 s) plus `CodeInsightsCodeEvaluationMetric` and basic HELM metrics. Functional correctness is the model's test pass rate. Runtime ratio is LLM mean seconds per passing test over the student's. Alignment maps that ratio onto (0, 1] with a reciprocal so faster and slower both move away from 1. Runs with zero passing tests are skipped in the average. Host load, `g++`, and Linux `timeout` all move the clock. Default `num_testcases=1` times a single test.

## Dataset and licence

HELM reads `Scenario4_data.csv` and `test_cases_by_qid.json` from `Kazchoko/my_dataset`. A direct parse found 696 rows, 50 students, 175 questions, 101 JSON keys, and 19 HELM instances after the four-row and JSON-key filters. Kazchoko has no licence card. The paper calls the full dump departmental IP; the gated `CodeInsightTeam/code_insights_csv` card says `cc-by-4.0`. HELM answers are public.

## Who publishes it

Same HELM PR 3644 (15 July 2025) as the other CodeInsights scenarios, with the same CodeInsight authors and VNU-HCM CS source. The dataset paper was posted 1 September 2026 (arXiv:2609.00940v1); the abstract lists no conference. No public leaderboard URL was found.

## Lineage

Siblings: [codeinsights_student_coding](codeinsights_student_coding.md), [codeinsights_student_mistake](codeinsights_student_mistake.md), [codeinsights_correct_code](codeinsights_correct_code.md), [codeinsights_edge_case](codeinsights_edge_case.md). Do not merge with [ci_mcqa](ci_mcqa.md) or [humaneval](humaneval.md).

## Saturation and contamination

Unknown saturation on 19 public items. The CSV and JSON have been downloadable since April 2025. Full trajectories are gated. Wall-clock scores are not portable across machines.

## How to run it

HELM run spec `codeinsights_code_efficiency` with `temperature` and `num_testcases`. Adapter output noun is "Your code". Metrics need `g++` and Linux `timeout`; CodeBERT is optional on the extra evaluation metric. lm-eval and inspect_evals names were not found.

## Reading the numbers

A high alignment score with a low functional_correctness means both programs were slow or broken in a similar way, not that the model wrote a fast solution. A ratio of 2 means the LLM took twice as long on passing tests. Nineteen students make ranking noisy. Read beside [codeinsights_correct_code](codeinsights_correct_code.md): that id ignores style and speed.
