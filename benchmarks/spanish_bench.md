---
id: spanish_bench
name: "SpanishBench"
aliases:
  - "spanish_bench"
page_kind: benchmark
category: composite
subcategory: "fifteen-task European Spanish NLU/NLG suite (part of IberoBench)"
status: active
summary: "Fifteen-task European Spanish suite spanning commonsense, QA, NLI, translation, math, summarisation and more, run as one lm-evaluation-harness group tag."
measures: >
  SpanishBench is the European-Spanish slice of IberoBench, a multi-task benchmark covering five
  Iberian languages (Basque, Catalan, Galician, European Spanish and European Portuguese) built
  on lm-evaluation-harness. It combines two newly created tasks (COPA-es for commonsense causal
  reasoning, OpenBookQA_es for open-book QA) with adaptations of established datasets covering
  linguistic acceptability (EsCoLA), reading comprehension (Belebele_es), translation (FLORES_es),
  math word problems (MGSM_es), paraphrase identification (PAWS-X_es), natural language inference
  (WNLI-es, XNLI_es), summarisation (XL-Sum_es), story-ending commonsense (XStoryCloze_es),
  extractive QA (XQuAD_es), and a few additional tasks (Cocoteros_es, EQ-Bench_es, phrases_es)
  added to the harness after the original paper's publication.
task_format: >
  Mixed by constituent task: multiple choice (COPA-es, OpenBookQA_es, XStoryCloze_es), sentence
  classification (EsCoLA, PAWS-X_es, WNLI-es, XNLI_es), span extraction (XQuAD_es), free-text
  generation scored against references (FLORES_es translation, XL-Sum_es summarisation,
  MGSM_es math), and other task-specific formats. lm-eval's `spanish_bench` tag runs all
  constituent tasks under one group; it does not fine-tune, only zero/few-shot prompt.
metric:
  name: "per-task metric (accuracy, F1, BLEU/chrF, ROUGE, exact match; task-dependent)"
  direction: higher_is_better
  unit: "%"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single metric or random baseline applies across the fifteen constituent tasks; each task
    keeps its own scoring rule (for example FLORES_es uses translation metrics, XNLI_es and
    WNLI-es use accuracy, XL-Sum_es uses ROUGE). The IberoBench paper reports per-task and
    per-language results rather than one blended SpanishBench number.
dataset:
  size: null
  size_note: >
    There is no single item pool: each constituent task has its own size (for example FLORES_es
    covers nine language-pair directions, and MGSM_es reuses the 250-item MGSM test set
    translated to Spanish). The IberoBench paper describes the full multilingual benchmark as 62
    tasks divided into 179 subtasks across five languages; a Spanish-only task or subtask count
    was not independently tallied for this page.
  url: ""
  license: ""
  languages:
    - es
  modalities:
    - text
  splits: "per-task train/validation/test as defined by each constituent dataset"
  public_test_set: true
publisher:
  org: "Barcelona Supercomputing Center (Language Technologies Unit)"
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
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/spanish_bench"
paper:
  title: "IberoBench: A Benchmark for LLM Evaluation in Iberian Languages"
  arxiv: ""
  url: "https://aclanthology.org/2025.coling-main.699/"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/spanish_bench"
released: "2025"
last_updated: "2026-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - basque_bench
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    IberoBench evaluated 33 existing LLMs in 0- and 5-shot settings as of the COLING 2025 paper,
    but a Spanish-specific aggregate top score was not extracted from a source opened for this
    page, since the paper reports per-task rather than one blended number. Status is left
    unknown rather than assumed, especially given several constituent tasks (XNLI, PAWS-X) are
    old, well-known NLI/paraphrase sets that newer, larger models tend to score highly on.
contamination:
  risk: medium
  note: >
    Most constituent datasets (XNLI, PAWS-X, WNLI, XQuAD, FLORES, XL-Sum, XStoryCloze) are
    long-public multilingual NLP benchmarks predating most current LLMs' training cutoffs, so
    contamination is plausible for those tasks specifically. The two newly created tasks
    (COPA-es, OpenBookQA_es) are more recent Spanish adaptations and carry comparatively lower
    risk, but the group as a whole should be treated as mixed rather than uniformly low or high.
harness:
  lm_eval: "spanish_bench"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Constituent task names in the spanish_bench directory: belebele_spa_Latn, copa_es, escola, openbookqa_es, wnli_es, xnli_es_spanish_bench, xstorycloze_es, xquad_es, xlsum_es, paws_es_spanish_bench, mgsm_direct_es_spanish_bench, eqbench_es, flores_es, phrases_es, cocoteros_es."
tags:
  - spanish
  - nlu
  - nlg
  - multilingual
  - iberobench
  - composite
sources:
  - url: "https://aclanthology.org/2025.coling-main.699/"
    title: "IberoBench ACL Anthology page (COLING 2025): abstract, 15-author list, 62 tasks/179 subtasks, five Iberian languages, 33 models evaluated"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/spanish_bench/README.md"
    title: "lm-evaluation-harness spanish_bench README (task list, new vs previously-published dataset split, citation to IberoBench)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/spanish_bench/spanish_bench.yaml"
    title: "lm-eval spanish_bench.yaml group config (group tag spanish_bench, 15 constituent task names, version 1.2)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/spanish_bench"
    title: "lm-evaluation-harness spanish_bench directory listing (yaml files, flores_es and phrases_es subdirectories, utils.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-003"
---

## What it measures

SpanishBench is not a single test but a bundle: it is the European-Spanish language slice of IberoBench, a five-language benchmark (Basque, Catalan, Galician, European Spanish, European Portuguese) built specifically because most multi-task LLM benchmarks only exist in a handful of high-resource languages. Running `spanish_bench` in lm-evaluation-harness executes fifteen constituent tasks together: two written specifically for this benchmark (COPA-es for causal commonsense, OpenBookQA_es for open-book science QA) and the rest adapted from established multilingual datasets covering linguistic acceptability, reading comprehension, translation, math word problems, paraphrase detection, natural language inference, summarisation, story-ending choice and extractive QA. A few additional tasks (Cocoteros_es, EQ-Bench_es, phrases_es) were added to the harness group after the original COLING 2025 paper.

## How it is scored

There is no unified SpanishBench score. Each constituent task keeps its native metric: accuracy for the NLI and paraphrase tasks (XNLI_es, WNLI-es, PAWS-X_es), accuracy or F1 for the multiple-choice tasks (COPA-es, OpenBookQA_es, XStoryCloze_es), translation quality metrics for FLORES_es, ROUGE for XL-Sum_es summarisation, and exact-match/F1 for XQuAD_es extractive QA. The IberoBench paper reports 0-shot and 5-shot results per task and per language rather than one blended Spanish number; running the `spanish_bench` group tag in lm-eval produces a per-task results table, and any single "SpanishBench score" quoted elsewhere should specify which task(s) or an explicit averaging method, since none is defined by the harness group itself.

## Dataset and licence

Because SpanishBench aggregates fifteen independently sourced datasets, there is no single item count, size or licence for the whole. The IberoBench paper describes the full five-language benchmark as 62 tasks divided into 179 subtasks; a Spanish-only subtask count was not independently tallied here. Constituent datasets carry their own original licences and splits (for example FLORES_es and XNLI_es are Meta/Facebook-published multilingual sets, XQuAD_es is Google-published, and COPA-es/OpenBookQA_es are IberoBench's own Spanish adaptations); readers should check each constituent dataset's own card before assuming a uniform licence applies to the group.

## Who publishes it

The IberoBench paper lists fifteen authors: Irene Baucells, Javier Aula-Blasco, Iria de-Dios-Flores, Silvia Paniagua Suárez, Naiara Perez, Anna Salles, Susana Sotelo Docio, Júlia Falcão, Jose Javier Saiz, Robiert Sepulveda Torres, Jeremy Barnes, Pablo Gamallo, Aitor Gonzalez-Agirre, German Rigau and Marta Villegas, published at COLING 2025 (bibkey `baucells-etal-2025-iberobench`). The group is affiliated with the Barcelona Supercomputing Center's Language Technologies Unit, which also publishes the parallel Basque, Catalan and Galician harness groups. The paper evaluated 33 existing LLMs across all five languages in zero- and five-shot settings.

## Lineage

SpanishBench is one of five parallel language slices of IberoBench; this repository separately documents [BasqueGLUE](basqueglue.md), an older, standalone nine-task Basque suite that predates IberoBench and is reused as one component inside IberoBench's Basque slice (`basque_bench`, not yet a page in this repository). SpanishBench has no predecessor of its own within this repository and no tracked successor.

## Saturation and contamination

The COLING 2025 paper evaluated 33 models zero- and five-shot, but a Spanish-specific aggregate top score was not extracted from a source opened for this page, since results are reported per task rather than as one blended figure; saturation status is therefore left unknown. Contamination risk is mixed and task-dependent: several constituent datasets (XNLI, PAWS-X, WNLI, XQuAD, FLORES, XL-Sum, XStoryCloze) are long-established, widely mirrored multilingual NLP benchmarks that plausibly appear in pretraining corpora for many current LLMs, while the two purpose-built tasks (COPA-es, OpenBookQA_es) are newer Spanish adaptations with comparatively less exposure.

## How to run it

lm-evaluation-harness runs the whole group with `--tasks spanish_bench`, which executes all fifteen constituent task yaml files listed in `spanish_bench.yaml` (version 1.2 as of research). Individual tasks can be run alone using their own names (for example `--tasks copa_es` or `--tasks flores_es`) for a narrower, more directly comparable result. No HELM, OpenCompass, inspect_evals or BIG-bench implementation of this specific fifteen-task Spanish group was found; several constituent datasets individually appear in other harnesses under their own names.

## Reading the numbers

A "SpanishBench" number is only meaningful if you know which constituent task or subset produced it; treat the group tag as a convenient way to run many tasks in one command, not as a single capability score. Strong performance on the older NLI/paraphrase tasks (XNLI, PAWS-X, WNLI) may partly reflect memorisation of long-public English-derived multilingual sets rather than genuine Spanish reasoning, so weight the newer, purpose-built tasks (COPA-es, OpenBookQA_es) and the generation tasks (FLORES_es, XL-Sum_es, MGSM_es) more heavily when judging real Spanish-language capability. Compare scores only when shot count (0-shot vs 5-shot) and the exact task subset match.
