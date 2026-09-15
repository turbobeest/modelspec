#!/usr/bin/env python3
"""Curation loop CI glue (MODEL-10 part 2). Every subcommand is safe to run locally.

    python3 scripts/curation/ci.py gate --event schedule --schedule '47 6 * * *' [--today 2026-09-17]
    python3 scripts/curation/ci.py plan --report benchmarks/_curation/reports/change_report.json
    python3 scripts/curation/ci.py draft --report .../change_report.json [--drafter claude]   # default fake
    python3 scripts/curation/ci.py issues --report .../change_report.json [--apply]          # default dry run

gate    decides whether this scheduled run belongs to the 7-day daily trial window.
plan    writes has_changes / has_work / has_dead for GITHUB_OUTPUT.
draft   drafts every page a classifiable change touches; leaderboard_dead never drafts.
issues  turns leaderboard_dead into one GitHub issue per page, commenting on an open one instead.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.curation import draft as drafting  # noqa: E402

CENSUS_DIR = ROOT / "benchmarks" / "_census"
REPORT = ROOT / "benchmarks" / "_curation" / "reports" / "change_report.json"

# ---------- 7-day daily trial (decision D) ----------
WEEKLY_CRON = "17 6 * * 1"
DAILY_CRON = "47 6 * * *"
#: Baseline plus 7 daily runs = 8 scheduled daily runs, one per date in this window (inclusive).
TRIAL_START, TRIAL_END = date(2026, 9, 16), date(2026, 9, 23)
DEAD = "leaderboard_dead"


def gate(event: str, schedule: str, today: date) -> tuple[bool, str]:
    """Dispatch always runs. The daily cron runs only inside the trial window; the weekly cron only outside it."""
    in_trial = TRIAL_START <= today <= TRIAL_END
    if event != "schedule":
        return True, f"{event}: always runs"
    if schedule == DAILY_CRON:
        return in_trial, ("daily trial run" if in_trial else
                          f"daily trial ended {TRIAL_END} (8 runs): skipped; remove the daily cron")
    if schedule == WEEKLY_CRON:
        return (not in_trial), ("weekly run" if not in_trial else "weekly run skipped: the daily trial covers today")
    return False, f"unknown schedule {schedule!r}"


# ---------- plan ----------
def kinds_of(item: dict) -> set[str]:
    return {k["kind"] for k in item.get("kinds", [])}


def draftable(report: dict) -> list[dict]:
    return [c for c in report.get("changes", []) if kinds_of(c) and DEAD not in kinds_of(c)]


def dead_items(report: dict) -> list[dict]:
    return [x for x in report.get("changes", []) + report.get("failures", []) if DEAD in kinds_of(x)]


def plan(report: dict) -> dict[str, bool]:
    has_changes = bool(draftable(report))
    return {"has_changes": has_changes, "has_work": has_changes or bool(report.get("census_leads")),
            "has_dead": bool(dead_items(report))}


# ---------- draft ----------
def draft_all(report: dict, report_dir: Path, drafter_kind: str, *, bench_dir: Path = drafting.BENCH_DIR,
              out_dir: Path = drafting.DEFAULT_OUT, today: str | None = None) -> list[dict]:
    today = today or datetime.now(UTC).date().isoformat()
    manifest = []
    for change in draftable(report):
        src = report_dir / change.get("source_text", "")
        source_text = src.read_text(encoding="utf-8") if change.get("source_text") and src.is_file() else ""
        for p in change["pages"]:
            one = {**change, "page": p["page"]}
            drafter = (drafting.ClaudeDrafter() if drafter_kind == "claude"
                       else drafting.FakeDrafter(url=change["url"], today=today))
            res = drafting.draft_page(bench_dir / f"{p['page']}.md", one, source_text, drafter,
                                      today=today, out_dir=out_dir)
            manifest.append(asdict(res))
    return manifest


# ---------- census leads (decision E) ----------
def _slugify(name: str) -> str:  # same rules as scripts/benchmarks/census.py slugify
    s = name.lower()
    s = re.sub(r"[\-–—/.]", "_", s)
    s = re.sub(r"[^a-z0-9_ ]", "", s)
    s = re.sub(r"\s+", "_", s.strip())
    s = re.sub(r"_+", "_", s)
    return s.strip("_")[:80]


def lead_name(url: str) -> str:
    u = urlparse(url)
    parts = [x for x in u.path.split("/") if x]
    return (parts[-1] if parts else u.netloc).removesuffix(".html")


def append_census_leads(urls: list[str], census_dir: Path = CENSUS_DIR, today: str | None = None) -> list[str]:
    """Append leads in census.py's own formats: a candidates.jsonl line and a queue_p3.json entry.

    Dedup: a URL already in candidates.jsonl or any queue_p*.json, or whose slug is already queued,
    is skipped, as is a repeat within `urls`. Returns the URLs actually added.
    """
    today = today or datetime.now(UTC).date().isoformat()
    cand = census_dir / "candidates.jsonl"
    lines = cand.read_text(encoding="utf-8").splitlines() if cand.exists() else []
    known_urls = {json.loads(x).get("url") for x in lines if x.strip()}
    known_slugs: set[str] = set()
    for qf in sorted(census_dir.glob("queue_p*.json")):
        for e in json.loads(qf.read_text(encoding="utf-8")):
            known_urls.update(e.get("urls") or [])
            known_slugs.add(e.get("slug") or e.get("id") or "")
    q3_path = census_dir / "queue_p3.json"
    q3 = json.loads(q3_path.read_text(encoding="utf-8")) if q3_path.exists() else []
    added, new_lines = [], []
    for url in urls:
        name = lead_name(url)
        slug = _slugify(name)
        if url in known_urls or not slug or slug in known_slugs:
            continue
        known_urls.add(url)
        known_slugs.add(slug)
        source = "curation:immediate_brief"
        new_lines.append(json.dumps({"name": name, "slug": slug, "source": source, "url": url,
                                     "evidence": f"immediate brief {today}; no benchmark page cites it",
                                     "category_hint": "", "kind": "lead", "priority": 3}))
        q3.append({"slug": slug, "name": name, "aliases": [], "sources": [source], "source_count": 1,
                   "urls": [url], "harness": {}, "category_hint": "", "priority": 3, "downloads": 0,
                   "score": 10.0})
        added.append(url)
    if added:
        with cand.open("a", encoding="utf-8") as f:
            if lines and not cand.read_text(encoding="utf-8").endswith("\n"):
                f.write("\n")
            f.write("\n".join(new_lines) + "\n")
        q3_path.write_text(json.dumps(q3, indent=1), encoding="utf-8")
    return added


# ---------- dead-leaderboard issues (decision F) ----------
def marker(page: str) -> str:
    return f"<!-- curation-leaderboard-dead:{page} -->"


def issue_payloads(report: dict) -> list[dict]:
    by_page: dict[str, list[dict]] = {}
    for item in dead_items(report):
        for p in item["pages"]:
            by_page.setdefault(p["page"], []).append(item)
    out = []
    for page, items in sorted(by_page.items()):
        ev = [f"- {i['url']}: " + "; ".join(k["evidence"] for k in i["kinds"] if k["kind"] == DEAD) for i in items]
        body = "\n".join([marker(page), f"The curation watcher found a dead leaderboard for `benchmarks/{page}.md` "
                          f"(run {report.get('run_at', '')}).", "", *ev, "",
                          "No page edit was drafted. A person decides whether the page's status or "
                          "leaderboard_url should change (MODEL-10)."])
        out.append({"page": page, "title": f"curation: leaderboard dead for {page}", "body": body})
    return out


class IssueClient(Protocol):
    def open_issues(self) -> list[dict]: ...
    def create(self, title: str, body: str) -> None: ...
    def comment(self, number: int, body: str) -> None: ...


class GhIssues:  # pragma: no cover - calls gh with GITHUB_TOKEN in CI
    def __init__(self, repo: str):
        self.repo = repo

    def _gh(self, *args: str) -> str:
        return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout

    def open_issues(self) -> list[dict]:
        out = self._gh("issue", "list", "--repo", self.repo, "--state", "open", "--limit", "500",
                       "--search", "curation: leaderboard dead in:title", "--json", "number,title,body")
        return json.loads(out or "[]")

    def create(self, title: str, body: str) -> None:
        self._gh("issue", "create", "--repo", self.repo, "--title", title, "--body", body)

    def comment(self, number: int, body: str) -> None:
        self._gh("issue", "comment", str(number), "--repo", self.repo, "--body", body)


def file_issues(payloads: list[dict], client: IssueClient) -> list[tuple[str, str]]:
    """One open issue per page, found by the hidden marker in its body; a repeat becomes a comment."""
    existing = client.open_issues()
    actions = []
    for p in payloads:
        hit = next((i for i in existing if marker(p["page"]) in (i.get("body") or "")), None)
        if hit:
            client.comment(int(hit["number"]), p["body"])
            actions.append((p["page"], f"commented #{hit['number']}"))
        else:
            client.create(p["title"], p["body"])
            existing.append({"number": 0, "body": p["body"]})
            actions.append((p["page"], "created"))
    return actions


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gate")
    g.add_argument("--event", required=True)
    g.add_argument("--schedule", default="")
    g.add_argument("--today", default="")
    for name in ("plan", "draft", "issues"):
        s = sub.add_parser(name)
        s.add_argument("--report", type=Path, default=REPORT)
    sub.choices["draft"].add_argument("--drafter", choices=["claude", "fake"], default="fake")
    sub.choices["draft"].add_argument("--manifest", type=Path, required=False)
    sub.choices["issues"].add_argument("--apply", action="store_true")
    sub.choices["issues"].add_argument("--repo", default="turbobeest/modelspec")
    args = ap.parse_args(argv)

    if args.cmd == "gate":
        today = date.fromisoformat(args.today) if args.today else datetime.now(UTC).date()
        run, why = gate(args.event, args.schedule, today)
        print(f"run={'true' if run else 'false'}")
        print(f"reason={why}")
        return 0
    report = json.loads(args.report.read_text())
    if args.cmd == "plan":
        for k, v in plan(report).items():
            print(f"{k}={'true' if v else 'false'}")
        return 0
    if args.cmd == "draft":
        manifest = draft_all(report, args.report.parent, args.drafter)
        out = args.manifest or args.report.parent / "drafts.json"
        out.write_text(json.dumps(manifest, indent=1))
        print(f"{sum(m['accepted'] for m in manifest)}/{len(manifest)} drafts accepted; manifest {out}")
        return 0
    payloads = issue_payloads(report)
    if not args.apply:
        print(json.dumps(payloads, indent=1))
        return 0
    for page, action in file_issues(payloads, GhIssues(args.repo)):
        print(f"{page}: {action}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
