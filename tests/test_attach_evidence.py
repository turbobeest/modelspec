"""MODEL-32: ranking-evidence attach is explicit, dated, and schema-valid."""

from __future__ import annotations

from datetime import date
import pytest
from pydantic import ValidationError

from api.ranking.engine import USE_CASE_PROFILES
from schema.card import BenchmarkEvidence
from scripts.attach_evidence import LEDGER_TO_CARD, RANKING_LEDGER, load_accepted, to_evidence
from scripts.build_manifest import BENCHMARK_WRITE_RULE


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
    assert "Qwen3.8-Max" not in LEDGER_TO_CARD
    assert "Claude Opus 5 (high)" not in LEDGER_TO_CARD
    assert "GPT-6 Astra (high)" not in LEDGER_TO_CARD
    assert LEDGER_TO_CARD["Command A+"] == "cohere/command-a-plus-05-2026"
    assert LEDGER_TO_CARD["GLM-5.3 (max)"] == "zhipu/glm-5-3"
    assert LEDGER_TO_CARD["GLM-5.2 (max)"] == "zhipu/glm-5-2"
    assert LEDGER_TO_CARD["glm-5.2-max"] == "zhipu/glm-5-2"
    assert "GLM-5.2 (Non-reasoning)" not in LEDGER_TO_CARD
    assert LEDGER_TO_CARD["Inkling"] == "thinkingmachines/inkling"
    assert LEDGER_TO_CARD["inkling"] == "thinkingmachines/inkling"
    assert LEDGER_TO_CARD["Nemotron 3.5 Lightning"] == (
        "nvidia/nvidia-nemotron-3-5-lightning-30b-a3b"
    )
    assert LEDGER_TO_CARD["Nemotron 3 Ultra"] == "nvidia/nvidia-nemotron-3-ultra-550b-a55b"
    assert LEDGER_TO_CARD["Cogito v2.1"] == "deepcogito/cogito-671b-v2-1"
    assert LEDGER_TO_CARD["muse-glimmer"] == "meta/muse-glimmer-30b"
    assert LEDGER_TO_CARD["Claude 3 Haiku"] == "anthropic/claude-3-haiku-20240307"
    assert LEDGER_TO_CARD["Llama 4 Maverick"] == "meta/llama-4-maverick-17b-128e-instruct"
    assert LEDGER_TO_CARD["qwen3.8-max"] == "qwen/qwen3-8-max"
    assert LEDGER_TO_CARD["Gemini 2.5 Flash (Apr)"] == (
        "google/gemini-2-5-flash-preview-04-17"
    )


def test_model13_traps_are_not_mapped():
    """Effort, quant, sibling-size, and dataset names stay off the product cards."""
    forbidden = (
        "Muse Glimmer (high)",
        "nvidia-nemotron-3-ultra-550b-a55b-nvfp4",
        "nvidia-nemotron-3.5-lightning-30b-a3b-nvfp4",
        "rnj-1",
        "rnj-1-base-evals",
        "rnj-1-instruct",
        "Rnj-1 Instruct",
        "Llama 4 Scout",
        "Gemini 3 Flash",
        "gemini-3-flash",
        "Gemma 4 12B",
        "Qwen2 72B",
        "GLM-5.2 (Non-reasoning)",
    )
    for name in forbidden:
        assert name not in LEDGER_TO_CARD, name
    # Own cards, never the similarly-named sibling.
    assert LEDGER_TO_CARD["Llama Nemotron Ultra"] == (
        "nvidia/llama-3-1-nemotron-ultra-253b-v1"
    )
    assert LEDGER_TO_CARD["Llama Nemotron Ultra"] != (
        "nvidia/nvidia-nemotron-3-ultra-550b-a55b"
    )
    assert LEDGER_TO_CARD["Inkling Small"] == "thinkingmachines/inkling-small"
    assert LEDGER_TO_CARD["Inkling Small"] != "thinkingmachines/inkling"


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


def test_write_rule_states_live_vs_static_date_policy():
    text = BENCHMARK_WRITE_RULE.lower()
    assert "live leaderboard" in text
    assert "observation" in text
    assert "static" in text
    assert "refusal" in text


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


def test_leaderboard_ledger_rows_are_mapped_ranked_and_dated():
    ranked = ranked_benchmarks()
    rows = [
        (bid, raw)
        for bid, raw in load_accepted()
        if raw.get("source_kind") == "independent_evaluator"
    ]
    assert rows, "ranking ledger must include live-leaderboard independent_evaluator rows"
    unmapped = sorted({raw["model_id"] for _, raw in rows} - set(LEDGER_TO_CARD))
    assert unmapped == []
    unknown = sorted({bid for bid, _ in rows} - ranked)
    assert unknown == []
    live_urls = {
        "https://artificialanalysis.ai/leaderboards/models",
        "https://lmarena.ai/leaderboard",
    }
    live = [(bid, raw) for bid, raw in rows if raw.get("source_url") in live_urls]
    assert live, "ledger must include AA/LM Arena live-board rows"
    for bid, raw in live:
        record = to_evidence(bid, raw, "2026-09-10")
        assert record.date_type == "evaluated"
        assert record.source_kind == "independent_evaluator"
        assert record.evidence_date  # observation or stated day, never blank


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


def _evidence(model_id: str) -> list[dict]:
    from scripts.attach_evidence import _card_index
    import yaml

    path = _card_index()[model_id]
    front = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
    return list((front.get("benchmarks") or {}).get("evidence") or [])


def test_glm52_live_aa_arena_rows_are_on_the_product_card():
    """AA (max) and Arena glm-5.2-max attach to zhipu/glm-5-2; Non-reasoning does not."""
    rows = _evidence("zhipu/glm-5-2")
    names = {e.get("model_id_as_evaluated") for e in rows}
    assert "GLM-5.2 (max)" in names
    assert "glm-5.2-max" in names
    assert "GLM-5.2 (Non-reasoning)" not in names
    by_id = {e["benchmark_id"]: e for e in rows
             if e.get("model_id_as_evaluated") == "GLM-5.2 (max)"}
    assert by_id["gpqa_diamond"]["score"] == 89.49
    assert by_id["scicode"]["score"] == 51.16
    assert by_id["aa_lcr"]["score"] == 78.33
    assert by_id["gdpval_aa"]["score"] == 45.88
    assert by_id["critpt"]["score"] == 20.86
    arena = [
        e for e in rows
        if e.get("benchmark_id") == "arena_elo_style_control"
        and e.get("model_id_as_evaluated") == "glm-5.2-max"
    ]
    assert arena and arena[0]["score"] == 1471.72
    assert all(e.get("source_url", "").startswith("https://") for e in rows)
    assert all(e.get("date_type") == "evaluated" for e in rows)


def test_glm53_published_scicode_is_the_chart_correction():
    rows = [
        e for e in _evidence("zhipu/glm-5-3")
        if e.get("benchmark_id") == "scicode" and e.get("date_type") == "published"
    ]
    assert rows, "GLM-5.3 must carry the dated AA v4.2 SciCode score"
    assert rows[0]["score"] == 59.0
    assert "reasoning_effort=max" in (rows[0].get("configuration") or "")


def test_glm53_flash_has_no_published_eligibility_gdpval():
    rows = [
        e for e in _evidence("zhipu/glm-5-3-flash")
        if e.get("benchmark_id") == "gdpval_aa" and e.get("date_type") == "published"
    ]
    assert rows == []
    live = [
        e for e in _evidence("zhipu/glm-5-3-flash")
        if e.get("benchmark_id") == "gdpval_aa" and e.get("score") == 59.0
    ]
    assert live == [], "stale cache copied 59 onto Flash; do not attach it"


def test_rnj1_instruct_has_no_dataset_evidence():
    rows = _evidence("essentialai/rnj-1-instruct")
    assert rows == []
    for e in rows:
        assert "rnj-1-base-evals" not in (e.get("model_id_as_evaluated") or "")


def test_muse_glimmer_high_is_not_on_the_card():
    names = {e.get("model_id_as_evaluated") for e in _evidence("meta/muse-glimmer-30b")}
    assert "Muse Glimmer (high)" not in names


def test_model13_rescued_live_rows_are_on_the_new_cards():
    inkling = {e["benchmark_id"] for e in _evidence("thinkingmachines/inkling")}
    assert {"aa_lcr", "gpqa_diamond", "scicode", "gdpval_aa", "critpt",
            "arena_elo_style_control"} <= inkling
    lightning = {e["benchmark_id"] for e in _evidence(
        "nvidia/nvidia-nemotron-3-5-lightning-30b-a3b"
    )}
    assert {"aa_lcr", "gpqa_diamond", "scicode", "gdpval_aa", "critpt"} <= lightning
    ultra = {e["benchmark_id"] for e in _evidence(
        "nvidia/nvidia-nemotron-3-ultra-550b-a55b"
    )}
    assert {"aa_lcr", "gpqa_diamond", "scicode", "gdpval_aa", "critpt"} <= ultra
    cogito = {e["benchmark_id"] for e in _evidence("deepcogito/cogito-671b-v2-1")}
    assert {"aa_lcr", "gpqa_diamond", "critpt"} <= cogito
    glimmer = {e["benchmark_id"] for e in _evidence("meta/muse-glimmer-30b")}
    assert "arena_elo_style_control" in glimmer
