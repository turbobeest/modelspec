"""MODEL-246: the lag job publishes the private data as of today minus nine months."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import date
from pathlib import Path

import pytest

from scripts import data_lag
from scripts.data_lag import cutoff_for, run


@pytest.mark.parametrize("today,expected", [
    ("2026-09-30", "2025-12-30"),
    ("2027-06-30", "2026-09-30"),
    ("2027-05-31", "2026-08-31"),
    ("2026-05-31", "2025-08-31"),
    ("2027-03-31", "2026-06-30"),
    ("2026-11-30", "2026-02-28"),
    ("2028-11-30", "2028-02-29"),
    ("2026-01-15", "2025-04-15"),
])
def test_cutoff_is_nine_calendar_months_back(today, expected):
    assert cutoff_for(date.fromisoformat(today)) == date.fromisoformat(expected)


def _commit(repo: Path, when: str, files: dict[str, str | None]) -> str:
    for rel, text in files.items():
        path = repo / rel
        if text is None:
            path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    env = {**os.environ, "GIT_AUTHOR_DATE": f"{when}T12:00:00+00:00",
           "GIT_COMMITTER_DATE": f"{when}T12:00:00+00:00"}
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-q", "-m", when], check=True, env=env)
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repos(tmp_path):
    private = tmp_path / "private"
    private.mkdir()
    subprocess.run(["git", "-C", str(private), "init", "-q", "-b", "main"], check=True)
    public = tmp_path / "public"
    (public / "models").mkdir(parents=True)
    (public / "models" / "stale.md").write_text("stale")
    (public / "pipeline").mkdir()
    (public / "pipeline" / "code.py").write_text("code")
    return private, public


def test_no_commit_old_enough_changes_nothing(repos):
    private, public = repos
    _commit(private, "2026-09-30", {"models/a.md": "v1", "benchmarks/b.md": "v1"})
    result = run(private, public, date(2027, 6, 29))
    assert result["status"] == "no-image-yet"
    assert (public / "models" / "stale.md").read_text() == "stale"
    assert not (public / "data-image.json").exists()


def test_the_seed_publishes_on_the_ninth_month(repos):
    private, public = repos
    seed = _commit(private, "2026-09-30", {"models/a.md": "v1", "benchmarks/b.md": "v1"})
    _commit(private, "2027-02-01", {"models/a.md": "v2"})
    result = run(private, public, date(2027, 6, 30))
    assert result["status"] == "published" and result["commit"] == seed
    assert (public / "models" / "a.md").read_text() == "v1"
    assert not (public / "models" / "stale.md").exists()
    assert (public / "pipeline" / "code.py").read_text() == "code"
    manifest = json.loads((public / "data-image.json").read_text())
    assert manifest["as_of"] == "2026-09-30" and manifest["source_commit"] == seed


def test_a_rerun_is_unchanged(repos):
    private, public = repos
    _commit(private, "2026-09-30", {"models/a.md": "v1", "benchmarks/b.md": "v1"})
    run(private, public, date(2027, 6, 30))
    assert run(private, public, date(2027, 6, 30))["status"] == "unchanged"


def test_later_history_advances_the_image_and_drops_removed_files(repos):
    private, public = repos
    _commit(private, "2026-09-30", {"models/a.md": "v1", "models/gone.md": "x", "benchmarks/b.md": "v1"})
    second = _commit(private, "2026-10-15", {"models/a.md": "v2", "models/gone.md": None})
    run(private, public, date(2027, 6, 30))
    result = run(private, public, date(2027, 7, 15))
    assert result["status"] == "published" and result["commit"] == second
    assert (public / "models" / "a.md").read_text() == "v2"
    assert not (public / "models" / "gone.md").exists()


def test_a_dry_run_writes_nothing(repos):
    private, public = repos
    _commit(private, "2026-09-30", {"models/a.md": "v1", "benchmarks/b.md": "v1"})
    assert run(private, public, date(2027, 6, 30), dry_run=True)["status"] == "would-publish"
    assert (public / "models" / "stale.md").exists()
    assert not (public / "data-image.json").exists()


def test_main_prints_the_result(repos, capsys):
    private, public = repos
    _commit(private, "2026-09-30", {"models/a.md": "v1", "benchmarks/b.md": "v1"})
    code = data_lag.main(["--private", str(private), "--public", str(public), "--today", "2026-10-01"])
    assert code == 0
    assert json.loads(capsys.readouterr().out)["status"] == "no-image-yet"
