# Capability model validation

Date: 2026-09-25; snapshot: `snap_113410f682a6fd7d`.

The fit used 462 admitted observations over 32 lineup models, 35 learned items and 12 registry domains.

## Backtests

Errors are RMSE after scaling each held-out value by its benchmark's spread.

- Benchmark-cell holdout (345 predictions): model 0.7060; benchmark-mean baseline 1.1049.
- Each model's newest eligible score (20 predictions): model 0.8326; benchmark-mean baseline 1.2245.

## Request latency

`explain: summary` over all 12 domain objectives: median 25.8 ms; maximum 37.4 ms. Measured on the local Worker-equivalent Python decision path; this is not a deployed-Worker network timing.

## Estimate/single-benchmark disagreements

Each row compares the estimate leader with the best admitted raw score on one tagged benchmark. A disagreement is expected when the other evidence, learned item discrimination, source offset, directness or recency changes the combined ordering.

| Domain | Benchmark | Tag | Estimate leader | Single-benchmark leader | Reading |
|---|---|---|---|---|---|
| `agentic_tool_use` | `metr_time_horizon_50` | direct | `openai/gpt-6-astra` | `anthropic/claude-opus-4-6` | 2026-02-20; [1](https://metr.org/assets/benchmark_results_1_1.yaml) |
| `agentic_tool_use` | `metr_time_horizon_80` | direct | `openai/gpt-6-astra` | `google/gemini-3-1-pro-preview` | 2026-04-15; [1](https://metr.org/assets/benchmark_results_1_1.yaml) |
| `agentic_tool_use` | `osworld_2` | direct | `openai/gpt-6-astra` | `anthropic/claude-opus-5` | 2026-09-25; [1](https://osworld-v2.xlang.ai/) |
| `agentic_tool_use` | `tau3_banking` | direct | `openai/gpt-6-astra` | `anthropic/claude-opus-5` | 2026-08-03; [1](https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/claude-opus-5_sierra_2026-08-04/submission.json) |
| `chat_preference` | `arena_elo_overall` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5-1` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_elo_style_control` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_business` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-opus-4-7` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_coding` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_creative_writing` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_expert` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_legal` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_math` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_multi_turn` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_non_english` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_science` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_vision` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/vision_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_sc_writing` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `chat_preference` | `arena_webdev` | direct | `anthropic/claude-opus-4-6` | `anthropic/claude-opus-5-5` | 2026-09-23; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset) |
| `engineering_stem` | `arena_sc_science` | proxy | `google/gemini-3-1-pro-preview` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `engineering_stem` | `gpqa_diamond` | direct | `google/gemini-3-1-pro-preview` | `openai/gpt-6-astra` | 2026-08-30; [1](https://epoch.ai/benchmarks/gpqa-diamond) |
| `engineering_stem` | `hle` | direct | `google/gemini-3-1-pro-preview` | `openai/gpt-6-astra` | 2026-09-24; [1](https://labs.scale.com/leaderboard/humanitys_last_exam) |
| `legal` | `arena_sc_legal` | proxy | `openai/gpt-6-astra` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `maths` | `aime_2026` | direct | `openai/gpt-6-astra` | `openai/gpt-5-4` | 2026-09-25; [1](https://matharena.ai/competition_tables/aime--aime_2026) |
| `maths` | `arena_sc_math` | proxy | `openai/gpt-6-astra` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `medical` | `arena_sc_medicine` | proxy | `meta/muse-spark` | `anthropic/claude-opus-4-6` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `multilingual` | `arena_sc_non_english` | proxy | `anthropic/claude-fable-5-1` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `multilingual` | `mteb_multilingual_v2` | proxy | `anthropic/claude-fable-5-1` | `microsoft/harrier-oss-v1-27b` | 2026-09-24; [1](https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(Multilingual,%20v2)/scores) |
| `reasoning` | `gpqa_diamond` | proxy | `openai/gpt-5-6-sol` | `openai/gpt-6-astra` | 2026-08-30; [1](https://epoch.ai/benchmarks/gpqa-diamond) |
| `reasoning` | `hle` | proxy | `openai/gpt-5-6-sol` | `openai/gpt-6-astra` | 2026-09-24; [1](https://labs.scale.com/leaderboard/humanitys_last_exam) |
| `software_engineering` | `arena_elo_coding` | proxy | `anthropic/claude-opus-5-5` | `anthropic/claude-opus-4-6` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text/latest-00000-of-00001.parquet) |
| `software_engineering` | `arena_sc_coding` | proxy | `anthropic/claude-opus-5-5` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `software_engineering` | `deepswe_v1_1` | direct | `anthropic/claude-opus-5-5` | `google/gemini-3-8-flash` | 2026-09-25; [1](https://deepswe.datacurve.ai/artifacts/v1.1/leaderboard-live.json) |
| `software_engineering` | `frontiercode_v1_1` | direct | `anthropic/claude-opus-5-5` | `anthropic/claude-fable-5` | 2026-09-25; [1](https://cognition.com/frontiercode) |
| `software_engineering` | `metr_time_horizon_50` | proxy | `anthropic/claude-opus-5-5` | `anthropic/claude-opus-4-6` | 2026-02-20; [1](https://metr.org/assets/benchmark_results_1_1.yaml) |
| `software_engineering` | `metr_time_horizon_80` | proxy | `anthropic/claude-opus-5-5` | `google/gemini-3-1-pro-preview` | 2026-04-15; [1](https://metr.org/assets/benchmark_results_1_1.yaml) |
| `software_engineering` | `swe_bench_multilingual` | direct | `anthropic/claude-opus-5-5` | `anthropic/claude-opus-4-6` | 2026-02-13; [1](https://www.swebench.com/) |
| `software_engineering` | `swe_bench_pro` | direct | `anthropic/claude-opus-5-5` | `meta/muse-spark-1-1` | 2026-07-09; [1](https://labs.scale.com/leaderboard/swe_bench_pro_public) |
| `software_engineering` | `swe_bench_verified` | direct | `anthropic/claude-opus-5-5` | `anthropic/claude-opus-4-7` | 2026-04-20; [1](https://epoch.ai/benchmarks/swe-bench-verified) |
| `software_engineering` | `terminal_bench_v4_0` | proxy | `anthropic/claude-opus-5-5` | `openai/gpt-6-astra` | 2026-09-03; [1](https://www.tbench.ai/) |
| `vision_documents` | `arena_sc_vision` | proxy | `meta/muse-spark` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/vision_style_control/latest-00000-of-00001.parquet) |
| `vision_documents` | `osworld_2` | proxy | `meta/muse-spark` | `anthropic/claude-opus-5` | 2026-09-25; [1](https://osworld-v2.xlang.ai/) |
| `writing` | `arena_sc_creative_writing` | proxy | `google/gemini-3-8-flash` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
| `writing` | `arena_sc_writing` | proxy | `google/gemini-3-8-flash` | `anthropic/claude-fable-5` | 2026-09-13; [1](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet) |
