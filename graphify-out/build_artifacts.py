"""Rebuild scoped graph artifacts after host-agent semantic extraction; no LLM."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from graphify.analyze import god_nodes, suggest_questions, surprising_connections
from graphify.build import build_from_json
from graphify.cache import save_semantic_cache
from graphify.cli import _stamped_manifest_files
from graphify.cluster import cluster, score_all
from graphify.detect import save_manifest
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report
from graphify.export import to_json
from graphify.report import generate

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "graphify-out"


def read(name: str):
    return json.loads((OUT / name).read_text())


def write(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_spec(snapshot: dict) -> Path:
    recorded = Path(snapshot.get("extraction_spec", ""))
    if recorded.is_file():
        return recorded
    from prepare_scope import find_spec as _find

    return _find()


def abs_source(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)
    return str(ROOT / candidate)


def merge_extraction(ast: dict, semantic: dict) -> dict:
    seen = {n["id"] for n in ast.get("nodes", [])}
    nodes = list(ast.get("nodes", []))
    for node in semantic.get("nodes", []):
        if node["id"] not in seen:
            nodes.append(node)
            seen.add(node["id"])
    return {
        "nodes": nodes,
        "edges": list(ast.get("edges", [])) + list(semantic.get("edges", [])),
        "hyperedges": list(semantic.get("hyperedges", [])),
        "input_tokens": semantic.get("input_tokens", 0),
        "output_tokens": semantic.get("output_tokens", 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--labelled",
        action="store_true",
        help="Use labels.json and finalize provenance",
    )
    args = parser.parse_args()
    snapshot = read(".build-source-snapshot.json")
    scope = read("scope.json")
    spec = find_spec(snapshot)
    for name, digest in snapshot["source_hashes"].items():
        if sha(ROOT / name) != digest:
            raise SystemExit(f"Source changed during extraction: {name}")
    detection = read(".graphify_detect.json")
    uncached = [
        line
        for line in (OUT / ".graphify_uncached.txt").read_text().splitlines()
        if line
    ]
    ast = read(".graphify_ast.json")
    if args.labelled:
        extraction = read(".graphify_extract.json")
    else:
        cached = (
            read(".graphify_cached.json")
            if (OUT / ".graphify_cached.json").exists()
            else {"nodes": [], "edges": [], "hyperedges": []}
        )
        chunk_paths = sorted(OUT.glob(".graphify_chunk_*.json"))
        if uncached and not chunk_paths:
            raise SystemExit("Uncached documents need host-agent extraction first")
        semantic = {
            "nodes": [],
            "edges": [],
            "hyperedges": [],
            "input_tokens": 0,
            "output_tokens": 0,
        }
        for chunk_path in chunk_paths:
            part = json.loads(chunk_path.read_text())
            if "nodes" not in part or "edges" not in part:
                raise SystemExit(f"invalid chunk {chunk_path}")
            for key in ("nodes", "edges", "hyperedges"):
                semantic[key].extend(part.get(key, []))
            semantic["input_tokens"] += part.get("input_tokens", 0)
            semantic["output_tokens"] += part.get("output_tokens", 0)
        if uncached:
            saved = save_semantic_cache(
                semantic["nodes"],
                semantic["edges"],
                semantic["hyperedges"],
                root=ROOT,
                allowed_source_files=uncached,
                prompt_file=str(spec),
                cache_root=ROOT,
            )
            print(f"Cached {saved} semantic sources")
        for key in ("nodes", "edges", "hyperedges"):
            semantic[key] = cached.get(key, []) + semantic[key]
        semantic["nodes"] = list({n["id"]: n for n in semantic["nodes"]}.values())
        write("semantic-evidence.json", semantic)
        extraction = merge_extraction(ast, semantic)
        write(".graphify_extract.json", extraction)

    expected = {str(ROOT / name) for name in scope["files"]}
    actual = {abs_source(n["source_file"]) for n in extraction["nodes"]}
    missing = expected - actual
    extra = actual - expected
    if missing:
        raise SystemExit(f"Coverage mismatch: missing={sorted(missing)}")
    if extra:
        print("note: extra source_file values (kept):", sorted(extra)[:8])
    ids = {n["id"] for n in extraction["nodes"]}
    for edge in extraction["edges"]:
        if edge["source"] not in ids or edge["target"] not in ids:
            raise SystemExit(f"edge endpoint missing: {edge}")
        if not edge.get("source_location"):
            raise SystemExit(f"edge missing source_location: {edge}")
    for node in extraction["nodes"]:
        if not node.get("source_location"):
            raise SystemExit(f"node missing source_location: {node['id']}")

    summary = diagnose_extraction(extraction, directed=False, root=str(ROOT))
    write("health.json", summary)
    print(format_diagnostic_report(summary))
    graph = build_from_json(extraction, root=str(ROOT), directed=False)
    if graph.number_of_nodes() == 0:
        raise SystemExit("Graph is empty")
    if args.labelled:
        analysis = read(".graphify_analysis.json")
        communities = {int(k): v for k, v in analysis["communities"].items()}
        labels = {int(k): v for k, v in read("labels.json").items()}
        if set(labels) != set(communities):
            raise SystemExit("labels.json must name every community")
    else:
        communities = cluster(graph)
        labels = {k: f"Community {k}" for k in communities}
    cohesion = score_all(graph, communities)
    gods = god_nodes(graph)
    surprises = surprising_connections(graph, communities)
    questions = suggest_questions(graph, communities, labels)
    if not to_json(
        graph, communities, str(OUT / "graph.json"), community_labels=labels
    ):
        raise SystemExit(
            "Graphify refused to shrink graph; investigate before replacing it"
        )
    tokens = {"input": 0, "output": 0}
    report = generate(
        graph,
        communities,
        cohesion,
        labels,
        gods,
        surprises,
        detection,
        tokens,
        str(ROOT),
        suggested_questions=questions,
    )
    notice = (
        f"> Scope: exactly {len(expected)} files in `scope.json` "
        "(current handoff, CLI/export contract, ranking implementation and tests). "
        "models/** and benchmarks/** are DATA and are excluded; the graph does not "
        "fact-check cards. Raw zero token fields are library placeholders. "
        "Refresh is manual and scoped; see README.md and scope-manifest.json.\n\n"
    )
    report = report.replace(
        "- Token cost: 0 input · 0 output",
        "- Token cost: unavailable (host-session usage not exposed; library zeros are placeholders)",
    )
    (OUT / "GRAPH_REPORT.md").write_text(notice + report)
    write(
        ".graphify_analysis.json",
        {
            "communities": {str(k): v for k, v in communities.items()},
            "cohesion": {str(k): v for k, v in cohesion.items()},
            "gods": gods,
            "surprises": surprises,
            "questions": questions,
        },
    )
    print(
        f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges, "
        f"{len(communities)} communities"
    )
    if not args.labelled:
        for cid, members in communities.items():
            print(
                cid,
                ":",
                ", ".join(graph.nodes[n].get("label", n) for n in list(members)[:12]),
            )
        return

    write(".graphify_labels.json", {str(k): v for k, v in labels.items()})
    stamped = _stamped_manifest_files(detection["files"], extraction, ROOT)
    scan = {f for fl in detection["files"].values() for f in fl}
    save_manifest(stamped, str(OUT / "manifest.json"), root=ROOT, scan_corpus=scan)
    uncached_rel = []
    for path in uncached:
        p = Path(path)
        uncached_rel.append(str(p.relative_to(ROOT)) if p.is_absolute() else path)
    documents = detection["files"].get("document", [])
    manifest = {
        "scope_version": 1,
        "name": scope["name"],
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": snapshot["source_commit"],
        "source_state": "working-tree bytes; commit alone is not freshness proof",
        "graphify_version": version("graphifyy"),
        "scope_sha256": sha(OUT / "scope.json"),
        "extraction_prompt_sha256": sha(spec),
        "extraction_method": "AST for scoped Python; one host-session semantic agent for scoped docs; no external LLM provider",
        "source_count": len(expected),
        "total_words": detection["total_words"],
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "communities": len(communities),
        "directed": False,
        "exclusions": scope["exclusions"],
        "data_policy": scope.get("data_policy"),
        "dpf_contract": scope.get("dpf_contract"),
        "global_registry_tag": scope.get("global_registry_tag"),
        "token_usage": None,
        "token_usage_note": "Not exposed by collaboration tool; library numeric zeros are placeholders",
        "sources": [
            {
                "path": name,
                "sha256": digest,
                "bytes": (ROOT / name).stat().st_size,
            }
            for name, digest in snapshot["source_hashes"].items()
        ],
        "semantic_refresh": {
            "extracted_sources": uncached_rel,
            "extracted_source_count": len(uncached_rel),
            "cached_source_count": max(0, len(documents) - len(uncached)),
            "note": "Uncached documents were semantically extracted this run; code used AST",
        },
    }
    write("scope-manifest.json", manifest)
    cost = read("cost.json") if (OUT / "cost.json").exists() else {"runs": []}
    cost["runs"].append(
        {
            "date": manifest["built_at"],
            "input_tokens": None,
            "output_tokens": None,
            "files": len(expected),
            "extracted_files": len(uncached_rel),
            "cached_files": manifest["semantic_refresh"]["cached_source_count"],
            "method": "AST + host semantic agent",
            "note": "Usage unavailable; no paid external provider invoked",
        }
    )
    cost.update(total_input_tokens=None, total_output_tokens=None)
    write("cost.json", cost)


if __name__ == "__main__":
    main()
