---
id: medcalc_bench
name: MedCalc-Bench
aliases:
  - MedCalc_Bench
page_kind: benchmark
category: domain
subcategory: clinical/medical calculation
status: active
summary: >-
  Tests whether a model can compute clinical values (dosages, risk scores, dates) from a patient note
  the way a bedside medical calculator would, graded by exact match or numeric tolerance.
measures: >
  MedCalc-Bench gives a model a patient note and a question naming a specific clinical calculation —
  a creatinine clearance, a Glasgow Coma Score, a gestational age, a drug dosage — and asks it to extract
  the relevant values from the note, apply the correct formula or clinical rule, and produce the answer a
  bedside calculator would give. This targets a narrower, more mechanical skill than open-ended medical
  question answering: correctly identifying which numbers in a note matter, and computing with them
  correctly, rather than recalling medical facts in prose.
task_format: >
  Given a patient note (drawn from case reports or clinical vignettes) and a question naming one of 55
  calculators, the model must extract relevant entities and output a numeric or categorical answer with
  its computation shown.
metric:
  name: "accuracy (exact match for rule-based and date calculators; within 5% tolerance for equation-based lab/physical/dosage calculators)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Answers are open numeric or categorical values rather than multiple choice, so no random-guess
    baseline applies. Rule-based calculators (risk scores, severity, diagnosis rules) and date
    calculations require an exact match; equation-based lab, physical and dosage calculators are scored
    correct within 5% of the ground-truth value. No formal human-clinician baseline was found published
    by the authors.
dataset:
  size: 11643
  size_note: >
    10,543 training instances plus 1,100 test instances in the current ncbi/MedCalc-Bench release on
    Hugging Face. The paper's own headline figure is "1,047 manually reviewed" instances for the
    evaluation set specifically — close to, but not identical to, the 1,100-row test split now published;
    this page reports both numbers rather than resolve the small discrepancy, which most likely reflects
    revisions made across the v1.0/v1.1/v1.2 updates (see licence note). Instances span 55 distinct
    calculators: 36 equation-based (19 lab, 12 physical, 3 date, 2 dosage) and 19 rule-based (12 risk, 4
    severity, 3 diagnosis).
  url: https://huggingface.co/datasets/ncbi/MedCalc-Bench
  license: CC-BY-SA-4.0
  languages:
    - en
  modalities:
    - text
  splits: "10,543 train / 1,100 test (current release)"
  public_test_set: true
publisher:
  org: ""
  authors:
    - Nikhil Khandekar
    - Qiao Jin
    - Guangzhi Xiong
    - Soren Dunn
    - Serina S. Applebaum
    - Zain Anwar
    - Maame Sarfo-Gyamfi
    - Conrad W. Safranek
    - Abid A. Anwar
    - Andrew Zhang
    - Aidan Gilson
    - Maxwell B. Singer
    - Amisha Dave
    - Andrew Taylor
    - Aidong Zhang
    - Qingyu Chen
    - Zhiyong Lu
  url: https://github.com/ncbi-nlp/MedCalc-Bench
paper:
  title: "MedCalc-Bench: Evaluating Large Language Models for Medical Calculations"
  arxiv: "2406.12036"
  url: https://arxiv.org/abs/2406.12036
  year: 2024
leaderboard_url: ""
repo_url: https://github.com/ncbi-nlp/MedCalc-Bench
released: "2024-06"
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
    No leaderboard tracking current model scores on MedCalc-Bench was found; HELM and OpenCompass both
    implement it as one scenario among many rather than running a dedicated public leaderboard for it.
    Not established, rather than guessed.
contamination:
  risk: medium
  note: >
    The dataset has been public since June 2024 and is now on its third public revision (v1.0 through
    v1.2, plus a further author-maintained "Verified" continuation), so later training runs could
    plausibly include some of these patient notes and answers. Patient notes are drawn from public PubMed
    Central case reports and de-identified vignettes rather than real clinical records, which limits
    privacy risk but does not limit contamination risk, since PubMed Central text itself is common
    pretraining material.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: medcalc_bench
  opencompass: MedCalc_Bench
  bigbench: ""
  other: >
    HELM's MedCalcBenchScenario reads from the ncbi/MedCalc-Bench Hugging Face dataset and scores with a
    medcalc_bench_accuracy metric. OpenCompass configures it under
    opencompass/configs/datasets/MedCalc_Bench (MedCalcBench_official_gen_a5155f.py). No
    lm-evaluation-harness or inspect_evals implementation was found.
tags:
  - medical
  - clinical
  - calculator
  - domain-specific
  - numeric-reasoning
sources:
  - url: https://arxiv.org/abs/2406.12036
    title: "MedCalc-Bench: Evaluating Large Language Models for Medical Calculations"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/ncbi-nlp/MedCalc-Bench/main/README.md
    title: "ncbi-nlp/MedCalc-Bench README (licence, version history, MedCalc-Bench Verified pointer)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ncbi/MedCalc-Bench
    title: "ncbi/MedCalc-Bench dataset card and structure (10,543 train / 1,100 test, cc-by-sa-4.0)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/ncbi/MedCalc-Bench-v1.0
    title: "ncbi/MedCalc-Bench-v1.0 dataset card (kept for reproducibility; cc-by-4.0)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/medcalc_bench_scenario.py
    title: "HELM medcalc_bench_scenario.py (MedCalcBenchScenario)"
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/MedCalc_Bench
    title: "OpenCompass MedCalc_Bench dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MedCalc-Bench gives a model a patient note and a question naming a specific clinical calculation — a
creatinine clearance, a Glasgow Coma Score, a gestational age, a drug dosage adjustment — and asks it to
extract the relevant values from the note, apply the correct formula or clinical rule, and produce the
answer a bedside medical calculator would give. This is a narrower, more mechanical skill than open-ended
medical question answering: correctly identifying which numbers in a note matter, and computing with them
correctly, rather than recalling medical facts in prose. Patient notes are English-language case reports
and clinical vignettes rather than free-text chat.

## How it is scored

Answers are open numeric or categorical values, not multiple choice. Rule-based calculators — risk
scores, severity assessments and diagnostic rules — and date calculations are graded by exact match.
Equation-based calculators drawing on lab values, physical measurements or dosage conversions are graded
correct if the model's answer falls within 5% of the ground-truth value, since these often involve
continuous quantities and legitimate rounding differences. Because the task mixes exact-match and
tolerance-based grading across 55 different calculators, an aggregate accuracy figure is a blend across
two different grading regimes rather than one uniform metric.

## Dataset and licence

The current Hugging Face release (ncbi/MedCalc-Bench) holds 10,543 training instances and 1,100 test
instances across 55 distinct calculators — 36 equation-based (19 lab, 12 physical, 3 date, 2 dosage) and
19 rule-based (12 risk, 4 severity, 3 diagnosis). The paper's own headline number is "1,047 manually
reviewed" instances for the evaluation set, close to but not identical to the 1,100-row test split now
published; both numbers are reported here rather than reconciled. Patient notes derive from publicly
available PubMed Central case reports and de-identified vignettes, with no real patient health
information. The dataset has been revised across public versions: v1.0 was released under a CC-BY-4.0
licence; v1.1, v1.2 and the current unversioned release carry CC-BY-SA-4.0 instead, and the v1.0 card
itself now says it is "kept for reproducibility purposes only."

## Who publishes it

MedCalc-Bench comes from a 17-author group led by Nikhil Khandekar and Qiao Jin, including Guangzhi
Xiong, Andrew Taylor, Aidong Zhang, Qingyu Chen and Zhiyong Lu among others, posted to arXiv in June 2024.
The reference dataset and code are maintained at github.com/ncbi-nlp/MedCalc-Bench, consistent with
Zhiyong Lu's and Qingyu Chen's affiliation with NIH's National Library of Medicine; the paper's stated
support came from the NIH Intramural Research Program. The original lead author continues to maintain a
further revision under a separate name (see Lineage).

## Lineage

MedCalc-Bench names no formal predecessor; the paper positions it against prior medical QA benchmarks that
focus on question answering rather than quantitative calculation. It has since been revised in place
through v1.0, v1.1 and v1.2 by the original repository, and lead author Nikhil Khandekar now maintains a
further continuation, "MedCalc-Bench Verified," in a separate GitHub repository and Hugging Face dataset,
described as fixing calculator implementations and improving entity matching. None of these revisions has
its own page in this repository yet; this page documents the benchmark as introduced in the June 2024
paper and its current default Hugging Face release.

## Saturation and contamination

No leaderboard tracking current model scores on MedCalc-Bench was found in this research — HELM and
OpenCompass both run it as one scenario inside a broader suite rather than maintaining a dedicated public
leaderboard for it, so this page records saturation status as unknown rather than guessing a top score.
Contamination risk sits at medium: the dataset has been public since June 2024 and is now on its third
public revision, so later training runs could plausibly include some of its patient notes and answers;
the notes themselves draw on public PubMed Central text, which is common pretraining material even though
it carries no real patient data.

## How to run it

HELM's `MedCalcBenchScenario` reads directly from the ncbi/MedCalc-Bench Hugging Face dataset and scores
with a `medcalc_bench_accuracy` metric. OpenCompass configures the same benchmark under its `MedCalc_Bench`
dataset folder. Neither an lm-evaluation-harness nor an inspect_evals implementation was found. Because
the benchmark mixes exact-match and 5%-tolerance grading across calculator types, confirm which
calculators a reported aggregate score actually covers before comparing it against another source.

## Reading the numbers

A high MedCalc-Bench score shows a model can reliably extract the right numbers from a clinical note and
apply the correct formula or rule for a known calculator — a narrow, checkable skill relevant to
clinical-decision-support tooling. It does not show the model can handle calculators outside the 55
covered here, notice when a note lacks the information a calculation needs, or safely flag uncertainty,
none of which this benchmark's exact-match and tolerance grading directly tests. Because no active
leaderboard was found, treat any specific score you encounter as coming from whoever ran the evaluation,
and check their harness and calculator coverage before comparing it with another model's number.
