---
id: mediqa_qa2019
name: "MEDIQA 2019 QA (lm-eval)"
aliases:
  - "mediqa_qa2019_perplexity"
  - "MEDIQA-QA 2019 (lm-eval)"
page_kind: benchmark
category: domain
subcategory: "consumer health question answering (generation overlap metrics)"
status: unknown
summary: "lm-eval's generation wrap of MEDIQA 2019 Task 3: write an English answer to a consumer health question and score overlap against the first listed gold answer."
measures: >
  This id is EleutherAI lm-evaluation-harness task mediqa_qa2019, not the 2019 ranking
  shared task as originally scored, and not HELM medi_qa. MEDIQA 2019 Task 3 gave a
  consumer health question plus CHiQA candidate answers and asked systems to filter
  and re-rank them. lm-eval instead takes the question text and asks the model to
  generate a free-form answer. Inputs and outputs are English text. The original
  shared task also had medical NLI and recognizing-question-entailment tracks; those
  are not this id.
task_format: >
  generate_until generation, stopping at a blank line. The YAML description tells the
  model to answer a patient question as a doctor would. Gold is
  QUESTION.AnswerList[0].Answer.AnswerText from the Hugging Face source schema, which
  is XML file order, not the expert's ReferenceRank=1 answer. A separate task
  mediqa_qa2019_perplexity scores loglikelihood of that gold string.
metric:
  name: "bleu, rouge1, rouge2, rougeL, bleurt, bert_score (no designated headline)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    lm-eval logs six overlap metrics with nanmean aggregation. None is marked as the
    main score in the YAML. BLEURT uses bleurt-base-512; BERTScore is English F1.
    The 2019 shared task scored ranking with accuracy, MRR, precision and Spearman's
    rho and quoted 78.3% among 72 teams. Those ranking numbers are not on this
    overlap scale. No random or human baseline is stated for the generation protocol.
dataset:
  size: 150
  size_note: >
    lm-eval scores the test split of bigbio/mediqa_qa (150 questions). Hugging Face
    datasets-server also reports train_live_qa_med 104, train_alexa 104, and
    validation 25 under both mediqa_qa_source and mediqa_qa_bigbio_qa. The YAML sets
    those splits but the generation gold is always the first AnswerList entry. Test
    XML is MEDIQA2019-Task3-QA-TestSet-wLabels.xml. W19-5039 reports 1,107 associated
    test answers (839 LiveQA-Med train answers, 862 Alexa train answers, 234
    validation answers). lm-eval still scores one generated string per question.
  url: https://huggingface.co/datasets/bigbio/mediqa_qa
  license: "CC-BY-4.0 on the authors' GitHub README; Hugging Face bigbio/mediqa_qa lists licence as unknown"
  languages:
    - en
  modalities:
    - text
  splits: "lm-eval: train_live_qa_med / validation / test (150-question test scored). Hugging Face also has train_alexa (104)."
  public_test_set: true
publisher:
  org: "U.S. National Library of Medicine (LHC/NLM) and IBM Research; lm-eval task by EleutherAI"
  authors:
    - "Asma Ben Abacha"
    - "Chaitanya Shivade"
    - "Dina Demner-Fushman"
  url: https://sites.google.com/view/mediqa2019
paper:
  title: "Overview of the MEDIQA 2019 Shared Task on Textual Inference, Question Entailment and Question Answering"
  arxiv: ""
  url: https://aclanthology.org/W19-5039/
  year: 2019
leaderboard_url: https://www.aicrowd.com/challenges/mediqa-2019-question-answering-qa/leaderboards
repo_url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/mediqa_qa2019
released: "2019-08"
last_updated: ""
lineage:
  family: ""
  predecessor: live_qa
  successors: []
  variants:
    - medi_qa
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The 2019 ranking QA track reached 78.3% among 72 teams. No current top was read
    for lm-eval BLEU/ROUGE/BLEURT/BERTScore on this generation wrap.
contamination:
  risk: high
  note: >
    Test questions, candidate answers and labels have been public on GitHub since
    2019, including MEDIQA2019-Task3-QA-TestSet-wLabels.xml. lm-eval also sets
    should_decontaminate on the perplexity variant only.
harness:
  lm_eval: "mediqa_qa2019"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Also mediqa_qa2019_perplexity (loglikelihood_rolling). Dataset path
    bigbio/mediqa_qa, default Hugging Face config mediqa_qa_source. Distinct from
    HELM run spec medi_qa, which uses an LLM jury against the rank-1 reference.
tags:
  - medical
  - consumer-health
  - generation
  - overlap-metrics
  - lm-eval
sources:
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/mediqa_qa2019
    title: "lm-evaluation-harness mediqa_qa2019 task directory"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mediqa_qa2019/README.md
    title: "lm-eval mediqa_qa2019 README"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mediqa_qa2019/mediqa_qa2019.yaml
    title: "lm-eval mediqa_qa2019.yaml"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mediqa_qa2019/utils.py
    title: "lm-eval mediqa_qa2019 utils.py (gold = AnswerList[0])"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/bigbio/mediqa_qa
    title: "bigbio/mediqa_qa dataset card"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=bigbio/mediqa_qa
    title: "bigbio/mediqa_qa datasets-server split counts"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/bigbio/mediqa_qa/raw/main/mediqa_qa.py
    title: "bigbio/mediqa_qa loader (default config mediqa_qa_source)"
    accessed: "2026-09-08"
  - url: https://github.com/abachaa/MEDIQA2019
    title: "abachaa/MEDIQA2019 repository (CC BY 4.0 in README)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/abachaa/MEDIQA2019/master/README.md
    title: "MEDIQA2019 GitHub README (licence and 72-team note)"
    accessed: "2026-09-08"
  - url: https://aclanthology.org/W19-5039/
    title: "MEDIQA 2019 overview (ACL Anthology W19-5039)"
    accessed: "2026-09-08"
  - url: https://aclanthology.org/W19-5039.pdf
    title: "MEDIQA 2019 overview PDF (150 test questions, 1107 answers; QA metrics)"
    accessed: "2026-09-08"
  - url: https://sites.google.com/view/mediqa2019
    title: "MEDIQA 2019 shared-task site"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-058 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-058"
---

## What it measures

`mediqa_qa2019` is lm-eval's generation wrap of MEDIQA 2019 Task 3. It is not MedQA, and it is not the 2019 ranking contest as scored. The shared task gave a consumer health question and CHiQA answers, then asked teams to drop bad answers and re-rank the rest. lm-eval keeps the question string and asks the model to write an answer. The language is English. The output is free text.

The 2019 workshop also ran medical NLI and recognizing-question-entailment tracks. Those sets and metrics are separate. HELM's [medi_qa](medi_qa.md) uses the same questions with a different gold and an LLM jury. Do not treat the two ids as one number.

## How it is scored

lm-eval `mediqa_qa2019` is `generate_until` with stop sequence `\n\n`. It reports BLEU, ROUGE-1/2/L, BLEURT (bleurt-base-512) and English BERTScore F1, each aggregated with nanmean. The YAML does not name a headline metric. Empty predictions or empty golds become NaN.

Gold is `AnswerList[0]` in the Hugging Face source schema. That is XML order in the loader, not the expert's `ReferenceRank=1` string that HELM uses. The 2019 ranking headline of 78.3% among 72 teams is a different scale. No random or human baseline was stated for this overlap protocol. `mediqa_qa2019_perplexity` instead reports rolling perplexity of the same gold string.

## Dataset and licence

Hugging Face `bigbio/mediqa_qa` mirrors the GitHub XML. datasets-server counts 104 LiveQA-Med train questions, 104 Alexa train questions, 25 validation questions and 150 test questions. W19-5039 pairs those with 839, 862, 234 and 1,107 CHiQA answers. lm-eval scores `test` at question granularity. The authors' GitHub README states CC BY 4.0. The Hugging Face card lists the licence as unknown. GitHub's licence API field is null. Answers and ranks are public.

## Who publishes it

Asma Ben Abacha and Dina Demner-Fushman (Lister Hill Center, NLM) and Chaitanya Shivade (IBM) organised MEDIQA 2019 at ACL-BioNLP in Florence, August 2019. The overview is ACL Anthology W19-5039. EleutherAI ships the lm-eval task. The 2019 ranking board remains on AIcrowd.

## Lineage

Do not fold this into [MedQA](medqa.md). MedQA is USMLE-style multiple choice. One training file reuses TREC-2017 LiveQA medical questions, documented here as [live_qa](live_qa.md); lm-eval can load that split but scores `test`. HELM [medi_qa](medi_qa.md) is the jury wrap of the same test questions, not this overlap wrap. Later MEDIQA-Chat and MEDIQA-Sum tasks are different datasets.

## Saturation and contamination

Saturation of the lm-eval overlap metrics is not established. The 2019 ranking ceiling does not transfer. Contamination risk is high: the labelled test XML has been public since 2019. The perplexity YAML sets a decontamination query; the generation YAML does not.

## How to run it

```
lm_eval --model hf --model_args pretrained=... --tasks mediqa_qa2019
```

The companion task is `mediqa_qa2019_perplexity`. The loader uses default config `mediqa_qa_source`. Metrics need the `evaluate` extras named in `utils.py` (BLEU, ROUGE, BERTScore, BLEURT). Prompt wording, stop sequences and the `AnswerList[0]` gold make these numbers hard to compare with HELM `medi_qa` or with 2019 ranking accuracy.

## Reading the numbers

A high BLEU or BERTScore here means the generated English answer overlaps the first listed 2019 candidate, not that the model ranked CHiQA hits well. It is not a medical-licence exam score. Pair it with [medi_qa](medi_qa.md) if you need the jury protocol, and with a held-out clinical QA set if you need current medical knowledge. Do not quote the 78.3% ranking figure as this task.
