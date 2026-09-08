---
id: mmlu_redux
name: "MMLU-Redux"
aliases:
  - "MMLU Redux"
  - "Are We Done with MMLU?"
page_kind: benchmark
category: knowledge
subcategory: "manually re-annotated MMLU subset (label-error audit)"
status: active
summary: "A re-annotated slice of MMLU (5,700 items across 57 subjects in the 2.0 release) that tags label errors instead of adding new questions."
measures: >
  MMLU-Redux keeps Hendrycks MMLU questions and four options, then has experts tag each item with
  an error_type (including "ok") and, when needed, a corrected answer. The evaluated skill is
  still four-option academic/professional knowledge, but the score is meant to be read on items
  the annotators judged valid. English text. It is not a new exam like [MMLU-Pro](mmlu_pro.md) or
  the contamination-controlled [mmlu_cf](mmlu_cf.md).
task_format: >
  Four-option MCQ. lm-evaluation-harness group `mmlu_redux_generative` uses generate_until with
  regex `([ABCD])`, exact_match, dataset_path `fxmarty/mmlu-redux-2.0-ok`. Version 4 (PR 3410)
  keeps rows with error_type="ok" and drops 370 of 5,700 (~6.5%). Per-subject tasks are
  named `mmlu_redux_<subject>_generative`. An earlier Hugging Face dump,
  edinburgh-dawg/mmlu-redux, is 30 subjects × 100 = 3,000 rows from the first paper draft.
metric:
  name: accuracy (exact match on A–D)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    25% is four-option chance. No human-solver baseline was given in the sources opened here.
    The paper's headline is not a model leaderboard but an error-rate estimate: 6.49% of MMLU
    questions, with 57% of analysed Virology items tagged erroneous (including 33% wrong
    ground truth).
dataset:
  size: 5700
  size_note: >
    Paper v3 (arXiv HTML 10 Jan 2025) and edinburgh-dawg/mmlu-redux-2.0 (datasets-server): 57
    subjects × 100 = 5,700 test rows, CC-BY-4.0. The first public dump edinburgh-dawg/mmlu-redux
    is 30 configs × 100 = 3,000, matching earlier ar5iv wording. lm-eval v4 evaluates
    fxmarty/mmlu-redux-2.0-ok (datasets-server: 5,330 rows = 5,700 − 370). Each row still carries the original
    MMLU choices plus error_type, source, correct_answer, potential_reason.
  url: "https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "test only (100 per subject config); no separate validation split on the Hub cards"
  public_test_set: true
publisher:
  org: "University of Edinburgh (with Sapienza, University of Bari, University College London and co-authors)"
  authors:
    - "Aryo Pradipta Gema"
    - "Joshua Ong Jun Leang"
    - "Giwon Hong"
    - "Alessio Devoto"
    - "Alberto Carlo Maria Mancino"
    - "Rohit Saxena"
    - "Xuanli He"
    - "Yu Zhao"
    - "Xiaotang Du"
    - "Mohammad Reza Ghasemi Madani"
    - "Claire Barale"
    - "Robert McHardy"
    - "Joshua Harris"
    - "Jean Kaddour"
    - "Emile van Krieken"
    - "Pasquale Minervini"
  url: "https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0"
paper:
  title: "Are We Done with MMLU?"
  arxiv: "2406.04127"
  url: "https://arxiv.org/abs/2406.04127"
  year: 2024
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0"
released: "2024-06"
last_updated: "2025-02"
lineage:
  family: mmlu
  predecessor: mmlu
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No official model leaderboard was opened here. Because the items are a subset of already
    saturated MMLU, frontier scores on the "ok" slice are expected to sit high; the authors'
    claim is that uncorrected MMLU numbers mis-rank models, not that this set restores headroom.
contamination:
  risk: high
  note: >
    Every question is a public MMLU test item (public since 2020) plus a public error tag.
    Re-annotation does not withdraw the original answer key. The 2.0 dump and the lm-eval
    filtered copy are fully downloadable.
harness:
  lm_eval: "mmlu_redux_generative"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Harness directory is lm_eval/tasks/mmlu-redux (hyphen), not mmlu_redux. Dataset in YAML: fxmarty/mmlu-redux-2.0-ok. Group also rolls up mmlu_redux_{stem,other,social_sciences,humanities}_generative. A Spanish port exists at lm_eval/tasks/mmlu-redux-spanish (no page here)."
tags:
  - knowledge
  - multiple-choice
  - label-quality
  - four-option
  - mmlu
sources:
  - url: "https://arxiv.org/abs/2406.04127"
    title: "Are We Done with MMLU? abs (Gema et al.; 5,700 items, 6.49% error estimate)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2406.04127"
    title: "Are We Done with MMLU? HTML v3 (57×100, CC BY 4.0, error taxonomy)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux/raw/main/README.md"
    title: "edinburgh-dawg/mmlu-redux card (30×100 first release)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0/raw/main/README.md"
    title: "edinburgh-dawg/mmlu-redux-2.0 card (57 subjects)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=edinburgh-dawg/mmlu-redux"
    title: "datasets-server size mmlu-redux (3,000 rows, 30 configs)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=edinburgh-dawg/mmlu-redux-2.0"
    title: "datasets-server size mmlu-redux-2.0 (5,700 rows, 57 configs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mmlu-redux/generative/README.md"
    title: "lm-eval mmlu-redux generative README (group names; v4 filters 370/5700)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mmlu-redux/generative/_mmlu.yaml"
    title: "lm-eval group mmlu_redux_generative"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mmlu-redux/generative/_default_template_yaml"
    title: "lm-eval template (fxmarty/mmlu-redux-2.0-ok, generate_until)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux/raw/main/LICENSE"
    title: "CC BY 4.0 licence text on edinburgh-dawg/mmlu-redux"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=fxmarty/mmlu-redux-2.0-ok"
    title: "datasets-server size fxmarty/mmlu-redux-2.0-ok (5,330 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mmlu-redux/generative/mmlu_anatomy.yaml"
    title: "lm-eval mmlu_anatomy.yaml (task: mmlu_redux_anatomy_generative)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-012 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-012"
---

## What it measures

MMLU-Redux re-reads [MMLU](mmlu.md) rather than replacing it. Annotators keep the original question and four choices, then mark whether the labelled answer is usable. The model still picks A–D. The point is to stop wrong keys, ambiguous stems and multiple-true options from looking like model failures. English. Virology is the warning example: 57% of analysed items in that subject were tagged as some error. Figure 3's caption splits that as 33% wrong ground truth, 4% multiple-correct, and 14% unclear; §3.1 later says 30% wrong ground truth and 15% unclear.

## How it is scored

Accuracy is four-option exact match. lm-eval's current group `mmlu_redux_generative` is generative letter extraction, not the original MMLU log-likelihood scorer, so it is not a drop-in MMLU number. Version 4 drops items whose `error_type` is not `ok` (README: 370 of 5,700). Aggregates are size-weighted across subjects and across the usual MMLU buckets (stem, other, social sciences, humanities). State whether a reported run used the 30-subject 3,000-item dump, the 57-subject 5,700-item dump, or the filtered "ok" slice.

## Dataset and licence

Paper v3 and `edinburgh-dawg/mmlu-redux-2.0` hold 100 items in each of MMLU's 57 subjects (5,700). The first Hub dataset, `edinburgh-dawg/mmlu-redux`, is 30 subjects (3,000); that matches an older HTML wording of the paper. Both cards use CC-BY-4.0. Columns include error_type, source, correct_answer and potential_reason. There is no held-out split.

## Who publishes it

Aryo Pradipta Gema and co-authors at Edinburgh, Sapienza, Bari, UCL and elsewhere posted "Are We Done with MMLU?" as arXiv:2406.04127 on 6 Jun 2024 (v3 10 Jan 2025). The Hub orgs are `edinburgh-dawg`. Hugging Face tags also mention arXiv:2502.03461 ("Do Large Language Model Benchmarks Test Reliability?"), a different reliability paper, not this dataset's definition.

## Lineage

Predecessor is MMLU. [MMLU-Pro](mmlu_pro.md) writes harder ten-option items; [mmlu_cf](mmlu_cf.md) hides a new test set. MMLU-Redux does neither: it audits the old questions. lm-eval also ships `mmlu-redux-spanish`, which has no page here. This id is not an alias of `mmlu`.

## Saturation and contamination

No current top score was read. The "ok" slice is still public MMLU text, so contamination risk is high in the same sense as MMLU, and frontier models are likely bunched. The useful signal is the gap versus uncorrected MMLU and the per-subject error mix, not a new ceiling.

## How to run it

In EleutherAI lm-evaluation-harness the runnable group is `mmlu_redux_generative` (directory `lm_eval/tasks/mmlu-redux`). YAML `dataset_path` is `fxmarty/mmlu-redux-2.0-ok`. Per-subject files are named `mmlu_<subject>.yaml`; the runnable `task:` field is `mmlu_redux_<subject>_generative` (anatomy YAML checked). The census slug `mmlu_redux` is that group, not a second dataset. Prompting is generate-until with a "letter only" instruction, which will not match log-likelihood MMLU.

## Reading the numbers

A high MMLU-Redux score on `error_type=ok` items means the model matches the repaired key on a cleaned MMLU sample. It does not prove the original 14k MMLU test is trustworthy, and it does not measure contamination the way MMLU-CF does. Always say which dump and whether non-ok rows were dropped: 3,000, 5,700 and 5,330 "ok" are three different denominators. Check Virology and other high-error subjects before trusting an aggregate that still includes them unfiltered.
