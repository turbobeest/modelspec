---
id: squad
name: "SQuAD"
aliases:
  - "Stanford Question Answering Dataset"
  - "SQuAD 1.1"
page_kind: benchmark
category: reasoning
subcategory: "extractive reading comprehension: locate an answer span in a given Wikipedia passage, or (SQuAD 2.0) determine that no answer is supported"
status: saturated
summary: >-
  SQuAD (2016) and SQuAD 2.0 (2018) are the canonical Wikipedia span-extraction reading sets; the
  official leaderboard has sat above human performance since 2019, so a modern score there is uninformative.
measures: >
  SQuAD gives a model a paragraph from a Wikipedia article and a question about it, and the model
  must return the exact span of text in the paragraph that answers the question -- there is no
  free-form generation and, in the original 1.1 release, every question is guaranteed to be
  answerable from the given passage. The 2018 follow-up, SQuAD 2.0, adds a second requirement on top
  of the same task: over 50,000 questions written adversarially by crowdworkers to closely resemble
  answerable ones but have no answer in the passage, so a model must also decide when to abstain
  rather than guess a plausible-looking but wrong span. The two are frequently conflated under the
  single name "SQuAD," but they are meaningfully different tasks -- a system tuned only to extract
  spans has no mechanism for saying "no answer," and, as the 2.0 paper's own headline result shows, a
  strong system scoring 86% F1 on 1.1 drops to only 66% F1 once unanswerable questions are added.
task_format: >
  Extractive span selection: given a passage and a question, output the start and end of the answer
  span within the passage verbatim (SQuAD 1.1), or the same plus an explicit "no answer" option
  (SQuAD 2.0). Modern LLM harnesses instead prompt the model to generate the answer text directly
  (or a literal "unanswerable" / "impossible to answer" string) rather than pick a span by position.
metric:
  name: "Exact Match (EM) and F1 (word-overlap) against human reference answers, computed by the official evaluation script"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 89.452
  baseline_note: >
    Two different human baselines exist for the two versions, and they are not interchangeable. The
    original 1.1 paper reports human performance at 86.8% F1 against its own strong logistic-regression
    baseline's 51.0% F1 (versus a 20% F1 naive baseline). The SQuAD 2.0 paper reports a separate,
    slightly higher human figure specific to the harder 2.0 test set -- 86.831 EM / 89.452 F1, as
    listed on the official leaderboard -- and demonstrates that a strong 1.1 system's 86% F1 collapses
    to 66% F1 once it must also handle unanswerable questions. The human_baseline recorded here (89.452)
    is the SQuAD 2.0 figure, since that is the version almost every current harness actually runs (see
    How to run it). There is no meaningful random baseline for free-text span extraction.
dataset:
  size: 98169
  size_note: >
    SQuAD 1.1's public Hugging Face mirror (rajpurkar/squad) holds 87,599 train and 10,570 validation
    question-answer pairs (98,169 total), confirmed directly from the dataset's own split metadata.
    SQuAD 2.0's mirror (rajpurkar/squad_v2) holds 130,319 train and 11,873 validation pairs (142,192
    total) -- the difference from 1.1 is the added unanswerable questions plus some re-annotation. In
    both cases, only train and validation ("dev") splits are public; the official hidden test set that
    the original leaderboard scores against has never been released; a system can only get an official
    test-set score by submitting code for the maintainers to run. Nearly every harness and paper today
    evaluates against the public validation split instead, not the true hidden test set.
  url: "https://huggingface.co/datasets/rajpurkar/squad_v2"
  license: "CC BY-SA 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "SQuAD 1.1: train 87,599 / validation 10,570 (both public, both answerable); SQuAD 2.0: train 130,319 / validation 11,873 (public, mixes answerable and unanswerable); the official held-out test set for both versions has never been publicly released"
  public_test_set: false
publisher:
  org: "Stanford University"
  authors:
    - "Pranav Rajpurkar"
    - "Jian Zhang"
    - "Konstantin Lopyrev"
    - "Percy Liang"
  url: "https://rajpurkar.github.io/SQuAD-explorer/"
paper:
  title: "SQuAD: 100,000+ Questions for Machine Comprehension of Text"
  arxiv: "1606.05250"
  url: "https://arxiv.org/abs/1606.05250"
  year: 2016
leaderboard_url: "https://rajpurkar.github.io/SQuAD-explorer/"
repo_url: "https://github.com/rajpurkar/SQuAD-explorer"
released: "2016-06"
last_updated: "2018-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 93.214
  as_of: "2021-06"
  note: >
    Read directly from the official SQuAD 2.0 leaderboard (rajpurkar.github.io/SQuAD-explorer/): the
    top entry, "IE-Net (ensemble)" from RICOH_SRCB_DML (submitted June 2021), scores 90.939 EM / 93.214
    F1, above the 86.831 EM / 89.452 F1 human baseline the same leaderboard lists. Multiple systems
    (several ALBERT and ensemble variants dated from September 2019 onward) already sat above the
    human F1 figure years before that, so the leaderboard has been super-human at the top for years.
    The board still receives occasional new submissions -- one visible entry is dated September 2023 --
    but none of them have displaced the 2021 top score, so the ceiling itself has been essentially
    static even though submission activity has not fully stopped. No frontier LLM lab appears to submit
    to this leaderboard at all; modern models are instead scored on the public validation split by
    third-party harnesses, a different and generally easier exercise than the official hidden-test
    competition.
contamination:
  risk: high
  note: >
    The public train and validation files for both versions have been freely downloadable since 2016
    (1.1) and 2018 (2.0) respectively, and SQuAD is one of the most widely used, cited, mirrored and
    quoted datasets in NLP -- its passages, questions and answers appear across countless papers,
    tutorials, GitHub repositories and blog posts that a large web crawl would sweep up. The only part
    of SQuAD not exposed this way is the true hidden test set, which has never been released; but since
    almost no current evaluation actually targets that hidden set (see How to run it), the practically
    relevant portion of SQuAD -- the public validation split -- should be assumed to be in the training
    data of most current large language models.
harness:
  lm_eval: "squadv2"
  inspect_evals: "squad"
  helm: ""
  opencompass: "squad2.0"
  bigbench: ""
  other: >
    Every current harness implementation found for this page runs the SQuAD 2.0 (unanswerable-aware)
    data, not plain SQuAD 1.1, despite differing task names. inspect_evals' task is literally named
    `squad` but loads `rajpurkar/squad_v2`'s validation split and instructs the model to answer with
    the lowercase string "unanswerable" when appropriate, scoring with F1 and exact match.
    lm-evaluation-harness names its task `squadv2`, loads the `lighteval/squad_v2` mirror, and uses the
    official Hugging Face `evaluate` "squad_v2" metric, which reports separate exact/F1 scores for
    answerable questions (HasAns_*), unanswerable questions (NoAns_*), and threshold-optimised variants
    (best_exact/best_f1) alongside the overall numbers. OpenCompass's config (abbreviated `squad2.0`)
    reads a local `dev-v2.0.json` file and prompts the model to answer or say "impossible to answer" --
    different literal refusal wording from inspect_evals' "unanswerable." No SQuAD 1.1-only task (that
    never asks the model to abstain) was found in any of the three harnesses checked for this page.
tags:
  - reading-comprehension
  - question-answering
  - wikipedia
  - extractive-qa
  - saturated
sources:
  - url: "https://arxiv.org/abs/1606.05250"
    title: "SQuAD: 100,000+ Questions for Machine Comprehension of Text (arXiv abstract: authors, F1/human numbers, EMNLP 2016)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1806.03822"
    title: "Know What You Don't Know: Unanswerable Questions for SQuAD (arXiv abstract: SQuAD 2.0, the 86%-to-66% F1 result, ACL 2018)"
    accessed: "2026-09-08"
  - url: "https://rajpurkar.github.io/SQuAD-explorer/"
    title: "Official SQuAD-explorer site: dataset description, CC BY-SA 4.0 licence statement, hidden-test-set submission process, live SQuAD 2.0 leaderboard"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/rajpurkar/squad"
    title: "rajpurkar/squad dataset API record (SQuAD 1.1: split sizes, cc-by-sa-4.0 licence tag)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/rajpurkar/squad_v2"
    title: "rajpurkar/squad_v2 dataset API record (SQuAD 2.0: split sizes, cc-by-sa-4.0 licence tag)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/squad/squad.py"
    title: "inspect_evals squad.py task source (loads rajpurkar/squad_v2 validation split; f1+exact scorers)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/squadv2/task.py"
    title: "lm-evaluation-harness SQuAD2 task.py (task name squadv2; lighteval/squad_v2; HasAns/NoAns/best submetrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/squad20/squad20_gen_1710bc.py"
    title: "OpenCompass squad20_gen_1710bc.py config (abbr squad2.0; 'impossible to answer' prompt wording; SQuAD20Evaluator)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SQuAD gives a model a paragraph from a Wikipedia article and a question about it, and the model must return the exact span of text within that paragraph that answers the question -- no free-form generation, and in the 1.1 release every question is guaranteed answerable from the passage. The 2018 follow-up, SQuAD 2.0, layers a second requirement on the same task: over 50,000 questions written adversarially by crowdworkers to closely resemble answerable ones but with no answer anywhere in the passage, so a model must also learn when to abstain rather than confidently return a wrong span. The two versions are routinely referred to interchangeably as "SQuAD," but test meaningfully different things: a system built only to extract spans has no mechanism for declining to answer, and, as the 2.0 paper's own headline comparison shows, a strong system reaching 86% F1 on 1.1 falls to just 66% F1 once unanswerable questions are mixed in.

## How it is scored

The official evaluation computes Exact Match (does the predicted span match a reference answer after light normalisation) and F1 (word overlap) against human-written reference answers, per version. Two distinct human baselines exist: the 1.1 paper reports 86.8% F1 for human performance against its own logistic-regression baseline's 51.0%; the 2.0 paper reports a separate figure for the harder test, 86.831 EM / 89.452 F1, as listed on the live leaderboard. These are not interchangeable, and a model's EM/F1 on one version says little about the other.

## Dataset and licence

Both versions are hosted on Hugging Face under CC BY-SA 4.0, matching the licence on the official SQuAD-explorer site. SQuAD 1.1 holds 87,599 train and 10,570 validation pairs (98,169 total); SQuAD 2.0 holds 130,319 train and 11,873 validation pairs (142,192 total), the difference coming from the added unanswerable questions plus re-annotation. In both, only train and validation ("dev") are public; the true held-out test set has never been released -- an official score requires submitting a working system for the maintainers to run, via CodaLab. Almost all current evaluation, including every harness checked here, runs against the public validation split instead.

## Who publishes it

SQuAD 1.1 comes from Pranav Rajpurkar, Jian Zhang, Konstantin Lopyrev and Percy Liang at Stanford, published at EMNLP 2016. SQuAD 2.0 comes from a related but distinct author list -- Rajpurkar, Robin Jia and Percy Liang -- published at ACL 2018. The Stanford team maintains the official site and leaderboard at rajpurkar.github.io/SQuAD-explorer/.

## Lineage

SQuAD 2.0 (arXiv 1806.03822) is SQuAD's direct successor and has no page of its own here; this page discusses it throughout, since almost every practical use of "SQuAD" today is actually 2.0 data (see How to run it). SQuAD 1.1's span-extraction, given-passage design directly shaped later benchmarks with pages here: CoQA (`coqa`) built its evaluation tooling on SQuAD's own template, extending the format into multi-turn dialogue; DROP (`drop`) was designed to go beyond span extraction with discrete reasoning a shallow matcher cannot solve; TriviaQA (`triviaqa`), NarrativeQA (`narrativeqa`) and TyDiQA (`tydiqa`) all reuse SQuAD-style span/F1 evaluation in part. No true predecessor was confirmed.

## Saturation and contamination

The official SQuAD 2.0 leaderboard's top entry, "IE-Net (ensemble)" from RICOH_SRCB_DML (June 2021), scores 90.939 EM / 93.214 F1, above the board's own 86.831 EM / 89.452 F1 human baseline; several ALBERT-based systems had already crossed the human F1 figure by September 2019. The board still receives occasional submissions -- as recently as September 2023 -- but none have displaced the 2021 top score, so the ceiling has been effectively static for years, with no current frontier lab appearing to submit at all. Contamination risk is high: the public files for both versions have been freely downloadable since 2016 and 2018, and SQuAD is among the most widely mirrored, cited and reproduced datasets in NLP.

## How to run it

Every current harness implementation found here runs SQuAD 2.0 (unanswerable-aware) data, not plain 1.1, despite inconsistent naming. inspect_evals' task is literally named `squad` but loads `rajpurkar/squad_v2`'s validation split and instructs the model to answer "unanswerable" (lowercase) when appropriate, scoring with F1 and exact match. lm-evaluation-harness names its task `squadv2`, loads the `lighteval/squad_v2` mirror, and uses the official Hugging Face `evaluate` "squad_v2" metric, separately reporting answerable-only (HasAns_*), unanswerable-only (NoAns_*), and threshold-tuned (best_exact/best_f1) submetrics alongside overall EM/F1. OpenCompass's `squad2.0` config reads a local `dev-v2.0.json` file and prompts the model to answer or say "impossible to answer" -- different wording from inspect_evals. No SQuAD 1.1-only implementation was found in any of the three harnesses checked.

## Reading the numbers

Before trusting a reported "SQuAD" score, check which version and split produced it: given how consistently modern harnesses run SQuAD 2.0's validation set under the "squad" name, a score more likely reflects unanswerable-question handling than pure span extraction, whatever it is labelled. Because the official leaderboard has sat above human performance since 2019 and its ceiling has not moved since 2021, a high score from a modern LLM is close to uninformative on its own -- it mainly confirms basic extractive reading over short, clean Wikipedia passages, a capability that stopped differentiating systems years ago, and says nothing about longer documents or reasoning beyond span-matching. Given the dataset's age, scale and ubiquity, elevated performance is at least as plausibly explained by training exposure as by comprehension at evaluation time. A "SQuAD" number today is more useful as a sanity check than as a way to compare capable models.
