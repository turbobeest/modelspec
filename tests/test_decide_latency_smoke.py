"""The warning-only deploy report measures each vocabulary template separately."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "decide_latency_smoke", ROOT / ".github/scripts/check_decide_latency.py"
)
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


def test_every_template_excludes_initial_and_all_warmups(monkeypatch):
    templates = [
        {
            "id": f"template-{i}",
            "spec": {"spec_version": 1, "task_tokens": {"input": 1000 + i, "output": 100}},
        }
        for i in range(8)
    ]
    calls = []

    def curl(command, **kwargs):
        response = Path(command[command.index("-o") + 1])
        if "-d" not in command:
            response.write_text(json.dumps({"templates": templates}))
            return SimpleNamespace(returncode=0, stdout="200 0.01")
        payload = json.loads(command[command.index("-d") + 1])
        calls.append(payload)
        response.write_text('{"decision_id":"dec_test","snapshot":"snap_test"}')
        # Initial: 9 seconds. Two warmups: 8 and 7. Samples: 0.1, 0.2, 0.3.
        elapsed = [9, 8, 7, 0.1, 0.2, 0.3][(len(calls) - 1) % 6]
        return SimpleNamespace(returncode=0, stdout=f"200 {elapsed}")

    monkeypatch.setattr(smoke.subprocess, "run", curl)
    rows, reason = smoke.measure("api.example.test", count=3, warmups=2)
    summary, warnings = smoke.report(rows, reason, 2, 3, "full")
    assert reason is None and warnings == []
    assert len(calls) == 48
    assert rows[0]["initial_ms"] == 9000
    assert all(row["warm_ms"] == [100, 200, 300] for row in rows)
    for index, template in enumerate(templates):
        assert calls[index * 6]["task_tokens"] == template["spec"]["task_tokens"]
        assert f"| template-{index} | 9000.0 | 200.0 | 300.0 | 3 |" in summary


def test_one_slow_template_warns_without_aggregation():
    rows = [
        {"id": "fast", "initial_ms": 3000, "warm_ms": [100] * 20, "reason": None},
        {"id": "slow", "initial_ms": 4000, "warm_ms": [600] * 20, "reason": None},
    ]
    summary, warnings = smoke.report(rows, None, 5, 20, "full")
    assert "| fast | 3000.0 | 100.0 | 100.0 | 20 |" in summary
    assert "| slow | 4000.0 | 600.0 | 600.0 | 20 |" in summary
    assert warnings == ["Decision template slow warm p95 600.0 ms exceeds 500 ms"]


def test_access_refusal_records_a_skip_and_stops_sampling(monkeypatch):
    calls = []

    def curl(command, **kwargs):
        calls.append(command)
        response = Path(command[command.index("-o") + 1])
        response.write_text(
            json.dumps(
                {
                    "templates": [
                        {"id": f"template-{i}", "spec": {"spec_version": 1}} for i in range(8)
                    ]
                }
            )
        )
        return SimpleNamespace(returncode=0, stdout="200 .01" if len(calls) == 1 else "401 .01")

    monkeypatch.setattr(smoke.subprocess, "run", curl)
    rows, reason = smoke.measure("api.example.test")
    summary, warnings = smoke.report(rows, reason, 5, 20, "full")
    assert len(calls) == 2
    assert rows[0]["warm_ms"] == []
    assert "Skipped: anonymous callers require a key or are rate limited (HTTP 401)" in summary
    assert warnings


def test_unavailable_template_is_reported_without_a_decide_request(monkeypatch):
    templates = [
        {"id": f"template-{i}", "available": i != 2, "spec": {"spec_version": 1}}
        for i in range(8)
    ]
    calls = []

    def request(url, response_path, spec=None):
        if spec is None:
            return {"templates": templates}, 10, None
        calls.append(spec)
        return {"decision_id": "dec_test", "snapshot": "snap_test"}, 100, None

    monkeypatch.setattr(smoke, "request", request)
    rows, reason = smoke.measure("api.example.test", count=1, warmups=1)
    summary, warnings = smoke.report(rows, reason, 1, 1, "full")
    assert len(calls) == 21
    assert rows[2]["warm_ms"] == []
    assert "Skipped 1 unavailable vocabulary templates: template-2." in summary
    assert "Skipped: unavailable in vocabulary (available: false)" in summary
    assert warnings == []


def test_likely_new_isolate_share_uses_only_warm_samples():
    rows = [
        {"id": "a", "initial_ms": 5000, "warm_ms": [100, 1000, 1001], "reason": None},
        {"id": "b", "initial_ms": 5000, "warm_ms": [2000], "reason": None},
        {"id": "c", "initial_ms": None, "warm_ms": [],
         "reason": "unavailable in vocabulary (available: false)"},
    ]
    summary, _ = smoke.report(rows, None, 5, 20, "full")
    assert "Likely new isolate: 2/4 warm samples (50.0%) exceeded 1 s." in summary
