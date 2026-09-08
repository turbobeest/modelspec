---
id: basque_bench
name: "BasqueBench"
aliases: []
page_kind: benchmark
category: composite
subcategory: "Basque-language multitask suite spanning question answering, NLI, paraphrase, commonsense, math and translation"
status: active
summary: "18 Basque-language tasks -- reused Basque NLU/QA sets plus six built for this suite -- bundled into one lm-evaluation-harness group to score base LLMs on Basque, part of the wider IberoBench project."
measures: >
  BasqueBench is the Basque-language slice of IberoBench, a multilingual, multi-task benchmark for
  the official languages of the Iberian peninsula (Basque, Catalan, Galician, European Spanish and
  European Portuguese), built on EleutherAI's lm-evaluation-harness. Each of the five languages gets
  its own same-shaped suite -- BasqueBench, CatalanBench, GalicianBench, PortugueseBench and
  SpanishBench -- covering that language's own tasks rather than one shared multilingual task set.
  BasqueBench bundles 18 task groups: six built specifically for this project (ARC-eu, MGSM-eu,
  PAWS-eu, PIQA-eu, WNLI-eu and XCOPA-eu, translations or adaptations of established English
  benchmarks into Basque) alongside reused, previously published Basque resources -- the Latxa
  evaluation suite (EusExams, EusProficiency, EusReading, EusTrivia), Belebele's Basque config, FLORES
  translation pairs, BasqueGLUE's QNLIeu, XNLIeu, and XStoryCloze's Basque config. It measures broad
  base-model competence in Basque -- reading comprehension, commonsense inference, natural-language
  inference, paraphrase detection, grade-school math, and bidirectional translation -- as one
  aggregate suite rather than any single skill.
task_format: >
  Mixed by sub-task: multiple-choice question answering and commonsense reasoning (ARC-eu, PIQA-eu,
  XCOPA-eu, Belebele-eu, EusExams, EusProficiency, EusTrivia); extractive reading comprehension
  (EusReading); sentence-pair classification for natural-language inference and paraphrase detection
  (XNLIeu, WNLI-eu, PAWS-eu, QNLIeu); free-form grade-school math word problems, in both a
  direct-answer and a native chain-of-thought variant (MGSM-eu); and bidirectional machine translation
  between Basque and eight other languages (FLORES-eu). The IberoBench paper evaluates all of these
  under 0-shot and 5-shot prompting.
metric:
  name: "task-dependent: accuracy for most multiple-choice and NLI tasks; BLEU/ChrF-family scores for FLORES-eu translation directions; task-specific scoring for EusReading"
  direction: higher_is_better
  unit: "%"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random-guess percentage applies across a suite this heterogeneous: multiple-choice
    sub-tasks vary between two, three and four answer options, translation sub-tasks are scored on a
    continuous metric rather than accuracy, and the paper reports its own results as a normalised
    performance measure (NPM) averaged per category and per language rather than one raw baseline
    figure. No human baseline is reported.
dataset:
  size: null
  size_note: >
    BasqueBench aggregates many independently sized source datasets rather than one fixed item pool,
    so this page leaves `size` empty. Two counts from the IberoBench paper itself give a sense of
    scale at different levels: the full IberoBench project totals "62 tasks divided into 179
    subtasks" across all five languages, and, specifically for score aggregation, the paper states it
    averaged "14 [tasks] in Basque" (against 27 in Catalan, 17 in Spanish, 14 in Galician and 4 in
    Portuguese) -- a fixed subset used to compute each language's reported average, not necessarily
    every task available for that language. Separately, lm-evaluation-harness's own `basque_bench.yaml`
    lists 18 top-level task/group entries, one of which (`flores_eu`) itself expands into 16
    direction-specific translation subtasks, so the practically runnable task count depends on which
    of these three countings is used.
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/basque_bench"
  license: >
    Not a single licence. Checking the Hugging Face cards of the suite's own component datasets
    directly found at least five different terms in use: CC BY-SA 4.0 (ARC-eu, MGSM-eu, Belebele's
    Basque config), CC BY 4.0 (XCOPA-eu), CC BY-NC 4.0 (XNLIeu), AFL 3.0 (PIQA-eu), and "other" with
    no further detail given (PAWS-eu); EusTrivia and BasqueGLUE's cards set no licence tag at all.
    Anyone reusing BasqueBench as a whole needs to check the licence of whichever specific sub-tasks
    they use rather than assume one licence covers the suite.
  languages:
    - eu
  modalities:
    - text
  splits: "aggregates each source dataset's own splits; most sub-tasks are evaluated on a single test-like split, with 0-shot and 5-shot prompting as the two settings the IberoBench paper reports rather than distinct data splits"
  public_test_set: true
publisher:
  org: "Barcelona Supercomputing Center (BSC-CNS), with Universitat Pompeu Fabra (UPF), the Centro Singular de Investigacion en Tecnoloxias Intelixentes (CiTIUS, Universidade de Santiago de Compostela), and the HiTZ Center - IXA, University of the Basque Country (UPV/EHU)"
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
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/basque_bench"
paper:
  title: "IberoBench: A Benchmark for LLM Evaluation in Iberian Languages"
  arxiv: ""
  url: "https://aclanthology.org/2025.coling-main.699"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/basque_bench"
released: "2025-01"
last_updated: "2026-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    No current leaderboard was found for BasqueBench specifically. The IberoBench paper's own
    5-shot and 0-shot results, evaluated across 33 small and medium-size base models, state plainly
    that "model performance in Iberian languages still is behind state-of-the-art results," and its
    per-language figures show Basque as an outlier in one respect: Basque is the one language of the
    five where a language-specific continually-pretrained model (Latxa-13B) beats every
    multilingual-SOTA model tested, rather than losing to a larger multilingual model as happens in
    the other four languages. That is read here as evidence of real, unsaturated headroom rather than
    a specific numeric ceiling, since no aggregate top score was confirmed from a source read directly.
contamination:
  risk: medium
  note: >
    Component datasets span a wide range of ages and exposure: FLORES (2022) and Belebele (2023) have
    been public for years, the Latxa-suite datasets (EusExams, EusProficiency, EusReading, EusTrivia)
    and XNLIeu were released in 2024, and the six datasets built specifically for BasqueBench
    (ARC-eu, MGSM-eu, PAWS-eu, PIQA-eu, WNLI-eu, XCOPA-eu) are the newest. No held-out or
    periodically-refreshed portion was described for any of them, so contamination risk should be
    assessed per sub-task rather than assumed uniform across the suite.
harness:
  lm_eval: "basque_bench"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness's basque_bench.yaml lists 18 entries; one of them, the flores_eu group,
    itself expands into 16 direction-specific translation subtasks (8 into Basque, 8 out of Basque),
    so the number of individually runnable tasks is higher than the top-level group count.
tags:
  - basque
  - composite
  - multitask
  - iberobench
  - low-resource
  - multilingual
  - translation
  - nli
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basque_bench/README.md"
    title: "lm-evaluation-harness basque_bench task README (task table, sources, citation, changelog)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basque_bench/basque_bench.yaml"
    title: "lm-evaluation-harness basque_bench.yaml (18-task group definition, version)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.coling-main.699.pdf"
    title: "Baucells et al. (2025). IberoBench: A Benchmark for LLM Evaluation in Iberian Languages. COLING 2025, full PDF (author affiliations, task/subtask counts, per-language score-aggregation table, results discussion)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.coling-main.699"
    title: "IberoBench, ACL Anthology page"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/ARC-eu"
    title: "HiTZ/ARC-eu dataset metadata (licence: CC BY-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/PIQA-eu"
    title: "HiTZ/PIQA-eu dataset metadata (licence: AFL 3.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/EusExams"
    title: "HiTZ/EusExams dataset metadata (licence: CC BY-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/MGSM-eu"
    title: "HiTZ/MGSM-eu dataset metadata (licence: CC BY-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/XCOPA-eu"
    title: "HiTZ/XCOPA-eu dataset metadata (licence: CC BY 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/PAWS-eu"
    title: "HiTZ/PAWS-eu dataset metadata (licence: other, unspecified)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/xnli-eu"
    title: "HiTZ/xnli-eu dataset metadata (licence: CC BY-NC 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/belebele"
    title: "facebook/belebele dataset metadata (licence: CC BY-SA 4.0)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BasqueBench is the Basque-language slice of IberoBench, a multilingual, multi-task benchmark covering the official languages of the Iberian peninsula -- Basque, Catalan, Galician, European Spanish and European Portuguese -- built on top of EleutherAI's lm-evaluation-harness. Each language gets its own same-shaped suite named after it (BasqueBench, CatalanBench, GalicianBench, PortugueseBench, SpanishBench), each containing that language's own tasks rather than one shared multilingual set. BasqueBench itself bundles 18 task groups: six built specifically for this project -- ARC-eu, MGSM-eu, PAWS-eu, PIQA-eu, WNLI-eu and XCOPA-eu, translations or careful adaptations of established English-language benchmarks into Basque -- alongside reused, previously published Basque resources: the Latxa evaluation suite (EusExams, EusProficiency, EusReading, EusTrivia), a Basque configuration of Belebele, Basque-direction FLORES translation pairs, BasqueGLUE's QNLIeu task, XNLIeu, and a Basque configuration of XStoryCloze.

Taken together, these measure broad base-model competence in Basque rather than one specific skill: reading comprehension, commonsense inference, natural-language inference, paraphrase detection, grade-school arithmetic word problems, and bidirectional machine translation. Because Basque translation adjustments (for example, restructuring sentences that require an ergative subject, which English does not mark) needed real linguistic care, the IberoBench paper documents specific translation decisions for several of its Basque-specific tasks rather than treating translation as mechanical.

## How it is scored

Scoring is task-dependent rather than uniform, which is the norm for a composite suite this broad: multiple-choice and commonsense tasks (ARC-eu, PIQA-eu, XCOPA-eu, Belebele-eu, the Latxa-suite exam tasks) are scored by accuracy against two-, three- or four-option answer sets; sentence-pair tasks (XNLIeu, WNLI-eu, PAWS-eu, QNLIeu) are scored as classification accuracy; MGSM-eu is scored as free-form numeric exact match, in both a direct-answer and a native chain-of-thought prompting variant; and FLORES-eu's sixteen translation directions are scored on continuous machine-translation metrics rather than accuracy. Because of this mix, the IberoBench paper reports its own headline numbers as a normalised performance measure (NPM) averaged per task category and per language, rather than one raw accuracy figure, evaluated under both 0-shot and 5-shot prompting across 33 base models. For computing each language's single reported average, the paper uses a fixed subset of tasks rather than every available task -- 14 for Basque, specifically -- a detail easy to miss if reading only the headline per-language numbers.

## Dataset and licence

BasqueBench has no single dataset size, since it aggregates many independently sized and independently licensed source datasets rather than shipping as one file. Two IberoBench-level counts frame its scale: the full five-language project totals "62 tasks divided into 179 subtasks," and the paper's own score-aggregation table uses 14 tasks specifically for Basque (against 27 for Catalan, 17 for Spanish, 14 for Galician and 4 for Portuguese). Separately, lm-evaluation-harness's `basque_bench.yaml` lists 18 top-level task/group entries, one of which (`flores_eu`) itself expands into 16 direction-specific translation subtasks -- so "how many BasqueBench tasks are there" has at least three different defensible answers depending on which counting convention is used, and this page reports all three rather than picking one. Licensing is equally fragmented: checking the suite's own component datasets directly on Hugging Face found CC BY-SA 4.0 (ARC-eu, MGSM-eu, Belebele's Basque config), CC BY 4.0 (XCOPA-eu), CC BY-NC 4.0 (XNLIeu), AFL 3.0 (PIQA-eu), an unspecified "other" (PAWS-eu), and no licence tag at all (EusTrivia, BasqueGLUE). No single licence covers BasqueBench as a whole.

## Who publishes it

BasqueBench is one product of the IberoBench project, published by Irene Baucells, Javier Aula-Blasco, Iria de-Dios-Flores, Silvia Paniagua Suárez, Naiara Perez, Anna Salles, Susana Sotelo Docio, Júlia Falcão, Jose Javier Saiz, Robiert Sepulveda Torres, Jeremy Barnes, Pablo Gamallo, Aitor Gonzalez-Agirre, German Rigau and Marta Villegas, presented at COLING 2025 (Abu Dhabi, January 2025). The authors are affiliated with the Barcelona Supercomputing Center (BSC-CNS), Universitat Pompeu Fabra, the CiTIUS research centre at the Universidade de Santiago de Compostela, and the HiTZ Center (IXA group) at the University of the Basque Country (UPV/EHU) -- the same HiTZ group behind several of BasqueBench's reused component datasets and behind `bertaqa`, a separate benchmark also in this repository. The suite itself is distributed and maintained as part of EleutherAI's lm-evaluation-harness rather than through a standalone repository.

## Lineage

BasqueBench has four siblings within IberoBench that this repository does not yet have pages for: CatalanBench, GalicianBench, PortugueseBench and SpanishBench, each the same-shaped suite for its own language. It shares HiTZ-affiliated authorship and thematic territory with `bertaqa`, also in this repository, but the two are distinct artefacts, not variants of each other: BasqueBench's own task list includes EusTrivia, a Latxa-paper trivia dataset, but does not include BertaQA, a separate trivia benchmark from an overlapping set of HiTZ authors -- easy to conflate given the shared theme and contributors, but not the same dataset or the same paper. Alongside this repository's GreekMMLU and CMMLU, BasqueBench belongs to the broader pattern of native or regionally-focused language benchmarks built to avoid relying on machine-translated English test material, though its composite, many-small-tasks structure is closer to AGIEval's assembled-from-existing-resources approach than to either of those single-format multiple-choice knowledge suites.

## Saturation and contamination

No current leaderboard was found for BasqueBench specifically, so saturation is recorded as "open" rather than "saturated," on the strength of the IberoBench paper's own finding that "model performance in Iberian languages still is behind state-of-the-art results" across the 33 base models it evaluated. One result stands out for Basque specifically: it is the only one of the five languages in the paper where a language-specific, continually-pretrained model (Latxa-13B) achieves the best absolute performance, beating every multilingual-SOTA model tested -- in the other four languages, a larger multilingual model wins instead. Contamination risk is medium and uneven across sub-tasks: some component datasets (FLORES, Belebele) have been public for years, others (the Latxa suite, XNLIeu) since 2024, and the six datasets built specifically for this project are the newest and least exposed; none are described as held out or periodically refreshed.

## How to run it

lm-evaluation-harness implements BasqueBench as the `basque_bench` group, aggregating 18 sub-task/group YAML files (for example `arc_eu_challenge`, `eus_trivia`, `xcopa_eu`, `flores_eu`); a handful of these, like `belebele_eus_Latn` and `qnlieu`, reuse task implementations already present in the harness for other purposes rather than being BasqueBench-specific code. Because the suite mixes accuracy-based and translation-metric-based tasks, an aggregate "BasqueBench score" is not directly comparable to a single-metric benchmark elsewhere in this repository; compare at the level of individual tasks or task categories instead, matching how the IberoBench paper itself reports results.

## Reading the numbers

BasqueBench is best read task by task or category by category rather than as one blended score, given how many different skills and metrics it bundles together. Its most distinctive finding to date -- that Basque is the one Iberian language in the IberoBench comparison where a language-specific model outperforms every multilingual-SOTA competitor -- suggests continued Basque-specific pretraining pays off unusually well relative to the other four languages, though the underlying model pool tested so far is limited to smaller, pre-2025 base models rather than current frontier systems. Because component tasks carry different licences, different ages and different levels of prior public exposure, treat a single reported BasqueBench average cautiously, and check which of the 14, 18 or 179-subtask countings a given source used before comparing two reported task counts.
