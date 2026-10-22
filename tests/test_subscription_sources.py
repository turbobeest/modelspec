"""The independent subscription expectation admits cited facts as the snapshot does."""

import json
from datetime import date

import pytest
import yaml

from decision.registry import default as default_registry
from decision.snapshot import (
    FactValue,
    SnapshotInputs,
    build_snapshot,
    collect_repo,
    load_built_snapshot,
)
from tests.snapshot_records import fact, subscription, verification
from tests.subscription_sources import admitted_subscription_facts

REGISTRY = default_registry()
DAY = date(2026, 10, 19)
URLS = {"cited": "https://x.ai/pricing", "open": "https://example.com/pricing"}
PRICE = "offering.subscription.price"


def plan_fact(plan, facet, value, source="cited", **verified):
    """A complete subscription fact with its subject, unverified unless asked."""
    return fact("offering", f"sambanova/subscription/{plan}", facet, value, source=source,
                outcome=verified.get("outcome"))


def repository(tmp_path, log=()):
    (tmp_path / "registry").mkdir(parents=True)
    region = [{"id": "r1", "locator": {"kind": "page", "value": ""}}]
    (tmp_path / "registry/sources.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "sources": [{"id": sid, "url": url, "cited_regions": region} for sid, url in URLS.items()],
    }))
    (tmp_path / "verification").mkdir()
    (tmp_path / "verification/log.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in log))
    return tmp_path


def both(tmp_path, rows, log=()):
    """The helper's expectation and the real snapshot's admitted facts, per plan."""
    rows = {f"{row['provider']}/subscription/{row['plan']}": row for row in rows}
    helper = admitted_subscription_facts(repository(tmp_path, log), rows, DAY, registry=REGISTRY)
    index = load_built_snapshot(build_snapshot(
        SnapshotInputs(subscriptions=list(rows.values()), sources=URLS, verifications=list(log)),
        registry=REGISTRY, as_of=DAY))
    snapshot = {row["id"]: row["facts"] for row in index.subscription_offerings()}
    return helper, snapshot


def test_cited_facts_enter_without_a_verification_and_others_still_need_one(tmp_path):
    cited = [
        plan_fact("plus", PRICE, 8),
        plan_fact("plus", "offering.subscription.billing_period", "monthly"),
        plan_fact("plus", "offering.subscription.usage_allowance", "more"),
        plan_fact("plus", "offering.subscription.models_covered", ["lab/alpha"]),
        plan_fact("plus", "offering.subscription.programmatic_or_agent_use", "yes", "open"),
    ]
    cited[0]["sources"][0]["retrieved_at"] = "2026-10-18T09:33:48.466000Z"
    cited[3]["sources"][0]["snapshot_ref"] = "sha256:short"
    opened = [
        plan_fact("pro", PRICE, 20, "open"),
        plan_fact("pro", "offering.subscription.billing_period", "monthly", "open"),
        plan_fact("pro", "offering.subscription.usage_allowance", "most", "open"),
    ]
    opened[2]["sources"][0]["resolved_urls"] = ["https://docs.x.ai/plans"]
    same_family = verification("fact", opened[1]["id"], value="monthly")
    same_family["verifier"]["model_family"] = same_family["collector"]["model_family"]
    log = [
        verification("fact", cited[2]["id"], "mismatch", value="more"),
        verification("fact", cited[4]["id"], value="yes"),
        same_family,
    ]
    rows = [subscription("sambanova", "plus", facts=cited), subscription("sambanova", "pro", facts=opened)]

    helper, snapshot = both(tmp_path, rows, log)

    assert helper == {
        "sambanova/subscription/plus": {
            PRICE: FactValue("known", 8, ("cited",)),
            "offering.subscription.billing_period": FactValue("known", "monthly", ("cited",)),
            "offering.subscription.programmatic_or_agent_use": FactValue("known", "yes", ("open",)),
        },
        # A card's own redirect to a cite-only host never stands in for verification.
        "sambanova/subscription/pro": {},
    }
    assert helper == snapshot


@pytest.mark.parametrize("change", [
    lambda f: f["sources"][0].update(cited_regions=[""]),
    lambda f: f["sources"][0].update(cited_regions=["   "]),
    lambda f: f.update(value="cheap"),
], ids=["blank_region", "whitespace_region", "invalid_value"])
def test_an_invalid_cited_fact_stays_out(tmp_path, change):
    price = plan_fact("plus", PRICE, 8)
    change(price)

    helper, snapshot = both(tmp_path, [subscription("sambanova", "plus", facts=[price])])

    assert helper == {"sambanova/subscription/plus": {}}
    assert snapshot == helper


def _case(name):
    """One subscription price fact and log, varied by ``name``."""
    f = plan_fact("plus", PRICE, 20)
    ref = f["sources"][0]
    log = []
    if name == "unknown":
        f.update(state="unknown", value=None)
    elif name == "bad_hash":
        ref["snapshot_ref"] = "sha256:short"
    elif name == "empty_regions":
        ref["cited_regions"] = []
    elif name == "blank_region":
        ref["cited_regions"] = [""]
    elif name == "whitespace_region":
        ref["cited_regions"] = ["   "]
    elif name == "invalid_value":
        f["value"] = "cheap"
    elif name == "no_sources":
        f["sources"] = []
    elif name == "unregistered_source":
        f["sources"].append({**ref, "source_id": "missing"})
    elif name in {"mismatch", "unreachable"}:
        f["verification"] = verification("fact", f["id"], name, value=20)
    elif name == "verified":
        f["verification"] = verification("fact", f["id"], value=20)
    elif name.startswith("open"):
        ref["source_id"] = "open"
        if name != "open_unverified":
            f["verification"] = verification("fact", f["id"], value=20)
        if name == "open_same_family_verified":
            f["verification"]["verifier"]["model_family"] = "family-a"
    elif name.startswith("redirected"):
        ref.update(source_id="open", resolved_urls=["https://docs.x.ai/pricing"])
        if name == "redirected_verified":
            f["verification"] = verification("fact", f["id"], value=20)
    elif name.startswith("mixed_sources"):
        f["sources"].append({**ref, "source_id": "open"})
        if name == "mixed_sources_verified":
            f["verification"] = verification("fact", f["id"], value=20)
    elif name.startswith("latest_"):
        log = [verification("fact", f["id"], "verified", day="2026-10-01", value=20),
               verification("fact", f["id"], name.removeprefix("latest_"), day="2026-10-02",
                            value=20)]
    elif name == "same_day_log_wins":
        f["verification"] = verification("fact", f["id"], value=20)
        log = [verification("fact", f["id"], "mismatch", value=20)]
    return f, log


CASES = ["cited", "unknown", "bad_hash", "empty_regions", "blank_region", "whitespace_region",
         "invalid_value", "no_sources", "unregistered_source", "mismatch", "unreachable",
         "verified", "open_unverified", "open_verified", "open_same_family_verified",
         "redirected", "redirected_verified", "mixed_sources", "mixed_sources_verified",
         "latest_mismatch", "latest_unreachable",
         "latest_verified", "same_day_log_wins"]


@pytest.mark.parametrize("name", CASES)
def test_helper_matches_the_snapshot(tmp_path, name):
    f, log = _case(name)

    helper, snapshot = both(tmp_path, [subscription("sambanova", "plus", facts=[f])], log)

    assert helper == snapshot


def test_parity_cases_cover_admission_and_exclusion(tmp_path):
    admitted = {name for name in CASES
                if both(tmp_path / name, [subscription("sambanova", "plus", facts=[_case(name)[0]])],
                        _case(name)[1])[0]["sambanova/subscription/plus"]}
    assert admitted == {"cited", "verified", "open_verified", "redirected_verified",
                        "mixed_sources", "mixed_sources_verified", "latest_verified"}


@pytest.mark.parametrize("name", ["mixed_sources", "mixed_sources_verified"])
def test_a_mixed_citation_fact_is_admitted_as_cited_with_every_ref(tmp_path, name):
    """MODEL-439: a cited ref mixed with another enters as cited, never as verified."""
    f, log = _case(name)
    row = subscription("sambanova", "plus", facts=[f])

    helper, snapshot = both(tmp_path, [row], log)

    expected = {PRICE: FactValue("known", 20, ("cited", "open"))}
    assert helper == {"sambanova/subscription/plus": expected}
    assert snapshot == helper
    index = load_built_snapshot(build_snapshot(
        SnapshotInputs(subscriptions=[row], sources=URLS, verifications=list(log)),
        registry=REGISTRY, as_of=DAY))
    (offering,) = index.subscription_offerings()
    record = index.record(offering["facts"][PRICE].record_id)
    assert record["verification"] is None
    assert record["citation"]["status"] == "cited"
    assert [ref["source_id"] for ref in record["sources"]] == ["cited", "open"]


def test_a_raw_cited_fact_without_id_or_subject_is_admitted_as_the_snapshot_admits_it(tmp_path):
    """Raw YAML rows may omit id and subject; collect_repo adds them before validating."""
    price = plan_fact("plus", PRICE, 8)
    del price["id"], price["subject"]
    row = subscription("sambanova", "plus", facts=[price])
    root = repository(tmp_path)
    (root / "offerings/subscriptions").mkdir(parents=True)
    (root / "offerings/subscriptions/sambanova.yaml").write_text(yaml.safe_dump([row]))

    helper = admitted_subscription_facts(root, {"sambanova/subscription/plus": row}, DAY,
                                         registry=REGISTRY)
    index = load_built_snapshot(build_snapshot(collect_repo(root), registry=REGISTRY, as_of=DAY))
    snapshot = {sub["id"]: sub["facts"] for sub in index.subscription_offerings()}

    assert helper == {"sambanova/subscription/plus": {PRICE: FactValue("known", 8, ("cited",))}}
    assert snapshot == helper
