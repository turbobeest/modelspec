---
id: infinitebench
name: "∞Bench (InfiniteBench)"
aliases: ["InfiniteBench", "∞Bench"]
page_kind: benchmark
category: long-context
subcategory: "synthetic and realistic long-document tasks beyond 100K tokens (retrieval, math, code, book QA, dialogue), English and Chinese"
status: active
summary: "∞Bench tests long-context understanding on 12 synthetic and realistic tasks averaging around 200K tokens, well beyond the roughly 10K tokens most earlier long-context benchmarks used."
measures: >
  ∞Bench (InfiniteBench) tests whether a model can use information spread across contexts far longer than
  most earlier long-context benchmarks tested, which the paper says averaged around 10K tokens. It combines
  12 tasks in four groups: three synthetic retrieval tasks (finding a planted passkey, a number string, or
  a value in key-value pairs, buried in long noise text); two code tasks (spotting an injected bug across a
  repository, and simulating multi-step function execution); two math tasks (finding an extreme or median
  value in a long array, and tracking intermediate results through a long arithmetic expression); three
  novel/book comprehension tasks in English (summarization, aggregation-style question answering, and
  multiple-choice questions) plus one in Chinese; and one dialogue task that asks a model to identify a
  masked character's name from a long script. The synthetic tasks test raw long-range retrieval; the
  book and dialogue tasks test whether a model can reason over dependencies spread across a genuinely long
  document rather than just locate one planted fact.
task_format: >
  The model is given a long document or synthetic long context (input lengths mostly in the 100K-200K token
  range) plus a task-specific question or instruction, and produces a free-form or multiple-choice answer,
  evaluated per task against that task's own metric.
metric:
  name: "task-specific metric (accuracy, ROUGE-L-sum, or exact match, depending on task), averaged across the 12 tasks for a headline score"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random or human baseline applies across all 12 tasks, since they use different metrics and
    answer formats; the paper reports a per-task breakdown rather than one baseline number.
dataset:
  size: 3946
  size_note: >
    3,946 examples across the 12 tasks: Retrieve.PassKey 590, Retrieve.Number 590, Retrieve.KV 500, En.Sum
    103, En.QA 351, En.MC 229, Zh.QA 189, En.Dia 200, Code.Debug 394, Code.Run 400, Math.Calc 50, Math.Find
    350. Average context length is roughly 200K tokens across the suite, with individual tasks such as
    Retrieve.PassKey and Retrieve.Number averaging around 122K tokens and the QA/summarization tasks
    running to roughly 185K-207K tokens.
  url: "https://huggingface.co/datasets/xinrongzhang2022/InfiniteBench"
  license: "MIT, per the OpenBMB/InfiniteBench GitHub repository; the paper itself and the Hugging Face dataset card do not separately state a licence."
  languages: ["en", "zh"]
  modalities: ["text", "code"]
  splits: "12 task-specific files, no shared train/test split; each task is its own fixed evaluation set"
  public_test_set: true
publisher:
  org: "Department of Computer Science and Technology, Tsinghua University"
  authors: ["Xinrong Zhang", "Yingfa Chen", "Shengding Hu", "Zihang Xu", "Junhao Chen", "Moo Khai Hao", "Xu Han", "Zhen Leng Thai", "Shuo Wang", "Zhiyuan Liu", "Maosong Sun"]
  url: "https://github.com/OpenBMB/InfiniteBench"
paper:
  title: "∞Bench: Extending Long Context Evaluation Beyond 100K Tokens"
  arxiv: "2402.13718"
  url: "https://arxiv.org/abs/2402.13718"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/OpenBMB/InfiniteBench"
released: "2024-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 45.63
  as_of: "2024-02"
  note: >
    At release, GPT-4 led with an average of 45.63% across the 12 tasks (100% on Retrieve.PassKey, weaker
    elsewhere), ahead of Claude 2 (37.06%), Kimi-Chat (34.73%) and YaRN-Mistral-7B-128K (19.96%, 0% on
    Retrieve.KV) -- far below ceiling and clearly separating models at the time. The OpenBMB/InfiniteBench
    repository's commit history shows no activity since September 2024, and this research pass found no
    independently updated public leaderboard with more recent scores, so current-day standing is not
    established here; given how far frontier context windows have grown since 2024, today's top scores are
    plausibly much higher than this 2024 reading.
contamination:
  risk: medium
  note: >
    The dataset has been public without gating since February 2024. Its four synthetic tasks (the three
    retrieval tasks plus Math.Find and Math.Calc) are procedurally generated from random values, so the
    general task format is harder to answer from memorised training data than a fixed-answer benchmark,
    but the specific published instances are themselves fixed and could still be memorised verbatim. The
    book- and dialogue-based tasks draw on real novels and scripts that were plausibly already present in
    pretraining corpora independent of this benchmark. No source read for this page states a measured
    contamination rate.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "infinitebench"
  bigbench: ""
  other: >
    The authors' own evaluation scripts live under `src/` in the OpenBMB/InfiniteBench repository, calling
    various model APIs per task. OpenCompass registers all 12 subtasks individually (for example
    `infinitebench_retrievepasskey`, `infinitebench_codedebug`, `infinitebench_zhqa`). Not confirmed in the
    lm-evaluation-harness, HELM or BIG-bench task lists.
tags: ["long-context", "retrieval", "code", "math", "multilingual", "synthetic"]
sources:
  - url: "https://arxiv.org/abs/2402.13718"
    title: "∞Bench: Extending Long Context Evaluation Beyond 100K Tokens"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.13718"
    title: "∞Bench, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/xinrongzhang2022/InfiniteBench"
    title: "xinrongzhang2022/InfiniteBench dataset card API, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/OpenBMB/InfiniteBench"
    title: "OpenBMB/InfiniteBench repository"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/infinitebench"
    title: "OpenCompass infinitebench dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

∞Bench (InfiniteBench) tests whether a model can use information spread across contexts far longer than
most earlier long-context benchmarks tested -- the paper states those earlier suites averaged around 10K
tokens, while this one averages roughly 200K. It combines 12 tasks in four groups. Three synthetic
retrieval tasks bury a passkey, a number string, or a value from key-value pairs inside long noise text and
ask the model to find it. Two code tasks ask the model to spot an injected bug across a repository or
simulate multi-step function execution by hand. Two math tasks ask it to find an extreme or median value in
a long array, or track intermediate results through a long arithmetic expression. Four book/dialogue tasks
-- three in English (summarization, aggregation-style question answering, and multiple-choice questions)
and one in Chinese question answering, plus a separate English dialogue task that asks the model to name a
masked character from a long script -- test whether it can reason over dependencies spread across a
genuinely long document, rather than just locate one planted fact the way the synthetic tasks do.

## How it is scored

Each task uses its own metric: retrieval and math-find tasks and the multiple-choice book task use
accuracy; code debugging uses multiple-choice accuracy; code execution and the number/key-value retrieval
tasks use exact match; summarization uses ROUGE-L-Sum; and the long-arithmetic task scores the number of
correct intermediate values produced before the first error. A model's headline ∞Bench number is typically
the unweighted average of its per-task scores across all 12 tasks, so it blends several different metrics
into one figure rather than measuring one consistent quantity.

## Dataset and licence

3,946 examples span the 12 tasks, ranging from 50 examples (Math.Calc) to 590 (Retrieve.PassKey and
Retrieve.Number). Average context length across the suite is roughly 200K tokens; the retrieval tasks
average around 122K tokens of input, while the QA and summarization tasks run to roughly 185K-207K tokens.
The GitHub repository (OpenBMB/InfiniteBench) is MIT-licensed; neither the paper nor the Hugging Face
dataset card states a separate licence for the data itself. The dataset is publicly downloadable without
gating.

## Who publishes it

∞Bench was introduced by Xinrong Zhang, Yingfa Chen, Shengding Hu, Zihang Xu, Junhao Chen, Moo Khai Hao, Xu
Han, Zhen Leng Thai, Shuo Wang, Zhiyuan Liu and Maosong Sun, in the Department of Computer Science and
Technology at Tsinghua University, first posted to arXiv in February 2024. The authors maintain the
reference data and evaluation code at github.com/OpenBMB/InfiniteBench, whose commit history shows no
activity since September 2024; no actively updated public leaderboard was found during this research pass.

## Lineage

No predecessor, successor or formal variant of ∞Bench is catalogued in this repository. It is one of
several long-context suites built around the same idea of testing far beyond typical context lengths;
RULER is another such benchmark queued for this repository's benchmark census but not yet published here as
of this page's writing, and readers comparing long-context numbers across sources should check which suite
(and which task mix within it) produced a given score before treating two "long-context" numbers as the
same measurement.

## Saturation and contamination

At release, GPT-4 led with an average of 45.63% across the 12 tasks (essentially perfect on
Retrieve.PassKey, weaker elsewhere), ahead of Claude 2 (37.06%), Kimi-Chat (34.73%) and
YaRN-Mistral-7B-128K (19.96%, 0% on Retrieve.KV) -- far below ceiling and clearly separating models at the
time. The reference repository has shown no commit activity since September 2024, and this pass found no
independently updated leaderboard with more recent scores, so current-day standing is not established
here; given how far frontier context windows have grown since 2024, today's top scores are plausibly well
above this reading. Contamination risk is medium: the four procedurally generated synthetic tasks resist
verbatim memorization of the task format even though the specific published instances are fixed and
public, while the book- and dialogue-based tasks draw on real novels and scripts plausibly already present
in pretraining corpora independent of this benchmark; no source quantifies an actual contamination rate.

## How to run it

The authors' own evaluation scripts live under `src/` in the OpenBMB/InfiniteBench repository and call
various model APIs per task. OpenCompass registers all 12 subtasks individually (for example
`infinitebench_retrievepasskey`, `infinitebench_codedebug`, `infinitebench_zhqa`), the most likely route to
current scores under a shared harness. Not confirmed in the lm-evaluation-harness, HELM or BIG-bench lists.

## Reading the numbers

A high ∞Bench average shows a model can hold and use information across genuinely long contexts on a mix
of synthetic-retrieval and realistic tasks, not just pass a single "needle in a haystack" check -- the
suite deliberately includes tasks, like the book and math tasks, that a model cannot solve by retrieval
alone. Because the headline score averages several unrelated metrics (accuracy, ROUGE, exact match, an
error-position count) across tasks of very different difficulty, a similar overall number can come from
very different per-task profiles, so check the per-task breakdown rather than relying on the average alone.
Given this page could not confirm a current leaderboard, treat any recent ∞Bench number with the
understanding that it is being compared against a 2024 reference point rather than an actively tracked
ranking.
