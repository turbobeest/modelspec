---
id: mtsamples_replicate
name: "MTSamples Replicate (MedHELM)"
aliases:
  - "MTSamples"
  - "mtsamples_processed"
page_kind: benchmark
category: domain
subcategory: "treatment-plan generation from mixed-specialty transcribed clinical reports"
status: active
summary: "MedHELM wrap of mixed-specialty MTSamples notes: generate a treatment plan from a clinical transcription, scored by an LLM jury plus overlap metrics."
measures: >
  This id is HELM's mtsamples_replicate scenario in MedHELM, not the surgical-only
  mtsamples_procedures wrap and not a third-party MTSamples leaderboard. Each item
  is an English transcribed report from MTSamples.com, stored as
  mtsamples_processed on raulista1997/benchmarkdata. HELM prefers a PLAN section
  as the reference, else SUMMARY, else FINDINGS, and removes only PLAN from the
  prompt. MedHELM places the task in clinical decision support / planning
  treatments. Display name on the schema is MTSamples.
task_format: >
  Zero-shot generation. HELM instructions: "Given various information about a
  patient, return a reasonable treatment plan for the patient." No input noun.
  Output noun Answer. max_train_instances=0, max_tokens=512.
metric:
  name: "mtsamples_replicate_accuracy (HELM LLM-jury average of accuracy, completeness, clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_medhelm.yaml display name is MTSamples Replicate Jury Score. HELM also
    attaches summarization metrics (BERTScore, distilbert-base-uncased). Default
    jury: GPT-4o, Llama 3.3 70B Instruct, Claude 3.7 Sonnet. LLMJuryMetric mean of
    1-5 axis scores; default_score 1.0 if a judge fails. No published clinician
    baseline for this scenario. Not comparable to exact-match medical QA.
dataset:
  size: null
  size_note: >
    At HELM pin ebc104a4f96c5b7602242f301e081e9934a23344 the Git tree has 1,269
    .txt files under mtsamples_processed. HELM skips files with none of PLAN,
    SUMMARY or FINDINGS, so scored n is at most 1,269 and was not counted here.
    A sampled Angina note uses a TREATMENT header rather than PLAN, which this
    extractor would miss. The live MTSamples.com homepage (2026-09-08) advertises
    5,043 samples in 40 specialties; HELM uses a processed GitHub subset, not
    that full catalogue. MedHELM lists the benchmark as public and reformulated.
    No SPDX licence in HELM or the data README. The site allows educational
    print/share with credit and says samples are user-contributed and not
    guaranteed complete.
  url: "https://github.com/raulista1997/benchmarkdata/tree/ebc104a4f96c5b7602242f301e081e9934a23344/mtsamples_processed"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM TEST_SPLIT only, from filtered GitHub .txt files"
  public_test_set: true
publisher:
  org: "Stanford CRFM / MedHELM; source notes from MTSamples.com, packaged by raulista1997/benchmarkdata"
  authors:
    - "Suhana Bedi"
    - "Hejie Cui"
    - "Miguel Fuentes"
    - "Alyssa Unell"
    - "Michael Wornow"
    - "Yifan Mai"
    - "Percy Liang"
    - "Nigam H. Shah"
  url: "https://crfm.stanford.edu/helm/medhelm/latest/"
paper:
  title: "Holistic evaluation of large language models for medical tasks with MedHELM"
  arxiv: "2505.23802"
  url: "https://www.nature.com/articles/s41591-025-04151-2"
  year: 2026
leaderboard_url: "https://crfm.stanford.edu/helm/medhelm/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mtsamples_replicate_scenario.py"
released: "2025"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - mtsamples_procedures
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    MedHELM overall win rates (DeepSeek R1 0.66, o3-mini 0.64 in the 2025 preprint)
    are suite-level, not this scenario. No mtsamples_replicate jury top score was
    copied from a rendered leaderboard.
contamination:
  risk: high
  note: >
    Mixed-specialty MTSamples pages and the GitHub mirror are public. Nature
    Medicine lists MTSamples among unrestricted public datasets. Reference PLAN
    text is in the same files.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "mtsamples_replicate"
  opencompass: ""
  bigbench: ""
  other: "MedHELM run spec mtsamples_replicate; main_metric mtsamples_replicate_accuracy, main_split test."
tags:
  - medical
  - treatment-planning
  - generation
  - helm
  - medhelm
  - llm-jury
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mtsamples_replicate_scenario.py"
    title: "HELM mtsamples_replicate_scenario.py (pin, PLAN-only strip, metadata)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/medhelm_run_specs.py"
    title: "HELM get_mtsamples_spec (replicate prompt, jury, BERTScore)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/static/schema_medhelm.yaml"
    title: "schema_medhelm.yaml (MTSamples Replicate Jury Score; clinical decision support)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/annotation/mtsamples_replicate_annotator.py"
    title: "MTSamplesReplicateAnnotator (treatment-plan 1-5 rubric)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/medhelm/judges.yaml"
    title: "MedHELM default jury models"
    accessed: "2026-09-08"
  - url: "https://github.com/raulista1997/benchmarkdata"
    title: "raulista1997/benchmarkdata (1,269 processed .txt at pin)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2505.23802"
    title: "MedHELM arXiv 2505.23802"
    accessed: "2026-09-08"
  - url: "https://www.nature.com/articles/s41591-025-04151-2"
    title: "Nature Medicine 2026 MedHELM article"
    accessed: "2026-09-08"
  - url: "https://www.mtsamples.com/"
    title: "MTSamples.com homepage (5,043 samples; educational-use credit request)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-013 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-013"
---

## What it measures

HELM `mtsamples_replicate` asks a model to write an English treatment plan from
a mixed-specialty transcribed report. Sources include clinic notes, consults
and some procedure write-ups from MTSamples.com. HELM hides the PLAN section
when it exists. If there is no PLAN, it still uses SUMMARY or FINDINGS as the
reference but leaves those sections in the prompt.

This is MedHELM's "MTSamples" decision-support task. It is not
[mtsamples_procedures](mtsamples_procedures.md), which is the operative-note
subset with a stricter strip of all three headers.

## How it is scored

Main metric `mtsamples_replicate_accuracy` is a three-judge 1-5 mean on
accuracy, completeness and clarity of the proposed plan. Overlap metrics such
as BERTScore are secondary. Decoding is zero-shot, 512 tokens. Missing jury
output becomes 1.0. The annotator prompt tells judges to use history,
medications and symptoms and to compare with the gold plan.

## Dataset and licence

The scenario pins `ebc104a` and downloads `mtsamples_processed`. That folder
has 1,269 `.txt` files. The post-filter instance count is not published. No
SPDX licence is stated. Nature Medicine treats the benchmark as public. The
website named in HELM metadata is mtsamples.com.

## Who publishes it

Stanford CRFM MedHELM (Bedi et al., arXiv 2505.23802; Nature Medicine 2026)
defines the scenario and jury. The text is MTSamples samples mirrored on
GitHub. The board is crfm.stanford.edu/helm/medhelm.

## Lineage

Sibling [mtsamples_procedures](mtsamples_procedures.md) is the surgical folder
and a note-generation group in the same schema. Other MedHELM generation ids
in this repository include [ACI-Bench](aci_bench.md) and [MIMIC-BHC](mimic_bhc.md).
There is no original MTSamples shared-task paper.

## Saturation and contamination

No scenario-level top score is recorded here. The notes have been public for
years, so contamination is high. A strong jury number on this dump is weak
evidence of private-EHR treatment planning.

## How to run it

`helm-run` with `mtsamples_replicate`. Name the jury models. Do not average
with `mtsamples_procedures` or with exact-match MedQA.

## Reading the numbers

A high score means the jury liked the plan relative to a short PLAN/SUMMARY
line from a public sample note. It does not measure drug-safety checking or
guideline citations. Many notes are educational transcriptions, not complete
charts. Use gated EHR tasks when the claim is real-clinic planning.
