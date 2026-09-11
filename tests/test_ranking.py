"""The ranking pipeline: filter, score, rank, explain.

The profiles, benchmark ranges and normalisation helpers are imported from
`api/ranking/engine.py` rather than copied, so these tests do not need to guard
against transcription drift — there is no transcription. What they pin is the
scoring arithmetic, the filters, and the honesty of what a ranking claims.
"""

from __future__ import annotations

import functools
import glob
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from api.ranking.engine import (  # noqa: E402
    BENCHMARK_RANGES, MIN_BENCHMARK_COUNT, MIN_BENCHMARK_COVERAGE, USE_CASE_PROFILES,
)
from pipeline import hardware  # noqa: E402
from pipeline.ranking import (  # noqa: E402
    FEATURED_PROFILES, Candidate, build_candidates, rank, rank_report, score,
)
from schema.card import ModelCard  # noqa: E402
from schema.graph import derive_graph  # noqa: E402


def _candidate(**kw) -> Candidate:
    base = dict(model_id="m", display_name="M", provider="P", model_type="llm-chat")
    base.update(kw)
    return Candidate(**base)


# ── the tables come from one place ───────────────────────────────────────────

def test_featured_profiles_all_exist() -> None:
    """A dropdown entry with no profile behind it would fail at runtime."""
    for key in FEATURED_PROFILES:
        assert key in USE_CASE_PROFILES, f"featured profile {key!r} is not defined"


#: Benchmarks a profile weights that have no entry in BENCHMARK_RANGES, so
#: normalisation falls back to "assume 0-100, higher is better". Tracked in
#: MODEL-30. Three of these are actively wrong rather than merely imprecise:
#: wer_librispeech and fid are lower-is-better, and mos_tts is a 1-5 scale.
#: clip_score alone remains unranged. Its convention is genuinely ambiguous —
#: a 0-1 cosine similarity in some papers, a 0-40 scaled value in others — and a
#: guessed range would be worse than an honest gap. See MODEL-30.
KNOWN_UNRANGED = {"clip_score"}


def test_no_new_benchmark_loses_its_normalisation_range() -> None:
    """A weighted benchmark with no range is normalised by a guess.

    The guess is "0-100, higher is better", which silently inverts any
    lower-is-better metric. This test does not fail on the ones already known
    (MODEL-30 fixes those); it fails if a new one appears.
    """
    ids = set(BENCHMARK_RANGES)
    unknown = {
        bench
        for profile in USE_CASE_PROFILES.values()
        for bench in (profile.get("benchmark_weights") or {})
        if bench not in ids
    }
    assert unknown <= KNOWN_UNRANGED, (
        f"new benchmarks weighted without a normalisation range: {sorted(unknown - KNOWN_UNRANGED)}"
    )


def test_speech_to_text_stays_off_the_wizard_while_it_cannot_rank() -> None:
    """MODEL-30: offered-and-empty is worse than hidden.

    Cost stays a query parameter (CLI `--price-sensitivity`, wizard Price
    sensitivity); every profile still defaults cost_weight to 0.
    """
    assert "speech_to_text" not in FEATURED_PROFILES
    assert "image_generation" not in FEATURED_PROFILES
    assert all(p.get("cost_weight", 0) == 0 for p in USE_CASE_PROFILES.values())


def test_a_profile_resting_on_an_unranged_benchmark_is_not_featured() -> None:
    """Do not put a ranking we know is guessing in front of anyone.

    image_generation weights clip_score, whose scale is ambiguous, so it stays
    out of the wizard until MODEL-30 settles the convention.
    """
    for key in FEATURED_PROFILES:
        weighted = set(USE_CASE_PROFILES[key].get("benchmark_weights") or {})
        assert not (weighted & KNOWN_UNRANGED), (
            f"featured profile {key!r} weights an unranged benchmark"
        )


def test_a_lower_is_better_metric_is_inverted() -> None:
    """Word error rate: 2% is excellent, 20% is poor. Higher must not win."""
    from api.ranking.engine import _normalize_benchmark
    good = _normalize_benchmark("wer_librispeech", 2.0)
    poor = _normalize_benchmark("wer_librispeech", 20.0)
    assert good > poor, "a worse transcriber is outranking a better one"
    assert good > 90 and poor < 30


def test_a_one_to_five_scale_uses_its_whole_range() -> None:
    from api.ranking.engine import _normalize_benchmark
    assert _normalize_benchmark("mos_tts", 1.0) == pytest.approx(0.0)
    assert _normalize_benchmark("mos_tts", 5.0) == pytest.approx(100.0)


# ── the arithmetic ───────────────────────────────────────────────────────────

def test_a_model_with_no_data_is_unranked() -> None:
    result = score(_candidate(model_type=None), USE_CASE_PROFILES["coding"])
    assert result["score"] is None
    assert result["benchmark_estimate"] is None
    assert result["rank_status"] == "unranked"
    assert result["evidence_basis"] == "none"


def test_benchmarks_contribute_and_are_explained() -> None:
    result = score(_candidate(benchmark_scores={"humaneval": 90.0}),
                   USE_CASE_PROFILES["coding"])
    assert result["benchmark_score"] > 0
    assert "humaneval" in result["benchmark_contributions"]
    assert result["evidence_basis"] == "unverified-legacy"


def test_free_beats_expensive_on_the_cost_axis() -> None:
    """The cost curve itself is correct, when a caller asks for it."""
    profile = USE_CASE_PROFILES["general"]
    free = score(_candidate(cost_input=0.0), profile, cost_weight=0.20)["cost_score"]
    cheap = score(_candidate(cost_input=0.5), profile, cost_weight=0.20)["cost_score"]
    dear = score(_candidate(cost_input=30.0), profile, cost_weight=0.20)["cost_score"]
    assert free > cheap > dear


def test_price_is_ignored_unless_the_caller_asks_for_it() -> None:
    """Every shipped profile carries cost_weight 0.0, deliberately.

    Setting them all to a non-zero weight was tried and produced worse
    rankings — a nano model topped `coding` on price alone. How much quality
    someone will trade for price is a property of the person, not of the use
    case, so it is a query parameter. See MODEL-30.
    """
    profile = USE_CASE_PROFILES["general"]
    free = score(_candidate(model_id="free", cost_input=0.0), profile)
    dear = score(_candidate(model_id="dear", cost_input=30.0), profile)
    assert free["cost_score"] == dear["cost_score"] == 0.0


def test_price_sensitivity_can_be_turned_on_per_query() -> None:
    profile = USE_CASE_PROFILES["general"]
    free = score(_candidate(model_id="free", cost_input=0.0), profile, cost_weight=0.25)
    dear = score(_candidate(model_id="dear", cost_input=30.0), profile, cost_weight=0.25)
    assert free["cost_score"] > dear["cost_score"]
    assert free["score_lower_bound"] > dear["score_lower_bound"]


def test_price_sensitivity_reorders_a_real_ranking() -> None:
    candidates = _real()
    indifferent = [r["model_id"] for r in rank_report(candidates, "coding", limit=5)["ranked"]]
    sensitive = [r["model_id"] for r in rank_report(candidates, "coding", limit=5, cost_weight=0.25)["ranked"]]
    assert indifferent != sensitive, "price sensitivity had no effect on a real ranking"


def test_context_is_log_scaled() -> None:
    profile = USE_CASE_PROFILES["general"]
    small = score(_candidate(context_window=8_000), profile)["context_score"]
    large = score(_candidate(context_window=1_000_000), profile)["context_score"]
    assert large > small
    # Log-scaled: a 125x context buys about 6x the points, not 125x.
    assert large < small * 10


def test_type_match_prefers_the_first_listed_type() -> None:
    profile = USE_CASE_PROFILES["coding"]
    first = profile["preferred_types"][0]
    second = profile["preferred_types"][1]
    assert (score(_candidate(model_type=first), profile)["type_bonus"]
            > score(_candidate(model_type=second), profile)["type_bonus"])


def test_a_subtype_can_earn_the_type_bonus() -> None:
    profile = USE_CASE_PROFILES["coding"]
    result = score(_candidate(model_type="unrelated",
                              model_subtypes=[profile["preferred_types"][0]]), profile)
    assert result["type_bonus"] > 0


def test_sub_capabilities_are_discounted_against_an_explicit_tier() -> None:
    profile = USE_CASE_PROFILES["coding"]
    explicit = score(_candidate(capability_tiers={"coding": "tier-1"}), profile)["capability_score"]
    implied = score(_candidate(capability_tiers={"coding:debugging": "tier-1"}), profile)["capability_score"]
    # 0.7 is the subtype discount in score(); update if that factor changes.
    assert implied == pytest.approx(explicit * 0.7, rel=0.01)


def test_score_is_clamped_to_a_hundred() -> None:
    huge = _candidate(
        benchmark_scores={k: 100.0 for k in BENCHMARK_RANGES},
        capability_tiers={k: "tier-1" for k in ("coding", "reasoning", "tool_use")},
        cost_input=0.0, context_window=10_000_000, model_type="llm-code")
    assert score(huge, USE_CASE_PROFILES["coding"])["score"] <= 100.0


# ── filters ──────────────────────────────────────────────────────────────────

def test_open_weights_filter_excludes_closed_models() -> None:
    pool = [_candidate(model_id="open", open_weights=True),
            _candidate(model_id="closed", open_weights=False)]
    report = rank_report(pool, "general", open_weights_only=True)
    ids = {r["model_id"] for r in report["ranked"] + report["unranked"]}
    assert ids == {"open"}


def test_hardware_filter_keeps_only_models_that_fit() -> None:
    pool = [_candidate(model_id="fits", fits={"gpu": 40.0}),
            _candidate(model_id="too-big", fits={})]
    report = rank_report(pool, "general", hardware_id="gpu")
    ids = {r["model_id"] for r in report["ranked"] + report["unranked"]}
    assert ids == {"fits"}


def test_ranking_is_ordered_by_score() -> None:
    pool = [_candidate(model_id=f"m{i}", benchmark_scores={
        b: float(i * 10) for b in USE_CASE_PROFILES["coding"]["benchmark_weights"]})
            for i in range(1, 6)]
    scores = [r["score"] for r in rank(pool, "coding")]
    assert scores == sorted(scores, reverse=True)


def test_rank_returns_eligible_models_when_the_catalogue_is_sparse() -> None:
    """Other models lacking coverage is ordinary; rank() must not raise."""
    candidates = _real()
    ranked = rank(candidates, "coding", limit=10)
    report = rank_report(candidates, "coding", limit=10)
    assert ranked == report["ranked"]
    # Unranked models are the expected catalogue state. Drop this if coding
    # ever has enough evidence to order every candidate.
    assert report["unranked_count"] > 0
    assert len(ranked) == min(10, report["ranked_count"])
    assert all(r["score"] is not None and r["rank"] is not None for r in ranked)


# ── against the real corpus ──────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _real():
    files = [f for f in sorted(glob.glob(str(REPO_ROOT / "models/**/*.md"), recursive=True))
             if not f.endswith("LICENSE.md")]
    cards = [ModelCard.from_yaml_file(f) for f in files]
    sink = derive_graph(cards)
    hardware.compute(sink, cards, hardware.load_devices(REPO_ROOT))
    return build_candidates(cards, sink)


def test_every_featured_profile_reports_whether_it_can_rank() -> None:
    candidates = _real()
    for key in FEATURED_PROFILES:
        report = rank_report(candidates, key, limit=10)
        assert report["ranked"] or report["unranked"], f"{key} returned nothing"
        assert report["ranking_status"] in {"complete", "partial", "unavailable"}
        if report["ranked"]:
            assert report["ranked"][0]["score"] > 0
        assert all(r["score"] is None for r in report["unranked"])


def test_a_hardware_constrained_ranking_is_smaller_and_still_useful() -> None:
    candidates = _real()
    unconstrained = rank_report(candidates, "coding", limit=1000)["ranked"]
    constrained = rank_report(candidates, "coding", limit=1000,
                              open_weights_only=True, hardware_id="nvidia_rtx_4090")["ranked"]
    assert 0 < len(constrained) < len(unconstrained)
    assert all(r["open_weights"] for r in constrained)


def test_rankings_disclose_their_evidence_basis() -> None:
    """Provenance is disclosed; `verified` is not applied to incomplete evidence.

    Ranked rows used to be pinned to `unverified-legacy` because that was the
    catalogue that day. Attaching reviewed evidence must be allowed to change
    the label; it must not be allowed to call a sparse or empty input `verified`.
    """
    report = rank_report(_real(), "coding", limit=10)
    for result in report["ranked"]:
        assert result["evidence_basis"] in {
            "unverified-legacy", "mixed", "partial-verified", "verified",
        }
        assert result["score"] is not None and result["rank"] is not None
        if result["evidence_basis"] == "verified":
            assert result["benchmark_coverage"] == pytest.approx(1.0)
    for result in report["unranked"]:
        assert result["evidence_basis"] != "verified"
        assert result["rank"] is result["score"] is None
        assert (
            result["benchmark_coverage"] < MIN_BENCHMARK_COVERAGE
            or result["benchmark_count"] < MIN_BENCHMARK_COUNT
        )


# ── verified evidence in a ranking ───────────────────────────────────────────

def test_reviewed_evidence_beats_the_flat_block_for_the_same_benchmark() -> None:
    """Same measurement, checked. The reviewed value wins."""
    import glob as _glob

    from pipeline.ranking import build_candidates
    from schema.graph import CollectingSink

    files = [f for f in sorted(_glob.glob(str(REPO_ROOT / "models/**/*.md"), recursive=True))
             if f.endswith("gpt-6-astra.md")]
    assert files, "expected a card carrying reviewed evidence"
    cards = [ModelCard.from_yaml_file(files[0])]
    candidate = build_candidates(cards, CollectingSink())[0]
    for record in cards[0].benchmarks.evidence:
        assert candidate.benchmark_scores[record.benchmark_id] == record.score
        assert record.benchmark_id in candidate.verified_benchmarks


def test_evidence_basis_distinguishes_verified_from_legacy() -> None:
    from pipeline.ranking import _basis

    assert _basis(0, 0, 0.0) == "none"
    assert _basis(3, 3, 1.0) == "verified"
    # 0.2 is a synthetic incomplete coverage, not a catalogue snapshot.
    assert _basis(3, 3, 0.2) == "partial-verified"
    assert _basis(3, 1, 1.0) == "mixed"
    assert _basis(3, 0, 1.0) == "unverified-legacy"


def test_a_ranking_reports_how_much_of_it_is_verified() -> None:
    profile = USE_CASE_PROFILES["coding"]
    plain = _candidate(benchmark_scores={"humaneval": 90.0})
    checked = _candidate(benchmark_scores={"humaneval": 90.0},
                         verified_benchmarks={"humaneval"})
    assert score(plain, profile)["evidence_basis"] == "unverified-legacy"
    assert score(checked, profile)["evidence_basis"] == "partial-verified"
    assert score(checked, profile)["verified_contributions"] == 1


def test_verified_benchmarks_now_carry_ranking_weight() -> None:
    """MODEL-32 option B: reviewed evidence is load-bearing."""
    import json as _json

    report = _json.loads(
        (REPO_ROOT / "benchmarks/_census/eligibility/current-report.json").read_text())
    active = set(report["active_ids"])
    weighted = set()
    for profile in USE_CASE_PROFILES.values():
        weighted |= set(profile.get("benchmark_weights") or {})
    assert active & weighted, "no verified benchmark carries any ranking weight"


def test_one_evaluators_index_cannot_dominate_a_profile() -> None:
    """The cap is the point: evidence matters without one source deciding "best"."""
    from api.ranking.engine import VERIFIED_ADDITIONS, VERIFIED_INDEX_WEIGHT

    for key, added in VERIFIED_ADDITIONS.items():
        weights = USE_CASE_PROFILES[key]["benchmark_weights"]
        share = sum(v for b, v in weights.items() if b in added)
        assert share <= VERIFIED_INDEX_WEIGHT + 0.001, f"{key}: {share} exceeds the cap"


def test_adding_verified_benchmarks_did_not_inflate_a_profile() -> None:
    """Existing weights are scaled down, so a profile sums to what it did before."""
    from api.ranking.engine import VERIFIED_ADDITIONS

    for key in VERIFIED_ADDITIONS:
        total = sum(USE_CASE_PROFILES[key]["benchmark_weights"].values())
        assert 0.99 <= total <= 1.01, f"{key} sums to {total}"


def test_every_verified_benchmark_has_a_normalisation_range() -> None:
    import json as _json

    report = _json.loads(
        (REPO_ROOT / "benchmarks/_census/eligibility/current-report.json").read_text())
    for benchmark in report["active_ids"]:
        assert benchmark in BENCHMARK_RANGES, f"{benchmark} would fall back to a guess"
