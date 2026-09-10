"""MODEL-32: ranking-evidence attach is explicit, dated, and schema-valid."""

from __future__ import annotations

from datetime import date
import pytest
from pydantic import ValidationError

from api.ranking.engine import USE_CASE_PROFILES
from schema.card import BenchmarkEvidence
from scripts.attach_evidence import LEDGER_TO_CARD, RANKING_LEDGER, load_accepted, to_evidence


def ranked_benchmarks() -> set[str]:
    keys: set[str] = set()
    for profile in USE_CASE_PROFILES.values():
        keys.update((profile.get("benchmark_weights") or {}).keys())
    return keys


def ranking_accepted() -> list[tuple[str, dict]]:
    return [
        (bid, raw)
        for bid, raw in load_accepted()
        if raw.get("source_kind") == "provider_self_report"
    ]


def test_ledger_to_card_is_explicit_dict():
    assert isinstance(LEDGER_TO_CARD, dict)
    assert "GPT-6 Astra (max)" in LEDGER_TO_CARD
    assert "GLM-5.3 (max)" not in LEDGER_TO_CARD
    assert "Qwen3.8-Max" not in LEDGER_TO_CARD


def test_every_mapped_id_has_a_card_file():
    from scripts.attach_evidence import _card_index

    found = set(_card_index())
    missing = sorted(set(LEDGER_TO_CARD.values()) - found)
    assert missing == []


def test_ranking_ledger_exists_and_loads():
    assert RANKING_LEDGER.is_file()
    rows = ranking_accepted()
    assert rows, "ranking_evidence/accepted.json must carry provider self-reports"


def test_ranking_ledger_keys_are_in_the_ranked_set():
    ranked = ranked_benchmarks()
    unknown = sorted({bid for bid, _ in ranking_accepted()} - ranked)
    assert unknown == []


def test_ranking_ledger_models_are_in_the_explicit_map():
    unmapped = sorted({raw["model_id"] for _, raw in ranking_accepted()} - set(LEDGER_TO_CARD))
    assert unmapped == []


def test_ranking_rows_validate_as_card_evidence():
    today = date.today().isoformat()
    for bid, raw in ranking_accepted():
        record = to_evidence(bid, raw, today)
        assert record.benchmark_id == bid
        assert record.source_url.startswith("https://")
        date.fromisoformat(record.evidence_date)
        date.fromisoformat(record.verified_at)


def test_schema_rejects_a_month_only_evidence_date():
    with pytest.raises(ValidationError):
        BenchmarkEvidence(
            benchmark_id="gpqa_diamond",
            model_id_as_evaluated="example",
            score=1.0,
            unit="percent",
            source_url="https://example.com/page",
            source_kind="provider_self_report",
            evidence_date="2026-09",
            date_type="published",
            verified_at="2026-09-09",
        )


def test_forbidden_variants_are_not_forced_into_ranked_keys():
    """Terminal-Bench 2.1, SWE-bench Pro, LiveCodeBench v5/v6 are not ranked keys."""
    bids = {bid for bid, _ in ranking_accepted()}
    assert "terminal_bench" not in bids
    versions = " ".join(
        raw.get("benchmark_version", "") for _, raw in ranking_accepted()
    ).lower()
    assert "terminal-bench 2.1" not in versions
    assert "swe-bench pro" not in versions
    assert "livecodebench v5" not in versions
    assert "livecodebench v6" not in versions
