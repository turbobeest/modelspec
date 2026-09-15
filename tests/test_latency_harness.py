"""MODEL-60 latency harness: parsers, task set, sandbox guards. No CLIs, no network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.latency import runner, tasks
from scripts.latency.parsers import parse_claude, parse_unverified

FIXTURE = Path(__file__).parent / "fixtures" / "latency" / "claude_stream.jsonl"


def _events():
    rows = [json.loads(line) for line in FIXTURE.read_text().splitlines()]
    return [(r["t"], r["event"]) for r in rows]


def test_claude_split_model_and_tool_time():
    t = parse_claude(_events(), end=18.946)
    assert t.startup_s == pytest.approx(0.6583)
    # tool intervals: tool_use receipt -> tool_result receipt
    assert t.tool_s == pytest.approx((3.2612 - 3.1288) + (10.2579 - 10.244) + (10.6801 - 10.5761) + (13.1352 - 13.0424))
    assert t.startup_s + t.model_s + t.tool_s + t.shutdown_s == pytest.approx(18.946)
    assert (t.turns, t.tool_calls) == (5, 4)
    assert t.tokens_in == 83846 and t.tokens_out == 1141
    assert t.cli_reported["duration_api_ms"] == 18393
    assert t.final_ok is True and t.notes == []


def test_claude_parallel_tool_calls_count_one_tool_interval():
    ev = [
        (1.0, {"type": "system"}),
        (2.0, {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "a"}]}}),
        (2.1, {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "b"}]}}),
        (3.0, {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "a"}]}}),
        (4.0, {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "b"}]}}),
        (5.0, {"type": "result", "usage": {}}),
    ]
    t = parse_claude(ev, end=5.5)
    assert t.tool_s == pytest.approx(2.0)
    assert t.model_s == pytest.approx(2.0)
    assert (t.turns, t.tool_calls) == (2, 2)


def test_claude_truncated_stream_is_flagged():
    t = parse_claude(_events()[:4], end=20.0)
    assert t.notes and "without a result" in t.notes[0]


def test_unverified_parser_leaves_split_null():
    t = parse_unverified([], end=8.3).as_dict()
    assert t["model_s"] is None and t["tool_s"] is None and t["notes"]


@pytest.mark.parametrize("text", [
    "API error (status 402 Payment Required): usage balance exhausted",
    "429 Too Many Requests",
    "You've hit your usage limit",
])
def test_limit_errors_detected(text):
    assert runner.classify_limit(text)


def test_ordinary_error_is_not_a_limit():
    assert runner.classify_limit("SyntaxError: invalid syntax") is None


def test_sandbox_env_drops_secrets(monkeypatch):
    for k in ("GH_TOKEN", "OPENAI_API_KEY", "SSH_AUTH_SOCK", "ANTHROPIC_BASE_URL", "OP_SESSION_x"):
        monkeypatch.setenv(k, "x")
    env = runner.sandbox_env()
    assert set(env) <= set(runner.ENV_ALLOW)


def test_claude_command_is_confined(tmp_path):
    cmd = runner.build_command(runner.SETUPS["claude-code/opus-5"], "p", tmp_path)
    assert "--strict-mcp-config" in cmd and "--no-session-persistence" in cmd
    settings = json.loads(cmd[cmd.index("--settings") + 1])
    assert settings["sandbox"]["enabled"] and not settings["sandbox"]["allowUnsandboxedCommands"]


def test_blocked_setups_have_no_adapter(tmp_path):
    with pytest.raises(NotImplementedError):
        runner.build_command(runner.SETUPS["codex/gpt-5.6"], "p", tmp_path)


def test_opencode_env_is_run_scoped(tmp_path):
    work = tmp_path / "run"
    env = runner.harness_env(runner.SETUPS["opencode/gemma4:26b"], work)
    assert env["HOME"].startswith(str(tmp_path)) and env["XDG_CONFIG_HOME"].startswith(str(tmp_path))
    cfg = json.loads(env["OPENCODE_CONFIG_CONTENT"])
    assert cfg["provider"]["spark-ollama"]["options"]["baseURL"] == runner.OLLAMA + "/v1"
    assert cfg["permission"]["external_directory"] == "deny"


def test_opencode_profile_denies_users_reads(tmp_path):
    prof = runner.opencode_profile(tmp_path / "run", Path("/Users/x/.opencode/bin/opencode"))
    assert '(deny file-read* (subpath "/Users"))' in prof
    assert f'(allow file-write* (subpath "{tmp_path}")' in prof


def test_runner_refuses_sandbox_in_home(tmp_path):
    with pytest.raises(SystemExit):
        runner.main(["--checkout", str(tmp_path), "--sandbox-root", str(Path.home() / "x")])


def _fake_checkout(root: Path, n: int = 21) -> Path:
    for i in range(n):
        d = root / tasks.PRACTICE / f"ex-{i:02d}"
        (d / ".docs").mkdir(parents=True)
        (d / ".meta").mkdir()
        (d / f"ex_{i:02d}.py").write_text("")
        (d / f"ex_{i:02d}_test.py").write_text("")
        (d / ".docs" / "instructions.md").write_text(f"do {i}")
        (d / ".meta" / "example.py").write_text("solution")
    return root


def test_task_selection_and_hash_are_deterministic(tmp_path):
    ts = tasks.select_tasks(_fake_checkout(tmp_path))
    assert len(ts) == 20 and ts[0].task_id == "ex-00" and ts[-1].task_id == "ex-19"
    h = tasks.task_set_hash(ts)
    assert h == tasks.task_set_hash(list(reversed(ts)))
    (ts[3].src / ".docs" / "instructions.md").write_text("changed")
    assert tasks.task_set_hash(ts) != h


def test_workdir_hides_reference_solution(tmp_path):
    task = tasks.select_tasks(_fake_checkout(tmp_path / "c"))[0]
    work = tmp_path / "run"
    tasks.prepare_workdir(task, work)
    assert not (work / ".meta").exists()
    assert (work / task.solution).exists() and (work / task.tests).exists()
    assert "ex_00.py" in tasks.build_prompt(task)


def test_opencode_split_uses_cli_tool_times():
    from scripts.latency.parsers import parse_opencode

    rows = [json.loads(line) for line in (FIXTURE.parent / "opencode_stream.jsonl").read_text().splitlines()]
    t = parse_opencode([(r["t"], r["event"]) for r in rows], end=156.057)
    assert t.startup_s == pytest.approx(37.4332)
    assert t.tool_s == pytest.approx((10 + 4 + 40) / 1000)
    steps_ms = (42300 - 37000) + (150900 - 44200) + (154650 - 154600) + (155580 - 155400)
    assert t.model_s == pytest.approx((steps_ms - 54) / 1000)
    assert (t.turns, t.tool_calls) == (4, 3)
    assert t.tokens_in == 7719 + 8043 + 10035 + 10070 and t.tokens_out == 382 + 6918 + 22 + 13
    assert t.final_ok is True and t.notes == []


def test_opencode_empty_stream_has_null_split():
    from scripts.latency.parsers import parse_opencode

    t = parse_opencode([], end=3.0)
    assert t.model_s is None and t.tool_s is None and t.startup_s == 3.0
