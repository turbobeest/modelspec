---
id: pmc_patients
name: "PMC-Patients"
aliases:
  - "PMC-Patients ReCDS"
  - "ReCDS-PAR"
  - "ReCDS-PPR"
page_kind: benchmark
category: embedding
subcategory: "patient-to-article and patient-to-patient clinical retrieval"
status: active
summary: >
  167k PMC case-report summaries with citation-graph labels for retrieving
  relevant PubMed articles (PAR) and similar patients (PPR).
measures: >
  PMC-Patients tests retrieval-based clinical decision support, not diagnosis
  from scratch. The query is an English patient summary taken from a PMC case
  report. PAR must rank PubMed title/abstract records that the citation graph
  marks relevant. PPR must rank other patient summaries marked similar. Labels
  are 2 or 1 from citation distance, not from a clinician re-reading the chart.
  Both tasks share the query split and use BEIR-style queries, corpus, and qrels.
task_format: >
  English text retrieval. Query: patient summary. PAR corpus: PubMed
  title+abstract. PPR corpus: other patient notes. Train/dev/test splits.
metric:
  name: "MRR"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Official columns are MRR, P@10, nDCG@10, and R@1k (percent). The homepage
    PAR leader (25 Jun 2023) is DPR SciMult-MHAExpert at 29.89 / 9.35 / 13.79 /
    53.71. The PPR leader (5 Apr 2023) is RRF at 27.76 / 6.96 / 24.12 / 85.14.
    BM25 remains a strong PPR baseline on that board.
dataset:
  size: 167034
  size_note: >
    Nature text: 167,034 summaries pass the extraction filters; homepage and
    GitHub round this to 167k, from 141k PMC articles, with 3.1M
    patient-article links and 293k patient-patient links. ReCDS-PPR corpus is
    155.2k reference patients. Nature, GitHub, and the ReCDS card give a PAR
    corpus of 11.7M PubMed articles. arXiv 2202.13876 Table 1 instead listed
    1.4M candidate articles. HF also ships PMC-Patients-V2 with 250,294
    patients (2024 PMC baseline); that dump is not the ReCDS split.
  url: "https://huggingface.co/datasets/zhengyun21/PMC-Patients-ReCDS"
  license: "CC-BY-NC-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "train/dev/test queries shared by PAR and PPR; article-level split"
  public_test_set: true
publisher:
  org: "Tsinghua University"
  authors:
    - "Zhengyun Zhao"
    - "Qiao Jin"
    - "Fangyuan Chen"
    - "Tuorui Peng"
    - "Sheng Yu"
  url: "https://pmc-patients.github.io/"
paper:
  title: "A large-scale dataset of patient summaries for retrieval-based clinical decision support systems"
  arxiv: "2202.13876"
  url: "https://www.nature.com/articles/s41597-023-02814-8"
  year: 2023
leaderboard_url: "https://pmc-patients.github.io/"
repo_url: "https://github.com/pmc-patients/pmc-patients"
released: "2023-12"
last_updated: "2024-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 29.89
  as_of: "2023-06"
  note: >
    Homepage PAR MRR 29.89 (DPR SciMult-MHAExpert, 25 Jun 2023). PPR MRR 27.76
    (RRF, 5 Apr 2023). Last listed run is MedCPT-d on 4 Oct 2023. Ceiling is
    not in reach. The board has not added rows in the HTML retrieved 2026-09-08.
contamination:
  risk: medium
  note: >
    Summaries and qrels are public (CC-BY-NC-SA-4.0). Source articles are PMC
    Open Access with at least CC BY-NC-SA. Labels come from the public citation
    graph. No publisher contamination study of LLM training data was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official evaluation.py on github.com/pmc-patients/pmc-patients (BEIR-style
    JSON results). Not one of BEIR's 18 core datasets.
tags:
  - biomedical
  - retrieval
  - clinical
  - english
  - beir-format
sources:
  - url: "https://pmc-patients.github.io/"
    title: "PMC-Patients homepage and PAR/PPR leaderboards"
    accessed: "2026-09-08"
  - url: "https://www.nature.com/articles/s41597-023-02814-8"
    title: "Scientific Data article (published 18 Dec 2023, CC BY 4.0 article)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2202.13876"
    title: "arXiv 2202.13876 full text (metrics and Table 1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/pmc-patients/pmc-patients/main/README.md"
    title: "Official PMC-Patients GitHub README"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/zhengyun21/PMC-Patients/raw/main/README.md"
    title: "zhengyun21/PMC-Patients card (CC-BY-NC-SA-4.0, V2 note)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/zhengyun21/PMC-Patients"
    title: "PMC-Patients Hub API (license tag cc-by-nc-sa-4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/zhengyun21/PMC-Patients-ReCDS/raw/main/README.md"
    title: "ReCDS benchmark card (11.7M PAR corpus; 155.2k PPR)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/zhengyun21/PMC-Patients-ReCDS"
    title: "ReCDS Hub API"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-079 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

PMC-Patients asks a retriever to help with a written case, not to diagnose it. The query is an English patient summary mined from a PubMed Central case report. Patient-to-article retrieval (PAR) must rank PubMed records that the citation graph treats as relevant. Patient-to-patient retrieval (PPR) must rank other summaries treated as similar patients.

Relevance is 2 or 1 from citation distance, not a fresh clinician grade. PAR and PPR share the query patients and the train/dev/test split. The format matches [BEIR](beir.md) (queries, corpus, qrels) but this suite is not one of BEIR's 18 core datasets.

## How it is scored

The paper and homepage use MRR, precision at 10, nDCG at 10, and recall at 1,000, reported as percentages. Official `evaluation.py` consumes a BEIR-style JSON of query-to-document scores. The live HTML table (retrieved 2026-09-08) still ranks DPR (SciMult-MHAExpert) first on PAR at 29.89 MRR / 9.35 P@10 / 13.79 nDCG@10 / 53.71 R@1k (25 June 2023). PPR is led by reciprocal rank fusion at 27.76 / 6.96 / 24.12 / 85.14 (5 April 2023). BM25 is sixth on PAR and third on PPR on that board.

## Dataset and licence

The Nature descriptor (18 December 2023) counts 167,034 summaries that pass the filters (homepage and GitHub round to 167k), plus 3.1M article links and 293k patient links. Hugging Face `zhengyun21/PMC-Patients` and `zhengyun21/PMC-Patients-ReCDS` both tag CC-BY-NC-SA-4.0. The Nature article text is CC BY 4.0; the authors built the redistributable set only from PMC OA papers with at least CC BY-NC-SA. Test qrels are public. A 2024 V2 dump adds 250,294 patients and is not the ReCDS split.

Nature, the GitHub README, and the ReCDS card all put the PAR corpus at 11.7 million PubMed title/abstract records. arXiv 2202.13876 Table 1 listed 1.4 million candidate articles. Use the Nature/GitHub figure for the published benchmark.

## Who publishes it

Zhengyun Zhao, Qiao Jin, Fangyuan Chen, Tuorui Peng, and Sheng Yu (Tsinghua). Scientific Data 10:909, received 3 July 2023, published 18 December 2023. Leaderboard submissions go by email to the contact on the GitHub README. Code and data: `github.com/pmc-patients/pmc-patients`. Collection code also sits at `zhao-zy15/PMC-Patients`.

## Lineage

This is a clinical retrieval suite, not a QA set like [PubMedQA](pubmedqa.md) or [MedQA](medqa.md). It borrows BEIR packaging. It is unrelated to PMC-OA, which is a figure-caption pretraining dump. No successor page exists here. PMC-Patients-V2 enlarges the note collection; it does not replace the ReCDS leaderboard.

## Saturation and contamination

PAR MRR still sits near 30 on the public board, so the ceiling is open. The table looks stale: nothing newer than MedCPT-d (4 October 2023) appears in the HTML. Notes and labels have been public since 2023, so web-scale models may have seen them. Risk is medium.

## How to run it

Download ReCDS from Hugging Face or Figshare, keep the `datasets` folder, dump ranked results as JSON, then `python evaluation.py --task PAR --split test --result_path ...` (or `PPR`). Submit to the homepage by email. No lm-eval, HELM, inspect_evals, or OpenCompass task name was found. Compare only runs that use the same PAR corpus size (11.7M vs the older 1.4M table).

## Reading the numbers

A 30 MRR on PAR means the first relevant article is still often far down a 11.7M-document list. That is citation-graph retrieval, not clinical correctness. P@10 under 10 on the leading PAR row shows that a short page of hits is usually mixed. Look at PPR separately: lexical fusion still wins that board. Do not treat V2's 250k notes as a new official test.
