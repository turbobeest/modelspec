---
id: general365
name: "General365"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "general logical reasoning independent of specialist domain knowledge, K-12 scope"
status: active
summary: "365 seed logic-and-reasoning problems expanded to 1,095 variants across eight categories, designed to test reasoning that needs only K-12 knowledge; even the top model reached 62.8% at release."
measures: >
  General365 tests general reasoning ability -- constraint satisfaction, branching and enumeration,
  spatial and temporal reasoning, recursive and backtracking logic, resistance to semantic
  interference, implicit-information inference, optimal-strategy selection, and probability under
  uncertainty -- while deliberately keeping the knowledge each problem requires at or below K-12
  level. The authors built it to isolate reasoning skill from specialist domain knowledge, arguing
  that benchmarks like competition mathematics or graduate-level science exams conflate the two:
  a model can fail a hard problem because it lacks the reasoning strategy, or because it lacks the
  domain fact, and most benchmarks cannot tell which. General365 tries to remove the second failure
  mode by using only material an educated non-specialist already knows.
task_format: >
  Free-form question answering with mixed answer types (a number, a short text answer, or a choice
  from given options), English, testing 365 hand-written seed problems expanded via controlled
  variation into 1,095 total problem instances.
metric:
  name: "accuracy, graded by a hybrid rule-based and LLM-judge scorer"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Numerical answers are checked with LaTeX-aware rule-based parsing (math-verify); text and
    single-choice answers are graded by an LLM judge (GPT-4.1 in the original paper). The authors
    report 99.6% agreement between this hybrid grader and manual verification across 1,460 checked
    instances. No random-guess or human baseline is given, since answer formats are mixed and the
    benchmark is framed around model comparison rather than a fixed baseline; the paper's own
    top score at release was 62.8% (Gemini-3-Pro), with most evaluated models below 60%.
dataset:
  size: 1095
  size_note: >
    365 hand-crafted seed problems expanded to 1,095 total problem variants (created by altering
    surface semantics or specific constraints while preserving the core reasoning skill each seed
    targets), across 8 categories. Only part of this is public: the released `General365_Public`
    dataset holds 180 seed problems and 720 associated variant instances (confirmed via the
    Hugging Face datasets-server-style size read on the dataset itself), with the remaining seeds
    and variants held back by the authors specifically to protect the benchmark from being trained
    on once its answers circulate.
  url: "https://huggingface.co/datasets/meituan-longcat/General365_Public"
  license: "MIT (Hugging Face dataset card and GitHub repository both state this)"
  languages:
    - en
  modalities:
    - text
  splits: "single public test split, 720 rows; a further, unpublished private split is used for the authors' own leaderboard"
  public_test_set: false
publisher:
  org: "Meituan (LongCat team), with a co-author at the University of Chinese Academy of Sciences"
  authors:
    - "Junlin Liu"
    - "Shengnan An"
    - "Shuang Zhou"
    - "Dan Ma"
    - "Shixiong Luo"
    - "Ying Xie"
    - "Yuan Zhang"
    - "Wenling Yuan"
    - "Yifan Zhou"
    - "Xiaoyu Li"
    - "Ziwen Wang"
    - "Xuezhi Cao"
    - "Xunliang Cai"
  url: "https://github.com/meituan-longcat/General365"
paper:
  title: "General365: Benchmarking General Reasoning in Large Language Models Across Diverse and Challenging Tasks"
  arxiv: "2604.11778"
  url: "https://arxiv.org/abs/2604.11778"
  year: 2026
leaderboard_url: "https://general365.github.io/"
repo_url: "https://github.com/meituan-longcat/General365"
released: "2026-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 62.8
  as_of: "2026-04"
  note: >
    At release, the top model (Gemini-3-Pro) scored 62.8%, followed by Gemini-3-Flash at 60.8% and
    GPT-5-Thinking at 58.6%, with most of the 26 evaluated models below 60%; the authors' own framing
    is that "state-of-the-art models barely achieve a passing level of performance." That leaves
    substantial headroom below the ceiling, so scores still separate models meaningfully rather than
    clustering near the top. This is a single snapshot from the paper's own results table, not an
    independently tracked leaderboard read over time.
contamination:
  risk: low
  note: >
    The benchmark is brand new (April 2026) and its authors specifically screened seed problems to
    be "non-replicable via standard web searches," and held back roughly a third of seeds and more
    than a third of variant instances from public release specifically to preserve a clean,
    uncontaminated evaluation set for their own leaderboard. The publicly released portion (720 of
    1,095 instances) is, by definition, at higher and rising risk the longer it stays public.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "General365"
  bigbench: ""
  other: ""
tags:
  - reasoning
  - logic
  - general-reasoning
  - llm-judge
  - contamination-resistant
sources:
  - url: "https://arxiv.org/abs/2604.11778"
    title: "General365: Benchmarking General Reasoning in Large Language Models Across Diverse and Challenging Tasks"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/abs/2604.11778"
    title: "General365 paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/meituan-longcat/General365"
    title: "meituan-longcat/General365 GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/meituan-longcat/General365_Public"
    title: "meituan-longcat/General365_Public dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/meituan-longcat/General365_Public"
    title: "General365_Public dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/General365"
    title: "OpenCompass General365 dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
---

## What it measures

General365 tests general reasoning ability across eight categories -- complex constraints, branching and enumeration, spatial and temporal reasoning, recursive and backtracking logic, resistance to semantic interference, implicit-information inference, optimal-strategy selection, and probability under uncertainty -- while deliberately keeping the knowledge each problem requires at or below K-12 level. The authors built it to separate reasoning skill from specialist domain knowledge, arguing that competition-math or graduate-science benchmarks conflate the two: a model can fail a hard problem either because it lacks the reasoning strategy or because it lacks the domain fact, and most benchmarks cannot tell which failure occurred. General365 tries to isolate the first failure mode by restricting every problem to knowledge an educated non-specialist already has, so a low score should point at reasoning weakness rather than missing expertise.

## How it is scored

Grading is hybrid: numerical answers are checked with LaTeX-aware rule-based parsing (the `math-verify` tool family), while free-text and single-choice answers are graded by an LLM judge, GPT-4.1 in the original paper's reported results. The authors validated this combined approach against manual review of 1,460 graded instances and report 99.6% agreement, which they use to justify the automated judge for full-scale runs. There is no fixed random-guess baseline, since answer formats mix numbers, short text and multiple-choice, and the benchmark is framed around comparing models against each other rather than against a baseline; at release, the best of 26 evaluated models reached 62.8%.

## Dataset and licence

The full benchmark comprises 365 hand-crafted seed problems, expanded to 1,095 total variants by altering surface wording or specific constraints while preserving the reasoning skill each seed targets. Only part of this is public: the released `General365_Public` Hugging Face dataset holds 180 seed problems and 720 variant instances, with the rest held back by the authors specifically to keep a clean evaluation set for their own leaderboard once the public portion's answers inevitably circulate. Both the GitHub repository and the Hugging Face dataset card give the licence as MIT. Every instance underwent manual review for quality during construction, per the authors' own description of their process.

## Who publishes it

General365 comes from Junlin Liu, Shengnan An, Shuang Zhou, Dan Ma, Shixiong Luo, Ying Xie, Yuan Zhang, Wenling Yuan, Yifan Zhou, Xiaoyu Li, Ziwen Wang, Xuezhi Cao and Xunliang Cai, with correspondence addresses at Meituan and an affiliation also listed for the University of Chinese Academy of Sciences. It was submitted to arXiv in April 2026. The reference repository sits under the `meituan-longcat` GitHub organisation -- the same team behind Meituan's LongCat model line -- alongside a Hugging Face dataset and a project page with an interactive leaderboard.

## Lineage

This repository does not track a predecessor or successor for General365; it is a newly introduced benchmark as of this research. "General365" is a generic-sounding name with no obvious connection to an unrelated product by that name found during this research: the OpenCompass dataset configuration, the Hugging Face dataset, the GitHub repository and the arXiv paper all cross-reference the same Meituan LongCat project and the same underlying dataset (`meituan-longcat/General365_Public`), so this page documents that one benchmark with reasonable confidence there is no name collision within the evaluation ecosystem.

## Saturation and contamination

At release, General365 is far from saturated: the top model, Gemini-3-Pro, reached only 62.8%, with Gemini-3-Flash at 60.8% and GPT-5-Thinking at 58.6%, and most of the 26 models the authors tested scored below 60%. That is a wide spread relative to the ceiling, and the authors themselves frame the result as showing frontier models "barely achieve a passing level of performance," so scores still separate models meaningfully rather than clustering near a ceiling. Contamination risk is low for now: the benchmark is only months old at the time of this research, seed problems were screened to be hard to find via ordinary web search, and roughly a third of seeds plus more than a third of variant instances were withheld from public release specifically to protect the evaluation from being trained on -- though the publicly released 720-instance portion will carry rising contamination risk the longer it remains public and gets cited in papers.

## How to run it

OpenCompass implements General365 via a single configuration (`general365_rawprompt_cascade_llmjudge_gen`) that loads the official public split directly from the `meituan-longcat/General365_Public` Hugging Face dataset, applies MATHVerifyEvaluator to numerical answers with failures escalated to an LLM judge, and grades text and multiple-choice answers directly through the judge, using the official project's judge prompt; it can be configured to use GPT-4.1 as the judge model to reproduce the published numbers. No lm-evaluation-harness, HELM or inspect_evals implementation was found during this research. Because grading depends on which model serves as the LLM judge, scores from a run using a different judge than GPT-4.1 are not strictly comparable to the paper's own numbers.

## Reading the numbers

A General365 score reflects general logical and spatial reasoning under deliberately restricted domain-knowledge demands, so a low score alongside strong performance on knowledge-heavy benchmarks suggests a model that leans on memorised facts or pattern-matched solutions rather than working through novel reasoning chains. Because the benchmark is new and far from saturated -- the best model managed only 62.8% at release -- differences of several points between models are more likely to be meaningful than they would be on a near-ceiling benchmark. Since grading partly depends on an LLM judge, treat scores as somewhat sensitive to which judge model was used, and check whether a reported number came from the small public split or from the authors' own held-out evaluation, since only the latter matches the paper's published leaderboard.
