"""MODEL-215: the coverage targets, the daily report and its alerts."""

from __future__ import annotations

import json
import re
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from api.ranking.engine import MIN_BENCHMARK_COUNT
from decision.snapshot import EvidenceValue, SnapshotInputs, audit_build, default_registry
from scripts.slo import alerts, render
from scripts.slo.__main__ import STAGED
from scripts.slo.report import (
    Check,
    Finding,
    Inputs,
    Lineup,
    Report,
    Result,
    Target,
    WatchedWorkflow,
    check_fact_age,
    check_facts_verified,
    check_lab_feeds,
    check_live_reading_age,
    check_new_model_cards,
    check_plans,
    check_refresh_prs,
    check_unclassified_evidence,
    check_workflows,
    load_config,
    measure,
    report_from_json,
    settle,
)

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "method" / "coverage-slo.md"
AS_OF = date(2026, 9, 29)
NOW = datetime(2026, 9, 29, 9, 37, tzinfo=UTC)
CONFIG = load_config()


# ── the written targets and the machine targets agree ──────────────────────


def _doc_table() -> dict[str, tuple[str, str]]:
    rows = {}
    for line in DOC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `([a-z-]+)` \| [^|]+ \| ([^|]+) \| ([^|]+) \|$", line)
        if m:
            rows[m[1]] = (m[2].strip(), m[3].strip())
    return rows


def test_every_target_is_written_down_with_its_threshold_and_state() -> None:
    table = _doc_table()
    assert list(table) == [t.id for t in CONFIG.targets]
    for t in CONFIG.targets:
        threshold, in_force = table[t.id]
        assert in_force.startswith("yes" if t.in_force else "no"), t.id
        for key in ("max_age_days", "min_benchmarks", "max_open_days"):
            if key in t.params:
                assert str(t.params[key]) in threshold, (t.id, key)


def test_the_thin_evidence_floor_is_the_ranking_floor() -> None:
    assert CONFIG.target("thin-evidence").params["min_benchmarks"] == MIN_BENCHMARK_COUNT


def test_every_watched_workflow_exists() -> None:
    for w in CONFIG.workflows:
        assert (ROOT / ".github" / "workflows" / w.file).is_file(), w.file


# ── a status is never a false green ────────────────────────────────────────


TARGET = Target("t", "A target", True, {})


def test_a_check_that_measured_nothing_is_not_met() -> None:
    r = settle(TARGET, Check(measured=0))
    assert r.status == "error"
    assert r.errors == ("nothing was measured, so the target cannot be called met",)


def test_an_unreadable_input_is_an_error_even_with_no_findings() -> None:
    assert settle(TARGET, Check(measured=5, errors=("models.dev: 503",))).status == "error"


def test_a_target_not_in_force_is_never_met_or_breached() -> None:
    r = settle(Target("s", "Speed", False, {}), Check(measured=3, findings=(Finding("x", "y"),)))
    assert (r.status, len(r.findings)) == ("not_in_force", 1)


def _report(*statuses: str) -> Report:
    return Report(AS_OF, NOW, None, None, tuple(
        Result(f"t{i}", "T", s, 1, ()) for i, s in enumerate(statuses)))  # type: ignore[arg-type]


@pytest.mark.parametrize(("statuses", "expected"), [
    (("met", "not_in_force"), "met"),
    (("met", "error"), "breach"),
    (("met", "breach"), "breach"),
])
def test_the_report_is_met_only_when_every_in_force_target_is(statuses, expected) -> None:
    assert _report(*statuses).status == expected


# ── workflow health ────────────────────────────────────────────────────────


def _run(conclusion: str | None, hours_ago: float, status: str = "completed") -> dict:
    created = (NOW - timedelta(hours=hours_ago)).isoformat().replace("+00:00", "Z")
    return {"status": status, "conclusion": conclusion, "created_at": created,
            "html_url": f"https://example.test/{hours_ago}"}


DAILY = WatchedWorkflow("daily.yml", 30, True)


def test_a_failing_workflow_is_a_breach_naming_the_streak() -> None:
    check = check_workflows(
        {"daily.yml": [_run("failure", 3), _run("failure", 27), _run("success", 51)]},
        [DAILY], NOW)
    assert [f.detail.split(":")[0] for f in check.findings] == [
        "latest run concluded failure; 2 failing run(s) in a row"]


def test_a_cancelled_run_is_skipped_over_and_an_overdue_one_is_a_breach() -> None:
    check = check_workflows({"daily.yml": [_run("cancelled", 1), _run("success", 40)]},
                            [DAILY], NOW)
    assert [f.detail for f in check.findings] == ["latest completed run is 40 h old, limit 30 h"]


def test_a_switched_off_pipeline_is_a_breach_only_where_skipping_is_not_ok() -> None:
    runs = {"signals.yml": [_run("skipped", 1)], "daily.yml": [_run("skipped", 1)]}
    check = check_workflows(runs, [WatchedWorkflow("signals.yml", 3, False), DAILY], NOW)
    assert [f.subject for f in check.findings] == ["signals.yml"]


def test_a_first_run_still_in_progress_is_not_a_breach() -> None:
    check = check_workflows({"daily.yml": [_run(None, 0, "in_progress")]}, [DAILY], NOW)
    assert (check.measured, check.findings) == (1, ())


def test_unreadable_runs_are_an_error_not_a_pass() -> None:
    check = check_workflows({"daily.yml": "HTTPError: 502"}, [DAILY], NOW)
    assert settle(TARGET, check).status == "error"


# ── the evidence and fact checks ───────────────────────────────────────────


LINEUP = Lineup(models=("acme/m1",), offerings={"acme/m1": ("p/acme/m1/global/standard",)},
                claims={"acme/m1": ("software-engineering",)})


def _reading(benchmark: str, record_id: str) -> EvidenceValue:
    # A board run date long ago: a re-read does not move it.
    return EvidenceValue(benchmark, None, None, 0.5, None, None, None, None,
                         date(2026, 2, 1), ("s",), record_id=record_id, date_type="evaluated")


def test_a_live_reading_ages_from_its_last_re_read_not_the_board_run_date() -> None:
    records = {"fresh": {"verification": {"date": "2026-09-20"}},
               "stale": {"verification": {"date": "2026-08-01"}}}
    evidence = {"acme/m1": [_reading("swe", "fresh"), _reading("hle", "stale")]}
    check = check_live_reading_age(LINEUP, evidence, records.__getitem__, AS_OF, 30)
    assert check.measured == 2
    assert [(f.subject, f.detail) for f in check.findings] == [
        ("acme/m1", "hle: last read 59 days ago (2026-08-01)")]


def test_a_stated_unknown_is_honest_but_a_quarantined_fact_is_not() -> None:
    rejected = {("acme/m1", "model.parameters_total"): "unknown",
                ("p/acme/m1/global/standard", "offering.price.input"): "quarantined (mismatch)"}
    authored = {"acme/m1": ["model.parameters_total"],
                "p/acme/m1/global/standard": ["offering.price.input"]}
    check = check_facts_verified(LINEUP, authored, rejected, gaps=())
    assert check.measured == 2
    assert check.findings == (Finding("p/acme/m1/global/standard",
                                      "offering.price.input: quarantined (mismatch)"),)


def test_a_subject_with_no_verified_fact_in_scope_is_a_finding_not_a_skip() -> None:
    records = {"r1": {"verification": {"date": "2026-09-28"}}}
    fact_records = {"plan/a": {"offering.subscription.price": "r1"}, "plan/b": {}}
    check = check_plans([{"id": "plan/a"}, {"id": "plan/b"}], fact_records,
                        records.__getitem__, rejected={}, as_of=AS_OF, max_age_days=7)
    assert check.measured == 2
    assert check.findings == (Finding("plan/b", "no verified plan facts"),)
    prices = check_fact_age(["o/1"], {"o/1": {"offering.data.retention": "r1"}},
                            records.__getitem__, AS_OF, 7,
                            lambda f: f.startswith("offering.price."), "price")
    assert settle(TARGET, prices).status == "breach"


def test_every_lineup_lab_needs_a_release_feed() -> None:
    lineup = Lineup(("openai/gpt-x", "querit/querit"), {}, {})
    check = check_lab_feeds(lineup, absent_pages=("openai",))
    assert [(f.subject, f.detail) for f in check.findings] == [
        ("openai", "models.dev has no 'openai' page"),
        ("querit", "no release feed tracks this lab; lineup models: querit/querit"),
    ]


def _card(models: Path, model_id: str, name: str, released: str) -> None:
    lab, slug = model_id.split("/")
    (models / lab).mkdir(parents=True, exist_ok=True)
    (models / lab / f"{slug}.md").write_text(
        f"---\nmodel_id: {model_id}\ndisplay_name: {name}\nrelease_date: '{released}'\n---\n",
        encoding="utf-8")


def test_a_recent_release_without_a_card_is_a_breach(tmp_path: Path) -> None:
    _card(tmp_path, "anthropic/claude-held-1", "Claude Held 1", "2026-09-20")
    payload = {"anthropic": {"models": {
        "claude-held-1": {"id": "claude-held-1", "name": "Claude Held 1",
                          "release_date": "2026-09-20"},
        "claude-new-2": {"id": "claude-new-2", "name": "Claude New 2",
                         "release_date": "2026-09-27"},
        "claude-today": {"id": "claude-today", "name": "Claude Today",
                         "release_date": "2026-09-29"},
        "claude-old": {"id": "claude-old", "name": "Claude Old", "release_date": "2026-01-02"},
    }}}
    check, absent = check_new_model_cards(payload, None, tmp_path, AS_OF, 1, 30)
    assert check.measured == 1
    assert [f.subject for f in check.findings] == ["anthropic/claude-new-2"]
    assert "openai" in absent


def test_an_unreadable_models_dev_is_an_error(tmp_path: Path) -> None:
    check, _ = check_new_model_cards(None, "ConnectError: boom", tmp_path, AS_OF, 1, 30)
    assert settle(TARGET, check).errors == ("models.dev could not be read: ConnectError: boom",)


# ── refresh pull requests (MODEL-232) ──────────────────────────────────────


REFRESH = "data/weekly-leaderboard-refresh"


def _pr(number: int, days_ago: float, *, state: str = "open", merged: bool = False) -> dict:
    created = NOW - timedelta(days=days_ago)
    closed = None if state == "open" else (created + timedelta(minutes=19)).isoformat()
    return {"number": number, "state": state, "html_url": f"https://example.test/pull/{number}",
            "created_at": created.isoformat().replace("+00:00", "Z"), "closed_at": closed,
            "merged_at": closed if merged else None}


def _refresh(*prs: dict) -> Check:
    return check_refresh_prs({REFRESH: list(prs)}, [REFRESH], NOW, 3)


def test_a_refresh_pr_open_past_the_limit_is_a_breach() -> None:
    check = _refresh(_pr(401, 4))
    assert check.measured == 1
    assert check.findings == (Finding(
        REFRESH, "#401 opened 2026-09-25, still open; 4 days without merging, limit 3: "
                 "https://example.test/pull/401"),)


def test_a_refresh_closed_unmerged_is_a_breach_once_past_the_limit() -> None:
    assert _refresh(_pr(337, 2, state="closed")).findings == ()
    [finding] = _refresh(_pr(337, 3.5, state="closed")).findings
    assert "#337 opened 2026-09-25, closed unmerged on 2026-09-25" in finding.detail


def test_only_the_newest_refresh_pr_counts() -> None:
    assert _refresh(_pr(337, 10, state="closed"), _pr(402, 1)).findings == ()
    assert _refresh(_pr(337, 10, state="closed"),
                    _pr(402, 5, state="closed", merged=True)).findings == ()


def test_a_branch_with_no_refresh_pr_is_measured_and_met() -> None:
    check = _refresh()
    assert (check.measured, check.findings, check.errors) == (1, (), ())


def test_unreadable_refresh_prs_are_an_error_not_a_pass() -> None:
    check = check_refresh_prs({REFRESH: "CalledProcessError: 403"}, [REFRESH], NOW, 3)
    assert settle(CONFIG.target("refresh-pr-merged"), check).status == "error"


def test_the_refresh_pr_fetch_reads_each_branch_once() -> None:
    from scripts.slo.report import fetch_refresh_prs

    calls = []

    def gh(args, stdin=None):
        calls.append(args)
        return json.dumps([_pr(401, 4)])

    got = fetch_refresh_prs([REFRESH], gh)
    assert calls == [["api", "repos/turbobeest/modelspec/pulls?state=all&head=turbobeest:"
                             f"{REFRESH}&sort=created&direction=desc&per_page=5"]]
    assert got[REFRESH][0]["number"] == 401


def test_the_weekly_refresh_branch_is_watched() -> None:
    workflow = (ROOT / ".github" / "private-writers" / "leaderboard-refresh.yml").read_text()
    for branch in CONFIG.target("refresh-pr-merged").params["branches"]:
        assert f"branch: {branch}" in workflow


# ── end to end: a staged breach through measure, render and the alert plan ──


def _measured(tmp_path: Path, staged: dict | None = None,
              refresh_prs: dict | None = None) -> Report:
    audit = audit_build(
        SnapshotInputs(models=[{"id": "acme/m1", "lifecycle": "active", "facts": []}]),
        registry=default_registry(), premier=["acme/m1"], as_of=AS_OF, guard=None)
    inputs = Inputs(
        audit=audit,
        premier={"models": [{"model_id": "acme/m1", "clauses": []}]},
        authored={},
        models_dev=(None, "offline"),
        runs={w.file: [_run("success", 1)] for w in CONFIG.workflows},
        models_dir=tmp_path,
        refresh_prs=refresh_prs or {
            b: [] for b in CONFIG.target("refresh-pr-merged").params["branches"]},
        extra_findings=staged or {},
    )
    return measure(inputs, CONFIG, as_of=AS_OF, now=NOW)


def test_measure_states_every_breach_and_round_trips_through_json(tmp_path: Path) -> None:
    report = _measured(tmp_path, {"workflow-health": (STAGED,)})
    by_id = {r.target: r for r in report.results}
    assert report.status == "breach"
    assert by_id["new-model-cards"].status == "error"
    assert by_id["lab-release-feeds"].findings[0].subject == "acme"
    assert by_id["thin-evidence"].status == "breach"
    assert len(by_id["lineup-facts-verified"].findings) == 20  # every guaranteed facet
    assert by_id["workflow-health"].findings == (STAGED,)
    assert by_id["premier-speed-age"].status == "not_in_force"
    assert report_from_json(json.loads(json.dumps(report.to_json()))) == report

    render.write(report, tmp_path / "out", CONFIG.report_url)
    page = (tmp_path / "out" / "index.html").read_text(encoding="utf-8")
    assert "noindex" in page and "staged-breach" in page
    assert "X-Robots-Tag: noindex" in (tmp_path / "out" / "_headers").read_text()


def test_a_stale_refresh_pr_opens_a_coverage_issue(tmp_path: Path) -> None:
    report = _measured(tmp_path, refresh_prs={REFRESH: [_pr(337, 4, state="closed")]})
    [result] = [r for r in report.results if r.target == "refresh-pr-merged"]
    assert result.status == "breach"
    assert [(a.kind, a.target, a.title) for a in
            alerts.plan(report, CONFIG, [], NOW, only=["refresh-pr-merged"])] == [
        ("create", "refresh-pr-merged", "Coverage SLO breach: refresh-pr-merged")]


# ── alerts: one issue per target, updated in place ─────────────────────────


def _one(status: str, *findings: Finding) -> Report:
    return Report(AS_OF, NOW, None, None, (Result("plan-age", "Plans", status, 5, findings),))  # type: ignore[arg-type]


BREACH = _one("breach", Finding("openai/subscription/go", "stale"))


def _issue(report: Report, since: datetime, escalated: bool = False,
           number: int = 7) -> alerts.Issue:
    body = alerts.body_for(report.results[0], report, CONFIG, since, escalated)
    return alerts.Issue(number, alerts.title_for("plan-age"), body)


def test_a_new_breach_opens_one_issue() -> None:
    [action] = alerts.plan(BREACH, CONFIG, [], NOW)
    assert (action.kind, action.title) == ("create", "Coverage SLO breach: plan-age")
    assert alerts.MARKER.search(action.body)["since"] == NOW.isoformat()


def test_an_unchanged_breach_makes_no_change() -> None:
    assert alerts.plan(BREACH, CONFIG, [_issue(BREACH, NOW - timedelta(hours=2))], NOW) == []


def test_changed_findings_edit_the_issue_in_place() -> None:
    later = _one("breach", Finding("openai/subscription/go", "stale"), Finding("x", "y"))
    [action] = alerts.plan(later, CONFIG, [_issue(BREACH, NOW - timedelta(hours=2))], NOW)
    assert (action.kind, action.issue) == ("edit", 7)


def test_a_breach_past_24_hours_escalates_once() -> None:
    since = NOW - timedelta(hours=25)
    edit, comment = alerts.plan(BREACH, CONFIG, [_issue(BREACH, since)], NOW)
    assert (edit.kind, alerts.MARKER.search(edit.body)["escalated"]) == ("edit", "1")
    assert comment.kind == "comment" and comment.body.startswith("@turbobeest ")
    assert alerts.plan(BREACH, CONFIG, [_issue(BREACH, since, escalated=True)], NOW) == []


def test_a_met_target_closes_its_issue_with_a_comment() -> None:
    met = _one("met")
    actions = alerts.plan(met, CONFIG, [_issue(BREACH, NOW - timedelta(hours=30))], NOW)
    assert [(a.kind, a.issue) for a in actions] == [("comment", 7), ("close", 7)]


def test_a_target_not_in_force_never_opens_an_issue() -> None:
    assert alerts.plan(_one("not_in_force", Finding("a", "b")), CONFIG, [], NOW) == []


def test_duplicates_are_closed_and_only_limits_the_targets() -> None:
    since = NOW - timedelta(hours=1)
    issues = [_issue(BREACH, since, number=3), _issue(BREACH, since, number=9)]
    actions = alerts.plan(BREACH, CONFIG, issues, NOW)
    assert [(a.kind, a.issue) for a in actions] == [("comment", 9), ("close", 9)]
    assert alerts.plan(BREACH, CONFIG, [], NOW, only=["workflow-health"]) == []


def test_apply_speaks_gh_and_creates_the_label_before_the_first_issue() -> None:
    calls: list[tuple[list[str], str | None]] = []

    def gh(args, stdin=None):
        calls.append((list(args), stdin))
        return ""

    actions = alerts.plan(BREACH, CONFIG, [], NOW)
    alerts.apply(actions, gh, CONFIG.issue_label, repo="o/r")
    assert [c[0][:2] for c in calls] == [["label", "create"], ["issue", "create"]]
    assert calls[1][0][-2:] == ["--body-file", "-"] and calls[1][1] == actions[0].body


def test_unclassified_evidence_names_each_model_with_a_row_kept_out() -> None:
    excluded = {"acme/m1": {"unclassified": 2, "unsourced": 1}, "acme/m2": {"unsourced": 4},
                None: {"quarantined": 1}}
    check = check_unclassified_evidence(excluded, admitted=10)
    assert check.measured == 12
    assert check.findings == (
        Finding("acme/m1", "2 evidence row(s) kept out: no measured_by"),)
    clean = check_unclassified_evidence({"acme/m2": {"unsourced": 4}}, admitted=10)
    assert clean.findings == () and clean.measured == 10
    assert settle(CONFIG.target("unclassified-evidence"), clean).status == "met"
    assert settle(CONFIG.target("unclassified-evidence"), check).status == "breach"
