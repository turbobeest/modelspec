"""Compose the frozen public image with deterministic synthetic private-size data.

The fixture contains invented sources and workloads. It never reads private data.
Use the resulting data directory with the engine's ordinary vendor.py command.
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from decision.model import fact_verification_value, value_hash  # noqa: E402
from pipeline.data_source import DATA_PATHS  # noqa: E402

RECIPE = Path(__file__).with_name("memory-fixture.json")


def _verification(rid: str, value: object) -> dict:
    return {
        "target": {"kind": "fact", "id": rid, "value_hash": value_hash(value)},
        "collector": {"agent": "fixture-collector", "model_family": "fixture-a", "method": "read"},
        "verifier": {"agent": "fixture-verifier", "model_family": "fixture-b", "method": "re-read"},
        "method": "Synthetic memory calibration only", "outcome": "verified", "date": "2026-09-20",
    }


def materialize(public: Path, out: Path, *, recipe: Path = RECIPE,
                as_of: date | None = None) -> Path:
    """Create a new data directory without modifying its public input."""
    config = json.loads(recipe.read_text())
    public, out = public.resolve(), out.resolve()
    out.mkdir(parents=True)
    for name in DATA_PATHS:
        source, target = public / name, out / name
        if not source.exists() or name in {"hardware", "offerings", "registry/sources.yaml"}:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source)
    shutil.copytree(public / "hardware", out / "hardware")
    shutil.copytree(public / "offerings", out / "offerings")
    source_path = out / "registry/sources.yaml"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    sources = yaml.safe_load((public / "registry/sources.yaml").read_text())
    ids = [f"memory-fixture-source-{i:04d}" for i in range(config["source_count"])]
    for i, sid in enumerate(ids):
        prefix = f"https://memory-fixture.example/source/{i:04d}/"
        regions = [{"id": "page", "locator": {"kind": "page", "value": ""}}]
        if i < config["extra_cited_regions"]:
            regions.append({"id": "table", "locator": {"kind": "table", "value": "0"}})
        sources["sources"].append({
            "id": sid,
            "url": prefix + "x" * max(0, config["source_url_characters"] - len(prefix)),
            "fetch": "conditional_http", "normaliser": "html-default",
            "cited_regions": regions,
        })
    source_path.write_text(yaml.safe_dump(sources, sort_keys=False))
    rows = []
    for i in range(config["hardware_fit_records"]):
        source_ids = [ids[(i + j) % len(ids)] for j in range(config["sources_per_record"])]
        rid = f"hardware-fit:memory-fixture-{i:04d}"

        def number(value: int, field: str) -> dict:
            return {"value": value, "record_id": f"{rid}:{field}", "source_ids": source_ids}

        row = {
            "id": rid, "status": "estimated", "model": config["model"], "sku": config["sku"],
            "device_count": 1, "runtime": f"memory-fixture@{i}", "quantisation": "fixture-fp16",
            "batch": 2, "context": 1024, "memory_bytes_per_device": 24_000_000_000,
            "observed_at": "2026-09-20", "source_ids": source_ids,
            "per_device": [{"weights_bytes": number(65_500_000_000 + i, "weights"),
                            "kv_bytes_per_token": number(100_000, "kv")}],
        }
        row["verification"] = _verification(rid, row)
        rows.append(row)
    fit_path = out / "hardware/fit/records.yaml"
    fit_path.parent.mkdir(parents=True, exist_ok=True)
    existing = yaml.safe_load(fit_path.read_text()) if fit_path.exists() else []
    fit_path.write_text(yaml.safe_dump([*(existing or []), *rows], sort_keys=False))
    # A real dated price makes vendor.py build the full successor and vocabulary.
    # Keep the boundary outside the 24-hour preload window during ordinary probes.
    today = as_of or datetime.now(UTC).date()
    boundary = today + timedelta(days=config["price_boundary_days"])
    offering_path = out / "offerings" / config["dated_offering"]
    offerings = yaml.safe_load(offering_path.read_text())
    facts = offerings[0]["facts"]
    current = next(fact for fact in facts if fact["facet"] == "offering.price.input")
    successor = copy.deepcopy(current)
    for fact, suffix in ((current, "current"), (successor, "successor")):
        fact["id"] += f":memory-fixture-{suffix}"
        fact["sources"] = [{"source_id": ids[0], "snapshot_ref": "sha256:" + "0" * 64,
                            "cited_regions": ["page"]}]
    current["effective_until"] = (boundary - timedelta(days=1)).isoformat()
    successor["effective_from"] = boundary.isoformat()
    successor["value"] = current["value"] + 0.125
    for fact in (current, successor):
        fact["verification"] = _verification(fact["id"], fact_verification_value(fact))
    facts.append(successor)
    offering_path.write_text(yaml.safe_dump(offerings, sort_keys=False))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-engine", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, default=RECIPE)
    args = parser.parse_args()
    materialize(args.public_engine, args.out, recipe=args.recipe)


if __name__ == "__main__":
    main()
