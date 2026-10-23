"""Offline MODEL-435 fact and candidate replay; never writes source bytes."""

from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from decision.model import Fact, Source, SourceRef, VerificationActor
from decision.registry import default
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, StoredRegions, deterministic_extractors
from decision.verify import verify as verify_claim
from scripts.accuracy import _latest_collected_claims
from scripts.data_trust.catalogue import load
from scripts.data_trust.sample import claim_for

AS_OF = date(2026, 10, 20)


class ExistingCopies(CopyStore):
    def __init__(self, locations):
        self.files = {}
        self.scanned = 0
        for root in locations:
            for path in sorted(root.rglob("*")):
                if not path.is_file() or path.is_symlink() or ".git" in path.parts:
                    continue
                raw = path.read_bytes()
                if path.suffix == ".gz":
                    try:
                        raw = gzip.decompress(raw)
                    except (OSError, EOFError):
                        continue
                self.scanned += 1
                ref = "sha256:" + hashlib.sha256(raw).hexdigest()
                self.files.setdefault(ref, path)

    def citation(self, ref):
        return None

    def has(self, ref):
        return ref in self.files

    def get(self, ref, *, source_url=None):
        path = self.files[ref]
        raw = path.read_bytes()
        if path.suffix == ".gz":
            raw = gzip.decompress(raw)
        assert "sha256:" + hashlib.sha256(raw).hexdigest() == ref
        return raw

    def put(self, *args, **kwargs):
        raise RuntimeError("Read-only audit store")


def result_dict(result):
    return {
        "outcome": result.outcome,
        "reason": result.reason,
        "diffs": [d.to_dict() for d in result.diffs],
        "verifier": result.verification.verifier.model_dump() if result.verification else None,
    }


def git_sha(path):
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--copies", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--compare", type=Path)
    parser.add_argument(
        "--summary-out", type=Path, help="Write only aggregate counts, hashes and diff counts here"
    )
    parser.add_argument(
        "--summary-only", action="store_true", help="Write only aggregate counts to --out"
    )
    parser.add_argument(
        "--require-candidate-copies",
        action="store_true",
        help="Exit 1 if any original mismatch lacks an older same-URL copy",
    )
    args = parser.parse_args()
    data = args.data
    registry = default()
    sources = load_sources(data / "registry/sources.yaml")
    catalogue = load(data)
    catalogue.claims = {
        (c.target.kind, c.target.id): c
        for c in _latest_collected_claims(data / "verification/queue/events.jsonl")
    }
    store = ExistingCopies([data, *args.copies])
    regions = StoredRegions(store, sources, cache_documents=True)
    extractors = deterministic_extractors()
    by_url = defaultdict(set)
    registered_refs = defaultdict(set)
    for c in catalogue.claims.values():
        for s in c.sources:
            registered_refs[s.source_id].add(s.snapshot_ref)
    # Historical queued claims retain snapshot references as well as current claims.
    for line in (data / "verification/queue/events.jsonl").read_text().splitlines():
        if line.strip():
            event = json.loads(line)
            for s in event.get("claim", {}).get("sources", []):
                registered_refs[s["source_id"]].add(s["snapshot_ref"])
    facts = []
    for f in catalogue.facts:
        if f["kind"] != "fact":
            continue
        sid = f["subject_id"]
        parent = catalogue.offerings.get(sid, {})
        anthropic = (
            sid.startswith("anthropic/")
            or parent.get("provider") == "anthropic"
            or str(parent.get("model", "")).startswith("anthropic/")
        )
        if not anthropic:
            continue
        kind = (
            "model"
            if sid in catalogue.models
            else "subscription"
            if "/subscription/" in sid
            else "offering"
        )
        refs = f.get("sources") or []
        for ref in refs:
            registered_refs[ref["source_id"]].add(ref["snapshot_ref"])
        row = {
            "id": f["id"],
            "subject": sid,
            "kind": kind,
            "facet": f["field"],
            "state": f.get("state"),
            "value": f["value"],
            "effective_from": f.get("effective_from"),
            "effective_until": f.get("effective_until"),
            "stored_verification_outcome": (f.get("verification") or {}).get("outcome"),
            "sources": [
                {
                    **ref,
                    "url": str(sources[ref["source_id"]].url)
                    if ref["source_id"] in sources
                    else None,
                    "copy_available": store.has(ref["snapshot_ref"]),
                }
                for ref in refs
            ],
        }
        if f.get("state") == "unknown":
            row["replay"] = {"outcome": "not_a_claim", "reason": "unknown has no value to verify"}
        elif not refs:
            row["replay"] = {"outcome": "unreachable", "reason": "filed fact has no sources"}
        else:
            claim = claim_for(f, catalogue, registry)
            # Preserve original labels and names but audit the current fact's own copies.
            claim = replace(claim, sources=tuple(SourceRef.model_validate(ref) for ref in refs))
            row["claim_names"] = list(claim.names)
            row["claim_label"] = claim.label
            row["replay"] = result_dict(verify_claim(claim, regions, extractors, today=AS_OF))
        facts.append(row)
    for sid, refs in registered_refs.items():
        if sid in sources:
            by_url[str(sources[sid].url)].update(refs)
    candidates_doc = json.loads((data / "research/model-430/reader-results.json").read_text())
    manifest = {
        row["source_id"]: row
        for row in json.loads((data / "research/model-430/sources/manifest.json").read_text())
    }
    candidate_spec = ast.parse(
        (data / "docs/evidence/g2-ios/MODEL-430/verify_sources.py").read_text()
    )
    labels = {}
    for node in candidate_spec.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name)
            and target.id in {"MODEL_CANDIDATES", "OFFERING_CANDIDATES"}
            for target in node.targets
        ):
            for row in node.value.elts:
                labels[ast.literal_eval(row.elts[0])] = ast.literal_eval(row.elts[4])
    removed_capture_refs = {capture["snapshot_ref"] for capture in manifest.values()}
    candidates = []
    actor = VerificationActor(
        agent="codex-model-435-audit", model_family="openai", method="retained-snapshot-audit"
    )
    for previous in candidates_doc["rows"]:
        fact = Fact.model_validate(previous["candidate"], context={"registry": registry})
        source_id = fact.sources[0].source_id
        captured = manifest[source_id]
        eligible_refs = sorted(
            ref
            for ref in by_url[captured["url"]]
            if store.has(ref) and ref not in removed_capture_refs
        )
        row = {
            "id": fact.id,
            "facet": fact.facet,
            "state": fact.state,
            "candidate_value": fact.value,
            "url": captured["url"],
            "removed_capture_ref": captured["snapshot_ref"],
            "historical_outcome": previous["outcome"],
            "retained_replays": [],
        }
        if not eligible_refs:
            row["replay_status"] = "unavailable_no_retained_same_url_copy"
        for ref in eligible_refs:
            # Whole-page source mirrors the original MODEL-430 probe, with older bytes.
            replay_source = Source.model_validate(
                {
                    "id": source_id,
                    "url": captured["url"],
                    "normaliser": captured["normaliser"],
                    "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}],
                }
            )
            replay_regions = StoredRegions(
                store, {**sources, source_id: replay_source}, cache_documents=True
            )
            claim = Claim.from_fact(
                fact,
                names=("Claude Haiku 5.5", "claude-haiku-5-5"),
                collector=actor,
                unit=registry.facet(fact.facet).unit,
                label=labels[fact.facet],
            )
            claim = replace(
                claim,
                sources=(SourceRef(source_id=source_id, snapshot_ref=ref, cited_regions=["page"]),),
            )
            result = verify_claim(claim, replay_regions, extractors, today=AS_OF)
            row["retained_replays"].append(
                {"snapshot_ref": ref, "copy_path": str(store.files[ref]), **result_dict(result)}
            )
            row["replay_status"] = "older_same_url_copy_replayed"
        candidates.append(row)
    facts.sort(key=lambda row: json.dumps(row, sort_keys=True, default=str))
    targeted_source_ids = {
        sid
        for sid, source in sources.items()
        if urlsplit(str(source.url)).hostname in {"platform.claude.com", "privacy.claude.com"}
    }
    targeted_refs = {ref for sid in targeted_source_ids for ref in registered_refs[sid]}
    all_refs = {source["snapshot_ref"] for row in facts for source in row["sources"]}
    available_refs = {ref for ref in all_refs if store.has(ref)}
    source_inputs = sorted(
        (ref, hashlib.sha256(store.get(ref)).hexdigest()) for ref in available_refs
    )
    report = {
        "as_of": str(AS_OF),
        "engine_sha": git_sha(Path.cwd()),
        "data_sha": git_sha(data),
        "retention": (
            "Existing bytes read in place; no network, source copying, fact writes "
            "or verification-log writes."
        ),
        "limits": (
            "Historical MODEL-430 outcomes used removed captures. Older same-URL copies "
            "can differ; historical outcomes are not reasserted."
        ),
        "scanned_files": store.scanned,
        "scope": (
            "All authored facts on Anthropic models, offerings of Anthropic models on every "
            "provider, and Anthropic subscriptions. Inherited and computed snapshot facts "
            "are outside authored reader replay."
        ),
        "targeted_source_coverage": {
            "registered_platform_privacy_sources": len(targeted_source_ids),
            "historical_and_current_unique_snapshot_refs": len(targeted_refs),
            "available_snapshot_refs": sum(store.has(ref) for ref in targeted_refs),
        },
        "full_authored_facts_digest": hashlib.sha256(
            json.dumps(facts, sort_keys=True, default=str).encode()
        ).hexdigest(),
        "available_source_bytes_digest": hashlib.sha256(
            json.dumps(source_inputs).encode()
        ).hexdigest(),
        "counts": {
            "facts": len(facts),
            "facts_by_kind": dict(Counter(r["kind"] for r in facts)),
            "replay_outcomes": dict(Counter(r["replay"]["outcome"] for r in facts)),
            "available_fact_citations": sum(
                s["copy_available"] for r in facts for s in r["sources"]
            ),
            "fact_citations": sum(len(r["sources"]) for r in facts),
            "unique_fact_snapshot_refs": len(all_refs),
            "unique_available_fact_snapshot_refs": len(available_refs),
            "unique_unavailable_fact_snapshot_refs": len(all_refs - available_refs),
            "candidate_original_mismatches": sum(
                r["historical_outcome"] == "mismatch" for r in candidates
            ),
            "candidate_original_mismatches_without_copies": sum(
                r["historical_outcome"] == "mismatch" and not r["retained_replays"]
                for r in candidates
            ),
            "candidates": len(candidates),
            "candidate_replay_status": dict(Counter(r["replay_status"] for r in candidates)),
        },
        "facts": facts,
        "candidates": candidates,
    }
    if args.compare:
        old = json.loads(args.compare.read_text())

        def grouped(rows):
            groups = defaultdict(list)
            for row in rows:
                groups[row["id"]].append(row)
            return {
                key: sorted(rows, key=lambda row: json.dumps(row, sort_keys=True, default=str))
                for key, rows in groups.items()
            }

        old_facts, new_facts = grouped(old["facts"]), grouped(facts)
        old_candidates, new_candidates = grouped(old["candidates"]), grouped(candidates)
        report["comparison"] = {
            "changed_facts": [
                {"id": key, "before": old_facts.get(key), "after": new_facts.get(key)}
                for key in sorted(old_facts.keys() | new_facts.keys())
                if old_facts.get(key) != new_facts.get(key)
            ],
            "full_authored_facts_equal": old_facts == new_facts,
            "candidate_outcome_changes": [
                {"id": key, "before": old_candidates.get(key), "after": new_candidates.get(key)}
                for key in sorted(old_candidates.keys() | new_candidates.keys())
                if old_candidates.get(key) != new_candidates.get(key)
            ],
        }
    summary = {
        key: report[key]
        for key in (
            "as_of",
            "engine_sha",
            "data_sha",
            "retention",
            "limits",
            "scanned_files",
            "scope",
            "targeted_source_coverage",
            "full_authored_facts_digest",
            "available_source_bytes_digest",
            "counts",
        )
    }
    summary["comparison"] = (
        None
        if "comparison" not in report
        else {
            "changed_facts": len(report["comparison"]["changed_facts"]),
            "full_authored_facts_equal": report["comparison"]["full_authored_facts_equal"],
            "candidate_outcome_changes": len(report["comparison"]["candidate_outcome_changes"]),
            "available_source_bytes_unchanged": old["available_source_bytes_digest"]
            == report["available_source_bytes_digest"],
        }
    )
    summary["input_readiness_passed"] = (
        report["counts"]["candidate_original_mismatches_without_copies"] == 0
    )
    args.out.write_text(
        json.dumps(summary if args.summary_only else report, indent=2, sort_keys=True, default=str)
        + "\n"
    )
    if args.summary_out:
        args.summary_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))
    if args.require_candidate_copies and not summary["input_readiness_passed"]:
        print(
            "INPUT READINESS FAILED: original mismatches lack eligible retained same-URL copies; "
            "parser regression coverage is unavailable."
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
