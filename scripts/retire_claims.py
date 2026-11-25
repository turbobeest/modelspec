"""Retire filed claims whose data row no longer exists (MODEL-557); dry-run unless --write.

A claim in ``verification/queue/events.jsonl`` describes a card fact, an offering fact
or an evidence row. When that row is gone (a removed offering, an evidence id a card
replaced), the claim still stands as the latest filed claim for its target, so the
nightly's data-fidelity layer keeps drawing it. This script appends one ``retired``
event per named target (``Queue.retire``). It edits no line and writes nothing else.

Each named target must have a filed claim and must have no data row in the checkout
(``decision.verify.data_row_targets``; ``Queue.retire`` enforces it again): any target that fails either check refuses the
whole run, and nothing is written. Output names targets, counts and fixed codes only.

Usage:
  retire_claims.py --root DATA [--target fact:<id> | evidence:<id>]... [--targets-file F]
                   [--reason no_data_row] [--write]
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from decision.verify import RETIRE_REASONS, Queue, target_ref


def data_rows(root: Path) -> set[tuple[str, str]]:
    """Every (kind, id) a card fact, an offering fact or an evidence row holds."""
    from decision import verify

    return verify.data_row_targets(root)


def plan(root: Path, refs: list[str]) -> tuple[list, list[str]]:
    """The targets to retire, and the problems that refuse the run."""
    targets, problems, seen = [], [], set()
    for ref in refs:
        try:
            target = target_ref(ref)
        except ValueError:
            problems.append(f"{ref!r}: not fact:<id> or evidence:<id>")
            continue
        key = (target.kind, target.id)
        if key in seen:
            problems.append(f"{ref}: named twice")
            continue
        seen.add(key)
        targets.append(target)
    filed = Queue(root / "verification").filed()
    rows = data_rows(root)
    for target in targets:
        key = (target.kind, target.id)
        if key not in filed:
            problems.append(f"{target.kind}:{target.id}: no filed claim to retire")
        if key in rows:
            problems.append(f"{target.kind}:{target.id}: a data row still holds it")
    return targets, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True, help="data checkout root")
    parser.add_argument("--target", action="append", default=[],
                        help="fact:<id> or evidence:<id>; repeatable")
    parser.add_argument("--targets-file", type=Path,
                        help="one fact:<id> or evidence:<id> per line")
    parser.add_argument("--reason", default="no_data_row", choices=sorted(RETIRE_REASONS))
    parser.add_argument("--write", action="store_true", help="append the retired events")
    args = parser.parse_args(argv)
    refs = list(args.target)
    if args.targets_file:
        refs += [line.strip() for line in args.targets_file.read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.lstrip().startswith("#")]
    if not refs:
        print("no targets named", file=sys.stderr)
        return 2
    targets, problems = plan(args.root, refs)
    for problem in problems:
        print(f"refused: {problem}", file=sys.stderr)
    if problems:
        print(f"{len(problems)} problems; nothing written", file=sys.stderr)
        return 1
    for target in targets:
        print(f"retire {target.kind}:{target.id} ({args.reason})")
    if not args.write:
        print(f"dry run: {len(targets)} targets would be retired")
        return 0
    # Queue.retire checks the same invariants again, so the write cannot bypass them.
    Queue(args.root / "verification").retire(targets, at=datetime.now(UTC), reason=args.reason,
                                             root=args.root)
    print(f"retired {len(targets)} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
