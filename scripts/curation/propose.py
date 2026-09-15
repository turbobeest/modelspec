#!/usr/bin/env python3
"""Curation PR gate (MODEL-10): one branch and one DRAFT PR per changed page.

    python3 scripts/curation/propose.py --manifest drafts.json            # dry run (default)
    python3 scripts/curation/propose.py --manifest drafts.json --open-prs # CI job 2, or a human

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

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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


def open_curation_heads(repo: str, run=subprocess.run) -> set[str]:
    """Head branches of open curation PRs, so a daily run never opens a second PR for a page."""
    r = run(["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "200",
             "--json", "headRefName", "--jq", ".[].headRefName"], capture_output=True, text=True, check=True)
    return {h for h in r.stdout.split() if h.startswith("curation/benchmarks/")}


def page_has_open_pr(page: str, heads: set[str]) -> bool:
    return any(h.startswith(f"curation/benchmarks/{page}-") for h in heads)


def open_prs(manifest: list[dict], today: str, repo: str, leads: list[str] | None = None,
             census_dir: Path | None = None) -> None:  # pragma: no cover - runs git and gh
    """Push one branch and one DRAFT PR per changed page. Census leads ride in the first PR opened.

    Git auth comes from the caller (CI sets an http extraheader from RESEARCH_PR_TOKEN); gh reads GH_TOKEN.
    """
    from scripts.curation.ci import append_census_leads  # local import: ci imports this module

    for tool in ("git", "gh"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} not on PATH")
    proposed, _ = plan(manifest)
    heads = open_curation_heads(repo)
    base = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    pending_leads = list(leads or [])
    items = [i for i in proposed if not page_has_open_pr(i["page"], heads)]
    for i in proposed:
        if i not in items:
            print(f"skip {i['page']}: an open curation PR already exists")
    if pending_leads and not items:
        items = [{"page": "census-leads", "census_only": True}]
    for item in items:
        branch = branch_name(item["page"], today)
        if subprocess.run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
                          capture_output=True, check=False).returncode == 0:
            print(f"skip {branch}: branch already exists")
            continue
        subprocess.run(["git", "switch", "-c", branch, "origin/main"], check=True)
        paths: list[str] = []
        if not item.get("census_only"):
            page = ROOT / "benchmarks" / f"{item['page']}.md"
            page.write_text(Path(item["draft_path"]).read_text(encoding="utf-8"), encoding="utf-8")
            paths.append(str(page))
        added: list[str] = []
        if pending_leads:
            added = append_census_leads(pending_leads, census_dir or ROOT / "benchmarks" / "_census", today)
            paths += [str((census_dir or ROOT / "benchmarks" / "_census") / f)
                      for f in ("candidates.jsonl", "queue_p3.json")]
            pending_leads = []
        if item.get("census_only"):
            if not added:
                subprocess.run(["git", "switch", base], check=True)
                continue
            title, body = f"benchgraph: curation census leads ({today})", census_body(added)
        else:
            title, body = pr_title(item), pr_body(item) + (census_body(added) if added else "")
        subprocess.run(["git", "add", *paths], check=True)
        subprocess.run(["git", "commit", "-m", title], check=True)
        subprocess.run(["git", "push", "-u", "origin", branch], check=True)
        subprocess.run(["gh", "pr", "create", "--repo", repo, "--base", "main", "--head", branch, "--draft",
                        "--title", title, "--body", body], check=True)
        subprocess.run(["git", "switch", base], check=True)


def census_body(urls: list[str]) -> str:
    lines = ["", "## New-benchmark census leads", "",
             "URLs no benchmark page cites, appended to `benchmarks/_census/candidates.jsonl` and "
             "`queue_p3.json` (deduplicated):", ""]
    return "\n".join(lines + [f"- {u}" for u in urls]) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--open-prs", action="store_true", help="really create branches and draft PRs")
    ap.add_argument("--repo", default="turbobeest/modelspec")
    ap.add_argument("--leads", type=Path, help="change_report.json whose census_leads join the PRs")
    args = ap.parse_args(argv)
    manifest = json.loads(args.manifest.read_text())
    today = datetime.now(UTC).date().isoformat()
    if args.open_prs:
        leads = json.loads(args.leads.read_text()).get("census_leads", []) if args.leads else []
        open_prs(manifest, today, args.repo, leads)
    else:
        print(f"dry run: wrote {write_dry_run(manifest, args.out, today)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
