---
id: discrim_eval
name: Discrim-Eval
aliases:
  - "discrim-eval"
  - "Evaluating and Mitigating Discrimination in Language Model Decisions"
page_kind: benchmark
category: safety
subcategory: "discrimination in high-stakes decision-making"
status: active
summary: Anthropic's test of whether a model's yes/no decisions on 70 high-stakes scenarios shift with a subject's age, gender or race; it produces a discrimination score where closer to zero is better, not a correctness score.
measures: >
  Discrim-Eval asks a model to make a binary yes/no decision in each of 70 hypothetical high-stakes
  scenarios spanning society -- approving a loan, granting parole, prioritising a transplant,
  issuing press credentials, and similar decisions -- where a "yes" is always the outcome that
  favours the person described. Each scenario is instantiated 135 ways, varying a described
  person's age (20 to 100 in steps of 10), gender (male, female, non-binary) and race (white, Black,
  Asian, Hispanic, Native American), so the same decision is asked once per demographic combination.
  The point is not whether the model reaches the "correct" decision -- these are hypothetical
  scenarios with no ground truth -- but whether its answer, or the probability it assigns to "yes,"
  shifts systematically with a person's demographic attributes alone.
task_format: >
  Single-turn binary decision prompts ("should this person receive X?"), answered yes or no. The
  dataset ships in two forms: `explicit`, where age, gender and race are stated directly in the
  prompt, and `implicit`, where the same scenarios instead use a name statistically associated with
  a demographic group, with no explicit demographic mention. Anthropic disclaims any endorsement of
  using language models for real automated decisions in the scenarios it tests.
metric:
  name: "discrimination score magnitude (|mean log-odds difference in P(yes) between a demographic group and the baseline group|)"
  direction: lower_is_better
  unit: "logit points"
  max_score: null
  random_baseline: 0.0
  human_baseline: null
  baseline_note: >
    The underlying discrimination score is signed, not just a magnitude: for each demographic
    attribute, Anthropic computes the average log-odds of a "yes" answer for each group relative to
    a fixed baseline person (white, 60-year-old, male), so a positive score means the model favours
    that group relative to the baseline ("positive discrimination") and a negative score means it
    disfavours it ("negative discrimination"). A score of exactly zero means the model's answers did
    not vary with that attribute at all, which is the desired outcome regardless of direction --
    hence this page records the metric as a magnitude with lower_is_better, per this batch's explicit
    guidance, rather than as the signed value the paper itself computes. lm-evaluation-harness'
    implementation reports, for each of race, gender and age, the single largest gap between any two
    groups' mean logit scores rather than the full signed table the paper publishes. There is no
    fixed maximum: the score is an unbounded log-odds difference, and a value of 0 is the
    theoretical floor for "no measured discrimination," not a ceiling.
dataset:
  size: 18900
  size_note: >
    70 decision scenarios x 135 demographic combinations (9 ages x 3 genders x 5 races) x 2 prompt
    styles (explicit, implicit) = 18,900 prompts total, confirmed by counting rows: 9,450 in
    explicit.jsonl and 9,450 in implicit.jsonl.
  url: https://huggingface.co/datasets/Anthropic/discrim-eval
  license: CC BY 4.0
  languages:
    - en
  modalities:
    - text
  splits: "no train/test split; explicit and implicit are parallel full sets, each used in full"
  public_test_set: true
publisher:
  org: Anthropic
  authors:
    - Alex Tamkin
    - Amanda Askell
    - Liane Lovitt
    - Esin Durmus
    - Nicholas Joseph
    - Shauna Kravec
    - Karina Nguyen
    - Jared Kaplan
    - Deep Ganguli
  url: https://huggingface.co/datasets/Anthropic/discrim-eval
paper:
  title: "Evaluating and Mitigating Discrimination in Language Model Decisions"
  arxiv: "2312.03689"
  url: https://arxiv.org/abs/2312.03689
  year: 2023
leaderboard_url: ""
repo_url: ""
released: "2023-12"
last_updated: "2024-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    "Saturated" and "open" describe convergence toward a correctness ceiling; Discrim-Eval's target
    is convergence toward zero measured difference between demographic groups, which is a different
    kind of trend to track and one this page found no maintained cross-model tracker for. The
    original paper's own finding was that careful system-prompt interventions (for example,
    explicitly instructing the model to ignore demographic information) sharply reduced Claude 2.0's
    measured discrimination scores in both directions, showing the metric is highly sensitive to
    prompting rather than a fixed model property.
contamination:
  risk: high
  note: >
    Every prompt template, filled example, and the pseudo-code for computing the discrimination
    score have been fully public on Hugging Face under CC BY 4.0 since December 2023. Because the
    70 scenarios and their exact wording are enumerable and public, a developer could specifically
    tune a model to minimise its measured gap on these exact prompts without addressing
    discrimination on differently worded but analogous decisions -- a benchmark-specific overfitting
    risk on top of ordinary text memorisation.
harness:
  lm_eval: "discrim_eval (discrim_eval_explicit and discrim_eval_implicit tasks; reports the largest between-group logit gap per demographic attribute)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - safety
  - bias
  - discrimination
  - decision-making
  - fairness
sources:
  - url: https://arxiv.org/abs/2312.03689
    title: "Evaluating and Mitigating Discrimination in Language Model Decisions (Tamkin et al., arXiv:2312.03689)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/Anthropic/discrim-eval
    title: "Anthropic/discrim-eval dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/discrim_eval
    title: "lm-evaluation-harness discrim_eval task README and configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Discrim-Eval probes whether a model's yes/no decisions in high-stakes hypothetical scenarios --
approving financing, granting parole, prioritising a scarce medical resource, and 67 others --
change when the only thing that varies is the age, gender or race of the person described. Every
scenario is written so "yes" is unambiguously the favourable outcome for that person, and every
scenario is instantiated across all 135 combinations of nine ages, three genders and five races, so
the same decision can be compared across an otherwise-identical prompt. The dataset ships an
`explicit` version, stating demographics directly, and an `implicit` version that instead uses a
name statistically associated with a demographic group, letting a reader separate a model's response
to stated demographics from its response to demographic cues implied by a name.

Anthropic is explicit that it does not endorse using language models to automate the real-world
version of any of these decisions; the eval exists to measure a risk before deployment, not to
validate a use case.

## How it is scored

For each prompt, the evaluator compares the probability the model assigns to "yes" against "no" and
converts it to a log-odds (logit) value. For each demographic attribute, Anthropic computes the mean
logit across all prompts sharing a given attribute value, then subtracts the mean logit for a fixed
baseline person (white, 60 years old, male) to get a signed discrimination score: positive means the
model favours that group relative to the baseline, negative means it disfavours it, and zero means
no measured difference. Because a fixed model bias in either direction is the concern, this page
reports the metric as a magnitude -- lower is better, with zero as the ideal -- rather than as
Anthropic's own signed value; a reported number should always be read alongside its sign in the
original source before being called "good" or "bad" in a specific direction.
lm-evaluation-harness implements a simplified version of this: for each of race, gender and age it
reports only the single largest gap between any two groups' mean logits, rather than the full table
of per-group scores against the baseline that the original paper publishes.

## Dataset and licence

The dataset totals 18,900 prompts: 70 decision scenarios, each instantiated across 135 demographic
combinations (9 ages from 20 to 100 in steps of 10, 3 genders, 5 races), released in both an
`explicit` and an `implicit` form (9,450 rows each, confirmed by direct row count). It is released
under CC BY 4.0 on Hugging Face with no train/test split -- both files are meant to be used in full.
Alongside the two evaluation files, Anthropic also released the prompts used to construct the
dataset and to elicit decisions, plus example code for computing the discrimination score from
per-example "yes"/"no" probabilities.

## Who publishes it

Discrim-Eval was published by Alex Tamkin, Amanda Askell, Liane Lovitt, Esin Durmus, Nicholas
Joseph, Shauna Kravec, Karina Nguyen, Jared Kaplan and Deep Ganguli at Anthropic in December 2023.
Anthropic hosts the dataset, construction prompts and example scoring code directly on Hugging Face;
no separate GitHub code repository for this benchmark was found (a direct check of
`anthropics/discrim-eval` on GitHub returned no such repository as of this page's research).

## Lineage

Discrim-Eval has no predecessor or successor tracked in this repository, and it measures a
distinctly different thing from `model_written_evals` (also documented in this repository): that
family's persona and advanced-AI-risk datasets probe a model's stated traits and intentions through
forced-choice questions with no external stakes, while Discrim-Eval probes concrete decision outputs
for demographic disparity. The two share an author (Amanda Askell) and a general Anthropic
safety-evaluation lineage but are separate papers, datasets and ids.

## Saturation and contamination

Saturation and openness do not map cleanly onto this benchmark, since the goal is convergence toward
zero measured difference between groups rather than toward a maximum correct-answer score. The
original paper's key finding was less about a fixed ceiling and more about sensitivity: careful
prompt-level interventions (for example, explicitly telling the model not to consider demographic
information) sharply reduced Claude 2.0's measured positive and negative discrimination in the
scenarios tested, without a single follow-up architecture change. No cross-model or cross-time
tracker for Discrim-Eval scores was found, so a saturation status is not established.

Contamination risk is high: the full prompt set, including the exact wording of all 70 scenarios and
the pseudo-code for scoring, has been public since December 2023. Because the scenarios are fully
enumerable, a model could be specifically tuned to minimise its measured gap on these exact wordings
-- a narrower and more gameable target than genuinely reducing discriminatory behaviour on
differently phrased but analogous real-world prompts.

## How to run it

lm-evaluation-harness carries `discrim_eval` as `discrim_eval_explicit` and `discrim_eval_implicit`
tasks, computing the normalised log-odds of "yes" for each prompt and reporting the largest
between-group gap per demographic attribute. Anthropic's own released code instead computes a
mixed-effects regression in R for the paper's primary results, and separately documents a simpler
method -- taking the difference of mean logits between groups directly -- that the dataset card
states gives very similar results. Because these are two different aggregation methods (a
regression coefficient vs. a raw mean-logit difference, and a single largest gap vs. a full per-group
table), a reported Discrim-Eval number should be checked for which method produced it before
comparing it across sources.

## Reading the numbers

A Discrim-Eval score close to zero means the model's decisions in these 70 hypothetical, high-stakes
scenarios did not vary detectably with the demographic attributes tested; it does not mean the model
is free of bias in general, only that this specific, publicly known set of prompts did not surface
one. A large score in either direction -- favouring or disfavouring a group relative to the white,
60-year-old male baseline -- is the signal to look at closely, since both directions count against
the model. Because the original paper found prompt-level interventions move these numbers
substantially, a reported score should be read alongside whether any bias-mitigation system prompt or
fine-tuning was applied, and because the exact scenarios are public, a very low score earned through
scenario-specific tuning is not strong evidence the underlying tendency is gone.
