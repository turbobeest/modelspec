---
id: math_500
name: MATH-500
aliases: ["MATH500", "hendrycks_math500", "minerva_math500"]
page_kind: benchmark
category: math
subcategory: "competition mathematics"
status: active
summary: "A fixed 500-problem subset of the MATH test set used to grade free-response competition mathematics after the rest of the split was moved into training data."
measures: >
  MATH-500 gives a model 500 written competition mathematics problems spanning algebra, geometry,
  number theory, counting and probability, precalculus, intermediate algebra and prealgebra. The
  model reads a problem statement in English and must produce a worked solution ending in a final
  answer; there are no answer choices. It tests multi-step symbolic and numeric reasoning and
  correct execution of a solution plan, not speed, tool use, or any skill beyond English-language
  mathematics.
task_format: "Free-response: read a competition math problem, output a worked solution and a final answer (typically after 'Answer:' or boxed)."
metric:
  name: "accuracy (pass@1)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "No confirmed random-guess or human baseline for this specific 500-item split; free-response grading has no meaningful chance rate."
dataset:
  size: 500
  size_note: "500 problems held out from the original MATH test split of 5,000; the other 4,500 MATH test problems were moved into the training set for this evaluation."
  url: "https://huggingface.co/datasets/HuggingFaceH4/MATH-500"
  license: ""
  languages: ["en"]
  modalities: ["text"]
  splits: "single 'test' split, 500 rows"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors: ["Hunter Lightman", "Vineet Kosaraju", "Yura Burda", "Harri Edwards", "Bowen Baker", "Teddy Lee", "Jan Leike", "John Schulman", "Ilya Sutskever", "Karl Cobbe"]
  url: "https://github.com/openai/prm800k"
paper:
  title: "Let's Verify Step by Step"
  arxiv: "2305.20050"
  url: "https://arxiv.org/abs/2305.20050"
  year: 2023
leaderboard_url: "https://artificialanalysis.ai/evaluations/math-500"
repo_url: "https://github.com/openai/prm800k"
released: "2023-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 99.4
  as_of: "2026-09"
  note: "Artificial Analysis's independently run leaderboard has GPT-5 (high) at 99.4%, with o3, Grok 3 mini Reasoning (high), GPT-5 (medium) and Claude 4 Sonnet all at 99.1-99.2%; top models are separated by tenths of a point."
contamination:
  risk: high
  note: "Answers and solutions are distributed in the open dataset. The source MATH corpus has circulated since 2021 and was the subject of a January 2025 DMCA takedown by Art of Problem Solving alleging over 10,000 of its 12,500 problems were copied from AoPS's Alcumus platform. Wu et al. 2025 (arXiv 2507.10532) report memorization-consistent behaviour by Qwen2.5-series models specifically on MATH-500."
harness:
  lm_eval: "hendrycks_math500, minerva_math500"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "OpenAI's openai/simple-evals loads MATH-500 via the math_500_test split in math_eval.py."
tags: ["math", "competition-math", "chain-of-thought", "free-response"]
sources:
  - url: "https://arxiv.org/abs/2305.20050"
    title: "Let's Verify Step by Step (Lightman et al., 2023)"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2103.03874"
    title: "Measuring Mathematical Problem Solving With the MATH Dataset (Hendrycks et al., 2021)"
    accessed: "2026-09-07"
  - url: "https://github.com/openai/prm800k"
    title: "openai/prm800k GitHub repository (math_splits/test.jsonl, MIT licence)"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/HuggingFaceH4/MATH-500"
    title: "HuggingFaceH4/MATH-500 dataset card"
    accessed: "2026-09-07"
  - url: "https://github.com/hendrycks/math"
    title: "hendrycks/math GitHub repository"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/hendrycks/competition_math"
    title: "hendrycks/competition_math dataset page (shows DMCA takedown notice)"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/huggingface-legal/takedown-notices/blob/main/2025/2025-01-02-AoPS.md"
    title: "Hugging Face legal takedown notice, Art of Problem Solving vs. hendrycks/competition_math"
    accessed: "2026-09-07"
  - url: "https://github.com/openai/simple-evals/blob/main/math_eval.py"
    title: "openai/simple-evals math_eval.py"
    accessed: "2026-09-07"
  - url: "https://github.com/openai/simple-evals/blob/main/README.md"
    title: "openai/simple-evals README"
    accessed: "2026-09-07"
  - url: "https://artificialanalysis.ai/evaluations/math-500"
    title: "MATH-500 Benchmark Leaderboard | Artificial Analysis"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2507.10532"
    title: "Reasoning or Memorization? Unreliable Results of Reinforcement Learning Due to Data Contamination (Wu et al., 2025)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice G"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MATH-500 gives a model 500 written competition mathematics problems drawn from algebra, geometry,
number theory, counting and probability, precalculus, intermediate algebra and prealgebra. The
model is given a problem statement in English and must produce a worked solution and a final
answer as free text; there are no answer choices to pick from. It exercises multi-step symbolic
and numeric reasoning: understanding what a problem is asking, planning a solution route, and
executing algebraic or geometric manipulation correctly. It does not test speed, tool use, or any
language beyond English.

## How it is scored

Grading compares a model's final answer against the reference answer, not the reasoning that
produced it. OpenAI's reference implementation (simple-evals, `math_eval.py`) asks for the final
line of a response to read "Answer: $ANSWER", extracts that line with a regular expression, and
checks it against the reference using a separate LLM call as an equality checker, since a correct
answer can be written more than one way (1/2 vs 0.5, for example). Reported numbers are usually
pass@1 accuracy under this protocol, but papers differ on sampling temperature, number of samples,
and whether they take a majority vote over several completions, so two MATH-500 numbers are only
directly comparable once you know both used the same protocol. No confirmed random-guess or human
baseline exists for this specific 500-item split.

## Dataset and licence

MATH-500 is 500 problems held out from the 5,000-problem test split of the original MATH dataset
(Hendrycks et al., 2021). OpenAI moved the other 4,500 MATH test problems into their training set
for process-supervision work and evaluated only on these 500, describing them as a representative,
independent and identically distributed sample of the original test split. Each item has a problem
statement, a full worked solution, a final answer, a subject label (one of seven categories such as
algebra, geometry or number theory) and a difficulty level from 1 to 5. It ships as a single "test"
split of 500 rows of English text, and the answers are public: there is no held-out grading server.
No licence is stated on the HuggingFaceH4/MATH-500 dataset card. The source corpus is legally
contested: Art of Problem Solving filed a DMCA takedown against the `hendrycks/competition_math`
dataset in January 2025, stating that more than 10,000 of the 12,500 MATH problems were copied from
its Alcumus learning platform, and asked that downstream datasets derived from MATH be removed too.
MATH-500 remains hosted on Hugging Face as of this writing, but its licensing status is unresolved.

## Who publishes it

The 500-problem split was defined by Hunter Lightman, Vineet Kosaraju, Yura Burda, Harri Edwards,
Bowen Baker, Teddy Lee, Jan Leike, John Schulman, Ilya Sutskever and Karl Cobbe at OpenAI, in "Let's
Verify Step by Step" (arXiv 2305.20050, posted May 2023, published at ICLR 2024). It builds on the
MATH dataset published by Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart,
Eric Tang, Dawn Song and Jacob Steinhardt at NeurIPS 2021. OpenAI's own simple-evals repository uses
MATH-500 as its default math evaluation for o1-class models onward, and independent trackers such as
Artificial Analysis run their own copy of the eval and publish current scores.

## Lineage

MATH-500 is a fixed subset of the MATH test set (Hendrycks et al., 2021); the full 12,500-problem
MATH dataset does not yet have its own page in this repository. MATH-500 has no announced successor
of its own. The same contamination pressure that pushed OpenAI toward a smaller held-out set has
since pushed newer math evaluations toward problems dated after a model's training cutoff, a route
MATH-500 cannot take, since its 500 problems and reference answers have been public since 2023.

## Saturation and contamination

MATH-500 is saturated for frontier models. On Artificial Analysis's independently run leaderboard
(accessed September 2026), GPT-5 (high) scores 99.4%, with o3, Grok 3 mini Reasoning (high), GPT-5
(medium) and Claude 4 Sonnet all at 99.1-99.2%; the top of the leaderboard is separated by tenths of
a point. Contamination risk is high: the answers are distributed in the open dataset, the source
MATH corpus has circulated since 2021, and Wu et al. (arXiv 2507.10532, 2025) report
memorization-consistent behaviour by Qwen2.5-series models specifically on MATH-500, which casts
doubt on reinforcement-learning gains measured against it. A high score today separates strong
models from each other by very little, and says nothing about whether that separation is genuine.

## How to run it

OpenAI's openai/simple-evals repository is the reference implementation (`math_eval.py`), which
loads the `math_500_test` split and grades with the equality-checker protocol described above. The
dataset is also mirrored at HuggingFaceH4/MATH-500. lm-evaluation-harness ships two tasks for this
split, `hendrycks_math500` and `minerva_math500`, both loading `HuggingFaceH4/MATH-500` directly and
differing only in the answer-extraction and grading style they inherit from `hendrycks_math` and
`minerva_math` respectively; those two parent tasks still run the full 5,000-item set, so check which
task name produced a number before comparing it. Because grading depends on an LLM
equality checker rather than exact string match, scores depend on which model performs that check
and on the exact prompt template, a common source of small cross-paper differences.

## Reading the numbers

A high MATH-500 score mainly shows that a model can execute multi-step symbolic manipulation
reliably and format its answer the way the grader expects. It does not show the model is free of
contamination on this exact test set; given the DMCA dispute over the source data and the
memorization findings above, treat any single MATH-500 number with more caution than a freshly
built benchmark deserves. Because the ceiling is close to 100%, small differences between top models
are not meaningful on their own; a harder, more recent competition-math benchmark separates frontier
models better. Before comparing two reported MATH-500 numbers, check the sampling and grading
protocol behind each one.
