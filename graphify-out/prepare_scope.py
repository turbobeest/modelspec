"""Bounded detect + AST for the ModelSpec allowlist. Never run an LLM."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "graphify-out"
MAX_FILES = 40
SPEC_CANDIDATES = [
    Path("/Users/terbeest/.agents/skills/graphify/references/extraction-spec.md"),
    Path("/Users/terbeest/.claude/skills/graphify/references/extraction-spec.md"),
    Path.home() / ".agents/skills/graphify/references/extraction-spec.md",
    Path.home() / ".claude/skills/graphify/references/extraction-spec.md",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_spec() -> Path:
    for path in SPEC_CANDIDATES:
        if path.is_file():
            return path
    raise FileNotFoundError("graphify extraction-spec.md not found")


def abs_source(path: str | Path) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        return str(candidate)
    return str(ROOT / candidate)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    scope = json.loads((OUT / "scope.json").read_text())
    paths = scope["files"]
    if not (0 < len(paths) <= MAX_FILES and len(paths) == len(set(paths))):
        raise SystemExit(f"scope.json must list 1..{MAX_FILES} unique relative paths")
    for name in paths:
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert (ROOT / name).is_file(), name
    hashes = {name: digest(ROOT / name) for name in paths}
    spec = find_spec()
    if args.check:
        manifest = json.loads((OUT / "scope-manifest.json").read_text())
        previous = {row["path"]: row["sha256"] for row in manifest["sources"]}
        changes = sorted(
            name
            for name in previous.keys() | hashes.keys()
            if previous.get(name) != hashes.get(name)
        )
        if digest(OUT / "scope.json") != manifest["scope_sha256"]:
            changes.append("scope.json (scope definition changed)")
        if digest(spec) != manifest["extraction_prompt_sha256"]:
            changes.append("extraction-spec.md (prompt changed)")
        print(
            "STALE: " + ", ".join(changes)
            if changes
            else f"FRESH: all {len(paths)} source hashes, scope, and extraction prompt match"
        )
        return int(bool(changes))

    from graphify.cache import check_semantic_cache
    from graphify.detect import detect
    from graphify.extract import extract

    # Stage outside the worktree. Copies of tests/ under graphify-out/ are
    # collected by pytest and fail because models/ is not in the staged tree.
    stage = Path("/tmp") / f"modelspec-graphify-scope-{ROOT.name}"
    if stage.exists():
        shutil.rmtree(stage)
    for name in paths:
        destination = stage / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    detection = detect(stage, cache_root=ROOT, gitignore=False)
    for category, files in detection["files"].items():
        detection["files"][category] = [
            str(ROOT / Path(f).relative_to(stage)) for f in files
        ]
    detection["scan_root"] = str(ROOT)
    (OUT / ".graphify_detect.json").write_text(json.dumps(detection, indent=2))
    (OUT / ".graphify_python").write_text(sys.executable)
    (OUT / ".graphify_root").unlink(missing_ok=True)

    code_files = [Path(f) for f in detection["files"].get("code", [])]
    if code_files:
        ast = extract(code_files, cache_root=ROOT)
        for node in ast["nodes"]:
            node["source_file"] = abs_source(node["source_file"])
        for edge in ast.get("edges", []):
            if edge.get("source_file"):
                edge["source_file"] = abs_source(edge["source_file"])
        keep = {
            n["id"]
            for n in ast["nodes"]
            if n.get("source_location") and Path(n["source_file"]).is_file()
        }
        ast["nodes"] = [n for n in ast["nodes"] if n["id"] in keep]
        ast["edges"] = [
            e
            for e in ast.get("edges", [])
            if e.get("source") in keep and e.get("target") in keep
        ]
    else:
        ast = {"nodes": [], "edges": [], "input_tokens": 0, "output_tokens": 0}
    (OUT / ".graphify_ast.json").write_text(json.dumps(ast, indent=2))

    documents = detection["files"].get("document", [])
    nodes, edges, hyperedges, uncached = check_semantic_cache(
        documents, root=ROOT, prompt_file=str(spec), cache_root=ROOT
    )
    cached = OUT / ".graphify_cached.json"
    if nodes or edges or hyperedges:
        cached.write_text(
            json.dumps(
                {"nodes": nodes, "edges": edges, "hyperedges": hyperedges}
            )
        )
    else:
        cached.unlink(missing_ok=True)
    (OUT / ".graphify_uncached.txt").write_text("\n".join(uncached))
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    (OUT / ".build-source-snapshot.json").write_text(
        json.dumps(
            {
                "source_commit": commit,
                "source_hashes": hashes,
                "extraction_spec": str(spec),
            },
            indent=2,
        )
        + "\n"
    )
    detected = detection["total_files"]
    print(
        f"Corpus: {detected} files, ~{detection['total_words']} words; "
        f"AST {len(ast['nodes'])} nodes / {len(ast['edges'])} edges; "
        f"semantic cache {len(documents) - len(uncached)} hit / "
        f"{len(uncached)} uncached; sensitive skipped: "
        f"{detection.get('skipped_sensitive', [])}"
    )
    if detected != len(paths):
        raise SystemExit(
            f"detect saw {detected} files, scope lists {len(paths)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
