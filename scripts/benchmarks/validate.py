#!/usr/bin/env python3
"""Validate benchmark wiki pages: python3 scripts/benchmarks/validate.py [benchmarks/<id>.md ...]

With no arguments, validates every page under benchmarks/. Exit 1 on any error.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from schema.benchmark import BenchmarkCard, REQUIRED_SECTIONS  # noqa: E402

PLACEHOLDERS = re.compile(r"\b(TODO|TBD|lorem ipsum|placeholder|FIXME)\b", re.I)


def check(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return ["no YAML front matter"]
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return [f"front matter is not valid YAML: {e}"]
    if "models_covered" in fm:
        errs.append("models_covered must not be authored (derived from the cards)")
    try:
        card = BenchmarkCard.model_validate(fm)
    except Exception as e:  # pydantic ValidationError
        return errs + [f"schema: {e}"]
    if card.id != path.stem:
        errs.append(f"id '{card.id}' does not match filename '{path.stem}'")
    if not card.name.strip():
        errs.append("name is empty")
    if not card.summary.strip():
        errs.append("summary is empty")
    if len(card.measures.strip()) < 40:
        errs.append("measures must be a real paragraph (40+ characters)")
    if not card.sources:
        errs.append("at least one source is required")
    for s in card.sources:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", s.accessed or ""):
            errs.append(f"source {s.url} needs an accessed date YYYY-MM-DD")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", card.freshness.researched or ""):
        errs.append("freshness.researched must be YYYY-MM-DD")
    if not card.freshness.researched_by.strip():
        errs.append("freshness.researched_by is empty")
    body = m.group(2)
    heads = [h.strip() for h in re.findall(r"^##\s+(.+?)\s*$", body, re.M)]
    for req in REQUIRED_SECTIONS[card.page_kind]:
        if req not in heads:
            errs.append(f"missing section '## {req}'")
    if card.page_kind == "subset" and not card.lineage.family:
        errs.append("subset pages must name lineage.family")
    if PLACEHOLDERS.search(text):
        errs.append("placeholder text found (TODO/TBD/etc.)")
    words = len(re.findall(r"\w+", body))
    minimum = 120 if card.page_kind == "subset" else 350
    if words < minimum:
        errs.append(f"body too short ({words} words; minimum {minimum} for a {card.page_kind} page)")
    return errs


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] or sorted((ROOT / "benchmarks").glob("*.md"))
    # AUTHORING.md, LICENSE.md and anything underscore-prefixed are repository files, not pages.
    skip = {"AUTHORING.md", "LICENSE.md", "README.md"}
    paths = [p for p in paths if p.name not in skip and not p.name.startswith("_")]
    bad = 0
    for p in paths:
        errs = check(p)
        if errs:
            bad += 1
            print(f"FAIL {p.relative_to(ROOT) if p.is_absolute() else p}")
            for e in errs:
                print(f"   - {e}")
        else:
            print(f"ok   {p.name}")
    print(f"\n{len(paths) - bad} ok, {bad} failing")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
