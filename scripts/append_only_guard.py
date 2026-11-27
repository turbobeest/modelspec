"""Every evidence log in the private data is append-only (MODEL-491, orchestrator 2026-11-27).

A log's bytes at the trusted base must be a byte prefix of its bytes at the head: no line edited
(its hash recomputed or not), deleted or reordered, no log removed, its file mode unchanged, and
no symlink at a log path or in any directory above it. A pure append passes, and so does a merge
of main that puts main's lines first. The logs are every JSONL file under ``verification/`` (the
verification log, the queue, the rule-15 attempt log, the clearing, ruling, supersession and
re-read logs) and under ``reports/evidence-reread/``.

Both sides are read as raw git objects (``git ls-tree`` and ``git cat-file``), never through the
filesystem, and the working tree must hold exactly the head's logs. The base is an explicit full
commit SHA, never a branch name (``resolve_base``):

- ``--base`` or ``MODELSPEC_APPEND_ONLY_BASE``;
- in a pull request, the event's ``pull_request.base.sha`` (the trusted base, not a merge base:
  a stale branch cannot drop rows main added after it branched);
- on a push, the event's ``before``;
- otherwise the commit ``refs/remotes/origin/<default branch>`` names, or, when that is the
  head itself, the head's first parent.

The head must contain the base, and the base must not be the head: either refuses. The data
workflows run it at the pin through ``scripts/prepare_data_writer.py``; it also runs by hand:

    python scripts/append_only_guard.py --data <private checkout> [--base SHA] [--head SHA]

Output names a log, what broke and counts, never a line's content.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

#: The logs the rule covers: directory prefix, and whether files in subdirectories count.
LOG_ROOTS = (("verification/", True), ("reports/evidence-reread/", False))
NEWLINE = b"\n"
_SHA = re.compile(r"[0-9a-f]{40}")
SYMLINK = "120000"


class BaseUnresolvedError(ValueError):
    """The trusted base cannot be shown: the check fails closed."""


def is_log(path: str) -> bool:
    """Whether a repository path is one of the append-only evidence logs."""
    if not path.endswith(".jsonl"):
        return False
    for prefix, nested in LOG_ROOTS:
        if path.startswith(prefix) and (nested or "/" not in path[len(prefix):]):
            return True
    return False


def _git(data: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(data), *args], check=True,
                          capture_output=True).stdout


def _commit(data: Path, rev: str) -> str:
    """The full SHA of a commit named by a full SHA or an explicit ``refs/...`` name."""
    try:
        sha = _git(data, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}").decode().strip()
    except subprocess.CalledProcessError:
        raise BaseUnresolvedError(f"{rev!r} is not a commit of the checkout") from None
    if not _SHA.fullmatch(sha):
        raise BaseUnresolvedError("the base is not one full commit SHA")
    return sha


def _event() -> dict:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise BaseUnresolvedError("the event payload cannot be read") from None


def resolve_base(data: Path, head: str, explicit: str | None = None) -> str:
    """The trusted base commit, as a full SHA, or ``BaseUnresolvedError``. See the module text."""
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    explicit = explicit or os.environ.get("MODELSPEC_APPEND_ONLY_BASE")
    if explicit:
        if not _SHA.fullmatch(explicit):
            raise BaseUnresolvedError("an explicit base must be one full lowercase commit SHA")
        base = _commit(data, explicit)
    elif event_name in ("pull_request", "pull_request_target"):
        sha = str(((_event().get("pull_request") or {}).get("base") or {}).get("sha") or "")
        if not _SHA.fullmatch(sha):
            raise BaseUnresolvedError("the pull request event names no base SHA")
        base = _commit(data, sha)
    elif event_name == "push":
        sha = str(_event().get("before") or "")
        if not _SHA.fullmatch(sha) or set(sha) == {"0"}:
            raise BaseUnresolvedError("the push event names no earlier commit")
        base = _commit(data, sha)
    else:
        branch = os.environ.get("GITHUB_BASE_REF") or str(
            (_event().get("repository") or {}).get("default_branch") or "main")
        base = _commit(data, f"refs/remotes/origin/{branch}")
        if base == head:
            try:
                base = _commit(data, f"{head}^1")
            except BaseUnresolvedError:
                raise BaseUnresolvedError(
                    "the head has no earlier commit to compare with") from None
    if base == head:
        raise BaseUnresolvedError("the base is the head itself; the check would be vacuous")
    try:
        _git(data, "merge-base", "--is-ancestor", base, head)
    except subprocess.CalledProcessError:
        raise BaseUnresolvedError("the checked-out head does not contain the base commit") from None
    return base


def _tree(data: Path, rev: str) -> dict[str, tuple[str, str]]:
    """Path -> (mode, object id) for every entry of the commit's tree, recursively."""
    out: dict[str, tuple[str, str]] = {}
    raw = _git(data, "ls-tree", "-r", "-z", "--full-tree", rev).split(b"\0")
    for entry in raw:
        if not entry:
            continue
        meta, _, path = entry.partition(b"\t")
        mode, _kind, oid = meta.decode().split(" ")
        out[path.decode()] = (mode, oid)
    return out


def _symlinked(path: str, tree: dict[str, tuple[str, str]]) -> bool:
    """Whether the log path, or any directory above it, is a symlink in the tree."""
    parts = path.split("/")
    return any(tree.get("/".join(parts[:n]), ("", ""))[0] == SYMLINK
               for n in range(1, len(parts) + 1))


def _blob(data: Path, oid: str) -> bytes:
    return _git(data, "cat-file", "blob", oid)


def _kind(old: bytes, new: bytes) -> tuple[str, int]:
    """What broke the prefix, and how many of the base's lines are not in place."""
    before, after = old.splitlines(keepends=True), new.splitlines(keepends=True)
    moved = sum(1 for a, b in zip(before, after) if a != b) + max(0, len(before) - len(after))
    if not Counter(before) - Counter(after):
        return "reordered", moved  # every base line is still there, not in its place
    if old.startswith(new):
        return "truncated", moved
    if len(after) < len(before):
        return "deleted lines", moved
    return "edited", moved


def problems(data: Path, base: str, head: str) -> list[str]:
    """Every append-only break between two commits, one line per log: its path, what broke and
    counts. Raw git objects on both sides; a symlink or a mode change is a break."""
    old_tree, new_tree = _tree(data, base), _tree(data, head)
    out: list[str] = []
    for path in sorted(p for p in set(old_tree) | set(new_tree) if is_log(p)):
        if _symlinked(path, new_tree) or (path in old_tree and old_tree[path][0] == SYMLINK):
            out.append(f"{path}: a symlink at the log or a directory above it")
            continue
        if path not in old_tree:
            continue  # a new log: nothing to keep
        old_mode, old_oid = old_tree[path]
        old = _blob(data, old_oid)
        lines = old.count(NEWLINE)
        if path not in new_tree:
            out.append(f"{path}: removed ({lines} base line(s))")
            continue
        new_mode, new_oid = new_tree[path]
        if new_mode != old_mode:
            out.append(f"{path}: file mode changed")
            continue
        new = _blob(data, new_oid)
        if not new.startswith(old):
            kind, moved = _kind(old, new)
            out.append(f"{path}: {kind}; {moved} of {lines} base line(s) not in place")
    # A symlink planted above the logs in the head (a directory turned into a link) hides them.
    for path in sorted(p for p, (mode, _o) in new_tree.items() if mode == SYMLINK):
        if any(is_log(o) and (o == path or o.startswith(path + "/")) for o in old_tree):
            out.append(f"{path}: a symlink at the log or a directory above it")
    return sorted(set(out))


def worktree_problems(data: Path, head: str) -> list[str]:
    """The working tree must hold exactly the head's logs, with no symlink on the way: the build
    reads the files, so a local edit or link would bypass the commit check."""
    tree = _tree(data, head)
    out: list[str] = []
    for path, (_mode, oid) in sorted(tree.items()):
        if not is_log(path):
            continue
        target = data
        linked = False
        for part in path.split("/"):
            target = target / part
            if target.is_symlink():
                linked = True
                break
        if linked:
            out.append(f"{path}: a symlink in the working tree")
        elif not target.is_file() or target.read_bytes() != _blob(data, oid):
            out.append(f"{path}: the working tree differs from the head")
    return out


def check(data: Path, base: str | None = None, head: str | None = None) -> list[str]:
    """Resolve the base, then every break: commits and working tree. ``BaseUnresolvedError`` when
    the base cannot be shown."""
    head_sha = _commit(data, head or "HEAD")
    base_sha = resolve_base(data, head_sha, base)
    return problems(data, base_sha, head_sha) + (worktree_problems(data, head_sha)
                                                 if head is None else [])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--base", help="the trusted base commit, one full SHA")
    parser.add_argument("--head", help="the head commit (default: HEAD and the working tree)")
    args = parser.parse_args(argv)
    try:
        found = check(args.data, args.base, args.head)
    except BaseUnresolvedError as error:
        print(f"append-only guard: {error}", file=sys.stderr)
        return 2
    for line in found:
        print(f"append-only guard: {line}", file=sys.stderr)
    print(f"append-only guard: {len(found)} log(s) broke the append-only rule")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
