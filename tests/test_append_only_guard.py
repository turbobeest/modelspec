"""MODEL-491: every evidence log in the private data is append-only against its trusted base.

The base's bytes must be a byte prefix of the head's, both read as raw git objects: an edited
line (its hash recomputed or not), a deleted line, a reordered pair, a removed log, a mode change
and a symlink each fail; a pure append, a new log and a merge of main that puts main's lines
first pass. The base is an explicit full SHA (the pull request event's base, a push's before, or
the remote-tracking default branch), the head must contain it, and a run that cannot show it
fails closed. Every repository here is synthetic.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess

import pytest
from scripts.append_only_guard import (
    BaseUnresolvedError,
    check,
    is_log,
    main,
    problems,
    resolve_base,
)
from scripts.prepare_data_writer import append_only

LOG = "verification/cited-attempts.jsonl"
QUEUE = "verification/queue/events.jsonl"


@pytest.fixture(autouse=True)
def no_ci_event(monkeypatch):
    for name in ("GITHUB_EVENT_NAME", "GITHUB_EVENT_PATH", "GITHUB_BASE_REF", "GITHUB_ACTIONS",
                 "GITHUB_REPOSITORY", "MODELSPEC_APPEND_ONLY_BASE"):
        monkeypatch.delenv(name, raising=False)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def line(n, value="a"):
    body = {"n": n, "value": value}
    body["sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    return json.dumps(body, sort_keys=True) + "\n"


def write(root, text, path=LOG):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def commit(root, message):
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m",
        message)
    return git(root, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path):
    """A checkout with main at a base commit, its remote-tracking ref, and a PR branch."""
    root = tmp_path / "data"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, line(1) + line(2) + line(3))
    write(root, line(1), QUEUE)
    base = commit(root, "base")
    git(root, "update-ref", "refs/remotes/origin/main", base)
    git(root, "checkout", "-q", "-b", "pr")
    return root


def pull_request(monkeypatch, tmp_path, base_sha):
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"pull_request": {"base": {"sha": base_sha}}}))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))


def test_the_rule_covers_every_evidence_log():
    for path in ("verification/log.jsonl", QUEUE, LOG, "verification/quarantine-clearings.jsonl",
                 "verification/owner-rulings.jsonl",
                 "reports/evidence-reread/ruled-reopenings.jsonl"):
        assert is_log(path), path
    for path in ("models/a.md", "verification/README.md", "reports/evidence-reread/x/y.jsonl"):
        assert not is_log(path), path


def test_a_pure_append_and_a_new_log_pass(repo):
    write(repo, line(1) + line(2) + line(3) + line(4))
    write(repo, line(9), "verification/new-log.jsonl")
    commit(repo, "append")
    assert check(repo) == []


@pytest.mark.parametrize("change,kind", [
    ("edited", "edited"), ("edited_rehashed", "edited"), ("deleted", "deleted lines"),
    ("reordered", "reordered"), ("removed", "removed"), ("truncated", "truncated"),
])
def test_an_edit_a_deletion_a_reorder_or_a_removal_fails(repo, change, kind):
    broken = {"edited": line(1) + line(2).replace('"a"', '"b"') + line(3),
              "edited_rehashed": line(1) + line(2, value="b") + line(3),
              "deleted": line(1) + line(3), "reordered": line(2) + line(1) + line(3),
              "truncated": line(1) + line(2)}.get(change)
    if broken is None:
        (repo / LOG).unlink()
    else:
        write(repo, broken)
    commit(repo, change)
    found = check(repo)
    assert len(found) == 1 and found[0].startswith(f"{LOG}: {kind}")
    assert '"value"' not in found[0] and "sha256" not in found[0]  # counts only, no content
    assert main(["--data", str(repo)]) == 1


def test_a_merge_of_main_with_mains_lines_first_passes(repo, monkeypatch, tmp_path):
    write(repo, line(1) + line(2) + line(3) + line(10, "pr"))
    commit(repo, "pr appends")
    git(repo, "checkout", "-q", "main")
    write(repo, line(1) + line(2) + line(3) + line(20, "main"))
    main_tip = commit(repo, "main appends")
    git(repo, "update-ref", "refs/remotes/origin/main", main_tip)
    git(repo, "checkout", "-q", "pr")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "merge", "-q", "main",
        "--no-commit", "-X", "theirs")
    write(repo, line(1) + line(2) + line(3) + line(20, "main") + line(10, "pr"))
    commit(repo, "merge main, main's lines first")
    pull_request(monkeypatch, tmp_path, main_tip)
    assert check(repo) == []
    write(repo, line(1) + line(2) + line(3) + line(10, "pr") + line(20, "main"))
    commit(repo, "branch's lines first")
    found = check(repo)
    assert len(found) == 1 and "reordered" in found[0]


# --- review 1: the pull request's trusted base, not a merge base ---

def test_a_stale_pull_request_cannot_drop_rows_main_added(repo, monkeypatch, tmp_path):
    branched = git(repo, "rev-parse", "HEAD")
    write(repo, line(1) + line(2) + line(3) + line(10, "pr"))
    stale = commit(repo, "pr appends, branched before main's new row")
    git(repo, "checkout", "-q", "main")
    write(repo, line(1) + line(2) + line(3) + line(20, "main"))
    main_tip = commit(repo, "main adds a row")
    git(repo, "update-ref", "refs/remotes/origin/main", main_tip)
    pull_request(monkeypatch, tmp_path, main_tip)
    # The stale head itself: it does not contain the trusted base.
    git(repo, "checkout", "-q", stale)
    with pytest.raises(BaseUnresolvedError, match="does not contain the base"):
        check(repo)
    # A merge that contains the base but drops main's row is caught against it, where a merge
    # base (the branch point) would have passed it.
    git(repo, "checkout", "-q", "-b", "merged", stale)
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "merge", "-q", main_tip,
        "--no-commit", "-X", "ours")
    write(repo, line(1) + line(2) + line(3) + line(10, "pr"))
    merged = commit(repo, "merge that drops main's row")
    found = check(repo)
    assert len(found) == 1 and found[0].startswith(LOG)
    assert problems(repo, branched, merged) == []  # what the merge base would have said


# --- review 2: the base is an explicit full SHA, never a same-named branch ---

def test_a_missing_remote_ref_never_falls_back_to_a_local_branch(repo):
    git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    git(repo, "branch", "-f", "main", "pr")  # a local "main" that is the head itself
    write(repo, line(1) + line(2))
    commit(repo, "truncate")
    with pytest.raises(BaseUnresolvedError):
        check(repo)


def test_a_planted_local_branch_named_like_the_remote_ref_is_never_the_base(repo):
    # Codex review round 2: with refs/remotes/origin/main gone, rev-parse would resolve a local
    # branch called "refs/remotes/origin/main" (refs/heads/refs/remotes/origin/main). The exact
    # ref is read with show-ref --verify, and its absence refuses.
    git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    write(repo, line(1) + line(2))
    head = commit(repo, "truncate")
    git(repo, "branch", "refs/remotes/origin/main", head)  # the planted local branch
    assert git(repo, "rev-parse", "refs/remotes/origin/main") == head  # what rev-parse says
    with pytest.raises(BaseUnresolvedError, match="is not in the checkout"):
        check(repo)


def test_a_base_that_is_the_head_or_not_a_full_sha_refuses(repo, monkeypatch, tmp_path):
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(BaseUnresolvedError, match="vacuous"):
        resolve_base(repo, head, head)
    with pytest.raises(BaseUnresolvedError, match="full lowercase"):
        resolve_base(repo, head, "main")
    pull_request(monkeypatch, tmp_path, "not-a-sha")
    with pytest.raises(BaseUnresolvedError, match="no base SHA"):
        check(repo)


# --- review 3: raw git objects; a symlink or a mode change fails ---

@pytest.mark.parametrize("plant", ["log_link", "parent_link", "mode"])
def test_a_symlink_or_a_mode_change_fails(repo, plant):
    if plant == "log_link":
        (repo / LOG).unlink()
        (repo / "elsewhere.jsonl").write_text(line(1) + line(2) + line(3) + line(4))
        os.symlink("../elsewhere.jsonl", repo / LOG)
    elif plant == "parent_link":
        git(repo, "mv", "verification", "real-verification")
        os.symlink("real-verification", repo / "verification")
    else:
        os.chmod(repo / LOG, 0o755)
    commit(repo, plant)
    found = check(repo)
    assert found, plant
    assert any(("symlink" in f) or ("mode" in f) or ("removed" in f) for f in found)


def test_the_working_tree_must_hold_the_heads_logs(repo):
    write(repo, line(1) + line(2) + line(3) + line(4))
    commit(repo, "append")
    write(repo, line(1) + line(2))  # an uncommitted edit the build would read
    found = check(repo)
    assert found == [f"{LOG}: the working tree differs from the head"]
    write(repo, line(1) + line(2) + line(3) + line(4))
    (repo / QUEUE).unlink()
    (repo / "q.jsonl").write_text(line(1))
    os.symlink("../../q.jsonl", repo / QUEUE)
    assert check(repo) == [f"{QUEUE}: a symlink in the working tree"]


# --- review 4: fail closed; only an explicit local flag skips, and says so ---

def test_a_run_that_cannot_show_its_base_fails(tmp_path, monkeypatch, capsys):
    root = tmp_path / "local"
    root.mkdir()
    git(root, "init", "-q", "-b", "work")
    write(root, line(1))
    commit(root, "only")
    with pytest.raises(ValueError, match="append-only guard|refs/remotes"):
        append_only(root)  # local, no flag: fails closed
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(ValueError):
        append_only(root)  # CI, whatever the repository
    with pytest.raises(ValueError, match="local checkout only"):
        append_only(root, skip=True)  # the flag refuses inside GitHub Actions
    monkeypatch.delenv("GITHUB_ACTIONS")
    append_only(root, skip=True)
    assert "skipped" in capsys.readouterr().err
