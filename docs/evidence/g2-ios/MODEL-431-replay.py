"""Replay the filed Kimi facts from a caller-supplied private data checkout.

This is read-only and offline. It never writes source text, data facts, queue
events, or verification records. Prose readings are reported as hashes and
lengths so the resulting report can be reviewed without page quotations.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import subprocess
import sys
import types
from collections import Counter
from datetime import date
from pathlib import Path

import yaml


def git_output(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def verifier_source(root: Path, revision: str | None) -> bytes:
    if revision is None:
        return (root / "decision/verify.py").read_bytes()
    return subprocess.run(
        ["git", "-C", str(root), "show", f"{revision}:decision/verify.py"],
        check=True, capture_output=True,
    ).stdout


def verifier(root: Path, revision: str | None):
    if revision is None:
        return importlib.import_module("decision.verify")
    module = types.ModuleType("decision._model431_baseline")
    module.__package__ = "decision"
    module.__file__ = str(root / "decision/verify.py")
    sys.modules[module.__name__] = module
    source = verifier_source(root, revision)
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def value_summary(value):
    if not isinstance(value, str) or value in {
        "monthly", "annual", "existing_subscribers_only", "available", "retired"
    } or re.fullmatch(r"[0-9,.]+", value):
        return value
    return {
        "sha256": hashlib.sha256(value.encode()).hexdigest(),
        "characters": len(value),
        "words": len(value.split()),
    }


def reading_summary(reading):
    return {
        "subject": reading.subject,
        "value": value_summary(reading.value),
        "unit": reading.unit,
        "conditions": dict(reading.conditions),
    }


def diff_summary(diff):
    record = diff.to_dict()
    for key in ("expected", "found"):
        if key in record:
            record[key] = value_summary(record[key])
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--base-ref")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--expect-fixed", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo.resolve()))
    from decision.model import SourceRef, TargetRef, VerificationActor
    from decision.sources import CopyStore, load_sources

    v = verifier(args.repo, args.base_ref)
    offerings = yaml.safe_load(
        (args.data / "offerings/subscriptions/moonshot.yaml").read_text()
    )
    source_registry = load_sources(args.data / "registry/sources.yaml")
    store = CopyStore()
    regions = v.StoredRegions(store, source_registry, cache_documents=True)
    filed = v.Queue(args.data / "verification").filed()
    reader = v.SubscriptionPageExtractor()
    collector = VerificationActor(
        agent="model-431-offline-probe", model_family="human",
        method="read-only-replay@1",
    )
    all_facts = [fact for offering in offerings for fact in offering["facts"]]
    copy_refs = sorted({
        source["snapshot_ref"] for fact in all_facts
        for source in fact.get("sources", [])
    })
    copies = [
        {
            "snapshot_ref": ref, "present_and_hash_valid": store.has(ref),
            "citation_only": store.citation(ref) is not None,
        } for ref in copy_refs
    ]
    if not all(copy["present_and_hash_valid"] for copy in copies):
        raise RuntimeError("A cited retained copy is missing or fails its hash check")
    claims = {}
    probes = {}
    for offering in offerings:
        subject = f"moonshot/subscription/{offering['plan']}"
        fallback_names = (offering["name"], offering["plan"].title(), offering["plan"])
        current_sources = next(
            fact["sources"] for fact in offering["facts"]
            if fact["facet"] == "offering.subscription.billing_period"
        )
        for fact in offering["facts"]:
            fid = fact["id"]
            if fact["state"] == "unknown":
                # Unknown facts are not claims. Probe the reader separately
                # against the checked source's current filed snapshot.
                assert {
                    source["source_id"] for source in current_sources
                } <= set(fact["checked_sources"])
                claim = v.Claim(
                    target=TargetRef(kind="fact", id=fid), subject=subject,
                    names=fallback_names, field=fact["facet"], value=None,
                    collector=collector, sources=tuple(
                        SourceRef.model_validate(source) for source in current_sources
                    ),
                )
                readings = [
                    reading_summary(reading)
                    for source in claim.sources for rid in source.cited_regions
                    for reading in reader.extract(
                        claim, regions.text(source.source_id, source.snapshot_ref, rid)
                    )
                ]
                probes[fid] = {
                    "state": "unknown", "has_filed_claim": ("fact", fid) in filed,
                    "candidate_readings": readings,
                }
                continue
            claim = filed.get(("fact", fid))
            if claim is None:
                raise RuntimeError(f"Filed fact lacks a queued claim: {fid}")
            assert claim.value == fact.get("value"), fid
            assert claim.subject == fact["subject"]["id"], fid
            assert claim.field == fact["facet"], fid
            assert claim.sources == tuple(
                SourceRef.model_validate(source) for source in fact["sources"]
            ), fid
            result = v.verify(
                claim, regions, v.deterministic_extractors(), today=date(2026, 10, 20)
            )
            readings = [
                reading_summary(reading)
                for source in claim.sources for rid in source.cited_regions
                for reading in reader.extract(
                    claim, regions.text(source.source_id, source.snapshot_ref, rid)
                )
            ]
            claims[fid] = {
                "outcome": result.outcome,
                "method": result.verification.method if result.verification else None,
                "reason": result.reason,
                "diffs": [diff_summary(diff) for diff in result.diffs],
                "subscription_readings": readings,
            }
    report = {
        "engine_revision": git_output(args.repo, "rev-parse", args.base_ref or "HEAD"),
        "engine_verify_sha256": hashlib.sha256(
            verifier_source(args.repo, args.base_ref)
        ).hexdigest(),
        "private_data_revision": git_output(args.data, "rev-parse", "HEAD"),
        "date": "2026-10-20",
        "copies": copies,
        "fact_count": len(all_facts),
        "claim_count": len(claims),
        "unknown_count": len(probes),
        "outcomes": dict(Counter(item["outcome"] for item in claims.values())),
        "claims": claims,
        "unknown_candidate_probes": probes,
    }
    if args.compare:
        before = json.loads(args.compare.read_text())
        assert before["private_data_revision"] == report["private_data_revision"]
        assert before["claims"].keys() == claims.keys()
        report["outcome_changes"] = [
            {"id": fid, "before": previous["outcome"], "after": claims[fid]["outcome"]}
            for fid, previous in before["claims"].items()
            if previous["outcome"] != claims[fid]["outcome"]
        ]
        report["reading_changes"] = [
            {"id": fid, "before": previous["subscription_readings"],
             "after": claims[fid]["subscription_readings"]}
            for fid, previous in before["claims"].items()
            if previous["subscription_readings"] != claims[fid]["subscription_readings"]
        ]
        report["candidate_changes"] = [
            {"id": fid, "before": previous["candidate_readings"],
             "after": probes[fid]["candidate_readings"]}
            for fid, previous in before["unknown_candidate_probes"].items()
            if previous["candidate_readings"] != probes[fid]["candidate_readings"]
        ]
    if args.expect_fixed:
        if args.compare is None:
            raise ValueError("--expect-fixed requires --compare")
        expected_ids = {
            f"moonshot/subscription/{plan}#offering.subscription.availability"
            for plan in ("andante", "moderato", "allegretto", "allegro")
        }
        assert {
            change["id"] for change in report["outcome_changes"]
        } == expected_ids, report["outcome_changes"]
        assert all(
            change["before"] == "mismatch" and change["after"] == "verified"
            for change in report["outcome_changes"]
        )
        assert report["outcomes"] == {"verified": 48}, report["outcomes"]
        for offering in offerings:
            if offering["plan"] not in {"go", "plus", "pro", "max", "ultra"}:
                continue
            price = next(
                fact for fact in offering["facts"]
                if fact["facet"] == "offering.subscription.price_cny"
            )
            readings = claims[price["id"]]["subscription_readings"]
            assert len(readings) == 1, (price["id"], readings)
            assert float(readings[0]["value"]) == price["value"], (price["id"], readings)
        for fid, probe in probes.items():
            expected_empty = any(
                fid == f"moonshot/subscription/{plan}#offering.subscription.usage_allowance"
                for plan in ("go", "plus")
            )
            assert bool(probe["candidate_readings"]) != expected_empty, fid
            assert not probe["has_filed_claim"], fid
        report["fixed_assertions_passed"] = True
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    summary = {
        key: value for key, value in report.items()
        if key not in {
            "claims", "unknown_candidate_probes", "reading_changes", "candidate_changes"
        }
    }
    for field in ("reading_changes", "candidate_changes"):
        if field in report:
            summary[field] = [item["id"] for item in report[field]]
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
