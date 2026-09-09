---
id: mimic_repsum
name: "MIMIC-III Report Summarization (lm-eval)"
aliases: []
page_kind: benchmark
category: domain
subcategory: "findings-to-impression summarization over MIMIC-III notes in lm-evaluation-harness"
status: active
summary: "lm-eval task mimic_repsum: write an Impression from Findings parsed out of a MIMIC-III hospital-course dump, scored with ROUGE, BLEU, BERTScore, BLEURT and RadGraph-F1."
measures: >
  mimic_repsum is EleutherAI lm-evaluation-harness's radiology-style
  findings-to-impression task. The YAML loads Hugging Face
  dmacres/mimiciii-hospitalcourse-meta (train 24,993, validation 5,356,
  test 5,356). For each row, utils.py searches extractive_notes_summ for
  FINDING and IMPRESSION headings and prompts "Given the findings: {}.
  Summarize the findings." The README calls this MIMIC-III Report
  Summarization and cites the 2016 MIMIC-III database paper, not a
  dedicated summarization paper. It is not MedHELM's mimic_rrs.
task_format: >
  generate_until. Prompt from parsed findings; target is the parsed
  impression. Decoding stops at a blank line; top_p=0.95. A sibling task
  mimic_repsum_perplexity scores perplexity on the same setup.
metric:
  name: "F1-Radgraph plus BLEU, ROUGE-1/2/L, BLEURT and BERTScore (nanmean)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The YAML lists seven metrics; none is declared the single official
    score. F1-Radgraph uses the radgraph package at reward_level=partial
    (README links Delbrouck et al., Patterns 2023). Rows with impression
    or prediction shorter than 5 characters are scored as NaN. No human
    baseline is given in the task files.
dataset:
  size: 5356
  size_note: >
    Hugging Face dmacres/mimiciii-hospitalcourse-meta: train 24,993,
    validation 5,356, test 5,356 (Hub API dataset_info, accessed
    2026-09-08). lm-eval binds training_split, validation_split and
    test_split to those three names. After heading parse, some test rows
    may be skipped as NaN; that filtered count was not measured. The
    dataset card has no licence field.
  url: "https://huggingface.co/datasets/dmacres/mimiciii-hospitalcourse-meta"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "train 24,993 / validation 5,356 / test 5,356 on the Hub; lm-eval uses all three names"
  public_test_set: true
publisher:
  org: "EleutherAI (harness task); Hugging Face user dmacres (dataset dump); MIMIC-III from MIT Lab for Computational Physiology"
  authors: []
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/mimic_repsum"
paper:
  title: "MIMIC-III, a freely accessible critical care database"
  arxiv: ""
  url: "https://www.nature.com/articles/sdata201635"
  year: 2016
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/mimic_repsum"
released: "2023-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - mimic_rrs
    - mimic_bhc
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public leaderboard for the lm-eval task was found. Do not read
    MedHELM mimic_rrs jury scores as this metric set.
contamination:
  risk: high
  note: >
    The Hugging Face dump is public (created 2023-11-15 on the Hub API)
    with note text and extractive summaries in the clear. MIMIC-III itself
    is a 2016 PhysioNet credentialed corpus; this mirror's redistribution
    rights are not stated on the card. Models trained after late 2023
    could have seen the Hub files.
harness:
  lm_eval: "mimic_repsum"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Sibling lm-eval task mimic_repsum_perplexity; YAML version 1.4"
tags:
  - biomedical
  - radiology
  - summarization
  - lm-eval
  - mimic-iii
sources:
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mimic_repsum/README.md"
    title: "lm-eval mimic_repsum README"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mimic_repsum/mimic_repsum.yaml"
    title: "lm-eval mimic_repsum.yaml (task name, dataset_path, metrics)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mimic_repsum/utils.py"
    title: "lm-eval mimic_repsum utils.py (FINDING/IMPRESSION parse)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/dmacres/mimiciii-hospitalcourse-meta"
    title: "dmacres/mimiciii-hospitalcourse-meta Hub API (split sizes; no licence tag)"
    accessed: "2026-09-08"
  - url: "https://www.nature.com/articles/sdata201635"
    title: "Johnson et al. 2016 MIMIC-III database paper (cited by the task README)"
    accessed: "2026-09-08"
  - url: "https://www.cell.com/patterns/fulltext/S2666-3899(23)00157-5"
    title: "RadGraph-F1 paper linked from the task README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-006"
---

## What it measures

lm-eval `mimic_repsum` asks a model to turn radiology Findings into an
Impression. The prompt is built by regex over the `extractive_notes_summ`
field of `dmacres/mimiciii-hospitalcourse-meta`: the harness finds
FINDING and IMPRESSION headings, feeds the findings span, and uses the
impression span as the reference. The Hub dataset is named as a hospital-
course collection; the task code is nonetheless a findings→impression
summarizer, which is why the README's title is MIMIC-III Report
Summarization.

This is not [mimic_rrs](mimic_rrs.md). MedHELM loads Chen et al.'s
tokenized MIMIC-RRS files and scores an LLM jury. It is also not
[mimic_bhc](mimic_bhc.md), which writes Brief Hospital Course from
MIMIC-IV discharge notes.

## How it is scored

Default `mimic_repsum` is `generate_until` with `until: ["\n\n"]` and
`top_p: 0.95`. `process_results` computes BLEU, ROUGE-1/2/L, BLEURT
(bleurt-base-512), BERTScore F1, and F1-Radgraph (partial reward).
Aggregations are `nanmean`. Very short targets or predictions become
NaN rather than zero. `mimic_repsum_perplexity` is a separate task on
the same documents. There is no single headline metric in the YAML.

## Dataset and licence

Hub `dataset_info` gives 24,993 / 5,356 / 5,356 rows. Features include
subject_id, hadm_id, target_text, extractive_notes_summ, n_notes and a
list of notes. The card has no licence; tags do not include a licence
either. Underlying MIMIC-III is PhysioNet credentialed (Johnson et al.,
Scientific Data 2016). Whether the dmacres dump is a permitted public
redistribution is not established from the card.

## Who publishes it

The runnable evaluation is EleutherAI's harness task (YAML metadata
version 1.4). The dataset repository is Hugging Face user `dmacres`
(created 15 November 2023). The README's bibliographic citation is the
MIMIC-III database paper, not Chen et al. 2023 and not a dmacres paper —
no separate summarization paper for this packaging was found.

## Lineage

Do not fold this id into [mimic_rrs](mimic_rrs.md) or
[mimic_bhc](mimic_bhc.md). Shared ancestry is MIMIC clinical text.
The closest task shape is findings→impression, which MIMIC-RRS also
uses, with different files, splits, licence and metrics.

## Saturation and contamination

Saturation unknown. Contamination is high for the Hub dump: note text
is public there. That is the opposite access model from MedHELM's gated
PhysioNet scenarios.

## How to run it

`lm_eval --tasks mimic_repsum` (and optionally `mimic_repsum_perplexity`).
Install the extra metrics the utils import (`evaluate`, `bert-score`,
`rouge_score`, `radgraph`, BLEURT from Google's repo). Compare only to
other lm-eval runs of this YAML version.

## Reading the numbers

A high ROUGE or RadGraph-F1 here means the model's impression overlapped
the parsed gold span on this Hub dump. It does not measure MedHELM jury
quality, does not use Chen et al.'s official MIMIC-RRS splits, and the
heading parser can feed messy spans when FINDING/IMPRESSION order
varies. Prefer [mimic_rrs](mimic_rrs.md) when the claim is about
MIMIC-RRS, and treat this score as harness-specific.
