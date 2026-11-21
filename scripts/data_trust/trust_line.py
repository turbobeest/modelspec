"""The weekly trust line (MODEL-522): counts, never failures.

Three numbers a reader can watch from week to week:
  1. verified records older than an age line, by facet group;
  2. retained copies that a manifest names but the disk lacks, and the verified records
     whose digest only such a lost path names;
  3. sources whose final host differs from the registered host (MODEL-523 state).
Whether a record was never retained is deliberately not reported (owner decision).
The age lines come from decision.staleness (MODEL-521); explicit values still override.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from decision import staleness
from decision.retention import canonical_host, cite_only_origin_restrictive
from scripts.data_trust.catalogue import Catalogue, day
from scripts.data_trust.retention import MAX_MANIFEST_BYTES, PATH_FIELDS, _files, _records

STALE_DAYS = staleness.STALE_DAYS
STALE_DAYS_FAST = staleness.STALE_DAYS_FAST  # price and subscription facets move faster
FAST_GROUPS = {"offering price", "subscription"}
FINAL_HOSTS = "verification/final-hosts.json"  # MODEL-523 per-source state, in the data repo
HEX = re.compile(r"[0-9a-f]{64}")
CHANGE_KEYS = ("stale", "lost_paths", "lost_records", "moved")


def facet_group(f: dict) -> str:
    facet = f.get("field")
    if f.get("kind") == "evidence" or not facet:
        return "benchmark evidence"
    for prefix, group in (
        ("offering.price", "offering price"),
        ("offering.subscription", "subscription"),
        ("offering.attestation", "offering data/attestation"),
        ("offering.data", "offering data/attestation"),
        ("offering.", "offering other"),
        ("licence", "licence"),
        ("feature", "feature"),
        ("origin", "origin"),
    ):
        if str(facet).startswith(prefix):
            return group
    return "model"


def stale(c: Catalogue, as_of: date, days: int, fast_days: int) -> dict:
    groups = defaultdict(lambda: {"verified": 0, "older": 0})
    for f in c.facts:
        verified = (f.get("verification") or {}).get("date")
        if day(verified) is None:
            continue
        group = facet_group(f)
        line = fast_days if group in FAST_GROUPS else days
        row = groups[group]
        row["verified"] += 1
        row["older"] += (as_of - day(verified)).days > line
    return {
        "age_line_days": days,
        "age_line_days_price_subscription": fast_days,
        "verified": sum(r["verified"] for r in groups.values()),
        "older": sum(r["older"] for r in groups.values()),
        "by_group": dict(sorted(groups.items())),
    }


def _disk_digests(root: Path, files: list[Path]) -> set[str]:
    digests = set()
    for path in files:
        rel = path.relative_to(root).as_posix()
        if path.suffix == ".gz" and (rel.startswith("research/") or "source-copies" in rel):
            raw = path.read_bytes()
            digests.add(hashlib.sha256(raw).hexdigest())
            try:
                digests.add(hashlib.sha256(gzip.decompress(raw)).hexdigest())
            except (OSError, EOFError):
                pass
    return digests


def lost_copies(c: Catalogue, root: Path) -> dict:
    root = root.resolve()
    files = sorted(_files(root))
    names = {p.relative_to(root).as_posix() for p in files}
    lost_paths, lost_digests = set(), set()
    for path in files:
        if path.suffix != ".json" or path.stat().st_size > MAX_MANIFEST_BYTES:
            continue
        try:
            records = list(_records(json.loads(path.read_bytes())))
        except (OSError, ValueError, RecursionError):
            continue
        base = path.parent.relative_to(root).as_posix()
        for record in records:
            for key in PATH_FIELDS:
                value = record.get(key)
                if not isinstance(value, str) or not value:
                    continue
                present = value in names or os.path.normpath(os.path.join(base, value)) in names
                if present:
                    continue
                lost_paths.add((path.relative_to(root).as_posix(), value))
                for text in (record.get("sha256"), record.get("snapshot_ref"), value):
                    match = HEX.search(text) if isinstance(text, str) else None
                    if match:
                        lost_digests.add(match.group())
    on_disk = _disk_digests(root, files)
    records = 0
    for f in c.facts:
        if not (f.get("verification") or {}):
            continue
        refs = [s for s in f.get("sources") or [] if isinstance(s, dict)]
        digests = [
            m.group() for s in refs if (m := HEX.search(str(s.get("snapshot_ref") or "")))
        ]
        if not digests or any(d in on_disk for d in digests):
            continue
        urls = [(c.sources.get(s.get("source_id")) or {}).get("url") for s in refs]
        if urls and all(u and cite_only_origin_restrictive(u) for u in urls):
            continue  # cite-only by rule: nothing was to be kept
        records += any(d in lost_digests for d in digests)
    return {"lost_paths": len(lost_paths), "lost_records": records}


def moved_hosts(c: Catalogue, root: Path) -> dict:
    path = root / FINAL_HOSTS
    if not path.is_file():
        return {"recorded": False, "moved": 0, "source_ids": []}
    try:
        state = json.loads(path.read_text())
    except (OSError, ValueError):
        return {"recorded": False, "moved": 0, "source_ids": []}
    moved = []
    for sid, row in sorted(state.items() if isinstance(state, dict) else ()):
        registered, final = (c.sources.get(sid) or {}).get("url"), (row or {}).get("final_host")
        if not (registered and final):
            continue
        try:
            if canonical_host(registered) != str(final).lower():
                moved.append(sid)
        except ValueError:
            continue
    return {"recorded": True, "moved": len(moved), "source_ids": moved}


def compute(c: Catalogue, root: Path, as_of: date, days: int | None = None,
            fast_days: int | None = None) -> dict:
    # None means the rule in force on `as_of`, including the one-time first-quarter line.
    days = staleness.age_line("", as_of, fast=False) if days is None else days
    fast_days = staleness.age_line("offering.price", as_of, fast=True) if fast_days is None else fast_days
    return {
        "stale": stale(c, as_of, days, fast_days),
        "lost_copies": lost_copies(c, root),
        "moved_hosts": moved_hosts(c, root),
    }


def _numbers(line: dict) -> dict:
    return {
        "stale": line["stale"]["older"],
        "lost_paths": line["lost_copies"]["lost_paths"],
        "lost_records": line["lost_copies"]["lost_records"],
        "moved": line["moved_hosts"]["moved"] if line["moved_hosts"]["recorded"] else None,
    }


def with_change(line: dict, directory: Path | None, as_of: date) -> dict:
    """Week-over-week change against the latest earlier report in `directory`."""
    previous = None
    for path in sorted(directory.glob("*.json"), reverse=True) if directory and directory.is_dir() else ():
        if path.stem >= as_of.isoformat() or not path.stem[:4].isdigit():
            continue
        try:
            report = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(report.get("trust_line"), dict) and "stale" in report["trust_line"]:
            previous = (path.stem, report["trust_line"])
            break
    if previous is None:
        return {**line, "previous": None, "change": None}
    now, before = _numbers(line), _numbers(previous[1])
    change = {k: None if now[k] is None or before.get(k) is None else now[k] - before[k]
              for k in CHANGE_KEYS}
    return {**line, "previous": previous[0], "change": change}


def _delta(line: dict, key: str) -> str:
    change = line.get("change")
    if not change or change.get(key) is None:
        return ""
    return f" ({change[key]:+d} since {line['previous']})"


def text(line: dict) -> str:
    if "unavailable" in line:
        return f"Trust line: trust line unavailable ({line['unavailable']})\n"
    s, lost, hosts = line["stale"], line["lost_copies"], line["moved_hosts"]
    moved = (f"{hosts['moved']}{_delta(line, 'moved')}" if hosts["recorded"]
             else "not recorded yet")
    return (
        f"Trust line: verified records older than {s['age_line_days']} days "
        f"({s['age_line_days_price_subscription']} for price and subscription; "
        f"MODEL-521 rule): "
        f"{s['older']} of {s['verified']}{_delta(line, 'stale')}\n"
        f"Trust line: lost retained copies: {lost['lost_paths']} paths"
        f"{_delta(line, 'lost_paths')}; records whose digest only a lost path names: "
        f"{lost['lost_records']}{_delta(line, 'lost_records')}\n"
        f"Trust line: sources whose final host differs from the registered host: {moved}\n"
    )
