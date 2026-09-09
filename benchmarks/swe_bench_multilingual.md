---
id: swe_bench_multilingual
name: SWE-bench Multilingual
aliases: ["SWE-bench_Multilingual"]
page_kind: benchmark
category: coding
subcategory: "GitHub issue resolution / patch generation, non-Python languages"
status: active
summary: "SWE-bench Multilingual extends SWE-bench's real-GitHub-issue patch task to 300 tasks across 9 non-Python languages and 42 repositories."
measures: >
  SWE-bench Multilingual tests whether a model can resolve a real GitHub issue by patching a repository
  written in a language other than Python, since the original SWE-bench is Python-only. Each of the 300
  task instances gives the model an issue description and a snapshot of one of 42 repositories, spanning
  C, C++, Go, Java, JavaScript, TypeScript, PHP, Ruby and Rust, at the commit before a real pull request
  fixed the issue. The model must locate the relevant code in an unfamiliar, non-Python codebase and
  produce a change a maintainer would accept, without being shown the tests that grade it.
task_format: >
  Identical in spirit to SWE-bench: given an issue description and repository access, the system outputs
  a patch, applied inside a container and graded against FAIL_TO_PASS and PASS_TO_PASS tests recovered
  from the original fixing pull request. Multilingual reuses SWE-bench's dataset format and evaluation
  protocol so existing SWE-bench infrastructure can run it with no changes, but (unlike the original) does
  not pre-build shared dependency-cache "environment" images, since its 300 tasks are spread across 42
  largely dependency-independent repositories rather than concentrated in a few.
metric:
  name: "% resolved (FAIL_TO_PASS and PASS_TO_PASS tests both pass)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No human baseline published. The only score in the announcement is an SWE-agent + Claude 3.7 Sonnet run at 43% resolved, versus 63% for the same setup on SWE-bench Verified."
dataset:
  size: 300
  size_note: >
    300 task instances from 42 repositories across 9 languages: C, C++, Go, Java, JavaScript, TypeScript,
    PHP, Ruby and Rust. Repositories were chosen from the most-starred GitHub projects in each language
    (about 30% of candidates were discarded for being too slow or unable to build locally), then filtered
    to issue/PR pairs with at least one test file, a clearly stated problem, and a PR implementing only
    that issue. At the median, a task's gold patch touches 10 lines of code; at the 95th percentile, 110.
  url: "https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual"
  license: ""
  languages: [C, C++, Go, Java, JavaScript, TypeScript, PHP, Ruby, Rust]
  modalities: [code, text]
  splits: "single set of 300 task instances; no train/dev split described"
  public_test_set: true
publisher:
  org: "Independent release by Kabir Khandpur, developed in collaboration with the SWE-bench team; cross-posted on swebench.com"
  authors: ["Kabir Khandpur", "Kilian Lieret", "Carlos E. Jimenez", "Ofir Press", "John Yang"]
  url: "https://www.swebench.com/multilingual.html"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://www.swebench.com/multilingual.html"
repo_url: "https://github.com/swe-bench/SWE-bench"
released: "2025-05"
last_updated: ""
lineage:
  family: swe_bench
  predecessor: swe_bench
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 43.0
  as_of: "2025-05"
  note: >
    The only published number is the announcement's own baseline: SWE-agent under a $2.50 cost cap plus
    Claude 3.7 Sonnet resolved 43% of tasks, well below the 63% the same setup reached on SWE-bench
    Verified. Resolution rate varied sharply by language in that run, from 0% on the sampled
    micropython/babel/faker tasks up to 100% on the (small) nushell, nlohmann/json, javaparser and RxJava
    samples; the announcement itself cautions this reflects one model on a small per-repository sample,
    not a stable per-language ranking. No later, broader leaderboard was found, so whether stronger, more
    recent models have closed this gap is not established here.
contamination:
  risk: high
  note: >
    Same structural exposure as the rest of the family: every instance is a real, publicly merged GitHub
    pull request, so a model trained after an instance's merge date may have seen the literal fix.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Runs on the standard SWE-bench Docker evaluation harness and CLI (no dedicated harness of its own);
    the announcement's baseline used the SWE-agent scaffold. Not confirmed in the lm-evaluation-harness,
    HELM, OpenCompass or BIG-bench task lists.
tags: [coding, agentic, github-issues, patch-generation, docker, multilingual]
sources:
  - url: "https://www.swebench.com/multilingual.html"
    title: "SWE-bench Multilingual"
    accessed: "2026-09-08"
  - url: "http://web.archive.org/web/20250507074320/https://kabirk.com/multilingual"
    title: "SWE-bench Multilingual (original announcement, Wayback Machine capture 7 May 2025)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2310.06770"
    title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice M"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SWE-bench Multilingual asks whether a model's ability to resolve real GitHub issues, first measured by
SWE-bench in Python, holds up in other languages. It gives a model an issue description and a repository
snapshot from one of 42 projects written in C, C++, Go, Java, JavaScript, TypeScript, PHP, Ruby or Rust,
at the commit immediately before a real pull request fixed that issue. The model must find the relevant
code in a codebase it has likely never seen configured this way, and produce a change a maintainer would
accept, without seeing the tests used to grade it.

## How it is scored

Scoring is unchanged from SWE-bench: a candidate patch is applied inside a container and must make the
instance's FAIL_TO_PASS tests pass while leaving its PASS_TO_PASS tests passing, with no partial credit.
Multilingual deliberately keeps SWE-bench's dataset format and evaluation protocol so existing SWE-bench
tooling runs it without modification; the one difference is that it skips SWE-bench's pre-built
"environment" dependency-cache images, since 300 tasks spread across 42 repositories rarely share
dependencies the way SWE-bench's more concentrated set does.

## Dataset and licence

300 task instances were collected from 42 of the most-starred repositories in each of 9 languages chosen
from the Stack Overflow Developer Survey's most-used list. About 30% of candidate repositories were
dropped for being unbuildable or too slow to test locally. Within the survivors, issue/PR pairs were kept
only if the PR touched a test file, the issue was clearly specified, and the PR implemented just that
issue; each surviving instance then went through a manual build-test-apply-patch-retest cycle before
inclusion. No licence for the dataset itself was stated on the pages read for this entry.

## Who publishes it

SWE-bench Multilingual was released as an individual project by Kabir Khandpur, working with SWE-bench
team members Kilian Lieret, Carlos E. Jimenez, Ofir Press and John Yang, and cross-posted to swebench.com.
Archived copies place the announcement in early May 2025. Unlike SWE-bench, Verified and Multimodal, it
has no dedicated paper; the author's own citation request points readers to the unrelated SWE-smith paper
(arXiv:2504.21798) rather than a paper describing Multilingual itself.

## Lineage

Multilingual is one of several extensions built on the base SWE-bench (`swe_bench`) collection methodology
and dataset format, alongside SWE-bench Verified (`swe_bench_verified`), SWE-bench Multimodal
(`swe_bench_multimodal`) and the independently produced SWE-bench Pro. It is a sibling to these rather
than a descendant of Verified specifically: the announcement compares its results to Verified's numbers
but does not build on Verified's curated instance set. No successor to Multilingual itself was found.

## Saturation and contamination

The announcement reports exactly one evaluated setup — SWE-agent plus Claude 3.7 Sonnet under a $2.50
cost cap — resolving 43% of tasks, against 63% for the same pairing on SWE-bench Verified. Resolution rate
varied widely by language in that single run, from 0% on the sampled micropython, babel and faker tasks to
100% on small nushell, nlohmann/json, javaparser and RxJava samples; the author explicitly cautions this
reflects one model on small per-repository samples rather than a durable per-language ranking. No later or
broader leaderboard was found in this research pass, so it is not established whether, or by how much,
more recent models have improved on this baseline. Contamination risk is high for the same structural
reason as the rest of the family: every instance is a real, dated, publicly merged pull request.

## How to run it

Multilingual runs on the standard SWE-bench Docker evaluation harness and its `swebench` CLI; no separate
harness was built for it. The published baseline used the SWE-agent scaffold specifically, so, as with the
rest of the family, comparing resolution rates across publishers means comparing scaffolds and cost/step
budgets as much as underlying models. It was not found in the lm-evaluation-harness, HELM, OpenCompass or
BIG-bench task lists.

## Reading the numbers

A Multilingual score, where one exists, says whether a system's SWE-bench-style patching ability
generalises past Python and past the handful of languages many coding agents are tuned for. Because only
one baseline has been published for this benchmark, a reader encountering a Multilingual number elsewhere
should check what scaffold and cost budget produced it before comparing it to anything, including the 43%
baseline recorded here. A gap between a model's Verified and Multilingual scores, as seen in the one
available data point, points at tooling and training data skewed toward Python rather than at general
reasoning ability.
