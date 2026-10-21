"""Independent source expectations for subscription integration tests."""

import itertools
import json
import re
import subprocess

import yaml

from decision.citation import fact_citation
from decision.model import Fact, Measurement, value_hash, verification_counts
from decision.retention import (
    cite_only_origin_status, cite_only_status, metadata_origins, record_origin_status,
    redirect_urls,
)
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


def _cited_ref(ref, urls, store):
    """Cited by its registered URL or a fetcher record for its hash; never by the card.

    The card's redirects and any store record are validated first, in full;
    anything malformed raises ValueError and the fact stays out.
    """
    registered = urls.get(ref["source_id"], "")
    if cite_only_status(registered) is None:
        raise ValueError("invalid registered source URL")
    if "resolved_urls" in ref:
        redirect_urls(ref["resolved_urls"])
    snapshot_ref = ref.get("snapshot_ref")
    origins = ()
    if store is not None and isinstance(snapshot_ref, str) \
            and re.fullmatch(r"sha256:[0-9a-f]{64}", snapshot_ref):
        try:
            record = store.citation(snapshot_ref)
        except (OSError, AttributeError, TypeError):
            raise ValueError("unreadable citation record") from None
        if record is not None:
            if not isinstance(record, dict) or record.get("snapshot_ref") != snapshot_ref:
                raise ValueError("citation record does not match its hash")
            if record.get("url") != registered:
                raise ValueError("citation record names another source")
            if record_origin_status(record) is None:
                raise ValueError("invalid citation redirect record")
            origins = metadata_origins(record)
    # Granting: only a well-formed cite-only origin makes the ref cited.
    cited = cite_only_origin_status(registered, origins)
    if cited is None:
        raise ValueError("invalid citation origin")
    return cited


def bound_hashes(value, unordered):
    """The value hashes a verification of ``value`` may carry (MODEL-416).

    An unordered set facet binds its members: sorted, or in any order up to
    nine members. Anything else binds the value as filed.
    """
    hashes = {value_hash(value)}
    if unordered and isinstance(value, list):
        hashes.add(value_hash(sorted(value)))
        if len(value) <= 9:
            hashes.update(value_hash(list(order)) for order in itertools.permutations(value))
    return hashes


def admitted_subscription_facts(root, subscriptions, as_of, registry=None, store=None):
    """Project raw facts using the documented second-key and source rules.

    Do not call the snapshot compiler or collector to form its expected output.
    Log entries win same-day ties over inline verification, and later log rows
    win ties with earlier rows. Same-family verified entries do not count.

    A fact whose every source is cite-only, by its registered URL or by a
    redirect in the fetcher's citation record in ``store`` (never by the card's
    own ``resolved_urls``), enters without a verification record
    (docs/design/cite-only-sources.md), unless its citation or record is
    invalid (the fact must validate against ``registry`` as the snapshot
    validates it), it names an identifier facet, or its latest counting
    outcome is a mismatch or unreachable. A fact that mixes a cite-only source
    with another stays out. Every other fact still needs a latest counting
    outcome of verified.

    With ``registry``, an unordered set facet's verification binds its members
    (MODEL-416). A set with a repeated member never enters. Past nine members, a
    failed outcome on another hash of the fact, newer than its bound verdict,
    holds the fact: it may be a legacy row for another order of the same set.
    """
    log = [
        json.loads(line)
        for line in (root / "verification/log.jsonl").read_text().splitlines()
        if line.strip()
    ]
    sources = load_sources(root / "registry/sources.yaml")
    urls = {source_id: str(source.url) for source_id, source in sources.items()}
    expected = {}
    for sid, subscription in subscriptions.items():
        expected[sid] = {}
        for fact in subscription["facts"]:
            if fact["state"] == "unknown":
                continue
            # collect_repo adds the subject and id before the snapshot validates a fact.
            fact = {"subject": {"kind": "offering", "id": sid},
                    "id": f"{sid}#{fact.get('facet')}", **fact}
            fid = fact["id"]
            value = fact.get("value")
            value_type = registry.facet(fact["facet"]).value_type if registry else None
            unordered = getattr(value_type, "unordered", False)
            if (getattr(value_type, "kind", None) == "set" and isinstance(value, list)
                    and len(set(value)) != len(value)):
                continue
            bound = bound_hashes(value, unordered)
            rows = [
                (str(record["date"]), order, record)
                for order, record in enumerate([fact.get("verification"), *log])
                if record
                and record["target"]["kind"] == "fact"
                and record["target"]["id"] == fid
                and verification_counts(
                    record["outcome"],
                    record["collector"]["model_family"],
                    record["verifier"]["model_family"],
                )
            ]
            candidates = [row for row in rows if row[2]["target"].get("value_hash") in bound]
            best = max(candidates, key=lambda row: row[:2]) if candidates else None
            latest = best[2]["outcome"] if best else None
            if unordered and isinstance(value, list) and len(value) > 9:
                # Only the latest row per hash counts, as the snapshot reads the log.
                per_hash = {}
                for row in rows:
                    key = row[2]["target"].get("value_hash")
                    if key not in per_hash or row[:2] >= per_hash[key][:2]:
                        per_hash[key] = row
                if any(key not in bound and row[2]["outcome"] != "verified"
                       and (best is None or row[:2] > best[:2])
                       for key, row in per_hash.items()):
                    continue
            try:
                flags = [_cited_ref(ref, urls, store) for ref in fact.get("sources", [])]
            except ValueError:
                continue
            if any(flags):
                if not all(flags):
                    continue
                if fact["facet"] in {"offering.api_model_id", "offering.router_slug"}:
                    continue
                try:
                    fact_citation(fact, urls, store)
                    Fact.model_validate({**fact, "verification": None},
                                        context={"registry": registry})
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
