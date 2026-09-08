---
id: arc_challenge
name: ARC-Challenge
aliases:
  - AI2 Reasoning Challenge
  - ARC (Challenge Set)
page_kind: benchmark
category: reasoning
subcategory: science multiple-choice QA
status: superseded
summary: A multiple-choice grade-school science question set built so that simple retrieval and word-overlap methods fail, isolating genuine multi-hop reasoning.
measures: ARC-Challenge gives a model a grade-school-level natural science question with several answer choices, drawn from real school exam materials, and asks it to pick the correct one. Every question in the set was specifically selected because neither a retrieval-based algorithm nor a simple word-co-occurrence algorithm could answer it correctly, so it requires more than surface-level lexical matching between the question and background text. It tests a mix of scientific fact recall and the multi-step reasoning needed to combine that fact with the question.
task_format: Multiple-choice science question, typically 4 answer options, single correct answer.
metric:
  name: accuracy (often reported as acc_norm, length-normalised)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: Random baseline assumes 4 roughly balanced options; the original paper reported that leading contemporary neural QA models could not significantly beat this random baseline on the Challenge Set.
dataset:
  size: 2590
  size_note: "2,590 Challenge Set questions (1,119 train / 299 validation / 1,172 test), drawn from a pool of 7,787 total ARC questions alongside a separate 5,197-question Easy Set; a companion 14M-sentence ARC Corpus of science text is provided as an optional retrieval source"
  url: https://huggingface.co/datasets/allenai/ai2_arc
  license: CC BY-SA 4.0
  languages:
    - en
  modalities:
    - text
  splits: "train (1,119) / validation (299) / test (1,172)"
  public_test_set: true
publisher:
  org: Allen Institute for AI (AI2)
  authors:
    - Peter Clark
    - Isaac Cowhey
    - Oren Etzioni
    - Tushar Khot
    - Ashish Sabharwal
    - Carissa Schoenick
    - Oyvind Tafjord
  url: https://allenai.org/
paper:
  title: "Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge"
  arxiv: "1803.05457"
  url: https://arxiv.org/abs/1803.05457
  year: 2018
leaderboard_url: ""
repo_url: https://huggingface.co/datasets/allenai/ai2_arc
released: "2018-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 72.7
  as_of: "2024-07"
  note: Within the Hugging Face Open LLM Leaderboard v1 era, the highest tracked score was around 72.7% (acc_norm); the leaderboard's own team retired v1 in mid-2024, citing that ARC-Challenge (along with HellaSwag, MMLU, TruthfulQA, Winogrande and GSM8K) had become solvable through pattern-matching and no longer separated strong models well.
contamination:
  risk: medium
  note: The question and answer set has been fully public since 2018 and is widely mirrored, so any model trained on a broad web crawl since then has plausibly seen it; Hugging Face cited this style of leakage as one reason for retiring the leaderboard that leaned on it.
harness:
  lm_eval: arc_challenge
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - science-qa
  - multiple-choice
  - reasoning
  - legacy-benchmark
sources:
  - url: https://arxiv.org/abs/1803.05457
    title: "Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/allenai/ai2_arc
    title: allenai/ai2_arc dataset card
    accessed: "2026-09-07"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/arc/README.md
    title: lm-evaluation-harness ARC task README
    accessed: "2026-09-07"
  - url: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard
    title: Open LLM Leaderboard (archived) space
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ARC-Challenge is the harder half of the AI2 Reasoning Challenge, a set of natural, grade-school-level science exam questions. The dataset was split into an Easy Set and a Challenge Set, and a question only lands in the Challenge Set if both a retrieval-based solver and a simple word-co-occurrence solver got it wrong. That construction filters out questions answerable by lexical overlap alone, so the remaining set leans on genuine scientific knowledge combined with reasoning across more than one fact, rather than keyword matching between the question and a supporting passage.

The questions are text-only, English, and written for actual school assessments rather than generated for the benchmark, which is part of why AI2 describes them as natural rather than synthetic.

## How it is scored

Each question has multiple answer choices, most commonly four, and the model's predicted choice is compared against the single correct answer to compute accuracy. Because answer choices vary in token length, many harnesses report length-normalised accuracy (acc_norm), which adjusts for a language model's tendency to prefer shorter completions, alongside or instead of raw accuracy; the two can diverge by a few points for the same model; check which one a given score reports. The original 2018 paper found that contemporary retrieval and neural QA baselines could not significantly beat a random-guess baseline on the Challenge Set, which was the intended difficulty bar.

## Dataset and licence

The full ARC question set has 7,787 natural science questions, split into a 5,197-question Easy Set and a 2,590-question Challenge Set (1,119 train, 299 validation, 1,172 test). AI2 also released a supporting ARC Corpus of roughly 14 million science-relevant sentences that systems may use as a retrieval source, though most modern LLM evaluations run closed-book without it. The Hugging Face mirror lists the dataset under a CC BY-SA 4.0 licence.

## Who publishes it

ARC-Challenge was published by the Allen Institute for AI in the 2018 paper "Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge," by Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick and Oyvind Tafjord. AI2 continues to host the dataset; it no longer maintains its own leaderboard for it, and the Hugging Face Open LLM Leaderboard that most recently tracked it at scale has itself been archived.

## Lineage

ARC-Challenge and ARC-Easy are the two halves of a single original release; ARC-Easy is not a page in this repository. In practice it was superseded in most current leaderboard use by harder benchmarks introduced in 2024, including `mmlu_pro`, `gpqa_diamond`, `bbh` and `musr`, all tracked separately in this repository, which the Hugging Face Open LLM Leaderboard adopted specifically to replace ARC-Challenge and several other benchmarks it judged too easy.

## Saturation and contamination

Within the Hugging Face Open LLM Leaderboard v1, which normalised and tracked ARC-Challenge at scale, the highest recorded score sat around 72.7% (acc_norm) as of mid-2024; the leaderboard's maintainers retired that version shortly after, stating that ARC-Challenge, HellaSwag, MMLU, TruthfulQA, Winogrande and GSM8K had all become saturated, contaminated, or solvable through pattern-matching rather than the reasoning the benchmarks intended to test. Because the dataset has been fully public since 2018, contamination from broad web pretraining is plausible for most models released since, which is part of why it was dropped rather than merely re-weighted.

## How to run it

lm-evaluation-harness exposes it as the `arc_challenge` task (and a chat-formatted variant), built on the `allenai/ai2_arc` dataset's ARC-Challenge configuration. It is a straightforward multiple-choice log-likelihood task, so differences between reported scores usually come down to whether raw accuracy or acc_norm was used, how many few-shot examples were given, and whether the ARC Corpus was made available to the model.

## Reading the numbers

A high ARC-Challenge score today says less about a frontier model than it did in 2018, since most strong current models are well past the point where this set discriminates meaningfully between them, and the benchmark it once anchored has been retired in favour of harder replacements. It remains useful as a comparison point for older or smaller models, or for reproducing legacy leaderboard results, but a new model's ARC-Challenge score alone is weak evidence of its current-generation reasoning ability; look at `mmlu_pro`, `gpqa_diamond` or `bbh` instead for that.
