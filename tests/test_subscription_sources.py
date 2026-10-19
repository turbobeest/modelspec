"""The independent subscription expectation admits cited facts as the snapshot does."""

import json
from datetime import date

import yaml

from decision.model import value_hash
from decision.snapshot import FactValue
from tests.subscription_sources import admitted_subscription_facts

SID = "acme/subscription/plus"
HASH = "sha256:" + "ab" * 32


def ref(source_id, **extra):
    return {"source_id": source_id, "snapshot_ref": HASH, "cited_regions": ["page"], **extra}


def fact(facet, value, *refs):
    return {"id": f"{SID}#{facet}", "facet": facet, "state": "known", "value": value,
            "sources": list(refs)}


def record(facet, value, outcome, collector="gpt-5", verifier="claude"):
    return {
        "target": {"kind": "fact", "id": f"{SID}#{facet}", "value_hash": value_hash(value)},
        "collector": {"agent": "c", "model_family": collector, "method": "m"},
        "verifier": {"agent": "v", "model_family": verifier, "method": "m"},
        "method": "m", "outcome": outcome, "date": "2026-10-01",
    }


def repository(tmp_path, log):
    (tmp_path / "registry").mkdir()
    region = [{"id": "page", "locator": {"kind": "page", "value": ""}}]
    (tmp_path / "registry/sources.yaml").write_text(yaml.safe_dump({"schema_version": 1, "sources": [
        {"id": "cited", "url": "https://x.ai/pricing", "cited_regions": region},
        {"id": "open", "url": "https://example.com/pricing", "cited_regions": region},
    ]}))
    (tmp_path / "verification").mkdir()
    (tmp_path / "verification/log.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in log))
    return tmp_path


def test_cited_facts_enter_without_a_verification_and_others_still_need_one(tmp_path):
    facts = [
        fact("offering.subscription.price", 8, ref("cited", retrieved_at="2026-10-18T09:33:48.466000Z")),
        fact("offering.subscription.billing_period", "monthly", ref("cited")),
        fact("offering.subscription.usage_allowance", "more", ref("cited")),
        fact("offering.subscription.models_covered", ["acme/a"],
             {"source_id": "cited", "snapshot_ref": "sha256:short", "cited_regions": ["page"]}),
        fact("offering.subscription.seats", 1, ref("open")),
        fact("offering.subscription.price_annual", 80, ref("open")),
        fact("offering.subscription.trial", "none", ref("open")),
        fact("offering.subscription.tier", "plus",
             ref("open", resolved_urls=["https://docs.x.ai/plans"])),
    ]
    root = repository(tmp_path, [
        record("offering.subscription.usage_allowance", "more", "mismatch"),
        record("offering.subscription.price_annual", 80, "verified"),
        record("offering.subscription.trial", "none", "verified", "claude", "claude"),
    ])

    expected = admitted_subscription_facts(root, {SID: {"facts": facts}}, date(2026, 10, 19))

    assert expected == {SID: {
        "offering.subscription.price": FactValue("known", 8, ("cited",)),
        "offering.subscription.billing_period": FactValue("known", "monthly", ("cited",)),
        "offering.subscription.price_annual": FactValue("known", 80, ("open",)),
        "offering.subscription.tier": FactValue("known", "plus", ("open",)),
    }}
