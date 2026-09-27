"""Partition pytest files into deterministic, file-level CI shards."""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
from pathlib import Path

DEFAULT_SHARD_COUNT = 4


def test_files(root: Path) -> list[Path]:
    """Return every pytest module in the suite in stable path order."""
    return sorted(root.glob("tests/**/test_*.py"))


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
