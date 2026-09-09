---
id: mts_dialog
name: "MTS-Dialog (lm-eval)"
aliases:
  - "MTS-Dialog"
  - "MTS_Dialogue-Clinical_Note"
  - "mts_dialog_perplexity"
page_kind: benchmark
category: domain
subcategory: "lm-eval clinical-note section generation from short doctor-patient dialogue"
status: active
summary: "lm-eval wrap of MTS-Dialog: write an English clinical-note section from a short doctor-patient dialogue, scored with overlap metrics."
measures: >
  mts_dialog is EleutherAI lm-evaluation-harness's generation wrap of
  MTS-Dialog, a 2023 collection of short English doctor-patient
  dialogues paired with clinical-note sections. The model reads the
  dialogue and must write the corresponding section text. The original
  notes use twenty normalised headers (chief complaint, history of
  present illness, and so on). The Hugging Face mirror that lm-eval
  loads reformats the note as Symptoms / Diagnosis / History of Patient
  / Plan of Action. This is section-level note writing, not full-visit
  notes as in [aci_bench](aci_bench.md).
task_format: >
  generate_until, stop at a blank line. doc_to_text is the dialogue;
  doc_to_target is section_text. YAML instruction: extract a note that
  summarises the dialog. training_split, validation_split, and
  test_split are all `train` on har1/MTS_Dialogue-Clinical_Note.
  Companion task mts_dialog_perplexity uses loglikelihood_rolling.
metric:
  name: "BLEU, ROUGE-1/2/L, BERTScore, BLEURT (nanmean); perplexity on the companion task"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    utils.py loads Hugging Face evaluate BLEU, ROUGE, bertscore (English
    F1), and BLEURT-base-512. If prediction or reference is shorter than
    five characters, every overlap metric is NaN. BLEU 0.0 is replaced
    with 1e-5 to keep stderr defined. Perplexity task metrics are
    word_perplexity, byte_perplexity, and bits_per_byte (lower is
    better). The EACL 2023 paper also reports fact-based human scores
    and their correlation with ROUGE/BERTScore/BLEURT; those human
    figures are not a single harness baseline.
dataset:
  size: 1301
  size_note: >
    datasets-server on har1/MTS_Dialogue-Clinical_Note: 1,301 train
    rows, four columns. That matches 1,201 training pairs plus 100
    validation pairs from the original README, with the two 200-item
    test sets omitted. Original abachaa/MTS-Dialog: 1,700 pairs total
    (1,201 train, 100 valid, 200 MEDIQA-Chat 2023 Task A test, 200
    MEDIQA-Sum 2023 Task A/B test). Augmented train set: 3,603
    back-translated pairs; lm-eval does not load it.
  url: "https://github.com/abachaa/MTS-Dialog"
  license: "CC-BY-4.0 on abachaa/MTS-Dialog; MIT on Hugging Face har1/MTS_Dialogue-Clinical_Note"
  languages:
    - en
  modalities:
    - text
  splits: "lm-eval uses the HF train split for train/validation/test; original GitHub keeps train/valid/test1/test2"
  public_test_set: true
publisher:
  org: "Microsoft (original dataset); EleutherAI lm-evaluation-harness wrap; Hugging Face mirror by har1"
  authors:
    - "Asma Ben Abacha"
    - "Wen-wai Yim"
    - "Yadan Fan"
    - "Thomas Lin"
  url: "https://github.com/abachaa/MTS-Dialog"
paper:
  title: "An Empirical Study of Clinical Note Generation from Doctor-Patient Encounters"
  arxiv: ""
  url: "https://aclanthology.org/2023.eacl-main.168/"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/mts_dialog"
released: "2023-05"
last_updated: "2024-04"
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
    No lm-eval leaderboard cell for mts_dialog was opened. Overlap
    metrics on this short-note task are not comparable to HELM LLM-jury
    scores on [aci_bench](aci_bench.md).
contamination:
  risk: medium
  note: >
    Dialogues and gold sections have been public on GitHub under CC BY
    4.0 since the 2023 shared tasks, and the har1 mirror is public.
    lm-eval scores the 1,301-row train dump, not a hidden test set, so
    a model fine-tuned on MTS-Dialog train is being tested on its
    training pairs.
harness:
  lm_eval: "mts_dialog"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Companion task mts_dialog_perplexity (loglikelihood_rolling). YAML metadata version 1.2."
tags:
  - clinical
  - summarization
  - medical
  - lm-eval
  - dialogue
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mts_dialog/README.md"
    title: "lm-eval mts_dialog README (1,700 pairs, paper link, task names)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mts_dialog/mts_dialog.yaml"
    title: "mts_dialog.yaml (HF path, generate_until, metrics, all splits=train)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mts_dialog/utils.py"
    title: "utils.py (dialogue/section_text, BLEU/ROUGE/BERTScore/BLEURT, short-string NaNs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mts_dialog/mts_dialog_perplexity.yaml"
    title: "mts_dialog_perplexity.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/abachaa/MTS-Dialog/main/README.md"
    title: "Original MTS-Dialog README (splits 1201/100/200/200, 20 headers, CC BY 4.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/abachaa/MTS-Dialog/main/LICENSE.txt"
    title: "MTS-Dialog Creative Commons Attribution 4.0"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/har1/MTS_Dialogue-Clinical_Note/raw/main/README.md"
    title: "HF har1 card (MIT; 1,201+100; reformatted section headers)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/har1/MTS_Dialogue-Clinical_Note"
    title: "HF API (license mit, lastModified 2024-04-01)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=har1/MTS_Dialogue-Clinical_Note"
    title: "datasets-server size (1,301 train rows)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2023.eacl-main.168/"
    title: "EACL 2023 paper page (Ben Abacha, Yim, Fan, Lin; May 2023)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-060 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-060"
---

## What it measures

mts_dialog asks a model to turn a short English doctor-patient dialogue into the matching clinical-note section. The original MTS-Dialog set pairs each snippet with a header from a twenty-label list (chief complaint, family history, exam, and others). lm-eval loads `har1/MTS_Dialogue-Clinical_Note`, whose card says the target is a four-block note: symptoms, diagnosis, history, plan, with N/A when a block is empty.

This is section-level summarisation of brief encounters, not a full visit note. [aci_bench](aci_bench.md) is the longer ambient-visit sibling used in MEDIQA-Chat Task B/C. [covid_dialog](covid_dialog.md) is doctor-reply generation, not note writing.

## How it is scored

The generation task emits text until a blank line, then scores BLEU, ROUGE-1/2/L, BERTScore F1, and BLEURT, each nanmean. Strings shorter than five characters become NaN on every overlap metric. A true BLEU of 0 is nudged to 1e-5. `mts_dialog_perplexity` is a different number: rolling log-likelihood perplexity, where lower is better. The 2023 paper also used fact extraction and clinician ratings; those are not what lm-eval prints. Do not mix a ROUGE from this YAML with an ACI-Bench LLM-jury score.

## Dataset and licence

Asma Ben Abacha, Wen-wai Yim, Yadan Fan, and Thomas Lin released 1,700 pairs at EACL 2023 (May, Dubrovnik) under CC BY 4.0. Splits: 1,201 train, 100 valid, 200 MEDIQA-Chat 2023 Task A test, 200 MEDIQA-Sum 2023 Task A/B test. lm-eval does not use those test CSVs. It scores the 1,301-row Hugging Face train split (1,201+100). That mirror is labelled MIT and was last modified 2024-04-01. The two licences are both recorded; the GitHub dump is the original. Gold section text is public.

## Who publishes it

Microsoft authors published the dataset and paper. EleutherAI ships the harness tasks (`mts_dialog` version 1.2, plus `mts_dialog_perplexity`). The Hugging Face card lists additional mirror contributors (Patani, F, Harikrishnan, Sreeja, Jayaprakash) who reformatted the notes for a BART demo. MEDIQA-Chat 2023 and MEDIQA-Sum 2023 remain the shared-task homes.

## Lineage

MTS-Dialog is the short-dialogue track beside [aci_bench](aci_bench.md) in MEDIQA-Chat 2023 Task A. There is no successor page here. The 3,603-pair French/Spanish back-translation train set is a training resource, not this eval. Do not name a score `mts_dialog` if it was computed on the 200-item official tests with the twenty original headers.

## Saturation and contamination

No current lm-eval leaderboard cell was opened, so saturation is unknown. Contamination risk is medium: the pairs have been on GitHub since 2023, and the harness evaluates the public train dump. A model fine-tuned on MTS-Dialog train is being retested on those same 1,301 rows.

## How to run it

`lm_eval --tasks mts_dialog` (and optionally `mts_dialog_perplexity`). Install `evaluate`, `bert-score`, `rouge_score`, `nltk`, `absl-py`, and BLEURT from Google Research. Header format differs between GitHub and the har1 mirror; a number from one is not a number from the other. Stopping at `\n\n` truncates long notes.

## Reading the numbers

A high ROUGE or BERTScore means the written section overlapped the stored note on this short-dialogue dump. It does not mean the note is factually complete or safe to file. BLEURT and BERTScore need extra packages; a run that skipped them is not the YAML metric list. Always check whether the reporter used the 1,301-row HF train split or the 200-item official tests, and which section schema they scored.
