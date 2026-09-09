---
id: french_bench
name: "FrenchBench"
aliases:
  - "French Bench"
page_kind: benchmark
category: composite
subcategory: "native and machine-translated French suite: generative QA/summarisation, multiple-choice reasoning and linguistics, translation"
status: active
summary: "An lm-evaluation-harness suite of about twenty French tasks mixing native resources (FQuAD, French Trivia, OrangeSum) with GPT-3.5-translated ones (HellaSwag, ARC-Challenge), from the CroissantLLM paper."
measures: >
  FrenchBench bundles roughly twenty French-language tasks into one lm-evaluation-harness group,
  covering generative QA and summarisation (FrenchBench Gen), multiple-choice reasoning, linguistics
  and knowledge (FrenchBench MC), and further extras (an XNLI French config, a French BoolQ, a
  topic-based sentiment task) not part of either core tagged set. Critically, the tasks are not
  uniformly native or translated: FQuAD-derived question answering, MultiFQuAD, French Trivia,
  OrangeSum summarisation and the grammar/vocabulary/reading tests were authored or curated directly
  in French, while French HellaSwag and French ARC-Challenge are GPT-3.5 machine translations of their
  English originals, and XNLI(fr) and Belebele(fr) are professionally translated multilingual sets
  with a French configuration. The paper's own authors are explicit that the machine-translated pair
  is imperfect: "manual verification of the translation quality indicates the translations to be far
  from perfect but sufficient... to act as a correct performance proxy."
task_format: >
  Varies by sub-task: 4- or 5-option multiple choice for HellaSwag(fr), ARC-Challenge(fr), the
  grammar/vocabulary/reading tests and XNLI(fr); binary classification for French BoolQ; extractive or
  short free-text generation, scored few-shot, for the FQuAD-derived QA tasks and French Trivia;
  single-sentence or first-paragraph generation for OrangeSum; and sentence-level machine translation
  for the WMT14 English-French pair. lm-evaluation-harness exposes tag groups `french_bench_gen`,
  `french_bench_mc`, `french_bench_perplexity` and `french_bench_extra` alongside the umbrella
  `french_bench` tag (non-perplexity tasks only).
metric:
  name: "varies by sub-task: accuracy/acc_norm for multiple-choice and classification tasks, exact-match/F1/ROUGE-1 for generative QA and summarisation, BLEU/COMET for translation"
  direction: higher_is_better
  unit: "%"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random or human baseline applies across a suite this heterogeneous. The introducing
    paper's own headline tables report FrenchBench MC as a 5-task average (Hellaswag-fr, Arc-c-fr,
    fr-vocab, fr-grammar, Belebele-fr) and FrenchBench Gen as a 5-task ROUGE-1 average (FGenQ, FGenAns,
    MultiFQuAD, OSum(A), FTrivia), evaluated 5-shot -- each constituent task's own baseline should be
    read individually rather than assumed from either group average.
dataset:
  size: null
  size_note: >
    No single official item count across the full suite was found. Individually confirmed sizes for
    three components read directly from Hugging Face: manu/french_bench_hellaswag has 9,338 rows in
    the validation split the harness reads, manu/french_bench_arc_challenge has 2,585, and
    manu/french-trivia has 380. The remaining components (FQuAD-derived sets, OrangeSum, XNLI, the
    grammar/vocab/reading test) were not individually counted for this page.
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/french_bench"
  license: >
    Varies by sub-task: manu/fquad2_test is Apache-2.0 and manu/french-bench-grammar-vocab-reading is
    MIT (both per their Hugging Face cards); French Trivia is separately stated in the paper as
    MIT-licensed and MultiFQuAD's evaluation set as CC-BY-NC-SA 4.0; several `manu/`-hosted component
    cards (french_boolq, topic_based_nli_test, multifquad_test, french-trivia,
    french_bench_hellaswag, french_bench_arc_challenge) carry no machine-readable licence tag at all.
    This page did not check every component individually, so one suite-wide licence is not established.
  languages:
    - fr
  modalities:
    - text
  splits: >
    Varies by sub-task; most components read a "valid"/"validation" split rather than a held-out test
    split (confirmed from the harness YAML configs), so answers are effectively public for the great
    majority of tasks.
  public_test_set: null
publisher:
  org: >
    CroissantLLM project: core academic authors affiliated with CentraleSupelec (Universite Paris
    Saclay) and Instituto Superior Tecnico de Lisboa, with further contributors at Sorbonne Universite
    and Imperial College London; core industrial authors funded by Illuin Technology (Paris), Unbabel
    (Lisboa) and Equall (New York, Lisboa, Paris) -- all per the paper's own acknowledgements.
  authors:
    - "Manuel Faysse"
    - "Patrick Fernandes"
    - "Nuno M. Guerreiro"
    - "Antonio Loison"
    - "Duarte M. Alves"
    - "Caio Corro"
    - "Nicolas Boizard"
    - "Joao Alves"
    - "Ricardo Rei"
    - "Pedro H. Martins"
    - "Antoni Bigata Casademunt"
    - "Francois Yvon"
    - "Andre F. T. Martins"
    - "Gautier Viaud"
    - "Celine Hudelot"
    - "Pierre Colombo"
  url: "https://github.com/ManuelFay/CroissantLLM"
paper:
  title: "CroissantLLM: A Truly Bilingual French-English Language Model"
  arxiv: "2402.00786"
  url: "https://arxiv.org/abs/2402.00786"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/french_bench"
released: "2024-02"
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
    No maintained leaderboard for FrenchBench was found. The introducing paper's own 5-shot baseline
    comparison (Feb 2024, models from 1B to 7B parameters) shows Mistral-7B highest on both group
    averages -- 0.66 on FrenchBench MC and 0.56 on FrenchBench Gen (ROUGE-1), against CroissantLLM
    1.3B's 0.50 and 0.31 respectively -- with clear separation between models rather than ceiling
    clustering, but that comparison predates current frontier models entirely and used only a five-task
    subset of each tag group, so it is reported here as historical context rather than a current
    top_score.
contamination:
  risk: medium
  note: >
    Exposure varies sharply by component rather than being uniform: WMT14 (2014) and XNLI (2018) have
    been public for roughly a decade or more and are widely mirrored; OrangeSum (2020) and FQuAD (2020)
    are several years old; Belebele (2023) is newer; and French Trivia, the grammar/vocabulary/reading
    test, MultiFQuAD's evaluation set, and the GPT-3.5-translated HellaSwag/ARC-Challenge pair were all
    released alongside the paper in 2024. No publisher statement or independent contamination study
    covering the suite as a whole was found.
harness:
  lm_eval: >
    french_bench (group, non-perplexity tasks); tags french_bench_gen, french_bench_mc,
    french_bench_perplexity, french_bench_extra; constituent tasks include french_bench_boolqa,
    french_bench_fquadv2, french_bench_fquadv2_bool, french_bench_fquadv2_genq,
    french_bench_fquadv2_hasAns, french_bench_grammar, french_bench_hellaswag,
    french_bench_arc_challenge, french_bench_multifquad, french_bench_opus_perplexity,
    french_bench_orangesum_abstract, french_bench_orangesum_title, french_bench_reading_comp,
    french_bench_topic_based_nli, french_bench_trivia, french_bench_vocab,
    french_bench_wikitext_fr, french_bench_xnli, plus belebele_fra_Latn, wmt14-en-fr, wmt14-fr-en and
    crows_pairs_french from elsewhere in the harness.
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No HELM, OpenCompass or inspect_evals implementation of the group was found (checked directly:
    each returned 404 at its likely path).
tags:
  - composite
  - french
  - multilingual
  - machine-translation
  - question-answering
  - summarisation
  - nli
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/french_bench/README.md"
    title: "lm-evaluation-harness french_bench task group README"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.00786"
    title: "CroissantLLM: A Truly Bilingual French-English Language Model"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.00786"
    title: "CroissantLLM, full text (ar5iv) -- FrenchBench construction, task tables, results"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/french_bench/french_bench_hellaswag.yaml"
    title: "lm-evaluation-harness french_bench_hellaswag.yaml (dataset_path manu/french_bench_hellaswag)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/french_bench/french_bench_arc_challenge.yaml"
    title: "lm-evaluation-harness french_bench_arc_challenge.yaml"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/manu/french_bench_hellaswag"
    title: "manu/french_bench_hellaswag dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=manu/french_bench_hellaswag"
    title: "manu/french_bench_hellaswag row count, Hugging Face datasets-server (9,338 rows)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=manu/french_bench_arc_challenge"
    title: "manu/french_bench_arc_challenge row count, Hugging Face datasets-server (2,585 rows)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=manu/french-trivia"
    title: "manu/french-trivia row count, Hugging Face datasets-server (380 rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/manu/fquad2_test"
    title: "manu/fquad2_test dataset metadata, Hugging Face API (licence: apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/manu/french-bench-grammar-vocab-reading"
    title: "manu/french-bench-grammar-vocab-reading dataset metadata, Hugging Face API (licence: mit)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

FrenchBench bundles roughly twenty French-language tasks into one lm-evaluation-harness group, built to
assess French text understanding and generation across several skills rather than one. Its introducing
paper, CroissantLLM, splits the suite into FrenchBench Gen (generative QA and summarisation, scored
few-shot) and FrenchBench MC (multiple-choice reasoning, linguistics and knowledge), with further
extras -- an XNLI French configuration, a French BoolQ, a topic-based sentiment task -- added to the
harness outside either core tagged set.

Provenance is genuinely mixed, and matters for how a score should be read. FQuAD-derived question
answering, MultiFQuAD, French Trivia, OrangeSum summarisation and the grammar/vocabulary/reading tests
were authored or curated directly in French. French HellaSwag and French ARC-Challenge, by contrast,
are GPT-3.5 machine translations of their English originals: the paper's own authors state plainly that
"manual verification of the translation quality indicates the translations to be far from perfect but
sufficient... to act as a correct performance proxy." XNLI(fr) and Belebele(fr) sit in between, as
professionally translated multilingual sets with a French configuration rather than French-native or
machine-translated constructions. One further wrinkle: French Trivia's questions are deliberately posed
in English, not French, specifically so monolingual English models could be tested on French cultural
knowledge on equal footing -- the paper notes this makes the task unusable for French-only models such
as GPT-fr and Pagnol-XL.

## How it is scored

Scoring is task-dependent. Multiple-choice tasks (HellaSwag-fr, ARC-Challenge-fr, the
grammar/vocabulary/reading tests, XNLI-fr) use accuracy or length-normalised accuracy. Generative tasks
score with exact-match and F1 (the FQuAD-derived question-answering tasks) or ROUGE-1 (French Trivia,
MultiFQuAD, OrangeSum abstract generation), typically in a 5-shot setting. The WMT14 English-French pair
is scored with BLEU and COMET. No single random or human baseline covers the whole suite; the paper's
own headline numbers are two 5-task group averages -- FrenchBench MC over Hellaswag-fr, Arc-c-fr,
fr-vocab, fr-grammar and Belebele-fr, and FrenchBench Gen (ROUGE-1) over FGenQ, FGenAns, MultiFQuAD,
OSum(A) and FTrivia -- narrower than the full ~20-task harness group.

## Dataset and licence

No single official item count across the full suite was found. Individually confirmed component sizes:
manu/french_bench_hellaswag has 9,338 rows in the validation split the harness reads,
manu/french_bench_arc_challenge has 2,585, and manu/french-trivia has 380. Licensing is fragmented
rather than uniform: manu/fquad2_test is Apache-2.0, manu/french-bench-grammar-vocab-reading is MIT,
French Trivia is stated as MIT in the paper, and MultiFQuAD's evaluation set is CC-BY-NC-SA 4.0, while
several other `manu/`-hosted component cards carry no machine-readable licence tag at all. Most
components read from a "valid" or "validation" split rather than a held-out test split, so answers are
effectively public for the great majority of tasks.

## Who publishes it

FrenchBench was introduced alongside CroissantLLM by Manuel Faysse and fifteen co-authors, posted to
arXiv in February 2024. Core academic authors are affiliated with CentraleSupelec (Universite Paris
Saclay) and Instituto Superior Tecnico de Lisboa, with further contributors at Sorbonne Universite and
Imperial College London; core industrial authors are funded by Illuin Technology (Paris), Unbabel
(Lisboa) and Equall (New York, Lisboa, Paris). The task group is maintained inside EleutherAI's
lm-evaluation-harness rather than a standalone leaderboard site.

## Lineage

FrenchBench has no predecessor or successor tracked in this repository. It belongs to the same broad
pattern as this repository's [CatalanBench](catalan_bench.md) and [BasqueBench](basque_bench.md) --
regional/national-language suites assembled from a mix of purpose-built and repurposed multilingual
datasets under one evaluation umbrella -- but is an independent project with its own paper and authors,
not part of the IberoBench family those two belong to. Unlike CatalanBench and BasqueBench, which are
built largely from professional human translations, FrenchBench's own headline weak point is a
machine-translated pair (HellaSwag-fr, ARC-Challenge-fr) that the authors themselves flag as imperfect.

## Saturation and contamination

No maintained leaderboard for FrenchBench was found. The introducing paper's own 5-shot comparison
(February 2024, models from 1B to 7B parameters) shows Mistral-7B highest on both group averages --
0.66 on FrenchBench MC and 0.56 on FrenchBench Gen -- with clear separation between models rather than
ceiling clustering, but this predates current frontier models and covers only a five-task subset of
each tag group, so it is offered as historical context rather than a current reading. Contamination
risk is medium and uneven: WMT14 (2014) and XNLI (2018) are roughly a decade old and widely mirrored,
OrangeSum and FQuAD are from 2020, Belebele is from 2023, and French Trivia, the grammar/vocabulary
test, MultiFQuAD's evaluation set and the machine-translated HellaSwag/ARC-Challenge pair were all first
released alongside the 2024 paper.

## How to run it

The task group lives in EleutherAI's lm-evaluation-harness at `lm_eval/tasks/french_bench/`, runnable
as the umbrella `french_bench` tag (non-perplexity tasks) or via the `french_bench_gen`,
`french_bench_mc`, `french_bench_perplexity` and `french_bench_extra` tags. No HELM, OpenCompass or
inspect_evals implementation was found. Because the group mixes accuracy-, F1-, ROUGE- and
BLEU/COMET-scored tasks, a single averaged "FrenchBench score" is not something the harness defines on
its own; a reporter must state which tasks and which of the paper's two named groups (MC or Gen) it
used.

## Reading the numbers

A strong FrenchBench result suggests broad French competence across reasoning, linguistics, QA,
summarisation and translation, but the suite's mixed provenance means the number is only as reliable as
its weakest component: scores on French HellaSwag and French ARC-Challenge reflect performance on
admittedly imperfect machine-translated text, not native French. Because French Trivia's prompts are in
English, a strong score there measures French cultural knowledge rather than French reading ability, and
is not comparable to a French-only model's score on that task. Given no combined public leaderboard was
found, treat any single reported "FrenchBench" figure as one reporter's own choice of sub-tasks and check
which ones -- and whether MC, Gen, or both -- it drew from before comparing it to another.
