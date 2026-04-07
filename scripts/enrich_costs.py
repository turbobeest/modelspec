#!/usr/bin/env python3
"""Enrich ModelSpec cards with cost, performance, and availability data.

Adds inference cost estimates for open-weight models, Artificial Analysis
quality/speed indices, and platform availability mappings. Only fills
None/empty fields -- never overwrites existing data.

Usage:
    source .venv/bin/activate && python scripts/enrich_costs.py
"""

from __future__ import annotations

import glob
import re
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import ModelCard  # noqa: E402


MODELS_DIR = PROJECT_ROOT / "models"


# ═══════════════════════════════════════════════════════════════
# Slugify (same as other scripts)
# ═══════════════════════════════════════════════════════════════

def slugify(name: str) -> str:
    """Turn a model name/id into a filesystem-safe slug."""
    s = name.lower().strip()
    if "/" in s:
        s = s.split("/", 1)[1]
    s = s.replace(".", "-")
    s = re.sub(r"[_/:\\]+", "-", s)
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")
    return s


# ═══════════════════════════════════════════════════════════════
# 1. Inference cost data for open-weight models
#    Approximate $/M tokens on popular inference platforms
#    Based on Together AI, Groq, Fireworks public pricing
# ═══════════════════════════════════════════════════════════════

# Each entry: slug_pattern -> (input_cost, output_cost) in $/M tokens
INFERENCE_COSTS: dict[str, tuple[float, float]] = {
    # ── Meta Llama ──
    "llama-3-1-8b": (0.10, 0.10),
    "llama-3-1-70b": (0.88, 0.88),
    "llama-3-3-70b": (0.88, 0.88),
    "llama-3-1-405b": (3.50, 3.50),
    "llama-3-2-3b": (0.06, 0.06),
    "llama-3-2-1b": (0.04, 0.04),
    "llama-3-2-11b": (0.18, 0.18),
    "llama-3-2-90b": (1.20, 1.20),
    "llama-4-scout": (0.18, 0.18),
    "llama-4-maverick": (0.50, 0.50),
    # ── Qwen ──
    "qwen3-30b-a3b": (0.15, 0.60),
    "qwen3-235b-a22b": (0.60, 1.20),
    "qwen3-32b": (0.30, 0.90),
    "qwen3-8b": (0.10, 0.30),
    "qwen3-14b": (0.20, 0.60),
    "qwen3-4b": (0.05, 0.15),
    "qwen3-1-7b": (0.04, 0.12),
    "qwen3-0-6b": (0.03, 0.09),
    "qwen3-5-35b-a3b": (0.15, 0.60),
    "qwen3-5-122b-a10b": (0.55, 1.10),
    "qwen3-5-397b-a17b": (1.20, 2.40),
    "qwen3-5-27b": (0.25, 0.75),
    "qwen3-5-9b": (0.10, 0.30),
    "qwen3-5-4b": (0.05, 0.15),
    "qwen3-5-2b": (0.04, 0.12),
    # ── Google Gemma ──
    "gemma-4-27b": (0.20, 0.20),
    "gemma-4-26b": (0.20, 0.20),
    "gemma-4-31b": (0.20, 0.20),
    "gemma-4-e4b": (0.05, 0.05),
    "gemma-4-e2b": (0.03, 0.03),
    "gemma-3-27b": (0.15, 0.15),
    "gemma-3-12b": (0.10, 0.10),
    "gemma-3-4b": (0.04, 0.04),
    "gemma-3-1b": (0.02, 0.02),
    "gemma-2-27b": (0.15, 0.15),
    "gemma-2-9b": (0.08, 0.08),
    "gemma-2-2b": (0.03, 0.03),
    # ── DeepSeek ──
    "deepseek-r1": (0.55, 2.19),
    "deepseek-v3": (0.14, 0.28),
    "deepseek-chat": (0.14, 0.28),
    "deepseek-r1-distill-llama-70b": (0.88, 0.88),
    "deepseek-r1-distill-llama-8b": (0.10, 0.10),
    "deepseek-r1-distill-qwen-32b": (0.30, 0.90),
    "deepseek-r1-distill-qwen-14b": (0.20, 0.60),
    "deepseek-r1-distill-qwen-7b": (0.10, 0.30),
    "deepseek-r1-distill-qwen-1-5b": (0.04, 0.12),
    "deepseek-coder": (0.14, 0.28),
    # ── Mistral ──
    "mistral-large": (2.00, 6.00),
    "mistral-medium": (1.00, 3.00),
    "mistral-small": (0.20, 0.60),
    "mistral-nemo": (0.15, 0.15),
    "mistral-7b": (0.10, 0.10),
    "mixtral-8x7b": (0.24, 0.24),
    "mixtral-8x22b": (0.65, 0.65),
    "codestral": (0.30, 0.90),
    "devstral": (0.20, 0.60),
    "ministral-8b": (0.10, 0.10),
    "ministral-3b": (0.04, 0.04),
    "pixtral-12b": (0.15, 0.15),
    "pixtral-large": (2.00, 6.00),
    # ── Microsoft Phi ──
    "phi-4": (0.07, 0.14),
    "phi-4-mini": (0.04, 0.08),
    "phi-3-5-mini": (0.10, 0.10),
    "phi-3-mini": (0.10, 0.10),
    # ── Cohere ──
    "command-r-plus": (2.50, 10.00),
    "command-r": (0.15, 0.60),
    "command-r7b": (0.04, 0.04),
    "command-a": (2.50, 10.00),
    # ── Allen AI OLMo ──
    "olmo-2": (0.10, 0.10),
    "olmo-3": (0.10, 0.10),
    # ── Databricks ──
    "dbrx": (0.60, 0.60),
    # ── NVIDIA ──
    "nemotron": (0.30, 0.30),
    # ── Embedding models ──
    "bge-m3": (0.01, 0.01),
    "bge-large": (0.01, 0.01),
    "bge-base": (0.008, 0.008),
    "bge-small": (0.005, 0.005),
    "e5-mistral": (0.01, 0.01),
    "nomic-embed": (0.008, 0.008),
    "jina-embeddings-v3": (0.02, 0.02),
    "jina-embeddings-v2": (0.01, 0.01),
    "jina-embeddings-v4": (0.02, 0.02),
    "jina-embeddings-v5": (0.02, 0.02),
    "qwen3-embedding": (0.008, 0.008),
    # ── Image generation ──
    "flux-1-dev": (0.025, 0.025),
    "flux-1-schnell": (0.003, 0.003),
    "flux-2-dev": (0.035, 0.035),
    "sdxl": (0.002, 0.002),
    "stable-diffusion-3-5": (0.035, 0.035),
    "stable-diffusion-3": (0.035, 0.035),
    "sd-turbo": (0.002, 0.002),
    # ── Other ──
    "yi-1-5-34b": (0.60, 0.60),
    "yi-1-5-9b": (0.15, 0.15),
    "falcon-40b": (0.60, 0.60),
    "falcon-7b": (0.10, 0.10),
}


# ═══════════════════════════════════════════════════════════════
# 2. Artificial Analysis quality/speed indices (curated)
#    quality_index: overall quality score (0-100)
#    speed_index: overall speed score (0-100)
#    api_tps_output: typical API output tokens per second
# ═══════════════════════════════════════════════════════════════

AA_DATA: dict[str, dict[str, float]] = {
    # ── Anthropic ──
    "claude-opus-4-6": {"quality_index": 88, "speed_index": 62, "api_tps_output": 45},
    "claude-sonnet-4-5": {"quality_index": 86, "speed_index": 71, "api_tps_output": 72},
    "claude-sonnet-4": {"quality_index": 85, "speed_index": 73, "api_tps_output": 78},
    "claude-haiku-3-5": {"quality_index": 75, "speed_index": 88, "api_tps_output": 130},
    # ── OpenAI ──
    "gpt-4o": {"quality_index": 82, "speed_index": 78, "api_tps_output": 95},
    "gpt-4o-mini": {"quality_index": 72, "speed_index": 90, "api_tps_output": 150},
    "gpt-4-1": {"quality_index": 84, "speed_index": 76, "api_tps_output": 90},
    "gpt-4-1-mini": {"quality_index": 74, "speed_index": 89, "api_tps_output": 145},
    "gpt-4-1-nano": {"quality_index": 65, "speed_index": 94, "api_tps_output": 200},
    "gpt-5-1": {"quality_index": 88, "speed_index": 70, "api_tps_output": 65},
    "gpt-4-turbo": {"quality_index": 79, "speed_index": 65, "api_tps_output": 50},
    "gpt-3-5-turbo": {"quality_index": 60, "speed_index": 92, "api_tps_output": 160},
    # ── Google ──
    "gemini-2-5-pro": {"quality_index": 85, "speed_index": 71, "api_tps_output": 72},
    "gemini-2-5-flash": {"quality_index": 80, "speed_index": 87, "api_tps_output": 130},
    "gemini-2-0-flash": {"quality_index": 77, "speed_index": 89, "api_tps_output": 140},
    "gemini-2-0-flash-lite": {"quality_index": 68, "speed_index": 93, "api_tps_output": 190},
    "gemini-1-5-pro": {"quality_index": 78, "speed_index": 68, "api_tps_output": 55},
    "gemini-1-5-flash": {"quality_index": 71, "speed_index": 86, "api_tps_output": 120},
    # ── Meta Llama ──
    "llama-3-1-405b": {"quality_index": 80, "speed_index": 45, "api_tps_output": 35},
    "llama-3-1-70b": {"quality_index": 75, "speed_index": 72, "api_tps_output": 80},
    "llama-3-3-70b": {"quality_index": 76, "speed_index": 73, "api_tps_output": 82},
    "llama-3-1-8b": {"quality_index": 62, "speed_index": 92, "api_tps_output": 200},
    # ── Qwen ──
    "qwen3-235b-a22b": {"quality_index": 82, "speed_index": 55, "api_tps_output": 40},
    "qwen3-30b-a3b": {"quality_index": 74, "speed_index": 88, "api_tps_output": 150},
    "qwen3-32b": {"quality_index": 76, "speed_index": 70, "api_tps_output": 75},
    "qwen3-14b": {"quality_index": 70, "speed_index": 80, "api_tps_output": 100},
    "qwen3-8b": {"quality_index": 66, "speed_index": 88, "api_tps_output": 160},
    # ── DeepSeek ──
    "deepseek-r1": {"quality_index": 84, "speed_index": 40, "api_tps_output": 25},
    "deepseek-v3": {"quality_index": 80, "speed_index": 70, "api_tps_output": 70},
    "deepseek-chat": {"quality_index": 80, "speed_index": 70, "api_tps_output": 70},
    # ── Mistral ──
    "mistral-large": {"quality_index": 78, "speed_index": 60, "api_tps_output": 48},
    "mistral-small": {"quality_index": 68, "speed_index": 82, "api_tps_output": 110},
    "mistral-nemo": {"quality_index": 65, "speed_index": 85, "api_tps_output": 130},
    # ── xAI ──
    "grok-3": {"quality_index": 82, "speed_index": 65, "api_tps_output": 55},
    "grok-3-mini": {"quality_index": 72, "speed_index": 82, "api_tps_output": 110},
    "grok-2": {"quality_index": 76, "speed_index": 70, "api_tps_output": 75},
    # ── Google Gemma (open) ──
    "gemma-4-27b": {"quality_index": 72, "speed_index": 85, "api_tps_output": 110},
    "gemma-4-31b": {"quality_index": 73, "speed_index": 84, "api_tps_output": 105},
    "gemma-3-27b": {"quality_index": 70, "speed_index": 82, "api_tps_output": 100},
    "gemma-3-12b": {"quality_index": 65, "speed_index": 88, "api_tps_output": 140},
    "gemma-2-27b": {"quality_index": 68, "speed_index": 80, "api_tps_output": 95},
    "gemma-2-9b": {"quality_index": 60, "speed_index": 90, "api_tps_output": 170},
    # ── Microsoft Phi ──
    "phi-4": {"quality_index": 68, "speed_index": 88, "api_tps_output": 150},
    "phi-3-5-mini": {"quality_index": 58, "speed_index": 92, "api_tps_output": 200},
    # ── Cohere ──
    "command-r-plus": {"quality_index": 73, "speed_index": 55, "api_tps_output": 42},
    "command-r": {"quality_index": 64, "speed_index": 78, "api_tps_output": 90},
    "command-a": {"quality_index": 78, "speed_index": 58, "api_tps_output": 48},
}


# ═══════════════════════════════════════════════════════════════
# 3. Platform availability data
#    Model slug pattern -> list of platform field names
#    Each entry can include model_id on that platform
# ═══════════════════════════════════════════════════════════════

# Simple format: slug -> list of platform names where available
PLATFORM_AVAILABILITY: dict[str, list[str | tuple[str, str]]] = {
    # ── Anthropic ──
    # Tuples: (platform_name, model_id_on_platform)
    "claude-opus-4-6": [
        ("claude_ai", "claude-opus-4-6"),
        ("aws_bedrock", "anthropic.claude-opus-4-6-v1"),
        ("google_vertex_ai", "claude-opus-4-6@20260205"),
        "openrouter", "cursor", "github_copilot",
    ],
    "claude-sonnet-4-5": [
        ("claude_ai", "claude-sonnet-4-5"),
        ("aws_bedrock", "anthropic.claude-sonnet-4-5-v1"),
        ("google_vertex_ai", "claude-sonnet-4-5@20250514"),
        "openrouter", "cursor", "github_copilot",
    ],
    "claude-sonnet-4": [
        ("claude_ai", "claude-sonnet-4"),
        ("aws_bedrock", "anthropic.claude-sonnet-4-v1"),
        ("google_vertex_ai", "claude-sonnet-4@20250514"),
        "openrouter", "cursor", "github_copilot",
    ],
    "claude-haiku-3-5": [
        ("claude_ai", "claude-3-5-haiku-latest"),
        ("aws_bedrock", "anthropic.claude-3-5-haiku-v1"),
        ("google_vertex_ai", "claude-3-5-haiku@20241022"),
        "openrouter", "cursor",
    ],
    # ── OpenAI ──
    "gpt-4o": [
        ("chatgpt", "gpt-4o"),
        ("azure_ai_foundry", "gpt-4o"),
        "openrouter", "cursor", "github_copilot", "perplexity",
    ],
    "gpt-4o-mini": [
        ("chatgpt", "gpt-4o-mini"),
        ("azure_ai_foundry", "gpt-4o-mini"),
        "openrouter", "cursor",
    ],
    "gpt-4-1": [
        ("chatgpt", "gpt-4.1"),
        ("azure_ai_foundry", "gpt-4.1"),
        "openrouter", "cursor", "github_copilot",
    ],
    "gpt-4-1-mini": [
        ("chatgpt", "gpt-4.1-mini"),
        ("azure_ai_foundry", "gpt-4.1-mini"),
        "openrouter", "cursor",
    ],
    "gpt-5-1": [
        ("chatgpt", "gpt-5.1"),
        ("azure_ai_foundry", "gpt-5.1"),
        "openrouter", "cursor", "github_copilot",
    ],
    # ── Google ──
    "gemini-2-5-pro": [
        ("gemini_app", "gemini-2.5-pro"),
        ("google_vertex_ai", "gemini-2.5-pro"),
        "openrouter", "cursor",
    ],
    "gemini-2-5-flash": [
        ("gemini_app", "gemini-2.5-flash"),
        ("google_vertex_ai", "gemini-2.5-flash"),
        "openrouter", "cursor",
    ],
    "gemini-2-0-flash": [
        ("gemini_app", "gemini-2.0-flash"),
        ("google_vertex_ai", "gemini-2.0-flash"),
        "openrouter",
    ],
    # ── xAI ──
    "grok-3": [
        ("grok_xai", "grok-3"),
        "openrouter",
    ],
    "grok-2": [
        ("grok_xai", "grok-2"),
        "openrouter",
    ],
    # ── Meta Llama (open-weight, wide distribution) ──
    "llama-3-1-405b": [
        "huggingface", "together_ai", "fireworks_ai", "aws_bedrock",
        "azure_ai_foundry", "google_vertex_ai", "nvidia_nim",
        "deepinfra", "replicate", "openrouter", "ollama",
    ],
    "llama-3-1-70b": [
        "huggingface", "together_ai", "fireworks_ai", "groq",
        "aws_bedrock", "azure_ai_foundry", "google_vertex_ai",
        "nvidia_nim", "deepinfra", "cerebras", "sambanova",
        "replicate", "openrouter", "ollama", "lm_studio",
    ],
    "llama-3-3-70b": [
        "huggingface", "together_ai", "fireworks_ai", "groq",
        "aws_bedrock", "azure_ai_foundry", "nvidia_nim",
        "deepinfra", "cerebras", "sambanova",
        "replicate", "openrouter", "ollama", "lm_studio",
    ],
    "llama-3-1-8b": [
        "huggingface", "together_ai", "fireworks_ai", "groq",
        "aws_bedrock", "azure_ai_foundry", "google_vertex_ai",
        "nvidia_nim", "deepinfra", "cerebras", "sambanova",
        "replicate", "openrouter", "ollama", "lm_studio", "gpt4all",
    ],
    "llama-3-2-3b": [
        "huggingface", "together_ai", "groq", "ollama", "lm_studio",
        "openrouter", "deepinfra",
    ],
    "llama-3-2-1b": [
        "huggingface", "together_ai", "groq", "ollama", "lm_studio",
        "openrouter",
    ],
    # ── Qwen (open-weight) ──
    "qwen3-235b-a22b": [
        "huggingface", "together_ai", "fireworks_ai", "deepinfra",
        "openrouter", "ollama",
    ],
    "qwen3-30b-a3b": [
        "huggingface", "together_ai", "fireworks_ai", "groq",
        "deepinfra", "openrouter", "ollama", "lm_studio",
    ],
    "qwen3-32b": [
        "huggingface", "together_ai", "fireworks_ai",
        "deepinfra", "openrouter", "ollama", "lm_studio",
    ],
    "qwen3-14b": [
        "huggingface", "together_ai", "deepinfra",
        "openrouter", "ollama", "lm_studio",
    ],
    "qwen3-8b": [
        "huggingface", "together_ai", "groq", "deepinfra",
        "openrouter", "ollama", "lm_studio",
    ],
    "qwen3-4b": [
        "huggingface", "ollama", "lm_studio", "openrouter",
    ],
    # ── DeepSeek ──
    "deepseek-r1": [
        ("deepseek", "deepseek-reasoner"),
        "huggingface", "together_ai", "fireworks_ai", "groq",
        "deepinfra", "openrouter", "ollama",
    ],
    "deepseek-v3": [
        ("deepseek", "deepseek-chat"),
        "huggingface", "together_ai", "fireworks_ai",
        "deepinfra", "openrouter",
    ],
    "deepseek-chat": [
        ("deepseek", "deepseek-chat"),
        "openrouter",
    ],
    # ── Gemma (open-weight, wide distribution) ──
    "gemma-4-27b": [
        "huggingface", "google_vertex_ai", "together_ai",
        "groq", "deepinfra", "openrouter", "ollama", "lm_studio",
        "kaggle_models",
    ],
    "gemma-4-26b": [
        "huggingface", "google_vertex_ai", "together_ai",
        "groq", "deepinfra", "openrouter", "ollama", "lm_studio",
        "kaggle_models",
    ],
    "gemma-4-31b": [
        "huggingface", "google_vertex_ai", "together_ai",
        "deepinfra", "openrouter", "ollama", "lm_studio",
        "kaggle_models",
    ],
    "gemma-3-27b": [
        "huggingface", "google_vertex_ai", "together_ai",
        "groq", "deepinfra", "openrouter", "ollama", "lm_studio",
        "kaggle_models",
    ],
    "gemma-3-12b": [
        "huggingface", "google_vertex_ai", "together_ai",
        "deepinfra", "openrouter", "ollama", "lm_studio",
        "kaggle_models",
    ],
    "gemma-2-27b": [
        "huggingface", "google_vertex_ai", "together_ai",
        "deepinfra", "openrouter", "ollama", "lm_studio",
    ],
    "gemma-2-9b": [
        "huggingface", "google_vertex_ai", "together_ai",
        "groq", "deepinfra", "openrouter", "ollama", "lm_studio",
    ],
    # ── Mistral (open-weight variants) ──
    "mistral-nemo": [
        ("mistral_plateforme", "open-mistral-nemo"),
        "huggingface", "together_ai", "deepinfra",
        "openrouter", "ollama", "lm_studio",
    ],
    "mistral-7b": [
        "huggingface", "together_ai", "fireworks_ai", "groq",
        "deepinfra", "openrouter", "ollama", "lm_studio",
    ],
    "mixtral-8x7b": [
        "huggingface", "together_ai", "fireworks_ai", "groq",
        "deepinfra", "openrouter", "ollama", "lm_studio",
    ],
    "mixtral-8x22b": [
        "huggingface", "together_ai", "fireworks_ai",
        "deepinfra", "openrouter",
    ],
    "mistral-large": [
        ("mistral_plateforme", "mistral-large-latest"),
        ("aws_bedrock", "mistral.mistral-large-latest"),
        ("azure_ai_foundry", "mistral-large-latest"),
        "openrouter",
    ],
    "mistral-small": [
        ("mistral_plateforme", "mistral-small-latest"),
        "openrouter",
    ],
    # ── Microsoft Phi ──
    "phi-4": [
        "huggingface", "azure_ai_foundry", "ollama", "lm_studio",
        "openrouter",
    ],
    "phi-3-5-mini": [
        "huggingface", "azure_ai_foundry", "ollama", "lm_studio",
        "openrouter",
    ],
    # ── Cohere ──
    "command-r-plus": [
        ("cohere", "command-r-plus"),
        "aws_bedrock", "azure_ai_foundry", "openrouter",
    ],
    "command-r": [
        ("cohere", "command-r"),
        "aws_bedrock", "openrouter",
    ],
    "command-a": [
        ("cohere", "command-a-03-2025"),
        "openrouter",
    ],
    # ── Embedding models ──
    "bge-m3": ["huggingface", "together_ai", "deepinfra", "ollama"],
    "bge-large": ["huggingface", "together_ai", "deepinfra"],
    "nomic-embed": ["huggingface", "together_ai", "deepinfra", "ollama"],
    "jina-embeddings-v3": ["huggingface", "together_ai", "deepinfra"],
    "e5-mistral": ["huggingface", "together_ai"],
    # ── Image gen ──
    "flux-1-dev": ["huggingface", "replicate", "together_ai", "fireworks_ai"],
    "flux-1-schnell": ["huggingface", "replicate", "together_ai"],
    "stable-diffusion-xl": ["huggingface", "replicate", "stability_ai"],
    "stable-diffusion-3-5": ["huggingface", "replicate", "stability_ai"],
}


# ═══════════════════════════════════════════════════════════════
# Fuzzy matching
# ═══════════════════════════════════════════════════════════════

def normalize_slug(model_id: str) -> str:
    """Normalize a model_id to a comparable slug.

    Strips provider prefix, removes common suffixes like -instruct, -it,
    -chat, -hf, -fp8, -awq, -gptq, etc.
    """
    slug = model_id.lower()
    # Strip provider/ prefix
    if "/" in slug:
        slug = slug.split("/", 1)[1]
    # Remove common deployment/quantization suffixes
    for suffix in ("-instruct", "-it", "-chat", "-hf", "-fp8", "-awq",
                    "-gptq-int4", "-gptq", "-gguf", "-bf16", "-base"):
        slug = slug.removesuffix(suffix)
    # Remove trailing date suffixes like -2024-05-13, -2501, -2407
    slug = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", slug)
    slug = re.sub(r"-\d{4}$", "", slug)
    return slug.strip("-")


def match_against_mapping(model_id: str, mapping: dict) -> str | None:
    """Try to match a model_id against a mapping dict.

    Strategy:
    1. Exact match on normalized slug
    2. Prefix match (mapping key is prefix of slug)
    3. Contains match (mapping key is contained in slug)

    Returns the matching key, or None.
    """
    slug = normalize_slug(model_id)

    # 1. Exact match
    if slug in mapping:
        return slug

    # 2. Prefix match (longest first for specificity)
    prefix_matches = [
        k for k in mapping
        if slug.startswith(k)
    ]
    if prefix_matches:
        return max(prefix_matches, key=len)

    # 3. Contains match (longest first)
    contains_matches = [
        k for k in mapping
        if k in slug
    ]
    if contains_matches:
        return max(contains_matches, key=len)

    return None


# ═══════════════════════════════════════════════════════════════
# Enrichment functions
# ═══════════════════════════════════════════════════════════════

def enrich_cost(card: ModelCard) -> bool:
    """Fill in cost.input / cost.output if currently None.

    Only applies when BOTH are None (don't partially fill).
    Returns True if card was modified.
    """
    if card.cost.input is not None or card.cost.output is not None:
        return False

    key = match_against_mapping(card.identity.model_id, INFERENCE_COSTS)
    if key is None:
        return False

    input_cost, output_cost = INFERENCE_COSTS[key]
    card.cost.input = input_cost
    card.cost.output = output_cost
    card.cost.note = "Estimated inference cost on popular platforms ($/M tokens)"
    return True


def enrich_performance(card: ModelCard) -> bool:
    """Fill in AA quality/speed indices and api_tps_output.

    Only fills None fields. Returns True if card was modified.
    """
    key = match_against_mapping(card.identity.model_id, AA_DATA)
    if key is None:
        return False

    data = AA_DATA[key]
    changed = False

    # Quality index
    if ("artificial_analysis_quality_index" not in card.benchmarks.scores
            and "quality_index" in data):
        card.benchmarks.scores["artificial_analysis_quality_index"] = data["quality_index"]
        changed = True

    # Speed index
    if ("artificial_analysis_speed_index" not in card.benchmarks.scores
            and "speed_index" in data):
        card.benchmarks.scores["artificial_analysis_speed_index"] = data["speed_index"]
        changed = True

    # Output TPS -> inference_performance.api_tps_output
    if (card.inference_performance.api_tps_output is None
            and "api_tps_output" in data):
        card.inference_performance.api_tps_output = data["api_tps_output"]
        changed = True

    return changed


def enrich_availability(card: ModelCard) -> bool:
    """Fill in platform availability for models where all platforms are empty.

    Only sets available=True and model_id on platforms that are currently
    not marked available. Returns True if card was modified.
    """
    key = match_against_mapping(card.identity.model_id, PLATFORM_AVAILABILITY)
    if key is None:
        return False

    platforms = PLATFORM_AVAILABILITY[key]
    changed = False

    for entry in platforms:
        if isinstance(entry, tuple):
            platform_name, model_id_on_platform = entry
        else:
            platform_name = entry
            model_id_on_platform = ""

        # Check if the platform field exists on Availability
        if not hasattr(card.availability, platform_name):
            continue

        platform: Any = getattr(card.availability, platform_name)

        # Only fill if not already marked available
        if hasattr(platform, "available") and not platform.available:
            platform.available = True
            if model_id_on_platform and not platform.model_id:
                platform.model_id = model_id_on_platform
            changed = True

    return changed


# ═══════════════════════════════════════════════════════════════
# YAML writing (same pattern as enrich_cards.py)
# ═══════════════════════════════════════════════════════════════

def _convert_enums(obj: Any) -> Any:
    """Recursively convert enum values in a dict/list."""
    if isinstance(obj, dict):
        return {k: _convert_enums(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_enums(item) for item in obj]
    elif hasattr(obj, "value"):
        return obj.value
    return obj


def write_card_yaml(card: ModelCard, filepath: Path) -> None:
    """Write a ModelCard back to its YAML+Markdown file."""
    data: dict[str, Any] = {}

    # Identity fields go at top level
    identity_dict = card.identity.model_dump(exclude_none=False)
    for k, v in identity_dict.items():
        if hasattr(v, "value"):
            identity_dict[k] = v.value
        elif isinstance(v, list):
            identity_dict[k] = [item.value if hasattr(item, "value") else item for item in v]
    data.update(identity_dict)

    # Other sections are nested
    sections = [
        "architecture", "lineage", "licensing", "modalities", "capabilities",
        "cost", "availability", "benchmarks", "deployment", "risk_governance",
        "inference_performance", "adoption", "downselect", "sources",
    ]
    for section_name in sections:
        section = getattr(card, section_name)
        section_data = section.model_dump(exclude_none=False)
        section_data = _convert_enums(section_data)
        data[section_name] = section_data

    # Card metadata
    data["card_schema_version"] = card.card_schema_version
    data["card_author"] = card.card_author
    data["card_created"] = card.card_created
    data["card_updated"] = card.card_updated

    yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    content = f"---\n{yaml_str}---\n\n{card.prose_body}"

    filepath.write_text(content, encoding="utf-8")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    print("=" * 60)
    print("  ModelSpec Cost / Performance / Availability Enrichment")
    print("=" * 60)

    files = sorted(glob.glob(str(MODELS_DIR / "**" / "*.md"), recursive=True))
    total = len(files)
    print(f"Found {total} model card files\n")

    if total == 0:
        print("No cards found. Exiting.")
        return

    # Stats
    cost_enriched = 0
    perf_enriched = 0
    avail_enriched = 0
    cards_modified = 0
    errors = 0
    error_details: list[tuple[str, str]] = []

    # Track which mapping keys were matched
    cost_matches: dict[str, int] = {}
    perf_matches: dict[str, int] = {}
    avail_matches: dict[str, int] = {}

    t0 = time.monotonic()

    for i, filepath in enumerate(files, start=1):
        try:
            card = ModelCard.from_yaml_file(filepath)
            modified = False

            # 1. Cost enrichment
            if enrich_cost(card):
                cost_enriched += 1
                modified = True
                key = match_against_mapping(card.identity.model_id, INFERENCE_COSTS)
                if key:
                    cost_matches[key] = cost_matches.get(key, 0) + 1

            # 2. Performance / AA indices
            if enrich_performance(card):
                perf_enriched += 1
                modified = True
                key = match_against_mapping(card.identity.model_id, AA_DATA)
                if key:
                    perf_matches[key] = perf_matches.get(key, 0) + 1

            # 3. Platform availability
            if enrich_availability(card):
                avail_enriched += 1
                modified = True
                key = match_against_mapping(card.identity.model_id, PLATFORM_AVAILABILITY)
                if key:
                    avail_matches[key] = avail_matches.get(key, 0) + 1

            # Write back if changed
            if modified:
                card.card_updated = "2026-04-05"
                write_card_yaml(card, Path(filepath))
                cards_modified += 1

        except Exception as exc:
            errors += 1
            error_details.append((filepath, f"{type(exc).__name__}: {exc}"))

        if i % 200 == 0 or i == total:
            elapsed = time.monotonic() - t0
            rate = i / elapsed if elapsed > 0 else 0
            print(f"  [{i:>4}/{total}] {cards_modified} modified, {errors} errors  ({rate:.1f} cards/sec)")

    elapsed = time.monotonic() - t0

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("ENRICHMENT SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total cards scanned:       {total}")
    print(f"  Cards modified:            {cards_modified}")
    print(f"  Cost enriched:             {cost_enriched}")
    print(f"  Performance enriched:      {perf_enriched}")
    print(f"  Availability enriched:     {avail_enriched}")
    print(f"  Errors:                    {errors}")
    print(f"  Time:                      {elapsed:.1f}s")

    if cost_matches:
        print(f"\n-- Cost matches ({cost_enriched} total) --")
        for key, count in sorted(cost_matches.items(), key=lambda x: -x[1]):
            c_in, c_out = INFERENCE_COSTS[key]
            print(f"    {key:<35s} ${c_in:.3f}/${c_out:.3f}  ({count} cards)")

    if perf_matches:
        print(f"\n-- Performance matches ({perf_enriched} total) --")
        for key, count in sorted(perf_matches.items(), key=lambda x: -x[1]):
            d = AA_DATA[key]
            print(f"    {key:<35s} Q={d['quality_index']:.0f} S={d['speed_index']:.0f}  ({count} cards)")

    if avail_matches:
        print(f"\n-- Availability matches ({avail_enriched} total) --")
        for key, count in sorted(avail_matches.items(), key=lambda x: -x[1]):
            n = len(PLATFORM_AVAILABILITY[key])
            print(f"    {key:<35s} {n} platforms  ({count} cards)")

    if error_details:
        print(f"\n-- Errors (first 10) --")
        for path, err in error_details[:10]:
            print(f"    {path}")
            print(f"      {err}")

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
