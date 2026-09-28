"""Partition pytest files into deterministic, file-level CI shards."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shlex
import statistics
import tomllib
from collections.abc import Iterable, Sequence
from pathlib import Path

DEFAULT_SHARD_COUNT = 4
DEFAULT_DURATIONS_PATH = Path("tests/shard_durations.json")
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
                name
                for name in names
                if not _excluded_directory(current / name, root, norecursedirs)
            ]
            discovered.update(
                current / filename
                for filename in filenames
                if _matches_python_file(current / filename, root, python_files)
            )
    return sorted(discovered)


def load_durations(path: Path) -> dict[str, float]:
    """Load measured test-file durations from a JSON object."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not all(
        isinstance(key, str)
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value >= 0
        for key, value in document.items()
    ):
        raise ValueError(f"{path} must map test file paths to non-negative seconds")
    return {key: float(value) for key, value in document.items()}


def file_weights(
    files: Iterable[Path], root: Path, durations: dict[str, float]
) -> dict[Path, float]:
    """Return measured durations, estimating any files absent from the data."""
    paths = list(files)
    known = {
        path: durations[path.relative_to(root).as_posix()]
        for path in paths
        if path.relative_to(root).as_posix() in durations
    }
    median = statistics.median(known.values()) if known else 1.0
    known_bytes = sum(path.stat().st_size for path in known)
    known_seconds = sum(known.values())
    seconds_per_byte = known_seconds / known_bytes if known_bytes else None
    return {
        path: known.get(
            path,
            path.stat().st_size * seconds_per_byte if seconds_per_byte else median,
        )
        for path in paths
    }


def partition_files(
    files: Iterable[Path],
    shard_count: int,
    *,
    root: Path | None = None,
    durations: dict[str, float] | None = None,
) -> list[list[Path]]:
    """Use longest-processing-time packing with stable tie-breaking."""
    if shard_count < 1:
        raise ValueError("shard_count must be positive")
    paths = list(files)
    if root is None:
        common = Path(os.path.commonpath(paths)) if paths else Path.cwd()
        root = common if common.is_dir() else common.parent
    weights = file_weights(paths, root, durations or {})
    shards: list[list[Path]] = [[] for _ in range(shard_count)]
    totals = [0.0] * shard_count
    weighted = sorted(paths, key=lambda path: (-weights[path], path.as_posix()))
    for path in weighted:
        shard_index = min(range(shard_count), key=lambda index: (totals[index], index))
        shards[shard_index].append(path)
        totals[shard_index] += weights[path]
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
    files = test_files(root)
    durations = load_durations(root / DEFAULT_DURATIONS_PATH)
    weights = file_weights(files, root, durations)
    shards = partition_files(files, args.shard_count, root=root, durations=durations)
    if args.summary:
        for index, shard in enumerate(shards, start=1):
            shard_seconds = sum(weights[path] for path in shard)
            print(
                f"shard {index}/{args.shard_count}: {len(shard)} files, "
                f"{shard_seconds:.3f} predicted seconds"
            )
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
