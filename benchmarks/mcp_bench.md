---
id: mcp_bench
name: MCP-Bench
aliases:
  - MCP-Bench
  - MCPBench
  - mcp-bench
page_kind: benchmark
category: agentic
subcategory: tool-using agents on live Model Context Protocol servers
status: active
summary: >
  MCP-Bench scores agents on 104 fuzzy multi-step tasks that must call tools
  across 28 live MCP servers (250 tools) without being told the tool names.
measures: >
  The agent gets a vague English instruction, a pool of MCP servers, and must
  finish a real-world style job: search papers, plan travel, convert units,
  query weather, and similar. Servers expose complementary tools, so a task
  often needs a chain, not one call. Instructions are fuzzy: they do not name
  the tool. Extra distraction servers are in the pool by default. The run
  mixes single-server tasks with two-server and three-server combinations.
  Scoring splits rule-based schema checks from an o4-mini judge of completion,
  tool use, and planning.
task_format: >
  Multi-round tool calling over live MCP (default max 20 rounds). Official
  task files: 56 single-server, 30 two-server, 18 three-server (104 total).
  Fuzzy descriptions on; concrete text and dependency notes are held for the
  judge. Time MCP is a resident server.
metric:
  name: overall score (rule-based schema checks plus LLM-judge axes)
  direction: higher_is_better
  unit: ''
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Leaderboard overall score is in [0, 1], averaged across single-server and
    multi-server settings. Rule-based traces score valid tool names, schema
    compliance, runtime success, and dependency order. The o4-mini judge
    scores task completion, tool usage, and planning on 1-10 rubrics,
    normalized to [0, 1], with five shuffled rubric-order passes averaged.
    Hugging Face space data.json (lastUpdated 2025-09-05) and the GitHub
    README both list gpt-5 at 0.749 as the top overall score among 20 models.
dataset:
  size: 104
  size_note: >
    Paper conclusion: 104 synthesized tasks. GitHub task JSONs (main branch)
    sum to the same 104: 56 single-server (2 per each of 28 servers), 30
    two-server, 18 three-server. Tooling: 28 MCP servers, 250 tools. Default
    config adds 10 distraction servers and always includes Time MCP.
  url: https://github.com/Accenture/mcp-bench
  license: ''
  languages:
    - en
  modalities:
    - text
  splits: >
    No hidden test split. Official files
    mcpbench_tasks_single_runner_format.json,
    mcpbench_tasks_multi_2server_runner_format.json, and
    mcpbench_tasks_multi_3server_runner_format.json.
  public_test_set: true
publisher:
  org: Accenture Center for Advanced AI, with UC Berkeley
  authors:
    - Zhenting Wang
    - Qi Chang
    - Hemani Patel
    - Shashank Biju
    - Cheng-En Wu
    - Quan Liu
    - Aolin Ding
    - Alireza Rezazadeh
    - Ankit Shah
    - Yujia Bao
    - Eugene Siow
  url: https://github.com/Accenture/mcp-bench
paper:
  title: 'MCP-Bench: Benchmarking Tool-Using LLM Agents with Complex Real-World Tasks via MCP Servers'
  arxiv: '2508.20453'
  url: https://arxiv.org/abs/2508.20453
  year: 2025
leaderboard_url: https://huggingface.co/spaces/mcpbench/mcp-bench
repo_url: https://github.com/Accenture/mcp-bench
released: '2025-08'
last_updated: '2025-10'
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 0.749
  as_of: '2025-09'
  note: >
    gpt-5 0.749 overall on the GitHub README table and Hugging Face space
    data.json dated 2025-09-05. Schema compliance for strong models is near
    ceiling (paper: several above 98%); planning and multi-server dependency
    still separate models.
contamination:
  risk: medium
  note: >
    Task JSONs are public. Servers are live APIs, so outputs move with the
    world and are not a frozen answer key. Fuzzy wording reduces exact-tool
    memorization, but the concrete descriptions exist in the repo for the
    judge.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: 'Official runner python run_benchmark.py in github.com/Accenture/mcp-bench; judge model o4-mini is required to match the published table.'
tags:
  - MCP
  - tool-use
  - agents
  - live-tools
  - LLM-judge
sources:
  - url: https://arxiv.org/abs/2508.20453
    title: 'MCP-Bench (arXiv abs v1)'
    accessed: '2026-09-08'
  - url: https://arxiv.org/html/2508.20453v1
    title: 'MCP-Bench (arXiv HTML v1)'
    accessed: '2026-09-08'
  - url: https://github.com/Accenture/mcp-bench
    title: 'Accenture/mcp-bench repository'
    accessed: '2026-09-08'
  - url: https://raw.githubusercontent.com/Accenture/mcp-bench/main/README.md
    title: 'mcp-bench README'
    accessed: '2026-09-08'
  - url: https://raw.githubusercontent.com/Accenture/mcp-bench/main/config/benchmark_config.yaml
    title: 'mcp-bench benchmark_config.yaml'
    accessed: '2026-09-08'
  - url: https://huggingface.co/spaces/mcpbench/mcp-bench
    title: 'MCP-Bench Hugging Face leaderboard space'
    accessed: '2026-09-08'
  - url: https://huggingface.co/spaces/mcpbench/mcp-bench/raw/main/data.json
    title: 'MCP-Bench leaderboard data.json'
    accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: 'Grok Build, batch-078 (Codex coordinated)'
  reviewed: ''
  reviewed_by: ''
---

## What it measures

MCP-Bench puts an LLM on the Model Context Protocol and asks it to finish messy, multi-step jobs. The prompt is fuzzy English. It does not name the tool. The agent must pick servers, call tools, and chain outputs. Twenty-eight live servers expose 250 tools across finance, travel, science, academic search, maps, weather, and similar domains.

Tasks come in three files: one server, two servers, or three. Extra unused servers sit in the pool as distractors. Time MCP is always present. The skill under test is planning and schema-faithful tool use against a real MCP ecosystem, not a toy API list.

## How it is scored

Two layers. Rule-based metrics on the trace: valid tool names, input schema, runtime success, and dependency order. An o4-mini judge then scores completion, tool use, and planning on 1-10 rubrics, averaged and scaled to [0, 1]. Five shuffled rubric orders are averaged to cut prompt-order bias. The judge sees the fuzzy prompt, the hidden concrete spec, a dependency note, the trace summary, and the final answer. The agent does not see the concrete spec.

The published overall score averages those pieces across single-server and multi-server settings and lies in [0, 1]. The GitHub README and the Hugging Face space `data.json` (lastUpdated 2025-09-05) both put gpt-5 at 0.749, o3 at 0.715, and gpt-oss-120b at 0.692. Schema checks for the strongest models exceed 98% in the paper; planning is what still moves.

## Dataset and licence

The paper and the three official JSON files agree on 104 tasks: 56 single-server (two per server), 30 two-server, 18 three-server. Tasks were synthesized, then inspected. Config defaults include a 5,000-second task timeout, three retries, and 20 execution rounds. Several tools are filtered as broken or rate-limited (listed in `benchmark_config.yaml`).

Licence is unsettled. The README badge says Apache 2.0. The GitHub API `license` field is null, and there is no LICENSE file on `main`. This page leaves `dataset.license` empty for that reason. The Hugging Face space README claims MIT for the leaderboard UI, which is not the benchmark code.

## Who publishes it

Accenture Center for Advanced AI, with Hemani Patel and Shashank Biju also at UC Berkeley. Corresponding author Zhenting Wang. arXiv v1 is 28 August 2025. The GitHub README says the work was accepted to the NeurIPS 2025 Workshop on Scaling Environments for Agents. The live table is the Hugging Face space, not a third-party harness.

## Lineage

The paper contrasts MCP-Bench with earlier API-tool suites that name the tool and stay inside one domain. In this repository, nearby tool-use pages are [BFCL](bfcl.md), [AgentDojo](agentdojo.md), and [tau_bench](tau_bench.md). Those are not MCP-Bench aliases. No sibling page already covers this Accenture suite.

## Saturation and contamination

0.749 is not a ceiling. Weak models drop when more servers are added; gpt-5 stays near 0.75 in both settings. Task files are public, so the wording can leak into training. Live servers still change, so a memorized final answer from 2025 may fail on a later API payload.

## How to run it

Clone [Accenture/mcp-bench](https://github.com/Accenture/mcp-bench), install the 28 servers, and set OpenRouter or Azure keys plus the per-server API keys in `mcp_servers/api_key`. `python ./utils/collect_mcp_info.py` should report 28/28 connected. `python run_benchmark.py --models <name>` runs all three task files. The README says the judge must be o4-mini to match the table. No lm-eval or inspect task name was found.

## Reading the numbers

A high overall score with weak planning still means the model mostly called valid tools, not that it solved the job. Always split schema columns from judge columns. Changing the judge, turning off fuzzy text, or dropping distraction servers makes the number incomparable. Compare against [BFCL](bfcl.md) only as a different tool-use skill (schema AST vs live MCP). The 0.749 gpt-5 figure is the 2025-09-05 space dump, not a later private rerun.
