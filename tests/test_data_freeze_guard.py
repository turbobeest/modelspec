"""MODEL-246: fresh data cannot land in the public repository."""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

import pytest

from scripts import data_freeze_guard as guard
from scripts.data_freeze_guard import judge, newer_than

TODAY = date(2027, 6, 30)  # cutoff 2026-09-30


def test_a_change_outside_the_data_paths_passes():
    assert judge(["docs/x.md", "pipeline/a.py", "registry/facets.yaml"], {}, None, "feature/x", TODAY).ok


def test_a_data_change_on_an_ordinary_branch_fails_and_names_the_file():
    verdict = judge(["models/a.md", "docs/x.md"], {}, None, "research/daily-models", TODAY)
    assert not verdict.ok
    assert "models/a.md" in verdict.problems[0]
    assert "turbobeest/modelspec-data" in verdict.problems[0]


def test_a_lone_manifest_change_on_an_ordinary_branch_fails():
    assert not judge(["data-image.json"], {}, None, "feature/x", TODAY).ok


def test_a_clean_lag_change_passes():
    verdict = judge(
        ["models/a.md", "data-image.json"],
        {"models/a.md": "release_date: '2026-09-30'\nlast_updated: 2026-01-02"},
        date(2026, 9, 30), "data-lag/image", TODAY,
    )
    assert verdict.ok, verdict.problems


def test_a_lag_change_with_a_date_after_the_cutoff_fails():
    verdict = judge(
        ["models/a.md", "data-image.json"], {"models/a.md": "last_updated: 2026-10-01"},
        date(2026, 9, 30), "data-lag/image", TODAY,
    )
    assert not verdict.ok and "2026-10-01" in verdict.problems[0]


def test_a_lag_change_whose_image_is_too_new_fails():
    verdict = judge(["models/a.md", "data-image.json"], {}, date(2026, 10, 1), "data-lag/image", TODAY)
    assert not verdict.ok and "after the cutoff" in verdict.problems[0]


def test_a_lag_change_without_the_manifest_fails():
    verdict = judge(["models/a.md"], {}, None, "data-lag/image", TODAY)
    assert not verdict.ok
    assert any("not part of" in p for p in verdict.problems)


def test_a_lag_change_with_an_unreadable_manifest_fails():
    verdict = judge(["models/a.md", "data-image.json"], {}, None, "data-lag/image", TODAY)
    assert not verdict.ok and any("no readable source_committed" in p for p in verdict.problems)


def test_the_cutoff_moves_with_today():
    added = {"models/a.md": "x: 2026-12-01"}
    changed = ["models/a.md", "data-image.json"]
    assert not judge(changed, added, date(2026, 12, 1), "data-lag/i", date(2027, 6, 30)).ok
    assert judge(changed, added, date(2026, 12, 1), "data-lag/i", date(2027, 9, 1)).ok


def test_newer_than_ignores_impossible_dates_and_longer_numbers():
    text = "a: 2026-13-45\nb: 12026-10-05\nc: 2026-10-05-x\nd: 2026-10-05"
    assert newer_than(text, date(2026, 9, 30)) == ["2026-10-05"]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


def test_collect_reads_the_three_dot_diff_from_git(tmp_path, monkeypatch):
    repo = tmp_path
    _git(repo, "init", "-q", "-b", "main")
    (repo / "models").mkdir()
    (repo / "models" / "a.md").write_text("last_updated: 2020-01-01\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "switch", "-q", "-c", "data-lag/image")
    (repo / "models" / "a.md").write_text("last_updated: 2020-01-01\nseen: 2026-10-03\n")
    (repo / "data-image.json").write_text('{"as_of": "2026-09-30", "source_committed": "2026-09-30"}')
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "lag")
    _git(repo, "switch", "-q", "main")
    (repo / "docs.txt").write_text("main moved")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "main moves")
    monkeypatch.setattr(guard, "REPO_ROOT", repo)
    changed, added, as_of = guard.collect("main", "data-lag/image")
    assert sorted(changed) == ["data-image.json", "models/a.md"]
    assert added["models/a.md"] == "seen: 2026-10-03"
    assert as_of == date(2026, 9, 30)
    assert not judge(changed, added, as_of, "data-lag/image", TODAY).ok
