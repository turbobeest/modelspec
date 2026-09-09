---
id: logiqa2
name: "LogiQA 2.0"
aliases:
  - "LogiQA2"
  - "LogiQA2.0"
  - "logiqa2_zh"
  - "logiqa2_nli"
page_kind: benchmark
category: reasoning
subcategory: "civil-service logical-reasoning MRC (English/Chinese) plus two-way NLI"
status: active
summary: "Expanded civil-service logical-reasoning suite: English and Chinese four-option MRC, plus a two-way NLI conversion of the same items."
measures: >
  LogiQA 2.0 reworks [LogiQA](logiqa.md). Items still come from China's civil-service
  examination materials, now with more questions, professional re-translation, and
  removal of culturally specific wording such as Chinese idioms. The main protocol
  is four-option reading comprehension: a passage, a question, and four answers.
  A second protocol converts each MRC item into premise-hypothesis pairs labelled
  entailed or not entailed. lm-evaluation-harness's `logiqa2` task scores the
  English MRC split only.
task_format: >
  MRC: four-option multiple choice; gold `answer` is an integer 0-3. NLI: two-way
  label entailed / not entailed over major_premise, minor_premise, and conclusion.
  English and Chinese MRC files are released separately. lm-eval `logiqa2` is
  zero-shot multiple choice with acc and acc_norm. A second harness task,
  `logieval`, is a 1-shot generate-until prompt from csitfun/LogiEval, not the
  paper's MRC loader.
metric:
  name: "accuracy (lm-eval also reports acc_norm on the English MRC task)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: null
  baseline_note: >
    Four-option MRC chance is 25%. NLI chance is 50% on a balanced two-way label.
    Counted NLI labels are close to even (train 15,749 entailed / 15,782 not
    entailed). No human-rater figure was read from a page that actually opened
    the IEEE paper body (the IEEE HTML fetch returned empty).
dataset:
  size: 15708
  size_note: >
    English MRC jsonl counted from csitfun/LogiQA2.0: 12,567 train / 1,569 dev /
    1,572 test (15,708). Chinese MRC: 12,751 / 1,593 / 1,594 (15,938). NLI:
    31,531 / 3,941 / 3,942 (39,414). The repository README and Hugging Face
    card still say "35k" NLI pairs; the files on GitHub are larger. lm-eval
    `logiqa2` reads the English MRC via baber/logiqa2 config `logiqa2`.
  url: "https://github.com/csitfun/LogiQA2.0"
  license: "CC BY-NC-SA 4.0 (GitHub README and the baber/logiqa2 loader's _LICENSE string). The Hugging Face cardData license field is cc-by-sa-4.0, which drops NonCommercial; treat the repository statement as the dataset licence."
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "MRC English 12,567/1,569/1,572 train/dev/test; MRC Chinese 12,751/1,593/1,594; NLI 31,531/3,941/3,942"
  public_test_set: true
publisher:
  org: "Westlake University and collaborators; translation funded by Microsoft Research Asia and annotated by Speechocean"
  authors:
    - "Hanmeng Liu"
    - "Jian Liu"
    - "Leyang Cui"
    - "Zhiyang Teng"
    - "Nan Duan"
    - "Ming Zhou"
    - "Yue Zhang"
  url: "https://github.com/csitfun/LogiQA2.0"
paper:
  title: "LogiQA 2.0—An Improved Dataset for Logical Reasoning in Natural Language Understanding"
  arxiv: ""
  url: "https://ieeexplore.ieee.org/document/10174688"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/csitfun/LogiQA2.0"
released: "2023"
last_updated: "2023-08"
lineage:
  family: ""
  predecessor: logiqa
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No current official leaderboard was opened. The IEEE paper body did not
    render in this pass, so 2023 baseline numbers are not copied here. A
    related 2023 preprint (arXiv:2304.03439) evaluates ChatGPT and GPT-4 on
    logical-reasoning sets including LogiQA 2.0; that paper is not the
    dataset release. Hugging Face tags arxiv:2304.03439 on baber/logiqa2,
    which is that evaluation paper, not TASLP 2023.3293046.
contamination:
  risk: high
  note: >
    Train, dev, and test answers are public jsonl on GitHub since the 2023
    release. Source items are public civil-service materials. lm-eval's
    `logiqa2` YAML sets should_decontaminate: false (unlike `logiqa` v1,
    which sets true).
harness:
  lm_eval: "logiqa2"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Runnable YAML in EleutherAI/lm-evaluation-harness: `logiqa2` (English MRC,
    baber/logiqa2 config logiqa2, acc/acc_norm) and `logieval` (generate_until,
    1-shot, exact_match on A-D). The harness README also lists `logiqa2_zh`
    and `logiqa2_NLI`, but those names have no YAML in lm_eval/tasks/logiqa2;
    they exist only as Hugging Face builder configs (logiqa2_zh, logiqa2_nli).
    The README itself says the subtasks have not been verified.
tags:
  - logical-reasoning
  - reading-comprehension
  - multiple-choice
  - nli
  - chinese
  - civil-service-exam
sources:
  - url: "https://raw.githubusercontent.com/csitfun/LogiQA2.0/main/README.md"
    title: "csitfun/LogiQA2.0 README (CC BY-NC-SA 4.0, MRC/NLI layout, IEEE citation)"
    accessed: "2026-09-08"
  - url: "https://github.com/csitfun/LogiQA2.0"
    title: "csitfun/LogiQA2.0 repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/logiqa2/README.md"
    title: "lm-eval logiqa2 README (task names, IEEE citation, unverified note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/logiqa2/logiqa2.yaml"
    title: "lm-eval task logiqa2 (baber/logiqa2, acc/acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/logiqa2/logieval.yaml"
    title: "lm-eval task logieval (1-shot generate_until)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/baber/logiqa2"
    title: "Hugging Face API: baber/logiqa2 (cardData license cc-by-sa-4.0; arxiv tag 2304.03439; lastModified 2023-08-01)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/baber/logiqa2/raw/main/logiqa2.py"
    title: "baber/logiqa2 loader (configs logiqa2/logiqa2_zh/logiqa2_nli/logieval; _LICENSE CC BY-NC-SA 4.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/baber/logiqa2/raw/main/README.md"
    title: "baber/logiqa2 dataset card (cites both TASLP 2023 and arXiv:2304.03439)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2304.03439"
    title: "arXiv:2304.03439 (related ChatGPT/GPT-4 logical-reasoning eval, not the TASLP dataset paper)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-055 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-055"
---

## What it measures

LogiQA 2.0 tests logical reasoning on civil-service exam passages. The model reads a short text, a question, and four options, then picks the supporting, weakening, or entailed choice. The 2023 release enlarges [LogiQA](logiqa.md), re-translates Chinese into English with professional translators, and drops items whose wording is too culture-specific. A second track turns each MRC item into two-way NLI: premises plus a conclusion, labelled entailed or not entailed.

The same questions exist in Chinese and in English. Those file counts are not identical, so a "LogiQA 2.0" score must name the language and the MRC-versus-NLI protocol.

## How it is scored

lm-eval `logiqa2` is English four-option accuracy (`acc`) plus length-normalised `acc_norm`, with no few-shot count in the YAML. Chance is 25%. `logieval` is a different 1-shot generation task that regex-extracts A-D from LogiEval prompts; do not average it with `logiqa2`. NLI scoring, when used, is two-way accuracy on entailed versus not entailed. Fine-tune papers that train on the jsonl splits are not comparable to zero-shot lm-eval.

## Dataset and licence

English MRC jsonl on GitHub has 15,708 lines (12,567 / 1,569 / 1,572). Chinese MRC has 15,938. NLI has 39,414 lines; the README's "35k" figure does not match those files. Test labels ship in the public jsonl. The repository README and the Hugging Face loader string both say CC BY-NC-SA 4.0. The Hugging Face `cardData.license` field says cc-by-sa-4.0. There is no LICENSE file in the GitHub tree. Prefer the README's BY-NC-SA statement.

## Who publishes it

Hanmeng Liu, Jian Liu, Leyang Cui, Zhiyang Teng, Nan Duan, Ming Zhou, and Yue Zhang published the dataset in IEEE/ACM TASLP 2023 (doi 10.1109/TASLP.2023.3293046, volume 31, pages 2947-2962). The GitHub repo is csitfun/LogiQA2.0. Microsoft Research Asia funded the 2021 Speechocean translation. EleutherAI's harness and the baber/logiqa2 mirror are separate.

## Lineage

Predecessor in this repository: [logiqa](logiqa.md) (2020, 8,678 items). LogiQA 2.0 is a new collection plus re-translation, not a rename of the 2020 files. Hugging Face's arxiv:2304.03439 tag points at "Evaluating the Logical Reasoning Ability of ChatGPT and GPT-4", a later eval paper by overlapping authors, not the TASLP dataset paper. LogiEval is an instruction-style wrapper, not a third dataset release.

## Saturation and contamination

Present-day standing is not established here: the IEEE HTML did not render, and no live leaderboard was opened. Contamination risk is high. Test answers have been public jsonl since 2023, and the source exams were already public. lm-eval does not enable decontamination on `logiqa2`.

## How to run it

`lm_eval --tasks logiqa2` loads baber/logiqa2 config `logiqa2` (English MRC). `logieval` is the 1-shot generation sibling in the same folder. `logiqa2_zh` and `logiqa2_nli` are Hugging Face configs without matching harness YAML. Always record language, split, and whether the run was MRC, NLI, or LogiEval.

## Reading the numbers

A high `logiqa2` score means the model picks the labelled option on English civil-service logic items. It does not measure formal proof, math, or Chinese unless that split was run. Do not compare a LogiQA 2.0 number to [logiqa](logiqa.md) or to `logieval` without saying so. Given public labels and the licence mismatch on Hugging Face, read any 2025-era score as possibly contaminated and check which file the reporter actually loaded.
