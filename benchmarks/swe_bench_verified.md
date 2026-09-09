---
id: swe_bench_verified
name: SWE-bench Verified
aliases: ["SWE-bench-V"]
page_kind: benchmark
category: coding
subcategory: "GitHub issue resolution / patch generation"
status: active
summary: "A 500-task, human-screened subset of SWE-bench that OpenAI released with the SWE-bench authors to remove unfair or impossible samples; now the default SWE-bench reference."
measures: >
  SWE-bench Verified measures the same thing as SWE-bench: whether a model can resolve a real GitHub
  issue by patching a Python repository, graded by the tests from the pull request that actually fixed
  it. The difference is curation: OpenAI ran a large human-annotation campaign to remove instances whose
  issue description was too vague or whose tests would reject a genuinely correct fix, so a low score is
  more likely to reflect a real capability gap than a broken task.
task_format: >
  Identical to SWE-bench: given an issue description and repository access, the system outputs a patch,
  which is applied inside a container and graded against FAIL_TO_PASS and PASS_TO_PASS tests recovered
  from the original fixing pull request.
metric:
  name: "% resolved"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No formal human-solve-rate baseline was published; annotators estimated per-task difficulty in wall-clock time instead (see Dataset and licence)."
dataset:
  size: 500
  size_note: >
    500 instances kept from 1,699 samples of the original SWE-bench test set that 93 professional
    software developers screened for well-specified issues and fair tests. Per OpenAI's own annotation
    results, 68.3% of the 1,699 screened samples were filtered out for underspecified problem statements
    (38.3%), unfair or narrow tests (61.1%, these overlap with the first category), or other flagged
    issues; the 500 that remained were chosen by keeping as many harder (1-4 hour and >4 hour) tasks as
    possible and randomly sampling the rest. Within the final 500, OpenAI reports an "easy" subset of
    196 tasks estimated at under 15 minutes to fix and a "hard" subset of 45 tasks estimated at over an
    hour.
  url: "https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified"
  license: MIT
  languages: [Python]
  modalities: [code, text]
  splits: "single test split of 500 instances"
  public_test_set: true
publisher:
  org: "OpenAI, in collaboration with the SWE-bench authors (Princeton NLP / SWE-bench Team)"
  authors: []
  url: "https://openai.com/index/introducing-swe-bench-verified/"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://www.swebench.com/"
repo_url: "https://github.com/SWE-bench/SWE-bench"
released: "2024-08"
last_updated: "2025-02"
lineage:
  family: swe_bench
  predecessor: swe_bench
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 79.2
  as_of: "2025-12"
  note: >
    On swebench.com's own Verified leaderboard (default "Bash Only" harness view, accessed
    2026-09-07), the top entries are two Claude 4.5 Opus runs (Sonar Foundation Agent; live-SWE-agent)
    at 79.20% resolved, both dated December 2025, still unbeaten at access time nine months later even
    as newer frontier models were submitted below that mark. That plateau, well short of 100%, suggests
    the leaderboard's most heavily optimised harnesses have stopped finding easy additional wins, though
    the benchmark itself is not saturated in the sense of sitting at a hard ceiling. GPT-4o resolved
    33.2% at the benchmark's August 2024 release.
contamination:
  risk: high
  note: >
    Inherits SWE-bench's structural contamination risk: every instance is a real, publicly merged pull
    request, so a model trained after an instance's fix date may have seen the literal patch. Verified
    reduces task-quality noise but does not address this.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Uses the SWE-bench Docker-based evaluation harness (co-developed by OpenAI and the SWE-bench
    authors for this release; see github.com/princeton-nlp/SWE-bench/tree/main/docs/20240627_docker).
    swebench.com's own leaderboard additionally distinguishes submissions by scaffold (for example a
    "Bash Only" harness such as mini-SWE-agent versus tool-augmented agents), which materially affects
    scores and is not part of the dataset itself.
tags: [coding, agentic, github-issues, patch-generation, docker, human-filtered]
sources:
  - url: "https://openai.com/index/introducing-swe-bench-verified/"
    title: "Introducing SWE-bench Verified | OpenAI"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2310.06770"
    title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
    accessed: "2026-09-07"
  - url: "https://www.swebench.com/"
    title: "SWE-bench Leaderboards"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SWE-bench Verified measures the same capability as SWE-bench — resolving a real GitHub issue with a
patch that a project's own tests accept — on a subset OpenAI curated specifically to be fair. As part of
its Preparedness Framework work on model autonomy, OpenAI found that SWE-bench "systematically
underestimat[ed] models' autonomous software engineering capabilities" because many instances had
underspecified issue text or tests that would reject valid solutions. Verified removes those instances
so that a failure is more likely to reflect a genuine limitation of the model than a flaw in the task.

## How it is scored

Scoring is unchanged from SWE-bench: a candidate patch is applied inside a container and must make the
instance's FAIL_TO_PASS tests pass while keeping its PASS_TO_PASS tests passing, with no partial credit.
What changed is task selection. OpenAI worked with 93 professional Python developers to label 1,699
SWE-bench test instances on two axes — how well-specified the issue is, and how fair the tests are — each
on a four-point severity scale, with three independent annotators per instance and the maximum severity
among them used as the final label. Instances flagged as severe on either axis, or flagged for other
major problems, were dropped; the paper reports this removed 68.3% of the annotated pool. The final 500
were chosen to keep as many harder tasks as possible before filling the rest at random.

## Dataset and licence

Released under the MIT licence, consistent with the rest of the SWE-bench project, and hosted on Hugging
Face. All 500 instances and their tests are public. OpenAI also published its full annotation set for
all SWE-bench test instances (not just the 500 that became Verified), which lets researchers reproduce
or refine the filtering, and an annotation rubric describing exactly how severity was judged.

## Who publishes it

OpenAI released SWE-bench Verified on 2024-08-13, in collaboration with the original SWE-bench authors,
and updated the post on 2025-02-24. It sits within the broader SWE-bench project (swebench.com), which
hosts its leaderboard and evaluation tooling.

## Lineage

SWE-bench Verified is a direct successor to `swe_bench`: OpenAI states plainly that it "supersedes the
original SWE-bench and SWE-bench Lite test sets," and it is now the version most vendors report by
default when they say "SWE-bench." It sits alongside `swe_bench_multimodal`, `swe_bench_multilingual`,
`swe_bench_pro` and `swe_bench_agent` as the most actively tracked member of the family. It also
motivated the SWE-bench team's own Docker-based evaluation harness, developed jointly with OpenAI for
this release and since adopted as the project's standard.

## Saturation and contamination

Verified opened at a GPT-4o score of 33.2% in August 2024. On swebench.com's own leaderboard, the top
"Bash Only" harness entries have sat at 79.20% since December 2025 and were still unbeaten at the time
this page was researched (September 2026), which points to a plateau among the most tuned open scaffolds
even as new frontier models continue to be submitted lower down the board. Contamination risk remains
high for the reason it is high across the whole family: every instance is a real, dated, publicly merged
pull request.

## How to run it

Run through the SWE-bench Docker harness and the `swebench` CLI, same as the base benchmark. Because the
Verified leaderboard mixes submissions using very different scaffolds — from a plain bash-only agent
loop (mini-SWE-agent) to heavily tool-augmented commercial systems — a resolved-rate comparison across
rows is really a comparison of harnesses as much as of underlying models, and swebench.com's own UI
splits results by harness type for exactly this reason.

## Reading the numbers

A high score on SWE-bench Verified means a system reliably fixes real, moderately scoped bugs in popular
open-source Python projects when the issue is clearly stated and the tests are fair — a meaningfully
higher bar than the noisier original set, but still narrower than general software engineering. It says
little about unfamiliar or private codebases, non-Python languages, or issues that need architectural
judgment rather than a localized fix; `swe_bench_pro`, `swe_bench_multilingual` and `swe_bench_multimodal`
each probe one of those gaps directly.
