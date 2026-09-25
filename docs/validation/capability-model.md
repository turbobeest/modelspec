# Capability model validation

Date: 2026-09-25; snapshot: `snap_be03a066f9c574aa`.

The fit used 462 admitted observations over 32 lineup models, 35 learned items and 12 registry domains.

## Backtests

Errors are RMSE after scaling each held-out value by its benchmark's spread.

- Benchmark-cell holdout (345 predictions): model 0.7060; benchmark-mean baseline 1.1049.
- Each model's newest eligible score (20 predictions): model 0.8326; benchmark-mean baseline 1.2245.

## Request latency

`explain: summary` over all 12 domain objectives: median 13.9 ms; maximum 19.4 ms. Measured on the local Worker-equivalent Python decision path; this is not a deployed-Worker network timing.

## Separable estimate/single-benchmark disagreements

Each row compares the estimate leader with the best admitted raw score on one tagged benchmark. Point-order differences whose estimate intervals overlap are not listed as disagreements. The report found 34 such not-separable point orders. Every listed disagreement names the other direct evidence that can explain it.

| Domain | Benchmark | Tag | Estimate leader | Single-benchmark leader | Other direct evidence | Reading |
|---|---|---|---|---|---|---|
| `agentic_tool_use` | `metr_time_horizon_80` | direct | `openai/gpt-6-astra` | `google/gemini-3-1-pro-preview` | `terminal_bench_v4_0`, `vending_bench_2` | 2026-04-15; [1](https://metr.org/assets/benchmark_results_1_1.yaml) |
| `engineering_stem` | `arena_sc_science` | proxy | `openai/gpt-6-astra` | `anthropic/claude-fable-5` | `gpqa_diamond`, `hle` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `software_engineering` | `metr_time_horizon_80` | proxy | `anthropic/claude-opus-5-5` | `google/gemini-3-1-pro-preview` | `cursorbench_4` | 2026-04-15; [1](https://metr.org/assets/benchmark_results_1_1.yaml) |
