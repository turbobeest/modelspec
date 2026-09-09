---
id: vqa_rad
name: "VQA-RAD"
aliases: []
page_kind: benchmark
category: multimodal
subcategory: "medical visual question answering (radiology)"
status: active
summary: >-
  The first manually constructed radiology visual question answering dataset, pairing clinician
  questions about head, chest and abdominal images with reference answers.
measures: >
  VQA-RAD shows a model a radiology image (a head CT/MRI, chest X-ray, or abdominal CT) together
  with a naturally occurring clinical question about it, such as its imaging modality, anatomical
  plane, organ system, or whether an abnormality is present, and asks the model to answer. It
  measures whether a model can combine basic radiology image interpretation with reading
  comprehension of a clinically phrased question, across 11 question categories spanning both
  yes/no (closed) and free-text (open) answer types.
task_format: >
  The model receives an image and a question in a single multimodal turn and must answer in text.
  inspect_evals' implementation scores closed-ended (yes/no) questions by exact string match and
  open-ended questions with a tool-calling grader model that judges semantic equivalence to the
  reference answer, then reports closed, open, and overall accuracy.
metric:
  name: "Accuracy (exact match for closed/yes-no questions; model-graded semantic match for open-ended questions)"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random-chance baseline applies since closed questions are yes/no (baseline ~50%
    if guessing) while open questions are free-text with no defined chance rate. No human baseline
    figure was found in the sources read for this page; the original paper's own baseline model
    (MCB_RAD) scored 60.6% closed-ended and 25.4% open-ended accuracy, which is a model baseline,
    not a human one.
dataset:
  size: 2244
  size_note: >
    The original 2018 paper reports 315 images and 3,515 total question-answer pairs (58% closed,
    42% open, across 11 question categories). The commonly used repackaged version on the Hugging
    Face Hub (flaviagiammarino/vqa-rad), which inspect_evals loads directly, instead splits the
    data into 1,793 train (313 images) and 451 test (203 images) question-answer pairs, 2,244
    total; inspect_evals evaluates on its 451-pair test split. This discrepancy between the
    paper's reported 3,515 pairs and the widely used repackaging's 2,244 was not resolved by a
    source read for this page.
  url: "https://huggingface.co/datasets/flaviagiammarino/vqa-rad"
  license: "CC BY 4.0 (paper); the Hugging Face dataset card states CC0 1.0 Universal, a discrepancy not resolved by a source read for this page"
  languages:
    - en
  modalities:
    - image
    - text
  splits: "train (1,793 pairs / 313 images), test (451 pairs / 203 images), per the Hugging Face repackaging used by inspect_evals"
  public_test_set: true
publisher:
  org: "Lister Hill National Center for Biomedical Communications, U.S. National Library of Medicine"
  authors:
    - "Jason J. Lau"
    - "Soumya Gayen"
    - "Asma Ben Abacha"
    - "Dina Demner-Fushman"
  url: "https://doi.org/10.17605/OSF.IO/89KPS"
paper:
  title: "A dataset of clinically generated visual questions and answers about radiology images"
  arxiv: ""
  url: "https://doi.org/10.1038/sdata.2018.251"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/vqa_rad"
released: "2018-11"
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
    The original paper's own MCB_RAD baseline scored 60.6% closed-ended and 25.4% open-ended
    accuracy in 2018, well short of a ceiling, but no maintained leaderboard tracking current
    frontier multimodal models on this exact task and split was found for this page, so present-day
    saturation is not established.
contamination:
  risk: medium
  note: >
    The dataset has been publicly archived on the Open Science Framework since 2018 and further
    re-hosted on the Hugging Face Hub, so the fixed image-question-answer set could appear in
    training or fine-tuning data for models exposed to broad web or dataset-hub scrapes,
    particularly medical-domain fine-tunes that specifically target radiology VQA data.
harness:
  lm_eval: ""
  inspect_evals: "vqa_rad"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - radiology
  - visual-question-answering
  - multimodal
sources:
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/vqa_rad"
    title: "inspect_evals vqa_rad task directory README: dataset description, 315 images/2,244 QA pairs, 451-pair test split, closed/open scoring method, MCB_RAD baseline results"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/vqa_rad/dataset.py"
    title: "inspect_evals vqa_rad dataset.py: loads flaviagiammarino/vqa-rad Hugging Face dataset at a pinned revision, closed/open answer-type classification, question-type and organ-region metadata"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/vqa_rad/eval.yaml"
    title: "inspect_evals vqa_rad eval.yaml metadata: multimodal group, citation DOI 10.1038/sdata.2018.251"
    accessed: "2026-09-08"
  - url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC6244189/"
    title: "A dataset of clinically generated visual questions and answers about radiology images (Lau, Gayen, Ben Abacha, Demner-Fushman, Scientific Data 2018): 315 images, 3,515 QA pairs, 58%/42% closed/open split, 11 question categories, authors and affiliation, CC BY 4.0 licence statement, OSF archive DOI"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/flaviagiammarino/vqa-rad"
    title: "flaviagiammarino/vqa-rad dataset card on Hugging Face Hub: CC0 1.0 licence tag, train (1,793 pairs/313 images) and test (451 pairs/203 images) split sizes"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-008 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-008"
---

## What it measures

VQA-RAD shows a model a radiology image, either a head CT/MRI, a chest X-ray, or an abdominal CT,
together with a question a clinician actually asked about that image, and requires an answer. The
315 source images and their questions span 11 categories including imaging modality, anatomical
plane, organ system, presence of abnormality, positional reasoning, counting and colour, and are
split between closed (yes/no) and open (free-text) answer types. It was introduced as the first
manually constructed visual question answering dataset specific to radiology, and tests whether a
model can combine visual interpretation of a clinical image with natural-language understanding of
a domain-specific question.

## How it is scored

inspect_evals' implementation scores closed-ended (yes/no) questions with exact string match
against the reference answer, and open-ended questions with a tool-calling grader model that
judges semantic equivalence, since free-text medical answers can be phrased many correct ways.
Overall, closed, and open accuracy are reported separately. The original 2018 paper's own baseline
model (MCB_RAD) achieved 60.6% closed-ended and 25.4% open-ended accuracy, illustrating that open
questions are markedly harder than closed ones on this dataset.

## Dataset and licence

The original paper describes 315 radiology images and 3,515 total question-answer pairs (58%
closed, 42% open) collected from clinicians, across 11 question categories. inspect_evals instead
loads a widely used repackaging of the dataset from the Hugging Face Hub
(flaviagiammarino/vqa-rad), which splits the data into 1,793 train pairs (313 images) and 451 test
pairs (203 images), 2,244 pairs total, and evaluates on the 451-pair test split; the gap between
the paper's 3,515 and this repackaging's 2,244 total pairs was not resolved by a source read for
this page. The paper itself states a CC BY 4.0 licence and a U.S. government work notice, while the
Hugging Face dataset card instead tags the data CC0 1.0 Universal; both licence statements are
reported here since they were not reconciled in the sources read for this page.

## Who publishes it

VQA-RAD was created by Jason J. Lau, Soumya Gayen, Asma Ben Abacha and Dina Demner-Fushman at the
Lister Hill National Center for Biomedical Communications, part of the U.S. National Library of
Medicine, and published in Scientific Data in November 2018. The data is archived on the Open
Science Framework; the Hugging Face repackaging used by inspect_evals is independently maintained
and is the version most current benchmark harnesses load.

## Lineage

VQA-RAD has no predecessor benchmark; it was the first dataset of its kind (manually constructed
radiology VQA with clinician-authored questions) and predates several later, larger medical VQA
datasets that are not tracked in this repository. It has no tracked successor or variant page here.

## Saturation and contamination

The original paper's own baseline scored well below ceiling (60.6% closed, 25.4% open), but no
maintained leaderboard tracking current frontier multimodal models on this exact task and split
was found for this page, so present-day saturation is not established. Contamination risk is
medium: the dataset has been publicly archived since 2018 and further re-hosted on the Hugging Face
Hub, making the fixed image-question-answer set a plausible target for both broad web scrapes and
medical-domain fine-tuning corpora that specifically curate radiology VQA data.

## How to run it

Run via inspect_evals' `vqa_rad` task, which loads the flaviagiammarino/vqa-rad Hugging Face
dataset at a pinned revision, evaluates on its 451-pair test split, and scores closed questions by
exact match and open questions with a model grader. No confirmed equivalent task exists in
lm-evaluation-harness, HELM, OpenCompass or BIG-bench for this page. Scores computed against the
Hugging Face repackaging's 451-pair test split are not directly comparable to any evaluation run
against the original paper's full 3,515-pair dataset, since the item counts differ.

## Reading the numbers

A high overall score suggests a model can both interpret basic radiology image features (modality,
plane, organ, presence of abnormality) and answer in the format a clinician expects. Because closed
and open accuracy are reported separately and differ hugely in difficulty even for the paper's own
baseline model, an aggregate number can obscure whether a model is doing well on easy yes/no
questions while failing at open-ended description; check the closed/open breakdown before
comparing models. The dataset's small size (a few hundred images) also means scores can be
sensitive to a handful of examples, and the benchmark does not establish that strong performance
here generalises to real-world radiology images outside its fixed head/chest/abdomen image set.
