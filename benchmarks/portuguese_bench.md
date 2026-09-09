---
id: portuguese_bench
name: "PortugueseBench"
aliases:
  - "portuguese_bench"
  - "Portuguese Bench"
page_kind: benchmark
category: composite
subcategory: "European Portuguese IberoBench slice: NLI, paraphrase, reading comprehension and translation"
status: active
summary: "IberoBench's European Portuguese suite: ASSIN entailment and paraphrase, Belebele reading, and FLORES translation, plus two extra ASSIN2 tasks in the current harness group."
measures: >
  PortugueseBench is the European Portuguese slice of IberoBench, the same five-language
  project as this repository's CatalanBench, BasqueBench and GalicianBench pages. IberoBench
  Table 1 lists four Portuguese tasks: assin_entailment (NLI), assin_paraphrase, belebele_por_Latn
  (reading comprehension) and flores_pt (translation). The paper states that several task types
  are not yet available for European Portuguese. Translations into Portuguese were aimed at the
  European variety. The current lm-evaluation-harness group also runs assin2_rte and assin2_sts,
  which Table 1 does not list.
task_format: >
  Mixed: two-way multiple choice for ASSIN entailment and paraphrase; multiple-choice reading
  for Belebele Portuguese; sentence-level machine translation for sixteen FLORES directions
  to or from Portuguese; multiple-choice RTE and free-form 1-5 similarity for ASSIN2 in the
  harness-only extras. IberoBench evaluates 0-shot and 5-shot.
metric:
  name: "task-dependent: accuracy (ASSIN, Belebele); BLEU/ROUGE-family scores for FLORES; macro-F1 (assin2_rte); Pearson r (assin2_sts)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random baseline covers the suite. IberoBench reports a Normalized Preferred
    Metric (NPM) that maps each task's random score to 0 and its maximum to 100 so heterogeneous
    metrics can be averaged. The paper's Portuguese aggregate uses the four Table 1 tasks, not
    necessarily the six-entry harness group.
dataset:
  size: null
  size_note: >
    No official suite-wide item count. Component sizes confirmed from Hugging Face:
    facebook/belebele por_Latn test is 900 rows; nilc-nlp/assin full split is 5,000 train /
    1,000 validation / 4,000 test (with separate ptbr and ptpt 2,000-row tests); nilc-nlp/assin2
    is 6,500 / 500 / 2,448. FLORES-200 is gated on the Hub; the facebook/flores API still
    reports a 1,012-sentence evaluation split (devtest) per language. IberoBench treats
    flores_pt as one task that expands to 16 directions in the harness (pt-ca, pt-de, pt-en,
    pt-es, pt-eu, pt-fr, pt-gl, pt-it and the reverse).
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/portuguese_bench"
  license: >
    Varies by component. facebook/belebele is CC-BY-SA-4.0. facebook/flores is CC-BY-SA-4.0
    (gated). nilc-nlp/assin and nilc-nlp/assin2 list licence as unknown on their Hugging Face
    cards. No suite-wide licence is established.
  languages:
    - pt
  modalities:
    - text
  splits: "each component keeps its own train/validation/test; evaluation uses the test splits named in the task YAMLs"
  public_test_set: true
publisher:
  org: "IberoBench consortium: Barcelona Supercomputing Center (BSC-CNS), Universitat Pompeu Fabra, CiTIUS-USC, and HiTZ Center - IXA (UPV/EHU)"
  authors:
    - "Irene Baucells"
    - "Javier Aula-Blasco"
    - "Iria de-Dios-Flores"
    - "Silvia Paniagua Suárez"
    - "Naiara Perez"
    - "Anna Salles"
    - "Susana Sotelo Docio"
    - "Júlia Falcão"
    - "Jose Javier Saiz"
    - "Robiert Sepulveda Torres"
    - "Jeremy Barnes"
    - "Pablo Gamallo"
    - "Aitor Gonzalez-Agirre"
    - "German Rigau"
    - "Marta Villegas"
  url: "https://aclanthology.org/2025.coling-main.699/"
paper:
  title: "IberoBench: A Benchmark for LLM Evaluation in Iberian Languages"
  arxiv: ""
  url: "https://aclanthology.org/2025.coling-main.699"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/portuguese_bench"
released: "2025-01"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - catalan_bench
    - basque_bench
    - galician_bench
saturation:
  status: open
  top_score: null
  as_of: "2025-01"
  note: >
    No PortugueseBench-only leaderboard was found. IberoBench evaluated 33 base models at
    0-shot and 5-shot and states that performance in Iberian languages "still is behind
    state-of-the-art results." Portuguese is the smallest language slice (four Table 1
    tasks). top_score is empty because the paper reports NPM per category rather than one
    raw Portuguese figure confirmed here.
contamination:
  risk: medium
  note: >
    Belebele (2023) and FLORES are widely mirrored multilingual sets. ASSIN (Fonseca et al.,
    2016) and ASSIN2 are older Portuguese NLI/STS resources. IberoBench required human
    revision of automatically annotated sets such as ASSIN. No suite-wide contamination
    study was found. Answers are public.
harness:
  lm_eval: >
    portuguese_bench (group); flores_pt (FLORES subgroup); constituent tasks assin_paraphrase,
    assin_entailment, assin2_rte, assin2_sts, belebele_por_Latn, flores_pt-ca, flores_pt-de,
    flores_pt-en, flores_pt-es, flores_pt-eu, flores_pt-fr, flores_pt-gl, flores_pt-it,
    flores_ca-pt, flores_de-pt, flores_en-pt, flores_es-pt, flores_eu-pt, flores_fr-pt,
    flores_gl-pt, flores_it-pt
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - composite
  - portuguese
  - iberobench
  - multilingual
  - nli
  - translation
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/portuguese_bench/README.md"
    title: "lm-evaluation-harness portuguese_bench README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/portuguese_bench/portuguese_bench.yaml"
    title: "portuguese_bench.yaml group membership"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/portuguese_bench/assin_entailment.yaml"
    title: "assin_entailment.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/portuguese_bench/assin_paraphrase.yaml"
    title: "assin_paraphrase.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/portuguese_bench/assin2_rte.yaml"
    title: "assin2_rte.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/portuguese_bench/assin2_sts.yaml"
    title: "assin2_sts.yaml"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.coling-main.699.pdf"
    title: "IberoBench COLING 2025 PDF (Table 1 Portuguese tasks, NPM setup, 33-model evaluation)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/belebele"
    title: "facebook/belebele API (CC-BY-SA-4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/nilc-nlp/assin"
    title: "nilc-nlp/assin API (licence listed unknown)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/nilc-nlp/assin2"
    title: "nilc-nlp/assin2 API (licence listed unknown)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=nilc-nlp/assin"
    title: "nilc-nlp/assin split sizes"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=nilc-nlp/assin2"
    title: "nilc-nlp/assin2 split sizes"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/flores"
    title: "facebook/flores API (CC-BY-SA-4.0, gated; FLORES-200 1,012-sentence eval split)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=facebook/belebele"
    title: "facebook/belebele row counts (por_Latn test 900)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-019 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-019"
---

## What it measures

PortugueseBench is IberoBench's European Portuguese suite. IberoBench (Baucells et al., COLING 2025) covers Basque, Catalan, Galician, European Spanish and European Portuguese on EleutherAI's lm-evaluation-harness. Table 1 of that paper gives Portuguese four tasks only: `assin_entailment`, `assin_paraphrase`, `belebele_por_Latn` and `flores_pt`. The authors note that several categories still have no Portuguese dataset.

The current harness group `portuguese_bench` adds `assin2_rte` and `assin2_sts` on top of those four, and expands `flores_pt` into sixteen translation directions. The README still says a dedicated PortugueseBench paper is "coming soon" and, in its task table, mislabels Belebele and FLORES as `_es`; the runnable ids are Portuguese (`belebele_por_Latn`, `flores_pt`).

## How it is scored

ASSIN entailment and paraphrase are two-way multiple-choice accuracy. Belebele Portuguese is multiple-choice accuracy. FLORES directions use the harness translation metrics (IberoBench discusses BLEU and ROUGE as the family it actually reports). The extra ASSIN2 RTE task uses macro-F1; ASSIN2 STS is a generated 1-5 similarity scored with Pearson r. IberoBench's own headline comparisons use NPM, rescaling each task so random maps to 0 and the maximum to 100, then averaging a fixed per-language subset — four tasks for Portuguese versus 27 for Catalan. A harness `portuguese_bench` group run that includes ASSIN2 is therefore not the paper's four-task NPM.

## Dataset and licence

There is no single official item count. Belebele Portuguese contributes 900 test items. ASSIN's full card is 5,000/1,000/4,000 plus separate Brazilian and European 2,000-row tests; ASSIN2 is 6,500/500/2,448. FLORES-200 is gated; the Hub API still lists 1,012 evaluation sentences per language (devtest). Licensing is mixed: Belebele and FLORES are CC-BY-SA-4.0; both ASSIN cards currently list licence as unknown. Gold labels are public.

## Who publishes it

IberoBench is authored by Irene Baucells and fourteen co-authors at BSC-CNS, Universitat Pompeu Fabra, CiTIUS-USC and HiTZ/IXA (UPV/EHU), presented at COLING 2025 in Abu Dhabi (January 2025). ASSIN itself is an earlier Portuguese shared task (Fonseca et al., 2016, cited in the IberoBench references). The task group is maintained inside lm-evaluation-harness, not on a standalone leaderboard.

## Lineage

PortugueseBench is a sibling of [CatalanBench](catalan_bench.md), [BasqueBench](basque_bench.md) and [GalicianBench](galician_bench.md). SpanishBench is named in the same paper and does not yet have a page here. It is not [ENEM Challenge](enem_challenge.md), which uses Brazilian secondary-school exam questions, and it is not the Portuguese slice of [P-MMEval](pmmeval.md), which is a ten-language Qwen suite. IberoBench explicitly targeted European Portuguese, not a Brazilian mix.

## Saturation and contamination

Saturation is recorded as open on the IberoBench finding that Iberian-language scores still lag, with no Portuguese-only leaderboard found. Contamination risk is medium: FLORES and Belebele are standard multilingual sets, ASSIN dates to 2016, and all answers are public. IberoBench's inclusion rule for ASSIN was that automatic annotations had been human-revised.

## How to run it

In lm-evaluation-harness, run the `portuguese_bench` group or any constituent id (`assin_entailment`, `belebele_por_Latn`, `flores_pt-en`, `assin2_sts`, …). No OpenCompass, HELM or inspect_evals group with this name was found. State whether a reported number is the paper's four-task NPM, the six-entry harness group, or a FLORES-only average.

## Reading the numbers

A strong PortugueseBench result, on the paper's four tasks, is competence on European Portuguese NLI, paraphrase, reading and translation together, not exam knowledge (there is no Portuguese MMLU-style paper in this slice). Including ASSIN2 changes the mix and the metrics. Do not treat a Portuguese P-MMEval or ENEM number as a substitute: different items, different variety, different skills.
