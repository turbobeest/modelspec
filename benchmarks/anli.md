---
id: anli
name: "ANLI (Adversarial NLI)"
aliases:
  - "Adversarial NLI"
page_kind: benchmark
category: reasoning
subcategory: "adversarial natural language inference"
status: unknown
summary: "A three-round adversarial natural language inference benchmark where annotators iteratively wrote examples to fool the strongest model trained on all prior rounds."
measures: >
  ANLI tests natural language inference: given a short context passage and a one-sentence
  hypothesis, a model must decide whether the hypothesis is entailed by the context, contradicted
  by it, or neither (neutral). What separates ANLI from earlier inference datasets like SNLI and
  MNLI is not the task format but how its examples were built. Human annotators were shown a
  context and a target label, then wrote a hypothesis specifically intended to fool a
  state-of-the-art NLI model already trained on all prior data; an item only entered the dataset
  once it beat that model and passed a separate human-verification pass. Three rounds (R1, R2, R3)
  repeated this loop with progressively stronger target models and, from round three onward, a
  wider range of source genres beyond Wikipedia.
task_format: "Three-way classification: given a context and a hypothesis, label the pair as entailment, contradiction, or neutral."
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: null
  baseline_note: "Random guessing scores 33.3% on this three-way task. The paper reports no single pooled human-accuracy figure across all three rounds; it instead reports per-round model accuracy and the annotation pipeline's own human-verification agreement rates, which check label quality rather than establish a human performance ceiling comparable to a model score."
dataset:
  size: 169265
  size_note: "162,865 train + 3,200 dev + 3,200 test, pooled across three rounds: R1 (16,946 / 1,000 / 1,000), R2 (45,460 / 1,000 / 1,000) and R3 (100,459 / 1,200 / 1,200)."
  url: "https://github.com/facebookresearch/anli/"
  license: "CC BY-NC 4.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "train (162,865) / dev (3,200) / test (3,200), each further split by round (R1/R2/R3)"
  public_test_set: true
publisher:
  org: "Facebook AI Research (FAIR), with the University of North Carolina at Chapel Hill"
  authors: ["Yixin Nie", "Adina Williams", "Emily Dinan", "Mohit Bansal", "Jason Weston", "Douwe Kiela"]
  url: "https://github.com/facebookresearch/anli/"
paper:
  title: "Adversarial NLI: A New Benchmark for Natural Language Understanding"
  arxiv: "1910.14599"
  url: "https://arxiv.org/abs/1910.14599"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/facebookresearch/anli"
released: "2019-10"
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
  note: "No dedicated current leaderboard or recent top-score figure was confirmed from a source opened during this research; the project's own web page is described in its repository as a demo rather than an ongoing submission leaderboard. Because each round's items were built specifically to fool the strongest contemporary model available at the time, and current frontier models are far stronger than the RoBERTa ensembles used to filter round three, scores have plausibly risen substantially since 2020, but no confirmed recent figure was found."
contamination:
  risk: high
  note: "All three rounds' labels have been public on GitHub and Hugging Face since 2019-2020, and the round one and two contexts are drawn from HotpotQA's Wikipedia passages, which are themselves widely mirrored across the web. No dedicated ANLI contamination study was found in the sources consulted; this assessment rests on the dataset's fully public mechanics rather than a measured leakage rate."
harness:
  lm_eval: "anli"
  inspect_evals: ""
  helm: ""
  opencompass: "anli"
  bigbench: ""
  other: ""
tags: ["nli", "adversarial", "entailment", "multi-round", "legacy-benchmark"]
sources:
  - url: "https://arxiv.org/abs/1910.14599"
    title: "Adversarial NLI: A New Benchmark for Natural Language Understanding"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1910.14599"
    title: "Adversarial NLI (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/facebookresearch/anli/"
    title: "facebookresearch/anli repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/facebookresearch/anli/main/LICENSE"
    title: "facebookresearch/anli LICENSE file"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/splits?dataset=facebook/anli"
    title: "facebook/anli dataset splits (datasets-server)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/anli"
    title: "lm-evaluation-harness anli task directory"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/anli"
    title: "OpenCompass anli dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ANLI tests natural language inference: given a short context passage and a one-sentence hypothesis, a model must decide whether the hypothesis is entailed by the context, contradicted by it, or neither (neutral). What separates ANLI from earlier inference datasets like SNLI and MNLI is not the task format but how its examples were built. Human annotators were shown a context and a target label, then wrote a hypothesis specifically intended to fool a state-of-the-art NLI model that had already been trained on all prior data; an item only entered the dataset once it beat that model and passed a separate human-verification pass. Every item is adversarial with respect to some real model of its era, rather than difficult by an author's guess at what might be hard.

Three rounds -- R1, R2 and R3 -- repeated this loop with progressively stronger target models (BERT-Large for R1, RoBERTa ensembles trained on all prior rounds for R2 and R3), and from round three onward drew on a wider range of source genres beyond Wikipedia.

## How it is scored

Each example is a three-way classification, so random guessing scores 33.3%. The paper reports no single pooled human-accuracy figure spanning all three rounds; instead it reports the annotation pipeline's own verification statistics -- whether independent checkers agreed an example matched its target label -- a data-quality check rather than a human performance ceiling comparable to a model's score. Most reporters give accuracy separately per round (R1/R2/R3) and sometimes a pooled average, since accuracy typically drops from R1 to R3 as both source text and adversarial pressure increase.

## Dataset and licence

ANLI totals 169,265 examples: 162,865 for training, 3,200 for development and 3,200 for test, split unevenly across the three rounds -- 18,946 total in round one (16,946 / 1,000 / 1,000), 47,460 in round two (45,460 / 1,000 / 1,000) and 102,859 in round three (100,459 / 1,200 / 1,200). Round one and two contexts are short Wikipedia passages (250-600 characters) drawn from the HotpotQA dataset; round three broadens to news text (via Common Crawl), fiction (StoryCloze, the Children's Book Test), formal spoken transcripts (MASC), procedural text (WikiHow) and the RTE5 dataset. The GitHub repository states the dataset is licensed under Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0); all splits, including test-set labels, are distributed openly rather than held out behind a leaderboard.

## Who publishes it

ANLI comes from Facebook AI Research, with the University of North Carolina at Chapel Hill, published as "Adversarial NLI: A New Benchmark for Natural Language Understanding" at ACL 2020 by Yixin Nie, Adina Williams, Emily Dinan, Mohit Bansal, Jason Weston and Douwe Kiela. The authors host the reference data and code at github.com/facebookresearch/anli, with a project page at adversarialnli.com that the repository itself describes as a demo rather than an ongoing submission leaderboard.

## Lineage

ANLI was built as a direct response to SNLI and MNLI (`snli` and `mnli`, neither yet a page in this repository), which the authors argue had become vulnerable to annotation artifacts that let models do well without performing real inference. It has no formal predecessor benchmark of its own construction and no successor or variant id is tracked in this repository. lm-evaluation-harness and OpenCompass both expose it as three per-round tasks grouped under one `anli` tag; none of the three rounds has its own page here.

## Saturation and contamination

No dedicated current leaderboard or recent top-score figure was confirmed from a source opened during this research; the project's own web page functions as a demo rather than a tracked, ongoing submission board. Because each round's examples were written to fool the strongest contemporary model available to the annotators, and current frontier models are far stronger than the RoBERTa ensembles used to filter round three, scores have plausibly risen substantially since 2020. All three rounds' labels have been public on GitHub and Hugging Face since 2019-2020, and the round one and two contexts are drawn from HotpotQA's Wikipedia passages, themselves widely mirrored across the web, so contamination through broad pretraining is plausible. No dedicated ANLI contamination study was found in the sources consulted.

## How to run it

lm-evaluation-harness implements `anli_r1`, `anli_r2` and `anli_r3` as separate tasks grouped under the `anli` tag, scored by comparing the log-likelihood the model assigns to each of the three label continuations rather than by free generation. OpenCompass carries equivalent generative (`anli_gen`) and log-likelihood (`anli_ppl`) configurations. Because the three rounds differ systematically in source genre and difficulty, a single pooled ANLI accuracy can obscure large per-round gaps; check whether a reported score is pooled or per-round before comparing across papers.

## Reading the numbers

A high pooled ANLI score suggests a model resists the kind of adversarially constructed inference traps that defeated 2019-2020-era systems, but says less about inference ability in general than about resistance to that specific historical attack surface. Because round three is both the hardest and the most recent round, and pooled scores can hide a model doing well on R1 while struggling on R3, look at per-round numbers rather than the pooled average when they are available. As with any NLI benchmark whose full labels have been public for several years, treat an unusually high score with some caution absent corroboration from a fresher inference benchmark.
