---
id: swe_bench_java
name: SWE-bench-java
aliases: ["SWE-bench-java-verified", "SWE-bench Java"]
page_kind: benchmark
category: coding
subcategory: "Java GitHub issue resolution / patch generation"
status: active
summary: "A 91-instance, human-screened Java SWE-bench set from six popular repositories, scored by fail-to-pass unit tests."
measures: >
  SWE-bench-java tests whether a model can resolve a real Java GitHub issue by
  patching the repository at the pre-fix commit. It is the Java analogue of
  SWE-bench Verified: issues are filtered so they compile, have fail-to-pass
  tests, and survive developer screening.
task_format: >
  The system sees the issue text and a Dockerized Maven/Java checkout, then
  emits a patch. Tests from the fixing pull request grade the result. The
  authors evaluated SWE-agent rather than a one-shot RAG baseline.
metric:
  name: "resolved rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No human baseline. Paper Table 2 reports SWE-agent results on all 91 verified instances."
dataset:
  size: 91
  size_note: >
    Final verified split: 91 instances from 6 repositories, counted in
    swe-bench-java-verified.json (google/gson 5, FasterXML/jackson-core 23,
    FasterXML/jackson-databind 49, FasterXML/jackson-dataformat-xml 5,
    apache/dubbo 4, GoogleContainerTools/jib 5). Construction crawled 1,979
    issue instances from 19 repositories, kept 308 that compiled, 137 with
    fail-to-pass and no pass-to-fail tests, then 91 after 10 Java developers
    applied SWE-bench Verified-style screens.
  url: "https://huggingface.co/datasets/Daoguang/Multi-SWE-bench"
  license: Apache-2.0
  languages: [Java]
  modalities: [code, text]
  splits: "java_verified (91 instances)"
  public_test_set: true
publisher:
  org: "Huawei and collaborators"
  authors: [Daoguang Zan, Zhirong Huang, Ailun Yu, Shaoxin Lin, Yifan Shi, Wei Liu, Dong Chen, Zongshuai Qi, Hao Yu, Lei Yu, Dezhi Ran, Muhan Zeng, Bo Shen, Pan Bian, Guangtai Liang, Bei Guan, Pengjie Huang, Tao Xie, Yongji Wang, Qianxiang Wang]
  url: "https://multi-swe-bench.github.io"
paper:
  title: "SWE-bench-java: A GitHub Issue Resolving Benchmark for Java"
  arxiv: "2408.14354"
  url: "https://arxiv.org/abs/2408.14354"
  year: 2024
leaderboard_url: "https://multi-swe-bench.github.io"
repo_url: "https://github.com/multi-swe-bench/multi-swe-bench-env"
released: "2024-08"
last_updated: "2024-09"
lineage:
  family: swe_bench
  predecessor: swe_bench
  successors: [multi_swe_bench]
  variants: [swe_bench_multilingual]
saturation:
  status: open
  top_score: 9.89
  as_of: "2024-08"
  note: >
    Paper Table 2: SWE-agent + DeepSeek-V2-0628 resolved 9.89% (9/91). Other
    listed runs: DeepSeekCoder-V2 7.69%, GPT-4o 6.59%, GPT-4o-mini 1.10%,
    Doubao-pro-128k 1.10%. No later verified-split leaderboard figure was
    confirmed. These 2024 agent scores should not be read as a 2026 ceiling.
contamination:
  risk: high
  note: >
    Instances are public merged Java pull requests with gold patches in the
    dataset, the same structural leak as original SWE-bench.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Docker evaluation environment at multi-swe-bench/multi-swe-bench-env.
    Paper runs used SWE-agent. The authors note they did not configure a
    runtime for every Java issue before those SWE-agent experiments.
tags: [coding, agentic, java, github-issues, patch-generation, docker]
sources:
  - url: "https://arxiv.org/abs/2408.14354"
    title: "SWE-bench-java (arXiv:2408.14354v1)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2408.14354v1"
    title: "SWE-bench-java HTML full text"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Daoguang/Multi-SWE-bench"
    title: "Daoguang/Multi-SWE-bench (SWE-bench-java-verified) dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Daoguang/Multi-SWE-bench/resolve/main/swe-bench-java-verified.json"
    title: "swe-bench-java-verified.json instance file"
    accessed: "2026-09-08"
  - url: "https://github.com/multi-swe-bench/multi-swe-bench-env"
    title: "multi-swe-bench/multi-swe-bench-env Java evaluation README"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-074 (Codex coordinated)"
  reviewed: "2026-09-09"
  reviewed_by: "Grok Build independent review, batch-074"
---

## What it measures

SWE-bench-java measures GitHub issue resolution in Java. The agent gets an issue
and a pre-fix snapshot of a Maven-built project, then must produce a patch that
the project's tests accept. The public set is the verified slice of 91 tasks
from six widely used repositories, including Jackson, Gson, Dubbo, and Jib.

The authors built it as a first non-Python SWE-bench, using Verified-style
human screens so underspecified issues and unfair tests are reduced.

## How it is scored

Resolved rate is the share of the 91 instances where all listed tests pass after
the patch. That is the same fail-to-pass plus pass-to-pass rule as SWE-bench.
Table 2 of the paper reports only SWE-agent runs. DeepSeek-V2 reached 9.89%
(9/91); GPT-4o reached 6.59%. The paper says the SWE-agent port was hasty and
did not configure a runtime for every issue, so those figures are a lower bound
on what a fully wired Java agent might score in 2024.

## Dataset and licence

The Hugging Face card Daoguang/Multi-SWE-bench is Apache-2.0 and contains
`swe-bench-java-verified.json` (91 rows). That hub name is easy to confuse with
ByteDance's later [Multi-SWE-bench](multi_swe_bench.md). Construction started
from 19 Java repositories and 1,979 crawled issues, then compile checks, test
filters, and ten Java developers using OpenAI's Verified annotation rubric.

## Who publishes it

Daoguang Zan, Zhirong Huang, Ailun Yu, Shaoxin Lin, and co-authors at Huawei
and collaborating organisations posted arXiv:2408.14354 on 2024-08-26. The
dataset went up on 2024-08-24 and was last modified 2024-09-03. The 2024 paper
and the Java Docker README still point to multi-swe-bench.github.io; that
domain now titles itself Multi-SWE-bench, which is also the name of the later
multilingual successor. Do not read the live homepage as a 2026 Java-91 board.

## Lineage

This is the Java precursor in the [SWE-bench](swe_bench.md) family. It is not
[SWE-bench Multilingual](swe_bench_multilingual.md), which samples nine
languages including Java in a 300-task SWE-bench-team set. Overlapping authors
later released Multi-SWE-bench (1,632 instances, seven languages, 2025-04),
which is the broader successor rather than a rename of these 91 tasks.

## Saturation and contamination

9.89% in August 2024 is not a ceiling; it is an early SWE-agent snapshot.
Whether 2026 agents saturate the 91-set was not established here. Contamination
risk is high because gold patches are public pull requests.

## How to run it

Use the published Docker environment and the `java_verified` JSON. State the
agent scaffold. Do not drop these 91 Java tasks into a Multi-SWE-bench or
SWE-bench Multilingual average without saying so.

## Reading the numbers

A SWE-bench-java score is Java-only and 91 instances, heavily weighted toward
jackson-databind (49 tasks). It is not a multilingual result. If you need
broader Java-plus-other-language coverage, look at Multi-SWE-bench or
SWE-bench Multilingual instead, and do not treat 2024 SWE-agent percentages as
today's frontier.
