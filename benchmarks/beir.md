---
id: beir
name: BEIR
aliases:
  - "BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models"
page_kind: benchmark
category: embedding
subcategory: zero-shot information retrieval
status: active
summary: A suite of 18 public retrieval datasets across 9 task types used to test whether a search or embedding model generalises to new domains without fine-tuning.
measures: "BEIR gathers 18 pre-existing retrieval datasets spanning nine task types, including fact-checking, question answering, biomedical IR, news retrieval, argument retrieval, duplicate-question detection, citation prediction, tweet retrieval and entity retrieval, and evaluates one retrieval system across all of them without per-dataset fine-tuning. Given a query, a system ranks a corpus of passages or documents by relevance, scored against human relevance judgments. The premise is that a good retriever should generalise zero-shot to a new domain rather than needing supervised training data from each one, so BEIR is most informative when compared against what the system was actually trained on."
task_format: "Zero-shot passage/document retrieval and ranking across 18 datasets and 9 task types; corpora range from thousands to millions of documents"
metric:
  name: nDCG@10
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: "Recall@100, MAP and Precision@10 are also reported in the original paper. There is no single official average across the 18 datasets; reporters choose their own subset to average."
dataset:
  size: 18
  size_note: "18 retrieval datasets across 9 tasks (MS MARCO, TREC-COVID, NFCorpus, BioASQ, NQ, HotpotQA, FiQA-2018, Signal-1M, TREC-NEWS, Robust04, ArguAna, Touche-2020, CQADupStack, Quora, DBPedia, SCIDOCS, FEVER, Climate-FEVER, SciFact); per-dataset corpora range from a few thousand to several million documents."
  url: https://github.com/beir-cellar/beir
  license: Apache-2.0
  languages:
    - en
  modalities:
    - text
  splits: ""
  public_test_set: true
publisher:
  org: UKP Lab, TU Darmstadt
  authors:
    - Nandan Thakur
    - Nils Reimers
    - Andreas Rücklé
    - Abhishek Srivastava
    - Iryna Gurevych
  url: https://github.com/beir-cellar/beir
paper:
  title: "BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models"
  arxiv: "2104.08663"
  url: https://arxiv.org/abs/2104.08663
  year: 2021
leaderboard_url: https://huggingface.co/spaces/mteb/leaderboard
repo_url: https://github.com/beir-cellar/beir
released: "2021"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - mteb
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "BEIR is 18 heterogeneous datasets, not one scale, so a single ceiling is not meaningful. Per-dataset scores on the MTEB leaderboard vary widely by design, which is a known property of the suite rather than a recent shift."
contamination:
  risk: medium
  note: "Queries, corpora and relevance judgments are fully public. Several component datasets, including MS MARCO and Natural Questions, are also standard supervised training sets for retrieval models; training on them breaks the zero-shot premise BEIR was designed to test, a distinction the original paper itself draws between in-domain and zero-shot results."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "beir-cellar/beir: reference Python package for loading, indexing and scoring. Most current scores are read from the MTEB leaderboard's Retrieval task, which reuses BEIR's datasets and evaluation method."
tags:
  - retrieval
  - information-retrieval
  - embeddings
  - zero-shot
sources:
  - url: https://arxiv.org/abs/2104.08663
    title: "BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models"
    accessed: "2026-09-07"
  - url: https://github.com/beir-cellar/beir
    title: "beir-cellar/beir (GitHub repository)"
    accessed: "2026-09-07"
  - url: https://huggingface.co/spaces/mteb/leaderboard
    title: "MTEB Leaderboard"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BEIR asks a single retrieval or embedding system to search 18 different collections it was not built for, covering fact-checking, question answering, biomedical literature, news, arguments, duplicate questions, citation matching, tweets and Wikipedia entities. Given a query, the system ranks a corpus of passages or documents by relevance and is scored against human relevance judgments.

The point of the suite is generalisation rather than raw retrieval quality on any one domain: a retriever tuned on one style of query, most often MS MARCO's web-search queries, is tested cold on everything else, and its BEIR score is most meaningful read alongside what it was actually trained on.

## How it is scored

Systems are scored per dataset, primarily by nDCG@10, normalised discounted cumulative gain over the top 10 results, which is bounded between 0 and 1 by construction. The original paper also reports Recall@100, MAP and Precision@10. There is no single official average across the suite; different reporters compute their own mean over a subset of the 18 datasets, and that subset is not standardised, so an aggregate "BEIR score" from two different sources is not guaranteed to cover the same datasets. The paper's own zero-shot condition trains a system only on MS MARCO, if at all, then evaluates without further tuning on the rest.

## Dataset and licence

BEIR wraps 18 pre-existing public datasets, among them MS MARCO, TREC-COVID, NFCorpus, NQ, HotpotQA, FiQA-2018, ArguAna, Touche-2020, Quora, CQADupStack, DBPedia, SCIDOCS, FEVER, Climate-FEVER and SciFact, behind one loading and evaluation interface. The beir-cellar/beir toolkit is released under an Apache-2.0 licence; each underlying dataset keeps its own original licence, documented per dataset in the repository. All queries, corpora and relevance judgments are public, with corpus sizes ranging from a few thousand documents to several million.

## Who publishes it

BEIR was introduced by Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek Srivastava and Iryna Gurevych at UKP Lab, TU Darmstadt, appearing at the NeurIPS 2021 Datasets and Benchmarks track. The code originally lived at UKPLab/beir on GitHub; maintenance has since moved to the community-run beir-cellar/beir repository, developed together with UKP Lab, Castorini and Hugging Face.

## Lineage

BEIR has no predecessor of its own; it repackages 18 earlier retrieval datasets under one protocol rather than introducing new data. Its most consequential successor is [MTEB](mteb.md) (Massive Text Embedding Benchmark), which explicitly reuses BEIR's datasets and evaluation method as MTEB's Retrieval task category. In this repository's own census of reported scores, most current BEIR numbers are in fact read off the Retrieval column of the MTEB leaderboard rather than a standalone BEIR-only leaderboard, which makes MTEB the practical successor even though BEIR's own toolkit still works standalone.

## Saturation and contamination

No single ceiling applies across BEIR's 18 heterogeneous datasets, so an overall saturation status is not established here. Per-dataset leaderboards on MTEB show some datasets with much higher top scores than others, which is a known property of a suite built from datasets of very different difficulty, not a recent development. Contamination risk is best treated as medium: queries, corpora and relevance judgments are fully public, and several component datasets, including MS MARCO and Natural Questions, are also standard supervised training sets for retrieval models, so training on them breaks the zero-shot premise BEIR was designed to test. The original paper itself distinguishes in-domain (MS MARCO-trained) from zero-shot results for exactly this reason.

## How to run it

The reference implementation is the beir-cellar/beir Python package, which handles dataset download, indexing and scoring against BM25 and dense baselines. Because BEIR is not one dataset but 18, published numbers are hard to compare unless the reporter states which subset they averaged, which retriever architecture and index they used (sparse, dense, late-interaction or reranking), and whether the underlying embedding model saw any BEIR component's training split during its own training. The MTEB leaderboard is the most current public source for BEIR-derived retrieval scores today.

## Reading the numbers

A strong average BEIR or MTEB-Retrieval score suggests a model generalises across retrieval domains rather than overfitting to one style of query. It does not tell you how the model does on any single domain you care about, since a high average can hide a low score on the one dataset closest to your use case. Always check whether the reporter trained on any BEIR component, especially MS MARCO or NQ, before treating a score as genuinely zero-shot, and check which of the 18 datasets were actually averaged into the number you are reading.
