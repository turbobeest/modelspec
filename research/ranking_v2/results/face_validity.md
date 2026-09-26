# Face validity: top 10 as of 2026-09-24

## View: sourced

{'observations': 2324, 'models': 240, 'items': 120, 'by_source_kind': {'independent_evaluator': 2187, 'provider_self_report': 107, 'benchmark_author': 30}, 'by_link': {'lin': 2023, 'pct': 279, 'log': 22}}

Scale: sd of g over the 211 models with 3+ observations is 1.00 latent units (the unit every threshold and U below is in).

Fit: 3.0 s, 86 sweeps. Source-kind offsets (latent units, ± se): provider_self_report +0.35 ± 0.04, flat_unsourced +0.00 ± 0.50

Domain sd (learned): coding 0.34, agentic 0.42, reasoning 0.33, math 0.37, knowledge 0.35, chat 0.27, vision 0.28, long_context 0.37, retrieval 0.85, speech 0.80, safety 0.80, multilingual 0.79, fam:mmlu 0.82, fam:flores 0.80, fam:multipl_e 0.80, fam:mteb 0.80

Items: {"free": 20, "borrowed": 19, "awaiting_overlap": 65, "single_model": 16}

### coding (sourced)

Mix {'coding': 0.6, 'agentic': 0.3, 'reasoning': 0.1}. Placed 218 (90 ranked, 128 provisional); scoring every candidate took 2 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) |
|---:|---|---|---|---|---|
| 1 | anthropic/claude-opus-5-5 (2026-09) | 2.13 (1.99, 2.27) | ranked | yes |  |
| 2 | anthropic/claude-mythos-5-1 (2026-09) | 2.12 (1.58, 2.67) | provisional | yes |  |
| 3 | openai/gpt-6-astra (2026-09) | 1.86 (1.79, 1.92) | ranked |  |  |
| 4 | anthropic/claude-fable-5-1 (2026-09) | 1.84 (1.77, 1.91) | ranked |  |  |
| 5 | anthropic/claude-opus-5 (2026-07) | 1.65 (1.58, 1.72) | ranked |  |  |
| 6 | anthropic/claude-mythos-preview (2026-04) | 1.61 (1.40, 1.81) | provisional |  |  |
| 7 | openai/gpt-6-sol (2026-09) | 1.58 (1.33, 1.83) | ranked |  |  |
| 8 | anthropic/claude-fable-5 (2026-06) | 1.51 (1.44, 1.57) | ranked |  |  |
| 9 | moonshot/kimi-k3 (2026-07) | 1.50 (1.44, 1.57) | ranked |  |  |
| 10 | qwen/qwen3-8-max (2026-08) | 1.46 (1.40, 1.53) | ranked |  |  |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-opus-5-5** — U 2.13 ± 0.11, ranked (independent evidence in the primary domain):
  - webdev/overall = 1818 (independent_evaluator, 2026-09-23, claude-opus-5.5-max, webdev/overall) → implies +2.05 ± 0.06, weight 56%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - hle_tools = 67.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (with tools)) → implies +2.00 ± 0.41, weight 11%; https://www.anthropic.com/claude-opus-5-5-system-card
  - terminal_bench_v4_0 = 66.4% (provider_self_report, 2026-09-22, Claude Opus 5.5 (xhigh), Terminal-Bench 4.0) → implies +2.59 ± 0.42, weight 9%; https://www.anthropic.com/claude-opus-5-5-system-card
  - terminal_bench_science = 58.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Terminal-Bench-Science 0.1) → implies +1.82 ± 0.55, weight 6%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle = 64.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (no tools)) → implies +2.29 ± 0.30, weight 6%; https://www.anthropic.com/claude-opus-5-5-system-card
- **anthropic/claude-mythos-5-1** — U 2.12 ± 0.42, provisional (no independent measurement in coding):
  - terminal_bench_v4_0 = 60.9% (provider_self_report, 2026-09-01, Claude Mythos 5.1, Terminal-Bench 4.0) → implies +2.28 ± 0.43, weight 100%; https://www.anthropic.com/claude-fable-5-1-system-card
- **openai/gpt-6-astra** — U 1.86 ± 0.05, ranked (independent evidence in the primary domain):
  - webdev/overall = 1792 (independent_evaluator, 2026-09-23, gpt-6-astra-max, webdev/overall) → implies +1.96 ± 0.06, weight 59%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - agent/overall = 0.1154 (independent_evaluator, 2026-09-15, GPT 6 Astra (Max), agent/overall) → implies +1.86 ± 0.10, weight 26%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - hle_tools = 57.2% (provider_self_report, 2026-09-03, GPT-6 Astra, Humanity's Last Exam (w/ tools)) → implies +1.22 ± 0.37, weight 4%; https://openai.com/index/gpt-6-astra/
  - text_style_control/hard_prompts = 1497 (independent_evaluator, 2026-09-13, gpt-6-astra-max, text_style_control/hard_prompts) → implies +1.09 ± 0.41, weight 2%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - terminal_bench_science = 64.6% (provider_self_report, 2026-09-03, GPT-6 Astra, Terminal-Bench Science 0.1) → implies +2.23 ± 0.53, weight 2%; https://openai.com/index/gpt-6-astra/

Newest candidates with an evidence gap (not ranked low, not ranked): openai/gpt-6-luna (2026-09-22): no usable measurement; stepfun/step-5-preview (2026-09-16): no usable measurement; inception/mercury-2-5 (2026-09-08): no usable measurement; openbmb/minicpm5-2b (2026-09-06): no usable measurement; inclusionai/ling-3-0-flash-vl (2026-09-04): no usable measurement


### reasoning (sourced)

Mix {'reasoning': 0.6, 'math': 0.25, 'knowledge': 0.15}. Placed 210 (7 ranked, 203 provisional); scoring every candidate took 2 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) |
|---:|---|---|---|---|---|
| 1 | anthropic/claude-opus-5-5 (2026-09) | 2.10 (1.81, 2.39) | provisional | yes |  |
| 2 | anthropic/claude-mythos-preview (2026-04) | 1.71 (1.40, 2.02) | provisional |  |  |
| 3 | anthropic/claude-fable-5 (2026-06) | 1.51 (1.20, 1.82) | provisional |  |  |
| 4 | google/gemini-3-8-flash (2026-09) | 1.48 (1.22, 1.74) | ranked |  |  |
| 5 | anthropic/claude-fable-5-1 (2026-09) | 1.46 (1.16, 1.76) | provisional |  |  |
| 6 | anthropic/claude-opus-5 (2026-07) | 1.42 (1.11, 1.73) | provisional |  |  |
| 7 | anthropic/claude-opus-4-6 (2026-02) | 1.39 (1.08, 1.70) | provisional |  |  |
| 8 | openai/gpt-5-6-sol (2026-07) | 1.39 (1.09, 1.69) | provisional |  |  |
| 9 | openai/gpt-6-astra (2026-09) | 1.38 (1.11, 1.66) | provisional |  |  |
| 10 | anthropic/claude-opus-4-7 (2026-04) | 1.36 (1.05, 1.67) | provisional |  |  |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-opus-5-5** — U 2.10 ± 0.23, provisional (no independent measurement in reasoning):
  - hle = 64.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (no tools)) → implies +2.29 ± 0.30, weight 43%; https://www.anthropic.com/claude-opus-5-5-system-card
  - webdev/overall = 1818 (independent_evaluator, 2026-09-23, claude-opus-5.5-max, webdev/overall) → implies +2.05 ± 0.06, weight 19%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - hle_tools = 67.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (with tools)) → implies +2.00 ± 0.41, weight 17%; https://www.anthropic.com/claude-opus-5-5-system-card
  - terminal_bench_science = 58.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Terminal-Bench-Science 0.1) → implies +1.82 ± 0.55, weight 10%; https://www.anthropic.com/claude-opus-5-5-system-card
  - swe_bench_multimodal = 61.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, SWE-bench Multimodal) → implies +1.97 ± 0.37, weight 9%; https://www.anthropic.com/claude-opus-5-5-system-card
- **anthropic/claude-mythos-preview** — U 1.71 ± 0.24, provisional (no independent measurement in reasoning):
  - hle = 56.8% (provider_self_report, 2026-04-07, Claude Mythos Preview, Humanity's Last Exam, no tools) → implies +1.83 ± 0.33, weight 42%; https://www.anthropic.com/glasswing
  - hle_tools = 64.7% (provider_self_report, 2026-04-07, Claude Mythos Preview, Humanity's Last Exam, with tools) → implies +1.77 ± 0.43, weight 17%; https://www.anthropic.com/glasswing
  - metr_time_horizon_50 = 1045 min (benchmark_author, 2026-05-08, claude_mythos_preview_early_inspect, METR-Horizon-v1.1) → implies +1.47 ± 0.21, weight 16%; https://metr.org/assets/benchmark_results_1_1.yaml
  - swe_bench_multimodal = 59% (provider_self_report, 2026-04-07, Claude Mythos Preview, SWE-bench Multimodal (internal implementation)) → implies +1.80 ± 0.42, weight 13%; https://www.anthropic.com/glasswing
  - gpqa_diamond = 94.55% (provider_self_report, 2026-04-07, Claude Mythos Preview, GPQA Diamond (198 questions)) → implies +1.55 ± 0.89, weight 6%; https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
- **anthropic/claude-fable-5** — U 1.51 ± 0.24, provisional (no independent measurement in reasoning):
  - text_style_control/hard_prompts = 1532 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/hard_prompts) → implies +1.41 ± 0.41, weight 21%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - document_style_control/overall = 1499 (independent_evaluator, 2026-09-13, claude-fable-5, document_style_control/overall) → implies +1.69 ± 0.10, weight 20%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - webdev/overall = 1627 (independent_evaluator, 2026-09-23, claude-fable-5-high, webdev/overall) → implies +1.42 ± 0.05, weight 15%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - vision_style_control/overall = 1310 (independent_evaluator, 2026-09-13, claude-fable-5, vision_style_control/overall) → implies +1.41 ± 0.09, weight 11%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - agent/overall = 0.08814 (independent_evaluator, 2026-09-15, Claude Fable 5 (High), agent/overall) → implies +1.69 ± 0.08, weight 10%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Newest candidates with an evidence gap (not ranked low, not ranked): openai/gpt-6-luna (2026-09-22): no usable measurement; openai/gpt-6-sol (2026-09-22): no measurement in reasoning; measured only in coding; xai/grok-4-7 (2026-09-21): no measurement in reasoning; measured only in agentic, coding; stepfun/step-5-preview (2026-09-16): no usable measurement; inception/mercury-2-5 (2026-09-08): no usable measurement


### chat (sourced)

Mix {'chat': 0.8, 'knowledge': 0.1, 'reasoning': 0.1}. Placed 206 (199 ranked, 7 provisional); scoring every candidate took 2 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) |
|---:|---|---|---|---|---|
| 1 | anthropic/claude-fable-5 (2026-06) | 1.47 (1.28, 1.65) | ranked | yes |  |
| 2 | anthropic/claude-opus-4-6 (2026-02) | 1.42 (1.23, 1.60) | ranked | yes |  |
| 3 | anthropic/claude-fable-5-1 (2026-09) | 1.37 (1.18, 1.56) | ranked | yes |  |
| 4 | anthropic/claude-opus-4-7 (2026-04) | 1.37 (1.18, 1.55) | ranked | yes |  |
| 5 | google/gemini-3-8-flash (2026-09) | 1.36 (1.17, 1.54) | ranked | yes |  |
| 6 | anthropic/claude-opus-5 (2026-07) | 1.30 (1.12, 1.49) | ranked | yes |  |
| 7 | openai/gpt-5-6-sol (2026-07) | 1.28 (1.10, 1.46) | ranked |  |  |
| 8 | moonshot/kimi-k3 (2026-07) | 1.27 (1.08, 1.46) | ranked |  |  |
| 9 | anthropic/claude-opus-4-8 (2026-05) | 1.25 (1.07, 1.43) | ranked |  |  |
| 10 | google/gemini-3-7-flash (2026-08) | 1.24 (1.04, 1.43) | ranked |  |  |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-fable-5** — U 1.47 ± 0.14, ranked (independent evidence in the primary domain):
  - text_style_control/instruction_following = 1511 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/instruction_following) → implies +1.48 ± 0.41, weight 13%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/overall = 1506 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/overall) → implies +1.39 ± 0.41, weight 13%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/multi_turn = 1518 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/multi_turn) → implies +1.36 ± 0.45, weight 11%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1532 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/hard_prompts) → implies +1.41 ± 0.41, weight 10%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/expert = 1548 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/expert) → implies +1.48 ± 0.45, weight 9%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
- **anthropic/claude-opus-4-6** — U 1.42 ± 0.14, ranked (independent evidence in the primary domain):
  - text_style_control/instruction_following = 1513 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/instruction_following) → implies +1.50 ± 0.40, weight 13%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/overall = 1505 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/overall) → implies +1.38 ± 0.41, weight 13%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/multi_turn = 1517 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/multi_turn) → implies +1.36 ± 0.44, weight 11%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1533 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/hard_prompts) → implies +1.42 ± 0.41, weight 11%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/expert = 1546 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/expert) → implies +1.45 ± 0.44, weight 9%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
- **anthropic/claude-fable-5-1** — U 1.37 ± 0.15, ranked (independent evidence in the primary domain):
  - text_style_control/overall = 1498 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, text_style_control/overall) → implies +1.33 ± 0.41, weight 14%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/instruction_following = 1496 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, text_style_control/instruction_following) → implies +1.34 ± 0.43, weight 13%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1517 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, text_style_control/hard_prompts) → implies +1.27 ± 0.42, weight 10%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/multi_turn = 1488 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, text_style_control/multi_turn) → implies +1.11 ± 0.49, weight 10%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - vision_style_control/overall = 1289 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, vision_style_control/overall) → implies +1.22 ± 0.10, weight 8%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Newest candidates with an evidence gap (not ranked low, not ranked): anthropic/claude-opus-5-5 (2026-09-22): no measurement in chat; measured only in agentic, coding, knowledge, reasoning, vision; openai/gpt-6-luna (2026-09-22): no usable measurement; openai/gpt-6-sol (2026-09-22): no measurement in chat; measured only in coding; xai/grok-4-7 (2026-09-21): no measurement in chat; measured only in agentic, coding; stepfun/step-5-preview (2026-09-16): no usable measurement


### agentic (sourced)

Mix {'agentic': 0.6, 'coding': 0.25, 'reasoning': 0.15}. Placed 72 (68 ranked, 4 provisional); scoring every candidate took 2 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) |
|---:|---|---|---|---|---|
| 1 | anthropic/claude-opus-5-5 (2026-09) | 2.20 (1.94, 2.45) | provisional | yes |  |
| 2 | anthropic/claude-mythos-5-1 (2026-09) | 2.13 (1.58, 2.68) | provisional | yes |  |
| 3 | anthropic/claude-fable-5-1 (2026-09) | 1.86 (1.77, 1.96) | ranked |  |  |
| 4 | openai/gpt-6-astra (2026-09) | 1.80 (1.71, 1.89) | ranked |  |  |
| 5 | anthropic/claude-opus-5 (2026-07) | 1.68 (1.59, 1.77) | ranked |  |  |
| 6 | anthropic/claude-mythos-preview (2026-04) | 1.60 (1.38, 1.82) | ranked |  |  |
| 7 | anthropic/claude-fable-5 (2026-06) | 1.59 (1.50, 1.68) | ranked |  |  |
| 8 | openai/gpt-5-6-sol (2026-07) | 1.50 (1.35, 1.65) | ranked |  |  |
| 9 | moonshot/kimi-k3 (2026-07) | 1.49 (1.41, 1.58) | ranked |  |  |
| 10 | anthropic/claude-opus-4-8 (2026-05) | 1.47 (1.39, 1.56) | ranked |  |  |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-opus-5-5** — U 2.20 ± 0.20, provisional (no independent measurement in agentic):
  - hle_tools = 67.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (with tools)) → implies +2.00 ± 0.41, weight 21%; https://www.anthropic.com/claude-opus-5-5-system-card
  - webdev/overall = 1818 (independent_evaluator, 2026-09-23, claude-opus-5.5-max, webdev/overall) → implies +2.05 ± 0.06, weight 20%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - terminal_bench_v4_0 = 66.4% (provider_self_report, 2026-09-22, Claude Opus 5.5 (xhigh), Terminal-Bench 4.0) → implies +2.59 ± 0.42, weight 18%; https://www.anthropic.com/claude-opus-5-5-system-card
  - terminal_bench_science = 58.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Terminal-Bench-Science 0.1) → implies +1.82 ± 0.55, weight 12%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle = 64.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (no tools)) → implies +2.29 ± 0.30, weight 10%; https://www.anthropic.com/claude-opus-5-5-system-card
- **anthropic/claude-mythos-5-1** — U 2.13 ± 0.43, provisional (no independent measurement in agentic):
  - terminal_bench_v4_0 = 60.9% (provider_self_report, 2026-09-01, Claude Mythos 5.1, Terminal-Bench 4.0) → implies +2.28 ± 0.43, weight 100%; https://www.anthropic.com/claude-fable-5-1-system-card
- **anthropic/claude-fable-5-1** — U 1.86 ± 0.07, ranked (independent evidence in the primary domain):
  - agent/overall = 0.1371 (independent_evaluator, 2026-09-15, Claude Fable 5.1 (Max), agent/overall) → implies +2.00 ± 0.09, weight 56%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - webdev/overall = 1755 (independent_evaluator, 2026-09-23, claude-fable-5.1-max, webdev/overall) → implies +1.84 ± 0.05, weight 25%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1517 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, text_style_control/hard_prompts) → implies +1.27 ± 0.42, weight 4%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - terminal_bench_science = 52.6% (provider_self_report, 2026-09-01, Claude Fable 5.1, Terminal-Bench-Science 0.1) → implies +1.41 ± 0.54, weight 3%; https://www.anthropic.com/claude-fable-5-1-system-card
  - document_style_control/overall = 1493 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, document_style_control/overall) → implies +1.58 ± 0.15, weight 3%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Newest candidates with an evidence gap (not ranked low, not ranked): openai/gpt-6-luna (2026-09-22): no usable measurement; openai/gpt-6-sol (2026-09-22): no measurement in agentic; measured only in coding; stepfun/step-5-preview (2026-09-16): no usable measurement; inception/mercury-2-5 (2026-09-08): no usable measurement; openbmb/minicpm5-2b (2026-09-06): no usable measurement


### vision (sourced)

Mix {'vision': 0.8, 'reasoning': 0.2}. Placed 89 (86 ranked, 3 provisional); scoring every candidate took 1 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) |
|---:|---|---|---|---|---|
| 1 | anthropic/claude-opus-5-5 (2026-09) | 2.07 (1.72, 2.43) | provisional | yes | meta/llama-4-maverick-17b-128e-instruct |
| 2 | anthropic/claude-mythos-preview (2026-04) | 1.70 (1.33, 2.07) | provisional |  | meta/llama-4-scout-17b-16e-instruct |
| 3 | anthropic/claude-fable-5 (2026-06) | 1.45 (1.33, 1.57) | ranked |  | openbmb/minicpm-v-4 |
| 4 | anthropic/claude-opus-4-7 (2026-04) | 1.36 (1.24, 1.47) | ranked |  | qwen/qwen2-vl-7b-instruct |
| 5 | anthropic/claude-opus-4-6 (2026-02) | 1.35 (1.23, 1.47) | ranked |  |  |
| 6 | qwen/qwen3-8-max (2026-08) | 1.33 (1.20, 1.45) | ranked |  |  |
| 7 | anthropic/claude-fable-5-1 (2026-09) | 1.30 (1.17, 1.42) | ranked |  |  |
| 8 | anthropic/claude-opus-5 (2026-07) | 1.29 (1.17, 1.41) | ranked |  |  |
| 9 | openai/gpt-5-6-sol (2026-07) | 1.26 (1.14, 1.38) | ranked |  |  |
| 10 | openai/gpt-6-astra (2026-09) | 1.24 (1.11, 1.36) | ranked |  |  |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-opus-5-5** — U 2.07 ± 0.28, provisional (no independent measurement in vision):
  - swe_bench_multimodal = 61.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, SWE-bench Multimodal) → implies +1.97 ± 0.37, weight 33%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle = 64.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (no tools)) → implies +2.29 ± 0.30, weight 28%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle_tools = 67.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (with tools)) → implies +2.00 ± 0.41, weight 13%; https://www.anthropic.com/claude-opus-5-5-system-card
  - webdev/overall = 1818 (independent_evaluator, 2026-09-23, claude-opus-5.5-max, webdev/overall) → implies +2.05 ± 0.06, weight 12%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - terminal_bench_science = 58.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Terminal-Bench-Science 0.1) → implies +1.82 ± 0.55, weight 8%; https://www.anthropic.com/claude-opus-5-5-system-card
- **anthropic/claude-mythos-preview** — U 1.70 ± 0.29, provisional (no independent measurement in vision):
  - swe_bench_multimodal = 59% (provider_self_report, 2026-04-07, Claude Mythos Preview, SWE-bench Multimodal (internal implementation)) → implies +1.80 ± 0.42, weight 30%; https://www.anthropic.com/glasswing
  - hle = 56.8% (provider_self_report, 2026-04-07, Claude Mythos Preview, Humanity's Last Exam, no tools) → implies +1.83 ± 0.33, weight 28%; https://www.anthropic.com/glasswing
  - metr_time_horizon_50 = 1045 min (benchmark_author, 2026-05-08, claude_mythos_preview_early_inspect, METR-Horizon-v1.1) → implies +1.47 ± 0.21, weight 19%; https://metr.org/assets/benchmark_results_1_1.yaml
  - hle_tools = 64.7% (provider_self_report, 2026-04-07, Claude Mythos Preview, Humanity's Last Exam, with tools) → implies +1.77 ± 0.43, weight 12%; https://www.anthropic.com/glasswing
  - swe_bench_verified = 93.9% (provider_self_report, 2026-04-07, Claude Mythos Preview, SWE-bench Verified) → implies +1.98 ± 0.46, weight 4%; https://www.anthropic.com/glasswing
- **anthropic/claude-fable-5** — U 1.45 ± 0.09, ranked (independent evidence in the primary domain):
  - vision_style_control/overall = 1310 (independent_evaluator, 2026-09-13, claude-fable-5, vision_style_control/overall) → implies +1.41 ± 0.09, weight 72%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - document_style_control/overall = 1499 (independent_evaluator, 2026-09-13, claude-fable-5, document_style_control/overall) → implies +1.69 ± 0.10, weight 11%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1532 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/hard_prompts) → implies +1.41 ± 0.41, weight 7%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - webdev/overall = 1627 (independent_evaluator, 2026-09-23, claude-fable-5-high, webdev/overall) → implies +1.42 ± 0.05, weight 3%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - agent/overall = 0.08814 (independent_evaluator, 2026-09-15, Claude Fable 5 (High), agent/overall) → implies +1.69 ± 0.08, weight 2%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Newest candidates with an evidence gap (not ranked low, not ranked): openai/gpt-6-luna (2026-09-22): no usable measurement; openai/gpt-6-sol (2026-09-22): no measurement in vision; measured only in coding; xai/grok-4-7 (2026-09-21): no measurement in vision; measured only in agentic, coding; stepfun/step-5-preview (2026-09-16): no usable measurement; deepseek/deepseek-flash (2026-09-10): no measurement in vision; measured only in agentic, coding, knowledge, reasoning


## View: flat

{'observations': 7132, 'models': 492, 'items': 174, 'by_source_kind': {'flat_unsourced': 4808, 'independent_evaluator': 2187, 'provider_self_report': 107, 'benchmark_author': 30}, 'by_link': {'pct': 4795, 'lin': 2315, 'log': 22}}

Scale: sd of g over the 437 models with 3+ observations is 1.00 latent units (the unit every threshold and U below is in).

Fit: 13.5 s, 133 sweeps. Source-kind offsets (latent units, ± se): provider_self_report +0.40 ± 0.04, flat_unsourced -0.00 ± 0.01

Domain sd (learned): coding 0.42, agentic 0.72, reasoning 0.28, math 0.34, knowledge 0.34, chat 0.25, vision 0.39, long_context 0.37, retrieval 0.54, speech 0.76, safety 0.51, multilingual 0.62, fam:mmlu 0.73, fam:flores 0.76, fam:multipl_e 0.43, fam:mteb 0.29

Items: {"free": 132, "borrowed": 23, "single_model": 13, "awaiting_overlap": 6}

### coding (flat)

Mix {'coding': 0.6, 'agentic': 0.3, 'reasoning': 0.1}. Placed 250 (90 ranked, 160 provisional); scoring every candidate took 4 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) | v1 (production data) |
|---:|---|---|---|---|---|---|
| 1 | anthropic/claude-opus-5-5 (2026-09) | 2.50 (2.36, 2.65) | ranked | yes | anthropic/claude-opus-4-6 | google/gemini-2-5-pro |
| 2 | anthropic/claude-mythos-5-1 (2026-09) | 2.45 (1.95, 2.95) | provisional | yes | google/gemini-2-5-pro | anthropic/claude-sonnet-4-5-20250929 |
| 3 | openai/gpt-6-astra (2026-09) | 2.24 (2.18, 2.31) | ranked |  | anthropic/claude-opus-4-20250514 | anthropic/claude-opus-4-6 |
| 4 | anthropic/claude-fable-5-1 (2026-09) | 2.24 (2.18, 2.30) | ranked |  | anthropic/claude-opus-4-1-20250805 | anthropic/claude-opus-4-20250514 |
| 5 | anthropic/claude-opus-5 (2026-07) | 2.04 (1.97, 2.11) | ranked |  | anthropic/claude-opus-4-1 | anthropic/claude-opus-4-1-20250805 |
| 6 | anthropic/claude-mythos-preview (2026-04) | 1.98 (1.75, 2.22) | provisional |  | anthropic/claude-sonnet-4-5-20250929 | anthropic/claude-opus-4-1 |
| 7 | openai/gpt-6-sol (2026-09) | 1.92 (1.56, 2.27) | ranked |  | anthropic/claude-sonnet-4-20250514 | anthropic/claude-sonnet-4-20250514 |
| 8 | anthropic/claude-fable-5 (2026-06) | 1.90 (1.84, 1.97) | ranked |  | anthropic/claude-sonnet-4-5 | anthropic/claude-sonnet-4-5 |
| 9 | moonshot/kimi-k3 (2026-07) | 1.88 (1.82, 1.95) | ranked |  | google/gemini-2-5-pro-preview-06-05 | google/gemini-2-5-pro-preview-06-05 |
| 10 | qwen/qwen3-8-max (2026-08) | 1.84 (1.77, 1.90) | ranked |  | google/gemini-2-5-pro-preview-05-06 | google/gemini-2-5-pro-preview-05-06 |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-opus-5-5** — U 2.50 ± 0.12, ranked (independent evidence in the primary domain):
  - webdev/overall = 1818 (independent_evaluator, 2026-09-23, claude-opus-5.5-max, webdev/overall) → implies +2.38 ± 0.06, weight 47%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - terminal_bench_v4_0 = 66.4% (provider_self_report, 2026-09-22, Claude Opus 5.5 (xhigh), Terminal-Bench 4.0) → implies +2.92 ± 0.38, weight 15%; https://www.anthropic.com/claude-opus-5-5-system-card
  - swe_bench_pro = 89.9% (provider_self_report, 2026-09-22, Claude Opus 5.5, SWE-bench Pro) → implies +3.16 ± 0.46, weight 10%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle_tools = 67.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (with tools)) → implies +2.18 ± 0.47, weight 10%; https://www.anthropic.com/claude-opus-5-5-system-card
  - terminal_bench_science = 58.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Terminal-Bench-Science 0.1) → implies +2.22 ± 0.51, weight 9%; https://www.anthropic.com/claude-opus-5-5-system-card
- **anthropic/claude-mythos-5-1** — U 2.45 ± 0.39, provisional (no independent measurement in coding):
  - terminal_bench_v4_0 = 60.9% (provider_self_report, 2026-09-01, Claude Mythos 5.1, Terminal-Bench 4.0) → implies +2.63 ± 0.38, weight 100%; https://www.anthropic.com/claude-fable-5-1-system-card
- **openai/gpt-6-astra** — U 2.24 ± 0.05, ranked (independent evidence in the primary domain):
  - webdev/overall = 1792 (independent_evaluator, 2026-09-23, gpt-6-astra-max, webdev/overall) → implies +2.30 ± 0.05, weight 59%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - agent/overall = 0.1154 (independent_evaluator, 2026-09-15, GPT 6 Astra (Max), agent/overall) → implies +2.33 ± 0.11, weight 26%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - gpqa_diamond = 96% (provider_self_report, 2026-09-03, GPT-6 Astra (max), GPQA Diamond) → implies +1.77 ± 0.31, weight 3%; https://openai.com/index/gpt-6-astra/
  - hle_tools = 57.2% (provider_self_report, 2026-09-03, GPT-6 Astra, Humanity's Last Exam (w/ tools)) → implies +1.30 ± 0.42, weight 2%; https://openai.com/index/gpt-6-astra/
  - text_style_control/hard_prompts = 1497 (independent_evaluator, 2026-09-13, gpt-6-astra-max, text_style_control/hard_prompts) → implies +1.48 ± 0.39, weight 2%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Newest candidates with an evidence gap (not ranked low, not ranked): openai/gpt-6-luna (2026-09-22): no usable measurement; stepfun/step-5-preview (2026-09-16): no usable measurement; inception/mercury-2-5 (2026-09-08): no usable measurement; openbmb/minicpm5-2b (2026-09-06): no usable measurement; inclusionai/ling-3-0-flash-vl (2026-09-04): no usable measurement


### reasoning (flat)

Mix {'reasoning': 0.6, 'math': 0.25, 'knowledge': 0.15}. Placed 344 (9 ranked, 335 provisional); scoring every candidate took 4 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) | v1 (production data) |
|---:|---|---|---|---|---|---|
| 1 | anthropic/claude-opus-5-5 (2026-09) | 2.16 (1.88, 2.44) | provisional | yes | anthropic/claude-opus-4-6 | anthropic/claude-opus-4-6 |
| 2 | anthropic/claude-fable-5 (2026-06) | 1.87 (1.58, 2.17) | provisional |  | google/gemini-2-5-pro | google/gemini-2-5-pro |
| 3 | anthropic/claude-mythos-preview (2026-04) | 1.84 (1.57, 2.10) | provisional |  | google/gemini-2-5-pro-preview-05-06 | google/gemini-2-5-pro-preview-05-06 |
| 4 | anthropic/claude-fable-5-1 (2026-09) | 1.83 (1.54, 2.11) | provisional |  | google/gemini-2-5-pro-preview-06-05 | google/gemini-2-5-pro-preview-06-05 |
| 5 | anthropic/claude-opus-4-6 (2026-02) | 1.77 (1.48, 2.07) | provisional |  | openai/o3-pro | openai/o3-pro |
| 6 | anthropic/claude-opus-5 (2026-07) | 1.76 (1.46, 2.06) | provisional |  | anthropic/claude-opus-4-20250514 | anthropic/claude-opus-4-20250514 |
| 7 | google/gemini-3-8-flash (2026-09) | 1.74 (1.53, 1.95) | ranked |  | openai/o3-mini | anthropic/claude-opus-4-5-20251101 |
| 8 | openai/gpt-5-6-sol (2026-07) | 1.73 (1.47, 1.99) | provisional |  | anthropic/claude-opus-4-5-20251101 | anthropic/claude-opus-4-5 |
| 9 | openai/gpt-6-astra (2026-09) | 1.73 (1.48, 1.97) | provisional |  | anthropic/claude-opus-4-5 | openai/o3-mini |
| 10 | anthropic/claude-opus-4-7 (2026-04) | 1.72 (1.43, 2.02) | provisional |  | anthropic/claude-sonnet-4-6 | anthropic/claude-sonnet-4-6 |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-opus-5-5** — U 2.16 ± 0.22, provisional (no independent measurement in reasoning):
  - hle = 64.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (no tools)) → implies +2.19 ± 0.24, weight 55%; https://www.anthropic.com/claude-opus-5-5-system-card
  - webdev/overall = 1818 (independent_evaluator, 2026-09-23, claude-opus-5.5-max, webdev/overall) → implies +2.38 ± 0.06, weight 14%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - swe_bench_multimodal = 61.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, SWE-bench Multimodal) → implies +2.25 ± 0.34, weight 10%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle_tools = 67.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (with tools)) → implies +2.18 ± 0.47, weight 9%; https://www.anthropic.com/claude-opus-5-5-system-card
  - terminal_bench_science = 58.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Terminal-Bench-Science 0.1) → implies +2.22 ± 0.51, weight 8%; https://www.anthropic.com/claude-opus-5-5-system-card
- **anthropic/claude-fable-5** — U 1.87 ± 0.23, provisional (no independent measurement in reasoning):
  - document_style_control/overall = 1499 (independent_evaluator, 2026-09-13, claude-fable-5, document_style_control/overall) → implies +2.05 ± 0.09, weight 25%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1532 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/hard_prompts) → implies +1.75 ± 0.39, weight 22%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - webdev/overall = 1627 (independent_evaluator, 2026-09-23, claude-fable-5-high, webdev/overall) → implies +1.80 ± 0.05, weight 12%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/expert = 1548 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/expert) → implies +1.80 ± 0.43, weight 10%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/math = 1526 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/math) → implies +1.81 ± 0.50, weight 10%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
- **anthropic/claude-mythos-preview** — U 1.84 ± 0.21, provisional (no independent measurement in reasoning):
  - hle = 56.8% (provider_self_report, 2026-04-07, Claude Mythos Preview, Humanity's Last Exam, no tools) → implies +1.85 ± 0.24, weight 49%; https://www.anthropic.com/glasswing
  - gpqa_diamond = 94.55% (provider_self_report, 2026-04-07, Claude Mythos Preview, GPQA Diamond (198 questions)) → implies +1.58 ± 0.41, weight 17%; https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
  - swe_bench_multimodal = 59% (provider_self_report, 2026-04-07, Claude Mythos Preview, SWE-bench Multimodal (internal implementation)) → implies +2.09 ± 0.38, weight 11%; https://www.anthropic.com/glasswing
  - hle_tools = 64.7% (provider_self_report, 2026-04-07, Claude Mythos Preview, Humanity's Last Exam, with tools) → implies +1.94 ± 0.47, weight 8%; https://www.anthropic.com/glasswing
  - charxiv_reasoning = 86.1% (provider_self_report, 2026-04-07, Claude Mythos Preview, CharXiv Reasoning, no tools) → implies +1.49 ± 0.84, weight 5%; https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf

Newest candidates with an evidence gap (not ranked low, not ranked): openai/gpt-6-luna (2026-09-22): no usable measurement; openai/gpt-6-sol (2026-09-22): no measurement in reasoning; measured only in coding; xai/grok-4-7 (2026-09-21): no measurement in reasoning; measured only in agentic, coding; stepfun/step-5-preview (2026-09-16): no usable measurement; inception/mercury-2-5 (2026-09-08): no usable measurement


### chat (flat)

Mix {'chat': 0.8, 'knowledge': 0.1, 'reasoning': 0.1}. Placed 331 (206 ranked, 125 provisional); scoring every candidate took 4 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) | v1 (production data) |
|---:|---|---|---|---|---|---|
| 1 | anthropic/claude-fable-5 (2026-06) | 1.81 (1.64, 1.98) | ranked | yes | openai/gpt-4-1 | openai/gpt-4-1 |
| 2 | anthropic/claude-opus-4-6 (2026-02) | 1.77 (1.60, 1.94) | ranked | yes | anthropic/claude-opus-4-6 | anthropic/claude-opus-4-6 |
| 3 | anthropic/claude-opus-4-7 (2026-04) | 1.72 (1.55, 1.89) | ranked | yes | google/gemini-2-5-pro | google/gemini-2-5-pro |
| 4 | anthropic/claude-fable-5-1 (2026-09) | 1.72 (1.54, 1.90) | ranked | yes | anthropic/claude-opus-4-20250514 | anthropic/claude-opus-4-20250514 |
| 5 | google/gemini-3-8-flash (2026-09) | 1.69 (1.52, 1.85) | ranked | yes | anthropic/claude-sonnet-4-5-20250929 | anthropic/claude-sonnet-4-5-20250929 |
| 6 | anthropic/claude-opus-5 (2026-07) | 1.66 (1.49, 1.83) | ranked | yes | openai/gpt-4-1-mini | openai/gpt-4-1-mini |
| 7 | openai/gpt-5-6-sol (2026-07) | 1.65 (1.48, 1.81) | ranked |  | anthropic/claude-sonnet-4-20250514 | anthropic/claude-sonnet-4-20250514 |
| 8 | moonshot/kimi-k3 (2026-07) | 1.62 (1.44, 1.79) | ranked |  | google/gemini-2-5-pro-preview-05-06 | google/gemini-2-5-pro-preview-05-06 |
| 9 | google/gemini-3-7-flash (2026-08) | 1.61 (1.43, 1.79) | ranked |  | google/gemini-2-5-pro-preview-06-05 | google/gemini-2-5-pro-preview-06-05 |
| 10 | xai/grok-4-20-0309-reasoning (2026-03) | 1.59 (1.32, 1.87) | provisional |  | qwen/qwen3-235b-a22b | qwen/qwen3-235b-a22b |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-fable-5** — U 1.81 ± 0.13, ranked (independent evidence in the primary domain):
  - text_style_control/overall = 1506 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/overall) → implies +1.74 ± 0.35, weight 15%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/instruction_following = 1511 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/instruction_following) → implies +1.81 ± 0.35, weight 15%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/multi_turn = 1518 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/multi_turn) → implies +1.71 ± 0.39, weight 12%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1532 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/hard_prompts) → implies +1.75 ± 0.39, weight 11%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/expert = 1548 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/expert) → implies +1.80 ± 0.43, weight 9%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
- **anthropic/claude-opus-4-6** — U 1.77 ± 0.13, ranked (independent evidence in the primary domain):
  - text_style_control/instruction_following = 1513 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/instruction_following) → implies +1.83 ± 0.35, weight 15%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/overall = 1505 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/overall) → implies +1.73 ± 0.35, weight 15%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/multi_turn = 1517 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/multi_turn) → implies +1.71 ± 0.38, weight 13%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1533 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/hard_prompts) → implies +1.76 ± 0.38, weight 11%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/expert = 1546 (independent_evaluator, 2026-09-13, claude-opus-4-6-high, text_style_control/expert) → implies +1.78 ± 0.42, weight 10%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
- **anthropic/claude-opus-4-7** — U 1.72 ± 0.13, ranked (independent evidence in the primary domain):
  - text_style_control/instruction_following = 1503 (independent_evaluator, 2026-09-13, claude-opus-4-7-high, text_style_control/instruction_following) → implies +1.74 ± 0.35, weight 15%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/overall = 1502 (independent_evaluator, 2026-09-13, claude-opus-4-7-high, text_style_control/overall) → implies +1.71 ± 0.35, weight 15%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/multi_turn = 1516 (independent_evaluator, 2026-09-13, claude-opus-4-7-high, text_style_control/multi_turn) → implies +1.70 ± 0.38, weight 12%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1526 (independent_evaluator, 2026-09-13, claude-opus-4-7-high, text_style_control/hard_prompts) → implies +1.70 ± 0.38, weight 11%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/expert = 1533 (independent_evaluator, 2026-09-13, claude-opus-4-7-high, text_style_control/expert) → implies +1.69 ± 0.42, weight 9%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Newest candidates with an evidence gap (not ranked low, not ranked): anthropic/claude-opus-5-5 (2026-09-22): no measurement in chat; measured only in agentic, coding, knowledge, reasoning, vision; openai/gpt-6-luna (2026-09-22): no usable measurement; openai/gpt-6-sol (2026-09-22): no measurement in chat; measured only in coding; xai/grok-4-7 (2026-09-21): no measurement in chat; measured only in agentic, coding; stepfun/step-5-preview (2026-09-16): no usable measurement


### agentic (flat)

Mix {'agentic': 0.6, 'coding': 0.25, 'reasoning': 0.15}. Placed 92 (66 ranked, 26 provisional); scoring every candidate took 4 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) | v1 (production data) |
|---:|---|---|---|---|---|---|
| 1 | anthropic/claude-opus-5-5 (2026-09) | 2.64 (2.35, 2.93) | provisional | yes | anthropic/claude-opus-4-6 | anthropic/claude-opus-4-6 |
| 2 | anthropic/claude-mythos-5-1 (2026-09) | 2.49 (1.99, 2.99) | provisional | yes | google/gemini-2-5-pro | google/gemini-2-5-pro |
| 3 | anthropic/claude-fable-5-1 (2026-09) | 2.31 (2.22, 2.41) | ranked |  | anthropic/claude-opus-4-20250514 | anthropic/claude-opus-4-20250514 |
| 4 | openai/gpt-6-astra (2026-09) | 2.23 (2.13, 2.32) | ranked |  | anthropic/claude-opus-4-1-20250805 | anthropic/claude-opus-4-1-20250805 |
| 5 | anthropic/claude-opus-5 (2026-07) | 2.10 (2.00, 2.20) | ranked |  | anthropic/claude-opus-4-1 | anthropic/claude-opus-4-1 |
| 6 | anthropic/claude-fable-5 (2026-06) | 2.01 (1.92, 2.10) | ranked |  | anthropic/claude-sonnet-4-5-20250929 | anthropic/claude-sonnet-4-5-20250929 |
| 7 | anthropic/claude-mythos-preview (2026-04) | 1.98 (1.71, 2.25) | ranked |  | anthropic/claude-sonnet-4-5 | anthropic/claude-sonnet-4-20250514 |
| 8 | openai/gpt-5-6-sol (2026-07) | 1.90 (1.73, 2.06) | ranked |  | anthropic/claude-sonnet-4-20250514 | anthropic/claude-sonnet-4-5 |
| 9 | moonshot/kimi-k3 (2026-07) | 1.89 (1.80, 1.98) | ranked |  | openai/gpt-4-1 | openai/gpt-4-1 |
| 10 | anthropic/claude-opus-4-8 (2026-05) | 1.88 (1.79, 1.97) | ranked |  | qwen/qwen3-coder-480b-a35b-instruct | qwen/qwen3-coder-480b-a35b-instruct |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-opus-5-5** — U 2.64 ± 0.23, provisional (no independent measurement in agentic):
  - terminal_bench_v4_0 = 66.4% (provider_self_report, 2026-09-22, Claude Opus 5.5 (xhigh), Terminal-Bench 4.0) → implies +2.92 ± 0.38, weight 29%; https://www.anthropic.com/claude-opus-5-5-system-card
  - swe_bench_pro = 89.9% (provider_self_report, 2026-09-22, Claude Opus 5.5, SWE-bench Pro) → implies +3.16 ± 0.46, weight 20%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle_tools = 67.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (with tools)) → implies +2.18 ± 0.47, weight 20%; https://www.anthropic.com/claude-opus-5-5-system-card
  - terminal_bench_science = 58.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Terminal-Bench-Science 0.1) → implies +2.22 ± 0.51, weight 17%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle = 64.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (no tools)) → implies +2.19 ± 0.24, weight 6%; https://www.anthropic.com/claude-opus-5-5-system-card
- **anthropic/claude-mythos-5-1** — U 2.49 ± 0.39, provisional (no independent measurement in agentic):
  - terminal_bench_v4_0 = 60.9% (provider_self_report, 2026-09-01, Claude Mythos 5.1, Terminal-Bench 4.0) → implies +2.63 ± 0.38, weight 100%; https://www.anthropic.com/claude-fable-5-1-system-card
- **anthropic/claude-fable-5-1** — U 2.31 ± 0.07, ranked (independent evidence in the primary domain):
  - agent/overall = 0.1371 (independent_evaluator, 2026-09-15, Claude Fable 5.1 (Max), agent/overall) → implies +2.49 ± 0.10, weight 54%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - webdev/overall = 1755 (independent_evaluator, 2026-09-23, claude-fable-5.1-max, webdev/overall) → implies +2.19 ± 0.05, weight 23%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1517 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, text_style_control/hard_prompts) → implies +1.63 ± 0.40, weight 4%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - terminal_bench_science = 52.6% (provider_self_report, 2026-09-01, Claude Fable 5.1, Terminal-Bench-Science 0.1) → implies +1.83 ± 0.50, weight 3%; https://www.anthropic.com/claude-fable-5-1-system-card
  - document_style_control/overall = 1493 (independent_evaluator, 2026-09-13, claude-fable-5.1-max, document_style_control/overall) → implies +1.95 ± 0.14, weight 3%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Newest candidates with an evidence gap (not ranked low, not ranked): openai/gpt-6-luna (2026-09-22): no usable measurement; openai/gpt-6-sol (2026-09-22): no measurement in agentic; measured only in coding; stepfun/step-5-preview (2026-09-16): no usable measurement; inception/mercury-2-5 (2026-09-08): no usable measurement; openbmb/minicpm5-2b (2026-09-06): no usable measurement


### vision (flat)

Mix {'vision': 0.8, 'reasoning': 0.2}. Placed 109 (86 ranked, 23 provisional); scoring every candidate took 2 ms.

| # | v2 | U (80% interval) | state | lead set | v1 (purged) | v1 (production data) |
|---:|---|---|---|---|---|---|
| 1 | anthropic/claude-opus-5-5 (2026-09) | 2.18 (1.77, 2.58) | provisional | yes | openai/gpt-4-1 | openai/gpt-4-1 |
| 2 | anthropic/claude-mythos-preview (2026-04) | 1.88 (1.48, 2.28) | provisional | yes | openai/gpt-4-1-mini | openai/gpt-4-1-mini |
| 3 | anthropic/claude-fable-5 (2026-06) | 1.81 (1.70, 1.92) | ranked |  | meta/llama-4-maverick-17b-128e-instruct | meta/llama-4-maverick-17b-128e-instruct |
| 4 | anthropic/claude-opus-4-7 (2026-04) | 1.73 (1.62, 1.83) | ranked |  | openai/gpt-4-1-nano | openai/gpt-4-1-nano |
| 5 | anthropic/claude-opus-4-6 (2026-02) | 1.72 (1.62, 1.83) | ranked |  | meta/llama-4-scout-17b-16e-instruct | meta/llama-4-scout-17b-16e-instruct |
| 6 | qwen/qwen3-8-max (2026-08) | 1.69 (1.58, 1.81) | ranked |  | meta/llama-4-maverick-17b-128e-instruct-fp8 | meta/llama-4-maverick-17b-128e-instruct-fp8 |
| 7 | google/gemini-3-8-flash (2026-09) | 1.69 (1.27, 2.10) | provisional |  | google/gemini-1-5-pro | google/gemini-1-5-pro |
| 8 | anthropic/claude-fable-5-1 (2026-09) | 1.67 (1.56, 1.78) | ranked |  | google/gemini-2-0-flash-lite | google/gemini-2-0-flash-lite |
| 9 | anthropic/claude-opus-5 (2026-07) | 1.66 (1.55, 1.76) | ranked |  | anthropic/claude-opus-4-6 | anthropic/claude-opus-4-6 |
| 10 | meta/muse-spark (2026-04) | 1.64 (1.54, 1.74) | ranked |  | google/gemini-2-5-pro | google/gemini-2-5-pro |

Why, for the top 3 (the five measurements carrying the most weight):

- **anthropic/claude-opus-5-5** — U 2.18 ± 0.32, provisional (no independent measurement in vision):
  - swe_bench_multimodal = 61.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, SWE-bench Multimodal) → implies +2.25 ± 0.34, weight 47%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle = 64.4% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (no tools)) → implies +2.19 ± 0.24, weight 36%; https://www.anthropic.com/claude-opus-5-5-system-card
  - hle_tools = 67.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Humanity's Last Exam (with tools)) → implies +2.18 ± 0.47, weight 7%; https://www.anthropic.com/claude-opus-5-5-system-card
  - terminal_bench_science = 58.7% (provider_self_report, 2026-09-22, Claude Opus 5.5, Terminal-Bench-Science 0.1) → implies +2.22 ± 0.51, weight 6%; https://www.anthropic.com/claude-opus-5-5-system-card
  - webdev/overall = 1818 (independent_evaluator, 2026-09-23, claude-opus-5.5-max, webdev/overall) → implies +2.38 ± 0.06, weight -4%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
- **anthropic/claude-mythos-preview** — U 1.88 ± 0.31, provisional (no independent measurement in vision):
  - swe_bench_multimodal = 59% (provider_self_report, 2026-04-07, Claude Mythos Preview, SWE-bench Multimodal (internal implementation)) → implies +2.09 ± 0.38, weight 38%; https://www.anthropic.com/glasswing
  - hle = 56.8% (provider_self_report, 2026-04-07, Claude Mythos Preview, Humanity's Last Exam, no tools) → implies +1.85 ± 0.24, weight 29%; https://www.anthropic.com/glasswing
  - gpqa_diamond = 94.55% (provider_self_report, 2026-04-07, Claude Mythos Preview, GPQA Diamond (198 questions)) → implies +1.58 ± 0.41, weight 10%; https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
  - charxiv_reasoning = 86.1% (provider_self_report, 2026-04-07, Claude Mythos Preview, CharXiv Reasoning, no tools) → implies +1.49 ± 0.84, weight 10%; https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
  - hle_tools = 64.7% (provider_self_report, 2026-04-07, Claude Mythos Preview, Humanity's Last Exam, with tools) → implies +1.94 ± 0.47, weight 7%; https://www.anthropic.com/glasswing
- **anthropic/claude-fable-5** — U 1.81 ± 0.08, ranked (independent evidence in the primary domain):
  - vision_style_control/overall = 1310 (independent_evaluator, 2026-09-13, claude-fable-5, vision_style_control/overall) → implies +1.78 ± 0.07, weight 75%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - document_style_control/overall = 1499 (independent_evaluator, 2026-09-13, claude-fable-5, document_style_control/overall) → implies +2.05 ± 0.09, weight 10%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/hard_prompts = 1532 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/hard_prompts) → implies +1.75 ± 0.39, weight 6%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - webdev/overall = 1627 (independent_evaluator, 2026-09-23, claude-fable-5-high, webdev/overall) → implies +1.80 ± 0.05, weight 2%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  - text_style_control/expert = 1548 (independent_evaluator, 2026-09-13, claude-fable-5, text_style_control/expert) → implies +1.80 ± 0.43, weight 1%; https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Newest candidates with an evidence gap (not ranked low, not ranked): openai/gpt-6-luna (2026-09-22): no usable measurement; openai/gpt-6-sol (2026-09-22): no measurement in vision; measured only in coding; xai/grok-4-7 (2026-09-21): no measurement in vision; measured only in agentic, coding; stepfun/step-5-preview (2026-09-16): no usable measurement; deepseek/deepseek-flash (2026-09-10): no measurement in vision; measured only in agentic, coding, knowledge, reasoning
