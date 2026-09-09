---
id: codeinsights_student_coding
name: "CodeInsights Student Coding"
aliases:
  - "CodeInsightsStudentCodingScenario"
  - "codeinsights student coding"
page_kind: benchmark
category: coding
subcategory: "HELM C++ student-style generation on a CodeInsight sample"
status: unknown
summary: "HELM scenario that asks a model to write C++ in one student's style given three of their submissions and a new problem."
measures: >
  codeinsights_student_coding is a Stanford HELM run spec. It samples one undergraduate from a
  public CodeInsight CSV, shows three of that student's earlier C++ submissions, and asks the
  model to solve a fourth problem in the same personal style. Problem text is typically Vietnamese;
  the model must emit only a C++ body that drops into a {{ STUDENT_ANSWER }} template. HELM
  then compares that body to the student's own later submission and to unit-test outcomes. It is
  a style-and-behaviour imitation task, not the CodeInsight paper's next-attempt score prediction
  benchmark, and not [ci_mcqa](ci_mcqa.md).
task_format: >
  English HELM instruction plus a Vietnamese/English problem prompt; model returns a fenced C++
  fragment. Default run uses temperature 0, max_tokens 4000, and the first unit test only
  (num_testcases=1).
metric:
  name: "composite: ast_distance, asm_distance, codebert_similarity, unittest_alignment_ratio"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM attaches CodeInsightsComprehensiveCodeEvaluationMetric. The AST helper's docstring
    says 0 is identical and 1 is a parse failure, but the code calls Levenshtein.ratio
    (similarity; 1 if identical) and still writes 1.0 on empty code or compile failure.
    CodeBERT cosine similarity is recorded when transformers are installed. Unit-test
    alignment compares LLM versus student pass bits. There is no schema_codeinsights.yaml
    headline metric. Treat reported fields as HELM-defined, not as a single direction.
    No random or human baseline is published for this run spec.
dataset:
  size: 29
  size_note: >
    Direct count of Kazchoko/my_dataset Scenario1_2_data.csv: 184 rows, 49 student_id values,
    84 question_unittest_id values. HELM groups by student, sorts by timestamp, skips students
    with fewer than four rows, and uses the fourth row as the target, yielding 29 instances at
    default num_testcases=1. This is a sample, not the full CodeInsight release. Paper Table 1:
    3,286 unique students, 394 problems, 3,074,795 submissions. Hugging Face
    CodeInsightTeam/code_insights_csv reports 3,074,799 train rows and, on the gated card,
    781 students in 2023–2024 (not the paper totals).
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
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_student_coding_scenario.py"
paper:
  title: "A Dataset for Modeling Iterative Problem-Solving"
  arxiv: "2609.00940"
  url: "https://arxiv.org/abs/2609.00940"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/codeinsights_student_coding_scenario.py"
released: "2025-07"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - codeinsights_student_mistake
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public HELM CodeInsights leaderboard or schema file was found. The HELM README states
    that HELM entered maintenance mode on 2026-06-01. No model card in this repository currently
    cites this id.
contamination:
  risk: medium
  note: >
    The HELM CSV, including student responses and unit tests, has been public on
    Kazchoko/my_dataset since that dataset's Hugging Face createdAt 2025-04-18. The full
    CodeInsight dump on CodeInsightTeam/code_insights_csv is gated. Course problems and student
    solutions may also exist in other crawls. No measured training overlap was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "codeinsights_student_coding"
  opencompass: ""
  bigbench: ""
  other: "Run spec name is codeinsights_student_coding:temperature={tpr},num_testcases={n}; default tpr=0.0, num_testcases=1."
tags:
  - coding
  - cplusplus
  - student-code
  - style-imitation
  - helm
  - cs-education
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/codeinsights_student_coding_scenario.py"
    title: "HELM CodeInsightsStudentCodingScenario (CSV URLs, prompt, grouping rule)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/codeinsights_run_specs.py"
    title: "HELM codeinsights_student_coding run spec (adapter, metrics, groups)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_metric_specs.py"
    title: "HELM CodeInsights comprehensive metric spec"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/codeinsights_code_evaluation_metrics.py"
    title: "HELM AST, CodeBERT, assembly, and unit-test alignment metrics"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/stanford-crfm/helm/pulls/3644"
    title: "HELM PR 3644 (merged 2025-07-15): undergraduate student-code scenarios"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Kazchoko/my_dataset"
    title: "Hugging Face Kazchoko/my_dataset API (files, createdAt, no licence card)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2609.00940"
    title: "CodeInsight paper (arXiv:2609.00940), EMNLP 2026 Findings"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2609.00940"
    title: "CodeInsight HTML: Table 1 counts, VNU-HCM, departmental licence"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CodeInsightTeam/code_insights_csv"
    title: "Hugging Face CodeInsightTeam/code_insights_csv API (gated, cc-by-4.0, 3,074,799 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0 (harness, not the student dataset)"
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

HELM's codeinsights_student_coding run asks a model to impersonate one C++ student. The prompt includes a topic-level pass-rate profile, three earlier submissions from that student, a new problem with a code template, and (by default) the first unit test. The model must return only the C++ that replaces `{{ STUDENT_ANSWER }}`. `int main` is already in the template. Problem names and stems in the HELM CSV are Vietnamese undergraduate assignments from VNU-HCM University of Technology.

This is not the CodeInsight paper's main benchmark. That paper (arXiv:2609.00940, EMNLP 2026 Findings) scores next-attempt outcome prediction on full trajectories. HELM instead scores whether generated C++ looks and behaves like that student. It is also not [ci_mcqa](ci_mcqa.md), a private concept-inventory MCQ scenario.

## How it is scored

The run spec attaches `CodeInsightsComprehensiveCodeEvaluationMetric` plus HELM's basic metrics. The comprehensive class records `ast_distance` and `asm_distance` from libclang / `g++ -S` comparisons, `codebert_similarity` from microsoft/codebert-base when available, and unit-test alignment (`unittest_alignment_ratio`, LLM versus student pass bits) via `g++`. The AST docstring treats 1 as maximum difference, but both distance fields are filled with `Levenshtein.ratio` (similarity) and still use 1.0 on parse or compile failure, so the names and the failure default disagree. There is no `schema_codeinsights.yaml`, so HELM does not publish one headline number. Default `num_testcases=1` means alignment uses only the first parsed unit test. Compiles need a local C++ toolchain; missing CodeBERT drops the similarity field rather than failing the run.

## Dataset and licence

HELM reads `Scenario1_2_data.csv` and `student_performace_by_topic.csv` from Hugging Face `Kazchoko/my_dataset` (created 2025-04-18, lastModified 2025-07-31, no dataset card licence). A direct parse of that CSV found 184 rows, 49 students, and 29 HELM instances after the four-row filter. The official CodeInsight dump `CodeInsightTeam/code_insights_csv` is gated, tagged `cc-by-4.0`, and reports 3,074,799 train rows against paper Table 1's 3,074,795 submissions. The gated card overview instead describes 781 students in 2023–2024, which does not match Table 1's 3,286 unique students. The paper says the dataset is departmental IP, educational use, released on request. Answers in the HELM CSV are public.

## Who publishes it

The HELM scenario landed in stanford-crfm/helm PR 3644 on 15 July 2025, authored by Kazunori Fukuhara with Sang T. Truong and Duc Q. Nguyen. The HELM reviewer marked the code experimental. The dataset paper is Patel, Truong, Nguyen, Fukuhara, Domingue, Koyejo and Haber, posted 1 September 2026. Data come from two introductory C++ courses (Programming Fundamentals and Data Structures and Algorithms) at the Department of Computer Science, VNU-HCM University of Technology, in the 2022 and 2023 academic years (paper §4 / Table 1). No public CodeInsights leaderboard URL was found.

## Lineage

No family page exists in this repository. The sibling HELM run spec [codeinsights_student_mistake](codeinsights_student_mistake.md) uses a different CSV and asks the model to reproduce likely errors. Three further HELM scenarios — `codeinsights_correct_code`, `codeinsights_code_efficiency`, `codeinsights_edge_case` — share the same run-spec file but do not yet have pages. The CodeInsight paper's RSSM / LLM-as-predictor protocol is a different evaluation on the same course logs. Do not fold this id into [ci_mcqa](ci_mcqa.md) or [humaneval](humaneval.md).

## Saturation and contamination

Saturation is not established: there is no leaderboard, and the HELM sample is 29 items. The sampled CSV and unit tests have been public since April 2025. The full dump is gated. Course solutions may still appear in other student-code crawls. Treat public HELM numbers as easy to overfit.

## How to run it

In HELM: `codeinsights_student_coding` with optional `temperature` and `num_testcases`. The generation adapter uses a student-persona instruction, output noun "Your code", 4000 max tokens, and no stop sequences. Reproducing AST and unit-test metrics needs libclang, `g++`, and optionally torch plus transformers. Numbers from a run that skipped CodeBERT or compiled with a different standard are not comparable. lm-eval and inspect_evals names were not found.

## Reading the numbers

A high CodeBERT score with a low unit-test alignment means the model copied style but not behaviour, or the reverse. Because HELM keeps one target problem per student and defaults to one unit test, small gaps are noisy. The Vietnamese stems mean an English-only model can fail the problem before style is an issue. A strong score does not mean the model predicts a student's next attempt, which is what the CodeInsight paper actually scores. Compare against [codeinsights_student_mistake](codeinsights_student_mistake.md) before treating either as generic coding skill.
