"""Assemble the rank Worker's Python bundle from the repository's own modules.

MODEL-68. The Worker must not hold a second copy of the scorer, so there is no
copy in git: this script materialises `api/worker/python_modules/` on demand,
and `.gitignore` keeps it out of the tree. CI runs it before the bundle is
built and before the byte-identity test, so the thing that is deployed and the
thing that is tested are produced by the same step from the same sources.

`python_modules/` at the Worker root is the directory Wrangler bundles for a
Python Worker (`docs/rank-api.md` cites the configuration reference), and it is
on `sys.path` inside the isolate, so `from pipeline.ranking import rank_report`
resolves there exactly as it resolves in this repository.

Only two modules are copied, byte for byte:

* `api/ranking/engine.py` — the profiles, benchmark ranges, normalisation and
  the floors.
* `pipeline/ranking.py` — `Candidate`, `score`, `_basis`, `rank_report`.

Both import nothing outside the standard library, which is checked here rather
than assumed: a new third-party import in either would break the Worker at
deploy time, and this turns that into a failure on the pull request.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKER_ROOT = Path(__file__).resolve().parent
BUNDLE = WORKER_ROOT / "python_modules"

#: repository path -> path inside the bundle. Copied verbatim; if a copy here
#: ever needed an edit, the two implementations would have forked and the
#: byte-identity test would be measuring a fork against itself.
SOURCES = {
    Path("api/__init__.py"): Path("api/__init__.py"),
    Path("api/ranking/__init__.py"): Path("api/ranking/__init__.py"),
    Path("api/ranking/engine.py"): Path("api/ranking/engine.py"),
    Path("pipeline/__init__.py"): Path("pipeline/__init__.py"),
    Path("pipeline/ranking.py"): Path("pipeline/ranking.py"),
}

#: What the bundle is allowed to need. `schema`, `pydantic` and `yaml` are the
#: ones that would actually show up, and none of them exist in the isolate.
ALLOWED_TOP_LEVEL = {"api", "pipeline"}


def build(destination: Path | None = None) -> Path:
    """Write the bundle and return its root. Idempotent."""
    out = destination or BUNDLE
    if out.exists():
        shutil.rmtree(out)
    for source, target in SOURCES.items():
        dest = out / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / source, dest)
    return out


def check_imports_are_stdlib_only(bundle: Path) -> list[str]:
    """Import the bundle in isolation and report anything it dragged in.

    Returns the offending top-level module names, empty when the bundle is
    clean. Run in a subprocess by the caller so the repository's own already
    imported `pipeline.ranking` cannot mask a missing dependency.
    """
    before = set(sys.modules)
    sys.path.insert(0, str(bundle))
    try:
        import pipeline.ranking  # noqa: F401 - imported for its side effects
    finally:
        sys.path.remove(str(bundle))
    # Importing left `__pycache__` beside the sources. Wrangler's default
    # `python_modules.exclude` drops `*.pyc`, but a bundle that is only correct
    # because of a default is one configuration change from shipping bytecode.
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
    parser.add_argument("--out", default=None, help="Bundle root (default: python_modules/).")
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
        print("bundle imports cleanly with only the standard library")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
