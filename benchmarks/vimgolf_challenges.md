---
id: vimgolf_challenges
name: "VimGolf Challenges (inspect_evals)"
aliases:
  - "vimgolf_single_turn"
  - "VimGolf"
page_kind: benchmark
category: coding
subcategory: "single-turn Vim keystroke sequences on public VimGolf challenges"
status: active
summary: "Single-turn inspect_evals task: emit a Vim keystroke string that turns each of 612 public VimGolf inputs into the target buffer."
measures: >
  The model sees a VimGolf challenge (description, start buffer, target buffer) and must
  write one line of Vim keycodes that transforms the start text into the target. It does
  not get an interactive Vim session. A solution is correct only if it is non-empty, uses
  fewer keystrokes than the target's character length (so dumping the output file is
  illegal), and a Dockerised Vim run reproduces the target (checksum or formatted text).
  The skill is Vim editing, not GUI computer use.
task_format: >
  Single-turn generate. A system prompt explains VimGolf notation and shows two example
  solutions. The last non-empty line of the completion is the candidate. Scoring runs
  vimgolf-verifier.py inside Docker (image built from the task Dockerfile, 15s timeout).
  inspect eval id is vimgolf_single_turn; the directory and extra are vimgolf_challenges.
metric:
  name: "accuracy (binary correct/incorrect per challenge)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    inspect_ai accuracy plus stderr. The task README reports ollama/gpt-oss:20b at 0.118
    accuracy (72 correct, 540 incorrect) on the 612-task public set. Human VimGolf scores
    are keystroke counts on vimgolf.com, not this binary "valid under the length cap"
    metric, so no human baseline is recorded. Random keystrokes have no meaningful chance
    rate.
dataset:
  size: 612
  size_note: >
    eval.yaml dataset_samples: 612. inspect loads
    cybergod-kevin/vimgolf-public-challenges-inspect-eval split test, revision
    909a17f2b57d5866c077ebac019f6b0f271de919; datasets-server also reports 612 test rows.
    Upstream scrape James4Ever0/vimgolf_challenges_and_solutions holds public challenges
    from vimgolf.com plus a published worst solution per challenge. This eval does not
    use the interactive james4ever0/vimgolf-gym environment.
  url: "https://huggingface.co/datasets/cybergod-kevin/vimgolf-public-challenges-inspect-eval"
  license: "MIT on inspect_evals (UK AI Security Institute, 2024). James4Ever0/vimgolf_challenges_and_solutions is Unlicense. Challenge text originates from vimgolf.com."
  languages:
    - en
  modalities:
    - text
    - code
  splits: "single test split of 612 challenges; no train split in the inspect dataset"
  public_test_set: true
publisher:
  org: "UK AI Security Institute (inspect_evals packaging); challenges from vimgolf.com; inspect port by james4ever0"
  authors:
    - "james4ever0"
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/vimgolf_challenges"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/vimgolf_challenges"
released: "2025-10"
last_updated: "2026-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    The only numeric result opened for this page is gpt-oss:20b at 0.118 accuracy
    (11.8%; 72 / 612) in the inspect README. That is not a frontier ceiling, so it is
    not recorded as top_score. It only shows the public set is far from solved for that
    model. Changelog version 2-A (2026-02-16) is the eval comparability version.
contamination:
  risk: medium
  note: >
    Challenges and worst-solution keystroke strings are public on vimgolf.com and in the
    Unlicense scrape. Models may have seen the buffers. The length cap blocks the naive
    paste-the-output cheat; it does not block memorising a known best solution.
harness:
  lm_eval: ""
  inspect_evals: "vimgolf_single_turn"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Directory, extra and eval.yaml dependency id are vimgolf_challenges. Runnable inspect task is vimgolf_single_turn. pip install inspect-evals[vimgolf_challenges]. Docker required for the scorer sandbox."
tags:
  - vim
  - code-editing
  - single-turn
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/vimgolf_challenges/README.md"
    title: "inspect_evals vimgolf_challenges README (612 tasks, scoring, gpt-oss:20b 0.118)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/vimgolf_challenges/eval.yaml"
    title: "eval.yaml: task vimgolf_single_turn, 612 samples, version 2-A"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/vimgolf_challenges/vimgolf_challenges.py"
    title: "Task implementation: Docker scorer, length cap, Hub revision pin"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/James4Ever0/vimgolf_challenges_and_solutions/raw/main/README.md"
    title: "Upstream scrape card (Unlicense, vimgolf.com challenges)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=cybergod-kevin/vimgolf-public-challenges-inspect-eval"
    title: "inspect dataset: 612 test examples"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT licence"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/pull/517"
    title: "PR 517 VimGolf Challenges implementation, merged 2025-10-29"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-023 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-023"
---

## What it measures

Each item is a public VimGolf puzzle: start text in, target text out, plus a short English description. The model must emit Vim keystrokes (`i…<Esc>`, `:%s/…/g<NL>:wq<NL>`, and so on) that a real Vim, running in Docker, applies to the start buffer. Success is a correct final buffer, not a pretty explanation. The length rule forbids typing the whole target. This page documents the inspect_evals single-turn port, not an agent loop in a live terminal.

## How it is scored

The scorer takes the last non-empty line of the completion. It tokenises that line as VimGolf keycodes. If the key count is below the target length and the Docker verifier matches the target (SHA-256 or formatted text), the item is correct; otherwise it is incorrect. Timeouts (15s) count as failures. The README's only opened result is gpt-oss:20b at 11.8% (72 / 612). That figure is accuracy, not a human keystroke rank from vimgolf.com.

## Dataset and licence

612 public challenges. inspect pins `cybergod-kevin/vimgolf-public-challenges-inspect-eval` at revision `909a17f2…`. The scrape `James4Ever0/vimgolf_challenges_and_solutions` is Unlicense; inspect_evals is MIT. Challenge content still comes from vimgolf.com. A "worst solution" is shipped for humans on the site; the inspect scorer does not grade against that string.

## Who publishes it

inspect_evals is maintained by the UK AI Security Institute. The VimGolf task was contributed by james4ever0. PR 517 merged on 2025-10-29. Eval metadata version 2-A is dated 2026-02-16. There is no paper. Two netlify writeups are linked from the README; this page did not use them as scoring sources.

## Lineage

Not a CUA/GUI benchmark and not vimgolf-gym's interactive environment, which the README explicitly does not use. No predecessor id in this repository. The census directory name `vimgolf_challenges` is the extra/dependency; the runnable Inspect name is `vimgolf_single_turn`.

## Saturation and contamination

11.8% on gpt-oss:20b is an existence proof that the set still fails that model, not a SOTA. Challenges have been public for years, so memorisation of famous solutions is possible. The paste-the-output cheat is blocked by the keystroke cap.

## How to run it

```bash
pip install inspect-evals[vimgolf_challenges]
inspect eval inspect_evals/vimgolf_single_turn --model <model>
```

Docker must work for the current user. `inspect_evals/vimgolf_challenges` as an eval name is the folder, not the `@task`. Comparability is tied to version 2-A.

## Reading the numbers

A high accuracy means the model can emit working, non-trivial Vim macros for these 612 buffers in one shot. It does not measure multi-turn repair, GUI editing, or general coding. Failures mix wrong edits, over-long dumps, verifier timeouts, and format mistakes (the prompt forbids wrapping the solution in fences). Compare runs only under the same inspect version and Docker verifier.
