"""Reject changes to published blog revisions and existing correction entries."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any

import yaml


class _InvalidHistoryError(ValueError):
    pass


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"Cannot read blog base history: {detail}")
    return result.stdout


def _working_bytes(root: Path, relative: str) -> bytes:
    path = root / relative
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise _InvalidHistoryError(f"{relative}: published history cannot use symbolic links")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise _InvalidHistoryError(f"{relative}: missing or unreadable published history") from exc


def _yaml(data: bytes, path: str, expected: type) -> Any:
    try:
        value = yaml.safe_load(data)
    except (UnicodeError, yaml.YAMLError) as exc:
        raise _InvalidHistoryError(f"{path}: invalid YAML") from exc
    if not isinstance(value, expected):
        raise _InvalidHistoryError(f"{path}: expected a YAML {expected.__name__}")
    return value


def _identical(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _identical(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(_identical(a, b) for a, b in zip(left, right))
    return left == right


def _published_rows(metadata: dict, path: str) -> dict[int, dict]:
    revisions = metadata.get("revisions")
    if not isinstance(revisions, list):
        raise _InvalidHistoryError(f"{path}: expected a revisions list")
    result = {}
    seen = set()
    for row in revisions:
        if not isinstance(row, dict) or type(row.get("revision")) is not int or row["revision"] < 1:
            raise _InvalidHistoryError(f"{path}: invalid revision metadata")
        number = row["revision"]
        if number in seen:
            raise _InvalidHistoryError(f"{path}: duplicate revision {number}")
        seen.add(number)
        if row.get("published") is not None:
            result[number] = row
    return result


def check_append_only(root: Path, *, base: str = "origin/main") -> list[str]:
    """Compare committed base history with the working tree, including unstaged edits.

    Return every violation. An unavailable git base raises ValueError so the
    caller cannot mistake a skipped check for a successful one.
    """
    root = Path(root).resolve()
    base_tree = (
        _git(root, "rev-parse", "--verify", "--end-of-options", f"{base}^{{tree}}").decode().strip()
    )
    entries = _git(root, "ls-tree", "-r", "-z", base_tree, "--", "blog/posts/")
    blobs = {}
    for entry in entries.split(b"\0"):
        if entry:
            attributes, path = entry.split(b"\t", 1)
            _mode, kind, object_id = attributes.split()
            if kind == b"blob":
                blobs[path.decode("utf-8")] = object_id.decode("ascii")

    def base_bytes(path: str) -> bytes:
        return _git(root, "cat-file", "blob", blobs[path])

    problems = []
    for path in sorted(blobs):
        if not path.endswith("/post.yaml") or len(Path(path).parts) != 4:
            continue
        try:
            original = _yaml(base_bytes(path), path, dict)
            frozen = _published_rows(original, path)
            if not frozen:
                if original.get("status") == "published":
                    raise _InvalidHistoryError(f"{path}: published post has no published revision")
                continue
            current = _yaml(_working_bytes(root, path), path, dict)
            current_rows = _published_rows(current, path)
            commentary = f"{Path(path).parent}/commentary.md"
            if commentary in blobs:
                if _working_bytes(root, commentary) != base_bytes(commentary):
                    problems.append(f"{commentary}: published commentary cannot change")
            elif (root / commentary).exists():
                problems.append(f"{commentary}: cannot add commentary to a published post")
            for field in ("schema_version", "model", "title", "status", "early_access"):
                if not _identical(current.get(field), original.get(field)):
                    problems.append(f"{path}: published {field} cannot change")
            for number, original_row in frozen.items():
                if not _identical(current_rows.get(number), original_row):
                    problems.append(
                        f"{path}: published revision {number} metadata cannot change or be removed"
                    )
                directory = f"{Path(path).parent}/r{number}/"
                original_files = {name for name in blobs if name.startswith(directory)}
                for name in sorted(original_files):
                    try:
                        if _working_bytes(root, name) != base_bytes(name):
                            problems.append(f"{name}: published revision file cannot change")
                    except _InvalidHistoryError as exc:
                        problems.append(str(exc))
                current_directory = root / directory
                if current_directory.is_symlink():
                    problems.append(
                        f"{directory}: published revision directory cannot use symbolic links"
                    )
                else:
                    for file in sorted(current_directory.rglob("*")):
                        if file.is_symlink() or file.is_file():
                            name = file.relative_to(root).as_posix()
                            if name not in original_files:
                                problems.append(
                                    f"{name}: cannot add a file to a published revision"
                                )
        except _InvalidHistoryError as exc:
            problems.append(str(exc))

    for path in sorted(blobs):
        if not path.endswith("/corrections.yaml") or len(Path(path).parts) != 4:
            continue
        try:
            original = _yaml(base_bytes(path), path, list)
            current = _yaml(_working_bytes(root, path), path, list)
            if len(current) < len(original) or not _identical(current[: len(original)], original):
                problems.append(
                    f"{path}: existing corrections must remain an identical prefix; "
                    "only append entries"
                )
        except _InvalidHistoryError as exc:
            problems.append(str(exc))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base", default="origin/main", help="git revision containing published history"
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    args = parser.parse_args(argv)
    try:
        problems = check_append_only(args.root, base=args.base)
    except ValueError as exc:
        print(str(exc))
        return 1
    if problems:
        print("\n".join(problems))
        return 1
    print(f"Blog publication history is append-only against {args.base}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
