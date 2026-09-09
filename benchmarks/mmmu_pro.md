---
id: mmmu_pro
name: "MMMU-Pro"
aliases: ["MMMU-Pro: A More Robust Multi-discipline Multimodal Understanding Benchmark"]
page_kind: benchmark
category: multimodal
subcategory: "expert multi-discipline knowledge, filtered against text-only shortcuts, with a vision-only setting"
status: active
summary: "A harder MMMU variant that filters out text-answerable questions, expands options to ten, and adds a vision-only setting where the question is embedded in a photo or screenshot."
measures: >
  MMMU-Pro rebuilds MMMU specifically to close two shortcuts the authors found models exploiting:
  answering from the text alone, and guessing from patterns among the answer options. Construction
  ran in three steps. First, four strong text-only open-source LLMs each answered MMMU questions
  without seeing the images, ten times per question; any question at least three of the four models
  answered correctly across most trials was excluded, and 1,800 questions were then sampled evenly
  across MMMU's 30 subjects (60 each) from what remained. Second, candidate answer options were
  expanded from four to ten (GPT-4o generates, Claude 3.5 Sonnet filters, two rounds of human review
  refine), which itself removed 70 more low-quality questions, leaving 1,730. Third, a vision-only
  setting embeds each question and its options inside a photograph or screenshot -- captured by human
  annotators across varied backgrounds, fonts and display conditions -- so a model must read the
  question rather than receive it as separate text, mirroring how people often share a question by
  screenshotting it.
task_format: >
  Multiple-choice questions paired with one or more images, evaluated in three settings: Standard (4
  options, the original unaugmented MMMU-style question, reported only as a difficulty-comparison
  baseline and excluded from the headline score), Standard (10 options, the augmented format), and
  Vision (the same 10-option question rendered as a single photo or screenshot with no separate text
  input). The official MMMU-Pro score averages the Standard-10-option and Vision settings only. Both
  Direct and chain-of-thought (CoT) prompting are evaluated, with the paper reporting whichever is
  higher; the paper separately finds OCR-specific prompting has little effect while CoT generally
  helps.
metric:
  name: "accuracy, averaged across the Standard (10-option) and Vision settings"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 12.6
  human_baseline: 85.4
  baseline_note: >
    The paper's own Random Choice baseline scores 12.8% on Standard (10 options) and 12.4% on Vision
    (12.6% averaged); Frequent Choice (always the most common option) scores 12.1% on both. Human
    performance is not separately measured for MMMU-Pro; instead the authors approximate it by
    reusing their original MMMU human-evaluation data at three expert tiers (Low/Medium/High), giving
    85.4% for both the Standard-10-option and Vision settings at the "High" tier -- the same figure
    for both settings because it is an approximation carried over from MMMU rather than an
    independent re-measurement.
dataset:
  size: 3460
  size_note: >
    1,730 questions in the augmented Standard (10-option) format and the same 1,730 questions again
    as Vision-only screenshots/photos, for 3,460 total graded instances (confirmed per-config via the
    Hugging Face datasets-server: "standard (10 options)," "standard (4 options)" and "vision" each
    hold exactly 1,730 rows). The unaugmented Standard (4-option) config is the same 1,730 questions
    before option expansion, kept only for the paper's own before/after comparison and excluded from
    the official score.
  url: "https://huggingface.co/datasets/MMMU/MMMU_Pro"
  license: Apache-2.0
  languages: ["en"]
  modalities: ["text", "image"]
  splits: "test only (1,730 x 3 parallel configs: standard 4-option, standard 10-option, vision); no train/dev split"
  public_test_set: true
publisher:
  org: "Carnegie Mellon University (MMMU Team, a multi-institution collaboration)"
  authors: ["Xiang Yue", "Tianyu Zheng", "Yuansheng Ni", "Yubo Wang", "Kai Zhang", "Shengbang Tong", "Yuxuan Sun", "Botao Yu", "Ge Zhang", "Huan Sun", "Yu Su", "Wenhu Chen", "Graham Neubig"]
  url: "https://github.com/MMMU-Benchmark/MMMU"
paper:
  title: "MMMU-Pro: A More Robust Multi-discipline Multimodal Understanding Benchmark"
  arxiv: "2409.02813"
  url: "https://arxiv.org/abs/2409.02813"
  year: 2024
leaderboard_url: "https://mmmu-benchmark.github.io/#leaderboard"
repo_url: "https://github.com/MMMU-Benchmark/MMMU"
released: "2024-09"
last_updated: "2026-07"
lineage:
  family: ""
  predecessor: mmmu
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: "2026-07"
  note: >
    Verified-versus-self-reported scores tell very different stories, so this page leaves top_score
    unset rather than pick one. The MMMU team's own leaderboard (last updated 2026-07-01) marks every
    score added after the original 2024 evaluation with an asterisk for "self-reported, not
    independently verified" -- which covers essentially the entire current top of the table. Under
    that caveat, the leaderboard's highest entry, "Chance Vision 1.5" at 86.9%, exceeds the paper's
    own 85.4% Human-Expert-High approximation, and a cluster of major-lab self-reports sits close
    behind (GPT-5.4 Thinking with tools 82.1%, Gemini 3.0 Pro 81.0%, Gemini 3.1 Pro Thinking (High)
    80.5%). A third-party aggregator, llm-stats.com (accessed 2026-09), independently shows a current
    leader around 83.6% (Gemini 3.5 Flash) across 69 tracked models, corroborating that frontier
    scores now sit near the human-expert approximation. By contrast, the MMMU team's own verified
    figure for the original release remains GPT-4o (0513) at 51.9% (49.7 Vision, 54.0 Standard),
    which was already 33.5 points below the human baseline in September 2024. Given self-reported
    frontier scores now cluster at or above the paper's human-expert approximation, this benchmark
    reads as saturated at the top even though this page could not independently verify the specific
    leading number.
contamination:
  risk: medium
  note: >
    MMMU-Pro's questions are drawn and filtered from MMMU's existing pool (public since November
    2023) rather than newly authored, so any leakage affecting MMMU is inherited here too, though the
    filtering, option augmentation and vision-only rendering are new as of September 2024 and not
    identical to any single MMMU item. The dataset carries no access gating and its answers
    (including an "explanation" field) are public on Hugging Face; the maintainers continue to patch
    incorrect ground-truth labels and option-augmentation errors as recently as July 2026, which is
    good for correctness but means scores measured before and after a given fix are not perfectly
    comparable.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "MMMU_Pro (config name MMMU_Pro_10c, Standard 10-option setting only, run through VLMEvalKit integration; no OpenCompass config for the Standard 4-option or Vision settings was found)"
  bigbench: ""
  other: "The authors' own inference and evaluation scripts live under mmmu-pro/ in the MMMU-Benchmark/MMMU repository, with separate infer_xxx.py scripts per model family and support for cot/direct modes and all three input settings."
tags: ["multimodal", "college-level", "multi-discipline", "multiple-choice", "vision-language", "robustness"]
sources:
  - url: "https://arxiv.org/abs/2409.02813"
    title: "MMMU-Pro: A More Robust Multi-discipline Multimodal Understanding Benchmark (Yue et al., arXiv:2409.02813)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2409.02813"
    title: "MMMU-Pro, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/MMMU/MMMU_Pro"
    title: "MMMU/MMMU_Pro dataset card and changelog, Hugging Face (Apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=MMMU/MMMU_Pro"
    title: "MMMU/MMMU_Pro datasets-server size API (per-config row counts)"
    accessed: "2026-09-08"
  - url: "https://github.com/MMMU-Benchmark/MMMU"
    title: "MMMU-Benchmark/MMMU GitHub repository (mmmu-pro/ inference and evaluation scripts)"
    accessed: "2026-09-08"
  - url: "https://mmmu-benchmark.github.io/#leaderboard"
    title: "MMMU benchmark homepage and leaderboard (MMMU-Pro, MMMU Val and Test tables; last updated 2026-07-01)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/MMMU_Pro"
    title: "OpenCompass MMMU_Pro dataset config (MMMU_Pro_10c_vlmevalkit_gen.py)"
    accessed: "2026-09-08"
  - url: "https://llm-stats.com/benchmarks/mmmu-pro"
    title: "MMMU-Pro leaderboard, llm-stats.com (third-party aggregator, 69 tracked models)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MMMU-Pro rebuilds MMMU to close two shortcuts the authors found models exploiting: answering from
the accompanying text alone, and guessing from patterns among the answer options rather than from
the image. Construction ran in three steps. First, four strong text-only open-source LLMs each
answered MMMU questions without seeing the images, ten times per question; any question at least
three of the four models answered correctly across most trials was excluded as too easy without
vision, and 1,800 questions were sampled evenly across MMMU's 30 subjects from what remained. Second,
candidate answer options were expanded from four to ten -- GPT-4o generates distractors, Claude 3.5
Sonnet filters them, and two rounds of human review refine the result -- which itself flagged and
removed 70 more low-quality questions, leaving 1,730. Third, a vision-only setting embeds each
question and its options inside a photograph or screenshot, captured by annotators across varied
backgrounds, fonts and display conditions, so a model must read the question directly from the image
rather than receive it as separate text.

## How it is scored

Accuracy is measured in three settings: Standard (4 options, the original unaugmented format, kept
only as a before/after comparison point and excluded from the headline score), Standard (10 options),
and Vision (the same question as a single image). The official MMMU-Pro score averages the
Standard-10-option and Vision accuracies. Both direct answering and chain-of-thought prompting are
evaluated, with the higher of the two reported; the paper separately finds that OCR-specific prompts
make little difference while CoT generally helps. Random Choice scores 12.8% (Standard 10-option) and
12.4% (Vision); the paper's Human-Expert-High approximation, carried over from MMMU's own human
evaluation rather than independently re-measured for MMMU-Pro, sits at 85.4% for both settings.

## Dataset and licence

1,730 questions in the augmented Standard (10-option) format and the same 1,730 questions again as
Vision-only images, for 3,460 total graded instances, confirmed per-config via the Hugging Face
datasets-server. The dataset is Apache-2.0 licensed, ungated, and includes an explanation field
alongside each answer. The maintainers actively patch errors -- a May 2026 fix corrected an option-
augmentation issue in the Standard-10-option and Vision settings, and a July 2026 fix corrected two
incorrect ground-truth labels -- so scores measured before and after a given patch may not be
perfectly comparable at the individual-item level.

## Who publishes it

Xiang Yue, Tianyu Zheng, Yuansheng Ni, Yubo Wang, Kai Zhang, Shengbang Tong, Yuxuan Sun, Botao Yu, Ge
Zhang, Huan Sun, Yu Su, Wenhu Chen and Graham Neubig published MMMU-Pro in September 2024
(arXiv:2409.02813, revised May 2025), largely overlapping with the original MMMU author team and
publishing under the same "MMMU Team" banner; contact is listed through Carnegie Mellon University
(Xiang Yue). The team maintains the shared MMMU-Benchmark/MMMU repository, the Hugging Face dataset,
and a combined leaderboard covering MMMU (Val and Test) and MMMU-Pro together.

## Lineage

MMMU-Pro's direct predecessor is MMMU (`mmmu`), from which every question is drawn before filtering,
option augmentation and vision-only rendering. No further successor to MMMU-Pro specifically was
identified in this research, though the shared leaderboard tracks a "with tools" variant for several
recent models (for example Claude Opus 4.6 and GPT-5.4 Thinking, each reported both with and without
tool access) that is not a separately catalogued benchmark here.

## Saturation and contamination

The MMMU team's own leaderboard, last updated 2026-07-01, marks nearly every post-2024 score as
self-reported and not independently verified -- which covers essentially the whole current top of the
table. Under that caveat, the leading entry, "Chance Vision 1.5" at 86.9%, exceeds the paper's own
85.4% human-expert approximation, and a cluster of major-lab self-reports (GPT-5.4 Thinking with
tools 82.1%, Gemini 3.0 Pro 81.0%) sits close behind; a third-party aggregator, llm-stats.com, shows a
similar current picture (a 83.6% leader across 69 tracked models). The team's own verified figure for
the original 2024 release remains GPT-4o (0513) at 51.9%, 33.5 points below the human baseline at the
time. Given how far and how quickly self-reported frontier scores have moved toward and past the
human-expert line, this benchmark now reads as saturated at the top for the strongest models, even
though the specific leading numbers are unverified. Contamination risk is medium: questions are
filtered and remixed from the existing, public MMMU pool rather than newly written, so MMMU's own
exposure carries over, tempered by the added augmentation and rendering being new as of September
2024.

## How to run it

The authors' own repository provides per-model-family inference scripts (`infer_xxx.py`) and a
shared `evaluate.py`, supporting direct and CoT prompting across all three input settings; a known
quirk documented in the repository is that in the Standard (10-option) setting, the order of `<image
i>` tokens in the shuffled option list does not necessarily match the order of the underlying
`image_i` dataset fields, which the reference inference code handles but a from-scratch
implementation could get wrong. OpenCompass implements only the Standard-10-option setting, as
`MMMU_Pro_10c`, through a VLMEvalKit integration; no Standard-4-option or Vision-setting OpenCompass
config, and no lm-evaluation-harness, inspect_evals or HELM implementation, was found during this
research.

## Reading the numbers

A strong MMMU-Pro score, especially on the Vision setting, is meaningfully stronger evidence of real
multimodal understanding than a strong MMMU score, since MMMU-Pro was specifically built to remove
the text-only and option-guessing shortcuts that inflate MMMU. Because the official score averages
two settings that differ substantially in difficulty (Standard 10-option is consistently easier than
Vision for every model in the paper's own release-time table), check the per-setting breakdown before
assuming uniform capability, and note whether tool access was enabled, since the leaderboard reports
several recent models both with and without it. Given how many current leaderboard entries are
self-reported rather than verified by the MMMU team, treat any single top-of-table score with more
caution than the team's own original, verified release-time comparisons.
