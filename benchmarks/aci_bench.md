---
id: aci_bench
name: ACI-Bench
aliases:
  - "ACI-BENCH"
page_kind: benchmark
category: domain
subcategory: "clinical note generation from doctor-patient dialogue"
status: active
summary: Tests whether a model can turn a doctor-patient conversation transcript into a structured clinical note; 207 real dialogue-note pairs, the largest public dataset of its kind at publication.
measures: >
  ACI-Bench (Ambient Clinical Intelligence Benchmark) tests a model's ability to convert a
  transcribed doctor-patient conversation into a structured clinical visit note -- the
  documentation task physicians otherwise do by hand after (or during) every visit. Given a
  dialogue transcript, the model must produce a note covering sections such as history of present
  illness, physical exam findings, results, and assessment and plan. It is single-turn,
  text-to-text, English-language summarisation grounded in real (de-identified or simulated)
  clinical encounters rather than synthetic dialogue.
task_format: >
  Given a full doctor-patient dialogue transcript as input, the model generates free text
  structured as a clinical note with the required section headers. Some transcripts include
  automatic-speech-recognition artefacts, including occasional swapped speaker tags
  ([doctor]/[patient]), which the dataset authors left uncorrected deliberately to reflect a
  realistic, imperfect transcription pipeline rather than clean input.
metric:
  name: "varies by reporter: ROUGE / BERTScore / BLEURT ensemble (original MEDIQA shared tasks) or LLM-jury score (HELM's MedHELM implementation)"
  direction: higher_is_better
  unit: "points (scale depends on method)"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single official metric exists. The MEDIQA-Chat/MEDIQA-Sum shared tasks that used this
    dataset scored submissions with an ensemble of ROUGE, BERTScore and BLEURT chosen to correlate
    with human judgment of note quality. HELM's MedHELM implementation instead uses a documented
    "LLM jury": several annotator models each rate a generated note against the reference on
    accuracy, completeness and clarity, each on a 1-5 scale, averaged into a single "Jury Score"
    (HELM calls this metric aci_bench_accuracy, a naming choice from HELM's own schema rather than a
    correctness/accuracy metric in the usual sense). These two scoring approaches are not
    comparable, so a reported ACI-Bench number should be checked for which one produced it.
dataset:
  size: 207
  size_note: >
    207 total dialogue-note pairs across five splits, per the reference repository's own published
    counts: train 67, valid 20, test1 40 (the MEDIQA-Chat 2023 Task B test set), test2 40 (the
    MEDIQA-Chat 2023 Task C test set), test3 40 (the MEDIQA-Sum 2023 Task C test set). The
    collection is further divided into three sub-workflows: aci (ambient doctor-patient dialogue,
    the largest subset), virtassist (dialogue with spoken triggers for a virtual-assistant feature),
    and virtscribe (dialogue with a short doctor dictation at the start).
  url: https://github.com/wyim/aci-bench
  license: CC BY 4.0
  languages:
    - en
  modalities:
    - text
  splits: "train (67), valid (20), test1 (40), test2 (40), test3 (40)"
  public_test_set: true
publisher:
  org: Microsoft
  authors:
    - Wen-wai Yim
    - Yujuan Fu
    - Asma Ben Abacha
    - Neal Snider
    - Thomas Lin
    - Meliha Yetisgen
  url: https://github.com/wyim/aci-bench
paper:
  title: "Aci-bench: a Novel Ambient Clinical Intelligence Dataset for Benchmarking Automatic Visit Note Generation"
  arxiv: ""
  url: https://www.nature.com/articles/s41597-023-02487-3
  year: 2023
leaderboard_url: ""
repo_url: https://github.com/wyim/aci-bench
released: "2023"
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
    No maintained public leaderboard tracking frontier-model scores over time was found. HELM's
    MedHELM suite reports current model runs on its own site using the LLM-jury metric, but this
    page did not independently confirm a current top score there, and the original shared-task
    leaderboards (MEDIQA-Chat / MEDIQA-Sum 2023) reflect submissions from that specific 2023
    competition rather than an ongoing tracker.
contamination:
  risk: medium
  note: >
    The full dataset, including gold notes, has been publicly available on GitHub and via Figshare
    since the 2023 MEDIQA-Chat and MEDIQA-Sum shared tasks, with no held-out or rotating split
    described for ongoing evaluation, so exact-pair memorisation is plausible for any model trained
    on general web or GitHub-derived data since then.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "aci_bench (part of the MedHELM suite; zero-shot generation, LLM-jury scoring)"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - clinical
  - summarization
  - dialogue
  - domain
sources:
  - url: https://www.nature.com/articles/s41597-023-02487-3
    title: "Aci-bench: a Novel Ambient Clinical Intelligence Dataset for Benchmarking Automatic Visit Note Generation (Yim et al., Nature Scientific Data, 2023)"
    accessed: "2026-09-08"
  - url: https://github.com/wyim/aci-bench
    title: "wyim/aci-bench GitHub repository (README, data splits, licence)"
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/aci_bench_scenario.py
    title: "HELM aci_bench_scenario.py (ACIBenchScenario, MedHELM suite)"
    accessed: "2026-09-08"
  - url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/annotation/aci_bench_annotator.py
    title: "HELM ACIBenchAnnotator (LLM-jury scoring prompt and rubric)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/mkieffer/ACI-Bench
    title: "mkieffer/ACI-Bench dataset card, Hugging Face (third-party mirror with split counts)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ACI-Bench targets one of the most time-consuming parts of a clinical visit: writing up the
encounter as a structured note afterward. Given a transcribed doctor-patient conversation, a model
must produce a note with the standard sections a clinician expects -- history of present illness,
physical exam, results, and assessment and plan -- capturing what was actually said and organising
it the way a chart note is organised, rather than simply summarising the conversation in prose.

The dialogues come from three related workflows: plain ambient doctor-patient conversation (the
`aci` subset), conversation containing spoken triggers meant to invoke a virtual-assistant feature
(`virtassist`), and conversation that opens with a short doctor dictation before the patient
exchange begins (`virtscribe`). Because the transcripts come from real or simulated encounters
processed through automatic speech recognition, some retain ASR artefacts -- including, in places,
swapped `[doctor]`/`[patient]` speaker tags -- which the authors left uncorrected on purpose, to keep
the benchmark realistic rather than clean.

## How it is scored

There is no single official ACI-Bench metric. The dataset originally powered Task B (dialogue-to-
note) and Task C (note-to-dialogue and dialogue-to-note, reusing the same pairs) of the MEDIQA-Chat
and MEDIQA-Sum 2023 shared tasks, which scored submissions with an ensemble of ROUGE, BERTScore and
BLEURT selected by the organisers to correlate with human judgment of summary quality. HELM's later
MedHELM implementation takes a different approach entirely: it prompts the model zero-shot to
generate the four-section note (an average response of about 619 tokens, per HELM's own adapter
configuration), then has several annotator language models independently rate the generated note
against the gold note on accuracy, completeness and clarity, each on a 1-5 scale, described as an
"LLM jury" and averaged into HELM's `aci_bench_accuracy` metric -- a HELM naming convention, not a
literal exact-match accuracy. These are materially different scoring methods, and a reported
ACI-Bench number should always be checked against which one produced it before being compared to
another.

## Dataset and licence

The dataset totals 207 dialogue-note pairs, confirmed against the reference repository's own stated
splits: 67 for training, 20 for validation, and 40 each in three test sets (test1 was MEDIQA-Chat
2023's Task B test set; test2 and test3 were MEDIQA-Chat and MEDIQA-Sum 2023's respective Task C
test sets, reusing dialogue-note pairs from the same underlying collection). The GitHub repository
states the data is published under a CC BY 4.0 licence. A third-party Hugging Face mirror
(`mkieffer/ACI-Bench`) republishes the same splits in parquet form, along with a pointer to
correction scripts for the known ASR speaker-tag-swap issue.

## Who publishes it

ACI-Bench was published by Wen-wai Yim, Yujuan Fu, Asma Ben Abacha, Neal Snider, Thomas Lin and
Meliha Yetisgen in Nature Scientific Data in 2023. Two of the listed authors' contact details in the
reference repository (Yim and Ben Abacha) are Microsoft email addresses, confirming Microsoft as a
publishing organisation; this page did not independently confirm other authors' institutional
affiliations and does not assert them. The reference repository, `wyim/aci-bench`, remains actively
maintained (last updated January 2026 at the time of this research) and is the canonical source for
data, licence and splits.

## Lineage

ACI-Bench has no predecessor benchmark and no successor tracked in this repository. It is one
dataset shared across two related but distinct shared tasks -- MEDIQA-Chat 2023 (paired with the
separate MTS-Dialog dataset for its short-dialogue Task A) and MEDIQA-Sum 2023 -- and is now also
one of several clinical-documentation scenarios inside HELM's broader MedHELM suite, alongside
MTSamples, MedAlign, DischargeMe and others not covered by this page.

## Saturation and contamination

No maintained public leaderboard tracking frontier-model ACI-Bench scores over time was found, and
the two incompatible scoring methods in use (the original ROUGE/BERTScore/BLEURT ensemble vs.
HELM's LLM-jury score) make a single saturation read across sources unreliable, so saturation status
is not established here.

Contamination risk is medium: the full dataset, including gold notes, has been publicly available
via GitHub and Figshare since the 2023 shared tasks, with no held-out or rotating split maintained
for ongoing evaluation, so a model trained on general web or code-hosting data since then has a
plausible chance of having seen these exact transcript-note pairs.

## How to run it

The reference data and challenge-format splits live in `wyim/aci-bench` on GitHub. HELM implements
it as the `aci_bench` scenario inside its MedHELM suite: a zero-shot generation task instructing the
model to produce a four-section note, scored by an LLM jury defined in `ACIBenchAnnotator`
(accuracy, completeness and clarity, each 1-5, averaged across annotator models). No
lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench implementation was confirmed. Because
the original MEDIQA shared-task scoring (ROUGE/BERTScore/BLEURT) and HELM's LLM-jury scoring measure
different things on different scales, results from the two should never be compared directly.

## Reading the numbers

A strong ACI-Bench score means a model reliably pulls the clinically relevant content out of a
messy, real-world-style conversation transcript and organises it into the section structure
clinicians expect -- a genuinely useful proxy for ambient clinical documentation tools. It does not
mean the note is safe to use unreviewed: neither scoring method directly penalises a clinically
dangerous omission or fabrication the way a domain expert reviewer would, and the dataset's own
retained ASR errors mean part of what is being tested is robustness to imperfect input, not just
summarisation quality. Because ROUGE/BERTScore/BLEURT and LLM-jury scores are not on the same scale
or measuring the same thing, always check which scoring method underlies a reported number, and
treat any single score as a proxy to be checked against qualitative note review rather than a
stand-alone clinical-safety signal.
