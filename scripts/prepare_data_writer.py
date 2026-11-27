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


def prepare(engine: Path, data: Path, *, skip_append_only: bool = False) -> None:
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
    append_only(data, skip=skip_append_only)
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


def append_only(data: Path, *, skip: bool = False) -> None:
    """Refuse a checkout whose evidence logs are not append-only against its trusted base
    (MODEL-491, ``scripts.append_only_guard``): every data workflow runs this step at the pin.
    It fails closed: a run that cannot show its base fails. Only the explicit local flag
    ``--skip-append-only`` skips it, and says so; inside GitHub Actions the flag itself refuses."""
    from scripts.append_only_guard import check

    if skip:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            raise ValueError("append-only guard: --skip-append-only is for a local checkout only")
        print("append-only guard: skipped (--skip-append-only, a local writer checkout)",
              file=sys.stderr)
        return
    found = check(data)  # raises when the base cannot be shown
    if found:
        raise ValueError("append-only guard: " + "; ".join(found))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--skip-append-only", action="store_true",
                        help="a local writer checkout only: skip the append-only guard (printed)")
    args = parser.parse_args()
    prepare(args.engine, args.data, skip_append_only=args.skip_append_only)


if __name__ == "__main__":
    # Invoked by path from the private checkout; resolve the pinned engine imports.
    main()
