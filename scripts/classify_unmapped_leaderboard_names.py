#!/usr/bin/env python3
"""Dump unique unmapped leaderboard names vs the live catalogue.

Read-only against cards and ranking_evidence. Writes a JSON index under
benchmarks/_census/ (not ranking_evidence/) for a human classification pass.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import ModelCard  # noqa: E402
from scripts.build_manifest import inspect  # noqa: E402
from scripts.fetch_ranking_leaderboards import (  # noqa: E402
    EFFORT_TOKENS,
    _MAX_SUFFIX,
    slugify,
)

REFUSALS = PROJECT_ROOT / "benchmarks/_census/ranking_evidence/leaderboard_refusals.json"
MODELS = PROJECT_ROOT / "models"
OUT = PROJECT_ROOT / "benchmarks/_census/unmapped_name_index.json"

_NON_SLUG = re.compile(r"[^a-z0-9]+")


def normalize(s: str) -> str:
    return slugify(s)


def tokens(s: str) -> set[str]:
    return {p for p in normalize(s).split("-") if p and p not in {"the", "a", "of"}}


def load_cards() -> list[dict]:
    cards = []
    for path in sorted(MODELS.glob("*/*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        try:
            front = yaml.safe_load(text.split("---", 2)[1]) or {}
        except Exception:
            continue
        model_id = str(front.get("model_id") or "")
        if not model_id:
            continue
        display = str(front.get("display_name") or "")
        cards.append(
            {
                "model_id": model_id,
                "display_name": display,
                "provider": str(front.get("provider") or ""),
                "status": str(front.get("status") or ""),
                "model_type": str(front.get("model_type") or ""),
                "family": str(front.get("family") or ""),
                "version": str(front.get("version") or ""),
                "path": str(path.relative_to(PROJECT_ROOT)),
                "suffix": slugify(model_id),
                "display_slug": slugify(display) if display else slugify(model_id),
            }
        )
    return cards


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def candidates(name: str, cards: list[dict], limit: int = 8) -> list[dict]:
    slug = normalize(name)
    stem = slugify(_MAX_SUFFIX.sub("", name).strip())
    name_toks = tokens(name)
    scored: list[tuple[float, dict]] = []
    for card in cards:
        score = 0.0
        reasons: list[str] = []
        if card["display_name"].strip().lower() == name.strip().lower():
            score += 10
            reasons.append("exact_display")
        if card["display_slug"] == slug or card["suffix"] == slug:
            score += 8
            reasons.append("exact_slug")
        if stem and (card["display_slug"] == stem or card["suffix"] == stem):
            score += 7
            reasons.append("stem_slug")
        if slug in card["display_slug"] or slug in card["suffix"]:
            score += 3
            reasons.append("slug_contains")
        if card["display_slug"] in slug or card["suffix"] in slug:
            score += 2.5
            reasons.append("name_contains_card")
        jac = max(
            jaccard(name_toks, tokens(card["display_name"])),
            jaccard(name_toks, tokens(card["model_id"])),
        )
        if jac >= 0.4:
            score += jac * 4
            reasons.append(f"jaccard={jac:.2f}")
        # shared distinctive tokens
        shared = name_toks & (tokens(card["display_name"]) | tokens(card["model_id"]))
        stop = {"b", "it", "instruct", "chat", "base", "max", "pro", "plus", "mini", "flash"}
        distinctive = shared - stop
        if len(distinctive) >= 2:
            score += 1.5 * len(distinctive)
            reasons.append(f"shared={sorted(distinctive)}")
        if score >= 2.5:
            scored.append(
                (
                    score,
                    {
                        "model_id": card["model_id"],
                        "display_name": card["display_name"],
                        "model_type": card["model_type"],
                        "status": card["status"],
                        "score": round(score, 2),
                        "reasons": reasons,
                    },
                )
            )
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:limit]]


def unrankable_breakdown(cards_meta: list[dict]) -> dict:
    """Recompute unrankable cards from live files (not the cached manifest)."""
    rows = []
    for path in sorted(MODELS.glob("*/*.md")):
        try:
            card = ModelCard.from_yaml_file(path)
        except Exception as exc:
            rows.append({"path": str(path), "error": str(exc)})
            continue
        rec = inspect(path, card)
        if any(g.tier == "unrankable" for g in rec.gaps):
            ident = card.identity
            rows.append(
                {
                    "model_id": ident.model_id,
                    "display_name": ident.display_name,
                    "provider": ident.provider,
                    "status": ident.status.value if hasattr(ident.status, "value") else str(ident.status),
                    "model_type": ident.model_type.value if ident.model_type and hasattr(ident.model_type, "value") else str(ident.model_type or ""),
                    "family": ident.family,
                }
            )
    by_type: dict[str, int] = Counter(r.get("model_type") or "unknown" for r in rows if "error" not in r)
    by_status: dict[str, int] = Counter(r.get("status") or "unknown" for r in rows if "error" not in r)
    by_provider: dict[str, int] = Counter(r.get("provider") or "unknown" for r in rows if "error" not in r)
    return {
        "count": len([r for r in rows if "error" not in r]),
        "errors": [r for r in rows if "error" in r],
        "by_type": dict(by_type.most_common()),
        "by_status": dict(by_status.most_common()),
        "by_provider": dict(by_provider.most_common()),
        "cards": rows,
    }


def main() -> None:
    refusals = json.loads(REFUSALS.read_text(encoding="utf-8"))
    rows = refusals["refusals"]["unmapped_name"]
    counts = Counter(r["name"] for r in rows)
    unique = sorted(counts)
    print(f"unmapped_name rows={len(rows)} unique={len(unique)}")

    cards = load_cards()
    print(f"catalogue cards={len(cards)}")

    names = []
    for name in unique:
        effort = tokens(name) & EFFORT_TOKENS
        is_max = bool(_MAX_SUFFIX.search(name) or normalize(name).endswith("-max"))
        names.append(
            {
                "name": name,
                "cells": counts[name],
                "slug": normalize(name),
                "effort_tokens": sorted(effort),
                "is_max": is_max,
                "candidates": candidates(name, cards),
            }
        )

    print("computing unrankable breakdown (loads every card)...")
    unrank = unrankable_breakdown(cards)
    print(f"unrankable={unrank['count']}")

    payload = {
        "as_of": refusals.get("as_of"),
        "unique_unmapped": len(unique),
        "cells": sum(counts.values()),
        "names": names,
        "unrankable": {
            "count": unrank["count"],
            "by_type": unrank["by_type"],
            "by_status": unrank["by_status"],
            "by_provider": unrank["by_provider"],
            "cards": unrank["cards"],
            "errors": unrank["errors"],
        },
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
