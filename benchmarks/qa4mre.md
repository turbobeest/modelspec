---
id: qa4mre
name: "QA4MRE"
aliases:
  - "Question Answering for Machine Reading Evaluation"
  - "qa4mre_2011"
  - "qa4mre_2012"
  - "qa4mre_2013"
page_kind: benchmark
category: reasoning
subcategory: "CLEF multiple-choice reading comprehension over a single document"
status: unknown
summary: >
  CLEF 2011–2013 reading-comprehension lab: five-way questions about one
  document, shipped in lm-eval as English main-track sets for each year.
measures: >
  QA4MRE tests whether a system can read one short document and pick the
  correct answer among five candidates. Organisers wrote the questions to
  require paraphrase, coreference, and sometimes facts from a background
  collection on the same topic (AIDS, climate change, music and society,
  Alzheimer's). lm-eval ships only the English main-track configs for 2011,
  2012, and 2013. It does not run the Alzheimer's, entrance-exam, or
  modality/negation pilots, and it does not use the original c@1 metric that
  rewarded leaving a question unanswered.
task_format: >
  Multiple choice. Prompt is the document plus the question; choices come from
  answer_options.answer_str. Target index is correct_answer_id minus one.
  lm-eval output_type is multiple_choice on the Hub train split of each year.
metric:
  name: "accuracy (acc and acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20
  human_baseline: null
  baseline_note: >
    Five candidates give a 20% chance rate. The CLEF lab scored c@1, which
    treats an unanswered item differently from a wrong guess. lm-eval reports
    mean acc and length-normalised acc_norm only. No human c@1 or accuracy
    figure was read from the overview paper's opening pages.
dataset:
  size: 564
  size_note: >
    lm-eval English main configs on community-datasets/qa4mre: 2011.main.EN
    120, 2012.main.EN 160, 2013.main.EN 284 (564 questions). The Hub snapshot
    as a whole has 3,266 rows across 20 language/year configs, including
    Alzheimer's and entrance-exam pilots that the harness does not run. The
    2013 overview describes 240 Main questions plus 44 Auxiliary items per
    language; 240+44=284, matching the Hub 2013.main.EN split the harness
    loads (Main and Auxiliary together, not Main only).
  url: "https://huggingface.co/datasets/community-datasets/qa4mre"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "lm-eval uses each year's Hub train split as the eval set (no held-out test); 2011.main.EN 120 / 2012.main.EN 160 / 2013.main.EN 284"
  public_test_set: true
publisher:
  org: "UNED NLP&IR Group (CLEF QA4MRE lab)"
  authors:
    - "Anselmo Peñas"
    - "Eduard Hovy"
    - "Pamela Forner"
    - "Álvaro Rodrigo"
    - "Richard Sutcliffe"
    - "Roser Morante"
  url: "http://nlp.uned.es/clef-qa/repository/qa4mre.php"
paper:
  title: "QA4MRE 2011-2013: Overview of Question Answering for Machine Reading Evaluation"
  arxiv: ""
  url: "https://link.springer.com/chapter/10.1007/978-3-642-40802-1_29"
  year: 2013
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/qa4mre"
released: "2011"
last_updated: "2013"
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
    The CLEF lab ended in 2013. No current lm-eval leaderboard for the qa4mre
    group was found. Historical c@1 figures from working notes were not
    extracted as a single comparable top score.
contamination:
  risk: high
  note: >
    Main-track documents, questions, and gold answers have been public since
    the 2011–2013 campaigns and sit on Hugging Face with answers in the only
    split. Background collections were crawled from news and Wikipedia on
    the same topics.
harness:
  lm_eval: "qa4mre (tag group: qa4mre_2011, qa4mre_2012, qa4mre_2013)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Dataset community-datasets/qa4mre configs 2011.main.EN, 2012.main.EN,
    2013.main.EN. should_decontaminate is true. Original CLEF metric is c@1,
    not acc.
tags:
  - reading-comprehension
  - multiple-choice
  - clef
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/qa4mre/README.md"
    title: "lm-evaluation-harness qa4mre README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/qa4mre/qa4mre_2011.yaml"
    title: "lm-eval qa4mre_2011.yaml (multiple_choice, acc/acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/qa4mre/qa4mre_2012.yaml"
    title: "lm-eval qa4mre_2012.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/qa4mre/qa4mre_2013.yaml"
    title: "lm-eval qa4mre_2013.yaml"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/community-datasets/qa4mre"
    title: "Hugging Face community-datasets/qa4mre card (split sizes, licence unknown)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=community-datasets/qa4mre"
    title: "Hugging Face datasets-server size for qa4mre configs"
    accessed: "2026-09-08"
  - url: "https://www.cs.cmu.edu/~hovy/papers/13CLEF-QA4MRE.pdf"
    title: "Peñas et al. CLEF 2013 overview PDF"
    accessed: "2026-09-08"
  - url: "http://nlp.uned.es/clef-qa/repository/qa4mre.php"
    title: "UNED QA4MRE lab page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-067 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-067"
---

## What it measures

QA4MRE is a reading-comprehension exam over one document at a time. The model sees a passage, a question, and five answers, and must pick the gold option. Questions were written to need more than string overlap: purpose, method, causal, factoid, and which-is-true types, with some items requiring a fact from a topic background corpus.

lm-eval's English main tasks are the reusable CLEF tests, not the Alzheimer's scientific-language pilot, not Tokyo entrance exams, and not the standalone modality/negation labelling task. Those extra tracks exist on the Hub and in the 2013 overview, but they are outside this harness group.

## How it is scored

lm-eval scores multiple-choice accuracy and length-normalised accuracy. Chance is 20% with five options. The gold index is `correct_answer_id` minus one.

CLEF used c@1 so a system could return NoA instead of guessing. A modern acc number is therefore not the campaign ranking. Year-by-year tasks are not pooled in the YAML; a `qa4mre` group mean is a tag aggregate of 2011+2012+2013 English, which have different sizes.

## Dataset and licence

English main-track sizes on the Hub are 120 (2011), 160 (2012), and 284 (2013). The 2013 284-row split matches the overview's 240 Main plus 44 Auxiliary questions. The Hub card tags the licence as unknown. The overview says 2013 test documents were taken from copyright-free sources or by permission, then translated; that is not an SPDX grant for redistribution. Treat reuse as unset unless you have the CLEF release terms.

Answers are in the only split. lm-eval evaluates that split. Parallel translations exist for Arabic, Bulgarian, German, Spanish, Italian, and Romanian; the harness does not load them.

## Who publishes it

The lab was run at CLEF 2011–2013 by UNED with co-organisers at CMU, CELCT, Essex, and Antwerp. The overview is Peñas, Hovy, Forner, Rodrigo, Sutcliffe, and Morante, Springer LNCS 8138 (2013). The living lab page is at UNED. There is no current official leaderboard.

## Lineage

QA4MRE replaced earlier CLEF QA pipelines that the authors say stalled near 60% because retrieval errors dominated. It is a multiple-choice reading test, not [boolq](boolq.md) yes/no, not [coqa](coqa.md) dialogue, and not [drop](drop.md) discrete reasoning over Wikipedia.

[headqa](headqa.md) is a later multilingual exam-style set and is not a successor. The 2013 entrance-exam pilot overlaps NTCIR Todai Robot work; that pilot is not this id.

## Saturation and contamination

The shared task is finished. Whether today's models sit on the ceiling of the 564 English items is not established from a current table. The items and keys have been public for more than a decade, so contamination risk is high. Background crawls included Wikipedia and news on the same topics.

## How to run it

`lm_eval --tasks qa4mre` uses the tag group, or run `qa4mre_2011`, `qa4mre_2012`, and `qa4mre_2013` separately. Data is `community-datasets/qa4mre` with names `2011.main.EN`, `2012.main.EN`, and `2013.main.EN`. Decontamination is enabled against document plus question text.

Do not compare acc to published c@1. Do not mix Alzheimer's or entrance-exam configs into the group without saying so.

## Reading the numbers

A high acc on 2011's 120 items is a small English reading test, not a modern long-context exam. 2013 is larger and includes "None of the above" items in the original design. Report the year. If you need a live reading-comprehension number, look at [drop](drop.md) or [coqa](coqa.md) rather than treating this CLEF snapshot as current SOTA.
