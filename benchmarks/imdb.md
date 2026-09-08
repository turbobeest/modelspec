---
id: imdb
name: "IMDb (Large Movie Review Dataset)"
aliases:
  - "IMDB"
  - "Large Movie Review Dataset"
  - "aclImdb"
page_kind: benchmark
category: reasoning
subcategory: "binary sentiment classification of movie reviews (legacy dataset, now mainly a calibration and robustness check)"
status: saturated
summary: "50,000 polarised IMDb movie reviews for binary sentiment classification, from a 2011 paper; frontier models sit far past the ceiling, so it now serves mainly as a robustness and calibration check."
measures: >
  IMDb asks a model to read a full movie review scraped from the IMDb website and classify it as
  positive or negative. Only strongly polarised reviews are included -- a rating of 7/10 or higher
  counts as positive, 4/10 or lower as negative, and the ambiguous middle range was deliberately
  excluded -- so the classification task itself is unambiguous even though real review text is
  often long, informal and mixed in tone. This predates the instruction-tuned LLM era entirely: it
  was built as a representation-learning benchmark for word-vector and embedding methods, not to
  probe reasoning, knowledge or instruction-following, and it is best read today as exactly that --
  an old, well-understood classification dataset now used mainly to sanity-check a model's basic
  text-classification competence and robustness rather than to differentiate strong modern models.
task_format: >
  Binary sentiment classification given the full text of one review; the model outputs "Positive"
  or "Negative", typically zero- or few-shot, scored by exact or quasi-exact match against the
  gold label.
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  baseline_note: >
    50% is the two-class random-guess rate on this label-balanced dataset. The original 2011 paper's
    own best model reached 88.89% accuracy; the dataset's current official landing page states that
    modern transformer models (BERT and later) reach 95-97% test accuracy, well past the level at
    which the benchmark meaningfully separates strong models from each other.
dataset:
  size: 50000
  size_note: >
    50,000 labelled reviews, split evenly into 25,000 for training and 25,000 for testing, each half
    itself balanced between positive and negative labels; confirmed via the Hugging Face
    datasets-server for the `stanfordnlp/imdb` mirror. A further 50,000 unlabelled reviews are
    included for unsupervised or semi-supervised use and are not part of the classification task
    HELM or other harnesses score. HELM's scenario evaluates the 25,000-review test split, with a
    small number of matched examples swapped out for their counterparts from Allen AI's IMDb
    Contrast Sets (Gardner et al., 2020), a human-perturbed robustness check built on top of this
    dataset.
  url: "https://huggingface.co/datasets/stanfordnlp/imdb"
  license: >
    Not formally stated by the original release; the Hugging Face mirror's card lists the licence
    only as "other," without further detail, and the dataset's own official page states no explicit
    licence terms beyond a request to cite the paper.
  languages:
    - en
  modalities:
    - text
  splits: "25,000 train / 25,000 test (both balanced positive/negative) / 50,000 further unlabelled reviews outside the classification task"
  public_test_set: true
publisher:
  org: "Stanford University"
  authors:
    - "Andrew L. Maas"
    - "Raymond E. Daly"
    - "Peter T. Pham"
    - "Dan Huang"
    - "Andrew Y. Ng"
    - "Christopher Potts"
  url: "https://ai.stanford.edu/~amaas/data/sentiment/"
paper:
  title: "Learning Word Vectors for Sentiment Analysis"
  arxiv: ""
  url: "https://aclanthology.org/P11-1015/"
  year: 2011
leaderboard_url: ""
repo_url: "https://ai.stanford.edu/~amaas/data/sentiment/"
released: "2011-06"
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
    This page found no continuously maintained public leaderboard specific to IMDb, and did not
    confirm a single current top score from a primary source, so none is recorded here. The
    dataset's own official page states that modern transformer models reach 95-97% test accuracy,
    against an 88.89% score for the original 2011 paper's best model and a 50% random-guess floor;
    that gap, and IMDb's current role as one line inside broader suites like HELM rather than a
    standalone leaderboard, is why this page records it as saturated rather than open or watch.
contamination:
  risk: high
  note: >
    The full labelled dataset, including test-split answers, has been publicly downloadable without
    gating or a canary string since the 2011 release -- about fifteen years of exposure to web
    crawls and training corpora by this research date -- and the underlying reviews were themselves
    scraped from a public website even before that. This is among the most re-published and
    re-hosted classic NLP datasets in existence (mirrored across Hugging Face, TensorFlow Datasets,
    Keras and PyTorch-NLP), which only adds to its exposure.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "imdb"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - sentiment-classification
  - text-classification
  - legacy-benchmark
  - robustness
  - saturated
sources:
  - url: "https://aclanthology.org/P11-1015/"
    title: "Learning Word Vectors for Sentiment Analysis"
    accessed: "2026-09-08"
  - url: "https://ai.stanford.edu/~amaas/data/sentiment/"
    title: "Large Movie Review Dataset (IMDB), official dataset page"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/stanfordnlp/imdb"
    title: "stanfordnlp/imdb dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/stanfordnlp/imdb"
    title: "stanfordnlp/imdb dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/imdb_scenario.py"
    title: "HELM imdb_scenario.py"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

IMDb asks a model to read the full text of one movie review and classify its sentiment as positive or negative. Only strongly polarised reviews were included when the dataset was built -- a user rating of 7 out of 10 or higher counts as positive, 4 or lower as negative, and the ambiguous middle range was deliberately excluded -- so the labelling task itself is unambiguous even though the review text is often long, informal, and mixed in tone.

This dataset predates the instruction-tuned LLM era by roughly a decade. It was built to evaluate word-vector and representation-learning methods, not to probe reasoning, knowledge, or instruction-following, and it should be read today as exactly what it is: a well-understood, historically important text-classification dataset that modern language models solve close to a ceiling. A high score on it says a model can do basic sentiment classification, a capability that stopped differentiating strong models years ago -- it does not indicate strong reasoning, knowledge, or safety, and its main current value is as a floor check or a robustness probe rather than as a benchmark that separates capable models from each other.

## How it is scored

Scoring is plain accuracy against the gold positive/negative label, with a 50% random-guess floor on this label-balanced dataset. HELM's implementation prompts the model with the review text followed by "Sentiment:" and checks the generated completion against the label by quasi-exact match. The original 2011 paper's own best model reached 88.89% accuracy; the dataset's current official page states that modern transformer models reach 95-97%, effectively at ceiling for a two-class, heavily-polarised classification task.

## Dataset and licence

IMDb totals 50,000 labelled reviews, split evenly into 25,000 for training and 25,000 for testing, each half balanced between positive and negative labels, plus a further 50,000 unlabelled reviews included for unsupervised or semi-supervised use that fall outside the classification task itself. No formal licence is stated by the original release; the Hugging Face mirror's card lists the licence only as "other," without further detail. HELM's scenario scores the 25,000-review test split, with a small number of matched reviews swapped out for their counterparts from Allen AI's IMDb Contrast Sets (Gardner et al., 2020) -- human-written minimal edits designed to flip or stress-test the model's decision near the sentiment boundary.

## Who publishes it

IMDb comes from Andrew L. Maas, Raymond E. Daly, Peter T. Pham, Dan Huang, Andrew Y. Ng and Christopher Potts at Stanford University, presented at ACL-HLT 2011. The dataset continues to be maintained at its original Stanford URL, and is separately mirrored through Hugging Face Datasets, TensorFlow Datasets, Keras and PyTorch-NLP; no standalone leaderboard was found.

## Lineage

This repository does not track a formal predecessor for IMDb. Allen AI's IMDb Contrast Sets, referenced above, are the one directly relevant variant, since HELM's own scenario incorporates them as a built-in robustness check rather than treating IMDb as a plain classification task; contrast sets do not have their own page in this repository. The Stanford Sentiment Treebank (SST, and its binary variant SST-2, later folded into GLUE) is a related but independently built sentiment-classification benchmark from roughly the same research community and era; it is not a derivative of IMDb and does not have a page here either.

## Saturation and contamination

IMDb is saturated for any model built on modern pretraining. The gap the dataset's own page reports -- 95-97% for modern transformer models against an 88.89% score for the original 2011 baseline and a 50% random floor -- leaves little room to separate strong models, which is consistent with its current role as one line inside broader evaluation suites like HELM rather than a standalone leaderboard. Contamination risk is high: the full labelled dataset, test-split answers included, has been publicly downloadable without gating since 2011, roughly fifteen years of exposure by this research date, and it is among the most widely re-hosted classic NLP datasets in existence.

## How to run it

HELM implements this as the `imdb` scenario: it downloads the original `aclImdb_v1.tar.gz` archive, evaluates the 25,000-review test split (with contrast-set substitutions where available), and scores quasi-exact match between the generated completion and the gold sentiment label. No lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench implementation was confirmed for IMDb specifically in the sources reviewed for this page.

## Reading the numbers

A high IMDb score today confirms only that a model can do basic sentiment classification on clearly polarised text, a capability frontier models cleared years ago -- treat it as a floor check or a debugging sanity check, not as evidence of anything distinguishing about a model's language understanding. Because the dataset has been public for about fifteen years and is heavily re-hosted, any score should be read with contamination in mind rather than as clean evidence of generalisation. If IMDb appears in an evaluation report at all today, look specifically at whether the contrast-set examples were included and how the model performed on those relative to the plain test set -- that comparison, not the raw accuracy number, is where this dataset still has something to say about a model's robustness near a decision boundary.
