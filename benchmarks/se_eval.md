---
id: se_eval
name: SE-Eval
aliases:
  - SE-Eval
page_kind: benchmark
category: multimodal
subcategory: "speech editing quality: MOS, boundary naturalness, and contextual consistency"
status: proposed
summary: >
  Human-rated speech-editing set of 9,151 clips with 1-5 MOS and consistency labels,
  released as ground truth for scoring speech editors while the ICME 2026 paper stays anonymous.
measures: >
  SE-Eval scores speech editors on local edits, not on full-utterance TTS quality.
  Each item pairs a source clip with a model-edited clip and the source and target
  transcripts. Human raters mark overall quality, join-point naturalness, and whether
  environment, prosody, or emotion stayed consistent after the edit. Audio is English
  speech. The Hub card presents the labels as ground truth for automatic evaluators,
  not as a live leaderboard of new systems.
task_format: >
  A rater hears original and edited speech with the intended transcript and assigns
  1-5 scores on the dimensions that apply to that sub-domain. RealEdit and LongHard
  items carry overall MOS and boundary MOS. Environment, Prosody, and Emotion items
  carry the matching consistency score. Protocol details sit in the still-anonymous
  ICME 2026 paper and are not restated on the dataset card.
metric:
  name: "mean opinion score and consistency scores on a 1-5 scale"
  direction: higher_is_better
  unit: "points (1-5)"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The published numbers are themselves human ratings, not a separate human-attempt
    baseline. final.json stores clip-level values on five 1-5 fields (mos,
    boundary_mos, env_consistency, prosody_consistency, emotion_consistency). Many
    values fall on thirds (for example 1.33), which is consistent with a small rater
    panel being averaged, but the card does not state the panel size. No automatic
    MOS predictor protocol is specified on the Hub page.
dataset:
  size: 9151
  size_note: >
    final.json has 9,151 unique edited clips, matching the card's "9,151 unique
    synthesized clips." The git listing has 9,281 tar_audio wavs and 970 src_audio
    wavs (10,251 wavs). The extra 130 tar files are not in final.json. Sub-domain
    counts in the json are RealEdit 2,863, LongHard 2,929, Emotion 1,144,
    Environment 1,109, Prosody 1,106. Ten named editors appear; DiffEditor (762)
    and FluentSpeech (753) have fewer labeled clips than VoiceCraft (969). The Hub
    card claims 24.21 hours and 44,451 subjective scores. Summing stored 1-5 fields
    in final.json yields 14,943 values, not 44,451. datasets-server reports a
    102-row default/train split; the API also tags size_categories n<1K from that
    parquet view, while the card YAML says 10K<n<100K.
  url: "https://huggingface.co/datasets/SE-Eval/SE-Eval"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - audio
    - text
  splits: >
    Card describes one evaluation set. Hub datasets-server exposes default/train
    with 102 rows. The git repo holds src_audio, tar_audio, and final.json with
    9,151 labeled clips. No separate validation split is documented.
  public_test_set: true
publisher:
  org: ""
  authors: []
  url: "https://huggingface.co/datasets/SE-Eval/SE-Eval"
paper:
  title: "SE-Eval: A Generative Speech Dataset for Speech Editing Assessment"
  arxiv: ""
  url: "https://huggingface.co/datasets/SE-Eval/SE-Eval"
  year: 2026
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/SE-Eval/SE-Eval"
released: "2026-01"
last_updated: "2026-01"
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
    The release labels ten speech editors. It does not publish a ranked automatic
    metric or a current leaderboard, so ceiling status is not established.
contamination:
  risk: medium
  note: >
    Source and edited wavs plus clip-level scores have been public on Hugging Face
    since January 2026. Source material is drawn from RealEdit, IEMOCAP, ambient
    scenes, and Genshin-style game speech, so those corpora can leak into speech
    models. This is not a text LLM exam with answer keys in pretraining dumps.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No lm-evaluation-harness, inspect_evals, HELM, OpenCompass, or BIG-bench task
    was confirmed. The reference artifact is the Hugging Face dataset. Automatic
    scoring code is not published on the card.
tags:
  - speech-editing
  - mos
  - audio
  - human-ratings
sources:
  - url: "https://huggingface.co/datasets/SE-Eval/SE-Eval"
    title: "SE-Eval dataset card on Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/SE-Eval/SE-Eval"
    title: "Hugging Face datasets API for SE-Eval/SE-Eval"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=SE-Eval/SE-Eval"
    title: "Hugging Face datasets-server info for SE-Eval/SE-Eval"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/SE-Eval/SE-Eval/resolve/main/final.json"
    title: "SE-Eval final.json clip-level labels"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-081 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SE-Eval asks whether a speech editor changed the intended words without wrecking the rest of the clip. The model is not answering a text question. It rewrites a span of English speech. Raters then judge the edit as audio.

Each labeled item names a source wav, an edited wav, and the two transcripts. RealEdit uses everyday recordings. LongHard uses long sentences with rare terms. Environment, Prosody, and Emotion hold ambient, expressive, and affective speech. The skill is local edit quality plus context that should not change.

## How it is scored

Human scores sit on a 1-5 scale. The card lists overall MOS, boundary MOS, and three consistency axes: environment, prosody, and emotion. In `final.json`, RealEdit and LongHard rows carry `mos` and `boundary_mos`. Emotion, Environment, and Prosody rows carry only the matching consistency field.

The Hub text does not define the listening protocol, the number of raters, or an official automatic predictor. Stored values often fall on thirds, which suggests averaged ratings, but that is an inference from the numbers, not a stated rule. Higher is better. There is no published random baseline.

## Dataset and licence

The Hub card, dated for anonymous ICME 2026 review, claims 9,151 unique synthesized clips, 24.21 hours, ten editors, and 44,451 subjective scores. `final.json` has exactly 9,151 records. The licence tag is CC-BY-4.0. Answers and audio are public.

The git tree lists 10,251 wav files: 970 sources and 9,281 edited files. One hundred and thirty edited wavs have no json row. Hugging Face's parquet viewer and datasets-server show 102 train rows and an auto `n<1K` size tag, which does not match the card's `10K<n<100K` tag or the 9,151 json rows. Treat the json as the labeled set and the 102-row viewer as an incomplete audiofolder conversion.

Ten editor names appear: VoiceCraft, higgs, VALLE, MaskGCT, E2-tts, F5-tts, PlayDiffusion, SSR-SPEECH, DiffEditor, and FluentSpeech. Source prefixes follow the five sub-domains on the card.

## Who publishes it

The Hub organisation is `SE-Eval`. The README says author names, affiliations, and grants were stripped for double-blind ICME 2026 review. No arXiv id was attached as of this research date. The API reports `createdAt` 2026-01-01 and `lastModified` 2026-01-24. There is no public leaderboard.

## Lineage

The card positions SE-Eval against generic TTS metrics that miss join-point quality. Source corpora named on the card are RealEdit, IEMOCAP, ambient scenes, and Genshin-style game speech. SpeechEditBench (arXiv 2606.01804) is a later bilingual instruction-guided editing bench with a different protocol; it has no page in this repository. SE-Eval is not a text LLM exam and is not an alias of AIR-Bench.

## Saturation and contamination

No automatic leaderboard is published, so saturation is not established. Human means on stored fields sit in the mid 2s to mid 3s on a 1-5 scale, which is not a ceiling. The test audio and labels have been public since January 2026. Speech models trained on IEMOCAP or game voice lines may have seen related source material. Edited outputs of the ten named systems are also public.

## How to run it

Download `SE-Eval/SE-Eval` from Hugging Face. Use `final.json` for ids, paths, transcripts, and scores. Map Windows-style paths in that file onto `src_audio/` and `tar_audio/`. There is no confirmed lm-eval, inspect_evals, HELM, OpenCompass, or BIG-bench task. Scoring a new editor requires generating edits on the same sources and either collecting new MOS or fitting a predictor; neither recipe is on the card.

## Reading the numbers

A higher MOS means listeners liked that editor's clip more, not that a text LLM is stronger. Compare scores only within a sub-domain, because each clip carries a different subset of axes. Do not treat the 102-row Hub viewer as the dataset size. Do not treat the 44,451 figure as something you can recompute from `final.json` without the paper. Look at which editors are missing clips before ranking them. For instruction-guided or bilingual editing, this set is the wrong instrument.
