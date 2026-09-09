---
id: swe_bench_lite
name: SWE-bench Lite
aliases: ["SWE-bench_Lite", "SWE-Bench-Lite"]
page_kind: benchmark
category: coding
subcategory: "GitHub issue resolution / patch generation (filtered subset)"
status: active
summary: "A 300-task, single-file-edit subset of original SWE-bench, kept as a cheaper Python issue-resolution reporting split."
measures: >
  SWE-bench Lite measures the same skill as SWE-bench: produce a patch that
  resolves a real GitHub issue in a popular Python repository. The 300 test
  tasks are filtered to shorter, more self-contained edits so evaluation is
  cheaper than the full 2,294-instance set.
task_format: >
  Identical to SWE-bench: issue text plus repository access, patch output,
  Docker grading with FAIL_TO_PASS and PASS_TO_PASS tests. Lite additionally
  drops multi-file gold patches, file create/delete, short problem statements,
  and several other hard cases.
metric:
  name: "% resolved"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No human baseline. OpenAI's 2024-08-13 Verified post cited the SWE-bench leaderboard at 43% on Lite as of 2024-08-05. swebench.com later lists higher agent scores (see saturation)."
dataset:
  size: 300
  size_note: >
    300 test instances from 11 of the original 12 SWE-bench Python
    repositories, plus 23 development instances. Hugging Face
    princeton-nlp/SWE-bench_Lite and SWE-bench/SWE-bench_Lite both expose
    test=300 and dev=23. Selection removes images and external links, problem
    statements under 40 words, gold patches that touch more than one file or
    more than three hunks, file create/delete, and tests that check error
    strings, then samples 300+23 from the remainder.
  url: "https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite"
  license: MIT
  languages: [Python]
  modalities: [code, text]
  splits: "test 300, dev 23"
  public_test_set: true
publisher:
  org: "SWE-bench Team (originally Princeton NLP)"
  authors: [Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik R. Narasimhan]
  url: "https://www.swebench.com/lite.html"
paper:
  title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
  arxiv: "2310.06770"
  url: "https://arxiv.org/abs/2310.06770"
  year: 2023
leaderboard_url: "https://www.swebench.com/"
repo_url: "https://github.com/SWE-bench/SWE-bench"
released: "2024-03"
last_updated: "2026-08"
lineage:
  family: swe_bench
  predecessor: swe_bench
  successors: [swe_bench_verified]
  variants: []
saturation:
  status: watch
  top_score: 60.33
  as_of: "2025-06"
  note: >
    On swebench.com's Lite board (embedded JSON, accessed 2026-09-08) the
    highest listed resolved rate is 60.33% for ExpeRepair-v1.0 + Claude 4
    Sonnet (2025-06-25, unchecked). The highest checked entry among the top
    rows is SWE-agent + Claude 4 Sonnet at 56.67% (2025-05-26). OpenAI's
    August 2024 note cited 43% on Lite. The split still sits below 100%, but
    many vendors now prefer Verified, so Lite is a watch item rather than the
    default open ranking.
contamination:
  risk: high
  note: >
    Same structural risk as SWE-bench: public merged pull requests with gold
    patches in the dataset. Filtering for single-file edits does not hide
    those patches.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official SWE-bench Docker harness and `swebench` CLI, with dataset
    princeton-nlp/SWE-bench_Lite or SWE-bench/SWE-bench_Lite. inspect_evals
    ships inspect_evals/swe_bench (default Verified) and can load Lite if the
    dataset argument is overridden; there is no dedicated inspect task name
    for Lite. R2E-Gym/SWE-Bench-Lite is a 300-row Docker-enriched copy, not
    the official split.
tags: [coding, agentic, github-issues, patch-generation, docker, python, subset]
sources:
  - url: "https://www.swebench.com/lite.html"
    title: "SWE-bench Lite overview"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite"
    title: "SWE-bench/SWE-bench_Lite dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite"
    title: "princeton-nlp/SWE-bench_Lite dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/R2E-Gym/SWE-Bench-Lite"
    title: "R2E-Gym/SWE-Bench-Lite (repack, not the official split)"
    accessed: "2026-09-08"
  - url: "https://www.swebench.com/"
    title: "SWE-bench leaderboards (Lite JSON)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2310.06770"
    title: "SWE-bench paper"
    accessed: "2026-09-08"
  - url: "https://github.com/SWE-bench/SWE-bench"
    title: "SWE-bench/SWE-bench repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/swe_bench/README.md"
    title: "inspect_evals SWE-bench README"
    accessed: "2026-09-09"
  - url: "https://openai.com/index/introducing-swe-bench-verified/"
    title: "OpenAI: Introducing SWE-bench Verified"
    accessed: "2026-09-09"
  - url: "https://raw.githubusercontent.com/SWE-bench/SWE-bench/main/LICENSE"
    title: "SWE-bench MIT licence"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-074 (Codex coordinated)"
  reviewed: "2026-09-09"
  reviewed_by: "Grok Build independent review, batch-074"
---

## What it measures

SWE-bench Lite is the official 300-task reporting subset of original SWE-bench.
The agent still receives a GitHub issue and a Python repository snapshot, then
must write a patch that the project's tests accept. The subset keeps 11 of the
12 original repositories but throws away tasks that are long, multi-file, or
poorly specified.

The filter is intentional. Lite exists so groups can iterate without running
all 2,294 full-set instances. That also makes Lite easier than the unfiltered
set: gold patches edit one file and at most three hunks.

## How it is scored

Scoring is unchanged from SWE-bench. A patch must flip FAIL_TO_PASS tests to
passing and leave PASS_TO_PASS tests passing. OpenAI's Verified announcement
cited the SWE-bench leaderboard at 43% on Lite as of 2024-08-05, not an OpenAI
in-house Lite run. The swebench.com Lite board later lists agent results up
to 60.33% (ExpeRepair-v1.0 + Claude 4 Sonnet, 2025-06-25, unchecked) and 56.67%
for a checked SWE-agent + Claude 4 Sonnet run (2025-05-26). Scaffold and whether
maintainers checked logs still matter as much as the model name.

## Dataset and licence

The SWE-bench GitHub repository is MIT-licensed; the Hugging Face Lite cards do
not declare a separate licence tag. Hugging Face hosts matching test=300 and
dev=23 splits under princeton-nlp/SWE-bench_Lite (created 2024-03-19) and
SWE-bench/SWE-bench_Lite (last modified 2026-08-16). Gold patches and test names
are public. R2E-Gym/SWE-Bench-Lite is a third 300-row dump with extra Docker
fields; it is a repack, not a new sample.

## Who publishes it

Carlos E. Jimenez, John Yang, and the original SWE-bench authors at Princeton
NLP introduced Lite with the SWE-bench project. The SWE-bench Team still hosts
the overview at swebench.com/lite.html and the leaderboard at swebench.com.

## Lineage

Lite is a subset of [SWE-bench](swe_bench.md), not of
[SWE-bench Verified](swe_bench_verified.md). Verified later became the default
fairness-filtered set of 500 tasks and explicitly superseded Lite for most
vendor reporting. Do not confuse this page with the frozen `lite` split of
[SWE-bench-Live](swe_bench_live.md), which is a different 300-instance sample
from post-2024 issues.

## Saturation and contamination

60% on a filtered 300-task set is high enough to watch, especially because
Verified is now the preferred board. Contamination risk is high: these are the
same public pull requests as the original benchmark, just the easier slice.

## How to run it

Run the official SWE-bench harness on the Lite dataset id. If you use
inspect_evals, pass `dataset="princeton-nlp/SWE-bench_Lite"` into
`inspect_evals/swe_bench`; the default inspect task is Verified. Record whether
you used the 23-instance dev split (you should not report it as the test score).

## Reading the numbers

A Lite score is not a Verified score and not a full SWE-bench score. It over-
represents short, single-file Python fixes in well-known projects. When a model
card says "SWE-bench" without Lite/Verified/full, ask which split. Prefer
Verified for a current fairness-filtered number, and treat Lite as a cheaper
historical comparison.
