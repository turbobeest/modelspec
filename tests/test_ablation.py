"""The ablation command uses scripted fixtures, never subscription or vendor calls."""

from __future__ import annotations

import json
import os
import socket
from datetime import date

import pytest

from qa import ablation, tui_harness
from qa import run_with_modelspec_key as launcher
from qa import subscription_jobs as jobs
from qa.ablation_proxy import Variants, metadata
from qa.docker.entrypoint import VENDOR_ENV


@pytest.fixture(autouse=True)
def offline_environment(monkeypatch):
    for name in tuple(os.environ):
        if VENDOR_ENV.search(name):
            monkeypatch.delenv(name)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(socket.socket, "connect", lambda *a, **k: pytest.fail("Network connection"))
    monkeypatch.setattr(socket.socket, "bind", lambda *a, **k: pytest.fail("Listening socket"))
    monkeypatch.setattr(tui_harness, "launch", lambda *a, **k: pytest.fail("Live CLI"))
    monkeypatch.setattr(tui_harness, "verify_isolation", lambda *a, **k: pytest.fail("Live doctor"))
    monkeypatch.setattr(jobs, "publish", lambda *a, **k: pytest.fail("Publication"))
    monkeypatch.setattr(jobs, "require_ready", lambda *a, **k: pytest.fail("Live readiness"))


def test_scenario_sets_are_exact_and_disjoint(monkeypatch):
    assert ablation.TUNING == (
        "budget-approved",
        "hardware-spark",
        "prompt-code",
        "prompt-maths",
        "prompt-policy",
        "recall-q01",
        "recall-q03",
        "recall-q04",
        "recall-q07",
        "recall-q09",
    )
    assert ablation.HOLDOUT == ("recall-q02", "recall-q05", "recall-q08", "recall-q10")
    assert set(ablation.TUNING).isdisjoint(ablation.HOLDOUT)
    with pytest.raises(ValueError, match="HOLDOUT"):
        ablation.select(["v1"], "holdout")
    with pytest.raises(ValueError, match="belong"):
        ablation.select(["baseline"], "tuning", ["recall-q02"])
    monkeypatch.setattr(ablation, "supports_plugin", lambda module: True)
    assert ablation.select(None, "holdout") == (["baseline", "combined"], list(ablation.HOLDOUT))


@pytest.mark.parametrize("arm", ["v2", "combined"])
def test_plugin_arms_refuse_before_any_work_if_flag_missing(tmp_path, monkeypatch, capsys, arm):
    monkeypatch.setattr(ablation, "supports_plugin", lambda module: False)
    output = tmp_path / "report"
    assert (
        ablation.main(
            [
                "--dry-run",
                "--arms",
                arm,
                "--out",
                str(output),
                "--state-dir",
                str(tmp_path / "state"),
            ]
        )
        == 2
    )
    assert "--claude-plugin modelspec" in capsys.readouterr().err
    assert not output.exists()


def test_plugin_flag_is_passed_only_for_v2_and_combined(tmp_path):
    for arm in ablation.ARMS:
        info = metadata(ablation.ARMS[arm], "http://host.docker.internal:8765/mcp")
        args = ablation.harness_arguments(
            "run", arm, tmp_path / arm, tmp_path / "state", info, ["budget-approved"], dry_run=True
        )
        assert ("--claude-plugin" in args) == (arm in {"v2", "combined"})
        if "--claude-plugin" in args:
            assert args[args.index("--claude-plugin") + 1] == "modelspec"
        for judge in ("grok", "codex"):
            judge_doctor = ablation.harness_arguments(
                "doctor", arm, tmp_path / arm, tmp_path / "state", info,
                ["budget-approved"], cli=judge,
            )
            assert "--claude-plugin" not in judge_doctor
            assert "--judge" not in judge_doctor
        assert "--judge" not in args
        assert args[args.index("--state-dir") + 1] == str(tmp_path / "state" / arm)


@pytest.mark.parametrize("codex_exit_code,expected_exit_code", [(0, 0), (2, 2)])
def test_doctor_checks_agent_and_both_panel_judges_in_private_arm_state(
    tmp_path, monkeypatch, capsys, codex_exit_code, expected_exit_code,
):
    invocations = []

    def fixture_proxy(variants, root, *, port, upstream):
        info = metadata(variants, f"http://host.docker.internal:{port}/mcp", upstream)
        return ablation.dry_proxy(variants, root, info)

    def doctor(arguments):
        invocations.append(arguments)
        cli = arguments[arguments.index("--cli") + 1]
        return codex_exit_code if cli == "codex" else 0

    monkeypatch.setattr(ablation, "running_proxy", fixture_proxy)
    monkeypatch.setattr(tui_harness, "main", doctor)
    state = tmp_path / "private-state"
    assert ablation.main([
        "doctor", "--arms", "v1", "--out", str(tmp_path / "out"),
        "--state-dir", str(state),
    ]) == expected_exit_code
    assert [args[args.index("--cli") + 1] for args in invocations] == [
        "claude", "grok", "codex",
    ]
    for args in invocations:
        assert args[0] == "doctor"
        assert args[args.index("--state-dir") + 1] == str(state.resolve() / "v1")
        assert "--judge" not in args
        assert "--claude-plugin" not in args
    if codex_exit_code:
        assert "v1: codex doctor failed" in capsys.readouterr().err
    else:
        capsys.readouterr()


def test_dry_run_replays_whole_tuning_path_and_proves_proxy_rewrites(
    tmp_path, monkeypatch, capsys,
):
    invocations = []
    replay_launch = ablation.FixtureReplay.launch

    def capture_launch(self, cli, config, workspace, prompt, *, mcp_enabled, **kwargs):
        invocations.append((cli, mcp_enabled, prompt))
        return replay_launch(
            self, cli, config, workspace, prompt, mcp_enabled=mcp_enabled, **kwargs,
        )

    monkeypatch.setattr(ablation.FixtureReplay, "launch", capture_launch)
    output, state = tmp_path / "report", tmp_path / "state"
    assert (
        ablation.main(
            [
                "--dry-run",
                "--arms",
                "baseline",
                "v1",
                "v3",
                "v4",
                "--out",
                str(output),
                "--state-dir",
                str(state),
            ]
        )
        == 0
    )
    report = json.loads((output / "ablation.json").read_text())
    assert report["mode"] == "dry-run"
    assert len(report["runs"]) == 40
    assert report["arms"] == {
        "baseline": {"passed": 0, "total": 10, "pass_rate": 0.0},
        "v1": {"passed": 0, "total": 10, "pass_rate": 0.0},
        "v3": {"passed": 0, "total": 10, "pass_rate": 0.0},
        "v4": {"passed": 0, "total": 10, "pass_rate": 0.0},
    }
    assert [(cli, mcp_enabled) for cli, mcp_enabled, _prompt in invocations] == [
        ("claude", True), ("grok", False), ("codex", False),
    ] * 40
    for index in range(0, 120, 3):
        assert invocations[index + 1][2] == invocations[index + 2][2]
    assert "Scripted fixture" in report["evidence_note"]
    assert report["proxy"]["baseline"]["counters"].get("rewritten_calls", 0) == 0
    assert report["proxy"]["v1"]["counters"]["instructions"] == 10
    assert report["proxy"]["v1"]["counters"]["body.next_move"] > 0
    assert report["proxy"]["v1"]["counters"]["complete_fetch"] == 7
    assert report["proxy"]["v3"]["counters"]["tools.decide.description"] == 10
    assert report["proxy"]["v4"]["counters"]["content.user_summary"] == 7
    for arm, values in report["proxy"].items():
        assert not values["counters"].get("bounded_fallback")
        assert not values["counters"].get("proxy_error")
        assert values["ablation"]["variants"] == ablation.ARMS[arm].names()
        rows = [row for row in report["runs"] if row["arm"] == arm]
        assert all(len(row["rationale"]) <= 300 for row in rows)
        assert all(row["ablation"] == values["ablation"] for row in rows)
        assert all(row["proxy_rewrites"]["responses"] > 0 for row in rows)
        for row in rows:
            assert [(judge["cli"], judge["passed"]) for judge in row["judges"]] == [
                ("grok", False), ("codex", False),
            ]
            assert [execution["cli"] for execution in row["judge_executions"]] == [
                "grok", "codex",
            ]
            assert all(execution["status"] == "completed" for execution in row["judge_executions"])
            assert row["judge"]["strategy"] == "panel"
            assert row["judge"]["agreed"] is True
            assert row["judge"]["passed"] is False
            assert row["judge_passed"] is False
            assert row["passed"] is False
            assert len(row["judge"]["rationale"]) <= 300
            assert all(len(judge["rationale"]) <= 300 for judge in row["judges"])
        harness_report = json.loads(
            (output / arm / "report" / f"{date.today()}-tui-agent-scenarios.json").read_text()
        )
        assert harness_report["metadata"]["fixture_replay"]
        assert harness_report["metadata"]["judge"] == {
            "mode": "panel",
            "routes": {
                "claude": ["grok", "codex"],
                "codex": ["grok", "claude"],
                "gemini": ["codex", "claude"],
                "grok": ["codex", "claude"],
            },
        }
        assert report["metadata"]["judge"][arm] == harness_report["metadata"]["judge"]
        assert harness_report["cli_invocations"] == {
            "claude": {"agent": 10, "judge": 0},
            "grok": {"agent": 0, "judge": 10},
            "codex": {"agent": 0, "judge": 10},
            "gemini": {"agent": 0, "judge": 0},
        }
        assert set(harness_report["isolation"]) == {"claude", "grok", "codex"}
        assert all(not value["verified"] for value in harness_report["isolation"].values())
    assert not state.exists()
    table = (output / "ablation.md").read_text()
    assert "Judge rationale | Proxy rewrites" in table
    assert "Judge verdicts | Aggregate judge pass" in table
    assert table.count("grok: fail; codex: fail") == 40
    assert "unanimous judge approval" in table
    assert "Scripted fixture" in table
    capsys.readouterr()


@pytest.mark.parametrize(
    "grok_passed,codex_passed,codex_models,agreed,passed,pass_rate",
    [
        (True, True, [], True, True, 1.0),
        (True, False, [], False, False, 0.0),
        (False, True, [], False, False, 0.0),
        (True, True, ["fixture/model"], False, False, 0.0),
    ],
)
def test_panel_requires_unanimous_verdicts_and_uses_aggregate_for_pass_rate(
    tmp_path, monkeypatch, capsys, grok_passed, codex_passed, codex_models,
    agreed, passed, pass_rate,
):
    replay_launch = ablation.FixtureReplay.launch

    def scripted_launch(self, cli, config, workspace, prompt, *, mcp_enabled, **kwargs):
        execution = replay_launch(
            self, cli, config, workspace, prompt, mcp_enabled=mcp_enabled, **kwargs,
        )
        if not mcp_enabled:
            models = codex_models if cli == "codex" else []
            execution.transcript.final_answer = json.dumps({
                "passed": codex_passed if cli == "codex" else grok_passed,
                "rationale": f"Scripted {cli} verdict.",
                "top_models": models,
                "answer_kind": "single" if models else "abstain",
                "missing_capabilities": [],
            })
        return execution

    monkeypatch.setattr(ablation.FixtureReplay, "launch", scripted_launch)
    output = tmp_path / "out"
    assert ablation.main([
        "--dry-run", "--arms", "baseline", "--scenario", "budget-approved",
        "--out", str(output), "--state-dir", str(tmp_path / "state"),
    ]) == 0
    report = json.loads((output / "ablation.json").read_text())
    row = report["runs"][0]
    assert [(judge["cli"], judge["passed"]) for judge in row["judges"]] == [
        ("grok", grok_passed), ("codex", codex_passed),
    ]
    assert row["judge"]["strategy"] == "panel"
    assert row["judge"]["agreed"] is agreed
    assert row["judge"]["passed"] is passed
    assert row["judge_passed"] is passed
    assert row["variant_applied"] is True
    assert row["passed"] is passed
    assert report["arms"]["baseline"] == {
        "passed": int(passed), "total": 1, "pass_rate": pass_rate,
    }
    verdicts = (
        f"grok: {'pass' if grok_passed else 'fail'}; "
        f"codex: {'pass' if codex_passed else 'fail'}"
    )
    assert f"| {verdicts} | {passed} |" in (output / "ablation.md").read_text()
    capsys.readouterr()


def test_codex_readiness_is_required_before_the_fixture_agent_runs(tmp_path, monkeypatch, capsys):
    replay_runner = ablation.FixtureReplay.runner

    def unavailable_codex(self, config, output, scenarios):
        runner = replay_runner(self, config, output, scenarios)
        runner.isolation["codex"].update(verified=False, reason="Scripted Codex doctor failure")
        return runner

    monkeypatch.setattr(ablation.FixtureReplay, "runner", unavailable_codex)
    output = tmp_path / "out"
    assert ablation.main([
        "--dry-run", "--arms", "baseline", "--scenario", "budget-approved",
        "--out", str(output), "--state-dir", str(tmp_path / "state"),
    ]) == 0
    report = json.loads((output / "ablation.json").read_text())
    row = report["runs"][0]
    assert row["status"] == "judge_unavailable"
    assert row["judges"] == []
    assert [(execution["cli"], execution["status"]) for execution in row["judge_executions"]] == [
        ("codex", "isolation_failed"),
    ]
    assert row["judge_passed"] is False
    assert row["passed"] is False
    assert report["arms"]["baseline"] == {"passed": 0, "total": 1, "pass_rate": 0.0}
    harness_report = json.loads(
        (output / "baseline/report" / f"{date.today()}-tui-agent-scenarios.json").read_text()
    )
    assert harness_report["cli_invocations"] == {
        "claude": {"agent": 0, "judge": 0},
        "grok": {"agent": 0, "judge": 0},
        "codex": {"agent": 0, "judge": 0},
        "gemini": {"agent": 0, "judge": 0},
    }
    capsys.readouterr()


def test_holdout_dry_run_only_uses_held_out_recall(tmp_path, capsys):
    assert (
        ablation.main(
            [
                "--dry-run",
                "--arms",
                "baseline",
                "--set",
                "holdout",
                "--out",
                str(tmp_path / "out"),
                "--state-dir",
                str(tmp_path / "state"),
            ]
        )
        == 0
    )
    report = json.loads((tmp_path / "out/ablation.json").read_text())
    assert [row["scenario"] for row in report["runs"]] == list(ablation.HOLDOUT)
    assert report["scenario_set"] == "holdout"
    capsys.readouterr()


def test_plain_dry_run_harness_and_scenarios_job_record_proxy_metadata(tmp_path, capsys):
    url = "http://host.docker.internal:8765/mcp"
    info = metadata(Variants(annotations=True), url)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(info))
    common = [
        "--dry-run",
        "--cli",
        "claude",
        "--scenario",
        "budget-approved",
        "--ablation-proxy",
        url,
        "--ablation-metadata",
        str(manifest),
    ]
    assert (
        tui_harness.main(
            [*common, "--out", str(tmp_path / "tui"), "--state-dir", str(tmp_path / "state")]
        )
        == 0
    )
    tui = json.loads((tmp_path / "tui" / f"{date.today()}-tui-agent-scenarios.json").read_text())
    assert tui["metadata"]["ablation"] == info
    assert jobs.main(["scenarios", *common, "--state-dir", str(tmp_path / "jobs")]) == 0
    job = json.loads(
        next(
            (tmp_path / "jobs/dry-run/scenarios/reports/agent-scenarios").glob("*.json")
        ).read_text()
    )
    assert job["metadata"]["ablation"] == info
    assert job["runs"][0]["ablation"] == info
    capsys.readouterr()


def test_scenarios_proxy_flag_refuses_default_state_before_mutation(tmp_path, capsys):
    assert (
        jobs.main(
            ["scenarios", "--dry-run", "--ablation-proxy", "http://host.docker.internal:8765/mcp"]
        )
        == 2
    )
    assert "own private --state-dir" in capsys.readouterr().out


def test_checkpoint_separates_variants_on_the_same_proxy_url(tmp_path):
    config = jobs.configuration(tmp_path, max_runs=32)
    scenario = {"id": "budget-approved"}
    kwargs = {"day": "2026-10-10", "engine_sha": "fixture-sha", "config": config}
    ordinary = jobs._scenario_checkpoint(tmp_path, ["claude"], [scenario], **kwargs)
    config["ablation"] = metadata(Variants(), "http://host.docker.internal:8765/mcp")
    baseline = jobs._scenario_checkpoint(tmp_path, ["claude"], [scenario], **kwargs)
    config["ablation"]["variants"] = ["v1"]
    variant = jobs._scenario_checkpoint(tmp_path, ["claude"], [scenario], **kwargs)
    assert len({ordinary, baseline, variant}) == 3


@pytest.mark.parametrize(
    "arguments,module",
    [
        (["scenarios", "--cli", "claude"], "qa.subscription_jobs"),
        (["ablation", "--dry-run", "--arms", "baseline"], "qa.ablation"),
    ],
)
def test_clean_launcher_routes_ablation_and_keeps_default_job_argv(arguments, module, monkeypatch):
    monkeypatch.setenv("MODELSPEC_API_KEY", "live-fixture-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "vendor-key")
    captured = []
    monkeypatch.setattr(os, "execve", lambda *args: captured.append(args))
    launcher.main(arguments)
    executable, argv, env = captured[0]
    suffix = arguments[1:] if module == "qa.ablation" else arguments
    assert argv == [executable, "-m", module, *suffix]
    assert "live-fixture-secret" not in argv
    assert "OPENAI_API_KEY" not in env
    assert env["MODELSPEC_API_KEY"] == "live-fixture-secret"


@pytest.mark.parametrize("failure", ["budget_passthrough", "bounded_fallback", "candidates_truncated"])
def test_pass_requires_variant_exposure_and_preserves_judge_rationale(failure):
    row = {
        "scenario": "budget-approved",
        "success": True,
        "judge": {"rationale": "r" * 400},
        "proxy_rewrites": {
            "responses": 4,
            "instructions": 1,
            "tools.decide.description": 1,
            failure: 1,
        },
    }
    report = ablation.combined_report(
        {"v1": {"runs": [row], "metadata": {}}}, {}, "tuning", ["budget-approved"], dry_run=True
    )
    assert report["runs"][0]["judge_passed"] is True
    assert report["runs"][0]["passed"] is False
    assert report["runs"][0]["rationale"] == "r" * 300
    assert report["arms"]["v1"]["pass_rate"] == 0


@pytest.mark.parametrize("symlink", [False, True])
def test_incomplete_markdown_report_uses_private_permissions_and_refuses_symlinks(
    tmp_path, monkeypatch, capsys, symlink,
):
    output = tmp_path / "out"
    target = tmp_path / "untouched.md"
    target.write_text("Keep this text.\n")
    run = tui_harness.main

    def fail_after_fixture_run(*args, **kwargs):
        assert run(*args, **kwargs) == 0
        if symlink:
            (output / "ablation.md").symlink_to(target)
        return 2

    monkeypatch.setattr(tui_harness, "main", fail_after_fixture_run)
    arguments = ["--dry-run", "--arms", "baseline", "--scenario", "budget-approved",
                 "--out", str(output), "--state-dir", str(tmp_path / "state")]
    if symlink:
        with pytest.raises(ValueError, match="Ablation table must not be a symlink"):
            ablation.main(arguments)
        assert target.read_text() == "Keep this text.\n"
    else:
        assert ablation.main(arguments) == 2
        report = json.loads((output / "ablation.json").read_text())
        assert report["incomplete"] is True
        assert (output / "ablation.md").read_text() == ablation.table(report)
        assert (output / "ablation.md").stat().st_mode & 0o777 == 0o600
    capsys.readouterr()


def test_incomplete_report_keeps_all_requested_arm_scenario_cells():
    report = ablation.combined_report(
        {"baseline": {"runs": [], "metadata": {}}},
        {},
        "tuning",
        ["budget-approved"],
        dry_run=True,
        expected_arms=["baseline", "v1"],
    )
    assert [(row["arm"], row["status"]) for row in report["runs"]] == [
        ("baseline", "not_run"),
        ("v1", "not_run"),
    ]
    assert report["arms"]["v1"] == {"passed": 0, "total": 1, "pass_rate": 0}


def test_docstring_contains_exact_launcher_and_private_doctor_command():
    assert "python -m qa.run_with_modelspec_key" in ablation.__doc__
    assert "python -m qa.ablation doctor" in ablation.__doc__
    assert "--state-dir /private/tmp/claude-501/m339/ablation-state" in ablation.__doc__
    assert "receipts for Claude, Grok and Codex" in ablation.__doc__
    assert "Both judges must agree and pass" in ablation.__doc__
