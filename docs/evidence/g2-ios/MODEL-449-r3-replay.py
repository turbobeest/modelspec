"""Read-only comparison of current sourced facts and evidence against retained bytes.

Run once with --revision for a baseline and again without it using --compare.
Reports contain private identifiers and page evidence; keep them outside public git.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import types


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--revision", help="Read this revision's verifier; otherwise working file")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    engine, root = args.engine.resolve(), args.data.resolve()
    sys.path.insert(0, str(engine))

    def no_network(*_args, **_kwargs):
        raise AssertionError("private replay prohibits network access")

    socket.socket.connect = no_network
    socket.socket.connect_ex = no_network
    socket.create_connection = no_network
    source = (git(engine, "show", args.revision + ":decision/verify.py")
              if args.revision else (engine / "decision/verify.py").read_bytes())
    import decision
    module = types.ModuleType("decision.verify")
    module.__file__ = str(engine / "decision/verify.py")
    module.__package__ = "decision"
    sys.modules["decision.verify"] = module
    decision.verify = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    module.REPO_ROOT = root

    from decision.model import Fact, VerificationActor, fact_verification_value, evidence_verification_value
    from decision.retention import cite_only_origin_restrictive, canonical_host
    from decision.sources import CopyStore, load_sources
    from decision.snapshot import collect_repo, _Compiler
    from pipeline.load import load_models

    tracked = [Path(name) for name in git(root, "ls-files", "-z").decode().split("\0") if name]
    before = {str(path): hashlib.sha256((root / path).read_bytes()).hexdigest()
              for path in tracked if (root / path).is_file()}
    inputs = collect_repo(root)
    sources = load_sources(root / "registry/sources.yaml")
    filed = module.Queue(root / "verification").filed()
    compiler = _Compiler(inputs, registry=None, guard=None, as_of=date(2026, 11, 5))
    raw_facts = [fact for owner in [*inputs.models, *inputs.offerings, *inputs.subscriptions]
                 for fact in owner["facts"]]
    for lab in inputs.labs.values():
        if lab.state == "known":
            raw_facts.append(lab.fact())
        else:
            raw_facts.append({
                "id": f"lab:{lab.id}#origin.lab_jurisdiction",
                "subject": {"kind": "model", "id": f"lab:{lab.id}"},
                "facet": "origin.lab_jurisdiction",
                "state": "unknown" if lab.state == "gap" else lab.state,
                "value": None,
                "sources": [{k: v for k, v in source.items() if k != "party"}
                            for source in lab.sources],
            })
    cards = {card.model_id: card for card in load_models(root)}
    names_by_subject = defaultdict(list)
    collectors = {}
    for claim in filed.values():
        names_by_subject[claim.subject].extend(claim.names)
        collectors.setdefault(claim.subject, claim.collector)
    for mid, card in cards.items():
        names_by_subject[mid].extend(n for n in (card.front.get("display_name"), mid.rsplit("/", 1)[-1]) if n)
    for offering in inputs.offerings:
        oid = f"{offering['provider']}/{offering['model']}/{offering['region']}/{offering['tier']}"
        names_by_subject[oid].extend(names_by_subject[offering["model"]])
    for plan in inputs.subscriptions:
        sid = f"{plan['provider']}/subscription/{plan['plan']}"
        names_by_subject[sid].extend([plan["name"], plan["plan"]])
    for lab in inputs.labs.values():
        names_by_subject[f"lab:{lab.id}"].extend(n for n in (lab.entity, lab.parent_entity, lab.id) if n)
    fallback_collector = VerificationActor(agent="private-replay-unfiled", model_family="human",
                                           method="existing-catalogue-record@1")
    skipped = []
    records = []
    for kind, raw in [("fact", row) for row in raw_facts] + [("evidence", row) for row in inputs.evidence]:
        if not raw.get("sources") or (kind == "fact" and raw["state"] == "unknown"):
            skipped.append({"kind": kind, "id": raw.get("id"), "reason": "unknown" if raw.get("state") == "unknown" else "no_sources"})
            continue
        record = Fact.model_validate(raw) if kind == "fact" else types.SimpleNamespace(id=raw["id"])
        original = filed.get((kind, raw["id"]))
        subject = raw["subject"]["id"]
        names = original.names if original else tuple(dict.fromkeys(names_by_subject[subject]))
        assert names, f"missing catalogue names for {kind}:{record.id}"
        collector = original.collector if original else collectors.get(subject, fallback_collector)
        if kind == "fact":
            claim = module.Claim.from_fact(record, names=names, collector=collector,
                                           label=original.label if original else None,
                                           unit=original.unit if original else None,
                                           base_model=original.base_model if original else None)
            verification_value = fact_verification_value(raw)
        else:
            verification_value = evidence_verification_value(raw)
            claim = module.Claim.from_dict({
                "target": {"kind": kind, "id": raw["id"]}, "subject": subject,
                "names": names, "field": raw["benchmark_id"], "value": verification_value,
                "unit": raw.get("unit"), "label": original.label if original else None,
                "conditions": {"effort": raw.get("effort"), "harness": raw.get("harness"),
                               "date": raw.get("evidence_date")},
                "collector": collector.model_dump(), "sources": raw["sources"],
            })
        authored, unsure = compiler._verdicts(kind, record.id, raw.get("verification"),
                                             verification_value, raw.get("facet"))
        records.append((record, claim, original, authored, unsure))
    keys = [(c.target.kind, c.target.id) for _, c, _, _, _ in records]
    assert len(keys) == len(set(keys)), "duplicate current target"
    current_keys = set(keys) | {(row["kind"], row["id"]) for row in skipped}
    wanted = {ref.snapshot_ref for _, claim, _, _, _ in records for ref in claim.sources
              if ref.source_id in sources and not cite_only_origin_restrictive(sources[ref.source_id].url, ref.resolved_urls)}
    copies = {}
    for relative in tracked:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            continue
        try:
            digest = hashlib.sha256()
            with (gzip.open(path, "rb") if path.suffix == ".gz" else path.open("rb")) as handle:
                while block := handle.read(1024 * 1024):
                    digest.update(block)
            ref = "sha256:" + digest.hexdigest()
            if ref in wanted:
                copies.setdefault(ref, path)
        except (OSError, EOFError):
            continue

    class ArchiveStore(CopyStore):
        def has(self, ref):
            return ref in copies

        def get(self, ref, *, source_url=None):
            if source_url is not None and cite_only_origin_restrictive(source_url):
                raise ValueError("cite-only source cannot be read")
            path = copies[ref]
            body = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
            assert "sha256:" + hashlib.sha256(body).hexdigest() == ref
            return body

        def citation(self, ref):
            return None

        def put(self, *_args, **_kwargs):
            raise AssertionError("read-only replay")

        def record_citation(self, *_args, **_kwargs):
            raise AssertionError("read-only replay")

    assert not list(root.rglob("*.citation.json")), "Add read-only citation lookup before replay"
    regions = module.StoredRegions(ArchiveStore(root / "unused-copy-store"), sources,
                                   cache_documents=True)
    readers = module.deterministic_extractors()
    rows = []
    for index, (record, claim, original, authored, unsure) in enumerate(records):
        result = module.verify(claim, regions, readers, today=date(2026, 11, 5))
        rows.append({
            "kind": claim.target.kind, "id": claim.target.id, "field": claim.field,
            "state": getattr(record, "state", None), "value": claim.value,
            "outcome": result.outcome, "reason": result.reason,
            "method": result.verification.method if result.verification else None,
            "diffs": [asdict(diff) for diff in result.diffs],
            "source_count": len(claim.sources),
            "available_source_count": sum(ref.snapshot_ref in copies for ref in claim.sources),
            "readable_region_count": sum(
                regions.text(ref.source_id, ref.snapshot_ref, region_id) is not None
                for ref in claim.sources for region_id in ref.cited_regions
                if ref.source_id in sources and not cite_only_origin_restrictive(
                    sources[ref.source_id].url, ref.resolved_urls)),
            "claim_names": list(claim.names), "filed_claim": original is not None,
            "filed_sources_differ": original is not None and original.sources != claim.sources,
            "filed_value_differs": original is not None and original.value != claim.value,
            "authored_outcome": authored["outcome"] if authored else None,
            "authored_unsure": unsure,
        })
        if (index + 1) % 500 == 0:
            print(f"Verified {index + 1}/{len(records)} current targets", flush=True)
    after = {str(path): hashlib.sha256((root / path).read_bytes()).hexdigest()
             for path in tracked if (root / path).is_file()}
    assert before == after, "tracked private data changed"
    assert git(root, "status", "--porcelain") == b"", "private checkout changed"
    summary = {
        "data_sha": git(root, "rev-parse", "HEAD").decode().strip(),
        "verifier_sha256": hashlib.sha256(source).hexdigest(),
        "revision": args.revision or "working-tree",
        "raw_facts": len(raw_facts), "lab_facts": len(inputs.labs), "raw_evidence": len(inputs.evidence),
        "filed_not_current": dict(Counter(kind for kind, rid in filed if (kind, rid) not in current_keys)),
        "replayed": len(rows), "kinds": dict(Counter(row["kind"] for row in rows)),
        "states": dict(Counter(row["state"] for row in rows if row["kind"] == "fact")),
        "outcomes": dict(Counter(row["outcome"] for row in rows)),
        "outcomes_by_kind": {kind: dict(Counter(row["outcome"] for row in rows if row["kind"] == kind)) for kind in ("fact", "evidence")},
        "no_filed_claim": dict(Counter(row["kind"] for row in rows if not row["filed_claim"])),
        "skipped": dict(Counter(f"{row['kind']}:{row['reason']}" for row in skipped)),
        "retained_noncited_refs": len(copies), "requested_noncited_refs": len(wanted),
        "targets_with_retained_copy": sum(bool(row["available_source_count"]) for row in rows),
        "targets_with_readable_region": sum(bool(row["readable_region_count"]) for row in rows),
        "methods": dict(Counter(row["method"] or "none" for row in rows)),
        "tracked_files_unchanged": len(before), "network_calls": 0,
    }
    report = {"summary": summary, "records": rows, "unverifiable_records": skipped,
              "copy_index": {ref: str(path.relative_to(root)) for ref, path in sorted(copies.items())}}
    if args.compare:
        baseline = json.loads(args.compare.read_text())
        old = {(r["kind"], r["id"]): r for r in baseline["records"]}
        assert set(old) == set(keys)
        compare_fields = ("outcome", "reason", "method", "diffs")
        terms_path = root / "registry/source-terms.json"
        terms = json.loads(terms_path.read_text()) if terms_path.exists() else {}
        changed = []
        for row, (_, claim, _, _, _) in zip(rows, records):
            previous = old[(row["kind"], row["id"])]
            if all(previous[k] == row[k] for k in compare_fields):
                continue
            pages = []
            for ref in claim.sources:
                registered = sources.get(ref.source_id)
                page = {"source": ref.model_dump(mode="json"), "url": str(registered.url) if registered else None,
                        "retained_path": str(copies[ref.snapshot_ref].relative_to(root)) if ref.snapshot_ref in copies else None,
                        "regions": []}
                if registered and not cite_only_origin_restrictive(registered.url, ref.resolved_urls):
                    retain_text = all(terms.get(canonical_host(url)) in {"permits", "restricts"}
                                      for url in (registered.url, *ref.resolved_urls))
                    page["source_terms_allow_new_text"] = retain_text
                    for region_id in ref.cited_regions:
                        text = regions.text(ref.source_id, ref.snapshot_ref, region_id)
                        page["regions"].append({
                            "id": region_id,
                            "text": text if retain_text else None,
                            "normalised_sha256": hashlib.sha256(text.encode()).hexdigest() if text is not None else None,
                            "line_count": len(text.splitlines()) if text is not None else None,
                        })
                pages.append(page)
            changed.append({"before": previous, "after": row, "pages": pages})
        report["comparison"] = {
            "baseline_summary": baseline["summary"],
            "changed_records": changed,
            "outcome_changes": sum(item["before"]["outcome"] != item["after"]["outcome"] for item in changed),
            "baseline_verified_flips": sum(item["before"]["outcome"] == "verified" and item["after"]["outcome"] != "verified" for item in changed),
            "authored_verified_flips": sum(item["before"]["outcome"] == "verified" and item["after"]["outcome"] != "verified" and item["after"]["authored_outcome"] == "verified" for item in changed),
        }
        print(json.dumps({k: v for k, v in report["comparison"].items() if k not in {"changed_records", "baseline_summary"}}), flush=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
