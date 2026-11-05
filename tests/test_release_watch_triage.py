"""Discovery triage defaults to offline review; explicit apply is bounded."""

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


def _run(tmp_path: Path, issues: list, *extra: str, expected_exit: int = 0) -> tuple[dict, str]:
    triage = importlib.import_module("scripts.triage_release_discoveries")
    source = tmp_path / "issues.json"
    report = tmp_path / "report.json"
    summary = tmp_path / "summary.md"
    source.write_text(json.dumps(issues), encoding="utf-8")
    original = source.read_bytes()
    if "--apply" in extra and "--repo" not in extra:
        extra = (*extra, "--repo", "example/models")
    assert triage.main([
        "--issues", str(source), "--report", str(report), "--summary", str(summary), *extra,
    ]) == expected_exit
    assert source.read_bytes() == original
    return json.loads(report.read_text()), summary.read_text()


def test_triage_classifies_duplicates_carded_releases_real_and_noise(tmp_path):
    catalogue = _catalogue(tmp_path / "private")
    report, summary = _run(tmp_path, [
        _issue(12, "Acme New 2"),
        _issue(40, "acme-one-1"),
        _issue(31, "acme-sdk"),
        _issue(32, "acme-sdk-2"),
        _issue(11, createdAt="2026-10-18T00:00:00Z"),
        _issue(50, "acme-one-2"),
    ], "--catalogue-root", str(catalogue))

    assert report["dry_run"] is True
    assert report["catalogue_checked"] is True
    assert report["counts"] == {"duplicate": 1, "superseded": 1, "real": 3, "noise": 1}
    rows = {row["number"]: row for row in report["issues"]}
    assert rows[12]["classification"] == "duplicate"
    assert rows[12]["duplicate_of"] == 11
    assert rows[11]["classification"] == "real"
    assert rows[40]["classification"] == "superseded"
    assert rows[31]["classification"] == "noise"
    assert rows[32]["classification"] == "real"
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


@pytest.mark.parametrize("option", ["--close", "--label", "--post"])
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


class FakeGitHub:
    """Exercise the CLI against a process/time boundary, never live GitHub."""

    def __init__(self, monkeypatch, issues):
        import time

        self.now = 0.0
        self.calls = []
        self.labels = {"release-review"}
        self.fail_once = None
        self.issues = {
            row["number"]: {
                "state": "OPEN", "labels": [{"name": "release-discovery"}],
                "comments": [], "body": row["body"], "title": row["title"],
            }
            for row in issues
        }
        monkeypatch.setattr(subprocess, "run", self.run)
        monkeypatch.setattr(time, "monotonic", lambda: self.now)
        monkeypatch.setattr(time, "sleep", self.sleep)

    def sleep(self, seconds):
        assert seconds >= 0
        self.now += seconds

    def run(self, argv, **kwargs):
        assert argv[0] == "gh"
        assert kwargs.get("stdin") == subprocess.DEVNULL
        assert kwargs.get("timeout") is not None
        self.calls.append((self.now, argv))
        self.now += 0.1
        action = tuple(argv[1:3])
        if action == self.fail_once:
            self.fail_once = None
            return subprocess.CompletedProcess(argv, 1, "", "synthetic GitHub failure")
        if action == ("label", "list"):
            output = [{"name": name} for name in self.labels]
        elif action == ("label", "create"):
            self.labels.add(argv[3])
            output = None
        elif action == ("issue", "list"):
            output = [
                {"number": number, "labels": issue["labels"]}
                for number, issue in self.issues.items()
                if issue["state"] == "OPEN"
                and any(label["name"] == "release-discovery" for label in issue["labels"])
            ]
        else:
            number = int(argv[3])
            issue = self.issues[number]
            if action == ("issue", "view"):
                output = issue
            elif action == ("issue", "comment"):
                issue["comments"].append({"body": argv[argv.index("--body") + 1]})
                output = None
            elif action == ("issue", "close"):
                assert argv[argv.index("--reason") + 1] == "not planned"
                issue["state"] = "CLOSED"
                output = None
            elif action == ("issue", "edit"):
                label = argv[argv.index("--add-label") + 1]
                assert label in self.labels
                assert "--remove-label" not in argv, "discovery identity must remain dedupable"
                issue["labels"].append({"name": label})
                output = None
            else:
                pytest.fail(f"Unexpected GitHub command: {argv}")
        return subprocess.CompletedProcess(argv, 0, json.dumps(output), "")


def test_dry_run_reports_every_issue_with_decision_and_rule(tmp_path):
    report, summary = _run(tmp_path, [_issue(n, f"acme-{n}") for n in range(1, 9)])
    assert len(report["issues"]) == 8
    for row in report["issues"]:
        assert row["decision"] == "relabel"
        assert row["rule"] == "possible-release"
        assert f"#{row['number']}]" in summary
        assert row["title"] in summary


def test_apply_closes_noise_and_relabels_real_with_paced_reason_comments(tmp_path, monkeypatch):
    issues = [_issue(1, "acme-sdk"), _issue(2, "mistral-large-4")]
    fake = FakeGitHub(monkeypatch, issues)
    report, summary = _run(tmp_path, issues, "--apply", "--max-calls", "10")

    assert report["dry_run"] is False
    assert "DRY RUN" not in summary
    assert fake.issues[1]["state"] == "CLOSED"
    assert fake.issues[2]["state"] == "OPEN"
    assert {label["name"] for label in fake.issues[2]["labels"]} == {
        "release-review", "release-discovery",
    }
    for issue in fake.issues.values():
        assert len(issue["comments"]) == 1
        assert "\n" not in issue["comments"][0]["body"]
    assert all(b[0] - a[0] >= 1 for a, b in zip(fake.calls, fake.calls[1:]))
    assert report["apply"]["calls_used"] == len(fake.calls)


def test_apply_call_cap_includes_reads_and_leaves_unstarted_writes_pending(tmp_path, monkeypatch):
    issues = [_issue(1, "acme-sdk"), _issue(2, "acme-docs")]
    fake = FakeGitHub(monkeypatch, issues)
    report, _ = _run(tmp_path, issues, "--apply", "--max-calls", "5", expected_exit=1)

    assert len(fake.calls) == 5
    assert fake.issues[1]["state"] == "CLOSED"
    assert fake.issues[2]["state"] == "OPEN"
    assert fake.issues[2]["comments"] == []
    assert report["apply"]["budget_exhausted"] is True
    assert report["issues"][1]["apply_status"] == "pending_budget"


def test_apply_resumes_without_touching_closed_or_already_reviewed_issues(tmp_path, monkeypatch):
    issues = [_issue(1, "acme-sdk"), _issue(2, "acme-new-2")]
    fake = FakeGitHub(monkeypatch, issues)
    _run(tmp_path, issues, "--apply")
    first_comments = [len(fake.issues[n]["comments"]) for n in (1, 2)]
    fake.calls.clear()

    report, _ = _run(tmp_path, issues, "--apply")
    assert [len(fake.issues[n]["comments"]) for n in (1, 2)] == first_comments
    assert [argv[1:3] for _, argv in fake.calls] == [["issue", "list"]]
    assert [row["apply_status"] for row in report["issues"]] == [
        "skipped_not_open_discovery", "skipped_reviewed",
    ]


def test_apply_failure_is_reported_and_resume_does_not_duplicate_reason(tmp_path, monkeypatch):
    issues = [_issue(1, "acme-sdk")]
    fake = FakeGitHub(monkeypatch, issues)
    fake.fail_once = ("issue", "close")
    triage = importlib.import_module("scripts.triage_release_discoveries")
    source, report_path = tmp_path / "issues.json", tmp_path / "report.json"
    source.write_text(json.dumps(issues))
    args = ["--issues", str(source), "--report", str(report_path), "--apply", "--repo", "example/models"]

    assert triage.main(args) == 1
    report = json.loads(report_path.read_text())
    assert "synthetic GitHub failure" in report["apply"]["error"]
    assert fake.issues[1]["state"] == "OPEN"
    assert len(fake.issues[1]["comments"]) == 1

    assert triage.main(args) == 0
    assert fake.issues[1]["state"] == "CLOSED"
    assert len(fake.issues[1]["comments"]) == 1


def test_apply_ensures_review_label_within_call_cap(tmp_path, monkeypatch):
    issues = [_issue(1)]
    fake = FakeGitHub(monkeypatch, issues)
    fake.labels.clear()
    report, _ = _run(tmp_path, issues, "--apply", "--max-calls", "6")

    assert "release-review" in fake.labels
    assert len(fake.calls) == 6
    assert report["issues"][0]["apply_status"] == "relabeled"
    assert all(b[0] - a[0] >= 1 for a, b in zip(fake.calls, fake.calls[1:]))


def test_apply_skips_issue_removed_from_discovery_or_edited_since_export(tmp_path, monkeypatch):
    issues = [_issue(1, "acme-sdk"), _issue(2, "acme-docs")]
    fake = FakeGitHub(monkeypatch, issues)
    fake.issues[1]["labels"] = []
    fake.issues[2]["body"] = "A curator replaced the original signal."
    report, _ = _run(tmp_path, issues, "--apply")

    assert all(argv[1:3] in (["issue", "list"], ["issue", "view"]) for _, argv in fake.calls)
    assert [row["apply_status"] for row in report["issues"]] == [
        "skipped_not_open_discovery", "skipped_changed",
    ]


@pytest.mark.parametrize("cap", ["0", "-1"])
def test_apply_rejects_nonpositive_call_caps_before_github(tmp_path, monkeypatch, cap):
    issues = [_issue(1)]
    fake = FakeGitHub(monkeypatch, issues)
    source = tmp_path / "issues.json"
    source.write_text(json.dumps(issues))
    triage = importlib.import_module("scripts.triage_release_discoveries")
    with pytest.raises(SystemExit) as error:
        triage.main(["--issues", str(source), "--apply", "--max-calls", cap])
    assert error.value.code == 2
    assert fake.calls == []


def test_resume_reaches_pending_issues_beyond_a_full_call_budget_of_closed_issues(tmp_path, monkeypatch):
    issues = [_issue(n, "acme-sdk") for n in range(1, 13)]
    fake = FakeGitHub(monkeypatch, issues)
    for n in range(1, 12):
        fake.issues[n]["state"] = "CLOSED"
    report, _ = _run(tmp_path, issues, "--apply", "--max-calls", "10")

    assert fake.issues[12]["state"] == "CLOSED"
    assert report["issues"][-1]["apply_status"] == "closed"
    assert len(fake.calls) <= 10


def test_triage_matches_separator_variants_to_cards_and_duplicate_issues(tmp_path):
    catalogue = _catalogue(tmp_path / "private")
    card = catalogue / "models" / "google" / "gemini-25-flash.md"
    card.parent.mkdir()
    card.write_text(
        "---\nmodel_id: google/gemini-25-flash\ndisplay_name: Gemini 25 Flash\n"
        "provider: google\nprovider_display: Google\nversion: gemini-25-flash\n---\n"
    )
    def google_issue(number, name):
        return _issue(number, name, body="```json\n" + json.dumps(_signal(name, provider="google")) + "\n```")

    report, _ = _run(tmp_path, [
        google_issue(1, "gemini-2.5-flash"), google_issue(2, "gemini-25-flash"),
        google_issue(3, "gemini-2.5-next"), google_issue(4, "gemini-25-next"),
    ], "--catalogue-root", str(catalogue))
    assert [row["classification"] for row in report["issues"]] == [
        "superseded", "duplicate", "real", "duplicate",
    ]


def test_triage_keeps_distinct_numeric_versions_separate(tmp_path):
    report, _ = _run(tmp_path, [_issue(1, "acme-2.10"), _issue(2, "acme-21.0")])
    assert [row["classification"] for row in report["issues"]] == ["real", "real"]


def test_apply_does_not_close_duplicate_when_its_original_issue_changed(tmp_path, monkeypatch):
    issues = [_issue(1), _issue(2)]
    fake = FakeGitHub(monkeypatch, issues)
    fake.issues[1]["body"] = "A different release after curator review."
    report, _ = _run(tmp_path, issues, "--apply")
    assert fake.issues[2]["state"] == "OPEN"
    assert fake.issues[2]["comments"] == []
    assert report["issues"][1]["apply_status"] == "skipped_changed_anchor"


def test_triage_checks_original_hub_org_after_watch_provider_was_canonicalized(tmp_path):
    signal = _signal(
        "LFM-2.5", provider="liquid", first_seen_url="https://huggingface.co/unsloth/LFM-2.5",
    )
    report, _ = _run(tmp_path, [_issue(1, body="```json\n" + json.dumps(signal) + "\n```")])
    assert report["issues"][0]["classification"] == "noise"
    assert report["issues"][0]["rule"] == "reupload/quant organization"


@pytest.mark.parametrize("failure", ["listing-error", "listing-limit"])
def test_apply_stops_without_writes_if_open_listing_fails_or_may_be_incomplete(tmp_path, monkeypatch, failure):
    issues = [_issue(n) for n in range(1, 1001)] if failure == "listing-limit" else [_issue(1)]
    fake = FakeGitHub(monkeypatch, issues)
    if failure == "listing-error":
        fake.fail_once = ("issue", "list")
    source, report_path = tmp_path / "issues.json", tmp_path / "report.json"
    source.write_text(json.dumps(issues))
    triage = importlib.import_module("scripts.triage_release_discoveries")
    assert triage.main([
        "--issues", str(source), "--report", str(report_path), "--apply", "--repo", "example/models",
    ]) == 1
    report = json.loads(report_path.read_text())
    assert report["apply"]["error"]
    assert len(fake.calls) == 1
    assert all(issue["comments"] == [] and issue["state"] == "OPEN" for issue in fake.issues.values())


@pytest.mark.parametrize("output_flag", ["--report", "--summary"])
def test_triage_refuses_to_write_inside_private_catalogue(tmp_path, monkeypatch, output_flag):
    issues = [_issue(1)]
    fake = FakeGitHub(monkeypatch, issues)
    catalogue = _catalogue(tmp_path / "private")
    protected = catalogue / "models" / "acme" / "acme-one-1.md"
    original = protected.read_bytes()
    source = tmp_path / "issues.json"
    source.write_text(json.dumps(issues))
    triage = importlib.import_module("scripts.triage_release_discoveries")
    with pytest.raises(SystemExit) as error:
        triage.main([
            "--issues", str(source), "--catalogue-root", str(catalogue),
            output_flag, str(protected), "--apply", "--repo", "example/models",
        ])
    assert error.value.code == 2
    assert protected.read_bytes() == original
    assert fake.calls == []


def test_apply_rejects_export_from_a_different_repository_before_github(tmp_path, monkeypatch):
    issues = [_issue(1, "acme-sdk")]
    fake = FakeGitHub(monkeypatch, issues)
    source = tmp_path / "issues.json"
    source.write_text(json.dumps(issues))
    triage = importlib.import_module("scripts.triage_release_discoveries")
    with pytest.raises(SystemExit) as error:
        triage.main(["--issues", str(source), "--apply", "--repo", "wrong/repository"])
    assert error.value.code == 2
    assert fake.calls == []
