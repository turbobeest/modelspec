---
id: rolebench
name: "RoleBench"
aliases:
  - "RoleLLM"
  - "RoleBench (RoleLLM)"
page_kind: benchmark
category: generation
subcategory: "character-level role-play: instruction and role generalization, English and Chinese"
status: active
summary: "A 168,093-sample role-play benchmark over 100 characters; OpenCompass scores English and Chinese splits with ROUGE against RoleGPT-style references."
measures: >
  RoleBench tests whether a model can stay in character. Each item names a role, gives a
  short profile, and asks a question. The model must answer in that voice without breaking
  character. The paper splits evaluation two ways: instruction generalization (held-out
  questions for seen roles) and role generalization (held-out English roles). Profiles cover
  95 English characters and 5 Chinese ones (100 roles). References come from RoleGPT
  (GPT-4 role prompting) and Context-Instruct, not from human scripts of the same replies.
  OpenCompass runs three of those splits as generation tasks.
task_format: >
  Chat-style generation: a system prompt that assigns the role and description, then a
  user question. OpenCompass is zero-shot with max_out_len 512. English uses RougeEvaluator;
  Chinese uses JiebaRougeEvaluator.
metric:
  name: "ROUGE-L (OpenCompass RougeEvaluator / JiebaRougeEvaluator); paper also reports GPT-3.5 judgments"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper's protocol is ROUGE-L against RoleGPT/Context-Instruct references, plus GPT-3.5
    pairwise or rating judgments. OpenCompass reports the ROUGE family from RougeEvaluator
    (English) or JiebaRougeEvaluator (Chinese). No single 0-100 headline and no human ROUGE
    baseline were extracted from the paper HTML.
dataset:
  size: 168093
  size_note: >
    Paper and Hugging Face card: 168,093 samples over 100 roles. OpenCompass concatenates
    general plus role_specific jsonl, then shuffles with seed 42. Line counts on the Hub
    test files used by OpenCompass: instruction-generalization English 28,083 general +
    4,750 role-specific (32,833 test); role-generalization English 5,000 + 2,534 (7,534
    test); Chinese instruction-generalization 1,451 + 239 (1,690 test). Train files for
    English instruction-generalization add 112,142 + 18,949. Role-generalization and
    Chinese train files were not line-counted here. Do not add every split: they overlap
    as different partitions of the same pool.
  url: "https://huggingface.co/datasets/ZenMoore/RoleBench"
  license: "Apache-2.0"
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "per-split train/test jsonl under rolebench-eng/instruction-generalization, rolebench-eng/role-generalization, and rolebench-zh"
  public_test_set: true
publisher:
  org: "InteractiveNLP-Team (RoleLLM)"
  authors:
    - "Zekun Moore Wang"
    - "Zhongyuan Peng"
    - "Haoran Que"
    - "Jiaheng Liu"
    - "Wangchunshu Zhou"
    - "Yuhan Wu"
    - "Hongcheng Guo"
    - "Ruitong Gan"
    - "Zehao Ni"
    - "Jian Yang"
    - "Man Zhang"
    - "Zhaoxiang Zhang"
    - "Wanli Ouyang"
    - "Ke Xu"
    - "Stephen W. Huang"
    - "Jie Fu"
    - "Junran Peng"
  url: "https://github.com/InteractiveNLP-Team/RoleLLM-public"
paper:
  title: "RoleLLM: Benchmarking, Eliciting, and Enhancing Role-Playing Abilities of Large Language Models"
  arxiv: "2310.00746"
  url: "https://arxiv.org/abs/2310.00746"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/InteractiveNLP-Team/RoleLLM-public"
released: "2023-10"
last_updated: "2023-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: "2023-10"
  note: >
    No maintained public leaderboard was found. The paper compares RoleGPT (GPT-4), RoleLLaMA
    and RoleGLM on ROUGE-L and GPT-3.5 judges; a single current top ROUGE was not extracted
    from the HTML tables. OpenCompass still ships the three configs.
contamination:
  risk: medium
  note: >
    The full train and test jsonl, including RoleGPT references, have been public on Hugging
    Face since 19 October 2023 under Apache-2.0. Many roles are famous fictional or historical
    figures whose dialogue is common in pretraining. Nothing is held out or refreshed.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    RoleBench_instruct_eng (InstructionGeneralizationEnglishDataset),
    RoleBench_role_eng (RoleGeneralizationEnglishDataset),
    RoleBench_instruct_zh (InstructionGeneralizationChineseDataset);
    path ZenMoore/RoleBench
  bigbench: ""
  other: "OpenCompass integration noted on the RoleLLM README (PR 633, 2023-12-01). No lm-eval or inspect_evals task was found."
tags:
  - role-play
  - generation
  - rouge
  - english
  - chinese
sources:
  - url: "https://arxiv.org/abs/2310.00746"
    title: "RoleLLM paper abs (arXiv:2310.00746); 168,093 samples, 100 roles"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2310.00746"
    title: "RoleLLM paper HTML (ROUGE-L protocol, instruction vs role generalization)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ZenMoore/RoleBench/raw/main/README.md"
    title: "ZenMoore/RoleBench card: Apache-2.0, file layout, 100 roles"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ZenMoore/RoleBench"
    title: "ZenMoore/RoleBench API (created 2023-10-19, licence apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/InteractiveNLP-Team/RoleLLM-public/main/README.md"
    title: "RoleLLM-public README; OpenCompass integration 2023-12-01"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/rolebench/instruction_generalization_eng.py"
    title: "OpenCompass RoleBench_instruct_eng + RougeEvaluator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/rolebench/role_generalization_eng.py"
    title: "OpenCompass RoleBench_role_eng"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/rolebench/instruction_generalization_zh.py"
    title: "OpenCompass RoleBench_instruct_zh + JiebaRougeEvaluator"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/rolebench.py"
    title: "RoleBench loaders concatenate general/ and role_specific/ jsonl"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-020 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-020"
---

## What it measures

RoleBench asks a model to speak as a named character. The prompt gives the role and a profile, then a question. A good reply matches that character's knowledge and style and does not admit to being a language model. The English set has 95 roles (Sherlock Holmes, Jack Sparrow, HAL 9000, and others). The Chinese set has five (including 孙悟空 and 李白). Instruction-generalization holds out questions; role-generalization holds out English roles. References are RoleGPT outputs, so the test is overlap with a GPT-4 teacher, not with a human actor.

OpenCompass does not ship a Chinese role-generalization config. Its three tasks are English instruction generalization, English role generalization, and Chinese instruction generalization.

## How it is scored

The paper uses ROUGE-L against the stored RoleGPT/Context-Instruct strings, plus GPT-3.5 as a judge. OpenCompass uses `RougeEvaluator` (English) or `JiebaRougeEvaluator` (Chinese) on the generated turn, `max_out_len` 512. There is no accuracy ceiling of 100 that both protocols share. A higher ROUGE means closer n-gram overlap with the teacher, not that a fan would accept the voice. GPT-judge numbers from the paper are a different scale from OpenCompass ROUGE.

## Dataset and licence

The authors state 168,093 samples. Hugging Face `ZenMoore/RoleBench` is Apache-2.0, created 19 October 2023. Each OpenCompass split concatenates `general/` and `role_specific/` jsonl, using `generated[0]` as the answer. Test-file line counts for the three OpenCompass tasks are 32,833, 7,534 and 1,690. Train and test answers are public. Hugging Face datasets-server did not return split metadata for the default config.

## Who publishes it

The RoleLLM team (InteractiveNLP-Team), with Wang and Peng among the primary authors. The paper is arXiv:2310.00746 (1 October 2023). The public code repo is RoleLLM-public. OpenCompass added the configs on 1 December 2023 (their README). There is no live leaderboard URL.

## Lineage

Standalone. It is the evaluation piece of RoleLLM, alongside RoleGPT, RoleLLaMA and RoleGLM. It is not [MT-Bench](mt_bench.md) (multi-turn helpfulness) and not a subset of [EQ-Bench](eq_bench.md). No successor page is in this repository.

## Saturation and contamination

No current public table was confirmed, so saturation is unknown. The test strings have been on the Hub since 2023, and the characters are famous, so medium contamination risk. A model trained on RoleBench itself will look strong on ROUGE without being a better role-player on unseen characters.

## How to run it

`datasets.load_dataset("ZenMoore/RoleBench")` or OpenCompass configs under `configs/datasets/rolebench/`. Abbreviations: `RoleBench_instruct_eng`, `RoleBench_role_eng`, `RoleBench_instruct_zh`. System prompts differ by language. No lm-eval or inspect_evals task was found. Compare ROUGE only within one split and one tokenizer (Jieba vs space-token ROUGE).

## Reading the numbers

A high OpenCompass ROUGE means the model echoed the RoleGPT reference for that split. It does not prove faithful long-script knowledge, safety under jailbreaks, or preference-level acting quality. Read instruction-generalization and role-generalization separately: the second is the stricter unseen-role test. Pair with a human or LLM-judge protocol if the claim is "better role-play," not "higher ROUGE to GPT-4."
