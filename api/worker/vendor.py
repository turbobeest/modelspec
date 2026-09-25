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
beside the decision package because it is the decision vocabulary at runtime.

* `api/ranking/engine.py` — the profiles, benchmark ranges, normalisation and
  the floors.
* `api/classes.py` — the class vocabulary used by the facet registry.
* `pipeline/ranking.py` — `Candidate`, `score`, `_basis`, `rank_report`.

The ranker imports only the standard library. The decision path also imports
Pydantic and PyYAML, the two packages declared in the Worker's ``pyproject.toml``.
The check below refuses any undeclared dependency before deployment.
"""

from __future__ import annotations

import argparse
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
    Path("decision/computed.py"): Path("decision/computed.py"),
    Path("decision/contract.py"): Path("decision/contract.py"),
    Path("decision/engine.py"): Path("decision/engine.py"),
    Path("decision/excluded.py"): Path("decision/excluded.py"),
    Path("decision/explain.py"): Path("decision/explain.py"),
    Path("decision/filter.py"): Path("decision/filter.py"),
    Path("decision/model.py"): Path("decision/model.py"),
    Path("decision/optimise.py"): Path("decision/optimise.py"),
    Path("decision/relax.py"): Path("decision/relax.py"),
    Path("decision/registry.py"): Path("decision/registry.py"),
    Path("decision/resolve.py"): Path("decision/resolve.py"),
    Path("decision/snapshot.py"): Path("decision/snapshot.py"),
    Path("schema/__init__.py"): Path("schema/__init__.py"),
    Path("schema/applicability.py"): Path("schema/applicability.py"),
    Path("schema/card.py"): Path("schema/card.py"),
    Path("schema/enums.py"): Path("schema/enums.py"),
    Path("registry/domains.yaml"): Path("registry/domains.yaml"),
    Path("registry/facets.yaml"): Path("registry/facets.yaml"),
    Path("registry/harnesses.yaml"): Path("registry/harnesses.yaml"),
    Path("registry/providers.yaml"): Path("registry/providers.yaml"),
    Path("registry/sources.yaml"): Path("registry/sources.yaml"),
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
    "schema",
    "typing_extensions",
    "typing_inspection",
    "yaml",
}


def build(destination: Path | None = None) -> Path:
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
    for source, target in SOURCES.items():
        dest = out / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / source, dest)
    return out


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

        decision.registry.default()
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
    parser.add_argument("--check", action="store_true",
                        help="Also import the bundle and fail on a non-stdlib dependency.")
    args = parser.parse_args()

    bundle = build(Path(args.out) if args.out else None)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
