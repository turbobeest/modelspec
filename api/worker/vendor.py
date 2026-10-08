"""Assemble the Worker's Python bundle from the repository's own modules.

MODEL-68. The Worker must not hold a second copy of the scorer, so there is no
copy in git: this script materialises generated packages under
`api/worker/src/`, and `.gitignore` keeps those directories out of the tree. CI
runs it before the bundle is built and before the byte-identity test, so the
thing that is deployed and the thing that is tested are produced by the same
step from the same sources.

The generated packages live beside `src/entry.py`, in the source tree Wrangler
walks for a Python Worker. Pywrangler owns `python_modules/`: every deploy
recreates that directory from the dependency lock, so repository code placed
there before a deploy would be deleted. Both locations are on `sys.path` in the
isolate.

The ranker and decision engine are copied byte for byte. Registry YAML is copied
beside the decision package because it is the decision vocabulary at runtime,
and so are the `hardware/` device files, whose names are the device IDs.

* `api/ranking/engine.py` — the profiles, benchmark ranges, normalisation and
  the floors.
* `api/classes.py` — the class vocabulary used by the facet registry.
* `pipeline/ranking.py` — `Candidate`, `score`, `_basis`, `rank_report`.

The ranker imports only the standard library. The decision path also imports
Pydantic and PyYAML, the two packages declared in the Worker's ``pyproject.toml``.
The check below refuses any undeclared dependency before deployment.
"""

from __future__ import annotations

import json
import traceback
import argparse
import os
import subprocess
import tempfile
import gzip
import base64
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKER_ROOT = Path(__file__).resolve().parent
BUNDLE = WORKER_ROOT / "src"

#: repository path -> path inside the bundle. Copied verbatim; if a copy here
#: ever needed an edit, the two implementations would have forked and the
#: byte-identity test would be measuring a fork against itself.
SOURCES = {
    Path("api/__init__.py"): Path("api/__init__.py"),
    Path("api/ranking/__init__.py"): Path("api/ranking/__init__.py"),
    Path("api/ranking/engine.py"): Path("api/ranking/engine.py"),
    Path("api/classes.py"): Path("api/classes.py"),
    Path("pipeline/__init__.py"): Path("pipeline/__init__.py"),
    Path("pipeline/ranking.py"): Path("pipeline/ranking.py"),
    Path("decision/__init__.py"): Path("decision/__init__.py"),
    Path("decision/bands.py"): Path("decision/bands.py"),
    Path("decision/by_model.py"): Path("decision/by_model.py"),
    Path("decision/capability.py"): Path("decision/capability.py"),
    Path("decision/computed.py"): Path("decision/computed.py"),
    Path("decision/compare.py"): Path("decision/compare.py"),
    Path("decision/contract.py"): Path("decision/contract.py"),
    Path("decision/coverage.py"): Path("decision/coverage.py"),
    Path("decision/engine.py"): Path("decision/engine.py"),
    Path("decision/estate.py"): Path("decision/estate.py"),
    Path("decision/excluded.py"): Path("decision/excluded.py"),
    Path("decision/explain.py"): Path("decision/explain.py"),
    Path("decision/filter.py"): Path("decision/filter.py"),
    Path("decision/model.py"): Path("decision/model.py"),
    Path("decision/normalise.py"): Path("decision/normalise.py"),
    Path("decision/optimise.py"): Path("decision/optimise.py"),
    Path("decision/plans.py"): Path("decision/plans.py"),
    Path("decision/relax.py"): Path("decision/relax.py"),
    Path("decision/reading.py"): Path("decision/reading.py"),
    Path("decision/bounded.py"): Path("decision/bounded.py"),
    Path("decision/summary.py"): Path("decision/summary.py"),
    Path("decision/refinements.py"): Path("decision/refinements.py"),
    Path("decision/registry.py"): Path("decision/registry.py"),
    Path("decision/regions.py"): Path("decision/regions.py"),
    Path("decision/recovery.py"): Path("decision/recovery.py"),
    Path("decision/resolve.py"): Path("decision/resolve.py"),
    Path("decision/snapshot.py"): Path("decision/snapshot.py"),
    Path("decision/templates.py"): Path("decision/templates.py"),
    Path("decision/units.py"): Path("decision/units.py"),
    Path("decision/vocabulary.py"): Path("decision/vocabulary.py"),
    Path("schema/__init__.py"): Path("schema/__init__.py"),
    Path("schema/applicability.py"): Path("schema/applicability.py"),
    # The decision path needs these shared definitions, not every card section.
    # pipeline.ranking imports ModelCard only under TYPE_CHECKING.
    Path("schema/availability.py"): Path("schema/availability.py"),
    Path("schema/evidence.py"): Path("schema/evidence.py"),
    Path("schema/benchmark_values.py"): Path("schema/benchmark_values.py"),
    Path("schema/enums.py"): Path("schema/enums.py"),
    Path("release_signals/__init__.py"): Path("release_signals/__init__.py"),
    Path("release_signals/contract.py"): Path("release_signals/contract.py"),
    Path("registry/domains.yaml"): Path("registry/domains.yaml"),
    Path("registry/facets.yaml"): Path("registry/facets.yaml"),
    Path("registry/families.yaml"): Path("registry/families.yaml"),
    Path("registry/harnesses.yaml"): Path("registry/harnesses.yaml"),
    Path("registry/providers.yaml"): Path("registry/providers.yaml"),
    Path("registry/refinements.yaml"): Path("registry/refinements.yaml"),
    Path("registry/sources.yaml"): Path("registry/sources.yaml"),
    Path("registry/templates.yaml"): Path("registry/templates.yaml"),
    # The device IDs `estate.devices` is checked against are these files' stems
    # (registry `values_from: hardware`). Without them the isolate knew no device
    # and refused every one the page offers (MODEL-203).
    **{
        Path("hardware") / path.name: Path("hardware") / path.name
        for path in sorted((REPO_ROOT / "hardware").glob("*.yaml"))
        if not path.name.startswith("_")
    },
}

GENERATED_ROOTS = {target.parts[0] for target in SOURCES.values()}

#: What the bundle is allowed to need. `schema`, `pydantic` and `yaml` are the
#: ones that would actually show up, and none of them exist in the isolate.
ALLOWED_TOP_LEVEL = {
    "annotated_types",
    "api",
    "cython_runtime",
    "decision",
    "pydantic",
    "pydantic_core",
    "pipeline",
    "release_signals",
    "schema",
    "typing_extensions",
    "typing_inspection",
    "yaml",
}


def build(destination: Path | None = None, *, data_dir: Path | None = None) -> Path:
    """Write the bundle and return its root. Idempotent."""
    out = destination or BUNDLE
    if destination is not None and out.exists():
        shutil.rmtree(out)
    elif destination is None:
        # Keep the hand-written Worker modules in src/. Only these top-level
        # paths belong to the generator, and clearing them removes files that
        # disappeared from SOURCES on a later run.
        for name in GENERATED_ROOTS:
            generated = out / name
            if generated.is_dir():
                shutil.rmtree(generated)
            elif generated.exists():
                generated.unlink()
    sources = {s: t for s, t in SOURCES.items() if s.parts[0] != "hardware"}
    data_root = data_dir or REPO_ROOT
    sources.update({Path("hardware") / p.name: Path("hardware") / p.name
                    for p in sorted((data_root / "hardware").glob("*.yaml"))
                    if not p.name.startswith("_")})
    private = {Path("registry") / (name + ".yaml")
               for name in ("harnesses", "providers", "sources")}
    for source, target in sources.items():
        dest = out / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        source_root = data_root if source in private or source.parts[0] == "hardware" else REPO_ROOT
        shutil.copyfile(source_root / source, dest)
    embedded = out / "bundled_data.py"
    embedded.unlink(missing_ok=True)
    if data_dir is not None:
        bundle_data(out, data_dir)
    return out


def bundle_data(out: Path, data_dir: Path) -> None:
    """Generate private data as an imported module, never a public asset."""
    with tempfile.TemporaryDirectory(prefix="modelspec-worker-") as tmp:
        site = Path(tmp) / "site"
        env = dict(os.environ, DATA_SPLIT_ENABLED="false", MODELSPEC_REQUIRE_DATA_DIR="1")
        # Build output and exceptions may contain private rows. Emit only status.
        completed = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--export-data", str(site),
             "--data-dir", str(data_dir.resolve())],
            cwd=REPO_ROOT, env=env, capture_output=True,
        )
        if completed.returncode:
            # The child emits only path/category diagnostics in private mode.
            for line in completed.stderr.decode("utf-8", errors="replace").splitlines():
                if line.startswith(("Worker bundle build failed: path=", "uncited policy rows:")):
                    print(line, file=sys.stderr)
            raise RuntimeError("private Worker data build failed")
        api = site
        paths = ("rank/candidates.json", "rank/hardware.json", "policy/catalogue.json",
                 "decision/snapshot.json.gz", "decision/vocabulary.json")
        blobs = {}
        for rel in paths:
            raw = (api / rel).read_bytes()
            blobs["/api/" + rel] = base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")
        (out / "bundled_data.py").write_text(
            "# Generated private Worker data. Never publish as a site asset.\n"
            "import base64, gzip\n"
            + "BLOBS = " + repr(blobs) + "\n"
            + "def read(path):\n    value = BLOBS.get(path)\n"
              "    return gzip.decompress(base64.b64decode(value)) if value else None\n",
            encoding="utf-8",
        )


def export_data(out: Path, data_dir: Path) -> None:
    """Build only the exports consumed by the Worker, using the shared builders."""
    sys.path.insert(0, str(REPO_ROOT))
    from datetime import date
    from decision import registry, snapshot
    from pipeline import data_source, export, hardware, policy_export, ranking
    from pipeline.build import write_decision_vocabulary
    from pipeline.load import load_models, load_catalogue
    from schema.card import ModelCard
    from schema.graph import derive_graph

    with tempfile.TemporaryDirectory(prefix="modelspec-worker-root-") as tmp:
        root = data_source.overlay(REPO_ROOT, data_dir, Path(tmp) / "root")
        registry.use_root(root)
        models = load_models(root)
        cards = [ModelCard.from_yaml_file(str(model.path)) for model in models]
        build = export.make_build(load_catalogue(root), root).to_json()
        devices = hardware.load_devices(root)
        graph = derive_graph(cards, hardware.device_classes(devices))
        hardware.compute(graph, cards, devices)
        ranking.write_export(out / "rank", cards, graph, build)
        policy_export.write_export(out, cards, build)
        require_cited_policy(out / "policy/catalogue.json")
        written = snapshot.build_from_repo(
            root, premier=root / "premier/slice-1.yaml", as_of=date.today(),
        ).write(out / "decision/snapshot.json.gz")
        write_decision_vocabulary(root, written, key=snapshot.env_key())
        from api.worker.src.display_vocabulary import trim
        display_models = {model.model_id for model in models
                          if model.front.get("lifecycle") != "retired"}
        values = {}
        for facet in registry.default().facets():
            if facet.value_type.kind in {"enum", "boolean"}:
                values[facet.id] = [True, False] if facet.value_type.kind == "boolean" else sorted(registry.default().allowed_values(facet) or ())
        vocabulary_path = out / "decision/vocabulary.json"
        vocabulary = trim(json.loads(vocabulary_path.read_text()), model_ids=display_models, facet_values=values)
        vocabulary_path.write_text(json.dumps(vocabulary), encoding="utf-8")


def require_cited_policy(path: Path) -> None:
    """Refuse uncited residency claims in the private bundled catalogue."""
    policy = json.loads(path.read_text())
    uncited = sum(row["primary_provider"]["data_residency_disclosure"] == "published"
                  and not (row["primary_provider"]["data_residency_source"] or {}).get("read_on")
                  for row in policy["models"])
    if uncited:
        print(f"uncited policy rows: {uncited}", file=sys.stderr)
        error = ValueError("uncited policy catalogue")
        error.filename = str(path)
        raise error


def check_imports_are_stdlib_only(bundle: Path) -> list[str]:
    """Import the bundle in isolation and report undeclared dependencies.

    Returns the offending top-level module names, empty when the bundle is
    clean. Run in a subprocess by the caller so the repository's own already
    imported `pipeline.ranking` cannot mask a missing dependency.
    """
    before = set(sys.modules)
    sys.path.insert(0, str(bundle))
    try:
        import decision.registry
        import pipeline.ranking  # noqa: F401 - imported for its side effects

        registry = decision.registry.default()
        if not registry.allowed_values(registry.facet("model.fits_hardware")):
            return ["hardware/ (no device IDs reached the bundle)"]
    finally:
        sys.path.remove(str(bundle))
    # Importing left `__pycache__` beside the sources. Remove it so generated
    # bytecode is never mistaken for a source module by a later bundle step.
    for cached in bundle.rglob("__pycache__"):
        shutil.rmtree(cached, ignore_errors=True)
    pulled = {name.split(".", 1)[0] for name in set(sys.modules) - before}
    return sorted(
        name for name in pulled
        if name not in ALLOWED_TOP_LEVEL
        and name not in sys.stdlib_module_names
        and not name.startswith("_")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None, help="Bundle root (default: src/).")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--export-data", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--check", action="store_true",
                        help="Also import the bundle and fail on a non-stdlib dependency.")
    args = parser.parse_args()

    if os.environ.get("MODELSPEC_REQUIRE_DATA_DIR") == "1" and args.data_dir is None:
        print("private Worker build requires --data-dir", file=sys.stderr)
        return 2
    if args.data_dir is not None and not os.environ.get("MODELSPEC_SNAPSHOT_KEY"):
        print("private Worker build requires the snapshot verification key", file=sys.stderr)
        return 2
    try:
        if args.export_data is not None:
            export_data(args.export_data, args.data_dir)
            return 0
        bundle = build(Path(args.out) if args.out else None, data_dir=args.data_dir)
        print(f"vendored {len(SOURCES)} files into {bundle}")
        if args.check:
            stray = check_imports_are_stdlib_only(bundle)
            if stray:
                print(
                    "error: the Worker bundle imports modules the isolate does not have: "
                    + ", ".join(stray),
                    file=sys.stderr,
                )
                return 1
            print("bundle imports cleanly with only declared dependencies")
    except Exception as error:
        if args.data_dir is None:
            traceback.print_exc()
        else:
            # Exception messages and validation errors can contain private values.
            path = getattr(error, "filename", None)
            if path is None and getattr(error, "_modelspec_redacted", False):
                path = str(error).split(": line ", 1)[0]
            path = path or str(args.data_dir)
            print(f"Worker bundle build failed: path={path}; category={type(error).__name__}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
