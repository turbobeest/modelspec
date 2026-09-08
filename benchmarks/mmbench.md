---
id: mmbench
name: "MMBench"
aliases:
  - "MMBench_DEV_EN"
  - "MMBench-EN"
page_kind: benchmark
category: multimodal
subcategory: "bilingual vision-language multiple-choice with CircularEval"
status: active
summary: "A bilingual vision-language multiple-choice benchmark with CircularEval over 20 ability dimensions; English and Chinese Dev and Test splits."
measures: >
  MMBench tests whether a vision-language model can answer a multiple-choice
  question about an image across a taxonomy of perception and reasoning
  skills, rather than on one downstream task such as captioning or VQA.
  Questions are written in English and in a matched Chinese translation.
  Level-1 abilities are Perception and Reasoning; those split into six
  level-2 groups and twenty level-3 skills. Images plus text; not video.
task_format: >
  Multiple-choice with a single gold option. Free-form model text is mapped
  to A/B/C/D first by rule matching, then by an LLM choice extractor. Paper
  v5 uses GPT-4 (gpt-4-0125 by default); the GitHub README still says
  ChatGPT. CircularEval repeats each N-option item N times with rotated
  choices; the item counts only if every pass is correct. OpenCompass's
  in-tree config wraps VLMEvalKit MMBench_DEV_EN only.
metric:
  name: CircularEval accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Option count is not fixed across items, so no single chance baseline is
    stated. CircularEval is stricter than one-pass accuracy; the README says
    a 10–20% drop versus vanilla top-1 is common. No human-exam baseline was
    confirmed from the sources opened here.
dataset:
  size: 2948
  size_note: >
    Official GitHub README table (accessed 2026-09-08): English Dev 1,164 and
    Test 1,784 (2,948); Chinese Dev/Test the same counts; CCBench is a
    separate 510-item Chinese-culture set. README prose also says
    "approximately 3000" and "currently, contains 2974" questions. The paper
    (arXiv:2307.06281) states 3,217 questions spanning 20 L-3 abilities.
    This page records 2,948 from the README split table as the current
    English MMBench Dev+Test total and leaves the paper/prose mismatch in
    the note.
  url: "https://github.com/open-compass/MMBench"
  license: "Apache-2.0"
  languages:
    - en
    - zh
  modalities:
    - text
    - image
  splits: "Dev (1,164) and Test (1,784) per language; Chinese splits are a verified translation of the English items"
  public_test_set: false
publisher:
  org: "OpenCompass / Shanghai AI Laboratory, with CUHK, NUS and Zhejiang University"
  authors:
    - "Yuan Liu"
    - "Haodong Duan"
    - "Yuanhan Zhang"
    - "Bo Li"
    - "Songyang Zhang"
    - "Wangbo Zhao"
    - "Yike Yuan"
    - "Jiaqi Wang"
    - "Conghui He"
    - "Ziwei Liu"
    - "Kai Chen"
    - "Dahua Lin"
  url: "https://github.com/open-compass/MMBench"
paper:
  title: "MMBench: Is Your Multi-modal Model an All-around Player?"
  arxiv: "2307.06281"
  url: "https://arxiv.org/abs/2307.06281"
  year: 2024
leaderboard_url: "https://mmbench.opencompass.org.cn/mmbench-submission"
repo_url: "https://github.com/open-compass/MMBench"
released: "2023-07"
last_updated: "2024-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 78.1
  as_of: "2024-08"
  note: >
    Paper v5 HTML Table 3, CircularEval on MMBench-test L-2 overall:
    InternLM-XComposer2* 78.1%, Qwen-VL-Max 75.4%, GPT-4v 74.3%. HTML Table 2
    is MMBench-dev CircularEval (InternLM-XComposer2 79.1%, Qwen-VL-Max 76.4%,
    GPT-4v 74.3%). The asterisk marks extra in-house data. No later public
    top score was confirmed from a rendered leaderboard here. 78% is well
    below 100% under CircularEval.
contamination:
  risk: medium
  note: >
    Dev labels are in the public TSVs (the README's display example shows
    ANSWER). Test answers are submitted to the OpenCompass server rather than
    shipped as a public key file. Questions and images have been public since
    2023. This is not a fully hidden test, but it is not a fully labelled
    public test either.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "MMBench"
  bigbench: ""
  other: >
    OpenCompass in-tree config is MMBench_DEV_EN_vlmevalkit_gen.py, dataset
    abbr MMBench_DEV_EN, scored through VLMEvalKit. Official eval is
    VLMEvalKit (`python run.py --model … --data MMBench_TEST_EN`). Test
    predictions are an xlsx uploaded at mmbench.opencompass.org.cn. Other
    VLMEvalKit names: MMBench_DEV_CN, MMBench_TEST_CN. CCBench is a sibling
    Chinese-culture set, not MMBench.
tags:
  - multimodal
  - vision-language
  - multiple-choice
  - circular-eval
  - bilingual
sources:
  - url: "https://arxiv.org/abs/2307.06281"
    title: "MMBench: Is Your Multi-modal Model an All-around Player? (arXiv:2307.06281)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2307.06281"
    title: "MMBench paper HTML (3,217 questions, CircularEval, HTML Tables 2–3 scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/MMBench/main/README.md"
    title: "open-compass/MMBench README (split table 1164/1784, CircularEval, VLMEvalKit)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/MMBench/main/LICENSE"
    title: "MMBench Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/MMBench/MMBench_DEV_EN_vlmevalkit_gen.py"
    title: "OpenCompass MMBench_DEV_EN VLMEvalKit wrapper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-016 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-016"
---

## What it measures

MMBench asks a vision-language model to pick one option on a question about an image. The authors grouped items into Perception and Reasoning, then into six mid-level skills and twenty leaf skills (for example coarse perception, single-instance detail, attribute reasoning). The goal is a fine-grained ability profile, not a score on captioning or VQA as a task. English and Chinese versions of the same items exist so bilingual gaps can be compared. Text plus image; not video, and not [MMMU](mmmu.md), which is college-exam knowledge with figures.

## How it is scored

The headline protocol is CircularEval. For an N-option item the harness runs N passes, rotating the option order each time; the item is correct only if every pass is correct. The README says this often cuts top-1 accuracy by 10–20% versus a single pass. Free-form answers are mapped to a letter by rules, then by an LLM extractor. Paper v5 uses GPT-4 (gpt-4-0125); the README still names ChatGPT. Test-split scores come from submitting an xlsx to the OpenCompass server; Dev can be scored locally. OpenCompass's repository config in this tree only wraps VLMEvalKit `MMBench_DEV_EN`.

## Dataset and licence

The official README table lists 1,164 Dev and 1,784 Test items in English (2,948) and the same counts in Chinese, plus a separate 510-item CCBench. README prose still says about 3,000 and "currently, contains 2974" questions. The paper states 3,217 items. This page uses the table's 2,948 for English Dev+Test and treats 2,974 / 3,217 as unresolved. Items were collected from public datasets and the web. The repository LICENSE is Apache-2.0. Dev labels are in the public TSVs. Test labels are not distributed for local scoring.

## Who publishes it

Yuan Liu, Haodong Duan, Yuanhan Zhang, Bo Li, Songyang Zhang, Wangbo Zhao, Yike Yuan, Jiaqi Wang, Conghui He, Ziwei Liu, Kai Chen and Dahua Lin, at OpenCompass / Shanghai AI Laboratory with CUHK, NUS and Zhejiang University. Posted as arXiv:2307.06281 on 12 July 2023 (v5 20 August 2024) and published as an ECCV 2024 oral. Code: github.com/open-compass/MMBench. Evaluation: VLMEvalKit. Test submission: mmbench.opencompass.org.cn.

## Lineage

MMBench sits among vision-language multiple-choice suites such as [MMMU](mmmu.md) and [AI2D](ai2d.md); it is not a child of those pages. CCBench (Chinese culture, 510 items) is shipped from the same README table but is a different benchmark. MMBench-Video, if reported elsewhere, is not this id. OpenCompass `MMBench` in this repository is the Dev-EN VLMEvalKit wrapper, not the full bilingual test.

## Saturation and contamination

Paper v5 CircularEval on the test set (HTML Table 3) puts InternLM-XComposer2* at 78.1% overall, Qwen-VL-Max at 75.4% and GPT-4v at 74.3% (August 2024). Qwen-VL-Max 76.4% is the Dev CircularEval figure in HTML Table 2, not the test overall. That is not a ceiling. No later leaderboard figure was extracted here. Dev answers are public; test answers are server-side. Questions have been on the web since 2023, so contamination risk is medium rather than low.

## How to run it

Official: VLMEvalKit `run.py --data MMBench_TEST_EN` (or `_DEV_EN`, `_TEST_CN`, `_DEV_CN`), then upload test xlsx for server scoring. OpenCompass: config directory `datasets/MMBench`, runnable abbr `MMBench_DEV_EN`. A Dev-EN number is not a Test-EN CircularEval number. LLM-extractor choice and whether CircularEval was on change the score.

## Reading the numbers

A high CircularEval score means the model still picks the right letter after the options have been rotated, not only that it answered once in a preferred order. It does not measure open-ended captioning, exam-level subject knowledge, or video. Compare English and Chinese only when the split and CircularEval setting match. Treat Dev scores as more exposed than Test. Quote VLMEvalKit versus OpenCompass Dev-EN before stacking two "MMBench" figures.
