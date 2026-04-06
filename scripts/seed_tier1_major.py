#!/usr/bin/env python3
"""Seed model cards for Tier 1 major providers using HuggingFace Hub API.

Covers: NVIDIA, Microsoft, IBM Granite, Stability AI, Black Forest Labs,
RWKV, TII (Falcon), AI21 Labs, plus gap-filling for Meta and Google.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.seed_huggingface import seed_org, HFProviderConfig

configs: list[HFProviderConfig] = [
    # NVIDIA
    HFProviderConfig(
        hf_org="nvidia",
        provider_slug="nvidia",
        provider_display="NVIDIA",
        country="US",
        limit=50,
        min_downloads=500,
    ),

    # Microsoft
    HFProviderConfig(
        hf_org="microsoft",
        provider_slug="microsoft",
        provider_display="Microsoft",
        country="US",
        limit=50,
        min_downloads=1000,
    ),

    # IBM Granite
    HFProviderConfig(
        hf_org="ibm-granite",
        provider_slug="ibm",
        provider_display="IBM",
        country="US",
        limit=40,
        min_downloads=500,
    ),

    # Stability AI
    HFProviderConfig(
        hf_org="stabilityai",
        provider_slug="stability",
        provider_display="Stability AI",
        country="GB",
        limit=30,
        min_downloads=1000,
    ),

    # Black Forest Labs (FLUX)
    HFProviderConfig(
        hf_org="black-forest-labs",
        provider_slug="black-forest-labs",
        provider_display="Black Forest Labs",
        country="DE",
        limit=20,
        min_downloads=500,
    ),

    # RWKV
    HFProviderConfig(
        hf_org="RWKV",
        provider_slug="rwkv",
        provider_display="RWKV Foundation",
        country="",
        org_type="open-collective",
        limit=20,
        min_downloads=500,
    ),

    # TII (Falcon)
    HFProviderConfig(
        hf_org="tiiuae",
        provider_slug="tii",
        provider_display="TII",
        country="AE",
        limit=30,
        min_downloads=500,
    ),

    # AI21 Labs
    HFProviderConfig(
        hf_org="ai21labs",
        provider_slug="ai21",
        provider_display="AI21 Labs",
        country="IL",
        limit=20,
        min_downloads=200,
    ),

    # Meta — fill gaps (Llama Guard, Code Llama, etc.)
    HFProviderConfig(
        hf_org="meta-llama",
        provider_slug="meta",
        provider_display="Meta",
        country="US",
        limit=80,
        min_downloads=500,
    ),

    # Google — fill gaps (PaliGemma, MedGemma, ShieldGemma, etc.)
    HFProviderConfig(
        hf_org="google",
        provider_slug="google",
        provider_display="Google DeepMind",
        country="US",
        limit=80,
        min_downloads=1000,
    ),
]


def main() -> None:
    print("=" * 70)
    print("  Tier 1 Major Providers — HuggingFace Seeder")
    print("=" * 70)
    print(f"  Providers: {len(configs)}")
    print()

    results: dict[str, list[str]] = {}
    failures: list[tuple[str, str]] = []

    for i, cfg in enumerate(configs):
        try:
            created = seed_org(cfg, verbose=True)
            results[cfg.provider_slug] = created
        except Exception as exc:
            print(f"  PROVIDER FAILED: {cfg.hf_org} — {exc}")
            results[cfg.provider_slug] = []
            failures.append((cfg.hf_org, str(exc)))

        # Small sleep between providers to avoid rate limiting
        if i < len(configs) - 1:
            time.sleep(0.5)

    # ── Summary ───────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    grand_total = 0
    for slug, created_ids in results.items():
        count = len(created_ids)
        grand_total += count
        marker = "  ✓" if count > 0 else "  –"
        print(f"  {marker} {slug:25s} {count:4d} new cards")

    print(f"\n  Grand total: {grand_total} new model cards created")

    if failures:
        print(f"\n  Failures ({len(failures)}):")
        for org, err in failures:
            print(f"    - {org}: {err}")

    print()


if __name__ == "__main__":
    main()
