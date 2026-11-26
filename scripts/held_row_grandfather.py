"""The held-row grandfather list (MODEL-552 follow-up): write it, or check that it only shrinks.

``python -m scripts.held_row_grandfather write --data-dir <data checkout>`` builds the snapshot
from the data with the check off, and writes ``verification/held-row-grandfather.json`` listing the
failed verdicts on row ids the data no longer has (``held_row_missing``): hashes and counts, no
values. Run once, to seed the list, and review it in the PR that adds it.

``python -m scripts.held_row_grandfather check --data-dir <data checkout> [--base origin/main]``
fails (exit 1) when the list at HEAD names a hash the list at the merge base with ``--base`` does
not: the list may only shrink. A list that is absent at the merge base is being seeded.

The output is counts only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from decision.quarantine_clearing import (
    GRANDFATHER_FILE,
    grandfather_added,
    grandfather_document,
    parse_grandfather,
    read_grandfather,
)


def missing_hashes(root: Path) -> dict[str, list[str]]:
    """The hashes of the failed verdicts on vanished row ids, by kind, with no grandfather list."""
    from decision import snapshot
    from decision.registry import default

    inputs = replace(snapshot.collect_repo(root), held_row_grandfather={}, check_held_rows=False)
    compiler = snapshot._compile(inputs, default(), None, datetime.now(UTC).date(), False, None)
    found: dict[str, list[str]] = {}
    for kind, sha in compiler.missing_holds():
        found.setdefault(kind, []).append(sha)
    return found


def _base_list(root: Path, base: str) -> dict | None:
    merge = subprocess.run(["git", "-C", str(root), "merge-base", "HEAD", base],
                           capture_output=True, text=True, check=True).stdout.strip()
    shown = subprocess.run(["git", "-C", str(root), "show", f"{merge}:{GRANDFATHER_FILE}"],
                           capture_output=True, text=True)
    if shown.returncode != 0:
        return None
    return parse_grandfather(json.loads(shown.stdout))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=("write", "check"))
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--base", default="origin/main")
    args = ap.parse_args(argv)
    root = args.data_dir.resolve()
    if args.command == "write":
        document = grandfather_document(missing_hashes(root))
        (root / GRANDFATHER_FILE).write_text(json.dumps(document, indent=1, sort_keys=True) + "\n",
                                             encoding="utf-8")
        print(json.dumps({"written": GRANDFATHER_FILE, "counts": document["counts"]}))
        return 0
    head = read_grandfather(root / GRANDFATHER_FILE)
    added = grandfather_added(head, _base_list(root, args.base))
    print(json.dumps({"counts": {k: len(v) for k, v in head.items()}, "added": added}))
    return 1 if added else 0


if __name__ == "__main__":
    sys.exit(main())
