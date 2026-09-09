from __future__ import annotations

import json
from datetime import date

import pytest
from pydantic import ValidationError

from schema.benchmark_eligibility import BenchmarkEvidence, ModelReferenceSet, evaluate
from scripts.benchmarks.downselect import build_report

URL = "https://example.com/source"


def reference(as_of="2026-09-01", *, same_org=False, no_open=False):
    return ModelReferenceSet.model_validate(
        {
            "as_of": as_of,
            "models": [
                {
                    "model_id": "frontier",
                    "organization": "Org A",
                    "domain": "text",
                    "cohort": "frontier",
                    "openness": "closed",
                    "source_url": URL,
                    "rationale": "listed",
                },
                {
                    "model_id": "open",
                    "organization": "Org A" if same_org else "Org B",
                    "domain": "text",
                    "cohort": "open",
                    "openness": "closed" if no_open else "open_weight",
                    "source_url": URL,
                    "rationale": "listed",
                },
            ],
        }
    )


def evidence(
    *,
    days_old=19,
    candidate_id="bench",
    canonical_id="bench",
    review="approved",
    usefulness="useful",
):
    evidence_date = (
        date(2026, 9, 8).fromordinal(date(2026, 9, 8).toordinal() - days_old).isoformat()
    )
    return BenchmarkEvidence.model_validate(
        {
            "candidate_id": candidate_id,
            "canonical_id": canonical_id,
            "domain": "text",
            "researcher": "collector",
            "identity": {"url": URL, "rationale": "canonical page"},
            "task": "question answering",
            "metric": "accuracy",
            "protocol": "fixed",
            "usefulness": {"verdict": usefulness, "rationale": "reviewed", "source_url": URL},
            "results": [
                {
                    "model_id": "frontier",
                    "benchmark_version": "v1",
                    "configuration": "fixed",
                    "score": 80,
                    "unit": "%",
                    "source_url": URL,
                    "evidence_date": evidence_date,
                    "date_type": "evaluated",
                    "verified_at": "2026-09-01",
                    "source_kind": "benchmark_author",
                },
                {
                    "model_id": "open",
                    "benchmark_version": "v1",
                    "configuration": "fixed",
                    "score": 79,
                    "unit": "%",
                    "source_url": URL,
                    "evidence_date": evidence_date,
                    "date_type": "evaluated",
                    "verified_at": "2026-09-01",
                    "source_kind": "independent_evaluator",
                },
            ],
            "review": {
                "reviewer": "reviewer",
                "reviewed_at": "2026-09-02",
                "verdict": review,
                "rationale": "checked",
            },
        }
    )


def test_current_and_60_day_boundary_are_current():
    ref = reference()
    assert evaluate(evidence(days_old=60), ref, date(2026, 9, 8)).status == "active"
    assert evaluate(evidence(days_old=61), ref, date(2026, 9, 8)).status == "historical"


def test_future_dates_and_missing_review_are_unverified():
    ref = reference()
    future = evidence()
    future.results[0].evidence_date = date(2026, 9, 9)
    assert evaluate(future, ref, date(2026, 9, 8)).status == "unverified"
    assert evaluate(evidence(review="needs_work"), ref, date(2026, 9, 8)).status == "unverified"


def test_no_open_same_org_and_alias():
    assert evaluate(evidence(), reference(no_open=True), date(2026, 9, 8)).status == "unverified"
    assert evaluate(evidence(), reference(same_org=True), date(2026, 9, 8)).status == "unverified"
    assert (
        evaluate(
            evidence(candidate_id="alias", canonical_id="bench"), reference(), date(2026, 9, 8)
        ).status
        == "alias"
    )


def test_freshness_timestamp_does_not_rejuvenate_old_result():
    result = evaluate(evidence(days_old=61), reference(), date(2026, 9, 8))
    assert result.status == "historical"
    assert result.accepted_results[0]["evidence_date"] == "2026-07-09"


def test_strict_malformed_and_nonfinite_data():
    with pytest.raises(ValidationError):
        BenchmarkEvidence.model_validate({"candidate_id": "x"})
    item = evidence()
    invalid = item.model_dump(mode="json")
    invalid["results"][0]["score"] = float("nan")
    with pytest.raises(ValidationError):
        BenchmarkEvidence.model_validate(invalid)


def test_cli_duplicate_ids_and_aged_reference_fail_closed(tmp_path):
    ev_dir = tmp_path / "evidence"
    ev_dir.mkdir()
    payload = evidence().model_dump(mode="json")
    (ev_dir / "a.json").write_text(json.dumps(payload))
    duplicate = dict(payload)
    duplicate["task"] = "another"
    (ev_dir / "b.json").write_text(json.dumps(duplicate))
    ref_path = tmp_path / "reference.json"
    ref_path.write_text(json.dumps(reference().model_dump(mode="json")))
    with pytest.raises(ValueError, match="duplicate candidate_id"):
        build_report(ev_dir, ref_path, date(2026, 9, 8))

    (ev_dir / "b.json").unlink()
    aged = reference(as_of="2026-07-01")
    ref_path.write_text(json.dumps(aged.model_dump(mode="json")))
    report = build_report(ev_dir, ref_path, date(2026, 9, 8))
    assert report.rows[0].status == "unverified"


@pytest.mark.parametrize("field", ["configuration", "benchmark_version", "unit"])
def test_incompatible_results_never_form_a_pair(field):
    item = evidence()
    setattr(item.results[1], field, "different")
    assert evaluate(item, reference(), date(2026, 9, 8)).status == "unverified"


@pytest.mark.parametrize("alias", [False, True])
@pytest.mark.parametrize("failure", ["missing", "self", "future", "before_verification"])
def test_independent_review_is_required(alias, failure):
    item = evidence(candidate_id="alias" if alias else "bench")
    if failure == "missing":
        item.review = None
    elif failure == "self":
        item.review.reviewer = item.researcher
    elif failure == "future":
        item.review.reviewed_at = date(2026, 9, 9)
    else:
        item.review.reviewed_at = date(2026, 8, 30)
        if alias:
            # Alias identity review need not approve model evaluation results.
            assert evaluate(item, reference(), date(2026, 9, 8)).status == "alias"
            return
    assert evaluate(item, reference(), date(2026, 9, 8)).status == "unverified"


def test_unknown_usefulness_and_incomplete_protocol_are_unverified():
    assert (
        evaluate(evidence(usefulness="unknown"), reference(), date(2026, 9, 8)).status
        == "unverified"
    )
    item = evidence()
    item.protocol = " "
    assert evaluate(item, reference(), date(2026, 9, 8)).status == "unverified"


def test_historical_mixed_age_and_saturated_results_require_review():
    item = evidence()
    item.results[1].evidence_date = date(2026, 7, 9)
    assert evaluate(item, reference(), date(2026, 9, 8)).status == "historical"
    saturated = evidence(usefulness="saturated")
    assert evaluate(saturated, reference(), date(2026, 9, 8)).status == "historical"
    saturated.review = None
    assert evaluate(saturated, reference(), date(2026, 9, 8)).status == "unverified"


@pytest.mark.parametrize("refdate", ["2026-08-08", "2026-09-09"])
def test_direct_gate_rejects_expired_and_future_reference_sets(refdate):
    assert evaluate(evidence(), reference(as_of=refdate), date(2026, 9, 8)).status == "unverified"


@pytest.mark.parametrize("score", [True, "80", float("inf")])
def test_scores_do_not_coerce_invalid_types(score):
    raw = evidence().model_dump(mode="json")
    raw["results"][0]["score"] = score
    with pytest.raises(ValidationError):
        BenchmarkEvidence.model_validate(raw)


def test_alias_can_coexist_with_canonical_and_duplicate_references_fail(tmp_path):
    ev_dir = tmp_path / "evidence"
    ev_dir.mkdir()
    for name, item in [("canonical", evidence()), ("alias", evidence(candidate_id="alias"))]:
        (ev_dir / f"{name}.json").write_text(item.model_dump_json())
    ref_path = tmp_path / "reference.json"
    ref_path.write_text(reference().model_dump_json())
    report = build_report(ev_dir, ref_path, date(2026, 9, 8))
    assert report.active_ids == ["bench"]
    assert [row.status for row in report.rows] == ["alias", "active"]
    with pytest.raises(ValueError, match="directory does not exist"):
        build_report(tmp_path / "absent", ref_path, date(2026, 9, 8))
    raw = reference().model_dump(mode="json")
    raw["models"].append(raw["models"][0])
    with pytest.raises(ValidationError, match="duplicate reference"):
        ModelReferenceSet.model_validate(raw)


def test_failed_cli_invalidates_old_report_without_deleting_input(tmp_path):
    from scripts.benchmarks.downselect import main

    output = tmp_path / "report.json"
    output.write_text('{"active_ids": ["old"]}')
    reference_path = tmp_path / "reference.json"
    reference_path.write_text(reference().model_dump_json())
    args = [
        "--evidence",
        str(tmp_path / "missing"),
        "--reference-set",
        str(reference_path),
        "--as-of",
        "2026-09-08",
        "--output",
        str(output),
    ]
    with pytest.raises(SystemExit):
        main(args)
    assert not output.exists()
    args[-1] = str(reference_path)
    with pytest.raises(SystemExit):
        main(args)
    assert reference_path.exists()
