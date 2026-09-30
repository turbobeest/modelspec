"""Copy the stored feedback out of Workers KV into one JSON Lines file (MODEL-221).

Run by whoever holds the Cloudflare credentials, on their own machine, never in
a GitHub workflow: the output is private feedback text. The output path is
refused if it is inside this repository.

    python scripts/feedback/export.py --namespace-id <FEEDBACK id> \\
        --out ~/feedback/2026-10-05.jsonl

It lists `feedback/v1/record/` (the record names hold a day and a hash, never
a receipt or an address), reads each record, and checks it is exactly a stored
record before writing it. Counters under `feedback/v1/limit/` are not read.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from digest import DigestError, refuse_repo_path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api" / "worker" / "src"))
import feedback_service as fb  # noqa: E402

Runner = Callable[[Sequence[str]], str]


def wrangler(args: Sequence[str]) -> str:
    return subprocess.run(["npx", "wrangler", *args], check=True, capture_output=True,
                          text=True).stdout


def export(namespace_id: str, out: Path, run: Runner = wrangler) -> int:
    out = refuse_repo_path(out, "--out")
    listed = json.loads(run(["kv", "key", "list", "--namespace-id", namespace_id,
                             "--prefix", fb.RECORD_PREFIX, "--remote"]))
    lines = []
    for row in sorted(listed, key=lambda r: r["name"]):
        record = json.loads(run(["kv", "key", "get", row["name"], "--namespace-id",
                                 namespace_id, "--remote", "--text"]))
        if tuple(record) != fb.STORED_FIELDS:
            raise DigestError(f"{row['name']} is not a stored feedback record")
        lines.append(json.dumps(record, separators=(",", ":")))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    return len(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--namespace-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        count = export(args.namespace_id, args.out)
    except DigestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"records": count, "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
