---
id: siqa
aliases: ["social_iqa"]
name: "Social IQa"
aliases:
  - "SocialIQA"
  - "Social Interaction QA"
page_kind: benchmark
category: reasoning
subcategory: "social-commonsense multiple-choice question answering"
status: saturated
summary: "35,364 public three-way multiple-choice questions about people's motivations and reactions in social situations; a 2019 AI2/UW benchmark with a dead leaderboard and no current model-card coverage."
measures: >
  Social IQa (SIQA) tests commonsense reasoning about people's motivations, reactions and mental
  states in everyday social interactions, rather than reasoning about the physical world the way
  contemporaries such as PIQA do. Each item gives a short context describing an interaction --
  for example, "Jordan wanted to tell Tracy a secret, so Jordan leaned towards Tracy" -- plus a
  question about intent, effect or reaction, such as "Why did Jordan do this?", with three candidate
  answers. Contexts were seeded from event tuples in the ATOMIC commonsense knowledge graph. The
  authors designed a specific crowdsourcing framework to reduce a known artifact of earlier
  multiple-choice datasets: rather than having one worker write both a correct and an incorrect
  answer to the same question (which tends to give wrong answers a detectable "wrongness" in their
  surface style), incorrect answers were instead sourced as the correct answers to a different,
  related question, making them harder to rule out on style alone.
task_format: >
  Three-way multiple-choice question answering over a short social context and question, typically
  zero- or few-shot, English only; no supporting passage beyond the one- or two-sentence context is
  supplied.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: 86.9
  baseline_note: >
    33.3% is the three-way random-guess rate. The paper reports separate human-accuracy figures for
    Dev (86.9%) and Test (84.4%), each measured on a random sample of 900 examples and marked with an
    asterisk in its results table; 86.9% is recorded here because Dev/validation is the split every
    current harness actually scores (see Dataset and licence). Its 2019 baselines on the same
    Dev/Test splits were GPT at 63.3/63.0%, BERT-base at 63.3/63.1%, and BERT-large at 66.0/64.5% --
    consistent with the paper abstract's claim of a ">20% gap" between its strongest baseline and
    human performance.
dataset:
  size: 35364
  size_note: >
    The official Hugging Face mirror (allenai/social_i_qa) and the lighteval/siqa mirror that
    lm-evaluation-harness reads both total 35,364 examples: 33,410 train and 1,954 validation, with
    no test split hosted in either. The paper's own headline figure is "38,000" questions, and its
    Table 1 reports roughly 33k/2k/2k train/dev/test tuples -- consistent with the public total plus
    a further ~2,000-question test set whose answers were never included in either public mirror
    checked for this page.
  url: "https://huggingface.co/datasets/allenai/social_i_qa"
  license: >
    Not established: no licence tag or statement was found on the Hugging Face dataset card, and no
    separate licence file was confirmed in the sources checked for this page.
  languages:
    - en
  modalities:
    - text
  splits: "train (33,410) / validation (1,954); the paper's own ~2,000-question test split was never included in the public mirrors checked for this page"
  public_test_set: false
publisher:
  org: "Allen Institute for Artificial Intelligence (AI2); Paul G. Allen School of Computer Science & Engineering, University of Washington"
  authors:
    - "Maarten Sap"
    - "Hannah Rashkin"
    - "Derek Chen"
    - "Ronan Le Bras"
    - "Yejin Choi"
  url: "https://allenai.org"
paper:
  title: "Social IQa: Commonsense Reasoning about Social Interactions"
  arxiv: "1904.09728"
  url: "https://arxiv.org/abs/1904.09728"
  year: 2019
leaderboard_url: ""
repo_url: ""
released: "2019-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    No current top score could be confirmed for this page: AI2's leaderboard subdomain
    (leaderboard.allenai.org), which historically hosted Social IQa submissions, fails to resolve at
    all (the same DNS failure found while researching `openbookqa`, a sibling AI2 benchmark from the
    same period), and no other maintained leaderboard was found. Combined with a 2019 human ceiling
    already at 86.9% Dev / 84.4% Test, a best 2019 baseline already at roughly 66%, and zero mentions
    of "siqa" or "social iqa" anywhere in this repository's own model-card corpus (checked by grep),
    the benchmark is treated here as saturated and effectively retired from current frontier-model
    reporting rather than actively tracked.
contamination:
  risk: high
  note: >
    The validation split, which is the only split any harness reviewed for this page actually
    scores, has carried public answers since 2019. The paper's crowdsourced contexts draw on the
    ATOMIC knowledge graph, itself long public, giving a second route by which similar content could
    reach pretraining data even independent of the exact benchmark items.
harness:
  lm_eval: "social_iqa (lives under the lm_eval/tasks/siqa directory; dataset_path lighteval/siqa, a third-party mirror rather than the original allenai/social_i_qa; output_type multiple_choice; scores accuracy on the validation split)"
  inspect_evals: ""
  helm: ""
  opencompass: "siqa (OpenCompass ships several generation-based and perplexity/log-likelihood-based config variants rather than a single scoring protocol)"
  bigbench: ""
  other: ""
tags:
  - multiple-choice
  - social-commonsense
  - reasoning
  - retired-leaderboard
sources:
  - url: "https://arxiv.org/abs/1904.09728"
    title: "Social IQa: Commonsense Reasoning about Social Interactions (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.org/abs/1904.09728"
    title: "Social IQa (ar5iv full text, incl. Table 2 baseline scores and Section 3.5 data statistics)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/D19-1454/"
    title: "Social IQa: Commonsense Reasoning about Social Interactions, ACL Anthology (EMNLP-IJCNLP 2019)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/social_i_qa"
    title: "allenai/social_i_qa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/lighteval/siqa"
    title: "lighteval/siqa dataset (the mirror lm-evaluation-harness's social_iqa task actually reads)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/siqa/siqa.yaml"
    title: "lm-evaluation-harness siqa task config (task name social_iqa)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Social IQa (SIQA) tests commonsense reasoning about people's motivations, reactions and mental states in everyday social interactions, rather than reasoning about the physical world the way contemporaries such as PIQA do. Each item gives a short context describing an interaction -- for example, "Jordan wanted to tell Tracy a secret, so Jordan leaned towards Tracy" -- plus a question about intent, effect or reaction, such as "Why did Jordan do this?", with three candidate answers. Contexts were seeded from event tuples in the ATOMIC commonsense knowledge graph. The authors designed a specific crowdsourcing framework to reduce a known artifact of earlier multiple-choice datasets: rather than having one worker write both a correct and an incorrect answer to the same question, which tends to give wrong answers a detectable "wrongness" in their surface style, incorrect answers were instead sourced as the correct answers to a different, related question, making them harder to rule out on style alone.

## How it is scored

Systems pick one of three answer choices per question, scored by plain accuracy. 33.3% is the random-guess rate for three options. The paper separately reports human accuracy on Dev (86.9%) and Test (84.4%), each measured on a random sample of 900 examples, against contemporary 2019 baselines of GPT at 63.3/63.0%, BERT-base at 63.3/63.1%, and its strongest model, BERT-large, at 66.0/64.5% -- a roughly 21-point gap on Dev, consistent with the paper's own claim of a ">20% gap" between its best baseline and human performance. An ablation in the paper also found that removing either the context or the question from BERT-large's input collapsed its accuracy toward random, confirming both pieces are actually necessary rather than the question alone leaking the answer.

## Dataset and licence

The official Hugging Face mirror (`allenai/social_i_qa`) and the `lighteval/siqa` mirror that lm-evaluation-harness actually reads both total 35,364 examples: 33,410 train and 1,954 validation, with no test split hosted in either. The paper's own headline figure is "38,000" questions, and its Table 1 reports roughly 33k/2k/2k train/dev/test tuples -- consistent with the public total plus a further ~2,000-question test set whose answers were never included in either public mirror checked for this page. No licence tag or statement was found on the Hugging Face dataset card, and no separate licence file was confirmed in the sources checked for this page.

## Who publishes it

Social IQa comes from Maarten Sap, Hannah Rashkin, Derek Chen, Ronan Le Bras and Yejin Choi, jointly affiliated with the Allen Institute for Artificial Intelligence and the Paul G. Allen School of Computer Science & Engineering at the University of Washington, presented at EMNLP-IJCNLP 2019 (ACL Anthology D19-1454). AI2 historically hosted a submissions leaderboard for the benchmark on its leaderboard.allenai.org site; that subdomain fails to resolve at all today, the same DNS failure found while researching the sibling AI2 benchmark `openbookqa`, and no replacement leaderboard was found.

## Lineage

Social IQa has no predecessor or successor tracked in this repository. It is frequently bundled alongside contemporaries such as HellaSwag and PIQA (`piqa`) as part of standard commonsense-reasoning eval suites -- this repository's own `commonsense_qa` page notes the same grouping -- without any one of them being a formal successor to another. Within this research batch specifically, it is the social-commonsense counterpart to `openbookqa` and shares a research-community lineage (AI2, and overlapping authorship habits) with `arc_challenge` and `commonsense_qa`, all part of the same 2018-2019 wave of four- or five-way multiple-choice reasoning benchmarks that predate MMLU-era evaluation.

## Saturation and contamination

No current top score could be confirmed for this page: AI2's leaderboard subdomain fails to resolve at all, and no other maintained leaderboard was found. Combined with a 2019 human ceiling already at 86.9% Dev / 84.4% Test, a best 2019 baseline already around 66%, and zero mentions of "siqa" or "social iqa" anywhere in this repository's own model-card corpus, the benchmark is treated here as saturated and effectively retired from current frontier-model reporting. Contamination risk is high: the validation split, the only split any harness reviewed for this page actually scores, has carried public answers since 2019, and the underlying ATOMIC knowledge graph its contexts are drawn from has been public even longer.

## How to run it

lm-evaluation-harness implements `social_iqa`, filed under its `siqa` task directory, but reads a third-party Hugging Face mirror (`lighteval/siqa`) rather than the original `allenai/social_i_qa`; the two mirrors report identical split counts, so this is a naming rather than a data difference. It scores multiple-choice log-likelihood accuracy on the validation split only, since no test-split answers are available. OpenCompass ships several `siqa` config variants, some generation-based and some perplexity/log-likelihood-based, rather than a single fixed protocol, so a reported OpenCompass "siqa" number should be checked against which config produced it before comparing across papers.

## Reading the numbers

A high Social IQa score mostly confirms a model can track intent and reaction in short, simple social vignettes, a capability that already looked close to solved by 2019-era transformer baselines and has had no maintained leaderboard to track since. Because the only scored split has been public for years and the benchmark is absent from this repository's own current model cards, treat any reported number as a floor check rather than a meaningful differentiator between modern frontier models, and prefer a newer, harder social- or theory-of-mind reasoning benchmark if one is available for the comparison you actually need.
