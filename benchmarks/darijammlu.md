---
id: darijammlu
name: "DarijaMMLU"
aliases:
  - "Darija MMLU"
  - "MBZUAI-Paris/DarijaMMLU"
page_kind: benchmark
category: knowledge
subcategory: "Moroccan Darija multiple-choice exam QA translated from MMLU and ArabicMMLU"
status: active
summary: "22,027 Darija multiple-choice questions across 44 subjects, translated from selected MMLU and ArabicMMLU subsets."
measures: >
  DarijaMMLU tests whether a model can answer subject questions written in
  Moroccan Darija. Forty-four Hub configs mix two sources: selected English
  [MMLU](mmlu.md) subjects and selected [ArabicMMLU](arabic_mmlu.md) subjects,
  both translated with Claude 3.5 Sonnet. Items have two to five options.
  Some ArabicMMLU-derived rows carry a context passage. This is not a native
  Darija exam corpus and not a full copy of either parent benchmark.
task_format: >
  Multiple-choice QA in Darija. lm-eval group darijammlu prompts with a Darija
  instruction, the subject name, the question, and A.–E. options, then scores
  letter accuracy. Template: test_split test, fewshot_split dev, sampler
  first_n. YAML does not pin num_fewshot; the Atlas-Chat table reports 0-shot
  and 3-shot.
metric:
  name: "accuracy (size-weighted mean across tasks)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Option count varies from 2 to 5, so there is no single chance rate in the
    sources opened here. Atlas-Chat Table 2 (Darija prompts) reports
    Atlas-Chat-27B at 61.95% 0-shot and 63.30% 3-shot; gemma-2-27b-it 36.47%
    and 59.80% on those two columns. No human Darija exam-taker baseline was
    found.
dataset:
  size: 22027
  size_note: >
    Card and paper: 22,027 questions, 44 subjects. Hub dataset_info sums to
    21,792 test + 235 dev = 22,027 across 44 configs. Largest test subjects
    include islamic_studies 2,210, professional_law 1,534, biology 1,409.
    Smallest test subject in the dump is philosophy_ar 39. lm-eval splits
    source tags: darijammlu_mmlu (22 English-MMLU subjects) and
    darijammlu_ar_mmlu (22 ArabicMMLU subjects).
  url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaMMLU"
  license: "MIT (Hub card, linking hendrycks/test); ArabicMMLU parent licence is stated two ways on arabic_mmlu.md (GitHub CC-BY-NC-SA-4.0 vs Hub cc-by-nc-4.0)"
  languages:
    - ary
  modalities:
    - text
  splits: "per-subject test + dev; lm-eval scores test and draws few-shot from dev"
  public_test_set: true
publisher:
  org: "MBZUAI-Paris, with EMINES-UM6P, LINAGORA, KTH, AtlasIA and École Polytechnique"
  authors:
    - "Guokan Shang"
    - "Hadi Abdine"
    - "Yousef Khoubrane"
    - "Amr Mohamed"
    - "Yassine Abbahaddou"
    - "Sofiane Ennadir"
    - "Imane Momayiz"
    - "Xuguang Ren"
    - "Eric Moulines"
    - "Preslav Nakov"
    - "Michalis Vazirgiannis"
    - "Eric Xing"
  url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaMMLU"
paper:
  title: "Atlas-Chat: Adapting Large Language Models for Low-Resource Moroccan Arabic Dialect"
  arxiv: "2409.17912"
  url: "https://arxiv.org/abs/2409.17912"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/MBZUAI-Paris/lm-evaluation-harness-atlas-chat"
released: "2024-09"
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
    Paper Table 2 best listed 0-shot is Atlas-Chat-27B at 61.95%. No
    independent live leaderboard was opened for this page.
contamination:
  risk: high
  note: >
    Both parent sets are long-public, answers are on the Hub, and the
    translation has been public since 27 September 2024. A model that
    memorised English MMLU or ArabicMMLU may still benefit after translation.
harness:
  lm_eval: "darijammlu"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Groups darijammlu_mmlu and darijammlu_ar_mmlu; subject YAML tags use a _tasks suffix (darijammlu_mmlu_tasks, darijammlu_ar_mmlu_tasks). README also lists category tags darijammlu_stem, darijammlu_social_sciences, darijammlu_humanities, darijammlu_language, darijammlu_other."
tags:
  - darija
  - moroccan-arabic
  - multiple-choice
  - knowledge
  - mmlu
  - arabicmmlu
  - translation
sources:
  - url: "https://arxiv.org/abs/2409.17912"
    title: "Atlas-Chat paper (arXiv:2409.17912)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2409.17912v2"
    title: "Atlas-Chat v2 HTML; Table 2 Atlas-Chat-27B 61.95 / 63.30 on DarijaMMLU"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/MBZUAI-Paris/DarijaMMLU"
    title: "MBZUAI-Paris/DarijaMMLU dataset card (44 subjects, MIT claim)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/MBZUAI-Paris/DarijaMMLU"
    title: "Hub API (44 configs, 21792 test + 235 dev)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijammlu/README.md"
    title: "lm-eval darijammlu README (group and tags)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijammlu/_darijammlu.yaml"
    title: "lm-eval group YAML (size-weighted acc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijammlu/_default_darijammlu_template_yaml"
    title: "lm-eval default template (test/dev, multiple_choice acc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijammlu/_generate_configs.py"
    title: "Subject lists: 22 MMLU + 22 ArabicMMLU"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijammlu/_darijammlu_mmlu.yaml"
    title: "lm-eval group darijammlu_mmlu (tag darijammlu_mmlu_tasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/darijammlu/_darijammlu_ar_mmlu.yaml"
    title: "lm-eval group darijammlu_ar_mmlu (tag darijammlu_ar_mmlu_tasks)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-037 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-037"
---

## What it measures

DarijaMMLU is a Darija reading of two existing exam suites. Twenty-two subjects come from English MMLU. Twenty-two come from ArabicMMLU, including Moroccan-relevant material such as driving tests and Islamic studies. The model sees a Darija question, optional context, and two to five choices. The intended claim is knowledge and exam-style reasoning in Darija, not whether the model can sit a real Moroccan paper in the original wording.

It is not [ArabicMMLU](arabic_mmlu.md), which is native MSA, and not [DarijaBench](darija_bench.md), which is NLP tasks rather than subject exams.

## How it is scored

lm-eval's `darijammlu` group takes a size-weighted mean of per-subject accuracy. Each task uses the multiple-choice letter as the target. Dev rows (235 in total) are the few-shot pool when you request shots; the YAML does not hard-code a shot count. Atlas-Chat Table 2 prints 0-shot and 3-shot. Those two columns are not interchangeable, and gemma-2-27b-it's jump from 36.47% to 59.80% shows how much the shot setting can move a non-specialised model.

## Dataset and licence

22,027 rows over 44 Hub configs, matching the card, the paper, and a sum of `dataset_info`. Fields: `question`, `context`, `choices`, `answer` (integer index), `subject`, `subject_darija`, `source`. The card claims MIT and links the original MMLU licence. [ArabicMMLU](arabic_mmlu.md) records two parent-licence readings (GitHub CC-BY-NC-SA-4.0 vs Hub cc-by-nc-4.0) and leaves SPDX unset. This page records those readings rather than collapsing them. Hub language tag is `ma`; this catalogue uses `ary`.

## Who publishes it

Same Atlas-Chat team as [DarijaBench](darija_bench.md) and [DarijaHellaSwag](darijahellaswag.md). arXiv 2409.17912, Hub snapshot 27 September 2024. lm-evaluation-harness vendors group `darijammlu`.

## Lineage

Built from selected [MMLU](mmlu.md) and [ArabicMMLU](arabic_mmlu.md) subjects, not from a new item-writing campaign. [DarijaBench](darija_bench.md) already named DarijaMMLU as a sibling eval; this page is that eval, not a duplicate of DarijaBench. No successor is in this repository.

## Saturation and contamination

61.95% 0-shot for Atlas-Chat-27B in 2024 is not a ceiling, but both parent quizzes are classic pretraining contaminants and this translation is public. Do not treat a high score as proof the model acquired Darija-only knowledge.

## How to run it

`lm_eval --tasks darijammlu` for the size-weighted group. Groups `darijammlu_mmlu` and `darijammlu_ar_mmlu` split the two parents (subject files tag `*_tasks`). README also lists category tags for stem, social sciences, humanities, language, and other. State the shot count. Per-subject YAML names follow `darijammlu_<subject>`.

## Reading the numbers

A strong group score means the model picked the keyed letter on this translated mix. It does not measure spoken Darija, native exam authorship, or English MMLU. Always say whether the figure is 0-shot or 3-shot, and whether it is the full group or one source tag. Read it beside [ArabicMMLU](arabic_mmlu.md) and [DarijaHellaSwag](darijahellaswag.md).
