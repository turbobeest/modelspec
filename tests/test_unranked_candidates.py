"""MODEL-110: a ranking names the models it could not rank.

`unranked_count` alone lets a stale shortlist look authoritative: a caller asking
for the best coding model never learns that a model released last month exists
and has no benchmark scores yet. `rank_report` therefore carries
`unranked_candidates` — a bounded, newest-first list of the models that passed
every filter the request applied, match the use case's model types, and still
could not be ordered.

It is disclosure only. The last test in this file proves the rest of the report
is byte-for-byte what the scorer produced before this field existed, over a
frozen slice of a real built export.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from api.ranking.engine import USE_CASE_PROFILES
from pipeline import ranking
from pipeline.ranking import Candidate, rank_report

CODING = USE_CASE_PROFILES["coding"]
CODING_BENCHMARKS = sorted(b for b, w in CODING["benchmark_weights"].items() if w > 0)
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "rank_golden_pre_model110.json"


def full(model_id: str, **kw) -> Candidate:
    """Enough coding evidence to rank."""
    return Candidate(model_id, model_id, "Test", kw.pop("model_type", "llm-code"),
                     benchmark_scores={b: 60.0 for b in CODING_BENCHMARKS}, **kw)


def bare(model_id: str, release_date: str | None = None, **kw) -> Candidate:
    """A coding-type model with no score on any coding benchmark."""
    return Candidate(model_id, model_id, "Test", kw.pop("model_type", "llm-chat"),
                     release_date=release_date, **kw)


def names(report: dict) -> list[str]:
    return [m["model_id"] for m in report["unranked_candidates"]["models"]]


# ── what the list holds ──────────────────────────────────────────────────────

def test_a_zero_score_model_that_passes_the_filters_is_named_with_no_scores() -> None:
    report = rank_report([full("a/ranked"), bare("new/model", "2026-08-01")], "coding")

    block = report["unranked_candidates"]
    assert block["count"] == 1
    assert block["cap"] == ranking.UNRANKED_CANDIDATES_CAP
    entry, = block["models"]
    assert entry == {
        "model_id": "new/model",
        "display_name": "new/model",
        "release_date": "2026-08-01",
        "reason": "no_scores",
        "missing_benchmarks": CODING_BENCHMARKS,
    }
    # The ranked shortlist is untouched by the disclosure.
    assert [r["model_id"] for r in report["ranked"]] == ["a/ranked"]


def test_the_reasons_are_the_ones_the_floors_can_tell_apart() -> None:
    one = bare("thin/one", benchmark_scores={"scicode": 70.0})
    two = bare("thin/two", benchmark_scores={"humaneval": 80.0, "aider_polyglot": 50.0})
    # With the coverage floor lowered to 10%, one benchmark (scicode, 20%) fails
    # only the count floor.
    low = rank_report([one, bare("none/at-all")], "coding", min_benchmark_coverage=0.10)
    reasons = {m["model_id"]: m["reason"] for m in low["unranked_candidates"]["models"]}
    assert reasons == {"thin/one": "below_count_floor", "none/at-all": "no_scores"}
    # At the CLI floor, two benchmarks worth 28% fail only the coverage floor, and
    # scicode alone fails both — the count floor is named first.
    cli = rank_report([one, two], "coding")
    reasons = {m["model_id"]: m["reason"] for m in cli["unranked_candidates"]["models"]}
    assert reasons == {"thin/one": "below_count_floor", "thin/two": "below_coverage_floor"}
    assert set(ranking.UNRANKED_REASONS) == {"no_scores", "below_count_floor",
                                             "below_coverage_floor"}


def test_missing_benchmarks_are_the_profile_benchmarks_the_model_lacks() -> None:
    thin = bare("thin/one", benchmark_scores={"scicode": 70.0, "not_a_coding_bench": 1.0})
    entry, = rank_report([thin], "coding")["unranked_candidates"]["models"]
    assert entry["missing_benchmarks"] == [b for b in CODING_BENCHMARKS if b != "scicode"]


def test_only_models_that_pass_the_requests_filters_count() -> None:
    pool = [
        full("a/ranked", open_weights=True, fits={"gpu": 10.0}),
        bare("keep/open-fits", "2026-07-01", open_weights=True, fits={"gpu": None}),
        bare("drop/closed", "2026-09-01", open_weights=False, fits={"gpu": 5.0}),
        bare("drop/no-fit", "2026-09-01", open_weights=True),
        bare("drop/rehost", "2026-09-01", open_weights=True, fits={"gpu": 5.0},
             rehost_of="keep/open-fits"),
        # Scores nothing on coding and is not a coding-capable type: not a candidate.
        bare("drop/embedder", "2026-09-02", model_type="embedding-text",
             open_weights=True, fits={"gpu": 5.0}),
        bare("drop/untyped", "2026-09-02", model_type=None, open_weights=True,
             fits={"gpu": 5.0}),
    ]
    report = rank_report(pool, "coding", open_weights_only=True, hardware_id="gpu")
    assert names(report) == ["keep/open-fits"]
    assert report["unranked_candidates"]["count"] == 1
    # unranked_count is unchanged in meaning: every unrankable model in the pool.
    assert report["unranked_count"] == 3

    with_rehosts = rank_report(pool, "coding", open_weights_only=True, hardware_id="gpu",
                               include_rehosts=True)
    assert names(with_rehosts) == ["drop/rehost", "keep/open-fits"]


def test_a_subtype_match_counts_as_a_type_match() -> None:
    model = bare("sub/typed", "2026-01-01", model_type="embedding-text",
                 model_subtypes=["llm-code"])
    assert names(rank_report([model], "coding")) == ["sub/typed"]


# ── order and bound ──────────────────────────────────────────────────────────

def test_newest_first_unknown_dates_last_ties_by_id() -> None:
    pool = [
        bare("z/old", "2025-01-15"),
        bare("m/undated"),
        bare("b/newest", "2026-09-01"),
        bare("a/same-day", "2026-06-10"),
        bare("c/same-day", "2026-06-10"),
        bare("d/month-only", "2026-06"),
        bare("e/garbled", "sometime in June"),
        bare("f/empty", ""),
    ]
    report = rank_report(pool, "coding")
    assert names(report) == ["b/newest", "a/same-day", "c/same-day", "d/month-only",
                             "z/old", "e/garbled", "f/empty", "m/undated"]
    by_id = {m["model_id"]: m for m in report["unranked_candidates"]["models"]}
    # Published as the card has it; only the ordering refuses to parse prose.
    assert by_id["e/garbled"]["release_date"] == "sometime in June"
    assert by_id["f/empty"]["release_date"] is None
    assert by_id["m/undated"]["release_date"] is None


def test_the_list_is_capped_and_the_count_is_not() -> None:
    pool = [bare(f"m/{i:02d}", f"2026-01-{i:02d}") for i in range(1, 14)]
    report = rank_report(pool, "coding", limit=0)
    block = report["unranked_candidates"]
    assert ranking.UNRANKED_CANDIDATES_CAP == 10
    assert block["count"] == 13
    assert len(block["models"]) == 10
    assert names(report)[0] == "m/13" and names(report)[-1] == "m/04"


def test_an_empty_disclosure_is_present_not_absent() -> None:
    report = rank_report([full("a/ranked")], "coding")
    assert report["unranked_candidates"] == {
        "count": 0, "cap": ranking.UNRANKED_CANDIDATES_CAP, "models": []}


def test_the_wizard_floor_is_the_floor_the_reasons_use() -> None:
    two = bare("thin/two", benchmark_scores={"scicode": 70.0, "humaneval": 80.0})  # 36%
    assert names(rank_report([two], "coding")) == ["thin/two"]
    assert names(rank_report([two], "coding",
                             min_benchmark_coverage=ranking.WIZARD_BENCHMARK_COVERAGE)) == []


# ── the release date travels through the export ──────────────────────────────

def test_release_date_is_on_the_exported_candidate() -> None:
    row = bare("x/y", "2026-05-01").to_json()
    assert row["release_date"] == "2026-05-01"
    assert bare("x/z").to_json()["release_date"] is None


# ── nothing else moved ───────────────────────────────────────────────────────

def _golden() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def _frozen_pool(frozen: dict) -> list[Candidate]:
    return [
        Candidate(
            model_id=c["model_id"], display_name=c["display_name"], provider=c["provider"],
            model_type=c.get("model_type"), model_subtypes=c.get("model_subtypes") or [],
            benchmark_scores=c.get("benchmark_scores") or {},
            capability_tiers=c.get("capability_tiers") or {},
            cost_input=c.get("cost_input"), context_window=c.get("context_window"),
            open_weights=bool(c.get("open_weights")), scores_as_of=c.get("scores_as_of"),
            fits=c.get("fits") or {},
            verified_benchmarks=set(c.get("verified_benchmarks") or []),
            rehost_of=c.get("rehost_of"), release_date=c.get("release_date"),
        )
        for c in frozen["candidates"]
    ]


@pytest.mark.parametrize("vector", sorted(_golden()["vectors"]))
def test_the_rest_of_the_report_is_byte_identical_to_before(vector: str) -> None:
    """Golden bytes, captured from the pre-MODEL-110 scorer on a real export slice.

    Serialised exactly as `write_export` serialises `rankings.json`. Drop the one
    new key and nothing else may differ — not a score, not an order, not a count.
    """
    frozen = _golden()
    kwargs = dict(frozen["vectors"][vector])
    profile = kwargs.pop("profile_key")
    report = rank_report(_frozen_pool(frozen), profile, **kwargs)
    assert "unranked_candidates" in report
    before = {k: v for k, v in report.items() if k != "unranked_candidates"}
    digest = hashlib.sha256(
        json.dumps(before, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    assert before["ranked_count"] == frozen["golden"][vector]["ranked_count"]
    assert digest == frozen["golden"][vector]["sha256"], (
        f"{vector}: rank_report changed outside unranked_candidates")


def test_the_golden_slice_exercises_the_disclosure() -> None:
    """A golden over a slice with nothing to disclose would prove little."""
    frozen = _golden()
    pool = _frozen_pool(frozen)
    seen = set()
    for kwargs in frozen["vectors"].values():
        kwargs = dict(kwargs)
        report = rank_report(pool, kwargs.pop("profile_key"), **kwargs)
        seen.update(m["reason"] for m in report["unranked_candidates"]["models"])
    assert "no_scores" in seen
    assert seen - {"no_scores"}, "no thin-evidence reason appears in the golden slice"
