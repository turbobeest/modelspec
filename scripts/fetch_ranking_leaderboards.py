#!/usr/bin/env python3
"""Harvest ranked-benchmark scores from AA and LM Arena live leaderboards.

The two highest-value census targets:

    https://artificialanalysis.ai/leaderboards/models
    https://lmarena.ai/leaderboard

Default fetch is a plain HTTP GET of those pages (0 Firecrawl credits). The
HTML already carries the Next.js flight payloads with per-model scores.
Firecrawl markdown is available via --firecrawl but is not required; JSON /
query / highlight formats are refused by the fetch path.

Observation dates come from the cache metadata written at fetch time, never
from a later parse pass.

    python scripts/fetch_ranking_leaderboards.py --no-fetch --dry-run
    python scripts/fetch_ranking_leaderboards.py --budget 300
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.ranking.engine import USE_CASE_PROFILES  # noqa: E402
from schema.card import BenchmarkEvidence  # noqa: E402
from scripts.benchmarks.fetch import (  # noqa: E402
    DEFAULT_BUDGET,
    RAW_CACHE,
    CachedPage,
    CreditBudgetExceeded,
    CreditGuard,
    load_or_get,
    remaining_credits,
    resolve_key,
    scrape,
)

RANKING_LEDGER = PROJECT_ROOT / "benchmarks/_census/ranking_evidence/accepted.json"
REFUSALS_PATH = PROJECT_ROOT / "benchmarks/_census/ranking_evidence/leaderboard_refusals.json"
PROPOSED_MAP_PATH = PROJECT_ROOT / "benchmarks/_census/ranking_evidence/ledger_to_card_proposed.json"

AA_URL = "https://artificialanalysis.ai/leaderboards/models"
ARENA_URL = "https://lmarena.ai/leaderboard"

# Live-board columns that ARE ranked keys. Identity must be exact.
# AA `gpqa` is GPQA Diamond per artificialanalysis.ai/methodology/intelligence-benchmarking.
AA_FIELD_TO_RANKED: dict[str, tuple[str, str, str]] = {
    "gpqa": ("gpqa_diamond", "percent", "GPQA Diamond"),
    "scicode": ("scicode", "percent", "SciCode"),
    "lcr": ("aa_lcr", "percent", "AA-LCR v1.1"),
    "gdpvalNormalized": ("gdpval_aa", "percent", "GDPval-AA v2 normalized Elo percent"),
    "critpt": ("critpt", "percent", "CritPt"),
}

AA_REFUSED_FIELDS: dict[str, str] = {
    "intelligenceIndex": "AA Intelligence Index is a composite, not a ranked raw benchmark",
    "mmmuPro": "MMMU-Pro is not the ranked key mmmu",
    "terminalbenchV21": "Terminal-Bench 2.1 is not terminal_bench (v1.0)",
    "terminalbenchV40": "Terminal-Bench 4.0 is not terminal_bench (v1.0)",
    "terminalbenchHard": "Terminal-Bench Hard is not terminal_bench (v1.0)",
    "tau2": "τ2-bench is not the ranked key tau_bench",
    "tauBanking": "τ-bench banking split is not the ranked key tau_bench",
    "hle": "Humanity's Last Exam is not in the ranked key set",
    "ifbench": "IFBench is not the ranked key ifeval",
    "omniscience": "AA-Omniscience is not a ranked key",
    "analystAgent": "Analyst-Agent is not a ranked key",
    "apexAgents": "APEX-Agents is not a ranked key",
    "itbenchSre": "ITBench-SRE is not a ranked key",
}

# Snapshot id on the Arena overview page → ranked key. Style-control overall
# is the only snapshot on /leaderboard whose identity matches a ranked key.
ARENA_SNAPSHOT_TO_RANKED: dict[str, tuple[str, str, str]] = {
    "text-overall-style_control": (
        "arena_elo_style_control",
        "elo",
        "Text Arena overall, style-controlled",
    ),
}

ARENA_REFUSED_SNAPSHOTS: dict[str, str] = {
    "webdev-overall-raw": "WebDev arena Elo is not arena_elo_coding",
    "vision-overall-style_control": (
        "Vision style-control Elo is not the ranked key arena_elo_vision"
    ),
    "document-overall-raw": "Document arena is not a ranked key",
    "text_to_image-overall-raw": "Image arena is not a ranked LLM key",
    "image_edit-overall-raw": "Image-edit arena is not a ranked LLM key",
    "image_to_webdev-overall-raw": "Image-to-WebDev is not arena_elo_coding",
    "search-overall-raw": "Search arena is not a ranked key",
    "text_to_video-overall-raw": "Video arena is not a ranked LLM key",
    "image_to_video-overall-raw": "Video arena is not a ranked LLM key",
    "video_to_video-overall-raw": "Video arena is not a ranked LLM key",
}

# Effort / serving tokens that mean "this row is not the base product card".
# `max` is handled separately: AA and Arena use it as the canonical product row.
EFFORT_TOKENS = frozenset(
    {
        "high",
        "low",
        "medium",
        "xhigh",
        "x-high",
        "xh",
        "thinking",
        "reasoning",
        "non-reasoning",
        "nonreasoning",
        "preview",
        "experimental",
        "fast",
        "turbo",
        "search",
        "grounding",
        "latest",
    }
)

_NON_SLUG = re.compile(r"[^a-z0-9]+")
_MAX_SUFFIX = re.compile(r"(?:\s*\(max\)|[-_\s]max)$", re.I)
_PAREN_QUALIFIER = re.compile(r"\(([^)]+)\)")


def ranked_benchmarks() -> set[str]:
    keys: set[str] = set()
    for profile in USE_CASE_PROFILES.values():
        keys.update((profile.get("benchmark_weights") or {}).keys())
    return keys


def slugify(name: str) -> str:
    s = name.lower().strip()
    if "/" in s and "://" not in s:
        s = s.rsplit("/", 1)[-1]
    s = s.replace("+", "-plus-")
    s = s.replace(".", "-")
    s = _NON_SLUG.sub("-", s)
    return re.sub(r"-+", "-", s).strip("-")


def iter_next_f_strings(html: str) -> list[str]:
    """Decode Next.js `self.__next_f.push(...)` payloads to their string bodies."""
    marker = "self.__next_f.push("
    decoder = json.JSONDecoder()
    out: list[str] = []
    start = 0
    while True:
        i = html.find(marker, start)
        if i < 0:
            break
        j = i + len(marker)
        try:
            payload, end = decoder.raw_decode(html, j)
        except json.JSONDecodeError:
            start = j
            continue
        start = end
        if isinstance(payload, list) and len(payload) >= 2 and isinstance(payload[1], str):
            body = payload[1]
            if re.match(r"^[0-9a-fA-F]+:", body[:8] or ""):
                body = body.split(":", 1)[1]
            out.append(body)
    return out


def extract_json_after(text: str, needle: str) -> Any | None:
    idx = text.find(needle)
    if idx < 0:
        return None
    start = idx + len(needle)
    try:
        value, _end = json.JSONDecoder().raw_decode(text, start)
    except json.JSONDecodeError:
        return None
    return value


def parse_aa_models(html: str) -> list[dict[str, Any]]:
    for body in iter_next_f_strings(html):
        models = extract_json_after(body, '"models":')
        if isinstance(models, list) and models and isinstance(models[0], dict):
            if "intelligenceIndex" in models[0] or "shortName" in models[0]:
                return models
    return []


def parse_arena_snapshots(html: str) -> dict[str, list[dict[str, Any]]]:
    found: dict[str, list[dict[str, Any]]] = {}
    decoder = json.JSONDecoder()
    pattern = re.compile(
        r'leaderboards/([a-z0-9_./-]+)/leaderboard-snapshots/latest","entries":'
    )
    for body in iter_next_f_strings(html):
        for match in pattern.finditer(body):
            slug = match.group(1)
            try:
                entries, _end = decoder.raw_decode(body, match.end())
            except json.JSONDecodeError:
                continue
            if isinstance(entries, list):
                found[slug] = entries
    return found


def parse_stated_date(text: str) -> str | None:
    """Prefer a snapshot / as-of / last-updated day when the page states one."""
    patterns = [
        re.compile(
            r"(?:as of|last updated|updated on|snapshot(?: date)?)[:\s]+"
            r"(20\d{2}-\d{2}-\d{2})",
            re.I,
        ),
        re.compile(
            r"(?:as of|last updated|updated on)\s+"
            r"([A-Z][a-z]+ \d{1,2}, 20\d{2})",
            re.I,
        ),
    ]
    for pat in patterns:
        match = pat.search(text)
        if not match:
            continue
        raw = match.group(1)
        if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", raw):
            return raw
        try:
            return datetime.strptime(raw, "%B %d, %Y").date().isoformat()
        except ValueError:
            continue
    return None


@dataclass
class ExtractedScore:
    evaluator_name: str
    benchmark_id: str
    score: float
    unit: str
    source_url: str
    evidence_date: str
    date_type: str
    date_source: str
    benchmark_version: str
    configuration: str
    source_kind: str = "independent_evaluator"


@dataclass
class Refusal:
    cause: str
    detail: str
    name: str = ""
    extra: str = ""


def _aa_score_as_percent(value: Any) -> float | None:
    if value is None or value == "$undefined":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:  # NaN
        return None
    # AA stores accuracies as 0-1 fractions. An already-percent 0-100 value
    # would be > 1 for every real result on these benches.
    if 0.0 <= number <= 1.0:
        return round(number * 100.0, 2)
    if 1.0 < number <= 100.0:
        return round(number, 2)
    return None


def extract_aa(
    page: CachedPage, ranked: set[str]
) -> tuple[list[ExtractedScore], list[Refusal]]:
    models = parse_aa_models(page.text)
    refusals: list[Refusal] = [
        Refusal(cause="aa_field_not_ranked", detail=reason, extra=field)
        for field, reason in AA_REFUSED_FIELDS.items()
    ]
    if not models:
        refusals.append(Refusal(cause="parse_empty", detail="no AA models array in page HTML"))
        return [], refusals

    stated = parse_stated_date(page.text)
    if stated:
        evidence_date, date_type, date_source = stated, "evaluated", "stated_on_page"
    else:
        evidence_date, date_type, date_source = (
            page.observation_date,
            "evaluated",
            "observation_fetch_date",
        )

    scores: list[ExtractedScore] = []
    for model in models:
        name = str(model.get("shortName") or model.get("slug") or "").strip()
        if not name:
            refusals.append(Refusal(cause="missing_name", detail="AA row with no shortName"))
            continue
        for field, (benchmark_id, unit, version) in AA_FIELD_TO_RANKED.items():
            if benchmark_id not in ranked:
                refusals.append(
                    Refusal(
                        cause="ranked_key_missing",
                        detail=f"{benchmark_id} is not in USE_CASE_PROFILES",
                        extra=field,
                    )
                )
                continue
            raw = model.get(field)
            percent = _aa_score_as_percent(raw)
            if percent is None:
                continue
            scores.append(
                ExtractedScore(
                    evaluator_name=name,
                    benchmark_id=benchmark_id,
                    score=percent,
                    unit=unit,
                    source_url=AA_URL,
                    evidence_date=evidence_date,
                    date_type=date_type,
                    date_source=date_source,
                    benchmark_version=version,
                    configuration=(
                        f"Artificial Analysis live LLM leaderboard. "
                        f"Column {field} = {version}. "
                        f"evidence_date {date_source}={evidence_date}."
                    ),
                )
            )
    return scores, refusals


def extract_arena(
    page: CachedPage, ranked: set[str]
) -> tuple[list[ExtractedScore], list[Refusal]]:
    snapshots = parse_arena_snapshots(page.text)
    refusals: list[Refusal] = []
    for slug, reason in ARENA_REFUSED_SNAPSHOTS.items():
        if slug in snapshots:
            refusals.append(
                Refusal(
                    cause="arena_variant_mismatch",
                    detail=reason,
                    extra=slug,
                    name=f"{len(snapshots[slug])} rows",
                )
            )
        else:
            refusals.append(
                Refusal(cause="arena_variant_mismatch", detail=reason, extra=slug)
            )
    for slug in snapshots:
        if slug not in ARENA_SNAPSHOT_TO_RANKED and slug not in ARENA_REFUSED_SNAPSHOTS:
            refusals.append(
                Refusal(
                    cause="arena_variant_unknown",
                    detail="snapshot id is not a ranked Arena Elo key; refused rather than guessed",
                    extra=slug,
                    name=f"{len(snapshots[slug])} rows",
                )
            )

    if not snapshots:
        refusals.append(Refusal(cause="parse_empty", detail="no Arena snapshot arrays in page HTML"))
        return [], refusals

    stated = parse_stated_date(page.text)
    if stated:
        evidence_date, date_type, date_source = stated, "evaluated", "stated_on_page"
    else:
        evidence_date, date_type, date_source = (
            page.observation_date,
            "evaluated",
            "observation_fetch_date",
        )

    scores: list[ExtractedScore] = []
    for slug, (benchmark_id, unit, version) in ARENA_SNAPSHOT_TO_RANKED.items():
        if benchmark_id not in ranked:
            refusals.append(
                Refusal(
                    cause="ranked_key_missing",
                    detail=f"{benchmark_id} is not in USE_CASE_PROFILES",
                    extra=slug,
                )
            )
            continue
        entries = snapshots.get(slug) or []
        for entry in entries:
            name = str(entry.get("modelDisplayName") or entry.get("modelKey") or "").strip()
            if not name:
                refusals.append(Refusal(cause="missing_name", detail="Arena row with no display name"))
                continue
            try:
                rating = float(entry["rating"])
            except (KeyError, TypeError, ValueError):
                continue
            scores.append(
                ExtractedScore(
                    evaluator_name=name,
                    benchmark_id=benchmark_id,
                    score=round(rating, 2),
                    unit=unit,
                    source_url=ARENA_URL,
                    evidence_date=evidence_date,
                    date_type=date_type,
                    date_source=date_source,
                    benchmark_version=version,
                    configuration=(
                        f"LM Arena live board ({slug}). "
                        f"{version}. Style-control overall is not raw overall "
                        f"and is not a category Elo. "
                        f"evidence_date {date_source}={evidence_date}."
                    ),
                )
            )
    return scores, refusals


@dataclass
class CardRef:
    model_id: str
    display_name: str
    suffix: str
    display_slug: str


def load_cards() -> list[CardRef]:
    import yaml

    cards: list[CardRef] = []
    for path in sorted((PROJECT_ROOT / "models").rglob("*.md")):
        if path.name == "LICENSE.md":
            continue
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
        suffix = slugify(model_id)
        cards.append(
            CardRef(
                model_id=model_id,
                display_name=display,
                suffix=suffix,
                display_slug=slugify(display) if display else suffix,
            )
        )
    return cards


def _tokens(slug: str) -> set[str]:
    return {part for part in slug.split("-") if part}


def _effort_tokens(slug: str) -> set[str]:
    return _tokens(slug) & EFFORT_TOKENS


_SIBLING_TAILS = frozenset({"instruct", "it", "chat", "instruct-tuned"})


def _instruct_sibling_exists(name: str, cards: list[CardRef]) -> bool:
    """Unqualified 'Llama 3.1 405B' must not steal the Instruct card's score, or vice versa."""
    stem = name.strip().lower()
    if not stem:
        return False
    for card in cards:
        display = card.display_name.strip().lower()
        if display == stem:
            continue
        if display.startswith(stem):
            rest = display[len(stem):].strip(" -_")
            if rest in _SIBLING_TAILS:
                return True
        if stem.startswith(display):
            rest = stem[len(display):].strip(" -_")
            if rest in _SIBLING_TAILS:
                return True
    return False


def propose_explicit_maps(
    names: Iterable[str], cards: list[CardRef]
) -> tuple[dict[str, str], list[Refusal]]:
    """Unique exact matches only. Effort variants other than canonical (max) are refused.

    This function is used to *propose* literal LEDGER_TO_CARD entries. Attach
    still uses only the explicit dict — it never calls this at write time.
    """
    by_display: dict[str, list[CardRef]] = defaultdict(list)
    by_slug: dict[str, list[CardRef]] = defaultdict(list)
    for card in cards:
        if card.display_name:
            by_display[card.display_name.strip().lower()].append(card)
        by_slug[card.display_slug].append(card)
        by_slug[card.suffix].append(card)

    mapping: dict[str, str] = {}
    refusals: list[Refusal] = []

    def unique(hits: list[CardRef]) -> CardRef | None:
        ids = {card.model_id for card in hits}
        if len(ids) == 1:
            return hits[0]
        return None

    for name in names:
        raw = name.strip()
        if not raw:
            continue
        lower = raw.lower()
        display_hits = by_display.get(lower, [])
        exact = unique(display_hits)
        if exact:
            already_qualified = bool(_tokens(slugify(raw)) & _SIBLING_TAILS)
            if not already_qualified and _instruct_sibling_exists(raw, cards):
                refusals.append(
                    Refusal(
                        cause="ambiguous_name",
                        detail="unqualified name has an Instruct/IT/Chat sibling card",
                        name=raw,
                        extra=exact.model_id,
                    )
                )
                continue
            mapping[raw] = exact.model_id
            continue

        slug = slugify(raw)
        effort = _effort_tokens(slug)
        is_max = bool(_MAX_SUFFIX.search(raw) or slug.endswith("-max"))
        if effort and not is_max:
            refusals.append(
                Refusal(
                    cause="effort_variant",
                    detail="row is an effort/serving variant, not the base product",
                    name=raw,
                    extra=",".join(sorted(effort)),
                )
            )
            continue
        if effort and is_max:
            # `max` is a product-default on these boards, but high/low mixed in
            # the same slug is not.
            extra = effort - {"max"}
            if extra:
                refusals.append(
                    Refusal(
                        cause="effort_variant",
                        detail="max row also carries another effort token",
                        name=raw,
                        extra=",".join(sorted(extra)),
                    )
                )
                continue

        stem = _MAX_SUFFIX.sub("", raw).strip()
        stem_lower = stem.lower()
        stem_hits = by_display.get(stem_lower, [])
        stem_card = unique(stem_hits)
        if is_max and stem_card:
            mapping[raw] = stem_card.model_id
            continue

        slug_stem = slugify(stem)
        slug_hits = by_slug.get(slug_stem, [])
        slug_card = unique(slug_hits)
        if slug_card and not _effort_tokens(slug_stem):
            # A unique slug hit is only accepted when the evaluator slug and
            # the card slug are the same string — no leftover tokens.
            if slug_stem in {slug_card.suffix, slug_card.display_slug}:
                mapping[raw] = slug_card.model_id
                continue

        if len(display_hits) > 1 or len(slug_hits) > 1:
            ids = sorted({c.model_id for c in display_hits + slug_hits})
            refusals.append(
                Refusal(
                    cause="ambiguous_name",
                    detail="name matches more than one card",
                    name=raw,
                    extra=",".join(ids),
                )
            )
            continue

        refusals.append(
            Refusal(
                cause="unmapped_name",
                detail="no unique exact card match",
                name=raw,
            )
        )

    return mapping, refusals


def to_ledger_row(score: ExtractedScore, verified_at: str) -> dict[str, Any]:
    record = {
        "model_id": score.evaluator_name,
        "score": score.score,
        "unit": score.unit,
        "source_url": score.source_url,
        "source_kind": score.source_kind,
        "evidence_date": score.evidence_date,
        "date_type": score.date_type,
        "verified_at": verified_at,
        "benchmark_version": score.benchmark_version,
        "configuration": score.configuration,
    }
    # Refuse to emit a row the card schema would reject.
    BenchmarkEvidence(
        benchmark_id=score.benchmark_id,
        model_id_as_evaluated=record["model_id"],
        score=record["score"],
        unit=record["unit"],
        source_url=record["source_url"],
        source_kind=record["source_kind"],
        evidence_date=record["evidence_date"],
        date_type=record["date_type"],
        verified_at=record["verified_at"],
        benchmark_version=record["benchmark_version"],
        configuration=record["configuration"],
    )
    return record


def merge_ledger(
    existing: dict[str, Any],
    new_rows: list[tuple[str, dict[str, Any]]],
) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    for row in existing.get("rows") or []:
        cid = row.get("canonical_id")
        if cid:
            by_id[cid] = row
    for canonical_id, result in new_rows:
        bucket = by_id.setdefault(
            canonical_id,
            {"canonical_id": canonical_id, "status": "active", "accepted_results": []},
        )
        accepted = bucket.setdefault("accepted_results", [])
        key = (result["model_id"], result["source_url"], result["score"])
        seen = {(r.get("model_id"), r.get("source_url"), r.get("score")) for r in accepted}
        if key not in seen:
            accepted.append(result)
    existing["rows"] = [by_id[k] for k in sorted(by_id)]
    return existing


def group_refusals(refusals: list[Refusal]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in refusals:
        grouped[row.cause].append(
            {"name": row.name, "detail": row.detail, "extra": row.extra}
        )
    return dict(grouped)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument(
        "--budget",
        type=int,
        default=DEFAULT_BUDGET,
        help=f"Firecrawl credit budget if --firecrawl is set (default {DEFAULT_BUDGET})",
    )
    parser.add_argument(
        "--firecrawl",
        action="store_true",
        help="also scrape markdown through Firecrawl (1 credit/page). HTML GET is the parser input.",
    )
    parser.add_argument("--cache-dir", default=str(RAW_CACHE))
    args = parser.parse_args(argv)

    cache_dir = Path(args.cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = PROJECT_ROOT / cache_dir

    ranked = ranked_benchmarks()
    credits: dict[str, Any] = {
        "opening": None,
        "spent": 0,
        "closing": None,
        "guard_hit": False,
        "fetcher": "http_get",
    }
    key = resolve_key()
    if key:
        try:
            credits["opening"] = remaining_credits(key)
            credits["closing"] = credits["opening"]
        except Exception as exc:
            credits["credit_usage_error"] = str(exc)

    pages: dict[str, CachedPage] = {}
    page_errors: list[str] = []
    for url, suffix in ((AA_URL, ".html"), (ARENA_URL, ".html")):
        try:
            pages[url] = load_or_get(url, cache_dir, fetch=not args.no_fetch, suffix=suffix)
        except Exception as exc:
            page_errors.append(f"{url}: {exc}")
            print(f"  FAIL {url}: {exc}")

    if args.firecrawl:
        credits["fetcher"] = "firecrawl+http_get"
        if not key:
            print("no Firecrawl key; cannot honour --firecrawl", file=sys.stderr)
            return 2
        guard = CreditGuard(key=key, budget=args.budget)
        opening = guard.start()
        credits["opening"] = opening
        print(f"credits opening={opening} budget={args.budget}")
        try:
            for url in (AA_URL, ARENA_URL):
                scrape(
                    url,
                    formats=["markdown"],
                    guard=guard,
                    named_cache_dir=cache_dir,
                )
        except CreditBudgetExceeded as exc:
            credits["guard_hit"] = True
            credits["spent"] = exc.spent
            credits["closing"] = exc.remaining
            print(str(exc), file=sys.stderr)
            return 3
        credits["closing"] = guard.last_remaining
        credits["spent"] = guard.spent()
        print(
            f"credits remaining={credits['closing']} spent={credits['spent']} "
            f"closing={credits['closing']}"
        )
    elif credits["opening"] is not None and key:
        try:
            credits["closing"] = remaining_credits(key)
            credits["spent"] = credits["opening"] - credits["closing"]
        except Exception:
            pass

    all_scores: list[ExtractedScore] = []
    all_refusals: list[Refusal] = []
    if AA_URL in pages:
        scores, refusals = extract_aa(pages[AA_URL], ranked)
        all_scores.extend(scores)
        all_refusals.extend(refusals)
        print(
            f"  AA {pages[AA_URL].path.name} fetched_at={pages[AA_URL].observation_date} "
            f"from_cache={pages[AA_URL].from_cache} scores={len(scores)}"
        )
    if ARENA_URL in pages:
        scores, refusals = extract_arena(pages[ARENA_URL], ranked)
        all_scores.extend(scores)
        all_refusals.extend(refusals)
        print(
            f"  Arena {pages[ARENA_URL].path.name} fetched_at={pages[ARENA_URL].observation_date} "
            f"from_cache={pages[ARENA_URL].from_cache} scores={len(scores)}"
        )

    cards = load_cards()
    names = [score.evaluator_name for score in all_scores]
    proposed, map_refusals = propose_explicit_maps(names, cards)
    # Harvest writes only names a human put in LEDGER_TO_CARD. Unique
    # display/slug proposals are reported beside the ledger; they do not
    # attach a score until they are copied into that dict.
    from scripts.attach_evidence import LEDGER_TO_CARD

    map_refusals = [row for row in map_refusals if row.name not in LEDGER_TO_CARD]
    all_refusals.extend(map_refusals)

    mapped_scores = [s for s in all_scores if s.evaluator_name in LEDGER_TO_CARD]
    unmapped_scores = [s for s in all_scores if s.evaluator_name not in LEDGER_TO_CARD]
    print(
        f"{len(all_scores)} extracted scores; {len(mapped_scores)} with LEDGER_TO_CARD maps "
        f"({len(proposed)} unique display/slug proposals); "
        f"{len(unmapped_scores)} unmapped"
    )

    verified_at = datetime.now(UTC).date().isoformat()
    ledger_rows = [
        (score.benchmark_id, to_ledger_row(score, verified_at)) for score in mapped_scores
    ]

    if not args.dry_run:
        if RANKING_LEDGER.is_file():
            existing = json.loads(RANKING_LEDGER.read_text(encoding="utf-8"))
        else:
            existing = {"as_of": verified_at, "note": "", "rows": []}
        note = existing.get("note") or ""
        live_note = (
            " Live leaderboard readings (AA, LM Arena) use date_type=evaluated "
            "and evidence_date=observation (fetch) date unless the page states an as-of."
        )
        if "Live leaderboard readings" not in note:
            existing["note"] = (note + live_note).strip()
        existing["as_of"] = verified_at
        merge_ledger(existing, ledger_rows)
        RANKING_LEDGER.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        PROPOSED_MAP_PATH.write_text(
            json.dumps(proposed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        REFUSALS_PATH.write_text(
            json.dumps(
                {
                    "as_of": verified_at,
                    "credits": credits,
                    "page_errors": page_errors,
                    "extracted": len(all_scores),
                    "mapped": len(mapped_scores),
                    "unmapped": len(unmapped_scores),
                    "refusals": group_refusals(all_refusals),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {RANKING_LEDGER}")
        print(f"wrote {PROPOSED_MAP_PATH} ({len(proposed)} explicit maps)")
        print(f"wrote {REFUSALS_PATH}")
    else:
        print("(dry run) proposed maps", len(proposed))
        print(json.dumps(credits))

    grouped = group_refusals(all_refusals)
    for cause, rows in sorted(grouped.items()):
        print(f"  REFUSAL {cause}: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
