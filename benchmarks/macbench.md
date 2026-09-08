---
id: macbench
name: "MaCBench"
aliases:
  - "MaCBench: Probing the limitations of multimodal language models for chemistry and materials research"
page_kind: benchmark
category: domain
subcategory: "multimodal (vision-language) chemistry and materials science"
status: active
summary: >-
  A 1,153-question, 34-subset benchmark testing whether vision-language models can extract, reason
  about and interpret chemistry and materials-science data from images paired with text.
measures: >
  MaCBench evaluates vision-language models on real-world chemistry and materials-science tasks that
  require reading an image together with accompanying text: every question needs both modalities to
  answer. Its 34 subsets are grouped into three categories -- data extraction (hand-drawn molecules,
  organic-chemistry reaction schemas, chirality, isomers, reading tables and plots, US patent figures),
  in-silico and lab experiments (lab safety and equipment QA, crystal-structure analysis from CIF
  data: atomic species, density, symmetry, volume, crystal system) and data interpretation (AFM image
  analysis, adsorption-isotherm and Henry-constant comparisons for metal-organic frameworks,
  electronic-structure and XRD pattern reading). It is a sibling of this repository's `chembench`
  page, built by an overlapping author group specifically to extend that text-only chemistry
  benchmark into the multimodal setting.
task_format: >
  A mix of multiple-choice and open-ended (numeric or short-text) questions, each pairing an image
  (a diagram, plot, spectrum, micrograph or hand-drawn structure) with a text question. An optional
  chain-of-thought mode can be enabled; by default samples are shuffled.
metric:
  name: >-
    accuracy: regex/pattern match against the labelled option for multiple-choice questions, and a
    tolerance-based numeric match (mean absolute error against a per-question relative or absolute
    tolerance) for open-ended quantitative questions, aggregated into one overall accuracy plus
    per-subset accuracy and standard error
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random-guess baseline applies because option counts vary and a portion of questions are
    open-ended. Unlike this repository's `chembench` page, no human-expert baseline study for MaCBench
    was found in the sources opened for this page.
dataset:
  size: 1153
  size_note: >
    1,153 multimodal question-answer pairs across 34 subsets, manually curated by chemistry and
    materials-science experts (confirmed from both the paper and the inspect_evals task README).
    Every question requires both an image and its accompanying text to answer.
  url: "https://huggingface.co/datasets/jablonkagroup/MaCBench"
  license: "MIT"
  languages: ["en"]
  modalities: ["text", "image"]
  splits: "single evaluation corpus (no train/test split), organised into 34 named subsets under 3 categories"
  public_test_set: true
publisher:
  org: "Laboratory of Organic and Macromolecular Chemistry (IOMC), Friedrich Schiller University Jena; multi-institution collaboration"
  authors: ["Nawaf Alampara", "Mara Schilling-Wilhelmi", "Martiño Ríos-García", "Indrajeet Mandal", "Pranav Khetarpal", "Hargun Singh Grover", "N. M. Anoop Krishnan", "Kevin Maik Jablonka"]
  url: "https://github.com/lamalab-org/chembench"
paper:
  title: "Probing the limitations of multimodal language models for chemistry and materials research"
  arxiv: "2411.16955"
  url: "https://arxiv.org/abs/2411.16955"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/lamalab-org/chembench"
released: "2024-11"
last_updated: "2025-02"
lineage:
  family: ""
  predecessor: "chembench"
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 72.59
  as_of: "2026-04"
  note: >
    inspect_evals' own reproducibility report (evaluation version 1-A) recorded `openai/gpt-5-nano`
    at 68.78% overall accuracy on 2026-03-04 and `openai/gpt-5.2` at 72.59% on 2026-04-23, both
    scoring all 1,153 samples; the 72.59% figure matched the original MaCBench-codebase summary for
    the same model exactly. The paper's own framing supports "watch" over "saturated": it reports
    near-perfect scores on basic perception tasks like equipment identification, alongside
    fundamental, still-unresolved weaknesses in spatial reasoning, cross-modal synthesis and
    multi-step inference, so the overall figure sits well below a ceiling despite easy subsets
    already being solved.
contamination:
  risk: medium
  note: >
    The dataset and its answers are public on Hugging Face and GitHub under the MIT licence, so
    exposure through training on web-scraped chemistry content is plausible for any model trained
    after November 2024. Because every question is genuinely multimodal (an image plus text, rather
    than text alone), verbatim memorisation is harder than for pure-text benchmarks, which is a
    structural mitigant rather than a designed contamination-resistance mechanism. No dedicated
    contamination study was found in the sources opened for this page.
harness:
  lm_eval: ""
  inspect_evals: "macbench"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The paper's own reference implementation is the `chembench` Python package
    (github.com/lamalab-org/chembench), which added multimodal support specifically to run MaCBench;
    see lamalab-org.github.io/chembench/getting_started/#how-to-benchmark-on-multi-modal-tasks.
    inspect_evals' `macbench` task takes a `task_name` parameter selecting one of the 34 subsets (or
    all, merged) and a `cot` flag, and pins the Hugging Face dataset to a specific revision
    (ca13e7aff2f9a40cb638360c3e569de173ae1fdd) for reproducibility.
tags:
  - domain
  - chemistry
  - materials-science
  - multimodal
  - vision-language
  - image-to-text
sources:
  - url: "https://arxiv.org/abs/2411.16955"
    title: "Probing the limitations of multimodal language models for chemistry and materials research"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2411.16955"
    title: "MaCBench (full text, ar5iv) -- affiliations, reference-implementation link"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/macbench/README.md"
    title: "inspect_evals macbench task README (34 subsets, scoring, dated evaluation report)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/jablonkagroup/MaCBench"
    title: "jablonkagroup/MaCBench dataset metadata (Hugging Face API) -- MIT licence, not gated"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MaCBench evaluates vision-language models on real-world chemistry and materials-science tasks that
genuinely require reading an image together with its accompanying text -- neither modality alone is
enough. Its 34 subsets fall into three categories: data extraction (hand-drawn molecules, organic
reaction schemas, chirality, isomers, tables, plots, US patent figures), in-silico and lab
experiments (lab safety and equipment identification, and crystal-structure analysis from CIF data
covering atomic species, density, symmetry, volume and crystal system) and data interpretation (AFM
image analysis, adsorption-isotherm and Henry-constant comparisons for metal-organic frameworks,
electronic-structure reasoning, and XRD pattern reading). It is a direct sibling of this repository's
`chembench` page: an overlapping author group, including corresponding author Kevin Maik Jablonka,
built MaCBench specifically to extend ChemBench's text-only chemistry evaluation into the multimodal
setting.

## How it is scored

Multiple-choice questions are scored with a regex/pattern match against the labelled correct option.
Open-ended quantitative questions are scored by extracting a numeric answer and checking it against a
per-question tolerance -- inherited from ChemBench's scoring code, falling back to ChemBench's 1%
relative-tolerance convention when a question does not specify its own. Results are reported as
overall accuracy plus a per-subset breakdown with standard error, rather than one undifferentiated
number, since the paper's own findings show sharply uneven performance across subsets. No single
random-guess baseline applies given the mixed multiple-choice/open-ended format, and unlike its
`chembench` sibling, no human-expert baseline study was found for MaCBench in the sources opened for
this page.

## Dataset and licence

MaCBench holds 1,153 multimodal question-answer pairs across 34 subsets, manually curated by
chemistry and materials-science experts, each requiring both an image (a diagram, spectrum,
micrograph, plot or hand-drawn structure) and accompanying text to answer. The Hugging Face dataset
(`jablonkagroup/MaCBench`) and the GitHub reference implementation are both released under the MIT
licence and are not gated; the full corpus, with answers, is public.

## Who publishes it

MaCBench comes from Nawaf Alampara, Mara Schilling-Wilhelmi, Martiño Ríos-García, Indrajeet Mandal,
Pranav Khetarpal, Hargun Singh Grover, N. M. Anoop Krishnan and corresponding author Kevin Maik
Jablonka, primarily based at the Laboratory of Organic and Macromolecular Chemistry (IOMC), Friedrich
Schiller University Jena, Germany, in a multi-institution collaboration. The paper was first posted
to arXiv in November 2024 and revised in February 2025. The `lamalab-org` GitHub organisation, the
same group that maintains ChemBench, maintains the reference implementation.

## Lineage

MaCBench is the direct multimodal extension of this repository's `chembench` page: ChemBench's own
Hugging Face dataset card in fact cites the MaCBench paper as the source of its multimodal
capabilities, and MaCBench's reference implementation lives inside the same `chembench` code
repository rather than a separate one. No further successor or variant of MaCBench was found in
sources opened for this page. Readers should not confuse `macbench` (this page, a vision-language
chemistry and materials benchmark) with `matbench` (a text-only, classical-ML materials-property
suite) or `mathbench` (a mathematics education benchmark) elsewhere in this batch -- the names are
easy to mistake for one another but test unrelated things.

## Saturation and contamination

inspect_evals' own reproducibility report recorded `openai/gpt-5-nano` at 68.78% overall accuracy on
2026-03-04 and `openai/gpt-5.2` at 72.59% on 2026-04-23 (both over all 1,153 samples), with the
72.59% figure matching the original MaCBench codebase's own summary for the same model exactly. The
paper's own framing backs a "watch" rather than "saturated" call: it reports near-perfect scores on
basic perception subtasks like equipment identification and standardised data extraction, alongside
fundamental, still-open weaknesses in spatial reasoning, cross-modal information synthesis and
multi-step logical inference -- so the overall number sits well below a ceiling even where individual
easy subsets are already solved. Contamination risk is medium: the dataset and answers are public
since November 2024 under the MIT licence, though the requirement to read an image alongside text
makes verbatim memorisation harder than for text-only benchmarks.

## How to run it

inspect_evals registers the task as `inspect_evals/macbench`, with a `task_name` parameter to run one
of the 34 named subsets (or all, merged, by default) and a `cot` flag to enable chain-of-thought
prompting; it pins the Hugging Face dataset to a specific revision
(`ca13e7aff2f9a40cb638360c3e569de173ae1fdd`) for reproducibility. The paper's own reference
implementation is the `chembench` Python package's multimodal extension, documented at
lamalab-org.github.io/chembench. No lm-evaluation-harness, HELM, OpenCompass or BIG-bench
registration was confirmed during this research.

## Reading the numbers

A high overall MaCBench score can hide large gaps between subsets: the paper's own results show
near-perfect performance on basic identification tasks next to weak performance on tasks requiring
spatial reasoning or synthesising information across the image and the text, so the per-subset
breakdown matters more than the aggregate. Because scoring mixes an exact pattern match (multiple
choice) with a tolerance-based numeric check (open-ended questions), always confirm which subsets
contributed to a reported number before comparing two MaCBench scores, and check whether
chain-of-thought prompting was enabled, since that is an explicit, scoring-relevant option in the
reference harness.
