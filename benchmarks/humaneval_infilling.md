---
id: humaneval_infilling
name: "HumanEval-Infilling"
aliases: []
page_kind: benchmark
category: coding
subcategory: "code infilling / fill-in-the-middle"
status: active
summary: "Four fill-in-the-middle tasks built by masking spans of HumanEval's solutions; two (single/multi-line) come from the InCoder paper, two (random-span) were added by OpenAI's FIM paper."
measures: >
  HumanEval-Infilling tests a model's ability to fill in a missing piece of code given the text on
  both sides of the gap, rather than only continuing left to right. Each task takes one of HumanEval's
  164 canonical solutions and removes a span of it -- a single line, several consecutive lines, or a
  randomly chosen character span -- so the model must produce the missing piece from the docstring,
  the code before the gap, and the code after it. This exercises a different skill from HumanEval's
  own generate-from-scratch task, closer to how code gets edited than to how it gets written new.
task_format: >
  Given a function's prefix and suffix with a span of the canonical solution removed (a single line,
  several consecutive lines, or a random character span), generate the missing span; the reassembled
  function is graded by executing it against HumanEval's original unit tests (pass@k), alongside an
  exact-match check against the removed text.
metric:
  name: "pass@1"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    lm-evaluation-harness reports pass@1 per subset and aggregates the four subsets (single-line,
    multi-line, random-span, random-span-light) with an unweighted mean, despite the subsets ranging
    from 164 to 5,815 tasks, so one blended score can be dominated by whichever subset happens to
    score best or worst. The InCoder and FIM papers also report exact match as a secondary metric. No
    random-guess or human baseline is established.
dataset:
  size: null
  size_note: >
    No single size: four differently sized subsets are built by masking spans out of HumanEval's 164
    canonical solutions. Per the lm-evaluation-harness task README, single-line infilling has 1,033
    tasks (one per non-blank line across all 164 solutions), multi-line has 5,815 (one per contiguous
    span of non-blank lines), random-span has 1,640, and random-span-light -- a smaller, faster
    version -- has 164, one per problem.
  url: "https://github.com/openai/human-eval-infilling"
  license: "MIT"
  languages:
    - English
  modalities:
    - text
    - code
  splits: "four task subsets (single-line, multi-line, random-span, random-span-light), each derived from HumanEval's 164-problem test set; no train split"
  public_test_set: true
publisher:
  org: "OpenAI"
  authors:
    - "Mohammad Bavarian"
    - "Heewoo Jun"
    - "Nikolas Tezak"
    - "John Schulman"
    - "Christine McLeavey"
    - "Jerry Tworek"
    - "Mark Chen"
  url: "https://github.com/openai/human-eval-infilling"
paper:
  title: "Efficient Training of Language Models to Fill in the Middle"
  arxiv: "2207.14255"
  url: "https://arxiv.org/abs/2207.14255"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/openai/human-eval-infilling"
released: "2022-07"
last_updated: ""
lineage:
  family: "humaneval"
  predecessor: "humaneval"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No current, actively maintained leaderboard for HumanEval-Infilling could be found, so saturation
    is graded "unknown" rather than inferred from either source paper's now-dated model comparisons.
contamination:
  risk: high
  note: >
    Contamination risk here is arguably sharper than for an ordinary HumanEval score: every task's
    expected answer is a verbatim substring of a HumanEval canonical solution that has been sitting in
    a public GitHub repository since July 2021, so a model that has simply memorised HumanEval's
    solutions can reconstruct many infilling spans without any real fill-in-the-middle ability.
harness:
  lm_eval: "humaneval_infilling"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >-
    lm-evaluation-harness implements the group `humaneval_infilling` over four child tasks
    (humaneval_single_line_infilling, humaneval_multi_line_infilling, humaneval_random_span_infilling,
    humaneval_random_span_infilling_light), built on Hugging Face's `evaluate` code_eval metric. The
    original reference implementation is openai/human-eval-infilling.
tags:
  - code-generation
  - python
  - fill-in-the-middle
  - infilling
  - pass-at-k
  - functional-correctness
sources:
  - url: "https://arxiv.org/abs/2207.14255"
    title: "Efficient Training of Language Models to Fill in the Middle"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2204.05999"
    title: "InCoder: A Generative Model for Code Infilling and Synthesis"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2207.14255"
    title: "Efficient Training of Language Models to Fill in the Middle (full text, for the Fried et al. 2022 attribution of the single/multi-line tasks)"
    accessed: "2026-09-08"
  - url: "https://github.com/openai/human-eval-infilling"
    title: "openai/human-eval-infilling repository"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/humaneval_infilling/README.md"
    title: "lm-evaluation-harness: humaneval_infilling task README"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/humaneval_infilling/humaneval_infilling.yaml"
    title: "lm-evaluation-harness: humaneval_infilling group config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

HumanEval-Infilling tests fill-in-the-middle completion: given the code both before and after a gap,
can a model produce what belongs in the gap, rather than only continuing text left to right. Each
task takes one of HumanEval's 164 canonical solutions and removes a piece of it -- a single line, a
run of consecutive lines, or a randomly chosen span of characters -- leaving the model the docstring,
the code before the gap, and the code after it. This is a different skill from HumanEval's own
code-generation task: a model that writes a correct function from scratch is not automatically good
at inserting a missing piece into someone else's code with both sides already fixed, which is closer
to how code gets edited in practice than to writing it from nothing.

## How it is scored

A completion is checked two ways: whether the reassembled function (prefix plus generated span plus
suffix) passes HumanEval's original unit tests, and whether the generated span exactly matches the
text that was removed. The lm-evaluation-harness implementation reports pass@1 and aggregates the
four subsets (single-line, multi-line, random-span, random-span-light) with an unweighted mean,
despite the subsets ranging from 164 to 5,815 tasks, so a single reported score can be dominated by
whichever subset happens to score best or worst rather than reflecting task volume.

## Dataset and licence

There is no single dataset size: HumanEval-Infilling packages four differently sized task subsets
built by masking HumanEval's 164 canonical solutions. Per the lm-evaluation-harness task README,
single-line infilling has 1,033 tasks (one per non-blank line across all 164 solutions), multi-line
has 5,815 (one per contiguous span of non-blank lines), random-span has 1,640, and random-span-light
-- a smaller, faster-to-run version -- has 164, one per problem. The reference repository,
openai/human-eval-infilling, is released under the MIT licence. Prompts are in English; the only
programming language covered is Python.

## Who publishes it

The bundled benchmark and its reference harness were released by OpenAI's Mohammad Bavarian, Heewoo
Jun, Nikolas Tezak, John Schulman, Christine McLeavey, Jerry Tworek and Mark Chen in "Efficient
Training of Language Models to Fill in the Middle," posted to arXiv in July 2022. Two of its four
subsets are not new to that paper: the paper's own text credits the single-line and multi-line
infilling tasks to Daniel Fried and co-authors' InCoder paper ("Fried et al. 2022"), which built them
by masking non-blank lines out of HumanEval's canonical solutions several months earlier, confirmed
directly in InCoder's own paper. OpenAI's own contribution was the two random-span variants, plus
packaging all four as one released benchmark and harness. OpenAI maintains the
openai/human-eval-infilling repository.

## Lineage

HumanEval-Infilling's predecessor is HumanEval (this repository's humaneval page): every task is
built by masking spans out of HumanEval's own canonical solutions, so its 164-problem base carries
the same age and exposure as the parent. Its own lineage is unusually split: half of its four subsets
(single-line, multi-line) trace to Daniel Fried et al.'s InCoder paper (arXiv 2204.05999, April
2022), which does not have its own page in this repository, while the other half (random-span,
random-span-light) and the bundled repository that packages all four originate in OpenAI's later FIM
paper (arXiv 2207.14255, July 2022). A report that simply cites "the InCoder benchmark" or "the FIM
benchmark" is describing only part of what the id humaneval_infilling actually runs.

## Saturation and contamination

No current, actively maintained leaderboard for HumanEval-Infilling could be found, so saturation is
graded "unknown" rather than inferred from either paper's now-dated model comparisons. Contamination
risk is high, and arguably sharper than for an ordinary HumanEval score: every task's expected answer
is a verbatim substring of a HumanEval canonical solution that has been sitting in a public GitHub
repository since July 2021, so a model that has simply memorised HumanEval's solutions can reconstruct
many infilling spans without any real fill-in-the-middle ability.

## How to run it

lm-evaluation-harness implements all four subsets under the task group `humaneval_infilling`
(individually `humaneval_single_line_infilling`, `humaneval_multi_line_infilling`,
`humaneval_random_span_infilling`, `humaneval_random_span_infilling_light`), built on the `code_eval`
metric from Hugging Face's `evaluate` package, which -- like the original HumanEval harness --
executes untrusted, model-generated code and requires deliberately enabling that behaviour. The
original reference implementation, openai/human-eval-infilling, provides the same four benchmarks
directly.

## Reading the numbers

A high HumanEval-Infilling score shows a model can use context on both sides of a gap, useful signal
for editor-style code completion rather than generate-from-scratch coding. Because every answer is
drawn from HumanEval's long-public solutions, a high score is even less informative about genuine
infilling ability than a high HumanEval score is about genuine synthesis ability -- check whether a
model was evaluated on this benchmark specifically for fill-in-the-middle capability (typically base,
completion-focused code models) rather than assuming a chat-tuned model was tested on it at all.
Because the four subsets are unevenly sized and averaged without weighting, look at the per-subset
breakdown, not just one blended number, before comparing two models.
