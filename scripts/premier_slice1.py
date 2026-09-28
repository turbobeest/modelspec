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
from decision.excluded import excluded_sources  # noqa: E402
from decision.model import value_hash, verification_counts  # noqa: E402
from decision.registry import default as default_registry  # noqa: E402
from decision.sources import load_sources  # noqa: E402

INPUTS = ROOT / "premier" / "inputs"
OUTPUT = ROOT / "premier" / "slice-1.yaml"
SLICE2_INPUT = INPUTS / "slice-2.yaml"

READ_DATE = "2026-09-24"
RELEASE_WINDOW_START = "2026-06-26"  # 90 days before the read date
PAST_YEAR_START = "2025-09-24"

# Slice-1 balance. Sum is 29, inside the "about 30" cap. A short group stays
# short: the script does not borrow from another group to fill it.
QUOTA = {
    "frontier-generation": 12,
    "open-weights-generation": 6,
    "embedding": 6,
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
            source_rows = [row for row in table["rows"] if row.get("model_type") != "cross-encoder"]
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
    verifications = _verification_index()
    guaranteed = {
        facet.id
        for facet in default_registry().facets()
        if facet.subject == "model"
        and facet.tier == "guaranteed"
        and facet.computed_by is None
    }
    for path in sorted((ROOT / "models").glob("*/*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        frontmatter = text.split("---", 2)[1]

        def scalar(name: str) -> str:
            match = re.search(rf"(?m)^{re.escape(name)}:\s*['\"]?([^\n'\"]*)", frontmatter)
            return match.group(1).strip() if match else ""

        data = yaml.safe_load(frontmatter)
        model_id = scalar("model_id")
        if not model_id:
            continue
        platforms = []
        availability = frontmatter.partition("\navailability:")[2].partition("\nbenchmarks:")[0]
        primary = re.search(
            r"(?ms)^  primary_provider:\n(.*?)(?=^  [a-z][a-z0-9_]*:|\Z)", availability
        )
        if primary and re.search(
            r"(?m)^    (?:api_endpoint|model_id_on_platform):\s*\S+", primary.group(1)
        ):
            platforms.append("lab_api")
        for name in MAJOR_PLATFORMS:
            entry = re.search(
                rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  [a-z][a-z0-9_]*:|\Z)",
                availability,
            )
            if entry and re.search(r"(?m)^    available:\s*true\s*$", entry.group(1)):
                platforms.append(name)
        open_match = re.search(
            r"(?ms)^licensing:\n.*?^  open_weights:\s*(true|false)\s*$", frontmatter
        )
        release = scalar("release_date")[:10]
        retirement = scalar("retirement_date") or scalar("deprecation_date") or None
        model_type = scalar("model_type")
        verified_facets = {
            str(fact["facet"])
            for fact in data.get("facts") or []
            if fact.get("facet")
            and fact.get("sources")
            and (
                verification := verifications.get(
                    (
                        "fact",
                        f"{model_id}#{fact['facet']}",
                        value_hash(fact.get("value")),
                    )
                )
            )
            and verification["outcome"] == "verified"
        }
        cards[model_id] = {
            "model_id": model_id,
            "display_name": scalar("display_name"),
            "provider": scalar("provider"),
            "status": scalar("status"),
            "model_type": model_type,
            "class_id": class_for_model_type(model_type) or "",
            "open_weights": bool(open_match and open_match.group(1) == "true"),
            "release_date": release,
            "retirement_date": str(retirement)[:10] if retirement else None,
            "platforms": platforms,
            "guaranteed_facts_verified": guaranteed <= verified_facets,
            "path": str(path.relative_to(ROOT)),
        }
    return cards


def _verification_index() -> dict[tuple[str, str, str], dict]:
    """Latest counting verification for each exact record value."""
    latest: dict[tuple[str, str, str], tuple[str, int, dict]] = {}
    path = ROOT / "verification" / "log.jsonl"
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not verification_counts(
            str(row["outcome"]),
            str(row["collector"]["model_family"]),
            str(row["verifier"]["model_family"]),
        ):
            continue
        target = row["target"]
        key = (str(target["kind"]), str(target["id"]), str(target["value_hash"]))
        candidate = (str(row["date"]), line_number, row)
        if key not in latest or candidate[:2] >= latest[key][:2]:
            latest[key] = candidate
    return {key: row for key, (_, _, row) in latest.items()}


def _record_is_admitted(
    record: dict,
    *,
    kind: str,
    value_field: str,
    verifications: dict[tuple[str, str, str], dict],
    source_urls: dict[str, str],
) -> bool:
    record_id = record.get("id")
    sources = record.get("sources") or []
    source_ids = [str(source.get("source_id") or "") for source in sources]
    if (
        not record_id
        or not source_ids
        or any(source_id not in source_urls for source_id in source_ids)
    ):
        return False
    guard = excluded_sources()
    if any(guard.url(source_urls[source_id]) for source_id in source_ids):
        return False
    if kind == "evidence" and guard.benchmark(record.get("benchmark_id")):
        return False
    key = (kind, str(record_id), value_hash(record.get(value_field)))
    verification = verifications.get(key)
    return verification is not None and verification["outcome"] == "verified"


def select_budget_candidates(candidates: list[dict], *, quota_per_class: int) -> list[dict]:
    """Select the cheapest eligible candidates in each class."""
    by_class: dict[str, list[dict]] = {}
    for candidate in candidates:
        if not candidate.get("prices_verified") or not candidate.get("has_admitted_evidence"):
            continue
        by_class.setdefault(str(candidate["class"]), []).append(candidate)
    selected = []
    for class_id in sorted(by_class):
        rows = sorted(
            by_class[class_id],
            key=lambda row: (
                float(row["input_price_per_million"]),
                float(row["output_price_per_million"]),
                str(row["model_id"]),
            ),
        )
        selected.extend(rows[:quota_per_class])
    return selected


def select_widely_offered_candidates(
    cards: dict[str, dict], *, minimum_major_providers: int
) -> list[dict]:
    """Select every card offered by the required number of major providers."""
    selected = []
    for model_id, card in cards.items():
        providers = sorted(set(card.get("platforms") or []))
        if card.get("guaranteed_facts_verified") and len(providers) >= minimum_major_providers:
            selected.append({"model_id": model_id, "providers": providers})
    return sorted(selected, key=lambda row: row["model_id"])


def select_local_candidates(candidates: list[dict], *, max_memory_gb: float) -> list[dict]:
    """Admit local models only when every size fact is verified and runtime fits."""
    return [
        candidate
        for candidate in candidates
        if candidate.get("parameter_verified")
        and candidate.get("artifact_verified")
        and candidate.get("runtime_memory_verified")
        and float(candidate["published_size_gb"]) <= max_memory_gb
        and float(candidate["runtime_memory_gb"]) <= max_memory_gb
    ]


def local_candidate_universe(candidates: list[dict]) -> list[dict]:
    """Attach exact-value verification state to the filed local facts."""
    verifications = _verification_index()
    suffixes = {
        "parameter_verified": ("model.parameters_total", "parameter_count"),
        "artifact_verified": ("local.quantised_size_bytes", "published_size_bytes"),
        "runtime_memory_verified": ("local.runtime_memory_gb", "runtime_memory_gb"),
    }
    normalized = []
    for candidate in candidates:
        row = dict(candidate)
        for flag, (suffix, value_field) in suffixes.items():
            key = (
                "fact",
                f"{row['model_id']}#{suffix}",
                value_hash(row.get(value_field)),
            )
            verification = verifications.get(key)
            row[flag] = verification is not None and verification["outcome"] == "verified"
        normalized.append(row)
    return normalized


def budget_candidate_universe(cards: dict[str, dict]) -> list[dict]:
    """Derive budget candidates from admitted offering prices and card evidence."""
    verifications = _verification_index()
    sources = load_sources(ROOT / "registry" / "sources.yaml")
    source_urls = {source_id: str(source.url) for source_id, source in sources.items()}

    evidence_by_model: dict[str, dict] = {}
    for model_id, card in cards.items():
        raw = yaml.safe_load((ROOT / card["path"]).read_text(encoding="utf-8").split("---", 2)[1])
        for evidence in (raw.get("benchmarks") or {}).get("evidence") or []:
            if _record_is_admitted(
                evidence,
                kind="evidence",
                value_field="score",
                verifications=verifications,
                source_urls=source_urls,
            ):
                evidence_by_model[model_id] = evidence
                break

    cheapest: dict[str, dict] = {}
    for path in sorted((ROOT / "offerings").glob("*/*/*.yaml")):
        for offering in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            model_id = str(offering.get("model") or "")
            card = cards.get(model_id)
            if card is None or card["status"] == "sunset" or model_id not in evidence_by_model:
                continue
            facts = {fact.get("facet"): fact for fact in offering.get("facts") or []}
            input_fact = facts.get("offering.price.input")
            output_fact = facts.get("offering.price.output")
            if not input_fact or not output_fact:
                continue
            prices_verified = all(
                _record_is_admitted(
                    fact,
                    kind="fact",
                    value_field="value",
                    verifications=verifications,
                    source_urls=source_urls,
                )
                and fact.get("state") == "known"
                and isinstance(fact.get("value"), int | float)
                for fact in (input_fact, output_fact)
            )
            if not prices_verified:
                continue
            source_id = str((input_fact.get("sources") or [{}])[0].get("source_id") or "")
            candidate = {
                "model_id": model_id,
                "class": card["class_id"],
                "input_price_per_million": input_fact["value"],
                "output_price_per_million": output_fact["value"],
                "benchmark_id": evidence_by_model[model_id]["benchmark_id"],
                "source_url": source_urls[source_id],
                "read_date": str(input_fact.get("verified_at") or "2026-09-26")[:10],
                "prices_verified": True,
                "has_admitted_evidence": True,
            }
            current = cheapest.get(model_id)
            key = (candidate["input_price_per_million"], candidate["output_price_per_million"])
            if current is None or key < (
                current["input_price_per_million"],
                current["output_price_per_million"],
            ):
                cheapest[model_id] = candidate
    return list(cheapest.values())


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
        exact = [
            mid
            for mid in pool
            if slug(mid, strip=True) == key or slug(cards[mid]["display_name"], strip=True) == key
        ]
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
    slice2 = yaml.safe_load(SLICE2_INPUT.read_text(encoding="utf-8"))

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

    qualifying_labs = {
        item["card"]["provider"] for item in by_model.values() if item["card"]["provider"]
    }

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

    widely_offered_candidates = select_widely_offered_candidates(
        cards,
        minimum_major_providers=int(slice2["widely_offered"]["minimum_major_providers"]),
    )
    widely_offered = {candidate["model_id"] for candidate in widely_offered_candidates}
    clause3_pool: list[str] = []
    for candidate in widely_offered_candidates:
        model_id = candidate["model_id"]
        card = cards[model_id]
        if card["class_id"] not in SLICE_CLASSES:
            continue
        if card["status"] == "sunset":
            continue
        clause3_pool.append(model_id)
        entry = by_model.setdefault(model_id, {"card": card, "evidence": [], "clauses": set()})
        entry["clauses"].add(3)
        entry["platforms"] = candidate["providers"]

    # Clause 4. The brief names this card; it is not inferred from a board.
    if DECISION_MODEL in cards:
        entry = by_model.setdefault(
            DECISION_MODEL,
            {"card": cards[DECISION_MODEL], "evidence": [], "clauses": set()},
        )
        entry["clauses"].add(4)

    budget_candidates = select_budget_candidates(
        budget_candidate_universe(cards),
        quota_per_class=int(slice2["budget"]["quota_per_class"]),
    )
    for candidate in budget_candidates:
        model_id = candidate["model_id"]
        entry = by_model.setdefault(
            model_id, {"card": cards[model_id], "evidence": [], "clauses": set()}
        )
        entry["clauses"].add(5)
        entry["budget"] = candidate

    local_limit = float(slice2["local"]["max_memory_gb"])
    local_candidates = select_local_candidates(
        local_candidate_universe(slice2["local"]["candidates"]),
        max_memory_gb=local_limit,
    )
    for candidate in local_candidates:
        model_id = candidate["model_id"]
        if model_id not in cards or cards[model_id]["status"] == "sunset":
            continue
        entry = by_model.setdefault(
            model_id, {"card": cards[model_id], "evidence": [], "clauses": set()}
        )
        entry["clauses"].add(6)
        entry["local"] = candidate

    def release_key(model_id: str) -> int:
        raw = by_model[model_id]["card"]["release_date"]
        digits = raw.replace("-", "") if raw else ""
        return int(digits) if digits.isdigit() else 0

    def sort_key(model_id: str) -> tuple:
        entry = by_model[model_id]
        fresh = [item["rank"] for item in entry["evidence"] if item["board"] in FRESH_BOARDS]
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

    for group in (
        "vision",
        "frontier-generation",
        "open-weights-generation",
        "embedding",
        "rerank",
        "decision",
    ):
        take(group, grouped[group])

    # Slice 2 clauses are additions to the balanced frontier cut. Clause 3 is
    # no longer suppressed by a full quota: continued sale by three major
    # providers is the evidence that keeps an older model in the live lineup.
    supplemental = [
        model_id
        for model_id, entry in by_model.items()
        if entry["card"]["status"] != "sunset"
        and (entry["clauses"].intersection({5, 6}) or model_id in widely_offered)
    ]
    supplemental.sort()
    for model_id in supplemental:
        if model_id not in selected_set:
            selected.append(model_id)
            selected_set.add(model_id)

    # A model that reached a top 10 and shipped in the last three weeks is not
    # cut to honour the quota. Grok 4.7 is the case this is here for.
    protected = [
        model_id
        for model_id, entry in by_model.items()
        if entry["card"]["status"] != "sunset"
        and (
            (1 in entry["clauses"] and entry["card"]["release_date"] >= "2026-09-01")
            or (2 in entry["clauses"] and entry["card"]["release_date"] >= "2026-09-19")
        )
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
            model_id for model_id in clause2_only if bucket_for(cards[model_id], set()) == group
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
            model_id for model_id in clause3_only if bucket_for(cards[model_id], set()) == group
        ]
        take(group, pool)

    models = []
    for model_id in selected:
        entry = by_model[model_id]
        card = entry["card"]
        clauses = []
        for item in sorted(
            entry["evidence"],
            key=lambda row: (row["domain"], row["board"], row["rank"]),
        ):
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
        if 5 in entry["clauses"]:
            candidate = entry["budget"]
            clauses.append(
                {
                    "clause": 5,
                    "class": candidate["class"],
                    "input_price_per_million": candidate["input_price_per_million"],
                    "output_price_per_million": candidate["output_price_per_million"],
                    "benchmark": candidate["benchmark_id"],
                    "url": candidate["source_url"],
                    "read_date": candidate["read_date"],
                    "note": "Within the cheapest verified, benchmarked candidates in its class.",
                }
            )
        if 6 in entry["clauses"]:
            candidate = entry["local"]
            clauses.append(
                {
                    "clause": 6,
                    "quantisation": candidate["quantisation"],
                    "parameter_count": candidate["parameter_count"],
                    "published_size_bytes": candidate["published_size_bytes"],
                    "published_size_gb": candidate["published_size_gb"],
                    "runtime_memory_gb": candidate["runtime_memory_gb"],
                    "context_tokens": candidate["context_tokens"],
                    "memory_method": candidate["memory_method"],
                    "max_memory_gb": slice2["local"]["max_memory_gb"],
                    "parameter_url": candidate["parameter_source_url"],
                    "artifact_url": candidate["size_source_url"],
                    "url": candidate["memory_source_url"],
                    "read_date": candidate["read_date"],
                    "note": (
                        "The published runtime-memory requirement at this quantisation and "
                        "context is no larger than the 24 GB limit."
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
        "status": "approved",
        "approved_date": "2026-09-26",
        "read_date": READ_DATE,
        "release_window_start": RELEASE_WINDOW_START,
        "rule": [
            "Top 10 of its class on a slice-1 board, after collapsing effort "
            "settings of the same model.",
            "Released on or after the window start by a lab that has a model in the first clause.",
            "At least three major providers recorded on the card.",
            "A reviewer added it. Slice 1 adds the TypeSafe Jev card.",
            "Among the cheapest verified candidates in its class with admitted benchmark evidence.",
            "Verified parameter count, quantised artifact size, and runtime/peak memory "
            "at the stated quantisation and context all fit the 24 GB consumer-hardware limit.",
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
