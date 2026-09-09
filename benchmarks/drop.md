---
id: drop
name: "DROP"
aliases: ["DROP: A Reading Comprehension Benchmark Requiring Discrete Reasoning Over Paragraphs"]
page_kind: benchmark
category: reasoning
subcategory: "reading comprehension with discrete reasoning"
status: active
summary: "An adversarially crowdsourced reading-comprehension test requiring numerical and discrete operations -- addition, counting, sorting -- over a paragraph, not just span lookup."
measures: >
  DROP gives a model a short English passage -- commonly a Wikipedia paragraph about an NFL game, a
  census report or a historical event -- and a question that cannot be answered by locating one
  matching span of text. Answering requires resolving references to multiple positions in the
  passage and then performing a discrete operation over what is found there: adding or subtracting
  numbers, counting how many events satisfy a condition, sorting values, or comparing dates.
  Answers are a number, a date, or one or more short text spans; there are no answer choices.
task_format: "Free-response reading comprehension: passage plus question in, a number, a date, or one or more text spans out; no answer choices."
metric:
  name: "F1 (exact match also reported)"
  direction: higher_is_better
  unit: "% F1"
  max_score: 100
  random_baseline: null
  human_baseline: 96.0
  baseline_note: >
    The original paper reports 96.0% F1 for expert human performance and 32.7% F1 for the best 2019
    system (a semantic-parsing baseline); the authors' own NAQANet model, combining reading
    comprehension with simple numerical reasoning, reached 47.0% F1. No meaningful random-guess
    baseline exists for free-response numeric, date and span answers.
dataset:
  size: 9535
  size_note: >
    96,567 question-answer pairs were collected in total (the paper's figure) over roughly 7,000
    passages, randomly partitioned by passage into training (80%), development (10%) and test (10%)
    so no passage's questions cross a split. The public Hugging Face mirror (ucinlp/drop) carries
    only training (77,400 rows) and validation (9,535 rows, the number recorded here as `size` since
    it is the split almost every current harness actually scores against); the original held-out
    test split is not in the public download. A second mirror lm-evaluation-harness itself pulls
    from, EleutherAI/drop, carries train (77,409) and validation (9,536) -- a small, few-question
    difference from ucinlp/drop that neither dataset card explains.
  url: "https://huggingface.co/datasets/ucinlp/drop"
  license: "CC BY-SA 4.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "train (77,400), validation (9,535) on the public mirror; a held-out test split exists per the paper's 80/10/10 partition but is not in the public download"
  public_test_set: true
publisher:
  org: "University of California, Irvine; Allen Institute for AI; University of Washington; Hebrew University of Jerusalem"
  authors: ["Dheeru Dua", "Yizhong Wang", "Pradeep Dasigi", "Gabriel Stanovsky", "Sameer Singh", "Matt Gardner"]
  url: "https://allenai.org/data/drop"
paper:
  title: "DROP: A Reading Comprehension Benchmark Requiring Discrete Reasoning Over Paragraphs"
  arxiv: "1903.00161"
  url: "https://arxiv.org/abs/1903.00161"
  year: 2019
leaderboard_url: "https://leaderboard.allenai.org/drop/submissions/public"
repo_url: "https://github.com/allenai/allennlp-reading-comprehension"
released: "2019-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 80.9
  as_of: "2023-03"
  note: >
    OpenAI's GPT-4 technical report (2023-03) records 80.9 F1 3-shot on DROP, ahead of GPT-3.5's 64.1
    but still behind QDGAT, a system trained specifically for DROP, at 88.4 F1 -- one of the few
    benchmarks in that report where a specialised model still beat GPT-4. That leaves real distance
    to the original paper's 96.0% human-performance estimate. No later frontier-model DROP score was
    found during this research, so current standing beyond 2023 is not established here.
contamination:
  risk: medium
  note: >
    GPT-4's technical report separately estimates about 21% overlap between DROP and GPT-4's
    pretraining data, but reports GPT-4 scoring 82.5 F1 on the non-overlapping subsample versus 80.9
    F1 overall -- a higher score on the clean portion, which argues against contamination inflating
    that particular result. The validation split's answers have been public since 2019 and are
    widely mirrored, so risk should be assumed higher for models trained on more recent, less
    curated web crawls without explicit decontamination.
harness:
  lm_eval: "drop"
  inspect_evals: "drop"
  helm: ""
  opencompass: "drop"
  bigbench: ""
  other: ""
tags: ["reading-comprehension", "numerical-reasoning", "discrete-reasoning", "free-response", "crowdsourced"]
sources:
  - url: "https://arxiv.org/abs/1903.00161"
    title: "DROP: A Reading Comprehension Benchmark Requiring Discrete Reasoning Over Paragraphs (Dua et al., 2019)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1903.00161"
    title: "DROP paper, full text (ar5iv HTML)"
    accessed: "2026-09-08"
  - url: "https://github.com/allenai/allennlp-reading-comprehension"
    title: "allenai/allennlp-reading-comprehension GitHub repository (drop_eval.py reference scorer)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ucinlp/drop"
    title: "ucinlp/drop dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/drop"
    title: "EleutherAI/drop dataset (mirror used by lm-evaluation-harness)"
    accessed: "2026-09-08"
  - url: "https://allenai.org/data/drop"
    title: "DROP dataset homepage, Allen Institute for AI"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/drop"
    title: "lm-evaluation-harness drop task"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/drop"
    title: "inspect_evals drop task"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/drop"
    title: "OpenCompass drop dataset configs"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2303.08774"
    title: "GPT-4 Technical Report (OpenAI, 2023) -- DROP score and contamination estimate"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

DROP gives a model a short English passage -- commonly drawn from Wikipedia articles about NFL game
recaps, census data or history -- and a question that cannot be answered by finding one matching
span of text. A question typically requires resolving references to multiple positions in the
passage and then performing a discrete operation over what is found there: adding or subtracting two
numbers, counting how many events satisfy a condition, sorting a set of values, or comparing two
dates. Answers are a number, a date, or one or more short text spans copied from the passage; there
are no multiple-choice options. It targets a specific gap the authors identified in earlier
reading-comprehension datasets such as SQuAD: systems that had learned to locate a matching span
without doing any arithmetic or comparison over what they found.

## How it is scored

Predictions are scored against a normalized reference answer with exact match (EM) and token-level
F1, using number and date normalization so "6" and "six", or reordered multi-span answers, still
count as correct; the bipartite-matching approach for multi-span answers is adapted from SQuAD-style
scoring. The original paper's own baselines set the scale: a semantic-parsing system reached 32.7%
F1 and the authors' own NAQANet, combining a reading-comprehension model with simple numerical
reasoning, reached 47.0% F1, against 96.0% F1 for expert human performance. lm-evaluation-harness
and OpenCompass both report EM and F1; a fixed random-guess baseline is not meaningful for
free-response numeric, date and span answers.

## Dataset and licence

The authors crowdsourced 96,567 question-answer pairs adversarially -- workers saw a passage and a
baseline model's live predictions, then wrote questions the model got wrong -- over roughly 7,000
Wikipedia passages, randomly partitioned by passage into training (80%), development (10%) and test
(10%) so no passage's questions cross a split boundary. The public Hugging Face mirror (`ucinlp/drop`,
CC BY-SA 4.0) carries only the training split (77,400 rows) and the development split, labelled
`validation` (9,535 rows); the original test split is not in the public download, consistent with a
leaderboard-graded evaluation whose test answers were never fully opened. In practice almost every
harness, including lm-evaluation-harness, scores against this public validation split, so its answers
are effectively public for anyone running the benchmark today. A second mirror lm-evaluation-harness
itself uses, `EleutherAI/drop`, carries train (77,409) and validation (9,536) rows -- a small,
unexplained difference from `ucinlp/drop`.

## Who publishes it

DROP was introduced by Dheeru Dua, Yizhong Wang, Pradeep Dasigi, Gabriel Stanovsky, Sameer Singh and
Matt Gardner, with affiliations spanning UC Irvine, the Allen Institute for AI, the University of
Washington and the Hebrew University of Jerusalem, and published at NAACL 2019. AI2 hosts the dataset
and reference evaluation code inside its `allennlp-reading-comprehension` repository and originally
ran a public leaderboard at leaderboard.allenai.org/drop; that URL did not respond during this
research (2026-09), suggesting it may no longer be maintained. Today the benchmark is mainly kept
usable through general-purpose harnesses -- lm-evaluation-harness, Inspect Evals and OpenCompass each
ship a `drop` task.

## Lineage

DROP has no formal predecessor or successor in this repository; it was built as a direct response to
the limits of span-extraction datasets like SQuAD, which the authors argued could be solved without
arithmetic or discrete reasoning. No dataset has explicitly superseded it, though its
numerical/discrete-reasoning framing anticipated a wave of later benchmarks that pair reading
comprehension with light computation.

## Saturation and contamination

DROP is not fully saturated, but the frontier moved well past its 2019 baselines. OpenAI's GPT-4
technical report (2023-03) recorded 80.9 F1 3-shot -- ahead of GPT-3.5's 64.1 F1, but still short of
QDGAT, a system trained specifically for DROP, at 88.4 F1, one of the few benchmarks in that report
where a specialised model still beat GPT-4. That leaves real distance to the paper's 96.0%
human-performance estimate, and no more recent frontier-model score was found during this research,
so current standing is not established here. Contamination risk is medium: GPT-4's report separately
estimated about 21% overlap between DROP and its pretraining data, but found GPT-4 scoring 82.5 F1 on
the non-overlapping subsample versus 80.9 F1 overall -- a higher score on the clean portion, evidence
against contamination inflating that particular number. The public validation split's answers have
been downloadable since 2019, so risk should be assumed higher for any model trained on more recent,
less curated crawls.

## How to run it

lm-evaluation-harness's `drop` task (`generate_until`, scored on EM and F1 against the `EleutherAI/drop`
validation split) implements the original AI2 evaluation logic from `allennlp-reading-comprehension`.
Inspect Evals and OpenCompass each ship their own `drop` task; Inspect Evals defaults to a 3-shot
prompt. Because scoring depends on an answer-normalization step (numbers, articles, punctuation)
rather than raw string match, reported EM and F1 can shift slightly between implementations that
normalize differently, and prompt format (zero-shot versus few-shot, whether the model is told where
to stop generating) affects generation-based scoring more than it would a multiple-choice task.

## Reading the numbers

A high DROP score shows a model can combine simple arithmetic, counting or comparison with reading
comprehension, not just locate a matching sentence -- a meaningfully different skill from
SQuAD-style extraction. Because the practically-used evaluation split has had public answers since
2019, and frontier vendors rarely headline DROP scores today, treat any DROP number with the caution
due an older, unrefreshed benchmark: corroborate it against a newer numerical-reasoning benchmark
before drawing conclusions about current capability. The gap AI2's own benchmark-specific baseline
held over general-purpose GPT-4 as late as 2023 is a reminder that a benchmark's ceiling and a
general model's score on it can diverge for a long time.
