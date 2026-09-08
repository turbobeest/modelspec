---
id: swe_bench
name: SWE-bench
aliases: ["SWE-bench Full", "SWE-bench Original"]
page_kind: family
category: coding
subcategory: "GitHub issue resolution / patch generation"
status: superseded
summary: "SWE-bench tests whether a model can resolve real GitHub issues by generating a patch, checked by the repository's own test suite; Verified now supersedes the original set for most reporting."
measures: >
  SWE-bench gives a model a real GitHub issue and a snapshot of the repository at the commit before it
  was fixed, and asks it to produce a patch that resolves the issue. Tasks require locating the
  relevant code across a real, multi-file Python codebase, understanding what the issue is asking for,
  and making a change that a project maintainer would accept, rather than answering a self-contained
  puzzle. The model is not shown the tests used to grade it.
task_format: >
  Given an issue description and repository access (directly, or through retrieval, depending on the
  system under test), the model outputs a patch/diff. The patch is applied to a containerised checkout
  of the repository and graded by running two sets of tests recovered from the pull request that
  originally fixed the issue.
metric:
  name: "% resolved (FAIL_TO_PASS and PASS_TO_PASS tests both pass)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No formal human baseline was established by the original paper."
dataset:
  size: 2294
  size_note: "2,294 task instances collected from pull requests and issues across 12 popular Python repositories."
  url: "https://huggingface.co/datasets/princeton-nlp/SWE-bench"
  license: MIT
  languages: [Python]
  modalities: [code, text]
  splits: "single test split (no official train/dev split in the original release)"
  public_test_set: true
publisher:
  org: "Originally Princeton NLP; maintained today by the SWE-bench Team"
  authors: [Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik R. Narasimhan]
  url: "https://www.swebench.com/"
paper:
  title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
  arxiv: "2310.06770"
  url: "https://arxiv.org/abs/2310.06770"
  year: 2023
leaderboard_url: "https://www.swebench.com/"
repo_url: "https://github.com/SWE-bench/SWE-bench"
released: "2023-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: [swe_bench_verified]
  variants: [swe_bench_pro, swe_bench_multilingual, swe_bench_multimodal, swe_bench_agent]
saturation:
  status: open
  top_score: 20.0
  as_of: "2024-08"
  note: >
    OpenAI's SWE-bench Verified announcement cites 20% resolved on the original SWE-bench leaderboard
    and 43% on SWE-bench Lite as of 2024-08-05, up from a 1.96% RAG baseline at the October 2023
    release and 12.47% for the first agent-based system (SWE-agent) shortly after. Community
    leaderboard activity on the unfiltered original set largely stopped after SWE-bench Verified
    launched days later, so a more recent top score for this exact dataset was not found.
contamination:
  risk: high
  note: >
    Every task instance is a real, merged GitHub pull request with a public commit history; a model
    trained after an instance's fix was merged may have seen the exact patch during pretraining, not
    just the surrounding repository. This is a stronger contamination vector than "the repo appears in
    training data" alone.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official Docker-based evaluation harness in the SWE-bench repository (see
    docs/20240627_docker), invoked via the `swebench` CLI (`swebench eval ...`). Not confirmed to be
    part of the lm-evaluation-harness, HELM, OpenCompass or BIG-bench task lists.
tags: [coding, agentic, github-issues, patch-generation, docker, software-engineering]
sources:
  - url: "https://arxiv.org/abs/2310.06770"
    title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
    accessed: "2026-09-07"
  - url: "https://github.com/SWE-bench/SWE-bench"
    title: "SWE-bench/SWE-bench repository"
    accessed: "2026-09-07"
  - url: "https://www.swebench.com/original.html"
    title: "SWE-bench (original) overview"
    accessed: "2026-09-07"
  - url: "https://www.swebench.com/SWE-bench/"
    title: "SWE-bench project overview"
    accessed: "2026-09-07"
  - url: "https://openai.com/index/introducing-swe-bench-verified/"
    title: "Introducing SWE-bench Verified | OpenAI"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SWE-bench measures whether a language model can act as a software engineer on a real codebase: given a
GitHub issue and the repository at the commit before it was fixed, produce a change that resolves it.
Each of the 2,294 task instances is built from an actual merged pull request in one of 12 popular Python
projects (including Django, Sympy, scikit-learn and matplotlib), so tasks require finding the right
files in a large, unfamiliar codebase and making a change consistent with how the project is actually
structured, not just solving an isolated puzzle. The model sees only the issue text; it does not see the
tests that will grade it.

## How it is scored

Every instance carries two sets of tests recovered from the original fixing pull request. FAIL_TO_PASS
tests fail before the fix and pass after it; they are the primary signal that the issue was actually
resolved. PASS_TO_PASS tests pass both before and after; they confirm the patch did not break unrelated
functionality. A patch must satisfy both sets to count as resolved — there is no partial credit. The
original paper's baseline used retrieval-augmented generation (RAG) to fetch candidate files before
asking a model to generate a patch in one shot; most current results instead come from agentic systems
that read, run and edit the repository over multiple steps.

## Dataset and licence

The dataset and evaluation code are released under the MIT licence. It contains 2,294 instances mined by
crawling pull requests and issues from 12 popular Python repositories, keeping only PRs that resolve an
issue and touch at least one test file. Each instance ships with a Docker image that reproduces the
repository's environment at the pre-fix commit. All instances, and their tests, are public.

## Who publishes it

SWE-bench comes from Carlos E. Jimenez and John Yang (equal contribution), with Alexander Wettig, Shunyu
Yao, Kexin Pei, Ofir Press and Karthik Narasimhan, originally at Princeton NLP. It was released in
October 2023 and accepted as an oral presentation at ICLR 2024. The project, now presented as maintained
by "the SWE-bench Team," continues to host the dataset, leaderboard and a growing family of related
tools (SWE-agent, SWE-smith, SWE-ReX, mini-SWE-agent, the SWE-bench CLI) at swebench.com.

## Lineage

SWE-bench is the root of its own family. SWE-bench Verified (`swe_bench_verified`), released by OpenAI
with the SWE-bench authors in August 2024, explicitly supersedes both the original set and SWE-bench
Lite (a smaller, faster-to-run subset that does not yet have its own page in this repository) and has
become the default reference. SWE-bench Multimodal (`swe_bench_multimodal`) and SWE-bench Multilingual
(`swe_bench_multilingual`) extend the same collection methodology to visual, JavaScript/TypeScript tasks
and to nine non-Python languages respectively. SWE-bench Pro (`swe_bench_pro`) is a harder, independently
produced benchmark from Scale AI in the same spirit rather than an official successor. `swe_bench_agent`
is catalogued in this repository as a further family member; see its own page for what could and could
not be established about it.

## Saturation and contamination

On the original, unfiltered instance set, OpenAI reported roughly 20% resolved for the best agents as of
August 2024 — up sharply from a 1.96% baseline at launch and 12.47% for the first agentic system,
SWE-agent, but still far from any ceiling. Contamination risk is high and structural: every instance is a
real pull request with public history, so a model trained after an instance's merge date may have seen
the literal fix rather than having to derive it. OpenAI's own investigation (leading to SWE-bench
Verified) additionally found that many original instances were unfairly hard or impossible regardless of
contamination, due to underspecified issues or overly strict tests — a separate, non-contamination source
of noise in reported scores.

## How to run it

The reference harness lives in the SWE-bench GitHub repository and evaluates predictions inside
per-instance Docker containers, applying a candidate patch and running the FAIL_TO_PASS/PASS_TO_PASS
tests. It is invoked through the `swebench` command-line tool. Numbers are hard to compare across
publishers because of differences in scaffold (RAG-style single-shot generation versus a multi-step
agent with a shell), how much of the repository the system is allowed to see, and time/step budgets;
none of these are fixed by the benchmark itself.

## Reading the numbers

A "SWE-bench" score without qualification is ambiguous today: check whether it is the original 2,294-
instance set, SWE-bench Lite, or (most likely for a current model) SWE-bench Verified, since scores on
these are not interchangeable. A high score demonstrates a system can localise and fix real, moderately
scoped bugs in familiar open-source Python projects; it says little about unfamiliar codebases, other
languages, or issues requiring architectural changes, which is exactly the gap the later family members
were built to probe.
