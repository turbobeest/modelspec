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
    WorkflowRepo,
    check_fact_age,
    check_facts_verified,
    check_lab_feeds,
    check_live_reading_age,
    check_new_model_cards,
    check_plans,
    check_refresh_prs,
    check_unclassified_evidence,
    check_workflows,
    discover_workflows,
    fetch_runs,
    load_config,
    measure,
    report_from_json,
    settle,
)
from scripts.slo.schedule import CronError, cadence_hours, scheduled_workflows

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


def test_every_unscheduled_workflow_exists() -> None:
    for w in CONFIG.unscheduled:
        assert w.repo == "turbobeest/modelspec"
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


# ── workflow health (MODEL-215, MODEL-421) ────────────────────────────────


@pytest.mark.parametrize(("crons", "hours"), [
    (["17 6 * * 1"], 168),
    (["41 */6 * * *"], 6),
    (["23 * * * *"], 1),
    (["0 6 * * *"], 24),
    (["17 6 * * 1", "47 6 * * *"], 24),
    (["0 9 * * MON-FRI"], 72),
    (["0 0 1 * *"], 744),
    (["0 0 13 * 5"], 168),
])
def test_a_cadence_is_the_longest_gap_between_cron_firings(crons, hours) -> None:
    assert cadence_hours(crons) == hours


@pytest.mark.parametrize("line", ["0 6 * *", "61 * * * *", "*/0 * * * *", "0 6 * * funday"])
def test_an_unreadable_cron_line_is_refused(line) -> None:
    with pytest.raises(CronError):
        cadence_hours([line])


def _workflows(base: Path, files: dict[str, str]) -> Path:
    d = base / ".github" / "workflows"
    d.mkdir(parents=True)
    for name, text in files.items():
        (d / name).write_text(text, encoding="utf-8")
    return base


WEEKLY = "on:\n  schedule:\n    - cron: '17 6 * * 1'\n  workflow_dispatch:\njobs: {}\n"
EVERY_6H = "on:\n  schedule:\n    - cron: '41 */6 * * *'\njobs: {}\n"
DAILY_CRON = "on:\n  schedule:\n    - cron: 0 6 * * *\njobs: {}\n"
PUSH_ONLY = "on:\n  push:\n    branches: [main]\njobs: {}\n"
def test_the_watched_list_and_cadences_come_from_the_cron_triggers(tmp_path: Path) -> None:
    public = _workflows(tmp_path / "public", {
        "release-watch.yml": EVERY_6H, "accuracy-nightly.yml": DAILY_CRON,
        "deploy-sites.yml": PUSH_ONLY})
    private = _workflows(tmp_path / "private", {
        "data-trust-audit.yml": WEEKLY, "price-reread.yml": WEEKLY,
        "daily-research.yml": DAILY_CRON, "release-signals.yml": PUSH_ONLY})
    watched, errors = discover_workflows(
        tmp_path, CONFIG, {"turbobeest/modelspec": public,
                           "turbobeest/modelspec-data": private})
    assert errors == ()
    assert [(w.key, w.cadence_hours, w.max_age_hours) for w in watched] == [
        ("modelspec/accuracy-nightly.yml", 24, 36),
        ("modelspec/release-watch.yml", 6, 9),
        ("modelspec-data/daily-research.yml", 24, 36),
        ("modelspec-data/data-trust-audit.yml", 168, 252),
        ("modelspec-data/price-reread.yml", 168, 252),
        # Push-triggered, so no cadence: only a red run counts.
        ("modelspec/deploy-sites.yml", None, None),
    ]


def test_a_missing_private_checkout_is_an_error_not_an_empty_list(tmp_path: Path) -> None:
    public = _workflows(tmp_path / "public", {"release-watch.yml": EVERY_6H})
    watched, errors = discover_workflows(tmp_path, CONFIG, {"turbobeest/modelspec": public})
    assert "modelspec-data/release-watch.yml" not in {w.key for w in watched}
    assert len(errors) == 1 and errors[0].startswith("turbobeest/modelspec-data: no workflow")
    check = check_workflows({w.key: [] for w in watched}, watched, NOW, errors)
    assert settle(CONFIG.target("workflow-health"), check).status == "error"


def test_every_scheduled_workflow_here_is_watched_with_its_cron_cadence() -> None:
    found, errors = scheduled_workflows(ROOT / ".github" / "workflows")
    assert errors == []
    cadences = {s.file: s.cadence_hours for s in found}
    assert cadences["release-watch.yml"] == 6
    assert cadences["coverage-slo.yml"] == 24
    assert "deploy-sites.yml" not in cadences


FIXTURE_RUNS = json.loads(
    (ROOT / "tests" / "fixtures" / "workflow_health" / "runs.json").read_text(encoding="utf-8"))


def _fixture_gh(calls: list):
    def gh(args, stdin=None):
        calls.append(args)
        path = args[1].split("?", 1)[0]
        if path not in FIXTURE_RUNS:
            raise ValueError(f"no fixture for {path}")
        return json.dumps(FIXTURE_RUNS[path])
    return gh


def _fixture_check() -> tuple[Check, list]:
    watched = (
        WatchedWorkflow("turbobeest/modelspec-data", "data-trust-audit.yml", 168, 252),
        WatchedWorkflow("turbobeest/modelspec-data", "price-reread.yml", 168, 252),
        WatchedWorkflow("turbobeest/modelspec", "release-watch.yml", 6, 9),
        WatchedWorkflow("turbobeest/modelspec", "accuracy-nightly.yml", 24, 36),
        WatchedWorkflow("turbobeest/modelspec-data", "daily-research.yml", 24, 36),
    )
    calls: list = []
    gh = _fixture_gh(calls)
    runs = fetch_runs(watched, {"turbobeest/modelspec": gh, "turbobeest/modelspec-data": gh})
    return check_workflows(runs, watched, NOW), calls


def test_failed_cancelled_and_stale_workflows_are_red_with_their_run_urls() -> None:
    check, calls = _fixture_check()
    assert check.measured == 5 and check.errors == ()
    assert [(f.subject, f.detail) for f in check.findings] == [
        ("modelspec-data/data-trust-audit.yml",
         "latest run concluded failure on 2026-09-29T06:37:00Z; 2 red run(s) in a row: "
         "https://github.com/turbobeest/modelspec-data/actions/runs/1001"),
        ("modelspec-data/price-reread.yml",
         "latest run concluded cancelled on 2026-09-28T07:37:00Z; 1 red run(s) in a row: "
         "https://github.com/turbobeest/modelspec-data/actions/runs/1004"),
        ("modelspec/release-watch.yml",
         "has not run for 20 h; scheduled every 6 h, limit 9 h; last run: "
         "https://github.com/turbobeest/modelspec/actions/runs/1006"),
    ]
    # One call per workflow, each on main.
    assert calls[0] == ["api", "repos/turbobeest/modelspec-data/actions/workflows/"
                               "data-trust-audit.yml/runs?branch=main&per_page=10"
                               "&exclude_pull_requests=true"]
    assert len(calls) == 5


def test_a_red_workflow_makes_the_report_red() -> None:
    check, _ = _fixture_check()
    assert settle(CONFIG.target("workflow-health"), check).status == "breach"


def test_a_successful_run_and_a_run_in_progress_are_green() -> None:
    check, _ = _fixture_check()
    red = {f.subject for f in check.findings}
    assert {"modelspec/accuracy-nightly.yml", "modelspec-data/daily-research.yml"} & red == set()


def _run(conclusion: str | None, hours_ago: float, status: str = "completed") -> dict:
    created = (NOW - timedelta(hours=hours_ago)).isoformat().replace("+00:00", "Z")
    return {"status": status, "conclusion": conclusion, "created_at": created,
            "html_url": f"https://example.test/{hours_ago}"}


DAILY = WatchedWorkflow("turbobeest/modelspec", "daily.yml", 24, 36)


@pytest.mark.parametrize("conclusion", ["cancelled", "timed_out", "startup_failure",
                                        "action_required"])
def test_a_cancelled_or_timed_out_run_is_never_skipped_over(conclusion) -> None:
    check = check_workflows({DAILY.key: [_run(conclusion, 1), _run("success", 25)]},
                            [DAILY], NOW)
    assert [f.detail.split(" on ")[0] for f in check.findings] == [
        f"latest run concluded {conclusion}"]


def test_a_job_switched_off_by_its_own_if_is_not_red() -> None:
    check = check_workflows({DAILY.key: [_run("skipped", 1)]}, [DAILY], NOW)
    assert (check.measured, check.findings) == (1, ())


def test_a_scheduled_workflow_that_never_ran_is_red() -> None:
    check = check_workflows({DAILY.key: []}, [DAILY], NOW)
    assert [f.detail for f in check.findings] == [
        "no run on main; scheduled every 24 h, limit 36 h"]


def test_unreadable_runs_are_an_error_not_a_pass() -> None:
    check = check_workflows({DAILY.key: "HTTPError: 502"}, [DAILY], NOW)
    assert settle(TARGET, check).status == "error"


def test_an_unset_private_token_is_an_error_for_its_workflows() -> None:
    from scripts.slo.report import repo_clients

    clients = repo_clients(CONFIG, gh=lambda args, stdin=None: "{}", environ={})
    assert clients["turbobeest/modelspec-data"] == (
        "MODELSPEC_DATA_TOKEN is not set, so turbobeest/modelspec-data's runs cannot be read")
    private = WatchedWorkflow("turbobeest/modelspec-data", "price-reread.yml", 168, 252)
    runs = fetch_runs([private], clients)
    check = check_workflows(runs, [private], NOW)
    assert settle(TARGET, check).status == "error"


def test_the_private_repo_is_read_with_its_own_token() -> None:
    from scripts.slo.report import repo_clients

    clients = repo_clients(CONFIG, environ={"MODELSPEC_DATA_TOKEN": "t"})
    assert callable(clients["turbobeest/modelspec-data"])
    assert [r.token_env for r in CONFIG.workflow_repos] == [None, "MODELSPEC_DATA_TOKEN"]
    workflow = (ROOT / ".github" / "workflows" / "coverage-slo.yml").read_text()
    assert "repository: turbobeest/modelspec-data" in workflow
    assert "sparse-checkout: .github/workflows" in workflow
    assert "path: modelspec-data" in workflow
    assert WorkflowRepo("turbobeest/modelspec-data", "modelspec-data",
                        "MODELSPEC_DATA_TOKEN") in CONFIG.workflow_repos


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
        runs={DAILY.key: [_run("success", 1)]},
        watched=(DAILY,),
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
