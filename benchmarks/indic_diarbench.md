---
id: indic_diarbench
name: "Indic DiarBench"
aliases:
  - "IndicDiarBench"
  - "sarvamai/indic-diarbench"
page_kind: benchmark
category: multimodal
subcategory: "joint speaker diarization and speaker-attributed ASR for 22 scheduled Indian languages"
status: active
summary: "Joint diarization and speaker-attributed ASR across all 22 scheduled Indian languages on about 108 hours of overlapping multi-speaker audio."
measures: >
  Indic DiarBench tests whether a speech system can transcribe Indian conversational audio
  and assign each word to the right speaker at the same time. Items are natural multi-speaker
  recordings, not read prompts. They include English code-mixing, dialectal variation, and
  overlapping talk. The suite spans all 22 scheduled Indian languages under three acoustic
  conditions: near-field virtual meetings, far-field distant microphones, and in-the-wild
  YouTube conversations. It measures speaker-attributed ASR, not isolated single-speaker
  recognition and not diarization without transcripts.
task_format: >
  Audio in (16 kHz mono WAV). The system must emit time-aligned, speaker-labelled transcripts.
  All systems in the paper were given the same single-channel mixed audio. Diarization-only
  models such as Pyannote are excluded because they do not produce joint ASR output.
metric:
  name: "DER (no forgiveness collar, overlap included); cpWER and WDER reported alongside"
  direction: lower_is_better
  unit: "%"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Lower is better on all three metrics. DER is acoustic diarization error. cpWER is
    concatenated minimum-permutation word error after resolving speaker permutation.
    WDER is the share of aligned words given to the wrong speaker. Annotators produce both
    a native-script transcript and a normalized form (English in Roman script, Arabic
    numerals); both are accepted when computing word error so script convention is not
    penalized. No human transcriber baseline percentage is reported.
dataset:
  size: 1164
  size_note: >
    Hugging Face datasets-server reports 1,164 rows across 22 language configs, all test
    splits, summing to the card's "1,164 samples". Duration is about 108 hours (53.2 near-field,
    26.8 far-field, 27.6 in-the-wild). The 1,164 clips come from 590 source recordings; 47
    recordings contribute more than one clip. Meeting speakers: 485 people from 189 districts.
    In-the-wild: about 750 speakers across 10 languages. Average overlap 12.8%. Speakers per
    session 2-9. Far-field covers the eight largest languages; in-the-wild covers ten. The
    other languages are near-field only.
  url: "https://huggingface.co/datasets/sarvamai/indic-diarbench"
  license: "CC-BY-4.0"
  languages:
    - as
    - bn
    - brx
    - doi
    - gu
    - hi
    - kn
    - ks
    - kok
    - mai
    - ml
    - mni
    - mr
    - ne
    - or
    - pa
    - sa
    - sat
    - sd
    - ta
    - te
    - ur
  modalities:
    - audio
    - text
  splits: "22 language configs, each with a test split only; designed for evaluation, not training"
  public_test_set: true
publisher:
  org: "Sarvam AI; AI4Bharat, IIT Madras"
  authors:
    - "Deovrat Mehendale"
    - "Aditya Mehndiratta"
    - "Dhruv Rathi"
    - "Kaushal Bhogale"
    - "Mitesh M. Khapra"
  url: "https://huggingface.co/datasets/sarvamai/indic-diarbench"
paper:
  title: "Indic DiarBench: A Multilingual Joint Diarization and ASR Benchmark for Indian Languages"
  arxiv: "2607.23808"
  url: "https://arxiv.org/abs/2607.23808"
  year: 2026
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/sarvamai/indic-diarbench"
released: "2026-07"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 16.0
  as_of: "2026-07"
  note: >
    Best duration-weighted DER in the paper and dataset card is 16.0% for the Indic-specialized
    Sarvam pipeline, with cpWER 38.8% and WDER 33.1%. AWS Transcribe is the strongest commercial
    API at 23.5% DER and 43.7% cpWER. GPT-4o is 36.2% DER and 83.1% cpWER. Gemini 3 Pro has
    74.0% DER despite a competitive 58.9% cpWER. None of these is near zero error. Grey cells
    in the per-language heatmap mark unsupported languages, so unweighted language averages
    are skewed.
contamination:
  risk: medium
  note: >
    Audio and human transcripts have been public on Hugging Face since July 2026 under
    CC BY 4.0, with no held-out answer key. The set is labelled evaluation-only, not a
    training corpus. Risk is not rated high because the release is recent and the task is
    full conversational audio rather than short memorisable strings, but a later speech
    model could have seen the clips or YouTube sources.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No lm-eval, inspect_evals, HELM, OpenCompass, or BIG-bench task was found. Load language configs from sarvamai/indic-diarbench and score joint ASR+diarization with DER (no collar), cpWER, and WDER on mixed single-channel audio."
tags:
  - asr
  - diarization
  - indic
  - speech
  - multilingual
  - audio
  - code-mixing
sources:
  - url: "https://arxiv.org/abs/2607.23808"
    title: "Indic DiarBench (Mehendale, Mehndiratta, Rathi, Bhogale, Khapra, arXiv:2607.23808)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2607.23808"
    title: "Indic DiarBench HTML full text (evaluation setup, Table 3, Figure 2)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2607.23808.pdf"
    title: "Indic DiarBench PDF"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/sarvamai/indic-diarbench"
    title: "sarvamai/indic-diarbench dataset card (CC BY 4.0, 1,164 samples, baselines)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/sarvamai/indic-diarbench/raw/main/README.md"
    title: "indic-diarbench README.md"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/sarvamai/indic-diarbench"
    title: "Hugging Face dataset API metadata (created 2026-07-25, licence cc-by-4.0)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=sarvamai/indic-diarbench"
    title: "datasets-server per-language test split row counts (sum 1,164)"
    accessed: "2026-09-08"
  - url: "https://www.sarvam.ai/blogs/indic-diarbench"
    title: "Sarvam AI blog: Indic DiarBench dataset and metric definitions"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-077 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Indic DiarBench asks a speech system to write down who said what in Indian multi-speaker audio. The input is a mixed single-channel recording. The output is a time-aligned transcript with speaker labels. That is a different job from single-speaker ASR on IndicVoices-style read speech, and from diarization that never emits words.

The corpus covers all 22 scheduled Indian languages, about 108 hours, across near-field meetings (one close mic per remote participant), far-field distant mics, and in-the-wild YouTube conversations. Overlap averages 12.8%. Sessions have two to nine speakers. English code-mixing is common. The authors built it because earlier Indic diarization work (DISPLACE) either skipped ASR labels or scored ASR on cleaner single-speaker audio.

## How it is scored

Three metrics, all lower-is-better. DER uses no forgiveness collar and counts overlapping speech. cpWER measures transcription after the best speaker permutation. WDER isolates speaker-attribution errors on aligned words. Native-script and normalized transcripts are both accepted at scoring time.

The paper and Hugging Face card report the same duration-weighted table. The Indic-specialized Sarvam pipeline is best: 16.0% DER, 38.8% cpWER, 33.1% WDER. AWS Transcribe leads the commercial APIs (23.5% DER, 43.7% cpWER). Gemini 3 Pro has a poor 74.0% DER (41.7% missed detection) but 58.9% cpWER and 33.0% WDER when segments are found. GPT-4o is stronger on diarization than Gemini (36.2% DER) and much weaker on words (83.1% cpWER). Not every vendor supports every language; grey heatmap cells are missing coverage, so a simple mean over languages is misleading.

## Dataset and licence

Hugging Face datasets-server counts 1,164 test rows across 22 configs, matching the card. Those clips are not independent: they come from 590 source recordings. Group by `recording_id` if you split or average. Near-field covers all 22 languages. Far-field covers eight. In-the-wild covers ten and has no speaker IDs. The authors say the set is for evaluation, not training.

Annotation is human-in-the-loop: multi-ASR drafts, professional time-aligned speaker transcripts, dual code-mixed scripts, language-wise quality checkers, then in-house expert review. The Hugging Face card and the paper both state CC BY 4.0. The arXiv HTML is also CC BY 4.0.

## Who publishes it

Deovrat Mehendale, Aditya Mehndiratta, and Dhruv Rathi (equal contribution) are at Sarvam AI. Kaushal Bhogale and Mitesh M. Khapra are at AI4Bharat, IIT Madras. The dataset appeared on Hugging Face on 25 July 2026; arXiv v1 is dated 26 July 2026. The card and Sarvam blog say the paper is for Interspeech 2026. Hugging Face lastModified is 11 August 2026. There is no separate live leaderboard.

## Lineage

The paper compares AMI, CALLHOME, DIHARD III, VoxConverse, LibriCSS, AliMeeting, NOTSOFAR-1, and DISPLACE 2023/2024. DISPLACE is the closest Indic predecessor, but the 2024 ASR track used a separate cleaner single-speaker subset and covered only five Indic languages with joint labels. IndicVoices and Lahaja are cited as single-speaker or accent ASR resources, not joint diarization. None of those have pages in this repository yet. This page is not [IndicXNLI](indicxnli.md) or [INDIC-DIALECT](indic_dialect.md).

## Saturation and contamination

The benchmark is open. Even the best pipeline leaves 16% DER and almost 39% cpWER. High-overlap languages such as Telugu, Maithili, and Dogri are harder. Dravidian near-field cpWER sits about five points above Indo-Aryan at similar DER. Multimodal LLMs are not close to replacing a speech stack.

Contamination risk is medium. The test audio and transcripts are public. YouTube sources could appear in other crawls. The release is recent and labelled eval-only, so it is not treated as a long-public exam set.

## How to run it

Load a language config from `sarvamai/indic-diarbench` (for example Hindi, split `test`). Feed mixed mono audio. Score DER without a collar, plus cpWER and WDER, using the human segments as reference. No lm-eval, inspect_evals, HELM, OpenCompass, or BIG-bench task name was found. Compare duration-weighted aggregates, not unweighted language means, and do not average clips without grouping `recording_id`.

## Reading the numbers

A low DER with high cpWER means the system found speakers but not words. The reverse, as with Gemini 3 Pro, means decent transcription on the spans it kept and broken segmentation. Sarvam's 16% DER is the current published floor, not a saturated ceiling. Always name the metric, the language set, and the acoustic condition. A Hindi near-field number is not a 22-language far-field number. Grey "unsupported language" cells mean that vendor should be left out of that language's comparison rather than scored as perfect or as zero.
