---
id: melt_ir
name: "HELM MELT information retrieval (Vietnamese mMARCO and mRobust)"
aliases:
  - "melt_information_retrieval"
  - "melt_information_retrieval_mmarco"
  - "melt_information_retrieval_mrobust"
page_kind: family
category: knowledge
subcategory: "Vietnamese passage ranking with a binary LLM ranker"
status: unknown
summary: "HELM's Vietnamese information-retrieval track: rank passages for a query on translated mMARCO (RR@10) and mRobust (NDCG@10)."
measures: >
  MELT IR is not one item set. HELM file `melt_ir_scenario.py` implements two Vietnamese ranking
  scenarios that share a binary ranker: mMARCO (translated MS MARCO passage ranking) and mRobust
  (translated TREC Robust 2004). For each query the model is asked, in Vietnamese, whether a passage
  answers the query. HELM then turns those yes/no decisions into ranking metrics. There is no official
  average of the two tracks. HELM's schema labels the parent group "MELT Scenarios"; the same file's
  one-line description says "medical domain", which does not match these retrieval tasks.
task_format: >
  Binary ranking: query plus candidate passage, Vietnamese prompt "Đoạn văn này có trả lời được câu hỏi
  không?", stop at newline. Default run entries set valid_topk=30. Training uses 1,000 query pairs with
  one positive and one negative passage each.
metric:
  name: "RR@10 on Vietnamese mMARCO; NDCG@10 on Vietnamese mRobust (no combined score)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM schema_melt.yaml sets main_metric RR@10 and main_split valid for mMARCO, and NDCG@10 / valid
    for mRobust. Scenario metadata on the Python classes matches those names. No random or human
    baseline for the HELM Vietnamese ranker is stated in the scenario file, the schema, or the
    mMARCO/mRobust cards opened here.
dataset:
  size: null
  size_note: >
    Two source datasets, not one. HELM loads `unicamp-dl/mmarco` subset `vietnamese` at revision
    6d039c4638c0ba3e46a9cb7b498b145e7edc6230, and `unicamp-dl/mrobust` subset `vietnamese` at
    revision fda452a7fbfd9550db2f78d9d98e6b3ec16734df. The shared scenario class caps training at
    1,000 queries (NUM_TRAIN_QUERIES). Validation instances come from a `runs-{subset}` config's
    `bm25` split, truncated at valid_topk (30 in the published run entries). Exact Vietnamese query
    counts in those Hugging Face configs were not returned by the datasets-server size endpoint
    (404 on config=vietnamese).
  url: "https://huggingface.co/datasets/unicamp-dl/mmarco"
  license: >
    mMARCO README states Apache-2.0; the dataset repo also ships a Creative Commons Attribution 4.0
    licence text. Both were opened. mRobust's card citation block states Creative Commons Attribution
    4.0 International for the mRobust04 paper; a separate licence file was not opened for mRobust.
  languages:
    - vi
  modalities:
    - text
  splits: "HELM train (first 1,000 mMARCO/mRobust train triples) / valid (BM25 run passages, top-k=30 in default run entries)"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM MELT scenarios); mMARCO/mRobust from unicamp-dl"
  authors:
    - "Luiz Bonifacio"
    - "Vitor Jeronymo"
    - "Hugo Queiroz Abonizio"
    - "Israel Campiotti"
    - "Marzieh Fadaee"
    - "Roberto Lotufo"
    - "Rodrigo Nogueira"
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_ir_scenario.py"
paper:
  title: "mMARCO: A Multilingual Version of the MS MARCO Passage Ranking Dataset"
  arxiv: "2108.13897"
  url: "https://arxiv.org/abs/2108.13897"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_ir_scenario.py"
released: "2021"
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
    No MELT leaderboard URL resolved (https://crfm.stanford.edu/helm/melt/latest/ returned 404).
    HELM's README lists other leaderboards but not MELT. Saturation on these Vietnamese ranking
    tracks is not established.
contamination:
  risk: medium
  note: >
    mMARCO and mRobust translations have been public on Hugging Face since 2022. Queries and
    collections are translated MS MARCO / Robust04, which themselves are older public IR sets.
    HELM scores a validation ranking pool rather than a hidden test qrel file. Whether the
    Vietnamese translations appear in LLM pretraining is not measured in the sources opened here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "melt_information_retrieval_mmarco:valid_topk=30 and melt_information_retrieval_mrobust:valid_topk=30 (run_entries_melt.conf). There is no run spec named melt_ir."
  opencompass: ""
  bigbench: ""
  other: "Source file helm.benchmark.scenarios.melt_ir_scenario; base class name melt_information_retrieval."
tags:
  - information-retrieval
  - ranking
  - vietnamese
  - helm
  - melt
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_ir_scenario.py"
    title: "HELM melt_ir_scenario.py"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/melt_run_specs.py"
    title: "HELM melt_run_specs.py (mmarco and mrobust run specs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_melt.yaml"
    title: "HELM schema_melt.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_melt.conf"
    title: "HELM run_entries_melt.conf"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/unicamp-dl/mmarco"
    title: "unicamp-dl/mmarco dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/unicamp-dl/mmarco/raw/main/LICENSE"
    title: "unicamp-dl/mmarco LICENSE file (CC BY 4.0 text)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/unicamp-dl/mrobust"
    title: "unicamp-dl/mrobust dataset card"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2108.13897"
    title: "mMARCO paper (Bonifacio et al., arXiv:2108.13897)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/README.md"
    title: "HELM README (leaderboard list; no MELT board)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-003"
---

## What it measures

MELT IR is HELM's Vietnamese passage-ranking track. The census id names the Python file, not a single runnable score. Two scenarios share the file: Vietnamese mMARCO, a translation of MS MARCO passage ranking, and Vietnamese mRobust, a translation of TREC Robust 2004. The model sees a Vietnamese query and a passage and must say whether the passage answers the query. HELM then ranks the candidate passages from those binary decisions. The language is Vietnamese. The skill is query-passage relevance, not generation quality.

## How it is scored

There is no combined MELT IR number. schema_melt.yaml sets RR@10 on the valid split for `melt_information_retrieval_mmarco`, and NDCG@10 on valid for `melt_information_retrieval_mrobust`. The Python metadata on those classes matches. Run specs reuse HELM's MS MARCO ranking metric with `ADAPT_RANKING_BINARY`, using the "regular" measure list for mMARCO and the "trec" list for mRobust. Default run entries pass `valid_topk=30`. Training instances are 1,000 query pairs with one gold and one non-gold passage. No random or human baseline for this HELM ranker is stated in the opened files.

## Dataset and licence

HELM pins `unicamp-dl/mmarco` revision `6d039c4…` subset `vietnamese`, and `unicamp-dl/mrobust` revision `fda452a…` subset `vietnamese`. The shared class stops after 1,000 training queries. Validation rows come from a `runs-{subset}` config, `bm25` split, truncated at top-k. Hugging Face datasets-server did not return a size for config `vietnamese` (404), so the full Vietnamese query count is not recorded. mMARCO's README says Apache-2.0; the same repo's LICENSE file is CC BY 4.0. Both readings are kept. mRobust's citation block claims CC BY 4.0 for the 2022 paper. MS MARCO itself is older Microsoft data; Robust04 is TREC 2004.

## Who publishes it

Stanford CRFM implements the ranker inside HELM (`melt_ir_scenario.py`, `melt_run_specs.py`). The translations come from unicamp-dl (Bonifacio, Campiotti, Jeronymo, Abonizio, Lotufo, Nogueira). mMARCO is arXiv:2108.13897 (2021); mRobust04 is arXiv:2209.13738 (2022, cited on the mrobust card). The expansion of "MELT" is not stated in the schema or scenario file. schema_melt.yaml's group blurb "Scenarios for the medical domain" contradicts the Vietnamese retrieval tasks and is not used as a definition. No MELT leaderboard URL was found; `/helm/melt/latest/` returned 404.

## Lineage

This is not English MS MARCO and not a SuperGLUE task. It is HELM's Vietnamese slice of mMARCO and mRobust. This repository has no `mmarco` or `mrobust` page. Sibling MELT file-slugs in this batch are `melt_knowledge` and `melt_srn`. Queued but unassigned HELM names include `melt_synthetic_reasoning` and `melt_translation`, which are different files. Do not report a score as `melt_ir`; HELM's runnable names are `melt_information_retrieval_mmarco` and `melt_information_retrieval_mrobust`.

## Saturation and contamination

Saturation is unknown: no public MELT board was opened. Contamination risk is medium. The English source collections are old and public, and the translations have been on Hugging Face since 2022, but this page has no measurement of overlap with any model's training data. HELM evaluates a BM25-derived validation pool, not a hidden TREC-style test.

## How to run it

Install HELM and use the published run entries:

`melt_information_retrieval_mmarco:model=full_functionality_text,valid_topk=30,max_train_instances=melt`

`melt_information_retrieval_mrobust:model=full_functionality_text,valid_topk=30,max_train_instances=melt`

Both live in `run_entries_melt.conf` (priority-1 entries also include `data_augmentation=canonical` variants). There is no `melt_ir` run spec. Changing `valid_topk` changes the candidate pool and the ranking metric. `max_train_instances=melt` is the few-shot cap, not the 1,000-query training pool. Not confirmed in lm-evaluation-harness, OpenCompass, inspect_evals, or BIG-bench. HELM entered maintenance mode on 1 June 2026 per its README; that is a project status, not a dataset withdrawal.

## Reading the numbers

An RR@10 on Vietnamese mMARCO and an NDCG@10 on Vietnamese mRobust are different metrics on different collections. Do not average them unless the reporter says how. A strong score means the binary LLM ranker ordered BM25 candidates well in Vietnamese, not that the model is a general retriever. Compare only runs that share `valid_topk` and the same translation (HELM pins specific revisions). If a model card writes `melt_ir` without naming mMARCO or mRobust, the number is not interpretable.
