---
id: swe_evo
name: SWE-EVO
aliases: []
page_kind: benchmark
category: coding
subcategory: long-horizon software evolution / multi-file patch generation
status: active
summary: SWE-EVO gives coding agents a real project release note and asks for the multi-file changes it describes, checked against the project's own tests.
measures: >
  SWE-EVO tests whether a coding agent can carry out a realistic software evolution task rather than
  a single isolated bug fix. Each task is derived from the release notes of a mature open-source
  Python project and requires locating and editing code across many files to implement the described
  set of changes, then passing the project's real test suite. This targets sustained, multi-file
  reasoning over a large codebase rather than the single-issue, single-file patches typical of
  SWE-bench style benchmarks.
task_format: >
  The agent is given a repository snapshot and a natural-language description of the intended
  evolution (drawn from the project's release notes), and must produce a set of file edits. The
  result is graded by running the project's test suite, which averages 874 tests per task instance.
metric: {name: "Resolved rate / Fix rate", direction: higher_is_better, unit: percent, max_score: 100, random_baseline: null, human_baseline: null, baseline_note: "Resolved rate is the share of tasks fully solved; Fix rate is a partial-credit metric based on the fraction of previously-failing tests the agent's patch makes pass."}
dataset: {size: 48, size_note: "48 software-evolution tasks built from the release notes of 7 mature open-source Python projects; tasks average ~21 files changed and 874 tests per instance.", url: "https://github.com/SWE-EVO/SWE-EVO", license: "", languages: [Python], modalities: [code, text], splits: "single evaluation set", public_test_set: null}
publisher: {org: "FPT Software AI Center; University of Melbourne (School of Computing and Information Systems)", authors: [Minh Vu Thai Pham, Tue Le, Dung Nguyen Manh, Huy Nhat Phan, Nghi D. Q. Bui], url: "https://github.com/SWE-EVO/SWE-EVO"}
paper: {title: "SWE-EVO: Benchmarking Coding Agents in Long-Horizon Software Evolution Scenarios", arxiv: "2512.18470", url: "https://arxiv.org/abs/2512.18470", year: 2026}
leaderboard_url: ""
repo_url: https://github.com/SWE-EVO/SWE-EVO
released: "2026-04"
last_updated: ""
lineage: {family: swe_bench, predecessor: swe_bench_verified, successors: [], variants: []}
saturation: {status: open, top_score: 25, as_of: "2026-04", note: "GPT-5.4 with OpenHands scores 25% resolved on SWE-EVO versus 72.80% on SWE-Bench Verified, per the paper; the authors present this gap as evidence the benchmark is unsaturated and separates models that look similar on single-issue SWE-bench tasks."}
contamination: {risk: unknown, note: "Tasks are built from real project release notes; the paper does not state a contamination study or training-data exclusion method, so exposure risk is not established."}
harness: {lm_eval: "", inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: "Reference harness in the SWE-EVO GitHub repository; the paper reports results using OpenHands as the agent scaffold."}
tags: [benchmark, coding, agentic, multi-file, software-evolution]
sources:
  - url: https://arxiv.org/abs/2512.18470
    title: "SWE-EVO: Benchmarking Coding Agents in Long-Horizon Software Evolution Scenarios"
    accessed: "2026-09-08"
  - url: https://arxiv.org/html/2512.18470v5
    title: SWE-EVO paper, HTML rendering (v5)
    accessed: "2026-09-08"
  - url: https://github.com/SWE-EVO/SWE-EVO
    title: SWE-EVO reference repository
    accessed: "2026-09-08"
freshness: {researched: "2026-09-09", researched_by: "GPT-5.6 Luna, luna-stream-b-003 (Codex coordinated)", reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-stream-b-003"}
---
## What it measures

SWE-EVO tests whether a coding agent can execute a realistic software evolution task instead of a
single, isolated bug fix. Each task starts from the release notes of a mature open-source Python
project and asks the agent to make the set of multi-file changes the notes describe, working from a
repository snapshot taken before those changes landed.

Where SWE-bench style benchmarks isolate one GitHub issue in one or a few files, SWE-EVO tasks span
an average of about 21 files and are checked against an average of 874 tests per instance, so success
requires understanding how a change ripples across a codebase rather than patching a single
function.

## How it is scored

The paper reports two metrics: Resolved rate, the share of task instances where all tests pass after
the agent's changes are applied, and Fix rate, a partial-credit metric giving the fraction of the
task's previously-failing tests that the agent's patch turns passing. Fix rate is intended to
distinguish agents that make real partial progress on a large task from agents that make none, since
binary resolution is rare at this task size. No random or human baseline is established in the
sources reviewed.

## Dataset and licence

SWE-EVO comprises 48 tasks drawn from seven mature open-source Python projects, built from each
project's release notes rather than from individual issues. The reviewed sources do not state a
dataset licence; this is left unknown rather than assumed. The benchmark's reference materials are
hosted at the SWE-EVO GitHub repository.

## Who publishes it

SWE-EVO was introduced by researchers at the FPT Software AI Center, with a co-author from the
University of Melbourne's School of Computing and Information Systems. The paper, "SWE-EVO:
Benchmarking Coding Agents in Long-Horizon Software Evolution Scenarios," is authored by Minh Vu
Thai Pham, Tue Le, Dung Nguyen Manh, Huy Nhat Phan, and Nghi D. Q. Bui. No separate public leaderboard
was found in the sources reviewed.

## Lineage

SWE-EVO is positioned as a harder, longer-horizon successor to the single-issue SWE-bench family: the
paper contrasts its own results directly against SWE-Bench Verified scores for the same models. It
does not use SWE-bench's dataset or task format, so it is recorded here as a distinct benchmark in the
SWE-bench family rather than a subset. No predecessor or successor benchmark within this repository
was established beyond that comparison.

## Saturation and contamination

SWE-EVO is not saturated: the paper reports GPT-5.4 with the OpenHands scaffold resolving only 25% of
tasks, against 72.80% for the same class of model on SWE-Bench Verified, and frames this gap as
evidence that current agents struggle with sustained, multi-file reasoning. Contamination risk is
unknown; the reviewed sources do not describe a contamination check, and the tasks are built from
public release notes of existing open-source projects, which could appear in training data.

## How to run it

There is no listed lm-evaluation-harness, HELM, or OpenCompass task name in the sources reviewed. The
paper's own results were produced using the OpenHands agent scaffold, and a reference implementation
is published at the SWE-EVO GitHub repository. Because the benchmark grades agents rather than raw
completions, reported scores depend heavily on the agent scaffold, tool access, and step budget used,
none of which are standardized across reporters in the material reviewed.

## Reading the numbers

A high SWE-EVO score means an agent can plan and execute changes that span many files in a real
codebase and keep a large test suite passing, a stronger and rarer signal than resolving a single
GitHub issue. A low score does not mean the agent is generally weak at coding, since the task horizon
here is intentionally much longer than SWE-bench's. Because Fix rate gives partial credit, look at
both Fix rate and Resolved rate together rather than either alone. With only 48 tasks, differences of
a few tasks translate into large percentage swings, so treat close scores as within noise. Compare
scores only across the same agent scaffold and step budget, since the paper reports very different
results for the same model family depending on how it is deployed.
