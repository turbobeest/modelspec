---
id: atlas
name: "ATLAS (AGI-Oriented Testbed for Logical Application in Science)"
aliases:
  - "ATLAS"
  - "AGI-Oriented Testbed for Logical Application in Science"
page_kind: benchmark
category: reasoning
subcategory: "high-difficulty multidisciplinary scientific problem solving"
status: active
summary: "798 expert-written STEM problems across seven fields, scored by an LLM judge; GPT-5-High is at 42.9% on the public validation set."
measures: >
  ATLAS gives a model an original scientific problem and asks for a structured final answer,
  often with several sub-answers, rather than a single letter choice. Items cover mathematics,
  physics, chemistry, biology, computer science, earth science and materials science. The paper
  says most items are calculation and derivation, with smaller shares of selection, explanation
  and composite formats. Problems were written or substantially rewritten by PhD-level domain
  experts so that the skill is multi-step scientific reasoning, not recall of a public exam item.
task_format: >
  Free-form generation. OpenCompass asks the model to solve the problem, then emit a JSON list
  of final answers. An LLM judge compares that list to a standard answer. Default config draws
  four samples (n=4) for accuracy and mG-Pass@{2,4}.
metric:
  name: "accuracy (LLM-judge); also mG-Pass@2 and mG-Pass@4"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No human-baseline figure was read from the paper or dataset card. Headline leaderboard
    numbers are average accuracy on the public validation set. The paper's Table 3 caption
    says those numbers were judged by GPT-OSS-120B; the Hugging Face and GitHub READMEs
    instead name OpenAI o4-mini as the leaderboard judge. OpenCompass's atlas config README
    reports a third, slightly lower trio of scores under an o4-mini judge. Treat judge identity
    as part of the score, not a detail that can be ignored.
dataset:
  size: 798
  size_note: >
    Paper Table 2 lists 798 items (Physics 175, Materials Science 140, Chemistry 117, Earth
    Science 109, Biology 102, Mathematics 94, Computer Science 61). The Hugging Face files
    opened for this page have 301 validation rows with non-empty standard answers and 497
    test rows whose refined_standard_answer fields are empty, summing to 798. Publisher
    READMEs round those splits as "~300" and "~500".
  url: "https://huggingface.co/datasets/opencompass/ATLAS"
  license: ""
  languages:
    - zh
    - en
  modalities:
    - text
  splits: "val (301, answers public) / test (497, answers blank in the public jsonl; OpenCompass supports infer only)"
  public_test_set: false
publisher:
  org: "Shanghai AI Laboratory (OpenCompass)"
  authors:
    - "Hongwei Liu"
    - "Junnan Liu"
    - "Shudong Liu"
    - "Haodong Duan"
    - "Yuqiang Li"
    - "Mao Su"
    - "Xiaohong Liu"
    - "Guangtao Zhai"
    - "Xinyu Fang"
    - "Qianhong Ma"
    - "Taolin Zhang"
    - "Zihan Ma"
    - "Yufeng Zhao"
    - "Peiheng Zhou"
    - "Linchen Xiao"
    - "Wenlong Zhang"
    - "Shijie Zhou"
    - "Xingjian Ma"
    - "Siqi Sun"
    - "Jiaye Ge"
    - "Meng Li"
    - "Yuhong Liu"
    - "Jianxin Dong"
    - "Jiaying Li"
    - "Hui Wu"
    - "Hanwen Liang"
    - "Jintai Lin"
    - "Yanting Wang"
    - "Jie Dong"
    - "Tong Zhu"
    - "Tianfan Fu"
    - "Conghui He"
    - "Qi Zhang"
    - "Songyang Zhang"
    - "Lei Bai"
    - "Kai Chen"
  url: "https://github.com/open-compass/ATLAS"
paper:
  title: "ATLAS: A High-Difficulty, Multidisciplinary Benchmark for Frontier Scientific Reasoning"
  arxiv: "2511.14366"
  url: "https://arxiv.org/abs/2511.14366"
  year: 2025
leaderboard_url: "https://huggingface.co/spaces/opencompass/ATLAS"
repo_url: "https://github.com/open-compass/ATLAS"
released: "2025-11"
last_updated: "2025-11"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 42.9
  as_of: "2025-11"
  note: >
    Hugging Face and GitHub READMEs, and the paper's Table 3, all list OpenAI GPT-5-High at
    42.9% average accuracy on the public validation set, well below 100. Gemini-2.5-Pro is
    35.3% and Grok-4 34.1% in that same table. This is not a ceiling. Judge-model disagreement
    (see baseline_note) means the 42.9 figure should not be mixed with OpenCompass config-README
    scores that put Gemini-2.5-Pro at 34.9 and Grok-4 at 32.9.
contamination:
  risk: medium
  note: >
    The paper presents the items as newly written or substantially adapted, with expert review,
    specifically to reduce leakage from public exams. The 301 validation answers are in the
    public jsonl as of the November 2025 Hugging Face snapshot. The 497-item test split ships
    without answers. That is a held-out test, not a fully private benchmark.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "atlas"
  bigbench: ""
  other: "OpenCompass default abbr is atlas-val; switch split to test and run -m infer for the blank-answer test file."
tags:
  - scientific-reasoning
  - stem
  - llm-judge
  - bilingual
  - frontier
sources:
  - url: "https://arxiv.org/abs/2511.14366"
    title: "ATLAS paper abstract (arXiv:2511.14366, submitted 2025-11-18)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2511.14366"
    title: "ATLAS paper HTML (ar5iv): 798-item Table 2, Table 3 scores, bilingual claim, Shanghai AI Laboratory"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/ATLAS/raw/main/README.md"
    title: "opencompass/ATLAS dataset card (splits, o4-mini leaderboard table, CC-BY-SA YAML vs CC BY-NC-SA badge)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/opencompass/ATLAS"
    title: "Hugging Face dataset API (license tag cc-by-sa-4.0, en/zh, created 2025-10-31)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/ATLAS/resolve/main/atlas_val.jsonl"
    title: "atlas_val.jsonl (301 rows, answers present)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/opencompass/ATLAS/resolve/main/atlas_test_pub.jsonl"
    title: "atlas_test_pub.jsonl (497 rows, standard answers empty)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/atlas/README.md"
    title: "OpenCompass atlas config README (o4-mini judge table with different scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/atlas/atlas_val_gen_b2d1b6.py"
    title: "OpenCompass atlas_val_gen config (ATLASDataset, n=4, LLM judge template)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/atlas/dataset_loader.py"
    title: "ATLASDataset loader (opencompass/ATLAS, fields question and refined_standard_answer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/ATLAS/main/README.md"
    title: "open-compass/ATLAS GitHub README (CC BY-NC-SA 4.0 badge, evaluation protocol)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-027 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-027"
---

## What it measures

ATLAS is a scientific problem set, not a multiple-choice exam dump. Each item states a hard problem in one of seven STEM fields and expects a final answer that may be a number, an expression, a short derivation, or several sub-answers. The paper's Table 2 says 71.4% of items are calculation and derivation. The rest are selection, explanation, or composite forms. Authors are PhD-level contributors listed under Shanghai AI Laboratory. The point is to test whether a reasoning model can actually work a new scientific question, not whether it has seen a Gaokao or MMLU stem before.

The paper states that every question is available in English and Chinese. The public Hugging Face jsonl files mixed the two: 267 of 301 validation questions contain CJK characters, and 34 do not. Do not assume a reporter used the English wording.

## How it is scored

OpenCompass prompts the model to reason, then to emit only a JSON list of final answers. A judge model grades each sub-answer against the standard. The judge template uses labels A (correct), B (incorrect) and C (invalid: incomplete, repetitive, or a refusal). Default configs set `n=4` so the run can report average accuracy plus mG-Pass@2 and mG-Pass@4. No random-guess rate applies, because answers are open-ended.

Three published tables disagree on the judge and, in one case, on the numbers. The paper's Table 3 caption names GPT-OSS-120B and lists GPT-5-High at 42.9% on validation. The Hugging Face and GitHub READMEs print the same 42.9 / 35.3 / 34.1 / 33.8 / 26.4 column but attribute it to o4-mini. The OpenCompass dataset-config README, also under an o4-mini heading, instead gives DeepSeek-R1-0528 25.8, Gemini-2.5-Pro 34.9 and Grok-4 32.9. A number without the judge and the split is not comparable.

## Dataset and licence

Paper Table 2 counts 798 items. That matches 301 validation rows plus 497 test rows in the Hugging Face jsonl files opened for this page. Validation answers are filled in. Every test `refined_standard_answer` in `atlas_test_pub.jsonl` is empty, which matches OpenCompass's rule that the test split is infer-only. Subject counts in Table 2 are the ones to cite for the whole set.

Licence is not established. Hugging Face YAML and the dataset API tag `cc-by-sa-4.0`. The GitHub README and the dataset-card badge both say CC BY-NC-SA 4.0. The paper HTML does not resolve the clash. Use neither tag until the publisher picks one.

## Who publishes it

The paper's affiliation line is Shanghai AI Laboratory. The dataset and evaluation live under the OpenCompass organisation on Hugging Face and GitHub (`opencompass/ATLAS`, `open-compass/ATLAS`). arXiv:2511.14366 was submitted on 18 November 2025 (v2 on 20 November). A Hugging Face Space is linked for test-set submission. No independent third-party leaderboard was opened.

## Lineage

ATLAS is a new 2025 suite. It is not a rescoring of MMLU, GPQA, OlympiadBench or C-Eval; the paper positions it against those as a harder, less leakable, more open-ended alternative. This repository has no predecessor or variant page for it. The OpenCompass config directory name is `atlas`, which is this evaluation, not Meta's ATLAS retrieval model or the particle-physics experiment.

## Saturation and contamination

GPT-5-High at 42.9% on validation, with the next models in the mid-30s, still separates frontier systems. That is an open benchmark, not a ceiling. Contamination risk is mixed. The authors claim items are new or heavily rewritten. Validation answers have been public since the late-2025 Hugging Face snapshot, so val numbers can leak into later training runs. Test answers are not in the public jsonl.

## How to run it

Install OpenCompass and import `opencompass.configs.datasets.atlas.atlas_gen.atlas_datasets`. Default abbreviation is `atlas-val` on the validation split. You must fill in a judge endpoint. For the test file, set `split` to `test` and run with `-m infer`; local judging is not supported without answers. Changing the judge, the sample count, or the language of the prompt will move the number. lm-eval, HELM and BIG-bench task names were not found for this suite.

## Reading the numbers

A validation accuracy in the 30s or 40s means the model sometimes finished a hard scientific item in a form the chosen judge accepted. It does not mean the model is a reliable scientist, and it does not transfer to a different judge. Always record the split (val vs test), the judge, and whether mG-Pass or single-sample accuracy was used. Look at per-subject breakdowns when a reporter publishes them: physics is the largest slice, computer science the smallest. Pair ATLAS with a held-out knowledge test and with a human-graded proof set before treating a gain as general scientific competence.
