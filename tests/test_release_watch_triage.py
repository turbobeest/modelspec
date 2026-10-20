"""Offline triage preserves uncertain discoveries and never changes issues."""

from __future__ import annotations

import importlib
import json
import os
import site
import socket
import subprocess
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _signal(name: str = "acme-new-2", **changes: object) -> dict:
    result = {
        "model_name": name,
        "provider": "acme",
        "first_seen_url": "https://models.acme.example/models",
        "timestamp": "2026-10-19T00:00:00Z",
        "confidence": 0.9,
        "signal_id": "watch:acme:discovery",
    }
    result.update(changes)
    return result


def _issue(number: int, name: str = "acme-new-2", **changes: object) -> dict:
    result = {
        "number": number,
        "title": f"release discovery: {name}",
        "url": f"https://github.com/example/models/issues/{number}",
        "createdAt": "2026-10-19T00:00:00Z",
        "body": "Discovery trigger.\n\n```json\n" + json.dumps(_signal(name)) + "\n```\n",
    }
    result.update(changes)
    return result


def _catalogue(root: Path) -> Path:
    card = root / "models" / "acme" / "acme-one-1.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "---\nmodel_id: acme/acme-one-1\ndisplay_name: Acme One 1\nprovider: acme\n"
        "provider_display: Acme\nversion: acme-one-1\n---\n"
        "PRIVATE-CARD-CONTENT-MUST-NOT-LEAK\n",
        encoding="utf-8",
    )
    return root


def _run(tmp_path: Path, issues: list, *extra: str) -> tuple[dict, str]:
    triage = importlib.import_module("scripts.triage_release_discoveries")
    source = tmp_path / "issues.json"
    report = tmp_path / "report.json"
    summary = tmp_path / "summary.md"
    source.write_text(json.dumps(issues), encoding="utf-8")
    original = source.read_bytes()
    assert triage.main([
        "--issues", str(source), "--report", str(report), "--summary", str(summary), *extra,
    ]) == 0
    assert source.read_bytes() == original
    return json.loads(report.read_text()), summary.read_text()


def test_triage_classifies_duplicates_carded_releases_real_and_noise(tmp_path):
    catalogue = _catalogue(tmp_path / "private")
    report, summary = _run(tmp_path, [
        _issue(12, "Acme New 2"),
        _issue(40, "acme-one-1"),
        _issue(31, "acme-sdk-2"),
        _issue(11, createdAt="2026-10-18T00:00:00Z"),
        _issue(50, "acme-one-2"),
    ], "--catalogue-root", str(catalogue))

    assert report["dry_run"] is True
    assert report["catalogue_checked"] is True
    assert report["counts"] == {"duplicate": 1, "superseded": 1, "real": 2, "noise": 1}
    rows = {row["number"]: row for row in report["issues"]}
    assert rows[12]["classification"] == "duplicate"
    assert rows[12]["duplicate_of"] == 11
    assert rows[11]["classification"] == "real"
    assert rows[40]["classification"] == "superseded"
    assert rows[31]["classification"] == "noise"
    assert rows[50]["classification"] == "real", "a later version is a distinct release"
    assert all(row["reason"] for row in rows.values())
    assert "DRY RUN" in summary
    assert "PRIVATE-CARD-CONTENT" not in json.dumps(report) + summary
    assert str(catalogue) not in json.dumps(report) + summary


@pytest.mark.parametrize("body", [
    "No structured signal here.",
    "```json\n{not json}\n```",
    "```json\n[]\n```",
    "```json\n" + json.dumps(_signal(confidence=True)) + "\n```",
    "```json\n" + json.dumps(_signal(extra="unsupported")) + "\n```",
    "```json\n" + json.dumps(_signal(first_seen_url="http://example.com/model")) + "\n```",
    "```json\n" + json.dumps(_signal()) + "\n```\n```json\n" + json.dumps(_signal()) + "\n```",
])
def test_malformed_discoveries_stay_real_for_manual_review(tmp_path, body):
    report, _ = _run(tmp_path, [_issue(7, "acme-sdk-2", body=body)])

    row = report["issues"][0]
    assert row["classification"] == "real"
    assert "manual review" in row["reason"].lower()
    assert row["duplicate_of"] is None
    assert report["counts"] == {"duplicate": 0, "superseded": 0, "real": 1, "noise": 0}


def test_triage_is_order_independent_and_uses_number_to_break_time_ties(tmp_path):
    issues = [_issue(9), _issue(3), _issue(7, "acme-next-3")]
    forward, first_summary = _run(tmp_path, issues)
    reverse, second_summary = _run(tmp_path, list(reversed(issues)))

    assert forward == reverse
    assert first_summary == second_summary
    assert forward["catalogue_checked"] is False
    rows = {row["number"]: row for row in forward["issues"]}
    assert rows[9]["duplicate_of"] == 3
    assert rows[3]["classification"] == "real"


def test_triage_cannot_make_network_requests_or_run_issue_commands(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("offline triage attempted network access or a subprocess")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(httpx.Client, "request", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    report, _ = _run(tmp_path, [_issue(1)])
    assert report["counts"]["real"] == 1


@pytest.mark.parametrize("option", ["--apply", "--close", "--label", "--post"])
def test_triage_rejects_mutating_modes(tmp_path, option):
    triage = importlib.import_module("scripts.triage_release_discoveries")
    source = tmp_path / "issues.json"
    source.write_text("[]", encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        triage.main(["--issues", str(source), option])
    assert error.value.code == 2


def test_triage_public_cli_reports_empty_input_as_dry_run(tmp_path):
    source = tmp_path / "issues.json"
    source.write_text("[]", encoding="utf-8")
    report = tmp_path / "report.json"
    summary = tmp_path / "summary.md"
    done = subprocess.run([
        sys.executable, str(ROOT / "scripts" / "triage_release_discoveries.py"),
        "--issues", str(source), "--report", str(report), "--summary", str(summary),
    ], cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT)}, capture_output=True, text=True,
        timeout=30)

    assert done.returncode == 0, done.stderr
    assert json.loads(report.read_text())["counts"] == {
        "duplicate": 0, "superseded": 0, "real": 0, "noise": 0,
    }
    assert "DRY RUN" in summary.read_text()
    assert "DRY RUN" in done.stdout


def test_triage_standalone_cli_does_not_need_pythonpath(tmp_path):
    source = tmp_path / "issues.json"
    source.write_text("[]", encoding="utf-8")
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    # Include installed dependencies without executing editable-install .pth files.
    runner = (
        "import runpy, sys; "
        f"sys.path.extend({site.getsitepackages()!r}); "
        "sys.argv = sys.argv[1:]; runpy.run_path(sys.argv[0], run_name='__main__')"
    )
    done = subprocess.run([
        sys.executable, "-S", "-c", runner,
        str(ROOT / "scripts" / "triage_release_discoveries.py"),
        "--issues", str(source),
    ], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)

    assert done.returncode == 0, done.stderr
    assert "DRY RUN" in done.stdout


def test_malformed_signal_url_stays_real_for_manual_review(tmp_path):
    body = "```json\n" + json.dumps(_signal(first_seen_url="https://[bad]/")) + "\n```"
    report, _ = _run(tmp_path, [_issue(7, body=body)])
    row = report["issues"][0]
    assert row["classification"] == "real"
    assert "manual review" in row["reason"].lower()
    assert row["duplicate_of"] is None


@pytest.mark.parametrize("collision", ["report-input", "summary-input", "report-summary"])
def test_triage_refuses_output_collisions_without_changing_files(tmp_path, collision):
    triage = importlib.import_module("scripts.triage_release_discoveries")
    source = tmp_path / "issues.json"
    source.write_text(json.dumps([_issue(7)]), encoding="utf-8")
    output = tmp_path / "output"
    output.write_text("existing output", encoding="utf-8")
    original = source.read_bytes()
    options = {
        "report-input": ["--report", str(source)],
        "summary-input": ["--summary", str(source)],
        "report-summary": ["--report", str(output), "--summary", str(output)],
    }
    with pytest.raises(SystemExit) as error:
        triage.main(["--issues", str(source), *options[collision]])
    assert error.value.code == 2
    assert source.read_bytes() == original
    assert output.read_text() == "existing output"
