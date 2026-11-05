"""MODEL-450: elapsed release coverage, privacy, and the offline CLI."""

import json
from datetime import UTC, datetime

import pytest

from scripts.slo import __main__ as cli
from scripts.slo import alerts, render
from scripts.slo import report as slo

NOW = datetime(2026, 11, 4, 12, tzinfo=UTC)


def test_release_lags_include_pending_work_and_scope_decidable_to_eligible_labs():
    start = datetime(2026, 11, 1, 12, tzinfo=UTC)
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/late", start, card_at=datetime(2026, 11, 2, 12, tzinfo=UTC),
                    price_at=datetime(2026, 11, 4, 12, tzinfo=UTC),
                    score_at=datetime(2026, 11, 3, 12, tzinfo=UTC),
                    premier_eligible=True),
        slo.Release("other/on-time", start, card_at=start, price_at=start, score_at=start),
        slo.Release("lab/old", datetime(2026, 9, 1, tzinfo=UTC), premier_eligible=True),
        slo.Release("lab/future", datetime(2026, 11, 5, tzinfo=UTC), premier_eligible=True),
    ), snapshot_history=True)
    report = slo.release_report(history, slo.load_config(), now=NOW, counts_only=False)
    results = {r.target: r for r in report.results}
    assert {key: r.status for key, r in results.items()} == {
        "release-card-lag": "met", "release-price-lag": "breach",
        "release-score-lag": "met", "release-decidable-lag": "met",
    }
    assert results["release-decidable-lag"].measured == 1
    coverage = report.to_json()["release_coverage"]
    price = coverage["stages"]["release-price-lag"]
    assert (price["p50_days"], price["p90_days"]) == (1.5, 2.7)
    assert price["completed"] == 2 and price["late"] == 1
    assert coverage["stages"]["release-decidable-lag"]["pending"] == 1
    assert len(coverage["releases"]) == 2
    assert "lab/late" in render.markdown(report, "https://example.test/")
    assert "p90" in render.page(report, "https://example.test/")
    assert slo.report_from_json(report.to_json()) == report


def test_private_release_report_exposes_counts_only_in_every_output():
    history = slo.ReleaseHistory(releases=(
        slo.Release("secret/hidden-model", datetime(2026, 11, 1, tzinfo=UTC),
                    discovery_source="private-signal-artifact", premier_eligible=True),
    ), errors=("secret/hidden-model: private-path",))
    report = slo.release_report(history, slo.load_config(), now=NOW, counts_only=True)
    body = json.dumps(report.to_json()) + render.markdown(report, "") + render.page(report, "")
    for secret in ("secret/hidden-model", "private-signal-artifact", "private-path", "2026-11-01"):
        assert secret not in body
    assert "p50_days" not in body and "p90_days" not in body
    assert "releases" not in report.to_json()["release_coverage"]
    assert report.release_coverage["stages"]["release-card-lag"]["late"] == 1
    assert alerts.plan(report, slo.load_config(), [], NOW) == []


def test_missing_snapshot_history_is_unmeasured_and_never_a_decidable_success():
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/new", datetime(2026, 11, 1, tzinfo=UTC), premier_eligible=True),
    ))
    report = slo.release_report(history, slo.load_config(), now=NOW, counts_only=False)
    result = next(r for r in report.results if r.target == "release-decidable-lag")
    assert result.status == "error"
    assert "snapshot" in result.errors[0]
    assert report.release_coverage["stages"][result.target]["p90_days"] is None


def test_one_late_release_opens_one_issue_per_late_stage_and_none_for_on_time_stages():
    start = datetime(2026, 10, 31, 12, tzinfo=UTC)
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/late", start, card_at=start, premier_eligible=True),
        slo.Release("lab/on-time", start, card_at=start, price_at=start, score_at=start,
                    decidable_at=start, premier_eligible=True),
    ), snapshot_history=True)
    report = slo.release_report(history, slo.load_config(), now=NOW, counts_only=False)
    actions = alerts.plan(report, slo.load_config(), [], NOW)
    assert [(a.kind, a.target) for a in actions] == [
        ("create", "release-price-lag"), ("create", "release-score-lag"),
        ("create", "release-decidable-lag"),
    ]
    issues = [alerts.Issue(i, a.title, a.body) for i, a in enumerate(actions, 1)]
    assert alerts.plan(report, slo.load_config(), issues, NOW) == []


def test_staged_price_breach_runs_through_cli_render_and_offline_alert(tmp_path, monkeypatch,
                                                                    capsys):
    from scripts.slo import releases

    start = datetime(2026, 11, 3, 12, tzinfo=UTC)
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/on-time", start, card_at=start, price_at=start, score_at=start,
                    decidable_at=start, premier_eligible=True),
    ), snapshot_history=True)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setattr(releases, "read_release_history", lambda *a, **kw: history)
    monkeypatch.setattr(cli, "gh_cli", lambda *a, **kw: pytest.fail("unexpected GitHub call"))
    out = tmp_path / "report"
    assert cli.main(["releases", "--data-dir", str(tmp_path), "--private-detail", "--out",
                     str(out), "--now", NOW.isoformat(),
                     "--stage-breach", "release-price-lag"]) == 0
    report = slo.report_from_json(json.loads((out / "coverage.json").read_text()))
    assert "p90" in (out / "index.html").read_text()
    assert report.release_coverage["repository"] == "turbobeest/modelspec-data"
    empty = tmp_path / "issues.json"
    empty.write_text("[]")
    capsys.readouterr()
    assert cli.main(["alert", "--report", str(out / "coverage.json"), "--issues-json",
                     str(empty), "--only", "release-price-lag", "--now", NOW.isoformat()]) == 0
    assert capsys.readouterr().out.strip() == (
        "create Coverage SLO breach: release-price-lag: staged-breach (release-price-lag)")
    monkeypatch.setenv("GITHUB_REPOSITORY", "turbobeest/modelspec")
    with pytest.raises(SystemExit, match="private"):
        cli.main(["alert", "--report", str(out / "coverage.json"), "--issues-json", str(empty)])


def test_private_details_are_refused_in_public_jobs_before_history_is_read(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "turbobeest/modelspec")
    with pytest.raises(SystemExit, match="private"):
        cli.main(["releases", "--data-dir", str(tmp_path), "--private-detail", "--out",
                  str(tmp_path / "out")])
    assert not (tmp_path / "out").exists()


def test_public_report_imports_only_counts_and_refuses_stale_or_inconsistent_counts():
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/new", datetime(2026, 11, 1, tzinfo=UTC), premier_eligible=True),
    ))
    data = slo.release_report(history, slo.load_config(), now=NOW).to_json()
    data["targets"][0]["errors"] = ["secret-error-text"]
    data["release_coverage"]["releases"] = [{"model_id": "secret/hidden"}]
    data["release_coverage"]["stages"]["release-price-lag"]["p90_days"] = 1234
    public = slo.public_release_report(data, slo.load_config(), now=NOW)
    text = json.dumps(public.to_json())
    assert "secret" not in text and "p90_days" not in text
    assert public.results[0].status == "breach"
    with pytest.raises(ValueError, match="current"):
        slo.public_release_report(data, slo.load_config(), now=datetime(2026, 11, 5, tzinfo=UTC))
    data["release_coverage"]["stages"]["release-price-lag"]["completed"] = 20
    with pytest.raises(ValueError, match="counts"):
        slo.public_release_report(data, slo.load_config(), now=NOW)


def test_imported_milestone_is_unknown_instead_of_a_late_pending_stage():
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/imported", datetime(2026, 10, 30, tzinfo=UTC),
                    unknown_stages=("release-card-lag",)),
    ))
    report = slo.release_report(history, slo.load_config(), now=NOW, counts_only=False)
    card = report.results[0]
    assert card.status == "error" and not card.findings
    assert report.release_coverage["stages"][card.target]["unknown"] == 1
    assert report.release_coverage["stages"][card.target]["pending"] == 0


@pytest.mark.parametrize("observed", [
    datetime(2026, 10, 29, tzinfo=UTC),
    datetime(2026, 11, 3, tzinfo=UTC),
    datetime(2026, 11, 5, tzinfo=UTC),
])
def test_stale_or_future_snapshot_cannot_establish_a_pending_decidable_breach(observed):
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/new", datetime(2026, 10, 30, tzinfo=UTC), premier_eligible=True),
    ), snapshot_history=True, snapshot_observed_at=observed)
    report = slo.release_report(history, slo.load_config(), now=NOW, counts_only=False)
    result = next(r for r in report.results if r.target == "release-decidable-lag")
    assert result.status == "error" and not result.findings
    summary = report.release_coverage["stages"][result.target]
    assert (summary["measured"], summary["pending"], summary["unknown"], summary["late"]) == (
        0, 0, 1, 0)
    assert summary["p90_days"] is None and summary["errors"] == 1


def test_fresh_snapshot_bounds_pending_decidable_lag_at_observation_time():
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/new", datetime(2026, 10, 31, 12, tzinfo=UTC), premier_eligible=True),
    ), snapshot_history=True, snapshot_observed_at=datetime(2026, 11, 4, 6, tzinfo=UTC))
    report = slo.release_report(history, slo.load_config(), now=NOW, counts_only=False)
    result = next(r for r in report.results if r.target == "release-decidable-lag")
    assert result.status == "breach"
    summary = report.release_coverage["stages"][result.target]
    assert (summary["measured"], summary["pending"], summary["unknown"], summary["late"]) == (
        1, 1, 0, 1)
    assert summary["p50_days"] == summary["p90_days"] == 3.75
    assert report.release_coverage["releases"][0]["stages"][result.target]["lag_days"] == 3.75


@pytest.mark.parametrize("has_history", [True, False])
def test_observed_decidable_completion_stays_measured_when_other_snapshots_are_stale(has_history):
    history = slo.ReleaseHistory(releases=(
        slo.Release("lab/new", datetime(2026, 11, 1, 12, tzinfo=UTC),
                    decidable_at=datetime(2026, 11, 2, 12, tzinfo=UTC), premier_eligible=True),
    ), snapshot_history=has_history,
       snapshot_observed_at=datetime(2026, 11, 2, 12, tzinfo=UTC) if has_history else None)
    report = slo.release_report(history, slo.load_config(), now=NOW, counts_only=False)
    result = next(r for r in report.results if r.target == "release-decidable-lag")
    assert result.status == "met" and not result.errors
    summary = report.release_coverage["stages"][result.target]
    assert (summary["completed"], summary["pending"], summary["unknown"]) == (1, 0, 0)
    assert summary["p90_days"] == 1
