from __future__ import annotations

import json
import threading
import time
from types import SimpleNamespace

import pytest

import scripts.benchmarks.run_eligible as runner


def fake_report(ids):
    return SimpleNamespace(
        active_ids=list(ids),
        rows=[
            SimpleNamespace(
                candidate_id=item,
                model_dump=lambda mode="json", item=item: {"candidate_id": item},
            )
            for item in ids
        ],
    )


def test_rejects_nonactive_ids_before_creating_run_dir(tmp_path, monkeypatch):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    reference = tmp_path / "reference.json"
    reference.write_text("{}")
    monkeypatch.setattr(runner, "pause_marker", lambda: tmp_path / "QUALITY_AUDIT_PAUSE.json")
    monkeypatch.setattr(runner, "GLOBAL_LOCK_PATH", tmp_path / "eligible-run.lock")
    monkeypatch.setattr(runner, "build_report", lambda *args: fake_report(["allowed"]))
    with pytest.raises(SystemExit):
        runner.main(
            [
                "--evidence",
                str(evidence),
                "--reference-set",
                str(reference),
                "--ids",
                "denied",
                "--run-dir",
                str(tmp_path / "run"),
                "--grok",
                "/fake/grok",
            ]
        )
    assert not (tmp_path / "run").exists()


def test_bounded_jobs_write_partitioned_review_and_status(tmp_path, monkeypatch):
    ids = ["one", "two", "three"]
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    reference = tmp_path / "reference.json"
    reference.write_text("{}")
    monkeypatch.setattr(runner, "pause_marker", lambda: tmp_path / "QUALITY_AUDIT_PAUSE.json")
    monkeypatch.setattr(runner, "GLOBAL_LOCK_PATH", tmp_path / "eligible-run.lock")
    pages = {item: tmp_path / f"{item}.md" for item in ids}
    for item in ids:
        (evidence / f"{item}.json").write_text(json.dumps({"candidate_id": item}))
    monkeypatch.setattr(runner, "build_report", lambda *args: fake_report(ids))
    monkeypatch.setattr(runner, "page_for", lambda item: pages[item])
    monkeypatch.setattr(runner, "page_hash", lambda path: "hash")
    lock = threading.Lock()
    running = 0
    maximum = 0

    def fake_run(command, log_dir, stem, cwd):
        nonlocal running, maximum
        with lock:
            running += 1
            maximum = max(maximum, running)
        time.sleep(0.01)
        if stem == "reviewer":
            job_id = log_dir.parent.name
            (log_dir.parent / "review.json").write_text(
                json.dumps(
                    {"id": job_id, "verdict": "approved", "reason": "primary source checked"}
                )
            )
        with lock:
            running -= 1
        return 0

    monkeypatch.setattr(runner, "run_logged", fake_run)
    monkeypatch.setattr(runner, "STOP", threading.Event())
    run_dir = tmp_path / "run"
    assert (
        runner.main(
            [
                "--evidence",
                str(evidence),
                "--reference-set",
                str(reference),
                "--ids",
                *ids,
                "--run-dir",
                str(run_dir),
                "--concurrency",
                "2",
                "--grok",
                "/fake/grok",
            ]
        )
        == 0
    )
    assert maximum <= 2
    status = json.loads((run_dir / "status.json").read_text())
    assert status["phase"] == "ready-for-coordinator"
    assert all(item["status"] == "ready-for-coordinator" for item in status["jobs"].values())
    for item in ids:
        review = json.loads((run_dir / "jobs" / item / "review.json").read_text())
        assert set(review) == {"id", "reason", "verdict"}


def test_invalid_review_needs_attention_and_preserves_page(tmp_path, monkeypatch):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    reference = tmp_path / "reference.json"
    reference.write_text("{}")
    monkeypatch.setattr(runner, "pause_marker", lambda: tmp_path / "QUALITY_AUDIT_PAUSE.json")
    monkeypatch.setattr(runner, "GLOBAL_LOCK_PATH", tmp_path / "eligible-run.lock")
    page = tmp_path / "page.md"
    page.write_text("verified existing page")
    monkeypatch.setattr(runner, "build_report", lambda *args: fake_report(["one"]))
    monkeypatch.setattr(runner, "page_for", lambda item: page)

    def fake_run(command, log_dir, stem, cwd):
        if stem == "reviewer":
            (log_dir.parent / "review.json").write_text(
                json.dumps({"id": "one", "verdict": "approved", "reason": ""})
            )
        return 0

    monkeypatch.setattr(runner, "run_logged", fake_run)
    assert (
        runner.main(
            [
                "--evidence",
                str(evidence),
                "--reference-set",
                str(reference),
                "--ids",
                "one",
                "--run-dir",
                str(tmp_path / "run"),
                "--grok",
                "/fake/grok",
            ]
        )
        == 2
    )
    assert page.read_text() == "verified existing page"


@pytest.mark.parametrize(
    "scenario", ["stop", "expired", "pause_removed", "page_mutated", "approved"]
)
def test_phase_admission_soft_stop_and_review_binding(tmp_path, monkeypatch, scenario):
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    (evidence_dir / "one.json").write_text('{"candidate_id":"one"}')
    reference = tmp_path / "reference.json"
    reference.write_text("{}")
    page = tmp_path / "one.md"
    page.write_text("original draft")
    admitted = True
    paused = True
    calls = []
    monkeypatch.setattr(runner, "STOP", threading.Event())
    monkeypatch.setattr(runner, "page_for", lambda _: page)
    monkeypatch.setattr(runner, "pause_marker", lambda: tmp_path if paused else None)
    monkeypatch.setattr(
        runner, "build_report", lambda *args: fake_report(["one"] if admitted else [])
    )

    def fake_run(command, log_dir, stem, cwd):
        nonlocal admitted, paused
        calls.append(stem)
        if stem == "writer":
            page.write_text("researched draft")
            if scenario == "stop":
                runner.STOP.set()
            elif scenario == "expired":
                admitted = False
            elif scenario == "pause_removed":
                paused = False
        if stem == "reviewer":
            (log_dir.parent / "review.json").write_text(
                json.dumps(
                    {
                        "id": "one",
                        "verdict": "approved",
                        "reason": "independent source review",
                    }
                )
            )
            if scenario == "page_mutated":
                page.write_text("unexpected concurrent edit")
        return 0

    monkeypatch.setattr(runner, "run_logged", fake_run)
    run_dir = tmp_path / "run"
    _, ok, _ = runner.job("one", run_dir, evidence_dir, reference, "/fake/grok", {"jobs": {}})
    assert ok is (scenario == "approved")
    assert (run_dir / "jobs/one/before.md").read_text() == "original draft"
    if scenario in {"stop", "expired", "pause_removed"}:
        assert "reviewer" not in calls
    assert (run_dir / "jobs/one/approved-page.json").exists() is ok
