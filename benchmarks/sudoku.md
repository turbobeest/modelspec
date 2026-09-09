---
id: sudoku
name: "Sudoku"
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "interactive symbolic / logical reasoning"
status: active
summary: "Programmatic BIG-bench task where a model interactively fills in procedurally generated Sudoku puzzles one cell at a time, scored on command syntax, rule-following and full solution."
measures: "This task gives a model a Sudoku puzzle (4x4, 9x9 or 16x16) rendered as a text grid and asks it to fill empty cells one at a time by issuing repeated '<x> <y> <digit>' commands, receiving the updated board state after each move. It tests whether a model can follow a precisely specified, hard rule set (no repeated digit in a row, column or sub-grid), reason symbolically about a Cartesian coordinate grid, and sustain a multi-step interactive procedure, rather than producing a single free-form answer. The task's author designed it specifically because Sudoku is easy for a basic computer program (e.g. constraint propagation) but was, at the time of authoring, hard for language models, making it a probe of symbolic/algorithmic reasoning rather than pattern-matching over text."
task_format: "Free-text, multi-turn interactive generation: the model emits one move command per turn (parsed by regex), receives the updated board and any error message, and this repeats until the puzzle's empty cells are exhausted or the context budget is reached."
metric:
  name: "combined score"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: "The reference task.py computes, per puzzle, a syntax score (fraction of turns with a validly parsed command), a rules score (fraction of turns that were valid Sudoku moves) and a solution score (1.0 if the puzzle was fully and correctly solved, else 0.0), then combines them as combined = (syntax + 2*rules + solution) / 4, i.e. rule-following is weighted twice as heavily as syntax or full solution. This differs from the task's own README, which describes the intended weighting as syntax 0-0.25, rules 0-0.25 and solution 0-0.5 (summing to 0-1); this page follows the executable task.py as the authoritative scoring logic and flags the mismatch with the README prose. Scores are reported per one of 15 subtasks (3 board sizes x 5 difficulty levels); no random baseline is defined by the source, and none of the small open-source models the author tested (GPT-2 family, OpenAI GPT) scored above zero."
dataset:
  size: null
  size_note: "The task procedurally generates puzzles at evaluation time rather than shipping a fixed item set; there is no fixed dataset size to record. The default configuration (num_trials=60) evaluates 60 puzzles split across 3 board sizes (4x4, 9x9, 16x16) and 5 difficulty levels each (15 size-by-difficulty subtasks), and the task's own metadata caps the run at 4,868 model queries for that default; the task directory's auto-generated header separately reports 4,808 free-text queries and 0 multiple-choice queries from an actual dummy-model run, a small discrepancy from the docstring's stated 4,868 that this page could not resolve from the sources reviewed."
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sudoku"
  license: "Apache-2.0 (BIG-bench repository); the puzzle-generation code is also described as drawing on and using Peter Norvig's 'Solving Every Sudoku Puzzle' essay code under Norvig's own permissive license"
  languages: ["en"]
  modalities: ["text"]
  splits: "no fixed splits; puzzles are generated on the fly from a seeded random number generator"
  public_test_set: true
publisher:
  org: "Google (BIG-bench collaboration)"
  authors: ["Adrià Garriga-Alonso"]
  url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sudoku"
paper:
  title: "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models"
  arxiv: "2206.04615"
  url: "https://arxiv.org/abs/2206.04615"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sudoku"
released: "2022"
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
  note: "The task's own README states that all small GPT-2-family and GPT models the author tested achieved zero score, unable to follow the command syntax at all, and speculates (without measurement) that GPT-3-class models would do better. No source reviewed here gives a dated, current score for frontier models, so present-day saturation status is not established."
contamination:
  risk: low
  note: "Puzzles are procedurally generated from a random seed at evaluation time rather than drawn from a fixed public item bank, so the exact puzzle instances a model is scored on are not fixed, memorizable content; the task's canary string and BIG-bench's general public GitHub hosting still mean the task's prompt format, rules text and generation code are publicly known."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: "sudoku"
  other: ""
tags: ["logical reasoning", "interactive", "programmatic", "game-play", "symbolic-reasoning"]
sources:
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/sudoku"
    title: "sudoku task directory, BIG-bench"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/sudoku/README.md"
    title: "sudoku README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google/BIG-bench/main/bigbench/benchmark_tasks/sudoku/task.py"
    title: "sudoku task.py (reference implementation)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2206.04615"
    title: "Beyond the Imitation Game (BIG-bench paper)"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench/blob/main/LICENSE"
    title: "BIG-bench repository LICENSE"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-005 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-005"
---

## What it measures

The Sudoku task asks a model to solve a procedurally generated Sudoku puzzle (4x4, 9x9 or 16x16) interactively: it is shown the current board as a text grid and must issue one move at a time in the form "`<x> <y> <digit>`", receiving the updated board and feedback (invalid move, cell already filled, or acceptance) before the next turn. The author designed it to isolate the ability to follow a precisely specified, hard rule set on the spot, reason over a Cartesian coordinate grid, and vary effort per output token (a short, information-dense command rather than fluent prose), in a domain that is easy for a simple constraint-solving program but was hard for the language models available when the task was written.

Because the puzzle is generated fresh each run from a seed, the task also measures sustained multi-turn interaction: solving a large, empty 16x16 puzzle can require over 200 sequential correct moves.

## How it is scored

The reference `task.py` computes three per-puzzle components: a syntax score (the fraction of turns where the model's output parsed as a valid command), a rules score (the fraction of turns that were legal Sudoku moves), and a solution score (1.0 if the puzzle ended fully and correctly solved, 0.0 otherwise). These combine as `combined = (syntax + 2*rules + solution) / 4`, giving rule-following twice the weight of either syntax or a full solve. This is the score actually computed by the executable code; the task's own README describes a different intended weighting (syntax 0-0.25, rules 0-0.25, solution 0-0.5), which does not match the code's `(syntax + 2*rules + solution)/4` formula -- a discrepancy this page flags rather than resolves. Scores are reported separately for each of 15 subtasks, one per combination of board size (4x4/9x9/16x16) and one of five procedurally controlled difficulty levels; there is no single scalar "full" score computed by the task itself, though BIG-bench's reporting layer produces an aggregate "normalized aggregate score" plot across subtasks.

## Dataset and licence

There is no fixed item set: puzzles are generated at evaluation time by code adapted from Peter Norvig's "Solving Every Sudoku Puzzle" essay, seeded for reproducibility. The default configuration runs 60 puzzles (num_trials=60), split evenly across the three board sizes and, within each size, across the five difficulty levels, and the task's declared metadata caps this at 4,868 model queries; a recorded dummy-model run in the task's own README instead shows 4,808 free-text queries, a small unexplained discrepancy. The BIG-bench repository is Apache-2.0 licensed; the puzzle-generation code additionally credits and uses logic from Norvig's own permissively licensed essay code.

## Who publishes it

The task was contributed to BIG-bench by Adrià Garriga-Alonso and appears in the BIG-bench collaboration's 2022 paper "Beyond the Imitation Game." There is no independent leaderboard beyond the auto-generated performance plots in the task's own `results/` directory.

## Lineage

The task has no family page, predecessor or successor confirmed from a primary source in this repository. Its README places it in the broader context of symbolic-AI-versus-deep-learning research (citing SATNet as related work on differentiable Sudoku solving) without naming a direct predecessor benchmark.

## Saturation and contamination

The task's README reports that every small open-source model the author tested (the GPT-2 family and OpenAI GPT) scored zero, unable to produce valid command syntax at all; it speculates, without evidence, that GPT-3-class models would do somewhat better. No source reviewed here gives a current, dated score for frontier models, so saturation status is unknown. Because puzzles are procedurally generated per run rather than fixed and published, direct answer memorization is unlikely, though the task's prompt format and rules text are public.

## How to run it

The task runs through BIG-bench's programmatic task interface (`task.py`, using a custom `sudoku.py` puzzle generator, not a JSON task) as `sudoku`, configurable via `num_trials`, `seed` and `max_context_length`. This task was not found in the lm-evaluation-harness's dynamically generated BIG-bench task list (drawn from the JSON-only `hails/bigbench` Hugging Face mirror), and no inspect_evals, HELM or OpenCompass integration was confirmed from a primary source for this page; its multi-turn, model-generates-and-receives-feedback design does not fit a single-shot JSON multiple-choice or generate-until harness without custom support.

## Reading the numbers

A high combined score indicates a model can sustain a long, rule-constrained interactive procedure: parsing feedback, avoiding illegal moves, and often fully solving the puzzle. Because rule-following is weighted twice as heavily as syntax or a complete solve in the executable scoring, a model can score moderately well by making many legal-but-unproductive moves without ever finishing the puzzle, so the combined score alone does not indicate solve rate -- check the "solution" component specifically for that. Scores should also be read per board size and difficulty rather than as one aggregate, since the task explicitly warns that harder (emptier) boards can inflate scores for weak models simply because more random-ish moves happen to be legal.
