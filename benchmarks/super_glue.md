---
id: super_glue
name: "SuperGLUE (Super General Language Understanding Evaluation benchmark)"
aliases:
  - "Super General Language Understanding Evaluation benchmark"
  - "SGLUE"
page_kind: family
category: composite
subcategory: "multi-task English sentence and sentence-pair understanding suite, successor to GLUE"
status: superseded
summary: "An eight-task English language-understanding suite that replaced GLUE once models exceeded its human baseline, itself since superseded by harder generative and agentic benchmarks."
measures: >
  SuperGLUE bundles eight separately scored English understanding tasks behind one composite score,
  chosen specifically to be harder than GLUE's tasks and to cover a wider range of task formats:
  question answering with yes/no answers over a passage (BoolQ), three-way textual entailment from
  naturally occurring discourse (CB, CommitmentBank), causal reasoning between two alternatives (COPA),
  multi-sentence reading comprehension with a variable number of correct answers (MultiRC), span-based
  reading comprehension requiring cloze-style entity prediction (ReCoRD), two-way textual entailment
  (RTE), word-sense disambiguation in context (WiC), and coreference resolution via the Winograd
  schema (WSC). Two further diagnostic sets, AX-b (broad-coverage entailment) and AX-g (Winogender
  gender-bias probe), are reported alongside the suite but excluded from its main score. All tasks are
  English text classification or span extraction, not open-ended generation.
task_format: >
  Eight separately scored tasks, each single-sentence, sentence-pair, or short-passage classification or
  span extraction; each keeps its own metric (see How it is scored) and the eight per-task scores are
  averaged, unweighted, into one SuperGLUE Score out of 100. Two diagnostic sets (AX-b, AX-g) are
  reported separately and not folded into the score.
metric:
  name: "SuperGLUE Score: unweighted average of eight per-task scores (accuracy for five tasks; accuracy and F1 averaged for CB; F1a and exact match averaged for MultiRC; F1 and exact match averaged for ReCoRD)"
  direction: higher_is_better
  unit: points
  max_score: 100
  random_baseline: null
  human_baseline: 89.8
  baseline_note: >
    No single random baseline applies across all eight tasks, since they range from binary
    classification (about 50% chance) to entity-span prediction with no simple chance rate; see each
    task's own page for its specific baseline. The paper reports overall human performance at 89.8, well
    above its own strongest baseline at the time (BERT++, 71.5), which the authors present as the
    headroom justifying the benchmark's difficulty relative to GLUE.
dataset:
  size: 25730
  size_note: >
    Summing the paper's own per-task table: BoolQ 9,427/3,270/3,245 (train/dev/test), CB 250/57/250,
    COPA 400/100/500, MultiRC 5,100/953/1,800, ReCoRD ~101k/10k/10k, RTE 2,500/278/300, WiC 6,000/638/1,400,
    WSC 554/104/146. Dev-split sizes alone (the split most non-leaderboard papers actually score) sum to
    roughly 25,730 across the eight tasks, dominated by ReCoRD's approximately 10,000-example dev set.
    Test-set labels for all eight tasks are withheld and scored only via the official SuperGLUE
    evaluation server; this page's own `superglue_cb` subset page independently found the released CB
    files hold 56 dev examples rather than the paper's stated 57, so per-task counts can differ slightly
    between the paper's table and the distributed data files.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: >
    The Hugging Face dataset card lists licence "other": SuperGLUE reuses or extends multiple
    pre-existing datasets (CommitmentBank, COPA, MultiRC, ReCoRD, RTE, WiC, the Winograd Schema
    Challenge, Winogender) and each retains its own original terms rather than one unified SuperGLUE
    licence.
  languages:
    - en
  modalities:
    - text
  splits: "8 tasks x (train, dev, test); test labels withheld for all 8 and scored only via the official leaderboard server; plus AX-b and AX-g, both test-only diagnostic sets scored separately"
  public_test_set: false
publisher:
  org: "New York University"
  authors:
    - "Alex Wang"
    - "Yada Pruksachatkun"
    - "Nikita Nangia"
    - "Amanpreet Singh"
    - "Julian Michael"
    - "Felix Hill"
    - "Omer Levy"
    - "Samuel R. Bowman"
  url: "https://super.gluebenchmark.com/"
paper:
  title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems"
  arxiv: "1905.00537"
  url: "https://arxiv.org/abs/1905.00537"
  year: 2019
leaderboard_url: "https://super.gluebenchmark.com/leaderboard"
repo_url: "https://github.com/nyu-mll/jiant"
released: "2019-05"
last_updated: ""
lineage:
  family: ""
  predecessor: "glue"
  successors: []
  variants:
    - superglue_cb
    - superglue_copa
    - superglue_multirc
    - superglue_record
    - superglue_rte
    - superglue_wic
    - superglue_wsc
    - superglue_ax_b
    - superglue_ax_g
    - boolq
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    SuperGLUE's own per-task human estimates are already at or above 90% for several tasks (for example
    98.9% accuracy on CB), leaving little headroom, and multiple per-task subset pages in this
    repository (e.g. `superglue_cb`) independently describe their own task as saturated for current
    models. No current, aggregated eight-task leaderboard score was recovered from the SuperGLUE site,
    which is client-rendered, so no present-day composite top score is recorded here; in practice the
    field's move to harder suites (MMLU, agentic and long-context benchmarks) is the strongest evidence
    that the composite is no longer used to differentiate frontier models.
contamination:
  risk: high
  note: >
    Dev-split labels for all eight tasks, and the training data for all of them, have been public since
    2019 and are widely mirrored on GitHub and Hugging Face; several of the underlying source datasets
    (the Winograd Schema Challenge, RTE) were already public for years before SuperGLUE adopted them.
    Because most harness implementations score the labelled dev split rather than submitting to the
    hidden-label test server, memorisation of the dev files is a realistic contamination path across
    the whole suite.
harness:
  lm_eval: >
    No single `super_glue` task; the tag `super-glue-lm-eval-v1` groups the individually runnable tasks
    boolq, cb, copa, multirc, record, rte, wic, wsc, and a second tag `super-glue-t5-prompt` provides a
    T5-style prompt variant of each.
  inspect_evals: ""
  helm: ""
  opencompass: "No single combined SuperGLUE dataset; each task is configured separately, e.g. SuperGLUE_CB, SuperGLUE_COPA, SuperGLUE_WSC."
  bigbench: ""
  other: ""
tags:
  - composite
  - classification
  - nlu
  - superseded
  - glue
  - historical
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems (Wang et al., arXiv:1905.00537)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/aps/super_glue"
    title: "aps/super_glue dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/super_glue"
    title: "lm-evaluation-harness super_glue tasks directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/super_glue/README.md"
    title: "lm-evaluation-harness SuperGLUE README (raw)"
    accessed: "2026-09-08"
  - url: "https://super.gluebenchmark.com/"
    title: "SuperGLUE homepage (JavaScript app; leaderboard scores not recovered as static text)"
    accessed: "2026-09-08"
  - url: "https://github.com/nyu-mll/jiant"
    title: "nyu-mll/jiant, the toolkit used for SuperGLUE's own baselines"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-006"
---

## What it measures

SuperGLUE bundles eight separately scored English tasks behind a single composite score, deliberately chosen to be harder and more format-diverse than GLUE's mostly single-sentence classification tasks. BoolQ asks yes/no questions over a Wikipedia passage; CB (CommitmentBank) is three-way entailment over naturally occurring discourse; COPA asks which of two alternatives is the more plausible cause or effect of a premise; MultiRC is multi-sentence reading comprehension where a question can have zero, one, or several correct answers; ReCoRD is cloze-style entity prediction over news passages; RTE is two-way entailment; WiC asks whether a word is used with the same sense in two sentences; and WSC is Winograd-schema pronoun coreference resolution. Two further sets, AX-b (a broad-coverage entailment diagnostic) and AX-g (a Winogender-based gender-bias probe), are reported alongside the suite but are analysis tools, not part of the main score.

The eight tasks intentionally span very different formats -- classification, span extraction, and multi-label selection -- to reward models that generalize across task shapes rather than ones tuned to one input pattern.

## How it is scored

Each task keeps its own metric: accuracy for BoolQ, COPA, RTE, and WiC; the average of accuracy and F1 for CB; the average of F1a (a relaxed per-answer F1) and exact match for MultiRC; the average of F1 and exact match for ReCoRD; and accuracy for WSC. The headline SuperGLUE Score is the unweighted average of those eight per-task numbers. The paper explains this weighting choice explicitly: "lacking a fair criterion with which to weight the contributions of each task to the overall score, we opt for the simple approach of weighing each task equally," with multi-metric tasks first averaged internally before entering the overall mean.

Officially, scoring the eight-task composite means submitting predictions to the SuperGLUE evaluation server, since test-set labels were never published for any of the eight tasks. Most papers and harnesses outside the official leaderboard instead score the labelled dev split per task, as lm-evaluation-harness and OpenCompass both do.

## Dataset and licence

Summing the paper's own per-task table gives train sizes from 250 (CB) to roughly 101,000 (ReCoRD), and dev sizes from 57 (CB) to roughly 10,000 (ReCoRD), totalling about 25,730 dev-split examples across the eight tasks -- the split most non-leaderboard numbers actually use, since test labels are withheld for all eight. This repository's own `superglue_cb` subset page independently counted the released CB files and found 56 dev examples rather than the paper's stated 57, a small but real discrepancy between the paper's table and the distributed data, worth checking per-task rather than assuming the paper's numbers exactly match any given data release. AX-b and AX-g are separate, test-only, hidden-label diagnostic sets scored outside the eight-task average. The Hugging Face dataset card lists licence "other": SuperGLUE republishes or extends several pre-existing datasets, each keeping its own original terms.

## Who publishes it

Alex Wang, Yada Pruksachatkun, Nikita Nangia, Amanpreet Singh, Julian Michael, Felix Hill, Omer Levy and Samuel R. Bowman, at New York University, published SuperGLUE at NeurIPS 2019 as "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems." The benchmark site and leaderboard live at super.gluebenchmark.com; the authors' own baseline and evaluation toolkit is `nyu-mll/jiant` on GitHub.

## Lineage

GLUE (`glue.md`) is SuperGLUE's direct predecessor: SuperGLUE was built by an overlapping author group specifically because GLUE's composite score had been exceeded by models within about 14 months of release, leaving no headroom to separate strong systems. Nine of SuperGLUE's component tasks and diagnostics already have their own pages in this repository -- `superglue_cb`, `superglue_copa`, `superglue_multirc`, `superglue_record`, `superglue_rte`, `superglue_wic`, `superglue_wsc`, `superglue_ax_b`, and `superglue_ax_g` -- along with `boolq`, which is SuperGLUE's BoolQ task documented under its own bare id rather than a `superglue_`-prefixed one; none of those pages' own `lineage.family` fields point back to `super_glue` yet, since this family page did not exist when they were written. This repository has no tracked successor id for SuperGLUE itself, though the field's broad move to open-ended, agentic, and long-context benchmarks after 2020-2021 functions as its informal successor.

## Saturation and contamination

SuperGLUE is saturated. Several of its component tasks already report near-ceiling human estimates in the original paper (98.9% accuracy on CB, for instance), and multiple per-task pages in this repository independently reach the same `saturated` conclusion for their own component task. No current, aggregated eight-task leaderboard score was recovered from the SuperGLUE site during this research pass, since it renders via JavaScript rather than static content, so this page records no present-day composite top score rather than guessing one. The strongest available evidence of saturation is indirect: the field's benchmarking attention moved on to MMLU-style knowledge tests, agentic evaluations, and long-context suites well before the current generation of models, and no model card in this repository reports a `super_glue` composite score.

Contamination risk is high across the suite. Dev-split labels and training data for all eight component tasks have been public since 2019 and widely mirrored on GitHub and Hugging Face; several source datasets (the Winograd Schema Challenge underlying WSC, the RTE challenge sets) were already public for years before SuperGLUE incorporated them. Because most harness implementations score the dev split rather than submitting to SuperGLUE's hidden-label test server, a model that has seen the dev files during pretraining has a realistic path to an inflated score on any component task.

## How to run it

lm-evaluation-harness has no single runnable `super_glue` task; instead its `super-glue-lm-eval-v1` tag groups the eight tasks (`boolq`, `cb`, `copa`, `multirc`, `record`, `rte`, `wic`, `wsc`) as individually runnable tasks scored on the dev split, and a second tag, `super-glue-t5-prompt`, provides a T5-paper-matching prompt variant of each (noting `record` can error under `accelerate` in that variant). OpenCompass likewise configures each task separately -- `SuperGLUE_CB`, `SuperGLUE_COPA`, `SuperGLUE_WSC`, and so on -- rather than exposing one combined SuperGLUE dataset. No SuperGLUE configuration was found in HELM's or BIG-bench's task lists in the sources opened for this page. The official SuperGLUE composite score requires submitting predictions to the evaluation server at super.gluebenchmark.com, since public test-set labels do not exist for any of the eight tasks.

## Reading the numbers

A high SuperGLUE composite score, on its own, mostly says a model handles a specific slate of 2019-era English classification and span-extraction formats well -- it says little about current frontier capability, since the suite was designed to separate 2019 systems and has not been the field's benchmark of choice for years. The composite also hides which of eight very differently shaped tasks moved the number: a strong ReCoRD F1/EM and a weak WSC accuracy can average to the same headline score as the reverse, so check the per-task breakdown (via this repository's own `superglue_*` and `boolq` pages) before treating a single SuperGLUE figure as evidence of general language understanding. Given the suite's near-ceiling human baselines on several component tasks and its high contamination risk, treat any SuperGLUE number, composite or per-task, as measuring a fixed, dated target rather than open-ended capability.
