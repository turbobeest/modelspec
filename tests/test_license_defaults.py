"""MODEL-85: a seeder must not guess a licence.

`scripts/enrich_cards.py` used to fill missing `license_type` from a provider
table. Cerebras defaulted to `llama-community` because it also hosts Llama,
which wrote Llama's licence onto GPT-OSS, Qwen, and GLM. A missing licence
stays null.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.card import Identity, Licensing, ModelCard  # noqa: E402
from schema.enums import LicenseType  # noqa: E402
from scripts.enrich_cards import enrich_license, infer_license  # noqa: E402
from scripts.seed_huggingface import map_license  # noqa: E402
from scripts.seed_models_dev import build_model_card  # noqa: E402
import scripts.enrich_cards as enrich_cards  # noqa: E402


def _card(
    model_id: str,
    provider: str,
    *,
    family: str = "",
    tags: list[str] | None = None,
    open_weights: bool = True,
) -> ModelCard:
    return ModelCard(
        identity=Identity(
            model_id=model_id,
            display_name=model_id.split("/")[-1],
            provider=provider,
            family=family,
            tags=tags or [],
        ),
        licensing=Licensing(open_weights=open_weights),
    )


def _front(model_id: str) -> dict:
    provider, slug = model_id.split("/", 1)
    path = REPO_ROOT / "models" / provider / f"{slug}.md"
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])


def test_provider_license_table_is_gone() -> None:
    assert not hasattr(enrich_cards, "PROVIDER_LICENSE")


def test_infer_license_does_not_default_llama_community_for_cerebras() -> None:
    card = _card("cerebras/gpt-oss-120b", "cerebras")
    assert infer_license(card) is None
    assert enrich_license(card) is False
    assert card.licensing.license_type is None


def test_infer_license_does_not_guess_from_provider_or_name() -> None:
    cases = [
        _card("cerebras/gpt-oss-120b", "openai"),
        _card("cerebras/qwen-3-235b-a22b-instruct-2507", "qwen", family="qwen"),
        _card("cerebras/zai-glm-4-7", "zhipu"),
        _card("meta/llama-3-1-8b", "meta", family="llama"),
        _card("google/gemma-3-27b", "google", family="gemma"),
        _card("acme/mystery", "acme", tags=["apache-2.0"]),
        _card("openai/gpt-4o", "openai", open_weights=False),
    ]
    for card in cases:
        assert infer_license(card) is None, card.identity.model_id
        assert enrich_license(card) is False, card.identity.model_id
        assert card.licensing.license_type is None, card.identity.model_id


def test_enrich_license_does_not_overwrite_a_sourced_licence() -> None:
    card = _card("openai/gpt-oss-120b", "openai")
    card.licensing.license_type = LicenseType.APACHE_2_0
    assert enrich_license(card) is False
    assert card.licensing.license_type is LicenseType.APACHE_2_0


def test_models_dev_seeder_does_not_set_a_licence() -> None:
    card = build_model_card(
        {
            "id": "gpt-oss-120b",
            "name": "GPT OSS 120B",
            "open_weights": True,
            "modalities": {"input": ["text"], "output": ["text"]},
        },
        "cerebras",
        {"slug": "cerebras", "display": "Cerebras", "country": "US"},
    )
    assert card.licensing.license_type is None


def test_empty_hf_license_is_not_llama_community() -> None:
    license_type, _ = map_license({"license": "", "tags": []})
    assert license_type is None


def test_stated_llama31_still_maps_to_llama_community() -> None:
    license_type, _ = map_license({"license": "llama3.1", "tags": []})
    assert license_type is LicenseType.LLAMA_COMMUNITY


def test_named_cerebras_cards_no_longer_carry_llama_community() -> None:
    assert _front("cerebras/gpt-oss-120b")["licensing"]["license_type"] == "apache-2.0"
    assert _front("cerebras/qwen-3-235b-a22b-instruct-2507")["licensing"]["license_type"] == "apache-2.0"
    assert _front("cerebras/zai-glm-4-7")["licensing"]["license_type"] == "mit"


def test_muse_spark_no_longer_carries_the_llama_default() -> None:
    assert _front("meta/muse-spark")["licensing"]["license_type"] is None


def test_llama_3_1_8b_base_does_not_claim_cerebras() -> None:
    cerebras = _front("meta/llama-3-1-8b")["availability"]["cerebras"]
    assert cerebras["available"] is False


def test_llama_3_1_8b_instruct_still_records_cerebras() -> None:
    cerebras = _front("meta/llama-3-1-8b-instruct")["availability"]["cerebras"]
    assert cerebras["model_id"] == "llama3.1-8b"
    assert cerebras["url"] == "https://inference-docs.cerebras.ai/models/llama-31-8b"
