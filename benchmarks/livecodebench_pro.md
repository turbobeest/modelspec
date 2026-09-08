---
id: livecodebench_pro
name: LiveCodeBench Pro
aliases: ["LCB Pro"]
page_kind: benchmark
category: coding
subcategory: "Olympiad-level competitive programming (Codeforces, ICPC, IOI), continuously updated, medalist-annotated"
status: active
summary: "LiveCodeBench Pro tests models on Olympiad-level Codeforces, ICPC and IOI problems, annotated by competitive-programming medalists, and still finds 0% pass@1 on hard problems for most models."
measures: >
  LiveCodeBench Pro asks whether frontier models can solve genuinely hard, Olympiad-level competitive
  programming problems, in response to claims that LLMs now outperform elite human competitors. Problems
  come from Codeforces, ICPC and IOI (plus a small number of university contests), captured in real time as
  contests conclude and before any accepted solutions, editorials or discussion threads appear online, so
  the pool keeps growing rather than sitting fixed. A team of Olympiad medalists tags every problem by
  difficulty and by a three-way cognitive-focus taxonomy -- knowledge-heavy (template algorithms and
  mathematical facts), logic-heavy (systematic derivation) and observation-heavy (problems that need a
  creative insight or "aha moment") -- and the same medalists conduct line-by-line review of failed
  model submissions to characterize where models actually go wrong.
task_format: >
  The model is given a competitive-programming problem statement and must produce a working solution,
  typically in C++, graded against hidden test cases by an automated judge; the paper's primary evaluation
  gives models no external tools or terminal access. Problems are grouped into Easy (Codeforces rating up to
  2000), Medium (2000-3000) and Hard (above 3000) difficulty tiers.
metric:
  name: "Pass@1 by difficulty tier (Easy/Medium/Hard)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    No single numeric human baseline is published (the paper instead frames results against what
    Olympiad-medalist humans can do on the same problems, qualitatively). The live leaderboard at
    livecodebenchpro.com additionally converts performance into a Codeforces-style Elo rating per model, a
    second, ranking-oriented metric alongside per-tier pass@1 that this schema's single metric field does
    not capture directly.
dataset:
  size: null
  size_note: >
    584 problems as of the paper's original April 25, 2025 cutoff, sourced from Codeforces, ICPC and IOI
    (plus a small number of university contests such as MIT's and Tsinghua's), explicitly excluding
    LeetCode as "easier and especially prone to training-data contamination." The pool is continuously
    updated: the Hugging Face dataset card (accessed 2026-09-08) organizes problems into dated
    quarterly/biannual splits, for example a `quater_2025_7_9` split of 144 problems for July-September
    2025, confirming growth well beyond the paper's original count and window.
  url: "https://huggingface.co/datasets/QAQAQAQAQ/LiveCodeBench-Pro"
  license: >
    Apache-2.0 per the Hugging Face dataset card's licence tag; no licence file was found in the
    GavinZhengOI/LiveCodeBench-Pro evaluation-code repository. Individual problem statements originate from
    Codeforces, ICPC and IOI and may carry those contests' own terms independent of this repackaging.
  languages: ["en"]
  modalities: ["text", "code"]
  splits: >
    No fixed train/test split; the Hugging Face dataset is organized into dated quarterly/biannual snapshots
    (for example quater_2024_10_12, quater_2025_1_3, quater_2025_4_6, quater_2025_7_9) as the live pool
    grows, and the public leaderboard additionally offers a rolling "Live" view plus fixed quarterly windows
    (24Q4, 25Q1, 25Q2, 25Q3).
  public_test_set: false
publisher:
  org: "New York University, Princeton University, UC San Diego, University of Washington and other institutions (multi-university team with Olympiad-medalist annotators)"
  authors: ["Zihan Zheng", "Zerui Cheng", "Zeyu Shen", "Shang Zhou", "Kaiyuan Liu", "Hansen He", "Dongruixuan Li", "Stanley Wei", "Hangyi Hao", "Jianzhu Yao", "Peiyao Sheng", "Zixuan Wang", "Wenhao Chai", "Aleksandra Korolova", "Peter Henderson", "Sanjeev Arora", "Pramod Viswanath", "Jingbo Shang", "Saining Xie"]
  url: "https://livecodebenchpro.com"
paper:
  title: "LiveCodeBench Pro: How Do Olympiad Medalists Judge LLMs in Competitive Programming?"
  arxiv: "2506.11928"
  url: "https://arxiv.org/abs/2506.11928"
  year: 2025
leaderboard_url: "https://livecodebenchpro.com/projects/livecodebench-pro/leaderboard"
repo_url: "https://github.com/GavinZhengOI/LiveCodeBench-Pro"
released: "2025-06"
last_updated: ""
lineage:
  family: ""
  predecessor: "live_code_bench"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 46.7
  as_of: "2026-09"
  note: >
    At the paper's original release, every evaluated model scored 0% pass@1 on Hard-tier problems, and the
    best model (o4-mini-high) reached only 53.5% on Medium and 83.1% on Easy. The live leaderboard at
    livecodebenchpro.com, accessed 2026-09-08 on its rolling "Live" window, showed clear progress and
    continued separation rather than saturation: Gemini 3 Deep Think led on Hard at 46.7% (81.6% Medium,
    95.0% Easy, 3298 Elo), ahead of Gemini 3.1 Pro Preview at 40.0% Hard (2887 Elo) and GPT-5.2-high
    (2025-12-11) at 33.3% Hard (2393 Elo); several other current models clustered around 6.7% Hard and a
    further group sat at 0.0% Hard, so scores still spread widely across the field even though the ceiling
    itself has moved a great deal since mid-2025.
contamination:
  risk: low
  note: >
    Contamination resistance is a core design goal, inherited from and strengthened beyond the original
    LiveCodeBench: problems are captured in real time as contests conclude, explicitly before any accepted
    solutions, editorials or discussion threads appear online, and LeetCode problems are excluded by policy
    for being especially contamination-prone. The Hugging Face dataset is also access-gated (automatic
    approval) rather than freely scraped, and the judge grades against hidden test cases not included in the
    public problem statements, so a model cannot pattern-match a public reference solution to the exact
    grading tests. Risk rises for older dated snapshots as more time passes and more models are trained
    after those problems' release dates, the same dynamic that motivates the benchmark's continuously
    updated design.
harness:
  lm_eval: ""
  inspect_evals: "livecodebench_pro"
  helm: ""
  opencompass: "livecodebench_pro"
  bigbench: ""
  other: >
    The paper's primary evaluation uses the fixed prompt "You are a competitive programmer. You will be
    given a problem statement, please implement the solution in C++," submitted without external tools or
    terminal access; a separate pass@k analysis (with multiple sampled attempts) is reported alongside
    pass@1. The UK AI Security Institute's Inspect Evals package registers `livecodebench_pro`
    (`uv run inspect eval inspect_evals/livecodebench_pro --model <name>`), grading submissions through a
    Docker-based judge service ("LightCPVerifier", built on go-judge) that requires privileged Docker mode
    and returns CORRECT, INCORRECT or Unscored (judge-infrastructure failures are scored Unscored rather
    than Incorrect so outages do not depress results). OpenCompass separately registers `livecodebench_pro`
    with matching generation and raw-prompt configs.
tags: ["coding", "competitive-programming", "olympiad", "contamination-resistant", "continuously-updated"]
sources:
  - url: "https://arxiv.org/abs/2506.11928"
    title: "LiveCodeBench Pro: How Do Olympiad Medalists Judge LLMs in Competitive Programming?"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2506.11928"
    title: "LiveCodeBench Pro, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://livecodebenchpro.com/projects/livecodebench-pro/leaderboard"
    title: "LiveCodeBench Pro full leaderboard"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/QAQAQAQAQ/LiveCodeBench-Pro"
    title: "QAQAQAQAQ/LiveCodeBench-Pro dataset card API, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/GavinZhengOI/LiveCodeBench-Pro"
    title: "GavinZhengOI/LiveCodeBench-Pro evaluation code repository"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/livecodebench_pro"
    title: "inspect_evals livecodebench_pro task"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/livecodebench_pro/README.md"
    title: "inspect_evals: livecodebench_pro README"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/livecodebench_pro"
    title: "OpenCompass livecodebench_pro dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LiveCodeBench Pro asks whether frontier models can solve genuinely hard, Olympiad-level competitive
programming problems, written in direct response to claims that LLMs already outperform elite human
competitors. Problems come from Codeforces, ICPC and IOI, plus a small number of university contests,
captured in real time as contests conclude and before any accepted solutions, editorials or discussion
threads appear online, so the pool grows continuously rather than sitting fixed. A team of Olympiad
medalists annotates every problem by difficulty and by a three-way cognitive-focus taxonomy --
knowledge-heavy (template algorithms and mathematical facts), logic-heavy (systematic derivation), and
observation-heavy (needing a creative insight) -- and the same medalists conduct line-by-line review of
failed model submissions, giving the benchmark a qualitative diagnosis of where models go wrong, not just a
pass/fail count.

## How it is scored

A submitted solution, typically C++, is compiled and run against hidden test cases by an automated judge
and scored pass@1; a separate pass@k analysis with multiple sampled attempts is reported alongside it.
Problems are grouped into Easy (Codeforces rating up to 2000), Medium (2000-3000) and Hard (above 3000)
tiers, and pass@1 is reported per tier rather than blended into one number. The paper's primary evaluation
gives models no external tools or terminal access, so scores reflect direct code generation alone. The
public leaderboard additionally converts performance into a Codeforces-style Elo rating, read against the
same scale competitive programmers use for each other.

## Dataset and licence

584 problems as of the paper's original April 2025 cutoff, drawn from Codeforces, ICPC and IOI (plus a few
university contests), with LeetCode excluded by policy as "easier and especially prone to training-data
contamination." The Hugging Face dataset card shows the pool organized into dated quarterly and biannual
snapshots and still growing past the paper's original count. The card lists an Apache-2.0 licence; no
separate licence file was found in the evaluation-code repository, and individual problems may also carry
their originating contest's own terms. Unlike most benchmarks in this repository, the dataset is
access-gated on Hugging Face (automatic approval), and the hidden test cases used for grading are not
included in the public problem statements.

## Who publishes it

LiveCodeBench Pro comes from a 19-author, multi-university team led by Zihan Zheng and Zerui Cheng (full
list in this page's front matter), spanning New York University, Princeton University, UC San Diego and the
University of Washington among others, posted to arXiv in June 2025. The project maintains a dedicated
site, livecodebenchpro.com, with a continuously updated leaderboard and later publications (such as an
"AutoCode" follow-on) beyond the original paper.

## Lineage

LiveCodeBench Pro is an explicit, harder successor to LiveCodeBench (this repository's live_code_bench.md):
where the original draws continuously from LeetCode, AtCoder and Codeforces at a range of difficulties,
LiveCodeBench Pro narrows to Olympiad-tier Codeforces, ICPC and IOI problems, deliberately excludes
LeetCode, and adds medalist annotation and line-by-line failure review the original lacks. No successor or
variant of LiveCodeBench Pro itself is catalogued in this repository.

## Saturation and contamination

At release, every model scored 0% pass@1 on Hard, and the best model (o4-mini-high) reached only 53.5% on
Medium and 83.1% on Easy -- elite human competitors still clearly outperformed every model on the hardest
problems. The live leaderboard, accessed 2026-09-08 on its rolling "Live" window, shows real progress
without saturation: Gemini 3 Deep Think led Hard at 46.7% (81.6% Medium, 95.0% Easy, 3298 Elo), ahead of
Gemini 3.1 Pro Preview (40.0% Hard) and GPT-5.2-high (33.3% Hard), with several models clustered near 6.7%
Hard and a further group at 0.0% -- scores still separate the field even as the frontier has moved
substantially. Contamination risk is low by design: continuously updated dated collection, excluding
contamination-prone LeetCode, gated dataset access, and hidden grading test cases together make this one of
the more contamination-resistant coding benchmarks here, though risk rises for older snapshots over time.

## How to run it

The reference protocol submits a fixed prompt ("You are a competitive programmer... implement the solution
in C++") with no external tools or terminal access, grading pass@1 and pass@k against hidden test cases.
Inspect Evals registers `livecodebench_pro` (`uv run inspect eval inspect_evals/livecodebench_pro --model
<name>`), using a Docker-based judge ("LightCPVerifier," built on go-judge) that needs privileged Docker
mode and returns CORRECT, INCORRECT or Unscored, with judge-infrastructure failures scored Unscored so
outages do not depress results. OpenCompass separately registers `livecodebench_pro` with matching configs.
Because the pool keeps growing, always check which dated window or "Live" snapshot a score used.

## Reading the numbers

A high LiveCodeBench Pro score, especially on Hard, is meaningful: at launch every model scored 0% there,
and reaching even the mid-40s percent as of this research date required real progress, not incremental
gains. Because the benchmark reports Easy, Medium and Hard separately (and the live site adds an Elo
rating), compare the same tier and metric, and note whether a score used the paper's no-tools setting or a
leaderboard submission with different tool access. Since the pool is continuously updated and partly gated,
also check the dated window: an early, more-exposed snapshot is not comparable to the most recent one.
