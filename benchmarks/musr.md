---
id: musr
name: MuSR
aliases:
  - Multistep Soft Reasoning
page_kind: benchmark
category: reasoning
subcategory: multistep narrative and long-context reasoning
status: active
summary: Algorithmically generated murder mysteries, object placement puzzles and team allocation problems needing long-range narrative reasoning.
measures: >
  MuSR (Multistep Soft Reasoning) tests whether a model can answer a question that requires combining
  facts scattered across a long narrative, rather than reasoning that is stated in one place. Each item
  is an algorithmically generated story of roughly 1,000 words in one of three domains: a murder mystery
  (identify the culprit), an object placement puzzle (determine where an object ended up after being
  moved), or a team allocation problem (assign people to tasks under stated constraints). The stories
  are produced by a "neurosymbolic synthetic-to-natural generation algorithm," which builds a structured
  reasoning tree first and then renders it into free-form prose, so the correct answer depends on
  connecting details spread through the narrative rather than pattern-matching a single sentence. It is
  a single-turn, English-language, text-only task.
task_format: >
  A narrative of roughly 1,000 words followed by a multiple-choice question; the model must integrate
  facts scattered through the text to select the correct option.
metric:
  name: accuracy (normalized)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    The chance baseline differs by domain: murder mysteries offer 2 answer choices (50% chance),
    object placements 5 (20% chance), and team allocation 3 (roughly 33% chance), so no single random
    baseline applies across the whole benchmark. The original paper reports human majority-vote
    performance of 94.1% (murder mysteries), 95.0% (object placements) and 100.0% (team allocation); no
    single overall human baseline figure was found in the sources reviewed, so none is set here.
dataset:
  size: 756
  size_note: >
    756 items: 250 murder mysteries, 256 object placements and 250 team allocation problems, with
    narratives ranging from roughly 3,800 to 7,300 characters. There is no train/dev/test split; it is
    released as a single evaluation set.
  url: https://huggingface.co/datasets/TAUR-Lab/MuSR
  license: "MIT (authors' GitHub repository); a Hugging Face mirror separately labels it CC BY 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "single evaluation set, no train/test split"
  public_test_set: true
publisher:
  org: University of Texas at Austin
  authors:
    - Zayne Sprague
    - Xi Ye
    - Kaj Bostrom
    - Swarat Chaudhuri
    - Greg Durrett
  url: https://github.com/Zayne-sprague/MuSR
paper:
  title: "MuSR: Testing the Limits of Chain-of-thought with Multistep Soft Reasoning"
  arxiv: "2310.16049"
  url: https://arxiv.org/abs/2310.16049
  year: 2023
leaderboard_url: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard
repo_url: https://github.com/Zayne-sprague/MuSR
released: "2023-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  note: >
    Hugging Face's own release material for Open LLM Leaderboard v2 states plainly that, as of June
    2024, "few models score better than random performance" on MuSR, one of the reasons it was chosen
    for the suite. This page could not confirm a specific current top score from a live, dated source
    during this research; the leaderboard's own Space returned only an unrendered loading screen rather
    than renderable results, so top_score and as_of are left unset rather than estimated.
contamination:
  risk: medium
  note: >
    Hugging Face selected MuSR for Open LLM Leaderboard v2 partly for its "youth," reasoning that a
    dataset released in October 2023 had less opportunity to leak into training corpora than older
    benchmarks. By the time of this research the dataset is roughly three years old, hosted without
    gating or a canary string, which will have eroded that original advantage somewhat.
harness:
  lm_eval: leaderboard_musr
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Confirmed in EleutherAI's lm-evaluation-harness: the three per-domain tasks
    (leaderboard_musr_murder_mysteries, leaderboard_musr_object_placements,
    leaderboard_musr_team_allocation) are grouped as leaderboard_musr and combined as a size-weighted
    mean of normalized accuracy (acc_norm) across the three, all evaluated zero-shot. This is the
    configuration Hugging Face's Open LLM Leaderboard v2 documentation describes using.
tags:
  - reasoning
  - long-context
  - chain-of-thought
  - open-llm-leaderboard-v2
  - narrative
sources:
  - url: https://arxiv.org/abs/2310.16049
    title: "MuSR: Testing the Limits of Chain-of-thought with Multistep Soft Reasoning"
    accessed: "2026-09-08"
  - url: https://github.com/Zayne-sprague/MuSR
    title: "Zayne-sprague/MuSR GitHub repository"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/TAUR-Lab/MuSR
    title: "TAUR-Lab/MuSR dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://huggingface.co/spaces/open-llm-leaderboard/blog
    title: "Performances are plateauing, let's make the leaderboard steep again (Open LLM Leaderboard v2 announcement), Hugging Face"
    accessed: "2026-09-08"
  - url: https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about
    title: "Open LLM Leaderboard: About, Hugging Face docs"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/leaderboard/musr/_musr.yaml
    title: "leaderboard_musr group config, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice O"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MuSR (Multistep Soft Reasoning) tests whether a model can answer a question that requires combining
facts scattered across a long narrative, rather than reasoning that is stated in one place. Each item is
an algorithmically generated story of roughly 1,000 words in one of three domains: a murder mystery
(identify the culprit), an object placement puzzle (determine where an object ended up after being
moved), or a team allocation problem (assign people to tasks under stated constraints). The stories are
produced by a "neurosymbolic synthetic-to-natural generation algorithm," which builds a structured
reasoning tree first and then renders it into free-form prose, so the correct answer depends on
connecting details spread through the narrative rather than pattern-matching a single sentence. It is a
single-turn, English-language, text-only task.

## How it is scored

Models are graded on accuracy against a set of answer options that differs by domain: murder mysteries
offer 2 choices, object placements 5, and team allocation 3, so the chance baseline is 50%, 20% and
roughly 33% respectively rather than one fixed number across the whole benchmark. Hugging Face's Open
LLM Leaderboard v2, the suite that made MuSR widely reported, evaluates all three domains zero-shot and
reports normalized accuracy (acc_norm), where a score of 0 corresponds to that domain's own chance
baseline and 100 to a perfect score, then averages the three domains weighted by size. The original
paper itself reported GPT-4 at 80.4% (murder mysteries), 60.9% (object placements) and 68.4% (team
allocation), against human majority-vote performance of 94.1%, 95.0% and 100.0% on the same three
domains.

## Dataset and licence

MuSR contains 756 items: 250 murder mysteries, 256 object placements and 250 team allocation problems,
with narratives ranging from roughly 3,800 to 7,300 characters. There is no train/dev/test split; it is
released as one evaluation set. The authors' GitHub repository carries an MIT licence; a Hugging Face
mirror (TAUR-Lab/MuSR) instead labels the dataset CC BY 4.0, and this page could not resolve which
licence statement the authors consider authoritative.

## Who publishes it

MuSR was introduced by Zayne Sprague, Xi Ye, Kaj Bostrom, Swarat Chaudhuri and Greg Durrett of the
Department of Computer Science at the University of Texas at Austin, first posted to arXiv in October
2023 with a revised version in March 2024, and presented as a spotlight paper at ICLR 2024. The authors
maintain the reference dataset and generation code on GitHub. Since mid-2024 it has been most visibly run
and reported through Hugging Face's Open LLM Leaderboard v2, which evaluates it as one of six standard
tasks.

## Lineage

MuSR has no formal predecessor or successor of its own. It is one of six tasks Hugging Face selected for
Open LLM Leaderboard v2 in June 2024, alongside MMLU-Pro, GPQA, MATH Level 5, IFEval and BBH; GPQA's
harder "Diamond" subset has its own page in this repository (gpqa_diamond.md), though the leaderboard
itself runs plain GPQA rather than Diamond specifically. MuSR is not a variant of any of those
benchmarks; it was selected for the suite as its own, independently developed reasoning format.

## Saturation and contamination

Hugging Face's own release material for Open LLM Leaderboard v2 states plainly that, as of June 2024,
"few models score better than random performance" on MuSR, one of the reasons it was chosen for the
suite: a benchmark that still separates models is more useful than one where every model clusters near
the ceiling. This page could not confirm a specific current top score from a live, dated source during
this research; the leaderboard's own Space returned only an unrendered loading screen rather than
renderable results. Contamination risk sits at medium: Hugging Face selected MuSR partly for its "youth," reasoning
that a dataset released in October 2023 had less opportunity to leak into training corpora than older
benchmarks, but by the time of this research that dataset is roughly three years old, hosted without
gating or a canary string, which will have eroded that original advantage somewhat.

## How to run it

Hugging Face's fork of lm-evaluation-harness implements the three domains as
`leaderboard_musr_murder_mysteries`, `leaderboard_musr_object_placements` and
`leaderboard_musr_team_allocation`, grouped under `leaderboard_musr` and combined as a size-weighted mean
of normalized accuracy (acc_norm), all evaluated zero-shot. The authors' GitHub repository also ships a
dataset-generation pipeline (requiring OpenAI API access), since MuSR's items were themselves generated
with GPT-4; most model reports use the fixed, pre-generated 756-item set rather than regenerating new
instances.

## Reading the numbers

A high MuSR score shows a model can hold a roughly 1,000-word narrative in mind and connect scattered
details to answer correctly, a reasonable proxy for long-range narrative and commonsense reasoning, but
not a general measure of reasoning ability. Because the three domains carry different chance baselines
(50%, 20%, 33%), check whether a reported number is raw accuracy or Open LLM Leaderboard v2's normalized
accuracy before comparing scores across sources, since the two can diverge substantially for the
2-choice murder mystery domain, where a raw score near 50% is barely better than guessing. Given how far
even strong 2023-era models sat below the paper's human baselines, treat MuSR as still meaningfully
separating models rather than as a saturated benchmark.
