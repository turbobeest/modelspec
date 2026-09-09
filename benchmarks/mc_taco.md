---
id: mc_taco
name: "MC-TACO"
aliases:
  - "MC-TACO"
  - "MCTACO"
  - "mc-taco"
  - "Multiple Choice TemporAl COmmonsense"
page_kind: benchmark
category: reasoning
subcategory: "temporal commonsense as per-candidate yes/no plausibility"
status: unknown
summary: "13k English temporal-commonsense candidate answers; the paper scores question-level EM/F1, while lm-eval reports pair-level acc/F1."
measures: >
  MC-TACO (Multiple Choice TemporAl COmmonsense) gives a MultiRC context
  sentence, a temporal question, and one candidate answer. The system must
  say whether that candidate is plausible. Five properties: duration,
  ordering, typical time, frequency, and stationarity. More than one
  candidate per question can be yes. English only. This is not a single
  exclusive MCQ and not a cooking-TACO code benchmark.
task_format: >
  lm-eval multiple_choice on CogComp/mc_taco. Prompt:
  "{sentence} Question: {question} Answer: {answer} Plausible:".
  Choices no/yes. Target is the binary label. validation and test splits.
  should_decontaminate true. --limit shuffles pairs and can drop some
  options of a question.
metric:
  name: "paper: question-level EM and F1; lm-eval: pair-level acc and F1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 87.1
  baseline_note: >
    Paper Table 2 on the full test set: Random F1 36.2 / EM 8.1; Always
    Positive 49.8 / 12.1; BERT+unit 69.9 / 42.7. Human F1 87.1 / EM 75.8
    is a 100-question subset, not the full 1,332 questions. Prose later
    quotes BERT+unit F1=72 EM=45, which does not match Table 2. lm-eval
    metric_list is acc and f1 on each candidate pair, not question EM.
dataset:
  size: 13225
  size_note: >
    Hub CogComp/mc_taco: test 9,442 pairs, validation 3,783 pairs (13,225
    total). Those match dataset/test_9442.tsv and dev_3783.tsv. Question
    counts: 1,332 test and 561 dev. No train split; the authors treat dev
    as the only supervision. Context sentences come from MultiRC.
  url: "https://github.com/CogComp/MCTACO"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "validation/dev 3,783 pairs (561 questions); test 9,442 pairs (1,332 questions); no train"
  public_test_set: true
publisher:
  org: "University of Pennsylvania / Allen Institute for AI / University of Illinois"
  authors:
    - "Ben Zhou"
    - "Daniel Khashabi"
    - "Qiang Ning"
    - "Dan Roth"
  url: "https://github.com/CogComp/MCTACO"
paper:
  title: "\"Going on a vacation\" takes longer than \"Going for a walk\": A Study of Temporal Commonsense Understanding"
  arxiv: "1909.03065"
  url: "https://arxiv.org/abs/1909.03065"
  year: 2019
leaderboard_url: ""
repo_url: "https://github.com/CogComp/MCTACO"
released: "2019-09"
last_updated: "2020-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 69.9
  as_of: "2019"
  note: >
    Best full-test system in Table 2 is BERT+unit F1 69.9 / EM 42.7, about
    17 F1 below the 100-question human subset. No later public cell was
    opened. lm-eval pair-level acc is a different scale.
contamination:
  risk: high
  note: >
    Dev and test have been public on GitHub since 2019-08-18 and on the Hub
    as CogComp/mc_taco. Contexts are MultiRC sentences. lm-eval sets
    should_decontaminate on question+sentence. There is no hidden test.
harness:
  lm_eval: "mc_taco"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "official evaluator/evaluator.py reports question-level em and f1"
tags:
  - temporal
  - commonsense
  - multiple-choice
  - lm-eval
sources:
  - url: "https://arxiv.org/abs/1909.03065"
    title: "MC-TACO paper (arXiv 1909.03065, EMNLP 2019)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/1909.03065"
    title: "MC-TACO HTML (Table 2 Random/BERT/Human; 1,332 test questions)"
    accessed: "2026-09-08"
  - url: "https://github.com/CogComp/MCTACO"
    title: "CogComp/MCTACO repository (no licence file; created 2019-08-18)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/CogComp/MCTACO/master/dataset/readme.txt"
    title: "dataset/readme.txt (561/1332 questions; 3783/9442 pairs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/CogComp/MCTACO/master/evaluator/evaluator.py"
    title: "Official question-level EM/F1 evaluator"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/CogComp/mc_taco"
    title: "Hub card CogComp/mc_taco (licence unknown; 9442/3783 splits)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mc_taco/README.md"
    title: "lm-eval mc_taco README (task name, --limit warning)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mc_taco/default.yaml"
    title: "lm-eval default.yaml (task mc_taco, acc and f1)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-056 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-056"
---

## What it measures

MC-TACO tests English temporal commonsense. The model sees a context sentence from MultiRC, a question about time, and one candidate answer. It must say yes (plausible) or no. Zhou, Khashabi, Ning, and Roth group questions into duration, ordering, typical time, frequency, and stationarity. A question can have several gold-yes answers, or none. Crowdsourcing on Mechanical Turk built the questions and labels. This is not an exclusive four-way quiz and not a code-TACO task.

## How it is scored

The paper and `evaluator.py` score at question level. Exact match requires every candidate of that question to be labelled correctly. Question F1 is the precision/recall of the yes set, then averaged. Table 2 (full test): Random 36.2 F1 / 8.1 EM; BERT+unit 69.9 / 42.7. Human 87.1 / 75.8 is 100 questions only. lm-eval task `mc_taco` instead reports accuracy and F1 on each isolated pair, which is easier and not the paper metric. `--limit` shuffles pairs and can drop some options, so those runs are invalid for EM/F1.

## Dataset and licence

Dev: 561 questions, 3,783 pairs. Test: 1,332 questions, 9,442 pairs. Hub `CogComp/mc_taco` matches those pair counts. There is no train split; the authors say world knowledge should come from pretraining. The GitHub repo has no licence file. The Hub card lists `license: unknown`. Leave the licence empty.

## Who publishes it

Ben Zhou and Dan Roth (then Penn / UIUC), Daniel Khashabi (Allen Institute for AI), Qiang Ning (then Illinois). EMNLP 2019; arXiv 1909.03065 (6 September 2019). Code at `CogComp/MCTACO`. The lm-eval README still names `https://leaderboard.allenai.org/mctaco`; that host did not resolve on 2026-09-08.

## Lineage

No predecessor page in this repository. Contexts come from MultiRC. No temporal-commonsense successor is filed here under this id. Do not confuse with later "TACO" code datasets.

## Saturation and contamination

2019 BERT+unit still sat well below the 100-question human subset on question EM. Whether current LLMs saturate question-level EM was not established here. Dev and test have been public since 2019, so pair text is an obvious training-data risk.

## How to run it

Paper protocol: predict yes/no per pair, then `python evaluator/evaluator.py eval --test_file dataset/test_9442.tsv --prediction_file ...`. lm-eval: `lm_eval --tasks mc_taco` on `CogComp/mc_taco`. Do not pass `--limit`. Do not quote lm-eval acc as Table 2 EM.

## Reading the numbers

A strong paper EM means the model got every candidate of most questions right, including the no's. Pair-level accuracy can look high while EM stays low. Human 87.1 F1 is not a full-test ceiling. Random F1 is 36.2, not 50, because F1 is on the yes set. If a card reports "MC-TACO" without saying EM versus pair acc, treat the figure as incomparable.
