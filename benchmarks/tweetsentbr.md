---
id: tweetsentbr
name: TweetSentBR
aliases: [tweetSentBR]
page_kind: benchmark
category: domain
subcategory: Brazilian Portuguese sentiment
status: active
summary: TweetSentBR evaluates sentiment classification for Brazilian Portuguese tweets.
measures: Tweets are labeled Positive, Negative, or Neutral by multiple annotators.
task_format: Classify each tweet into one of three labels.
metric:
  name: accuracy
  direction: higher_is_better
  unit: percent
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 2085
  size_note: "75 train rows and 2,010 test rows (2,085 total), per the Hugging Face datasets-server for eduagarcia/tweetsentbr_fewshot; the HELM scenario code itself only says 75 training samples and 'all' of the 2,000-plus test instances."
  url: https://huggingface.co/datasets/eduagarcia/tweetsentbr_fewshot
  license: ""
  languages: [Brazilian Portuguese]
  modalities: [text]
  splits: train, test
  public_test_set: true
publisher:
  org: NILC, University of São Paulo (original corpus); Stanford CRFM HELM (few-shot scenario)
  authors: [Henrico Brum, Maria das Graças Volpe Nunes]
  url: https://github.com/brasileiras-pln/tweetSentBR
paper:
  title: "Building a Sentiment Corpus of Tweets in Brazilian Portuguese"
  arxiv: ""
  url: https://aclanthology.org/L18-1658/
  year: 2018
leaderboard_url: ""
repo_url: https://github.com/stanford-crfm/helm
released: "2018"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: unknown, top_score: null, as_of: "", note: No current standalone leaderboard was established.}
contamination: {risk: medium, note: "The corpus dates from 2017-2018 and full tweet text is redistributed via the eduagarcia/tweetsentbr_fewshot mirror on Hugging Face, so it is old enough and accessible enough to plausibly appear in training data, though no publisher or community report of leakage was found."}
harness: {lm_eval: "", inspect_evals: "", helm: tweetsentbr, opencompass: "", bigbench: "", other: ""}
tags: [sentiment, portuguese, classification]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/tweetsentbr_scenario.py
    title: HELM TweetSentBR scenario
    accessed: "2026-09-08"
  - url: https://aclanthology.org/L18-1658/
    title: "Building a Sentiment Corpus of Tweets in Brazilian Portuguese (Brum and Volpe Nunes, LREC 2018)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/abs/1712.08917
    title: "Building a Sentiment Corpus of Tweets in Brazilian Portuguese, HTML version"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/eduagarcia/tweetsentbr_fewshot
    title: TweetSentBR dataset
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/size?dataset=eduagarcia/tweetsentbr_fewshot
    title: Hugging Face datasets-server split sizes for tweetsentbr_fewshot
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-002 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: Claude Sonnet 5 independent review, luna-new-002}
---

## What it measures

TweetSentBR classifies Brazilian Portuguese tweets, drawn from television-show discussion on Twitter, as Positive, Negative, or Neutral. The original corpus paper reports tweets about talk shows, reality shows, and variety programs collected between January and July 2017.

## How it is scored

HELM constructs one correct reference label per tweet and evaluates single-label classification, mapping the English class names to Portuguese outputs (Positivo, Negativo, Neutro). The original 2018 paper reports 80.99% F-measure for a binary (positive/negative) classifier as its own headline result; that number is not directly comparable to the three-way accuracy HELM reports, since the label set and evaluation differ.

## Dataset and licence

The original corpus (Brum and Volpe Nunes, 2018) contains 15,000 annotated tweets, split 12,999 train / 2,001 test, labelled by seven native-speaker annotators with label shares of roughly 44% positive, 26-29% neutral, and 29% negative in each split. Because Twitter's terms restrict redistribution of tweet text, the original release ships only tweet IDs, requiring re-download via the Twitter API. The Hugging Face datasets-server reports 75 train rows and 2,010 test rows (2,085 total) for `eduagarcia/tweetsentbr_fewshot`, the differently sized and pre-formatted mirror the HELM scenario actually loads; its own licence terms were not established.

## Who publishes it

TweetSentBR was introduced by Henrico Brum and Maria das Graças Volpe Nunes of NILC, University of São Paulo, published at LREC 2018. Stanford CRFM maintains the HELM few-shot scenario that packages a re-split, pre-formatted version of the corpus from `eduagarcia/tweetsentbr_fewshot`.

## Lineage

This page documents the HELM few-shot scenario built on the original TweetSentBR corpus. The scenario's 75/2,010 split does not match the original paper's 12,999/2,001 split, so scores from the two should not be merged. No further predecessor or successor was established.

## Saturation and contamination

Saturation is unknown; no current leaderboard or ceiling analysis was established. Contamination risk is medium: the underlying tweets were collected in 2017 and published in 2018, and the HELM scenario's mirror redistributes full tweet text rather than IDs only, so the text is old and accessible enough to plausibly have entered training corpora, even though no specific leakage report was found.

## How to run it

Run HELM scenario `tweetsentbr`; it loads train and test splits and maps labels to Positivo, Negativo, and Neutro. Record dataset revision.

## Reading the numbers

A strong score indicates sentiment classification ability on Brazilian Portuguese tweets. It does not measure broader Portuguese language understanding or sentiment outside this corpus. Compare label mapping and few-shot examples.
