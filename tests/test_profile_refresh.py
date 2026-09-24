"""MODEL-123: the profiles rest on current, sourced benchmarks.

The MODEL-108 audit (docs/audits/2026-09-staleness.md) found that the use-case
profiles weighted benchmarks nobody runs on new models, and that the
normalisation bounds clipped the frontier flat. These tests pin the refresh so
it cannot quietly decay again:

* **The guard.** Every active profile must be able to rank a current-generation
  model from current, non-Artificial-Analysis sources alone, at the CLI floor.
  No weighted benchmark may sit on a page its own authors mark superseded or
  saturated, unless Jamie approved that key by name.
* **Bounds.** A percentage benchmark's ceiling is 100. Arena is normalised
  within one pinned snapshot, never against a fixed Elo bound.
* **Evidence rules.** A live reading older than `STALE_AFTER_DAYS` is flagged
  and still counts. An independent reading beats a provider self-report for
  the same key; among rows of one kind, the highest reasoning effort wins.
"""

from __future__ import annotations

import ast
import math
import re
from datetime import date
from pathlib import Path

import pytest
import yaml

from api.ranking import engine
from api.ranking.engine import (
    APPROVED_DESPITE_SATURATION,
    ARENA_SNAPSHOT,
    BENCHMARK_RANGES,
    CURRENT_SOURCES,
    MIN_BENCHMARK_COVERAGE,
    STALE_AFTER_DAYS,
    USE_CASE_PROFILES,
    _benchmark_evidence,
    _normalize_arena,
    ranking_policy,
)
from pipeline.ranking import (
    FEATURED_PROFILES,
    Candidate,
    build_candidates,
    rank_report,
    score,
)
from schema.card import ModelCard
from schema.graph import CollectingSink

REPO = Path(__file__).resolve().parents[1]
BENCHMARKS = REPO / "benchmarks"

#: Keys whose only data source is Artificial Analysis. MODEL-117: AA's terms
#: forbid our use of its numbers, so no profile weight may depend on one.
AA_KEYS = {"aa_briefcase", "aa_lcr", "aa_omniscience", "automationbench_aa",
           "gdp_pdf_aa", "gdpval_aa", "scicode", "critpt",
           "artificial_analysis_quality_index"}


def _page(key: str) -> dict:
    path = BENCHMARKS / f"{key}.md"
    assert path.exists(), f"weighted benchmark {key!r} has no page"
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])


def _active() -> dict[str, dict]:
    return {k: p for k, p in USE_CASE_PROFILES.items() if p.get("status") != "suspended"}


def _base_weights(key: str) -> dict[str, float]:
    """A profile's own weights, without the MODEL-32 verified additions."""
    additions = set(getattr(engine, "VERIFIED_ADDITIONS", {}).get(key, []))
    return {b: w for b, w in USE_CASE_PROFILES[key]["benchmark_weights"].items()
            if b not in additions}


# ── the guard ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("key", sorted(_active()))
def test_every_active_profile_can_rank_a_current_model_from_current_sources(key):
    """Strict live coverage: weight on keys a 2026 model can get today, non-AA.

    `CURRENT_SOURCES` names, per key, where a current-generation model's score
    comes from. A key that is not in it (dead, static, or AA-only) earns
    nothing here. If this fails, a profile has drifted back onto benchmarks
    that new models are not run on, and the CLI floor will rank none of them.
    """
    weights = USE_CASE_PROFILES[key]["benchmark_weights"]
    total = sum(weights.values())
    live = sum(w for b, w in weights.items() if b in CURRENT_SOURCES and b not in AA_KEYS)
    assert live / total + 1e-9 >= MIN_BENCHMARK_COVERAGE, (
        f"{key}: only {live / total:.2f} of the weight has a current non-AA source")


def test_every_current_source_names_where_the_number_comes_from():
    for key, sources in CURRENT_SOURCES.items():
        assert sources, key
        for source in sources:
            assert source.startswith("https://"), (key, source)
        assert key not in AA_KEYS, f"{key} is AA-only and cannot be a current source"


@pytest.mark.parametrize("key", sorted(USE_CASE_PROFILES))
def test_no_new_profile_weight_depends_on_an_aa_key(key):
    """MODEL-117. The verified additions are left to the AA-removal PR."""
    assert not set(_base_weights(key)) & AA_KEYS


def _weighted_keys() -> set[str]:
    return {b for p in _active().values() for b in p["benchmark_weights"]
            if b not in AA_KEYS}


@pytest.mark.parametrize("key", sorted(_weighted_keys()))
def test_no_weighted_key_sits_on_a_superseded_or_saturated_page(key):
    page = _page(key)
    marked = page.get("status") in {"superseded", "saturated", "deprecated"} or (
        (page.get("saturation") or {}).get("status") == "saturated")
    if marked:
        assert key in APPROVED_DESPITE_SATURATION, (
            f"{key} is marked {page.get('status')}/"
            f"{(page.get('saturation') or {}).get('status')} on its own page")


def test_saturation_exceptions_are_few_named_and_still_saturated():
    """An exception that no longer needs to be one should be removed."""
    assert len(APPROVED_DESPITE_SATURATION) <= 4
    for key, why in APPROVED_DESPITE_SATURATION.items():
        assert "MODEL-123" in why
        page = _page(key)
        assert (page.get("saturation") or {}).get("status") == "saturated" or \
            page.get("status") == "saturated", f"{key} is no longer saturated; drop it"


@pytest.mark.parametrize("key", sorted(USE_CASE_PROFILES))
def test_weights_sum_to_one_and_have_a_range_or_a_snapshot(key):
    weights = USE_CASE_PROFILES[key]["benchmark_weights"]
    assert math.isclose(sum(weights.values()), 1.0, abs_tol=1e-3), key
    for bench in USE_CASE_PROFILES[key]["benchmark_weights"]:
        assert bench in BENCHMARK_RANGES or bench in ARENA_SNAPSHOT["boards"] \
            or bench == "clip_score", f"{key}: {bench} has no normalisation"


def test_a_retired_key_is_weighted_nowhere():
    from api.ranking.engine import RETIRED_FROM_PROFILES
    for key, profile in USE_CASE_PROFILES.items():
        assert not set(profile["benchmark_weights"]) & RETIRED_FROM_PROFILES, key


def test_suspended_profiles_say_why_and_are_not_featured():
    suspended = {k for k, p in USE_CASE_PROFILES.items() if p.get("status") == "suspended"}
    assert {"speech_to_text", "text_to_speech"} <= suspended
    for key in suspended:
        assert USE_CASE_PROFILES[key].get("suspended_reason", "").strip(), key
        assert key not in FEATURED_PROFILES


def test_text_to_speech_does_not_rank_a_chat_llm():
    """It used to: its only filled keys were Arena and MT-Bench (MODEL-108 §4.7)."""
    llm = Candidate("anthropic/claude-opus-4-6", "Claude Opus 4.6", "Anthropic", "llm-chat",
                    benchmark_scores={b: 1500.0 for b in ARENA_SNAPSHOT["boards"]}
                    | {"mt_bench": 9.0, "arena_elo_overall": 1400.0})
    assert score(llm, USE_CASE_PROFILES["text_to_speech"])["rank_status"] == "unranked"
    weights = USE_CASE_PROFILES["text_to_speech"]["benchmark_weights"]
    assert not any(b.startswith("arena_") or b == "mt_bench" for b in weights)


# ── bounds ───────────────────────────────────────────────────────────────────

def test_the_ranges_literal_defines_each_benchmark_once():
    """`hle` was defined twice; the later entry silently won (MODEL-108 §5)."""
    tree = ast.parse((REPO / "api/ranking/engine.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            dupes = {k for k in keys if keys.count(k) > 1}
            assert not dupes, f"duplicate keys in a dict literal: {sorted(dupes)}"


@pytest.mark.parametrize("key", sorted(BENCHMARK_RANGES))
def test_a_percentage_benchmark_has_the_natural_ceiling(key):
    path = BENCHMARKS / f"{key}.md"
    if not path.exists():
        pytest.skip("no page to read the unit from")
    unit = (_page(key).get("metric") or {}).get("unit")
    if unit not in ("%", "F1 x100"):
        pytest.skip(f"unit {unit!r} is not a percentage")
    assert BENCHMARK_RANGES[key][1] == 100.0, (
        f"{key} is a percentage but its ceiling is {BENCHMARK_RANGES[key][1]}")


def test_no_card_is_within_ten_percent_of_an_open_ended_bound():
    """Vending-Bench 2 is dollars with no natural ceiling; warn before it clips."""
    low, high = BENCHMARK_RANGES["vending_bench_2"]
    for path in sorted((REPO / "models").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if "vending_bench_2" not in text:
            continue
        card = ModelCard.from_yaml_file(path)
        values = [e.score for e in card.benchmarks.evidence if e.benchmark_id == "vending_bench_2"]
        values += [v for k, v in card.benchmarks.scores.items() if k == "vending_bench_2"]
        for value in values:
            assert value < low + 0.9 * (high - low), (
                f"{path.name}: vending_bench_2 {value} is near the {high} bound; raise it")


def test_frontier_values_no_longer_tie_at_the_ceiling():
    gpqa = _benchmark_evidence({"gpqa_diamond": 96.0, "hle": 64.4},
                               {"benchmark_weights": {"gpqa_diamond": 0.5, "hle": 0.5}})
    other = _benchmark_evidence({"gpqa_diamond": 88.0, "hle": 64.4},
                                {"benchmark_weights": {"gpqa_diamond": 0.5, "hle": 0.5}})
    assert gpqa["benchmark_lower_bound"] > other["benchmark_lower_bound"]


# ── Arena: one snapshot, normalised within it ───────────────────────────────

def test_arena_snapshot_is_pinned_to_one_dataset_revision():
    assert ARENA_SNAPSHOT["dataset"] == "lmarena-ai/leaderboard-dataset"
    assert ARENA_SNAPSHOT["license"] == "CC BY 4.0"
    assert re.fullmatch(r"[0-9a-f]{40}", ARENA_SNAPSHOT["revision"])
    for key, board in ARENA_SNAPSHOT["boards"].items():
        date.fromisoformat(board["published"])
        assert board["leader"] > 1000, key
        assert key not in BENCHMARK_RANGES, f"{key} must not also have a fixed Elo bound"


def test_the_engine_snapshot_is_the_one_the_evidence_was_read_from():
    """The data PR records the snapshot; the engine must normalise against the same one."""
    import json
    recorded = json.loads((BENCHMARKS / "_census/ranking_evidence/arena_snapshot.json")
                          .read_text(encoding="utf-8"))
    assert recorded["revision"] == ARENA_SNAPSHOT["revision"]
    assert set(recorded["boards"]) == set(ARENA_SNAPSHOT["boards"])
    for key, board in ARENA_SNAPSHOT["boards"].items():
        assert recorded["boards"][key]["published"] == board["published"], key
        assert recorded["boards"][key]["leader"] == board["leader"], key
        assert (recorded["boards"][key]["subset"], recorded["boards"][key]["category"]) == (
            board["subset"], board["category"]), key


def test_the_snapshot_leader_scores_100_and_the_gap_is_a_win_probability():
    board = ARENA_SNAPSHOT["boards"]["arena_sc_coding"]
    leader = board["leader"]
    assert _normalize_arena("arena_sc_coding", leader) == pytest.approx(100.0)
    # 400 points behind: expected win rate against the leader is 1/11.
    assert _normalize_arena("arena_sc_coding", leader - 400) == pytest.approx(200 / 11)
    assert _normalize_arena("arena_sc_coding", leader + 50) == 100.0
    values = [_normalize_arena("arena_sc_coding", leader - gap) for gap in (0, 25, 100, 300)]
    assert values == sorted(values, reverse=True)


def _arena_profile():
    return {"benchmark_weights": {"arena_sc_coding": 0.5, "swe_bench_pro": 0.5}}


def test_an_arena_value_off_the_pinned_snapshot_does_not_count():
    """Every Arena value in a ranking shares its board's one publish date."""
    board = ARENA_SNAPSHOT["boards"]["arena_sc_coding"]
    scores = {"arena_sc_coding": board["leader"], "swe_bench_pro": 50.0}
    on = _benchmark_evidence(scores, _arena_profile(),
                             evidence_dates={"arena_sc_coding": board["published"]})
    off = _benchmark_evidence(scores, _arena_profile(),
                              evidence_dates={"arena_sc_coding": "2026-08-21"})
    undated = _benchmark_evidence(scores, _arena_profile())
    assert on["benchmark_count"] == 2 and "arena_sc_coding" in on["benchmark_contributions"]
    for row in (off, undated):
        assert "arena_sc_coding" not in row["benchmark_contributions"]
        assert "arena_sc_coding" in row["missing_benchmarks"]
        assert row["off_snapshot_benchmarks"] == ["arena_sc_coding"]
    assert on["off_snapshot_benchmarks"] == []


@pytest.mark.parametrize("key", sorted(ARENA_SNAPSHOT["boards"]))
def test_each_arena_page_carries_the_cc_by_attribution(key):
    text = (BENCHMARKS / f"{key}.md").read_text(encoding="utf-8")
    assert "CC BY 4.0" in text, key
    assert "huggingface.co/datasets/lmarena-ai/leaderboard-dataset" in text, key


# ── staleness, precedence and effort ─────────────────────────────────────────

def _evidence(**kw) -> dict:
    row = {"benchmark_id": "swe_bench_pro", "model_id_as_evaluated": "Model X",
           "score": 50.0, "unit": "%", "source_url": "https://labs.scale.com/leaderboard/swe_bench_pro_public",
           "source_kind": "independent_evaluator", "evidence_date": "2026-09-01",
           "date_type": "evaluated", "verified_at": "2026-09-24"}
    row.update(kw)
    return row


def _card(*evidence: dict) -> ModelCard:
    return ModelCard.model_validate({
        "identity": {"model_id": "acme/x", "display_name": "X", "provider": "acme",
                     "model_type": "llm-chat"},
        "benchmarks": {"evidence": list(evidence)},
    })


def test_an_independent_reading_beats_a_provider_self_report_whatever_the_order():
    own = _evidence(score=90.0, source_kind="provider_self_report", date_type="published",
                    source_url="https://acme.example/system-card", evidence_date="2026-09-20")
    board = _evidence(score=60.0)
    for rows in ((own, board), (board, own)):
        cand, = build_candidates([_card(*rows)], CollectingSink())
        assert cand.benchmark_scores["swe_bench_pro"] == 60.0


def test_a_self_report_never_fills_a_key_an_independent_board_carries():
    """Even alone: the provider's harness is not the board's (Jamie's rule, per key)."""
    from api.ranking.engine import INDEPENDENT_BOARD_KEYS
    assert "swe_bench_pro" in INDEPENDENT_BOARD_KEYS
    own = _evidence(score=89.9, source_kind="provider_self_report", date_type="published",
                    source_url="https://acme.example/system-card")
    cand, = build_candidates([_card(own)], CollectingSink())
    assert "swe_bench_pro" not in cand.benchmark_scores
    assert "swe_bench_pro" not in cand.verified_benchmarks


def test_a_self_report_fills_a_key_no_independent_board_carries():
    own = _evidence(benchmark_id="browsecomp", score=80.0, source_kind="provider_self_report",
                    date_type="published", source_url="https://acme.example/system-card")
    cand, = build_candidates([_card(own)], CollectingSink())
    assert cand.benchmark_scores["browsecomp"] == 80.0
    assert "browsecomp" in cand.verified_benchmarks


def test_the_max_effort_row_is_the_product_row():
    high = _evidence(model_id_as_evaluated="model-x-high", score=70.0, evidence_date="2026-09-10")
    top = _evidence(model_id_as_evaluated="Model X (max)", score=65.0, evidence_date="2026-09-01")
    for rows in ((high, top), (top, high)):
        cand, = build_candidates([_card(*rows)], CollectingSink())
        assert cand.benchmark_scores["swe_bench_pro"] == 65.0


def test_candidates_carry_the_date_and_kind_of_the_row_they_use():
    board = _evidence(source_url="https://www.tbench.ai/leaderboard/terminal-bench/4.0",
                      benchmark_id="terminal_bench_v4_0", source_kind="benchmark_author")
    own = _evidence(benchmark_id="browsecomp", source_kind="provider_self_report",
                    date_type="published", source_url="https://acme.example/card",
                    evidence_date="2026-01-05")
    cand, = build_candidates([_card(board, own)], CollectingSink())
    assert cand.evidence_dates == {"terminal_bench_v4_0": "2026-09-01", "browsecomp": "2026-01-05"}
    assert cand.live_benchmarks == {"terminal_bench_v4_0"}
    assert cand.to_json()["evidence_dates"] == cand.evidence_dates
    assert cand.to_json()["live_benchmarks"] == ["terminal_bench_v4_0"]


def _dated(scores, dates, live):
    return Candidate("acme/x", "X", "Acme", "llm-code", benchmark_scores=scores,
                     verified_benchmarks=set(scores), evidence_dates=dates,
                     live_benchmarks=set(live))


def test_a_live_reading_older_than_the_window_is_flagged_and_still_counts():
    profile = {"benchmark_weights": {"swe_bench_pro": 0.5, "browsecomp": 0.5}}
    cand = _dated({"swe_bench_pro": 60.0, "browsecomp": 70.0},
                  {"swe_bench_pro": "2026-07-01", "browsecomp": "2026-01-01"},
                  live={"swe_bench_pro"})
    row = score(cand, profile, as_of=date(2026, 9, 24))
    assert row["stale_benchmarks"] == ["swe_bench_pro"]  # a static report is not "stale"
    assert "swe_bench_pro" in row["benchmark_contributions"]
    assert row["oldest_live_reading"] == "2026-07-01"
    fresh = score(cand, profile, as_of=date(2026, 7, 20))
    assert fresh["stale_benchmarks"] == []


def test_the_policy_publishes_the_window_and_the_snapshot():
    policy = ranking_policy()
    assert policy["stale_after_days"] == STALE_AFTER_DAYS == 45
    assert policy["arena_snapshot"]["revision"] == ARENA_SNAPSHOT["revision"]
    assert policy["arena_snapshot"]["normalisation"] == "win_probability_vs_snapshot_leader"


def test_rank_report_rows_always_carry_the_new_fields():
    cand = _dated({"swe_bench_pro": 60.0, "terminal_bench_v4_0": 50.0},
                  {"swe_bench_pro": "2026-09-01", "terminal_bench_v4_0": "2026-09-01"},
                  live={"swe_bench_pro"})
    report = rank_report([cand], "coding", as_of=date(2026, 9, 24),
                         min_benchmark_coverage=0.1)
    for row in report["ranked"] + report["unranked"]:
        assert row["stale_benchmarks"] == []
        assert row["off_snapshot_benchmarks"] == []
        assert "oldest_live_reading" in row
