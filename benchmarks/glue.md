---
id: glue
name: "GLUE (General Language Understanding Evaluation benchmark)"
aliases:
  - "General Language Understanding Evaluation benchmark"
page_kind: family
category: composite
subcategory: "multi-task English sentence and sentence-pair understanding suite (acceptability, sentiment, paraphrase, similarity, inference)"
status: superseded
summary: "A nine-task English sentence-understanding suite that defined pre-LLM benchmarking from 2018; models exceeded its human baseline within about 14 months, and its own successor SuperGLUE replaced it."
measures: >
  GLUE bundles nine separately scored English sentence- and sentence-pair-classification tasks behind one
  composite score, plus a hand-built diagnostic set reported on the side. Single-sentence tasks ask whether
  a sentence is grammatically acceptable (CoLA) or what sentiment it expresses (SST-2). Similarity and
  paraphrase tasks ask whether two sentences paraphrase each other (MRPC), how similar they are on a 1-5
  scale (STS-B), or whether two Quora questions ask the same thing (QQP). Inference tasks recast entailment,
  reading comprehension and coreference as two- or three-way sentence-pair classification (MNLI, QNLI, RTE,
  WNLI). The nine tasks vary enormously in size by design, from a few hundred training pairs (WNLI) to
  hundreds of thousands (QQP, MNLI), so a model must generalise across data-scarce and data-rich tasks
  rather than simply having enough examples to fine-tune on any single one.
task_format: >
  Nine separately trained-and-scored tasks, almost all single-sentence or sentence-pair classification;
  STS-B alone is a regression. Each task keeps its own metric (see How it is scored) and the nine scores are
  averaged, unweighted, into one GLUE Score out of 100. A separate, analysis-only diagnostic set (AX) is
  reported alongside the score but not folded into it.
metric:
  name: "GLUE Score: unweighted average of nine per-task scores (accuracy for five tasks, Matthews correlation for CoLA, mean of accuracy and F1 for MRPC and QQP, mean of Pearson and Spearman correlation for STS-B)"
  direction: higher_is_better
  unit: points
  max_score: 100
  random_baseline: null
  human_baseline: 87.1
  baseline_note: >
    No single random baseline applies across all nine tasks: they range from 0, the uninformed-guess value
    of the correlation-based metrics (CoLA, STS-B), to roughly 50-65% for the unbalanced binary
    classification tasks, so see each task's own page rather than the family average. The 87.1 human
    baseline is as reported in the SuperGLUE paper (Wang et al., 2019), which attributes it to Nangia and
    Bowman (2019); this page opened the SuperGLUE paper directly but did not independently open that
    underlying source.
dataset:
  size: 69711
  size_note: >
    69,711 validation-split rows sum across the nine tasks (MNLI's matched and mismatched dev sets counted
    separately: 9,815 and 9,832) -- the split most published, non-leaderboard numbers actually use, since
    GLUE's own test-set labels are undisclosed for eight of the nine tasks (returned as -1 placeholders by
    the Hugging Face mirror) and are scored only by submitting predictions to the official leaderboard.
    MRPC is the exception: its Hugging Face test split carries real, publicly disclosed labels, because the
    corpus already had a public test set before GLUE adopted it. Training splits sum to 949,733 rows,
    dominated by QQP (363,846) and MNLI (392,702); the smallest task, WNLI, has only 635 training and 71
    validation rows. A separate 1,104-example diagnostic set (AX) is test-only, hidden-label, and scored by
    a three-class generalisation of Matthews correlation (R3) rather than folded into the nine-task average.
  url: "https://huggingface.co/datasets/nyu-mll/glue"
  license: >
    The Hugging Face dataset card gives licence "other": GLUE reuses nine pre-existing datasets, and the
    card and paper refer users to each one's original licence rather than publishing one unified GLUE
    licence.
  languages:
    - en
  modalities:
    - text
  splits: "9 tasks x (train, validation, test), MNLI's validation and test further split matched/mismatched; test labels hidden (returned as -1) for 8 of 9 tasks, public for MRPC; plus a 1,104-example test-only AX diagnostic set, scored separately"
  public_test_set: false
publisher:
  org: "New York University"
  authors:
    - "Alex Wang"
    - "Amanpreet Singh"
    - "Julian Michael"
    - "Felix Hill"
    - "Omer Levy"
    - "Samuel R. Bowman"
  url: "https://gluebenchmark.com/"
paper:
  title: "GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding"
  arxiv: "1804.07461"
  url: "https://arxiv.org/abs/1804.07461"
  year: 2019
leaderboard_url: "https://gluebenchmark.com/leaderboard"
repo_url: "https://github.com/nyu-mll/GLUE-baselines"
released: "2018-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 88.4
  as_of: "2019-07"
  note: >
    The SuperGLUE paper records the GLUE state of the art as of early July 2019 at 88.4 (XLNet; Yang et al.
    2019), 1.3 points above the 87.1 human-performance estimate it cites (Nangia and Bowman, 2019), and
    states the leading model exceeded that human estimate on four of the nine tasks outright. This page
    found no actively maintained current leaderboard reading beyond that point (see How to run it); today,
    frontier models are not commonly benchmarked on raw GLUE at all -- no model card in this repository
    reports a glue score, consistent with the field having moved to SuperGLUE and later suites.
contamination:
  risk: high
  note: >
    Eight of the nine tasks' training data, and all nine tasks' input text if not every label, have been
    continuously public since GLUE's 2018 release, built on source corpora (the Stanford Sentiment
    Treebank, the Microsoft Research Paraphrase Corpus, SNLI/MultiNLI, SQuAD, four RTE challenge datasets,
    Quora Question Pairs) that were mostly already public for years before that. Wide mirroring across
    GitHub and Hugging Face since 2018 makes exclusion from web-scale pretraining corpora hard to guarantee
    for any of the nine tasks.
harness:
  lm_eval: "glue (tag grouping cola, mnli, mrpc, qnli, qqp, rte, sst, wnli as individually runnable tasks, each scored on the validation split; STS-B is not included in this tag)"
  helm: ""
  opencompass: "No single combined GLUE dataset was found; each task is configured separately, e.g. GLUE_CoLA, GLUE_MRPC, GLUE_QQP."
  bigbench: ""
  other: >
    lm-evaluation-harness's own task README states that GLUE's official test-set labels are not publicly
    available, so it evaluates every subtask on the validation split instead of the hidden test split.
tags:
  - composite
  - classification
  - nlu
  - superseded
  - superglue
  - historical
sources:
  - url: "https://arxiv.org/abs/1804.07461"
    title: "GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding (Wang et al., arXiv:1804.07461)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1804.07461"
    title: "GLUE, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/nyu-mll/glue"
    title: "nyu-mll/glue dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/nyu-mll/glue"
    title: "nyu-mll/glue dataset API, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=nyu-mll/glue"
    title: "nyu-mll/glue datasets-server info (split and config sizes)"
    accessed: "2026-09-08"
  - url: "https://github.com/nyu-mll/GLUE-baselines"
    title: "nyu-mll/GLUE-baselines GitHub repository"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems (Wang et al., arXiv:1905.00537)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/glue"
    title: "lm-evaluation-harness glue tasks directory and README"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/GLUE_CoLA/GLUE_CoLA_ppl_77d0df.py"
    title: "OpenCompass GLUE_CoLA ppl config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

GLUE bundles nine separately scored tasks behind a single composite score: grammatical acceptability
(CoLA); sentiment (SST-2); whether two sentences paraphrase each other (MRPC) or how similar they are 1-5
(STS-B); whether two Quora questions are duplicates (QQP); and entailment between a premise and a
hypothesis, recast from four source tasks into two- or three-way classification (MNLI, QNLI, RTE, WNLI).
Nearly every task is single-sentence or sentence-pair classification in English; only STS-B is a regression.
A separate, hand-built diagnostic set (AX) tests fine-grained entailment phenomena alongside the main score,
not folded into it. The nine tasks deliberately span very different data regimes, from a few hundred
training pairs (WNLI) to hundreds of thousands (QQP, MNLI), to reward models that share knowledge across
tasks rather than ones that merely have enough data for any single one.

## How it is scored

Each task keeps its own metric: accuracy for SST-2, MNLI, QNLI, RTE and WNLI; Matthews correlation
coefficient for CoLA (-1 to 1, 0 the uninformed baseline, chosen for CoLA's unbalanced classes); the mean of
accuracy and F1 for MRPC and QQP, also class-unbalanced; and the mean of Pearson and Spearman correlation
for STS-B. The headline GLUE Score is the unweighted average of those nine numbers, scaled to 0-100, so a
single point does not represent the same underlying quantity from one task to the next.

Officially, scoring means submitting predictions to the GLUE leaderboard, since eight of the nine tasks'
test-set labels were never published (Hugging Face's mirror returns -1 as a dummy label for them); MRPC is
the exception, its labels already public before GLUE adopted the corpus. Most papers outside the official
leaderboard report validation-split scores instead, as lm-evaluation-harness does for every subtask.

## Dataset and licence

69,711 validation rows sum across the nine tasks (MNLI's matched and mismatched dev sets counted
separately) -- the split most non-leaderboard numbers actually use. Training splits sum to 949,733 rows,
overwhelmingly from QQP (363,846) and MNLI (392,702). A separate 1,104-example AX diagnostic set is
test-only, hidden-label, and scored outside the nine-task average (see Saturation and contamination). The
Hugging Face dataset card sets licence "other": GLUE republishes nine pre-existing datasets and refers users
to each one's original licence rather than stating one for the whole suite.

## Who publishes it

Alex Wang, Amanpreet Singh, Julian Michael, Felix Hill, Omer Levy and Samuel R. Bowman, at New York
University, first presented GLUE at the EMNLP 2018 BlackboxNLP workshop, with a revised version at ICLR
2019. The benchmark site and leaderboard live at gluebenchmark.com; the authors' own baseline code is
archived at `nyu-mll/GLUE-baselines` on GitHub.

## Lineage

GLUE has no predecessor -- it repackaged nine pre-existing English NLU datasets under one leaderboard. Its
direct successor is SuperGLUE (Wang et al., 2019), built by several of the same authors specifically
because, in that paper's own words, GLUE performance had "recently surpassed the level of non-expert
humans, suggesting limited headroom for further research"; SuperGLUE does not yet have its own page here.
GLUE also inspired same-shaped benchmarks this repository catalogues, including CLUE (`clue`, released as
"ChineseGLUE" before its current name) and BasqueGLUE, reused inside `basque_bench`. Three of GLUE's nine
tasks have subset pages here (`glue_cola`, `glue_mrpc`, `glue_qqp`); the other six and the AX diagnostic do
not yet have pages.

## Saturation and contamination

GLUE is saturated, and by its own successor's telling, was saturated almost immediately. The SuperGLUE paper
records GLUE's state of the art as of July 2019 at 88.4 (XLNet), 1.3 points above the 87.1 human-performance
estimate it cites (Nangia and Bowman, 2019), beating that estimate outright on four of the nine tasks. That
was barely 14 months after GLUE's own paper reported GPT and BERT at 72.8 and 80.2 against a 63.7
no-transfer-learning baseline -- a climb fast enough that GLUE could no longer discriminate between strong
systems, exactly the case SuperGLUE's authors made for replacing it. Tellingly, aggregate saturation masked
persistent weakness elsewhere: even as the composite score passed the human estimate, GLUE's own diagnostic
set stayed far below its human baseline (0.42 vs 0.80 R3, per SuperGLUE's re-reading of it) -- a saturated
headline number coexisting with a real gap on harder linguistic phenomena.

Contamination risk is high. Every task's training text, and most tasks' labels, have been continuously
public since 2018, built on source corpora mostly already public for years before that, and mirrored
across GitHub and Hugging Face since -- exclusion from web-scale pretraining is not something any of the
nine tasks can claim.

## How to run it

lm-evaluation-harness groups eight of the nine tasks (cola, mnli, mrpc, qnli, qqp, rte, sst, wnli; STS-B
excluded) under a `glue` tag, evaluated on the validation split since GLUE's test labels are not public.
OpenCompass configures each task separately instead -- `GLUE_CoLA`, `GLUE_MRPC`, `GLUE_QQP` and so on -- and
its CoLA config notably scores plain accuracy rather than Matthews correlation, a real protocol difference
from both the paper and lm-evaluation-harness's own `mcc`-scored `cola` task (see `glue_cola`). Not
confirmed in HELM's or BIG-bench's task lists. The GLUE leaderboard (gluebenchmark.com/leaderboard) is
client-rendered and did not return scores as static content during this research pass.

## Reading the numbers

A high GLUE Score, on its own, mostly says a model is competent at short-sentence English classification
circa 2018-2019 -- not much more. The benchmark was designed to separate systems when 70-80 was a good
score; once frontier systems cleared the high 80s it stopped discriminating among them, which is why no
model card in this repository reports it and why SuperGLUE, then harder suites still, took its place. A GLUE
number also hides which of nine unrelated metrics moved it: check the per-task breakdown, since a strong QQP
F1 and a weak CoLA correlation can average to the same headline figure as the reverse. And treat any GLUE
number as measuring a fixed, dated target rather than open-ended language understanding: the diagnostic set
showed models could pass the main score while still failing basic entailment phenomena, so a high GLUE Score
reads better as "solved 2018-era sentence classification" than as "understands language."
