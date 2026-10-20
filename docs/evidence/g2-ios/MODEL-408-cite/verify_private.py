"""Check MODEL-408 citations in private data and the generated signed Worker bundle.

Only counts are printed. Run with the engine root on PYTHONPATH and a test
MODELSPEC_SNAPSHOT_KEY matching the key used by api/worker/vendor.py.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from datetime import date, datetime
from pathlib import Path

import yaml

from decision.citation import fact_citation
from decision.model import Fact, VerificationActor
from decision.snapshot import load_snapshot_bytes
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, StoredRegions, deterministic_extractors, verify


class NoPageReads(StoredRegions):
    def text(self, *args, **kwargs):
        raise AssertionError("Citation verification attempted to read source text")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args()
    sources = load_sources(args.data_dir / "registry/sources.yaml")
    urls = {sid: str(source.url) for sid, source in sources.items()}
    plans = yaml.safe_load((args.data_dir / "offerings/subscriptions/xai.yaml").read_text())
    facts = [raw for plan in plans for raw in plan["facts"] if any(
        ref["source_id"] == "model-408-xai-pricing-exact" for ref in raw.get("sources", [])
    )]
    assert len(facts) == 35
    assert sum(raw["state"] == "known" for raw in facts) == 17
    assert sum(raw["state"] == "unknown" for raw in facts) == 18
    actor = VerificationActor(agent="citation-audit", model_family="fixture", method="offline")
    with tempfile.TemporaryDirectory() as directory:
        regions = NoPageReads(CopyStore(directory), sources)
        for raw in facts:
            fact = Fact.model_validate(raw)
            citation = fact_citation(raw, urls)
            assert citation["status"] == "cited"
            if fact.state == "unknown":
                assert fact.value is None
                continue
            result = verify(Claim.from_fact(fact, names=[fact.subject.id], collector=actor),
                            regions, deterministic_extractors(), today=date(2026, 10, 19))
            assert result.outcome == "cited" and result.verification is None
        assert not list(Path(directory).rglob("*"))

    spec = importlib.util.spec_from_file_location(
        "model408_bundle", args.bundle / "bundled_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = []
    for path in ("/api/decision/snapshot.json.gz", "/api/decision/snapshot-successor.json.gz"):
        blob = module.read(path)
        if blob is None:
            assert path.endswith("-successor.json.gz")
            continue
        index = load_snapshot_bytes(blob)
        assert index.signature_verified
        subscriptions = {row["id"]: row for row in index.subscription_offerings()}
        known = unknown = 0
        for raw in facts:
            row = subscriptions[raw["subject"]["id"]]["facts"]
            if raw["state"] == "unknown":
                assert raw["value"] is None and raw["facet"] not in row
                unknown += 1
                continue
            value = row[raw["facet"]]
            assert value.state == "known" and value.value == raw["value"]
            record = index.record(value.record_id)
            assert record["verification"] is None
            assert record["citation"]["status"] == "cited"
            expected = raw["sources"][0]
            actual = record["citation"]["sources"][0]
            assert actual["url"] == "https://x.ai/pricing"
            assert actual["snapshot_ref"] == expected["snapshot_ref"]
            assert datetime.fromisoformat(actual["retrieved_at"]) == datetime.fromisoformat(
                expected["retrieved_at"])
            known += 1
        assert (known, unknown) == (17, 18)
        checks.append({"path": path, "signed": True, "known_cited": known,
                       "unknown_not_admitted": unknown})
    print(json.dumps({"facts_validated": 35, "verifier_cited_without_page_reads": 17,
                      "snapshots": checks}, indent=2))


if __name__ == "__main__":
    main()
