---
id: paws
name: "PAWS"
aliases:
  - "PAWS-Wiki"
  - "Paraphrase Adversaries from Word Scrambling"
page_kind: benchmark
category: reasoning
subcategory: "binary paraphrase identification on high lexical-overlap English sentence pairs"
status: active
summary: "Inspect Evals yes/no paraphrase detection on the 8,000-item PAWS-Wiki labeled-final test set of high-overlap sentence pairs."
measures: >
  This id is UKGovernmentBEIS inspect_evals task paws, not PAWS-X and not GLUE
  MRPC. Each item is two English sentences with high bag-of-words overlap.
  The model must answer Yes if they are paraphrases and No otherwise. Zhang,
  Baldridge and He (NAACL 2019) built the pairs from Wikipedia (and a separate
  QQP-derived set) by word swapping and back-translation so that overlap no
  longer implies equivalence. Inspect uses Hugging Face config labeled_final,
  test split only.
task_format: >
  Yes/No generation. Inspect prompt: answer Yes or No whether two sentences are
  paraphrases, with Sentence1/Sentence2 lines, no other tokens. Default shuffle
  true. English text.
metric:
  name: "accuracy (Inspect includes scorer against Yes/No)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Two classes, chance 50%. Labeled (Final) is 44.2% paraphrase (Yes), so a
    majority-No classifier scores about 55.8% accuracy. Inspect eval.yaml lists
    8,000 dataset_samples. Human agreement in the paper is 94.7% on Wikipedia
    paraphrase judgements (five-way majority), which is annotator agreement,
    not a held-out human accuracy, so human_baseline is empty. Models trained
    only on QQP scored under 40% accuracy on PAWS in the 2019 paper. The abstract
    and official README say adding PAWS training lifts BERT to 85%; that 85% is
    the QQP-domain result in the introduction, not a PAWS-Wiki test figure.
dataset:
  size: 8000
  size_note: >
    Inspect scores google-research-datasets/paws config labeled_final split
    test (8,000 pairs), pinned at revision 161ece9501cf0a11f3e48bd356eaa82de46d6a09.
    Official PAWS-Wiki Labeled (Final): train 49,401 / dev 8,000 / test 8,000
    (Hugging Face API matches). Additional public sets: Labeled Swap-only train
    30,397; Unlabeled Final train 645,652 plus 10,000 validation. Headline paper
    count is 108,463 human-labelled pairs plus 656k noisy pairs. PAWS-QQP
    (11,988 train, 677 dev+test) is not in this Inspect task.
  url: "https://huggingface.co/datasets/google-research-datasets/paws"
  license: "other (Google: may be freely used for any purpose, acknowledgement appreciated; AS IS, no warranty)"
  languages:
    - en
  modalities:
    - text
  splits: "Inspect: labeled_final test (8,000). Official Final also has train 49,401 and validation 8,000."
  public_test_set: true
publisher:
  org: "Google Research"
  authors:
    - "Yuan Zhang"
    - "Jason Baldridge"
    - "Luheng He"
  url: "https://github.com/google-research-datasets/paws"
paper:
  title: "PAWS: Paraphrase Adversaries from Word Scrambling"
  arxiv: "1904.01130"
  url: "https://arxiv.org/abs/1904.01130"
  year: 2019
leaderboard_url: ""
repo_url: "https://github.com/google-research-datasets/paws"
released: "2019"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - paws_x
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    2019 BERT+PAWS reached 85% in the paper's QQP-domain result. No current
    Inspect Evals leaderboard top accuracy was copied here. Status is watch
    because the test set is small, public and old, while the original QQP-only
    failure mode is no longer the interesting comparison for frontier LLMs.
contamination:
  risk: high
  note: >
    Train, dev and test labels have been public since 2019. Wikipedia source
    sentences are web text. Inspect evaluates the public test split.
harness:
  lm_eval: ""
  inspect_evals: "paws"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    inspect eval inspect_evals/paws. Dataset google-research-datasets/paws
    labeled_final test. Scorer includes(). Version 2-A in eval.yaml (2026-02-16).
tags:
  - paraphrase
  - sentence-pair
  - inspect-evals
  - english
  - adversarial
sources:
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/src/inspect_evals/paws/paws.py"
    title: "inspect_evals paws.py (labeled_final test, Yes/No template, pin)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/src/inspect_evals/paws/eval.yaml"
    title: "inspect_evals paws eval.yaml (8,000 samples, arXiv 1904.01130)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/src/inspect_evals/paws/README.md"
    title: "inspect_evals PAWS README (usage, example, accuracy)"
    accessed: "2026-09-08"
  - url: "https://github.com/google-research-datasets/paws"
    title: "google-research-datasets/paws README and LICENSE"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/google-research-datasets/paws"
    title: "Hugging Face PAWS card (split counts, licence text)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/google-research-datasets/paws"
    title: "Hugging Face PAWS API (labeled_final 49401/8000/8000)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1904.01130"
    title: "PAWS paper abstract"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1904.01130"
    title: "PAWS paper HTML (counts, 85% BERT+PAWS, <40% QQP-only)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-013 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-013"
---

## What it measures

Inspect `paws` is English paraphrase identification on PAWS-Wiki. Two
sentences share most of their words. The model must say whether they still
mean the same thing. Typical traps swap arguments, entities or modifiers
("flights from New York to Florida" versus the reverse).

This is not [PAWS-X](paws_x.md), which translates the same Wikipedia pairs.
It is not [GLUE MRPC](glue_mrpc.md) or [QQP](glue_qqp.md), which lack these
adversarial swaps. Inspect does not score PAWS-QQP.

## How it is scored

Inspect reports accuracy. The target is the string `Yes` or `No`. The scorer
is `includes()`, so a longer completion that contains that token can still
count as correct. The prompt forbids other answers. Shuffle defaults to true.
Do not mix this generation accuracy with the 2019 BERT classification table
without naming both protocols.

## Dataset and licence

PAWS-Wiki Labeled (Final) has 49,401 / 8,000 / 8,000 train/dev/test with
44.2% Yes. Inspect uses the 8,000-item test split at a pinned Hugging Face
revision. Google’s licence allows free use with acknowledgement and no
warranty; Hugging Face marks it `other`. The GitHub repo is archived
(API `archived` true; archive date not returned). Test labels are public.

## Who publishes it

Zhang, Baldridge and He (Google; NAACL 2019; arXiv 1904.01130). Inspect Evals
(UK DSIT / formerly BEIS) wraps the Hugging Face dump as `inspect_evals/paws`.

## Lineage

Successor [paws_x](paws_x.md) adds six human-translated languages plus English
PAWS-X files. IberoBench `paws_gl` and `paws_ca` (see
[GalicianBench](galician_bench.md) and [CatalanBench](catalan_bench.md)) are
further translations inside those suites, not this Inspect id. MRPC and QQP
are older paraphrase sets without the swap adversaries.

## Saturation and contamination

QQP-trained models collapsed here in 2019; models trained with PAWS data did
not. Frontier LLMs may sit near ceiling on 8,000 public pairs. Contamination
is high. No live Inspect top score is recorded on this page.

## How to run it

`inspect eval inspect_evals/paws`. Pin the dataset revision if you need to
match published logs. Do not report a `pawsx` group mean as this id.

## Reading the numbers

A high Inspect score means the model usually said Yes or No in line with the
2019 Wikipedia labels on scrambled pairs. It does not measure paraphrase
generation, cross-lingual transfer, or robustness on PAWS-QQP. Look at
[paws_x](paws_x.md) when the claim is multilingual structure sensitivity.
