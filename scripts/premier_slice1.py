#!/usr/bin/env python3
"""Reproduce the slice-1 premier set from the snapshots in ``premier/inputs``.

The snapshots are plain-HTTP reads taken on 2026-09-24. This script does not
fetch anything. It ranks models, maps them onto cards, applies the premier-set
rule, and writes ``premier/slice-1.yaml``.

    python scripts/premier_slice1.py           # write the YAML
    python scripts/premier_slice1.py --check   # fail if the YAML differs
    python scripts/premier_slice1.py --report  # print the cut, write nothing
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.classes import class_for_model_type  # noqa: E402

INPUTS = ROOT / "premier" / "inputs"
OUTPUT = ROOT / "premier" / "slice-1.yaml"

READ_DATE = "2026-09-24"
RELEASE_WINDOW_START = "2026-06-26"  # 90 days before the read date
PAST_YEAR_START = "2025-09-24"

# Slice-1 balance. Sum is 29, inside the "about 30" cap. A short group stays
# short: the script does not borrow from another group to fill it.
QUOTA = {
    "frontier-generation": 12,
    "open-weights-generation": 6,
    "embedding": 4,
    "rerank": 2,
    "vision": 4,
    "decision": 1,
}
# Boards whose tables were current on the read date. The official SWE-bench
# Verified bash table's newest row is 2026-02-26, so it does not lead the cut.
FRESH_BOARDS = {
    "terminal-bench-4.0",
    "swe-bench-pro",
    "arena-text",
    "arena-webdev",
    "arena-vision",
    "matharena-expected",
    "epoch-frontiermath-tiers-1-3-v2",
    "epoch-gpqa-diamond",
    "epoch-swe-bench-verified",
    "scale-hle",
    "mteb-eng-v2",
    "mteb-multilingual-v2",
    "mteb-eng-v2-rerank",
    "mteb-multilingual-v2-rerank",
}
GROUP_ORDER = list(QUOTA)

MAJOR_PLATFORMS = (
    "aws_bedrock",
    "azure_ai_foundry",
    "google_vertex_ai",
    "groq",
    "together_ai",
    "fireworks_ai",
    "replicate",
    "deepinfra",
    "cerebras",
    "sambanova",
    "nvidia_nim",
)
SLICE_CLASSES = {"text-generator", "vectoriser", "orderer", "decider"}

EFFORT = {
    "max",
    "xhigh",
    "x-high",
    "high",
    "medium",
    "low",
    "none",
    "promax",
    "minimal",
    "thinking",
    "non-thinking",
    "nonthinking",
}
_NON_SLUG = re.compile(r"[^a-z0-9]+")
_DATE_TOKEN = re.compile(r"20\d{6}")

# Reviewer addition required by the MODEL-136 brief.
DECISION_MODEL = "typesafe/jev-1-13"


def slug(name: str, *, strip: bool) -> str:
    """Fold a leaderboard name or a card name onto one key."""
    text = (name or "").lower().strip()
    if "/" in text and "://" not in text:
        text = text.rsplit("/", 1)[-1]
    text = text.replace("+", " plus ")
    text = text.replace(".", " ")
    text = re.sub(r"\([^)]*\)", " ", text)
    parts = [p for p in _NON_SLUG.sub(" ", text).split() if p]
    if strip:
        while parts and parts[-1] in EFFORT:
            parts.pop()
        while parts and _DATE_TOKEN.fullmatch(parts[-1]):
            parts.pop()
        while (
            len(parts) >= 3
            and re.fullmatch(r"20\d{2}", parts[-3])
            and re.fullmatch(r"\d{2}", parts[-2])
            and re.fullmatch(r"\d{2}", parts[-1])
        ):
            parts = parts[:-3]
    return "-".join(parts)


def _load_json(name: str) -> dict:
    return json.loads((INPUTS / name).read_text())


def _rows_from_csv(name: str) -> list[dict]:
    with (INPUTS / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def leaderboards() -> list[dict]:
    """One ranking table per board. Higher score is better on every board."""
    boards: list[dict] = []

    swe = _load_json("swebench-verified.json")
    boards.append(
        {
            "id": "swe-bench-verified-bash",
            "domain": "software-engineering",
            "url": swe["source_url"],
            "family": "generation",
            "rows": [
                {
                    "name": row["model_display"] or row["name"],
                    "score": row["resolved"],
                    "date": row["date"],
                    "org": row.get("model_org") or "",
                }
                for row in swe["rows"]
                if row.get("agent") == "mini-SWE-agent" and row.get("resolved") is not None
            ],
        }
    )

    pro = _load_json("swebench-pro.json")
    boards.append(
        {
            "id": "swe-bench-pro",
            "domain": "software-engineering",
            "url": pro["source_url"],
            "family": "generation",
            "rows": [
                {
                    "name": row["model"],
                    "score": row["resolve_rate"],
                    "date": READ_DATE,
                    "org": "",
                }
                for row in pro["rows"]
            ],
        }
    )

    terminal = _load_json("terminal-bench-4.0.json")
    boards.append(
        {
            "id": "terminal-bench-4.0",
            "domain": "software-engineering",
            "url": "https://www.tbench.ai/",
            "family": "generation",
            "rows": [
                {
                    "name": row["model"],
                    "score": row["accuracy"],
                    "date": row["date"],
                    "org": row.get("model_org") or "",
                }
                for row in terminal["rows"]
            ],
        }
    )

    epoch_swe = _rows_from_csv("epoch-swe_bench_verified.csv")
    boards.append(
        {
            "id": "epoch-swe-bench-verified",
            "domain": "software-engineering",
            "url": "https://epoch.ai/benchmarks/use-this-data",
            "family": "generation",
            "rows": [
                {
                    "name": row["Model version"],
                    "score": float(row["mean_score"]),
                    "date": READ_DATE,
                    "org": row.get("Organization") or "",
                }
                for row in epoch_swe
                if row.get("mean_score")
            ],
        }
    )

    for config, domain in (
        ("text", "chat-or-preference"),
        ("webdev", "software-engineering"),
        ("vision", "vision"),
    ):
        arena = _load_json(f"arena-{config}.json")
        boards.append(
            {
                "id": f"arena-{config}",
                "domain": domain,
                "url": arena["source_url"],
                "family": "generation",
                "rows": [
                    {
                        "name": row["model_name"],
                        "score": row["rating"],
                        "date": row["leaderboard_publish_date"],
                        "org": row.get("organization") or "",
                    }
                    for row in arena["rows"]
                ],
            }
        )

    matharena = _load_json("matharena-expected.json")
    boards.append(
        {
            "id": "matharena-expected",
            "domain": "reasoning-and-maths",
            "url": matharena["source_url"],
            "family": "generation",
            "rows": [
                {
                    "name": row["name"],
                    "score": row["capability"],
                    "date": READ_DATE,
                    "org": row.get("creator") or "",
                }
                for row in matharena["rows"]
            ],
        }
    )

    for filename, board_id in (
        ("epoch-frontiermath_tiers_1_3_v2.csv", "epoch-frontiermath-tiers-1-3-v2"),
        ("epoch-gpqa_diamond.csv", "epoch-gpqa-diamond"),
    ):
        boards.append(
            {
                "id": board_id,
                "domain": "reasoning-and-maths",
                "url": "https://epoch.ai/benchmarks/use-this-data",
                "family": "generation",
                "rows": [
                    {
                        "name": row["Model version"],
                        "score": float(row["mean_score"]),
                        "date": READ_DATE,
                        "org": row.get("Organization") or "",
                    }
                    for row in _rows_from_csv(filename)
                    if row.get("mean_score")
                ],
            }
        )

    hle = _load_json("scale-hle.json")
    boards.append(
        {
            "id": "scale-hle",
            "domain": "reasoning-and-maths",
            "url": hle["source_url"],
            "family": "generation",
            "rows": [
                {
                    "name": row["model"],
                    "score": row["accuracy"],
                    "date": READ_DATE,
                    "org": "",
                }
                for row in hle["rows"]
            ],
        }
    )

    for filename, board_id, kind in (
        ("mteb-eng-v2.json", "mteb-eng-v2", "embedding"),
        ("mteb-multilingual-v2.json", "mteb-multilingual-v2", "embedding"),
        ("mteb-eng-v2.json", "mteb-eng-v2-rerank", "rerank"),
        ("mteb-multilingual-v2.json", "mteb-multilingual-v2-rerank", "rerank"),
    ):
        table = _load_json(filename)
        if kind == "embedding":
            source_rows = [
                row for row in table["rows"] if row.get("model_type") != "cross-encoder"
            ]
            score_of = lambda row: row.get("mean_task")  # noqa: E731
        else:
            source_rows = [
                row
                for row in table["rows"]
                if row.get("model_type") == "cross-encoder" and row.get("reranking") is not None
            ]
            score_of = lambda row: row.get("reranking")  # noqa: E731
        boards.append(
            {
                "id": board_id,
                "domain": "retrieval-and-embedding",
                "url": table["api"],
                "family": kind,
                "rows": [
                    {
                        "name": row["name"],
                        "score": score_of(row),
                        "date": READ_DATE,
                        "org": "",
                    }
                    for row in source_rows
                    if score_of(row) is not None
                ],
            }
        )
    return boards


def rank_board(board: dict) -> list[dict]:
    """Best score per model identity, then a rank. Ties at the cutoff all count."""
    best: dict[str, dict] = {}
    for row in board["rows"]:
        key = slug(row["name"], strip=True)
        if not key or row["score"] is None:
            continue
        current = best.get(key)
        if current is None or row["score"] > current["score"]:
            best[key] = {
                "slug": key,
                "name": row["name"],
                "score": row["score"],
                "date": row["date"] or READ_DATE,
                "org": row["org"],
            }
    ordered = sorted(best.values(), key=lambda item: (-item["score"], item["slug"]))
    if not ordered:
        return []
    cutoff = ordered[min(9, len(ordered) - 1)]["score"]
    ranked = []
    for index, item in enumerate(ordered, start=1):
        item = dict(item)
        item["rank"] = index
        # A tie with the 10th score stays in. A shorter board counts every row.
        item["top10"] = item["score"] >= cutoff if len(ordered) >= 10 else True
        item["board"] = board["id"]
        item["domain"] = board["domain"]
        item["url"] = board["url"]
        ranked.append(item)
    return ranked


def load_cards() -> dict[str, dict]:
    cards: dict[str, dict] = {}
    for path in sorted((ROOT / "models").glob("*/*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        try:
            front = yaml.safe_load(text.split("---", 2)[1]) or {}
        except yaml.YAMLError:
            continue
        model_id = str(front.get("model_id") or "")
        if not model_id:
            continue
        licensing = front.get("licensing") or {}
        availability = front.get("availability") or {}
        primary = availability.get("primary_provider") or {}
        platforms = []
        if (primary.get("api_endpoint") or primary.get("model_id_on_platform") or "").strip():
            platforms.append("lab_api")
        for name in MAJOR_PLATFORMS:
            entry = availability.get(name) or {}
            if isinstance(entry, dict) and entry.get("available") is True:
                platforms.append(name)
        release = str(front.get("release_date") or "")[:10]
        retirement = front.get("retirement_date") or front.get("deprecation_date") or None
        cards[model_id] = {
            "model_id": model_id,
            "display_name": str(front.get("display_name") or ""),
            "provider": str(front.get("provider") or ""),
            "status": str(front.get("status") or ""),
            "model_type": str(front.get("model_type") or ""),
            "class_id": class_for_model_type(str(front.get("model_type") or "")) or "",
            "open_weights": licensing.get("open_weights") is True,
            "release_date": release,
            "retirement_date": str(retirement)[:10] if retirement else None,
            "platforms": platforms,
            "path": str(path.relative_to(ROOT)),
        }
    return cards


def match_index(cards: dict[str, dict], aliases: dict[str, str]) -> dict[str, str]:
    """slug -> model_id. An alias wins. Otherwise one unambiguous card."""
    buckets: dict[str, list[str]] = {}
    for model_id, card in cards.items():
        keys = {
            slug(card["display_name"], strip=False),
            slug(card["display_name"], strip=True),
            slug(model_id, strip=False),
            slug(model_id, strip=True),
        }
        for key in keys:
            if key:
                buckets.setdefault(key, []).append(model_id)
    resolved: dict[str, str] = {}
    for key, model_ids in buckets.items():
        unique = list(dict.fromkeys(model_ids))
        if len(unique) == 1:
            resolved[key] = unique[0]
            continue
        undated = [mid for mid in unique if not _DATE_TOKEN.search(mid)]
        active = [mid for mid in (undated or unique) if cards[mid]["status"] == "active"]
        pool = active or undated or unique
        exact = [mid for mid in pool if slug(mid, strip=True) == key or slug(cards[mid]["display_name"], strip=True) == key]
        pool = exact or pool
        if len(pool) == 1:
            resolved[key] = pool[0]
    for key, model_id in aliases.items():
        if model_id in cards:
            resolved[key] = model_id
    return resolved


def bucket_for(card: dict, domains: set[str]) -> str:
    class_id = card["class_id"]
    if class_id == "decider":
        return "decision"
    if class_id == "vectoriser":
        return "embedding"
    if class_id == "orderer":
        return "rerank"
    if card["model_type"] == "vlm" and domains == {"vision"}:
        return "vision"
    if card["open_weights"]:
        return "open-weights-generation"
    return "frontier-generation"


def _evidence(hit: dict) -> dict:
    return {
        "clause": 1,
        "domain": hit["domain"],
        "board": hit["board"],
        "rank": hit["rank"],
        "score": round(float(hit["score"]), 4),
        "model_on_board": hit["name"],
        "url": hit["url"],
        "read_date": READ_DATE,
    }


def build() -> dict:
    aliases = json.loads((INPUTS / "aliases.json").read_text())
    cards = load_cards()
    index = match_index(cards, aliases)

    missing: list[dict] = []
    by_model: dict[str, dict] = {}
    for board in leaderboards():
        for hit in rank_board(board):
            if not hit["top10"]:
                continue
            if hit["date"] and hit["date"] < PAST_YEAR_START:
                continue
            model_id = index.get(hit["slug"])
            if model_id is None:
                missing.append(
                    {
                        "board": hit["board"],
                        "domain": hit["domain"],
                        "rank": hit["rank"],
                        "score": round(float(hit["score"]), 4),
                        "name": hit["name"],
                        "organization": hit["org"],
                        "slug": hit["slug"],
                    }
                )
                continue
            card = cards[model_id]
            entry = by_model.setdefault(
                model_id,
                {"card": card, "evidence": [], "clauses": set()},
            )
            entry["evidence"].append(_evidence(hit))
            entry["clauses"].add(1)

    qualifying_labs = {item["card"]["provider"] for item in by_model.values() if item["card"]["provider"]}

    clause2_pool: list[str] = []
    for model_id, card in cards.items():
        if card["provider"] not in qualifying_labs:
            continue
        if not card["release_date"] or card["release_date"] < RELEASE_WINDOW_START:
            continue
        if card["class_id"] not in SLICE_CLASSES:
            continue
        if card["status"] == "sunset":
            continue
        clause2_pool.append(model_id)
        entry = by_model.setdefault(model_id, {"card": card, "evidence": [], "clauses": set()})
        entry["clauses"].add(2)

    clause3_pool: list[str] = []
    for model_id, card in cards.items():
        if len(card["platforms"]) < 3:
            continue
        if card["class_id"] not in SLICE_CLASSES:
            continue
        if card["status"] == "sunset":
            continue
        clause3_pool.append(model_id)
        entry = by_model.setdefault(model_id, {"card": card, "evidence": [], "clauses": set()})
        entry["clauses"].add(3)
        entry["platforms"] = card["platforms"]

    # Clause 4. The brief names this card; it is not inferred from a board.
    if DECISION_MODEL in cards:
        entry = by_model.setdefault(
            DECISION_MODEL,
            {"card": cards[DECISION_MODEL], "evidence": [], "clauses": set()},
        )
        entry["clauses"].add(4)

    def release_key(model_id: str) -> int:
        raw = by_model[model_id]["card"]["release_date"]
        digits = raw.replace("-", "") if raw else ""
        return int(digits) if digits.isdigit() else 0

    def sort_key(model_id: str) -> tuple:
        entry = by_model[model_id]
        fresh = [
            item["rank"] for item in entry["evidence"] if item["board"] in FRESH_BOARDS
        ]
        fresh_best = min(fresh) if fresh else 50
        return (fresh_best, -release_key(model_id), model_id)

    archived: list[dict] = []
    for model_id, entry in by_model.items():
        card = entry["card"]
        domains = {item["domain"] for item in entry["evidence"]}
        entry["group"] = bucket_for(card, domains)
        if card["status"] == "sunset" and (1 in entry["clauses"] or 4 in entry["clauses"]):
            archived.append(_archived_row(entry))

    # The vision board's leaders are general generators. Holding the four
    # strongest of them in the vision balance keeps that domain in the set
    # without spending the frontier quota on the same four names.
    vision_leaders = []
    for model_id, entry in by_model.items():
        if entry["card"]["status"] == "sunset" or 1 not in entry["clauses"]:
            continue
        vision = [item for item in entry["evidence"] if item["domain"] == "vision"]
        if vision:
            vision_leaders.append((min(item["rank"] for item in vision), model_id))
    vision_leaders.sort()
    for _, model_id in vision_leaders[: QUOTA["vision"]]:
        by_model[model_id]["group"] = "vision"

    grouped: dict[str, list[str]] = {name: [] for name in GROUP_ORDER}
    for model_id, entry in by_model.items():
        if entry["card"]["status"] == "sunset":
            continue
        if entry["group"] in grouped and (1 in entry["clauses"] or 4 in entry["clauses"]):
            grouped[entry["group"]].append(model_id)
    for model_ids in grouped.values():
        model_ids.sort(key=sort_key)

    selected: list[str] = []
    selected_set: set[str] = set()

    def take(group: str, model_ids: list[str]) -> None:
        for model_id in model_ids:
            filled = sum(1 for mid in selected if by_model[mid]["group"] == group)
            if filled >= QUOTA[group]:
                return
            if model_id in selected_set:
                continue
            selected.append(model_id)
            selected_set.add(model_id)

    for group in ("vision", "frontier-generation", "open-weights-generation", "embedding", "rerank", "decision"):
        take(group, grouped[group])

    # A model that reached a top 10 and shipped in the last three weeks is not
    # cut to honour the quota. Grok 4.7 is the case this is here for.
    protected = [
        model_id
        for model_id, entry in by_model.items()
        if 1 in entry["clauses"]
        and entry["card"]["status"] != "sunset"
        and entry["card"]["release_date"] >= "2026-09-01"
    ]
    protected.sort(key=sort_key)
    for model_id in protected:
        if model_id not in selected_set:
            selected.append(model_id)
            selected_set.add(model_id)

    # Clause 2 fills a quota that clause 1 left open, newest release first.
    clause2_only = [
        model_id
        for model_id in clause2_pool
        if model_id not in selected_set and 1 not in by_model[model_id]["clauses"]
    ]
    clause2_only.sort(key=lambda mid: (cards[mid]["release_date"], mid), reverse=True)
    for group in GROUP_ORDER:
        pool = [
            model_id
            for model_id in clause2_only
            if bucket_for(cards[model_id], set()) == group
        ]
        take(group, pool)

    clause3_only = [
        model_id
        for model_id in clause3_pool
        if model_id not in selected_set and 1 not in by_model[model_id]["clauses"]
    ]
    clause3_only.sort(key=lambda mid: (-len(cards[mid]["platforms"]), mid))
    for group in GROUP_ORDER:
        pool = [
            model_id
            for model_id in clause3_only
            if bucket_for(cards[model_id], set()) == group
        ]
        take(group, pool)

    models = []
    for model_id in selected:
        entry = by_model[model_id]
        card = entry["card"]
        clauses = []
        for item in sorted(entry["evidence"], key=lambda row: (row["domain"], row["board"], row["rank"])):
            clauses.append(item)
        if 2 in entry["clauses"]:
            clauses.append(
                {
                    "clause": 2,
                    "release_date": card["release_date"],
                    "lab": card["provider"],
                    "note": (
                        "Released on or after "
                        f"{RELEASE_WINDOW_START} by {card['provider']}, a lab with a "
                        "top-10 model on a current board."
                    ),
                }
            )
        if 3 in entry["clauses"]:
            clauses.append(
                {
                    "clause": 3,
                    "providers": card["platforms"],
                    "note": "At least three recorded major providers on the card.",
                }
            )
        if 4 in entry["clauses"]:
            clauses.append(
                {
                    "clause": 4,
                    "note": (
                        "Reviewer addition. The MODEL-136 brief requires one "
                        "decision model, and this card is the TypeSafe Jev card."
                    ),
                }
            )
        row = {
            "model_id": model_id,
            "display_name": card["display_name"],
            "class": card["class_id"],
            "model_type": card["model_type"],
            "slice1_group": entry["group"],
            "open_weights": card["open_weights"],
            "status": card["status"],
            "release_date": card["release_date"] or None,
            "lab": card["provider"],
            "clauses": clauses,
        }
        if card["status"] == "deprecated":
            row["retirement_date"] = card["retirement_date"]
        models.append(row)

    models.sort(
        key=lambda row: (
            GROUP_ORDER.index(row["slice1_group"]) if row["slice1_group"] in GROUP_ORDER else 99,
            row["model_id"],
        )
    )

    near = []
    for model_id, entry in sorted(by_model.items()):
        if model_id in selected_set:
            continue
        card = entry["card"]
        if card["status"] == "sunset":
            continue
        if 1 in entry["clauses"]:
            why = f"clause 1 on {entry['group']}; outside that group's slice-1 quota"
        else:
            continue
        near.append(
            {
                "model_id": model_id,
                "display_name": card["display_name"],
                "class": card["class_id"],
                "slice1_group": entry["group"],
                "why": why,
            }
        )

    newest_by_lab: dict[str, list[str]] = {}
    for model_id in clause2_only:
        lab = cards[model_id]["provider"]
        newest_by_lab.setdefault(lab, []).append(model_id)
    for lab, model_ids in sorted(newest_by_lab.items()):
        model_ids.sort(key=lambda mid: cards[mid]["release_date"], reverse=True)
        for model_id in model_ids[:3]:
            if model_id in selected_set:
                continue
            card = cards[model_id]
            near.append(
                {
                    "model_id": model_id,
                    "display_name": card["display_name"],
                    "class": card["class_id"],
                    "slice1_group": bucket_for(card, set()),
                    "why": (
                        f"clause 2; among the three newest {lab} releases in the "
                        "window and not needed to fill a quota"
                    ),
                }
            )

    missing.sort(key=lambda row: (row["board"], row["rank"], row["slug"]))
    # One row per board+slug.
    seen_missing = set()
    missing_unique = []
    for row in missing:
        key = (row["board"], row["slug"])
        if key in seen_missing:
            continue
        seen_missing.add(key)
        missing_unique.append(row)

    return {
        "schema_version": 1,
        "status": "pending-jamie-approval",
        "read_date": READ_DATE,
        "release_window_start": RELEASE_WINDOW_START,
        "rule": [
            "Top 10 of its class on a slice-1 board, after collapsing effort settings of the same model.",
            "Released on or after the window start by a lab that has a model in the first clause.",
            "At least three major providers recorded on the card.",
            "A reviewer added it. Slice 1 adds the TypeSafe Jev card.",
        ],
        "quota": QUOTA,
        "models": models,
        "archived": archived,
        "missing_cards": missing_unique,
        "near_misses": near,
        "counts": {
            "selected": len(models),
            "clause_1_cards": sum(1 for entry in by_model.values() if 1 in entry["clauses"]),
            "clause_2_pool": len(clause2_pool),
            "clause_3_pool": len(clause3_pool),
            "missing_top10_rows": len(missing_unique),
        },
    }


def _archived_row(entry: dict) -> dict:
    card = entry["card"]
    return {
        "model_id": card["model_id"],
        "display_name": card["display_name"],
        "status": card["status"],
        "why": "Sunset on the card, so it leaves the premier set for the live archive.",
    }


def _dump(document: dict) -> str:
    return yaml.safe_dump(
        document,
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the YAML differs")
    parser.add_argument("--report", action="store_true", help="print a short summary")
    args = parser.parse_args()
    document = build()
    if args.report:
        counts: dict[str, int] = {}
        for row in document["models"]:
            counts[row["slice1_group"]] = counts.get(row["slice1_group"], 0) + 1
        print("selected", document["counts"])
        print("groups", counts)
        for row in document["models"]:
            boards = sorted({item["board"] for item in row["clauses"] if item.get("board")})
            print(f"  {row['slice1_group']:24} {row['model_id']}  {boards}")
        print("missing", len(document["missing_cards"]))
        for row in document["missing_cards"]:
            if row["rank"] <= 10:
                print(f"  {row['board']:28} #{row['rank']} {row['name']}")
        return 0
    text = _dump(document)
    if args.check:
        current = OUTPUT.read_text() if OUTPUT.exists() else ""
        if yaml.safe_load(current) != document:
            print("premier/slice-1.yaml does not match the script", file=sys.stderr)
            return 1
        return 0
    OUTPUT.write_text(text)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({document['counts']['selected']} models)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
