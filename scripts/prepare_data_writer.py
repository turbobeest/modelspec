"""Copy pinned engine code beside private data without copying data or git state.

Run only in modelspec-data. Physical copies keep __file__ roots in that
checkout. Copied files are locally ignored, so only private data enters PRs.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.data_source import check_private, is_data_path  # noqa: E402


def prepare(engine: Path, data: Path) -> None:
    engine, data = engine.resolve(), check_private(data)
    remote = (
        subprocess.run(
            ["git", "-C", str(data), "remote", "get-url", "origin"],
            check=True,
            capture_output=True,
            text=True,
        )
        .stdout.strip()
        .removesuffix(".git")
    )
    if remote not in (
        "https://github.com/turbobeest/modelspec-data",
        "git@github.com:turbobeest/modelspec-data",
    ):
        raise ValueError("writer checkout must have modelspec-data as origin")
    append_only(data)
    tracked = subprocess.run(
        ["git", "-C", str(engine), "ls-files", "-z"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split("\0")
    ignored = []
    for relative in filter(None, tracked):
        if is_data_path(relative) or relative.startswith(".github/") or relative == "README.md":
            continue
        source, target = engine / relative, data / relative
        if not source.is_file():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        ignored.append("/" + relative)
    # Ignore generated Python/install files and writer scratch outputs too.
    ignored += [
        "__pycache__/",
        "*.egg-info/",
        "/survey.txt",
        "/validation.json",
        "/stale-guides.md",
        "/attribution.md",
    ]
    git_dir = subprocess.run(
        ["git", "-C", str(data), "rev-parse", "--absolute-git-dir"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    exclude = Path(git_dir) / "info/exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    with exclude.open("a") as out:
        out.write("\n" + "\n".join(ignored) + "\n")


def append_only(data: Path) -> None:
    """Refuse a checkout whose evidence logs are not append-only against its base (MODEL-491,
    ``scripts.append_only_guard``): every data workflow runs this step at the pin. With no base
    revision to compare with, a CI run refuses; a writer's local checkout without one is left
    alone, since it has no base branch to break, and so is any checkout outside the data
    repository's own CI."""
    from scripts.append_only_guard import base_revision, problems

    base = base_revision(data)
    if base is None:
        if os.environ.get("GITHUB_ACTIONS") == "true" \
                and os.environ.get("GITHUB_REPOSITORY", "").endswith("/modelspec-data"):
            raise ValueError("append-only guard: no base revision to compare the logs with")
        return
    found = problems(data, base)
    if found:
        raise ValueError("append-only guard: " + "; ".join(found))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.engine, args.data)


if __name__ == "__main__":
    # Invoked by path from the private checkout; resolve the pinned engine imports.
    main()
