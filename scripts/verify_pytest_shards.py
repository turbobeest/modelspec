"""Verify that shard collection artifacts exactly partition full collection."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path


def node_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if "::" in line and not line.startswith("=")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("full_collection", type=Path)
    parser.add_argument("shard_collections", nargs="+", type=Path)
    args = parser.parse_args()
    expected = node_ids(args.full_collection)
    actual = [node_id for path in args.shard_collections for node_id in node_ids(path)]
    duplicates = sorted(node_id for node_id, count in Counter(actual).items() if count > 1)
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    if duplicates or missing or unexpected or len(actual) != len(expected):
        print(f"full={len(expected)} shard_total={len(actual)} duplicates={len(duplicates)} "
              f"missing={len(missing)} unexpected={len(unexpected)}")
        for label, values in (("duplicate", duplicates), ("missing", missing),
                              ("unexpected", unexpected)):
            for value in values[:20]:
                print(f"{label}: {value}")
        return 1
    print(f"verified {len(expected)} node ids across {len(args.shard_collections)} shards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
