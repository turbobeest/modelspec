#!/usr/bin/env python3
"""Lineup coverage of the four licence facets for open-weights premier models.

Lists every open-weights lineup model whose ``licence.commercial_use``,
``licence.user_cap``, ``licence.output_training`` or ``licence.fine_tuning``
fact is absent, unknown, unverified in the log, or ``not_disclosed`` without
a citation whose source kind is in that facet's ``permitted_source_kinds``.
Exits non-zero when any model is listed.

``licence.user_cap`` permits ``licence_text`` only. The other three also
permit ``provider_terms``. A verified ``not_disclosed`` cited only to a
README is still a gap.

modelspec-data's data-trust audit should call this. Wiring that audit is a
later workflow change and is human-merged; this script adds no workflow.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from decision.model import value_hash
from decision.registry import default as default_registry
from decision.sources import load_sources
from decision.verify import VerificationLog

FACETS = (
    "licence.commercial_use",
    "licence.user_cap",
    "licence.output_training",
    "licence.fine_tuning",
)


def open_weights_lineup(premier: Path) -> list[str]:
    """Premier ``model_id`` values whose entry sets ``open_weights: true``."""
    data = yaml.safe_load(premier.read_text(encoding="utf-8")) or {}
    rows = data.get("models") if isinstance(data, dict) else data
    found = []
    for row in rows or []:
        if isinstance(row, dict) and row.get("open_weights") is True and row.get("model_id"):
            found.append(row["model_id"])
    return found


def _front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    return yaml.safe_load(text.split("---", 2)[1]) or {}


def _facts(root: Path, model_id: str) -> dict[str, dict]:
    path = root / "models" / f"{model_id}.md"
    if not path.is_file():
        return {}
    raw = _front_matter(path).get("facts") or []
    return {fact["facet"]: fact for fact in raw if isinstance(fact, dict) and fact.get("facet")}


def _cited_kinds(fact: dict, sources: dict) -> set[str]:
    kinds = set()
    for ref in fact.get("sources") or []:
        source = sources.get(ref.get("source_id"))
        if source is not None and source.kind:
            kinds.add(source.kind)
    return kinds


def _verified(log: dict, model_id: str, facet: str, value) -> bool:
    record = log.get(("fact", f"{model_id}#{facet}"))
    return (
        record is not None
        and record.outcome == "verified"
        and record.target.value_hash == value_hash(value)
    )


def coverage_report(root: Path, premier: Path) -> dict:
    """Gaps and per-facet counts for the open-weights lineup.

    Counts partition each facet: ``known_verified``, ``not_disclosed_cited``
    (and verified), ``failing``.
    """
    root = Path(root)
    registry = default_registry()
    sources = load_sources(root / "registry" / "sources.yaml")
    log = VerificationLog(root / "verification").latest()
    counts = {facet: {"known_verified": 0, "not_disclosed_cited": 0, "failing": 0}
              for facet in FACETS}
    gaps: list[str] = []
    for model_id in open_weights_lineup(Path(premier)):
        facts = _facts(root, model_id)
        for facet in FACETS:
            fact = facts.get(facet)
            permitted = set(registry.facet(facet).permitted_source_kinds)
            if fact is None:
                gaps.append(f"{model_id} {facet} absent")
                counts[facet]["failing"] += 1
                continue
            state = fact.get("state")
            value = fact.get("value")
            verified = _verified(log, model_id, facet, value)
            cited = _cited_kinds(fact, sources) & permitted
            if state == "known" and verified:
                counts[facet]["known_verified"] += 1
                continue
            if state == "not_disclosed" and cited and verified:
                counts[facet]["not_disclosed_cited"] += 1
                continue
            counts[facet]["failing"] += 1
            if state == "unknown" or state not in {"known", "not_disclosed"}:
                gaps.append(f"{model_id} {facet} {state or 'absent'}")
            elif not verified:
                gaps.append(f"{model_id} {facet} unverified")
            else:
                gaps.append(f"{model_id} {facet} not_disclosed without permitted citation")
    return {"gaps": gaps, "counts": counts}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--premier", type=Path, default=None)
    args = parser.parse_args(argv)
    premier = args.premier or (args.root / "premier" / "slice-1.yaml")
    report = coverage_report(args.root, premier)
    for facet, row in report["counts"].items():
        print(
            f"{facet} known_verified={row['known_verified']} "
            f"not_disclosed_cited={row['not_disclosed_cited']} failing={row['failing']}"
        )
    for gap in report["gaps"]:
        print(f"GAP {gap}")
    return 1 if report["gaps"] else 0


if __name__ == "__main__":
    sys.exit(main())
