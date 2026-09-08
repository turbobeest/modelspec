---
id: arc
name: "ARC (AI2 Reasoning Challenge)"
aliases:
  - "AI2 Reasoning Challenge"
page_kind: family
category: reasoning
subcategory: "grade-school science multiple-choice QA (Easy and Challenge splits)"
status: superseded
summary: "A grade-school science multiple-choice question set split into Easy and Challenge halves, whose scores are reported interchangeably far too often despite very different difficulty."
measures: >
  The AI2 Reasoning Challenge (ARC) is a set of 7,787 natural, grade-school-level science exam
  questions, split by the original authors into two pools of different difficulty: ARC-Easy
  (5,197 questions) and ARC-Challenge (2,590 questions). A question lands in the Challenge set only
  if two baseline solvers of the time -- an information-retrieval solver and a word-co-occurrence
  (PMI) solver -- both answered it incorrectly; anything either solver could get right went into
  Easy. That single filtering rule is the entire distinction between the two splits: they share the
  same format, the same source, and the same authors, and differ only in whether simple
  lexical-matching methods could solve them. Because both splits are commonly reported under the
  bare name "ARC" without specifying which one, and a model's score on Easy can be 20-30 points
  higher than on Challenge, conflating the two is one of the more common reporting errors in this
  space.
task_format: "Multiple-choice science question, typically 4 answer options, single correct answer; identical format for both splits."
metric:
  name: "accuracy (often reported as acc_norm, length-normalised)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: "Random baseline assumes 4 roughly balanced options. The original paper's central empirical claim concerned the Challenge split specifically: contemporary retrieval and neural QA baselines could not significantly beat random guessing on it, which was the intended difficulty bar for that split; no equivalent claim was made about Easy, which was by construction already solvable by those same baselines."
dataset:
  size: 7787
  size_note: "7,787 questions total. ARC-Easy: 5,197 (2,251 train / 570 dev / 2,376 test). ARC-Challenge: 2,590 (1,119 train / 299 dev / 1,172 test). A companion ARC Corpus of roughly 14 million science-relevant sentences (about 1.4GB) is provided as an optional retrieval source."
  url: "https://huggingface.co/datasets/allenai/ai2_arc"
  license: "CC-BY-SA-4.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "Easy: train (2,251) / dev (570) / test (2,376). Challenge: train (1,119) / dev (299) / test (1,172)."
  public_test_set: true
publisher:
  org: "Allen Institute for AI (AI2)"
  authors: ["Peter Clark", "Isaac Cowhey", "Oren Etzioni", "Tushar Khot", "Ashish Sabharwal", "Carissa Schoenick", "Oyvind Tafjord"]
  url: "https://allenai.org/"
paper:
  title: "Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge"
  arxiv: "1803.05457"
  url: "https://arxiv.org/abs/1803.05457"
  year: 2018
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/allenai/ai2_arc"
released: "2018-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: ["arc_challenge"]
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: "Within the Hugging Face Open LLM Leaderboard v1, the highest recorded ARC-Challenge score sat around 72.7% (acc_norm) as of mid-2024, shortly before that leaderboard's maintainers retired it, citing ARC-Challenge among several benchmarks that had become saturated. No comparably tracked recent ceiling figure for ARC-Easy specifically was found; since Easy was constructed from questions simple methods could already answer, it plausibly saturated earlier and further than Challenge, though no source consulted confirms a specific Easy top score."
contamination:
  risk: medium
  note: "Both splits' questions and answers have been fully public since 2018 and are widely mirrored, so any model trained on a broad web crawl since then has plausibly seen them. No dedicated post-hoc ARC contamination study was found in the sources consulted."
harness:
  lm_eval: "ai2_arc"
  inspect_evals: "arc_easy, arc_challenge"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["science-qa", "multiple-choice", "reasoning", "family", "legacy-benchmark"]
sources:
  - url: "https://arxiv.org/abs/1803.05457"
    title: "Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1803.05457"
    title: "ARC paper (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/ai2_arc"
    title: "allenai/ai2_arc dataset metadata (Hugging Face API)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/arc"
    title: "lm-evaluation-harness arc task directory"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/arc"
    title: "inspect_evals arc task directory"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

The AI2 Reasoning Challenge (ARC) is a set of 7,787 natural, grade-school-level science exam questions, split by the original authors into two pools of different difficulty: ARC-Easy (5,197 questions) and ARC-Challenge (2,590 questions). A question lands in the Challenge set only if two baseline solvers of the time -- an information-retrieval solver and a word-co-occurrence (PMI) solver -- both answered it incorrectly; anything either solver could get right went into Easy. That single filtering rule is the entire distinction between the two splits: they share the same format, the same source, and the same authors, and differ only in whether simple lexical-matching methods could solve them.

Because both splits are commonly reported under the bare name "ARC" or "AI2 Reasoning Challenge" without specifying which one, and because a model's score on Easy can run 20-30 points higher than its score on Challenge, conflating the two is one of the more common benchmark-reporting errors in this space.

## How it is scored

Every question is multiple choice, most often with four options, scored as accuracy against the single correct answer. Because answer options vary in token length, many harnesses report length-normalized accuracy (acc_norm) alongside or instead of raw accuracy, and the two can diverge by several points for the same model on the same split. The original 2018 paper's central empirical claim concerned the Challenge set specifically: contemporary retrieval and neural QA baselines could not significantly beat random guessing on it, which was the intended bar for that split; no equivalent claim was made about Easy, which by construction was already solvable by those same baselines.

## Dataset and licence

The full release totals 7,787 questions: ARC-Easy holds 5,197 (2,251 train / 570 dev / 2,376 test) and ARC-Challenge holds 2,590 (1,119 train / 299 dev / 1,172 test). AI2 also released a companion ARC Corpus of roughly 14 million science-relevant sentences (about 1.4GB) as an optional retrieval source, though most current LLM evaluations run closed-book without it. The Hugging Face dataset card for `allenai/ai2_arc` lists the release under a CC BY-SA 4.0 licence; both splits' test-set answers are public.

## Who publishes it

ARC was published by the Allen Institute for AI in "Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge" (2018), by Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick and Oyvind Tafjord. AI2 continues to host the dataset; it does not maintain an active public leaderboard for either split today.

## Lineage

ARC-Easy and ARC-Challenge are two halves of one original release rather than separate benchmarks with independent histories; this repository documents ARC-Challenge on its own page, [arc_challenge](arc_challenge.md), since it is overwhelmingly the split reported in practice, while ARC-Easy has no dedicated page yet. Do not confuse either split with [ARC-AGI-2](arc_agi_2.md) (`arc_agi_2`), a visual abstract-reasoning benchmark from the ARC Prize Foundation that shares only the "ARC" acronym and the general goal of testing reasoning -- it was built by a different organisation six years later, uses coloured-grid puzzles rather than text questions, and has no other relationship to AI2's dataset. Within leaderboard practice, this family was effectively superseded in 2024 by harder replacement benchmarks including `mmlu_pro`, `gpqa_diamond`, `bbh` and `musr`, all tracked separately in this repository.

## Saturation and contamination

Within the Hugging Face Open LLM Leaderboard v1, the highest recorded ARC-Challenge score sat around 72.7% (acc_norm) as of mid-2024, shortly before that leaderboard's maintainers retired it, citing ARC-Challenge among several benchmarks that had become saturated or otherwise stopped separating strong models. No comparably tracked recent ceiling figure for ARC-Easy specifically was found; since Easy was constructed from questions simple methods could already answer, it plausibly saturated earlier and further than Challenge did, though no source consulted confirms a specific Easy top score. Both splits have been fully public since 2018, so contamination from broad web pretraining is plausible for either.

## How to run it

lm-evaluation-harness implements `arc_easy` and `arc_challenge` as separate tasks (plus a chat-formatted `arc_challenge_chat` variant), grouped together under the tag `ai2_arc`; there is no single combined task that pools both splits into one number. inspect_evals likewise registers `arc_easy` and `arc_challenge` as two separate evaluations rather than one unified task. Because of this, always confirm which split a reported "ARC" score actually comes from before comparing it to another paper's number, and treat any bare "ARC" or "ARC score" citation that does not name Easy or Challenge as unverifiable until the source is checked.

## Reading the numbers

A high ARC-Easy score today says very little about a current frontier model, since the split was built specifically from questions weak 2018-era baselines could already answer; a high ARC-Challenge score is a somewhat stronger signal but is also long past the point of separating strong current models, and the benchmark it once anchored has been retired from the leaderboard that tracked it at scale. Both splits remain useful for reproducing legacy results or benchmarking smaller and older models, but neither should be read as evidence of current-generation reasoning ability on its own -- and any score reported simply as "ARC," with no split named, should be treated with suspicion until you confirm which one it is.
