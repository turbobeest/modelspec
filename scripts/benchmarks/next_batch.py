#!/usr/bin/env python3
"""Cut the next batch of unwritten benchmarks out of a census queue, into agent-sized slices.

    python3 scripts/benchmarks/next_batch.py [queue_p2.json] [count] [slice_size]

Requires reviewed, current eligibility evidence before selecting any census entry.
Skips written pages, keeps name families together, and writes next_batch_eligible.json.
The legacy next_batch.json is preserved as provenance, not used as a fallback.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "benchmarks" / "_census"
sys.path.insert(0, str(ROOT))

from scripts.benchmarks.downselect import build_report  # noqa: E402


def load_map() -> dict:
    f = CENSUS / "aliases.yaml"
    d = yaml.safe_load(f.read_text()) if f.exists() else {}
    return {
        "aliases": d.get("aliases") or {},
        "rename": d.get("rename") or {},
        "drop": set(d.get("not_a_benchmark") or []),
    }


def norm(s: str) -> str:
    """Collapse punctuation differences in slug spelling."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def written() -> set[str]:
    have = set()
    for p in (ROOT / "benchmarks").glob("*.md"):
        if p.name in ("AUTHORING.md", "LICENSE.md", "README.md"):
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", nargs="?", default="queue_p2.json")
    parser.add_argument("count", nargs="?", type=int, default=40)
    parser.add_argument("slice_size", nargs="?", type=int, default=7)
    parser.add_argument("--evidence", type=Path, default=CENSUS / "eligibility/evidence")
    parser.add_argument(
        "--reference-set", type=Path, default=CENSUS / "eligibility/reference-models.json"
    )
    parser.add_argument("--output", type=Path, default=CENSUS / "next_batch_eligible.json")
    args = parser.parse_args()
    if args.count < 1 or args.slice_size < 1:
        parser.error("count and slice_size must be positive")
    output = args.output.resolve()
    if output in {args.reference_set.resolve(), (CENSUS / args.queue).resolve()} or (
        output.parent == args.evidence.resolve()
    ):
        parser.error("output must be separate from queue, evidence and reference inputs")
    # Re-evaluate source records today. A saved report's active_ids can expire.
    try:
        eligibility = build_report(args.evidence, args.reference_set, date.today())
    except (OSError, ValueError) as exc:
        if args.output.exists():
            args.output.unlink()
        parser.error(f"eligibility check failed; no census fallback: {exc}")
    active_ids = set(eligibility.active_ids)
    qname, count, size = args.queue, args.count, args.slice_size
    q = json.loads((CENSUS / qname).read_text())
    have = written()
    m = load_map()
    pool, seen, folded = [], set(have), []
    for e in q:
        slug = e["slug"]
        if slug in m["drop"]:
            continue
        canon = m["aliases"].get(slug)
        if canon:
            if norm(canon) in have:
                folded.append((slug, canon))
                continue
            slug = m["rename"].get(slug, canon)
        else:
            slug = m["rename"].get(slug, slug)
        if slug not in active_ids:
            continue
        n = norm(slug)
        if n in seen:
            continue
        seen.add(n)
        e = dict(e, slug=slug, census_slug=e["slug"])
        pool.append(e)
        if len(pool) >= count:
            break
    if folded:
        print("folded into existing pages as aliases:")
        for s, c in folded:
            print(f"  {s} -> {c}")
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
    # NB: the queue's "score" is the census ranking score (how strongly the sources vouch for this
    # name), NOT a benchmark result. It is renamed here so writers cannot mistake it for one.
    hints = {}
    for e in pool:
        h = {
            k: e[k]
            for k in (
                "name",
                "aliases",
                "sources",
                "urls",
                "harness",
                "category_hint",
                "census_slug",
            )
            if k in e
        }
        h["census_rank_score"] = e.get("score")
        h["_note"] = (
            "census_rank_score ranks discovery support for this name; "
            "it is not a benchmark result or eligibility evidence"
        )
        hints[e["slug"]] = h
    payload = {
        "queue": qname,
        "eligibility_as_of": eligibility.as_of.isoformat(),
        "eligible_ids": sorted(active_ids),
        "slices": slices,
        "hints": hints,
    }
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(args.output)
    print(f"{len(pool)} eligible unwritten ids from {qname} in {len(slices)} slices:")
    for k, v in slices.items():
        print(f"  {k} ({len(v)}): {', '.join(v)}")


if __name__ == "__main__":
    main()
