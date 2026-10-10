"""Offline subscription panels, receipts, reports and checkpoint identity."""

import copy
import json
import os
from datetime import datetime, timezone

import pytest
import yaml

from qa import agent_harness, subscription_jobs as jobs, tui_harness as harness
from qa import tui_homes as homes, tui_isolation as isolation, tui_providers as providers
from qa.docker.entrypoint import VENDOR_ENV


CASE = {
    "id": "panel-case", "family": "F1", "persona": "Developer", "request": "Choose a model",
    "constraints": {}, "expected": None, "rubric": ["Use the supplied evidence"],
}
PASS = {
    "passed": True, "rationale": "Supported by evidence", "answer_kind": "single",
    "top_models": ["lab/model-a"], "missing_capabilities": [],
}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    for name in tuple(os.environ):
        if VENDOR_ENV.search(name) and not name.startswith("MODELSPEC_"):
            monkeypatch.delenv(name)
    monkeypatch.delenv("MODELSPEC_API_KEY", raising=False)
    monkeypatch.setattr(jobs, "git_command", lambda *a: "panel-engine")
    monkeypatch.setattr(jobs, "network_probe", lambda: pytest.fail("Unexpected network probe"))


@pytest.fixture
def config():
    return yaml.safe_load((harness.HERE / "tui_config.yaml").read_text())


def ready():
    return {cli: {"supported": True, "verified": True, "reason": None} for cli in providers.CLIS}


def execution(cli, answer, status="completed", *, limit=None, misuse=(), attempts=1):
    return providers.Execution(
        providers.Transcript(final_answer=answer, model=f"{cli}-actual", tokens_in=12, tokens_out=3),
        0, 25, status, limit_reason=limit, misuse=list(misuse), attempts=attempts,
    )


def install_launch(monkeypatch, replies, *, after=None):
    calls = []

    def launch(cli, config, workspace, prompt, *, mcp_enabled, **kwargs):
        calls.append((cli, mcp_enabled, workspace, prompt))
        result = execution(cli, "Choose lab/model-a.") if mcp_enabled else replies[cli]
        if after is not None:
            after(cli, mcp_enabled)
        return result

    monkeypatch.setattr(harness, "launch", launch)
    return calls


@pytest.mark.parametrize("arm,judges", [
    ("claude", ["grok", "codex"]),
    ("codex", ["grok", "claude"]),
    ("grok", ["codex", "claude"]),
])
def test_default_pair_runs_independently_on_identical_evidence(arm, judges, config, tmp_path, monkeypatch):
    calls = install_launch(monkeypatch, {
        cli: execution(cli, json.dumps(PASS)) for cli in ("claude", "codex", "grok")
    })
    runner = harness.Runner(config, tmp_path, ready())
    row = runner.scenario(CASE, arm)
    assert [(cli, mcp) for cli, mcp, _, _ in calls] == [(arm, True), (judges[0], False), (judges[1], False)]
    assert calls[1][3] == calls[2][3]
    assert json.loads(calls[1][3].split("Submitted data:\n")[1]) == {
        "scenario": {
            "id": "panel-case", "family": "F1", "persona": "Developer", "request": "Choose a model",
            "constraints": {}, "expected": None, "rubric": ["Use the supplied evidence"],
        },
        "final_answer": "Choose lab/model-a.", "tool_calls": [],
    }
    assert len({workspace for _, _, workspace, _ in calls}) == 3
    assert row["success"] is True
    assert row["evaluation_status"] == "judged"
    assert [(j["cli"], j["model"], j["passed"]) for j in row["judges"]] == [
        (judges[0], f"{judges[0]}-actual", True), (judges[1], f"{judges[1]}-actual", True),
    ]
    assert [(j["cli"], j["status"], j["attempts"]) for j in row["judge_executions"]] == [
        (judges[0], "completed", 1), (judges[1], "completed", 1),
    ]
    assert runner.counts[arm] == {"agent": 1, "judge": 0}
    assert [runner.counts[judge] for judge in judges] == [{"agent": 0, "judge": 1}, {"agent": 0, "judge": 1}]


@pytest.mark.parametrize("route,message", [
    (["claude", "codex"], "different CLI family"),
    (["grok", "claude"], "different CLI family"),
    (["codex", "codex"], "two distinct judge families"),
    (["grok", "grok"], "two distinct judge families"),
    (["grok"], "two distinct judges"),
    (["grok", "codex", "grok"], "two distinct judges"),
    (["grok", "unknown"], "different CLI family"),
    (["gemini", "codex"], "gemini cannot judge"),
    (None, "two distinct judges"),
])
def test_config_refuses_invalid_panel_members(route, message, config):
    config["judges"]["claude"] = route
    with pytest.raises(ValueError, match=message):
        harness.validate_config(config)


def test_pair_override_and_documented_single_override(config):
    assert harness.apply_judge_overrides(config, ["claude=codex,grok"]) == {"claude": ["codex", "grok"]}
    assert harness.required_clis(["claude"], config) == ["claude", "codex", "grok"]
    assert harness.apply_judge_overrides(config, ["claude=grok"]) == {"claude": "grok"}
    assert harness.required_clis(["claude"], config) == ["claude", "grok"]


@pytest.mark.parametrize("override,message", [
    ("claude=grok,grok", "two distinct judge families"),
    ("claude=grok,claude", "different CLI family"),
    ("claude=claude,codex", "different CLI family"),
    ("claude=grok,codex,claude", "two distinct judges"),
    ("claude=grok,gemini", "gemini cannot judge"),
])
def test_bad_pair_override_leaves_config_untouched(override, message, config):
    before = copy.deepcopy(config)
    with pytest.raises(ValueError, match=message):
        harness.apply_judge_overrides(config, [override])
    assert config == before


@pytest.mark.parametrize("second,passed,agreed,kind,top", [
    ({}, True, True, "single", ["lab/model-a"]),
    ({"passed": False}, False, False, "single", ["lab/model-a"]),
    ({"top_models": ["lab/model-b"]}, False, False, "abstain", []),
    ({"answer_kind": "abstain", "top_models": []}, False, False, "abstain", []),
])
def test_panel_requires_unanimous_verdict_and_extraction(second, passed, agreed, kind, top, config, tmp_path, monkeypatch):
    install_launch(monkeypatch, {
        "grok": execution("grok", json.dumps(PASS)),
        "codex": execution("codex", json.dumps(PASS | second)),
    })
    row = harness.Runner(config, tmp_path, ready()).scenario(CASE, "claude")
    assert row["judge"] == {
        "passed": passed, "rationale": "xai/grok-actual: Supported by evidence\nopenai/codex-actual: Supported by evidence",
        "answer_kind": kind, "top_models": top, "missing_capabilities": [],
        "mode": "live", "strategy": "panel", "agreed": agreed,
    }
    assert row["success"] is passed
    assert row["expected_match"] is None
    assert len(row["judges"]) == 2


def test_top_model_set_is_unordered_and_missing_capabilities_are_combined(config, tmp_path, monkeypatch):
    first = PASS | {"answer_kind": "tied", "top_models": ["lab/model-a", "lab/model-b"], "missing_capabilities": ["z"]}
    second = PASS | {"answer_kind": "tied", "top_models": ["lab/model-b", "lab/model-a", "lab/model-b"], "missing_capabilities": ["a", "z"]}
    install_launch(monkeypatch, {"grok": execution("grok", json.dumps(first)), "codex": execution("codex", json.dumps(second))})
    row = harness.Runner(config, tmp_path, ready()).scenario(CASE, "claude")
    assert (row["success"], row["judge"]["agreed"], row["judge"]["top_models"], row["judge"]["missing_capabilities"]) == (
        True, True, ["lab/model-a", "lab/model-b"], ["a", "z"],
    )


@pytest.mark.parametrize("judge", ["grok", "codex"])
@pytest.mark.parametrize("status,answer,evaluation", [
    ("timeout", "", "judge_timeout"),
    ("empty_answer", "", "judge_empty_answer"),
    ("completed", "invalid JSON", "evaluation_error"),
])
def test_failed_or_invalid_member_preserves_the_other_opinion(judge, status, answer, evaluation, config, tmp_path, monkeypatch):
    replies = {cli: execution(cli, json.dumps(PASS)) for cli in ("grok", "codex")}
    replies[judge] = execution(judge, answer, status)
    calls = install_launch(monkeypatch, replies)
    row = harness.Runner(config, tmp_path, ready()).scenario(CASE, "claude")
    assert [(cli, mcp) for cli, mcp, _, _ in calls] == [("claude", True), ("grok", False), ("codex", False)]
    assert [j["cli"] for j in row["judges"]] == (["codex"] if judge == "grok" else ["grok"])
    assert row["judge"] is None
    assert row["success"] is False
    assert row["evaluation_status"] == evaluation
    assert [j["status"] for j in row["judge_executions"]] == (
        [status, "completed"] if judge == "grok" else ["completed", status]
    )
    if status == "completed":
        invalid = next(j for j in row["judge_executions"] if j["cli"] == judge)
        assert invalid["evaluation_error"] == "Invalid judge response"


def test_unavailable_second_judge_refuses_before_agent_start(config, tmp_path, monkeypatch):
    receipts = ready()
    receipts["codex"].update(verified=False, reason="Missing isolation receipt")
    calls = install_launch(monkeypatch, {})
    runner = harness.Runner(config, tmp_path, receipts)
    row = runner.scenario(CASE, "claude")
    assert (row["status"], row["success"], row["judges"]) == ("judge_unavailable", False, [])
    assert row["judge_executions"] == [{
        "cli": "codex", "status": "isolation_failed", "exit_code": None, "wall_time_ms": None,
        "usage_limit": None, "error": "Missing isolation receipt", "attempts": 0,
    }]
    assert runner.counts["claude"] == {"agent": 0, "judge": 0}
    assert calls == []


def test_second_judge_can_become_unavailable_after_first_opinion(config, tmp_path, monkeypatch):
    runner = harness.Runner(config, tmp_path, ready())

    def after(cli, mcp):
        if cli == "grok":
            runner.isolation["codex"].update(verified=False, reason="Isolation revoked")

    calls = install_launch(monkeypatch, {"grok": execution("grok", json.dumps(PASS))}, after=after)
    row = runner.scenario(CASE, "claude")
    assert [(cli, mcp) for cli, mcp, _, _ in calls] == [("claude", True), ("grok", False)]
    assert [j["cli"] for j in row["judges"]] == ["grok"]
    assert row["judge"] is None and row["success"] is False
    assert row["judge_executions"][1] == {
        "cli": "codex", "status": "isolation_failed", "exit_code": None, "wall_time_ms": None,
        "usage_limit": None, "error": "Isolation revoked", "attempts": 0,
    }


@pytest.mark.parametrize("judge", ["grok", "codex"])
def test_each_judge_usage_limit_stops_that_cli_and_preserves_other_evaluation(judge, config, tmp_path, monkeypatch):
    replies = {cli: execution(cli, json.dumps(PASS)) for cli in ("grok", "codex")}
    replies[judge] = execution(judge, "", "usage_limit", limit="weekly usage limit")
    calls = install_launch(monkeypatch, replies)
    runner = harness.Runner(config, tmp_path, ready())
    row = runner.scenario(CASE, "claude")
    assert row["success"] is False and row["evaluation_status"] == "judge_usage_limit"
    assert runner.stopped == {judge: "weekly usage limit"}
    assert [j["cli"] for j in row["judges"]] == (["codex"] if judge == "grok" else ["grok"])
    assert runner.scenario(CASE, "claude")["status"] == "judge_unavailable"
    assert len(calls) == 3
    assert runner.counts["claude"] == {"agent": 1, "judge": 0}


@pytest.mark.parametrize("judge", ["grok", "codex"])
def test_each_judge_quota_refuses_without_spending_an_agent_start(judge, config, tmp_path):
    config["max_runs_per_cli"] = 1
    runner = harness.Runner(config, tmp_path, ready())
    runner.counts[judge]["judge"] = 1
    row = runner.scenario(CASE, "claude")
    assert (row["status"], row["success"]) == ("judge_unavailable", False)
    assert [(j["cli"], j["status"], j["attempts"]) for j in row["judge_executions"]] == [(judge, "max_runs", 0)]
    assert runner.counts["claude"] == {"agent": 0, "judge": 0}


def test_panel_misuse_is_attributed_to_each_judge(config, tmp_path, monkeypatch):
    install_launch(monkeypatch, {
        "grok": execution("grok", "", "isolation_misuse", misuse=["use_tool"]),
        "codex": execution("codex", "", "isolation_misuse", misuse=["browser_navigate"]),
    })
    row = harness.Runner(config, tmp_path, ready()).scenario(CASE, "claude")
    assert row["success"] is False
    assert agent_harness.isolation_misuse_rows([row]) == [
        ["panel-case", "grok", "judge", ["use_tool"]],
        ["panel-case", "codex", "judge", ["browser_navigate"]],
    ]


def test_subscription_report_keeps_both_opinions_and_lists_pairs(config, tmp_path, monkeypatch):
    checked = []
    monkeypatch.setattr(jobs, "require_ready", lambda cfg, clis, output: checked.append(clis) or ready())
    install_launch(monkeypatch, {"grok": execution("grok", json.dumps(PASS)), "codex": execution("codex", json.dumps(PASS))})
    report = jobs.scenario_report(config, ["claude"], [CASE], tmp_path, day="2026-10-10")
    assert checked == [["claude", "grok", "codex"]]
    assert report["metadata"]["judge"] == {
        "mode": "panel", "routes": {
            "claude": ["grok", "codex"], "codex": ["grok", "claude"],
            "gemini": ["codex", "claude"], "grok": ["codex", "claude"],
        },
    }
    assert [j["cli"] for j in report["runs"][0]["judges"]] == ["grok", "codex"]
    assert report["runs"][0]["judge"]["strategy"] == "panel"
    assert report["overall"]["success_rate"] == 1
    text = agent_harness.markdown(report)
    assert "## Judges used\n\n| Agent arm | Judge CLIs |" in text
    assert "| claude | grok + codex |" in text
    assert "| codex | grok + claude |" in text
    assert "| grok | codex + claude |" in text
    assert "| claude | xai | grok-actual | 1 |" in text
    assert "| claude | openai | codex-actual | 1 |" in text


def test_tui_report_records_panel_metadata_and_pairs(config, tmp_path, monkeypatch):
    install_launch(monkeypatch, {"grok": execution("grok", json.dumps(PASS)), "codex": execution("codex", json.dumps(PASS))})
    runner = harness.Runner(config, tmp_path, ready())
    row = runner.scenario(CASE, "claude")
    report = harness.report_for([row], [CASE], ["claude"], config, ready(), runner.counts, {})
    assert report["metadata"]["judge"]["mode"] == "panel"
    assert report["metadata"]["judge"]["routes"]["claude"] == ["grok", "codex"]
    assert "| claude | grok + codex |" in harness.markdown(report)
    assert report["overall"]["success_rate"] == 1


def test_second_judge_quiet_hours_refusal_marks_single_row_report_partial(config, tmp_path, monkeypatch):
    config["_quiet_hours"] = True
    hour = [7]
    guard = harness.quiet_hours_guard
    monkeypatch.setattr(harness, "quiet_hours_guard", lambda enabled, force: guard(
        enabled, force, datetime(2026, 10, 10, hour[0]),
    ))
    monkeypatch.setattr(jobs, "require_ready", lambda *a: ready())

    def after(cli, mcp):
        if cli == "grok":
            hour[0] = 8

    install_launch(monkeypatch, {"grok": execution("grok", json.dumps(PASS))}, after=after)
    report = jobs.scenario_report(config, ["claude"], [CASE], tmp_path, day="2026-10-10")
    assert report["partial"] is True
    row = report["runs"][0]
    assert (row["status"], row["evaluation_status"], row["success"]) == ("completed", "judge_unavailable", False)
    assert [(j["cli"], j["status"], j["attempts"]) for j in row["judge_executions"]] == [
        ("grok", "completed", 1), ("codex", "quiet_hours", 0),
    ]
    assert report["metadata"]["cli_invocations"]["codex"] == {"agent": 0, "judge": 0}
    assert agent_harness.markdown(report).startswith("# Agent scenarios, 2026-10-10 (partial: quiet_hours)")


def test_required_receipts_include_the_second_judge(config, tmp_path, monkeypatch):
    config["_state_dir"] = str(tmp_path / ".tui-state")
    for cli in ("claude", "grok"):
        directory = homes.state_directory(cli, config)
        directory.mkdir(parents=True, exist_ok=True)
        isolation.receipt_file(directory).write_text(json.dumps({"certified_at": datetime.now(timezone.utc).isoformat()}))
    monkeypatch.setattr(jobs, "isolation_result", lambda cli, cfg: ready()[cli])
    monkeypatch.setattr(harness, "launch", lambda *a, **k: pytest.fail("CLI started without every receipt"))
    with pytest.raises(ValueError, match="codex: missing or stale doctor receipt"):
        jobs.scenario_report(config, ["claude"], [CASE], tmp_path, day="2026-10-10")


def test_default_and_overridden_pairs_key_resume_even_without_override_metadata(config, tmp_path, monkeypatch):
    monkeypatch.setattr(jobs, "require_ready", lambda *a: ready())
    install_launch(monkeypatch, {"grok": execution("grok", json.dumps(PASS)), "codex": execution("codex", json.dumps(PASS))})
    jobs.scenario_report(config, ["claude"], [CASE], tmp_path, day="2026-10-10")
    config["judges"]["claude"] = ["codex", "grok"]
    with pytest.raises(ValueError, match="judge pairs must match"):
        jobs.scenario_report(config, ["claude"], [CASE], tmp_path, day="2026-10-10", resume=True)
    assert "_judge_overrides" not in config


def test_resume_totals_count_both_judges_and_attempts_but_not_refusals():
    total = jobs._cli_invocation_totals(
        {"claude": {"agent": 0, "judge": 0}, "grok": {"agent": 0, "judge": 0}, "codex": {"agent": 0, "judge": 0}},
        [{"cli": "claude", "attempts": 1, "judge_executions": [
            {"cli": "grok", "attempts": 2}, {"cli": "codex", "attempts": 1},
        ]}, {"cli": "claude", "attempts": 1, "judge_executions": [{"cli": "grok", "attempts": 0}]}],
    )
    assert total == {
        "claude": {"agent": 2, "judge": 0}, "grok": {"agent": 0, "judge": 2}, "codex": {"agent": 0, "judge": 1},
    }


def test_resume_does_not_count_agent_or_judge_starts_for_preflight_refusals(config, tmp_path):
    receipts = ready()
    receipts["codex"].update(verified=False, reason="Receipt revoked")
    runner = harness.Runner(config, tmp_path, receipts)
    row = runner.scenario(CASE, "claude") | {"cli": "claude"}
    assert jobs._cli_invocation_totals(runner.counts, [row]) == {
        "claude": {"agent": 0, "judge": 0}, "codex": {"agent": 0, "judge": 0},
        "gemini": {"agent": 0, "judge": 0}, "grok": {"agent": 0, "judge": 0},
    }
    assert (row["status"], row["success"]) == ("judge_unavailable", False)


def test_network_tag_checks_second_judge_execution():
    probe = {
        "checks": [
            {"url": "https://api.modelspec.dev/v1/health", "reachable": True},
            {"url": "https://www.cloudflare.com/cdn-cgi/trace", "reachable": True},
        ],
    }
    tag = jobs.network_tag({
        "status": "completed", "judge_executions": [
            {"cli": "grok", "status": "completed", "error": None},
            {"cli": "codex", "status": "timeout", "error": "read ECONNRESET"},
        ],
    }, probe=lambda: probe)
    assert tag == {
        "class": "network_suspect", "failed_stage": "judge", "error_signature": True,
        "api_reachable": True, "probe": {
            "checks": [
                {"url": "https://api.modelspec.dev/v1/health", "reachable": True},
                {"url": "https://www.cloudflare.com/cdn-cgi/trace", "reachable": True},
            ],
        },
    }
