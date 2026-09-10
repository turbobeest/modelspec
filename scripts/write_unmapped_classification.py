#!/usr/bin/env python3
"""Emit the 284-name classification report. Data, not inference."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "benchmarks/_census/unmapped_name_index.json"
OUT_JSON = ROOT / "benchmarks/_census/unmapped_name_classification.json"
OUT_MD = ROOT / "benchmarks/_census/UNMAPPED_NAME_CLASSIFICATION.md"

# class: naming_drift | effort_or_serving_variant | ambiguous | missing_carded | could_not_confirm | not_a_model
# naming_drift: unique existing card, different spelling → alias
# effort_or_serving_variant: dated/effort/quant/wrapper of a carded product; do NOT alias
# ambiguous: more than one honest card; do NOT alias
# missing_carded: no card at harvest; card created this task (or 2563e7a for Cogito/Inkling)
# could_not_confirm: looks like a model; no primary source that uniquely identifies it
# not_a_model: dataset / harness / aggregate — none of the 284 are this, recorded explicitly

C = {
    # --- Claude word-order / dated snapshots that uniquely hit one card ---
    "Claude 3 Haiku": ("naming_drift", "anthropic/claude-3-haiku-20240307", "display is Claude Haiku 3; only Claude 3 Haiku card"),
    "Claude 3 Opus": ("naming_drift", "anthropic/claude-3-opus-20240229", "display is Claude Opus 3"),
    "Claude 3 Sonnet": ("naming_drift", "anthropic/claude-3-sonnet-20240229", "display is Claude Sonnet 3"),
    "Claude 3.5 Haiku": ("naming_drift", "anthropic/claude-3-5-haiku-20241022", "dated card display Claude Haiku 3.5; latest sibling has (latest)"),
    "Claude 3.5 Sonnet (June)": ("naming_drift", "anthropic/claude-3-5-sonnet-20240620", "June 2024 snapshot is 20240620"),
    "Claude 3.5 Sonnet (Oct)": ("naming_drift", "anthropic/claude-3-5-sonnet-20241022", "Oct 2024 snapshot is 20241022 / Sonnet 3.5 v2"),
    "Claude 3.7 Sonnet": ("naming_drift", "anthropic/claude-3-7-sonnet-20250219", "display is Claude Sonnet 3.7; unique"),
    "Claude 4 Opus": ("naming_drift", "anthropic/claude-opus-4-20250514", "word order of Claude Opus 4; latest sibling has (latest)"),
    "Claude 4 Sonnet": ("naming_drift", "anthropic/claude-sonnet-4-20250514", "word order of Claude Sonnet 4"),
    "Claude 4.1 Opus": ("naming_drift", "anthropic/claude-opus-4-1-20250805", "word order of Claude Opus 4.1 dated card"),
    "Claude 4.5 Haiku": ("naming_drift", "anthropic/claude-haiku-4-5-20251001", "word order of Claude Haiku 4.5 dated card"),
    "Claude 4.5 Sonnet": ("naming_drift", "anthropic/claude-sonnet-4-5-20250929", "word order of Claude Sonnet 4.5 dated card"),
    "Claude 2.0": ("missing_carded", "anthropic/claude-2-0", "closed; Anthropic 2023-07-11 announcement"),
    "Claude 2.1": ("missing_carded", "anthropic/claude-2-1", "closed; Anthropic 2023-11-21 announcement"),
    "Claude Instant": ("missing_carded", "anthropic/claude-instant-1", "closed; Anthropic Instant SKU"),
    "Claude Fable 5 (with fallback)": ("effort_or_serving_variant", "anthropic/claude-fable-5", "fallback serving of Fable 5; not the product row"),
    "Claude Fable 5.1 (max with fallback)": ("effort_or_serving_variant", "anthropic/claude-fable-5-1", "fallback serving even with max"),

    # --- Cogito / Inkling (2563e7a cards; harvest missed them) ---
    "Cogito v2.1": ("naming_drift", "deepcogito/cogito-671b-v2-1", "card display is Cogito v2.1 671B"),
    "Inkling": ("naming_drift", "thinkingmachines/inkling", "exact display after 2563e7a; harvest predates the card"),
    "inkling": ("naming_drift", "thinkingmachines/inkling", "Arena slug of Inkling"),
    "Inkling Small": ("missing_carded", "thinkingmachines/inkling-small", "Hub thinkingmachines/Inkling-Small safetensors 265956439090"),

    # --- DeepSeek ---
    "DeepSeek Coder V2 Lite": ("naming_drift", "deepseek/deepseek-coder-v2-lite-instruct", "only Lite card is Instruct"),
    "DeepSeek R1 (Jan)": ("naming_drift", "deepseek/deepseek-r1", "original R1 is the Jan 2025 row; 0528 is a later card"),
    "DeepSeek V3 (Dec)": ("naming_drift", "deepseek/deepseek-v3", "original V3 Dec 2024; 0324 is a later card"),
    "DeepSeek V3.1 Terminus": ("missing_carded", "deepseek/deepseek-v3-1-terminus", "Hub deepseek-ai/DeepSeek-V3.1-Terminus"),
    "deepseek-v3.1-terminus": ("missing_carded", "deepseek/deepseek-v3-1-terminus", "Arena slug of Terminus"),
    "DeepSeek V3.2 Speciale": ("missing_carded", "deepseek/deepseek-v3-2-speciale", "Hub deepseek-ai/DeepSeek-V3.2-Speciale"),
    "DeepSeek-V2.5 (Dec)": ("missing_carded", "deepseek/deepseek-v2-5", "Hub deepseek-ai/DeepSeek-V2.5"),
    "DeepSeek V4 Flash Vision (max)": ("effort_or_serving_variant", "deepseek/deepseek-v4-flash-vision-exp", "max row of the vision-exp card; not folded onto exp"),
    "DeepSeek V4 Pro 0813 (max)": ("effort_or_serving_variant", "deepseek/deepseek-v4-pro", "0813 is a dated checkpoint of V4 Pro"),

    # --- GPT-4o dated / ChatGPT wrapper ---
    "GPT-4o (Aug)": ("naming_drift", "openai/gpt-4o-2024-08-06", "dated card GPT-4o (2024-08-06)"),
    "GPT-4o (May)": ("naming_drift", "openai/gpt-4o-2024-05-13", "dated card GPT-4o (2024-05-13)"),
    "GPT-4o (Nov)": ("naming_drift", "openai/gpt-4o-2024-11-20", "dated card GPT-4o (2024-11-20)"),
    "GPT-4o (Mar)": ("could_not_confirm", None, "GPT-4o launched May 2024; no March snapshot card or Hub repo"),
    "GPT-4o (ChatGPT)": ("effort_or_serving_variant", "openai/gpt-4o", "ChatGPT wrapper, not the API product row"),
    "GPT-5 (ChatGPT)": ("effort_or_serving_variant", "openai/gpt-5", "ChatGPT wrapper"),
    "GPT-5 (minimal)": ("effort_or_serving_variant", "openai/gpt-5", "minimal effort; token not in EFFORT_TOKENS"),
    "GPT-5 mini (minimal)": ("effort_or_serving_variant", "openai/gpt-5-mini", "minimal effort"),
    "GPT-5 nano (minimal)": ("effort_or_serving_variant", "openai/gpt-5-nano", "minimal effort"),
    "GPT-5.5 Instant (June 2026)": ("effort_or_serving_variant", "openai/gpt-5-5", "Instant is a serving SKU of GPT-5.5"),
    "GPT-5.5 Instant (May 2026)": ("effort_or_serving_variant", "openai/gpt-5-5", "dated Instant serving"),
    "gpt-5.5-instant": ("effort_or_serving_variant", "openai/gpt-5-5", "Arena Instant SKU"),
    "gpt-5-chat": ("ambiguous", None, "gpt-5-chat-latest vs gpt-5-1/5-2 chat-latest"),
    "gpt-4.1-2025-04-14": ("naming_drift", "openai/gpt-4-1", "API snapshot id of GPT-4.1"),
    "gpt-4.1-mini-2025-04-14": ("naming_drift", "openai/gpt-4-1-mini", "API snapshot id of GPT-4.1 mini"),
    "o1-2024-12-17": ("naming_drift", "openai/o1", "API snapshot id of o1"),
    "o3-2025-04-16": ("naming_drift", "openai/o3", "API snapshot id of o3"),
    "o4-mini-2025-04-16": ("naming_drift", "openai/o4-mini", "API snapshot id of o4-mini"),

    # --- Gemini ---
    "Gemini 1.0 Pro": ("missing_carded", "google/gemini-1-0-pro", "closed; Gemini 1.0 announcement 2023-12-06"),
    "Gemini 1.5 Flash (May)": ("effort_or_serving_variant", "google/gemini-1-5-flash", "dated snapshot of the single 1.5 Flash card"),
    "Gemini 1.5 Flash (Sep)": ("effort_or_serving_variant", "google/gemini-1-5-flash", "dated snapshot of the single 1.5 Flash card"),
    "Gemini 1.5 Pro (May)": ("effort_or_serving_variant", "google/gemini-1-5-pro", "dated snapshot"),
    "Gemini 1.5 Pro (Sep)": ("effort_or_serving_variant", "google/gemini-1-5-pro", "dated snapshot"),
    "Gemini 2.0 Flash (exp)": ("effort_or_serving_variant", "google/gemini-2-0-flash", "experimental serving"),
    "gemini-2.0-flash-001": ("naming_drift", "google/gemini-2-0-flash", "GA API id of Gemini 2.0 Flash"),
    "Gemini 2.0 Flash-Lite (Feb)": ("effort_or_serving_variant", "google/gemini-2-0-flash-lite", "dated snapshot"),
    "Gemini 2.5 Flash (Apr)": ("naming_drift", "google/gemini-2-5-flash-preview-04-17", "April preview card exists"),
    "Gemini 2.5 Flash (Sep)": ("naming_drift", "google/gemini-2-5-flash-preview-09-2025", "September preview card exists"),
    "Gemini 2.5 Flash-Lite (Sep)": ("naming_drift", "google/gemini-2-5-flash-lite-preview-09-2025", "September preview card exists"),
    "Gemini 2.5 Pro (Mar)": ("could_not_confirm", None, "2.5 Pro preview cards are 05-06 and 06-05; no March card"),
    "Gemini 2.5 Pro (May)": ("naming_drift", "google/gemini-2-5-pro-preview-05-06", "May preview card"),
    "Gemini 3 Deep Think": ("effort_or_serving_variant", "google/gemini-3-pro-preview", "Deep Think is a thinking mode, not a separate product card"),
    "Gemini 3 Flash": ("could_not_confirm", None, "only gemini-3-flash-preview is carded; GA vs preview not confirmed as the same weights"),
    "gemini-3-flash": ("could_not_confirm", None, "same as Gemini 3 Flash"),
    "gemini-3-pro": ("ambiguous", None, "gemini-3-pro-preview vs gemini-3-pro-image"),
    "Gemini 3.5 Flash (minimal)": ("effort_or_serving_variant", "google/gemini-3-5-flash", "minimal effort"),

    # --- Gemma ---
    "Gemma 3 1B": ("ambiguous", None, "gemma-3-1b-it and gemma-3-1b-pt both exist"),
    "Gemma 3n E2B": ("naming_drift", "google/gemma-3n-e2b-it", "display Gemma 3n 2B; only IT card"),
    "Gemma 3n E4B": ("naming_drift", "google/gemma-3n-e4b-it", "display Gemma 3n 4B; only IT card"),
    "Gemma 3n E4B (May)": ("naming_drift", "google/gemma-3n-e4b-it", "May launch of the only E4B card"),
    "Gemma 4 12B": ("missing_carded", "google/gemma-4-12b-it", "Hub has base and IT; both carded; unqualified name stays ambiguous — no alias"),
    "Gemma 4 26B A4B": ("naming_drift", "google/gemma-4-26b-a4b-it", "only A4B card is IT"),
    "gemma-4-26b-a4b": ("naming_drift", "google/gemma-4-26b-a4b-it", "Arena slug of 26B A4B IT"),
    "Gemma 4 E2B": ("naming_drift", "google/gemma-4-e2b-it", "only E2B card is IT"),
    "Gemma 4 E4B": ("naming_drift", "google/gemma-4-e4b-it", "only E4B card is IT"),
    "DiffusionGemma 26B A4B": ("missing_carded", "google/diffusiongemma-26b-a4b-it", "Hub google/diffusiongemma-26B-A4B-it"),

    # --- Grok ---
    "Grok 4.20 0309": ("ambiguous", None, "reasoning and non-reasoning 0309 cards both exist"),
    "Grok 4.20 0309 v2": ("could_not_confirm", None, "no v2 card; not the same as 0309 reasoning/non-reasoning"),
    "Grok Build 0.1 0616": ("effort_or_serving_variant", "xai/grok-build-0-1", "dated 0616 snapshot of Grok Build 0.1"),
    "grok-3-mini-beta": ("effort_or_serving_variant", "xai/grok-3-mini", "beta serving"),
    "grok-4-0709": ("naming_drift", "xai/grok-4", "Grok 4 launch id 0709"),
    "grok-4.1": ("ambiguous", None, "grok-4-1-fast and grok-4-1-fast-non-reasoning; no plain 4.1 card"),
    "grok-4.20-beta1": ("could_not_confirm", None, "not identified with the 0309 reasoning/non-reasoning pair"),
    "grok-4.20-multi-agent-beta-0309": ("naming_drift", "xai/grok-4-20-multi-agent-0309", "beta tag on the 0309 multi-agent card"),

    # --- Qwen ---
    "Qwen1.5 Chat 110B": ("missing_carded", "qwen/qwen1-5-110b-chat", "Hub Qwen/Qwen1.5-110B-Chat"),
    "Qwen2 72B": ("missing_carded", "qwen/qwen2-72b-instruct", "carded Instruct; unqualified 72B not aliased (base may exist)"),
    "Qwen2.5 72B": ("naming_drift", "qwen/qwen2-5-72b-instruct", "only 72B card is Instruct"),
    "Qwen2.5 Coder 32B": ("naming_drift", "qwen/qwen2-5-coder-32b-instruct", "only 32B coder card is Instruct"),
    "Qwen2.5 Coder 7B": ("naming_drift", "qwen/qwen2-5-coder-7b-instruct", "only 7B coder card is Instruct"),
    "Qwen2.5 Instruct 32B": ("naming_drift", "qwen/qwen2-5-32b-instruct", "display Qwen2.5 32B Instruct"),
    "Qwen2.5 Max": ("could_not_confirm", None, "Hub Qwen/Qwen2.5-Max is 401/gated; API-only product not independently confirmed here"),
    "qwen2.5-max": ("could_not_confirm", None, "same as Qwen2.5 Max"),
    "QwQ-32B": ("missing_carded", "qwen/qwq-32b", "Hub Qwen/QwQ-32B"),
    "Qwen3 235B": ("naming_drift", "qwen/qwen3-235b-a22b", "unqualified 235B is the original A22B card"),
    "Qwen3 235B A22B 2507": ("naming_drift", "cerebras/qwen-3-235b-a22b-instruct-2507", "only 2507 instruct card is the Cerebras serving"),
    "qwen3-235b-a22b-instruct-2507": ("naming_drift", "cerebras/qwen-3-235b-a22b-instruct-2507", "exact Cerebras card slug"),
    "Qwen3 30B": ("ambiguous", None, "qwen3-30b-a3b vs instruct-2507 vs nvfp4"),
    "Qwen3 30B A3B 2507": ("naming_drift", "qwen/qwen3-30b-a3b-instruct-2507", "unique 2507 instruct card"),
    "Qwen3 4B 2507": ("ambiguous", None, "instruct-2507 and thinking-2507 both exist"),
    "Qwen3 Coder 30B A3B": ("naming_drift", "qwen/qwen3-coder-30b-a3b-instruct", "only 30B coder card is Instruct"),
    "Qwen3 Coder 480B": ("naming_drift", "qwen/qwen3-coder-480b-a35b-instruct", "only 480B coder card is Instruct"),
    "Qwen3 Next 80B A3B": ("ambiguous", None, "instruct vs thinking cards"),
    "Qwen3 Omni 30B A3B": ("missing_carded", "qwen/qwen3-omni-30b-a3b-instruct", "Hub Qwen/Qwen3-Omni-30B-A3B-Instruct"),
    "Qwen3 VL 32B": ("naming_drift", "qwen/qwen3-vl-32b-instruct", "only 32B VL card is Instruct"),
    "Qwen3 VL 4B": ("naming_drift", "qwen/qwen3-vl-4b-instruct", "only 4B VL card is Instruct"),
    "Qwen3 VL 8B": ("naming_drift", "qwen/qwen3-vl-8b-instruct", "only 8B VL card is Instruct"),
    "qwen3-vl-235b-a22b-instruct": ("naming_drift", "qwen/qwen3-vl-235b-a22b", "card display Qwen3-VL 235B-A22B"),
    "Qwen3.5 Omni Flash": ("naming_drift", "qwen/qwen3-omni-flash", "display Qwen3-Omni Flash"),
    "Qwen3.5 Omni Plus": ("could_not_confirm", None, "Hub Qwen/Qwen3.5-Omni-Plus 401; not the same as qwen3-5-plus"),
    "qwen3.5-flash": ("could_not_confirm", None, "no Qwen3.5 Flash card; not qwen3-8-flash"),
    "Qwen3.8 2.4T A95B": ("missing_carded", "qwen/qwen3-8-2-4t-a95b", "Hub Qwen/Qwen3.8-2.4T-A95B"),
    "Qwen3.8-Flash-Next": ("missing_carded", "qwen/qwen3-8-flash-next", "Hub Qwen/Qwen3.8-Flash-Next"),
    "qwen3.8-max": ("naming_drift", "qwen/qwen3-8-max", "slug qwen3-8-max vs display Qwen3.8 Max"),
    "qwen3-max-2025-09-23": ("effort_or_serving_variant", "qwen/qwen3-max", "dated snapshot of Qwen3 Max"),

    # --- Llama ---
    "Llama 2 Chat 13B": ("naming_drift", "meta/llama-2-13b-chat-hf", "chat-hf card"),
    "Llama 2 Chat 70B": ("naming_drift", "meta/llama-2-70b-chat-hf", "chat-hf card"),
    "Llama 2 Chat 7B": ("naming_drift", "meta/llama-2-7b-chat-hf", "chat-hf card"),
    "Llama 3 70B": ("ambiguous", None, "base and instruct both exist (same defect as Llama 3.1 70B refusal)"),
    "Llama 3 8B": ("ambiguous", None, "base and instruct both exist"),
    "Llama 3.3 70B": ("naming_drift", "meta/llama-3-3-70b-instruct", "only 70B 3.3 card is Instruct"),
    "Llama 4 Maverick": ("naming_drift", "meta/llama-4-maverick-17b-128e-instruct", "no base Maverick card; FP8 is a quant"),
    "Llama 4 Scout": ("ambiguous", None, "base scout-17b-16e and instruct both exist"),
    "Llama 3.1 Nemotron 70B": ("missing_carded", "nvidia/llama-3-1-nemotron-70b-instruct-hf", "Hub nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"),
    "Llama 3.1 Nemotron Nano 4B v1.1": ("missing_carded", "nvidia/llama-3-1-nemotron-nano-4b-v1-1", "Hub nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1"),
    "Llama 3.3 Nemotron Super 49B": ("naming_drift", "nvidia/llama-3-3-nemotron-super-49b-v1-5", "v1.5 is the Super 49B card"),
    "Llama Nemotron Super 49B v1.5": ("naming_drift", "nvidia/llama-3-3-nemotron-super-49b-v1-5", "same card"),
    "Llama Nemotron Ultra": ("missing_carded", "nvidia/llama-3-1-nemotron-ultra-253b-v1", "older Llama-3.1-Nemotron-Ultra-253B line, not Nemotron 3 Ultra"),

    # --- Nemotron 3.x ---
    "Nemotron 3 Nano": ("ambiguous", None, "bf16 / fp8 / nvfp4 / base-bf16 all carded"),
    "Nemotron 3 Nano 4B": ("missing_carded", "nvidia/nvidia-nemotron-3-nano-4b-bf16", "Hub NVIDIA-Nemotron-3-Nano-4B-BF16"),
    "Nemotron 3 Nano Omni 30B A3B": ("missing_carded", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning-bf16", "BF16 reasoning; NVFP4 not carded (serving quant)"),
    "Nemotron 3 Super": ("ambiguous", None, "bf16 / fp8 / nvfp4 all carded"),
    "Nemotron 3 Ultra": ("naming_drift", "nvidia/nvidia-nemotron-3-ultra-550b-a55b", "display NVIDIA Nemotron 3 Ultra"),
    "Nemotron 3.5 Lightning": ("naming_drift", "nvidia/nvidia-nemotron-3-5-lightning-30b-a3b", "display NVIDIA Nemotron 3.5 Lightning 30B A3B"),
    "NVIDIA Nemotron Nano 12B v2 VL": ("ambiguous", None, "bf16 and fp8 VL cards"),
    "nvidia-nemotron-3-super-120b-a12b": ("ambiguous", None, "bf16 / fp8 / nvfp4"),
    "nvidia-nemotron-3-ultra-550b-a55b-nvfp4": ("effort_or_serving_variant", "nvidia/nvidia-nemotron-3-ultra-550b-a55b", "NVFP4 serving dump; 2563e7a refused to card it"),
    "nvidia-nemotron-3.5-lightning-30b-a3b-nvfp4": ("effort_or_serving_variant", "nvidia/nvidia-nemotron-3-5-lightning-30b-a3b", "NVFP4 serving dump"),

    # --- Mistral ---
    "Devstral Small (May)": ("naming_drift", "mistral/devstral-small-2505", "May is 2505; display Devstral Small is the July 2507 card"),
    "Magistral Small 1": ("ambiguous", None, "magistral-small and magistral-small-2506"),
    "Magistral Small 1.2": ("could_not_confirm", None, "no 1.2 Hub repo found"),
    "Ministral 3 14B": ("naming_drift", "mistral/ministral-3-14b-instruct-2512", "only 14B card is Instruct"),
    "Ministral 3 3B": ("ambiguous", None, "base-2512 and instruct-2512 both exist"),
    "Ministral 3 8B": ("naming_drift", "mistral/ministral-3-8b-instruct-2512", "bf16 sibling is a serving dump"),
    "Mistral Large (Feb)": ("effort_or_serving_variant", "mistral/mistral-large-latest", "dated snapshot; Large 2.1/3 are other cards"),
    "Mistral Large 2 (Jul)": ("could_not_confirm", None, "mistral-large-2411 is Large 2.1 Nov; July 2 not uniquely identified"),
    "Mistral Large 2 (Nov)": ("naming_drift", "mistral/mistral-large-2411", "display Mistral Large 2.1"),
    "Mistral Saba": ("could_not_confirm", None, "Hub mistralai/Mistral-Saba-24B 401"),
    "Mistral Small (Feb)": ("could_not_confirm", None, "several Small cards; February snapshot not unique"),
    "Mistral Small (Sep)": ("could_not_confirm", None, "September snapshot not unique"),
    "Mistral Small 3": ("naming_drift", "mistral/mistral-small-24b-instruct-2501", "Small 3 is the Jan 2025 24B instruct"),
    "Mistral Small 3.1": ("naming_drift", "mistral/mistral-small-3-1-24b-instruct-2503", "display Mistral Small 3.1 24B Instruct 2503"),
    "Pixtral Large": ("naming_drift", "mistral/pixtral-large-latest", "only Pixtral Large card"),

    # --- IBM / Liquid / Upstage / Phi / Molmo ---
    "Granite 3.3 8B": ("naming_drift", "ibm/granite-3-3-8b-instruct", "display granite 3.3 8B instruct"),
    "Granite 4.1 30B": ("missing_carded", "ibm/granite-4-1-30b", "Hub ibm-granite/granite-4.1-30b"),
    "Granite 4.1 3B": ("missing_carded", "ibm/granite-4-1-3b", "Hub ibm-granite/granite-4.1-3b"),
    "Granite 4.1 8B": ("missing_carded", "ibm/granite-4-1-8b", "Hub ibm-granite/granite-4.1-8b"),
    "Granite 4.2 30B": ("missing_carded", "ibm/granite-4-2-30b", "Hub ibm-granite/granite-4.2-30b"),
    "Granite 4.2 3B": ("missing_carded", "ibm/granite-4-2-3b", "Hub ibm-granite/granite-4.2-3b"),
    "Granite 4.2 8B": ("missing_carded", "ibm/granite-4-2-8b", "Hub ibm-granite/granite-4.2-8b"),
    "LFM 40B": ("could_not_confirm", None, "Hub LiquidAI/LFM-40B 401"),
    "LFM2 1.2B": ("missing_carded", "liquid/lfm2-1-2b", "Hub LiquidAI/LFM2-1.2B"),
    "LFM2 2.6B": ("missing_carded", "liquid/lfm2-2-6b", "Hub LiquidAI/LFM2-2.6B"),
    "LFM2 24B A2B": ("missing_carded", "liquid/lfm2-24b-a2b", "non-GGUF Hub repo; GGUF card already existed"),
    "LFM2.5-2.6B": ("missing_carded", "liquid/lfm2-5-2-6b", "Hub LiquidAI/LFM2.5-2.6B"),
    "LFM2.5-8B-A1B": ("missing_carded", "liquid/lfm2-5-8b-a1b", "Hub LiquidAI/LFM2.5-8B-A1B"),
    "Solar Open 100B": ("missing_carded", "upstage/solar-open-100b", "Hub upstage/Solar-Open-100B"),
    "Solar Open2 250B": ("missing_carded", "upstage/solar-open2-250b", "Hub upstage/Solar-Open2-250B"),
    "Solar Pro 2": ("naming_drift", "upstage/solar-pro2", "display solar-pro2"),
    "Solar Pro 3": ("naming_drift", "upstage/solar-pro3", "display solar-pro3"),
    "Phi-3 Mini": ("ambiguous", None, "4k and 128k instruct cards"),
    "Phi-4 Mini": ("naming_drift", "microsoft/phi-4-mini-instruct", "only Mini card is Instruct"),
    "Phi-4 Multimodal": ("naming_drift", "microsoft/phi-4-multimodal-instruct", "only multimodal card is Instruct"),
    "Molmo 7B-D": ("naming_drift", "allen-ai/molmo-7b-d-0924", "display Molmo 7B D 0924"),

    # --- Jamba / Command / Hermes / Olmo ---
    "Jamba 1.5 Large": ("naming_drift", "ai21/ai21-jamba-large-1-5", "display AI21 Jamba Large 1.5"),
    "Jamba 1.5 Mini": ("naming_drift", "ai21/ai21-jamba-mini-1-5", "display AI21 Jamba Mini 1.5"),
    "Jamba 1.6 Large": ("naming_drift", "ai21/ai21-jamba-large-1-6", "display AI21 Jamba Large 1.6"),
    "Jamba 1.6 Mini": ("naming_drift", "ai21/ai21-jamba-mini-1-6", "display AI21 Jamba Mini 1.6"),
    "Jamba 1.7 Large": ("missing_carded", "ai21/ai21-jamba-large-1-7", "Hub ai21labs/AI21-Jamba-Large-1.7"),
    "Jamba 1.7 Mini": ("naming_drift", "ai21/ai21-jamba-mini-1-7", "display AI21 Jamba Mini 1.7"),
    "Command-R (Mar)": ("could_not_confirm", None, "card is command-r-08-2024; March 2024 original is a different snapshot"),
    "Command-R+ (Apr)": ("could_not_confirm", None, "card is command-r-plus-08-2024; April original not uniquely mapped"),
    "Hermes 3 - Llama-3.1 70B": ("missing_carded", "nous-research/hermes-3-llama-3-1-70b", "Hub NousResearch/Hermes-3-Llama-3.1-70B"),
    "DeepHermes 3 - Llama-3.1 8B": ("could_not_confirm", None, "official Hub 401; GGUF dumps exist and were not carded"),
    "DeepHermes 3 - Mistral 24B": ("missing_carded", "nous-research/deephermes-3-mistral-24b-preview", "Hub NousResearch/DeepHermes-3-Mistral-24B-Preview"),
    "Hermes 4 405B": ("missing_carded", "nous-research/hermes-4-405b", "Hub NousResearch/Hermes-4-405B"),
    "Hermes 4 70B": ("missing_carded", "nous-research/hermes-4-70b", "official BF16; existing card is FP8 only"),
    "OLMo 2 32B": ("missing_carded", "allen-ai/olmo-2-0325-32b-instruct", "Hub allenai/OLMo-2-0325-32B-Instruct"),
    "OLMo 2 7B": ("ambiguous", None, "olmo-2-1124-7b base already existed; instruct now carded too"),
    "Olmo 3 32B Think": ("missing_carded", "allen-ai/olmo-3-32b-think", "Hub allenai/Olmo-3-32B-Think"),
    "Olmo 3 7B": ("ambiguous", None, "instruct, instruct-sft, think, 1025-7b"),
    "Olmo 3.1 32B Think": ("missing_carded", "allen-ai/olmo-3-1-32b-think", "distinct from olmo-3-1-32b-instruct"),
    "Tulu3 405B": ("missing_carded", "allen-ai/llama-3-1-tulu-3-405b", "Hub allenai/Llama-3.1-Tulu-3-405B"),
    "OpenChat 3.5": ("missing_carded", "openchat/openchat-3-5-0106", "Hub openchat/openchat-3.5-0106"),

    # --- Muse / MiniMax / MiniCPM / MiMo ---
    "muse-glimmer": ("naming_drift", "meta/muse-glimmer-30b", "display Muse Glimmer 30B"),
    "muse-spark-1.1": ("could_not_confirm", None, "card is unversioned Muse Spark; 1.1 not confirmed as the same weights"),
    "Muse Spark 1.3 (max)": ("could_not_confirm", None, "1.3 not on Hub as a distinct repo"),
    "MiniMax M1 40k": ("missing_carded", "minimax/minimax-m1-40k", "Hub MiniMaxAI/MiniMax-M1-40k"),
    "MiniMax M1 80k": ("missing_carded", "minimax/minimax-m1-80k", "Hub MiniMaxAI/MiniMax-M1-80k"),
    "minimax-m1": ("ambiguous", None, "40k and 80k both now carded"),
    "MiniCPM-V 4.6 1.3B": ("missing_carded", "openbmb/minicpm-v-4-6", "Hub openbmb/MiniCPM-V-4.6 (1.3B-class safetensors 1300428016)"),
    "MiniCPM5-1B": ("missing_carded", "openbmb/minicpm5-1b", "Hub openbmb/MiniCPM5-1B"),
    "MiniCPM5-2B": ("missing_carded", "openbmb/minicpm5-2b", "Hub openbmb/MiniCPM5-2B"),
    "MiMo-V2-Flash": ("missing_carded", "xiaomi/mimo-v2-flash", "Hub XiaomiMiMo/MiMo-V2-Flash"),
    "MiMo-V2-Flash (Feb 2026)": ("effort_or_serving_variant", "xiaomi/mimo-v2-flash", "dated snapshot of Flash"),
    "MiMo-V2-Omni": ("could_not_confirm", None, "Hub XiaomiMiMo/MiMo-V2-Omni 401"),
    "mimo-v2-omni": ("could_not_confirm", None, "same"),
    "MiMo-V2-Omni-0327": ("could_not_confirm", None, "dated Omni; official repo gated"),
    "MiMo-V2-Pro": ("could_not_confirm", None, "Hub XiaomiMiMo/MiMo-V2-Pro 401; not V2.5-Pro"),
    "mimo-v2-pro": ("could_not_confirm", None, "same"),
    "MiMo-V2.5": ("missing_carded", "xiaomi/mimo-v2-5", "Hub XiaomiMiMo/MiMo-V2.5"),
    "mimo-v2.5": ("missing_carded", "xiaomi/mimo-v2-5", "Arena slug"),
    "MiMo-V2.5-Pro": ("missing_carded", "xiaomi/mimo-v2-5-pro", "Hub XiaomiMiMo/MiMo-V2.5-Pro"),
    "mimo-v2.5-pro": ("missing_carded", "xiaomi/mimo-v2-5-pro", "Arena slug"),

    # --- Ling / Ring / LongCat / EXAONE / Apertus / Apriel ---
    "Ling-1T": ("missing_carded", "inclusionai/ling-1t", "Hub inclusionAI/Ling-1T"),
    "Ling-flash-2.0": ("missing_carded", "inclusionai/ling-flash-2-0", "Hub inclusionAI/Ling-flash-2.0"),
    "Ling-mini-2.0": ("missing_carded", "inclusionai/ling-mini-2-0", "Hub inclusionAI/Ling-mini-2.0"),
    "Ling-2.6-1T": ("missing_carded", "inclusionai/ling-2-6-1t", "Hub inclusionAI/Ling-2.6-1T"),
    "Ling 2.6 Flash": ("missing_carded", "inclusionai/ling-2-6-flash", "Hub inclusionAI/Ling-2.6-flash"),
    "Ling 3.0 Flash": ("missing_carded", "inclusionai/ling-3-0-flash", "Hub inclusionAI/Ling-3.0-flash"),
    "Ling 3.0 Tiny": ("missing_carded", "inclusionai/ling-3-0-tiny", "Hub inclusionAI/Ling-3.0-tiny"),
    "Ling-3.0-flash-VL": ("missing_carded", "inclusionai/ling-3-0-flash-vl", "Hub inclusionAI/Ling-3.0-flash-VL"),
    "Ring-1T": ("missing_carded", "inclusionai/ring-1t", "Hub inclusionAI/Ring-1T"),
    "Ring-flash-2.0": ("missing_carded", "inclusionai/ring-flash-2-0", "Hub inclusionAI/Ring-flash-2.0"),
    "Ring-2.6-1T": ("missing_carded", "inclusionai/ring-2-6-1t", "Hub inclusionAI/Ring-2.6-1T"),
    "LongCat 2.0": ("missing_carded", "meituan/longcat-2-0", "Hub meituan-longcat/LongCat-2.0"),
    "LongCat Flash Lite": ("missing_carded", "meituan/longcat-flash-lite", "Hub meituan-longcat/LongCat-Flash-Lite"),
    "longcat-flash-chat": ("missing_carded", "meituan/longcat-flash-chat", "Hub meituan-longcat/LongCat-Flash-Chat"),
    "longcat-flash-chat-2602-exp": ("effort_or_serving_variant", "meituan/longcat-flash-chat", "experimental dated serving; Hub 401"),
    "EXAONE 4.0 32B": ("missing_carded", "lgai-exaone/exaone-4-0-32b", "Hub LGAI-EXAONE/EXAONE-4.0-32B"),
    "Exaone 4.0 1.2B": ("missing_carded", "lgai-exaone/exaone-4-0-1-2b", "Hub LGAI-EXAONE/EXAONE-4.0-1.2B"),
    "EXAONE 4.5 33B": ("missing_carded", "lgai-exaone/exaone-4-5-33b", "Hub LGAI-EXAONE/EXAONE-4.5-33B"),
    "K-EXAONE": ("missing_carded", "lgai-exaone/k-exaone-236b-a23b", "Hub LGAI-EXAONE/K-EXAONE-236B-A23B"),
    "K-EXAONE 2.0": ("missing_carded", "lgai-exaone/k-exaone-2-0-750b-a37b", "Hub LGAI-EXAONE/K-EXAONE-2.0-750B-A37B"),
    "Apertus 70B Instruct": ("missing_carded", "swiss-ai/apertus-70b-instruct-2509", "Hub swiss-ai/Apertus-70B-Instruct-2509"),
    "Apertus 8B Instruct": ("missing_carded", "swiss-ai/apertus-8b-instruct-2509", "Hub swiss-ai/Apertus-8B-Instruct-2509"),
    "Apriel-v1.5-15B-Thinker": ("missing_carded", "servicenow/apriel-1-5-15b-thinker", "Hub ServiceNow-AI/Apriel-1.5-15b-Thinker"),
    "Apriel-v1.6-15B-Thinker": ("missing_carded", "servicenow/apriel-1-6-15b-thinker", "Hub ServiceNow-AI/Apriel-1.6-15b-Thinker"),
    "A.X-K2": ("missing_carded", "skt/a-x-k2", "Hub skt/A.X-K2"),
    "INTELLECT-3": ("missing_carded", "primeintellect/intellect-3", "Hub PrimeIntellect/INTELLECT-3"),
    "intellect-3": ("missing_carded", "primeintellect/intellect-3", "Arena slug"),
    "Kimi Linear 48B A3B Instruct": ("missing_carded", "moonshot/kimi-linear-48b-a3b-instruct", "Hub moonshotai/Kimi-Linear-48B-A3B-Instruct"),
    "Kimi K2": ("ambiguous", None, "kimi-k2-0711-preview and kimi-k2-0905-preview"),
    "kimi-k2.5-instant": ("effort_or_serving_variant", "moonshot/kimi-k2-5", "Instant serving of K2.5"),
    "Seed-OSS-36B-Instruct": ("missing_carded", "bytedance/seed-oss-36b-instruct", "Hub ByteDance-Seed/Seed-OSS-36B-Instruct"),
    "Reka Flash 3": ("missing_carded", "reka/reka-flash-3", "Hub RekaAI/reka-flash-3"),
    "Sarvam M": ("missing_carded", "sarvam/sarvam-m", "Hub sarvamai/sarvam-m"),
    "Step3 VL 10B": ("missing_carded", "stepfun/step3-vl-10b", "Hub stepfun-ai/Step3-VL-10B"),
    "Tiny Aya Global": ("missing_carded", "cohere/tiny-aya-global", "Hub CohereLabs/tiny-aya-global"),
    "Tri-21B-Think": ("missing_carded", "trillionlabs/tri-21b-think", "Hub trillionlabs/Tri-21B-Think"),
    "HyperCLOVA X SEED Think (32B)": ("missing_carded", "naver/hyperclovax-seed-think-32b", "Hub naver-hyperclovax/HyperCLOVAX-SEED-Think-32B"),
    "ERNIE 4.5 300B A47B": ("missing_carded", "baidu/ernie-4-5-300b-a47b-pt", "Hub baidu/ERNIE-4.5-300B-A47B-PT"),
    "Nanbeige4.1-3B": ("missing_carded", "nanbeige/nanbeige4-1-3b", "Hub Nanbeige/Nanbeige4.1-3B"),
    "Motif-2-12.7B": ("missing_carded", "motif/motif-2-12-7b-reasoning", "Hub Motif-Technologies/Motif-2-12.7B-Reasoning"),
    "Motif 3": ("missing_carded", "motif/motif-3", "Hub Motif-Technologies/Motif-3"),
    "Motif 3 (Beta)": ("effort_or_serving_variant", "motif/motif-3", "beta serving of Motif 3"),
    "Nex-N2-Pro": ("missing_carded", "nex-agi/nex-n2-pro", "Hub nex-agi/Nex-N2-Pro"),
    "K2 Think V2": ("missing_carded", "ifm/k2-think-v2", "Hub IFM/K2-Think-V2"),
    "Agnes 2.5 Pro Alpha": ("missing_carded", "agnes-ai/agnes-2-5-pro-alpha", "Hub Agnes-AI/Agnes-2.5-Pro-Alpha"),
    "Agnes 2.5 Pro Beta": ("could_not_confirm", None, "Hub Agnes-AI/Agnes-2.5-Pro-Beta 401"),
    "G9v3-39A5B": ("missing_carded", "ai9stars/g9v3-39a5b", "Hub ai9stars/G9v3-39A5B"),
    "G9v3-3B": ("missing_carded", "ai9stars/g9v3-3b", "Hub ai9stars/G9v3-3B"),
    "Hy3": ("missing_carded", "tencent/hy3", "Hub tencent/Hy3"),
    "hy3": ("missing_carded", "tencent/hy3", "Arena slug"),

    # --- Amazon Nova ---
    "Nova Lite": ("missing_carded", "amazon/nova-lite", "AWS Nova docs"),
    "Nova Micro": ("missing_carded", "amazon/nova-micro", "AWS Nova docs"),
    "Nova Premier": ("missing_carded", "amazon/nova-premier", "AWS Nova docs"),
    "Nova Pro": ("missing_carded", "amazon/nova-pro", "AWS Nova docs"),

    # --- unconfirmed / anonymous / gated ---
    "Apodex 1.1": ("could_not_confirm", None, "only apodex/Apodex-1.1-mini is public; full 1.1 401"),
    "Celeris-1": ("could_not_confirm", None, "no Hub repo"),
    "DBRX": ("could_not_confirm", None, "databricks/dbrx-instruct 401; gated, no safetensors in anonymous API"),
    "Doubao Seed Code": ("could_not_confirm", None, "ByteDance-Seed/Seed-Coder-8B-Instruct is a different 8B coder, not aliased"),
    "dola-seed-2.0-pro": ("could_not_confirm", None, "no Hub repo"),
    "ernie-5.0-0110": ("could_not_confirm", None, "no Hub repo; Baidu API id not independently documented here"),
    "ernie-5.1": ("could_not_confirm", None, "no Hub repo"),
    "hunyuan-t1-20250711": ("could_not_confirm", None, "no Hub repo; Tencent API snapshot"),
    "hunyuan-turbos-20250416": ("could_not_confirm", None, "no Hub repo; Tencent API snapshot"),
    "JT-35B-Flash": ("could_not_confirm", None, "no Hub repo"),
    "JT-4.1 Flash 236B A21B": ("could_not_confirm", None, "no Hub repo"),
    "JT-MINI": ("could_not_confirm", None, "no Hub repo"),
    "K2 Horizon 375B A23B": ("could_not_confirm", None, "IFM/K2-Horizon-MoVA-36B-A4B is a different size; not aliased"),
    "KAT-Coder-Pro V1": ("could_not_confirm", None, "Kwaipilot/KAT-Coder-Pro-V1 401"),
    "KAT-Coder-Pro V2": ("could_not_confirm", None, "no public Hub repo"),
    "Mi:dm K 2.5 Pro": ("could_not_confirm", None, "Midm-2.0 is a different version; 2.5 Pro not found"),
    "Quasar 438B (max)": ("could_not_confirm", None, "no Hub repo"),
}


def main() -> None:
    index = json.loads(INDEX.read_text())
    names = {row["name"]: row["cells"] for row in index["names"]}
    missing_from_c = sorted(set(names) - set(C))
    extra_in_c = sorted(set(C) - set(names))
    if missing_from_c or extra_in_c:
        print("MISSING IN C", missing_from_c)
        print("EXTRA IN C", extra_in_c)
        raise SystemExit("classification does not cover the 284 names exactly")

    by_class: dict[str, list] = defaultdict(list)
    for name, (cls, card, evidence) in C.items():
        by_class[cls].append(
            {
                "name": name,
                "cells": names[name],
                "card": card,
                "evidence": evidence,
            }
        )
    for cls in by_class:
        by_class[cls].sort(key=lambda r: r["name"].lower())

    aliases = [
        {"leaderboard_name": r["name"], "model_id": r["card"], "evidence": r["evidence"]}
        for r in by_class["naming_drift"]
        if r["card"]
    ]

    payload = {
        "unique_names": len(names),
        "cells": sum(names.values()),
        "counts": {cls: len(rows) for cls, rows in sorted(by_class.items())},
        "cells_by_class": {
            cls: sum(r["cells"] for r in rows) for cls, rows in sorted(by_class.items())
        },
        "classes": dict(by_class),
        "aliases_for_LEDGER_TO_CARD": aliases,
        "notes": {
            "LEDGER_TO_CARD_location": "scripts/attach_evidence.py — not edited this task",
            "wrong_alias_is_worse_than_refusal": True,
            "not_a_model": 0,
            "gemma_4_12b": "both base and IT carded; unqualified leaderboard name must stay unmapped",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Unmatched leaderboard names (284)")
    lines.append("")
    lines.append("Classification of `refusals.unmapped_name` from the 2026-09-10 AA + LM Arena harvest.")
    lines.append("Mapping is explicit. A wrong alias is worse than a refusal.")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append("| class | names | scored cells |")
    lines.append("| --- | ---: | ---: |")
    labels = {
        "naming_drift": "naming drift (unique existing card, different spelling)",
        "effort_or_serving_variant": "effort / serving / dated / quant variant of a carded model",
        "ambiguous": "ambiguous (more than one honest card)",
        "missing_carded": "genuinely missing; card created",
        "could_not_confirm": "could not confirm against a primary source",
        "not_a_model": "not a model (dataset / harness / aggregate)",
    }
    for cls in (
        "naming_drift",
        "effort_or_serving_variant",
        "ambiguous",
        "missing_carded",
        "could_not_confirm",
        "not_a_model",
    ):
        n = payload["counts"].get(cls, 0)
        c = payload["cells_by_class"].get(cls, 0)
        lines.append(f"| {labels[cls]} | {n} | {c} |")
    lines.append(f"| **total** | **{payload['unique_names']}** | **{payload['cells']}** |")
    lines.append("")
    lines.append("None of the 284 is a dataset, harness, or aggregate row. Leaderboard harvests are model rows;")
    lines.append("`rnj-1-base-evals` was a census candidate, not in this 284.")
    lines.append("")
    lines.append("## Aliases for `LEDGER_TO_CARD`")
    lines.append("")
    lines.append("`scripts/attach_evidence.py` is owned by another agent and was not edited.")
    lines.append("These are unique spelling matches only. Effort rows and ambiguous names are absent.")
    lines.append("")
    lines.append("```python")
    for a in aliases:
        lines.append(f'    {a["leaderboard_name"]!r}: {a["model_id"]!r},')
    lines.append("```")
    lines.append("")
    for cls in (
        "naming_drift",
        "effort_or_serving_variant",
        "ambiguous",
        "missing_carded",
        "could_not_confirm",
    ):
        lines.append(f"## {labels[cls]}")
        lines.append("")
        for r in by_class[cls]:
            card = r["card"] or "—"
            lines.append(f"- `{r['name']}` ({r['cells']} cells) → `{card}` — {r['evidence']}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", OUT_JSON)
    print("wrote", OUT_MD)
    print("counts", payload["counts"])


if __name__ == "__main__":
    main()
