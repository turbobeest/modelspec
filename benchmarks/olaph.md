---
id: olaph
name: "OLAPH / MedLFQA"
aliases:
  - "MedLFQA"
  - "dmis-lab/MedLFQA"
  - "olaph_perplexity"
page_kind: benchmark
category: domain
subcategory: "biomedical long-form question answering"
status: active
summary: "lm-eval wrap of MedLFQA: English biomedical long answers scored with BLEU, ROUGE, BERTScore and BLEURT on a 10% slice."
measures: >
  olaph, as this id, is EleutherAI's generate-until task on dmis-lab/MedLFQA.
  The model reads an English patient-style biomedical question and must write a
  long answer. Jeong et al. built MedLFQA so they could score factual claims
  (Must Have / Nice to Have statements) while training the OLAPH preference
  loop. The harness task does not score those claims. It compares the free-form
  answer to Free_form_answer with n-gram and embedding overlap. English text
  only. This is not [HealthBench](healthbench.md).
task_format: >
  Open-ended generation. YAML description tells the model it is a healthcare
  assistant and to answer concisely without omitting relevant information.
  Stops at a blank line. training/validation/test splits all point at the Hub
  test split. process_docs keeps the first 10% of rows (code uses 0.1; the
  comment says 1%). Sister task olaph_perplexity uses loglikelihood_rolling on
  the same slice.
metric:
  name: "BLEU, ROUGE-1/2/L, BERTScore, BLEURT (nanmean)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    lm-eval reports nanmean of BLEU, rouge1, rouge2, rougeL, bert_score, and
    bleurt. Predictions or references shorter than 10 characters become NaN.
    The paper's headline metrics are words composition (ROUGE), semantic
    similarity (BLEURT+BERTScore), and factuality (comprehensiveness minus
    hallucination on Must Have / Nice to Have). That factuality term is not in
    the YAML. olaph_perplexity reports word/byte perplexity (lower better).
dataset:
  size: 4948
  size_note: >
    datasets-server default config: 4,948 test rows. Paper Table 1 and Hub jsonl
    line counts: LiveQA 100, MedicationQA 666, HealthSearchQA 3,077, K-QA Golden
    201, K-QA Silver 904 (sum 4,948). K-QA (Manes et al., arXiv 2401.14493,
    Table 2) reports 1,212 questions and 201 physician answers; golden file here
    is 201. lm-eval scores only the first 10% after load, int(0.1*4948)=494 rows,
    in Hub file order, not a random sample and not the paper's leave-one-dataset-out
    split.
    Columns: Question, Free_form_answer, Must_have, Nice_to_have.
  url: "https://huggingface.co/datasets/dmis-lab/MedLFQA"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "Hub test only; YAML maps train, validation, and test to that split"
  public_test_set: true
publisher:
  org: "Korea University DMIS Lab (with Upstage AI and AIGEN Sciences)"
  authors:
    - "Minbyul Jeong"
    - "Hyeon Hwang"
    - "Chanwoong Yoon"
    - "Taewhoo Lee"
    - "Jaewoo Kang"
  url: "https://huggingface.co/datasets/dmis-lab/MedLFQA"
paper:
  title: "OLAPH: Improving Factuality in Biomedical Long-form Question Answering"
  arxiv: "2405.12701"
  url: "https://arxiv.org/abs/2405.12701"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/olaph"
released: "2024-05"
last_updated: "2024-09"
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
    No live MedLFQA leaderboard was opened. Paper Table 2–3 report 7B open
    models and proprietary models on the authors' factuality and similarity
    mix, not on lm-eval's 494-row BLEU slice. Those tables are not copied here
    as a current ceiling.
contamination:
  risk: medium
  note: >
    The 4,948 test rows, including Free_form_answer and the claim lists, are
    public. Some answers were generated with GPT-4 when the source set had
    questions only (HealthSearchQA, K-QA Silver). LiveQA, MedicationQA, and
    K-QA Golden start from expert answers. No held-out private test.
harness:
  lm_eval: "olaph"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "olaph_perplexity; dataset dmis-lab/MedLFQA"
tags:
  - biomedical
  - long-form-qa
  - factuality
  - generation
sources:
  - url: "https://arxiv.org/abs/2405.12701"
    title: "OLAPH paper (arXiv 2405.12701)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2405.12701"
    title: "OLAPH paper HTML (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/dmis-lab/MedLFQA"
    title: "dmis-lab/MedLFQA dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/dmis-lab/MedLFQA"
    title: "dmis-lab/MedLFQA API cardData"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=dmis-lab/MedLFQA"
    title: "datasets-server info for MedLFQA"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/olaph/README.md"
    title: "lm-eval olaph README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/olaph/olaph.yaml"
    title: "lm-eval olaph.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/olaph/olaph_perplexity.yaml"
    title: "lm-eval olaph_perplexity.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/olaph/utils.py"
    title: "lm-eval olaph utils.py"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2401.14493"
    title: "K-QA paper (arXiv 2401.14493)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2401.14493"
    title: "K-QA paper HTML (ar5iv)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-063 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-063"
---

## What it measures

The model is given an English biomedical question that a patient might ask and must write a long answer. Sources mixed into MedLFQA are LiveQA, MedicationQA, HealthSearchQA, and K-QA (golden expert pairs plus a silver split). Jeong et al. rebuilt those sets so each row has a question, a long answer, Must Have statements, and Nice to Have statements. Their OLAPH trainer uses those statements to reward answers that cover required claims and avoid hallucinations.

lm-eval's `olaph` task ignores Must_have and Nice_to_have. It only checks how close the generation is to Free_form_answer. That is a different skill from the paper's factuality score.

## How it is scored

`olaph` is `generate_until`, stopping at `\n\n`. Metrics are BLEU, ROUGE-1/2/L, BERTScore F1 (English), and BLEURT, each aggregated with `nanmean`. If either the prediction or the reference is under 10 characters, that row is NaN. Loading those metrics needs extra packages (`evaluate`, `bert-score`, `bleurt`). `olaph_perplexity` instead scores rolling log-likelihood of the reference.

The paper sorts samples with a weighted mix of ROUGE, BLEURT, BERTScore, and (comprehensiveness − hallucination). lm-eval never computes hallucination or comprehensiveness. Do not treat a YAML BLEU as an OLAPH-paper factuality number.

## Dataset and licence

Hub card: CC-BY-4.0, English. 4,948 test rows, no train split on the Hub. Paper Table 1 matches the Hub jsonl line counts: LiveQA 100, MedicationQA 666, HealthSearchQA 3,077, K-QA Golden 201, K-QA Silver 904. Manes et al.'s K-QA write-up (arXiv 2401.14493, Table 2) reports 1,212 questions and 201 physician answers; the golden file here is 201. For question-only sources, the authors generated answers and claim lists with GPT-4 and checked GPT-4 vs experts on K-QA Golden with three clinicians.

YAML `process_docs` takes `range(int(0.1 * n))`, i.e. the first 494 rows of whatever order `load_dataset` returns. The comment above that line says "first 1%". The paper's experiments instead leave one source out as test and train on the rest. Those protocols are not the same.

## Who publishes it

Minbyul Jeong, Hyeon Hwang, Chanwoong Yoon, Taewhoo Lee, and Jaewoo Kang, Korea University DMIS Lab, with Upstage AI and AIGEN Sciences on the author block. Paper: arXiv 2405.12701, 21 May 2024. Dataset: `dmis-lab/MedLFQA` (lastModified 2024-09-09). lm-eval task YAML version 1.2.

## Lineage

MedLFQA is a reconstruction of LiveQA (Abacha et al., 2017), MedicationQA (Abacha et al., 2019), HealthSearchQA from Med-PaLM (Singhal et al., 2023), and K-QA (Manes et al., 2024). OLAPH is the DPO-style training loop, not a second dataset. Related medical pages in this repository: [healthbench](healthbench.md), [healthqa_br](healthqa_br.md). No successor id is tracked.

## Saturation and contamination

No public lm-eval leaderboard was opened. Paper tables are 2024 7B and proprietary runs on a different metric mix. Answers are public, so a model can copy Free_form_answer. Risk is medium rather than high only because the long answers are diverse and some are GPT-4 synthetic rather than a short multiple-choice key.

## How to run it

```
lm_eval --model hf --model_args pretrained=... --tasks olaph
```

Install the extra metric packages listed in `utils.py`. `olaph_perplexity` is a separate task. Expect about 494 scored rows, not 4,948, unless someone patches `process_docs`. Do not compare to the paper's leave-one-dataset-out factuality columns.

## Reading the numbers

A high BLEU on this YAML means the model echoed the stored long answer on the first tenth of the dump. It does not mean the answer is safe or complete for a patient. Look at HealthBench-style expert rubrics or the paper's claim-level factuality if you need that. Check whether a reported run used the 494-row slice or the full 4,948.
