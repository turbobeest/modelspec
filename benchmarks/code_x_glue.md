---
id: code_x_glue
name: "CodeXGLUE"
aliases:
  - "Code-X-GLUE"
  - "Code X GLUE"
  - "codexglue"
  - "code2text"
page_kind: family
category: coding
subcategory: "Microsoft 10-task code understanding and generation suite; lm-eval ships code-to-text"
status: active
summary: "Microsoft CodeXGLUE is a 10-task, 14-dataset suite for code understanding and generation; EleutherAI lm-eval currently ships only the code-to-text group."
measures: >
  CodeXGLUE (General Language Understanding Evaluation for CODE) is Microsoft's
  2021 suite of 10 code-intelligence tasks on 14 datasets. The four scenarios
  are code-code (clone detection, defect detection, cloze, completion, repair,
  translation), text-code (search and text-to-code), code-text (summarization),
  and text-text (documentation translation). EleutherAI lm-evaluation-harness
  implements only the code-to-text group under lm_eval/tasks/code_x_glue:
  generate a natural-language docstring from tokenized code in Go, Java,
  JavaScript, PHP, Python, or Ruby. That wrap is CodeSearchNet-derived
  summarization scored with smoothed BLEU-4, not the whole suite.
task_format: >
  lm-eval code2text: generate_until on Hub datasets CM/codexglue_code2text_*.
  doc_to_text joins code_tokens; doc_to_target joins docstring_tokens.
  Beam 10, max_gen_toks 128, stop at </s>. Official CodeXGLUE tasks use
  task-specific metrics (accuracy, MAP, CodeBLEU, BLEU, EM) and often hold
  out test labels for email submission.
metric:
  name: "smoothed BLEU-4 (lm-eval code2text); suite-wide metrics vary by task"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Code-to-text README reports CodeBERT smoothed BLEU-4 of 12.16 Ruby, 14.90
    JavaScript, 18.07 Go, 19.06 Python, 17.65 Java, 25.16 PHP, 17.83 overall,
    against Seq2Seq 14.32 overall. Those are encoder-decoder baselines from
    2021, not LLM few-shot numbers. Clone, defect, and cloze tasks use
    accuracy or MAP instead. Do not copy a CodeBERT BLEU onto an lm-eval
    generate_until run without matching beam size and preprocessing.
dataset:
  size: null
  size_note: >
    Paper: 10 tasks, 14 datasets. Code-to-text (CodeSearchNet, filtered) test
    sizes from the Code-Text README and the Hub python card: Python 14,918,
    PHP 14,014, Go 8,122, Java 10,955, JavaScript 3,291, Ruby 1,261 (52,561
    test functions). Train: 251,820 / 241,241 / 167,288 / 164,923 / 58,025 /
    24,927. Other CodeXGLUE tasks (BigCloneBench, Devign, PY150, CONCODE,
    and the rest) are not in the lm-eval directory. This repository already
    has [clozetest_maxmin](clozetest_maxmin.md) as an OpenCompass wrap of
    another CodeXGLUE task.
  url: "https://github.com/microsoft/CodeXGLUE"
  license: "MIT (repository code); C-UDA (datasets, per README)"
  languages:
    - Python
    - Java
    - JavaScript
    - PHP
    - Go
    - Ruby
    - "C#"
    - en
  modalities:
    - code
    - text
  splits: "per dataset; code-to-text has train/validation/test jsonl (lm-eval uses those Hub splits)"
  public_test_set: true
publisher:
  org: "Microsoft Research Asia, Developer Division, and Bing"
  authors:
    - "Shuai Lu"
    - "Daya Guo"
    - "Shuo Ren"
    - "Junjie Huang"
    - "Alexey Svyatkovskiy"
    - "Ambrosio Blanco"
    - "Colin Clement"
    - "Dawn Drain"
    - "Daxin Jiang"
    - "Duyu Tang"
    - "Ge Li"
    - "Lidong Zhou"
    - "Linjun Shou"
    - "Long Zhou"
    - "Michele Tufano"
    - "Ming Gong"
    - "Ming Zhou"
    - "Nan Duan"
    - "Neel Sundaresan"
    - "Shao Kun Deng"
    - "Shengyu Fu"
    - "Shujie Liu"
  url: "https://github.com/microsoft/CodeXGLUE"
paper:
  title: "CodeXGLUE: A Machine Learning Benchmark Dataset for Code Understanding and Generation"
  arxiv: "2102.04664"
  url: "https://arxiv.org/abs/2102.04664"
  year: 2021
leaderboard_url: "https://microsoft.github.io/CodeXGLUE/"
repo_url: "https://github.com/microsoft/CodeXGLUE"
released: "2021-02"
last_updated: "2021-03"
lineage:
  family: ""
  predecessor: glue
  successors: []
  variants:
    - clozetest_maxmin
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    CodeBERT's 17.83 overall code-to-text BLEU is a 2021 pretrained-encoder
    baseline, not a modern LLM ceiling. Official test labels for several
    tasks are held for email submission. No current CodeXGLUE leaderboard
    cell was parsed from microsoft.github.io/CodeXGLUE/ (static HTML).
contamination:
  risk: high
  note: >
    Code-to-text functions come from CodeSearchNet GitHub dumps and have been
    public since 2019/2021, with tokenized code and docstrings in the clear.
    Clone and completion corpora are likewise public GitHub. Models trained
    on GitHub can have seen the unmasked functions.
harness:
  lm_eval: "code2text"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Runnable lm-eval tasks: code2text_python, code2text_java, code2text_javascript, code2text_php, code2text_go, code2text_ruby (group code2text). Directory is lm_eval/tasks/code_x_glue/code-text. OpenCompass clozeTest_maxmin is a different CodeXGLUE task."
tags:
  - coding
  - code-summarization
  - bleu
  - family
  - microsoft
  - lm-eval
sources:
  - url: "https://arxiv.org/abs/2102.04664"
    title: "CodeXGLUE paper (arXiv:2102.04664v2, 10 tasks / 14 datasets)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/README.md"
    title: "CodeXGLUE README (tasks, C-UDA datasets, MIT code, leaderboard)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/LICENSE"
    title: "CodeXGLUE repository MIT license"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/Code-Text/code-to-text/README.md"
    title: "Code-to-text README (split sizes, smoothed BLEU-4, CodeBERT table)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/code_x_glue/code-text/README.md"
    title: "lm-eval code_x_glue/code-text README (group code2text, NeurIPS 2021)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/code_x_glue/code-text/_codexglue.yaml"
    title: "lm-eval code2text group YAML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/code_x_glue/code-text/_default_template_yaml"
    title: "lm-eval code2text generate_until template (beam 10, BLEU-4)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/CM/codexglue_code2text_python"
    title: "Hub CM/codexglue_code2text_python (251820 / 13914 / 14918)"
    accessed: "2026-09-08"
  - url: "https://microsoft.github.io/CodeXGLUE/"
    title: "CodeXGLUE leaderboard site"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-032 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-032"
---

## What it measures

CodeXGLUE is a Microsoft suite, not a single prompt format. The 2021 paper counts 10 tasks on 14 datasets covering clone detection, defect detection, cloze, completion, repair, translation, code search, text-to-code, code summarization, and documentation translation. The name is GLUE for code.

This repository id matches the lm-eval directory `code_x_glue`. That directory only contains code-to-text: the model sees tokenized source and must write a docstring. Languages are Go, Java, JavaScript, PHP, Python, and Ruby. Other CodeXGLUE tasks live in the Microsoft repo and in OpenCompass cloze configs, not in this lm-eval folder.

## How it is scored

lm-eval `code2text_*` uses `smoothed_bleu_4` from the task's `bleu.py`, mean-aggregated and weighted by size in the `code2text` group. Generation is beam 10, 128 tokens, stop at `</s>`. The official Code-to-text README uses the same smoothed BLEU-4 script. CodeBERT's 17.83 overall is that protocol on the 2021 test files.

The rest of the suite does not use BLEU. Cloze is accuracy. Defect and clone detection are classification or retrieval. Text-to-code uses EM/BLEU/CodeBLEU. Microsoft asked for email submission of test predictions and did not publish some test labels. An lm-eval docstring BLEU is not a CodeXGLUE average.

## Dataset and licence

Code-to-text is filtered CodeSearchNet: drop unparseable functions, short or long docs, special tokens, and non-English docs. Test counts in the Code-Text README (and the Python Hub card) are Python 14,918, PHP 14,014, Go 8,122, Java 10,955, JavaScript 3,291, Ruby 1,261. lm-eval loads `CM/codexglue_code2text_{lang}`. The repository LICENSE is MIT. The README says datasets follow the Computational Use of Data Agreement (C-UDA). The Python Hub card has no licence field.

## Who publishes it

Shuai Lu, Daya Guo, Shuo Ren, and coauthors at Microsoft Research Asia, Developer Division, and Bing posted arXiv 2102.04664 on 9 February 2021 (v2 16 March 2021). lm-eval cites NeurIPS Datasets and Benchmarks 2021. The leaderboard URL is https://microsoft.github.io/CodeXGLUE/. Official scoring contact in the README is `codexglue@microsoft.com`.

## Lineage

The suite is named after [glue](glue.md). Code-to-text reuses CodeSearchNet (Husain et al., 2019). This repository already documents [clozetest_maxmin](clozetest_maxmin.md), an OpenCompass A/B wrap of CodeXGLUE ClozeTest-maxmin; that is not this lm-eval group. [humaneval](humaneval.md) and [mbpp](mbpp.md) execute generated code. They do not score docstring BLEU. No `clozetest_all` page exists yet.

## Saturation and contamination

CodeBERT's mid-teens BLEU is not a ceiling for instruction-tuned models, and BLEU saturates poorly on short docs. Functions and docstrings have been public for years, so GitHub-trained models can copy comments. Microsoft's held-out test labels apply only to the email protocol, not to the Hub jsonl that lm-eval uses.

## How to run it

In lm-eval, run group `code2text` or a language task such as `code2text_python`. Do not pass `code_x_glue` as a task name; that is the directory. Beam size, max tokens, and the smoothed BLEU script must match to compare with the README table. OpenCompass `clozeTest_maxmin` is a different task. inspect_evals and HELM names were not found for this id.

## Reading the numbers

A 20 BLEU on `code2text_python` means n-gram overlap with Hub docstrings, not that the model can pass unit tests. Language averages hide Ruby versus PHP. Do not blend this BLEU with HumanEval pass@1 or with OpenCompass max/min cloze accuracy. If the paper you are reading reports CodeBERT 17.83, check whether the new model used beam 10 on the same filtered test files.
