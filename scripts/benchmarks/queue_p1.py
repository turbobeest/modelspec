#!/usr/bin/env python3
"""Build the batch-1 queue: every benchmark key that appears in the model cards, with hints.

Writes benchmarks/_census/queue_p1.json and benchmarks/_census/batch1_slices.json.
"""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "models"
OUT = ROOT / "benchmarks" / "_census"

FAMILY_RULES = [
    ("mmlu", r"^mmlu(_|$)(?!pro)"), ("multipl_e", r"^multipl_e"), ("mteb", r"^mteb"), ("arena_elo", r"^arena_elo"),
    ("swe_bench", r"^swe_bench"), ("flores", r"^flores"), ("graphwalks", r"^graphwalks"), ("charxiv", r"^charxiv"),
    ("screenspot_pro", r"^screenspot_pro"), ("lab_bench_figqa", r"^lab_bench_figqa"), ("hle", r"^hle"),
    ("terminal_bench", r"^terminal_bench"), ("artificial_analysis", r"^artificial_analysis"),
]


def family_of(k: str) -> str:
    for fam, rx in FAMILY_RULES:
        if re.match(rx, k):
            return fam
    return ""


def main() -> None:
    per_key: dict[str, dict] = collections.defaultdict(lambda: {"models": 0, "top": [], "sources": collections.Counter(), "dates": collections.Counter()})
    for c in CARDS.rglob("*.md"):
        txt = c.read_text(errors="ignore")
        m = re.match(r"---\n(.*?)\n---", txt, re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            continue
        b = fm.get("benchmarks") or {}
        sc = b.get("scores") or {}
        if not isinstance(sc, dict):
            continue
        name = (fm.get("identity") or {}).get("display_name") or fm.get("display_name") or fm.get("name") or c.stem
        for k, v in sc.items():
            if v is None:
                continue
            e = per_key[k]
            e["models"] += 1
            if isinstance(v, (int, float)):
                e["top"].append((float(v), str(name)))
            if b.get("benchmark_source"):
                e["sources"][str(b["benchmark_source"])[:80]] += 1
            if b.get("benchmark_as_of"):
                e["dates"][str(b["benchmark_as_of"])[:7]] += 1
    queue = []
    for k, e in sorted(per_key.items()):
        top = sorted(e["top"], reverse=True)[:3]
        fam = family_of(k)
        kind = "family" if k == fam else ("subset" if fam and k != fam else "benchmark")
        if k in ("mmlu_pro",):
            kind, fam = "benchmark", "mmlu"
        queue.append({
            "id": k, "priority": 1, "page_kind_hint": kind, "family_hint": fam,
            "models_reporting": e["models"],
            "top_scores": [{"model": n, "score": v} for v, n in top],
            "score_sources": [s for s, _ in e["sources"].most_common(4)],
            "score_dates": [d for d, _ in e["dates"].most_common(3)],
        })
    # families that have subsets but no key of their own get a family page too
    fams_needed = {q["family_hint"] for q in queue if q["family_hint"]} - {q["id"] for q in queue}
    for fam in sorted(fams_needed):
        queue.append({"id": fam, "priority": 1, "page_kind_hint": "family", "family_hint": fam,
                      "models_reporting": 0, "top_scores": [], "score_sources": [], "score_dates": [],
                      "note": "family page: subsets exist in the cards, the family itself has no score key"})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "queue_p1.json").write_text(json.dumps(queue, indent=1))
    # slices for the agents: keep families together
    groups: dict[str, list[str]] = collections.defaultdict(list)
    for q in queue:
        groups[q["family_hint"] or "_single"].append(q["id"])
    singles = groups.pop("_single")
    slices: dict[str, list[str]] = {}
    mmlu = sorted(groups.pop("mmlu"))
    half = (len(mmlu) + 1) // 2
    slices["A-mmlu-1"] = mmlu[:half]
    slices["B-mmlu-2"] = mmlu[half:]
    coding = sorted(groups.pop("multipl_e")) + sorted(groups.pop("swe_bench")) + sorted(groups.pop("terminal_bench", []))
    slices["C-coding-families"] = coding
    emb = sorted(groups.pop("mteb")) + sorted(groups.pop("flores")) + sorted(groups.pop("arena_elo"))
    slices["D-embedding-translation-arena"] = emb
    rest_fams = [i for fam in sorted(groups) for i in sorted(groups[fam])]
    pool = rest_fams + sorted(singles)
    n = 4
    size = (len(pool) + n - 1) // n
    for i in range(n):
        slices[f"{'EFGH'[i]}-singles-{i + 1}"] = pool[i * size:(i + 1) * size]
    (OUT / "batch1_slices.json").write_text(json.dumps(slices, indent=1))
    print("queue:", len(queue), "ids;", {k: len(v) for k, v in slices.items()})


if __name__ == "__main__":
    main()
