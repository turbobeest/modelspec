"""Check the local private Worker bundle without printing private fact rows."""

from __future__ import annotations

import argparse
import runpy
import subprocess
from pathlib import Path

import yaml

from decision.retention import is_cite_only
from decision.snapshot import load_snapshot_bytes
from decision.sources import load_sources


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--base", default="d299550bc36e863a46c2d8f925ec61e41a0d9b7a")
    parser.add_argument("--key", default="model-368-cite-test-signing-key-only",
                        help="test-only snapshot signing key used for the local bundle")
    args = parser.parse_args()
    relative = "offerings/subscriptions/perplexity.yaml"
    original = yaml.safe_load(subprocess.check_output(
        ["git", "-C", str(args.data_dir), "show", f"{args.base}:{relative}"], text=True,
    ))
    current = yaml.safe_load((args.data_dir / relative).read_text())
    before = {fact["id"]: fact for plan in original for fact in plan["facts"]}
    after = {fact["id"]: fact for plan in current for fact in plan["facts"]}
    assert before.keys() == after.keys(), "fact identities changed"
    for fid, row in after.items():
        assert (row["state"], row["value"]) == (before[fid]["state"], before[fid]["value"]), fid
        for old_ref, new_ref in zip(before[fid].get("sources", []), row.get("sources", []), strict=True):
            assert {k: v for k, v in new_ref.items() if k != "retrieved_at"} == old_ref, fid
    pin = subprocess.check_output(
        ["git", "-C", str(args.data_dir), "show", f"{args.base}:.engine-pin"], text=True,
    )
    assert (args.data_dir / ".engine-pin").read_text() == pin, "engine pin changed"

    bundle = runpy.run_path(str(args.bundle / "bundled_data.py"))
    raw = bundle["read"]("/api/decision/snapshot.json.gz")
    assert raw is not None, "missing signed snapshot"
    index = load_snapshot_bytes(raw, key=args.key)
    plans = {plan["id"]: plan for plan in index.subscription_offerings()}
    sources = load_sources(args.data_dir / "registry/sources.yaml")
    cited = 0
    missing = []
    for plan in current:
        sid = f"{plan['provider']}/subscription/{plan['plan']}"
        assert sid in plans, "missing subscription"
        for row in plan["facts"]:
            refs = row.get("sources", [])
            if not any(is_cite_only(sources[ref["source_id"]].url) for ref in refs):
                continue
            exported = plans[sid]["facts"].get(row["facet"])
            if exported is None:
                missing.append(row["id"])
                continue
            assert exported.state == row["state"], row["id"]
            assert exported.value == row["value"], row["id"]
            record = index.record(exported.record_id)
            assert record["verification"] is None, row["id"]
            assert record["citation"]["status"] == "cited", row["id"]
            expected = [{
                "source_id": ref["source_id"],
                "url": str(sources[ref["source_id"]].url),
                "snapshot_ref": ref["snapshot_ref"],
                "retrieved_at": ref.get("retrieved_at"),
            } for ref in refs]
            assert record["citation"]["sources"] == expected, row["id"]
            cited += 1
    print(f"PASS: {len(after)} fact values/states unchanged; {cited} cited exports; no verification claims")
    print("PASS: original URLs/hashes/fetch metadata preserved; engine pin unchanged")
    if missing:
        print("FAIL: curated facts absent from snapshot: " + ", ".join(missing))
        raise SystemExit(1)
    assert cited == 6, f"expected six cited Perplexity facts, got {cited}"


if __name__ == "__main__":
    main()
