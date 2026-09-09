---
id: summscreen
name: "SummScreen"
aliases:
  - "SummScreen: A Dataset for Abstractive Screenplay Summarization"
page_kind: benchmark
category: generation
subcategory: "long-document abstractive summarization of TV episode transcripts into human-written recaps"
status: active
summary: "Pairs of TV series transcripts and human-written episode recaps, testing long-document abstractive summarization where plot detail is scattered across dialogue."
measures: >
  SummScreen pairs a full television episode transcript (dialogue plus scene descriptions) with a
  human-written recap of that episode's plot. A model must produce an abstractive summary that
  identifies and integrates plot-relevant information scattered non-contiguously across long dialogue,
  while omitting comedic asides and character-development detail that do not advance the plot. This
  makes it a long-input, entity-centric summarization test in English: input transcripts run into the
  thousands of tokens (averaging roughly 6,400-7,600 tokens depending on the source), while target
  recaps are much shorter (roughly 110-380 tokens on average).
task_format: "Free-text generation: given a full episode transcript, produce an abstractive plot recap; scored automatically and with two entity-centric metrics proposed by the paper."
metric:
  name: "ROUGE (standard) plus two entity-centric metrics proposed by the paper for character/plot fidelity"
  direction: higher_is_better
  unit: "score"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No numeric baseline was found in the sources opened for this page. The paper's own contribution is
    partly that standard ROUGE under-rewards entity-centric plot fidelity, motivating its two additional
    metrics; it does not report a single "human" or "random" ROUGE figure that would apply cleanly here.
dataset:
  size: 26851
  size_note: >
    Two sources, not overlapping in TV series: ForeverDreaming (FD), 3,673 train / 338 dev / 337 test
    episodes (4,348 total), and TVMegaSite (TMS), 18,915 train / 1,795 dev / 1,793 test episodes
    (22,503 total), summing to 26,851 transcript-recap pairs across both sources. FD recaps are shorter
    on average (about 113.7 tokens) and drawn from Wikipedia/TVMaze; TMS recaps are longer (about 380.6
    tokens) and were contributed alongside the transcripts on the same fan site.
  url: "https://github.com/mingdachen/SummScreen"
  license: "Not established: the GitHub repository page did not state an explicit licence in the sources opened for this page."
  languages:
    - en
  modalities:
    - text
  splits: "ForeverDreaming: train 3,673 / dev 338 / test 337. TVMegaSite: train 18,915 / dev 1,795 / test 1,793."
  public_test_set: true
publisher:
  org: "Toyota Technological Institute at Chicago (TTIC)"
  authors:
    - "Mingda Chen"
    - "Zewei Chu"
    - "Sam Wiseman"
    - "Kevin Gimpel"
  url: "https://github.com/mingdachen/SummScreen"
paper:
  title: "SummScreen: A Dataset for Abstractive Screenplay Summarization"
  arxiv: "2104.07091"
  url: "https://arxiv.org/abs/2104.07091"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/mingdachen/SummScreen"
released: "2021-04"
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
    No current or historical top score was found in the sources opened for this page; the paper's own
    finding that baseline neural models "underutilize" the input transcript relative to an oracle
    extractive upper bound suggests substantial headroom remained at release, but no post-release
    leaderboard tracking was located.
contamination:
  risk: high
  note: >
    The transcripts and recaps have been publicly hosted (via the authors' Google Drive links and
    mirrored copies) since the dataset's 2021 arXiv release and 2022 ACL publication, and the underlying
    fan-transcript and recap sites (ForeverDreaming, TVMegaSite, Wikipedia, TVMaze) were themselves
    public for years before that, so both the source transcripts and many gold recaps are plausible
    pretraining-data members for current large models.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "summscreen"
  bigbench: ""
  other: ""
tags:
  - summarization
  - long-context
  - generation
  - narrative
  - entity-centric
sources:
  - url: "https://arxiv.org/abs/2104.07091"
    title: "SummScreen: A Dataset for Abstractive Screenplay Summarization"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2104.07091"
    title: "SummScreen, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.acl-long.589/"
    title: "SummScreen (ACL Anthology, ACL 2022)"
    accessed: "2026-09-08"
  - url: "https://github.com/mingdachen/SummScreen"
    title: "mingdachen/SummScreen repository"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/summscreen"
    title: "OpenCompass summscreen dataset configs directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/summscreen/summscreen_gen_aa5eb3.py"
    title: "OpenCompass summscreen_gen_aa5eb3 config (raw)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/summscreen.py"
    title: "OpenCompass SummScreen dataset loader (raw)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-006"
---

## What it measures

SummScreen pairs a full television episode transcript -- dialogue with speaker names, plus scene descriptions -- with a human-written recap of that episode's plot. A model must read the transcript and produce an abstractive summary that identifies the plot-relevant events, which the paper's authors note are typically expressed indirectly through character dialogue and scattered non-contiguously across the episode, while filtering out comedic banter and character-development detail that do not move the plot forward. This is a long-input English summarization task: source transcripts average roughly 6,400 to 7,600 tokens depending on the source corpus, while target recaps are much shorter, averaging roughly 110 to 380 tokens.

Because television recaps are heavily entity- and relationship-centric (who did what to whom), the paper argues standard summarization systems and metrics under-serve the task, and proposes two additional entity-centric evaluation metrics alongside standard ROUGE to capture whether a summary correctly tracks characters.

## How it is scored

The primary evaluation reported in the paper is standard ROUGE, supplemented by the authors' own two entity-centric metrics designed to check whether characters and their relationships are correctly represented in the generated summary, since the paper finds ROUGE alone under-rewards this aspect. Prompted or fine-tuned generation is the evaluation setup; no fixed maximum score or human/random baseline applicable to ROUGE was found in the sources opened for this page.

OpenCompass's `summscreen` configuration takes a different approach: it merges both the ForeverDreaming and TVMegaSite subsets into a single `dev` split, prompts the model to "summarize the following English report in English," and scores with a `BleuEvaluator` rather than ROUGE -- a real protocol difference from the paper's own evaluation, generating output up to 500 tokens from inputs truncated to 8,192 tokens.

## Dataset and licence

SummScreen totals 26,851 transcript-recap pairs from two non-overlapping sources. ForeverDreaming (FD) contributes 4,348 pairs (3,673 train, 338 dev, 337 test), with recaps sourced from Wikipedia and TVMaze and averaging about 113.7 tokens. TVMegaSite (TMS) contributes 22,503 pairs (18,915 train, 1,795 dev, 1,793 test), with recaps contributed on the same fan site as the transcripts and averaging about 380.6 tokens -- substantially longer than FD's. The authors filtered episodes by a minimum character-overlap ratio (over 85%) between recap and transcript and a minimum utterance length, and the two sources cover disjoint sets of TV series. The GitHub repository distributes both a tokenized, anonymized version and an untokenized version (which requires manually recovering the official train/dev/test split) via Google Drive links; this page did not find an explicit licence statement for the redistributed data in the sources opened.

## Who publishes it

SummScreen is by Mingda Chen, Zewei Chu, Sam Wiseman and Kevin Gimpel at the Toyota Technological Institute at Chicago (TTIC), published as "SummScreen: A Dataset for Abstractive Screenplay Summarization" at ACL 2022 (originally posted to arXiv in April 2021). The authors maintain the reference repository and download links at `mingdachen/SummScreen` on GitHub.

## Lineage

No predecessor, successor, or variant of SummScreen was found in the sources opened for this page, and it has no family page in this repository. It sits within the broader family of long-document, narrative-summarization benchmarks (alongside book- and screenplay-summarization datasets that appeared around the same period), but no specific lineage relationship to another id in this repository was confirmed.

## Saturation and contamination

No current or historical top score was found in the sources opened for this page, so `saturation.status` is left `unknown`. The paper itself reports that its neural baselines, using a Longformer encoder with a standard transformer decoder, "underutilize" the input transcript compared with an oracle extractive upper bound built from the gold recap, which suggests meaningful headroom remained at release; whether that gap has since closed for current large models was not established here. Contamination risk is high: the transcripts and many gold recaps have been continuously public since well before the dataset's 2021 release (the underlying fan-transcript and recap sites, and Wikipedia/TVMaze, predate it by years), and the dataset itself has been publicly downloadable and mirrored since publication.

## How to run it

OpenCompass configures the task as `summscreen`, merging the FD and TMS subsets into one `dev` split, using a fixed English summarization prompt and scoring with `BleuEvaluator` rather than the paper's own ROUGE-plus-entity-metric protocol -- a difference to flag explicitly when comparing OpenCompass numbers to the original paper's reported results. No configuration for this dataset was found in lm-evaluation-harness, HELM, or BIG-bench in the sources opened for this page. The authors' own repository provides baseline training and evaluation code (a Longformer-based encoder-decoder model) and the reference data splits for reproducing the paper's own numbers, including its entity-centric metrics.

## Reading the numbers

A strong SummScreen score suggests a model can extract and integrate plot-relevant information buried in long, dialogue-heavy input, which is a harder and more entity-centric test than typical news summarization. Because the paper's own baselines underutilized the transcript relative to an oracle extractive summary, and because standard ROUGE can miss character-tracking errors that its proposed entity-centric metrics are designed to catch, a ROUGE-only score should be read with caution: check whether a reported number also includes the paper's entity-centric metrics before treating it as a full picture of summary quality. Scores from OpenCompass's BLEU-scored, merged-split configuration are not directly comparable to the paper's own ROUGE-and-entity-metric numbers on the official FD/TMS test splits.
