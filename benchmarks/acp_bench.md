---
id: acp_bench
name: "ACPBench"
aliases: ["ACP Bench", "acp-bench"]
page_kind: benchmark
category: reasoning
subcategory: "planning and action reasoning"
status: active
summary: "IBM's boolean- and multiple-choice test of seven atomic reasoning skills needed for planning -- action applicability, reachability, justification, landmarks and more -- across 13 formal domains."
measures: >
  ACPBench gives a model a natural-language description of a planning problem (translated from a
  formal PDDL domain and problem definition, covering domains such as Blocksworld, Logistics,
  Grippers and Alfworld) and asks a targeted question about one of seven atomic reasoning skills:
  whether an action is applicable in the current state, what a state looks like after an action
  (progression), whether a goal atom is reachable, whether an action sequence validly achieves a
  goal, whether an action could ever become applicable on some future path (action reachability),
  whether an action in a plan is unjustified and can be dropped, or which facts every valid plan must
  pass through (landmarks). It isolates the specific reasoning sub-skills end-to-end plan generation
  depends on, rather than asking a model to produce a full plan itself.
task_format: "Boolean (yes/no) or four-option multiple-choice questions over a natural-language-translated planning problem; the base ACPBench tasks require no free-text generation (a separate, harder generative version, ACPBench-Hard, exists -- see Lineage)."
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Random-guess baseline is approximately 50% for the boolean questions and 25% for the four-option
    multiple-choice questions; the paper reports per-task accuracy rather than a single blended
    figure, so no single random baseline applies to an aggregate score. No controlled human baseline
    is published.
dataset:
  size: null
  size_note: >
    Per-task-per-format counts on the Hugging Face dataset (ibm-research/acp_bench) run 120-130 test
    rows and 40 validation rows for each of the seven original ACPBench tasks in each of its boolean
    and multiple-choice formats (14 configs), plus generative-format configs added by the follow-on
    ACPBench-Hard collection that shares the same repository; the paper's Table 1 gives per-domain
    problem statistics across 13 domains instead of a single item total, so no single confirmed total
    question count is reported here. The top 8 of the 13 domains (by the paper's own grouping) are
    also used for a fine-tuning experiment; the remaining 5 are held out for evaluation only.
  url: "https://huggingface.co/datasets/ibm-research/acp_bench"
  license: "CDLA-Permissive-2.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "test and validation rows per task-format config; see size_note"
  public_test_set: true
publisher:
  org: "IBM Research"
  authors: ["Harsha Kokel", "Michael Katz", "Kavitha Srinivas", "Shirin Sohrabi"]
  url: "https://ibm.github.io/ACPBench"
paper:
  title: "ACPBench: Reasoning about Action, Change, and Planning"
  arxiv: "2410.05669"
  url: "https://arxiv.org/abs/2410.05669"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/IBM/ACPBench"
released: "2024-10"
last_updated: "2026-02"
lineage:
  family: ""
  predecessor: ""
  successors: ["acp_bench_hard"]
  variants: []
saturation:
  status: open
  top_score: 87.31
  as_of: "2024-10"
  note: >
    The paper's own evaluation (2-shot chain-of-thought) has OpenAI o1-preview at 87.31% average
    accuracy on the multiple-choice tasks, with its weakest single task down at 63.08%; GPT-4o trails
    at 78.40% average, with its weakest task (validation) at 52.50%. ACPBench-Hard's generative-format
    follow-up (arXiv 2503.24378) reports that on its harder, open-ended tasks "no model outperforms
    another" consistently and "with a few exceptions all tested language models score below 65%" --
    including o1-class reasoning models. No 2025-2026 frontier-model score was found during this
    research.
contamination:
  risk: low
  note: >
    Problems are synthesized programmatically from formally specified PDDL planning domains with
    provably correct solutions, rather than drawn from an existing text corpus, so a specific graded
    instance is unlikely to pre-exist in training data verbatim; the authors note this construction
    method lets them scale to more problems without added human effort. The domains themselves
    (Blocksworld, Logistics and other classic PDDL benchmarks) are old and well known in the planning
    literature, so a model could still have absorbed general strategies for solving them.
harness:
  lm_eval: "acp_bench (harness directory named acpbench; boolq_cot_2shot, mcq_cot_2shot, gen_2shot and gen_2shot_with_pddl task groups)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "acp_bench_hard is a separate lm-evaluation-harness task, in the same acpbench directory, covering ACPBench-Hard's generative questions."
tags: ["planning", "reasoning", "action-reasoning", "pddl", "multiple-choice", "boolean"]
sources:
  - url: "https://arxiv.org/abs/2410.05669"
    title: "ACPBench: Reasoning about Action, Change, and Planning (Kokel et al., 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2410.05669"
    title: "ACPBench paper, full text (ar5iv HTML) -- task definitions, domain table, accuracy results"
    accessed: "2026-09-08"
  - url: "https://github.com/IBM/ACPBench"
    title: "IBM/ACPBench GitHub repository (task table, ACPBench-Hard news, worked examples)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ibm-research/acp_bench"
    title: "ibm-research/acp_bench dataset card, Hugging Face (CDLA-Permissive-2.0, 13 domains, per-config split sizes)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2503.24378"
    title: "ACPBench Hard: Unrestrained Reasoning about Action, Change, and Planning (Kokel et al., 2025) -- successor benchmark"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/acpbench"
    title: "lm-evaluation-harness acpbench task directory (acp_bench and acp_bench_hard task names)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ACPBench gives a model a natural-language description of a planning problem -- translated from a
formal PDDL domain and problem definition, spanning domains such as Blocksworld, Logistics,
Grippers, Ferry, Rovers, Satellite and Alfworld -- and asks a targeted question exercising one of
seven atomic reasoning skills that end-to-end planning depends on: whether an action is applicable in
the current state, what the state looks like after an action (progression), whether a goal fact is
reachable at all, whether an action sequence validly achieves the goal, whether an action could ever
become applicable along some future path (action reachability), whether an action inside a plan is
unnecessary and can be dropped without breaking it (justification), and which facts every valid plan
must pass through (landmarks). Rather than asking a model to generate a full plan -- hard to evaluate
and hard to attribute failure within -- it isolates these component skills so a wrong answer points
at a specific reasoning gap.

## How it is scored

Every question is either boolean (yes/no) or four-option multiple-choice, scored as plain accuracy;
there is no free-text generation or partial credit in the base tasks. Chance level is roughly 50% for
boolean questions and 25% for multiple-choice, though the paper reports per-task accuracy rather than
one blended figure, since difficulty varies sharply -- GPT-4o's reported accuracy ranges from 52.50%
on the hardest task (validation) up past 90% on the easiest. ACPBench-Hard, a separate, harder
collection, replaces the fixed answer options with open-ended generative questions and provides its
own per-task validation algorithms rather than string matching, since a generated plan fragment can
be correct in more than one surface form.

## Dataset and licence

The Hugging Face dataset (`ibm-research/acp_bench`, CDLA-Permissive-2.0) packages each of the seven
ACPBench tasks in both boolean and multiple-choice format, each with roughly 120-130 test rows and 40
validation rows, across 13 planning domains: Blocksworld, Logistics, Grippers, Grid, Ferry, FloorTile,
Rovers, VisitAll, Depot, Goldminer, Satellite, Swap and Alfworld. The paper's Table 1 reports domain
complexity (predicate and lifted-action counts) rather than a single overall item total. The top 8 of
these domains are also used in a fine-tuning experiment testing whether smaller models can be taught
these skills directly, while the remaining 5 are held out for evaluation only, to check
generalisation to unseen domains. Problem instances are synthesized from the underlying PDDL domain
files by a solver-driven pipeline with provably correct answers, and translated into natural language
using templates the authors report crafting by hand after finding LLM-generated templates unreliable.

## Who publishes it

ACPBench was introduced by Harsha Kokel, Michael Katz, Kavitha Srinivas and Shirin Sohrabi at IBM
Research, posted to arXiv in October 2024 and presented at AAAI 2025. IBM continues to maintain the
benchmark actively: a generative follow-up, ACPBench-Hard, was accepted at ICLR 2026, and the
original paper's own arXiv listing was revised as recently as February 2026. The team also presented
the work in a NeurIPS 2025 tutorial on planning with language models.

## Lineage

ACPBench has no predecessor benchmark of its own, though the authors position it against a related
prior benchmark, ActionReasoningBench, noting deliberate overlap (both cover an actions'-effects
task) alongside deliberate non-overlap (ACPBench adds reachability, action reachability, validation,
justification and landmarks). Its direct successor, ACPBench-Hard (`acp_bench_hard`, not yet a
separate page here), extends the same seven tasks into open-ended generative questions and adds an
eighth, "next action," while sharing the same Hugging Face dataset repository -- which is why that
repository's own description currently lists eight tasks rather than the original paper's seven.

## Saturation and contamination

ACPBench is not saturated. In the paper's 2-shot chain-of-thought evaluation, OpenAI's o1-preview
reached the highest reported average, 87.31% across the multiple-choice tasks, still dropping to
63.08% on its hardest task; GPT-4o averaged 78.40%, falling to 52.50% on the hardest (validation)
task. The harder, generative ACPBench-Hard follow-up reports a starker picture: "no model outperforms
another" consistently, and with few exceptions every tested model -- including o1-class reasoning
models -- scores below 65%. No 2025-2026 frontier-model score was found for either version.
Contamination risk is low: problems are synthesized programmatically from formal PDDL domains with
solver-verified answers rather than sourced from existing text, though the domains themselves
(Blocksworld, Logistics and similar) are decades-old and widely known in the planning literature.

## How to run it

lm-evaluation-harness ships the benchmark under the task name `acp_bench` (in a directory named
`acpbench`), with `boolq_cot_2shot` and `mcq_cot_2shot` task groups matching the original paper's
boolean and multiple-choice formats, plus `gen_2shot` and `gen_2shot_with_pddl` groups for
ACPBench-Hard's generative tasks (listed as a separate `acp_bench_hard` task pulling from the same
dataset repository). No HELM, Inspect Evals, BIG-bench or OpenCompass task was confirmed during this
research. Because the generative tasks require dedicated per-task validators rather than string
matching -- the authors built a distinct correctness checker for each generative task type -- a
generative-format score depends on which validator implementation graded it, more so than the
boolean or multiple-choice base tasks do.

## Reading the numbers

A high ACPBench score is evidence a model can reliably reason about the mechanics of a planning
problem -- what is currently possible, what would happen next, what is reachable, what is redundant --
in its simplest boolean or multiple-choice form; it does not show the model can generate a full
multi-step plan, which is a substantially harder, open-ended task that ACPBench-Hard targets instead.
Because per-task accuracy varies widely (the paper's own numbers span roughly 50 to 98 percentage
points across tasks for the same model), an aggregate ACPBench score can hide a specific weak skill --
validation and action-reachability were the hardest tasks for every model in the original paper -- so
check the task-level breakdown before concluding a model can plan reliably.
