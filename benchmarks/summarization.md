---
id: summarization
name: "HELM Summarization"
aliases:
  - "SummarizationScenario"
page_kind: benchmark
category: generation
subcategory: "single-document abstractive summarization (HELM scenario wrapping XSum and CNN/DailyMail)"
status: active
summary: "HELM's single-document summarization scenario, which scores models on abstracting BBC news articles (XSum) or CNN/DailyMail articles into short summaries, mainly by ROUGE-2."
measures: >
  This is HELM's generic single-document summarization scenario: given a news article, the model must
  produce a short abstractive summary. The scenario class (`SummarizationScenario`) does not define one
  fixed dataset; it currently wraps two underlying corpora as separate configurable variants -- XSum
  (BBC news articles paired with a single-sentence, highly abstractive summary) and CNN/DailyMail
  (news articles paired with multi-sentence "highlight" summaries), plus an "xsum-sampled" variant that
  subsets XSum. All variants are English news text, and the model sees only the source article, with
  optional truncation and length-based filtering controls exposed by the scenario code.
task_format: "Free-text generation: given a news article (optionally truncated to a maximum token length), produce an abstractive summary."
metric:
  name: "ROUGE-2 (primary metric per HELM's own scenario metadata); other ROUGE variants also reported"
  direction: higher_is_better
  unit: "score"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    ROUGE-2 has no fixed random or human baseline comparable across datasets; HELM's own published
    finding (in the HELM paper) is that automated ROUGE-based scores on both XSum and CNN/DailyMail
    "largely fail to discriminate" between models that differ clearly under human evaluation, and that
    human raters judged some model summaries as better than the datasets' own reference summaries. No
    single numeric baseline was found in the sources opened for this page, so this field is left empty.
dataset:
  size: null
  size_note: >
    Size is not established for the scenario as a whole: it depends on which underlying dataset
    (xsum, xsum-sampled, or cnn-dm) is selected, each with its own train/validation/test counts drawn
    from the XSum and CNN/DailyMail releases respectively. This page did not independently re-derive
    exact per-variant counts as served by HELM's own pickled data mirror, so no single figure is
    recorded here; see the XSum and CNN/DailyMail primary sources for their own published sizes.
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/summarization_scenario.py"
  license: >
    Not established for the scenario as a whole. XSum and CNN/DailyMail are each redistributed by their
    own original publishers under their own terms (BBC news text and CNN/Daily Mail news text
    respectively); this page did not independently confirm a single licence covering HELM's
    repackaged, pickled copies of either dataset.
  languages:
    - en
  modalities:
    - text
  splits: "train / validation / test, drawn from each underlying dataset's own splits (XSum or CNN/DailyMail); HELM scores the test split by default"
  public_test_set: null
publisher:
  org: "Stanford Center for Research on Foundation Models (CRFM)"
  authors:
    - "Percy Liang"
    - "Rishi Bommasani"
    - "Tony Lee"
    - "and the HELM collaboration (many additional co-authors)"
  url: "https://crfm.stanford.edu/helm/"
paper:
  title: "Holistic Evaluation of Language Models"
  arxiv: "2211.09110"
  url: "https://arxiv.org/abs/2211.09110"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm"
released: "2022-11"
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
    Marked `watch` rather than `open` or `saturated` on the strength of HELM's own published finding
    that ROUGE-based automated scores on both XSum and CNN/DailyMail "largely fail to discriminate"
    genuine quality differences among models that human evaluators do distinguish, and that reference
    summaries in these datasets were themselves rated worse than some model outputs by human judges.
    That is evidence the automated metric has stopped being a reliable ranking signal, independent of
    whether any specific top score sits near a ceiling; no current top score was found in the sources
    opened for this page.
contamination:
  risk: high
  note: >
    Both underlying datasets -- XSum (BBC articles) and CNN/DailyMail -- have been public and widely
    mirrored across the open web and common pretraining corpora since 2015-2018, so their test-split
    articles and reference summaries are plausible pretraining-data members for current large models.
    No dedicated contamination study specific to HELM's summarization scenario was found in the sources
    consulted; this assessment rests on the source datasets' long public availability.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "summarization"
  opencompass: ""
  bigbench: ""
  other: >
    HELM's scenario code names itself "summarization" internally, but the runnable HELM run-specs are
    the three separate configurations `summarization_xsum`, `summarization_xsum_sampled`, and
    `summarization_cnndm`; there is no single runnable HELM task literally called `summarization`.
tags:
  - summarization
  - generation
  - news
  - rouge
  - helm
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/summarization_scenario.py"
    title: "HELM summarization_scenario.py (SummarizationScenario)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/summarization_scenario.py"
    title: "HELM summarization_scenario.py (raw)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM classic_run_specs.py, summarization_xsum/xsum_sampled/cnndm run specs"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2211.09110"
    title: "Holistic Evaluation of Language Models (Liang et al., arXiv:2211.09110)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2211.09110"
    title: "Holistic Evaluation of Language Models, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/D18-1206/"
    title: "Narayan et al. 2018, the XSum paper (cited by HELM's scenario docstring)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/K16-1028/"
    title: "Nallapati et al. 2016, CNN/DailyMail summarization dataset paper (cited by HELM's scenario docstring)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/helm/classic/latest/"
    title: "HELM classic leaderboard (JavaScript app; scenario-level scores not recovered as static text)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-006"
---

## What it measures

HELM's summarization scenario asks a model to read a news article and produce a short abstractive summary. It is not one fixed dataset: the underlying `SummarizationScenario` class currently supports two source corpora as separate configurable variants -- XSum, whose BBC news articles pair with a single, highly abstractive one-sentence summary, and CNN/DailyMail, whose articles pair with multi-sentence "highlight" summaries -- plus an `xsum-sampled` variant that draws a filtered subset of XSum. All variants are English news text, and the scenario exposes length-based filtering and truncation options (minimum/maximum training-document length, maximum document length at inference) rather than defining one canonical input length.

Because the underlying corpora differ so much in reference-summary style (XSum's single abstractive sentence versus CNN/DailyMail's multi-sentence extractive-leaning highlights), a score on one variant does not transfer to the other; they are best read as related but separate evaluations sharing one scenario implementation.

## How it is scored

Model output is free-text generation, scored primarily by ROUGE-2 against the dataset's reference summary, per HELM's own scenario metadata (`main_metric: rouge_2`, evaluated on the test split). HELM also reports other ROUGE variants alongside ROUGE-2 in its full results. Critically, HELM's own paper reports that automated ROUGE scoring on both XSum and CNN/DailyMail "largely fails to discriminate" between models that human evaluators judge clearly differently, and that human raters sometimes preferred model-generated summaries over the datasets' own reference summaries -- a direct finding about this scenario's own metric, not a general aside, that should inform how much weight a ROUGE-2 number carries here.

## Dataset and licence

Dataset size and licence are not established at the scenario level, because both depend on which of the three configurations (`xsum`, `xsum-sampled`, `cnn-dm`) is selected: each pulls its own train/validation/test split from XSum or CNN/DailyMail respectively, and HELM serves pickled copies of each from its own cloud storage rather than loading the original dataset hosts directly. XSum text originates from BBC articles and CNN/DailyMail text from CNN and Daily Mail articles; this page did not independently confirm a single licence statement covering HELM's repackaged copies of either, so `dataset.license` is left as a qualified "not established" rather than a guess.

## Who publishes it

HELM is published by the Stanford Center for Research on Foundation Models (CRFM), led by Percy Liang, Rishi Bommasani, Tony Lee and a large multi-author collaboration, in "Holistic Evaluation of Language Models" (arXiv:2211.09110, 2022). CRFM maintains the reference implementation and the public leaderboard at crfm.stanford.edu/helm.

## Lineage

This scenario has no tracked predecessor or successor id in this repository; it packages two pre-existing, independently published datasets (XSum, from Narayan et al. 2018, and CNN/DailyMail, built by Hermann et al. 2015 and adapted for summarization by Nallapati et al. 2016) rather than introducing a new one. Neither `xsum` nor `cnn_dailymail` has its own page in this repository at the time of writing; a separate `cnn_dailymail_abisee.md` page here covers a different (non-HELM) framing of the CNN/DailyMail corpus and is not the same evaluation protocol as this scenario.

## Saturation and contamination

This page marks the scenario `watch` rather than `open` or `saturated` because HELM's own paper reports that its automated ROUGE scoring on both underlying datasets fails to separate models the way human evaluation does, and that human judges sometimes rated model summaries above the datasets' reference summaries -- evidence the metric itself has stopped being a trustworthy ranking signal, independent of any single top score. No current top score was found in the sources opened for this page. Contamination risk is high: both XSum and CNN/DailyMail have been public and widely mirrored since 2015-2018, well within the range of likely pretraining-corpus inclusion for current large models, though no contamination study specific to this HELM scenario was found.

## How to run it

The scenario's own internal name is `summarization`, but HELM does not expose a single runnable task by that exact name: the three run-specs actually invoked are `summarization_xsum`, `summarization_xsum_sampled`, and `summarization_cnndm`, each combining the shared `SummarizationScenario` class with `get_summarization_adapter_spec()` and `get_summarization_metric_specs()`, plus HELM's standard generative-harms metrics. No configuration for this scenario was found in lm-evaluation-harness, OpenCompass, or BIG-bench in the sources opened for this page. Because HELM truncates and filters documents by length before scoring, and different reporters may run different variants (xsum vs. cnn-dm) under the shared "summarization" label, always confirm which specific run-spec a reported number came from before comparing it to another source.

## Reading the numbers

A ROUGE-2 score on this scenario mostly reflects lexical overlap with one dataset's reference summaries, not demonstrated summary quality -- and HELM's own paper is explicit that this overlap-based scoring often fails to track what human raters actually prefer. Treat a high score here as weak evidence at best, and prefer HELM's own human-evaluation results over the automated ROUGE numbers when they are available for a given model. Because the scenario spans two structurally different datasets under one name, always check whether a reported number is from the XSum, xsum-sampled, or CNN/DailyMail configuration before comparing it across models or papers.
