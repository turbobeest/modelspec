---
id: web_of_lies
name: "Web of Lies"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "multi-step boolean logic (nested truth-teller/liar word problems)"
status: active
summary: >-
  A BIG-bench task that phrases a chain of nested boolean functions as a word problem about people
  who tell the truth or lie, and asks the model to answer yes or no.
measures: >
  Web of Lies gives a model a short narrative in which several people each state whether another
  person tells the truth or lies, forming a chain equivalent to a composition of negation and
  identity functions, f_n(f_{n-1}(...f_1(x)...)). The model must determine whether the final person
  in the chain is telling the truth, answering yes or no. It measures multi-step boolean reasoning
  and the ability to track state (truth-value) through a chain of statements, framed as a
  naturalistic word problem rather than an explicit logic formula.
task_format: >
  Zero-shot binary (yes/no) multiple-choice classification, scored with BIG-bench's
  multiple_choice_grade metric. Examples are generated procedurally at runtime by randomly
  assigning names and truth/lie statements to build a chain of a given length, rather than drawn
  from a fixed, pre-written item bank.
metric:
  name: "Multiple choice grade (accuracy on the yes/no final-truth-value question)"
  direction: higher_is_better
  unit: "accuracy"
  max_score: 1.0
  random_baseline: 0.5
  human_baseline: null
  baseline_note: >
    The task is a balanced binary yes/no choice, so chance performance is 0.5. No human baseline
    figure was found in the source read for this page.
dataset:
  size: 1600
  size_note: >
    1,600 multiple-choice queries, per the task's own README and results for the reference
    ("dummy") model. Examples are generated procedurally by the task's own code, which builds
    random chains of truth-teller/liar statements of varying length rather than sampling from a
    static, hand-written question bank.
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/web_of_lies"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "Single BIG-bench task file of 1,600 procedurally generated examples; no separate train/validation/test split is defined by the task itself"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration); task author Roman Novak"
  authors:
    - "Roman Novak"
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/web_of_lies"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/web_of_lies"
released: "2021"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    No maintained standalone leaderboard for this task was found for this page. It is included as
    one of the 23 tasks in BIG-bench Hard (BBH), a subset selected because the original BIG-bench
    paper found no prior language model beat average human rater performance on it, implying it
    was not saturated at BIG-bench's original 2022 evaluation. The task's own README also notes it
    can in principle be solved by a shortcut, checking the parity of how many times the word "lies"
    appears in the prompt, without doing the underlying reasoning, so a high score does not by
    itself confirm the intended reasoning is happening. Whether current frontier models have
    saturated it, and whether they rely on that shortcut, is not established from a source read for
    this page.
contamination:
  risk: low
  note: >
    Because examples are generated procedurally at runtime rather than drawn from a fixed,
    pre-written item bank, the exact chains of names and statements a model sees are unlikely to
    match items memorised from a fixed public file, lowering contamination risk relative to
    BIG-bench tasks built from static item sets. The general task format and its README (including
    the documented "lies" parity shortcut) have been public since 2021, so a model could still learn
    to exploit that shortcut from public discussion of the task rather than from seeing exact items.
harness:
  lm_eval: "bbh_zeroshot_web_of_lies"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "web_of_lies"
  other: >
    Also ships as one of the 23 tasks in BIG-bench Hard (BBH). lm-evaluation-harness carries
    several BBH variants (zero-shot, few-shot, and chain-of-thought) under its `bbh` task group;
    the confirmed zero-shot task name is `bbh_zeroshot_web_of_lies`, which extracts a yes/no answer
    via regex matching phrases like "tells the truth" or "does not tell the truth."
tags:
  - logical-reasoning
  - multi-step-reasoning
  - big-bench
  - bbh
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/web_of_lies"
    title: "BIG-bench web_of_lies task directory (README: task description, boolean function composition framing, 1,600 examples, multiple_choice_grade metric, author, keywords, documented parity shortcut)"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench/blob/main/bigbench/benchmark_tasks/web_of_lies/task.py"
    title: "BIG-bench web_of_lies task.py: procedural generation of random truth-teller/liar chains, binary yes/no scoring via p_yes vs p_no comparison"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bbh/zeroshot/web_of_lies.yaml"
    title: "lm-evaluation-harness BBH zero-shot web_of_lies.yaml (task name bbh_zeroshot_web_of_lies, prompt template, yes/no regex answer extraction)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-008"
---

## What it measures

Web of Lies presents a short word problem in which a chain of people each assert whether another
person tells the truth or lies, mathematically equivalent to composing a chain of negation and
identity functions, and asks whether the last person in the chain is telling the truth. Answering
requires tracking a boolean state correctly through several nested statements, testing multi-step
logical reasoning framed as a naturalistic narrative rather than an explicit formula.

## How it is scored

The task is a balanced binary yes/no multiple-choice classification, scored with BIG-bench's
multiple_choice_grade metric (accuracy); chance performance is 0.5. Examples are generated
procedurally by the task's own code rather than drawn from a static file, producing chains of
varying length. No human baseline figure was found in the source read for this page.

## Dataset and licence

The task holds 1,600 multiple-choice examples, generated procedurally at runtime by randomly
assigning names and truth-or-lie statements to build chains of nested boolean functions. Because
generation is procedural rather than from a fixed, hand-curated item file, there is no separate
static dataset file with its own licence beyond the BIG-bench repository's own terms; no explicit
licence is stated for the task's generation code in the directory itself.

## Who publishes it

The task was contributed to BIG-bench by Roman Novak (Google) as part of the broader, multi-author
BIG-bench collaboration. No separate standalone paper describing this task in isolation was found;
it is documented in the task's own README and code, and separately appears in the BIG-bench Hard
paper as one of the tasks selected for that harder subset.

## Lineage

Web of Lies is one of several hundred independent BIG-bench tasks. It was later selected as one of
the 23 tasks making up BIG-bench Hard (BBH), a subset chosen because prior language models had not
exceeded average human rater performance on it in the original BIG-bench evaluation; BBH does not
have its own page in this repository yet. The task has no predecessor or successor tracked here.

## Saturation and contamination

No maintained standalone leaderboard for this task was found. Its inclusion in BIG-bench Hard
signals that, as of BIG-bench's original evaluation, no model tested had beaten average human
performance on it, but whether current frontier models have since closed that gap is not
established from a source read for this page, so saturation status is marked "watch." The task's
own README documents a known shortcut, that the task can be solved by checking the parity of how
many times the word "lies" appears in the prompt without doing the underlying reasoning, which
means a high score does not by itself confirm a model is performing genuine multi-step tracking.
Contamination risk is low relative to fixed-item BIG-bench tasks because examples are generated
procedurally at runtime rather than sampled from a static public file, though the task format and
its documented shortcut have been publicly discussed since 2021.

## How to run it

Run as the `web_of_lies` task in the BIG-bench repository
(`bigbench/benchmark_tasks/web_of_lies`), or via BIG-bench Hard. lm-evaluation-harness implements
several BBH variants of it under its `bbh` task group (zero-shot, few-shot and chain-of-thought
forms); the confirmed zero-shot task name is `bbh_zeroshot_web_of_lies`, which prompts with a plain
"Q: ... A:" template and extracts a yes/no answer via regex matching phrases like "tells the truth"
or "does not tell the truth." Scores from the two source repositories, and across BBH's own
variant task names, are not directly comparable without checking shot count and whether
chain-of-thought was used.

## Reading the numbers

A high score suggests a model can track a boolean state correctly through a chain of nested
truth-teller/liar statements, a simple form of multi-step logical reasoning. Because the task can
in principle be solved by a documented shortcut (counting occurrences of "lies" and checking
parity) rather than by explicitly tracking the chain, a high score alone does not confirm the model
is doing the intended step-by-step reasoning; comparisons that also check performance on longer
chains, where the shortcut still applies but explicit tracking gets harder, are more informative
than the raw accuracy number.
