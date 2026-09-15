#!/usr/bin/env python3
"""Curation drafter (MODEL-10 part 1): turn a detected change into a proposed page edit.

    python3 scripts/curation/draft.py --change change.json --source-text src.txt --dry-run
    python3 scripts/curation/draft.py --change change.json --source-text src.txt --drafter claude

The drafter is pluggable. `claude` shells out to `claude -p` (headless Claude
Code) with a strict prompt built from benchmarks/AUTHORING.md; `fake` (what
--dry-run selects) makes a deterministic, schema-valid edit for tests. Any agent
CLI that reads a prompt on stdin and prints the whole revised page can be added.

Gate: every draft is written to a scratch file, stamped with
freshness.researched, then checked by scripts/benchmarks/validate.py plus the
curation checks below. A draft that fails is discarded and the page on disk is
never touched. An accepted draft goes to --out-dir; only --apply writes the page.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Protocol

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.benchmarks.validate import check  # noqa: E402

BENCH_DIR = ROOT / "benchmarks"
AUTHORING = BENCH_DIR / "AUTHORING.md"
DEFAULT_OUT = BENCH_DIR / "_curation" / "drafts"
BEGIN, END = "<<<BEGIN PAGE>>>", "<<<END PAGE>>>"


class Drafter(Protocol):
    label: str

    def __call__(self, prompt: str, page_text: str) -> str: ...


def build_prompt(page_id: str, page_text: str, change: dict, source_text: str, today: str) -> str:
    rules = AUTHORING.read_text(encoding="utf-8")
    kinds = "; ".join(f"{k['kind']}: {k['evidence']}" for k in change.get("kinds", []))
    return f"""You are updating one benchmark page in the ModelSpec repository. You do not run git, do not
open other files, and do not browse. You edit only from the source text given below.

## Authoring rules (benchmarks/AUTHORING.md, binding)
{rules}

## Curation rules (binding, on top of the authoring rules)
1. Change only what the source text below supports. If it supports nothing, return the page unchanged.
2. Every fact you add or change must be backed by the watched source: add or update its entry in
   `sources` with `url: {change['url']}` and `accessed: "{today}"`. Never cite anything else.
3. Unknown stays empty. Do not fill a field from memory. Do not round a number you did not read.
4. When the source disagrees with the page, keep both readings in the prose, each with its source
   and date, and leave the contested front-matter field empty unless the source is authoritative.
5. Keep `id`, the section headings and their order. Do not add `models_covered`.
6. Do not edit `freshness`; the pipeline stamps it.
7. Output the complete revised file, front matter included, between {BEGIN} and {END}, and nothing else.

## Detected change
- page: {page_id}
- source: {change['url']}
- kinds: {kinds}
- previous reading: {change.get('previous_fetched_at') or 'none'}; this reading: {change.get('fetched_at') or today}

## Current page
{page_text}

## Source text (normalised, as fetched {today})
{source_text[:60000]}
"""


def extract_page(output: str) -> str:
    m = re.search(re.escape(BEGIN) + r"\n?(.*?)\n?" + re.escape(END), output, re.S)
    return (m.group(1) if m else "").strip("\n") + "\n"


@dataclass
class ClaudeDrafter:
    """Headless Claude Code. Local only in part 1: CI has no credential yet."""

    label: str = "claude -p curation drafter"
    binary: str = "claude"
    timeout: int = 900

    def __call__(self, prompt: str, page_text: str) -> str:
        if not shutil.which(self.binary):
            raise RuntimeError(f"{self.binary} not on PATH")
        r = subprocess.run([self.binary, "-p", "--output-format", "text"], input=prompt,
                           capture_output=True, text=True, timeout=self.timeout, check=False)
        if r.returncode != 0:
            raise RuntimeError(f"{self.binary} exited {r.returncode}")
        return extract_page(r.stdout)


@dataclass
class FakeDrafter:
    """Deterministic drafter for --dry-run and tests: cites the watched source, changes nothing else.

    `transform` lets tests inject a broken draft.
    """

    label: str = "fake curation drafter"
    url: str = ""
    today: str = ""
    transform: Callable[[str], str] | None = None

    def __call__(self, prompt: str, page_text: str) -> str:
        if self.transform:
            return self.transform(page_text)
        fm, body = split(page_text)
        sources = [s for s in fm.get("sources") or [] if s.get("url") != self.url]
        sources.append({"url": self.url, "title": "Watched source (curation re-read)", "accessed": self.today})
        fm["sources"] = sources
        return join(fm, body)


def split(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def join(fm: dict, body: str) -> str:
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=100) + "---\n" + body


@dataclass
class DraftResult:
    page: str
    url: str
    kinds: list[dict]
    accepted: bool
    errors: list[str] = field(default_factory=list)
    draft_path: str = ""
    drafter: str = ""
    sources: list[dict] = field(default_factory=list)
    validator: str = ""
    changed: bool = False


def curation_checks(page_id: str, original: dict, draft: dict, change_url: str, today: str) -> list[str]:
    errs = []
    if draft.get("id") != page_id:
        errs.append("draft changed the page id")
    cited = [s for s in draft.get("sources") or [] if s.get("url") == change_url]
    if not cited or cited[-1].get("accessed") != today:
        errs.append(f"draft does not cite {change_url} with accessed {today}")
    if len(draft.get("sources") or []) < len(original.get("sources") or []):
        errs.append("draft dropped existing sources")
    return errs


def draft_page(page_path: Path, change: dict, source_text: str, drafter: Drafter, *,
               today: str | None = None, out_dir: Path = DEFAULT_OUT, apply: bool = False) -> DraftResult:
    today = today or datetime.now(UTC).date().isoformat()
    page_id = page_path.stem
    original_text = page_path.read_text(encoding="utf-8")
    res = DraftResult(page=page_id, url=change["url"], kinds=change.get("kinds", []), accepted=False,
                      drafter=drafter.label)
    try:
        out = drafter(build_prompt(page_id, original_text, change, source_text, today), original_text)
    except Exception as exc:
        res.errors = [f"drafter failed: {exc}"]
        return res
    fm, body = split(out)
    if not fm:
        res.errors = ["draft has no front matter"]
        return res
    orig_fm, _ = split(original_text)
    fresh = dict(fm.get("freshness") or {})
    fresh.update({"researched": today, "researched_by": drafter.label})
    fm["freshness"] = fresh
    candidate = join(fm, body)

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / f"{page_id}.md"
        scratch.write_text(candidate, encoding="utf-8")
        errs = check(scratch)
    errs += curation_checks(page_id, orig_fm, fm, change["url"], today)
    res.validator = "ok" if not errs else "FAIL: " + "; ".join(errs)
    if errs:
        res.errors = errs  # discarded: nothing written, page untouched
        return res

    res.accepted = True
    res.sources = [{"url": s.get("url"), "accessed": s.get("accessed")} for s in fm.get("sources") or []
                   if s.get("accessed") == today]
    res.changed = split(candidate)[0] != {**orig_fm, "freshness": fresh} or body != split(original_text)[1] \
        or orig_fm.get("sources") != fm.get("sources")
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{page_id}.md"
    dest.write_text(candidate, encoding="utf-8")
    res.draft_path = str(dest)
    if apply:
        page_path.write_text(candidate, encoding="utf-8")
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--change", type=Path, required=True,
                    help="one change record from change_report.json, with a `page` key")
    ap.add_argument("--source-text", type=Path, required=True)
    ap.add_argument("--drafter", choices=["claude", "fake"], default="claude")
    ap.add_argument("--dry-run", action="store_true", help="use the fake drafter; never touch the page")
    ap.add_argument("--apply", action="store_true", help="write an accepted draft over the page")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--bench-dir", type=Path, default=BENCH_DIR)
    ap.add_argument("--manifest", type=Path, help="append the result to this JSON list")
    args = ap.parse_args(argv)

    change = json.loads(args.change.read_text())
    page_id = change.get("page") or change["pages"][0]["page"]
    today = datetime.now(UTC).date().isoformat()
    if args.dry_run or args.drafter == "fake":
        drafter: Drafter = FakeDrafter(url=change["url"], today=today)
    else:
        drafter = ClaudeDrafter()
    res = draft_page(args.bench_dir / f"{page_id}.md", change, args.source_text.read_text(encoding="utf-8"),
                     drafter, today=today, out_dir=args.out_dir, apply=args.apply and not args.dry_run)
    if args.manifest:
        items = json.loads(args.manifest.read_text()) if args.manifest.exists() else []
        items.append(asdict(res))
        args.manifest.write_text(json.dumps(items, indent=1))
    print(json.dumps(asdict(res), indent=1))
    return 0 if res.accepted else 1


if __name__ == "__main__":
    sys.exit(main())
