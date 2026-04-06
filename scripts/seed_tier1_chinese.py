#!/usr/bin/env python3
"""Seed ModelSpec cards for Tier 1 Chinese and regional providers.

Uses HuggingFace Hub API via the shared seed_huggingface utility.
"""

import sys
import time
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.seed_huggingface import seed_org, HFProviderConfig

configs = [
    # Tencent Hunyuan
    HFProviderConfig(
        hf_org="tencent",
        provider_slug="tencent",
        provider_display="Tencent",
        country="CN",
        limit=30,
        min_downloads=200,
    ),

    # Zhipu / THUDM (GLM, CogVideo) — migrated to zai-org on HF
    HFProviderConfig(
        hf_org="zai-org",
        provider_slug="zhipu",
        provider_display="Zhipu AI",
        country="CN",
        limit=40,
        min_downloads=500,
    ),

    # 01.AI (Yi)
    HFProviderConfig(
        hf_org="01-ai",
        provider_slug="01-ai",
        provider_display="01.AI",
        country="CN",
        limit=30,
        min_downloads=500,
    ),

    # Baichuan
    HFProviderConfig(
        hf_org="baichuan-inc",
        provider_slug="baichuan",
        provider_display="Baichuan",
        country="CN",
        limit=20,
        min_downloads=200,
    ),

    # Qwen — fill gaps (Qwen-Audio, Qwen-VL, Qwen-Embedding, etc.)
    HFProviderConfig(
        hf_org="Qwen",
        provider_slug="qwen",
        provider_display="Alibaba / Qwen Team",
        country="CN",
        limit=80,
        min_downloads=500,
    ),

    # Samsung SDS Research (SGuard safety models)
    HFProviderConfig(
        hf_org="SamsungSDS-Research",
        provider_slug="samsung",
        provider_display="Samsung",
        country="KR",
        limit=10,
        min_downloads=100,
    ),

    # Kakao Brain
    HFProviderConfig(
        hf_org="kakaobrain",
        provider_slug="kakao",
        provider_display="Kakao Brain",
        country="KR",
        limit=10,
        min_downloads=200,
    ),

    # DeepSeek — fill gaps
    HFProviderConfig(
        hf_org="deepseek-ai",
        provider_slug="deepseek",
        provider_display="DeepSeek",
        country="CN",
        limit=30,
        min_downloads=500,
    ),
]


def main():
    print("=" * 60)
    print("  Tier 1 Chinese & Regional Provider Seeder")
    print("=" * 60)

    summary: dict[str, int] = {}
    total_created = 0

    for i, config in enumerate(configs):
        try:
            created = seed_org(config, verbose=True)
            summary[config.provider_slug] = len(created)
            total_created += len(created)
        except Exception as e:
            print(f"\n  FATAL ERROR for {config.provider_slug}: {e}")
            summary[config.provider_slug] = -1

        # Sleep between providers to avoid rate limiting (skip after last)
        if i < len(configs) - 1:
            time.sleep(0.5)

    # Final summary
    print("\n")
    print("=" * 60)
    print("  FINAL SUMMARY")
    print("=" * 60)
    for slug, count in summary.items():
        status = f"{count} cards created" if count >= 0 else "FAILED"
        print(f"  {slug:20s} {status}")
    print(f"\n  Total new cards: {total_created}")
    print("=" * 60)


if __name__ == "__main__":
    main()
