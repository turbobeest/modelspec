---
id: cardbiomedbench
name: CARDBiomedBench
aliases: []
page_kind: benchmark
category: domain
subcategory: "biomedical research question answering (neurodegenerative-disease pilot domain)"
status: active
summary: An NIH biomedical-research QA benchmark of 68,227 expert- and template-generated questions on neurodegenerative-disease genetics, molecular biology and clinical knowledge, LLM-judged for quality and safety.
measures: >
  CARDBiomedBench tests whether a model can answer complex biomedical-research questions that
  require integrating genetic, molecular and clinical knowledge, rather than simple fact lookup. Its
  pilot implementation focuses on neurodegenerative diseases (NDDs), a domain the authors chose
  because it demands combining several kinds of specialised evidence. Items were built by combining
  expert-annotated question-answer pairs with semi-automated, template-based augmentation drawn from
  authoritative public resources: drug-development data, genome-wide association studies (GWAS), and
  summary-data-based Mendelian randomisation (SMR) analyses. Each item is tagged with one or more of
  ten biological categories (for example, "Drug Disease Relations" or "Drug Gene Relations") and one
  or more of nine reasoning-skill categories (for example, "Multi-Filter" or "Join," names that echo
  the database-query templates the augmented items were generated from). It is a single-turn,
  English-only, text-only, open-ended question-answering task.
task_format: >
  Open-ended free-text biomedical question, answered zero-shot with no answer options offered; the
  free-text response is graded against a reference answer by a separate LLM judge rather than by
  exact string match, since correct biomedical answers vary in phrasing.
metric:
  name: "LLM-judged correctness; the paper's own two-axis Response Quality Rate and Safety Rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper reports two illustrative, not necessarily best-of-seven, headline results across seven
    private and open-source LLMs it evaluated: Claude-3.5-Sonnet scored a Response Quality Rate of
    25% (95% CI 25% +/- 1) with a Safety Rate of 76% +/- 1, described as excessively cautious, while
    ChatGPT-4o scored a Response Quality Rate of 37% +/- 1 with a Safety Rate of only 31% +/- 1,
    described as both inaccurate and unsafe. The abstract does not state which of the seven models
    scored highest overall on either axis, so neither figure is recorded here as a top score. No
    random or separate human baseline applies to this open-ended, judge-graded format. OpenCompass's
    own integration instead scores a single binary CORRECT/INCORRECT per item via a generic
    LLM-judge rubric (`GenericLLMEvaluator`), which collapses the paper's own two-axis quality/safety
    metric into one accuracy-like number.
dataset:
  size: 68227
  size_note: >
    68,227 question-answer pairs (58,079 train / 10,148 test), confirmed directly against the live
    Hugging Face parquet files; the paper's abstract rounds this to "over 68,000 Q/A pairs." Items
    pool expert-annotated questions with semi-automated, template-based augmentation, each tagged
    with one or more of ten biological categories and nine reasoning-skill categories (fields can
    hold several semicolon-separated values per item).
  url: "https://huggingface.co/datasets/NIH-CARD/CARDBiomedBench"
  license: "OpenRAIL++, per the Hugging Face dataset card's own metadata -- an unusual choice for a text QA dataset (more common for model weights); no separate licence statement was found in the paper itself."
  languages:
    - en
  modalities:
    - text
  splits: "58,079 train / 10,148 test (Hugging Face parquet split sizes); both splits carry gold answers"
  public_test_set: true
publisher:
  org: "Center for Alzheimer's and Related Dementias (CARD), National Institute on Aging, National Institutes of Health, with DataTecnica LLC, the Department of Computer Science at Johns Hopkins University, and NIA's Laboratory of Neurogenetics"
  authors:
    - Owen Bianchi
    - Maya Willey
    - Chelsea X. Alvarado
    - Benjamin Danek
    - Marzieh Khani
    - Nicole Kuznetsov
    - Anant Dadu
    - Syed Shah
    - Mathew J. Koretsky
    - Mary B. Makarious
    - Cory Weller
    - Kristin S. Levine
    - Sungwon Kim
    - Paige Jarreau
    - Dan Vitale
    - Elise Marsan
    - Hirotaka Iwaki
    - Hampton Leonard
    - Sara Bandres-Ciga
    - Andrew B. Singleton
    - Mike A. Nalls
    - Shekoufeh Mokhtari
    - Daniel Khashabi
    - Faraz Faghri
  url: "https://github.com/NIH-CARD/CARDBiomedBench"
paper:
  title: "CARDBiomedBench: A Benchmark for Evaluating Large Language Model Performance in Biomedical Research"
  arxiv: ""
  url: "https://www.biorxiv.org/content/10.1101/2025.01.15.633272"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/NIH-CARD/CARDBiomedBench"
released: "2025-01"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2025-01"
  note: >
    Both headline figures the paper reports sit well below the 100% ceiling (Claude-3.5-Sonnet 25%
    Response Quality Rate, ChatGPT-4o 37%), and the paper presents these as illustrating different
    failure modes (excessive caution versus inaccurate-and-unsafe) rather than as the top of a
    ranking, so no single top_score is recorded here. This is a single preprint's pilot evaluation on
    one disease domain (neurodegenerative disease), not an independently maintained leaderboard, and
    no updated public tracking of frontier-model CARDBiomedBench scores was found for this page.
contamination:
  risk: medium
  note: >
    The full dataset, including gold answers in both splits, has been publicly downloadable on
    Hugging Face since around the paper's January 2025 posting, so a model trained since then could
    plausibly have seen it. No publisher statement or independent community study demonstrating
    actual contamination was found, so this page does not go beyond "medium."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "cardbiomedbench (CARDBiomedBench_llmjudge_gen_99a231.py, CARDBiomedBench_llmjudge_rawprompt_gen_b4d90c.py)"
  bigbench: ""
  other: ""
tags:
  - domain
  - biomedical
  - healthcare
  - question-answering
  - llm-judge
  - safety
sources:
  - url: "https://www.biorxiv.org/content/10.1101/2025.01.15.633272v1"
    title: "CARDBiomedBench: A Benchmark for Evaluating Large Language Model Performance in Biomedical Research (Bianchi et al., bioRxiv 2025.01.15.633272)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/NIH-CARD/CARDBiomedBench"
    title: "NIH-CARD/CARDBiomedBench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://github.com/NIH-CARD/CARDBiomedBench"
    title: "NIH-CARD/CARDBiomedBench GitHub repository"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CARDBiomedBench/CARDBiomedBench_llmjudge_gen_99a231.py"
    title: "OpenCompass CARDBiomedBench_llmjudge_gen_99a231.py (evaluation config)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CARDBiomedBench tests whether a model can answer complex biomedical-research questions that require integrating genetic, molecular and clinical knowledge, rather than simple fact lookup. Its pilot implementation focuses on neurodegenerative diseases, a domain the authors picked because answering well requires combining several specialised kinds of evidence at once. Items combine expert-annotated question-answer pairs with semi-automated, template-based augmentation drawn from authoritative public resources: drug-development data, genome-wide association studies, and summary-data-based Mendelian randomisation analyses.

Every item carries one or more of ten biological-category tags (such as "Drug Disease Relations" or "Drug Gene Relations") and one or more of nine reasoning-skill tags (such as "Multi-Filter" or "Join," names that echo the database-query templates behind the augmented items), so results can be broken down by both subject matter and reasoning type rather than read as one lump score. It is a single-turn, English-only, text-only, open-ended question-answering task with no multiple-choice options.

## How it is scored

A model's free-text answer is graded against a reference answer by a separate LLM judge rather than by exact string match, since correct biomedical phrasing varies. The paper's own framework goes further than plain correctness: it reports a Response Quality Rate and a separate Safety Rate for each model, evaluated across seven private and open-source LLMs on the ten biological categories and nine reasoning skills. Two results the paper highlights illustrate different failure modes rather than a simple ranking: Claude-3.5-Sonnet scored a Response Quality Rate of 25% with a Safety Rate of 76%, which the authors read as excessive caution, while ChatGPT-4o scored a Response Quality Rate of 37% with a Safety Rate of only 31%, which they read as both inaccurate and unsafe. OpenCompass's own integration simplifies this to a single binary CORRECT/INCORRECT judgement per item through a generic LLM-judge rubric, collapsing the paper's two-axis quality/safety framework into one accuracy-like number -- a real scoring difference to check for when comparing a reported number to the paper's own figures.

## Dataset and licence

The dataset totals 68,227 question-answer pairs, split 58,079 train and 10,148 test, confirmed directly against the live Hugging Face parquet files (the paper's abstract rounds this to "over 68,000"). The Hugging Face dataset card states an OpenRAIL++ licence, an unusual choice for a text question-answering dataset -- OpenRAIL licences are more commonly attached to model weights -- and no separate data licence statement was found in the paper itself. Both splits carry public gold answers; there is no held-out portion.

## Who publishes it

CARDBiomedBench comes from the NIH Center for Alzheimer's and Related Dementias (CARD), part of the National Institute on Aging within the National Institutes of Health, with co-authors from DataTecnica LLC, the Department of Computer Science at Johns Hopkins University, and NIA's Laboratory of Neurogenetics. The paper, led by Owen Bianchi and Faraz Faghri among 24 total authors, was posted to bioRxiv (not arXiv) in January 2025 and had not been confirmed as peer-reviewed and published in a journal as of this page's research date. The reference dataset and code are maintained on GitHub under the `NIH-CARD` organisation.

## Lineage

CARDBiomedBench has no predecessor or successor tracked in this repository, and shares no relationship with `medqa`, `medmcqa` or `pubmedqa` beyond the broad category of medical/biomedical question answering: those three test clinical licensing-exam recall, postgraduate entrance-exam recall, and PubMed-abstract reading comprehension respectively, all as closed-form (multiple-choice or yes/no/maybe) tasks, while CARDBiomedBench is open-ended, judge-graded, and scoped specifically to biomedical *research* knowledge (genetics, drug-gene relations, GWAS and SMR findings) in one disease domain rather than clinical practice or literature comprehension generally. The authors describe neurodegenerative disease as a pilot domain and state that future iterations will extend to other biomedical areas; no such extension had its own id or page in this repository as of this page's research date.

## Saturation and contamination

Both headline results the paper reports sit well below the 100% ceiling on Response Quality Rate, and the paper frames them as illustrating different failure modes -- excessive caution versus inaccurate-and-unsafe -- rather than naming a top performer, so no single top score is recorded on this page. This is a single preprint's pilot evaluation of seven models in one disease domain, not an independently maintained leaderboard, and no updated public tracking of frontier-model scores was found.

Contamination risk sits at medium: the full dataset, gold answers included in both splits, has been downloadable on Hugging Face since around the paper's January 2025 posting date, so a model trained since then could plausibly have seen it, though no publisher statement or independent study demonstrating actual leakage was found.

## How to run it

The reference implementation lives in the `NIH-CARD/CARDBiomedBench` GitHub repository and Hugging Face dataset. OpenCompass integrates it as the `cardbiomedbench` dataset, evaluated zero-shot with a generic LLM-judge grader. Note that OpenCompass's reader configuration expects columns named `Bio_Category`, `SQL_Category` and `expert`, none of which match the current public Hugging Face schema (`bio_category`, `reasoning_category`, with no `expert` field at all) -- a mismatch this page could not resolve from the sources read, and one to check before trusting an out-of-the-box OpenCompass run against the current public dataset. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found.

## Reading the numbers

A high CARDBiomedBench score suggests a model can synthesise genetic, molecular and clinical evidence about neurodegenerative disease into an answer that a judge model finds both correct and appropriately hedged -- not simply confident. The paper's own results show quality and safety can move independently: a cautious model can score low on quality while scoring high on safety, and a fluent-sounding model can score the reverse, so a single blended accuracy number (as OpenCompass's integration produces) hides which failure mode is present. Because the benchmark's pilot domain is neurodegenerative disease specifically, a strong score should not be read as evidence of broad biomedical-research competence without checking whether later, broader-domain iterations exist. Treat any reported number cautiously given the benchmark's own preprint status and the schema mismatch noted above.
