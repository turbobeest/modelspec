#!/usr/bin/env python3
"""Collect direct Finance Benchmark v2 evidence for the premier set."""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import USER_AGENT, CopyStore, load_sources
from decision.verify import Claim, Queue
from scripts.model_143_evidence import evidence_id
from scripts.model_160_evidence import append_rows, new_row_block

ROOT = Path(__file__).resolve().parents[1]
URL = "https://finbenchmark.ai/"
SOURCE_ID = "model-192-finance-benchmark-v2"
READ_DATE = "2026-09-28"
BENCHMARK_ID = "finance_benchmark_v2"
COLLECTOR = VerificationActor(
    agent="codex-model-192",
    model_family="openai",
    method="finance-benchmark-v2-projection@1",
)

# Canonical catalogue IDs use hyphenated release numbers. The source publishes
# the providers' dotted API IDs for these three models.
SOURCE_TO_MODEL = {
    "openai/gpt-5.6-sol": "openai/gpt-5-6-sol",
    "google/gemini-3.5-flash": "google/gemini-3-5-flash",
    "openai/gpt-5.4": "openai/gpt-5-4",
}

ROW = re.compile(
    r'\\"model_name\\":\\"(?P<model>[^\\"]+)\\",'
    r'\\"provider\\":\\"(?P<provider>[^\\"]+)\\".*?'
    r'\\"harness_version\\":\\"(?P<harness>[^\\"]+)\\".*?'
    r'\\"task_set_version\\":\\"(?P<task_set>[^\\"]+)\\".*?'
    r'\\"pass_at_1\\":(?P<score>[0-9.]+).*?'
    r'\\"completed_at\\":\\"(?P<date>[^T\\"]+)',
)


def fetch_rows(store: CopyStore) -> tuple[list[dict], str]:
    request = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        raw = response.read()
    fetched_copy = store.put(raw)
    html = raw.decode("utf-8")
    rows = []
    for match in ROW.finditer(html):
        row = match.groupdict()
        if row["task_set"] != "v2":
            continue
        rows.append({
            "model": f"{row['provider']}/{row['model']}",
            "pass_at_1": round(float(row["score"]) * 100, 4),
            "unit": "percent",
            "date": row["date"],
            "harness": "unregistered",
            "harness_version": row["harness"],
            "task_set_version": row["task_set"],
        })
    if not rows:
        raise RuntimeError("Finance Benchmark page contained no v2 rows")
    projected = json.dumps(
        {
            "source_url": URL,
            "read_date": READ_DATE,
            "provenance": {
                "fetched_copy": fetched_copy,
                "projection": (
                    "Finance Benchmark v2 rows from the page payload; pass_at_1 "
                    "converted from a fraction to percent"
                ),
            },
            "rows": rows,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return rows, store.put(projected)


def cards(root: Path) -> dict[str, Path]:
    premier = {
        row["model_id"]
        for row in yaml.safe_load((root / "premier" / "slice-1.yaml").read_text())["models"]
    }
    found = {}
    for path in sorted((root / "models").glob("*/*.md")):
        front = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        if front.get("model_id") in premier:
            found[front["model_id"]] = path
    return found


def collect(root: Path = ROOT) -> tuple[int, list[str]]:
    if SOURCE_ID not in load_sources(root / "registry" / "sources.yaml"):
        raise RuntimeError(f"register {SOURCE_ID} before collecting")
    store = CopyStore()
    rows, ref = fetch_rows(store)
    by_model = {SOURCE_TO_MODEL.get(row["model"], row["model"]): row for row in rows}
    queue = Queue(root / "verification")
    filed_at = datetime.now(UTC)
    added = 0
    matched = []
    for model_id, path in cards(root).items():
        source = by_model.get(model_id)
        if source is None:
            continue
        text = path.read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        evidence = ((front.get("benchmarks") or {}).get("evidence") or [])
        existing = next((row for row in evidence if row["benchmark_id"] == BENCHMARK_ID), None)
        if existing is not None:
            old_ref = existing["sources"][0]["snapshot_ref"]
            if old_ref != ref:
                path.write_text(text.replace(old_ref, ref, 1), encoding="utf-8")
                queue.file(Claim(
                    target=TargetRef(kind="evidence", id=existing["id"]),
                    subject=model_id,
                    names=(source["model"], front["display_name"], model_id.rsplit("/", 1)[-1]),
                    field=BENCHMARK_ID,
                    label="pass_at_1",
                    value=existing["score"],
                    unit=existing["unit"],
                    conditions={"effort": None, "harness": "unregistered",
                                "date": existing["evidence_date"]},
                    collector=COLLECTOR,
                    sources=(SourceRef(source_id=SOURCE_ID, snapshot_ref=ref,
                                       cited_regions=["rows"]),),
                ), at=filed_at)
            matched.append(model_id)
            continue
        row = {
            "benchmark_id": BENCHMARK_ID,
            "model_id_as_evaluated": source["model"],
            "score": source["pass_at_1"],
            "unit": "percent",
            "source_url": URL,
            "source_kind": "independent_evaluator",
            "evidence_date": source["date"],
            "date_type": "evaluated",
            "observed_at": READ_DATE,
            "verified_at": READ_DATE,
            "benchmark_version": "Finance Benchmark v2, harness " + source["harness_version"],
            "configuration": "73 v2 tasks; three attempts per task; temperature zero.",
            "limitations": (
                "Passes at least once, so this value does not measure repeated-run consistency."
            ),
            "measured_by": "independent_evaluator",
            "effort": None,
            "harness": "unregistered",
            "sources": [{
                "source_id": SOURCE_ID,
                "snapshot_ref": ref,
                "cited_regions": ["rows"],
            }],
        }
        row["id"] = evidence_id(model_id, row)
        append_rows(path, [new_row_block(row)])
        queue.file(Claim(
            target=TargetRef(kind="evidence", id=row["id"]),
            subject=model_id,
            names=(source["model"], front["display_name"], model_id.rsplit("/", 1)[-1]),
            field=BENCHMARK_ID,
            label="pass_at_1",
            value=row["score"],
            unit=row["unit"],
            conditions={"effort": None, "harness": "unregistered", "date": row["evidence_date"]},
            collector=COLLECTOR,
            sources=(SourceRef(**row["sources"][0]),),
        ), at=filed_at)
        matched.append(model_id)
        added += 1
    return added, sorted(matched)


if __name__ == "__main__":
    added, matched = collect()
    print(f"evidence rows added: {added}")
    print(f"lineup matches: {len(matched)}")
    for model_id in matched:
        print(model_id)
