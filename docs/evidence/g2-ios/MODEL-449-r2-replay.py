"""Read-only replay of every authored offering price against committed copies."""

import argparse
from collections import Counter
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
    args = parser.parse_args()
    engine, root = args.engine.resolve(), args.data.resolve()
    sys.path.insert(0, str(engine))

    def no_network(*_args, **_kwargs):
        raise AssertionError("price replay prohibits network access")

    socket.socket.connect = no_network
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

    from decision.model import load_offerings
    from decision.retention import cite_only_origin_restrictive
    from decision.sources import CopyStore, load_sources

    tracked = [Path(name) for name in git(root, "ls-files", "-z").decode().split("\0") if name]
    before = {str(path): hashlib.sha256((root / path).read_bytes()).hexdigest()
              for path in tracked if (root / path).is_file()}
    facts = [fact for path in sorted((root / "offerings").glob("*/*/*.yaml"))
             for offering in load_offerings(path) for fact in offering.facts
             if fact.facet.startswith("offering.price.")]
    sources = load_sources(root / "registry/sources.yaml")
    filed = module.Queue(root / "verification").filed()
    wanted = {ref.snapshot_ref for fact in facts for ref in fact.sources
              if not cite_only_origin_restrictive(sources[ref.source_id].url, ref.resolved_urls)}
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
            # The committed private tree contains no CopyStore citation sidecars.
            # Registered URLs and the fact's resolved URLs still enforce policy.
            return None

        def put(self, *_args, **_kwargs):
            raise AssertionError("read-only price replay")

        def record_citation(self, *_args, **_kwargs):
            raise AssertionError("read-only price replay")

    assert not list(root.rglob("*.citation.json")), "Add read-only citation lookup before replay"
    regions = module.StoredRegions(ArchiveStore(root / "unused-copy-store"), sources,
                                   cache_documents=True)
    readers = module.deterministic_extractors()
    rows = []
    for fact in facts:
        original = filed[("fact", fact.id)]
        claim = module.Claim.from_fact(fact, names=original.names, collector=original.collector,
                                       label=original.label, unit=original.unit,
                                       base_model=original.base_model)
        result = module.verify(claim, regions, readers, today=date(2026, 11, 5))
        rows.append({
            "fact_id": fact.id, "state": fact.state,
            "outcome": result.outcome, "reason": result.reason,
            "method": result.verification.method if result.verification else None,
            "diffs": [asdict(diff) for diff in result.diffs],
            "source_count": len(fact.sources),
            "available_source_count": sum(ref.snapshot_ref in copies for ref in fact.sources),
            "claim_names": list(claim.names),
        })
    after = {str(path): hashlib.sha256((root / path).read_bytes()).hexdigest()
             for path in tracked if (root / path).is_file()}
    assert before == after, "tracked private data changed"
    assert git(root, "status", "--porcelain") == b"", "private checkout changed"
    summary = {
        "data_sha": git(root, "rev-parse", "HEAD").decode().strip(),
        "verifier_sha256": hashlib.sha256(source).hexdigest(),
        "revision": args.revision or "working-tree",
        "price_facts": len(rows),
        "states": dict(Counter(fact.state for fact in facts)),
        "outcomes": dict(Counter(row["outcome"] for row in rows)),
        "retained_noncited_refs": len(copies), "requested_noncited_refs": len(wanted),
        "facts_with_retained_copy": sum(bool(row["available_source_count"]) for row in rows),
        "tracked_files_unchanged": len(before),
        "network_calls": 0,
    }
    args.output.write_text(json.dumps({"summary": summary, "facts": rows}, indent=2) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
