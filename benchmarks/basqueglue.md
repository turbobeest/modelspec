---
id: basqueglue
name: "BasqueGLUE"
aliases:
  - "Basque GLUE"
  - "orai-nlp/basqueGLUE"
page_kind: benchmark
category: composite
subcategory: "nine-task Basque NLU suite (NER, dialogue, topic, sentiment, stance, QNLI, WiC, coreference)"
status: active
summary: "Nine-task Basque NLU suite in the GLUE mould, spanning NER, dialogue, topic, sentiment, stance, QNLI, word-in-context and coreference."
measures: >
  BasqueGLUE scores Basque language understanding across nine tasks built from existing and
  newly adapted datasets, following GLUE and SuperGLUE design rules. Tasks include in- and
  out-of-domain NER, FMTOD intent classification and slot filling, news topic classification
  (BHTCv2), election-tweet sentiment (BEC2016eu), vaccine-stance detection, QNLI-style QA
  entailment, word-in-context, and binary coreference. The original evaluation fine-tunes
  encoder models per task and averages the nine scores.
task_format: >
  Mixed: token-level sequence labelling (NER, slots); single-text classification (topic,
  sentiment, stance, intent); sentence-pair classification (QNLI, WiC, coreference). lm-eval
  implements six of the nine as Basque-prompted multiple-choice tasks and does not include
  NER or FMTOD.
metric:
  name: "unweighted average of per-task scores (F1 or accuracy by task)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper and GitHub report encoder averages of 73.23 (BERTeus) and 73.71 (ElhBERTeu) after
    per-task fine-tuning. Metrics are micro-F1 except VaxxStance (macro-F1 of FAVOR/AGAINST)
    and QNLI, WiC, coreference (accuracy). NER in the average is the mean of in-domain and
    out-of-domain F1. No single random baseline applies across this mix. lm-eval does not
    compute that nine-task average.
dataset:
  size: null
  size_note: >
    Not one item pool. Paper Table 1 (and the GitHub/HF README) lists per-task train/val/test
    sizes. Sequence-labelling rows are token counts (NERC, slots); the others are example
    counts. WiCeu train alone is 408,559 pairs, which drives the Hugging Face
    100K<n<1M size tag. Summing those rows as "items" would mix tokens with examples.
  url: "https://huggingface.co/datasets/orai-nlp/basqueGLUE"
  license: "mixed: most tasks CC BY-NC-SA 4.0; QNLIeu CC BY-SA 4.0; VaxxStance CC BY 4.0 plus Twitter terms; BEC2016eu Twitter terms plus CC BY-NC-SA 4.0"
  languages:
    - eu
  modalities:
    - text
  splits: "per-task train / validation / test as in Table 1; test sets are public"
  public_test_set: true
publisher:
  org: "orai NLP Technologies (Elhuyar) and HiTZ Center - Ixa, University of the Basque Country (UPV/EHU)"
  authors:
    - "Gorka Urbizu"
    - "Iñaki San Vicente"
    - "Xabier Saralegi"
    - "Rodrigo Agerri"
    - "Aitor Soroa"
  url: "https://github.com/orai-nlp/BasqueGLUE"
paper:
  title: "BasqueGLUE: A Natural Language Understanding Benchmark for Basque"
  arxiv: ""
  url: "https://aclanthology.org/2022.lrec-1.172/"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/orai-nlp/BasqueGLUE"
released: "2022-06"
last_updated: "2024-04"
lineage:
  family: ""
  predecessor: "glue"
  successors: []
  variants:
    - basque_bench
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    2022 encoder averages sit near 74 after fine-tuning. That is not an LLM zero-shot ceiling.
    The Latxa paper (arXiv:2403.20266) later uses BasqueGLUE for decoder models; those scores
    were not extracted for this page. No current public LLM leaderboard was opened.
contamination:
  risk: medium
  note: >
    Test sets are public, as SuperGLUE-style design required. Several source corpora (news,
    Wikipedia, tweets, Wordnet) predate 2022 and may appear in Basque pretraining. No
    rotating held-out set is described. Tweet tasks also carry Twitter terms of use.
harness:
  lm_eval: "basque-glue"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Runnable lm-eval tasks: bhtc_v2, bec2016eu, vaxx_stance, qnlieu, wiceu, epec_koref_bin. Tag basque-glue runs those six and does not average. NER and FMTOD are omitted."
tags:
  - basque
  - nlu
  - glue
  - classification
  - low-resource
sources:
  - url: "https://aclanthology.org/2022.lrec-1.172/"
    title: "ACL Anthology page, LREC 2022"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.lrec-1.172.pdf"
    title: "BasqueGLUE LREC 2022 PDF (nine tasks, Table 1 sizes, CC-BY-NC paper licence)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/orai-nlp/BasqueGLUE/main/README.md"
    title: "orai-nlp/BasqueGLUE README (task table, per-task licences, encoder results)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/orai-nlp/basqueGLUE/raw/main/README.md"
    title: "orai-nlp/basqueGLUE dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/orai-nlp/basqueGLUE"
    title: "Hugging Face dataset API (language eu, lastModified 2024-04-08)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basqueglue/README.md"
    title: "lm-eval basqueglue README (six tasks, tag basque-glue, Latxa citation)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basqueglue/bhtc.yaml"
    title: "lm-eval bhtc_v2.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basqueglue/bec.yaml"
    title: "lm-eval bec2016eu.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basqueglue/qnli.yaml"
    title: "lm-eval qnlieu.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basqueglue/wic.yaml"
    title: "lm-eval wiceu.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basqueglue/vaxx.yaml"
    title: "lm-eval vaxx_stance.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/basqueglue/coref.yaml"
    title: "lm-eval epec_koref_bin.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/orai-nlp/BasqueGLUE/main/eval_basqueglue.py"
    title: "Official eval_basqueglue.py (per-task prediction vs test.jsonl)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-027 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-027"
---

## What it measures

BasqueGLUE is a Basque NLU suite, not a single skill test. A model is scored on nine tasks that together cover named-entity recognition, task-oriented dialogue (intent and slots), news-topic classification, tweet sentiment, vaccine stance, question-answer entailment, word-sense in context, and mention coreference. The LREC 2022 paper says the authors followed GLUE and SuperGLUE selection rules and reused Basque datasets where they could, adding new splits where they could not. Language is Basque (`eu`) throughout.

lm-eval's `basqueglue` directory is a decoder-oriented slice of that suite: six multiple-choice tasks with Basque prompts. It drops NER and the FMTOD dialogue pair. A number from `--tasks basque-glue` is not the paper's nine-task encoder average.

## How it is scored

The reference script `eval_basqueglue.py` compares a prediction file to each task's `test.jsonl`. Headline metric in the paper is an unweighted average of the nine task scores. NER contributes the mean of in-domain and out-of-domain F1. VaxxStance uses macro-F1 on FAVOR and AGAINST only. QNLI, WiC and coreference use accuracy. The 2022 baselines fine-tune BERTeus and ElhBERTeu separately on each task.

lm-eval scores the six implemented tasks as multiple-choice, with micro-F1 on BHTC and BEC, a two-class F1 on VaxxStance, and accuracy on QNLI, WiC and coreference. The tag `basque-glue` runs all six and does not average them. Do not drop a single "BasqueGLUE" percentage from lm-eval without saying which tasks went into it.

## Dataset and licence

There is no one row count. Table 1 of the paper (copied on GitHub and Hugging Face) lists train/val/test sizes per task. NER and slot rows are tokens; the rest are examples. Test data are public. Licences differ by task: most are CC BY-NC-SA 4.0, QNLIeu is CC BY-SA 4.0, VaxxStance is CC BY 4.0 plus Twitter's terms, and BEC2016eu adds Twitter's terms to CC BY-NC-SA 4.0. The evaluation script itself is CC BY-SA 4.0. The LREC PDF is under ELRA CC-BY-NC-4.0, which is the paper, not the data.

## Who publishes it

Gorka Urbizu, Iñaki San Vicente and Xabier Saralegi (then Elhuyar / now orai NLP) with Rodrigo Agerri and Aitor Soroa (HiTZ Center - Ixa, UPV/EHU). The paper is LREC 2022, Marseille, 20–25 June 2022, pages 1603–1612. Current repo is `orai-nlp/BasqueGLUE`; the PDF still mentions `Elhuyar/BasqueGLUE`. Hugging Face: `orai-nlp/basqueGLUE`, last updated 2024-04-08.

## Lineage

English [GLUE](glue.md) and SuperGLUE are the design templates. [BasqueBench](basque_bench.md) later reuses BasqueGLUE's QNLIeu inside the IberoBench Basque slice, alongside many tasks BasqueGLUE does not contain. Latxa (arXiv:2403.20266) uses BasqueGLUE to score decoder models. This page is the original nine-task suite, not BasqueBench.

## Saturation and contamination

A 74% fine-tuned BERT average from 2022 does not tell you whether today's Basque LLMs have used up the suite. Decoder numbers need the Latxa paper or a fresh lm-eval run. Test labels are public, and several source domains are old, so contamination is a live concern, especially for Wikipedia QNLI and news NER.

## How to run it

Official: fine-tune, write `test.jsonl`-shaped predictions, run `python3 eval_basqueglue.py --task ...`. lm-eval: `--tasks basque-glue` or the six names `bhtc_v2`, `bec2016eu`, `vaxx_stance`, `qnlieu`, `wiceu`, `epec_koref_bin`, dataset `orai-nlp/basqueGLUE`. WiC decoding in lm-eval re-encodes strings as latin-1 then utf-8 to repair an encoding issue. Prompt language is Basque. HELM and OpenCompass names were not found.

## Reading the numbers

A 73% "BasqueGLUE" figure from 2022 is an encoder fine-tune average, not a zero-shot LLM score. An lm-eval run on six tasks is a different slice and a different protocol. Check which tasks, which metric, and whether NER was included. Pair it with [BasqueBench](basque_bench.md) if you care about exam QA and translation as well as this older NLU core. Non-commercial licences on most tasks also limit redistribution even when the average looks open.
