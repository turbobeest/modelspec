#!/usr/bin/env python3
"""Report verified hardware-fact coverage for the open-weights lineup (MODEL-348)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from decision.registry import default as default_registry
from decision.sources import load_sources
from decision.verify import DENSE_ARCHITECTURES, VerificationLog
from scripts.policy.licence_coverage import _card, _cited_kinds, _verified, open_weights_lineup

FACETS = (
    "model.architecture",
    "model.parameters_total",
    "model.parameters_active",
    "model.experts_total",
    "model.experts_per_token",
)
EXPERT_FACETS = frozenset({"model.experts_total", "model.experts_per_token"})


def coverage_report(root: Path, premier: Path | None = None) -> dict:
    """Dense expert counts need no facts; Fact has no inapplicable state.

    A dense exemption needs a known, verified architecture. Card front matter
    alone cannot exempt an unverified model from expert coverage.
    """
    root = Path(root)
    sources = load_sources(root / "registry" / "sources.yaml")
    log = VerificationLog(root / "verification").latest()
    registry = default_registry()
    counts = {
        facet: {"known_verified": 0, "not_disclosed_cited": 0, "dense_exempt": 0, "missing": 0}
        for facet in FACETS
    }
    gaps = []
    for model_id in open_weights_lineup(premier or root / "premier" / "slice-1.yaml"):
        _, facts = _card(root, model_id)
        architecture = facts.get("model.architecture") or {}
        dense = (
            architecture.get("state") == "known"
            and architecture.get("value") in DENSE_ARCHITECTURES
            and _verified(log, model_id, "model.architecture", architecture.get("value"))
        )
        for facet in FACETS:
            if facet in EXPERT_FACETS and dense:
                counts[facet]["dense_exempt"] += 1
                continue
            fact = facts.get(facet) or {}
            value, state = fact.get("value"), fact.get("state")
            verified = _verified(log, model_id, facet, value)
            permitted = set(registry.facet(facet).permitted_source_kinds)
            cited = bool(_cited_kinds(fact, sources) & permitted)
            checked = set(fact.get("checked_sources") or [])
            if state == "known" and verified:
                counts[facet]["known_verified"] += 1
            elif (
                state == "not_disclosed"
                and cited
                and verified
                and checked
                and checked <= sources.keys()
            ):
                counts[facet]["not_disclosed_cited"] += 1
            else:
                counts[facet]["missing"] += 1
                reason = (
                    "unverified"
                    if state in {"known", "not_disclosed"} and not verified
                    else "not_disclosed without permitted citation and checked sources"
                    if state == "not_disclosed"
                    else state or "absent"
                )
                gaps.append(f"{model_id} {facet} {reason}")
    cards = 0
    active = 0
    for path in (root / "models").rglob("*.md"):
        text = path.read_text(encoding="utf-8").split("---", 2)
        if len(text) < 3 or not re.search(r"(?m)^model_id:", text[1]):
            continue
        cards += 1
        block = re.search(r"(?m)^architecture:\n((?:[ \t]+.*\n|\n)*)", text[1])
        if block is None:
            continue
        architecture = yaml.safe_load(block.group(0))["architecture"] or {}
        active += architecture.get("active_parameters") is not None
    return {
        "counts": counts,
        "gaps": gaps,
        "catalogue": {"active_parameters": active, "cards": cards},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    report = coverage_report(args.root)
    for facet, row in report["counts"].items():
        print(
            f"{facet} known_verified={row['known_verified']} "
            f"not_disclosed_cited={row['not_disclosed_cited']} "
            f"dense_exempt={row['dense_exempt']} missing={row['missing']}"
        )
    catalogue = report["catalogue"]
    print(
        f"catalogue architecture.active_parameters={catalogue['active_parameters']} "
        f"of {catalogue['cards']} cards"
    )
    for gap in report["gaps"]:
        print(f"GAP {gap}")
    return 1 if report["gaps"] else 0


if __name__ == "__main__":
    sys.exit(main())
