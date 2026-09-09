---
id: narrativeqa
name: "NarrativeQA"
aliases:
  - "The NarrativeQA Reading Comprehension Challenge"
page_kind: benchmark
category: long-context
subcategory: "generative question answering over long narratives (books and screenplays)"
status: active
summary: "Free-form questions about entire books and movie scripts, scored against human reference answers, though most harnesses answer from a summary rather than the full narrative."
measures: >
  NarrativeQA gives a model a question about a book or a movie script and asks it to produce a
  free-form answer, the way a reader who has actually read the work could. The stories come from
  Project Gutenberg (books) and sites such as IMSDb (movie scripts); each was paired with its
  Wikipedia plot summary, and Amazon Mechanical Turk annotators wrote ten question-answer pairs per
  story after reading only the summary, not the full text, so that questions probe the underlying
  narrative rather than a specific sentence. The paper defines two settings that differ enormously in
  difficulty: "summaries only," where the model reads the same Wikipedia summary the annotators used,
  and "stories only," where it must find the answer somewhere in the full book or script, which can
  run to tens of thousands of words. Only the second setting exercises the long-document
  comprehension the benchmark is best known for.
task_format: >
  Free-form text generation: given a passage (a summary or a full story, depending on setting) and a
  question, produce a short answer. Each question has two independently written human reference
  answers. The official evaluation script scores against both metrics from the paper (Bleu-1, Bleu-4,
  Meteor and Rouge-L); HELM's implementation instead reports a single token-level F1 as its main
  metric, which does not appear in the original paper at all.
metric:
  name: "Rouge-L, Bleu-1, Bleu-4 and Meteor against two reference answers (the paper's own metric suite); HELM instead reports token-level F1 as its main metric, and OpenCompass scores with a TriviaQA-style evaluator"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: 57.17
  baseline_note: >
    The paper measures human performance only once, by scoring one Mechanical Turk reference answer
    against the other under the "given summaries" setting, and explicitly reuses that same figure in
    its "full stories" results table rather than collecting a separate human score for the harder
    setting (its Table 6 caption states this directly). The 57.17 recorded here is that human figure
    for Rouge-L; the same exercise gives Bleu-1 44.24, Bleu-4 18.17 and Meteor 23.87. Because no human
    baseline exists for the stories-only setting, a model's stories-only score cannot be compared
    against human performance the way its summaries-only score can. There is no meaningful random
    baseline for free-form generation.
dataset:
  size: 46765
  size_note: >
    46,765 question-answer pairs (32,747 train, 3,461 validation, 10,557 test), each attached to one
    of 1,102 / 115 / 355 stories per split -- confirmed directly from the Hugging Face mirror's split
    counts and from HELM's own scenario docstring, which state the same numbers. HELM's docstring
    gives a headline total of "1,567 stories," which is five short of the 1,572 its own per-split
    figures sum to; this page uses the per-split figures. The book/script text itself is not shipped
    in the Hugging Face parquet files (only a `document.url` pointer and Wikipedia summary are), so
    reproducing the full "stories only" setting requires separately downloading the source texts,
    which the reference repository's `download_stories.sh` script does.
  url: "https://huggingface.co/datasets/deepmind/narrativeqa"
  license: "Apache-2.0"
  languages:
    - en
  modalities:
    - text
  splits: "train (32,747 QA pairs / 1,102 stories) / validation (3,461 / 115) / test (10,557 / 355); all three splits, including test, ship with answers"
  public_test_set: true
publisher:
  org: "DeepMind"
  authors:
    - "Tomáš Kočiský"
    - "Jonathan Schwarz"
    - "Phil Blunsom"
    - "Chris Dyer"
    - "Karl Moritz Hermann"
    - "Gábor Melis"
    - "Edward Grefenstette"
  url: "https://github.com/google-deepmind/narrativeqa"
paper:
  title: "The NarrativeQA Reading Comprehension Challenge"
  arxiv: "1712.07040"
  url: "https://arxiv.org/abs/1712.07040"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/google-deepmind/narrativeqa"
released: "2018"
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
    No dedicated NarrativeQA leaderboard was found; it is reported as one scenario inside broader
    suites (HELM, OpenCompass) rather than tracked on its own, and this repository's own model cards
    currently report no NarrativeQA scores at all (checked by grep across `models/`). Because HELM
    scores the easy summaries-only setting with its own F1 metric while OpenCompass feeds truncated
    raw story text and scores with a different evaluator, scores from the two are not comparable, and
    neither maps onto the original paper's Bleu/Meteor/Rouge-L numbers. That fragmentation, not a
    settled ceiling, is why status is unknown rather than saturated or open.
contamination:
  risk: high
  note: >
    Every story is either a pre-1928 Project Gutenberg book or a script mirrored on public sites such
    as IMSDb, and the Wikipedia summaries, questions and reference answers have all been public on
    GitHub and Hugging Face since 2017-2018. Both the source texts and the QA pairs are exactly the
    kind of widely-mirrored public text that ends up in large web crawls, and the test split's answers
    are public rather than held out, so a model could plausibly have seen the summary-question-answer
    triples directly during training rather than needing to read the story to answer.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "narrative_qa (HELM implements only the summaries-only setting, sampling one question per story with a fixed random seed rather than using all ten; scored with token-level F1 as HELM's main_metric)"
  opencompass: "narrativeqa (OpenCompass's own NarrativeQADataset loader reads each story's downloaded raw content, truncated to the first 100,000 characters, as the 'evidence' field -- not the Wikipedia summary -- then evaluates the public 'valid' split inside an 8,192-token sequence window with a TriviaQA-style evaluator)"
  bigbench: ""
  other: ""
tags:
  - reading-comprehension
  - long-context
  - question-answering
  - books
  - screenplays
sources:
  - url: "https://arxiv.org/abs/1712.07040"
    title: "The NarrativeQA Reading Comprehension Challenge (arXiv abstract)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.org/abs/1712.07040"
    title: "The NarrativeQA Reading Comprehension Challenge (ar5iv full text)"
    accessed: "2026-09-08"
  - url: "https://github.com/google-deepmind/narrativeqa"
    title: "google-deepmind/narrativeqa GitHub repository (README, data files, licence)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/deepmind/narrativeqa"
    title: "deepmind/narrativeqa dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/narrativeqa_scenario.py"
    title: "HELM NarrativeQAScenario source"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/narrativeqa"
    title: "OpenCompass narrativeqa dataset config directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/narrativeqa.py"
    title: "OpenCompass NarrativeQADataset loader source"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

NarrativeQA gives a model a question about a book or a movie script and asks for a free-form answer, the way an actual reader could give one. Stories come from Project Gutenberg and script archives such as IMSDb; each was matched to its Wikipedia plot summary, and crowd annotators wrote ten question-answer pairs per story after reading only that summary, so questions probe the narrative rather than a memorable sentence. Crucially, the benchmark defines two settings of very different difficulty: "summaries only," where the model reads the same short Wikipedia summary the annotators used, and "stories only," where it must locate the answer somewhere in the full book or script, which can run to tens of thousands of words. Only the stories setting exercises the long-document comprehension NarrativeQA is known for; as the "How to run it" section below shows, most current harnesses do not actually use it.

## How it is scored

Answers are free text, graded against two independent human reference answers per question. The paper's own metric suite is Bleu-1, Bleu-4, Meteor and Rouge-L; it reports no single token-F1 number. Later re-implementations diverge from this and from each other: HELM computes its own token-level F1 as the scenario's main metric, and OpenCompass applies a TriviaQA-style evaluator instead. A model's human ceiling is only known for the summaries setting -- the paper scores one crowd worker's reference answer against the other's and explicitly reuses that same figure in its stories-only results table rather than running a separate human evaluation, so there is no human baseline specific to the harder, full-document task.

## Dataset and licence

The Hugging Face mirror reports 46,765 question-answer pairs over 1,572 stories, split 32,747/3,461/10,557 pairs (1,102/115/355 stories) across train, validation and test; all three splits, including test, ship with answers. The dataset is released under the Apache-2.0 licence. The parquet files carry the Wikipedia summaries and metadata directly but only a URL pointer to each story's full text, so running the "stories only" setting requires a separate download step (the reference repository ships a `download_stories.sh` script for this), and some linked pages have gone missing since 2017.

## Who publishes it

NarrativeQA comes from Tomáš Kočiský, Jonathan Schwarz, Phil Blunsom, Chris Dyer, Karl Moritz Hermann, Gábor Melis and Edward Grefenstette at DeepMind, first posted to arXiv in December 2017 and published in Transactions of the Association for Computational Linguistics in 2018. DeepMind (now Google DeepMind) continues to host the reference data and evaluation code on GitHub; there is no dedicated leaderboard.

## Lineage

This repository has no separate page yet for either of NarrativeQA's two constituent tasks (SQuAD-style extractive QA, which it deliberately moves beyond, or free-form generative QA more broadly), so no predecessor or successor id is recorded. NarrativeQA is itself used as a component scenario inside larger suites rather than spawning its own family of named variants: HELM includes it as a standard scenario, and OpenCompass carries its own dataset config, both discussed below.

## Saturation and contamination

No dedicated NarrativeQA leaderboard was found, and this repository's own model cards currently report no NarrativeQA scores at all. Because HELM and OpenCompass test different settings with different metrics -- and neither matches the original paper's Bleu/Meteor/Rouge-L suite -- there is no single number to call saturated or open, so status is recorded as unknown rather than guessed. Contamination risk is high: every story is public-domain or web-mirrored text, and the summaries, questions and answers (including the test split's) have been openly downloadable since 2017-2018, making it plausible a model has seen the summary-question-answer triples directly rather than needing to read the story.

## How to run it

No lm-evaluation-harness or inspect_evals task for NarrativeQA was found in either project's current task list. HELM implements a `narrative_qa` scenario, but only the summaries-only setting, and it randomly samples a single question per story (fixed seed) rather than evaluating all ten, scoring the result with its own token-F1 metric. OpenCompass's `narrativeqa` config takes the opposite approach to HELM: its `NarrativeQADataset` loader reads each story's raw downloaded content, truncated to the first 100,000 characters, as the model's "evidence," not the Wikipedia summary, then evaluates the public `valid` split inside an 8,192-token generation window using a TriviaQA-style evaluator -- meaning the model very often sees only the opening of a long book or script rather than the portion relevant to a given question. These are three genuinely different tasks sharing one name.

## Reading the numbers

Before trusting a reported "NarrativeQA" score, establish which setting produced it: a summaries-only score mostly measures short-passage reading comprehension, while a true stories-only score would measure whether a model can find and use information buried in a very long document -- but almost no current harness actually runs that setting end to end, and OpenCompass's context-window truncation means even its story-based numbers may not reflect the full text either. Scores computed with different metrics (F1 versus Bleu/Meteor/Rouge-L) are not interchangeable and should not be compared directly. Given the dataset's age and full public availability, treat any strong score with some suspicion of memorization rather than genuine long-document reasoning.
