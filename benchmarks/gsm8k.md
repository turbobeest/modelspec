---
id: gsm8k
name: "GSM8K"
aliases: ["Grade School Math 8K"]
page_kind: benchmark
category: math
subcategory: "grade-school arithmetic word problems"
status: active
summary: "8.5K grade-school math word problems scored by exact match on the final numeric answer, testing multi-step arithmetic reasoning."
measures: "GSM8K tests whether a model can solve short, English-language math word problems that take two to eight linked arithmetic steps to reach an answer, such as working out a total after several purchases and discounts. OpenAI wrote the problems so that a bright middle-school student could solve every one of them by hand, deliberately excluding algebra, calculus or other advanced mathematics. The skill under test is multi-step arithmetic planning and consistent calculation rather than mathematical sophistication."
task_format: "Free-response word problem in English; the model produces a reasoning chain ending in one final numeric answer, extracted after a `####` marker and graded by exact match."
metric:
  name: "accuracy (exact-match final answer)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 8792
  size_note: "7,473 training problems + 1,319 test problems; a parallel Socratic-format version of each split adds auto-generated guiding sub-questions"
  url: "https://huggingface.co/datasets/openai/gsm8k"
  license: "MIT"
  languages: ["en"]
  modalities: ["text"]
  splits: "train (7,473) / test (1,319)"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors: ["Karl Cobbe", "Vineet Kosaraju", "Mohammad Bavarian", "Mark Chen", "Heewoo Jun", "Lukasz Kaiser", "Matthias Plappert", "Jerry Tworek", "Jacob Hilton", "Reiichiro Nakano", "Christopher Hesse", "John Schulman"]
  url: "https://github.com/openai/grade-school-math"
paper:
  title: "Training Verifiers to Solve Math Word Problems"
  arxiv: "2110.14168"
  url: "https://arxiv.org/abs/2110.14168"
  year: 2021
leaderboard_url: ""
repo_url: "https://github.com/openai/grade-school-math"
released: "2021-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 99.7
  as_of: "2026-04"
  note: "A third-party leaderboard aggregator put several frontier models at or above 99% as of April 2026 (Baidu's ERNIE 5.0 highest at 99.7%), leaving little room to separate current top models."
contamination:
  risk: medium
  note: "Test-set answers have been public since 2021. A 2024 NeurIPS study (the GSM1k paper) found accuracy drops of up to 8 points on a freshly written, matched-difficulty set, correlated with how likely a model was to regenerate GSM8K items verbatim -- evidence of memorization in several model families -- though the same study found frontier models showed comparatively little of this effect."
harness:
  lm_eval: "gsm8k"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["math", "word-problems", "chain-of-thought", "arithmetic", "exact-match"]
sources:
  - url: "https://arxiv.org/abs/2110.14168"
    title: "Training Verifiers to Solve Math Word Problems"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/openai/gsm8k"
    title: "openai/gsm8k dataset card"
    accessed: "2026-09-07"
  - url: "https://github.com/openai/grade-school-math"
    title: "openai/grade-school-math repository"
    accessed: "2026-09-07"
  - url: "https://github.com/openai/grade-school-math/blob/master/LICENSE"
    title: "grade-school-math LICENSE (MIT)"
    accessed: "2026-09-07"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/gsm8k/README.md"
    title: "lm-evaluation-harness gsm8k task README"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2405.00332"
    title: "A Careful Examination of Large Language Model Performance on Grade School Arithmetic (GSM1k)"
    accessed: "2026-09-07"
  - url: "https://www.codesota.com/llm/gsm8k-math"
    title: "GSM8K & MATH Benchmark Leaderboard 2025-2026"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

GSM8K tests whether a language model can solve grade-school-level math word problems that need several linked arithmetic steps rather than one calculation. Each item gives a short English story problem -- for example, working out how much change is left after a series of purchases -- and the model must produce a chain of reasoning that ends in a single numeric answer. OpenAI built the set so that "a bright middle school student" could solve every problem, deliberately staying below algebra or calculus. The skill under test is multi-step arithmetic planning and consistent calculation, not advanced mathematics.

## How it is scored

Models are scored by exact match on the final numeric answer, which reference solutions mark with a `####` delimiter after a written chain of reasoning; there is no partial credit for correct intermediate steps. The original paper evaluated fine-tuned GPT-3-scale models, with and without a learned verifier that reranked multiple sampled solutions. Later work standardized on zero-shot or few-shot chain-of-thought prompting with greedy decoding, which is how most model cards now report it. Because the paper does not fix a single prompt format, shot count and chain-of-thought phrasing vary between reporters, and self-consistency decoding (sampling many chains and voting) can add several points over greedy decoding.

## Dataset and licence

The public release holds 7,473 training problems and 1,319 test problems, each paired with a natural-language solution that carries calculator-style annotations (`<<...>>`) for intermediate arithmetic. A parallel "Socratic" version of each split adds auto-generated guiding sub-questions. Problems were written by human problem writers and checked through multiple rounds of worker-agreement review. OpenAI publishes the data and code on GitHub and Hugging Face under the MIT licence, and the test-set answers are public rather than held out.

## Who publishes it

GSM8K comes from Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, Christopher Hesse and John Schulman at OpenAI, published as "Training Verifiers to Solve Math Word Problems" on arXiv in October 2021. OpenAI maintains the reference dataset and scoring code at github.com/openai/grade-school-math. There is no OpenAI-run public leaderboard, but third parties score it continuously and most model cards report a GSM8K number.

## Lineage

GSM8K does not name a predecessor benchmark of its own. Reaching its difficulty ceiling prompted harder or contamination-resistant follow-ups outside this repository's current pages, including Scale AI's GSM1k -- a matched-difficulty, held-out replacement built specifically to test overfitting on GSM8K -- and Apple's GSM-Symbolic, which perturbs GSM8K-style problems to probe brittleness. Neither has a page in this repository yet, and no successor or variant id is tracked here.

## Saturation and contamination

Multiple frontier models now cluster at or above 99% accuracy: a third-party leaderboard aggregator put Baidu's ERNIE 5.0 at 99.7% as of April 2026, with several other frontier models at or near 99% the same month, leaving little room to separate current top systems. A 2024 NeurIPS study (the GSM1k paper) tested this directly by writing a fresh, matched-difficulty test set: accuracy dropped by up to 8 points on it, and the size of the drop correlated with how likely a model was to regenerate GSM8K items verbatim, evidence of memorization in several model families. The same study found frontier models showed comparatively little of this effect, so the ceiling looks more like a genuine capability limit for top models than pure memorization -- though the four-plus-year-old, publicly answered test set remains a plausible contamination vector for any model trained on general web text.

## How to run it

lm-evaluation-harness implements it as the `gsm8k` task family, including `gsm8k_cot` (chain-of-thought), `gsm8k_cot_self_consistency` (multi-sample voting) and a Llama-specific chat-template variant. OpenAI's own grade-school-math repository ships a reference scorer that strips the calculator annotations and checks the answer after `####`. Because shot count, chain-of-thought instructions and self-consistency sampling all move the score, two reported GSM8K numbers are only comparable when the evaluation protocol matches.

## Reading the numbers

A high GSM8K score by itself now says little about a frontier model, since most of them already sit at or near the ceiling; the benchmark mostly still distinguishes small or older models from current ones. A low score remains meaningful, flagging weak elementary arithmetic or an inconsistent reasoning chain. Given the age of the public test set and the documented memorization gap on GSM1k, treat any single GSM8K number as a rough signal and check harder, newer math benchmarks before drawing conclusions about a model's actual mathematical reasoning.
