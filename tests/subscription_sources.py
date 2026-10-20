"""Independent source expectations for subscription integration tests."""

import json
import subprocess

import yaml

from decision.citation import fact_citation
from decision.model import Fact, Measurement, value_hash, verification_counts
from decision.snapshot import FactValue
from decision.sources import load_sources


def source_subscriptions(root, registry):
    tracked = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z", "--", "offerings/subscriptions/*.yaml"],
        text=True,
    ).split("\0")
    tracked = {name for name in tracked if name}
    assert tracked, "no tracked subscription files"
    present = {
        str(path.relative_to(root)) for path in (root / "offerings/subscriptions").glob("*.yaml")
    }
    assert not tracked - present, f"missing subscription files: {sorted(tracked - present)}"
    sources = load_sources(root / "registry/sources.yaml")
    vendors = {vendor.id for vendor in registry.vendors()}  # MODEL-205 pins its own
    subscriptions = {}
    for relative in sorted(present):
        for row in yaml.safe_load((root / relative).read_text()):
            registry.plan_owner(row["provider"])
            if row["provider"] in vendors:
                continue
            sid = f"{row['provider']}/subscription/{row['plan']}"
            assert sid not in subscriptions, f"duplicate subscription: {sid}"
            facets = [fact["facet"] for fact in row["facts"]]
            assert len(facets) == len(set(facets)), f"duplicate subscription facet: {sid}"
            for fact in row["facts"]:
                registry.facet(fact["facet"])
                if fact["state"] == "known":
                    assert fact.get("sources"), f"unsourced known subscription fact: {sid}"
                    assert all(ref["source_id"] in sources for ref in fact["sources"]), sid
            subscriptions[sid] = row
    return subscriptions


def json_record(record):
    return json.loads(json.dumps(record, default=lambda value: value.isoformat()))


def admitted_subscription_facts(root, subscriptions, as_of, registry=None, store=None):
    """Project raw facts using the documented second-key and source rules.

    Do not call the snapshot compiler or collector to form its expected output.
    Log entries win same-day ties over inline verification, and later log rows
    win ties with earlier rows. Same-family verified entries do not count.
    A fact whose every ref is cite-only is admitted without a verified outcome.
    ``store`` supplies fetcher redirect records; card redirect URLs do not.
    """
    log = [
        json.loads(line)
        for line in (root / "verification/log.jsonl").read_text().splitlines()
        if line.strip()
    ]
    sources = load_sources(root / "registry/sources.yaml")
    urls = {sid: str(source.url) for sid, source in sources.items()}
    expected = {}
    for sid, subscription in subscriptions.items():
        expected[sid] = {}
        for fact in subscription["facts"]:
            if fact["state"] == "unknown":
                continue
            fid = fact.get("id", f"{sid}#{fact['facet']}")
            candidates = [
                (str(record["date"]), order, record)
                for order, record in enumerate([fact.get("verification"), *log])
                if record
                and record["target"]["kind"] == "fact"
                and record["target"]["id"] == fid
                and record["target"].get("value_hash") == value_hash(fact.get("value"))
                and verification_counts(
                    record["outcome"],
                    record["collector"]["model_family"],
                    record["verifier"]["model_family"],
                )
            ]
            latest = max(candidates, key=lambda row: row[:2])[2]["outcome"] if candidates else None
            try:
                citation = fact_citation(fact, urls, store)
            except ValueError:
                continue
            if citation is not None:
                if fact["facet"] in {"offering.api_model_id", "offering.router_slug"}:
                    continue
                try:
                    Fact.model_validate(
                        {**fact, "verification": None}, context={"registry": registry},
                    )
                except ValueError:
                    continue
                if latest in {"mismatch", "unreachable"}:
                    continue
            elif latest != "verified":
                continue
            source_ids = tuple(sorted({ref["source_id"] for ref in fact.get("sources", [])}))
            if not source_ids or not all(source in sources for source in source_ids):
                continue
            if fact.get("measurement"):
                measurement = Measurement.model_validate(fact["measurement"])
                assert measurement.provenance != "fixture"
                if measurement.stale(as_of):
                    continue
            expected[sid][fact["facet"]] = FactValue(
                fact["state"],
                fact.get("value") if fact["state"] == "known" else None,
                source_ids,
            )
    return expected
