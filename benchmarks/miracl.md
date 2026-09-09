---
id: miracl
name: MIRACL
aliases:
  - "Making a MIRACL"
  - "Multilingual Information Retrieval Across a Continuum of Languages"
  - "MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages"
page_kind: benchmark
category: embedding
subcategory: multilingual retrieval
status: active
summary: Monolingual ad hoc retrieval over Wikipedia passages in 18 languages, built from native-speaker queries and relevance judgments.
measures: >
  MIRACL tests whether a retrieval or embedding system can rank passages by relevance to a query
  within the same language, across 18 typologically diverse languages, most of them under-served by
  earlier retrieval benchmarks built mainly for English. For each language, the corpus is that
  language's Wikipedia, split into passages; native speakers of the language wrote the queries and
  judged which passages were relevant, rather than translating an English query set. It is
  monolingual retrieval (query and corpus share a language), not cross-lingual retrieval, and it is
  text-only, covering Arabic, Bengali, German, English, Spanish, Persian, Finnish, French, Hindi,
  Indonesian, Japanese, Korean, Russian, Swahili, Telugu, Thai, Yoruba and Chinese.
task_format: >
  Given a query in one language, rank a passage corpus drawn from that language's Wikipedia by
  relevance to the query; relevance judgments were produced by native-speaker annotators per
  language, not machine-translated from a single source language.
metric:
  name: nDCG@10
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The original paper's shared task also reported Recall@100. nDCG@10 is bounded 0-1 by
    construction in standard information-retrieval usage; scores in this repository's cards, and on
    the MTEB leaderboard where most current MIRACL numbers are read, are typically shown on a
    0-100 scale instead. No random or human baseline was established from the sources read.
dataset:
  size: 18
  size_note: >
    18 languages: 16 were named at the initial release (Arabic, Bengali, English, Spanish, Persian,
    Finnish, French, Hindi, Indonesian, Japanese, Korean, Russian, Swahili, Telugu, Thai, Chinese),
    with German and Yoruba added as the two initially unannounced "surprise" languages for the
    WSDM 2023 Cup shared task (per MTEB's task definition, which cites the published paper).
    Per-language topic counts range from roughly 2,863-4,683 training queries and 213-1,271
    development queries, with 1,606-41,358 relevance judgments per language, per the Hugging Face
    dataset card.
  url: https://huggingface.co/datasets/miracl/miracl
  license: >
    Apache-2.0 for the project-miracl/miracl toolkit and repository code; MTEB's task metadata lists
    the dataset content itself as CC BY-SA 4.0, consistent with the licence of the Wikipedia text the
    passage collections are built from.
  languages:
    - ar
    - bn
    - de
    - en
    - es
    - fa
    - fi
    - fr
    - hi
    - id
    - ja
    - ko
    - ru
    - sw
    - te
    - th
    - yo
    - zh
  modalities:
    - text
  splits: >
    Train and development splits are public for every language with judgments. A "testA" split
    exists only for the languages MIRACL shares with the earlier Mr. TyDi benchmark. MTEB's
    reference MIRACLRetrieval task evaluates on the development split.
  public_test_set: true
publisher:
  org: David R. Cheriton School of Computer Science, University of Waterloo, with Huawei Noah's Ark Lab
  authors:
    - Xinyu Zhang
    - Nandan Thakur
    - Odunayo Ogundepo
    - Ehsan Kamalloo
    - David Alfonso-Hermelo
    - Xiaoguang Li
    - Qun Liu
    - Mehdi Rezagholizadeh
    - Jimmy Lin
  url: https://github.com/project-miracl/miracl
paper:
  title: "MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages"
  arxiv: "2210.09984"
  url: https://arxiv.org/abs/2210.09984
  year: 2023
leaderboard_url: https://huggingface.co/spaces/mteb/leaderboard
repo_url: https://github.com/project-miracl/miracl
released: "2022-10"
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
  note: >
    MIRACL is 18 separate per-language retrieval tasks, not one scale, so a single ceiling is not
    meaningful; per-language difficulty varies with corpus size and query style. This repository
    found no source that assesses whether frontier embedding models have collectively saturated
    MIRACL across its 18 languages, so an overall status is not established here.
contamination:
  risk: medium
  note: >
    Every language's corpus is built from that language's public Wikipedia, and the train and
    development query-judgment splits have been public since the dataset's October 2022 release, so
    both sides of the retrieval task (documents and labelled relevant queries) are exposed to
    anything trained on web text after that date. The original WSDM 2023 Cup shared task likely held
    out a further test set during the live competition window, but this repository could not confirm
    whether any such hidden test material is still withheld today; current MIRACL-derived scores,
    including those on the MTEB leaderboard, are read from the public development split.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The reference implementation is the project-miracl/miracl GitHub repository, built on Pyserini
    for indexing and evaluation. In practice, most current MIRACL scores for embedding models are
    read off the MTEB leaderboard, which runs it as the "MIRACLRetrieval" task (with a
    "MIRACLRetrievalHardNegatives" variant built by pooling top results from BM25 and two
    embedding models) inside its multilingual retrieval collection, scored by nDCG@10 on the
    development split — see mteb/tasks/retrieval/multilingual/miracl_retrieval.py in the
    embeddings-benchmark/mteb repository.
tags:
  - retrieval
  - embedding
  - multilingual
  - information-retrieval
sources:
  - url: https://arxiv.org/abs/2210.09984
    title: "Making a MIRACL: Multilingual Information Retrieval Across a Continuum of Languages (arXiv preprint)"
    accessed: "2026-09-08"
  - url: https://doi.org/10.1162/tacl_a_00595
    title: "MIRACL: A Multilingual Retrieval Dataset Covering 18 Diverse Languages (Transactions of the Association for Computational Linguistics, 2023, vol. 11, pp. 1114-1131)"
    accessed: "2026-09-08"
  - url: https://github.com/project-miracl/miracl
    title: "project-miracl/miracl (GitHub repository, README)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/miracl/miracl
    title: "miracl/miracl dataset card (Hugging Face)"
    accessed: "2026-09-08"
  - url: https://github.com/embeddings-benchmark/mteb/blob/main/mteb/tasks/retrieval/multilingual/miracl_retrieval.py
    title: "MTEB MIRACLRetrieval task definition (embeddings-benchmark/mteb)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice P"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MIRACL (Multilingual Information Retrieval Across a Continuum of Languages) tests whether a
retrieval or embedding system can rank passages by relevance to a query within one language, across
18 typologically diverse languages that earlier retrieval benchmarks, built mainly around English,
left under-served. For each language, the corpus is that language's Wikipedia, split into passages;
crucially, native speakers of each language wrote the queries and judged relevance themselves,
rather than a single English query set being machine-translated outward. The task is monolingual
retrieval — query and corpus share a language — not cross-lingual search, and it is text-only.

The 18 languages are Arabic, Bengali, German, English, Spanish, Persian, Finnish, French, Hindi,
Indonesian, Japanese, Korean, Russian, Swahili, Telugu, Thai, Yoruba and Chinese. Coverage is
deliberately uneven with mainstream NLP benchmarking: languages like Swahili, Telugu and Yoruba have
comparatively little prior retrieval-training data, which is part of the point of the benchmark.

## How it is scored

Systems are ranked by nDCG@10, normalised discounted cumulative gain over the top 10 results,
computed separately per language against the native-speaker relevance judgments; the original paper
and shared task also reported Recall@100. nDCG@10 is conventionally bounded 0 to 1 in information
retrieval, but MIRACL numbers reported through MTEB, where most current scores are read, are
typically shown on a 0-100 scale instead — a display difference to check before comparing two
sources. There is no single official cross-language average; reporters choose which languages, and
which split, to summarise.

## Dataset and licence

MIRACL provides, per language, a Wikipedia-derived passage corpus, a set of native-speaker-authored
queries, and relevance judgments over query-passage pairs. Train and development splits are public
for every language with judgments, with per-language counts ranging from roughly 2,863 to 4,683
training queries and 213 to 1,271 development queries, and 1,606 to 41,358 relevance judgments. A
further "testA" split exists only for the languages MIRACL shares with the earlier Mr. TyDi
benchmark. The project-miracl/miracl toolkit and repository code are licensed Apache-2.0; MTEB's
task metadata separately lists the dataset content itself as CC BY-SA 4.0, consistent with the
licence of the underlying Wikipedia text.

## Who publishes it

MIRACL was introduced by Xinyu Zhang, Nandan Thakur, Odunayo Ogundepo, Ehsan Kamalloo and Jimmy
Lin at the David R. Cheriton School of Computer Science, University of Waterloo, together with
David Alfonso-Hermelo, Xiaoguang Li, Qun Liu and Mehdi Rezagholizadeh at Huawei Noah's Ark Lab. An
arXiv preprint, then titled "Making a MIRACL," appeared in October 2022 alongside the WSDM 2023 Cup
shared task the dataset was built for; the peer-reviewed version, "MIRACL: A Multilingual Retrieval
Dataset Covering 18 Diverse Languages," appeared in Transactions of the Association for
Computational Linguistics in September 2023. The authors maintain the reference repository at
github.com/project-miracl/miracl.

## Lineage

MIRACL's closest predecessor within the same research group is Mr. TyDi, an earlier, smaller
multilingual retrieval effort by overlapping authors — MIRACL's own "testA" split exists only for
the languages the two benchmarks share — though Mr. TyDi does not have a page in this repository.
MIRACL's most consequential downstream relationship is with [MTEB](mteb.md) (Massive Text Embedding
Benchmark), which implements it directly as a retrieval task, "MIRACLRetrieval," inside its
multilingual retrieval collection (plus a hard-negatives variant built by pooling BM25 and embedding
model results). In this repository's own census of reported scores, current MIRACL numbers are
typically read off the MTEB leaderboard rather than a standalone MIRACL-only leaderboard, which
makes MTEB the practical successor for day-to-day score reporting even though MIRACL's own toolkit
still runs standalone.

## Saturation and contamination

MIRACL is 18 separate per-language retrieval tasks rather than one scale, so a single saturation
verdict is not meaningful; difficulty varies with each language's corpus size, query style and how
much retrieval-training data exists for it already. This repository found no source assessing
whether frontier embedding models have collectively saturated MIRACL across all 18 languages, so an
overall status is not established here. Contamination risk sits at medium: every language's corpus
is drawn from that language's public Wikipedia, and the labelled train and development queries have
been public since the October 2022 release, so both sides of the retrieval task are exposed to
anything trained on web text since then. Whether any genuinely hidden test material still exists
from the original WSDM 2023 Cup shared task was not established; current scores are read from the
public development split.

## How to run it

The reference implementation is the project-miracl/miracl GitHub repository, built on the Pyserini
toolkit for indexing and evaluation. MIRACL is not one of the tasks bundled with lm-evaluation-harness,
inspect_evals, HELM, OpenCompass or BIG-bench. In practice, most current scores for embedding models
are produced through the mteb Python package, which implements MIRACL as the "MIRACLRetrieval" task
(plus a "MIRACLRetrievalHardNegatives" variant) within its multilingual retrieval group, evaluating
on the development split with nDCG@10 as the headline metric. Because embedding dimensionality,
maximum sequence length, pooling method, and whether a task-specific instruction prefix was
prepended to the query all affect retrieval scores and vary between reporters, MIRACL numbers from
different sources are not guaranteed to be comparable.

## Reading the numbers

A strong average MIRACL score suggests an embedding model retrieves well across a genuinely
diverse set of languages and scripts, not just the handful of high-resource languages most retrieval
models are tuned on — which is the benchmark's central point. It does not say the model performs
well on the specific language, domain or document type a real deployment needs, since per-language
scores vary substantially and an average can hide a model that is strong on, say, English and
Chinese but weak on Swahili or Yoruba. Check the per-language breakdown rather than a blended
average, note whether the score came from MIRACL's own toolkit or from MTEB's implementation, and
treat the two as roughly but not exactly comparable given their differing evaluation splits and
scaling conventions.
