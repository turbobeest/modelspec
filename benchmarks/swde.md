---
id: swde
name: "SWDE (lm-evaluation-harness zero-shot extraction task)"
aliases:
  - "Structured Web Data Extraction"
page_kind: benchmark
category: long-context
subcategory: "in-context information extraction / associative recall from long HTML documents (movie vertical)"
status: active
summary: "Zero-shot task: given a full movie webpage's text in-context, extract the value for a named attribute such as release date or director."
measures: >
  The model is given the raw text of a webpage (from the movie vertical of the SWDE web-extraction
  corpus) together with an attribute key such as "release date," "genre" or "director," and must
  produce the value for that attribute as it appears on the page. This exercises long-context
  associative recall and information extraction: the model must locate a specific fact inside a
  long, noisy, semi-structured document rather than answer from parametric knowledge. The
  lm-evaluation-harness README describes it as a version "designed for the zero-shot evaluation of
  small language models," deliberately adapted to be somewhat easier than the original SWDE
  wrapper-induction formulation.
task_format: "Zero-shot, free-form generation: prompt is page text + attribute key, target is the attribute's value as a short string."
metric:
  name: "contains"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    lm-evaluation-harness scores each item with a "contains" metric (task.py's contains_score):
    a case-insensitive regex search for whether the gold value appears in the model's generated
    continuation, taking the max over any listed valid labels, then averaged across items with
    np.mean. No random or human baseline is published for this harness adaptation. The README notes
    that harness version 1 (2026-06-22) started stripping whitespace from prompts and targets, so
    scores from that version are not comparable to version 0.
dataset:
  size: 1111
  size_note: >
    The Hugging Face dataset card for hazyresearch/based-swde-v2 (the dataset this task loads)
    lists 1,111 rows drawn from 141 documents, in a single "validation" split, ~1.83 MB as parquet.
  url: "https://huggingface.co/datasets/hazyresearch/based-swde-v2"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "validation only (1,111 rows / 141 documents); no separate train or test split in this harness dataset"
  public_test_set: true
publisher:
  org: "Stanford HazyResearch (dataset/task); EleutherAI (lm-evaluation-harness integration)"
  authors:
    - "Simran Arora"
    - "Brandon Yang"
    - "Sabri Eyuboglu"
    - "Avanika Narayan"
    - "Andrew Hojel"
    - "Immanuel Trummer"
    - "Christopher Ré"
  url: "https://github.com/HazyResearch/based-evaluation-harness"
paper:
  title: "Language Models Enable Simple Systems for Generating Structured Views of Heterogeneous Data Lakes"
  arxiv: "2304.09433"
  url: "https://arxiv.org/abs/2304.09433"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/swde"
released: "2023"
last_updated: "2026-06-22"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No leaderboard or cross-model score table for this specific lm-evaluation-harness adaptation was located; the EVAPORATE paper reports its own extraction-quality numbers under a different (non-harness) evaluation protocol, so they are not directly comparable."
contamination:
  risk: medium
  note: >
    The underlying page text and gold values are public (via the original SWDE corpus and the
    hazyresearch/based-swde-v2 Hugging Face dataset), and the movie-page content itself is drawn
    from a public website, so both the pages and plausible answer values could appear in
    pretraining data independent of this benchmark's own publication.
harness:
  lm_eval: "swde"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - information-extraction
  - long-context
  - recall
  - html
  - zero-shot
sources:
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/swde"
    title: "lm-evaluation-harness: swde task directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/swde/README.md"
    title: "swde task README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/swde/swde.yaml"
    title: "swde.yaml task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/swde/task.py"
    title: "swde task.py implementation"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hazyresearch/based-swde-v2"
    title: "hazyresearch/based-swde-v2 dataset card"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2304.09433"
    title: "Language Models Enable Simple Systems for Generating Structured Views of Heterogeneous Data Lakes (EVAPORATE)"
    accessed: "2026-09-08"
  - url: "https://github.com/HazyResearch/based-evaluation-harness"
    title: "HazyResearch based-evaluation-harness"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-007 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-007"
---

## What it measures

`swde` in lm-evaluation-harness gives a model the full text of a webpage — in this implementation,
pages from the movie vertical of the SWDE structured-web-data corpus — plus the name of an
attribute such as "release date," "genre," "MPAA rating" or "director." The model must generate the
value of that attribute as it appears on the page. Because the answer is present verbatim somewhere
in a long, HTML-derived block of text rather than in the model's parametric knowledge, the task is
best read as an associative-recall / in-context information-extraction probe: can the model find
and reproduce a specific fact buried in a longer document, given only a short key describing what
to look for.

The task is explicitly a simplified, zero-shot adaptation for smaller language models rather than a
reimplementation of the full original SWDE wrapper-induction benchmark, which asked systems to
induce extraction rules generalizing across many pages of a site.

## How it is scored

Scoring uses lm-evaluation-harness's own `contains` metric: `task.py`'s `contains_score` does a
case-insensitive regex search for whether the gold value(s) appear anywhere in the model's
generated continuation, taking the best match if multiple valid labels are given, and reports the
mean over the evaluation set. There is no fixed maximum other than 100% (all items matched) and no
published random or human baseline. The task's README flags a protocol change: version 1
(2026-06-22) strips whitespace from both prompts and targets before matching, which changes scores
enough that they should not be compared against version 0 runs.

## Dataset and licence

The harness loads `hazyresearch/based-swde-v2` from Hugging Face, which the dataset card lists as
1,111 rows drawn from 141 source documents, in a single "validation" split (roughly 1.83 MB as
parquet). Each row carries a document id, filename, attribute key, gold value and the page's full
text. No explicit licence is stated on the Hugging Face dataset card for this particular derivative;
the underlying page content originates from a real commercial movie-guide website (AMC), and the
original SWDE corpus it descends from was distributed for academic research use. Both the page text
and the gold answers are visible in the public dataset files.

## Who publishes it

The dataset and this evaluation format come from the EVAPORATE paper, "Language Models Enable
Simple Systems for Generating Structured Views of Heterogeneous Data Lakes" (Arora, Yang, Eyuboglu,
Narayan, Hojel, Trummer and Ré, arXiv:2304.09433, 2023), from Stanford's HazyResearch group. The
group also maintains a fork of lm-evaluation-harness ("based-evaluation-harness") that packages
`swde` alongside other recall-intensive tasks for evaluating sub-quadratic and small language
models; the task has since been folded into the mainline EleutherAI `lm-evaluation-harness` under
`lm_eval/tasks/swde`.

## Lineage

The name traces back to the original SWDE ("Structured Web Data Extraction") corpus introduced by
Hao et al. at SIGIR 2011, 124,291 pages across 80 sites and eight verticals for wrapper-induction
research, later extended with richer open-IE-style annotation by Lockard et al. (OpenCeres, NAACL
2019). The lm-evaluation-harness task's own README instead credits Lockard et al. with originally
curating SWDE for open information extraction from the semi-structured web; that appears to
conflate the original 2011 corpus with the later OpenCeres extension, since Hao et al.'s SIGIR 2011
paper is the source cited elsewhere in the literature for the SWDE corpus itself. The
lm-evaluation-harness `swde` task is a further, much smaller adaptation of that lineage —
restricted to the movie vertical and reformatted as a zero-shot generation task for LLMs — via the
HazyResearch `based-swde-v2` dataset built for the EVAPORATE paper and later reused in
HazyResearch's "recall-intensive" evaluation suite for the BASED architecture line
(arXiv:2402.18668). No successor or variant task of this specific harness adaptation exists in this
repository yet.

## Saturation and contamination

No public leaderboard or standardized cross-model score table for this exact harness task was
found, so saturation status is unknown; scores reported in the EVAPORATE paper itself use a
different, non-harness evaluation pipeline and are not directly comparable to the harness's
`contains` metric. Contamination risk is medium: the source pages are from a real public website and
the extraction dataset itself has been publicly available since 2023, so both the documents and
their attribute values could plausibly appear in pretraining data independent of this benchmark.

## How to run it

Run via lm-evaluation-harness with `--tasks swde`; the task is implemented as a custom Python class
(`task.py`'s `SWDE`, loaded through `swde.yaml`'s `class: !function task.SWDE`) rather than a plain
YAML config, so behavior (prompt construction, target extraction, the `contains_score` metric) lives
in that Python file. It is a zero-shot, generation-based task, not multiple choice. Because of the
2026-06-22 whitespace-handling change noted in the README, confirm which harness version produced
any number before comparing it to another report.

## Reading the numbers

A high `contains` score indicates a model can reliably locate and reproduce a short factual span
from inside a long, noisy in-context document when told what attribute to look for — a narrow but
practically relevant long-context retrieval skill. It says little about the model's ability to
generalize extraction rules across previously unseen page layouts (the harder skill the original
SWDE benchmark targeted), nor about structured-data extraction at the scale evaluated in the
EVAPORATE paper itself. Because there is no established public leaderboard for this harness
variant, treat any single score as informative mainly in comparison to other models run under the
identical harness version.
