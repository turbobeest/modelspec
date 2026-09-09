---
id: livemathbench
name: "LiveMathBench"
aliases: []
page_kind: benchmark
category: math
subcategory: "continuously-updated, contamination-resistant competition mathematics"
status: active
summary: >-
  A bilingual, periodically re-released competition-math benchmark from recent AMC, CNMO, CCEE and
  Putnam problems, paired with G-Pass@k, a metric scoring correctness and stability across samples.
measures: >
  LiveMathBench gives a model a recent competition mathematics problem, converted to free-response
  form (multiple-choice options are stripped so the model must derive the answer itself), drawn from
  four sources: the China National Mathematical Olympiad (CNMO), China's College Entrance
  Examination (CCEE, from mock exams), the American Mathematics Competition (AMC), and the William
  Lowell Putnam Mathematical Competition (WLPMC). Its purpose-built companion metric, G-Pass@k,
  measures not just whether a model can solve a problem once but whether it solves it consistently
  across many independent samples, addressing what the authors call a gap between a model's
  "potential" (can it ever get this right) and its "stability" (does it reliably get this right). A
  harder subset, LiveMathBench-Hard, is drawn from the same four sources at greater difficulty.
task_format: >
  Free-response: read a competition mathematics problem (in Chinese or English for the v202412
  release; English only for v202505) and produce a worked solution ending in a final answer, with no
  answer choices offered even where the original competition question was multiple choice.
metric:
  name: "G-Pass@k and mG-Pass@k (stability-aware pass rate across repeated samples), alongside plain Greedy accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    G-Pass@k_tau generalises Pass@k: given n samples per question and c of them correct, it computes
    the probability that at least a tau-fraction of any k-sized subset of samples is correct: G-Pass@k
    = E[C(c,k)/C(n,k)] with a threshold variant summing over j from ceil(tau*k) to c. mG-Pass@k
    integrates G-Pass@k_tau over tau from 0.5 to 1.0, combining potential and stability into one
    number. Free-response grading has no meaningful chance rate, so no random baseline is stated; no
    human baseline was found in the sources opened for this page.
dataset:
  size: 238
  size_note: >
    The v202412 release totals 238 problems (119 per language x 2 languages: 46 AMC, 44 CCEE (13
    fill-in-the-blank + 31 problem-solving), 18 CNMO, 11 WLPMC per language), confirmed from the
    paper's own Table 4 and matched by the per-file counts in the OpenCompass README. The v202505
    release (announced June 2025) replaces this with an English-only "all" and "hard" configuration
    on Hugging Face; this research could not confirm v202505's exact item count because the dataset
    repository requires an accepted access request to view. The project states LiveMathBench "will
    undergo ongoing updates with new questions," so its size is a moving target by design, not a
    fixed number.
  url: "https://huggingface.co/datasets/opencompass/LiveMathBench"
  license: >
    Listed as CC BY 4.0 on the dataset card, but the repository is access-gated and requires agreeing
    to a checkbox reading "I agree to use this dataset for non-commercial use ONLY" before download --
    a stated licence and a stated use restriction that are in tension with each other. Both readings
    are given here rather than picking one.
  languages: ["en", "zh"]
  modalities: ["text"]
  splits: >-
    versioned releases rather than a fixed train/test split: v202412 (per-language AMC/CCEE/CNMO/WLPMC
    files plus a "hard" subset) and v202505 (English-only "all" and "hard" configs)
  public_test_set: null
publisher:
  org: "Shanghai Artificial Intelligence Laboratory"
  authors: ["Junnan Liu", "Hongwei Liu", "Linchen Xiao", "Ziyi Wang", "Kuikun Liu", "Songyang Gao", "Wenwei Zhang", "Songyang Zhang", "Kai Chen"]
  url: "https://open-compass.github.io/GPassK/"
paper:
  title: "Are Your LLMs Capable of Stable Reasoning?"
  arxiv: "2412.13147"
  url: "https://arxiv.org/abs/2412.13147"
  year: 2024
leaderboard_url: "https://open-compass.github.io/GPassK/"
repo_url: "https://github.com/open-compass/GPassK"
released: "2024-12"
last_updated: "2025-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: "2025-01"
  note: >
    The maintainers' own results table (dated to the paper's early-2025 revisions, not to the current
    date) shows DeepSeek-R1 leading LiveMathBench-202412 at mG-Pass@16 77.6 and Greedy 81.1, with
    OpenAI o3-mini close behind (mG-Pass@16 76.8). On the harder LiveMathBench-Hard-202412 subset, the
    same top models drop sharply (DeepSeek-R1 mG-Pass@16 29.6, OpenAI o3-mini 28.6), showing the
    "Hard" subset still separates frontier reasoning models well. No current (2026) score was found in
    sources opened for this page, and the underlying question set has itself moved on to v202505 since
    that table was published, so these figures describe a specific past release, not where models
    stand today.
contamination:
  risk: low
  note: >
    Contamination resistance is close to the paper's entire reason for existing: every problem is
    drawn from recent, dated competitions and exams specifically chosen for low overlap with existing
    public datasets, and the authors commit to "ongoing updates with new questions" to keep the
    active question set ahead of any single model's training cutoff. Risk rises for the oldest
    released version (v202412) as more models are trained after its publication date without a
    corresponding refresh of results.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >-
    livemathbench (many config variants: livemathbench_gen for standard G-Pass@k, livemathbench_greedy_gen
    for greedy-only, livemathbench_hard_* for the Hard subset including LLM-verify and cascade-eval
    variants, and livemathbench_v202505_* for the 2025 release)
  bigbench: ""
  other: >
    The authors' own GPassK repository provides both a standalone Python implementation of the
    G-Pass@k metric class and an integration with Hugging Face's `lighteval` framework, alongside the
    OpenCompass configs. `G-Pass@16_0.5` and similar names encode k=16 samples at threshold tau=0.5;
    scores at different k or tau are not directly comparable to each other.
tags:
  - math
  - competition-math
  - contamination-resistant
  - continuous-refresh
  - bilingual
  - stability-metric
sources:
  - url: "https://arxiv.org/abs/2412.13147"
    title: "Are Your LLMs Capable of Stable Reasoning?"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2412.13147"
    title: "Are Your LLMs Capable of Stable Reasoning? (full text, ar5iv) -- Table 4 dataset statistics, author affiliation"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/GPassK"
    title: "open-compass/GPassK repository (README, G-Pass@k definitions, results tables, release notes)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/opencompass/LiveMathBench"
    title: "opencompass/LiveMathBench dataset metadata (Hugging Face API) -- licence tag, gating, configs list"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/livemathbench/README.md"
    title: "OpenCompass livemathbench config README (per-source, per-language item counts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/livemathbench/livemathbench_v202505_gen_9befbf.py"
    title: "OpenCompass livemathbench v202505 config (English-only, k/n sampling parameters)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LiveMathBench gives a model a recent competition mathematics problem, stripped of any multiple-choice
options so the model must derive the answer itself, drawn from four sources: the China National
Mathematical Olympiad (CNMO), mock exams for China's College Entrance Examination (CCEE), the
American Mathematics Competition (AMC), and the William Lowell Putnam Mathematical Competition
(WLPMC). Its purpose-built companion metric, G-Pass@k, is arguably the benchmark's main point: rather
than asking only whether a model can solve a problem once, it measures whether the model solves it
consistently across many independent samples, which the authors frame as the gap between a model's
raw potential and its practical stability. A harder subset, LiveMathBench-Hard, draws from the same
four sources at greater difficulty and separates frontier models far more sharply than the base set.

## How it is scored

G-Pass@k_tau generalises Pass@k from code generation: given n independent samples per question and c
judged correct, it estimates the probability that at least a tau-fraction of any k-sized subset of
those samples is correct. A low tau rewards mere potential (can the model ever get it right); a tau
near 1 rewards consistency (does it get it right nearly every time). mG-Pass@k integrates this across
tau from 0.5 to 1.0 into one number. Results also report plain "Greedy" accuracy (one deterministic
sample) for comparison. Free-response grading has no chance-level baseline, and no human baseline was
found in the sources opened for this page.

## Dataset and licence

The v202412 release totals 238 problems: 119 per language across two languages, made up of 46 AMC, 44
CCEE, 18 CNMO and 11 WLPMC problems per language, confirmed from the paper's own statistics table.
The Hugging Face dataset card states a CC BY 4.0 licence, but the repository itself is access-gated
behind a request that requires agreeing to use the dataset "for non-commercial use ONLY" -- a licence
grant and a use restriction that sit in tension with each other; this page records both readings
rather than resolving the conflict. The v202505 release (announced June 2025) replaced the bilingual
per-source files with an English-only configuration; this research could not confirm its exact item
count because the gated repository could not be opened without an approved access request.

## Who publishes it

LiveMathBench comes from Junnan Liu, Hongwei Liu, Linchen Xiao, Ziyi Wang, Kuikun Liu, Songyang Gao,
Wenwei Zhang, Songyang Zhang and Kai Chen at the Shanghai Artificial Intelligence Laboratory, posted
to arXiv in December 2024 and published at ACL 2025. The team maintains both the GitHub repository
and the project leaderboard, and continues to publish new dataset versions well past the original
release -- v202505 being the most recent confirmed by this research.

## Lineage

LiveMathBench names no formal predecessor. Several authors -- Kai Chen, Songyang Zhang and Wenwei
Zhang -- also appear on this repository's `mathbench` page, a sibling OpenCompass benchmark that
tests hierarchical, grade-by-grade proficiency rather than contamination resistance; the two are
separate projects with different goals, not versions of each other. No successor or variant of
LiveMathBench itself was found during this research.

## Saturation and contamination

The maintainers' own results table, dated to the paper's early-2025 revisions rather than to today,
shows DeepSeek-R1 leading the base LiveMathBench-202412 set (mG-Pass@16 77.6, Greedy 81.1). On
LiveMathBench-Hard-202412, the same top models drop sharply (DeepSeek-R1 mG-Pass@16 29.6), showing
the Hard subset still separated frontier reasoning models well at that point. No current, 2026-dated
score was found in sources opened for this page, and the question set has itself moved on to v202505
since that table was published, so these figures describe one past release, not where today's models
stand. Contamination risk is low by design: every problem is sourced from recent, dated competitions
chosen for low overlap with existing public data, and the authors commit to ongoing updates to stay
ahead of training cutoffs -- though risk rises for any single fixed version, like v202412, the longer
it goes without a refresh of published results.

## How to run it

OpenCompass is the reference harness, registering the benchmark under its `livemathbench` config
directory with numerous variants: a standard G-Pass@k config, a greedy-only config, several
LiveMathBench-Hard configs, and separate v202505 configs. The authors also publish a standalone
Python implementation of the G-Pass@k metric class and a `lighteval`-based integration. Because
G-Pass@k depends on the sample count (n) and threshold (tau) used, a score like "G-Pass@16_0.5" is
only comparable to another computed with the same k and tau.

## Reading the numbers

Because LiveMathBench is versioned, always check which release (v202412, v202505, or a later one)
a reported score used before comparing it to another -- the question sets, and for v202505 even the
language, differ between versions. Because the headline metric is stability-aware rather than a
simple accuracy, a high G-Pass@16 at a high tau threshold is a stronger claim than a high Greedy
score: it says the model gets the same problem right nearly every time, not just once. Read the base
and Hard results separately, since the Hard subset still separates models where the base set is
closer to solved.
