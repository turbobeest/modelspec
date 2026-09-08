---
id: fewclue
name: "FewCLUE (Chinese Few-shot Learning Evaluation Benchmark)"
aliases:
  - "Few-shot CLUE"
  - "Chinese Few-shot Learning Evaluation Benchmark"
page_kind: family
category: composite
subcategory: "Chinese few-shot NLU suite: sentiment, matching, classification, cloze and coreference tasks"
status: unknown
summary: "A Chinese few-shot NLU benchmark: nine tasks learned from 8-32 labelled examples per class across five parallel splits, so a score measures few-shot learning rather than full-data task competence."
measures: >
  FewCLUE bundles nine separate Chinese NLU tasks -- sentiment classification, long- and short-text
  topic classification, natural language inference, dialogue-intent matching, idiom cloze, scientific
  keyword verification, and pronoun coreference -- under one shared constraint: every task is learned
  from a handful of labelled examples (8 to 32 per class, depending on the task's number of labels)
  rather than a full-size training set. Five independent training/validation splits are provided per
  task specifically to average out the instability that small samples cause, plus up to 20,000
  unlabelled examples per task for semi-supervised research. A FewCLUE score measures how much a
  model can learn from a handful of examples, which is a different quantity from a full-data score on
  the same underlying task.
task_format: >
  Nine tasks: five single-sentence or sentence-pair classification tasks (2, 3, 15, 67 or 119
  classes), one dialogue short-text matching task, and two reading-comprehension/cloze tasks (idiom
  cloze, keyword verification), all graded by accuracy against one correct label. Training draws 8-32
  labelled examples per class from one of five parallel splits (train_0..train_4); a merged split and
  up to 20,000 unlabelled examples per task are also provided, unused for the scored metric.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 82.5
  baseline_note: >
    No single random-guess rate applies across tasks with such different label counts (2 to 119
    classes); the paper's own naive "majority class" baseline ranges from 0.8% (IFLYTEK, 119 classes)
    to 50% (the five roughly-balanced binary/ternary tasks) -- see each subset page for its own
    figure. 82.5% is the paper's aggregate human score (recomputed here as the mean of its nine
    per-task human scores, which lands on 82.49-82.50; the paper's own prose separately rounds this to
    82.40% elsewhere in the same document, a minor internal inconsistency in the source).
dataset:
  size: 16251
  size_note: >
    Sum of the nine tasks' labelled public test sets (test_public.json), the split most third-party
    harnesses score against: from 610 (EPRSTMT) to 2,828 (CSL) per task. Training data is the actual
    point of the benchmark and is deliberately tiny: 32 examples total for the five tasks with three
    or fewer labels (EPRSTMT, OCNLI, BUSTM, CSL, CLUEWSC), 240 for TNEWS (16/class x 15 classes), 536
    for CSLDCP and 928 for IFLYTEK (approx. 8/class), and 42 for CHID (6 examples for each of 7 blank
    positions). Every task repeats its training/validation pair across five independent splits
    (train_0..train_4, dev_0..dev_4) plus a deduplicated train_few_all/dev_few_all merge, and
    separately ships up to 20,000 unlabelled examples per task (not used for the accuracy metric) and
    a private, unlabelled test set (test.json) used only for the original 2021 leaderboard. Figures
    are from the paper's Table 1, cross-checked against the GitHub README's own statistics table
    (identical).
  url: "https://github.com/CLUEbenchmark/FewCLUE"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train_0..train_4 + train_few_all; dev_0..dev_4 + dev_few_all; test_public (16,251 total, labelled, used for scoring); test (private, unlabelled, original leaderboard only); unlabeled (up to 20,000/task, not scored)"
  public_test_set: true
publisher:
  org: "CLUE team"
  authors:
    - "Liang Xu"
    - "Xiaojing Lu"
    - "Chenyang Yuan"
    - "Xuanwei Zhang"
    - "Huilin Xu"
    - "Hu Yuan"
    - "Guoao Wei"
    - "Xiang Pan"
    - "Xin Tian"
    - "Libo Qin"
    - "Hu Hai"
  url: "https://github.com/CLUEbenchmark/FewCLUE"
paper:
  title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark"
  arxiv: "2107.07498"
  url: "https://arxiv.org/abs/2107.07498"
  year: 2021
leaderboard_url: "https://www.cluebenchmarks.com/fewclue.html"
repo_url: "https://github.com/CLUEbenchmark/FewCLUE"
released: "2021-04"
last_updated: "2022-09"
lineage:
  family: ""
  predecessor: clue
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 59.91
  as_of: "2021-09"
  note: >
    The paper's own baseline sweep found its best method (P-tuning on RoBERTa) scoring 59.91 -- the
    unweighted mean of its nine per-task accuracies -- against a human score of 82.5, roughly 23
    points of headroom, but only for 2021-era BERT/RoBERTa/ERNIE/GPT-scale models under classic
    prompt-tuning methods (PET, P-tuning, ADAPET, LM-BFF, EFL). No model card in this repository
    reports FewCLUE and the public leaderboard shows no visible activity beyond the original 2021
    launch notice, so whether current frontier models have closed this gap is not established.
contamination:
  risk: high
  note: >
    The labelled public test set (test_public.json, 16,251 items total) has sat unchanged in the
    open GitHub repository since 2021 and is what OpenCompass and most third-party reproductions
    score against. The genuinely held-out split (test.json) was used only for the original 2021
    leaderboard's private grading and is not what a third-party harness run today typically uses.
harness:
  lm_eval: ""
  helm: ""
  opencompass: "Per-task FewCLUE_<task> dataset configs, confirmed for bustm, chid, cluewsc, csl, eprstmt, ocnli_fc and tnews; no combined umbrella task name found, and csldcp/iflytek are absent from the registry"
  bigbench: ""
  other: ""
tags:
  - chinese
  - few-shot
  - multi-task
  - composite
  - classification
  - nli
sources:
  - url: "https://arxiv.org/abs/2107.07498"
    title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark (Xu et al., arXiv:2107.07498)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/FewCLUE"
    title: "CLUEbenchmark/FewCLUE GitHub repository (README, task descriptions, dataset statistics, licence section)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/CLUEbenchmark/FewCLUE"
    title: "CLUEbenchmark/FewCLUE repository metadata via the GitHub REST API (creation/push dates, licence field)"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/fewclue.html"
    title: "FewCLUE leaderboard, cluebenchmarks.com"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets"
    title: "OpenCompass datasets config directory (FewCLUE_* task configs and absence of csldcp/iflytek)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/clue"
    title: "clue dataset card, Hugging Face API (full-size CLUE benchmark mirror, for Lineage comparison)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets?search=fewclue"
    title: "Hugging Face dataset search results for \"fewclue\" (no official CLUE-team dataset card found)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/EleutherAI/lm-evaluation-harness/contents/lm_eval/tasks"
    title: "lm-evaluation-harness tasks directory listing via the GitHub REST API (no clue/fewclue task)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/stanford-crfm/helm/contents/src/helm/benchmark/scenarios"
    title: "HELM scenarios directory listing via the GitHub REST API (no clue/fewclue scenario)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice B"
---

## What it measures

FewCLUE does not test one skill; it bundles nine Chinese NLU tasks -- sentiment classification,
topic classification, natural language inference, dialogue-intent matching, idiom cloze, scientific
keyword verification, and pronoun coreference -- under one shared constraint: every task is learned
from a handful of labelled examples, not the thousands a standard supervised split gives. A FewCLUE
score answers "how much can this model learn from 32 labelled reviews," not "can this model do
sentiment analysis" -- the same task on CLUE's full-size training set answers a different question,
which is why FewCLUE and CLUE keep separate ids in this wiki for the six tasks they share (Lineage).

The protocol has three deliberate parts. Sampling is stingy and label-count-aware: three or fewer
classes gets 32 training examples total (five of the nine tasks); 4-20 classes gets 16 per class
(TNEWS); more than 20 gets 8 per class (CSLDCP, IFLYTEK); CHID, sampled by answer position rather
than semantic class, gets six examples per position, 42 total. Because a set this small causes
"severe fluctuation" in results -- the paper's own TNEWS ablation found accuracy swinging several
points across otherwise-identical resamplings -- every task ships five independent train/dev splits
(train_0..train_4) plus a deduplicated merge, so a score can be averaged across draws instead of
resting on one lucky split. Each task also carries up to 20,000 unlabelled examples, unused in the
scored metric but there for semi-supervised research.

## How it is scored

All nine tasks are scored by accuracy against a labelled public test set (test_public.json), one
label per item, no partial credit. Each method's headline "Score" is the unweighted mean of the nine
per-task accuracies -- confirmed here by recomputing it: P-tuning-on-RoBERTa's reported 59.91 is
exactly that mean. A second, larger test set was held out unlabelled, purely for the original
closed-leaderboard contest (NLPCC 2021 Task 2); most third-party evaluations, including OpenCompass,
score against the labelled set instead, which matters for contamination (see below).

Baselines span a majority-class heuristic (0.8% to 50%, depending on the task's label count) through
five prompt-based few-shot methods (PET, ADAPET, LM-BFF, P-tuning, EFL) compared against plain
fine-tuning, zero-shot prompting, and a trained human evaluation (82.5% overall, annotators trained
the same way SuperGLUE trains its raters). The best method tested, P-tuning on RoBERTa, reached
59.91 -- about 23 points below the human figure -- with EFL notably stronger specifically on the two
sentence-pair tasks (OCNLI, BUSTM), and CHID behaving close to zero-shot learning under PET because
its native format is already cloze-shaped.

## Dataset and licence

The labelled public test set totals 16,251 questions across the nine tasks, from 610 (EPRSTMT) to
2,828 (CSL); training data follows the small, label-count-scaled sizes set out above, repeated over
five splits plus a merged train_few_all/dev_few_all. Six tasks (TNEWS, CHID, IFLYTEK, OCNLI, CSL,
CLUEWSC) are existing CLUE-benchmark tasks resampled into this few-shot shape, in places with fresh
annotation; three (EPRSTMT, CSLDCP, BUSTM) are new, built from e-commerce reviews, academic abstracts
and a voice assistant's intent-matching logs respectively. All text is Chinese.

No licence is published for the data: the GitHub README marks its licence section as still being
written, and the repository (confirmed via the GitHub API) has no LICENSE file -- treat the licence
as not established. No official Hugging Face dataset card exists either (only a stale 2022 community
mirror), so this page treats the GitHub repository as authoritative.

## Who publishes it

FewCLUE was built by the CLUE team -- Liang Xu, Xiaojing Lu, Chenyang Yuan, Xuanwei Zhang, Huilin Xu,
Hu Yuan, Guoao Wei, Xiang Pan, Xin Tian, Libo Qin and Hu Hai -- released as arXiv:2107.07498
(submitted July 2021, revised September 2021) and used as the shared task for NLPCC 2021's few-shot
learning contest. The GitHub repository CLUEbenchmark/FewCLUE is the reference implementation and
data host; a leaderboard is hosted at cluebenchmarks.com/fewclue.html.

## Lineage

FewCLUE's parent project is CLUE (`clue` in this wiki): six of its nine tasks -- TNEWS, CHID,
IFLYTEK, OCNLI, CSL, CLUEWSC -- are CLUE tasks resampled into few-shot splits; full-size OCNLI is
tracked separately here as `clue_ocnli`. The other three (EPRSTMT, CSLDCP, BUSTM) are new to
FewCLUE. This page's seven subset pages (`fewclue_bustm`, `fewclue_chid`, `fewclue_cluewsc`,
`fewclue_csl`, `fewclue_eprstmt`, `fewclue_tnews`, `fewclue_ocnli_fc`) match exactly the seven of
nine tasks OpenCompass implements as harness configs; `fewclue_csldcp` and `fewclue_iflytek` have
neither a page here nor a confirmed OpenCompass config. No confirmed successor exists: the
repository has had no code changes since September 2022, and Chinese LLM evaluation has since
largely moved to broad knowledge-exam suites such as `ceval` and `cmmlu` -- a different question
(breadth of static knowledge) from FewCLUE's own (how much a model learns from a handful of
examples).

## Saturation and contamination

Saturation status is not established for current models: no model card in this repository reports
FewCLUE, and the cluebenchmarks.com leaderboard shows no visible activity beyond the initial 2021
launch notice. The roughly 23-point gap between the best method and human performance (see How it is
scored) describes only 2021-era BERT/RoBERTa/ERNIE/GPT-scale models under classic prompt-tuning;
whether it still holds for current frontier LLMs is unknown.

Contamination risk is high for the numbers actually in circulation: the labelled public test set has
sat unchanged in the open GitHub repository since 2021 and is what OpenCompass and most external
reproductions score against; the genuinely held-out split mattered only for the original leaderboard's
private grading.

## How to run it

OpenCompass ships seven of the nine tasks as individual `FewCLUE_<task>` dataset configs (confirmed
for bustm, chid, cluewsc, csl, eprstmt, ocnli_fc and tnews; csldcp and iflytek are absent), each
scored with an accuracy evaluator against test_public.json; no task-specific entry was found in
lm-evaluation-harness or HELM. The GitHub repository itself is the reference implementation, with
baseline scripts for fine-tuning, PET, P-tuning, ADAPET, LM-BFF, EFL and zero-shot prompting under
`baselines/`, keyed by task and split. Because five splits exist per task, treat a single-split score
as noisy -- the paper's own ablation shows one small split can swing a result by several points, and
reporters are not guaranteed to average the same way.

## Reading the numbers

A FewCLUE score answers "how much can this model learn from a handful of examples," not "how good is
this model at the task" -- the same nine tasks at full CLUE scale produce different numbers. A high
score suggests strong few-shot adaptation, not necessarily strong task competence on its own; the
paper's own baselines never got within 20 points of human performance under any method tested.
Because the test set is small and public since 2021, treat a modern score with caution on both
variance (multiple splits, not one) and contamination.
