---
id: prism
name: "PRiSM"
aliases:
  - "Phone Realization in Speech Models"
page_kind: benchmark
category: multimodal
subcategory: "phone recognition and phonetic downstream probes"
status: active
summary: >
  Open suite for phone recognition: phonetic-feature error on IPA transcripts
  plus clinical, L2, and multilingual probes of speech models.
measures: >
  PRiSM tests whether a speech model hears phones, not words. Intrinsic tasks
  ask for an IPA transcript of an utterance and score articulatory-feature
  edits against gold phones (PFER), rather than token-level phone error rate.
  Extrinsic tasks reuse those transcripts or hidden states on dysarthria
  intelligibility, atypical child speech, L1 classification, L2 assessment,
  language id, geolocation, and phone-inventory induction. The paper argues
  that transcription error alone hides failures on clinical and sociophonetic
  work.
task_format: >
  Audio in, IPA transcript and/or frozen representation out. Hydra configs
  under github.com/changelinglab/prism. Kaldi-style test sets for PR; Hugging
  Face repos for downstream probes.
metric:
  name: "PFER (intrinsic); task F1 / Recall@1 (extrinsic)"
  direction: lower_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Table 1 marks core PFER tasks as lower-is-better and downstream utility as
    higher-is-better. PFER is feature-level edit distance, not PER. F1-PI is
    defined in the appendix. No single official average. The paper reports
    encoder-CTC models as more stable than AED, and specialised PR models
    ahead of LALMs (Gemini 2.5 Flash, Qwen3-Omni) on phonetic probes.
dataset:
  size: null
  size_note: >
    No single item count. Intrinsic PR configs include DoReCo, Speech Accent
    Archive, L2-ARCTIC Perceived, TIMIT, Tusom2021, and VoxAngeles (Appendix A
    lists e.g. TIMIT 6,300; DoReCo 18,734; VoxAngeles 5,445). Extrinsic HF
    repos in collection changelinglab/prism include EasyCall, UltraSuite,
    EdAcc L1, CMU/L2 Arctic L1, SpeechOcean L2, FLEURS-24 LID; Vaani
    geolocation marked unreleased in the README.
  url: "https://huggingface.co/collections/changelinglab/prism"
  license: ""
  languages: []
  modalities:
    - audio
    - text
  splits: "per-source train/dev/test where the upstream corpus defines them"
  public_test_set: true
publisher:
  org: "Changeling Lab / Carnegie Mellon and collaborators"
  authors:
    - "Shikhar Bharadwaj"
    - "Chin-Jou Li"
    - "Yoonjae Kim"
    - "Kwanghee Choi"
    - "Eunjung Yeo"
    - "Ryan Soh-Eun Shim"
    - "Hanyu Zhou"
    - "Brendon Boldt"
    - "Karen Rosero Jacome"
    - "Kalvin Chang"
    - "Darsh Agrawal"
    - "Keer Xu"
    - "Chao-Han Huck Yang"
    - "Jian Zhu"
    - "Shinji Watanabe"
    - "David R. Mortensen"
  url: "https://github.com/changelinglab/prism"
paper:
  title: "PRiSM: Benchmarking Phone Realization in Speech Models"
  arxiv: "2601.14046"
  url: "https://arxiv.org/abs/2601.14046"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/changelinglab/prism"
released: "2026-01"
last_updated: "2026-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    No live leaderboard. The paper's qualitative ranking is that specialised
    PR models beat large audio language models, with POWSM-CTC strongest on
    several representation probes. PFER on seen-language variation remains
    high enough that the suite still separates systems.
contamination:
  risk: medium
  note: >
    Several test sets are long-public (TIMIT is LDC-licensed; DoReCo CC0;
    others CC BY / CC BY-NC). Gold IPA and probe labels are in the collection.
    Risk is medium for models trained on common speech corpora, unknown for
    LALM pretraining.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official Hydra entrypoint: python src/main.py experiment=inference/transcribe_powsm
    or experiment=probing/... on github.com/changelinglab/prism.
tags:
  - speech
  - phonetics
  - audio
  - multilingual
  - asr
sources:
  - url: "https://arxiv.org/abs/2601.14046"
    title: "PRiSM arXiv abs (v1 20 Jan 2026; v2 13 Jul 2026; ACL 2026)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2601.14046"
    title: "PRiSM full text (PFER, Table 1, Appendix A licences)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/changelinglab/prism/main/README.md"
    title: "changelinglab/prism README (HF collection, task table)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/collections/changelinglab/prism"
    title: "Hugging Face collection changelinglab/prism"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-079 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

PRiSM (Phone Realization in Speech Models) is a speech benchmark, not a text exam. A system hears an utterance and must emit an IPA phone string, or offer a frozen representation for a probe. Intrinsic tests compare that string to gold phones with phonetic feature error rate (PFER): edit distance over articulatory features such as voicing, not token-level phone error rate.

Extrinsic tests ask whether those transcripts or hidden states help on clinical and sociolinguistic jobs: dysarthria intelligibility (EasyCall), atypical child speech (UltraSuite), L1 classification, L2 assessment, FLEURS language id, Hindi dialect geolocation, and phone-inventory induction. Audio is the input; English is not the only language.

## How it is scored

Table 1 splits metrics. Core recognition uses PFER (lower is better). Downstream utility uses F1, Recall@1, or F1-PI (higher is better). There is no official macro average. The authors run transcription probes (a small GRU on predicted IPA) and representation probes (MLP on encoder states). They compare encoder-CTC, attention encoder-decoder, and large audio language models with fixed prompts.

The paper's headline comparison is qualitative: diverse training languages help; encoder-CTC is more stable; specialised PR models still beat LALMs on these probes. POWSM-CTC is called out as strongest on several representation tasks. No single top score is published as a leaderboard number.

## Dataset and licence

Data are a union of existing corpora, not one new dump. The README lists Kaldi-style PR sets (DoReCo, Speech Accent Archive, L2-ARCTIC Perceived, TIMIT, Tusom2021, VoxAngeles) and Hugging Face probe repos under `changelinglab/prism`. Appendix A of the paper lists per-source licences (TIMIT LDC; DoReCo CC0; several CC BY or CC BY-NC; Tusom2021 MIT). There is no one SPDX id for the suite. GEO-v (Vaani) was still marked unreleased in the README retrieved 2026-09-08. Gold transcripts for the listed PR sets are public if you hold each source licence.

## Who publishes it

Shikhar Bharadwaj and co-authors including Shinji Watanabe and David R. Mortensen. arXiv 2601.14046, submitted 20 January 2026, revised 13 July 2026, presented at ACL 2026. Code: `github.com/changelinglab/prism`. The README notes acceptance on 7 April 2026.

## Lineage

This page is PRiSM the phone-recognition suite. It is not [PRISM-Bench](prism_bench.md) (text-to-audio-video, arXiv 2609.04867). It is not PRISM the LLM peer-review scorer (arXiv 2605.26730). It is not the PRISM alignment preference dataset. Those share an acronym only. PRiSM sits next to SUPERB-style speech probes rather than replacing them.

## Saturation and contamination

LALMs still lag specialised PR models on the paper's probes, so the suite is open. Several source sets are old and public, so models trained on TIMIT or Common Voice may have seen related audio. Feature-level gold for PFER is newer packaging. Risk is medium.

## How to run it

Clone `changelinglab/prism`, install from `requirements.txt`, download `*-pr` repos into one tree, then `python src/main.py experiment=inference/transcribe_powsm data=powsmeval data.data_dir=...`. Probing uses `experiment=probing/lid_fleurs_powsm` and siblings. No lm-eval or HELM task was found. Compare PFER to F1 only with the paper's split of lower-vs-higher-is-better tasks.

## Reading the numbers

A low PFER means the model is close in articulatory features, not that it would pass a clinical listening test. Downstream F1 can rise from non-phonetic cues in the representation probe. LALM numbers in the paper use the authors' IPA prompts; a different prompt is a different exam. Report intrinsic and extrinsic columns separately, and name the source corpus.
