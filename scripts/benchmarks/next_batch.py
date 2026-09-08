#!/usr/bin/env python3
"""Cut the next batch of unwritten benchmarks out of a census queue, into agent-sized slices.

    /opt/homebrew/bin/python3.11 scripts/benchmarks/next_batch.py [queue_p2.json] [count] [slice_size]

Skips anything already written in benchmarks/ (by id or by alias), keeps name families together,
and writes benchmarks/_census/next_batch.json: {"slices": {label: [ids]}, "hints": {id: {...}}}.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "benchmarks" / "_census"


def norm(s: str) -> str:
    """Collapse slug spelling variants: live_code_bench == livecodebench, commonsense_qa == commonsenseqa."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def written() -> set[str]:
    have = set()
    for p in (ROOT / "benchmarks").glob("*.md"):
        if p.name == "AUTHORING.md":
            continue
        have.add(norm(p.stem))
        head = p.read_text(errors="ignore")[:2000]
        m = re.search(r"^aliases:\s*\[(.*?)\]", head, re.M)
        if m:
            have.update(norm(a.strip().strip("'\"")) for a in m.group(1).split(",") if a.strip())
    return have


def family_key(slug: str) -> str:
    parts = slug.split("_")
    for n in (2, 1):
        if len(parts) > n:
            return "_".join(parts[:n])
    return slug


def main() -> None:
    qname = sys.argv[1] if len(sys.argv) > 1 else "queue_p2.json"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    q = json.loads((CENSUS / qname).read_text())
    have = written()
    pool, seen = [], set(have)
    for e in q:
        n = norm(e["slug"])
        if n in seen:
            continue
        seen.add(n)
        pool.append(e)
        if len(pool) >= count:
            break
    groups: dict[str, list[dict]] = collections.defaultdict(list)
    for e in pool:
        groups[family_key(e["slug"])].append(e)
    slices: dict[str, list[str]] = {}
    cur: list[str] = []
    label = ord("A")
    for fam in sorted(groups, key=lambda f: -len(groups[f])):
        ids = [e["slug"] for e in groups[fam]]
        if cur and len(cur) + len(ids) > size:
            slices[chr(label)] = cur
            label += 1
            cur = []
        cur.extend(ids)
        while len(cur) > size:
            slices[chr(label)] = cur[:size]
            label += 1
            cur = cur[size:]
    if cur:
        slices[chr(label)] = cur
    hints = {e["slug"]: {k: e[k] for k in ("name", "aliases", "sources", "urls", "harness", "category_hint", "score")} for e in pool}
    (CENSUS / "next_batch.json").write_text(json.dumps({"queue": qname, "slices": slices, "hints": hints}, indent=1))
    print(f"{len(pool)} unwritten ids from {qname} in {len(slices)} slices:")
    for k, v in slices.items():
        print(f"  {k} ({len(v)}): {', '.join(v)}")


if __name__ == "__main__":
    main()
