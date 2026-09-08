---
id: acp_bench_hard
name: "ACPBench-Hard"
aliases: ["ACPBench Hard"]
page_kind: benchmark
category: reasoning
subcategory: "generative planning and action reasoning (open-ended variant of ACPBench)"
status: active
summary: "IBM's harder, generative companion to ACPBench: the same planning-reasoning skills plus a new 'next action' task, answered as open text and checked by per-task validators, not multiple choice."
measures: >
  ACPBench-Hard tests the same underlying skill set as ACPBench -- reasoning about action applicability,
  progression, reachability, action reachability, plan validation, action justification and landmarks in
  natural-language-translated PDDL planning problems -- but removes the multiple-choice and yes/no answer
  options that make the base benchmark comparatively easy to pass by elimination. A model must instead
  produce the answer directly as open-ended text: name the applicable action, state the resulting facts,
  output a plan, or identify the unjustified step, rather than pick from a short list. ACPBench-Hard adds
  an eighth task on top of the original seven, Next Action, which asks a model to choose the correct next
  step toward a goal with no candidates supplied at all. The authors motivate this generative format as a
  closer match to how an actual planning system operates, which never gets to choose from a curated
  multiple-choice menu.
task_format: >
  Open-ended, free-text generation over the same natural-language-translated PDDL planning problems
  ACPBench uses: given a context and a question (for example, "which action is applicable in this
  state?" or "what is a valid plan to reach the goal?"), the model must produce the exact action, fact,
  action sequence or judgment in its own words, with no answer choices given. Two prompting conditions
  are used in lm-evaluation-harness: natural-language-only, and natural language with the underlying PDDL
  domain/problem file included in context.
metric:
  name: "accuracy (each generated answer checked by a task-specific program validator, not string matching)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no meaningful random-guess baseline for open-ended generation the way there is for
    ACPBench's boolean (~50%) or four-option multiple-choice (~25%) formats. Instead of string matching,
    each task has its own correctness validator: simple tasks such as Applicability and Progression can
    be checked in constant or linear time against the problem's known state, while harder tasks --
    Reachability, Landmarks and Next Action -- require actually invoking a planner, since checking them
    is PSPACE-complete in the general case. No controlled human baseline is published.
dataset:
  size: 1040
  size_note: >
    1,040 test items: 8 generative tasks (app, prog, reach, areach, val, just, land, and the new nexta)
    x 130 test rows each, confirmed directly from the Hugging Face dataset card's per-config split
    metadata for the `_gen` configs in the shared `ibm-research/acp_bench` repository; each task also
    has 40 validation rows (320 total), for 1,360 generative items overall. Items are synthesized from
    the same 13 PDDL planning domains as the base ACPBench (Blocksworld, Logistics, Grippers, Grid,
    Ferry, FloorTile, Rovers, VisitAll, Depot, Goldminer, Satellite, Swap and Alfworld).
  url: "https://huggingface.co/datasets/ibm-research/acp_bench"
  license: "CDLA-Permissive-2.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "test (130/task) and validation (40/task) for each of 8 generative task configs, in the same repository as base ACPBench"
  public_test_set: true
publisher:
  org: "IBM Research"
  authors: ["Harsha Kokel", "Michael Katz", "Kavitha Srinivas", "Shirin Sohrabi"]
  url: "https://ibm.github.io/ACPBench"
paper:
  title: "ACPBench Hard: Unrestrained Reasoning about Action, Change, and Planning"
  arxiv: "2503.24378"
  url: "https://arxiv.org/abs/2503.24378"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/IBM/ACPBench"
released: "2025-03"
last_updated: "2026-02"
lineage:
  family: acp_bench
  predecessor: acp_bench
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    No single leading score was found in the sources read for this page, and the paper's own framing
    argues against picking one: it reports that "no model outperforms another" consistently across
    ACPBench-Hard's tasks, and that "with a few exceptions all tested language models score below 65%,"
    a group that includes o1-class reasoning models struggling on roughly half the benchmark. That
    combination -- no clear leader, and a hard ceiling most models do not approach -- is the paper's own
    evidence that removing multiple-choice framing from ACPBench meaningfully raises its difficulty,
    consistent with an open rather than saturated or merely-watch benchmark.
contamination:
  risk: low
  note: >
    Like base ACPBench, items are synthesized programmatically from formally specified PDDL domains with
    solver- and validator-checked correct answers, rather than drawn from existing text, so a specific
    graded instance is unlikely to already exist verbatim in training data. The underlying domains
    (Blocksworld, Logistics and similar) are old and well known in the planning literature, so a model
    could still have absorbed general domain strategy, but the generative answer format and program-based
    validators make superficial memorisation of a fixed answer key less useful here than on a
    multiple-choice benchmark.
harness:
  lm_eval: "acp_bench_hard (separate task in the same acpbench directory as acp_bench; gen_2shot and gen_2shot_with_pddl groups)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Task-specific validator code and the reference dataset loader are in github.com/IBM/ACPBench, alongside base ACPBench."
tags: ["planning", "reasoning", "action-reasoning", "pddl", "generative", "open-ended", "iclr-2026"]
sources:
  - url: "https://arxiv.org/abs/2503.24378"
    title: "ACPBench Hard: Unrestrained Reasoning about Action, Change, and Planning (Kokel, Katz, Srinivas, Sohrabi, 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2503.24378"
    title: "ACPBench Hard, full text (ar5iv) -- task definitions, validators, results"
    accessed: "2026-09-08"
  - url: "https://github.com/IBM/ACPBench"
    title: "IBM/ACPBench GitHub repository -- task table (App/Prog/Reach/Val/AReach/Just/Land/NextA), news section confirming ICLR 2026 acceptance"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ibm-research/acp_bench"
    title: "ibm-research/acp_bench dataset card, Hugging Face -- CDLA-Permissive-2.0 licence, per-config _gen split sizes"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ibm-research/acp_bench"
    title: "ibm-research/acp_bench dataset card API -- exact _gen config split sizes"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/acpbench"
    title: "lm-evaluation-harness acpbench task directory (acp_bench and acp_bench_hard task names)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ACPBench-Hard tests the same seven atomic planning-reasoning skills as ACPBench -- action applicability,
progression, atom reachability, action reachability, plan validation, action justification and landmarks
-- over the same style of natural-language-translated PDDL problems, but strips away the multiple-choice
and yes/no answer options that let a model narrow down a correct answer by elimination. A model must
instead generate the action, fact, plan or judgment directly as open-ended text. The authors add an
eighth task, Next Action, that has no analogue in base ACPBench at all: given a planning problem, produce
the single correct next step toward the goal, with no candidates supplied. The motivation is that a real
planning system never gets to choose from a curated shortlist, so a generative test is closer to how
these reasoning skills actually get used.

## How it is scored

Because answers are open-ended text rather than a letter or yes/no, ACPBench-Hard cannot be scored by
string matching against one canonical answer -- a correct plan, applicable action or landmark fact can
often be phrased more than one valid way. The authors instead built a dedicated program-based validator
for each of the eight tasks. The simplest, such as Applicability and Progression, can be checked in
constant or linear time by comparing the generated answer against the problem's known state. The hardest
-- Reachability, Landmarks and Next Action -- require actually invoking a planner during validation, since
determining whether a given claim is correct is PSPACE-complete for these tasks in general. This makes a
reported ACPBench-Hard score dependent on which validator implementation graded it, more so than a plain
multiple-choice or boolean accuracy figure would be.

## Dataset and licence

ACPBench-Hard's generative items are hosted inside the same Hugging Face repository as base ACPBench
(`ibm-research/acp_bench`, CDLA-Permissive-2.0), as eight additional `_gen`-suffixed configs -- one per
task, including the new `nexta` task -- each with 130 test rows and 40 validation rows, confirmed
directly from the dataset card's split metadata. That gives 1,040 test items and 320 validation items
across the eight generative tasks. Items are synthesized from the same 13 PDDL domains as base ACPBench
(Blocksworld, Logistics, Grippers, Grid, Ferry, FloorTile, Rovers, VisitAll, Depot, Goldminer, Satellite,
Swap and Alfworld), using the same solver-driven, hand-templated translation pipeline.

## Who publishes it

ACPBench-Hard comes from the same team as the original benchmark -- Harsha Kokel, Michael Katz, Kavitha
Srinivas and Shirin Sohrabi at IBM Research -- posted to arXiv on 2025-03-31 and revised in February 2026.
It was accepted to ICLR 2026, per both the paper's own arXiv listing and IBM's GitHub news feed for the
ACPBench project, which the same team continues to maintain.

## Lineage

ACPBench-Hard is the direct generative successor to `acp_bench`, sharing its underlying PDDL domains, its
translation methodology and its Hugging Face dataset repository, while replacing multiple-choice and
boolean questions with open-ended generation and adding the Next Action task. It has no further successor
catalogued in this repository.

## Saturation and contamination

ACPBench-Hard is explicitly not saturated by the authors' own framing: they report that "no model
outperforms another" consistently across its tasks, and that with a few exceptions every tested model --
including o1-class reasoning models -- scores below 65%, a sharp contrast with base ACPBench's multiple-
choice results, where the paper's own 2-shot evaluation had o1-preview reaching 87.31% average accuracy.
That gap is itself evidence of how much the multiple-choice format was propping up scores on the original
benchmark. Contamination risk is low: like the base benchmark, items are synthesized programmatically
from PDDL domains with validator-checked correct answers rather than drawn from existing text, though the
domains themselves are old and well known in the planning literature.

## How to run it

lm-evaluation-harness lists `acp_bench_hard` as a separate task in the same `acpbench` directory as
`acp_bench`, with `gen_2shot` and `gen_2shot_with_pddl` task groups -- the latter including the raw PDDL
domain and problem files in context alongside the natural-language description, the former using natural
language alone. Because grading requires a dedicated, per-task validator rather than a shared scoring
function, and the harder tasks require running an actual planner to check a submitted answer, reproducing
a reported score depends on using the same validator implementation the original number came from. No
HELM, Inspect Evals, BIG-bench or OpenCompass implementation was confirmed during this research.

## Reading the numbers

A high ACPBench-Hard score is considerably stronger evidence of real planning-reasoning skill than a high
ACPBench score, precisely because there is no answer list to narrow down by elimination -- the model has
to produce a specific, verifiably correct action, fact or plan fragment from scratch. Given the paper's
own finding that most models, including strong reasoning models, score under 65% with no clear leader,
treat any single high score with scrutiny and check which of the eight tasks and which prompting
condition (with or without raw PDDL in context) it covers, since the base ACPBench multiple-choice numbers
for the same underlying skills run dramatically higher for the same models.
