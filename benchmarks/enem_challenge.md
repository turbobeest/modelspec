---
id: enem_challenge
name: "ENEM Challenge"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "Brazilian national secondary-school exam multiple-choice QA (Portuguese)"
status: active
summary: "1,432 multiple-choice questions from Brazil's national secondary-school exam (ENEM), spanning 2009-2017 and 2022-2023, across humanities, languages, sciences and mathematics."
measures: >
  ENEM Challenge tests a model on real questions from the Exame Nacional do Ensino Medio (ENEM), the
  Brazilian government's high-school-level exam used nationwide as a university-admission gateway.
  Questions span four broad areas -- Humanities, Languages, Sciences (natural sciences and mathematics
  together, per the exam's own structure) -- and are written in Portuguese for Brazilian secondary-school
  graduates, so answering them draws on general academic knowledge and Portuguese reading comprehension
  together, not one narrow skill. The dataset compiled for this benchmark spans exam sittings from 2009
  through 2023, though not every intervening year is present.
task_format: >
  Multiple-choice question with five labelled options (A-E), single correct answer, in Portuguese;
  HELM's implementation drops any question the source data marks as officially annulled ("ANULADO") and
  scores the model's chosen option by exact match against the correct text.
metric:
  name: exact_match (accuracy)
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 20.0
  human_baseline: null
  baseline_note: >
    Every scored item has exactly five options, so naive random guessing scores 20%. No human baseline
    (such as the real national average ENEM score) is attached to this dataset by its source; ENEM's own
    real-world pass/percentile statistics are a separate, external reference this page did not pull in.
dataset:
  size: 1432
  size_note: >
    1,432 questions, confirmed directly from the Hugging Face dataset's own row count. The exam-year
    breakdown (read from the dataset's own `exam_year` field) covers 2009 through 2017 and separately
    2022 and 2023 -- eleven distinct years in total, with 2018 through 2021 absent from this particular
    compilation for a reason this page could not confirm. Per-year counts otherwise run roughly 108-136
    questions, except 2016, which has 244 -- roughly double a typical year -- a discrepancy this page
    also could not explain from the sources reviewed. Each question carries five answer choices (A-E).
  url: "https://huggingface.co/datasets/eduagarcia/enem_challenge"
  license: "Not established -- the Hugging Face dataset card sets no licence tag and its README body contains no licence statement beyond the dataset's structural (YAML) metadata."
  languages:
    - pt
  modalities:
    - text
  splits: "single `train`-named split (1,432 rows) on the source Hugging Face dataset; HELM's own scenario treats every one of these rows as its TEST_SPLIT regardless of the upstream split name, since no separate held-out test file is provided"
  public_test_set: true
publisher:
  org: ""
  authors:
    - "Eduardo A. S. Garcia"
  url: "https://huggingface.co/datasets/eduagarcia/enem_challenge"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://huggingface.co/spaces/eduagarcia/open_pt_llm_leaderboard"
repo_url: "https://huggingface.co/datasets/eduagarcia/enem_challenge"
released: "2024"
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
    No dated, per-model ENEM Challenge score was confirmed from a source opened for this page. The
    dataset's other major public consumer, the Open Portuguese LLM Leaderboard, is explicitly labelled
    "(Archived)" on its own Hugging Face Space page, and its live results table did not render in this
    page's fetch of that Space; HELM's own scenario code and metadata carry no reported score either.
    This page therefore leaves saturation status unknown rather than guessing from memory.
contamination:
  risk: high
  note: >
    ENEM is a real, government-administered exam whose official questions and answer keys are published
    by Brazil's Ministry of Education shortly after each yearly sitting and have circulated on the
    Portuguese-language web for years -- the oldest exam year in this compilation dates to 2009. No
    held-out portion, canary string, or refresh mechanism was found for this specific dataset, so a
    model trained on a broad Portuguese-language or general web crawl has a real chance of having seen
    this exact question-and-answer text.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "enem_challenge"
  opencompass: ""
  bigbench: ""
  other: >
    Not present in the upstream EleutherAI/lm-evaluation-harness task list (confirmed by directory
    listing) or in OpenCompass's dataset configs. The Open Portuguese LLM Leaderboard runs its own
    evaluations through a separate fork, eduagarcia/lm-evaluation-harness-pt, which this page did not
    inspect in detail.
tags:
  - portuguese
  - brazil
  - knowledge
  - multiple-choice
  - exam-qa
  - national-exam
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/enem_challenge_scenario.py"
    title: "HELM ENEMChallengeScenario source"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enem_challenge_specs.py"
    title: "HELM enem_challenge run spec (adapter, Portuguese instructions, exact-match metric)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/eduagarcia/enem_challenge"
    title: "eduagarcia/enem_challenge dataset metadata, Hugging Face API (no licence tag; last modified 2024-01-30)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/eduagarcia/enem_challenge/raw/main/README.md"
    title: "eduagarcia/enem_challenge dataset card (structural YAML only; no prose body or citation found)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/statistics?dataset=eduagarcia%2Fenem_challenge&config=default&split=train"
    title: "eduagarcia/enem_challenge column statistics, Hugging Face datasets-server (exam_year distribution, nullified column all-NaN)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/eduagarcia/open_pt_llm_leaderboard"
    title: "Open Portuguese LLM Leaderboard (Archived), Hugging Face Space -- About/citation text, including the ENEM-Challenge bibtex entry (Silveira & Malua, BRACIS 2017), fetched via Firecrawl"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ENEM Challenge tests a model on real questions from the Exame Nacional do Ensino Medio (ENEM), the
Brazilian government's national high-school-level exam, used nationwide as a gateway to university
admission. Questions are written in Portuguese and span the exam's broad subject groups -- Humanities,
Languages, and Sciences (natural sciences and mathematics) -- so correctly answering them requires
Portuguese reading comprehension together with general secondary-school academic knowledge, rather than
any single narrow skill. The compiled dataset spans exam sittings from 2009 through 2023, though not
every year in that range is represented.

## How it is scored

Each question offers five labelled options (A-E) with one correct answer, so random guessing scores
20%. HELM's implementation excludes any question the source data marks as officially annulled
("ANULADO" -- a status ENEM itself sometimes assigns to flawed or disputed questions after the fact) and
scores the model's selected option by exact match against the correct answer text.

## Dataset and licence

1,432 questions in total, confirmed directly from the source Hugging Face dataset's row count. Reading
the dataset's own `exam_year` field shows coverage of 2009 through 2017 plus 2022 and 2023 -- eleven
distinct years -- with 2018 through 2021 absent from this particular compilation for a reason this page
could not confirm from the sources reviewed. Most years contribute roughly 108-136 questions each,
except 2016, which contributes 244, about double a typical year; this page could not explain that
discrepancy either. No licence tag or licence statement was found on the dataset card, so licence is
recorded as not established.

## Who publishes it

The `eduagarcia/enem_challenge` dataset that both HELM and the Open Portuguese LLM Leaderboard load from
is attributed to Eduardo A. S. Garcia on Hugging Face. The Open Portuguese LLM Leaderboard's own citation
list -- itself maintained by Garcia -- separately credits a specific academic source for the idea of
using ENEM as an AI benchmark: Igor Cataneo Silveira and Denis Deratani Malua, "University Entrance Exam
as a Guiding Test for Artificial Intelligence," presented at BRACIS 2017. This page did not open that
2017 paper directly (only its citation, as reproduced on the leaderboard page), and the specific
1,432-item, eleven-year compilation used here is presumably a later, larger curation than whatever
dataset the 2017 paper itself originally used.

## Lineage

ENEM Challenge has no predecessor or successor benchmark, and no variant page, in this repository. The
same leaderboard citation list that names its likely originating paper also cites several related but
distinct Brazilian-exam benchmarks with no page here yet: BLUEX (Almeida et al., 2023, arXiv:2307.05410),
covering entrance exams from other leading Brazilian universities rather than ENEM specifically; a
GPT-4-vision-focused study of Brazilian admission exams (Pires et al., 2023, arXiv:2311.14169); and a
Brazilian bar-exam (OAB) benchmark (Rademaker, 2017). None of these should be treated as a variant of
ENEM Challenge -- each covers a different exam or a different research question -- but a reader
assembling a fuller picture of Brazilian-exam LLM evaluation should be aware they exist.

## Saturation and contamination

No dated, per-model ENEM Challenge score was confirmed from a source opened for this page. The Open
Portuguese LLM Leaderboard, the dataset's other major public consumer, is explicitly marked
"(Archived)" on its own Hugging Face Space, and its results table did not render in this page's fetch
of that Space, so this page leaves saturation status unknown rather than estimate one from memory.
Contamination risk is assessed as high: ENEM is a real government exam whose official questions and
answers are published shortly after each yearly sitting and have been circulating publicly for years --
the oldest year in this dataset is 2009 -- with no held-out portion or canary mechanism found.

## How to run it

HELM implements it as the single `enem_challenge` scenario (no language or subject parameterisation),
downloading `eduagarcia/enem_challenge` directly, prompting in Portuguese with a fixed instruction and
worked example, and scoring by exact match. It is not present in the upstream EleutherAI
lm-evaluation-harness task list or in OpenCompass's dataset configs; the Open Portuguese LLM Leaderboard
instead runs its own evaluations through a separate fork of lm-evaluation-harness
(`eduagarcia/lm-evaluation-harness-pt`), which this page did not inspect in detail, so a score from that
leaderboard may not use exactly the same prompting or scoring code as HELM's.

## Reading the numbers

A high ENEM Challenge score indicates a model can read and reason through the kind of general-academic,
Portuguese-language question a Brazilian secondary-school graduate is expected to handle -- broad
subject knowledge and reading comprehension together, rather than a specialised skill. Because the
dataset skips several exam years (2018-2021) and one included year (2016) is roughly double the size of
the others for reasons this page could not confirm, an aggregate score may not weight all covered years
evenly; check the per-year breakdown if that matters for a given comparison. Given the high plausibility
of pretraining exposure to real, long-public exam text, and the absence of any confirmed current
leaderboard, treat a reported ENEM Challenge number as a rough capability signal rather than a precise,
independently verified ranking.
