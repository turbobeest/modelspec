"""MODEL-491: every evidence log in the private data is append-only against its base.

The base's bytes must be a byte prefix of the head's: an edited line (its hash recomputed or
not), a deleted line, a reordered pair and a removed log each fail; a pure append, a new log and
a merge of main that puts main's lines first pass. Every repository here is synthetic.
"""

from __future__ import annotations

import hashlib
import json
import subprocess

import pytest
from scripts.append_only_guard import base_revision, is_log, main, problems
from scripts.prepare_data_writer import append_only

LOG = "verification/cited-attempts.jsonl"


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
    root = tmp_path / "data"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, line(1) + line(2) + line(3))
    write(root, line(1), "verification/queue/events.jsonl")
    commit(root, "base")
    git(root, "checkout", "-q", "-b", "pr")
    return root


def test_the_rule_covers_every_evidence_log():
    for path in ("verification/log.jsonl", "verification/queue/events.jsonl", LOG,
                 "verification/quarantine-clearings.jsonl", "verification/owner-rulings.jsonl",
                 "reports/evidence-reread/ruled-reopenings.jsonl"):
        assert is_log(path), path
    for path in ("models/a.md", "verification/README.md", "reports/evidence-reread/x/y.jsonl",
                 "reports/data-trust/2026.json"):
        assert not is_log(path), path


def test_a_pure_append_and_a_new_log_pass(repo):
    write(repo, line(1) + line(2) + line(3) + line(4))
    write(repo, line(9), "verification/new-log.jsonl")
    base = base_revision(repo)
    assert problems(repo, base) == []
    head = commit(repo, "append")
    assert problems(repo, base, head) == []


@pytest.mark.parametrize("change,kind", [
    ("edited", "edited"),
    ("edited_rehashed", "edited"),
    ("deleted", "deleted lines"),
    ("reordered", "reordered"),
    ("removed", "removed"),
    ("truncated", "truncated"),
])
def test_an_edit_a_deletion_a_reorder_or_a_removal_fails(repo, change, kind):
    if change == "edited":  # a value changed, the stated hash left as it was
        broken = line(1) + line(2).replace('"a"', '"b"') + line(3)
    elif change == "edited_rehashed":  # a value changed and its hash recomputed to match
        broken = line(1) + line(2, value="b") + line(3)
    elif change == "deleted":
        broken = line(1) + line(3)
    elif change == "reordered":
        broken = line(2) + line(1) + line(3)
    elif change == "truncated":
        broken = line(1) + line(2)
    if change == "removed":
        (repo / LOG).unlink()
    else:
        write(repo, broken)
    base = base_revision(repo)
    found = problems(repo, base)
    assert len(found) == 1 and found[0].startswith(f"{LOG}: {kind}")
    assert '"value"' not in found[0] and "sha256" not in found[0]  # counts only, no content
    assert main(["--data", str(repo)]) == 1
    with pytest.raises(ValueError, match="append-only guard"):
        append_only(repo)


def test_a_merge_of_main_with_mains_lines_first_passes(repo):
    write(repo, line(1) + line(2) + line(3) + line(10, "pr"))
    commit(repo, "pr appends")
    git(repo, "checkout", "-q", "main")
    write(repo, line(1) + line(2) + line(3) + line(20, "main"))
    commit(repo, "main appends")
    git(repo, "checkout", "-q", "pr")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "merge", "-q", "main",
        "--no-commit", "-X", "theirs")
    write(repo, line(1) + line(2) + line(3) + line(20, "main") + line(10, "pr"))
    head = commit(repo, "merge main, main's lines first")
    assert problems(repo, base_revision(repo), head) == []
    # The same merge with this branch's lines first breaks the rule.
    write(repo, line(1) + line(2) + line(3) + line(10, "pr") + line(20, "main"))
    head = commit(repo, "branch's lines first")
    found = problems(repo, base_revision(repo), head)
    assert len(found) == 1 and "reordered" in found[0]


def test_outside_the_data_ci_a_checkout_without_a_base_is_left_alone(tmp_path, monkeypatch):
    root = tmp_path / "local"
    root.mkdir()
    git(root, "init", "-q", "-b", "work")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    append_only(root)  # no base branch to break: nothing to check
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_REPOSITORY", "turbobeest/modelspec-data")
    with pytest.raises(ValueError, match="no base revision"):
        append_only(root)
