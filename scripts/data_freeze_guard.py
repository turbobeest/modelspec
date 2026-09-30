"""Fail a pull request that lands fresh curated data in the public repository.

MODEL-246. Fresh data belongs in `turbobeest/modelspec-data`. In this
repository the data paths (`pipeline.data_source.DATA_PATHS`) are frozen: the
only change allowed is the scheduled lag job's, which arrives on a `data-lag/*`
branch and must satisfy all of:

  * `data-image.json` is part of the change, and its `as_of` is not after the
    cutoff (`today - 9 months`);
  * no line the change adds carries an ISO date (YYYY-MM-DD) after the cutoff.

Anything else touching a data path fails, listing the files.

    python scripts/data_freeze_guard.py --base origin/main --head HEAD --branch "$BRANCH"
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.data_source import is_data_path  # noqa: E402
from scripts.data_lag import LAG_MONTHS, MANIFEST, cutoff_for  # noqa: E402

LAG_BRANCH_PREFIX = "data-lag/"
_ISO_DATE = re.compile(r"(?<![\d-])(\d{4})-(\d{2})-(\d{2})(?![\d-])")


@dataclass
class Verdict:
    ok: bool
    problems: list[str] = field(default_factory=list)


def newer_than(text: str, cutoff: date) -> list[str]:
    """ISO dates in `text` that fall after `cutoff` (impossible dates ignored)."""
    found: list[str] = []
    for y, m, d in _ISO_DATE.findall(text):
        try:
            if date(int(y), int(m), int(d)) > cutoff:
                found.append(f"{y}-{m}-{d}")
        except ValueError:
            continue
    return found


def judge(
    changed: list[str],
    added_text: dict[str, str],
    manifest_as_of: date | None,
    branch: str,
    today: date,
) -> Verdict:
    """Decide on a change. `changed` is every touched path, repo-relative.

    `added_text` maps a touched data path to the text of its added lines
    (absent for binary files); `manifest_as_of` is `data-image.json`'s `as_of`
    in the head tree, or None when the file is missing or unreadable.
    """
    data = sorted(p for p in changed if is_data_path(p))
    manifest_touched = MANIFEST in changed
    if not data and not manifest_touched:
        return Verdict(True)
    cutoff = cutoff_for(today, LAG_MONTHS)
    if not branch.startswith(LAG_BRANCH_PREFIX):
        head = ", ".join(data[:5]) + (f" and {len(data) - 5} more" if len(data) > 5 else "")
        touched = head or MANIFEST
        return Verdict(False, [
            f"fresh data must not land in this repository: {touched}. "
            f"Open the change against turbobeest/modelspec-data. "
            f"Only a `{LAG_BRANCH_PREFIX}*` branch may change {len(data)} frozen path(s)."
        ])
    problems: list[str] = []
    if not manifest_touched:
        problems.append(f"{MANIFEST} is not part of the lag change")
    if manifest_as_of is None:
        problems.append(f"{MANIFEST} is missing or has no readable as_of")
    elif manifest_as_of > cutoff:
        problems.append(f"{MANIFEST} as_of {manifest_as_of} is after the cutoff {cutoff}")
    for path in data:
        for value in sorted(set(newer_than(added_text.get(path, ""), cutoff)))[:3]:
            problems.append(f"{path} adds {value}, after the cutoff {cutoff}")
    return Verdict(not problems, problems)


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True,
                          text=True, check=True, errors="replace").stdout


def collect(base: str, head: str) -> tuple[list[str], dict[str, str], date | None]:
    """Read the three-dot diff from git; the merge-base keeps unrelated main moves out."""
    span = f"{base}...{head}"
    changed = [p for p in _git("diff", "--name-only", "--no-renames", span).split("\n") if p]
    added: dict[str, str] = {}
    for path in changed:
        if not is_data_path(path):
            continue
        patch = _git("diff", "--no-renames", "-U0", "--no-color", span, "--", path)
        if patch.startswith("Binary") or "\nBinary files" in patch:
            continue
        added[path] = "\n".join(
            line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++")
        )
    as_of = None
    try:
        raw = json.loads(_git("show", f"{head}:{MANIFEST}"))
        as_of = date.fromisoformat(raw["as_of"])
    except (subprocess.CalledProcessError, ValueError, KeyError, TypeError):
        pass
    return changed, added, as_of


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--branch", required=True, help="the pull request's head branch name")
    parser.add_argument("--today", default=None, help="ISO date; default: today (UTC)")
    args = parser.parse_args(argv)
    today = date.fromisoformat(args.today) if args.today else date.today()
    changed, added, as_of = collect(args.base, args.head)
    verdict = judge(changed, added, as_of, args.branch, today)
    for problem in verdict.problems:
        print(f"::error::{problem}")
    if verdict.ok:
        print("data freeze: ok")
    return 0 if verdict.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
