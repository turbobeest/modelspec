---
id: ulqa
name: "ULQA (Uyghur language eval group)"
aliases:
  - "ulqa_"
  - "uleval"
  - "ULUT"
  - "CELEP1"
  - "CELEP2"
  - "lambada_uyghur"
page_kind: benchmark
category: composite
subcategory: "Uyghur language and literature exams, textbook exercises, and last-word cloze"
status: active
summary: "lm-eval group of Uyghur textbook, exam, and cloze tasks covering basic language, literature, and last-word prediction."
measures: >
  ulqa is EleutherAI's group name for six Uyghur evaluations assembled by Hugging Face user
  keramjan, not a single published paper. The group mixes last-word cloze (lambada_uyghur),
  a five-task Uyghur language-understanding bundle (ulut), short generative language QA
  (ulqa_), four-way language MCQ (uleval), and 2011-2012 college-entrance literature items
  (celep1 multiple-choice, celep2 open-ended). All prompts are in Uyghur. The skill is
  Uyghur reading, vocabulary, grammar and literature exam answering, not a shared metric.
task_format: >
  Mixed. lambada_uyghur is log-likelihood last-word prediction. ulut, uleval and celep1
  are multiple-choice. ulqa_ and celep2 are greedy generate_until, stopping at "سۇئال:".
  ulqa_ is 2-shot; celep2 is 0-shot. Every YAML uses the Hugging Face train split as the
  test set. There is no held-out test split.
metric:
  name: "per-task accuracy or exact match; ulut also reports a size-weighted acc mean"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Multiple-choice tasks report acc and acc_norm. ulqa_ and celep2 report exact_match
    (case-insensitive). lambada_uyghur reports acc and perplexity (perplexity is
    lower-is-better). The parent group YAML has no aggregate_metric_list, so invoking
    `ulqa` prints six (plus ulut's five) separate scores, not one number. Chance would
    depend on the choice count (2, 3 or 4) and is not published. No human baseline.
dataset:
  size: 1468
  size_note: >
    Sum of Hugging Face train counts used as eval: ulut nug 31 + wag 50 + wsm 475 +
    wub 28 + wum 22 = 606; lambada_uyghur default 394 (harness config default, not
    main's 574); ulqa_ 171; uleval 217; celep1 28; celep2 52. Total 1,468. Sources
    are a high-school review book (ISBN 7 5631 0531 X/Z .25) for ulqa_, a middle-school
    Uyghur-language review book for uleval, 2011-2012 national Til-Edebiyat entrance
    exams for CELEP, internet materials for ULUT, and a Uyghur LAMBADA-style cloze set.
  url: "https://huggingface.co/datasets/keramjan/ulqa"
  license: "Mixed: Apache-2.0 on keramjan/ulqa, uleval, CELEP1, CELEP2, lambada_uyghur; MIT on keramjan/ulut. Underlying textbooks and exam papers are separately copyrighted."
  languages:
    - ug
  modalities:
    - text
  splits: "Hugging Face train split used as test_split on every task; no published validation/test cut"
  public_test_set: true
publisher:
  org: "keramjan (Hugging Face); packaged for lm-eval as group ulqa"
  authors:
    - "keramjan"
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/ulqa"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/ulqa"
released: "2025-08"
last_updated: "2025-10"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "No published model table was found. Several subsets have only a few dozen items, so scores will be noisy."
contamination:
  risk: high
  note: >
    CELEP items are 2011-2012 published entrance exams. ulqa_ and uleval come from
    printed review books. All splits and answers are public on Hugging Face. ULUT is
    drawn from internet materials. The harness README's "crowdsourced" wording does not
    match the dataset cards, which describe OCR from books (via datalab-to/marker) except
    for ULUT.
harness:
  lm_eval: "ulqa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group ulqa runs ulut, lambada_uyghur, ulqa_, uleval, celep1, celep2. Nested group
    ulut runs nug, wag, wsm, wub, wum. The generative language-QA task is named ulqa_
    (trailing underscore), not ulqa. lambada_uyghur loads config default (394 items),
    not main (574).
tags:
  - uyghur
  - language-understanding
  - literature
  - multiple-choice
  - cloze
  - exams
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ulqa/README.md"
    title: "lm-eval ulqa README (group contents; claims crowdsourcing)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ulqa/ulqa.yaml"
    title: "ulqa group YAML (six constituent tasks, no aggregate metric)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/keramjan/ulqa/raw/main/README.md"
    title: "keramjan/ulqa card: 171 items, Apache-2.0, high-school review book"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/keramjan/uleval/raw/main/README.md"
    title: "keramjan/uleval card: 217 four-way items, Apache-2.0"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/keramjan/CELEP1/raw/main/README.md"
    title: "keramjan/CELEP1 card: 28 MCQs from 2011-2012 Til-Edebiyat exams"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/keramjan/CELEP2/raw/main/README.md"
    title: "keramjan/CELEP2 card: 52 open-ended exam items, Apache-2.0"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/keramjan/ulut/raw/main/README.md"
    title: "keramjan/ulut card: five configs, MIT, 606 items"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/keramjan/lambada_uyghur"
    title: "keramjan/lambada_uyghur API: default 394 vs main 574, Apache-2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ulqa/ulqa_.yaml"
    title: "ulqa_ generative YAML (2-shot exact_match, dataset keramjan/ulqa)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ulqa/celep2.yaml"
    title: "celep2 YAML (0-shot generate_until exact_match, train used as test)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ulqa/ulut/nug.yaml"
    title: "ULUT nug YAML is multiple_choice despite the Hub card calling NUG generative"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-023 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-023"
---

## What it measures

ulqa is a bag of Uyghur school-style checks, not one exam. A model may have to finish a passage's last word, pick a synonym or antonym, judge whether a word is misused, answer a textbook language question, or sit 2011-2012 college-entrance literature items. Prompts are written in Uyghur. The group is useful as a low-resource language probe. It does not share one skill definition across tasks.

The harness README calls the collection crowdsourced. The Hugging Face cards for ulqa_, uleval and CELEP instead say the text was OCR'd from named books and exam compilations with datalab-to/marker. ULUT is the one card that says internet materials.

## How it is scored

Each task has its own metric. Multiple-choice tasks use mean accuracy (and acc_norm). ulqa_ and celep2 use exact match on the generated string. lambada_uyghur uses last-token accuracy plus perplexity. Nested group `ulut` averages accuracy weighted by size. Parent group `ulqa` does not average anything, so a quoted "ULQA score" that is a single percentage is not what the YAML defines. celep1 and celep2 are 80 items together; do not over-read a point estimate there.

## Dataset and licence

Counts above come from the Hub cards and API, not from re-tokenising the books. Hugging Face licences are Apache-2.0 except ULUT (MIT). That is a licence on the packaged JSON/Parquet, not a grant from the textbook or exam publishers. Answers are in the train split that the harness treats as the test set.

## Who publishes it

The datasets are uploaded by Hugging Face user keramjan in August-October 2025. No paper, organisation page, or leaderboard was found. lm-eval is only the packaging: group `ulqa` in `lm_eval/tasks/ulqa`.

## Lineage

This is not [lambada](lambada.md) or [lambada_multilingual](lambada_multilingual.md). `lambada_uyghur` is a separate Uyghur cloze set with 394 default passages. It is not a translation of OpenAI LAMBADA. CELEP is an exam dump, not CELEB or CELE. No predecessor id in this repository.

## Saturation and contamination

Saturation is unknown; no model table was opened. Contamination risk is high for CELEP and the review-book tasks because the items and keys are old, printed, and now mirrored on the Hub. Tiny subsets (nug 31, wum 22, celep1 28) will bounce with sampling noise.

## How to run it

```bash
lm_eval --model hf --model_args pretrained=<model> --tasks ulqa
```

To run one piece: `ulqa_`, `uleval`, `celep1`, `celep2`, `lambada_uyghur`, or `ulut`. Do not pass `ulqa` as a dataset path; the generative task is `ulqa_`. `lambada_uyghur` must keep `dataset_name: default` to match the 394-item card.

## Reading the numbers

Read the six (or eleven, if you expand ulut) scores separately. A strong `ulqa_` exact-match says the model can copy short language-book answers, not that it can write literature essays (`celep2`) or do last-word cloze. Because train is test, a model that saw these Hub rows in pretraining can look perfect without knowing Uyghur. Prefer ULUT's larger synonym set (wsm, 475) over the 22-item wum slice when you need a stable language-understanding number.
