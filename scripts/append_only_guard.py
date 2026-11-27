"""Every evidence log in the private data is append-only (MODEL-491, orchestrator 2026-11-27).

A log's bytes at the pull request's base must be a byte prefix of its bytes at the head: no line
edited (its hash recomputed or not), deleted or reordered, and the file never removed. A pure
append passes, and so does a merge of main that puts main's lines first. The logs are every JSONL
file under ``verification/`` (the verification log, the queue, the rule-15 attempt log, the
clearing, ruling, supersession and re-read logs) and under ``reports/evidence-reread/``.

The base is the merge base of the head with the base branch (``GITHUB_BASE_REF`` in a pull
request, else ``main``), taken from the private checkout's own git history. The data workflows
run it at the pin through ``scripts/prepare_data_writer.py``; it also runs by hand:

    python scripts/append_only_guard.py --data <private checkout> [--base REV] [--head REV]

Output names a log, what broke and counts, never a line's content.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

#: The logs the rule covers: directory prefix, and whether files in subdirectories count.
LOG_ROOTS = (("verification/", True), ("reports/evidence-reread/", False))


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


def base_revision(data: Path, branch: str | None = None) -> str | None:
    """The merge base of HEAD with the base branch's remote ref, or ``None`` when it is absent."""
    branch = branch or os.environ.get("GITHUB_BASE_REF") or "main"
    for ref in (f"refs/remotes/origin/{branch}", f"refs/heads/{branch}"):
        try:
            _git(data, "rev-parse", "--verify", "--quiet", ref)
        except subprocess.CalledProcessError:
            continue
        try:
            return _git(data, "merge-base", "HEAD", ref).decode().strip() or None
        except subprocess.CalledProcessError:
            return None
    return None


def _logs_at(data: Path, rev: str) -> list[str]:
    names = _git(data, "ls-tree", "-r", "--name-only", "-z", rev).decode().split("\0")
    return sorted(n for n in names if n and is_log(n))


NEWLINE = b"\n"


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


def problems(data: Path, base: str, head: str | None = None) -> list[str]:
    """Every append-only break between ``base`` and ``head`` (the working tree when ``None``),
    one line per log: its path, what broke and counts."""
    out: list[str] = []
    for path in _logs_at(data, base):
        old = _git(data, "show", f"{base}:{path}")
        if head is None:
            target = data / path
            new = target.read_bytes() if target.is_file() else None
        else:
            try:
                new = _git(data, "show", f"{head}:{path}")
            except subprocess.CalledProcessError:
                new = None
        lines = old.count(NEWLINE)
        if new is None:
            out.append(f"{path}: removed ({lines} base line(s))")
        elif not new.startswith(old):
            kind, moved = _kind(old, new)
            out.append(f"{path}: {kind}; {moved} of {lines} base line(s) not in place")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--base", help="the base revision (default: the merge base with main)")
    parser.add_argument("--head", help="the head revision (default: the working tree)")
    args = parser.parse_args(argv)
    base = args.base or base_revision(args.data)
    if base is None:
        print("append-only guard: no base revision to compare with", file=sys.stderr)
        return 2
    found = problems(args.data, base, args.head)
    for line in found:
        print(f"append-only guard: {line}", file=sys.stderr)
    print(f"append-only guard: {len(found)} log(s) broke the append-only rule")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
