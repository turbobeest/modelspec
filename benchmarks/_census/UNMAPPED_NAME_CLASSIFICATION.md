# Unmatched leaderboard names (284)

Classification of `refusals.unmapped_name` from the 2026-09-10 AA + LM Arena harvest.
Mapping is explicit. A wrong alias is worse than a refusal.

## Counts

| class | names | scored cells |
| --- | ---: | ---: |
| naming drift (unique existing card, different spelling) | 84 | 208 |
| effort / serving / dated / quant variant of a carded model | 30 | 69 |
| ambiguous (more than one honest card) | 22 | 61 |
| genuinely missing; card created | 104 | 329 |
| could not confirm against a primary source | 44 | 101 |
| not a model (dataset / harness / aggregate) | 0 | 0 |
| **total** | **284** | **768** |

None of the 284 is a dataset, harness, or aggregate row. Leaderboard harvests are model rows;
`rnj-1-base-evals` was a census candidate, not in this 284.

## Aliases for `LEDGER_TO_CARD`

`scripts/attach_evidence.py` is owned by another agent and was not edited.
These are unique spelling matches only. Effort rows and ambiguous names are absent.

```python
    'Claude 3 Haiku': 'anthropic/claude-3-haiku-20240307',
    'Claude 3 Opus': 'anthropic/claude-3-opus-20240229',
    'Claude 3 Sonnet': 'anthropic/claude-3-sonnet-20240229',
    'Claude 3.5 Haiku': 'anthropic/claude-3-5-haiku-20241022',
    'Claude 3.5 Sonnet (June)': 'anthropic/claude-3-5-sonnet-20240620',
    'Claude 3.5 Sonnet (Oct)': 'anthropic/claude-3-5-sonnet-20241022',
    'Claude 3.7 Sonnet': 'anthropic/claude-3-7-sonnet-20250219',
    'Claude 4 Opus': 'anthropic/claude-opus-4-20250514',
    'Claude 4 Sonnet': 'anthropic/claude-sonnet-4-20250514',
    'Claude 4.1 Opus': 'anthropic/claude-opus-4-1-20250805',
    'Claude 4.5 Haiku': 'anthropic/claude-haiku-4-5-20251001',
    'Claude 4.5 Sonnet': 'anthropic/claude-sonnet-4-5-20250929',
    'Cogito v2.1': 'deepcogito/cogito-671b-v2-1',
    'DeepSeek Coder V2 Lite': 'deepseek/deepseek-coder-v2-lite-instruct',
    'DeepSeek R1 (Jan)': 'deepseek/deepseek-r1',
    'DeepSeek V3 (Dec)': 'deepseek/deepseek-v3',
    'Devstral Small (May)': 'mistral/devstral-small-2505',
    'Gemini 2.5 Flash (Apr)': 'google/gemini-2-5-flash-preview-04-17',
    'Gemini 2.5 Flash (Sep)': 'google/gemini-2-5-flash-preview-09-2025',
    'Gemini 2.5 Flash-Lite (Sep)': 'google/gemini-2-5-flash-lite-preview-09-2025',
    'Gemini 2.5 Pro (May)': 'google/gemini-2-5-pro-preview-05-06',
    'gemini-2.0-flash-001': 'google/gemini-2-0-flash',
    'Gemma 3n E2B': 'google/gemma-3n-e2b-it',
    'Gemma 3n E4B': 'google/gemma-3n-e4b-it',
    'Gemma 3n E4B (May)': 'google/gemma-3n-e4b-it',
    'Gemma 4 26B A4B': 'google/gemma-4-26b-a4b-it',
    'Gemma 4 E2B': 'google/gemma-4-e2b-it',
    'Gemma 4 E4B': 'google/gemma-4-e4b-it',
    'gemma-4-26b-a4b': 'google/gemma-4-26b-a4b-it',
    'gpt-4.1-2025-04-14': 'openai/gpt-4-1',
    'gpt-4.1-mini-2025-04-14': 'openai/gpt-4-1-mini',
    'GPT-4o (Aug)': 'openai/gpt-4o-2024-08-06',
    'GPT-4o (May)': 'openai/gpt-4o-2024-05-13',
    'GPT-4o (Nov)': 'openai/gpt-4o-2024-11-20',
    'Granite 3.3 8B': 'ibm/granite-3-3-8b-instruct',
    'grok-4-0709': 'xai/grok-4',
    'grok-4.20-multi-agent-beta-0309': 'xai/grok-4-20-multi-agent-0309',
    'Inkling': 'thinkingmachines/inkling',
    'inkling': 'thinkingmachines/inkling',
    'Jamba 1.5 Large': 'ai21/ai21-jamba-large-1-5',
    'Jamba 1.5 Mini': 'ai21/ai21-jamba-mini-1-5',
    'Jamba 1.6 Large': 'ai21/ai21-jamba-large-1-6',
    'Jamba 1.6 Mini': 'ai21/ai21-jamba-mini-1-6',
    'Jamba 1.7 Mini': 'ai21/ai21-jamba-mini-1-7',
    'Llama 2 Chat 13B': 'meta/llama-2-13b-chat-hf',
    'Llama 2 Chat 70B': 'meta/llama-2-70b-chat-hf',
    'Llama 2 Chat 7B': 'meta/llama-2-7b-chat-hf',
    'Llama 3.3 70B': 'meta/llama-3-3-70b-instruct',
    'Llama 3.3 Nemotron Super 49B': 'nvidia/llama-3-3-nemotron-super-49b-v1-5',
    'Llama 4 Maverick': 'meta/llama-4-maverick-17b-128e-instruct',
    'Llama Nemotron Super 49B v1.5': 'nvidia/llama-3-3-nemotron-super-49b-v1-5',
    'Ministral 3 14B': 'mistral/ministral-3-14b-instruct-2512',
    'Ministral 3 8B': 'mistral/ministral-3-8b-instruct-2512',
    'Mistral Large 2 (Nov)': 'mistral/mistral-large-2411',
    'Mistral Small 3': 'mistral/mistral-small-24b-instruct-2501',
    'Mistral Small 3.1': 'mistral/mistral-small-3-1-24b-instruct-2503',
    'Molmo 7B-D': 'allen-ai/molmo-7b-d-0924',
    'muse-glimmer': 'meta/muse-glimmer-30b',
    'Nemotron 3 Ultra': 'nvidia/nvidia-nemotron-3-ultra-550b-a55b',
    'Nemotron 3.5 Lightning': 'nvidia/nvidia-nemotron-3-5-lightning-30b-a3b',
    'o1-2024-12-17': 'openai/o1',
    'o3-2025-04-16': 'openai/o3',
    'o4-mini-2025-04-16': 'openai/o4-mini',
    'Phi-4 Mini': 'microsoft/phi-4-mini-instruct',
    'Phi-4 Multimodal': 'microsoft/phi-4-multimodal-instruct',
    'Pixtral Large': 'mistral/pixtral-large-latest',
    'Qwen2.5 72B': 'qwen/qwen2-5-72b-instruct',
    'Qwen2.5 Coder 32B': 'qwen/qwen2-5-coder-32b-instruct',
    'Qwen2.5 Coder 7B': 'qwen/qwen2-5-coder-7b-instruct',
    'Qwen2.5 Instruct 32B': 'qwen/qwen2-5-32b-instruct',
    'Qwen3 235B': 'qwen/qwen3-235b-a22b',
    'Qwen3 235B A22B 2507': 'cerebras/qwen-3-235b-a22b-instruct-2507',
    'Qwen3 30B A3B 2507': 'qwen/qwen3-30b-a3b-instruct-2507',
    'Qwen3 Coder 30B A3B': 'qwen/qwen3-coder-30b-a3b-instruct',
    'Qwen3 Coder 480B': 'qwen/qwen3-coder-480b-a35b-instruct',
    'Qwen3 VL 32B': 'qwen/qwen3-vl-32b-instruct',
    'Qwen3 VL 4B': 'qwen/qwen3-vl-4b-instruct',
    'Qwen3 VL 8B': 'qwen/qwen3-vl-8b-instruct',
    'qwen3-235b-a22b-instruct-2507': 'cerebras/qwen-3-235b-a22b-instruct-2507',
    'qwen3-vl-235b-a22b-instruct': 'qwen/qwen3-vl-235b-a22b',
    'Qwen3.5 Omni Flash': 'qwen/qwen3-omni-flash',
    'qwen3.8-max': 'qwen/qwen3-8-max',
    'Solar Pro 2': 'upstage/solar-pro2',
    'Solar Pro 3': 'upstage/solar-pro3',
```

## naming drift (unique existing card, different spelling)

- `Claude 3 Haiku` (3 cells) → `anthropic/claude-3-haiku-20240307` — display is Claude Haiku 3; only Claude 3 Haiku card
- `Claude 3 Opus` (1 cells) → `anthropic/claude-3-opus-20240229` — display is Claude Opus 3
- `Claude 3 Sonnet` (1 cells) → `anthropic/claude-3-sonnet-20240229` — display is Claude Sonnet 3
- `Claude 3.5 Haiku` (4 cells) → `anthropic/claude-3-5-haiku-20241022` — dated card display Claude Haiku 3.5; latest sibling has (latest)
- `Claude 3.5 Sonnet (June)` (1 cells) → `anthropic/claude-3-5-sonnet-20240620` — June 2024 snapshot is 20240620
- `Claude 3.5 Sonnet (Oct)` (1 cells) → `anthropic/claude-3-5-sonnet-20241022` — Oct 2024 snapshot is 20241022 / Sonnet 3.5 v2
- `Claude 3.7 Sonnet` (2 cells) → `anthropic/claude-3-7-sonnet-20250219` — display is Claude Sonnet 3.7; unique
- `Claude 4 Opus` (2 cells) → `anthropic/claude-opus-4-20250514` — word order of Claude Opus 4; latest sibling has (latest)
- `Claude 4 Sonnet` (4 cells) → `anthropic/claude-sonnet-4-20250514` — word order of Claude Sonnet 4
- `Claude 4.1 Opus` (3 cells) → `anthropic/claude-opus-4-1-20250805` — word order of Claude Opus 4.1 dated card
- `Claude 4.5 Haiku` (5 cells) → `anthropic/claude-haiku-4-5-20251001` — word order of Claude Haiku 4.5 dated card
- `Claude 4.5 Sonnet` (5 cells) → `anthropic/claude-sonnet-4-5-20250929` — word order of Claude Sonnet 4.5 dated card
- `Cogito v2.1` (3 cells) → `deepcogito/cogito-671b-v2-1` — card display is Cogito v2.1 671B
- `DeepSeek Coder V2 Lite` (1 cells) → `deepseek/deepseek-coder-v2-lite-instruct` — only Lite card is Instruct
- `DeepSeek R1 (Jan)` (5 cells) → `deepseek/deepseek-r1` — original R1 is the Jan 2025 row; 0528 is a later card
- `DeepSeek V3 (Dec)` (5 cells) → `deepseek/deepseek-v3` — original V3 Dec 2024; 0324 is a later card
- `Devstral Small (May)` (3 cells) → `mistral/devstral-small-2505` — May is 2505; display Devstral Small is the July 2507 card
- `Gemini 2.5 Flash (Apr)` (1 cells) → `google/gemini-2-5-flash-preview-04-17` — April preview card exists
- `Gemini 2.5 Flash (Sep)` (3 cells) → `google/gemini-2-5-flash-preview-09-2025` — September preview card exists
- `Gemini 2.5 Flash-Lite (Sep)` (3 cells) → `google/gemini-2-5-flash-lite-preview-09-2025` — September preview card exists
- `Gemini 2.5 Pro (May)` (1 cells) → `google/gemini-2-5-pro-preview-05-06` — May preview card
- `gemini-2.0-flash-001` (1 cells) → `google/gemini-2-0-flash` — GA API id of Gemini 2.0 Flash
- `Gemma 3n E2B` (3 cells) → `google/gemma-3n-e2b-it` — display Gemma 3n 2B; only IT card
- `Gemma 3n E4B` (3 cells) → `google/gemma-3n-e4b-it` — display Gemma 3n 4B; only IT card
- `Gemma 3n E4B (May)` (1 cells) → `google/gemma-3n-e4b-it` — May launch of the only E4B card
- `Gemma 4 26B A4B` (4 cells) → `google/gemma-4-26b-a4b-it` — only A4B card is IT
- `Gemma 4 E2B` (4 cells) → `google/gemma-4-e2b-it` — only E2B card is IT
- `Gemma 4 E4B` (4 cells) → `google/gemma-4-e4b-it` — only E4B card is IT
- `gemma-4-26b-a4b` (1 cells) → `google/gemma-4-26b-a4b-it` — Arena slug of 26B A4B IT
- `gpt-4.1-2025-04-14` (1 cells) → `openai/gpt-4-1` — API snapshot id of GPT-4.1
- `gpt-4.1-mini-2025-04-14` (1 cells) → `openai/gpt-4-1-mini` — API snapshot id of GPT-4.1 mini
- `GPT-4o (Aug)` (3 cells) → `openai/gpt-4o-2024-08-06` — dated card GPT-4o (2024-08-06)
- `GPT-4o (May)` (1 cells) → `openai/gpt-4o-2024-05-13` — dated card GPT-4o (2024-05-13)
- `GPT-4o (Nov)` (3 cells) → `openai/gpt-4o-2024-11-20` — dated card GPT-4o (2024-11-20)
- `Granite 3.3 8B` (2 cells) → `ibm/granite-3-3-8b-instruct` — display granite 3.3 8B instruct
- `grok-4-0709` (1 cells) → `xai/grok-4` — Grok 4 launch id 0709
- `grok-4.20-multi-agent-beta-0309` (1 cells) → `xai/grok-4-20-multi-agent-0309` — beta tag on the 0309 multi-agent card
- `Inkling` (5 cells) → `thinkingmachines/inkling` — exact display after 2563e7a; harvest predates the card
- `inkling` (1 cells) → `thinkingmachines/inkling` — Arena slug of Inkling
- `Jamba 1.5 Large` (1 cells) → `ai21/ai21-jamba-large-1-5` — display AI21 Jamba Large 1.5
- `Jamba 1.5 Mini` (1 cells) → `ai21/ai21-jamba-mini-1-5` — display AI21 Jamba Mini 1.5
- `Jamba 1.6 Large` (1 cells) → `ai21/ai21-jamba-large-1-6` — display AI21 Jamba Large 1.6
- `Jamba 1.6 Mini` (1 cells) → `ai21/ai21-jamba-mini-1-6` — display AI21 Jamba Mini 1.6
- `Jamba 1.7 Mini` (3 cells) → `ai21/ai21-jamba-mini-1-7` — display AI21 Jamba Mini 1.7
- `Llama 2 Chat 13B` (1 cells) → `meta/llama-2-13b-chat-hf` — chat-hf card
- `Llama 2 Chat 70B` (1 cells) → `meta/llama-2-70b-chat-hf` — chat-hf card
- `Llama 2 Chat 7B` (1 cells) → `meta/llama-2-7b-chat-hf` — chat-hf card
- `Llama 3.3 70B` (4 cells) → `meta/llama-3-3-70b-instruct` — only 70B 3.3 card is Instruct
- `Llama 3.3 Nemotron Super 49B` (3 cells) → `nvidia/llama-3-3-nemotron-super-49b-v1-5` — v1.5 is the Super 49B card
- `Llama 4 Maverick` (5 cells) → `meta/llama-4-maverick-17b-128e-instruct` — no base Maverick card; FP8 is a quant
- `Llama Nemotron Super 49B v1.5` (2 cells) → `nvidia/llama-3-3-nemotron-super-49b-v1-5` — same card
- `Ministral 3 14B` (5 cells) → `mistral/ministral-3-14b-instruct-2512` — only 14B card is Instruct
- `Ministral 3 8B` (5 cells) → `mistral/ministral-3-8b-instruct-2512` — bf16 sibling is a serving dump
- `Mistral Large 2 (Nov)` (2 cells) → `mistral/mistral-large-2411` — display Mistral Large 2.1
- `Mistral Small 3` (2 cells) → `mistral/mistral-small-24b-instruct-2501` — Small 3 is the Jan 2025 24B instruct
- `Mistral Small 3.1` (5 cells) → `mistral/mistral-small-3-1-24b-instruct-2503` — display Mistral Small 3.1 24B Instruct 2503
- `Molmo 7B-D` (2 cells) → `allen-ai/molmo-7b-d-0924` — display Molmo 7B D 0924
- `muse-glimmer` (1 cells) → `meta/muse-glimmer-30b` — display Muse Glimmer 30B
- `Nemotron 3 Ultra` (5 cells) → `nvidia/nvidia-nemotron-3-ultra-550b-a55b` — display NVIDIA Nemotron 3 Ultra
- `Nemotron 3.5 Lightning` (5 cells) → `nvidia/nvidia-nemotron-3-5-lightning-30b-a3b` — display NVIDIA Nemotron 3.5 Lightning 30B A3B
- `o1-2024-12-17` (1 cells) → `openai/o1` — API snapshot id of o1
- `o3-2025-04-16` (1 cells) → `openai/o3` — API snapshot id of o3
- `o4-mini-2025-04-16` (1 cells) → `openai/o4-mini` — API snapshot id of o4-mini
- `Phi-4 Mini` (4 cells) → `microsoft/phi-4-mini-instruct` — only Mini card is Instruct
- `Phi-4 Multimodal` (1 cells) → `microsoft/phi-4-multimodal-instruct` — only multimodal card is Instruct
- `Pixtral Large` (1 cells) → `mistral/pixtral-large-latest` — only Pixtral Large card
- `Qwen2.5 72B` (2 cells) → `qwen/qwen2-5-72b-instruct` — only 72B card is Instruct
- `Qwen2.5 Coder 32B` (1 cells) → `qwen/qwen2-5-coder-32b-instruct` — only 32B coder card is Instruct
- `Qwen2.5 Coder 7B` (1 cells) → `qwen/qwen2-5-coder-7b-instruct` — only 7B coder card is Instruct
- `Qwen2.5 Instruct 32B` (1 cells) → `qwen/qwen2-5-32b-instruct` — display Qwen2.5 32B Instruct
- `Qwen3 235B` (3 cells) → `qwen/qwen3-235b-a22b` — unqualified 235B is the original A22B card
- `Qwen3 235B A22B 2507` (5 cells) → `cerebras/qwen-3-235b-a22b-instruct-2507` — only 2507 instruct card is the Cerebras serving
- `Qwen3 30B A3B 2507` (5 cells) → `qwen/qwen3-30b-a3b-instruct-2507` — unique 2507 instruct card
- `Qwen3 Coder 30B A3B` (3 cells) → `qwen/qwen3-coder-30b-a3b-instruct` — only 30B coder card is Instruct
- `Qwen3 Coder 480B` (3 cells) → `qwen/qwen3-coder-480b-a35b-instruct` — only 480B coder card is Instruct
- `Qwen3 VL 32B` (2 cells) → `qwen/qwen3-vl-32b-instruct` — only 32B VL card is Instruct
- `Qwen3 VL 4B` (3 cells) → `qwen/qwen3-vl-4b-instruct` — only 4B VL card is Instruct
- `Qwen3 VL 8B` (3 cells) → `qwen/qwen3-vl-8b-instruct` — only 8B VL card is Instruct
- `qwen3-235b-a22b-instruct-2507` (1 cells) → `cerebras/qwen-3-235b-a22b-instruct-2507` — exact Cerebras card slug
- `qwen3-vl-235b-a22b-instruct` (1 cells) → `qwen/qwen3-vl-235b-a22b` — card display Qwen3-VL 235B-A22B
- `Qwen3.5 Omni Flash` (3 cells) → `qwen/qwen3-omni-flash` — display Qwen3-Omni Flash
- `qwen3.8-max` (1 cells) → `qwen/qwen3-8-max` — slug qwen3-8-max vs display Qwen3.8 Max
- `Solar Pro 2` (3 cells) → `upstage/solar-pro2` — display solar-pro2
- `Solar Pro 3` (5 cells) → `upstage/solar-pro3` — display solar-pro3

## effort / serving / dated / quant variant of a carded model

- `Claude Fable 5 (with fallback)` (5 cells) → `anthropic/claude-fable-5` — fallback serving of Fable 5; not the product row
- `Claude Fable 5.1 (max with fallback)` (5 cells) → `anthropic/claude-fable-5-1` — fallback serving even with max
- `DeepSeek V4 Flash Vision (max)` (5 cells) → `deepseek/deepseek-v4-flash-vision-exp` — max row of the vision-exp card; not folded onto exp
- `DeepSeek V4 Pro 0813 (max)` (5 cells) → `deepseek/deepseek-v4-pro` — 0813 is a dated checkpoint of V4 Pro
- `Gemini 1.5 Flash (May)` (1 cells) → `google/gemini-1-5-flash` — dated snapshot of the single 1.5 Flash card
- `Gemini 1.5 Flash (Sep)` (1 cells) → `google/gemini-1-5-flash` — dated snapshot of the single 1.5 Flash card
- `Gemini 1.5 Pro (May)` (1 cells) → `google/gemini-1-5-pro` — dated snapshot
- `Gemini 1.5 Pro (Sep)` (1 cells) → `google/gemini-1-5-pro` — dated snapshot
- `Gemini 2.0 Flash (exp)` (1 cells) → `google/gemini-2-0-flash` — experimental serving
- `Gemini 2.0 Flash-Lite (Feb)` (1 cells) → `google/gemini-2-0-flash-lite` — dated snapshot
- `Gemini 3 Deep Think` (1 cells) → `google/gemini-3-pro-preview` — Deep Think is a thinking mode, not a separate product card
- `Gemini 3.5 Flash (minimal)` (3 cells) → `google/gemini-3-5-flash` — minimal effort
- `GPT-4o (ChatGPT)` (2 cells) → `openai/gpt-4o` — ChatGPT wrapper, not the API product row
- `GPT-5 (ChatGPT)` (2 cells) → `openai/gpt-5` — ChatGPT wrapper
- `GPT-5 (minimal)` (2 cells) → `openai/gpt-5` — minimal effort; token not in EFFORT_TOKENS
- `GPT-5 mini (minimal)` (3 cells) → `openai/gpt-5-mini` — minimal effort
- `GPT-5 nano (minimal)` (3 cells) → `openai/gpt-5-nano` — minimal effort
- `GPT-5.5 Instant (June 2026)` (5 cells) → `openai/gpt-5-5` — Instant is a serving SKU of GPT-5.5
- `GPT-5.5 Instant (May 2026)` (3 cells) → `openai/gpt-5-5` — dated Instant serving
- `gpt-5.5-instant` (1 cells) → `openai/gpt-5-5` — Arena Instant SKU
- `Grok Build 0.1 0616` (4 cells) → `xai/grok-build-0-1` — dated 0616 snapshot of Grok Build 0.1
- `grok-3-mini-beta` (1 cells) → `xai/grok-3-mini` — beta serving
- `kimi-k2.5-instant` (1 cells) → `moonshot/kimi-k2-5` — Instant serving of K2.5
- `longcat-flash-chat-2602-exp` (1 cells) → `meituan/longcat-flash-chat` — experimental dated serving; Hub 401
- `MiMo-V2-Flash (Feb 2026)` (3 cells) → `xiaomi/mimo-v2-flash` — dated snapshot of Flash
- `Mistral Large (Feb)` (1 cells) → `mistral/mistral-large-latest` — dated snapshot; Large 2.1/3 are other cards
- `Motif 3 (Beta)` (4 cells) → `motif/motif-3` — beta serving of Motif 3
- `nvidia-nemotron-3-ultra-550b-a55b-nvfp4` (1 cells) → `nvidia/nvidia-nemotron-3-ultra-550b-a55b` — NVFP4 serving dump; 2563e7a refused to card it
- `nvidia-nemotron-3.5-lightning-30b-a3b-nvfp4` (1 cells) → `nvidia/nvidia-nemotron-3-5-lightning-30b-a3b` — NVFP4 serving dump
- `qwen3-max-2025-09-23` (1 cells) → `qwen/qwen3-max` — dated snapshot of Qwen3 Max

## ambiguous (more than one honest card)

- `gemini-3-pro` (1 cells) → `—` — gemini-3-pro-preview vs gemini-3-pro-image
- `Gemma 3 1B` (3 cells) → `—` — gemma-3-1b-it and gemma-3-1b-pt both exist
- `gpt-5-chat` (1 cells) → `—` — gpt-5-chat-latest vs gpt-5-1/5-2 chat-latest
- `Grok 4.20 0309` (3 cells) → `—` — reasoning and non-reasoning 0309 cards both exist
- `grok-4.1` (1 cells) → `—` — grok-4-1-fast and grok-4-1-fast-non-reasoning; no plain 4.1 card
- `Kimi K2` (3 cells) → `—` — kimi-k2-0711-preview and kimi-k2-0905-preview
- `Llama 3 70B` (3 cells) → `—` — base and instruct both exist (same defect as Llama 3.1 70B refusal)
- `Llama 3 8B` (3 cells) → `—` — base and instruct both exist
- `Llama 4 Scout` (5 cells) → `—` — base scout-17b-16e and instruct both exist
- `Magistral Small 1` (3 cells) → `—` — magistral-small and magistral-small-2506
- `minimax-m1` (1 cells) → `—` — 40k and 80k both now carded
- `Ministral 3 3B` (5 cells) → `—` — base-2512 and instruct-2512 both exist
- `Nemotron 3 Nano` (5 cells) → `—` — bf16 / fp8 / nvfp4 / base-bf16 all carded
- `Nemotron 3 Super` (5 cells) → `—` — bf16 / fp8 / nvfp4 all carded
- `NVIDIA Nemotron Nano 12B v2 VL` (3 cells) → `—` — bf16 and fp8 VL cards
- `nvidia-nemotron-3-super-120b-a12b` (1 cells) → `—` — bf16 / fp8 / nvfp4
- `OLMo 2 7B` (2 cells) → `—` — olmo-2-1124-7b base already existed; instruct now carded too
- `Olmo 3 7B` (3 cells) → `—` — instruct, instruct-sft, think, 1025-7b
- `Phi-3 Mini` (1 cells) → `—` — 4k and 128k instruct cards
- `Qwen3 30B` (3 cells) → `—` — qwen3-30b-a3b vs instruct-2507 vs nvfp4
- `Qwen3 4B 2507` (3 cells) → `—` — instruct-2507 and thinking-2507 both exist
- `Qwen3 Next 80B A3B` (3 cells) → `—` — instruct vs thinking cards

## genuinely missing; card created

- `A.X-K2` (5 cells) → `skt/a-x-k2` — Hub skt/A.X-K2
- `Agnes 2.5 Pro Alpha` (5 cells) → `agnes-ai/agnes-2-5-pro-alpha` — Hub Agnes-AI/Agnes-2.5-Pro-Alpha
- `Apertus 70B Instruct` (3 cells) → `swiss-ai/apertus-70b-instruct-2509` — Hub swiss-ai/Apertus-70B-Instruct-2509
- `Apertus 8B Instruct` (3 cells) → `swiss-ai/apertus-8b-instruct-2509` — Hub swiss-ai/Apertus-8B-Instruct-2509
- `Apriel-v1.5-15B-Thinker` (3 cells) → `servicenow/apriel-1-5-15b-thinker` — Hub ServiceNow-AI/Apriel-1.5-15b-Thinker
- `Apriel-v1.6-15B-Thinker` (2 cells) → `servicenow/apriel-1-6-15b-thinker` — Hub ServiceNow-AI/Apriel-1.6-15b-Thinker
- `Claude 2.0` (1 cells) → `anthropic/claude-2-0` — closed; Anthropic 2023-07-11 announcement
- `Claude 2.1` (1 cells) → `anthropic/claude-2-1` — closed; Anthropic 2023-11-21 announcement
- `Claude Instant` (1 cells) → `anthropic/claude-instant-1` — closed; Anthropic Instant SKU
- `DeepHermes 3 - Mistral 24B` (1 cells) → `nous-research/deephermes-3-mistral-24b-preview` — Hub NousResearch/DeepHermes-3-Mistral-24B-Preview
- `DeepSeek V3.1 Terminus` (5 cells) → `deepseek/deepseek-v3-1-terminus` — Hub deepseek-ai/DeepSeek-V3.1-Terminus
- `DeepSeek V3.2 Speciale` (3 cells) → `deepseek/deepseek-v3-2-speciale` — Hub deepseek-ai/DeepSeek-V3.2-Speciale
- `DeepSeek-V2.5 (Dec)` (1 cells) → `deepseek/deepseek-v2-5` — Hub deepseek-ai/DeepSeek-V2.5
- `deepseek-v3.1-terminus` (1 cells) → `deepseek/deepseek-v3-1-terminus` — Arena slug of Terminus
- `DiffusionGemma 26B A4B` (4 cells) → `google/diffusiongemma-26b-a4b-it` — Hub google/diffusiongemma-26B-A4B-it
- `ERNIE 4.5 300B A47B` (2 cells) → `baidu/ernie-4-5-300b-a47b-pt` — Hub baidu/ERNIE-4.5-300B-A47B-PT
- `Exaone 4.0 1.2B` (3 cells) → `lgai-exaone/exaone-4-0-1-2b` — Hub LGAI-EXAONE/EXAONE-4.0-1.2B
- `EXAONE 4.0 32B` (2 cells) → `lgai-exaone/exaone-4-0-32b` — Hub LGAI-EXAONE/EXAONE-4.0-32B
- `EXAONE 4.5 33B` (4 cells) → `lgai-exaone/exaone-4-5-33b` — Hub LGAI-EXAONE/EXAONE-4.5-33B
- `G9v3-39A5B` (5 cells) → `ai9stars/g9v3-39a5b` — Hub ai9stars/G9v3-39A5B
- `G9v3-3B` (4 cells) → `ai9stars/g9v3-3b` — Hub ai9stars/G9v3-3B
- `Gemini 1.0 Pro` (1 cells) → `google/gemini-1-0-pro` — closed; Gemini 1.0 announcement 2023-12-06
- `Gemma 4 12B` (4 cells) → `google/gemma-4-12b-it` — Hub has base and IT; both carded; unqualified name stays ambiguous — no alias
- `Granite 4.1 30B` (4 cells) → `ibm/granite-4-1-30b` — Hub ibm-granite/granite-4.1-30b
- `Granite 4.1 3B` (4 cells) → `ibm/granite-4-1-3b` — Hub ibm-granite/granite-4.1-3b
- `Granite 4.1 8B` (3 cells) → `ibm/granite-4-1-8b` — Hub ibm-granite/granite-4.1-8b
- `Granite 4.2 30B` (5 cells) → `ibm/granite-4-2-30b` — Hub ibm-granite/granite-4.2-30b
- `Granite 4.2 3B` (5 cells) → `ibm/granite-4-2-3b` — Hub ibm-granite/granite-4.2-3b
- `Granite 4.2 8B` (5 cells) → `ibm/granite-4-2-8b` — Hub ibm-granite/granite-4.2-8b
- `Hermes 3 - Llama-3.1 70B` (1 cells) → `nous-research/hermes-3-llama-3-1-70b` — Hub NousResearch/Hermes-3-Llama-3.1-70B
- `Hermes 4 405B` (3 cells) → `nous-research/hermes-4-405b` — Hub NousResearch/Hermes-4-405B
- `Hermes 4 70B` (3 cells) → `nous-research/hermes-4-70b` — official BF16; existing card is FP8 only
- `Hy3` (5 cells) → `tencent/hy3` — Hub tencent/Hy3
- `hy3` (1 cells) → `tencent/hy3` — Arena slug
- `HyperCLOVA X SEED Think (32B)` (3 cells) → `naver/hyperclovax-seed-think-32b` — Hub naver-hyperclovax/HyperCLOVAX-SEED-Think-32B
- `Inkling Small` (6 cells) → `thinkingmachines/inkling-small` — Hub thinkingmachines/Inkling-Small safetensors 265956439090
- `INTELLECT-3` (3 cells) → `primeintellect/intellect-3` — Hub PrimeIntellect/INTELLECT-3
- `intellect-3` (1 cells) → `primeintellect/intellect-3` — Arena slug
- `Jamba 1.7 Large` (3 cells) → `ai21/ai21-jamba-large-1-7` — Hub ai21labs/AI21-Jamba-Large-1.7
- `K-EXAONE` (4 cells) → `lgai-exaone/k-exaone-236b-a23b` — Hub LGAI-EXAONE/K-EXAONE-236B-A23B
- `K-EXAONE 2.0` (5 cells) → `lgai-exaone/k-exaone-2-0-750b-a37b` — Hub LGAI-EXAONE/K-EXAONE-2.0-750B-A37B
- `K2 Think V2` (4 cells) → `ifm/k2-think-v2` — Hub IFM/K2-Think-V2
- `Kimi Linear 48B A3B Instruct` (2 cells) → `moonshot/kimi-linear-48b-a3b-instruct` — Hub moonshotai/Kimi-Linear-48B-A3B-Instruct
- `LFM2 1.2B` (3 cells) → `liquid/lfm2-1-2b` — Hub LiquidAI/LFM2-1.2B
- `LFM2 2.6B` (3 cells) → `liquid/lfm2-2-6b` — Hub LiquidAI/LFM2-2.6B
- `LFM2 24B A2B` (3 cells) → `liquid/lfm2-24b-a2b` — non-GGUF Hub repo; GGUF card already existed
- `LFM2.5-2.6B` (5 cells) → `liquid/lfm2-5-2-6b` — Hub LiquidAI/LFM2.5-2.6B
- `LFM2.5-8B-A1B` (3 cells) → `liquid/lfm2-5-8b-a1b` — Hub LiquidAI/LFM2.5-8B-A1B
- `Ling 2.6 Flash` (4 cells) → `inclusionai/ling-2-6-flash` — Hub inclusionAI/Ling-2.6-flash
- `Ling 3.0 Flash` (5 cells) → `inclusionai/ling-3-0-flash` — Hub inclusionAI/Ling-3.0-flash
- `Ling 3.0 Tiny` (5 cells) → `inclusionai/ling-3-0-tiny` — Hub inclusionAI/Ling-3.0-tiny
- `Ling-1T` (3 cells) → `inclusionai/ling-1t` — Hub inclusionAI/Ling-1T
- `Ling-2.6-1T` (3 cells) → `inclusionai/ling-2-6-1t` — Hub inclusionAI/Ling-2.6-1T
- `Ling-3.0-flash-VL` (5 cells) → `inclusionai/ling-3-0-flash-vl` — Hub inclusionAI/Ling-3.0-flash-VL
- `Ling-flash-2.0` (3 cells) → `inclusionai/ling-flash-2-0` — Hub inclusionAI/Ling-flash-2.0
- `Ling-mini-2.0` (2 cells) → `inclusionai/ling-mini-2-0` — Hub inclusionAI/Ling-mini-2.0
- `Llama 3.1 Nemotron 70B` (3 cells) → `nvidia/llama-3-1-nemotron-70b-instruct-hf` — Hub nvidia/Llama-3.1-Nemotron-70B-Instruct-HF
- `Llama 3.1 Nemotron Nano 4B v1.1` (2 cells) → `nvidia/llama-3-1-nemotron-nano-4b-v1-1` — Hub nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1
- `Llama Nemotron Ultra` (2 cells) → `nvidia/llama-3-1-nemotron-ultra-253b-v1` — older Llama-3.1-Nemotron-Ultra-253B line, not Nemotron 3 Ultra
- `LongCat 2.0` (5 cells) → `meituan/longcat-2-0` — Hub meituan-longcat/LongCat-2.0
- `LongCat Flash Lite` (3 cells) → `meituan/longcat-flash-lite` — Hub meituan-longcat/LongCat-Flash-Lite
- `longcat-flash-chat` (1 cells) → `meituan/longcat-flash-chat` — Hub meituan-longcat/LongCat-Flash-Chat
- `MiMo-V2-Flash` (3 cells) → `xiaomi/mimo-v2-flash` — Hub XiaomiMiMo/MiMo-V2-Flash
- `MiMo-V2.5` (5 cells) → `xiaomi/mimo-v2-5` — Hub XiaomiMiMo/MiMo-V2.5
- `mimo-v2.5` (1 cells) → `xiaomi/mimo-v2-5` — Arena slug
- `MiMo-V2.5-Pro` (5 cells) → `xiaomi/mimo-v2-5-pro` — Hub XiaomiMiMo/MiMo-V2.5-Pro
- `mimo-v2.5-pro` (1 cells) → `xiaomi/mimo-v2-5-pro` — Arena slug
- `MiniCPM-V 4.6 1.3B` (4 cells) → `openbmb/minicpm-v-4-6` — Hub openbmb/MiniCPM-V-4.6 (1.3B-class safetensors 1300428016)
- `MiniCPM5-1B` (3 cells) → `openbmb/minicpm5-1b` — Hub openbmb/MiniCPM5-1B
- `MiniCPM5-2B` (5 cells) → `openbmb/minicpm5-2b` — Hub openbmb/MiniCPM5-2B
- `MiniMax M1 40k` (1 cells) → `minimax/minimax-m1-40k` — Hub MiniMaxAI/MiniMax-M1-40k
- `MiniMax M1 80k` (3 cells) → `minimax/minimax-m1-80k` — Hub MiniMaxAI/MiniMax-M1-80k
- `Motif 3` (5 cells) → `motif/motif-3` — Hub Motif-Technologies/Motif-3
- `Motif-2-12.7B` (3 cells) → `motif/motif-2-12-7b-reasoning` — Hub Motif-Technologies/Motif-2-12.7B-Reasoning
- `Nanbeige4.1-3B` (4 cells) → `nanbeige/nanbeige4-1-3b` — Hub Nanbeige/Nanbeige4.1-3B
- `Nemotron 3 Nano 4B` (4 cells) → `nvidia/nvidia-nemotron-3-nano-4b-bf16` — Hub NVIDIA-Nemotron-3-Nano-4B-BF16
- `Nemotron 3 Nano Omni 30B A3B` (4 cells) → `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning-bf16` — BF16 reasoning; NVFP4 not carded (serving quant)
- `Nex-N2-Pro` (5 cells) → `nex-agi/nex-n2-pro` — Hub nex-agi/Nex-N2-Pro
- `Nova Lite` (3 cells) → `amazon/nova-lite` — AWS Nova docs
- `Nova Micro` (3 cells) → `amazon/nova-micro` — AWS Nova docs
- `Nova Premier` (3 cells) → `amazon/nova-premier` — AWS Nova docs
- `Nova Pro` (3 cells) → `amazon/nova-pro` — AWS Nova docs
- `OLMo 2 32B` (2 cells) → `allen-ai/olmo-2-0325-32b-instruct` — Hub allenai/OLMo-2-0325-32B-Instruct
- `Olmo 3 32B Think` (3 cells) → `allen-ai/olmo-3-32b-think` — Hub allenai/Olmo-3-32B-Think
- `Olmo 3.1 32B Think` (3 cells) → `allen-ai/olmo-3-1-32b-think` — distinct from olmo-3-1-32b-instruct
- `OpenChat 3.5` (1 cells) → `openchat/openchat-3-5-0106` — Hub openchat/openchat-3.5-0106
- `Qwen1.5 Chat 110B` (1 cells) → `qwen/qwen1-5-110b-chat` — Hub Qwen/Qwen1.5-110B-Chat
- `Qwen2 72B` (1 cells) → `qwen/qwen2-72b-instruct` — carded Instruct; unqualified 72B not aliased (base may exist)
- `Qwen3 Omni 30B A3B` (3 cells) → `qwen/qwen3-omni-30b-a3b-instruct` — Hub Qwen/Qwen3-Omni-30B-A3B-Instruct
- `Qwen3.8 2.4T A95B` (5 cells) → `qwen/qwen3-8-2-4t-a95b` — Hub Qwen/Qwen3.8-2.4T-A95B
- `Qwen3.8-Flash-Next` (5 cells) → `qwen/qwen3-8-flash-next` — Hub Qwen/Qwen3.8-Flash-Next
- `QwQ-32B` (2 cells) → `qwen/qwq-32b` — Hub Qwen/QwQ-32B
- `Reka Flash 3` (3 cells) → `reka/reka-flash-3` — Hub RekaAI/reka-flash-3
- `Ring-1T` (3 cells) → `inclusionai/ring-1t` — Hub inclusionAI/Ring-1T
- `Ring-2.6-1T` (5 cells) → `inclusionai/ring-2-6-1t` — Hub inclusionAI/Ring-2.6-1T
- `Ring-flash-2.0` (3 cells) → `inclusionai/ring-flash-2-0` — Hub inclusionAI/Ring-flash-2.0
- `Sarvam M` (3 cells) → `sarvam/sarvam-m` — Hub sarvamai/sarvam-m
- `Seed-OSS-36B-Instruct` (3 cells) → `bytedance/seed-oss-36b-instruct` — Hub ByteDance-Seed/Seed-OSS-36B-Instruct
- `Solar Open 100B` (3 cells) → `upstage/solar-open-100b` — Hub upstage/Solar-Open-100B
- `Solar Open2 250B` (5 cells) → `upstage/solar-open2-250b` — Hub upstage/Solar-Open2-250B
- `Step3 VL 10B` (3 cells) → `stepfun/step3-vl-10b` — Hub stepfun-ai/Step3-VL-10B
- `Tiny Aya Global` (3 cells) → `cohere/tiny-aya-global` — Hub CohereLabs/tiny-aya-global
- `Tri-21B-Think` (3 cells) → `trillionlabs/tri-21b-think` — Hub trillionlabs/Tri-21B-Think
- `Tulu3 405B` (1 cells) → `allen-ai/llama-3-1-tulu-3-405b` — Hub allenai/Llama-3.1-Tulu-3-405B

## could not confirm against a primary source

- `Agnes 2.5 Pro Beta` (5 cells) → `—` — Hub Agnes-AI/Agnes-2.5-Pro-Beta 401
- `Apodex 1.1` (5 cells) → `—` — only apodex/Apodex-1.1-mini is public; full 1.1 401
- `Celeris-1` (5 cells) → `—` — no Hub repo
- `Command-R (Mar)` (1 cells) → `—` — card is command-r-08-2024; March 2024 original is a different snapshot
- `Command-R+ (Apr)` (1 cells) → `—` — card is command-r-plus-08-2024; April original not uniquely mapped
- `DBRX` (1 cells) → `—` — databricks/dbrx-instruct 401; gated, no safetensors in anonymous API
- `DeepHermes 3 - Llama-3.1 8B` (1 cells) → `—` — official Hub 401; GGUF dumps exist and were not carded
- `dola-seed-2.0-pro` (1 cells) → `—` — no Hub repo
- `Doubao Seed Code` (3 cells) → `—` — ByteDance-Seed/Seed-Coder-8B-Instruct is a different 8B coder, not aliased
- `ernie-5.0-0110` (1 cells) → `—` — no Hub repo; Baidu API id not independently documented here
- `ernie-5.1` (1 cells) → `—` — no Hub repo
- `Gemini 2.5 Pro (Mar)` (1 cells) → `—` — 2.5 Pro preview cards are 05-06 and 06-05; no March card
- `Gemini 3 Flash` (3 cells) → `—` — only gemini-3-flash-preview is carded; GA vs preview not confirmed as the same weights
- `gemini-3-flash` (1 cells) → `—` — same as Gemini 3 Flash
- `GPT-4o (Mar)` (1 cells) → `—` — GPT-4o launched May 2024; no March snapshot card or Hub repo
- `Grok 4.20 0309 v2` (3 cells) → `—` — no v2 card; not the same as 0309 reasoning/non-reasoning
- `grok-4.20-beta1` (1 cells) → `—` — not identified with the 0309 reasoning/non-reasoning pair
- `hunyuan-t1-20250711` (1 cells) → `—` — no Hub repo; Tencent API snapshot
- `hunyuan-turbos-20250416` (1 cells) → `—` — no Hub repo; Tencent API snapshot
- `JT-35B-Flash` (3 cells) → `—` — no Hub repo
- `JT-4.1 Flash 236B A21B` (4 cells) → `—` — no Hub repo
- `JT-MINI` (3 cells) → `—` — no Hub repo
- `K2 Horizon 375B A23B` (5 cells) → `—` — IFM/K2-Horizon-MoVA-36B-A4B is a different size; not aliased
- `KAT-Coder-Pro V1` (4 cells) → `—` — Kwaipilot/KAT-Coder-Pro-V1 401
- `KAT-Coder-Pro V2` (4 cells) → `—` — no public Hub repo
- `LFM 40B` (1 cells) → `—` — Hub LiquidAI/LFM-40B 401
- `Magistral Small 1.2` (4 cells) → `—` — no 1.2 Hub repo found
- `Mi:dm K 2.5 Pro` (3 cells) → `—` — Midm-2.0 is a different version; 2.5 Pro not found
- `MiMo-V2-Omni` (3 cells) → `—` — Hub XiaomiMiMo/MiMo-V2-Omni 401
- `mimo-v2-omni` (1 cells) → `—` — same
- `MiMo-V2-Omni-0327` (3 cells) → `—` — dated Omni; official repo gated
- `MiMo-V2-Pro` (3 cells) → `—` — Hub XiaomiMiMo/MiMo-V2-Pro 401; not V2.5-Pro
- `mimo-v2-pro` (1 cells) → `—` — same
- `Mistral Large 2 (Jul)` (2 cells) → `—` — mistral-large-2411 is Large 2.1 Nov; July 2 not uniquely identified
- `Mistral Saba` (1 cells) → `—` — Hub mistralai/Mistral-Saba-24B 401
- `Mistral Small (Feb)` (1 cells) → `—` — several Small cards; February snapshot not unique
- `Mistral Small (Sep)` (1 cells) → `—` — September snapshot not unique
- `Muse Spark 1.3 (max)` (5 cells) → `—` — 1.3 not on Hub as a distinct repo
- `muse-spark-1.1` (1 cells) → `—` — card is unversioned Muse Spark; 1.1 not confirmed as the same weights
- `Quasar 438B (max)` (5 cells) → `—` — no Hub repo
- `Qwen2.5 Max` (1 cells) → `—` — Hub Qwen/Qwen2.5-Max is 401/gated; API-only product not independently confirmed here
- `qwen2.5-max` (1 cells) → `—` — same as Qwen2.5 Max
- `Qwen3.5 Omni Plus` (3 cells) → `—` — Hub Qwen/Qwen3.5-Omni-Plus 401; not the same as qwen3-5-plus
- `qwen3.5-flash` (1 cells) → `—` — no Qwen3.5 Flash card; not qwen3-8-flash

## Unrankable floor (the 601)

Harvest report: **601** unrankable cards. Live recount immediately before this task's new files: **604**. After the 102 new cards (all without evidence): **706**.

Unrankable is "no flat scores and no evidence". Ranking profiles cannot order those cards.

### Pre-task 604, by whether a profile can use them at all

| bucket | cards | can current profiles ever rank them? |
| --- | ---: | --- |
| image-generation / video-generation | 54 | no — Arena image/video snapshots were refused as not ranked keys; no image/video profile keys |
| audio-asr / audio-tts | 26 | no — no ASR/TTS ranked keys |
| document-ocr | 4 | no |
| llm-base | 11 | no — `llm-base` is not in any profile `preferred_types` |
| quantized-variant | 1 | no |
| **structurally unreachable under current profiles** | **96** | **no** |
| embedding-text / reranker | 26 | yes, if MTEB/BEIR evidence is attached (not this harvest) |
| safety-classifier / reward-model | 19 | yes, if HELM-safety/BBQ/ToxiGen evidence is attached (not this harvest) |
| llm-chat / llm-reasoning / llm-code / vlm | 463 | yes, if a ranked-key score exists |
| **total** | **604** | |

Of the 463 unrankable LLM/VLM cards:

- **75** have a name that appears on the AA/Arena harvest (strict slug match). Aliases, new cards, and the next attach pass can move these. This is the crawl-fixable set inside the 601.
- **388** have no row on those two boards. They become rankable only if someone runs evals or another source (Open LLM Leaderboard, papers) is attached. Crawling AA/Arena again will not find them.

Deprecated/sunset among the 604: **0** (status is widely still `active` even for old weights). Preview/alpha/beta: **25**.

### What "make every card rankable" actually means

It is not a reachable goal with the current ranking profiles and public boards.

A hard floor of **96 / 604 (~16%)** cannot be ranked no matter how completely AA and LM Arena are matched: image, video, audio, OCR, base checkpoints, and serving quants. The harvest already refused Arena's image/video snapshots because they are not ranked keys.

A practical crawl ceiling on the remaining 508 is much lower than 508:

- **~75** LLM/VLM cards are sitting on the boards we already fetched and failed to match (this task).
- **~45** embedding/safety cards need different boards (MTEB, HELM-safety), which this harvest did not take.
- **~388** LLM/VLM cards have no public row on AA or LM Arena. Matching cannot create those scores.

The 104 missing names we carded were not in the 601 (they had no card). They are new unrankable rows until `LEDGER_TO_CARD` is extended and attach runs. Many of those 104 *are* on the live boards, so they are the highest-yield follow-up after aliases.

`Llama Nemotron Ultra` (253B, Llama-3.1 line) was carded separately from `Nemotron 3 Ultra` (550B A55B). Those are different models.

