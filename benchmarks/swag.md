---
id: swag
name: "SWAG (Situations With Adversarial Generations)"
aliases:
  - "Situations With Adversarial Generations"
page_kind: benchmark
category: reasoning
subcategory: "grounded commonsense inference: predicting the next event in a video-caption situation"
status: saturated
summary: "113k four-way multiple-choice questions asking which of four captions plausibly continues a video-derived situation; HellaSwag's direct predecessor."
measures: >
  SWAG tests grounded commonsense inference: given a sentence describing part of a real-world situation
  (drawn from video captioning corpora), a model must pick which of four candidate sentences most
  plausibly follows. One ending is the true next caption; the other three are adversarially selected
  machine-generated distractors designed to look plausible on the surface while being wrong. The source
  situations come from ActivityNet Captions (short YouTube activity clips) and the Large Scale Movie
  Description Challenge (LSMDC, movie audio-description captions), so the task is English text only,
  though it is grounded in described physical and social activity rather than abstract text.
task_format: "Four-way multiple choice: given a context sentence, select the most plausible of four candidate continuations."
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Random guessing on the four-way task scores 25%. The paper's own headline result was that
    then-state-of-the-art models (ESIM+ELMo) reached about 59% while human annotators who validated the
    dataset agreed with the gold label roughly 88% of the time in that validation exercise; this page did
    not independently re-derive a single "human baseline" figure comparable across sources, so
    `human_baseline` is left empty rather than repeating a secondhand number.
dataset:
  size: 113000
  size_note: >
    The paper and dataset card both state approximately 113k multiple-choice questions in total. The
    Hugging Face `allenai/swag` "regular" configuration splits this as 73,546 train, 20,006 validation,
    and 20,005 test rows (totalling ~113.5k); the official GitHub repository additionally distributes
    "full" variants of the train/validation files that keep the ordinal annotation scores and video/source
    metadata behind each of the four endings, not only the regular 4-choice CSVs used for modelling.
  url: "https://huggingface.co/datasets/allenai/swag"
  license: "MIT (per the rowanz/swagaf GitHub repository's LICENSE file); the Hugging Face dataset card lists licence as unknown"
  languages:
    - en
  modalities:
    - text
  splits: "train 73,546 / validation 20,006 / test 20,005 (test labels withheld)"
  public_test_set: false
publisher:
  org: "Paul G. Allen School of Computer Science & Engineering, University of Washington"
  authors:
    - "Rowan Zellers"
    - "Yonatan Bisk"
    - "Roy Schwartz"
    - "Yejin Choi"
  url: "https://rowanzellers.com/swag/"
paper:
  title: "SWAG: A Large-Scale Adversarial Dataset for Grounded Commonsense Inference"
  arxiv: "1808.05326"
  url: "https://arxiv.org/abs/1808.05326"
  year: 2018
leaderboard_url: "https://rowanzellers.com/swag/"
repo_url: "https://github.com/rowanz/swagaf"
released: "2018-08"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - hellaswag
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    SWAG was retired by its own authors' next paper: HellaSwag (2019) reports that "BERT soon reached
    over 86%, almost human-level performance" on SWAG. The original BERT paper (Devlin et al. 2018)
    gives the specific figure behind that claim: BERT-Large at 86.6% dev / 86.3% test on SWAG, reached
    within months of SWAG's August 2018 release. That closes in on the paper's own ~88% human-agreement
    figure and eliminates the difficulty gap the adversarial filtering was built to create. That is the
    basis for treating SWAG as saturated; no independent current leaderboard or recent top score was
    found in the sources opened for this page, since public benchmarking attention moved to HellaSwag.
contamination:
  risk: high
  note: >
    Train and validation labels have been public since 2018 and are widely mirrored (GitHub, Hugging
    Face). Test labels are withheld in the official release, but most published SWAG numbers, including
    lm-evaluation-harness's, are scored on the validation split, whose labels have been public for years.
harness:
  lm_eval: "swag"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - commonsense
  - multiple-choice
  - adversarial-filtering
  - nli
  - saturated
sources:
  - url: "https://arxiv.org/abs/1808.05326"
    title: "SWAG: A Large-Scale Adversarial Dataset for Grounded Commonsense Inference"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1808.05326"
    title: "SWAG (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/rowanz/swagaf"
    title: "rowanz/swagaf repository"
    accessed: "2026-09-08"
  - url: "https://github.com/rowanz/swagaf/tree/master/data"
    title: "rowanz/swagaf data directory (train/val/test CSVs, full variants)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/rowanz/swagaf/license"
    title: "GitHub API: rowanz/swagaf license detection (MIT)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/swag"
    title: "allenai/swag dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/swag"
    title: "allenai/swag dataset API, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/swag/swag.yaml"
    title: "lm-evaluation-harness swag task YAML"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1905.07830"
    title: "HellaSwag: Can a Machine Really Finish Your Sentence? (Zellers et al., arXiv:1905.07830), states BERT 'soon reached over 86%' on SWAG"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1810.04805"
    title: "BERT (Devlin et al., arXiv:1810.04805), Table 4: BERT-Large 86.6% dev / 86.3% test on SWAG"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-006"
---

## What it measures

SWAG tests grounded commonsense inference: given a sentence describing part of a real-world situation, a model must choose which of four candidate sentences most plausibly follows. The situations are drawn from two video-captioning sources -- ActivityNet Captions (short clips of everyday activities) and the Large Scale Movie Description Challenge (audio-description captions from movies) -- so items are physically and socially grounded rather than abstract trivia. One ending is the true next caption; the other three are machine-generated distractors chosen by an adversarial filtering procedure to look plausible without being correct.

The task is entirely English text, framed as a next-event-prediction problem rather than open-ended generation, so a model only has to rank four given options rather than produce free text.

## How it is scored

Each item is four-way multiple choice, so random guessing scores 25%. The authors built the distractors with an "Adversarial Filtering" (AF) procedure: an ensemble of stylistic classifiers is trained to distinguish generated endings from the real one, and endings that fool the ensemble are kept, iteratively raising the difficulty for machine classifiers while (the authors argue) staying easy for humans. To keep the surviving distractors natural, the authors oversampled a large pool of candidate continuations from contemporary language models before filtering. The paper's own validation exercise found human annotators agreed with the gold label about 88% of the time; this page does not repeat that figure as a single authoritative "human baseline" since later papers describe it differently, so `metric.human_baseline` is left empty here.

## Dataset and licence

The dataset totals approximately 113,000 examples, released by Hugging Face's `allenai/swag` "regular" configuration as 73,546 train, 20,006 validation, and 20,005 test rows. The official GitHub repository (`rowanz/swagaf`) also ships "full" versions of the train and validation files that retain each ending's underlying video source and ordinal human-agreement scores, in addition to the regular 4-choice CSVs used for standard modelling. GitHub's own license detection reports MIT for the repository; the Hugging Face dataset card, by contrast, lists licence as unknown, so this page records the repository's stated licence and flags the disagreement. Test-set labels are withheld in the official release.

## Who publishes it

SWAG is by Rowan Zellers, Yonatan Bisk, Roy Schwartz, and Yejin Choi, at the Paul G. Allen School of Computer Science & Engineering, University of Washington, published as "SWAG: A Large-Scale Adversarial Dataset for Grounded Commonsense Inference" at EMNLP 2018. The authors continue to host the reference repository and project page at rowanzellers.com/swag.

## Lineage

SWAG has no tracked predecessor in this repository. Its direct successor is HellaSwag (`hellaswag`), built by an overlapping author group after BERT "soon reached over 86%" on SWAG (the original BERT paper gives 86.6% dev / 86.3% test for BERT-Large, reached within months of SWAG's release) -- language models had caught up to the adversarial filtering faster than expected, so HellaSwag reran the same idea with a stronger generator and discriminator to reopen a difficulty gap. No other successor or variant id is tracked here.

## Saturation and contamination

SWAG is saturated by its own successor's account: HellaSwag's paper reports that "BERT soon reached over 86%" on SWAG (the original BERT paper's own table gives BERT-Large at 86.6% dev / 86.3% test), closing most of the gap to the human-agreement range found during dataset validation and eliminating the separation the adversarial filtering was designed to produce. That is the direct evidence this page uses for `status: saturated`; no current leaderboard or recent top score was found in the sources consulted, since public attention and reporting moved to HellaSwag afterward. Contamination risk is high: train and validation labels have been public and widely mirrored since 2018, and most published SWAG numbers, including lm-evaluation-harness's own, are scored on the validation split rather than the held-out test set.

## How to run it

lm-evaluation-harness implements the task as `swag`, loading `allenai/swag` (config `regular`) with `output_type: multiple_choice`, scoring by both raw accuracy (`acc`) and length-normalised accuracy (`acc_norm`) over the four `ending0`-`ending3` fields, trained on `train` and evaluated on `validation` (there is no configured test split, consistent with the official test labels being withheld). OpenCompass, HELM, and BIG-bench task lists were checked in the sources opened for this page and none showed a SWAG scenario. The authors' own repository provides the adversarial-filtering code and reference data files for anyone re-deriving the dataset.

## Reading the numbers

A high SWAG score today mostly confirms that a model handles physically grounded, video-caption-style commonsense about as well as this particular adversarial-filtering pass could make hard, which by the late 2010s already described strong transformer encoders. Because BERT-Large reached the high 80s not long after release, SWAG stopped separating capable models well before the current generation, and no model card in this repository is expected to lean on it as a meaningful differentiator. Treat SWAG as a historical checkpoint in the commonsense-benchmark lineage rather than a live signal, and prefer its successor HellaSwag, which is still occasionally reported, when comparing current models on the same underlying task design.
