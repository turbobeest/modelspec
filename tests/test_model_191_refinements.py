"""MODEL-191 refinement benchmark and finance-tag data guards."""

from __future__ import annotations

from pathlib import Path

import yaml

from schema.benchmark import BenchmarkCard

ROOT = Path(__file__).parents[1]

ARENA_REFINEMENT_IDS = {
    "arena_sc_english",
    "arena_sc_chinese",
    "arena_sc_japanese",
    "arena_sc_korean",
    "arena_sc_russian",
    "arena_sc_spanish",
    "arena_sc_german",
    "arena_sc_french",
    "arena_sc_polish",
    "arena_sc_vision_ocr",
    "arena_sc_vision_diagram",
    "arena_sc_vision_homework",
    "arena_sc_document",
    "arena_sc_industry_software_it_services",
    "arena_sc_industry_entertainment_sports_media",
    "arena_sc_industry_mathematical",
    "arena_sc_factuality",
}


def _front(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])


def test_refinement_benchmark_pages_are_valid_and_domain_tagged() -> None:
    for benchmark_id in sorted(ARENA_REFINEMENT_IDS):
        path = ROOT / "benchmarks" / f"{benchmark_id}.md"
        card = BenchmarkCard.model_validate(_front(path))
        assert card.id == benchmark_id
        assert card.domains
        assert card.dataset.license == "CC BY 4.0"


def test_finance_proxy_tags_cover_the_three_approved_benchmarks() -> None:
    for benchmark_id in ("arena_sc_business", "vending_bench_2", "tau3_banking"):
        card = _front(ROOT / "benchmarks" / f"{benchmark_id}.md")
        assert {"id": "finance", "directness": "proxy"} in card["domains"]


def test_finance_domain_accepts_direct_evidence() -> None:
    domains = yaml.safe_load((ROOT / "registry" / "domains.yaml").read_text())[
        "domains"
    ]
    finance = next(domain for domain in domains if domain["id"] == "finance")
    assert finance["proxy_only"] is False


def test_arena_refinement_sources_are_registered_live() -> None:
    sources = yaml.safe_load((ROOT / "registry" / "sources.yaml").read_text())["sources"]
    by_id = {source["id"]: source for source in sources}
    for config in ("text-style-control", "vision-style-control", "document", "text-factuality"):
        source = by_id[f"model-160-arena-{config}"]
        assert source["volatility"] == "live"
        assert "lmarena-ai/leaderboard-dataset" in source["url"]
