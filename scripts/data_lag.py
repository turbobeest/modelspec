"""Publish the public data image: the private data as it was nine months ago.

MODEL-246. The public repository keeps a stale image of the curated data; the
fresh data lives in `turbobeest/modelspec-data`. This script finds the last
commit in that repository at or before `today - 9 months`, and makes the public
data paths match that commit exactly. It writes `data-image.json` recording
which commit that was.

Until the private history reaches back past the cutoff there is no such commit,
and the script changes nothing. With the private repo seeded on 2026-09-30 that
is until 2027-06-30.

    python scripts/data_lag.py --private ../modelspec-data [--today 2027-06-30] [--dry-run]

Run by `.github/workflows/data-lag.yml`, which opens a `data-lag/*` PR; the
freeze guard (`scripts/data_freeze_guard.py`) accepts data changes only from
such a branch, and only when they carry nothing newer than the cutoff.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.data_source import DATA_PATHS  # noqa: E402

LAG_MONTHS = 9
MANIFEST = "data-image.json"


def cutoff_for(today: date, months: int = LAG_MONTHS) -> date:
    """`today` minus whole calendar months, clamped to the target month's last day."""
    year, month = divmod(today.year * 12 + (today.month - 1) - months, 12)
    return _clamp(year, month + 1, today.day)


def _clamp(year: int, month: int, day: int) -> date:
    first_next = date(year + (month == 12), month % 12 + 1, 1)
    last = (first_next - timedelta(days=1)).day
    return date(year, month, min(day, last))


def _git(repo: Path, *args: str, binary: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=not binary, check=True)


def _end_of(cutoff: date) -> int:
    return int(datetime(cutoff.year, cutoff.month, cutoff.day, 23, 59, 59, tzinfo=timezone.utc).timestamp())


def commit_at_or_before(private: Path, cutoff: date) -> tuple[str, date] | None:
    """The newest first-parent commit with nothing newer than `cutoff` in its history.

    A backdated commit on top of fresh history has an old committer date but
    carries the fresh data, so every ancestor's date is checked, not just the
    commit's own. Returns the commit and its committer date (UTC).
    """
    limit = _end_of(cutoff)
    for commit in _git(private, "rev-list", "--first-parent", "HEAD").stdout.split():
        stamps = [int(t) for t in _git(private, "log", "--format=%ct", commit).stdout.split()]
        if max(stamps) <= limit:
            return commit, datetime.fromtimestamp(stamps[0], timezone.utc).date()
    return None


def _existing_paths(private: Path, commit: str) -> list[str]:
    return [
        p for p in DATA_PATHS
        if _git(private, "ls-tree", "--name-only", commit, "--", p).stdout.strip()
    ]


def read_manifest(public: Path) -> dict | None:
    path = public / MANIFEST
    return json.loads(path.read_text()) if path.is_file() else None


def sync(private: Path, commit: str, committed: date, public: Path, cutoff: date) -> list[str]:
    """Make each data path in `public` equal to `commit`; return paths present."""
    present = _existing_paths(private, commit)
    archive = _git(private, "archive", "--format=tar", commit, *present, binary=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(tmp, filter="data")
        for name in DATA_PATHS:
            target = public / name
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink(missing_ok=True)
            if name in present:
                source = Path(tmp) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
    manifest = {
        "as_of": cutoff.isoformat(),
        "lag_months": LAG_MONTHS,
        "source_repo": "turbobeest/modelspec-data",
        "source_commit": commit,
        "source_committed": committed.isoformat(),
        "paths": present,
    }
    (public / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n")
    return present


def run(private: Path, public: Path, today: date, *, dry_run: bool = False) -> dict:
    cutoff = cutoff_for(today)
    result = {"cutoff": cutoff.isoformat(), "status": "", "commit": None}
    picked = commit_at_or_before(private, cutoff)
    if picked is None:
        result["status"] = "no-image-yet"
        return result
    commit, committed = picked
    result["commit"] = commit
    current = read_manifest(public)
    if current and current.get("source_commit") == commit:
        result["status"] = "unchanged"
        return result
    result["status"] = "would-publish" if dry_run else "published"
    if not dry_run:
        sync(private, commit, committed, public, cutoff)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--private", required=True, help="checkout of modelspec-data, with history")
    parser.add_argument("--public", default=str(REPO_ROOT), help="public checkout to update")
    parser.add_argument("--today", default=None, help="ISO date; default: today (UTC)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    today = date.fromisoformat(args.today) if args.today else date.today()
    result = run(Path(args.private), Path(args.public), today, dry_run=args.dry_run)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
