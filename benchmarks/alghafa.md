---
id: alghafa
name: "AlGhafa"
aliases:
  - "AlGhafa Evaluation Benchmark"
  - "AlGhafa-Arabic-LLM-Benchmark-Native"
  - "arabic_leaderboard_alghafa"
page_kind: benchmark
category: composite
subcategory: "Arabic multiple-choice suite (reading, exams, sentiment, dialect identification)"
status: active
summary: "TII's Arabic multiple-choice suite; HELM and OALL score nine native Hugging Face configs with public answers, not the translated COPA/OpenBookQA extras."
measures: >
  AlGhafa is a multiple-choice evaluation for Arabic language models. A model sees an Arabic
  query and labelled options, then must pick the correct option. The native packaging mixes
  reading (Belebele MSA and dialects, SOQAL, XGLUE-MLQA), school exams, AraFacts true/false,
  hotel-review sentiment, and Twitter sentiment. It is Arabic text, not [arabic_mmlu](arabic_mmlu.md)
  (natively sourced school exams by subject) and not the English originals those reading sets
  come from.
task_format: >
  Multiple-choice with two to five options depending on the subset (true/false, 3-way sentiment,
  4-way exams/Belebele, 5-way SOQAL/XGLUE). HELM uses joint generation with Arabic letter prefixes
  (أ–هـ) and exact_match. lm-evaluation-harness OALL configs score log-likelihood accuracy (acc
  and acc_norm) on the same Native configs.
metric:
  name: "exact_match (HELM); acc / acc_norm (lm-evaluation-harness OALL group)"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Option arity is not uniform, so there is no single chance rate. HELM's Arabic schema headline
    is exact_match on the test split. The lm-eval group arabic_leaderboard_alghafa reports a
    size-weighted mean of acc and acc_norm across nine Native configs. OALL/v2_results scores
    eight Native configs (no mcq_exams) plus a separate arabic_exams task. Those protocols need
    not agree.
dataset:
  size: 22932
  size_note: >
    HELM pins OALL/AlGhafa-Arabic-LLM-Benchmark-Native revision
    a31ebd34ca311d7e0cfc6ad7f458b3435af280f5. Hugging Face datasets-server test counts:
    mcq_exams_test_ar 557, meta_ar_dialects 5395, meta_ar_msa 895,
    multiple_choice_facts_truefalse_balanced_task 75,
    multiple_choice_grounded_statement_soqal_task 150,
    multiple_choice_grounded_statement_xglue_mlqa_task 150,
    multiple_choice_rating_sentiment_no_neutral_task 7995,
    multiple_choice_rating_sentiment_task 5995, multiple_choice_sentiment_task 1720 (sum 22,932),
    plus 5 validation items per config (45). The Native README and the ArabicNLP 2023 paper
    instead quote 2,248 MCQ Exams items (HF has 562 including validation, matching
    [arabic_exams](arabic_exams.md)), and they list COPA Ar and OpenbookQA Ar, which are not
    Native configs (they sit in OALL/AlGhafa-Arabic-LLM-Benchmark-Translated).
  url: "https://huggingface.co/datasets/OALL/AlGhafa-Arabic-LLM-Benchmark-Native"
  license: ""
  languages:
    - ar
  modalities:
    - text
  splits: "per config: test plus a 5-item validation split (HELM maps validation to train)"
  public_test_set: true
publisher:
  org: "Technology Innovation Institute (TII); dataset hosted by OALL"
  authors:
    - "Ebtesam Almazrouei"
    - "Ruxandra Cojocaru"
    - "Michele Baldo"
    - "Quentin Malartic"
    - "Hamza Alobeidli"
    - "Daniele Mazzotta"
    - "Guilherme Penedo"
    - "Giulia Campesan"
    - "Mugariya Farooq"
    - "Maitha Alhammadi"
    - "Julien Launay"
    - "Badreddine Noune"
  url: "https://aclanthology.org/2023.arabicnlp-1.21/"
paper:
  title: "AlGhafa Evaluation Benchmark for Arabic Language Models"
  arxiv: ""
  url: "https://aclanthology.org/2023.arabicnlp-1.21/"
  year: 2023
leaderboard_url: "https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard"
repo_url: "https://gitlab.com/tiiuae/alghafa"
released: "2023-12"
last_updated: "2024-03"
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
    No dated numeric top score was read from a rendered leaderboard (OALL and HELM Arabic pages
    are JavaScript apps). The paper reports 2023-era TII models on these tasks; those figures are
    not a current ceiling.
contamination:
  risk: high
  note: >
    Test queries and labels are public on Hugging Face (Native card created 2024-02-03; paper
    December 2023). Several subsets reuse older public sources (Belebele, EXAMS, AraFacts, HARD,
    SOQAL, MLQA). No canary or held-out answer file is described.
harness:
  lm_eval: "arabic_leaderboard_alghafa"
  inspect_evals: ""
  helm: "alghafa"
  opencompass: ""
  bigbench: ""
  other: "HELM run names alghafa:subset=<config>. lm-eval also has copa_ar (Hennara/copa_ar) and piqa_ar (Hennara/pica_ar) under tasks/alghafa/; those are translated COPA/PIQA, not the Native suite. OALL v2_results uses eight Native configs and omits mcq_exams from the AlGhafa average."
tags:
  - arabic
  - multiple-choice
  - helm
  - oall
  - reading-comprehension
  - sentiment
sources:
  - url: "https://aclanthology.org/2023.arabicnlp-1.21/"
    title: "AlGhafa paper (ArabicNLP 2023; ACL Anthology HTML)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2023.arabicnlp-1.21.pdf"
    title: "AlGhafa PDF (Appendix C task list and counts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OALL/AlGhafa-Arabic-LLM-Benchmark-Native/raw/main/README.md"
    title: "Native dataset card (task list and claimed counts)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=OALL/AlGhafa-Arabic-LLM-Benchmark-Native"
    title: "datasets-server per-config test/validation example counts"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/OALL/AlGhafa-Arabic-LLM-Benchmark-Native"
    title: "Hugging Face dataset API (created 2024-02-03, revision a31ebd34…)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/alghafa_scenario.py"
    title: "HELM AlGhafaScenario (Native dataset, pinned revision, exact_match metadata)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/arabic_run_specs.py"
    title: "HELM alghafa run spec (joint MCQ, Arabic prefixes, EXPERIMENTAL)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_arabic.yaml"
    title: "HELM schema_arabic.yaml (alghafa group, main_name exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_arabic.conf"
    title: "HELM Arabic run entries (nine Native subsets, max_train_instances=0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/arabic_leaderboard_complete/arabic_leaderboard_alghafa/arabic_leaderboard_alghafa.yaml"
    title: "lm-eval group arabic_leaderboard_alghafa (nine Native tasks, size-weighted acc)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=OALL/AlGhafa-Arabic-LLM-Benchmark-Translated"
    title: "Translated sibling dataset (COPA/OpenBookQA and other MT tasks)"
    accessed: "2026-09-08"
  - url: "https://gitlab.com/tiiuae/alghafa/-/raw/main/README.md"
    title: "TII GitLab AlGhafa README (paper counts; no licence field)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OALL/v2_results"
    title: "OALL v2_results schema (eight Native AlGhafa configs; no mcq_exams; alrage_qa)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/alghafa/copa_ar/copa_ar.yaml"
    title: "lm-eval copa_ar (Hennara/copa_ar, not Native)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/alghafa/piqa_ar/piqa_ar.yaml"
    title: "lm-eval piqa_ar (Hennara/pica_ar, not Native)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-025 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-025"
---

## What it measures

AlGhafa asks an Arabic model to choose among short written options. The native Hugging Face package covers reading passages (Belebele in MSA and in dialects, SOQAL, an XGLUE-MLQA rewrite), Arabic exam items, balanced AraFacts claims, and sentiment from hotel reviews and tweets. HELM and the lm-eval OALL group run all nine Native configs. Live OALL v2 averages eight of those configs and scores exams separately. The skill mix is Arabic reading plus everyday classification, not one subject exam. It is not [arabic_mmlu](arabic_mmlu.md), and it is not the English Belebele or EXAMS pages.

## How it is scored

HELM's `alghafa` run spec uses joint multiple-choice generation with Arabic option letters and scores exact_match on the test split. Official Arabic run entries set `max_train_instances=0`, so those HELM numbers are zero-shot generations, not log-likelihood ranking. The lm-evaluation-harness group `arabic_leaderboard_alghafa` instead ranks option likelihoods and reports size-weighted `acc` and `acc_norm` over nine Native configs. OALL `v2_results` scores eight Native configs (no `mcq_exams_test_ar`) and keeps exams in `arabic_exams`. Do not treat a HELM exact_match, an lm-eval nine-config mean, and an OALL v2 eight-config mean as the same quantity.

## Dataset and licence

Count the Native test rows if you are comparing HELM or OALL: 22,932 test items plus 45 five-item validation splits, from datasets-server. Labels and options are public. The 2023 paper and the Native README still advertise 2,248 MCQ Exams items and include COPA Ar and OpenbookQA Ar; the Native configs contain 562 exam rows including validation (the same size as [arabic_exams](arabic_exams.md)) and have no COPA or OpenBookQA configs. Those two live on `OALL/AlGhafa-Arabic-LLM-Benchmark-Translated`. No licence field is set on the Native card, the paper PDF, or the GitLab README opened here, so licence is not established.

## Who publishes it

The ArabicNLP 2023 paper is by Ebtesam Almazrouei, Ruxandra Cojocaru, Michele Baldo, Quentin Malartic, Hamza Alobeidli, Daniele Mazzotta, Guilherme Penedo, Giulia Campesan, Mugariya Farooq, Maitha Alhammadi, Julien Launay, and Badreddine Noune at the Technology Innovation Institute in Abu Dhabi (December 2023, pages 244–275). The evaluation copy HELM pins is the OALL Native dataset (created 3 February 2024; last modified 7 March 2024). TII also keeps a GitLab tree at tiiuae/alghafa. Stanford CRFM wraps it as an experimental Arabic HELM scenario.

## Lineage

AlGhafa reuses older public sets rather than writing a new exam from scratch. [arabic_leaderboard_complete](arabic_leaderboard_complete.md) is an lm-eval aggregation that includes this Native nine-config group among 14 groups; that page is a leaderboard snapshot, not a second AlGhafa. OALL `v2_results` still scores Native AlGhafa configs beside ArabicMMLU, arabic_exams, MadinahQA, AraTrust, human-translated MMLU, and [alrage](alrage.md). That v2 AlGhafa average uses eight Native configs and omits `mcq_exams_test_ar` (exams sit in separate `arabic_exams`). Translated COPA and PIQA also appear under lm-eval `tasks/alghafa/` as `copa_ar` and `piqa_ar` on Hennara hosts; those are not HELM's Native run.

## Saturation and contamination

No current top cell was read from a rendered board. Contamination risk is high: answers are public, several source datasets predate 2023, and there is no held-out private test. A strong score may reflect training-set overlap with Belebele, EXAMS, HARD, or tweet sentiment as much as new Arabic skill.

## How to run it

HELM: `alghafa:subset=<Native config>` from `arabic_run_specs.py`, with the nine names listed in `run_entries_arabic.conf`. The scenario is marked EXPERIMENTAL; HELM itself entered maintenance mode on 1 June 2026. lm-eval: group `arabic_leaderboard_alghafa` (nine `arabic_leaderboard_alghafa_*` tasks on `OALL/AlGhafa-Arabic-LLM-Benchmark-Native`). Live OALL v2 uses eight Native configs and a separate `arabic_exams` task. Inspect Evals and OpenCompass were not confirmed to ship this suite.

## Reading the numbers

A high Native AlGhafa score means the model picked the labelled option on this public Arabic mix, under one of several incompatible protocols. It does not mean the model can write Arabic, retrieve Arabic documents ([alrage](alrage.md)), or pass [arabic_mmlu](arabic_mmlu.md). Sentiment subsets dominate the item count, so a size-weighted mean can hide weak reading. Check whether exams were in the AlGhafa average or scored as `arabic_exams`, whether COPA/OpenBookQA were added from the Translated repo, and whether the reporter used generation or log-likelihood.
