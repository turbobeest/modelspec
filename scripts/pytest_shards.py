"""Partition pytest files into deterministic, file-level CI shards."""

from __future__ import annotations

import argparse
import fnmatch
import os
import shlex
import tomllib
from collections.abc import Iterable, Sequence
from pathlib import Path

DEFAULT_SHARD_COUNT = 4
DEFAULT_PYTHON_FILES = ("test_*.py", "*_test.py")
DEFAULT_NORECURSEDIRS = (
    "*.egg",
    ".*",
    "_darcs",
    "build",
    "CVS",
    "dist",
    "node_modules",
    "venv",
    "{arch}",
)


def _option_values(value: object, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    if isinstance(value, str):
        return tuple(shlex.split(value))
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise TypeError("pytest discovery options must be strings or lists of strings")


def _pytest_options(root: Path) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    pyproject = root / "pyproject.toml"
    options: dict[str, object] = {}
    if pyproject.is_file():
        document = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        options = document.get("tool", {}).get("pytest", {}).get("ini_options", {})
    python_files = _option_values(options.get("python_files"), DEFAULT_PYTHON_FILES)
    testpaths = _option_values(options.get("testpaths"), (".",))
    norecursedirs = _option_values(options.get("norecursedirs"), DEFAULT_NORECURSEDIRS)
    return python_files, testpaths, norecursedirs


def _excluded_directory(path: Path, root: Path, patterns: tuple[str, ...]) -> bool:
    if path == root:
        return False
    relative = path.relative_to(root).as_posix()
    return (path / "pyvenv.cfg").is_file() or any(
        fnmatch.fnmatchcase(path.name, pattern) or fnmatch.fnmatchcase(relative, pattern)
        for pattern in patterns
    )


def _matches_python_file(path: Path, root: Path, patterns: tuple[str, ...]) -> bool:
    relative = path.relative_to(root).as_posix()
    return any(
        fnmatch.fnmatchcase(relative if "/" in pattern else path.name, pattern)
        for pattern in patterns
    )


def test_files(root: Path) -> list[Path]:
    """Return every pytest module in the suite in stable path order."""
    python_files, testpaths, norecursedirs = _pytest_options(root)
    discovered: set[Path] = set()
    for testpath in testpaths:
        start = root / testpath
        if start.is_file():
            if _matches_python_file(start, root, python_files):
                discovered.add(start)
            continue
        if not start.is_dir() or _excluded_directory(start, root, norecursedirs):
            continue
        for directory, names, filenames in os.walk(start):
            current = Path(directory)
            names[:] = [
                name for name in names
                if not _excluded_directory(current / name, root, norecursedirs)
            ]
            discovered.update(
                current / filename
                for filename in filenames
                if _matches_python_file(current / filename, root, python_files)
            )
    return sorted(discovered)


def partition_files(files: Iterable[Path], shard_count: int) -> list[list[Path]]:
    """Greedily balance whole files by byte size, with stable tie-breaking."""
    if shard_count < 1:
        raise ValueError("shard_count must be positive")
    shards: list[list[Path]] = [[] for _ in range(shard_count)]
    totals = [0] * shard_count
    weighted = sorted(files, key=lambda path: (-path.stat().st_size, path.as_posix()))
    for path in weighted:
        shard_index = min(range(shard_count), key=lambda index: (totals[index], index))
        shards[shard_index].append(path)
        totals[shard_index] += path.stat().st_size
    for shard in shards:
        shard.sort()
    return shards


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard-count", type=int, default=DEFAULT_SHARD_COUNT)
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--summary", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    shards = partition_files(test_files(root), args.shard_count)
    if args.summary:
        total_bytes = sum(path.stat().st_size for shard in shards for path in shard)
        for index, shard in enumerate(shards, start=1):
            shard_bytes = sum(path.stat().st_size for path in shard)
            share = 100 * shard_bytes / total_bytes if total_bytes else 0
            print(f"shard {index}/{args.shard_count}: {len(shard)} files, "
                  f"{shard_bytes} bytes ({share:.1f}% estimated runtime)")
        return 0
    if args.shard_index is None:
        _parser().error("--shard-index is required unless --summary is used")
    if not 0 <= args.shard_index < args.shard_count:
        _parser().error("--shard-index must be between 0 and shard-count - 1")
    for path in shards[args.shard_index]:
        print(path.relative_to(root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
