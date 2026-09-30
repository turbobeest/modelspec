"""Where the curated data comes from: this repository, or the private data repo.

MODEL-246. Fresh curated data lives in the private repository
`turbobeest/modelspec-data`. This repository keeps a frozen image that lags by
nine months. Everything that reads or writes data addresses it through a *root*
directory that has the code and the data side by side, so the split is done by
composing a root, not by teaching every reader a second path.

`overlay()` builds that root: every entry of the public checkout is
symlinked, except the `DATA_PATHS`, which are symlinked to the private
checkout. Readers (the site build, the export, the ranking) see one tree.
Writers (leaderboard refresh, price re-read, the speed probe) write through the
links, so their output lands in the private checkout, where it is committed.
`.git` is linked too, so `Build.commit` stays the commit of the *code*.

    python -m pipeline.data_source overlay --private ../modelspec-data --out "$RUNNER_TEMP/root"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Paths that hold fresh curated data or the evidence for it, relative to the
# repository root: a directory, or a single file inside a directory that is
# otherwise public (`registry/`). Inventory and reasoning:
# docs/design/data-split.md. The rest of `registry/` (vocabulary) and
# `decision/` (code) change in lock step with the engine and stay public.
DATA_PATHS: tuple[str, ...] = (
    "models",
    "benchmarks",
    "hardware",
    "hosts",
    "offerings",
    "verification",
    "measurements",
    "premier",
    "research",
    "registry/sources.yaml",
    "registry/providers.yaml",
    "registry/harnesses.yaml",
    "registry/release-watch-baseline.json",
)

DATA_DIR_ENV = "MODELSPEC_DATA_DIR"


class DataSourceError(RuntimeError):
    """The data checkout is missing or does not look like a data checkout."""


def is_data_path(path: str) -> bool:
    """True when a repo-relative path is inside one of the `DATA_PATHS`."""
    parts = tuple(p for p in path.replace("\\", "/").split("/") if p not in ("", "."))
    return any(parts[: len(d.split("/"))] == tuple(d.split("/")) for d in DATA_PATHS)


def check_private(private: Path) -> Path:
    """Return the resolved private checkout, or fail naming what is missing.

    A build from a checkout that lacks `models/` must not fall back to the
    public image: that would ship stale data under a fresh label.
    """
    private = private.resolve()
    if not private.is_dir():
        raise DataSourceError(f"data checkout {private} is not a directory")
    missing = [name for name in ("models", "benchmarks") if not (private / name).is_dir()]
    if missing:
        raise DataSourceError(f"data checkout {private} has no {', '.join(missing)}/")
    return private


def overlay(public: Path, private: Path, out: Path) -> Path:
    """Compose `out` from the code in `public` and the data in `private`.

    `out` must not exist or must be empty. A data path the private checkout
    lacks is simply absent from the result, exactly as it is in the private
    repository; the two required directories are checked by `check_private`.
    """
    public = public.resolve()
    private = check_private(private)
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise DataSourceError(f"overlay target {out} is not empty")
    _compose(public, private, out, ())
    return out


def _compose(public: Path, private: Path, out: Path, rel: tuple[str, ...]) -> None:
    """Fill `out` (the directory at `rel`) from the two checkouts.

    A directory that only holds data paths deeper down (`registry/`) becomes a
    real directory of links, so its vocabulary files stay public and its data
    files come from the private checkout.
    """
    here = "/".join(rel)
    for entry in sorted((public / here).iterdir() if here else public.iterdir()):
        path = "/".join((*rel, entry.name))
        if path in DATA_PATHS:
            continue
        if entry.is_dir() and any(d.startswith(path + "/") for d in DATA_PATHS):
            (out / entry.name).mkdir()
            _compose(public, private, out / entry.name, (*rel, entry.name))
        else:
            (out / entry.name).symlink_to(entry)
    for path in DATA_PATHS:
        parent, _, name = path.rpartition("/")
        if parent == here and (private / path).exists():
            (out / name).symlink_to(private / path)


def data_dir_from_env(env: dict[str, str] | None = None) -> Path | None:
    value = (env if env is not None else os.environ).get(DATA_DIR_ENV, "").strip()
    return Path(value) if value else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    ov = sub.add_parser("overlay", help="compose a root from public code and private data")
    ov.add_argument("--public", default=str(REPO_ROOT), help="public checkout (default: this repository)")
    ov.add_argument("--private", required=True, help="private data checkout")
    ov.add_argument("--out", required=True, help="empty directory to compose into")
    sub.add_parser("paths", help="print the data paths, one per line")
    args = parser.parse_args(argv)
    if args.command == "paths":
        print("\n".join(DATA_PATHS))
        return 0
    try:
        print(overlay(Path(args.public), Path(args.private), Path(args.out)))
    except DataSourceError as exc:
        print(f"data_source: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
