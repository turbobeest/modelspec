---
id: polemo2
name: "PolEmo 2.0"
aliases:
  - "PolEmo2"
  - "PolEmo 2.0"
  - "klej-polemo2"
  - "polemo2_in"
  - "polemo2_out"
page_kind: benchmark
category: domain
subcategory: "four-class Polish consumer-review sentiment, in-domain and out-of-domain"
status: unknown
summary: "Polish four-class review sentiment from PolEmo 2.0, scored in-domain and out-of-domain as two lm-evaluation-harness tasks."
measures: >
  PolEmo 2.0 is a Polish consumer-review corpus. The model reads a review and
  must label it neutral, negative, positive, or ambiguous. KLEJ splits the
  same hotel and medicine training reviews into an in-domain test
  (hotels and medicine) and an out-of-domain test (products and university).
  lm-evaluation-harness follows that pair as polemo2_in and polemo2_out.
  It is review-level four-way sentiment, not sentence-level tagging, and not
  English IMDb-style polarity.
task_format: >
  lm-eval generate_until. Polish prompt "Opinia:" plus four lettered options
  (A Neutralny, B Negatywny, C Pozytywny, D Niejednoznaczny). Decoding stops
  at "." or ",", temperature 0, max 50 tokens. A regex keeps the first A–D
  letter. Gold labels are __label__meta_zero, __label__meta_minus_m,
  __label__meta_plus_m, __label__meta_amb. Tag polemo2 runs both tasks.
metric:
  name: "micro-F1 and accuracy (Hugging Face evaluate); KLEJ cards also quote accuracy"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: 0.25
  human_baseline: null
  baseline_note: >
    Four labels, so uniform chance is 0.25 if classes were balanced. They are
    not: IN train is about 38% minus, 27% plus, 18% amb, 17% zero. The IN Hub
    card's random-demo accuracy is 0.251. Paper annotator PSA is 0.91 on texts
    and 0.88 on sentences, which is agreement, not a model accuracy ceiling.
    lm-eval reports micro-F1 and accuracy; the OUT Hub demo uses macro-F1.
dataset:
  size: 1216
  size_note: >
    lm-eval scores the test splits: allegro/klej-polemo2-in test 722 rows,
    allegro/klej-polemo2-out test 494 rows (Hugging Face datasets-server).
    IN also has train 5783 and validation 723. OUT reuses the same 5783 train
    rows and has validation 494. Those five splits sum to 8,216 unique
    reviews, matching the CoNLL 2019 paper. The OUT Hub README table copies
    IN's 723/722 val/test counts; the parquet files do not. The same README
    text says the out-of-domain eval set is about 1,000 reviews (988 in the
    files). Paper: 8,216 reviews, 57,466 sentences, 197,046 annotations.
  url: "https://huggingface.co/datasets/allegro/klej-polemo2-in"
  license: "CC-BY-NC-SA-4.0"
  languages:
    - pl
  modalities:
    - text
  splits: "IN 5783/723/722 train/val/test; OUT 5783/494/494 with shared train; lm-eval uses test"
  public_test_set: true
publisher:
  org: "Wrocław University of Science and Technology and University of Wrocław; KLEJ packaging by Allegro"
  authors:
    - "Jan Kocoń"
    - "Piotr Miłkowski"
    - "Monika Zaśko-Zielińska"
  url: "https://aclanthology.org/K19-1092/"
paper:
  title: "Multi-Level Sentiment Analysis of PolEmo 2.0: Extended Corpus of Multi-Domain Consumer Reviews"
  arxiv: ""
  url: "https://aclanthology.org/K19-1092/"
  year: 2019
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/polemo2"
released: "2019-11"
last_updated: "2022-08"
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
    No current public LLM leaderboard cell was opened. The 2019 paper reports
    BiLSTM and BERT experiments; those are fine-tunes, not the lm-eval
    letter-generation protocol. KLEJ has a leaderboard that was not read here.
contamination:
  risk: high
  note: >
    Reviews come from public sites named in the paper (including TripAdvisor,
    ZnanyLekarz, PolWro, Ceneo). The KLEJ CSVs, including test labels, have
    been on Hugging Face since 2022-03-02. lm-eval sets should_decontaminate
    on the review text. The CLARIN-PL handle cited by the Hub cards returned
    HTTP 404 on 2026-09-08.
harness:
  lm_eval: "polemo2"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Tag polemo2 runs polemo2_in (allegro/klej-polemo2-in) and polemo2_out
    (allegro/klej-polemo2-out). There is no group YAML, only a tag on
    polemo2_in.yaml. Metrics: Hugging Face micro-F1 and accuracy.
tags:
  - polish
  - sentiment
  - classification
  - klej
  - reviews
sources:
  - url: "https://aclanthology.org/K19-1092/"
    title: "Kocoń, Miłkowski, Zaśko-Zielińska, CoNLL 2019 (8,216 reviews; CC mentioned, not a SPDX id)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/K19-1092.pdf"
    title: "PolEmo 2.0 PDF (domains, 2+1 annotation, open-licence wording)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allegro/klej-polemo2-in"
    title: "Hub card klej-polemo2-in (IN splits 5783/723/722; YAML license cc-by-sa-4.0; body CC BY-NC-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allegro/klej-polemo2-out"
    title: "Hub card klej-polemo2-out (body table copies IN counts; OOD text ~1000 reviews)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=allegro/klej-polemo2-in"
    title: "datasets-server size: IN 5783/723/722"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=allegro/klej-polemo2-out"
    title: "datasets-server size: OUT 5783/494/494 (not the Hub table)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/polemo2/README.md"
    title: "lm-eval polemo2 README (group tag, in vs out domains)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/polemo2/polemo2_in.yaml"
    title: "polemo2_in.yaml (generate_until, micro-F1, letter map, decontaminate)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/polemo2/polemo2_out.yaml"
    title: "polemo2_out.yaml (include in; dataset allegro/klej-polemo2-out)"
    accessed: "2026-09-08"
  - url: "https://klejbenchmark.com/"
    title: "KLEJ homepage (nine Polish NLU tasks; PolEmo2 is packaged as two of them)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2005.00630"
    title: "KLEJ paper abs (Rybak et al., 2020); Allegro Reviews is a different KLEJ sentiment task"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-066 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-066"
---

## What it measures

PolEmo 2.0 asks a model to read a Polish consumer review and pick one of four sentiments: neutral, negative, positive, or ambiguous. Kocoń, Miłkowski, and Zaśko-Zielińska built the corpus from hotels, medicine, products, and university (school) reviews and labelled both whole reviews and sentences. About 85% of the reviews are hotels or medicine. The KLEJ packaging that lm-eval loads keeps hotel and medicine reviews as the training pool. polemo2_in tests the same two domains. polemo2_out tests products and university instead. Prompts are Polish. This is not [imdb](imdb.md) binary polarity and not Allegro Reviews, the other KLEJ sentiment task.

## How it is scored

lm-eval does not score log-likelihoods over the four labels. It generates a short continuation, takes the first A–D letter, maps it onto the gold class, and reports Hugging Face micro-F1 and accuracy. A run that never emits a letter is mapped to −1 and counted wrong. The Hub cards describe accuracy, and the OUT card's demo also prints macro-F1, so those numbers are not interchangeable with lm-eval micro-F1. Fine-tuned BERT figures from the 2019 paper use a different protocol. There is no single human accuracy; the paper's 0.91 / 0.88 figures are Positive Specific Agreement among annotators.

## Dataset and licence

The CoNLL 2019 paper counts 8,216 reviews and 57,466 sentences. The two Allegro Hub dumps plus shared train reconstruct that total: 7,228 IN rows and 988 extra OUT val/test rows. lm-eval evaluates 722 IN test rows and 494 OUT test rows. The Hub column is named `sentence` but the loading examples are full reviews. Test labels are public. The Hub YAML tag is `cc-by-sa-4.0`; the same README licence section says CC BY-NC-SA 4.0; the paper only says a Creative Commons copyright licence. This page records CC-BY-NC-SA-4.0 from the Hub prose and treats the YAML tag as a disagreement. The cited CLARIN-PL handle returned 404 when opened.

## Who publishes it

The corpus authors are at Wrocław University of Science and Technology and the University of Wrocław. CoNLL 2019 is the reference paper. Allegro published the KLEJ CSV mirrors used by lm-eval (Hub last modified 2022-08-30). EleutherAI maintains the harness YAMLs. No separate PolEmo 2.0 model-leaderboard URL was opened.

## Lineage

PolEmo 2.0 extends an earlier PolEmo resource described in the same authors' 2019 RANLP paper. KLEJ (Rybak et al., 2020) adopted it as two of nine Polish NLU tasks. This repository has no `klej` page. It is not [financial_phrasebank](financial_phrasebank.md) and not [legal_opinion_sentiment_classification](legal_opinion_sentiment_classification.md).

## Saturation and contamination

No 2026 LLM score was read, so saturation is unknown. The source sites and the labelled CSVs are public and old enough to sit in web crawls. lm-eval's decontamination flag only helps if the training corpus is scanned.

## How to run it

`lm_eval --tasks polemo2` runs both tagged tasks, or run `polemo2_in` and `polemo2_out` alone. Compare only letter-generation micro-F1/accuracy on the Hub test splits. Do not mix IN with OUT, and do not mix them with KLEJ fine-tune tables.

## Reading the numbers

A strong IN score means the model labels hotel and medicine reviews in Polish under this four-way scheme. It does not mean the model tracks product or campus reviews: that is OUT, and OUT's class mix is different (almost no neutral in the files). Letter extraction is brittle. The Hub OUT split table is wrong; use 494/494 from datasets-server. The OUT class-distribution table labels minus as "positive" and plus as "negative"; the same card's Tasks section and the lm-eval YAML map minus to negative. Licence strings on the Hub card disagree, so reuse of the CSVs needs a human check. Look at IN and OUT together, and do not treat a KLEJ fine-tune number as an lm-eval number.
