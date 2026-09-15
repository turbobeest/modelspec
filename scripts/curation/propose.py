#!/usr/bin/env python3
"""Curation PR gate (MODEL-10 part 1): one branch and one DRAFT PR per changed page.

    python3 scripts/curation/propose.py --manifest drafts.json            # dry run (default)
    python3 scripts/curation/propose.py --manifest drafts.json --open-prs # local, human-run only

Batching: one PR per page, not per run. A page is the unit a reviewer checks against its
sources, so a per-page PR keeps each review small, lets one bad page be closed without
blocking the rest, and a revert touches one file. The weekly pilot touches few pages.

Only accepted drafts that actually change the page are proposed. Rejected drafts are listed
in the dry-run file and never modify anything. PRs are opened as drafts and never merged.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "benchmarks" / "_curation" / "reports" / "pr_bodies.md"


def branch_name(page: str, today: str) -> str:
    return f"curation/benchmarks/{page}-{today}"


def pr_title(item: dict) -> str:
    kinds = ", ".join(sorted({k["kind"] for k in item["kinds"]}))
    return f"benchgraph: curation update for {item['page']} ({kinds})"


def pr_body(item: dict) -> str:
    lines = [f"Automated curation draft for `benchmarks/{item['page']}.md` (MODEL-10).", "",
             "## Detected change", "", f"- Source: {item['url']}"]
    lines += [f"- {k['kind']}: {k['evidence']}" for k in item["kinds"]]
    lines += ["", "## Sources cited in this edit (with accessed dates)", ""]
    lines += [f"- {s['url']} (accessed {s['accessed']})" for s in item["sources"]] or ["- none"]
    lines += ["", "## Validator", "", f"`scripts/benchmarks/validate.py`: {item['validator']}", "",
              f"Drafter: {item['drafter']}. A human reviews every fact against its source and merges. "
              "Nothing auto-merges.", "", "🤖 Generated with [Claude Code](https://claude.com/claude-code)"]
    return "\n".join(lines) + "\n"


def plan(manifest: list[dict]) -> tuple[list[dict], list[dict]]:
    proposed = [m for m in manifest if m.get("accepted") and m.get("changed")]
    skipped = [m for m in manifest if m not in proposed]
    return proposed, skipped


def write_dry_run(manifest: list[dict], out: Path, today: str) -> Path:
    proposed, skipped = plan(manifest)
    parts = [f"# Would-be curation PRs ({today})", "", f"{len(proposed)} PR(s); {len(skipped)} skipped.", ""]
    for item in proposed:
        parts += [f"## {pr_title(item)}", "", f"Branch: `{branch_name(item['page'], today)}` (draft PR)", "",
                  pr_body(item)]
    if skipped:
        parts += ["## Skipped (no PR, page untouched)", ""]
        parts += [f"- {m['page']}: " + ("no change" if m.get("accepted") else "; ".join(m.get("errors") or []))
                  for m in skipped]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return out


def open_prs(manifest: list[dict], today: str, repo: str) -> None:  # pragma: no cover - human-run only
    for tool in ("git", "gh"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} not on PATH")
    proposed, _ = plan(manifest)
    base = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    for item in proposed:
        page = ROOT / "benchmarks" / f"{item['page']}.md"
        branch = branch_name(item["page"], today)
        subprocess.run(["git", "switch", "-c", branch, "origin/main"], check=True)
        page.write_text(Path(item["draft_path"]).read_text(encoding="utf-8"), encoding="utf-8")
        subprocess.run(["git", "add", str(page)], check=True)
        subprocess.run(["git", "commit", "-m", pr_title(item)], check=True)
        subprocess.run(["git", "push", "-u", "origin", branch], check=True)
        subprocess.run(["gh", "pr", "create", "--repo", repo, "--base", "main", "--head", branch, "--draft",
                        "--title", pr_title(item), "--body", pr_body(item)], check=True)
        subprocess.run(["git", "switch", base], check=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--open-prs", action="store_true", help="really create branches and draft PRs")
    ap.add_argument("--repo", default="turbobeest/modelspec")
    args = ap.parse_args(argv)
    manifest = json.loads(args.manifest.read_text())
    today = datetime.now(UTC).date().isoformat()
    if args.open_prs:
        open_prs(manifest, today, args.repo)
    else:
        print(f"dry run: wrote {write_dry_run(manifest, args.out, today)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
