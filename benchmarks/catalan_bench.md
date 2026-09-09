---
id: catalan_bench
name: CatalanBench
aliases: []
page_kind: benchmark
category: composite
subcategory: "native and adapted Catalan/Valencian language suite: QA, NLI, commonsense, paraphrase, summarisation and translation"
status: active
summary: An EleutherAI lm-evaluation-harness suite aggregating roughly two dozen Catalan- and Valencian-language tasks -- QA, NLI, commonsense, paraphrase, summarisation and translation -- built and funded by BSC's Projecte AINA.
measures: >
  CatalanBench aggregates existing and purpose-built datasets to test Catalan, and for a handful of
  tasks Valencian, language understanding and generation across many different skills rather than
  one. Implemented in EleutherAI's lm-evaluation-harness as the `catalan_bench` task group, it
  currently spans roughly two dozen sub-tasks: multiple-choice science and commonsense reasoning
  (ARC_ca, OpenBookQA_ca, PIQA_ca, SIQA_ca, COPA-ca, XStoryCloze_ca), extractive and generative
  question answering (CatalanQA, CoQCat, XQuAD-ca, TerretaQA), natural language inference (TE-ca,
  WNLI-ca, XNLI-ca, XNLI-va), paraphrase and linguistic-acceptability judgement (Parafraseja,
  PAWS-ca, CatCoLA), reading comprehension (Belebele_ca), summarisation (caBREU), truthfulness
  (TruthfulQA_va, VeritasQA_ca), Catalan-translated grade-school math word problems (MGSM_ca), a
  Valencian language-proficiency exam (CieaCOVA) and Catalan-to/from-seven-other-language machine
  translation (FLORES_ca). Some constituent datasets were purpose-built for this suite by Projecte
  AINA; others are pre-existing multilingual datasets (Belebele, FLORES, XNLI among them) with a
  Catalan or Valencian configuration added.
task_format: >
  Varies by sub-task: four- or five-option multiple-choice for the QA and commonsense tasks, binary
  or three-way classification for the NLI and acceptability tasks, span extraction or short
  free-text generation for the remaining QA and summarisation tasks, and sentence-level machine
  translation for the FLORES_ca directions. lm-evaluation-harness runs each sub-task independently
  and additionally exposes a `catalan_bench` group covering all of them together.
metric:
  name: "varies by sub-task: accuracy or F1 for most classification/QA tasks, ROUGE for summarisation, spBLEU for translation"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random or human baseline applies across roughly two dozen structurally different
    sub-tasks; each constituent task's own baseline should be read individually rather than assumed
    from the group as a whole. The IberoBench paper, which surveys CatalanBench alongside four
    sibling per-language suites rather than presenting a CatalanBench-only analysis, reports its
    headline comparisons using a Normalized Preferred Metric (NPM): for each task, NPM rescales the
    raw score so that the task's own random-guess score maps to 0 and its maximum possible score maps
    to 100, which is what makes averaging across differently-scaled tasks (accuracy, BLEU, and so on)
    meaningful; a model can score below 0 on a task if it does worse than random.
dataset:
  size: null
  size_note: >
    CatalanBench aggregates roughly two dozen sub-tasks of very different sizes: for example arc_ca
    alone totals 2,950 Easy-split and 1,469 Challenge-split instances per its own Hugging Face card.
    The IberoBench paper (see Paper below), which surveys CatalanBench alongside its four sibling
    suites, states it uses "27 tasks in Catalan" specifically for its own per-language score
    aggregation table -- a fixed subset selected for that comparison, not necessarily a claim that
    exactly 27 is the total number of Catalan tasks available (the lm-evaluation-harness README's own
    task list, reproduced under `harness.lm_eval` on this page, runs longer once FLORES_ca's many
    translation directions are counted individually). No single official total *item* count (as
    opposed to task count) across the full suite was found, so `size` is left empty here; treat any
    single "CatalanBench size" figure with caution unless its source states exactly which sub-tasks,
    splits and counting convention it used.
  url: "https://huggingface.co/projecte-aina"
  license: "Varies by sub-task (for example CC-BY-SA-4.0 for arc_ca, per its own Hugging Face card); this page did not check all roughly two dozen constituent datasets individually, so one suite-wide licence is not established."
  languages:
    - ca
  modalities:
    - text
  splits: "varies by sub-task; most constituent datasets ship their own train/validation/test split documented on their individual Hugging Face cards"
  public_test_set: null
publisher:
  org: "Barcelona Supercomputing Center (BSC-CNS); most individual constituent datasets are curated by BSC's Language Technologies Unit and funded by Projecte AINA. The umbrella IberoBench survey adds three further institutions: Universitat Pompeu Fabra (UPF), the Centro Singular de Investigacion en Tecnoloxias Intelixentes (CiTIUS-USC), and the HiTZ Center - IXA, University of the Basque Country (UPV/EHU)."
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
  url: "https://projecteaina.cat/"
paper:
  title: "IberoBench: A Benchmark for LLM Evaluation in Iberian Languages"
  arxiv: ""
  url: "https://aclanthology.org/2025.coling-main.699"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/catalan_bench"
released: "2025-01"
last_updated: "2026-08"
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
    No maintained leaderboard for CatalanBench specifically was found, but the IberoBench paper
    evaluated 33 base models (0-shot and 5-shot) and states plainly that "model performance in
    Iberian languages still is behind state-of-the-art results," evidence of real headroom rather
    than saturation. Catalan shows a specific pattern worth noting: unlike Basque, where a
    language-specific continually-pretrained model wins outright, the paper finds the best
    Catalan-specific model it tested, CataLlama-8B, is outperformed on Catalan tasks by
    general-purpose multilingual models (Mistral-7B, Llama 3-8B, Gemma-7B), and is even beaten by
    the English-centric base model it was itself continually pretrained from (Llama 3-8B) -- though
    the paper separately notes the FLOR model family shows small, consistent gains from Catalan
    continual pretraining over its own BLOOM foundation. No single top_score is recorded here because
    the paper reports normalised (NPM) scores per task category rather than one aggregate figure
    confirmed from a source read directly for this page.
contamination:
  risk: medium
  note: >
    Exposure varies sharply by sub-task rather than being uniform across the suite: long-established
    multilingual sets repurposed here (FLORES, Belebele, XNLI) have been public for years and are
    plausibly well represented in training data, while several Projecte-AINA-original tasks are much
    newer (the README's changelog shows additions as recent as August 2026) and have had far less
    time in public circulation. No publisher statement or independent study of contamination across
    the group as a whole was found.
harness:
  lm_eval: "catalan_bench (group); constituent tasks include arc_ca_challenge, arc_ca_easy, belebele_cat_Latn, cabreu, catalanqa, catcola, cieacova, cocoteros_va, copa_ca, coqcat, flores_ca (plus 16 directional variants), mgsm_direct_ca, openbookqa_ca, parafraseja, paws_ca, phrases_va, piqa_ca, siqa_ca, teca, terretaqa, truthfulqa_va, veritasqa_gen_ca, veritasqa_mc1_ca, veritasqa_mc2_ca, wnli_ca, xnli_ca, xnli_va, xquad_ca, xstorycloze_ca"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - composite
  - catalan
  - iberobench
  - multilingual
  - low-resource
  - nli
  - translation
  - question-answering
sources:
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/catalan_bench/README.md"
    title: "lm-evaluation-harness catalan_bench task group README"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/projecte-aina/arc_ca"
    title: "projecte-aina/arc_ca dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.coling-main.699"
    title: "IberoBench: A Benchmark for LLM Evaluation in Iberian Languages (Baucells et al., COLING 2025)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2025.coling-main.699.pdf"
    title: "IberoBench full PDF (author affiliations, task/subtask counts, NPM metric definition, per-language results discussion)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CatalanBench aggregates existing and purpose-built datasets to test Catalan, and for a handful of tasks Valencian, language understanding and generation across many different skills at once rather than one. Implemented in EleutherAI's lm-evaluation-harness as the `catalan_bench` task group, it currently spans roughly two dozen sub-tasks covering multiple-choice science and commonsense reasoning, extractive and generative question answering, natural language inference, paraphrase and linguistic-acceptability judgement, reading comprehension, summarisation, truthfulness, translated grade-school math word problems, a Valencian language-proficiency exam, and Catalan-to/from-seven-other-language machine translation.

Some of these datasets were purpose-built for this suite by Projecte AINA, the Catalan government-funded language-technology initiative run through BSC; others are pre-existing multilingual datasets -- Belebele, FLORES, XNLI among them -- with a Catalan or Valencian configuration added. This mixed construction means CatalanBench is best read as a curated collection of tasks under one evaluation umbrella, not as a single coherently-designed test the way MMLU-style exam benchmarks are.

## How it is scored

Because CatalanBench spans structurally different task types, scoring varies by sub-task: accuracy or F1 for most classification and multiple-choice tasks, ROUGE for the caBREU summarisation task, and spBLEU for the FLORES_ca translation directions. lm-evaluation-harness runs each sub-task independently and additionally exposes a `catalan_bench` group so all tasks can be launched together, but no single random or human baseline applies across the group as a whole -- each constituent task's own baseline should be checked individually. No CatalanBench-specific paper was found giving one aggregate figure; the closest citation, IberoBench (Baucells et al., COLING 2025), surveys CatalanBench alongside four sibling per-language suites and reports its own headline comparisons using a Normalized Preferred Metric (NPM), which rescales each task's raw score so a random guess maps to 0 and the maximum possible score maps to 100 -- the mechanism that lets the paper average accuracy-, F1-, ROUGE- and BLEU-scored tasks into one comparable per-language figure, evaluated across 33 base models under both 0-shot and 5-shot prompting.

## Dataset and licence

No single official total *item* count across the full suite was found: the lm-evaluation-harness README states a dedicated CatalanBench paper is "coming soon" rather than citing published totals, and naively summing every constituent dataset's own reported size risks double-counting (arc_ca alone totals 2,950 Easy-split and 1,469 Challenge-split instances, by comparison). The IberoBench paper does give one precise *task*-count figure: "27 tasks in Catalan," the fixed subset it uses for its own per-language score-aggregation table, against 17 for Spanish, 14 each for Basque and Galician, and 4 for Portuguese -- the largest per-language task count of the five, though a fixed evaluation subset rather than necessarily every Catalan task available. Licensing varies by sub-task -- arc_ca, for instance, is CC-BY-SA-4.0 per its own Hugging Face card -- and this page did not check all roughly two dozen constituent datasets individually, so a single suite-wide licence is not established.

## Who publishes it

CatalanBench's individual constituent datasets are curated by the Language Technologies Unit at the Barcelona Supercomputing Center (BSC-CNS) and funded by Projecte AINA, the Catalan government's language-technology programme, per the individual dataset cards this page checked. The task group itself is implemented and maintained within EleutherAI's lm-evaluation-harness, with a changelog showing active additions as recently as August 2026 (a Valencian proficiency-exam task and a Valencian translation task).

The closest published academic citation is IberoBench: A Benchmark for LLM Evaluation in Iberian Languages, presented at COLING 2025 (Abu Dhabi, January 2025) by Irene Baucells and fourteen co-authors, affiliated with BSC-CNS, Universitat Pompeu Fabra, the CiTIUS research centre at the Universidade de Santiago de Compostela, and the HiTZ Center (IXA group) at the University of the Basque Country -- a survey-style benchmark paper covering CatalanBench alongside four sibling per-language suites, rather than a paper describing CatalanBench alone.

## Lineage

CatalanBench is one of five same-shaped, per-language suites presented together in the IberoBench paper: [BasqueBench](basque_bench.md), which also has a page in this repository, plus GalicianBench, PortugueseBench and SpanishBench, which do not yet. All five share IberoBench's construction approach and NPM scoring, so a reader comparing CatalanBench and BasqueBench scores is comparing siblings built by the same team under the same methodology, not two unrelated projects. CatalanBench has no other predecessor or successor tracked here.

It differs sharply from `greekmmlu`, also in this repository: GreekMMLU is a single natively-authored, MMLU-style multiple-choice exam across 45 subjects in one consistent format, while CatalanBench aggregates roughly two dozen pre-existing and purpose-built datasets across many different task *types* (QA, NLI, translation, summarisation and more), only some of which were natively authored in Catalan -- both share a low-resource-language motivation but pursue it through very different constructions.

## Saturation and contamination

No maintained leaderboard specific to CatalanBench was found, but the IberoBench paper evaluated 33 base models under 0-shot and 5-shot prompting and states plainly that "model performance in Iberian languages still is behind state-of-the-art results" -- real headroom rather than saturation. Catalan shows a distinctive pattern: unlike Basque, where a language-specific continually-pretrained model wins outright, the best Catalan-specific model tested, CataLlama-8B, is outperformed on Catalan tasks by general-purpose multilingual models (Mistral-7B, Llama 3-8B, Gemma-7B) and even by the English-centric base model it was continually pretrained from -- though the FLOR model family separately shows small, consistent gains from Catalan continual pretraining over its own BLOOM foundation, so the picture is mixed rather than uniformly negative for language-specific adaptation. Several constituent tasks are also independently tracked through their own original multilingual benchmarks, with Belebele, FLORES and XNLI in particular carrying separately published leaderboards elsewhere.

Contamination risk sits at medium, though exposure varies sharply by sub-task rather than being uniform: long-established multilingual sets repurposed here have been public for years and are plausibly well represented in training data, while several Projecte-AINA-original tasks are much newer, with additions as recent as August 2026, and have had far less time in public circulation. No publisher statement or independent study of contamination across the group as a whole was found.

## How to run it

The task group lives in EleutherAI's lm-evaluation-harness at `lm_eval/tasks/catalan_bench/`, runnable as the `catalan_bench` group or as any of its roughly two dozen individual task ids (for example `arc_ca_challenge`, `xnli_ca`, `flores_ca-en`). No OpenCompass, inspect_evals, HELM or BIG-bench implementation of the group was found, though some individual constituent datasets (FLORES, Belebele) are separately implemented elsewhere under their own ids. Because the group mixes multiple-choice, classification, generation and translation tasks with different metrics, a single averaged "CatalanBench score" is not something the source itself defines -- a reporter must state which sub-tasks it included and how it combined their differently-scaled metrics.

## Reading the numbers

A strong showing across CatalanBench suggests broad Catalan-language competence spanning reading comprehension, reasoning, inference and translation, rather than strength in any one skill, since the group deliberately mixes task types. Because the suite pools purpose-built and repurposed datasets of very different ages, sizes and provenance, a single blended score can mask large per-task variation -- a model might excel at translation into Catalan while lagging on native commonsense reasoning, and the group average would hide that. As the CataLlama-8B result above shows, "trained on Catalan data" is not a reliable proxy for "will score highest on CatalanBench." Given no combined leaderboard was found, treat any single reported "CatalanBench" number as one reporter's own aggregation choice, and check which sub-tasks it drew from before comparing it to another.
