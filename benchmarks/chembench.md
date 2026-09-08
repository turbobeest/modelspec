---
id: chembench
name: "ChemBench"
aliases: []
page_kind: benchmark
category: domain
subcategory: "chemistry knowledge and reasoning"
status: active
summary: "An automated chemistry benchmark of nearly 2,800 question-answer pairs, built specifically to compare frontier LLMs against surveyed human chemists rather than just each other."
measures: >
  ChemBench evaluates chemical knowledge and reasoning: questions range from general, inorganic,
  analytical and technical chemistry to toxicity and safety, and are separately tagged by which
  skills they require -- knowledge, reasoning, calculation, or chemical intuition -- and by
  difficulty (basic or advanced). Molecules are encoded as SMILES strings wrapped in explicit
  START_SMILES/END_SMILES tags so the format is unambiguous to a text-only model. The benchmark's
  distinguishing feature is that it was built specifically to be comparable to human performance: a
  curated subset was also given to surveyed chemists so model scores can be read against a
  same-questions human baseline rather than an assumed one.
task_format: >
  A mix of multiple-choice (2,544 questions) and open-ended free-response questions (244
  questions), evaluated on text completions only, including from tool-augmented systems. A curated
  236-question subset, ChemBench-Mini, restricted to "advanced"-difficulty items and balanced
  across topic/skill combinations, was answered by human volunteers through a custom web
  application for the paper's human-baseline comparison; some of those questions allowed the
  volunteers to use external tools such as web search.
metric:
  name: "accuracy (fraction of questions answered correctly)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random-guess baseline applies because option counts vary by question and a large
    minority of questions are open-ended rather than multiple choice. For the human baseline: the
    paper surveyed 19 chemistry experts (16 of whom reported their background: 2 beyond a first
    postdoc, 13 pursuing a PhD with a master's degree, 1 with a bachelor's degree) on
    ChemBench-Mini, and states that its leading model (o1) beat the best individual human's overall
    ChemBench-Mini score by "almost a factor of two," with many other models also exceeding the
    average human score -- but the underlying percentage figures are shown only in a chart (Figure
    3) that did not render as extractable text in the source read for this page, so no numeric
    human_baseline is recorded here. One specific, precisely quoted comparison from the paper:
    on a subset of questions sampled from a German chemical-safety certification exam bank
    (the Chemical Prohibition Ordinance), GPT-4 scored 71% and Claude 3.5 Sonnet 61%, against just
    3% for the human experts on that narrow subset -- illustrating that the human baseline is
    highly task-dependent rather than one fixed number.
dataset:
  size: 2788
  size_note: >
    The paper states 2,788 question-answer pairs: 1,039 manually generated and 1,749
    semi-automatically generated; 2,544 multiple-choice and 244 open-ended. The current Hugging
    Face mirror (jablonkagroup/ChemBench) totals 2,785 rows and the inspect_evals task
    documentation cites 2,786 -- both a handful fewer than the paper's figure, a small drift
    comparable to other benchmarks' mirrors versus their papers. A curated 236-question subset,
    ChemBench-Mini, restricted to advanced-difficulty items, is used for the human-baseline
    comparison described above.
  url: "https://huggingface.co/datasets/jablonkagroup/ChemBench"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "single evaluation corpus, no train/test split; ChemBench-Mini (236 questions) is a curated subset used for the human-baseline study"
  public_test_set: true
publisher:
  org: "Friedrich Schiller University Jena (Laboratory of Organic and Macromolecular Chemistry); Helmholtz Institute for Polymers in Energy Applications Jena (HIPOLE Jena); a multi-institution author collaboration"
  authors:
    - "Adrian Mirza and 33 other co-authors (35 total, including corresponding author Kevin Maik Jablonka)"
  url: "https://github.com/lamalab-org/chembench"
paper:
  title: "Are large language models superhuman chemists?"
  arxiv: "2404.01475"
  url: "https://arxiv.org/abs/2404.01475"
  year: 2024
leaderboard_url: "https://chembench.org"
repo_url: "https://github.com/lamalab-org/chembench"
released: "2024-04"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    The paper itself reports that its leading model (o1) beat the best human participant's overall
    ChemBench-Mini score by nearly a factor of two, and that many other models exceeded the average
    human score -- a strong signal that frontier models have already passed the human baseline this
    benchmark was built to compare against, even though the precise percentage figures were only
    visible in a chart, not extractable text, in the source read for this page. Performance is
    uneven across topics: even the strongest models struggled with some analytical-chemistry tasks,
    for instance scoring only 22% on an NMR-signal-counting task cited in the paper for o1. No
    numeric top_score is recorded here because no exact current figure was confirmed from a source
    opened for this page.
contamination:
  risk: medium
  note: >
    The dataset and its answers are public on GitHub and Hugging Face under an MIT licence, so
    exposure through web-scale pretraining is plausible for any model trained since mid-2024. The
    paper reports that some textbook-derived questions see notably better model performance than
    semi-automatically constructed ones on the same topic, which the authors attribute to models
    having seen similar textbook material, though they stop short of calling this proven leakage.
    No dedicated contamination study was found in the sources read for this page.
harness:
  lm_eval: ""
  inspect_evals: "chembench"
  helm: ""
  opencompass: "ChemBench (ChemBench_gen for direct scoring; ChemBench_llmjudge_gen and its variants for LLM-judged scoring of open-ended answers)"
  bigbench: ""
  other: "Reference implementation: the chembench Python package (pip install chembench), which loads the corpus directly from Hugging Face and reports per-topic scores."
tags:
  - domain
  - chemistry
  - knowledge
  - reasoning
  - human-baseline
sources:
  - url: "https://arxiv.org/abs/2404.01475"
    title: "Are large language models superhuman chemists?"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2404.01475"
    title: "Are large language models superhuman chemists? (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/lamalab-org/chembench"
    title: "lamalab-org/chembench GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/jablonkagroup/ChemBench"
    title: "jablonkagroup/ChemBench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/chembench"
    title: "inspect_evals chembench task"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/ChemBench"
    title: "OpenCompass ChemBench dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice E"
---

## What it measures

ChemBench evaluates chemical knowledge and reasoning across general, inorganic, analytical and technical chemistry, plus toxicity and safety. Every question is tagged by which skills it requires -- knowledge, reasoning, calculation, or chemical intuition -- and by difficulty (basic or advanced), so a score can be broken down by capability rather than read as one lump number. Molecules are encoded as SMILES strings wrapped in explicit tags so the format is unambiguous to a text-only model, and the benchmark operates purely on text completions so tool-augmented systems can be evaluated the same way as plain language models.

Its distinguishing feature is being built specifically for human comparison: a curated 236-question subset, ChemBench-Mini, was given to surveyed chemists through a custom web application, so model scores can be read against a same-questions human baseline instead of an assumed one.

## How it is scored

Scoring is plain accuracy: the fraction of questions answered correctly, with 2,544 of the corpus's 2,788 questions multiple choice and 244 open-ended free response. There is no single random-guess baseline, since option counts vary and a meaningful slice of questions are open-ended. The human-baseline study surveyed 19 chemistry experts, 16 of whom reported their background (2 beyond a first postdoc, 13 pursuing a PhD with a master's degree, 1 with a bachelor's degree), and compared them to models on the same ChemBench-Mini questions, with some questions allowing tool use on both sides. The paper reports its leading model at the time (o1) beat the best individual human's overall score by nearly a factor of two -- but that headline figure is task-dependent: on a subset drawn from a German chemical-safety certification exam, GPT-4 scored 71% and Claude 3.5 Sonnet 61%, against only 3% for the human experts on that narrow subset, since those volunteers were not necessarily trained for that specific certification.

## Dataset and licence

The paper states 2,788 question-answer pairs: 1,039 manually generated and 1,749 semi-automatically generated from chemical databases and textbooks. The current Hugging Face mirror totals 2,785 rows and the inspect_evals documentation cites 2,786, both a handful fewer than the paper's count -- a small drift similar to other benchmarks' papers versus their later mirrors. Every question was reviewed by at least two scientists beyond its original curator, plus automated checks. The GitHub repository and Hugging Face dataset are both released under the MIT licence, and the full corpus, with answers, is public.

## Who publishes it

ChemBench comes from a 35-author collaboration led by Adrian Mirza, Nawaf Alampara and Sreekanth Kunchapu, with Kevin Maik Jablonka as corresponding author, most affiliated with the Laboratory of Organic and Macromolecular Chemistry at Friedrich Schiller University Jena and the Helmholtz Institute for Polymers in Energy Applications Jena, Germany. It was posted to arXiv in April 2024. The `lamalab-org` GitHub organisation maintains the reference implementation as an installable Python package, and hosts a public leaderboard at chembench.org.

## Lineage

ChemBench has no predecessor or successor tracked in this repository. The same group later extended the framework to multimodal (vision-language) chemistry evaluation in a separate 2024 paper (arXiv:2411.16955); that extension has no id or page here, and the Hugging Face dataset card for the text corpus documented on this page in fact cites that later paper rather than the original.

## Saturation and contamination

The paper's own framing is a saturation signal in itself: its leading model (o1) is reported to have beaten the best human participant's overall ChemBench-Mini score by nearly a factor of two, and many other models also exceeded the average human score, even though the precise percentages were only visible in a chart rather than extractable text in the source read for this page. Performance is uneven rather than uniformly high, though: even the strongest models struggled on some analytical-chemistry tasks, such as counting distinct NMR signals from a SMILES string, where the paper cites o1 at only 22% correct. Contamination risk sits at medium: the corpus and answers are public under the MIT licence, and the paper notes models tend to do better on textbook-derived questions than on semi-automatically constructed ones on the same topic, which the authors suggest but do not prove reflects prior exposure to similar textbook material.

## How to run it

The `chembench` Python package is the reference implementation; it loads the corpus from the `jablonkagroup/ChemBench` Hugging Face dataset and can report scores broken down by topic. inspect_evals ships it as the `chembench` task, also pulling from the full Hugging Face corpus rather than ChemBench-Mini. OpenCompass provides both a direct-scoring config (`ChemBench_gen`) and an LLM-judge config (`ChemBench_llmjudge_gen`) for the open-ended portion of the corpus, so scores from different open-ended grading approaches are not automatically comparable.

## Reading the numbers

A high overall ChemBench score suggests broad chemical knowledge and reasoning ability, but the benchmark's own topic and skill tags matter more than the aggregate: a model can score well on textbook-style knowledge questions while failing basic quantitative or spectroscopic reasoning, as the NMR-counting result shows. Because the human baseline came from a specific, curated 236-question subset answered by a specific pool of volunteers rather than certified subject-matter experts in every niche the corpus touches, "beats the human baseline" should be read as beating those particular volunteers on those particular questions, not as a general claim about expert chemists. Always check whether a reported score used tool access, since the benchmark explicitly supports evaluating tool-augmented systems alongside plain language models.
