---
id: live_qa
name: "LiveQA (TREC-2017 Medical Task)"
aliases:
  - "TREC-2017 LiveQA: Medical Question Answering Task"
  - "LiveQA'17 Medical"
page_kind: benchmark
category: domain
subcategory: "consumer health / medical question answering, free-form generation graded by an LLM judge against reference answers"
status: unknown
summary: 104 real, historical (2017) consumer health questions from the TREC LiveQA medical track; despite the "live" name this is a static, fixed test set, not a continuously refreshed one.
measures: >
  Despite what "live" suggests, live_qa is not a continuously refreshed dataset -- it is HELM's
  implementation of a single, fixed historical benchmark: the TREC-2017 LiveQA Medical Task, a
  one-time consumer-health question-answering track organised with the U.S. National Library of
  Medicine (NLM). The name describes the provenance of the questions, not the freshness of the
  benchmark: the underlying questions are genuinely live in the sense that they were real,
  real-time queries submitted by members of the public to NLM's consumer health inquiry service,
  rather than written specifically for the benchmark. Once the TREC 2017 track concluded, the
  organisers released a fixed 104-question test set (alongside a separately released, larger
  training set) with reference answers vetted by medical experts, and that fixed archive is
  exactly what HELM's live_qa scenario downloads and evaluates against today -- it has not been
  expanded, refreshed, or replaced with newer questions since.
task_format: >
  A real consumer health question (for example, "What is the relationship between Noonan syndrome
  and polycystic renal disease?") in; a free-form generated answer out, produced zero-shot with no
  in-context examples.
metric:
  name: "LLM-as-judge score (0, 0.3, 0.7 or 1 per response, averaged across the test set as live_qa_score), plus HELM's standard open-ended-generation reference metrics"
  direction: higher_is_better
  unit: "points"
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random or human baseline is defined for this free-response medical QA task. HELM grades
    each response with a GPT-4o judge (model id "openai/gpt-4o-2024-05-13" in the version of the
    code read for this page) that scores a response 1 if it fully matches a correct reference's
    content and intent, 0.7 if correct but incomplete, 0.3 if partially correct or incorrect, or 0
    if unrelated or wrong, against the question's reference answer(s).
dataset:
  size: 104
  size_note: >
    104 test questions, confirmed by counting qid and NLM-Summary entries directly in the XML file
    HELM downloads, each carrying one or more expert-vetted reference answers (167 ANSWER entries
    total across the 104 questions, roughly 1.6 per question on average). A separate, larger
    634-question-answer-pair training set (388 pairs across 200 questions, plus 246 pairs across a
    further 246 questions) was released in the same repository, but HELM's adapter spec sets
    max_train_instances=0, so every evaluation is zero-shot against the 104-question test file
    only; the training data goes unused.
  url: "https://github.com/abachaa/LiveQA_MedicalTask_TREC2017"
  license: "CC BY 4.0, per the GitHub repository."
  languages:
    - en
  modalities:
    - text
  splits: "one fixed test file (104 questions); a separate 634-pair training set exists in the same repository but is not used by HELM's zero-shot evaluation"
  public_test_set: true
publisher:
  org: "U.S. National Library of Medicine (NLM); Emory University; TREC (Text REtrieval Conference)"
  authors:
    - "Asma Ben Abacha"
    - "Eugene Agichtein"
    - "Yuval Pinter"
    - "Dina Demner-Fushman"
  url: "https://github.com/abachaa/LiveQA_MedicalTask_TREC2017"
paper:
  title: "Overview of the Medical Question Answering Task at TREC 2017 LiveQA"
  arxiv: ""
  url: "https://trec.nist.gov/pubs/trec26/papers/Overview-QA.pdf"
  year: 2017
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm"
released: "2017"
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
    No published, dated leaderboard results for this specific HELM scenario were found during this
    research; it did not appear in either HELM Classic's or MedHELM's current published scenario
    lists at the URLs checked, though the scenario, annotator and metric code are present and
    appear actively maintained in the current HELM codebase (the configured judge model is
    GPT-4o-2024-05-13, a mid-2024 model). Saturation is therefore not established here rather than
    assumed from general model progress.
contamination:
  risk: high
  note: >
    This is the opposite of what the "live" name might suggest. The benchmark is not continuously
    refreshed: it is a single, fixed archive from a one-time 2017 TREC track, and both the 104 test
    questions and their expert-vetted reference answers have been hosted publicly on GitHub,
    ungated, since shortly after the track concluded -- roughly nine years by this research date.
    The genuinely "live" part of LiveQA is the original provenance of the questions (real,
    real-time consumer queries to a public health information service), not any ongoing refresh of
    the benchmark itself; once compiled, the test set has not changed.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "live_qa"
  opencompass: ""
  bigbench: ""
  other: >
    HELM's run spec (get_live_qa_spec) evaluates the scenario zero-shot (max_train_instances=0,
    max_tokens=512) with the instruction "Please answer the following consumer health question,"
    and scores each response with both HELM's standard open-ended-generation metrics and the
    dedicated LiveQAScoreMetric / LiveQAAnnotator LLM-judge pipeline.
tags:
  - domain
  - medical
  - question-answering
  - llm-judge
  - consumer-health
  - static-despite-name
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/live_qa_scenario.py"
    title: "live_qa_scenario.py: LiveQAScenario definition, source XML location, citation"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/live_qa_annotator.py"
    title: "live_qa_annotator.py: LLM-as-judge grading prompt and logic (GPT-4o)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/live_qa_metrics.py"
    title: "live_qa_metrics.py: LiveQAScoreMetric definition"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/classic_run_specs.py"
    title: "HELM classic_run_specs.py: get_live_qa_spec (adapter, metrics, groups)"
    accessed: "2026-09-08"
  - url: "https://github.com/abachaa/LiveQA_MedicalTask_TREC2017"
    title: "abachaa/LiveQA_MedicalTask_TREC2017 GitHub repository (dataset provenance, licence, citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/abachaa/LiveQA_MedicalTask_TREC2017/master/TestDataset/TREC-2017-LiveQA-Medical-Test-Questions-w-summaries.xml"
    title: "TREC-2017 LiveQA Medical test-question XML file (as downloaded by HELM)"
    accessed: "2026-09-08"
  - url: "https://trec.nist.gov/pubs/trec26/papers/Overview-QA.pdf"
    title: "Overview of the Medical Question Answering Task at TREC 2017 LiveQA (Ben Abacha et al.; PDF text could not be extracted during this research, cited for bibliographic reference only)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Despite what "live" suggests, live_qa is not a continuously refreshed dataset -- it is HELM's implementation of a single, fixed historical benchmark: the TREC-2017 LiveQA Medical Task, a one-time consumer-health question-answering track organised with the U.S. National Library of Medicine (NLM). The name describes the provenance of the questions, not the freshness of the benchmark: the underlying questions are genuinely live in the sense that they were real, real-time queries submitted by members of the public to NLM's consumer health inquiry service, rather than written specifically for the benchmark. Once the TREC 2017 track concluded, the organisers released a fixed 104-question test set (alongside a separately released, larger training set) with reference answers vetted by medical experts, and that fixed archive is exactly what HELM's live_qa scenario downloads and evaluates against today -- it has not been expanded, refreshed, or replaced with newer questions since.

## How it is scored

HELM evaluates every question zero-shot (no in-context examples), prompting the model with "Please answer the following consumer health question" and generating up to 512 tokens. Each response is then graded by a GPT-4o judge (the model id recorded in the code read for this page is `openai/gpt-4o-2024-05-13`) that compares the response against the question's reference answer(s) and scores it 1 if it fully matches a correct reference's content and intent, 0.7 if it is correct but incomplete, 0.3 if it is partially correct or incorrect, or 0 if it is unrelated or wrong; these per-question scores average into `live_qa_score`. HELM also computes its standard open-ended-generation reference metrics alongside the judge score, though the LLM-judge score is the scenario's distinguishing metric, added specifically because free-form medical answers are hard to grade against short reference strings with n-gram overlap alone.

## Dataset and licence

The test set holds 104 questions, confirmed by counting qid and NLM-Summary entries directly in the XML file HELM downloads, each carrying one or more expert-vetted reference answers -- 167 ANSWER entries in total, roughly 1.6 per question on average, several with a source URL and a reviewer comment explaining why the answer is considered relevant. A separate, larger 634-question-answer-pair training set (388 pairs across 200 questions, plus 246 pairs across a further 246 questions) was released in the same repository, but HELM's adapter spec sets max_train_instances=0, so every evaluation is zero-shot against the 104-question test file only; the training data goes unused. The data is released under a CC BY 4.0 licence, per the GitHub repository (abachaa/LiveQA_MedicalTask_TREC2017), which mirrors the original TREC release.

## Who publishes it

The TREC-2017 LiveQA Medical Task was organised by Asma Ben Abacha, Eugene Agichtein, Yuval Pinter and Dina Demner-Fushman, described in "Overview of the Medical Question Answering Task at TREC 2017 LiveQA," presented at TREC 2017 in cooperation with the U.S. National Library of Medicine. The GitHub mirror HELM downloads from is maintained under the original organisers' account. Stanford CRFM's HELM project subsequently wrapped this fixed dataset in the `live_qa` scenario, adapter and LLM-judge grading pipeline documented on this page; HELM did not create the underlying question-and-answer data itself.

## Lineage

The paper's own title situates this task inside a broader "TREC 2017 LiveQA" effort, of which the medical question-answering task is one part; this page's sources establish the medical task's own construction in detail but did not confirm the scope or years of TREC's wider, non-medical LiveQA activity, so that broader lineage is left unstated rather than guessed. Within this repository, live_qa has no predecessor or successor benchmark tracked, and no other TREC-derived medical QA benchmark currently has its own page here. It is unrelated to this repository's other medical domain benchmarks (kormedmcqa, medqa) beyond sharing the general "medical question answering" label -- live_qa is graded by an LLM judge against free-form reference answers rather than by multiple-choice accuracy.

## Saturation and contamination

No published, dated leaderboard results for this specific HELM scenario were found during this research; it did not appear in either HELM Classic's or MedHELM's current published scenario lists at the URLs checked, though the scenario, annotator and metric code are present and appear actively maintained in the current HELM codebase (the configured judge model is GPT-4o-2024-05-13, a mid-2024 model). Saturation is therefore not established here rather than assumed from general model progress.

Contamination risk is high -- the opposite of what the "live" name might suggest. The benchmark is not continuously refreshed: it is a single, fixed archive from a one-time 2017 TREC track, and both the 104 test questions and their expert-vetted reference answers have been hosted publicly on GitHub, ungated, since shortly after the track concluded -- roughly nine years by this research date. The genuinely "live" part of LiveQA is the original provenance of the questions (real, real-time consumer queries to a public health information service), not any ongoing refresh of the benchmark itself; once compiled, the test set has not changed.

## How to run it

HELM implements the benchmark as the `live_qa` run spec (`get_live_qa_spec`), which wires together `LiveQAScenario` (downloads and parses the fixed XML test file), a zero-shot generation adapter, HELM's standard open-ended-generation metrics, and the dedicated `LiveQAAnnotator` plus `LiveQAScoreMetric` for LLM-judge scoring. No lm-evaluation-harness, inspect_evals, OpenCompass or BIG-bench implementation was found during this research. Because the headline score depends on a specific judge model (GPT-4o-2024-05-13 in the version of the code read for this page), a live_qa score computed with a different or newer judge model is not guaranteed to be directly comparable to one computed with this default.

## Reading the numbers

A high live_qa score is evidence a model can generate medically accurate, complete free-form answers to genuine consumer health questions, as judged against expert-vetted reference answers -- a more realistic and harder task than selecting among multiple-choice options, but one whose grade depends on an LLM judge rather than an objective string match. Because the judge model itself can have blind spots or biases, and because this page could not confirm live_qa appears on any current, actively maintained public leaderboard, treat a reported score cautiously and check which judge model produced it before comparing it to another report. Most importantly, do not read the "live" in the name as a claim about dataset freshness: this is a fixed, nearly decade-old public test set, and a very high score could reflect memorized reference answers rather than genuine medical reasoning.
