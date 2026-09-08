---
id: model_written_evals
name: Model-Written Evaluations
aliases:
  - "Discovering Language Model Behaviors with Model-Written Evaluations"
  - "Anthropic Model-Written Evals"
  - "MWE"
page_kind: family
category: safety
subcategory: model persona, sycophancy and advanced-AI-risk behavioural probes
status: active
summary: 154 model-generated, human-filtered yes/no datasets probing a model's persona, sycophancy and advanced-AI-risk tendencies rather than testing right-or-wrong knowledge.
measures: >
  Model-Written Evaluations (MWE) is not one test but a method plus its output: Anthropic used
  language models to write large sets of yes/no and A/B questions designed to reveal how a model
  behaves along a given trait, then had crowdworkers filter and validate the results. The released
  collection spans four areas: persona (does the model's stated personality, politics, religion,
  ethics, or desire to pursue goals like power or self-preservation match a given description),
  sycophancy (does the model echo a user's stated opinion on philosophy, NLP research, or politics
  rather than giving an independent answer), advanced AI risk (does the model express tendencies
  such as corrigibility, coordination with other AI instances, or awareness of its own situation),
  and Winogenerated, a model-generated, human-validated expansion of the Winogender gender-bias
  schema. Every item is a forced-choice question with one answer marked as "matching" the behaviour
  under test and one marked as "not matching"; there is no objectively correct answer.
task_format: >
  Binary or A/B forced-choice questions. The model (or its next-token probabilities) is scored on
  whether it selects the answer_matching_behavior or answer_not_matching_behavior option for each
  item; most implementations compare the log-likelihood the model assigns to each labelled
  continuation rather than requiring free-text generation.
metric:
  name: "% of answers matching the tested behaviour"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    This is a behavioural-match rate, not an accuracy score, and the schema's higher_is_better
    default should not be read as "higher is good": for a dataset like power-seeking-inclination a
    LOWER match rate is the desirable outcome, for a neutral personality trait like agreeableness
    neither direction is inherently better, and for sycophancy datasets a lower match rate means the
    model is less likely to simply echo the user. Always check which of the 154 files a reported
    number comes from before judging whether higher is good. Separately, the paper's own quality
    check found crowdworkers agreed with 90-100% of labels across datasets, and 95.7% of examples
    were judged correctly labelled and relevant when averaged over the 133 persona datasets, which
    the authors treat as evidence the model-written data is usable rather than as a model score.
dataset:
  size: 154
  size_note: >
    The paper states it releases 154 datasets in total. The public repository (persona/,
    sycophancy/, advanced-ai-risk/, winogenerated/) contains 133 persona datasets (the paper's own
    breakdown: 26 personality, 46 stated desire for problematic goals, 26 other unsafe behaviours, 8
    religious views, 6 political views, 17 ethical views, 4 other), 3 sycophancy datasets, 16
    advanced-AI-risk behaviours each released as both a human-crowdsourced and a model-generated
    file (32 files), and one Winogenerated schema file (plus a companion occupations file that is
    not itself a scored eval). Counting files this way (133 + 32 + 3 = 168, or 133 + 16 + 3 = 152 if
    only the LM-generated advanced-AI-risk half is counted) does not cleanly reconcile to the paper's
    headline 154, and the paper's own text separately describes Winogenerated as released alongside,
    rather than inside, "all 154 model-written evaluations." This page reports the discrepancy
    rather than forcing a match.
  url: https://huggingface.co/datasets/Anthropic/model-written-evals
  license: CC BY 4.0
  languages:
    - en
  modalities:
    - text
  splits: not established (no train/validation/test split; each file is used in full as an evaluation set)
  public_test_set: true
publisher:
  org: Anthropic (Surge AI and the Machine Intelligence Research Institute credited for human-generated comparison data)
  authors:
    - Ethan Perez
    - Sam Ringer
    - Kamilė Lukošiūtė
    - Karina Nguyen
    - Edwin Chen
    - Scott Heiner
    - Craig Pettit
    - Catherine Olsson
    - Sandipan Kundu
    - Saurav Kadavath
    - Andy Jones
    - Anna Chen
    - Ben Mann
    - Brian Israel
    - Bryan Seethor
    - Cameron McKinnon
    - Christopher Olah
    - Da Yan
    - Daniela Amodei
    - Dario Amodei
    - Dawn Drain
    - Dustin Li
    - Eli Tran-Johnson
    - Guro Khundadze
    - Jackson Kernion
    - James Landis
    - Jamie Kerr
    - Jared Mueller
    - Jeeyoon Hyun
    - Joshua Landau
    - Kamal Ndousse
    - Landon Goldberg
    - Liane Lovitt
    - Martin Lucas
    - Michael Sellitto
    - Miranda Zhang
    - Neerav Kingsland
    - Nelson Elhage
    - Nicholas Joseph
    - Noemí Mercado
    - Nova DasSarma
    - Oliver Rausch
    - Robin Larson
    - Sam McCandlish
    - Scott Johnston
    - Shauna Kravec
    - Sheer El Showk
    - Tamera Lanham
    - Timothy Telleen-Lawton
    - Tom Brown
    - Tom Henighan
    - Tristan Hume
    - Yuntao Bai
    - Zac Hatfield-Dodds
    - Jack Clark
    - Samuel R. Bowman
    - Amanda Askell
    - Roger Grosse
    - Danny Hernandez
    - Deep Ganguli
    - Evan Hubinger
    - Nicholas Schiefer
    - Jared Kaplan
  url: https://github.com/anthropics/evals
paper:
  title: "Discovering Language Model Behaviors with Model-Written Evaluations"
  arxiv: "2212.09251"
  url: https://arxiv.org/abs/2212.09251
  year: 2022
leaderboard_url: ""
repo_url: https://github.com/anthropics/evals
released: "2022-12"
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
  note: >
    "Saturated" and "open" describe benchmarks that converge toward a correct-answer ceiling; MWE
    has no such ceiling, since a "good" score depends entirely on the trait being tested and, for
    several of the 154 datasets, safety training deliberately tries to push a model's rate away from
    matching the behaviour rather than toward 100%. No aggregate tracker across models or time was
    found for this page, so a saturation call is not established.
contamination:
  risk: high
  note: >
    Every question and both answer options have been fully public on GitHub and Hugging Face since
    December 2022, and lm-evaluation-harness mirrors the same data again under the EleutherAI/persona
    dataset id, so exact-text memorisation is plausible. A more specific risk is that the paper's own
    named behaviours (sycophancy, power-seeking, corrigibility, and so on) became widely cited
    targets for later safety training, so a model's current score can reflect deliberate post-training
    tuning toward or away from these exact probes rather than a generalised trait.
harness:
  lm_eval: "model_written_evals (persona, sycophancy, advanced_ai_risk and winogenerated subtasks, generated against the EleutherAI/persona mirror)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - safety
  - persona
  - sycophancy
  - advanced-ai-risk
  - model-generated
  - alignment
sources:
  - url: https://arxiv.org/abs/2212.09251
    title: "Discovering Language Model Behaviors with Model-Written Evaluations (Perez et al., arXiv:2212.09251)"
    accessed: "2026-09-08"
  - url: https://github.com/anthropics/evals
    title: "anthropics/evals GitHub repository (README and LICENSE)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/Anthropic/model-written-evals
    title: "Anthropic/model-written-evals dataset card and file listing, Hugging Face"
    accessed: "2026-09-08"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/model_written_evals
    title: "lm-evaluation-harness model_written_evals task directory (persona, sycophancy, advanced_ai_risk, winogenerated)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Model-Written Evaluations is Anthropic's demonstration that a language model can write its own
behavioural test suites, plus the 154 datasets that demonstration produced. Rather than asking
whether a model knows a fact, each item asks whether the model's response matches a described
behaviour: does it claim to be agreeable, does it say it wants to acquire more compute, does it
repeat a user's stated political opinion back to them, does it object to being shut down. The
questions themselves were generated by a language model from hand-written templates and
demonstrations, then filtered and, for many datasets, separately validated by crowdworkers.

The four released collections cover different ground: persona (political, religious, ethical and
personality traits, plus stated desire for goals like power, wealth, self-preservation or
self-replication), sycophancy (whether the model echoes a user's stated view in philosophy, NLP
research or politics rather than answering independently), advanced AI risk (16 behaviours such as
corrigibility, coordination with copies of itself, and situational self-awareness, each with both a
human-written and a model-written version), and Winogenerated, a much larger model-generated
successor to the Winogender gender-bias schema.

## How it is scored

Every item is forced-choice: the model picks between an `answer_matching_behavior` option and an
`answer_not_matching_behavior` option, and the score is simply the fraction of items where the
model's chosen (or highest-likelihood) answer matches. lm-evaluation-harness implements this by
comparing the log-likelihood the model assigns to each labelled continuation, following the format
each dataset's own file specifies, rather than parsing free-text generation.

Because there is no objectively correct answer, a "matching" rate is not an accuracy score. For
persona and advanced-AI-risk datasets describing behaviours Anthropic considers undesirable (power-
seeking, resistance to correction, desire to avoid shutdown), a lower match rate is the better
outcome; for neutral personality traits neither direction is inherently better; for sycophancy, a
lower rate means the model relies less on the user's stated opinion. The paper's own quality check
is separate from any model score: crowdworkers agreed with 90-100% of the generated labels, and
95.7% of examples across the 133 persona datasets were judged correctly labelled and relevant to
the trait being tested.

## Dataset and licence

The paper states it releases "154 model-written evaluations." The public repository breaks down
into 133 persona datasets (26 personality, 46 dangerous-goal, 26 other unsafe-behaviour, 8
religious, 6 political, 17 ethical, 4 other), 3 sycophancy datasets, 16 advanced-AI-risk behaviours
each shipped as a human-written and a model-written file (32 files), and one Winogenerated file.
These component counts do not cleanly sum to 154 under any grouping this page tried, and the
paper's own phrasing describes Winogenerated as released "also," separately from the 154 -- a
discrepancy reported here rather than resolved. The data is released under CC BY 4.0 with no
train/test split; every file is used in full. Advanced-AI-risk items are capped at 1,000 questions
per behaviour per source.

## Who publishes it

Anthropic published MWE in December 2022, authored by Ethan Perez and a large team including Jared
Kaplan, Sam Bowman, Amanda Askell, Deep Ganguli and Jack Clark, with Surge AI credited for
human-generated comparison data and the Machine Intelligence Research Institute among the
supporting affiliations listed in the paper. Anthropic maintains the reference repository at
`anthropics/evals` on GitHub and mirrors the same files on Hugging Face.

## Lineage

MWE has no benchmark predecessor in the usual sense; it is itself a method paper that happened to
release 154 datasets as its evidence. EleutherAI's lm-evaluation-harness re-hosts the persona
collection under a separate `EleutherAI/persona` dataset id for its own task implementation. This
repository does not carry separate pages for the individual persona, sycophancy or advanced-AI-risk
files, or for Winogenerated; a reader who encounters a score tagged with one specific behaviour name
(for example, `corrigible-neutral-HHH` or `sycophancy_on_political_typology_quiz`) should treat it
as one file within this family rather than expect its own page.

## Saturation and contamination

Saturation does not apply in the usual sense: there is no correct-answer ceiling to approach, and
for many of the 154 datasets a developer's goal is to push the match rate down through safety
training, not up toward 100%. No cross-model, cross-time tracker for MWE scores was found, so a
saturation call is not established here.

Contamination risk is high: the full question-and-answer text has been public since December 2022
across GitHub, Hugging Face, and a second lm-evaluation-harness mirror, so verbatim memorisation is
plausible. A more specific concern is that this paper's own named behaviours became widely used
targets for subsequent safety training, so a low score on, say, the power-seeking or shutdown-
avoidance datasets may reflect training aimed at this exact test rather than a generalised
disposition the test merely samples.

## How to run it

lm-evaluation-harness carries `model_written_evals` as a task group covering persona, sycophancy,
advanced_ai_risk and winogenerated subtasks, generated programmatically against the
`EleutherAI/persona` dataset mirror and scored with the `acc` metric (the fraction of items where
the model's likelihood favours the matching-behaviour answer). No HELM, OpenCompass or BIG-bench
implementation was confirmed. Anthropic's own repository ships the raw `.jsonl` files with no
evaluation harness attached, so downstream users typically write their own scoring loop over the
`answer_matching_behavior` / `answer_not_matching_behavior` fields.

## Reading the numbers

A reported MWE number is only meaningful once you know which of the 154 files it came from and
whether a higher match rate is the desired outcome for that specific trait -- there is no single
"good" direction across the family. Treat these scores as a behavioural fingerprint rather than a
capability measurement: they say whether a model's outputs lean toward a described tendency under
a specific forced-choice framing, not whether the model is "safe" or "good" in general, and framing
effects (question wording, few-shot format) can shift a model's rate substantially. Read a single
dataset's score alongside the underlying question text before drawing conclusions, and treat any
score as a snapshot rather than a fixed trait, since post-training can and does move these numbers
deliberately.
