---
id: kormedmcqa
name: "KorMedMCQA"
aliases: []
page_kind: benchmark
category: domain
subcategory: "Korean healthcare professional licensing exam multiple-choice questions (doctor, nurse, pharmacist, dentist)"
status: active
summary: 7,469 five-option Korean multiple-choice questions from doctor, nurse, pharmacist and dentist licensing exams (2012-2024), with a recorded human-examinee average of 77.05%.
measures: >
  KorMedMCQA is the first Korean-language medical multiple-choice question answering benchmark,
  built from real Korean healthcare professional licensing examinations administered between 2012
  and 2024. It covers four professions -- doctor, nurse, pharmacist and dentist -- each drawn from
  that profession's own official licensing exam, spanning a wide range of medical subjects within
  each. Every question is written in Korean and offers five answer options (A-E), matching the
  five-option format the source exams themselves use, so unlike this repository's four-option
  medqa (English, USMLE-style), guessing at random on KorMedMCQA scores 20% rather than 25%.
task_format: >
  A Korean-language exam question with five labelled options (A-E) in; the model completes a
  "정답：" ("the answer is:") prompt with a single option letter, evaluated in a 5-shot setting with
  exemplars drawn from a fixed set of five questions per profession, originally sampled from the
  exams' development portion by the paper's authors.
metric:
  name: "exact_match (accuracy on the extracted option letter), weighted by item count across the four professions for the group aggregate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20
  human_baseline: 77.05
  baseline_note: >
    Five options give a random baseline of 20%. The paper reports a human-examinee average of
    77.05% across the four professions' real exam-taker results. lm-evaluation-harness's v3.0 task
    revision added a regex-based answer-extraction cascade (matching patterns such as "정답: B" or
    "정답은 B입니다") specifically because scoring raw generations with exact_match alone scores a
    verbose but correct model 0.
dataset:
  size: 7469
  size_note: >
    7,469 questions across four profession configs on the Hugging Face dataset, matching the
    paper's own count: doctor 2,489, nurse 1,751, pharmacist 1,817, dentist 1,412 (each profession's
    train+dev+test rows read from the datasets-server, with that profession's 5 dedicated few-shot
    rows set aside). The live parquet files additionally carry those 20 few-shot exemplar rows (5
    per profession) in a separate "fewshot" split not counted in the paper's headline total, so the
    raw datasets-server row count (7,489) is 20 higher than the paper's reported 7,469 -- a
    reconciled difference, not an unresolved discrepancy. The test split lm-evaluation-harness
    actually scores totals 3,009 questions: doctor 435, nurse 878, pharmacist 885, dentist 811,
    drawn from the most recent exam years (2022-2024).
  url: "https://huggingface.co/datasets/sean0042/KorMedMCQA"
  license: "CC BY-NC 2.0, per the Hugging Face dataset card's licence tag; the paper's own arXiv listing separately shows a CC BY 4.0 licence for the paper text itself."
  languages:
    - ko
  modalities:
    - text
  splits: "four profession configs (doctor, nurse, pharm, dentist), each with train/dev/test/fewshot splits; lm-evaluation-harness scores the test split (3,009 questions total) using the 5-row fewshot split as fixed few-shot exemplars"
  public_test_set: true
publisher:
  org: "KAIST, with Ajou University School of Medicine, UNIST and Kyung Hee University College of Dentistry"
  authors:
    - "Sunjun Kweon"
    - "Byungjin Choi"
    - "Gyouk Chu"
    - "Junyeong Song"
    - "Daeun Hyeon"
    - "Sujin Gan"
    - "Jueon Kim"
    - "Minkyu Kim"
    - "Rae Woong Park"
    - "Edward Choi"
  url: "https://huggingface.co/datasets/sean0042/KorMedMCQA"
paper:
  title: "KorMedMCQA: Multi-Choice Question Answering Benchmark for Korean Healthcare Professional Licensing Examinations"
  arxiv: "2403.01469"
  url: "https://arxiv.org/abs/2403.01469"
  year: 2024
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/sean0042/KorMedMCQA"
released: "2024-03"
last_updated: "2024-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 92.72
  as_of: "2024-12"
  note: >
    Approaching its ceiling at the top end while still separating most models. OpenAI o1-preview
    scored 92.72% overall in the paper's results table, well above the paper's own recorded
    human-examinee average of 77.05%, and the strongest open-source model tested, Qwen2.5-72B,
    reached 78.86% -- also above the human figure, though 14 points behind o1-preview. The weakest
    model tested, Gemma-2-2B-it, scored 29.18%, so real separation remains across the broader model
    population even as the top score nears the ceiling. No continuously updated public leaderboard
    beyond the paper's own table was found during this research.
contamination:
  risk: high
  note: >
    The underlying licensing exams were administered as real, publicly disclosed Korean
    professional exams before being compiled into this dataset, and the compiled question set,
    gold answers included, has been hosted on Hugging Face without gating since around March 2024
    -- roughly two and a half years by this research date. Using the most recent exam years
    (2022-2024) as the test split was meant to postdate most models' training cutoffs at original
    release, but that protection erodes for any model trained on data crawled after the dataset's
    own publication, and there is no held-out or refreshed portion beyond that fixed test split.
harness:
  lm_eval: "kormedmcqa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness registers kormedmcqa as a group of four subtasks (kormedmcqa_doctor,
    kormedmcqa_nurse, kormedmcqa_pharm, kormedmcqa_dentist), each reading its own dataset_name
    config from sean0042/KorMedMCQA, scored on exact_match after the v3.0 answer-extraction filter
    and combined with weight_by_size aggregation.
tags:
  - domain
  - korean
  - medical
  - multiple-choice
  - exam
  - human-baseline
sources:
  - url: "https://arxiv.org/abs/2403.01469"
    title: "KorMedMCQA: Multi-Choice Question Answering Benchmark for Korean Healthcare Professional Licensing Examinations (Kweon et al., arXiv:2403.01469)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.01469"
    title: "KorMedMCQA, full text (ar5iv, reflecting the December 2024 v3 revision)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/sean0042/KorMedMCQA"
    title: "sean0042/KorMedMCQA dataset metadata, Hugging Face API (licence, configs)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=sean0042/KorMedMCQA"
    title: "Hugging Face datasets-server per-config, per-split row counts for sean0042/KorMedMCQA"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/kormedmcqa"
    title: "kormedmcqa tasks directory, lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kormedmcqa/README.md"
    title: "kormedmcqa task README (groups, tasks, v3.0 changelog), lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kormedmcqa/_template_yaml"
    title: "kormedmcqa shared task template (prompt, fewshot config, metric), lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kormedmcqa/utils.py"
    title: "kormedmcqa answer-extraction filter code, lm-evaluation-harness"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

KorMedMCQA is the first Korean-language medical multiple-choice question answering benchmark, built from real Korean healthcare professional licensing examinations administered between 2012 and 2024. It covers four professions -- doctor, nurse, pharmacist and dentist -- each drawn from that profession's own official licensing exam, spanning a wide range of medical subjects within each. Every question is written in Korean and offers five answer options (A-E), matching the five-option format the source exams themselves use, so unlike this repository's four-option medqa (English, USMLE-style), guessing at random on KorMedMCQA scores 20% rather than 25%.

## How it is scored

The model completes a "정답：" ("the answer is:") prompt with a single option letter, evaluated with lm-evaluation-harness's exact_match metric on the extracted letter, weighted by each profession's item count when combined into the kormedmcqa group's aggregate score. The paper's main evaluation uses a 5-shot setting, with exemplars drawn from the exams' development portion; the harness ships a fixed, pre-selected 5-question "fewshot" split per profession for this purpose rather than sampling fresh exemplars per run. Because models often answer verbosely (for example "정답: B" instead of a bare "B"), version 3.0 of the harness task added a regex-based answer-extraction cascade -- looking for patterns such as "정답: B" or "정답은 B입니다" before falling back to a bare letter -- so that a verbose but correct model is not scored 0 the way plain exact_match on raw text would score it.

## Dataset and licence

The Hugging Face dataset holds 7,469 questions across the four profession configs, matching the paper's own count once each profession's 5 dedicated few-shot exemplar rows (20 total) are set aside from the raw parquet row count of 7,489 read from the datasets-server -- a reconciled difference, not an unresolved one. The test split lm-evaluation-harness actually scores totals 3,009 questions: doctor 435, nurse 878, pharmacist 885, dentist 811, drawn specifically from the most recent exam years (2022-2024) so the split would postdate most contemporaneous models' training data. The Hugging Face dataset card states a CC BY-NC 2.0 licence; the paper's own arXiv listing separately shows a CC BY 4.0 licence for the paper text itself, so the paper and the data it describes are not licensed identically.

## Who publishes it

KorMedMCQA was introduced by Sunjun Kweon, Byungjin Choi, Gyouk Chu, Junyeong Song, Daeun Hyeon, Sujin Gan, Jueon Kim, Minkyu Kim, Rae Woong Park and Edward Choi, with affiliations spanning KAIST, Ajou University School of Medicine, UNIST and Kyung Hee University College of Dentistry, first posted to arXiv in March 2024 and revised as recently as December 2024 (v3). The authors host the dataset directly on Hugging Face under the sean0042 namespace and provide the lm-evaluation-harness integration themselves; no separate organisation runs a public leaderboard.

## Lineage

KorMedMCQA has no formal predecessor or successor of its own. It sits alongside two other benchmarks in this repository that each share one axis with it but not both: csatqa, a Korean-language benchmark but covering general secondary-school exam subjects rather than medicine, and medqa, a medical licensing-exam benchmark but in English, built from US exams rather than Korean ones. KorMedMCQA is, per its own claim, the first benchmark to combine both axes -- Korean language and medical licensing content -- in one dataset.

## Saturation and contamination

KorMedMCQA is approaching its ceiling at the top end while still separating most models. In the paper's results table, OpenAI o1-preview scored 92.72% overall, well above the paper's own recorded human-examinee average of 77.05%, and the strongest open-source model tested, Qwen2.5-72B, reached 78.86% -- also above the human figure, though 14 points behind o1-preview. The weakest model tested, Gemma-2-2B-it, scored 29.18%, so real separation remains across the broader model population even as the top score nears the ceiling. No continuously updated public leaderboard beyond the paper's own table was found during this research.

Contamination risk is high: the underlying licensing exams were administered as real, publicly disclosed Korean professional exams before being compiled into this dataset, and the compiled question set, gold answers included, has been hosted on Hugging Face without gating since around March 2024 -- roughly two and a half years by this research date. Using the most recent exam years (2022-2024) as the test split was meant to postdate most models' training cutoffs at original release, but that protection erodes for any model trained on data crawled after the dataset's own publication, and there is no held-out or refreshed portion beyond that fixed test split.

## How to run it

lm-evaluation-harness registers kormedmcqa as a group of four subtasks (kormedmcqa_doctor, kormedmcqa_nurse, kormedmcqa_pharm, kormedmcqa_dentist), each reading its own dataset_name config from sean0042/KorMedMCQA, scored on exact_match after the v3.0 answer-extraction filter and combined with weight_by_size aggregation. No inspect_evals, HELM, OpenCompass or BIG-bench implementation was found during this research. Because the answer-extraction cascade materially changes scores for verbose models, a kormedmcqa score computed on an older, pre-3.0 harness version is not directly comparable to a current one.

## Reading the numbers

A high KorMedMCQA score is comparatively strong evidence a model can apply Korean-language medical knowledge to the kind of question a licensed doctor, nurse, pharmacist or dentist in Korea would have to answer to qualify -- the recorded 77.05% human-examinee average gives this page one of the few genuine, item-matched human baselines in this repository. Because the four professions are weighted by item count when combined into one aggregate, a single overall score can be dominated by the larger categories (doctor, pharmacist) and obscure weaker performance on a smaller one; check the per-profession breakdown before treating one number as representative. Given the exam content's long public exposure and the fact that today's strongest models already exceed the human baseline, treat a high score as evidence of exam-style recall and applied medical reasoning in Korean specifically, not as a general medical-competence claim transferable to English-language benchmarks like medqa.
