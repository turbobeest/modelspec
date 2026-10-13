"""Published blog revisions and correction history cannot be replaced."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from pipeline.blog_append_only import check_append_only

REPO_ROOT = Path(__file__).resolve().parents[1]
SLUG = "2026-09-26-alpha"
POST = Path("blog/posts") / SLUG
CORRECTION = {
    "id": "c1",
    "date": "2026-09-27",
    "revision": 1,
    "field": "/standing/value",
    "was": {"value": 42, "record_id": "rec_old", "snapshot_id": "snap_old"},
    "now": {"value": 43, "record_id": "rec_new", "snapshot_id": "snap_new"},
    "effect": "The recorded reading changed.",
    "fix_pr": "https://github.com/turbobeest/modelspec/pull/999",
}


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Blog test",
            "-c",
            "user.email=blog@example.test",
            *args,
        ],
        capture_output=True,
        text=True,
        check=True,
    )


def _write(repo: Path, path: Path, text: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _metadata(repo: Path) -> dict:
    return yaml.safe_load((repo / POST / "post.yaml").read_text(encoding="utf-8"))


def _write_metadata(repo: Path, data: dict) -> None:
    _write(repo, POST / "post.yaml", yaml.safe_dump(data, sort_keys=False))


@pytest.fixture
def published_repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    _write_metadata(
        tmp_path,
        {
            "schema_version": 1,
            "model": "lab/alpha",
            "title": "Alpha release breakdown",
            "status": "published",
            "early_access": None,
            "revisions": [
                {
                    "revision": 1,
                    "published": "2026-09-26",
                    "approved_by": "jamie",
                    "approval": "https://github.com/turbobeest/modelspec/pull/998#issuecomment-1",
                }
            ],
        },
    )
    _write(tmp_path, POST / "r1/breakdown.json", '{"revision":1,"standing":42}\n')
    _write(tmp_path, POST / "r1/charts/standing.svg", "<svg>published chart</svg>\n")
    _write(tmp_path, POST / "corrections.yaml", yaml.safe_dump([CORRECTION]))
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "published blog")
    _git(tmp_path, "update-ref", "refs/remotes/origin/main", "HEAD")
    _git(tmp_path, "switch", "-q", "-c", "feature/blog")
    return tmp_path


def test_repository_preserves_published_blog_history():
    assert check_append_only(REPO_ROOT, base="origin/main") == []


def test_unchanged_published_revision_passes(published_repo: Path):
    assert check_append_only(published_repo, base="origin/main") == []


@pytest.mark.parametrize("change", ["add", "edit", "delete"])
def test_published_commentary_cannot_change(published_repo: Path, change: str):
    commentary = POST / "commentary.md"
    if change != "add":
        _write(published_repo, commentary, "The original commentary.\n")
        _git(published_repo, "add", "-A")
        _git(published_repo, "commit", "-q", "-m", "published commentary")
        _git(published_repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    if change == "delete":
        (published_repo / commentary).unlink()
    else:
        _write(published_repo, commentary, "A changed account of the model.\n")
    assert any("commentary" in problem for problem in check_append_only(published_repo))


@pytest.mark.parametrize("state", ["unstaged", "staged", "committed"])
def test_changed_published_file_fails_in_every_git_state(published_repo: Path, state: str):
    path = POST / "r1/breakdown.json"
    _write(published_repo, path, '{"revision":1,"standing":0}\n')
    if state in {"staged", "committed"}:
        _git(published_repo, "add", "-A")
    if state == "committed":
        _git(published_repo, "commit", "-q", "-m", "replace published value")
    problems = check_append_only(published_repo, base="origin/main")
    assert any(str(path) in problem for problem in problems), problems


def test_deleted_published_file_fails(published_repo: Path):
    path = POST / "r1/charts/standing.svg"
    (published_repo / path).unlink()
    assert any(str(path) in problem for problem in check_append_only(published_repo))


def test_new_file_in_published_directory_fails(published_repo: Path):
    path = POST / "r1/extra.md"
    _write(published_repo, path, "Unreviewed material.\n")
    assert any(str(path) in problem for problem in check_append_only(published_repo))


def test_deleted_published_post_fails(published_repo: Path):
    (published_repo / POST / "post.yaml").unlink()
    assert any(str(POST / "post.yaml") in problem for problem in check_append_only(published_repo))


@pytest.mark.parametrize(
    "field,value", [("title", "Changed title"), ("model", "lab/beta"), ("status", "draft")]
)
def test_published_post_identity_cannot_change(published_repo: Path, field: str, value: str):
    metadata = _metadata(published_repo)
    metadata[field] = value
    _write_metadata(published_repo, metadata)
    problems = check_append_only(published_repo)
    assert any("post.yaml" in problem and field in problem for problem in problems), problems


@pytest.mark.parametrize(
    "field,value",
    [
        ("published", "2026-09-28"),
        ("approved_by", "someone-else"),
        ("approval", None),
        ("revision", 2),
    ],
)
def test_published_revision_metadata_cannot_change(published_repo: Path, field: str, value: object):
    metadata = _metadata(published_repo)
    metadata["revisions"][0][field] = value
    _write_metadata(published_repo, metadata)
    assert any("post.yaml" in problem for problem in check_append_only(published_repo))


def test_published_revision_cannot_be_removed(published_repo: Path):
    metadata = _metadata(published_repo)
    metadata["revisions"] = []
    _write_metadata(published_repo, metadata)
    assert any("revision 1" in problem for problem in check_append_only(published_repo))


@pytest.mark.parametrize("change", ["edit", "delete", "prepend", "remove-file"])
def test_existing_corrections_remain_an_identical_prefix(published_repo: Path, change: str):
    path = POST / "corrections.yaml"
    entries = [dict(CORRECTION)]
    if change == "edit":
        entries[0]["effect"] = "Changed the historical explanation."
    elif change == "delete":
        entries.clear()
    elif change == "prepend":
        entries.insert(0, {**CORRECTION, "id": "c0"})
    if change == "remove-file":
        (published_repo / path).unlink()
    else:
        _write(published_repo, path, yaml.safe_dump(entries))
    assert any("corrections.yaml" in problem for problem in check_append_only(published_repo))


def test_correction_append_and_new_revision_pass(published_repo: Path):
    metadata = _metadata(published_repo)
    metadata["revisions"].append(
        {
            "revision": 2,
            "published": "2026-09-27",
            "approved_by": "jamie",
            "approval": "https://github.com/turbobeest/modelspec/pull/999",
        }
    )
    _write_metadata(published_repo, metadata)
    _write(published_repo, POST / "r2/breakdown.json", '{"revision":2,"standing":43}\n')
    _write(
        published_repo,
        POST / "corrections.yaml",
        yaml.safe_dump([CORRECTION, {**CORRECTION, "id": "c2"}]),
    )
    assert check_append_only(published_repo) == []


def test_draft_edit_and_publication_pass(published_repo: Path):
    metadata = _metadata(published_repo)
    metadata["status"] = "draft"
    metadata["revisions"][0].update(published=None, approved_by=None, approval=None)
    _write_metadata(published_repo, metadata)
    _git(published_repo, "add", "-A")
    _git(published_repo, "commit", "-q", "-m", "draft baseline")
    _git(published_repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    metadata["title"] = "An approved title"
    _write(published_repo, POST / "r1/breakdown.json", '{"revision":1,"standing":45}\n')
    _write_metadata(published_repo, metadata)
    assert check_append_only(published_repo) == []
    metadata["status"] = "published"
    metadata["revisions"][0].update(
        published="2026-09-26",
        approved_by="jamie",
        approval="https://github.com/turbobeest/modelspec/pull/999",
    )
    _write_metadata(published_repo, metadata)
    assert check_append_only(published_repo) == []


@pytest.mark.parametrize("path", ["post.yaml", "corrections.yaml"])
def test_malformed_existing_metadata_fails(published_repo: Path, path: str):
    _write(published_repo, POST / path, "[unclosed\n")
    assert any(path in problem for problem in check_append_only(published_repo))


def test_cli_returns_nonzero_and_names_replaced_file(published_repo: Path):
    path = POST / "r1/breakdown.json"
    _write(published_repo, path, "replacement\n")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pipeline.blog_append_only",
            "--base",
            "origin/main",
            "--root",
            str(published_repo),
        ],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, result.stderr
    assert str(path) in result.stdout + result.stderr


def test_unknown_base_fails_instead_of_skipping_the_check(published_repo: Path):
    with pytest.raises(ValueError, match="base"):
        check_append_only(published_repo, base="missing-base")


def test_existing_correction_value_types_cannot_change(published_repo: Path):
    path = POST / "corrections.yaml"
    entries = yaml.safe_load((published_repo / path).read_text(encoding="utf-8"))
    entries[0]["was"]["value"] = 42.0
    _write(published_repo, path, yaml.safe_dump(entries))
    assert any("corrections.yaml" in problem for problem in check_append_only(published_repo))


def test_correction_mapping_key_order_may_change(published_repo: Path):
    _write(published_repo, POST / "corrections.yaml", yaml.safe_dump([CORRECTION], sort_keys=False))
    assert check_append_only(published_repo) == []


def test_symbolic_link_cannot_replace_published_file(published_repo: Path):
    path = POST / "r1/breakdown.json"
    original = (published_repo / path).read_bytes()
    target = published_repo / "same-content.json"
    target.write_bytes(original)
    (published_repo / path).unlink()
    (published_repo / path).symlink_to(target)
    problems = check_append_only(published_repo)
    assert any(str(path) in problem and "symbolic" in problem for problem in problems), problems
