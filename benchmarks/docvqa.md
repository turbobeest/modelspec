---
id: docvqa
name: DocVQA
aliases:
  - Document Visual Question Answering
page_kind: benchmark
category: multimodal
subcategory: document understanding
status: active
summary: Question answering over scanned and typed document images, scored by fuzzy text match against reference answers.
measures: >
  DocVQA gives a model an image of a real document — a letter, memo, form, table or report — plus a
  natural-language question about its content, and asks for a short free-text answer. Questions require
  reading text in context (totals in a table, a form field's value, a handwritten note, a figure label)
  rather than isolated OCR, so the task combines text recognition, layout understanding and reading
  comprehension in a single English-language, single-image, single-turn call.
task_format: Document image plus a natural-language question in; a short free-text answer out.
metric:
  name: ANLS (Average Normalized Levenshtein Similarity)
  direction: higher_is_better
  unit: score (0-1)
  max_score: 1.0
  random_baseline: null
  human_baseline: 0.981
  baseline_note: >
    Human ANLS measured by the paper's authors on the test split; human exact-match accuracy on the
    same split was reported separately as 94.36%.
dataset:
  size: 50000
  size_note: 50,000 questions over 12,767 document images, split roughly 80/10/10 into train, validation and test.
  url: https://www.docvqa.org/
  license: ""
  languages:
    - en
  modalities:
    - image
    - text
  splits: train / validation / test; reference answers on the official test split are withheld by the organizers
  public_test_set: false
publisher:
  org: Computer Vision Center (Universitat Autònoma de Barcelona) and IIIT Hyderabad, with Amazon
  authors:
    - Minesh Mathew
    - Dimosthenis Karatzas
    - R. Manmatha
    - C.V. Jawahar
  url: https://www.docvqa.org/
paper:
  title: "DocVQA: A Dataset for VQA on Document Images"
  arxiv: "2007.00398"
  url: https://arxiv.org/abs/2007.00398
  year: 2021
leaderboard_url: https://www.docvqa.org/
repo_url: ""
released: "2020-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 0.964
  as_of: "2026-09"
  note: >
    llm-stats.com's DocVQA leaderboard put Qwen2.5 VL 72B Instruct at 0.964 ANLS as of early September
    2026, within two points of the paper's own human ANLS baseline of 0.981 and close to the metric's
    ceiling of 1.0.
contamination:
  risk: medium
  note: >
    The validation split's questions and reference answers have been public since 2020, so six years of
    web presence make some contamination plausible even though the official test-split answers remain
    withheld by the organizers.
harness:
  lm_eval: ""
  inspect_evals: docvqa
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - ocr
  - document-understanding
  - vqa
  - multimodal
sources:
  - url: https://arxiv.org/abs/2007.00398
    title: "DocVQA: A Dataset for VQA on Document Images"
    accessed: "2026-09-07"
  - url: https://arxiv.org/html/2007.00398
    title: "DocVQA: A Dataset for VQA on Document Images (HTML, evaluation metrics and results tables)"
    accessed: "2026-09-07"
  - url: https://www.docvqa.org/
    title: "DocVQA"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/lmms-lab/DocVQA
    title: "lmms-lab/DocVQA dataset card"
    accessed: "2026-09-07"
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/docvqa/README.md
    title: "inspect_evals: docvqa task README"
    accessed: "2026-09-07"
  - url: https://llm-stats.com/benchmarks/docvqa
    title: "DocVQA Leaderboard - llm-stats.com"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

DocVQA asks a model to read a scanned or born-digital document image — a letter, memo, form, or
report — and answer a short question about its content in free text. Questions probe layout-dependent
reading: totals in tables, handwritten notes, form field values, figure captions and running text, not
just plain paragraphs. It is a single-image, single-turn, English-language task that combines OCR,
layout understanding and reading comprehension in one model call.

The images come from real historical business documents rather than clean scans, so a model has to
cope with skew, low contrast, typewriter fonts and handwriting alongside typeset text.

## How it is scored

DocVQA is scored with ANLS, Average Normalized Levenshtein Similarity, a metric originally proposed for
the ST-VQA benchmark: it compares a predicted string against reference answers using normalized edit
distance, so answers that are close but not exact (typical of OCR noise) still earn partial credit
instead of zero. Each question can have more than one accepted reference answer, and the best match
counts. The paper also reports plain exact-match accuracy as a secondary metric, but treats ANLS as
primary specifically because it tolerates minor OCR-style mismatches. There is no fixed random baseline
because answers are open-ended text rather than multiple choice. Because reference answers on the
official test split are withheld by the organizers, most published leaderboard numbers today evaluate on
the validation split instead.

## Dataset and licence

50,000 questions were collected over 12,767 document images sourced from the UCSF Industry Documents
Library, a public archive of internal tobacco, drug and chemical industry records; images are split
roughly 80/10/10 into train, validation and test. Questions and answers were crowdsourced against each
image, with multiple accepted reference answers per question where wording could reasonably vary.
Neither docvqa.org nor the paper states an explicit licence for the released question-answer data
itself; a Hugging Face mirror maintained by lmms-lab tags the packaged dataset Apache-2.0, but that is
the mirror's own applied tag rather than a licence set by DocVQA's organizers, so this page leaves the
licence field unset rather than guess.

## Who publishes it

DocVQA was introduced by Minesh Mathew, Dimosthenis Karatzas, R. Manmatha and C.V. Jawahar, first posted
to arXiv in July 2020 and published at WACV 2021. It runs as Challenge 17 of the Robust Reading
Competition, organized jointly by the Computer Vision Center at the Universitat Autònoma de Barcelona
and IIIT Hyderabad, with Amazon's involvement through co-author R. Manmatha. The docvqa.org site also
credits Rubèn Pérez Tito, Ernest Valveny and Artemis Llabrés, who run related document-QA challenges
(InfographicVQA, DocCVQA) under the same portal. The organizers continue to run the Robust Reading
Competition site that hosts the official leaderboard.

## Lineage

DocVQA is the base task in a small family of document-image QA challenges run by the same group:
InfographicVQA asks questions over infographics rather than plain documents, DocCVQA is a conversational
variant, and MP-DocVQA (Multipage DocVQA) extends questions across multi-page documents instead of a
single page. None of those has its own page in this repository yet. DocVQA itself names no predecessor;
it was among the first large VQA-style datasets built specifically around scanned documents rather than
natural images.

## Saturation and contamination

Leading vision-language models now sit close to the paper's own human ANLS baseline of 0.981 on the
test split: llm-stats.com's DocVQA leaderboard put Qwen2.5 VL 72B Instruct at 0.964 as of early
September 2026, a gap of under two points. That leaves little room before the metric's ceiling of 1.0
or the original human reference point. The validation split's questions and reference answers have been
public since 2020, so six years of web presence make some contamination of that split plausible even
though the official test-split answers remain withheld; risk sits at medium rather than high because
those specific held-out answers were never published.

## How to run it

The reference implementation and official leaderboard live at docvqa.org's Robust Reading Competition
portal, which accepts predictions against the withheld test split. Inspect Evals (UK AISI's
inspect_evals package) ships a `docvqa` task that evaluates the public validation split with the same
ANLS metric, which is the practical way most model developers reproduce a comparable number without a
competition submission. Because the test split is closed, most reported scores in practice come from
the validation split, and papers do not always say which split, prompt format or image preprocessing
(resolution, cropping) they used, which makes cross-paper comparisons somewhat noisy.

## Reading the numbers

A high DocVQA score shows a model can read structured business documents and locate the right field or
figure, which transfers reasonably well to real invoice, form and report understanding. It says much
less about multi-page reasoning, arithmetic over table values, or documents in languages other than
English, none of which this benchmark covers. Given how close current models sit to the original human
baseline, a strong DocVQA number today mostly confirms basic competence rather than separating frontier
models from each other; for that, pair it with a harder, less saturated document benchmark such as
InfographicVQA or a multi-page task.
