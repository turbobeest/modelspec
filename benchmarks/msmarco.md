---
id: msmarco
name: "MS MARCO (HELM passage ranking)"
aliases:
  - "MS MARCO"
  - "MSMARCO"
  - "Microsoft MAchine Reading COmprehension"
  - "msmarco_regular"
  - "msmarco_trec"
page_kind: benchmark
category: knowledge
subcategory: "HELM binary LLM ranker on MS MARCO passage tracks (regular and TREC)"
status: unknown
summary: "HELM's MS MARCO passage-ranking wrap: an LLM says Yes or No whether a passage answers a Bing query, then HELM ranks those decisions."
measures: >
  This id is HELM's `msmarco` scenario, not the original 2016 reading-
  comprehension leaderboard and not an embedding nDCG run from
  [beir](beir.md). Microsoft MS MARCO pairs Bing queries with web
  passages. HELM follows Nogueira and Jiang (2020) and turns ranking
  into binary classification: given one passage and one query, the
  model must answer whether the passage answers the query. HELM then
  sorts passages by the Yes/No token and its log-probability. Two
  passage tracks exist: regular (dev.small qrels) and TREC (2019
  deep-learning qrels). English text.
task_format: >
  Binary ranking adapter. Prompt block is Passage / Query / "Does the
  passage answer the query?" / Answer: Yes or No. Default four in-context
  training instances (two blocks each: one gold, one non-gold). Stop at
  newline. Run spec name msmarco:track={regular|trec},valid_topk={int}.
  Regular gold relation is 1. TREC gold relations are 2 and 3 (0 and 1
  count as non-gold).
metric:
  name: "RR@10 (regular track); NDCG@10 (TREC track)"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM metadata: main_metric RR@10 on valid for msmarco_regular, NDCG@10
    on valid for msmarco_trec. Regular also logs success@k, recall@k, and
    recip_rank@k for k in the scenario lists. TREC adds ndcg_cut@k.
    Rankings use Yes before No before unknown tokens, with log-prob order
    inside each class (Yes high-to-low, No low-to-high). No HELM human
    baseline is stated. Original MS MARCO MRC metrics are not this wrap.
dataset:
  size: null
  size_note: >
    Passage collection: 8,841,823 cleaned passages (MacAvaney et al.
    2021), hosted on a CodaLab bundle. Regular track: 6,980 queries
    (queries.dev.small; official test qrels are not public). Regular
    qrels: 7,437 relations, gold value 1 only. TREC track: 200 queries
    and 502,982 qrels with grades 0–3. Train queries available: 808,731;
    HELM uses 1,000 train queries, two instances each. valid_topk, when
    set, must lie in [11, 1000]. HELM baseline tables quote 10,000
    validation requests for regular_topk at valid_topk=50. Query count
    after qrels/topk filtering is not a single fixed integer in the
    scenario file.
  url: "https://microsoft.github.io/msmarco/"
  license: "non-commercial research only; no IP licence granted (MS MARCO terms)"
  languages:
    - en
  modalities:
    - text
  splits: "HELM TRAIN_SPLIT plus VALID_SPLIT (regular=dev.small or TREC 2019); official MARCO test qrels withheld"
  public_test_set: true
publisher:
  org: "Microsoft (dataset); HELM wrap by Stanford CRFM"
  authors:
    - "Payal Bajaj"
    - "Daniel Campos"
    - "Nick Craswell"
    - "Li Deng"
    - "Jianfeng Gao"
    - "Xiaodong Liu"
    - "Rangan Majumder"
    - "Andrew McNamara"
    - "Bhaskar Mitra"
    - "Tri Nguyen"
    - "Mir Rosenberg"
    - "Xia Song"
    - "Alina Stoica"
    - "Saurabh Tiwary"
    - "Tong Wang"
  url: "https://microsoft.github.io/msmarco/"
paper:
  title: "MS MARCO: A Human Generated MAchine Reading COmprehension Dataset"
  arxiv: "1611.09268"
  url: "https://arxiv.org/abs/1611.09268"
  year: 2016
leaderboard_url: "https://microsoft.github.io/msmarco/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/msmarco_scenario.py"
released: "2016"
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
    No HELM leaderboard cell for msmarco_regular or msmarco_trec was
    opened here. Embedding nDCG@10 numbers on BEIR/MTEB MS MARCO are a
    different protocol.
contamination:
  risk: high
  note: >
    Queries, passages, and regular/TREC qrels used by HELM are public
    and have been standard supervised IR training data since 2016–2019.
    The official MARCO test qrels stay hidden; HELM therefore scores
    dev.small or TREC 2019 instead. [beir](beir.md) already warns that
    training on MS MARCO breaks a zero-shot retrieval claim.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "msmarco"
  opencompass: ""
  bigbench: ""
  other: "Run spec msmarco:track={regular|trec},valid_topk=.... Groups msmarco_regular and msmarco_trec. BinaryRankingAdapter labels Yes/No."
tags:
  - retrieval
  - ranking
  - helm
  - information-retrieval
  - ms-marco
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/msmarco_scenario.py"
    title: "HELM MSMARCOScenario (tracks, file counts, gold relations, metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM get_msmarco_spec (Yes/No adapter, four train instances)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/adapters/binary_ranking_adapter.py"
    title: "BinaryRankingAdapter (Passage/Query prompt, Yes/No labels)"
    accessed: "2026-09-08"
  - url: "https://microsoft.github.io/msmarco/"
    title: "Official MS MARCO site (tasks, non-commercial research terms)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1611.09268"
    title: "MS MARCO paper (arXiv:1611.09268; submitted 2016-11-28, v3 2018-10-31)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-060 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-060"
---

## What it measures

HELM `msmarco` tests whether a language model can tell if a web passage answers a Bing query, then uses those Yes/No decisions to rank passages. It is passage ranking, not answer writing. The original MS MARCO paper (Bajaj et al., 2016) also defined reading comprehension and answer generation; those tracks are not this id. HELM currently implements the passage tracks only.

Inputs are English. Regular track queries come from the public development small set because official test qrels are hidden. TREC track uses the 2019 deep-learning passage qrels. This is not [beir](beir.md)'s embedding nDCG on the same collection, and not [melt_ir](melt_ir.md)'s Vietnamese mMARCO.

## How it is scored

Each query–passage pair is a separate request. The adapter asks "Does the passage answer the query?" and expects `Yes` or `No`. HELM ranks Yes tokens (high log-prob first), then No tokens (low log-prob first), then anything else. Regular track metadata names RR@10 on the valid split. TREC metadata names NDCG@10. Regular gold labels are binary 1. TREC treats grades 2 and 3 as gold and 0 and 1 as not. Changing `valid_topk` changes how many BM25 candidates are scored and changes the request count. Scenario comments list four HELM baselines (regular_topk 10,000 requests at top-50, and three others). Those request counts are not model scores.

## Dataset and licence

Microsoft hosts MS MARCO for non-commercial research and states that the dump grants no IP licence. HELM downloads 8,841,823 cleaned passages from CodaLab (MacAvaney et al., 2021), train queries from the MARCO site, regular qrels as `qrels.dev.small.tsv` (7,437 relations), and TREC 2019 qrels from NIST (502,982 lines). Regular has 6,980 listed queries; TREC has 200. HELM then drops queries that lack qrels or top-k rows, so the scored query count is smaller and not printed as one number. Train time uses 1,000 queries. Answers for the official MARCO test set stay hidden; HELM never scores that file.

## Who publishes it

Microsoft Research released MS MARCO in 2016 (arXiv:1611.09268, v3 2018-10-31). Authors include Payal Bajaj, Nick Craswell, Jianfeng Gao, Bhaskar Mitra, and others listed on the abs page. Stanford CRFM maintains the HELM wrap (`MSMARCOScenario`, run spec `msmarco`). The live MARCO site remains the dataset home. That site marks Passage Retrieval RETIRED (10/26/2018–01/01/2023); it is not a HELM score table.

## Lineage

MS MARCO is older than HELM. [beir](beir.md) and [mteb](mteb.md) reuse the collection for embedding retrieval. [melt_ir](melt_ir.md) is a Vietnamese translation of passage ranking, not this English wrap. Document ranking is described in the scenario comments but is not implemented. Nogueira and Jiang (2020) is the cited binary-ranker recipe. MacAvaney et al. (2021) is the cleaned passage file.

## Saturation and contamination

No HELM msmarco cell was opened here, so saturation is unknown. Contamination risk is high: the queries and passages have been public training data for retrievers for years. A strong HELM RR@10 can mean the model already saw MS MARCO pairs, not that it generalises as a ranker. Do not read a BEIR MS MARCO nDCG as this Yes/No ranker.

## How to run it

HELM run spec `msmarco:track=regular,valid_topk=50` or `msmarco:track=trec,valid_topk=100` match the commented baselines. `track` must be `regular` or `trec`. `valid_topk`, if set, must be between 11 and 1,000. Four in-context examples is the adapter default. Yes/No string mismatches become "unknown" and sink in the ranking. HELM's README says the project entered maintenance mode on 2026-06-01; confirm the revision if you need a match to an old table.

## Reading the numbers

RR@10 on regular says a gold passage often landed in the top ten of the BM25 shortlist the scenario scored, after Yes/No sorting. NDCG@10 on TREC uses graded relevance and is not the same scale. Neither number is full-collection retrieval: HELM reranks a top-k list, not 8.8 million passages per query. Check track, `valid_topk`, and whether the reporter trained on MS MARCO before treating the score as zero-shot search quality.
