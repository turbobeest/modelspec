#!/usr/bin/env python3
"""Seed Tier 3 (embeddings, rerankers) and Tier 4 (safety, reward) model cards.

Uses the HuggingFace Hub API via the shared scraper utility.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.seed_huggingface import seed_org, seed_api_model, HFProviderConfig
from schema.enums import ModelType, LicenseType


def main():
    results: dict[str, list[str]] = {}

    # ── Tier 3: Embedding & Reranker Providers (HF org-based) ────────

    tier3_configs = [
        # Jina AI
        HFProviderConfig(
            hf_org="jinaai", provider_slug="jina", provider_display="Jina AI",
            country="DE", limit=20, min_downloads=200,
        ),
        # Nomic AI
        HFProviderConfig(
            hf_org="nomic-ai", provider_slug="nomic", provider_display="Nomic AI",
            country="US", limit=15, min_downloads=200,
        ),
        # BAAI (BGE models)
        HFProviderConfig(
            hf_org="BAAI", provider_slug="baai", provider_display="BAAI",
            country="CN", org_type="academic", limit=30, min_downloads=500,
        ),
        # Sentence Transformers
        HFProviderConfig(
            hf_org="sentence-transformers", provider_slug="sentence-transformers",
            provider_display="Sentence Transformers", country="",
            org_type="open-collective", limit=20, min_downloads=5000,
        ),
        # intfloat (E5 models)
        HFProviderConfig(
            hf_org="intfloat", provider_slug="intfloat", provider_display="intfloat",
            country="", org_type="open-collective", limit=15, min_downloads=500,
        ),
    ]

    print("=" * 70)
    print("  TIER 3: Embedding & Reranker Models (HuggingFace orgs)")
    print("=" * 70)

    for config in tier3_configs:
        try:
            created = seed_org(config)
            results[config.provider_slug] = created
        except Exception as e:
            print(f"  ERROR seeding {config.hf_org}: {e}")
            results[config.provider_slug] = []
        time.sleep(0.5)

    # ── Tier 3: Voyage AI (API-only embedding models) ────────────────

    print(f"\n{'=' * 70}")
    print("  TIER 3: Voyage AI (API-only embedding models)")
    print("=" * 70)

    voyage_models = [
        ("Voyage 3", "voyage-3", 1024, None),
        ("Voyage 3 Lite", "voyage-3-lite", 512, None),
        ("Voyage Code 3", "voyage-code-3", 1024, None),
        ("Voyage Multilingual 2", "voyage-multilingual-2", 1024, None),
        ("Voyage Finance 2", "voyage-finance-2", 1024, None),
        ("Voyage Law 2", "voyage-law-2", 1024, None),
    ]

    voyage_created = []
    for name, slug, dims, params in voyage_models:
        try:
            mid = seed_api_model(
                model_id=f"voyage/{slug}",
                display_name=name,
                provider_slug="voyage",
                provider_display="Voyage AI",
                country="US",
                model_type=ModelType.EMBEDDING_TEXT,
                license_type=LicenseType.PROPRIETARY,
                open_weights=False,
                tags=["embedding", "api-only"],
            )
            if mid:
                voyage_created.append(mid)
                print(f"  Created: {mid}")
            else:
                print(f"  Skipped (exists): voyage/{slug}")
        except Exception as e:
            print(f"  ERROR creating voyage/{slug}: {e}")

    results["voyage"] = voyage_created

    # ── Tier 4: Safety, Reward, and Judge Models ─────────────────────

    print(f"\n{'=' * 70}")
    print("  TIER 4: Safety, Reward, and Judge Models")
    print("=" * 70)

    safety_configs = [
        # Meta Llama Guard
        HFProviderConfig(
            hf_org="meta-llama", provider_slug="meta", provider_display="Meta",
            country="US", limit=20, min_downloads=100,
            extra_search="guard",
        ),
        # Google ShieldGemma
        HFProviderConfig(
            hf_org="google", provider_slug="google", provider_display="Google DeepMind",
            country="US", limit=10, min_downloads=100,
            extra_search="shield",
        ),
        # Skywork Reward
        HFProviderConfig(
            hf_org="Skywork", provider_slug="skywork", provider_display="Skywork",
            country="CN", limit=10, min_downloads=200,
        ),
        # OpenBMB
        HFProviderConfig(
            hf_org="openbmb", provider_slug="openbmb", provider_display="OpenBMB",
            country="CN", org_type="academic", limit=15, min_downloads=200,
        ),
    ]

    for config in safety_configs:
        try:
            created = seed_org(config)
            results[config.provider_slug] = results.get(config.provider_slug, []) + created
        except Exception as e:
            print(f"  ERROR seeding {config.hf_org}: {e}")
            if config.provider_slug not in results:
                results[config.provider_slug] = []
        time.sleep(0.5)

    # ── Summary ──────────────────────────────────────────────────────

    print(f"\n{'=' * 70}")
    print("  SEEDING SUMMARY")
    print("=" * 70)

    # Count by type — read back the created cards to classify
    total_embedding = 0
    total_reranker = 0
    total_safety_reward = 0
    grand_total = 0

    for provider, created_ids in sorted(results.items()):
        count = len(created_ids)
        grand_total += count
        print(f"\n  {provider}: {count} new cards")
        for mid in created_ids:
            # Classify by reading back the card
            slug = mid.split("/", 1)[-1] if "/" in mid else mid
            card_path = PROJECT_ROOT / "models" / provider / f"{slug}.md"
            card_type = _read_card_type(card_path)
            type_label = card_type or "unknown"
            print(f"    - {mid} [{type_label}]")

            if card_type in ("embedding-text", "embedding-multimodal", "embedding-code"):
                total_embedding += 1
            elif card_type == "reranker":
                total_reranker += 1
            elif card_type in ("safety-classifier", "reward-model"):
                total_safety_reward += 1

    print(f"\n{'─' * 50}")
    print(f"  Total embedding models:       {total_embedding}")
    print(f"  Total reranker models:         {total_reranker}")
    print(f"  Total safety/reward models:    {total_safety_reward}")
    print(f"  Other models:                  {grand_total - total_embedding - total_reranker - total_safety_reward}")
    print(f"  Grand total new cards:         {grand_total}")
    print(f"{'─' * 50}")


def _read_card_type(card_path: Path) -> str | None:
    """Read the model_type from a card's YAML frontmatter."""
    if not card_path.exists():
        return None
    try:
        import yaml
        text = card_path.read_text()
        if text.startswith("---"):
            # Extract YAML between --- markers
            parts = text.split("---", 2)
            if len(parts) >= 3:
                data = yaml.safe_load(parts[1])
                return data.get("model_type", None)
    except Exception:
        pass
    return None


if __name__ == "__main__":
    main()
