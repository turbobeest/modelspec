---
id: ro_n3ws
name: RO-N3WS
aliases: []
page_kind: benchmark
category: domain
subcategory: "Romanian automatic speech recognition"
status: proposed
summary: >
  A 126-hour Romanian ASR set that trains on broadcast news and tests on news plus
  audiobook, film, story, and podcast speech, scored by word error rate.
measures: >
  RO-N3WS measures Romanian speech-to-text under domain shift. The in-domain half is
  studio and field news from ProTV and Antena 1 (Observator). The out-of-distribution
  half is literary audiobooks, Romanian film dialogue, children's stories, and podcasts.
  Clips are short, usually under ten seconds. Transcripts restore diacritics, expand
  spoken numbers, and keep named entities as pronounced. The skill is transcription
  robustness, not dialogue or translation.
task_format: >
  A Romanian audio clip in; the system returns a word sequence. WER is computed against
  a manually corrected transcript, with extra references for number and punctuation
  variants on commercial APIs.
metric:
  name: "word error rate (WER)"
  direction: lower_is_better
  unit: "%"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    WER is insertions, deletions, and substitutions over reference length. Commercial
    API outputs were stripped of punctuation and case before scoring. No human WER
    baseline was reported.
dataset:
  size: 74134
  size_note: >
    74,134 clips: 62,392 in-domain news files (32,319 ProTV, 30,073 Observator/Antena 1)
    totalling 105 hours, plus 11,742 OOD files (about 21 hours: 4.2 h audiobooks, 8.2 h
    films, 4.4 h stories, 3.3 h podcasts). Abstract and Table 1 round the whole set as
    over 126 hours. In-domain splits are 53,049 train (~89.4 h), 6,219 validation
    (~10.4 h), and 3,124 test (~5.3 h), stratified in 20 folds without splitting a
    source video across folds.
  url: ""
  license: ""
  languages:
    - ro
  modalities:
    - audio
  splits: "in-domain train/validation/test plus OOD evaluation-only subsets"
  public_test_set: false
publisher:
  org: "Department of Computer Science, University of Bucharest"
  authors:
    - Alexandra Diaconu
    - Mădălina Vînaga
    - Bogdan Alexe
  url: "https://arxiv.org/abs/2603.02368"
paper:
  title: "RO-N3WS: Enhancing Generalization in Low-Resource ASR with Diverse Romanian Speech Benchmarks"
  arxiv: "2603.02368"
  url: "https://arxiv.org/abs/2603.02368"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 2.9
  as_of: "2026-03"
  note: >
    Lower WER is better. Whisper Large fine-tuned on RO-N3WS reached 2.9% on ProTV and
    4.4% on Antena 1 (Table 7). Microsoft Transcribe matched 2.9% ProTV in zero-shot
    (Table 6). OOD film WER stays high: 27.3% zero-shot Whisper Large and 31.7% after
    RO-N3WS fine-tuning. In-domain news is much closer to ceiling than films.
contamination:
  risk: medium
  note: >
    Source audio is public broadcast sites and YouTube. The cleaned splits and gold
    transcripts were not found in a public dump; the paper says they will be released
    on acceptance. Whisper first-pass transcripts were used, then 15 annotators with
    dual review. A model trained on the same raw YouTube news could look strong without
    using this split.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No public scripts, Hugging Face dataset, or standard LLM harness task were found.
    The paper evaluates Whisper Small/Large, Wav2Vec 2.0 (facebook/wav2vec2-base-10k-voxpopuli-ft-ro),
    Whisper Small + Echo, and zero-shot commercial APIs (Vatis, Microsoft Transcribe,
    Google Chirp/USM).
tags:
  - asr
  - speech
  - romanian
  - domain-shift
  - low-resource
sources:
  - url: "https://arxiv.org/abs/2603.02368"
    title: "RO-N3WS arXiv abstract (v1, 2 Mar 2026)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2603.02368v1"
    title: "RO-N3WS HTML full text, arXiv 2603.02368v1"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-080 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

RO-N3WS is a Romanian ASR test. Models transcribe short clips from two news channels, then from audiobooks, films, children's stories, and podcasts. The news half is the training domain. The rest is a domain-shift test. Clips keep named entities, diacritics, and spoken-number expansions, so WER also punishes formatting unless the scorer uses extra references.

The language is Romanian. The input is audio only. The output is text. It is not a spoken-language-understanding or translation benchmark.

## How it is scored

The metric is word error rate, lower is better. The paper reports ProTV and Antena 1 separately even though both are news. Commercial APIs were normalized for case and punctuation; remaining number-format clashes still inflate WER, so the authors keep extra references.

Table 6 is zero-shot. Whisper Large reached 12.3% ProTV and 5.9% Antena 1, and 14.8% / 27.3% / 10.9% / 11.7% on audiobooks, films, stories, and podcasts. Microsoft Transcribe reached 2.9% ProTV and 4.8% Antena 1. Vatis reached 5.2% and 4.4%. Table 7 is after fine-tuning on RO-N3WS. Whisper Large then reached 2.9% and 4.4% in-domain, but 31.7% on films. Whisper Small improved from 31.6% to 4.1% on ProTV. Fine-tuning on only one news source transferred poorly to the other.

## Dataset and licence

After cleaning, there are 74,134 files and about 126 hours. In-domain news is 105 hours (54.5 h ProTV, 50.5 h Antena 1). OOD is about 21 hours. Raw scrapes were larger: 207 hours before dropping overlap, music, ads, and bad Whisper segments. Fifteen annotators corrected Whisper drafts, two per file. Train / validation / test are 85% / 10% / 5% of in-domain audio, 20 folds, no video shared across folds. OOD is evaluation-only. The paper is CC BY 4.0. Dataset licence is not stated. Data, models, and scripts were promised on acceptance and were not found.

## Who publishes it

Alexandra Diaconu, Mădălina Vînaga, and Bogdan Alexe at the University of Bucharest Department of Computer Science posted the paper on 2 March 2026. There is no repository or leaderboard URL yet.

## Lineage

RO-N3WS sits next to other Romanian speech sets the paper tables: Common Voice, VoxPopuli, FLEURS, SWARA, RSC, and Echo. Those are mostly read or parliamentary speech. Echo is larger (378 h) but still scripted crowd-sourcing. This page is not RO-Bench, the video robustness benchmark. No sibling Romanian ASR page was found in this repository.

## Saturation and contamination

In-domain news WER is already in the low single digits for the best systems. Film OOD is not. A 2.9% ProTV number does not imply robustness. Source shows are public, so a model could have heard the same broadcasts. The authors' cleaned gold files are not public yet, which currently limits direct test-set scrape.

## How to run it

There is no public loader. The paper's recipe is: fine-tune Whisper or Wav2Vec 2.0 on the in-domain train and validation folds, then report WER on ProTV, Antena 1, and the four OOD sets. Do not average the two news tests if you want to match Table 6–7. No lm-eval or inspect_evals task was found. Until the promised dump appears, numbers can only be compared to the paper's own tables.

## Reading the numbers

A low in-domain WER means the model matches this news style, including numbers written as words. It does not mean the model handles overlapping film dialogue. Fine-tuning on RO-N3WS can raise some OOD WER (Whisper Large stories: 10.9% zero-shot versus 14.0% after fine-tuning), so report both. Commercial APIs are zero-shot only here. Compare with Echo or Common Voice Romanian only if the transcript conventions match.
