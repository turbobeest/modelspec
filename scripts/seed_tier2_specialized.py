#!/usr/bin/env python3
"""Seed model cards for Tier 2 specialized model makers from HuggingFace Hub.

Covers: Allen AI, Databricks, Snowflake, Salesforce, Together AI, Recraft,
        Liquid AI, Moondream, Nous Research, Teknium, Unsloth, Mistral (gap fill).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.seed_huggingface import seed_org, HFProviderConfig

configs = [
    # Allen AI (OLMo, Molmo, Tulu)
    HFProviderConfig(hf_org="allenai", provider_slug="allen-ai", provider_display="Allen AI",
                     country="US", org_type="nonprofit", limit=30, min_downloads=500),

    # Databricks (DBRX)
    HFProviderConfig(hf_org="databricks", provider_slug="databricks", provider_display="Databricks",
                     country="US", limit=15, min_downloads=200),

    # Snowflake (Arctic)
    HFProviderConfig(hf_org="Snowflake", provider_slug="snowflake", provider_display="Snowflake",
                     country="US", limit=15, min_downloads=200),

    # Salesforce (CodeGen, BLIP, xGen)
    HFProviderConfig(hf_org="Salesforce", provider_slug="salesforce", provider_display="Salesforce",
                     country="US", limit=30, min_downloads=500),

    # Together (StripedHyena, RedPajama)
    HFProviderConfig(hf_org="togethercomputer", provider_slug="together", provider_display="Together AI",
                     country="US", limit=15, min_downloads=200),

    # Recraft
    HFProviderConfig(hf_org="recraft-ai", provider_slug="recraft", provider_display="Recraft",
                     country="", limit=10, min_downloads=100),

    # Liquid AI
    HFProviderConfig(hf_org="LiquidAI", provider_slug="liquid", provider_display="Liquid AI",
                     country="US", limit=10, min_downloads=100),

    # Moondream
    HFProviderConfig(hf_org="vikhyatk", provider_slug="moondream", provider_display="Moondream",
                     country="US", limit=10, min_downloads=200),

    # Nous Research
    HFProviderConfig(hf_org="NousResearch", provider_slug="nous-research", provider_display="Nous Research",
                     country="US", org_type="open-collective", limit=20, min_downloads=500),

    # Teknium (OpenHermes)
    HFProviderConfig(hf_org="teknium", provider_slug="teknium", provider_display="Teknium",
                     country="US", org_type="open-collective", limit=10, min_downloads=500),

    # Unsloth
    HFProviderConfig(hf_org="unsloth", provider_slug="unsloth", provider_display="Unsloth",
                     country="US", limit=20, min_downloads=1000),

    # Mistral — fill gaps
    HFProviderConfig(hf_org="mistralai", provider_slug="mistral", provider_display="Mistral AI",
                     country="FR", limit=30, min_downloads=500),
]


def main() -> None:
    print("=" * 60)
    print("  Tier 2 Specialized Model Seeding")
    print("=" * 60)

    summary: dict[str, int] = {}
    total_created = 0
    total_errors = 0

    for i, config in enumerate(configs):
        try:
            created = seed_org(config, verbose=True)
            summary[config.provider_display] = len(created)
            total_created += len(created)
        except Exception as e:
            print(f"\n  FATAL ERROR for {config.provider_display}: {e}")
            summary[config.provider_display] = -1
            total_errors += 1

        # Sleep between providers (skip after last)
        if i < len(configs) - 1:
            time.sleep(0.5)

    # Print summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for provider, count in summary.items():
        status = f"{count} created" if count >= 0 else "FAILED"
        print(f"  {provider:25s} {status}")
    print(f"\n  Total new cards: {total_created}")
    if total_errors:
        print(f"  Providers with errors: {total_errors}")
    print("=" * 60)


if __name__ == "__main__":
    main()
