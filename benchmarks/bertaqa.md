---
id: bertaqa
name: "BertaQA"
aliases: []
page_kind: benchmark
category: knowledge
subcategory: "parallel Basque/English trivia testing local (Basque-culture) versus global knowledge"
status: active
summary: "4,756 three-choice trivia questions, parallel in Basque and English and split almost evenly between Basque-local and general-global topics, to isolate what a model knows about one specific culture."
measures: >
  BertaQA is a multiple-choice trivia dataset built specifically to separate two kinds of knowledge
  that most benchmarks conflate: general "global" world knowledge, and "local" knowledge specific to
  one under-represented culture, here the Basque Country. Every question exists in parallel Basque
  and English versions, with the English version produced by professional human translation (plus
  several machine-translated variants used for ablation), so the same 4,756 questions can be asked in
  either language. The dataset's own release splits questions almost evenly into a "global" subset
  (2,392 questions, general-interest trivia) and a "local" subset (2,364 questions, requiring specific
  knowledge of Basque history, culture and society) -- confirmed directly by reading the released
  data's own `group` field rather than the paper's rounded description. This local/global split is the
  entire point of the benchmark: the authors use it to show that state-of-the-art LLMs do well on
  global topics but struggle specifically on local ones, and that continued pre-training in Basque
  measurably improves a model's local-topic performance even when the model is later queried in
  English -- evidence, the authors argue, of knowledge transfer from a low-resource to a high-resource
  language.
task_format: >
  Three-option multiple-choice trivia (one correct answer, two distractors), evaluated zero-shot and
  few-shot. Each question also carries a category (one of eight) and a difficulty label. Besides the
  human-translated Basque (`eu`) and English (`en`) configs, the release ships eight further
  `en_mt_*` configs, the same questions machine-translated into English by different systems and
  models (NLLB, MADLAD, Latxa at several sizes, Llama 2 at several sizes, Gemma-7B), used to separate
  translation-quality effects from knowledge effects.
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.33
  human_baseline: null
  baseline_note: >
    33.33% is the three-option random-guess rate. No human baseline is reported by the authors.
    lm-evaluation-harness draws few-shot exemplars from the same `test` split as the evaluation items
    (excluding the current item), since no separate training or development split is released.
dataset:
  size: 4756
  size_note: >
    4,756 multiple-choice questions, confirmed by downloading the released `eu` config and counting
    rows directly. The dataset's own `group` field splits them 2,392 "Gai orokorrak" (general/global)
    to 2,364 "Euskal gaiak" (Basque/local) -- close to even, but not the exact 50/50 split the paper's
    prose implies. Eight categories are roughly balanced at 581-615 questions each (Geography and
    History 600, Cinema and Shows 597, Basque and Literature 615, Science and Technology 588, Sports
    and Leisure 599, Culture and Art 581, Music and Dance 589, Society and Traditions 587). Difficulty
    is recorded as three numeric levels (1: 1,686; 2: 1,733; 3: 1,337 questions); the dataset card's
    prose describes these as easy, medium and hard with roughly 80 hard questions per category-subset
    combination, consistent with level 3 being "hard," though this page did not find an explicit
    number-to-label mapping to confirm which of levels 1 and 2 is "easy" versus "medium."
  url: "https://huggingface.co/datasets/HiTZ/BertaQA"
  license: "Stated two ways: the Hugging Face card's own metadata tags give CC BY 4.0, while the same card's free-text \"License\" field literally reads \"[More Information Needed]\"; this page records both rather than picking one."
  languages:
    - eu
    - en
  modalities:
    - text
  splits: "single `test` split per language/translation config (eu, en, and 8 en_mt_* machine-translation variants); no dedicated train or dev split"
  public_test_set: true
publisher:
  org: "HiTZ Center - Ixa, University of the Basque Country (UPV/EHU)"
  authors:
    - "Julen Etxaniz"
    - "Gorka Azkune"
    - "Aitor Soroa"
    - "Oier Lopez de Lacalle"
    - "Mikel Artetxe"
  url: "https://github.com/juletx/BertaQA"
paper:
  title: "BertaQA: How Much Do Language Models Know About Local Culture?"
  arxiv: "2406.07302"
  url: "https://arxiv.org/abs/2406.07302"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/juletx/BertaQA"
released: "2024-06"
last_updated: ""
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
    No current leaderboard was found during this research, so no top score is recorded, but the
    paper's own headline result establishes real, uneven headroom: state-of-the-art LLMs at release
    performed well on the global subset while struggling specifically on the local subset, and
    continued pre-training in Basque closed part of that gap. A single overall accuracy figure
    therefore hides the benchmark's real story; the local/global gap for a given model is more
    informative than either number alone.
contamination:
  risk: medium
  note: >
    The authors report a specific mitigation check rather than an assumption: they searched Google
    for exact question text and found no results, and state that the dataset "was originally compiled
    in Basque by crawling public sources that are no longer available," arguing this makes prior
    model exposure unlikely though not impossible to rule out categorically. Against that, the
    questions and answers have been openly downloadable since June 2024, over two years by this
    page's research date, with no held-out or refreshed portion described.
harness:
  lm_eval: "bertaqa (group over bertaqa_eu, bertaqa_en and ten bertaqa_en_mt_* machine-translation variants)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - knowledge
  - trivia
  - multiple-choice
  - basque
  - local-culture
  - cross-lingual
  - low-resource
sources:
  - url: "https://arxiv.org/abs/2406.07302"
    title: "BertaQA: How Much Do Language Models Know About Local Culture?"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bertaqa/README.md"
    title: "lm-evaluation-harness bertaqa task README (includes paper abstract and citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bertaqa/_bertaqa_template"
    title: "lm-evaluation-harness bertaqa shared task template"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bertaqa/bertaqa_eu.yaml"
    title: "lm-evaluation-harness bertaqa_eu task config"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HiTZ/BertaQA/raw/main/README.md"
    title: "HiTZ/BertaQA dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HiTZ/BertaQA"
    title: "HiTZ/BertaQA dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HiTZ/BertaQA/resolve/main/eustrivia_zuzenduta.jsonl"
    title: "HiTZ/BertaQA Basque (eu) data file, downloaded and counted directly for size, group and category figures"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/juletx/BertaQA/main/README.md"
    title: "juletx/BertaQA reference repository README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BertaQA is a multiple-choice trivia dataset built specifically to separate two kinds of knowledge that most knowledge benchmarks conflate: general "global" world knowledge, and "local" knowledge specific to one under-represented culture -- here, the Basque Country. Every one of its 4,756 questions exists in parallel Basque and English versions (the English produced by professional human translation), so the same items can be asked in either language. That is the benchmark's whole point: the authors use the split to show that state-of-the-art LLMs handle global-topic questions well while specifically struggling with local ones, and that continued pre-training in Basque measurably improves a model's local-topic score even when the model is later queried in English -- evidence, they argue, of knowledge transfer from a low-resource into a high-resource language.

Reading the released data directly (rather than the paper's rounded description) shows the local/global split is close to even but not exact: 2,364 questions are labelled "Euskal gaiak" (Basque/local topics) against 2,392 labelled "Gai orokorrak" (general/global topics). Questions are also organised into eight roughly balanced categories -- Basque and Literature, Geography and History, Society and Traditions, Sports and Leisure, Culture and Art, Music and Dance, Science and Technology, and Cinema and Shows -- and three difficulty levels.

## How it is scored

Each item is three-option multiple choice (one correct answer, two distractors), so random guessing scores 33.33%. No human baseline is reported. Because BertaQA ships no separate training split, lm-evaluation-harness draws few-shot exemplars from the same `test` split as the scored items, excluding whichever item is currently being asked. Beyond the human-translated `eu` and `en` configs, the release adds eight `en_mt_*` configs -- the same 4,756 questions machine-translated into English by different systems (NLLB, MADLAD) and by several sizes of Latxa, Llama 2 and Gemma-7B -- specifically so a drop in English-language local-knowledge accuracy can be attributed to translation quality rather than to the model's own knowledge.

## Dataset and licence

The dataset totals 4,756 questions, confirmed here by downloading the released Basque config directly and counting rows rather than trusting the paper's summary. The eight categories are close to evenly sized (581 to 615 questions each), and the three numeric difficulty levels split 1,686 / 1,733 / 1,337 -- consistent with the dataset card's description of roughly 80 "hard" questions per category-subset combination corresponding to the smallest group (level 3), though this page could not confirm from a source which of levels 1 and 2 maps to "easy" versus "medium." The licence is stated two different ways on the same Hugging Face card: its structured metadata tags give CC BY 4.0, while its own free-text "License" field literally reads "[More Information Needed]." This page records both rather than resolving the conflict.

## Who publishes it

BertaQA comes from Julen Etxaniz, Gorka Azkune, Aitor Soroa, Oier Lopez de Lacalle and Mikel Artetxe at the HiTZ Center (Ixa research group, University of the Basque Country, UPV/EHU), posted to arXiv in June 2024 and accepted to the NeurIPS 2024 Datasets and Benchmarks track. The authors maintain the reference repository at `github.com/juletx/BertaQA` and the dataset on Hugging Face under the `HiTZ` organisation.

## Lineage

BertaQA has no predecessor or successor tracked in this repository, and it is not part of [BasqueBench](basque_bench.md) (also in this repository): BasqueBench's own task list, drawn from the IberoBench project, includes a same-topic-area trivia dataset called EusTrivia (from the earlier Latxa paper, also HiTZ-affiliated) but not BertaQA itself -- two related but separate Basque trivia artefacts from overlapping authors, easy to conflate. BertaQA is closer in spirit to this repository's [GreekMMLU](greekmmlu.md) and [CMMLU](cmmlu.md), both native-language knowledge benchmarks for under-represented languages, but its distinguishing feature is structural: where GreekMMLU and CMMLU mix in some locally-specific subjects among many general-academic ones, BertaQA is built from the ground up as a controlled local-versus-global comparison on the same question format and difficulty distribution.

## Saturation and contamination

No current leaderboard was found during this research, so this page records no top score, but the paper's own release-time finding establishes real and uneven headroom: strong performance on the global subset alongside a specific, measurable gap on the local subset for most evaluated models, a gap that continued Basque pre-training narrows but does not close. A single averaged accuracy figure hides this story -- the local/global gap for a given model is more informative than either number alone. Contamination risk is medium: the authors specifically checked that exact question text returns no Google results and describe the source material as crawled from public pages "no longer available," which argues against prior exposure without ruling it out, while the data itself has been openly downloadable with answers for over two years by this page's research date.

## How to run it

lm-evaluation-harness implements BertaQA as a `bertaqa` task group covering `bertaqa_eu`, `bertaqa_en`, and ten `bertaqa_en_mt_*` variants, each pointing at a different Hugging Face config of the same underlying questions. Because the `en` and `en_mt_*` configs differ only in translation source, a score reported simply as "BertaQA (English)" is ambiguous until the specific config is confirmed -- human-translated `en` and machine-translated `en_mt_*` scores are not the same measurement.

## Reading the numbers

A high overall BertaQA score is less informative here than the gap between its local and global subsets: a model that scores well on global trivia but drops sharply on Basque-local trivia is demonstrating exactly the anglocentric-knowledge pattern the benchmark was built to expose, not a general knowledge weakness. A model that narrows that gap, especially without being explicitly trained on Basque-language local content, is showing the kind of cross-lingual knowledge transfer the authors set out to measure. Because the released test data is shared across few-shot sampling and scoring, and because English-language scores can come from human or machine translation, confirm both the specific config and the local/global breakdown before comparing two reported BertaQA numbers.
