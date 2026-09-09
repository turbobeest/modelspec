---
id: exams_multilingual
name: "EXAMS (Multilingual)"
aliases:
  - "EXAMS"
  - "EXAMS-QA"
page_kind: benchmark
category: knowledge
subcategory: "multilingual high-school exam multiple-choice QA (16 languages, 24 subjects)"
status: active
summary: "24,143 real high-school exam questions across 16 languages and 24 subjects (Hardalov et al., 2020); arabic_exams documents the AceGPT-repackaged Arabic slice of this same corpus."
measures: >
  EXAMS gives a model a real high-school exam question, drawn from actual national school examinations
  rather than written for the benchmark, with three to five labelled answer options and one correct
  answer. Its distinguishing feature is breadth: the "multilingual" testbed this page documents spans
  16 languages across 8 language families and 24 subjects from the natural and social sciences, so a
  score on it mixes reading comprehension in a given language with subject-matter recall, and can be
  read per-language or per-subject rather than only as one blended number. A separate "cross-lingual"
  testbed (train in one language, test in another) exists in the same release but is not what this page
  or HELM's `exams_multilingual` scenario evaluate.
task_format: >
  Multiple-choice exam question with labelled options (commonly four, though the release's ARC-style
  format allows a variable number per item) and a single correct answer, in one of 16 languages; HELM
  parameterises a run by `language` and `subject` (each can be set to "all"), scoring the model's chosen
  option by exact match.
metric:
  name: exact_match (accuracy)
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random-guess figure applies across the whole multilingual set because the number of
    answer options per item is not fixed at one value throughout (commonly four, per the Arabic slice
    documented in arabic_exams.md, but the release's ARC-style structure permits variation); no
    aggregate baseline was found stated by the paper or by HELM for the full 16-language testbed.
dataset:
  size: 24143
  size_note: >
    24,143 questions in the "multilingual" testbed configuration that HELM's `exams_multilingual`
    scenario loads (`mhardalov/exams`, config "multilingual"): 7,961 train, 2,672 dev, 13,510 test,
    confirmed directly from the Hugging Face dataset's own split sizes and matching the source
    repository's own per-language table exactly. That table lists 16 languages: Albanian, Arabic,
    Bulgarian, Croatian, French, German, Hungarian, Italian, Lithuanian, Macedonian, Polish,
    Portuguese, Serbian, Spanish, Turkish and Vietnamese -- languages with fewer than 900 examples
    (Arabic, French, German, Lithuanian, Spanish) appear in the test split only. This figure and language
    count is confirmed independently three ways: the paper's own abstract ("more than 24,000... in 16
    languages"), the HELM scenario's docstring (which quotes the same abstract), and the Hugging Face
    dataset card's own structured language tags (16 ISO codes). The GitHub repository's introductory
    prose, by contrast, states the dataset spans "26" languages -- a figure this page could not
    reconcile with the same repository's own results table, its own per-language dataset files, or any
    of the three independent 16-language confirmations above; it is recorded here as an unresolved
    internal inconsistency in the source repository's documentation rather than a second valid reading.
  url: "https://huggingface.co/datasets/mhardalov/exams"
  license: "CC BY-SA 4.0, per both the GitHub repository's own licence metadata and the Hugging Face dataset card's licence tag"
  languages:
    - sq
    - ar
    - bg
    - hr
    - fr
    - de
    - hu
    - it
    - lt
    - mk
    - pl
    - pt
    - sr
    - es
    - tr
    - vi
  modalities:
    - text
  splits: "train (7,961) / dev (2,672) / test (13,510) in the multilingual-testbed configuration, split independently per language at roughly 37.5%/12.5%/50%; languages with under 900 examples have test-split-only data"
  public_test_set: true
publisher:
  org: ""
  authors:
    - "Momchil Hardalov"
    - "Todor Mihaylov"
    - "Dimitrina Zlatkova"
    - "Yoan Dinkov"
    - "Ivan Koychev"
    - "Preslav Nakov"
  url: "https://github.com/mhardalov/exams-qa"
paper:
  title: "EXAMS: A Multi-subject High School Examinations Dataset for Cross-lingual and Multilingual Question Answering"
  arxiv: "2011.03080"
  url: "https://aclanthology.org/2020.emnlp-main.438/"
  year: 2020
leaderboard_url: ""
repo_url: "https://github.com/mhardalov/exams-qa"
released: "2020-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - arabic_exams
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No maintained leaderboard or dated top-score reading for the full 16-language `exams_multilingual`
    aggregate was found in the sources reviewed for this page; HELM registers it as a runnable scenario,
    parameterised per language and subject, rather than as part of a published leaderboard site.
contamination:
  risk: medium
  note: >
    The full multilingual question set, including answers, has been publicly downloadable since the
    dataset's 2020 release under an open licence, so a model trained on a broad multilingual web crawl
    since then has plausibly seen at least some of these exact questions; no held-out portion or canary
    mechanism was found described for this dataset.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "exams_multilingual"
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness's own task list carries no general-purpose "exams" task over this multilingual
    corpus; it has only `aexams`, which loads a separate, AceGPT-curated Arabic-only mirror (documented
    on this repository's arabic_exams.md page), not this dataset directly.
tags:
  - knowledge
  - multiple-choice
  - multilingual
  - exam-qa
  - family
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/exams_multilingual_scenario.py"
    title: "HELM EXAMSMultilingualScenario source (docstring quoting the paper abstract; dataset_path, language/subject parameterisation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/multilingual_run_specs.py"
    title: "HELM multilingual_run_specs.py (exams_multilingual run-spec function, adapter and grouping)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2011.03080"
    title: "EXAMS: A Multi-Subject High School Examinations Dataset for Cross-Lingual and Multilingual Question Answering (arXiv abstract page)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2020.emnlp-main.438/"
    title: "EXAMS (ACL Anthology, EMNLP 2020 publication record)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/mhardalov/exams-qa/main/README.md"
    title: "mhardalov/exams-qa GitHub README (introductory '26 languages' prose; per-language Multilingual and Cross-lingual testbed tables listing 16 languages)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/mhardalov/exams"
    title: "mhardalov/exams dataset metadata, Hugging Face API (16 language tags, CC BY-SA 4.0 licence tag, arxiv:2011.03080 linked)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=mhardalov/exams&config=multilingual"
    title: "mhardalov/exams 'multilingual' config split sizes, Hugging Face datasets-server (train 7,961 / validation 2,672 / test 13,510)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

EXAMS gives a model a real high-school exam question, drawn from actual national school examinations
rather than written for the benchmark, with several labelled answer options and one correct answer. The
"multilingual" testbed this page documents -- the specific configuration HELM's `exams_multilingual`
scenario loads -- spans 16 languages across 8 language families and 24 subjects drawn from the natural
and social sciences, so a score reflects reading comprehension in a given language combined with
subject-matter recall, and is best read per language or per subject rather than as one blended figure.
A separate "cross-lingual" testbed in the same release, designed to test knowledge transfer from a
source language to an unseen target language, exists but is not what this page or HELM's scenario
evaluate.

## How it is scored

HELM parameterises each run by `language` and `subject` (either can be set to "all" to sweep the whole
axis), and scores the model's selected answer option by exact match against the reference text. Because
the underlying exam items follow an ARC-style format that does not fix the number of options at one
value across every language and subject, this page could not confirm a single random-guess baseline
that applies to the whole multilingual set; four options is the common case (as documented for the
Arabic slice in this repository's arabic_exams.md), but this should not be assumed uniform.

## Dataset and licence

The multilingual testbed totals 24,143 questions: 7,961 train, 2,672 dev and 13,510 test, split
independently per language at roughly 37.5%/12.5%/50% (languages with fewer than 900 examples appear in
the test split only). This page confirmed the 16-language count three independent ways: the paper's own
abstract, the HELM scenario's docstring (which quotes that abstract verbatim), and the Hugging Face
dataset card's own structured language tags. The source GitHub repository's introductory prose,
however, states the dataset spans "26" languages -- a figure that does not match its own results table,
its own per-language data files, or any of the three independent 16-language confirmations above. This
page records that as an unresolved inconsistency within the source repository's own documentation,
not as a second valid reading of the dataset's actual scope. The data is released under CC BY-SA 4.0,
stated identically by the repository and the Hugging Face dataset card, with public answers throughout.

## Who publishes it

EXAMS was published by Momchil Hardalov, Todor Mihaylov, Dimitrina Zlatkova, Yoan Dinkov, Ivan Koychev
and Preslav Nakov at EMNLP 2020 (posted to arXiv in November 2020). The authors maintain the reference
repository and its Hugging Face mirror.

## Lineage

This is the parent, full multilingual corpus. [Arabic EXAMS](arabic_exams.md), already documented in
this repository, covers only the Arabic-language slice, re-packaged for LLM evaluation by the AceGPT
project rather than loaded directly from this multilingual release. The two are closely connected in a
way this page can confirm numerically: this corpus's own per-language table lists exactly 562 Arabic
test-only items (Arabic falls below the 900-example threshold for a train/dev split), and
arabic_exams.md independently documents its AceGPT-curated Arabic dataset as totalling exactly 562 items
(537 test plus 25 dev, a re-split of the same pool for few-shot prompting purposes) -- strong evidence
the two trace to the same underlying Arabic question set, merely re-split differently. No other language
slice of this corpus has its own page in this repository yet.

## Saturation and contamination

No maintained leaderboard or dated top-score reading was found for the full 16-language
`exams_multilingual` aggregate; HELM registers it as a runnable, parameterised scenario rather than
listing it on a published leaderboard site, and this page found no independent tracking of frontier
model scores against it. Contamination risk is medium: the full question set, including answers, has
been publicly downloadable under an open licence since 2020, so a model trained on a broad multilingual
web crawl since then has plausibly seen at least some of it, though no held-out portion or canary
mechanism was found described for the release.

## How to run it

HELM implements it as the `exams_multilingual` scenario, loading `mhardalov/exams` at a pinned dataset
revision, with one RunSpec produced per `(language, subject)` pair (results are grouped under both the
overall `exams_multilingual` label and a finer `exams_multilingual_{language}_{subject}` label). No
lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench implementation of the full multilingual
corpus was found; lm-evaluation-harness's only EXAMS-derived task, `aexams`, loads a separate,
AceGPT-curated Arabic-only mirror rather than this dataset directly (see arabic_exams.md).

## Reading the numbers

A high EXAMS score for a given language and subject indicates a model can read that language well
enough to parse a real exam question and recall or infer the right academic fact -- but because the
corpus spans 16 languages of very different resource levels and 24 subjects, an aggregate score across
all of them can obscure large per-language gaps that matter more than the average. Always check which
language and subject a reported EXAMS number covers, and whether it comes from this multilingual
testbed or from a repackaged single-language slice such as arabic_exams -- the two are related but not
interchangeable, since repackaged slices can use different splits, prompt formats or scoring protocols
than this page's own HELM scenario.
