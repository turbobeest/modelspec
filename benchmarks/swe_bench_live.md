---
id: swe_bench_live
name: SWE-bench-Live
aliases: ["SWE-bench Live", "SWE-bench Goes Live"]
page_kind: benchmark
category: coding
subcategory: "live GitHub issue resolution / patch generation"
status: active
summary: "A continuously updated SWE-bench-style issue-resolution set built from recent GitHub issues, with frozen Lite/Verified splits and a growing full split."
measures: >
  SWE-bench-Live asks an agent to resolve a real GitHub issue on a snapshot of the
  repository from before the fix, then grades the patch with the project's tests.
  Unlike the original SWE-bench pool, instances are mined automatically from issues
  created since 2024 and refreshed over time so evaluation is less likely to rest on
  patches already seen in pretraining.
task_format: >
  The agent may use only the problem statement and the instance Docker image. It
  must not read FAIL_TO_PASS, PASS_TO_PASS, hints, or the test patch during rollout.
  A single patch is applied in the container and scored with fail-to-pass and
  pass-to-pass tests, following the original SWE-bench protocol.
metric:
  name: "% resolved"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: "No human solve-rate baseline is published. The paper also reports patch apply rate and file-level localization success."
dataset:
  size: 1888
  size_note: >
    Hugging Face SWE-bench-Live/SWE-bench-Live (Python, accessed 2026-09-09) lists
    four splits: test 1,000, lite 300, verified 500, and full 1,888. The May 2025
    paper described an initial 1,319 Python tasks from 93 repositories (issues from
    2024-01 through 2025-04). Maintainers froze the Python `lite` and `verified`
    splits for leaderboard comparisons. From 2025-09 they add about 50 newly
    quality-filtered issues each month; the Hugging Face card sends those to
    `full`, while the 2025-09-17 GitHub note says they go to `test`. Related
    public sets from the same project are SWE-bench-Live/MultiLang (1,077
    instances across C, C++, Go, JavaScript, Rust, Java, TypeScript, and C# as of
    2026-09-04) and SWE-bench-Live/Windows (61 test instances, MIT, last modified
    2026-09-04).
  url: "https://huggingface.co/datasets/SWE-bench-Live/SWE-bench-Live"
  license: MIT
  languages: [Python, C, C++, C#, Java, JavaScript, TypeScript, Go, Rust]
  modalities: [code, text]
  splits: "Python: test 1000, lite 300, verified 500, full 1888; MultiLang language splits; Windows test 61"
  public_test_set: true
publisher:
  org: Microsoft
  authors: [Linghao Zhang, Shilin He, Chaoyun Zhang, Yu Kang, Bowen Li, Chengxing Xie, Junhao Wang, Maoquan Wang, Yufan Huang, Shengyu Fu, Elsie Nallipogu, Qingwei Lin, Yingnong Dang, Saravan Rajmohan, Dongmei Zhang]
  url: "https://swe-bench-live.github.io/"
paper:
  title: "SWE-bench Goes Live!"
  arxiv: "2505.23419"
  url: "https://arxiv.org/abs/2505.23419"
  year: 2025
leaderboard_url: "https://swe-bench-live.github.io/"
repo_url: "https://github.com/microsoft/SWE-bench-Live"
released: "2025-05"
last_updated: "2026-09"
lineage:
  family: swe_bench
  predecessor: swe_bench
  successors: []
  variants: [swe_bench_verified, swe_bench_lite]
saturation:
  status: open
  top_score: 19.25
  as_of: "2025-05"
  note: >
    On the paper's then-current full Python set, OpenHands with Claude 3.7 Sonnet
    resolved 19.25% of instances (17.67% on the 300-instance Lite subset). The same
    setup resolved 43.20% on SWE-bench Verified. Later MultiLang and Windows
    leaderboard numbers were not extracted from the JavaScript homepage, so a
    2026 top score is not recorded here.
contamination:
  risk: medium
  note: >
    Instances are real public pull requests, so later training runs can still see
    gold patches. Recency (issues after 2024) and monthly additions lower that
    risk relative to the 2023 SWE-bench pool. Frozen lite and verified splits
    age in place; the full split is the moving target.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official evaluation lives in microsoft/SWE-bench-Live. Maintainers recommend
    the python-only branch for the NeurIPS Python set, and the main-branch
    evaluation.evaluation entry point for MultiLang and Windows. Submissions go
    through SWE-bench-Live/submission with rollout trajectories.
tags: [coding, agentic, github-issues, patch-generation, docker, live, contamination-resistant]
sources:
  - url: "https://arxiv.org/abs/2505.23419"
    title: "SWE-bench Goes Live! (arXiv:2505.23419)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2505.23419v2"
    title: "SWE-bench Goes Live! HTML full text"
    accessed: "2026-09-08"
  - url: "https://github.com/microsoft/SWE-bench-Live"
    title: "microsoft/SWE-bench-Live repository README"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/SWE-bench-Live/SWE-bench-Live"
    title: "SWE-bench-Live Python dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/SWE-bench-Live/MultiLang"
    title: "SWE-bench-Live/MultiLang dataset API"
    accessed: "2026-09-08"
  - url: "https://swe-bench-live.github.io/"
    title: "SWE-bench-Live leaderboard homepage"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/SWE-bench-Live/main/LICENSE"
    title: "SWE-bench-Live MIT licence"
    accessed: "2026-09-09"
  - url: "https://arxiv.org/abs/2603.05026"
    title: "RepoLaunch (arXiv:2603.05026)"
    accessed: "2026-09-09"
  - url: "https://huggingface.co/api/datasets/SWE-bench-Live/Windows"
    title: "SWE-bench-Live/Windows dataset API"
    accessed: "2026-09-09"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-074 (Codex coordinated)"
  reviewed: "2026-09-09"
  reviewed_by: "Grok Build independent review, batch-074"
---

## What it measures

SWE-bench-Live tests whether an agent can fix a recent, real GitHub issue. The agent
sees the issue text and a containerized checkout from before the fix, then writes a
patch. Tests recovered from the fixing pull request decide whether the issue is
resolved. The original paper set is Python. The same project later added MultiLang
and Windows tasks that follow the same issue-and-patch shape.

The point of the "live" design is freshness and coverage, not a new scoring rule.
RepoLaunch builds an executable image per instance so new repositories can enter
the pool without months of hand-written environments.

## How it is scored

Scoring copies SWE-bench. FAIL_TO_PASS tests must start failing and end passing.
PASS_TO_PASS tests must stay passing. There is no partial credit. The paper also
reports whether the patch applies cleanly and whether edited files match the gold
patch, but resolved rate is the headline number.

Protocol restrictions are strict. The agent may not apply the hidden test patch
during rollout, and prompts must not contain instance-specific solutions. The
maintainers ask for raw trajectories with leaderboard submissions so they can check
that rule.

## Dataset and licence

The code and Python dataset are MIT-licensed. Hugging Face currently publishes 1,888
Python instances in `full`, with frozen `lite` (300) and `verified` (500) splits
kept for cheaper, comparable runs. The May 2025 paper counted 1,319 Python tasks
from 93 repositories. From 2025-09 the maintainers add about 50 newly filtered
issues a month to the growing pool (`full` on Hugging Face; GitHub's note names
`test`). MultiLang adds 1,077 instances across eight language splits. Windows is a
separate 61-instance set. Gold patches and test lists ship in the dataset, but the
published protocol forbids using them at generation time.

## Who publishes it

Microsoft researchers led by Linghao Zhang, Shilin He, Chaoyun Zhang, Yu Kang, and
colleagues released the paper in May 2025 (arXiv:2505.23419). The GitHub repository
titles the work as NeurIPS 2025 Datasets and Benchmarks and cites NeurIPS volume 38.
The repository, Hugging Face collection, and leaderboard remain under SWE-bench-Live.
A later paper, RepoLaunch (arXiv:2603.05026, submitted 2026-03-05), describes the
multi-language and Windows environment builder.

## Lineage

This is a SWE-bench family member (`swe_bench`), not a replacement for
[SWE-bench Verified](swe_bench_verified.md). It keeps the same fail-to-pass tests
while changing how instances are collected and how often they refresh. Do not
confuse its frozen 300-instance `lite` split with official
[SWE-bench Lite](swe_bench_lite.md). LiveCodeBench is an unrelated live coding
contest set. Multi-SWE-bench and SWE-bench Multilingual are separate multilingual
pools.

## Saturation and contamination

On the paper's full Python set, the best reported agent resolved 19.25% of tasks,
versus 43.20% for the same OpenHands plus Claude 3.7 Sonnet run on Verified. That
gap is the reason the authors argue static SWE-bench numbers overstate skill on
unseen issues. Scores still separate models, so the set is open rather than
saturated. Contamination risk is medium: public history remains, but post-2024
issues and monthly additions reduce overlap with older training cuts.

## How to run it

Install the official repository and run its evaluation script on a predictions
directory. For the Python NeurIPS set, follow the `python-only` branch. For
MultiLang or Windows, use `python -m evaluation.evaluation` on the matching
Hugging Face dataset. Compare only like splits: Lite, Verified, full, MultiLang,
or Windows. Scaffold, iteration budget, and whether trajectories were audited all
move the number.

## Reading the numbers

A strong Live score means the system can localise and patch recent issues in
repositories that were not in the original twelve-project SWE-bench set. It does
not mean the same resolved rate will hold on Verified or Lite. Always name the
split and date, because `full` grows. Treat a large jump on a frozen split as a
capability claim, and a jump only on newly added months as a freshness check.
Look at Verified or SWE-bench Pro alongside it when you need a stable, heavily
reported reference.
