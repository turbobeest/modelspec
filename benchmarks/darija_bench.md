---
id: darija_bench
name: "DarijaBench"
aliases: []
page_kind: benchmark
category: composite
subcategory: "multi-task Moroccan Darija NLP suite: sentiment analysis, summarization, translation and transliteration"
status: active
summary: "An 11-task, four-way suite of held-out test slices for Moroccan Darija covering sentiment analysis, summarization, translation and transliteration, built for the Atlas-Chat model release."
measures: >
  DarijaBench bundles held-out test portions of pre-existing Darija datasets into four task groups:
  sentiment analysis (5 source datasets), summarization (1), translation (4, across six Darija-MSA/
  English/French directions) and transliteration between Darija written in Arabic script and Arabizi
  written in Latin script (1). It does not test one skill; it is a fixed collection point for
  Darija-specific NLP evaluation, assembled because, as the authors state, standardized Darija
  benchmarks barely existed beforehand. Most component test portions are a 10% held-out split of
  their respective source dataset.
task_format: >
  Format varies by group: sentiment is multiple-class classification (accuracy); summarization is
  free-text generation from a Darija article (ROUGE-1/2/L/Lsum, a BERTScore-style metric, and chrF);
  translation is free-text generation across six directions (BLEU, chrF, TER and a BERTScore-style
  metric); transliteration is free-text script conversion (the same BERTScore-style metric). All are
  zero-shot, single-turn generation tasks with no worked examples in the released harness configs.
metric:
  name: "per-task-group metric (accuracy for sentiment; ROUGE/BERTScore/chrF for summarization; BLEU/chrF/TER/BERTScore for translation; BERTScore for transliteration)"
  direction: higher_is_better
  unit: "mixed (%, points)"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single aggregate DarijaBench number exists; lm-evaluation-harness reports each of the 11
    component tasks separately, with a size-weighted accuracy aggregate only within the
    darija_sentiment group. No random or human baseline was confirmed from a source read for this
    page for any component.
dataset:
  size: 31476
  size_note: >
    31,476 rows total across 11 named Hugging Face splits (confirmed via the Hub API): translation --
    doda 6000, madar 4000, seed 1238, flores_plus 6072 (17,310 total, six translation directions);
    sentiment -- msda 5220, myc 1998, mac 1743, electro_maroc 1024, msac 200 (10,185 total);
    summarization -- marsum 1981; transliteration -- 2000. The dataset card's own prose describes only
    the sentiment, summarization and translation components; the transliteration split and task group
    are confirmed instead from the lm-evaluation-harness README, which the same paper is cited from.
  url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench"
  license: >-
    ODC-BY (top-level mirror licence); the dataset card explicitly warns this is a mixture with
    component-level licences that differ, some non-commercial -- see Dataset and licence.
  languages:
    - ary
    - arb
    - fr
    - en
  modalities:
    - text
  splits: "11 held-out test splits, one per source dataset, grouped into 4 task groups; no train split shipped in this mirror"
  public_test_set: true
publisher:
  org: "MBZUAI-Paris, in a multi-institution collaboration with EMINES-UM6P, LINAGORA, KTH, AtlasIA and École Polytechnique"
  authors:
    - "Guokan Shang"
    - "Hadi Abdine"
    - "Yousef Khoubrane"
    - "Amr Mohamed"
    - "Yassine Abbahaddou"
    - "Sofiane Ennadir"
    - "Imane Momayiz"
    - "Xuguang Ren"
    - "Eric Moulines"
    - "Preslav Nakov"
    - "Michalis Vazirgiannis"
    - "Eric Xing"
  url: "https://huggingface.co/MBZUAI-Paris"
paper:
  title: "Atlas-Chat: Adapting Large Language Models for Low-Resource Moroccan Arabic Dialect"
  arxiv: "2409.17912"
  url: "https://arxiv.org/abs/2409.17912"
  year: 2024
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench"
released: "2024-09"
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
    Not established from a source read for this page. The Atlas-Chat paper reports its own 2B/9B/27B
    models as strong performers on this suite relative to compared open Arabic-specialized models, but
    this page did not extract a directly comparable numeric leaderboard, and no independent leaderboard
    tracking DarijaBench was found.
contamination:
  risk: high
  note: >
    Several components are 10% held-out slices or existing test splits of long-public academic
    datasets (FLORES+, NLLB-Seed's Seed corpus, MADAR, MArSum) whose source material and reference
    translations have circulated publicly for years independent of this mirror, with no held-out
    private portion or canary mechanism found. The mirror itself has been public on Hugging Face
    since September 2024.
harness:
  lm_eval: >-
    No single darija_bench task or group exists; the runnable units are four separate lm-evaluation-harness
    groups under lm_eval/tasks/darija_bench/ -- darija_sentiment, darija_summarization, darija_translation,
    darija_transliteration -- each aggregating further per-source-dataset tasks (e.g.
    darija_sentiment_mac, darija_translation_flores). Confirmed by reading the group and task YAML
    files directly.
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - darija
  - moroccan-arabic
  - low-resource
  - composite
  - sentiment-analysis
  - summarization
  - translation
  - transliteration
sources:
  - url: "https://arxiv.org/abs/2409.17912"
    title: "Atlas-Chat: Adapting Large Language Models for Low-Resource Moroccan Arabic Dialect"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2409.17912"
    title: "Atlas-Chat (full text, ar5iv) -- DarijaBench description and author affiliations"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench"
    title: "MBZUAI-Paris/DarijaBench dataset card, Hugging Face (component licences)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/MBZUAI-Paris/DarijaBench"
    title: "MBZUAI-Paris/DarijaBench, Hugging Face Hub API (split sizes, tags)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/darija_bench/README.md"
    title: "lm-evaluation-harness: darija_bench README (groups, tasks, per-source citations)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/darija_bench"
    title: "lm-evaluation-harness: darija_bench task directory listing"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

DarijaBench is not one task but a fixed collection of held-out test slices, built to give Moroccan Darija -- a widely spoken but, per its authors, chronically under-benchmarked Arabic dialect -- a standardized evaluation surface across four groups: sentiment analysis (from five source datasets), summarization (one), translation (four sources, six directions between Darija, Modern Standard Arabic, French and English) and transliteration between Darija written in Arabic script and "Arabizi" written in Latin script. It was assembled for the Atlas-Chat paper alongside two sibling evaluations not covered by this page, DarijaMMLU and DarijaAlpacaEval. Most components are a 10% held-out split of an existing Darija dataset rather than newly authored data.

## How it is scored

Scoring is entirely per-component: sentiment tasks report classification accuracy (aggregated within the sentiment group by a size-weighted mean); summarization reports ROUGE-1/2/L/Lsum plus a BERTScore-style metric and chrF; translation reports BLEU, chrF, TER and the same BERTScore-style metric across each of its six directions; transliteration reports the BERTScore-style metric alone. There is no single blended DarijaBench score in the reference lm-evaluation-harness implementation -- a model's "DarijaBench result" is really 11 separate numbers unless someone chooses to average them.

## Dataset and licence

The Hugging Face mirror totals 31,476 rows across 11 splits, released under a top-level ODC-BY licence with an explicit warning that this is a mixture: the dataset card states component licences differ and some portions are non-commercial. Reading the card's per-component notes directly: MArSum (summarization) is CC BY 4.0; DODa-10K (translation, and the source for transliteration) is CC BY-NC 4.0, non-commercial; NLLB-Seed and FLORES+ (translation) are CC BY-SA 4.0; MADAR (translation) carries its own separate licence; and the five sentiment sources (MSDA, MSAC, ElecMorocco2016, MYC, MAC) are marked "no licence provided." Anyone redistributing scores or derived data should treat the non-commercial and unlicensed components accordingly rather than applying the top-level ODC-BY tag to the whole set.

## Who publishes it

DarijaBench comes from the Atlas-Chat paper, a 12-author collaboration led by Guokan Shang spanning MBZUAI, EMINES-UM6P, LINAGORA, KTH, AtlasIA and École Polytechnique, posted to arXiv in September 2024. The dataset is hosted and maintained under the MBZUAI-Paris organisation on Hugging Face.

## Lineage

DarijaBench has no predecessor or successor tracked in this repository; it is a purpose-built aggregation rather than a revision of an earlier benchmark. Within the Atlas-Chat evaluation suite it sits alongside DarijaMMLU (a discriminative knowledge benchmark) and DarijaAlpacaEval (an instruction-following comparison), neither of which has its own page here yet. None of DarijaBench's 11 component tasks or 4 task groups have their own pages in this repository either; they are documented only as part of this single page.

## Saturation and contamination

No leaderboard or comparable numeric ceiling was confirmed from a source read for this page, so saturation is not established. Contamination risk is graded high: several components reuse existing test splits of datasets that have been public for years independent of this mirror (FLORES+, the Seed corpus, MADAR, MArSum), with reference answers freely available and no held-out or canary-protected portion found, and the mirror itself has been fully public since September 2024.

## How to run it

There is no single runnable `darija_bench` task; lm-evaluation-harness instead exposes four separate groups -- `darija_sentiment`, `darija_summarization`, `darija_translation`, `darija_transliteration` -- each of which aggregates further per-source tasks (for example `darija_translation_flores`, `darija_sentiment_mac`). The harness README notes results are sensitive to padding side and recommends batch size 1. No HELM, inspect_evals, OpenCompass or BIG-bench implementation was found.

## Reading the numbers

Because DarijaBench reports 11 separate task scores rather than one blended figure, a "DarijaBench result" only means something once you know which group and which source dataset it comes from -- a strong translation score says nothing about sentiment or transliteration performance. Given the mixed and partly non-commercial licensing of its components, also check which sub-datasets a reported number actually draws on before reusing the figure. Because several components reuse long-public test data, a high score is also consistent with prior exposure to the underlying source datasets during pretraining, not only genuine Darija competence.
