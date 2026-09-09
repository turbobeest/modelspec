---
id: gold_commodity_news
name: "Gold Commodity News (HELM)"
aliases:
  - "gold_commodity_news"
  - "Gold Commodity News and Dimensions"
  - "gold-commodity-news-and-dimensions"
page_kind: benchmark
category: domain
subcategory: "HELM Enterprise yes/no classification of gold-commodity headlines"
status: unknown
summary: "HELM Enterprise yes/no classification of 11,412 gold-commodity headlines across nine information dimensions, scored by weighted F1."
measures: >
  gold_commodity_news is Stanford HELM's wrap of Sinha and Khandait's 2020
  gold-headline set. Each item is one English news headline about gold. The
  model answers Yes or No for one of nine binary dimensions: whether the
  headline is about price, direction up, constant, or down, past or future
  price, past or future non-price news, or a comparison with another asset.
  HELM does not score a joint multi-label vector. The skill is financial
  headline tagging, not price forecasting.
task_format: >
  Generation with get_generation_adapter_spec: instructions naming the
  dimension, input noun Headline, output noun Answer. Gold strings in the
  scenario are "Yes" or "No". Defaults: max_train_instances 5, max_tokens 5,
  temperature 0.0, stop at newline. Run spec name
  gold_commodity_news:category=<key>. Nine keys: price_or_not, direction_up,
  direction_constant, direction_down, past_price, future_price, past_news,
  future_news, assert_comparison.
metric:
  name: classification_weighted_f1
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    ScenarioMetadata.main_metric is classification_weighted_f1 on split test.
    The Enterprise run spec also attaches exact-match metrics and a
    ClassificationMetric with averages weighted and labels ["yes", "no"]
    (lowercase), while instance gold text is "Yes"/"No". No official random
    or human baseline is defined in the scenario. The 2020 paper reports
    classifier F1 on a held-out split of the same headlines, not HELM
    generation F1.
dataset:
  size: 11412
  size_note: >
    Paper and abstract: 11,412 human-annotated headlines from 2000–2019,
    scraped from Reuters, The Hindu, The Economic Times, Bloomberg, Kitco,
    MetalsDaily, and similar sites. Three annotators plus a consensus series
    (Cohen's kappa above 0.85 on every dimension). HELM downloads Kaggle
    version 1 as finalDataset_0208.csv, puts every row on TEST_SPLIT, then
    with random.seed(0) moves floor(n/10) rows to TRAIN_SPLIT (1,141 train /
    10,271 test if n is 11,412). There is no publisher train/test split.
    Classes are imbalanced (paper Table 2: 9,735 price-related vs 1,677 not).
  url: "https://www.kaggle.com/datasets/daittan/gold-commodity-news-and-dimensions"
  license: "Data files © Original Authors"
  languages:
    - en
  modalities:
    - text
  splits: "HELM: random 10% train / 90% test (seed 0); no official split in the paper"
  public_test_set: true
publisher:
  org: "Indian Institute of Management Ahmedabad (dataset); Stanford CRFM (HELM Enterprise scenario)"
  authors:
    - "Ankur Sinha"
    - "Tanmay Khandait"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/gold_commodity_news_scenario.py"
paper:
  title: "Impact of News on the Commodity Market: Dataset and Results"
  arxiv: "2009.04202"
  url: "https://arxiv.org/abs/2009.04202"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/gold_commodity_news_scenario.py"
released: "2020-09"
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
    No HELM Enterprise leaderboard cell was read (the public pages are JavaScript
    apps). Paper-era BERT/GRU F1 on the authors' own split is not a current LLM
    ceiling.
contamination:
  risk: medium
  note: >
    Headlines are public news text from 2000–2019. Kaggle JSON-LD dateModified
    is 2021-02-18 (dataset version 1). Labels are public. HELM's 90% test split
    is a random draw, not a hidden hold-out.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "gold_commodity_news"
  opencompass: ""
  bigbench: ""
  other: "Runnable HELM spec is gold_commodity_news:category=<key> in enterprise_run_specs.py."
tags:
  - helm
  - finance
  - classification
  - news
  - gold
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/gold_commodity_news_scenario.py"
    title: "HELM GoldCommodityNewsScenario"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enterprise_run_specs.py"
    title: "HELM Enterprise run spec gold_commodity_news"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2009.04202"
    title: "Sinha and Khandait, arXiv:2009.04202"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2009.04202"
    title: "Sinha and Khandait full text (11,412 items, nine dimensions, Table 2 counts)"
    accessed: "2026-09-08"
  - url: "https://www.kaggle.com/datasets/daittan/gold-commodity-news-and-dimensions"
    title: "Kaggle gold-commodity-news-and-dimensions (licence: Data files © Original Authors)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-046 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-046"
---

## What it measures

gold_commodity_news asks a language model to tag an English gold-market headline with one binary label at a time. The nine labels cover price versus other news, up, flat, or down, past versus future price, past versus future non-price news, and whether gold is compared with another asset. HELM builds a separate run per label. The original paper used those tags to study news and gold prices. The HELM task only scores the tags.

The headlines come from financial wires and aggregators over 2000–2019. Three experts annotated them from the headline alone. A consensus series resolved disagreements. Cohen's kappa was above 0.85 on every dimension.

## How it is scored

HELM generates a short Yes/No string after a one-sentence instruction. The adapter default is five training headlines, five output tokens, temperature 0. The named main metric is weighted classification F1 on the test split. Exact match is also recorded. The classification metric's label list is lowercase `yes`/`no`, while the scenario gold text is `Yes`/`No`. Compare numbers only when the category key matches. There is no official average across the nine keys.

The 2020 paper reports SVM, RNN, LSTM, GRU, and finance-BERT F1 on the authors' own split. Those figures are not HELM generation scores.

## Dataset and licence

The paper releases 11,412 headlines. Table 2 shows strong imbalance: 9,735 price-related versus 1,677 not; future-price and future-general tags are rare. HELM fetches Kaggle dataset version 1 (`daittan/gold-commodity-news-and-dimensions`) as `finalDataset_0208.csv`. It then assigns 10% of rows to train with `random.seed(0)`. Kaggle's published licence string is "Data files © Original Authors", not an SPDX id. HELM code is Apache-2.0. Test labels are public.

## Who publishes it

Ankur Sinha and Tanmay Khandait at IIM Ahmedabad posted the paper on 9 September 2020 (arXiv:2009.04202). India Gold Policy Centre funded the study (grant 1815012). Stanford CRFM wrapped the CSV as a HELM Enterprise finance scenario. There is no separate live leaderboard page that this research opened.

## Lineage

The dataset is original annotation, not a GLUE or FinBERT sentiment clone. HELM Enterprise siblings in this repository include [kpi_edgar](kpi_edgar.md) and [conv_fin_qa_calc](conv_fin_qa_calc.md). They share a harness, not items. No successor id is tracked here.

## Saturation and contamination

No current HELM cell was read. Paper-era neural taggers already reach high F1 on majority classes, so a strong LLM Yes/No score on `price_or_not` may say little. Rare tags such as future general news (82 true of 11,412) still separate systems. Headlines and labels have been public for years, so web-trained models may have seen both.

## How to run it

In HELM, run `gold_commodity_news` with a `category` argument from the nine keys. The group name is `gold_commodity_news`. lm-evaluation-harness and OpenCompass were not found under this id. Shot count, Yes/No casing, and which dimension was scored all move the number.

## Reading the numbers

A high weighted F1 on one dimension is headline tagging for that question, not trading skill. Majority classes inflate accuracy; F1 is the intended read, and even F1 is weak on rare tags. Do not average the nine HELM runs unless the reporter did. Check the 2020 paper's class counts before treating two models as comparable. Pair this score with a numeric finance task if the claim is about markets rather than news labels.
