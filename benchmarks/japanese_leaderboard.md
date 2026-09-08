---
id: japanese_leaderboard
name: "Japanese Leaderboard (lm-evaluation-harness)"
aliases:
  - "ja_leaderboard"
page_kind: family
category: composite
subcategory: "lm-evaluation-harness task group running eight independently-authored Japanese NLP tasks, reported without a combined score"
status: active
summary: "japanese_leaderboard is an lm-evaluation-harness group running eight independent Japanese NLP tasks -- JAQKET, four JGLUE tasks, MGSM, XL-Sum and XWinograd -- with no combined score computed."
measures: >
  japanese_leaderboard is not one benchmark but an lm-evaluation-harness task group: running it executes
  eight separately-authored Japanese evaluation tasks and reports each one's own metric, not a single
  blended score. Four come from JGLUE, Japan's general language-understanding benchmark suite
  (JCommonsenseQA, JNLI, JSQuAD, MARC-ja); the other four are JAQKET v2 (Wikipedia-grounded quiz question
  answering), the Japanese subset of MGSM (grade-school maths word problems), the Japanese subset of
  XL-Sum (news summarisation), and the Japanese subset of XWinograd (commonsense pronoun resolution). A
  model's results under this group name are eight separate numbers on different scales -- exact match,
  classification accuracy and ROUGE-2 among them -- not one measurement of "Japanese ability."
task_format: >
  A group of eight independently-formatted tasks. JCommonsenseQA, JNLI, MARC-ja and XWinograd are
  multiple-choice or classification tasks scored by comparing log-likelihoods over labelled options.
  JAQKET v2 and JSQuAD are extractive question answering scored by exact match against generated text.
  MGSM is a generated chain-of-reasoning math answer scored by extracting a final number. XL-Sum is
  free-form generated summarisation scored by ROUGE-2. Few-shot counts also vary by component, from
  zero (XWinograd) to five (MGSM); no single prompt format or shot count applies across the group.
metric:
  name: "no combined metric: each of the eight component tasks reports its own metric (exact_match, acc, or a custom ROUGE-2 aggregation) independently"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random baseline applies: JNLI is a three-way choice, MARC-ja is binary, JCommonsenseQA
    and XWinograd have their own separate option counts, and JAQKET v2, JSQuAD, MGSM and XL-Sum are
    generation tasks with no fixed-choice baseline at all. Unlike this repository's
    `arabic_leaderboard_complete` page, the harness's own group config for this task (`_ja_leaderboard.yaml`,
    read directly for this page) does not define an `aggregate_metric_list`, so no weighted or
    unweighted combined number is computed automatically the way one is for the Arabic group.
dataset:
  size: null
  size_note: >
    No single item count applies. This aggregates eight heterogeneous task groups drawn from three
    separate source projects -- JGLUE (four tasks), JAQKET, and separately-adapted multilingual sets for
    MGSM, XL-Sum and XWinograd -- each with its own train/validation/test structure. No source read for
    this page gives a combined item count across all eight groups.
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/japanese_leaderboard"
  license: "Varies by component dataset (JGLUE, JAQKET, MGSM, XL-Sum and XWinograd each carry their own terms); not established as a single licence for this page."
  languages: [ja]
  modalities: [text]
  splits: "each component task draws its own validation or test split for evaluation and its own training split for few-shot exemplars; no single split description applies across all eight"
  public_test_set: true
publisher:
  org: "lm-evaluation-harness (EleutherAI); the task group's README credits its prompts to Stability AI's Japanese fork of the harness"
  authors: []
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/japanese_leaderboard"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/japanese_leaderboard"
released: ""
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Because the harness computes no combined score for this group, "saturated" is not a well-defined
    question for japanese_leaderboard as a whole the way it can be for a single-metric benchmark; it
    would have to be asked separately of each of the eight components. No current per-component
    standings were established from a source read for this page.
contamination:
  risk: high
  note: >
    Every component dataset is public with answers and has been for two to six years by the date of
    this research: JAQKET since 2020, JGLUE (JCommonsenseQA, JNLI, JSQuAD, MARC-ja) since 2022, MGSM and
    XL-Sum since 2021-2022, and XWinograd's Japanese portion since around the same period -- all well
    before the training cutoff of any model current at the time of this research. No held-out or
    refreshed portion is described for any of the eight groups.
harness:
  lm_eval: "japanese_leaderboard"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The eight component task names are ja_leaderboard_jaqket_v2, ja_leaderboard_jcommonsenseqa,
    ja_leaderboard_jnli, ja_leaderboard_jsquad, ja_leaderboard_marc_ja, ja_leaderboard_mgsm,
    ja_leaderboard_xlsum and ja_leaderboard_xwinograd, each independently runnable. The group's own
    `_ja_leaderboard.yaml` lists only the group name and this eight-task list, with no
    `aggregate_metric_list` block -- confirmed by reading the file directly and comparing it against
    `arabic_leaderboard_complete.yaml`, which does define one.
tags: [composite, japanese, leaderboard, multiple-choice, question-answering, summarization, math, commonsense]
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/japanese_leaderboard/README.md"
    title: "japanese_leaderboard README: task list, sources and citations"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/japanese_leaderboard/_ja_leaderboard.yaml"
    title: "_ja_leaderboard.yaml: group definition, eight-task list, no aggregate_metric_list"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arabic_leaderboard_complete/arabic_leaderboard_complete.yaml"
    title: "arabic_leaderboard_complete.yaml: comparison point showing an explicit aggregate_metric_list"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/japanese_leaderboard/ja_leaderboard_xlsum.yaml"
    title: "ja_leaderboard_xlsum.yaml: ROUGE-2 metric definition"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/japanese_leaderboard/ja_leaderboard_mgsm.yaml"
    title: "ja_leaderboard_mgsm.yaml: 5-shot generation config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/japanese_leaderboard/ja_leaderboard_xwinograd.yaml"
    title: "ja_leaderboard_xwinograd.yaml: zero-shot multiple-choice config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

japanese_leaderboard is not one benchmark but an lm-evaluation-harness task group: invoking it runs eight
separately-authored Japanese evaluation tasks and reports each one's own result, not a single blended score.
Four tasks come from JGLUE, Japan's JGLUE general-language-understanding suite -- JCommonsenseQA
(commonsense multiple-choice), JNLI (natural-language inference), JSQuAD (extractive reading
comprehension) and MARC-ja (binary review-sentiment classification). The other four are JAQKET v2
(Wikipedia-grounded Japanese quiz question answering), the Japanese subset of MGSM (grade-school maths word
problems), the Japanese subset of XL-Sum (news summarisation) and the Japanese subset of XWinograd
(commonsense pronoun resolution). Because these eight tasks measure different skills on different scales, a
single number under this group's name does not exist, and treating any one component's score as
representative of "Japanese ability" overall would misread what the group actually reports.

## How it is scored

Each of the eight tasks is scored on its own terms. JCommonsenseQA, JNLI, MARC-ja and XWinograd compare
log-likelihoods over labelled multiple-choice options. JAQKET v2 and JSQuAD generate free text and score it
by exact match. MGSM generates a worked solution and extracts a final numeric answer for accuracy scoring.
XL-Sum generates a summary and scores it with ROUGE-2. Few-shot counts differ by task, from zero-shot
(XWinograd) up to five-shot (MGSM), and this repository's `arabic_leaderboard_complete` page is the
precedent for how this kind of many-tasks-under-one-name page is handled here: as in that case, this page
treats the group as a bundle of separate measurements rather than pretending a single figure summarises it.
Unlike the Arabic group, though, japanese_leaderboard's own harness configuration defines no combined
metric at all -- there is no size-weighted or unweighted aggregate here, only the eight independent results.

## Dataset and licence

No single item count or licence applies. The eight component tasks are drawn from three separate source
projects with their own dataset structures: JGLUE (JCommonsenseQA, JNLI, JSQuAD, MARC-ja), JAQKET, and
separately-adapted multilingual resources for MGSM, XL-Sum and XWinograd's Japanese portions. Each carries
its own licence, none summarised into one answer here, and its own split structure -- generally a training
split used for few-shot exemplars and a validation or test split used for scoring.

## Who publishes it

This task group is maintained inside EleutherAI's lm-evaluation-harness. Its README credits the prompt
templates to Stability AI's Japanese fork of the harness (`Stability-AI/lm-evaluation-harness`, branch
`jp-stable`). The eight underlying tasks have separate authorship: JAQKET was introduced by Suzuki et al.
in 2020; JGLUE (JCommonsenseQA, JNLI, JSQuAD, MARC-ja) by Kurihara, Kawahara and Shibata; MGSM extends
GSM8K (Cobbe et al.) to multiple languages via Shi et al.; XL-Sum is from Hasan et al.; and XWinograd's
multilingual construction comes from Muennighoff et al. and Tikhonov and Ryabinin. None of these five
source projects has its own page in this repository yet, though `gsm8k` (in this repository) documents the
English original that MGSM extends to Japanese and ten other languages.

## Lineage

No predecessor or successor is tracked for this id, and none of its eight component task groups has its
own page in this repository yet. As with `arabic_leaderboard_complete`, this page's job is to name what the
group aggregates and be explicit that the aggregate is not one measurement -- and the comparison between
the two pages is itself informative: the Arabic group defines a weighted combined score across its 14
components, while this Japanese group defines none across its eight, despite both being named and structured
similarly as harness task groups.

## Saturation and contamination

Because no combined score exists, whether japanese_leaderboard is "saturated" is not a well-formed question
for the group as a whole; it would need to be asked separately of each component, and no current
per-component standings were established from a source read for this page. Contamination risk is high:
every component dataset is public with answers and has been for two to six years by the date of this
research -- JAQKET since 2020, the four JGLUE tasks since 2022, and MGSM, XL-Sum and XWinograd's Japanese
portions since 2021-2022 -- all well before the training cutoff of any model current today. No held-out or
refreshed portion is described for any of the eight groups.

## How to run it

`lm_eval --tasks japanese_leaderboard` runs all eight component tasks in one invocation and reports each
one's own metric; any component can also be run alone by name (for example `lm_eval --tasks
ja_leaderboard_jsquad`). Because there is no aggregate_metric_list in the group's configuration, there is no
single number to compare across models from this group name -- comparing models means comparing the same
named component's score across runs, not a "japanese_leaderboard score."

## Reading the numbers

There is no single "japanese_leaderboard score" to read, and a report that presents one without naming
which of the eight components it came from should be treated with suspicion. Read each component the way
its own benchmark is normally read: JSQuAD and JAQKET v2 as extractive reading comprehension, JNLI and
JCommonsenseQA and MARC-ja and XWinograd as their respective classification or commonsense tasks, MGSM as
grade-school arithmetic reasoning in Japanese, and XL-Sum as summarisation quality by a lexical-overlap
metric that does not capture fluency or faithfulness well on its own. Given every component's long public
availability, a very high score on any one of them is at least as likely to reflect prior exposure as
genuine task skill.
