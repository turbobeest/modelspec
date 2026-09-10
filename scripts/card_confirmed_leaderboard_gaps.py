#!/usr/bin/env python3
"""Create model cards for Hub-confirmed leaderboard names with no catalogue card.

Sourced fields only: Hub safetensors total, config.json geometry, license,
pipeline tag, dates. No benchmark evidence. Existing cards are never overwritten.

    .venv/bin/python scripts/card_confirmed_leaderboard_gaps.py
"""
from __future__ import annotations

import os
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import (  # noqa: E402
    Adoption,
    Architecture,
    Availability,
    Deployment,
    Identity,
    Licensing,
    Lineage,
    Modalities,
    ModelCard,
    PlatformEntry,
    PrimaryProvider,
    Runtimes,
    Sources,
    TextDetail,
    VisionDetail,
    ImageGenDetail,
)
from schema.enums import (  # noqa: E402
    ArchitectureType,
    AttentionType,
    BaseModelRelation,
    LicenseType,
    ModelStatus,
    ModelType,
    Modality,
    OrgType,
    PositionalEncoding,
)
from scripts.fetch_geometry import (  # noqa: E402
    NON_UNIFORM_KEYS,
    extract_geometry,
    fetch_config,
)
from scripts.fetch_total_parameters import extract_safetensors_total  # noqa: E402
from scripts.seed_huggingface import (  # noqa: E402
    LICENSE_MAP,
    write_card_yaml,
)

TODAY = date.today().isoformat()
MODELS_DIR = PROJECT_ROOT / "models"
HF_API = "https://huggingface.co/api/models/{repo_id}"

# (hf_repo, model_id, display_name, provider, provider_display, family, country, org_type)
SPECS: list[tuple[str, str, str, str, str, str, str, str]] = [
    ("swiss-ai/Apertus-70B-Instruct-2509", "swiss-ai/apertus-70b-instruct-2509", "Apertus 70B Instruct", "swiss-ai", "Swiss AI", "apertus", "CH", "academic"),
    ("swiss-ai/Apertus-8B-Instruct-2509", "swiss-ai/apertus-8b-instruct-2509", "Apertus 8B Instruct", "swiss-ai", "Swiss AI", "apertus", "CH", "academic"),
    ("ServiceNow-AI/Apriel-1.5-15b-Thinker", "servicenow/apriel-1-5-15b-thinker", "Apriel-v1.5-15B-Thinker", "servicenow", "ServiceNow", "apriel", "US", "private"),
    ("ServiceNow-AI/Apriel-1.6-15b-Thinker", "servicenow/apriel-1-6-15b-thinker", "Apriel-v1.6-15B-Thinker", "servicenow", "ServiceNow", "apriel", "US", "private"),
    ("LGAI-EXAONE/EXAONE-4.0-32B", "lgai-exaone/exaone-4-0-32b", "EXAONE 4.0 32B", "lgai-exaone", "LG AI Research", "exaone", "KR", "private"),
    ("LGAI-EXAONE/EXAONE-4.0-1.2B", "lgai-exaone/exaone-4-0-1-2b", "EXAONE 4.0 1.2B", "lgai-exaone", "LG AI Research", "exaone", "KR", "private"),
    ("LGAI-EXAONE/EXAONE-4.5-33B", "lgai-exaone/exaone-4-5-33b", "EXAONE 4.5 33B", "lgai-exaone", "LG AI Research", "exaone", "KR", "private"),
    ("LGAI-EXAONE/K-EXAONE-236B-A23B", "lgai-exaone/k-exaone-236b-a23b", "K-EXAONE", "lgai-exaone", "LG AI Research", "k-exaone", "KR", "private"),
    ("LGAI-EXAONE/K-EXAONE-2.0-750B-A37B", "lgai-exaone/k-exaone-2-0-750b-a37b", "K-EXAONE 2.0", "lgai-exaone", "LG AI Research", "k-exaone", "KR", "private"),
    ("PrimeIntellect/INTELLECT-3", "primeintellect/intellect-3", "INTELLECT-3", "primeintellect", "Prime Intellect", "intellect", "US", "private"),
    ("moonshotai/Kimi-Linear-48B-A3B-Instruct", "moonshot/kimi-linear-48b-a3b-instruct", "Kimi Linear 48B A3B Instruct", "moonshot", "Moonshot AI", "kimi", "CN", "private"),
    ("inclusionAI/Ling-1T", "inclusionai/ling-1t", "Ling-1T", "inclusionai", "inclusionAI", "ling", "CN", "private"),
    ("inclusionAI/Ling-flash-2.0", "inclusionai/ling-flash-2-0", "Ling-flash-2.0", "inclusionai", "inclusionAI", "ling", "CN", "private"),
    ("inclusionAI/Ling-mini-2.0", "inclusionai/ling-mini-2-0", "Ling-mini-2.0", "inclusionai", "inclusionAI", "ling", "CN", "private"),
    ("inclusionAI/Ling-2.6-1T", "inclusionai/ling-2-6-1t", "Ling-2.6-1T", "inclusionai", "inclusionAI", "ling", "CN", "private"),
    ("inclusionAI/Ling-2.6-flash", "inclusionai/ling-2-6-flash", "Ling 2.6 Flash", "inclusionai", "inclusionAI", "ling", "CN", "private"),
    ("inclusionAI/Ling-3.0-flash", "inclusionai/ling-3-0-flash", "Ling 3.0 Flash", "inclusionai", "inclusionAI", "ling", "CN", "private"),
    ("inclusionAI/Ling-3.0-tiny", "inclusionai/ling-3-0-tiny", "Ling 3.0 Tiny", "inclusionai", "inclusionAI", "ling", "CN", "private"),
    ("inclusionAI/Ling-3.0-flash-VL", "inclusionai/ling-3-0-flash-vl", "Ling-3.0-flash-VL", "inclusionai", "inclusionAI", "ling", "CN", "private"),
    ("inclusionAI/Ring-1T", "inclusionai/ring-1t", "Ring-1T", "inclusionai", "inclusionAI", "ring", "CN", "private"),
    ("inclusionAI/Ring-flash-2.0", "inclusionai/ring-flash-2-0", "Ring-flash-2.0", "inclusionai", "inclusionAI", "ring", "CN", "private"),
    ("inclusionAI/Ring-2.6-1T", "inclusionai/ring-2-6-1t", "Ring-2.6-1T", "inclusionai", "inclusionAI", "ring", "CN", "private"),
    ("ByteDance-Seed/Seed-OSS-36B-Instruct", "bytedance/seed-oss-36b-instruct", "Seed-OSS-36B-Instruct", "bytedance", "ByteDance Seed", "seed", "CN", "private"),
    ("upstage/Solar-Open-100B", "upstage/solar-open-100b", "Solar Open 100B", "upstage", "Upstage", "solar", "KR", "private"),
    ("upstage/Solar-Open2-250B", "upstage/solar-open2-250b", "Solar Open2 250B", "upstage", "Upstage", "solar", "KR", "private"),
    ("Qwen/QwQ-32B", "qwen/qwq-32b", "QwQ-32B", "qwen", "Alibaba Cloud", "qwq", "CN", "private"),
    ("Qwen/Qwen1.5-110B-Chat", "qwen/qwen1-5-110b-chat", "Qwen1.5 Chat 110B", "qwen", "Alibaba Cloud", "qwen", "CN", "private"),
    ("Qwen/Qwen2-72B-Instruct", "qwen/qwen2-72b-instruct", "Qwen2 72B Instruct", "qwen", "Alibaba Cloud", "qwen", "CN", "private"),
    ("Qwen/Qwen3-Omni-30B-A3B-Instruct", "qwen/qwen3-omni-30b-a3b-instruct", "Qwen3 Omni 30B A3B Instruct", "qwen", "Alibaba Cloud", "qwen3-omni", "CN", "private"),
    ("Qwen/Qwen3.8-2.4T-A95B", "qwen/qwen3-8-2-4t-a95b", "Qwen3.8 2.4T A95B", "qwen", "Alibaba Cloud", "qwen3", "CN", "private"),
    ("Qwen/Qwen3.8-Flash-Next", "qwen/qwen3-8-flash-next", "Qwen3.8-Flash-Next", "qwen", "Alibaba Cloud", "qwen3", "CN", "private"),
    ("allenai/OLMo-2-0325-32B-Instruct", "allen-ai/olmo-2-0325-32b-instruct", "OLMo 2 32B Instruct", "allen-ai", "Allen Institute for AI", "olmo", "US", "nonprofit"),
    ("allenai/Olmo-3-32B-Think", "allen-ai/olmo-3-32b-think", "Olmo 3 32B Think", "allen-ai", "Allen Institute for AI", "olmo", "US", "nonprofit"),
    ("allenai/Olmo-3.1-32B-Think", "allen-ai/olmo-3-1-32b-think", "Olmo 3.1 32B Think", "allen-ai", "Allen Institute for AI", "olmo", "US", "nonprofit"),
    ("allenai/Llama-3.1-Tulu-3-405B", "allen-ai/llama-3-1-tulu-3-405b", "Tulu3 405B", "allen-ai", "Allen Institute for AI", "tulu", "US", "nonprofit"),
    ("NousResearch/Hermes-4-70B", "nous-research/hermes-4-70b", "Hermes 4 70B", "nous-research", "Nous Research", "hermes", "US", "private"),
    ("NousResearch/Hermes-4-405B", "nous-research/hermes-4-405b", "Hermes 4 405B", "nous-research", "Nous Research", "hermes", "US", "private"),
    ("NousResearch/Hermes-3-Llama-3.1-70B", "nous-research/hermes-3-llama-3-1-70b", "Hermes 3 Llama 3.1 70B", "nous-research", "Nous Research", "hermes", "US", "private"),
    ("NousResearch/DeepHermes-3-Mistral-24B-Preview", "nous-research/deephermes-3-mistral-24b-preview", "DeepHermes 3 Mistral 24B", "nous-research", "Nous Research", "deephermes", "US", "private"),
    ("ibm-granite/granite-4.1-3b", "ibm/granite-4-1-3b", "Granite 4.1 3B", "ibm", "IBM", "granite", "US", "private"),
    ("ibm-granite/granite-4.1-8b", "ibm/granite-4-1-8b", "Granite 4.1 8B", "ibm", "IBM", "granite", "US", "private"),
    ("ibm-granite/granite-4.1-30b", "ibm/granite-4-1-30b", "Granite 4.1 30B", "ibm", "IBM", "granite", "US", "private"),
    ("ibm-granite/granite-4.2-3b", "ibm/granite-4-2-3b", "Granite 4.2 3B", "ibm", "IBM", "granite", "US", "private"),
    ("ibm-granite/granite-4.2-8b", "ibm/granite-4-2-8b", "Granite 4.2 8B", "ibm", "IBM", "granite", "US", "private"),
    ("ibm-granite/granite-4.2-30b", "ibm/granite-4-2-30b", "Granite 4.2 30B", "ibm", "IBM", "granite", "US", "private"),
    ("LiquidAI/LFM2-1.2B", "liquid/lfm2-1-2b", "LFM2 1.2B", "liquid", "Liquid AI", "lfm2", "US", "private"),
    ("LiquidAI/LFM2-2.6B", "liquid/lfm2-2-6b", "LFM2 2.6B", "liquid", "Liquid AI", "lfm2", "US", "private"),
    ("LiquidAI/LFM2-24B-A2B", "liquid/lfm2-24b-a2b", "LFM2 24B A2B", "liquid", "Liquid AI", "lfm2", "US", "private"),
    ("LiquidAI/LFM2.5-2.6B", "liquid/lfm2-5-2-6b", "LFM2.5-2.6B", "liquid", "Liquid AI", "lfm2", "US", "private"),
    ("LiquidAI/LFM2.5-8B-A1B", "liquid/lfm2-5-8b-a1b", "LFM2.5-8B-A1B", "liquid", "Liquid AI", "lfm2", "US", "private"),
    ("XiaomiMiMo/MiMo-V2-Flash", "xiaomi/mimo-v2-flash", "MiMo-V2-Flash", "xiaomi", "Xiaomi", "mimo", "CN", "private"),
    ("XiaomiMiMo/MiMo-V2.5", "xiaomi/mimo-v2-5", "MiMo-V2.5", "xiaomi", "Xiaomi", "mimo", "CN", "private"),
    ("XiaomiMiMo/MiMo-V2.5-Pro", "xiaomi/mimo-v2-5-pro", "MiMo-V2.5-Pro", "xiaomi", "Xiaomi", "mimo", "CN", "private"),
    ("openbmb/MiniCPM-V-4.6", "openbmb/minicpm-v-4-6", "MiniCPM-V 4.6", "openbmb", "OpenBMB", "minicpm", "CN", "private"),
    ("openbmb/MiniCPM5-1B", "openbmb/minicpm5-1b", "MiniCPM5-1B", "openbmb", "OpenBMB", "minicpm", "CN", "private"),
    ("openbmb/MiniCPM5-2B", "openbmb/minicpm5-2b", "MiniCPM5-2B", "openbmb", "OpenBMB", "minicpm", "CN", "private"),
    ("MiniMaxAI/MiniMax-M1-80k", "minimax/minimax-m1-80k", "MiniMax M1 80k", "minimax", "MiniMax", "minimax", "CN", "private"),
    ("MiniMaxAI/MiniMax-M1-40k", "minimax/minimax-m1-40k", "MiniMax M1 40k", "minimax", "MiniMax", "minimax", "CN", "private"),
    ("nvidia/Llama-3_1-Nemotron-Ultra-253B-v1", "nvidia/llama-3-1-nemotron-ultra-253b-v1", "Llama Nemotron Ultra", "nvidia", "NVIDIA", "llama-nemotron", "US", "private"),
    ("nvidia/Llama-3.1-Nemotron-70B-Instruct-HF", "nvidia/llama-3-1-nemotron-70b-instruct-hf", "Llama 3.1 Nemotron 70B", "nvidia", "NVIDIA", "llama-nemotron", "US", "private"),
    ("allenai/OLMo-2-1124-7B-Instruct", "allen-ai/olmo-2-1124-7b-instruct", "OLMo 2 7B Instruct", "allen-ai", "Allen Institute for AI", "olmo", "US", "nonprofit"),
    ("nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1", "nvidia/llama-3-1-nemotron-nano-4b-v1-1", "Llama 3.1 Nemotron Nano 4B v1.1", "nvidia", "NVIDIA", "llama-nemotron", "US", "private"),
    ("nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16", "nvidia/nvidia-nemotron-3-nano-4b-bf16", "Nemotron 3 Nano 4B", "nvidia", "NVIDIA", "nemotron", "US", "private"),
    ("nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning-bf16", "Nemotron 3 Nano Omni 30B A3B", "nvidia", "NVIDIA", "nemotron", "US", "private"),
    ("RekaAI/reka-flash-3", "reka/reka-flash-3", "Reka Flash 3", "reka", "Reka", "reka", "US", "private"),
    ("sarvamai/sarvam-m", "sarvam/sarvam-m", "Sarvam M", "sarvam", "Sarvam AI", "sarvam", "IN", "private"),
    ("meituan-longcat/LongCat-Flash-Chat", "meituan/longcat-flash-chat", "LongCat Flash Chat", "meituan", "Meituan", "longcat", "CN", "private"),
    ("meituan-longcat/LongCat-Flash-Lite", "meituan/longcat-flash-lite", "LongCat Flash Lite", "meituan", "Meituan", "longcat", "CN", "private"),
    ("meituan-longcat/LongCat-2.0", "meituan/longcat-2-0", "LongCat 2.0", "meituan", "Meituan", "longcat", "CN", "private"),
    ("skt/A.X-K2", "skt/a-x-k2", "A.X-K2", "skt", "SK Telecom", "a-x", "KR", "private"),
    ("stepfun-ai/Step3-VL-10B", "stepfun/step3-vl-10b", "Step3 VL 10B", "stepfun", "StepFun", "step", "CN", "private"),
    ("thinkingmachines/Inkling-Small", "thinkingmachines/inkling-small", "Inkling Small", "thinkingmachines", "Thinking Machines Lab", "inkling", "US", "private"),
    ("Nanbeige/Nanbeige4.1-3B", "nanbeige/nanbeige4-1-3b", "Nanbeige4.1-3B", "nanbeige", "Nanbeige", "nanbeige", "CN", "private"),
    ("trillionlabs/Tri-21B-Think", "trillionlabs/tri-21b-think", "Tri-21B-Think", "trillionlabs", "Trillion Labs", "tri", "KR", "private"),
    ("naver-hyperclovax/HyperCLOVAX-SEED-Think-32B", "naver/hyperclovax-seed-think-32b", "HyperCLOVA X SEED Think 32B", "naver", "NAVER", "hyperclova", "KR", "private"),
    ("baidu/ERNIE-4.5-300B-A47B-PT", "baidu/ernie-4-5-300b-a47b-pt", "ERNIE 4.5 300B A47B", "baidu", "Baidu", "ernie", "CN", "state-backed"),
    ("Motif-Technologies/Motif-2-12.7B-Reasoning", "motif/motif-2-12-7b-reasoning", "Motif-2-12.7B", "motif", "Motif Technologies", "motif", "KR", "private"),
    ("Motif-Technologies/Motif-3", "motif/motif-3", "Motif 3", "motif", "Motif Technologies", "motif", "KR", "private"),
    ("nex-agi/Nex-N2-Pro", "nex-agi/nex-n2-pro", "Nex-N2-Pro", "nex-agi", "Nex-AGI", "nex", "CN", "private"),
    ("IFM/K2-Think", "ifm/k2-think", "K2 Think", "ifm", "Institute of Foundation Models", "k2-think", "AE", "academic"),
    ("IFM/K2-Think-V2", "ifm/k2-think-v2", "K2 Think V2", "ifm", "Institute of Foundation Models", "k2-think", "AE", "academic"),
    ("Agnes-AI/Agnes-2.5-Pro-Alpha", "agnes-ai/agnes-2-5-pro-alpha", "Agnes 2.5 Pro Alpha", "agnes-ai", "Agnes AI", "agnes", "US", "private"),
    ("deepseek-ai/DeepSeek-V3.1-Terminus", "deepseek/deepseek-v3-1-terminus", "DeepSeek V3.1 Terminus", "deepseek", "DeepSeek", "deepseek", "CN", "private"),
    ("deepseek-ai/DeepSeek-V3.2-Speciale", "deepseek/deepseek-v3-2-speciale", "DeepSeek V3.2 Speciale", "deepseek", "DeepSeek", "deepseek", "CN", "private"),
    ("deepseek-ai/DeepSeek-V2.5", "deepseek/deepseek-v2-5", "DeepSeek-V2.5", "deepseek", "DeepSeek", "deepseek", "CN", "private"),
    ("ai21labs/AI21-Jamba-Large-1.7", "ai21/ai21-jamba-large-1-7", "Jamba 1.7 Large", "ai21", "AI21 Labs", "jamba", "IL", "private"),
    ("google/diffusiongemma-26B-A4B-it", "google/diffusiongemma-26b-a4b-it", "DiffusionGemma 26B A4B", "google", "Google", "gemma", "US", "private"),
    ("google/gemma-4-12B-it", "google/gemma-4-12b-it", "Gemma 4 12B IT", "google", "Google", "gemma", "US", "private"),
    ("google/gemma-4-12B", "google/gemma-4-12b", "Gemma 4 12B", "google", "Google", "gemma", "US", "private"),
    ("CohereLabs/tiny-aya-global", "cohere/tiny-aya-global", "Tiny Aya Global", "cohere", "Cohere", "aya", "CA", "private"),
    ("ai9stars/G9v3-39A5B", "ai9stars/g9v3-39a5b", "G9v3-39A5B", "ai9stars", "AI9Stars", "g9", "CN", "private"),
    ("ai9stars/G9v3-3B", "ai9stars/g9v3-3b", "G9v3-3B", "ai9stars", "AI9Stars", "g9", "CN", "private"),
    ("tencent/Hy3", "tencent/hy3", "Hy3", "tencent", "Tencent", "hy3", "CN", "private"),
    ("openchat/openchat-3.5-0106", "openchat/openchat-3-5-0106", "OpenChat 3.5", "openchat", "OpenChat", "openchat", "US", "open-collective"),
]


def _headers() -> dict[str, str]:
    headers = {"User-Agent": "ModelSpec-LeaderboardGaps/1.0"}
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _model_type(hf: dict, display: str) -> ModelType:
    pipeline = (hf.get("pipeline_tag") or "").lower()
    name = (hf.get("id", "") + " " + display).lower()
    tags = [str(t).lower() for t in (hf.get("tags") or [])]
    if "diffusion" in name:
        return ModelType.IMAGE_GENERATION
    if pipeline in ("image-text-to-text", "any-to-any", "visual-question-answering"):
        return ModelType.VLM
    if pipeline == "text-to-image":
        return ModelType.IMAGE_GENERATION
    if any(k in name for k in ("-vl-", "-vl ", " omni", "vision", "thinker")):
        if "omni" in name or "vl" in name or "thinker" in name:
            if "thinker" in name or pipeline == "image-text-to-text":
                return ModelType.VLM if pipeline in ("image-text-to-text", "any-to-any") else ModelType.LLM_REASONING
    if any(k in name for k in ("think", "reason", "qwq", "speciale", "terminus")):
        return ModelType.LLM_REASONING
    if any(k in name for k in ("coder", "code")):
        return ModelType.LLM_CODE
    if "instruct" in name or "chat" in name or "it" in tags:
        return ModelType.LLM_CHAT
    return ModelType.LLM_CHAT


def _arch_type(config: dict[str, Any] | None, fields: dict[str, int], name: str) -> ArchitectureType | None:
    if "diffusion" in name.lower():
        return ArchitectureType.DIFFUSION
    if config:
        blob = json_dumps_keys(config)
        if any(k in config or k in blob for k in ("mamba_d_state", "mamba_expand", "mamba_d_conv")):
            return ArchitectureType.HYBRID_SSM_TRANSFORMER
        if any(k in config for k in NON_UNIFORM_KEYS) and fields.get("num_experts"):
            return ArchitectureType.HYBRID_SSM_TRANSFORMER
    if fields.get("num_experts"):
        return ArchitectureType.MOE
    if config:
        return ArchitectureType.DENSE_TRANSFORMER
    return None


def json_dumps_keys(config: dict[str, Any]) -> set[str]:
    keys = set(config)
    for nest in ("text_config", "llm_config", "language_config"):
        nested = config.get(nest)
        if isinstance(nested, dict):
            keys.update(nested)
    return keys


def _attention(fields: dict[str, int], config: dict[str, Any] | None) -> AttentionType | None:
    if config and any(k in json_dumps_keys(config) for k in NON_UNIFORM_KEYS):
        return None
    heads = fields.get("num_attention_heads")
    kv = fields.get("num_kv_heads")
    if heads is None or kv is None:
        return None
    if kv == heads:
        return AttentionType.MHA
    if kv < heads:
        return AttentionType.GQA
    return None


def _license(hf: dict) -> tuple[LicenseType | None, bool]:
    card = hf.get("cardData") or {}
    lic = (hf.get("license") or card.get("license") or "")
    if isinstance(lic, list):
        lic = lic[0] if lic else ""
    lic = str(lic).lower()
    gated = bool(hf.get("gated"))
    open_weights = not bool(hf.get("private"))
    mapped = LICENSE_MAP.get(lic)
    if mapped is None and lic:
        mapped = LicenseType.OTHER
    if not lic:
        mapped = None
    return mapped, open_weights and not (hf.get("private") is True)


def _base_model(hf: dict) -> str:
    for tag in hf.get("tags") or []:
        if isinstance(tag, str) and tag.startswith("base_model:"):
            return tag.split(":", 1)[1]
    card = hf.get("cardData") or {}
    base = card.get("base_model")
    if isinstance(base, str):
        return base
    if isinstance(base, list) and base and isinstance(base[0], str):
        return base[0]
    return ""


def build_card(spec: tuple, hf: dict, config: dict[str, Any] | None) -> ModelCard:
    hf_id, model_id, display, provider, provider_display, family, country, org = spec
    params = extract_safetensors_total(hf)
    geom = extract_geometry(config) if config else None
    fields = dict(geom.fields) if geom else {}
    if (
        fields.get("active_parameters") is not None
        and params is not None
        and fields["active_parameters"] > params
    ):
        fields.pop("active_parameters", None)

    model_type = _model_type(hf, display)
    license_type, is_open = _license(hf)
    try:
        org_type = OrgType(org)
    except ValueError:
        org_type = OrgType.PRIVATE

    rope = None
    if config:
        raw_rope = None
        for src in (config.get("text_config") or {}, config.get("llm_config") or {}, config):
            if isinstance(src, dict) and src.get("rope_theta") is not None:
                raw_rope = src.get("rope_theta")
                break
        if isinstance(raw_rope, (int, float)) and not isinstance(raw_rope, bool):
            rope = float(raw_rope)

    pos = PositionalEncoding.ROPE if rope is not None else None
    arch_type = _arch_type(config, fields, display)
    attention = _attention(fields, config)

    ctx = None
    if config:
        for key in ("max_position_embeddings", "model_max_length", "max_seq_len"):
            for src in (config.get("text_config") or {}, config.get("llm_config") or {}, config):
                if isinstance(src, dict) and isinstance(src.get(key), int) and not isinstance(src.get(key), bool):
                    ctx = src[key]
                    break
            if ctx is not None:
                break

    inputs = [Modality.TEXT]
    outputs = [Modality.TEXT]
    vision = VisionDetail()
    image_gen = ImageGenDetail()
    if model_type == ModelType.VLM:
        inputs = [Modality.TEXT, Modality.IMAGE]
        vision.supported = True
    if model_type == ModelType.IMAGE_GENERATION:
        outputs = [Modality.IMAGE]
        image_gen.supported = True

    library = hf.get("library_name") or ""
    runtimes = Runtimes()
    if library == "transformers":
        runtimes.transformers = True
    tags_l = [str(t).lower() for t in (hf.get("tags") or [])]
    if "vllm" in tags_l:
        runtimes.vllm = True

    created = (hf.get("createdAt") or "")[:10]
    modified = (hf.get("lastModified") or "")[:10]
    pipeline = hf.get("pipeline_tag") or ""
    our_tags = [pipeline] if pipeline else []
    if hf.get("gated"):
        our_tags.append("gated")

    base = _base_model(hf)
    relation = BaseModelRelation.FINETUNE if base else BaseModelRelation.ORIGINAL

    status = ModelStatus.ACTIVE
    low = display.lower()
    if "alpha" in low:
        status = ModelStatus.ALPHA
    elif "beta" in low:
        status = ModelStatus.BETA
    elif "preview" in low:
        status = ModelStatus.PREVIEW

    card = ModelCard(
        identity=Identity(
            model_id=model_id,
            display_name=display,
            provider=provider,
            provider_display=provider_display,
            family=family,
            version=model_id.split("/", 1)[-1],
            release_date=created,
            last_updated=modified,
            status=status,
            model_type=model_type,
            tags=our_tags,
            pipeline_tag=pipeline,
        ),
        architecture=Architecture(
            type=arch_type,
            total_parameters=params,
            total_parameters_source="safetensors" if params else "",
            active_parameters=fields.get("active_parameters"),
            num_experts=fields.get("num_experts"),
            experts_per_token=fields.get("experts_per_token"),
            num_layers=fields.get("num_layers"),
            hidden_size=fields.get("hidden_size"),
            intermediate_size=fields.get("intermediate_size"),
            attention_type=attention,
            num_attention_heads=fields.get("num_attention_heads"),
            num_kv_heads=fields.get("num_kv_heads"),
            positional_encoding=pos,
            rope_theta=rope,
            vocab_size=fields.get("vocab_size"),
        ),
        lineage=Lineage(
            base_model=base,
            base_model_relation=relation,
            library_name=library,
        ),
        licensing=Licensing(
            open_weights=is_open,
            license_type=license_type,
            origin_country=country,
            origin_org_type=org_type,
        ),
        modalities=Modalities(
            input=inputs,
            output=outputs,
            text=TextDetail(context_window=ctx),
            vision=vision,
            image_generation=image_gen,
        ),
        availability=Availability(
            primary_provider=PrimaryProvider(
                name=provider_display,
                platform_url=f"https://huggingface.co/{hf_id}",
                model_id_on_platform=hf_id,
            ),
            huggingface=PlatformEntry(
                available=True,
                model_id=hf_id,
                url=f"https://huggingface.co/{hf_id}",
                gated=bool(hf.get("gated")),
            ),
        ),
        deployment=Deployment(
            api_only=False,
            local_inference=True,
            self_hostable=True,
            runtimes=runtimes,
        ),
        adoption=Adoption(
            huggingface_downloads=hf.get("downloads"),
            huggingface_likes=hf.get("likes"),
        ),
        sources=Sources(
            huggingface_url=f"https://huggingface.co/{hf_id}",
            last_scraped_huggingface=TODAY,
        ),
        card_schema_version="3.0",
        card_author="modelspec",
        card_created=TODAY,
        card_updated=TODAY,
        prose_body=(
            f"# {display}\n\n"
            f"Carded from Hugging Face Hub [{hf_id}](https://huggingface.co/{hf_id}) "
            f"because a live AA/LM Arena row had no catalogue card. "
            f"{'Hub safetensors total {:,}. '.format(params) if params else 'Hub safetensors total not published; total_parameters left null. '}"
            "No benchmark evidence attached."
        ),
    )
    return card


def fetch_model(client: httpx.Client, repo_id: str) -> dict | None:
    url = HF_API.format(repo_id=repo_id) + "?blobs=true"
    try:
        resp = client.get(url)
    except httpx.HTTPError as exc:
        print(f"  ERROR network {repo_id}: {exc}")
        return None
    if resp.status_code != 200:
        print(f"  ERROR http {resp.status_code} {repo_id}")
        return None
    try:
        return resp.json()
    except ValueError:
        print(f"  ERROR non-json {repo_id}")
        return None


def existing_ids() -> set[str]:
    ids = set()
    for path in MODELS_DIR.glob("*/*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        try:
            front = yaml.safe_load(text.split("---", 2)[1]) or {}
        except Exception:
            continue
        mid = front.get("model_id")
        if mid:
            ids.add(str(mid))
    return ids


def main() -> int:
    have = existing_ids()
    created = []
    skipped = []
    failed = []
    with httpx.Client(timeout=30.0, follow_redirects=True, headers=_headers()) as client:
        for spec in SPECS:
            hf_id, model_id, display, *_ = spec
            if model_id in have:
                skipped.append((model_id, "already exists"))
                print(f"SKIP exists {model_id}")
                continue
            print(f"CARD {model_id} <- {hf_id}")
            hf = fetch_model(client, hf_id)
            if hf is None:
                failed.append((model_id, "hub fetch failed"))
                continue
            status, config, detail = fetch_config(client, hf_id)
            if status != "ok":
                print(f"  config {status} {detail} — geometry left null")
                config = None
            try:
                card = build_card(spec, hf, config)
                path = write_card_yaml(card, MODELS_DIR)
                ModelCard.from_yaml_file(path)
            except Exception as exc:
                failed.append((model_id, str(exc)))
                print(f"  FAIL {exc}")
                # if a partial file was written, leave it only if it round-trips
                continue
            created.append(str(path.relative_to(PROJECT_ROOT)))
            have.add(model_id)
            time.sleep(0.05)
    print(f"\ncreated={len(created)} skipped={len(skipped)} failed={len(failed)}")
    for item, why in failed:
        print(f"  FAILED {item}: {why}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
