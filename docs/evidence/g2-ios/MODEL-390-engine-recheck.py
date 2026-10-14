"""Recheck MODEL-390 from retained copies without changing the data checkout.

Run from the engine worktree with PYTHONPATH=$PWD and Python's -B flag.
Source bytes live only in a temporary directory outside both checkouts. New
verification records stay in memory. Output contains aggregate counts only.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import subprocess
import sys
from collections import Counter
from dataclasses import replace
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from decision.excluded import excluded_sources
from decision.model import Fact, VerificationActor
from decision.snapshot import (
    CompletenessError,
    build_snapshot,
    collect_repo,
    default_registry,
    load_premier,
)
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, StoredRegions, deterministic_extractors, verify
from scripts.accuracy import verify_fidelity_sample


class MemoryLog:
    def __init__(self):
        self.records = []

    def append(self, record):
        self.records.append(record)


class MemoryQueue:
    def checked(self, result, *, at):
        pass

    def requeue(self, targets, *, at):
        pass


def refuse_network(event, args):
    if event.startswith("socket."):
        raise RuntimeError("The offline recheck refuses socket operations")


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def gate_summary(inputs, *, registry, premier, as_of):
    try:
        build_snapshot(
            inputs, registry=registry, premier=premier, as_of=as_of,
            guard=excluded_sources(), gate=True,
        )
    except CompletenessError as exc:
        return {
            "status": "fail",
            "gap_count": len(exc.gaps),
            "gaps_by_facet": dict(sorted(Counter(gap.facet for gap in exc.gaps).items())),
        }
    return {"status": "pass", "gap_count": 0, "gaps_by_facet": {}}


def recheck(root, *, today, as_of):
    engine = Path(__file__).resolve().parents[3]
    before = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    sys.addaudithook(refuse_network)
    snapshot_logger = logging.getLogger("decision.snapshot")
    snapshot_logger.addHandler(logging.NullHandler())
    snapshot_logger.propagate = False
    plan = json.loads((root / "research/model-390/resolution.json").read_text())
    manifest = json.loads((root / "research/model-390/http-manifest.json").read_text())
    sources = load_sources(root / "registry/sources.yaml")
    registry = default_registry()
    actor = VerificationActor(
        agent="codex-model-390", model_family="openai",
        method="primary-licence-read@2026-10-14",
    )
    claims = []
    no_snapshot = 0
    for model in plan["models"]:
        mid = model["model"]
        front = yaml.safe_load((root / "models" / (mid + ".md")).read_text().split("---", 2)[1])
        for row in front["facts"]:
            if row["facet"] not in model["values"]:
                continue
            fact = Fact.model_validate({
                "id": mid + "#" + row["facet"], "subject": {"kind": "model", "id": mid}, **row,
            })
            if not fact.sources:
                no_snapshot += 1
                continue
            claims.append(Claim.from_fact(
                fact, names=(front["display_name"], mid), collector=actor,
                unit=registry.facet(fact.facet).unit,
            ))
    kinds = {
        ref.source_id: sources[ref.source_id].kind for claim in claims for ref in claim.sources
    }
    if any(kind is None for kind in kinds.values()):
        raise ValueError("Unknown source kind in the targeted licence set")
    outcomes = Counter()
    kind_mismatches = 0
    new_verifications = []
    with TemporaryDirectory(prefix="modelspec-model-390-", dir="/tmp") as scratch:
        store = CopyStore(Path(scratch) / "source-cache")
        for row in manifest:
            if "copy" not in row:
                continue
            body = gzip.decompress((root / row["copy"]).read_bytes())
            if hashlib.sha256(body).hexdigest() != row["sha256"]:
                raise ValueError("A retained copy differs from the HTTP manifest")
            if store.put(body) != "sha256:" + row["sha256"]:
                raise ValueError("A retained copy differs from its storage digest")
        regions = StoredRegions(store, sources, cache_documents=True)
        readers = deterministic_extractors()
        for claim in claims:
            result = verify(claim, regions, readers, today=today)
            outcomes[result.outcome] += 1
            kind_mismatches += any(diff.field == "source_kind" for diff in result.diffs)
            if result.verification is not None:
                new_verifications.append(result.verification)
        plans = yaml.safe_load((root / "offerings/subscriptions/openai.yaml").read_text())
        go = next(plan for plan in plans if plan["plan"] == "go")
        go_fact = Fact.model_validate(next(
            row for row in go["facts"] if row["facet"] == "offering.subscription.models_covered"
        ))
        go_result = verify(
            Claim.from_fact(
                go_fact, names=("ChatGPT Go", "Go"), collector=actor,
                unit=registry.facet(go_fact.facet).unit,
            ),
            regions, readers, today=today,
        )
        if go_result.verification is not None:
            new_verifications.append(go_result.verification)
        fidelity = verify_fidelity_sample(
            claims, regions=regions, extractors=readers, queue=MemoryQueue(), log=MemoryLog(),
            today=today, source_urls={sid: str(source.url) for sid, source in sources.items()},
        )
    inputs = collect_repo(root)
    premier = load_premier(root / "premier/slice-1.yaml")
    stored = gate_summary(inputs, registry=registry, premier=premier, as_of=as_of)
    overlay = replace(inputs, verifications=[
        *inputs.verifications, *[record.model_dump(mode="json") for record in new_verifications],
    ])
    current = gate_summary(overlay, registry=registry, premier=premier, as_of=as_of)
    unchanged = before == git(root, "status", "--porcelain=v1", "--untracked-files=all")
    report = {
        "engine_sha": git(engine, "rev-parse", "HEAD"),
        "engine_tracked_changes": bool(git(
            engine, "status", "--porcelain=v1", "--untracked-files=no",
        )),
        "data_sha": git(root, "rev-parse", "HEAD"),
        "data_engine_pin": (root / ".engine-pin").read_text().strip(),
        "read_date": today.isoformat(), "snapshot_as_of": as_of.isoformat(),
        "licence_fact_count": len(claims) + no_snapshot,
        "cited_licence_fact_count": len(claims),
        "licence_counts": {
            **{name: outcomes[name] for name in ("verified", "skipped", "mismatch", "unreachable")},
            "not_disclosed": no_snapshot,
        },
        "source_kind_mismatches": kind_mismatches,
        "fidelity_status": fidelity.status, "fidelity_counts": fidelity.counts,
        "go_outcome": go_result.outcome, "unknown_source_kinds": 0,
        "network_calls": 0, "completion_calls": 0,
        "stored_premier_gate": stored, "current_verification_premier_gate": current,
        "data_status_unchanged": unchanged,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if (
        unchanged and not no_snapshot and outcomes["verified"] == len(claims)
        and fidelity.status == "pass" and current["status"] == "pass"
        and go_result.outcome == "verified"
    ) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--date", type=date.fromisoformat, default=date(2026, 10, 14))
    parser.add_argument("--as-of", type=date.fromisoformat)
    args = parser.parse_args()
    raise SystemExit(recheck(args.data.resolve(), today=args.date, as_of=args.as_of or args.date))
