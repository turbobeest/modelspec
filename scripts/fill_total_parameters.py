#!/usr/bin/env python3
"""Fill missing total_parameters in model cards using known values and name-based extraction.

No web fetches — uses only a hardcoded lookup table and regex extraction from model names.
"""

import os
import re
from pathlib import Path

MODELS_DIR = Path("/mnt/walnut-drive/dev/modelspec/models")

# Known parameter counts (raw numbers)
KNOWN_PARAMS = {
    # Meta Llama
    "llama-2-7b": 7e9, "llama-2-13b": 13e9, "llama-2-70b": 70e9,
    "llama-3-8b": 8e9, "llama-3-70b": 70e9,
    "llama-3-1-8b": 8e9, "llama-3-1-70b": 70e9, "llama-3-1-405b": 405e9,
    "llama-3-2-1b": 1e9, "llama-3-2-3b": 3e9, "llama-3-2-11b": 11e9, "llama-3-2-90b": 90e9,
    "llama-3-3-70b": 70e9, "llama-3-3-8b": 8e9,
    "llama-4-scout": 109e9, "llama-4-maverick": 400e9,
    "codellama-7b": 7e9, "codellama-13b": 13e9, "codellama-34b": 34e9, "codellama-70b": 70e9,
    "llamaguard-7b": 7e9,
    "llama-guard-3-1b": 1e9, "llama-guard-3-8b": 8e9, "llama-guard-3-11b": 11e9,
    "llama-guard-4-12b": 12e9,
    "meta-llama-guard-2-8b": 8e9,
    "llama-prompt-guard-2-22m": 22e6, "llama-prompt-guard-2-86m": 86e6,
    "prompt-guard-86m": 86e6,
    # DeepSeek
    "deepseek-v2": 236e9, "deepseek-v2-lite": 16e9, "deepseek-v3": 671e9,
    "deepseek-r1": 671e9, "deepseek-r1-0528": 671e9,
    "deepseek-coder-1-3b": 1.3e9, "deepseek-coder-6-7b": 6.7e9, "deepseek-coder-33b": 33e9,
    "deepseek-coder-v2": 236e9, "deepseek-coder-v2-lite": 16e9,
    "deepseek-chat": 671e9, "deepseek-reasoner": 671e9,
    "deepseek-moe-16b": 16e9,
    # Mistral
    "mistral-7b": 7e9, "mixtral-8x7b": 46.7e9, "mixtral-8x22b": 141e9,
    "mistral-small": 24e9, "mistral-medium": 24e9, "mistral-large": 123e9,
    "codestral": 22e9, "devstral": 24e9,
    "mistral-nemo": 12e9, "pixtral-12b": 12e9, "pixtral-large": 123e9,
    "ministral-8b": 8e9, "ministral-3b": 3e9,
    "mamba-codestral-7b": 7e9,
    "mistral-embed": 0.1e9,  # small embedding model
    # Mistral versioned
    "mistral-small-24b": 24e9,
    "mistral-small-3-1-24b": 24e9, "mistral-small-3-2-24b": 24e9,
    "mistral-small-4-119b": 119e9,
    "mistral-large-2411": 123e9, "mistral-large-2512": 123e9,
    "mistral-medium-2505": 24e9, "mistral-medium-2508": 24e9,
    "devstral-2-123b": 123e9,
    "devstral-small-2-24b": 24e9,
    "magistral-small": 24e9, "magistral-medium": 123e9,
    "ministral-3-8b": 8e9, "ministral-3-3b": 3e9, "ministral-3-14b": 14e9,
    "voxtral-small-24b": 24e9, "voxtral-mini-3b": 3e9, "voxtral-mini-4b": 4e9,
    # Microsoft
    "phi-2": 2.7e9, "phi-3-mini": 3.8e9, "phi-3-small": 7e9, "phi-3-medium": 14e9,
    "phi-3-5-mini": 3.8e9, "phi-3-5-moe": 42e9, "phi-3-5-vision": 4.2e9,
    "phi-4": 14e9, "phi-4-mini": 3.8e9, "phi-4-multimodal": 5.6e9,
    "phi-tiny-moe": 2.7e9,
    "florence-2-base": 0.23e9, "florence-2-large": 0.77e9,
    "vibevoice-realtime-0-5b": 0.5e9,
    # Cohere
    "command-r": 35e9, "command-r-plus": 104e9, "command-a": 111e9,
    "embed-english-v3": 0.3e9, "embed-multilingual-v3": 0.3e9,
    # AI21
    "jamba-1-5-mini": 52e9, "jamba-1-5-large": 398e9,
    "jamba-v0-1": 52e9, "jamba2-mini": 52e9, "jamba2-3b": 3e9,
    # Zhipu/GLM
    "glm-4-9b": 9e9, "glm-5": 754e9, "glm-5-1": 754e9,
    "codegeex4-all-9b": 9e9, "glm-z1-32b": 32e9, "glm-edge-v-2b": 2e9,
    # RWKV
    "rwkv-5-world-3b": 3e9, "rwkv-6-world-1b6": 1.6e9, "rwkv-6-world-7b": 7e9,
    # Stability
    "stablelm-2-1-6b": 1.6e9, "stablelm-3b": 3e9, "stable-code-3b": 3e9,
    # Qwen (sizes from name patterns plus known ones)
    "qwen2-0-5b": 0.5e9, "qwen2-1-5b": 1.5e9, "qwen2-7b": 7e9, "qwen2-72b": 72e9,
    "qwen2-5-0-5b": 0.5e9, "qwen2-5-1-5b": 1.5e9, "qwen2-5-3b": 3e9,
    "qwen2-5-7b": 7e9, "qwen2-5-14b": 14e9, "qwen2-5-32b": 32e9, "qwen2-5-72b": 72e9,
    "qwen2-5-coder-32b": 32e9, "qwen2-5-coder-14b": 14e9,
    "qwen2-5-math-1-5b": 1.5e9,
    "qwen2-vl-2b": 2e9, "qwen2-vl-7b": 7e9, "qwen2-vl-72b": 72e9,
    "qwen2-5-vl-7b": 7e9, "qwen2-5-vl-72b": 72e9,
    "qwen2-5-omni-7b": 7e9,
    "qwen3-0-6b": 0.6e9, "qwen3-1-7b": 1.7e9, "qwen3-4b": 4e9,
    "qwen3-8b": 8e9, "qwen3-14b": 14e9, "qwen3-32b": 32e9,
    "qwen3-30b-a3b": 30e9, "qwen3-235b-a22b": 235e9,
    "qwen3-vl-8b": 8e9, "qwen3-vl-32b": 32e9,
    "qwen3-vl-30b-a3b": 30e9, "qwen3-vl-235b-a22b": 235e9,
    "qwen3-embedding-0-6b": 0.6e9, "qwen3-embedding-4b": 4e9, "qwen3-embedding-8b": 8e9,
    "qwen3-reranker-0-6b": 0.6e9, "qwen3-reranker-4b": 4e9,
    "qwen3-coder-480b-a35b": 480e9, "qwen3-coder-30b-a3b": 30e9,
    "qwen3-next-80b-a3b": 80e9,
    "qwen3-tts-12hz-0-6b": 0.6e9, "qwen3-tts-12hz-1-7b": 1.7e9,
    "qwen3-max": 235e9,  # known to be Qwen3-235B-A22B
    "qwen3-5-0-8b": 0.8e9, "qwen3-5-2b": 2e9, "qwen3-5-4b": 4e9,
    "qwen3-5-9b": 9e9, "qwen3-5-27b": 27e9,
    "qwen3-5-35b-a3b": 35e9, "qwen3-5-122b-a10b": 122e9, "qwen3-5-397b-a17b": 397e9,
    # Allen AI
    "olmo-1b": 1e9, "olmo-7b": 7e9,
    "olmo-3-7b": 7e9, "olmo-3-1025-7b": 7e9,
    "molmo2-8b": 8e9,
    # Cerebras
    "llama3-1-8b": 8e9,
    "gpt-oss-120b": 120e9,
    # Moonshot/Kimi
    "kimi-k2": 1000e9,  # Kimi K2 is a 1T MoE model
    # intfloat E5 models (embedding models, relatively small)
    "e5-small": 0.033e9, "e5-small-v2": 0.033e9,
    "e5-base": 0.11e9, "e5-base-v2": 0.11e9,
    "e5-large": 0.335e9, "e5-large-v2": 0.335e9, "e5-large-unsupervised": 0.335e9,
    "multilingual-e5-small": 0.118e9,
    "multilingual-e5-base": 0.278e9,
    "multilingual-e5-large": 0.56e9, "multilingual-e5-large-instruct": 0.56e9,
    "e5-mistral-7b-instruct": 7e9,
    # Microsoft misc
    "deberta-v3-small": 0.044e9, "deberta-v3-base": 0.086e9, "deberta-v3-large": 0.304e9,
    "deberta-large-mnli": 0.35e9, "deberta-xlarge-mnli": 0.75e9,
    "deberta-v2-xlarge": 0.9e9,
    "mdeberta-v3-base": 0.086e9,
    "biogpt": 0.347e9,
    "codebert-base": 0.125e9, "graphcodebert-base": 0.125e9, "unixcoder-base": 0.125e9,
    "layoutlmv2-base-uncased": 0.2e9, "layoutlmv3-base": 0.125e9,
    "markuplm-base": 0.11e9,
    "beit-base-patch16-224": 0.087e9,
    "swinv2-tiny-patch4-window16-256": 0.028e9,
    "resnet-50": 0.025e9,
    "xclip-base-patch32": 0.15e9,
    "speecht5-tts": 0.144e9,
    "wavlm-base-plus": 0.094e9, "wavlm-base-plus-sv": 0.094e9, "wavlm-large": 0.317e9,
    "dialogpt-medium": 0.345e9,
    "kosmos-2-patch14-224": 1.6e9,
    "trocr-base-printed": 0.334e9, "trocr-large-printed": 0.558e9, "trocr-large-handwritten": 0.558e9,
    "tapex-base-finetuned-wikisql": 0.14e9,
    "table-transformer-detection": 0.023e9, "table-transformer-structure-recognition": 0.023e9,
    "table-transformer-structure-recognition-v1-1-all": 0.023e9,
    "biomednlp-biomedbert-base-uncased-abstract": 0.11e9,
    "biomednlp-biomedbert-base-uncased-abstract-fulltext": 0.11e9,
    "biomedclip-pubmedbert-256-vit-base-patch16-224": 0.21e9,
    "llmlingua-2-xlm-roberta-large-meetingbank": 0.56e9,
    # BAAI
    "aquilachat2-7b": 7e9,
    "altclip": 0.4e9,
    "bge-large-zh": 0.326e9,
    "emu3-chat-hf": 8e9,
    # biomed-roberta-base (Allen AI)
    "biomed-roberta-base": 0.125e9,
    # TII Falcon
    "falcon-mamba-tiny-dev": 0.13e9,
    # Deepseek coder
    "deepseek-coder-1-3b-base": 1.3e9,
    # OpenAI - known/estimated parameter counts
    "gpt-3-5-turbo": 20e9,  # estimated ~20B
    "gpt-4": 1760e9,  # widely reported ~1.76T MoE
    "gpt-4-turbo": 1760e9,
    "gpt-4o": 200e9,  # estimated ~200B
    "gpt-4o-mini": 8e9,  # estimated ~8B
    "gpt-4-1": 200e9,  # same architecture family as 4o
    "gpt-4-1-mini": 8e9,
    "gpt-4-1-nano": 1e9,  # estimated ~1B for nano tier
    "text-embedding-3-small": 0.1e9,
    "text-embedding-3-large": 0.3e9,
    "text-embedding-ada-002": 0.175e9,
    "o1": 200e9,  # same base as gpt-4o
    "o1-mini": 100e9,  # estimated
    "o1-preview": 200e9,
    "o1-pro": 200e9,
    "o3": 200e9,
    "o3-mini": 100e9,
    "o3-pro": 200e9,
    "o4-mini": 100e9,
    # Google Gemini - known/estimated
    "gemini-1-5-flash": 30e9,  # estimated
    "gemini-1-5-pro": 175e9,  # estimated
    "gemini-2-0-flash": 30e9,
    "gemini-2-0-flash-lite": 10e9,  # estimated lite version
    "gemini-2-5-flash": 30e9,
    "gemini-2-5-pro": 175e9,
    # xAI Grok
    "grok-2": 314e9,  # widely reported
    "grok-3": 2000e9,  # widely reported ~2T
    "grok-3-mini": 100e9,  # estimated
    # Moonshot/Kimi
    "kimi-k2-5": 1000e9,
    # Cerebras
    "zai-glm-4-7": 9e9,  # GLM-4 variant
    # Qwen API models (parameter counts not disclosed, but known equivalents)
    "qwen3-coder-next": 480e9,  # same as qwen3-coder-480b
    # Google Gemini additional aliases
    "gemini-flash-latest": 30e9,  # alias for latest flash
    "gemini-flash-lite-latest": 10e9,  # alias for latest flash-lite
    "gemini-live-2-5-flash": 30e9,
    "gemini-live-2-5-flash-preview-native-audio": 30e9,
    "gemini-embedding-001": 1e9,  # estimated embedding model
    # Gemini 3.x (next gen, no public counts yet - skip)
    # xAI Grok 4 family
    "grok-4": 3000e9,  # estimated next gen
    "grok-beta": 314e9,  # original grok-2 beta
    "grok-vision-beta": 314e9,
    "grok-code-fast-1": 314e9,  # grok-2 based
    # Moonshot/Kimi additional
    "kimi-k2-0711-preview": 1000e9,
    "kimi-k2-0905-preview": 1000e9,
    "kimi-k2-turbo-preview": 1000e9,
    "kimi-k2-thinking": 1000e9,
    "kimi-k2-thinking-turbo": 1000e9,
}


def normalize_name(filename):
    """Strip extensions and common suffixes to get a matchable name."""
    name = filename.replace(".md", "")
    return name.lower()


def strip_suffixes(name):
    """Progressively strip known suffixes for lookup matching."""
    # Order matters: strip most specific/longest first
    suffixes = [
        "-instruct-2507-fp8", "-instruct-2507",
        "-instruct-2506", "-instruct-2503", "-instruct-2501",
        "-instruct-2512-bf16", "-instruct-2512",
        "-instruct-fp8", "-instruct-awq", "-instruct-gptq-int4",
        "-instruct-hf", "-instruct",
        "-chat-hf", "-chat",
        "-hf", "-fp8", "-awq", "-gptq-int4", "-bf16",
        "-base-2512", "-base",
        "-v0-1", "-v0-2", "-v0-3",
        "-128k-instruct", "-4k-instruct",
    ]
    variants = [name]
    for suffix in suffixes:
        if name.endswith(suffix):
            variants.append(name[:-len(suffix)])
    return variants


def extract_params_from_name(name):
    """Match patterns like '7b', '70b', '1.5b', '1-5b', '0-5b', '235b' in model name."""
    # Match NNb pattern, allowing decimal via dot or hyphen
    m = re.search(r'(\d+(?:[.-]\d+)?)b(?:-|$|[^a-z])', name.lower())
    if m:
        size_str = m.group(1).replace('-', '.')
        return int(float(size_str) * 1e9)
    # Match NNm pattern for small models (millions)
    m = re.search(r'(\d+(?:[.-]\d+)?)m(?:-|$|[^a-z])', name.lower())
    if m:
        size_str = m.group(1).replace('-', '.')
        return int(float(size_str) * 1e6)
    return None


def lookup_params(filename):
    """Try to find parameter count via lookup table, then name extraction."""
    name = normalize_name(filename)

    # Try exact match and suffix-stripped variants against lookup table
    for variant in strip_suffixes(name):
        if variant in KNOWN_PARAMS:
            return int(KNOWN_PARAMS[variant]), "lookup"

    # Also try matching without date suffixes like -2506, -2507, -2024-05-13
    # Strip trailing date patterns: -YYMM or -YYYY-MM-DD
    date_stripped = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', name)
    date_stripped = re.sub(r'-\d{4}$', '', date_stripped)
    if date_stripped != name:
        for variant in strip_suffixes(date_stripped):
            if variant in KNOWN_PARAMS:
                return int(KNOWN_PARAMS[variant]), "lookup+date"

    # Also try matching without "-latest" suffix
    for suffix in ["-latest", "-latest-2024", "-latest-2025", "-preview"]:
        if name.endswith(suffix):
            base = name[:-len(suffix)]
            for variant in strip_suffixes(base):
                if variant in KNOWN_PARAMS:
                    return int(KNOWN_PARAMS[variant]), "lookup+suffix"

    # Try prefix matching for versioned models (e.g., "mistral-small-2603" -> "mistral-small")
    # Check each known key if name starts with it
    best_match = None
    best_len = 0
    for key, val in KNOWN_PARAMS.items():
        if name.startswith(key) and len(key) > best_len:
            # Make sure what follows is a separator or version suffix
            remainder = name[len(key):]
            if remainder == "" or remainder[0] in ("-", "_"):
                best_match = key
                best_len = len(key)
    if best_match:
        return int(KNOWN_PARAMS[best_match]), "prefix"

    # Try regex extraction from the filename itself
    params = extract_params_from_name(name)
    if params:
        return params, "regex"

    return None, None


def process_file(filepath):
    """Read a model card file, check if total_parameters is null, and fill it if possible."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Only process files that have total_parameters: null
    if '  total_parameters: null' not in content:
        return None, None, None

    filename = os.path.basename(filepath)
    params, method = lookup_params(filename)

    if params is None:
        return filename, None, None

    # Replace the null value with the actual parameter count
    new_content = content.replace(
        '  total_parameters: null',
        f'  total_parameters: {params}',
        1  # Only replace first occurrence
    )

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return filename, params, method

    return filename, None, None


def main():
    updated = []
    skipped = []
    already_set = 0
    total_files = 0

    for root, dirs, files in os.walk(MODELS_DIR):
        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            total_files += 1
            filepath = os.path.join(root, fname)

            # Quick check: skip if not null
            with open(filepath, 'r') as f:
                first_chunk = f.read(1500)
            if '  total_parameters: null' not in first_chunk:
                already_set += 1
                continue

            filename, params, method = process_file(filepath)
            if params is not None:
                updated.append((filename, params, method))
            elif filename is not None:
                skipped.append(filename)

    # Print summary
    print(f"\n{'='*70}")
    print(f"TOTAL MODEL CARDS SCANNED: {total_files}")
    print(f"ALREADY HAD total_parameters SET: {already_set}")
    print(f"UPDATED: {len(updated)}")
    print(f"SKIPPED (no match found): {len(skipped)}")
    print(f"{'='*70}\n")

    if updated:
        print("UPDATED FILES:")
        print(f"{'File':<60} {'Params':>15} {'Method':<15}")
        print("-" * 90)
        for fname, params, method in sorted(updated):
            if params >= 1e9:
                human = f"{params/1e9:.1f}B"
            elif params >= 1e6:
                human = f"{params/1e6:.1f}M"
            else:
                human = str(params)
            print(f"  {fname:<58} {human:>15} {method:<15}")

    if skipped:
        print(f"\nSKIPPED FILES (total_parameters still null):")
        for fname in sorted(skipped):
            print(f"  {fname}")


if __name__ == "__main__":
    main()
