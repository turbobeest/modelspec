#!/usr/bin/env python3
"""Fill cost.input, cost.output and context_window from provider pricing pages.

A wrong price is worse than no price: it makes a model look affordable or
unaffordable when it is not. Matching is conservative. Ambiguous rows are
refused, never guessed. Existing values are never overwritten.

Only those three fields are written, and only where the card currently has
none. Benchmarks are ignored entirely — a pricing page that also shows
scores is not BenchmarkEvidence.

    python scripts/fetch_pricing.py --dry-run
    python scripts/fetch_pricing.py
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import ModelCard  # noqa: E402

DEFAULT_URLS = (
    "https://www.together.ai/pricing",
    "https://docs.together.ai/docs/serverless-models",
    "https://fireworks.ai/pricing",
    "https://docs.fireworks.ai/serverless/pricing",
)

WRITE_FIELDS = ("cost.input", "cost.output", "context_window")

# Serving-path tokens that mean "this row is not the base model".
# flash/plus/max/pro stay in the name — those are products, not SKUs.
SERVING_QUALIFIERS = frozenset(
    {
        "fast",
        "lite",
        "turbo",
        "throughput",
        "us",
        "fp8",
        "nvfp4",
        "preview",
        "highspeed",
    }
)

LINK_RE = re.compile(r"\[(.*?)\]\((https?://[^)]+)\)", re.DOTALL)
IMG_RE = re.compile(r"!\[.*?\]\([^)]*\)", re.DOTALL)
BR_RE = re.compile(r"\\?<br\s*/?>", re.IGNORECASE)
DOLLAR_RE = re.compile(r"\$\s*(\d+(?:\.\d+)?)")
NON_SLUG_RE = re.compile(r"[^a-z0-9-]+")
MULTI_HYPHEN_RE = re.compile(r"-+")


@dataclass(frozen=True)
class PricingRow:
    name: str
    source_url: str
    input_per_million: float | None = None
    output_per_million: float | None = None
    context_window: int | None = None
    api_id: str = ""
    page_slug: str = ""

    def values(self) -> dict[str, float | int]:
        out: dict[str, float | int] = {}
        if self.input_per_million is not None:
            out["cost.input"] = self.input_per_million
        if self.output_per_million is not None:
            out["cost.output"] = self.output_per_million
        if self.context_window is not None:
            out["context_window"] = self.context_window
        return out


@dataclass
class CardRef:
    model_id: str
    path: Path
    display_name: str
    suffix: str
    existing: dict[str, float | int | None]


# ─── Slugs ────────────────────────────────────────────────────────


def slugify(name: str) -> str:
    """Comparable slug: last path component, punctuation to hyphens."""
    s = name.lower().strip()
    if "://" in s:
        s = urlparse(s).path.rstrip("/").split("/")[-1]
    elif "/" in s:
        s = s.rsplit("/", 1)[-1]
    s = s.replace(".", "-")
    s = s.replace("_", "-")
    s = NON_SLUG_RE.sub("-", s)
    s = MULTI_HYPHEN_RE.sub("-", s)
    return s.strip("-")


def _extra_tokens(left: str, right: str) -> set[str]:
    return set(left.split("-")) - set(right.split("-")) - {""}


def url_slug_is_safe(display_slug: str, url_slug: str) -> bool:
    """Drop a page slug when the display name adds a serving-path qualifier.

    Fireworks lists "Kimi K3 Fast" with a URL that still ends in kimi-k3.
    Using that URL would write Fast prices onto the base card.
    """
    if not url_slug:
        return False
    if display_slug == url_slug:
        return True
    extra = _extra_tokens(display_slug, url_slug)
    return not (extra & SERVING_QUALIFIERS)


def match_keys(row: PricingRow) -> tuple[str, ...]:
    keys: list[str] = []
    seen: set[str] = set()

    def add(raw: str) -> None:
        slug = slugify(raw)
        if slug and slug not in seen:
            seen.add(slug)
            keys.append(slug)

    add(row.name)
    if row.api_id:
        add(row.api_id)
    if row.page_slug and url_slug_is_safe(slugify(row.name), row.page_slug):
        add(row.page_slug)
    return tuple(keys)


# ─── Markdown tables ──────────────────────────────────────────────


def _norm_header(cell: str) -> str:
    text = BR_RE.sub(" ", cell)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def _split_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells)


def iter_pipe_tables(markdown: str) -> list[tuple[list[str], list[list[str]]]]:
    tables: list[tuple[list[str], list[list[str]]]] = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        cells = _split_row(lines[i])
        if len(cells) >= 2 and i + 1 < len(lines):
            nxt = _split_row(lines[i + 1])
            if _is_separator(nxt) and len(nxt) == len(cells):
                rows: list[list[str]] = []
                j = i + 2
                while j < len(lines):
                    row = _split_row(lines[j])
                    if not row or _is_separator(row):
                        break
                    if len(row) != len(cells):
                        break
                    rows.append(row)
                    j += 1
                tables.append((cells, rows))
                i = j
                continue
        i += 1
    return tables


def classify_table(headers: list[str]) -> str | None:
    """Return a parser kind, or None if the table is not token input/output."""
    h = [_norm_header(c) for c in headers]
    joined = " | ".join(h)
    skip_needles = (
        "price per mp",
        "per image",
        "per video",
        "per audio",
        "default steps",
        "prefill",
        "train / 1m",
        "parameter count",
        "lora sft",
        "gpu type",
        "ptu",
    )
    if any(needle in joined for needle in skip_needles):
        return None
    if any("standard" == x or x.startswith("standard") for x in h) and any(
        "model" in x for x in h
    ):
        return "fireworks_standard"
    has_input = any(x == "input" or x.startswith("input pricing") for x in h)
    has_output = any(x == "output" or x.startswith("output pricing") for x in h)
    if has_input and has_output:
        return "input_output"
    return None


def _col(headers: list[str], *needles: str) -> int | None:
    normalized = [_norm_header(h) for h in headers]
    for needle in needles:
        for i, header in enumerate(normalized):
            if header == needle or header.startswith(needle):
                return i
    return None


def _visible_name(cell: str) -> str:
    text = IMG_RE.sub("", cell)
    text = BR_RE.sub("\n", text)
    links = list(LINK_RE.finditer(text))
    if links:
        inner = links[-1].group(1)
        inner = IMG_RE.sub("", inner)
        inner = BR_RE.sub("\n", inner)
        text = inner
    parts = [p.strip(" \t\\") for p in text.split("\n") if p.strip(" \t\\")]
    name = parts[-1] if parts else ""
    name = re.sub(r"\s+", " ", name).strip()
    name = name.replace("\\[", "[").replace("\\]", "]")
    return name


def _model_page_urls(cell: str) -> list[str]:
    """Model product URLs only — skip CDN image assets nested in the same cell."""
    urls = re.findall(r"https?://[^)\s]+", cell)
    kept: list[str] = []
    for url in urls:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        if any(marker in host for marker in ("cdn.", "website-files", "twimg")):
            continue
        if path.endswith((".svg", ".png", ".webp", ".jpg", ".jpeg", ".gif")):
            continue
        if "/models/" in path:
            kept.append(url)
    return kept


def _page_slug(cell: str) -> str:
    urls = _model_page_urls(cell)
    if not urls:
        return ""
    return slugify(urls[-1])


def parse_price(raw: str) -> float | None:
    """First dollar amount on the first line. Cached / Free / $0 are omitted."""
    if not raw:
        return None
    first = BR_RE.split(raw, maxsplit=1)[0]
    first = first.strip()
    lowered = first.lower()
    if lowered in {"", "-", "—", "free", "n/a", "na"}:
        return None
    match = DOLLAR_RE.search(first)
    if not match:
        return None
    value = float(match.group(1))
    if value <= 0:
        return None
    return value


def parse_context(raw: str) -> int | None:
    """Integer token counts only. '128K' is ambiguous (128000 vs 131072)."""
    text = BR_RE.sub(" ", raw or "").strip().replace(",", "")
    text = re.sub(r"\s+", "", text)
    if not text or text in {"-", "—", "n/a", "na"}:
        return None
    if re.fullmatch(r"\d+", text):
        number = int(text)
        return number if number > 0 else None
    return None


def parse_standard_triplet(raw: str) -> tuple[float | None, float | None]:
    """Fireworks Standard cell: input / cached input / output."""
    parts = [p.strip() for p in (raw or "").split("/")]
    if len(parts) < 3:
        return None, None
    return parse_price(parts[0]), parse_price(parts[2])


def rows_from_table(
    headers: list[str], body: list[list[str]], source_url: str
) -> list[PricingRow]:
    kind = classify_table(headers)
    if kind is None:
        return []
    name_i = _col(headers, "model name", "model")
    if name_i is None:
        return []
    api_i = _col(headers, "api model string", "model string for api")
    ctx_i = _col(headers, "context length", "context")
    rows: list[PricingRow] = []
    for cells in body:
        name = _visible_name(cells[name_i])
        if not name:
            continue
        page_slug = _page_slug(cells[name_i])
        api_id = cells[api_i].strip() if api_i is not None else ""
        context = parse_context(cells[ctx_i]) if ctx_i is not None else None
        if kind == "fireworks_standard":
            std_i = _col(headers, "standard")
            if std_i is None:
                continue
            inp, out = parse_standard_triplet(cells[std_i])
        else:
            inp_i = _col(headers, "input pricing", "input")
            out_i = _col(headers, "output pricing", "output")
            if inp_i is None or out_i is None:
                continue
            inp = parse_price(cells[inp_i])
            out = parse_price(cells[out_i])
        if inp is None and out is None and context is None:
            continue
        rows.append(
            PricingRow(
                name=name,
                source_url=source_url,
                input_per_million=inp,
                output_per_million=out,
                context_window=context,
                api_id=api_id,
                page_slug=page_slug,
            )
        )
    return rows


def extract_pricing_rows(markdown: str, source_url: str) -> list[PricingRow]:
    extracted: list[PricingRow] = []
    for headers, body in iter_pipe_tables(markdown):
        extracted.extend(rows_from_table(headers, body, source_url))
    return extracted


# ─── Matching ─────────────────────────────────────────────────────


def build_card_indexes(
    cards: list[CardRef],
) -> tuple[dict[str, list[CardRef]], list[str]]:
    """slug -> cards. A slug that hits two cards is unusable."""
    index: dict[str, list[CardRef]] = defaultdict(list)
    for card in cards:
        keys = {card.suffix, slugify(card.display_name)}
        for key in keys:
            if key:
                bucket = index[key]
                if card not in bucket:
                    bucket.append(card)
    ambiguous = sorted(key for key, hits in index.items() if len(hits) > 1)
    return index, ambiguous


def match_row(
    row: PricingRow, index: dict[str, list[CardRef]]
) -> tuple[CardRef | None, str | None]:
    """Return (card, None) on a unique hit, or (None, reason) to refuse/skip."""
    keys = match_keys(row)
    hits: list[CardRef] = []
    seen_ids: set[str] = set()
    ambiguous_keys: list[str] = []
    for key in keys:
        found = index.get(key, [])
        if len(found) > 1:
            ambiguous_keys.append(key)
            continue
        if len(found) == 1 and found[0].model_id not in seen_ids:
            hits.append(found[0])
            seen_ids.add(found[0].model_id)
    if ambiguous_keys:
        return None, f"ambiguous_slug:{','.join(ambiguous_keys)}"
    if len(hits) > 1:
        ids = ",".join(card.model_id for card in hits)
        return None, f"keys_point_at_different_cards:{ids}"
    if len(hits) == 1:
        return hits[0], None
    return None, None


def apply_values(
    existing: dict[str, float | int | None], fetched: dict[str, float | int]
) -> tuple[dict[str, float | int], list[dict[str, Any]], list[str]]:
    """Split fetched values into gained / conflicts / already-matching.

    A non-null existing value is never overwritten.
    """
    gained: dict[str, float | int] = {}
    conflicts: list[dict[str, Any]] = []
    already: list[str] = []
    for field_name, value in fetched.items():
        current = existing.get(field_name)
        if current is None:
            gained[field_name] = value
        elif _values_equal(current, value):
            already.append(field_name)
        else:
            conflicts.append(
                {"field": field_name, "existing": current, "fetched": value}
            )
    return gained, conflicts, already


def _values_equal(left: float | int, right: float | int) -> bool:
    if isinstance(left, int) and isinstance(right, int):
        return left == right
    return abs(float(left) - float(right)) < 1e-9


def merge_row_values(
    rows: list[PricingRow],
) -> tuple[dict[str, float | int], list[dict[str, Any]]]:
    """Collapse rows for one card. Disagreeing sources refuse that field."""
    by_field: dict[str, list[tuple[float | int, PricingRow]]] = defaultdict(list)
    for row in rows:
        for field_name, value in row.values().items():
            by_field[field_name].append((value, row))
    merged: dict[str, float | int] = {}
    conflicts: list[dict[str, Any]] = []
    for field_name, entries in by_field.items():
        distinct: list[float | int] = []
        for value, _row in entries:
            if not any(_values_equal(value, seen) for seen in distinct):
                distinct.append(value)
        if len(distinct) == 1:
            merged[field_name] = distinct[0]
        else:
            conflicts.append(
                {
                    "field": field_name,
                    "values": [
                        {
                            "value": value,
                            "source_url": row.source_url,
                            "name": row.name,
                        }
                        for value, row in entries
                    ],
                }
            )
    return merged, conflicts


# ─── Cards / writes ───────────────────────────────────────────────


def _card_paths() -> list[Path]:
    return [
        path
        for path in sorted((PROJECT_ROOT / "models").rglob("*.md"))
        if path.name != "LICENSE.md"
    ]


def existing_from_card(card: ModelCard) -> dict[str, float | int | None]:
    return {
        "cost.input": card.cost.input,
        "cost.output": card.cost.output,
        "context_window": card.modalities.text.context_window,
    }


def load_cards() -> list[CardRef]:
    refs: list[CardRef] = []
    for path in _card_paths():
        try:
            card = ModelCard.from_yaml_file(path)
        except Exception as exc:
            print(f"  SKIP unreadable {path.relative_to(PROJECT_ROOT)}: {exc}")
            continue
        model_id = card.identity.model_id
        refs.append(
            CardRef(
                model_id=model_id,
                path=path,
                display_name=card.identity.display_name,
                suffix=slugify(model_id),
                existing=existing_from_card(card),
            )
        )
    return refs


def _set_dotted(front: dict[str, Any], dotted: str, value: float | int) -> None:
    if dotted == "context_window":
        modalities = front.setdefault("modalities", {}) or {}
        text = modalities.setdefault("text", {}) or {}
        text["context_window"] = value
        modalities["text"] = text
        front["modalities"] = modalities
        return
    if dotted.startswith("cost."):
        cost = front.setdefault("cost", {}) or {}
        cost[dotted.split(".", 1)[1]] = value
        front["cost"] = cost
        return
    raise ValueError(f"refusing to write {dotted}")


def write_fields(path: Path, gained: dict[str, float | int]) -> None:
    """Patch only the three allowed fields, then refuse to leave a broken card."""
    unknown = [key for key in gained if key not in WRITE_FIELDS]
    if unknown:
        raise ValueError(f"refusing to write {unknown}")
    original = path.read_text(encoding="utf-8")
    parts = original.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path} has no YAML frontmatter")
    front_raw, body = parts[1], parts[2]
    front = yaml.safe_load(front_raw) or {}
    for dotted, value in gained.items():
        _set_dotted(front, dotted, value)
    path.write_text(
        "---\n"
        + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
        + "---"
        + body,
        encoding="utf-8",
    )
    try:
        round_tripped = ModelCard.from_yaml_file(path)
        if "cost.input" in gained and round_tripped.cost.input != gained["cost.input"]:
            raise ValueError("cost.input did not round-trip")
        if "cost.output" in gained and round_tripped.cost.output != gained["cost.output"]:
            raise ValueError("cost.output did not round-trip")
        if (
            "context_window" in gained
            and round_tripped.modalities.text.context_window != gained["context_window"]
        ):
            raise ValueError("context_window did not round-trip")
    except Exception:
        path.write_text(original, encoding="utf-8")
        raise


# ─── Fetch ────────────────────────────────────────────────────────


def cache_path_for(url: str, cache_dir: Path) -> Path:
    parsed = urlparse(url)
    host = parsed.netloc.replace("www.", "").replace(".", "-")
    tail = parsed.path.strip("/").replace("/", "-") or "index"
    return cache_dir / f"{host}-{tail}.md"


def credit_remaining() -> int | None:
    try:
        proc = subprocess.run(
            ["firecrawl", "credit-usage", "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        payload = json.loads(proc.stdout)
        return int(payload["data"]["remainingCredits"])
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def scrape_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "firecrawl",
            "scrape",
            url,
            "--wait-for",
            "4000",
            "--only-main-content",
            "-o",
            str(dest),
        ],
        check=True,
    )


def load_page_markdown(
    url: str, cache_dir: Path, fetch: bool
) -> tuple[str, Path, bool]:
    dest = cache_path_for(url, cache_dir)
    fetched = False
    if dest.exists():
        return dest.read_text(encoding="utf-8"), dest, False
    if not fetch:
        raise FileNotFoundError(f"no cached scrape for {url} at {dest}")
    scrape_url(url, dest)
    fetched = True
    return dest.read_text(encoding="utf-8"), dest, fetched


# ─── Main ─────────────────────────────────────────────────────────


def _row_sources(rows: list[PricingRow]) -> list[dict[str, str]]:
    seen: list[dict[str, str]] = []
    keys: set[tuple[str, str]] = set()
    for row in rows:
        pair = (row.source_url, row.name)
        if pair in keys:
            continue
        keys.add(pair)
        seen.append({"url": row.source_url, "name": row.name})
    return seen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--url",
        action="append",
        dest="urls",
        help="pricing page to scrape (repeatable). Default: Together + Fireworks.",
    )
    parser.add_argument(
        "--cache-dir",
        default=".firecrawl",
        help="directory for scraped markdown (default: .firecrawl)",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="only read cached scrapes; never call firecrawl",
    )
    parser.add_argument(
        "--report",
        default="benchmarks/_census/pricing_fetch.json",
    )
    args = parser.parse_args()

    urls = tuple(args.urls) if args.urls else DEFAULT_URLS
    cache_dir = (PROJECT_ROOT / args.cache_dir).resolve()
    fetched_at = datetime.now(UTC).date().isoformat()
    credits_before = credit_remaining()

    pages_report: list[dict[str, Any]] = []
    all_rows: list[PricingRow] = []
    page_errors: list[dict[str, str]] = []
    for url in urls:
        try:
            markdown, path, fetched = load_page_markdown(
                url, cache_dir, fetch=not args.no_fetch
            )
        except Exception as exc:
            page_errors.append({"url": url, "error": str(exc)})
            print(f"  FAIL {url}: {exc}")
            continue
        rows = extract_pricing_rows(markdown, url)
        all_rows.extend(rows)
        pages_report.append(
            {
                "url": url,
                "path": str(path.relative_to(PROJECT_ROOT)),
                "fetched": fetched,
                "rows": len(rows),
            }
        )
        print(f"  {url}  rows={len(rows)}  fetched={fetched}")

    credits_after = credit_remaining()
    credits_used: int | None = None
    if credits_before is not None and credits_after is not None:
        credits_used = credits_before - credits_after

    cards = load_cards()
    index, ambiguous_index = build_card_indexes(cards)

    matched_rows: dict[str, list[PricingRow]] = defaultdict(list)
    unmatched: list[dict[str, Any]] = []
    refused: list[dict[str, Any]] = []
    for row in all_rows:
        card, reason = match_row(row, index)
        payload = {
            "name": row.name,
            "source_url": row.source_url,
            "keys": list(match_keys(row)),
            "input": row.input_per_million,
            "output": row.output_per_million,
            "context_window": row.context_window,
        }
        if reason:
            refused.append({**payload, "reason": reason})
            continue
        if card is None:
            unmatched.append(payload)
            continue
        matched_rows[card.model_id].append(row)

    by_id = {card.model_id: card for card in cards}
    would_write: list[dict[str, Any]] = []
    already_report: list[dict[str, Any]] = []
    conflict_report: list[dict[str, Any]] = []
    written = 0

    for model_id, rows in sorted(matched_rows.items()):
        card = by_id[model_id]
        fetched, source_conflicts = merge_row_values(rows)
        if source_conflicts:
            conflict_report.append(
                {
                    "model_id": model_id,
                    "kind": "source_disagreement",
                    "conflicts": source_conflicts,
                    "sources": _row_sources(rows),
                    "fetched_at": fetched_at,
                }
            )
        gained, existing_conflicts, already = apply_values(card.existing, fetched)
        if existing_conflicts:
            conflict_report.append(
                {
                    "model_id": model_id,
                    "kind": "existing_value",
                    "conflicts": existing_conflicts,
                    "sources": _row_sources(rows),
                    "fetched_at": fetched_at,
                }
            )
        if already:
            already_report.append(
                {
                    "model_id": model_id,
                    "fields": already,
                    "sources": _row_sources(rows),
                    "fetched_at": fetched_at,
                }
            )
        if gained:
            entry = {
                "model_id": model_id,
                "gained": gained,
                "sources": _row_sources(rows),
                "fetched_at": fetched_at,
            }
            would_write.append(entry)
            if not args.dry_run:
                write_fields(card.path, gained)
                written += 1

    extracted_priced = sum(1 for row in all_rows if row.values())
    matched_n = len(matched_rows)
    match_rate = (matched_n / extracted_priced) if extracted_priced else 0.0

    report = {
        "dry_run": args.dry_run,
        "fetched_at": fetched_at,
        "credits_before": credits_before,
        "credits_after": credits_after,
        "credits_used": credits_used,
        "pages": pages_report,
        "page_errors": page_errors,
        "extracted_rows": len(all_rows),
        "extracted_with_values": extracted_priced,
        "matched_cards": matched_n,
        "match_rate": round(match_rate, 4),
        "unmatched_count": len(unmatched),
        "refused_count": len(refused),
        "would_write_count": len(would_write),
        "written": written,
        "already_count": len(already_report),
        "conflict_count": len(conflict_report),
        "ambiguous_index_slugs": ambiguous_index,
        "unmatched": unmatched,
        "refused": refused,
        "would_write": would_write,
        "already": already_report,
        "conflicts": conflict_report,
        "benchmarks_untouched": True,
    }
    out = PROJECT_ROOT / args.report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")

    print(
        f"\nextracted {len(all_rows)}  matched {matched_n}  "
        f"match_rate {match_rate:.1%}  refused {len(refused)}  "
        f"unmatched {len(unmatched)}"
    )
    print(
        f"would_write {len(would_write)}  already {len(already_report)}  "
        f"conflicts {len(conflict_report)}"
        + ("" if args.dry_run else f"  written={written}")
    )
    if credits_used is not None:
        print(f"credits used this run: {credits_used}")
    print(f"report: {out.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
