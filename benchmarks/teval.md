---
id: teval
name: T-Eval
aliases:
  - TEval
  - Tool-Eval
page_kind: benchmark
category: agentic
subcategory: step-wise LLM tool utilization
status: active
summary: >
  A bilingual tool-use benchmark that scores instruction, planning, reasoning,
  retrieval, understanding and review as separate steps rather than one success bit.
measures: >
  T-Eval tests whether a model can use tools by grading each sub-skill on its
  own. Given a query and a tool list, the model must plan, pick tools, fill
  parameters, emit a call, and review the tool response. The authors argue that
  scoring only the final answer hides which of those steps failed. English and
  Chinese prompts both exist. This is not a coding benchmark and not ToolBench's
  end-to-end win rate, though the paper plots the two against each other.
task_format: >
  Multi-turn chat with system/user/assistant roles and a tool schema in the
  prompt. OpenCompass uses `ChatInferencer` and `TEvalEvaluator` on local JSON
  files named `instruct_v1`, `plan_json_v1`, `plan_str_v1`, and similar. Hugging
  Face `lovesnowbest/T-Eval` currently ships v2 files (`instruct_v2.json`, ...).
metric:
  name: overall (mean of subset metrics)
  direction: higher_is_better
  unit: ""
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Overall is the average of the six skill groups. The paper's Table 1 gives
    GPT-4 an overall 86.4. Subset files use mixed string/JSON protocols, so a
    single random baseline is not defined.
dataset:
  size: 23305
  size_note: >
    Paper Table 2: 23,305 English test cases from 553 verified query-solution
    pairs (the same paper also says 533 pairs in Appendix A.1). Breakdown:
    Instruct 2,660, Retrieve 6,426, Plan 553, Reason 6,426, Review 487,
    Understand 6,753. Hugging Face v2 keeps 553 objects in most subset files
    (487 in review) for both EN and ZH; those objects are queries, not the
    23,305 expanded cases. OpenCompass still points at v1 filenames under
    `./data/teval/EN` and `./data/teval/ZH`.
  url: https://huggingface.co/datasets/lovesnowbest/T-Eval
  license: Apache-2.0
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "no train/test split; evaluation JSONs per skill, EN and ZH"
  public_test_set: true
publisher:
  org: "University of Science and Technology of China / Shanghai AI Laboratory / Tsinghua University / Jilin University / OpenCompass"
  authors:
    - Zehui Chen
    - Weihua Du
    - Wenwei Zhang
    - Kuikun Liu
    - Jiangning Liu
    - Miao Zheng
    - Jingming Zhuo
    - Songyang Zhang
    - Dahua Lin
    - Kai Chen
    - Feng Zhao
  url: https://github.com/open-compass/T-Eval
paper:
  title: "T-Eval: Evaluating the Tool Utilization Capability of Large Language Models Step by Step"
  arxiv: "2312.14033"
  url: https://arxiv.org/abs/2312.14033
  year: 2024
leaderboard_url: https://open-compass.github.io/T-Eval/leaderboard.html
repo_url: https://github.com/open-compass/T-Eval
released: "2023-12"
last_updated: "2024-02"
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
    The paper reports GPT-4 at 86.4 overall on the original English tables
    (December 2023 / January 2024). The live leaderboard URL was not successfully
    fetched here, so no later top score is recorded.
contamination:
  risk: medium
  note: >
    Queries, tools and gold traces are public (GitHub, Google Drive, Hugging
    Face). The 2024-02 v2 refresh changes file layout. That is newer than SVAMP
    or TabMWP, but the gold calls are not held out.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: teval
  bigbench: ""
  other: >
    OpenCompass configs `teval_en_gen` and `teval_zh_gen` expand to abbrs such as
    `teval-instruct_v1` and `teval-plan_json_v1_zh`. The standalone
    open-compass/T-Eval repo with Lagent is the paper's harness. CompassBench
    v1.1/v1.3 fold T-Eval / plugin_eval into an agent category; that composite
    is not this page.
tags:
  - tools
  - agents
  - bilingual
  - planning
  - instruction-following
sources:
  - url: https://arxiv.org/abs/2312.14033
    title: "T-Eval paper (arXiv abs)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2312.14033
    title: T-Eval HTML full text on ar5iv
    accessed: "2026-09-08"
  - url: https://aclanthology.org/2024.acl-long.515/
    title: "T-Eval ACL 2024 long paper (anthology 2024.acl-long.515)"
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/T-Eval
    title: open-compass/T-Eval repository (ACL 2024 badge, Apache-2.0)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/T-Eval/main/README.md
    title: T-Eval GitHub README
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/T-Eval/main/LICENSE
    title: T-Eval Apache-2.0 LICENSE
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/lovesnowbest/T-Eval
    title: lovesnowbest/T-Eval dataset card
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/lovesnowbest/T-Eval
    title: lovesnowbest/T-Eval Hugging Face API (v2 JSON siblings)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/teval/README.md
    title: OpenCompass teval config README
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/teval/teval_en_gen_1ac254.py
    title: OpenCompass teval_en_gen_1ac254.py (v1 filenames)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/teval/__init__.py
    title: OpenCompass TEvalDataset loader
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-022 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-022"
---

## What it measures

T-Eval grades tool use one step at a time. The model is given a user query and a list of APIs. It must follow the call format (instruct), plan a sequence, reason about the next action, retrieve the right tool, fill parameters (understand), and review the tool's reply. Each of those skills has its own subset, so a model can be strong at JSON calls and weak at planning.

Items are bilingual. English and Chinese files are parallel. This is not ToolBench's end-to-end "did the agent finish the task" score. The paper shows T-Eval overall moving with ToolBench win rate, then uses the subsets to say which step broke.

## How it is scored

Each subset has its own metric; overall is their average. The paper's Table 1 lists GPT-4 at 86.4 overall. Plan comes in JSON and string forms; reason, retrieve and understand likewise. OpenCompass wraps those files with `TEvalEvaluator(subset=...)` and a chat inferencer.

Do not mix an OpenCompass `teval-instruct_v1` number with a Hugging Face v2 file, or an English overall with a Chinese overall. The official scripts call `convert_results.py` after dumping per-query JSON.

## Dataset and licence

The paper builds 23,305 English test cases from a few hundred verified query-solution traces (553 in the main text, 533 in Appendix A.1). Table 2 splits those cases across six skills. Hugging Face v2 stores 553 query objects per most files (487 for review) in both languages. OpenCompass still documents v1 names under `data/teval/EN` and `ZH`. The Hub card's `100M<n<1B` size tag does not match these counts and is ignored.

GitHub and the Hub card state Apache-2.0. Gold traces are public.

## Who publishes it

Zehui Chen, Weihua Du, Wenwei Zhang and colleagues at USTC, Shanghai AI Laboratory, Tsinghua and Jilin University. arXiv 2312.14033 appeared 21 December 2023 (v3 15 January 2024). ACL 2024 published it as a long paper (anthology 2024.acl-long.515). Code is open-compass/T-Eval. A Chinese leaderboard is linked beside the English one. The live English leaderboard HTML did not expose scores without JavaScript.

## Lineage

T-Eval is a process-level tool benchmark, not a clone of ToolBench. [CompassBench v1.3](compassbench_v1_3.md) and [CompassBench 20 v1.1](compassbench_20_v1_1.md) reuse T-Eval / plugin_eval as their agent slice; those composites are separate pages. No successor id exists here.

## Saturation and contamination

GPT-4 already sat at 86.4 on the original English overall, so headroom depends on the subset. No later leaderboard scrape is recorded. Public gold traces make leakage possible; the 2024-02 v2 files are a mild refresh, not a hidden test.

## How to run it

Standalone: clone open-compass/T-Eval, put the JSON files in `data/`, run `test_all_en.sh` or `test_all_zh.sh`. OpenCompass: `--datasets teval_en_gen` or `teval_zh_gen`. Those configs still name v1 files. A `meta_template` must match the chat model. Do not compare a subset score with the paper's overall.

## Reading the numbers

A T-Eval overall is a mean of six tool skills, not a single agent success rate. Instruct can look high while plan is low. English and Chinese are separate. If a CompassBench card says T-Eval, it is that suite's agent category, not a full T-Eval run. For end-to-end tool success, look at the paper's ToolBench comparison rather than this page.
