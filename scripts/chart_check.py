#!/usr/bin/env python3
"""Rebuild published release charts from the evidence rows on the cards.

Fixtures live in ``benchmarks/_charts/<page>.yaml``. ``check`` classifies every
bar and writes JSON, Markdown, and one SVG per chart. ``reconcile`` compares
that reading with a second reader's YAML. Neither command edits cards.

Same-source evidence is compared first, whatever the bar's role. A second
configuration of the same model and benchmark is ``other_configuration`` when
one sibling matches. A different unit is ``unit_differs``. A non-headline
metric is ``other_metric``. A bar with no catalogue page is
``no_benchmark_page``.

``official_reports`` is the publisher quoting a rival's own number. That bar
is compared only with the rival card's ``provider_self_report`` rows for the
benchmark. A row from another source is context on a ``not_held`` bar.
``vendor_run`` stays a gap. ``unstated`` stays unresolved.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, NamedTuple

import yaml

from pipeline.load import Model, load_models
from schema.card import BenchmarkEvidence

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "benchmarks" / "_charts"
DEFAULT_OUT = Path("/Users/terbeest/dev/worktrees/.chart-check/out")
DEFAULT_MANIFEST = Path("/Users/terbeest/dev/worktrees/.chart-cache/manifest-phase1.tsv")

#: Phase 1 families. Coverage is reported for these even when a page has no
#: subject bar for them.
PHASE1_MODELS = (
    "openai/gpt-6-astra",
    "openai/gpt-6-sol",
    "openai/gpt-5-4",
    "openai/o3",
    "openai/o3-mini",
    "openai/o4-mini",
    "openai/gpt-4-1",
    "openai/gpt-4-1-mini",
    "google/gemini-3-8-flash",
    "google/gemini-2-5-pro",
    "google/gemini-2-5-flash",
    "deepseek/deepseek-flash",
    "deepseek/deepseek-v3-2",
    "deepseek/deepseek-v3-2-exp",
    "qwen/qwen3-235b-a22b",
)

COMPETITOR_NUMBERS = {"official_reports", "vendor_run", "unstated"}
ROLES = {"subject", "competitor", "evaluated"}
KINDS = {"image", "html_table", "text"}
HEADLINE_METRICS = {"", "score", "headline"}
HELD_STATUSES = {"matched", "mismatched", "other_configuration"}
CLASS_ORDER = (
    "matched",
    "other_configuration",
    "mismatched",
    "unit_differs",
    "other_metric",
    "no_benchmark_page",
    "not_held",
    "competitor_gap",
    "competitor_unresolved",
    "low_confidence",
    "disputed",
)

# Fields this check reads. They are the evidence contract, not a second parser.
READ_FIELDS = ("benchmark_id", "score", "unit", "source_url", "configuration")

_SCORE_LINE = re.compile(r"(?m)^[ \t]+score:[ \t]*([-+]?[0-9][0-9_]*(?:\.[0-9]+)?)\s*$")
_UNIT_ALIASES = {
    "%": "percent",
    "pct": "percent",
    "percentage": "percent",
    "percent": "percent",
    "elo": "elo",
    "index": "index",
    "score": "score",
    "rating": "rating",
    "minutes": "minutes",
    "normalized elo percent": "normalized elo percent",
    "normalised elo percent": "normalized elo percent",
}


def norm_url(url: str) -> str:
    """One trailing slash is not a different source."""
    text = url.strip()
    if text.endswith("/"):
        text = text[:-1]
    return text


def norm_unit(unit: Any) -> str:
    """Spelling variants of one unit. Elo and normalized Elo stay distinct."""
    text = str(unit or "").strip().casefold().replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return _UNIT_ALIASES.get(text, text)


def norm_label(value: Any) -> str:
    text = str(value or "").casefold().replace("–", "-").replace("—", "-").replace("_", " ")
    text = re.sub(r"[^a-z0-9.+]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def norm_page(url: str) -> str:
    """Hugging Face blob and raw README URLs are the same card."""
    text = norm_url(url)
    return re.sub(
        r"^(https://huggingface\.co/[^/]+/[^/]+)(?:/(?:blob|raw|resolve)/[^/]+/README\.md)$",
        r"\1",
        text,
    )


class ParsedScore(NamedTuple):
    kind: str
    value: float | None
    text: str
    tolerance: float | None


_BLANK_SCORES = {"", "-", "—", "–", "−"}
_SCORE_VALUE = re.compile(
    r"""
    ^\s*
    (?P<cur>[$£€])?
    \s*
    (?P<sign>[+-])?
    \s*
    (?P<number>(?:\d{1,3}(?:,\d{3})+|\d+))
    (?P<frac>\.\d+)?
    \s*
    (?P<suf>[kKmM])?
    \s*
    (?P<pct>(?:%|pp))?
    \s*
    (?P<note>(?:[*†‡§¶#※]+|\[[0-9]{1,3}\]|[¹²³⁴⁵⁶⁷⁸⁹⁰]+))?
    \s*$
    """,
    re.VERBOSE,
)
_SUFFIX_SCALE = {"k": 1_000.0, "m": 1_000_000.0}


def _infer_score_text(score: Any) -> str:
    if isinstance(score, str):
        return score.strip()
    if score is None:
        return ""
    if isinstance(score, bool):
        return str(score)
    if isinstance(score, int):
        return str(score)
    try:
        text = format(float(score), "f").rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return str(score).strip()
    return text if text else "0"


def _tolerance_from_mantissa(mantissa: str, scale: float) -> float:
    text = mantissa.strip()
    if "." not in text:
        step = 0.5
    else:
        places = len(text.split(".", 1)[1])
        step = 0.5 if places == 0 else 0.5 * (10 ** (-places))
    return step * scale


def parse_score(score: Any) -> ParsedScore:
    """Read a second-reader value. Odd text is unparsed and never raises."""
    if isinstance(score, bool):
        return ParsedScore("unparsed", None, str(score), None)
    if score is None:
        return ParsedScore("blank", None, "", None)
    if isinstance(score, (int, float)):
        text = _infer_score_text(score)
        return ParsedScore("number", float(score), text, _tolerance_from_mantissa(text, 1.0))
    text = str(score).strip()
    if text.casefold() in _BLANK_SCORES or text in _BLANK_SCORES:
        return ParsedScore("blank", None, text, None)
    match = _SCORE_VALUE.match(text)
    if match is None:
        return ParsedScore("unparsed", None, text, None)
    number = match.group("number").replace(",", "")
    frac = match.group("frac") or ""
    mantissa = f"{match.group('sign') or ''}{number}{frac}"
    scale = _SUFFIX_SCALE.get((match.group("suf") or "").casefold(), 1.0)
    try:
        value = float(mantissa) * scale
    except ValueError:
        return ParsedScore("unparsed", None, text, None)
    return ParsedScore("number", value, text, _tolerance_from_mantissa(mantissa, scale))


def tolerance_for(score_text: str) -> float:
    """Half the printed precision. ``78.2`` is ±0.05; ``78`` is ±0.5."""
    parsed = parse_score(score_text)
    if parsed.tolerance is not None:
        return parsed.tolerance
    return 0.5


def _metric_key(bar: dict[str, Any]) -> str:
    raw = bar.get("metric")
    if raw is None:
        return ""
    text = str(raw).strip().casefold()
    if text in HEADLINE_METRICS:
        return ""
    return text


def attach_score_text(data: dict[str, Any], source: str) -> None:
    """Remember the printed digits. YAML floats do not keep them."""
    raw = _SCORE_LINE.findall(source)
    bars = [bar for chart in data.get("charts") or [] for bar in chart.get("bars") or []]
    if len(raw) != len(bars):
        raise ValueError(
            f"score lines ({len(raw)}) do not match bars ({len(bars)}); "
            "each score must be on its own line"
        )
    for bar, text in zip(bars, raw, strict=True):
        bar["score_text"] = text


def load_fixture(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    data = yaml.safe_load(source)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: fixture is not a mapping")
    attach_score_text(data, source)
    data["_path"] = str(path)
    data["_slug"] = path.stem
    return data


def load_fixtures(directory: Path | None = None) -> list[dict[str, Any]]:
    root = directory or FIXTURE_DIR
    if not root.is_dir():
        return []
    return [load_fixture(path) for path in sorted(root.glob("*.yaml"))]


def _evidence(model: Model) -> list[dict[str, Any]]:
    block = model.front.get("benchmarks") or {}
    if not isinstance(block, dict):
        return []
    raw = block.get("evidence") or []
    if not isinstance(raw, list):
        return []
    out = []
    for row in raw:
        if isinstance(row, dict) and row.get("benchmark_id"):
            out.append(row)
    return out


def _within(chart_score: float, held: float, tolerance: float) -> bool:
    return abs(float(chart_score) - float(held)) <= tolerance + 1e-9


def _closest(chart_score: float, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return min(rows, key=lambda row: abs(float(row["score"]) - float(chart_score)))


def _same_unit(rows: list[dict[str, Any]], unit: Any) -> list[dict[str, Any]]:
    wanted = norm_unit(unit)
    return [row for row in rows if norm_unit(row.get("unit")) == wanted]


def _row_brief(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "score": row.get("score"),
        "unit": row.get("unit") or "",
        "source_url": row.get("source_url") or "",
        "configuration": row.get("configuration") or "",
    }


def _context_row(row: dict[str, Any]) -> dict[str, Any]:
    brief = _row_brief(row)
    brief["source_kind"] = row.get("source_kind") or ""
    return brief


def _hit(bar: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    tolerance = tolerance_for(str(bar.get("score_text") or _infer_score_text(bar["score"])))
    return next((row for row in rows if _within(float(bar["score"]), row["score"], tolerance)), None)


def _reading_disputes(chart: dict[str, Any]) -> set[tuple[str, str]]:
    """Bar keys whose per-reading scores disagree. One shared bar list cannot."""
    per_reader: list[dict[tuple[str, str], float]] = []
    for reading in chart.get("readings") or []:
        if not isinstance(reading, dict) or "bars" not in reading:
            continue
        found: dict[tuple[str, str], float] = {}
        for bar in reading.get("bars") or []:
            parsed = parse_score(bar.get("score"))
            if parsed.kind != "number" or parsed.value is None:
                continue
            key = (str(bar.get("model_as_labelled") or ""), str(bar.get("benchmark_id") or ""))
            found[key] = parsed.value
        per_reader.append(found)
    if len(per_reader) < 2:
        return set()
    keys = set.intersection(*(set(item) for item in per_reader))
    disputed = set()
    for key in keys:
        values = [item[key] for item in per_reader]
        if max(values) - min(values) > 1e-9:
            disputed.add(key)
    return disputed


def _explicit_dispute(bar: dict[str, Any]) -> bool:
    block = bar.get("disputed")
    if not isinstance(block, list) or len(block) < 2:
        return False
    values = []
    for item in block:
        if not isinstance(item, dict) or item.get("value") is None:
            continue
        parsed = parse_score(item.get("value"))
        if parsed.kind == "number" and parsed.value is not None:
            values.append(parsed.value)
    return len(values) >= 2 and max(values) - min(values) > 1e-9


def _base_result(bar: dict[str, Any]) -> dict[str, Any]:
    score_text = str(bar.get("score_text") or _infer_score_text(bar["score"]))
    benchmark_id = bar.get("benchmark_id") or None
    return {
        "model_as_labelled": bar.get("model_as_labelled") or "",
        "model_id": bar.get("model_id") or None,
        "benchmark_id": benchmark_id,
        "benchmark_as_labelled": bar.get("benchmark_as_labelled") or "",
        "role": bar.get("role") or "",
        "chart_score": float(bar["score"]),
        "score_text": score_text,
        "unit": bar.get("unit") or "",
        "metric": bar.get("metric") or "",
        "printed": bool(bar.get("printed")),
        "configuration": bar.get("configuration") or "",
        "tolerance": tolerance_for(score_text),
        "status": "",
        "held": None,
        "held_rows": [],
        "context": None,
        "same_source": False,
        "known_mismatch": bar.get("known_mismatch"),
        "disputed_values": bar.get("disputed") if _explicit_dispute(bar) else None,
    }


def _finish_match(result: dict[str, Any], row: dict[str, Any], status: str, same_source: bool) -> dict[str, Any]:
    result["status"] = status
    result["held"] = _row_brief(row)
    result["held_rows"] = [_row_brief(row)]
    result["same_source"] = same_source
    return result


def _finish_unit(result: dict[str, Any], rows: list[dict[str, Any]], same_source: bool) -> dict[str, Any]:
    result["status"] = "unit_differs"
    result["same_source"] = same_source
    result["held_rows"] = [_row_brief(row) for row in rows]
    result["held"] = result["held_rows"][0] if result["held_rows"] else None
    return result


def _lookup(
    bar: dict[str, Any], page: str, models_by_id: dict[str, Model]
) -> tuple[Model | None, list[dict[str, Any]], list[dict[str, Any]]]:
    model_id = bar.get("model_id") or None
    model = models_by_id.get(model_id) if model_id else None
    rows = _evidence(model) if model is not None else []
    benchmark_id = str(bar.get("benchmark_id") or "")
    same_benchmark = [row for row in rows if str(row.get("benchmark_id")) == benchmark_id]
    same_source = [
        row for row in same_benchmark if norm_url(str(row.get("source_url") or "")) == page
    ]
    return model, same_benchmark, same_source


def _fidelity_one(result: dict[str, Any], bar: dict[str, Any], same_rows: list[dict[str, Any]]) -> dict[str, Any]:
    same_unit = _same_unit(same_rows, bar.get("unit"))
    if not same_unit:
        return _finish_unit(result, same_rows, True)
    hit = _hit(bar, same_unit)
    if hit is not None:
        return _finish_match(result, hit, "matched", True)
    return _finish_match(result, _closest(float(bar["score"]), same_unit), "mismatched", True)


def _fidelity_siblings(
    idxs: list[int],
    bars: list[dict[str, Any]],
    results: list[dict[str, Any]],
    same_rows: list[dict[str, Any]],
) -> None:
    comparable: list[tuple[int, list[dict[str, Any]]]] = []
    for index in idxs:
        same_unit = _same_unit(same_rows, bars[index].get("unit"))
        if not same_unit:
            _finish_unit(results[index], same_rows, True)
        else:
            comparable.append((index, same_unit))
    if len(comparable) < 2:
        for index, rows in comparable:
            _fidelity_one(results[index], bars[index], rows)
        return
    matched: list[tuple[int, dict[str, Any]]] = []
    for index, rows in comparable:
        hit = _hit(bars[index], rows)
        if hit is not None:
            matched.append((index, hit))
    if not matched:
        for index, rows in comparable:
            _finish_match(
                results[index],
                _closest(float(bars[index]["score"]), rows),
                "mismatched",
                True,
            )
        return
    matched_at = {index: row for index, row in matched}
    exemplar = matched[0][1]
    for index, _rows in comparable:
        if index in matched_at:
            _finish_match(results[index], matched_at[index], "matched", True)
        else:
            _finish_match(results[index], exemplar, "other_configuration", True)


def _role_path(
    result: dict[str, Any],
    bar: dict[str, Any],
    rows: list[dict[str, Any]],
    competitor_numbers: str,
) -> dict[str, Any]:
    role = bar.get("role")
    if role == "subject" or not rows:
        result["status"] = "not_held"
        if rows:
            preferred = _same_unit(rows, bar.get("unit")) or rows
            result["context"] = _row_brief(_closest(float(bar["score"]), preferred))
        return result
    same_unit = _same_unit(rows, bar.get("unit"))
    if competitor_numbers == "official_reports":
        # Another evaluator's number is a different measurement. Only the
        # rival's own published row can show that this chart misquotes it.
        self_rows = [row for row in rows if row.get("source_kind") == "provider_self_report"]
        if not self_rows:
            result["status"] = "not_held"
            result["context"] = [_context_row(row) for row in rows]
            return result
        self_unit = _same_unit(self_rows, bar.get("unit"))
        if not self_unit:
            return _finish_unit(result, self_rows, False)
        hit = _hit(bar, self_unit)
        if hit is not None:
            return _finish_match(result, hit, "matched", False)
        return _finish_match(result, _closest(float(bar["score"]), self_unit), "mismatched", False)
    if competitor_numbers == "vendor_run":
        if not same_unit:
            return _finish_unit(result, rows, False)
        closest = _closest(float(bar["score"]), same_unit)
        result["status"] = "competitor_gap"
        result["held"] = _row_brief(closest)
        result["held_rows"] = [_row_brief(row) for row in same_unit]
        result["gap"] = float(bar["score"]) - float(closest["score"])
        return result
    result["status"] = "competitor_unresolved"
    result["held"] = _row_brief(_closest(float(bar["score"]), rows))
    result["held_rows"] = [_row_brief(row) for row in rows]
    return result


def _classify_chart(
    chart: dict[str, Any], page_url: str, models_by_id: dict[str, Model]
) -> list[dict[str, Any]]:
    disputed_keys = _reading_disputes(chart)
    page = norm_url(page_url)
    bars = list(chart.get("bars") or [])
    results: list[dict[str, Any] | None] = [None] * len(bars)
    pending: list[int] = []
    looked: dict[int, tuple[Any, list[dict[str, Any]], list[dict[str, Any]]]] = {}
    for index, bar in enumerate(bars):
        result = _base_result(bar)
        label_key = (str(bar.get("model_as_labelled") or ""), str(bar.get("benchmark_id") or ""))
        if _explicit_dispute(bar) or label_key in disputed_keys:
            result["status"] = "disputed"
            results[index] = result
            continue
        if not bar.get("printed"):
            result["status"] = "low_confidence"
            results[index] = result
            continue
        if not bar.get("benchmark_id"):
            result["status"] = "no_benchmark_page"
            results[index] = result
            continue
        if _metric_key(bar):
            result["status"] = "other_metric"
            results[index] = result
            continue
        results[index] = result
        looked[index] = _lookup(bar, page, models_by_id)
        pending.append(index)

    buckets: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for index in pending:
        _model, _rows, same = looked[index]
        bar = bars[index]
        model_id = bar.get("model_id") or ""
        if same and model_id:
            buckets[(str(model_id), str(bar.get("benchmark_id")), _metric_key(bar))].append(index)
            continue
        if same:
            _fidelity_one(results[index], bar, same)
        else:
            _role_path(results[index], bar, looked[index][1], str(chart.get("competitor_numbers") or ""))
    for idxs in buckets.values():
        same_rows = looked[idxs[0]][2]
        if len(idxs) >= 2:
            _fidelity_siblings(idxs, bars, results, same_rows)
        else:
            _fidelity_one(results[idxs[0]], bars[idxs[0]], same_rows)
    return [item for item in results if item is not None]


def classify_fixtures(fixtures: list[dict[str, Any]], models: list[Model]) -> dict[str, Any]:
    models_by_id = {model.model_id: model for model in models}
    charts_out = []
    counts: dict[str, int] = {}
    needs_reading = 0
    read = 0
    for fixture in fixtures:
        page_url = str(fixture["page_url"])
        for index, chart in enumerate(fixture.get("charts") or []):
            if chart.get("needs_reading"):
                needs_reading += 1
            else:
                read += 1
            flags = []
            if len(chart.get("readings") or []) < 2:
                flags.append("single_read")
            bars = _classify_chart(chart, page_url, models_by_id)
            for classified in bars:
                counts[classified["status"]] = counts.get(classified["status"], 0) + 1
            charts_out.append(
                {
                    "slug": fixture.get("_slug") or "",
                    "path": fixture.get("_path") or "",
                    "page_url": page_url,
                    "publisher": fixture.get("publisher") or "",
                    "title": chart.get("title") or "",
                    "index": index,
                    "kind": chart.get("kind") or "image",
                    "needs_reading": bool(chart.get("needs_reading")),
                    "flags": flags,
                    "competitor_numbers": chart.get("competitor_numbers"),
                    "image_sha256": chart.get("image_sha256") or "",
                    "bars": bars,
                }
            )
    return {
        "pages": len(fixtures),
        "charts": len(charts_out),
        "charts_read": read,
        "charts_needs_reading": needs_reading,
        "bars": sum(counts.values()),
        "by_class": counts,
        "charts_detail": charts_out,
        "coverage": _coverage(charts_out),
        "uncatalogued": _uncatalogued(charts_out),
    }


def _coverage(charts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Headline subject bars held from this page, over those with a catalogue id."""
    bucket: dict[str, dict[str, int]] = {
        model_id: {"published": 0, "held": 0, "matched": 0} for model_id in PHASE1_MODELS
    }
    for chart in charts:
        for bar in chart["bars"]:
            if bar["role"] != "subject" or not bar["model_id"] or not bar["benchmark_id"]:
                continue
            if bar["status"] in {"no_benchmark_page", "other_metric"}:
                continue
            slot = bucket.setdefault(bar["model_id"], {"published": 0, "held": 0, "matched": 0})
            slot["published"] += 1
            held = bar["status"] in HELD_STATUSES or (
                bar["status"] == "unit_differs" and bar.get("same_source")
            )
            if held:
                slot["held"] += 1
            if bar["status"] == "matched":
                slot["matched"] += 1
    rows = []
    for model_id, slot in bucket.items():
        published = slot["published"]
        rows.append(
            {
                "model_id": model_id,
                "published": published,
                "held": slot["held"],
                "matched": slot["matched"],
                "coverage": (slot["held"] / published) if published else None,
            }
        )
    return rows


def _uncatalogued(charts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for chart in charts:
        for bar in chart["bars"]:
            if bar["status"] != "no_benchmark_page":
                continue
            label = bar.get("benchmark_as_labelled") or "(no label)"
            counts[label] += 1
    return [{"benchmark_as_labelled": label, "bars": count} for label, count in sorted(counts.items())]


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        text = format(round(value, 10), "f").rstrip("0").rstrip(".")
        return text or "0"
    return str(value)


def _class_lines(counts: dict[str, int]) -> list[str]:
    lines = []
    seen = set()
    for status in CLASS_ORDER:
        if status in counts:
            lines.append(f"- {status}: {counts[status]}")
            seen.add(status)
    for status, count in sorted(counts.items()):
        if status not in seen:
            lines.append(f"- {status}: {count}")
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Chart check",
        "",
        f"Pages: {report['pages']}. Charts: {report['charts']}. "
        f"Read: {report['charts_read']}. Left needs_reading: {report['charts_needs_reading']}.",
        f"Bars: {report['bars']}.",
        "",
        "## Bars by class",
        "",
        *_class_lines(report["by_class"]),
        "",
        "## Coverage",
        "",
        "Headline subject bars with a catalogue id. Held means a same-source row exists.",
        "",
        "| Model | Published | Held | Matched | Held / published |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in report["coverage"]:
        ratio = "—" if row["coverage"] is None else f"{row['coverage']:.2f}"
        lines.append(
            f"| {row['model_id']} | {row['published']} | {row['held']} | "
            f"{row['matched']} | {ratio} |"
        )
    lines.extend(["", "## Mismatched", ""])
    mismatches = [
        (chart, bar)
        for chart in report["charts_detail"]
        for bar in chart["bars"]
        if bar["status"] == "mismatched"
    ]
    if not mismatches:
        lines.append("None.")
    for chart, bar in mismatches:
        held = bar["held"] or {}
        lines.append(
            f"- {chart['title']}: {bar['model_as_labelled']} / {bar['benchmark_id']} "
            f"chart {_fmt(bar['chart_score'])} {bar['unit']} on {chart['page_url']}, "
            f"held {_fmt(held.get('score'))} {held.get('unit') or ''} "
            f"({held.get('configuration') or 'no configuration'}) "
            f"from {held.get('source_url') or ''}"
        )
    lines.extend(["", "## Competitor gaps above 2 points", ""])
    gaps = []
    for chart in report["charts_detail"]:
        for bar in chart["bars"]:
            if bar["status"] != "competitor_gap":
                continue
            gap = bar.get("gap")
            if gap is None or abs(float(gap)) <= 2:
                continue
            gaps.append((abs(float(gap)), chart, bar))
    gaps.sort(key=lambda item: item[0], reverse=True)
    if not gaps:
        lines.append("None.")
    for _, chart, bar in gaps:
        lines.append(
            f"- {chart['title']}: {bar['model_as_labelled']} / {bar['benchmark_id']} "
            f"chart {_fmt(bar['chart_score'])} {bar['unit']} on {chart['page_url']} "
            f"({bar['configuration'] or 'unspecified'}). Gap {_fmt(bar.get('gap'))} "
            "versus the closest same-unit row."
        )
        for held in bar.get("held_rows") or []:
            lines.append(
                f"  - held {_fmt(held.get('score'))} {held.get('unit') or ''} "
                f"({held.get('configuration') or 'unspecified'}) from {held.get('source_url') or ''}"
            )
    lines.extend(["", "## Unit differs", ""])
    grouped: dict[tuple[str, str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for chart in report["charts_detail"]:
        for bar in chart["bars"]:
            if bar["status"] != "unit_differs":
                continue
            held = bar.get("held") or {}
            key = (
                str(bar.get("benchmark_id") or bar.get("benchmark_as_labelled") or ""),
                norm_unit(bar.get("unit")),
                norm_unit(held.get("unit")),
            )
            grouped[key].append((chart, bar))
    if not grouped:
        lines.append("None.")
    for key, items in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        chart, bar = items[0]
        held = bar.get("held") or {}
        lines.append(
            f"- {key[0]}: {len(items)} bars in {bar['unit']}, "
            f"held unit {held.get('unit') or ''}. "
            f"Example: {bar['model_as_labelled']} chart {_fmt(bar['chart_score'])} {bar['unit']}, "
            f"held {_fmt(held.get('score'))} {held.get('unit') or ''} "
            f"from {held.get('source_url') or chart['page_url']}."
        )
    lines.extend(["", "## Uncatalogued benchmarks", ""])
    if not report.get("uncatalogued"):
        lines.append("None.")
    for row in report.get("uncatalogued") or []:
        lines.append(f"- {row['benchmark_as_labelled']}: {row['bars']}")
    single = [chart["title"] for chart in report["charts_detail"] if "single_read" in chart["flags"]]
    lines.extend(["", "## Single read", ""])
    lines.append(f"{len(single)} charts have one reading. That is not a failure.")
    lines.append("")
    return "\n".join(lines) + "\n"


def _svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _svg_text(x: int, y: int, size: int, text: str, fill: str = "#222") -> str:
    body = _svg_escape(text)
    return (
        f'<text x="{x}" y="{y}" font-family="ui-sans-serif, sans-serif" '
        f'font-size="{size}" fill="{fill}">{body}</text>'
    )


def render_svg(chart: dict[str, Any]) -> str:
    bars = chart["bars"]
    row_h = 22
    label_w = 420
    plot_w = 360
    width = label_w + plot_w + 160
    height = 48 + max(1, len(bars)) * row_h + 28
    values = [abs(float(bar["chart_score"])) for bar in bars]
    for bar in bars:
        held = bar.get("held") or {}
        if held.get("score") is not None and norm_unit(held.get("unit")) == norm_unit(bar.get("unit")):
            values.append(abs(float(held["score"])))
    peak = max(values) if values else 1
    if peak <= 0:
        peak = 1
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        '<rect width="100%" height="100%" fill="#fbfbfb"/>',
        _svg_text(16, 24, 14, chart["title"]),
    ]
    if not bars:
        parts.append(_svg_text(16, 52, 12, "No bars transcribed.", "#555"))
    for i, bar in enumerate(bars):
        y = 40 + i * row_h
        bench = bar.get("benchmark_id") or bar.get("benchmark_as_labelled") or ""
        label = f"{bar['model_as_labelled']} · {bench}"
        parts.append(_svg_text(16, y + 14, 11, label[:70]))
        chart_w = plot_w * (abs(float(bar["chart_score"])) / peak) if peak else 0
        if not math.isfinite(chart_w) or chart_w < 0:
            chart_w = 0
        parts.append(
            f'<rect x="{label_w}" y="{y + 4}" width="{chart_w:.1f}" height="6" fill="#1f4b99"/>'
        )
        held_score = None if not bar.get("held") else bar["held"].get("score")
        same_scale = bar.get("held") and norm_unit(bar["held"].get("unit")) == norm_unit(bar.get("unit"))
        if held_score is not None and same_scale:
            held_w = plot_w * (abs(float(held_score)) / peak)
            if held_w < 0:
                held_w = 0
            parts.append(
                f'<rect x="{label_w}" y="{y + 12}" width="{held_w:.1f}" height="6" fill="#c45500"/>'
            )
        note = f"{_fmt(bar['chart_score'])} / {_fmt(held_score if same_scale else None)} {bar['status']}"
        parts.append(_svg_text(label_w + plot_w + 8, y + 14, 11, note, "#333"))
    parts.append(_svg_text(16, height - 10, 10, "Blue: chart. Orange: evidence we hold, same unit.", "#666"))
    parts.append("</svg>")
    return "\n".join(parts)


def write_report(report: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out / "report.md").write_text(render_markdown(report), encoding="utf-8")
    svg_dir = out / "svg"
    svg_dir.mkdir(exist_ok=True)
    for chart in report["charts_detail"]:
        name = f"{chart['slug']}-{chart['index']:02d}.svg"
        (svg_dir / name).write_text(render_svg(chart), encoding="utf-8")


def fixture_errors(fixtures: list[dict[str, Any]], models: list[Model]) -> list[str]:
    """Structural problems. Mismatches are a separate gate."""
    errors = []
    model_ids = {model.model_id for model in models}
    from pipeline.load import load_benchmarks

    page_ids = {bench.benchmark_id for bench in load_benchmarks()}
    score_keys: set[str] = set()
    for model in models:
        block = model.front.get("benchmarks") or {}
        if isinstance(block, dict) and isinstance(block.get("scores"), dict):
            score_keys.update(str(key) for key in block["scores"])
        for row in _evidence(model):
            score_keys.add(str(row["benchmark_id"]))
    missing = [name for name in READ_FIELDS if name not in BenchmarkEvidence.model_fields]
    if missing:
        errors.append(f"BenchmarkEvidence lost fields: {missing}")
    for fixture in fixtures:
        name = fixture.get("_slug") or "?"
        for field in ("page_url", "publisher", "read_on", "charts"):
            if field not in fixture:
                errors.append(f"{name}: missing {field}")
        for chart in fixture.get("charts") or []:
            title = chart.get("title") or "(untitled)"
            where = f"{name} / {title}"
            if chart.get("competitor_numbers") not in COMPETITOR_NUMBERS:
                allowed = ", ".join(sorted(COMPETITOR_NUMBERS))
                errors.append(f"{where}: competitor_numbers must be one of {allowed}")
            if not chart.get("readings"):
                errors.append(f"{where}: readings is empty")
            kind = chart.get("kind") or "image"
            if kind not in KINDS:
                errors.append(f"{where}: unknown kind {kind}")
            if kind == "image" and not chart.get("needs_reading"):
                if not chart.get("image_url") or not chart.get("image_sha256"):
                    errors.append(f"{where}: image chart needs image_url and image_sha256")
            digest = chart.get("image_sha256")
            if digest and not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
                errors.append(f"{where}: image_sha256 is not 64 hex digits")
            for bar in chart.get("bars") or []:
                if bar.get("role") not in ROLES:
                    errors.append(f"{where}: bar role {bar.get('role')!r}")
                model_id = bar.get("model_id")
                if model_id and model_id not in model_ids:
                    errors.append(f"{where}: unknown model_id {model_id}")
                benchmark_id = bar.get("benchmark_id") or ""
                labelled = str(bar.get("benchmark_as_labelled") or "").strip()
                if not benchmark_id:
                    if not labelled:
                        errors.append(f"{where}: bar needs benchmark_id or benchmark_as_labelled")
                elif benchmark_id not in page_ids and benchmark_id not in score_keys:
                    errors.append(
                        f"{where}: benchmark_id {benchmark_id} has no page and no score key"
                    )
                if "score" not in bar or isinstance(bar.get("score"), bool):
                    errors.append(f"{where}: bar missing score")
                if not isinstance(bar.get("printed"), bool):
                    errors.append(f"{where}: printed must be true or false")
    return errors


def mismatch_errors(report: dict[str, Any]) -> list[str]:
    errors = []
    for chart in report["charts_detail"]:
        for bar in chart["bars"]:
            marked = bool(bar.get("known_mismatch"))
            if bar["status"] == "mismatched" and not marked:
                errors.append(
                    f"{chart['title']}: {bar['model_as_labelled']} {bar['benchmark_id']} "
                    f"chart {bar['chart_score']} held {(bar.get('held') or {}).get('score')} "
                    "has no known_mismatch"
                )
            if marked and bar["status"] not in {"mismatched", "disputed"}:
                errors.append(
                    f"{chart['title']}: {bar['model_as_labelled']} {bar['benchmark_id']} "
                    f"is {bar['status']}, so known_mismatch is stale"
                )
    return errors


def load_manifest(path: Path) -> dict[str, str]:
    """Image file name to the 64-hex digest stored on the fixture."""
    found: dict[str, str] = {}
    if not path.is_file():
        return found
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        name, digest = parts[0].strip(), parts[1].strip().lower()
        hexdigest = digest.split(".", 1)[0]
        found[name] = hexdigest
    return found


def _metric_setting(bar: dict[str, Any]) -> str:
    metric = str(bar.get("metric") or "").strip()
    if metric:
        return metric
    return str(bar.get("configuration") or "").strip()


_DROP_VENDORS = {"openai", "google", "anthropic", "alibaba", "meta"}
_MODEL_ALIASES = {
    "opus 5": "claude opus 5",
    "sonnet 5": "claude sonnet 5",
    "k 3": "kimi k 3",
}
# Longer phrases first. A version marker "v" before a digit is already gone.
_BENCH_ALIASES = (
    ("humanity s last exam with tools", "hle tools"),
    ("humanity s last exam tools", "hle tools"),
    ("humanity s last exam", "hle"),
    ("artificial analysis intelligence index", "artificial analysis"),
    ("aa briefcase elo", "aa briefcase"),
    ("harvey s legal agent benchmark", "harvey legal"),
    ("harvey legal agent benchmark", "harvey legal"),
    ("gray swan ipi benchmark", "gray swan ipi"),
    ("simple qa verified", "simpleqa verified"),
    ("gdpval aa 2", "gdpval aa"),
    ("gdp pdf aa", "gdp pdf"),
    ("swe bench verified", "swe verified"),
    ("live code bench", "livecodebench"),
    ("humaneval plus", "evalplus"),
    ("browse comp zh", "browsecomp zh"),
    ("browse comp", "browsecomp"),
    ("long bench 2", "longbench 2"),
    ("code forces", "codeforces"),
    ("arena hard", "arenahard"),
    ("automation bench", "automationbench"),
    ("simple qa", "simpleqa"),
    ("hle w tools", "hle tools"),
    ("hle with tools", "hle tools"),
    ("osworld 2", "osworld"),
    ("aime 24", "aime 2024"),
    ("aime 25", "aime 2025"),
    ("crux o", "cruxeval"),
    ("aider polyglot", "aider"),
    ("deep swe", "deepswe"),
    ("c eval", "ceval"),
    ("nl 2 repo bench", "nl 2 repo"),
    ("zerobench main", "zerobench"),
    ("tone 1", "tone"),
)
_QUALIFIERS = (
    ("text only", "textonly"),
    ("with tools", "tools"),
    ("w tools", "tools"),
    ("without tools", "notools"),
    ("no tools", "notools"),
    ("human solvable", "humansolvable"),
    ("human difficult", "humandifficult"),
    ("static", "static"),
    ("notools", "notools"),
    ("tools", "tools"),
)
_FILLER_PHRASES = (
    "effort in the label",
    "bold in source",
    "lower is better",
    "temperature 1.0 top p 0.95",
    "max reasoning effort",
    "maximum at any effort",
    "base model internal framework",
    "pre trained base checkpoint",
    "official scaffold",
    "samples per task",
    "no network access",
    "deepseek harness minimal mode",
    "1 m context",
    "where the readme names another harness",
    "code agents use",
)
_GLOSS = {
    "a", "an", "the", "of", "for", "and", "in", "on", "to", "per", "by", "from", "at", "with",
    "mode", "section", "notes", "figure", "chart", "bar", "bars", "printed", "label", "labels",
    "effort", "rate", "score", "average", "avg", "reasoning", "higher", "better", "lower",
    "same", "settings", "under", "bold", "source", "read", "off", "task", "tasks",
    "index", "intelligence", "knowledge", "work", "engineering", "software", "horizon", "long",
    "legal", "complex", "workflows", "document", "expert", "comprehension", "attack", "success",
    "attempts", "within", "rating", "languages", "charts", "synthesis", "information",
    "research", "bioinformatics", "pdf", "caption", "ranking", "weights", "frontier", "pareto",
    "atomic", "criterion", "criteria", "every", "combined", "above", "below", "segment",
    "middle", "bottom", "legend", "shade", "suggests", "total", "lighter", "darker",
    "sample", "samples", "format", "function", "prompt", "baselines", "best", "fc", "call",
    "general", "multilingual", "mathematics", "science", "across", "internal", "benchmark",
    "partial", "enabled", "batch", "official", "scaffold", "harness", "temperature", "top",
    "context", "network", "access", "understanding", "video", "subset", "full", "n",
    "agentic", "coding", "analyst", "financial", "multidisciplinary", "biology", "real",
    "world", "capabilities", "computer", "use", "except", "readme", "names", "another",
    "where", "agents", "minimal", "passed", "stacked", "axis", "not",
    "prose", "open", "cost", "objectives", "completed", "objective", "met",
    "guardrail", "violation", "zeroes", "held", "out", "set", "share",
    "every", "no", "benchmark",
}
_SCAFFOLDS = {
    "claudecode", "codex", "dshminimal", "dshstandard", "dshptc", "miniswe", "opencode", "pi",
}
_EFFORT = {"max", "high", "xhigh", "low", "medium"}


def _basic_label(value: Any) -> str:
    text = str(value or "").casefold()
    text = text.replace("–", " ").replace("—", " ").replace("−", " ").replace("_", " ")
    text = text.replace("&", " and ").replace("@", " ").replace("/", " ")
    text = re.sub(r"\.(?!\d)", " ", text)
    text = re.sub(r"[^a-z0-9.+]+", " ", text)
    text = re.sub(r"v(?=\d)", " ", text)
    text = re.sub(r"([a-z])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([a-z])", r"\1 \2", text)
    text = re.sub(r"(\d{4})\.(\d{2})", r"\1 \2", text)
    text = re.sub(r"\b(\d+)\.0+\b", r"\1", text)
    text = text.replace("w o ", "without ")
    return re.sub(r"\s+", " ", text).strip()


def _join_version(text: str) -> str:
    text = re.sub(r"\b(\d{1,2}) (\d)\b", r"\1.\2", text)
    return re.sub(r"\b(\d+)\.0+\b", r"\1", text)


def _apply_aliases(text: str, aliases: tuple[tuple[str, str], ...]) -> str:
    padded = f" {text} "
    for src, dst in aliases:
        padded = padded.replace(f" {src} ", f" {dst} ")
    return re.sub(r"\s+", " ", padded).strip()


def _mark_settings(text: str) -> str:
    """One token for a setting, so 'no tools' and 'w/o tool use' compare equal."""
    text = text.replace("without tool use", "notools")
    text = text.replace("no tool use", "notools")
    text = text.replace("without tools", "notools")
    text = text.replace("no tools", "notools")
    text = text.replace("with tools", "tools")
    text = text.replace("w tools", "tools")
    text = text.replace("tool use", "tools")
    return re.sub(r"\s+", " ", text).strip()


def _pull_qualifiers(text: str) -> tuple[str, list[str]]:
    found: list[str] = []
    for phrase, name in _QUALIFIERS:
        needle = f" {phrase} "
        padded = f" {text} "
        if needle in padded:
            found.append(name)
            text = padded.replace(needle, " ")
            text = re.sub(r"\s+", " ", text).strip()
    return text, found


def canon_model(value: Any) -> str:
    text = _basic_label(value)
    if text.startswith("ds "):
        text = "deepseek " + text[3:]
    parts = text.split()
    while parts and parts[0] in _DROP_VENDORS and any(any(ch.isdigit() for ch in part) for part in parts[1:]):
        parts = parts[1:]
    text = " ".join(parts)
    text = re.sub(r" a \d+ b$", "", text)
    return _MODEL_ALIASES.get(text, text)


def canon_benchmark(value: Any) -> str:
    text = _join_version(_basic_label(value))
    return _apply_aliases(text, _BENCH_ALIASES)


def _prose_number(token: str) -> bool:
    """A version or a large count glued into a caption, not a shot or pass number."""
    if re.fullmatch(r"\d+\.\d+", token):
        return True
    return bool(token.isdigit() and int(token) > 100)


def canon_metric(value: Any, model: Any = "") -> str:
    text = _basic_label(value)
    text = text.replace("tasks completed", "taskscompleted")
    text = text.replace("exact match", "em")
    text = text.replace("llm judge", "llmjudge")
    text = text.replace("all pass", "allpass")
    text = text.replace("claude code", "claudecode")
    text = text.replace("mini swe", "miniswe")
    text = text.replace("dsh minimal", "dshminimal")
    text = text.replace("dsh standard", "dshstandard")
    text = text.replace("dsh ptc", "dshptc")
    text = text.replace("open code", "opencode")
    text = text.replace("not labelled diamond", "notdiamond")
    text = text.replace("non thinking", "nothink")
    text = text.replace("think mode off", "nothink")
    for phrase in _FILLER_PHRASES:
        text = f" {text} ".replace(f" {phrase} ", " ")
    text = re.sub(r"\s+", " ", text).strip()
    kept = []
    for tok in text.split():
        if tok in _GLOSS or tok in {"p", "0.95", "1.0"}:
            continue
        kept.append(tok)
    if "pass" in kept and "1" in kept:
        kept = [tok for tok in kept if tok not in {"pass", "1"}]
    if _SCAFFOLDS.intersection(kept):
        kept = [tok for tok in kept if tok not in _EFFORT and tok not in {"resolved", "pass"} and not tok.isdigit()]
    if kept == ["resolved"]:
        kept = ["miniswe"]
    kept = [tok for tok in kept if not _prose_number(tok)]
    model_tokens = set(_basic_label(model).split())
    kept = [tok for tok in kept if tok not in _EFFORT or tok not in model_tokens]
    return " ".join(sorted(set(kept)))


def _identity(model: Any, benchmark: Any, metric: Any) -> tuple[str, str, str]:
    bench = _mark_settings(canon_benchmark(benchmark))
    metric_text = _mark_settings(_basic_label(metric))
    if "verified" in metric_text.split() or bench.endswith(" verified") or " verified " in f" {bench} ":
        if bench == "hle" or bench.startswith("hle "):
            bench = "hle verified"
            metric_text = " ".join(tok for tok in metric_text.split() if tok not in {"verified", "hle"})
        elif bench == "simpleqa" or bench.startswith("simpleqa "):
            bench = "simpleqa verified"
            metric_text = " ".join(tok for tok in metric_text.split() if tok != "verified")
    bench, bench_quals = _pull_qualifiers(bench)
    metric_text, metric_quals = _pull_qualifiers(metric_text)
    quals = " ".join(sorted(set(bench_quals + metric_quals)))
    if quals:
        bench = f"{bench} {quals}".strip()
    return (canon_model(model), bench, canon_metric(metric_text, model))


def _pair_key(model: Any, benchmark: Any, metric: Any) -> tuple[str, str, str]:
    return _identity(model, benchmark, metric)


def _scores_agree(
    a_score: float,
    a_text: str,
    a_printed: bool,
    b_score: float,
    b_text: str,
    b_printed: bool,
    uncertainty: float | None,
) -> bool:
    if a_printed and b_printed:
        tolerance = max(tolerance_for(a_text), tolerance_for(b_text))
    elif uncertainty is not None:
        tolerance = float(uncertainty)
    elif a_printed or b_printed:
        tolerance = tolerance_for(a_text if a_printed else b_text)
    else:
        tolerance = 0.0
    return abs(float(a_score) - float(b_score)) <= tolerance + 1e-9


def _reading_row(item: dict[str, Any], *, side: str) -> dict[str, Any]:
    if side == "a":
        benchmark = item.get("benchmark_as_labelled") or item.get("benchmark_id") or ""
        metric = _metric_setting(item)
        model = item.get("model_as_labelled") or ""
    else:
        benchmark = item.get("benchmark_as_labelled") or item.get("benchmark_id") or ""
        metric = item.get("metric_or_setting") if "metric_or_setting" in item else _metric_setting(item)
        model = item.get("model_as_labelled") or ""
    parsed = parse_score(item.get("score"))
    text = item.get("score_text")
    if text is None or text == "":
        text = parsed.text
    else:
        text = str(text)
    model_key, bench_key, metric_key = _identity(model, benchmark, metric)
    return {
        "model_as_labelled": model,
        "benchmark_as_labelled": benchmark,
        "model_key": model_key,
        "bench_key": bench_key,
        "metric_key": metric_key,
        "score_kind": parsed.kind,
        "score_value": parsed.value,
        "score_text": text,
        "unit": item.get("unit") or "",
        "printed": bool(item.get("printed", side == "b")),
        "uncertainty": item.get("uncertainty"),
        "bar_index": item.get("bar_index"),
        "chart_index": item.get("chart_index"),
        "chart": item.get("chart") or "",
    }


def _judge_pair(a_item: dict[str, Any], b_item: dict[str, Any]) -> str:
    if a_item["score_kind"] == "unparsed" or b_item["score_kind"] == "unparsed":
        return "unparsed"
    if a_item["score_kind"] == "blank" and b_item["score_kind"] == "blank":
        return "agree"
    if a_item["score_kind"] != "number" or b_item["score_kind"] != "number":
        return "disagree"
    uncertainty = b_item.get("uncertainty")
    agree = _scores_agree(
        float(a_item["score_value"]),
        str(a_item["score_text"]),
        bool(a_item["printed"]),
        float(b_item["score_value"]),
        str(b_item["score_text"]),
        bool(b_item["printed"]),
        None if uncertainty is None else float(uncertainty),
    )
    return "agree" if agree else "disagree"


def _pair_record(
    status: str,
    source: str,
    fixture: dict[str, Any],
    reader: str,
    read_on: str,
    a_item: dict[str, Any] | None,
    b_item: dict[str, Any] | None,
) -> dict[str, Any]:
    shown = a_item or b_item or {}
    return {
        "class": status,
        "source": source,
        "fixture": fixture.get("_path") or "",
        "slug": fixture.get("_slug") or "",
        "chart_index": None if not a_item else a_item.get("chart_index"),
        "chart": (a_item or {}).get("chart") or (b_item or {}).get("chart") or "",
        "bar_index": None if not a_item else a_item.get("bar_index"),
        "reader": reader,
        "read_on": read_on,
        "model": shown.get("model_as_labelled") or "",
        "benchmark": shown.get("benchmark_as_labelled") or "",
        "metric": shown.get("metric_key") or "",
        "a": None
        if not a_item
        else {
            "score": a_item.get("score_value"),
            "score_text": a_item.get("score_text"),
            "unit": a_item.get("unit") or "",
            "printed": a_item.get("printed"),
        },
        "b": None
        if not b_item
        else {
            "score": b_item.get("score_value"),
            "score_text": b_item.get("score_text"),
            "unit": b_item.get("unit") or "",
            "printed": b_item.get("printed"),
            "uncertainty": b_item.get("uncertainty"),
        },
    }


def _pair_rows(
    a_rows: list[dict[str, Any]],
    b_rows: list[dict[str, Any]],
    source: str,
    fixture: dict[str, Any],
    reader: str,
    read_on: str,
) -> list[dict[str, Any]]:
    """Pair on model and benchmark. A repeated setting also has to match the metric."""
    a_by2: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    b_by2: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in a_rows:
        a_by2[(row["model_key"], row["bench_key"])].append(row)
    for row in b_rows:
        b_by2[(row["model_key"], row["bench_key"])].append(row)
    used_a: set[int] = set()
    used_b: set[int] = set()
    pairs: list[dict[str, Any]] = []
    for key, group in a_by2.items():
        other = b_by2.get(key) or []
        if len(group) == 1 and len(other) == 1:
            used_a.add(id(group[0]))
            used_b.add(id(other[0]))
            pairs.append(
                _pair_record(
                    _judge_pair(group[0], other[0]),
                    source,
                    fixture,
                    reader,
                    read_on,
                    group[0],
                    other[0],
                )
            )
    a_by3: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    b_by3: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in a_rows:
        if id(row) not in used_a:
            a_by3[(row["model_key"], row["bench_key"], row["metric_key"])].append(row)
    for row in b_rows:
        if id(row) not in used_b:
            b_by3[(row["model_key"], row["bench_key"], row["metric_key"])].append(row)
    for key in sorted(set(a_by3) | set(b_by3)):
        group = a_by3.get(key) or []
        other = b_by3.get(key) or []
        count = min(len(group), len(other))
        for index in range(count):
            pairs.append(
                _pair_record(
                    _judge_pair(group[index], other[index]),
                    source,
                    fixture,
                    reader,
                    read_on,
                    group[index],
                    other[index],
                )
            )
        for row in group[count:]:
            pairs.append(_pair_record("only_a", source, fixture, reader, read_on, row, None))
        for row in other[count:]:
            pairs.append(_pair_record("only_b", source, fixture, reader, read_on, None, row))
    return pairs


def _a_rows(charts: list[tuple[int, dict[str, Any]]]) -> list[dict[str, Any]]:
    rows = []
    for chart_index, chart in charts:
        for bar_index, bar in enumerate(chart.get("bars") or []):
            item = dict(bar)
            item["bar_index"] = bar_index
            item["chart_index"] = chart_index
            item["chart"] = chart.get("title") or ""
            rows.append(_reading_row(item, side="a"))
    return rows


def _b_rows(charts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for chart in charts:
        for item in chart.get("items") or []:
            if not isinstance(item, dict):
                continue
            copied = dict(item)
            copied["chart"] = chart.get("title") or ""
            rows.append(_reading_row(copied, side="b"))
    return rows


def _is_stub(reading: dict[str, Any]) -> bool:
    charts = [chart for chart in reading.get("charts") or [] if isinstance(chart, dict)]
    if not charts:
        return False
    return all(str(chart.get("title") or "") == "not_fetched" for chart in charts)


def reconcile_readings(
    fixtures: list[dict[str, Any]],
    readings: list[dict[str, Any]],
    manifest: dict[str, str],
) -> dict[str, Any]:
    """Pair a second reading onto fixture charts. Does not touch reader-b itself."""
    by_hash: dict[str, list[tuple[dict[str, Any], int, dict[str, Any]]]] = defaultdict(list)
    by_page: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        by_page[norm_page(str(fixture.get("page_url") or ""))] = fixture
        for index, chart in enumerate(fixture.get("charts") or []):
            digest = str(chart.get("image_sha256") or "").lower()
            if digest:
                by_hash[digest].append((fixture, index, chart))
    rows: list[dict[str, Any]] = []
    by_source: dict[str, dict[str, int]] = {}
    touched: list[dict[str, Any]] = []
    for reading in readings:
        source = str(reading.get("source") or "")
        reader = str(reading.get("reader") or "")
        read_on = str(reading.get("read_on") or "")
        b_charts = [chart for chart in reading.get("charts") or [] if isinstance(chart, dict)]
        b_items = _b_rows(b_charts)
        if _is_stub(reading):
            rows.append(
                {
                    "class": "unpaired_source",
                    "source": source,
                    "reader": reader,
                    "read_on": read_on,
                    "reason": "source was not fetched",
                }
            )
            fixture = by_page.get(norm_page(source)) if source.startswith(("http://", "https://")) else None
            a_count = 0
            if fixture is not None:
                a_count = sum(len(chart.get("bars") or []) for chart in fixture.get("charts") or [])
            by_source[source] = {
                "a_items": a_count,
                "b_items": len(b_items),
                "paired": 0,
                "agree": 0,
                "disagree": 0,
                "only_a": 0,
                "only_b": 0,
                "unparsed": 0,
                "unpaired_source": 1,
            }
            continue
        scope: list[tuple[dict[str, Any], list[tuple[int, dict[str, Any]]]]] = []
        if source.startswith(("http://", "https://")):
            fixture = by_page.get(norm_page(source))
            if fixture is None:
                rows.append(
                    {
                        "class": "unpaired_source",
                        "source": source,
                        "reader": reader,
                        "read_on": read_on,
                        "reason": "no fixture with this page_url",
                    }
                )
                by_source[source] = {
                    "a_items": 0,
                    "b_items": len(b_items),
                    "paired": 0,
                    "agree": 0,
                    "disagree": 0,
                    "only_a": 0,
                    "only_b": 0,
                    "unparsed": 0,
                    "unpaired_source": 1,
                }
                continue
            charts = [
                (index, chart)
                for index, chart in enumerate(fixture.get("charts") or [])
                if not chart.get("image_sha256")
            ]
            scope.append((fixture, charts))
        else:
            digest = manifest.get(source)
            located = by_hash.get(digest or "") or []
            if not digest or not located:
                rows.append(
                    {
                        "class": "unpaired_source",
                        "source": source,
                        "reader": reader,
                        "read_on": read_on,
                        "reason": "no fixture chart with this image hash",
                    }
                )
                by_source[source] = {
                    "a_items": 0,
                    "b_items": len(b_items),
                    "paired": 0,
                    "agree": 0,
                    "disagree": 0,
                    "only_a": 0,
                    "only_b": 0,
                    "unparsed": 0,
                    "unpaired_source": 1,
                }
                continue
            grouped: dict[int, tuple[dict[str, Any], list[tuple[int, dict[str, Any]]]]] = {}
            for fixture, index, chart in located:
                bucket = grouped.setdefault(id(fixture), (fixture, []))
                bucket[1].append((index, chart))
            scope.extend(grouped.values())
        source_rows: list[dict[str, Any]] = []
        for fixture, charts in scope:
            for chart_index, _chart in charts:
                touched.append(
                    {
                        "fixture": fixture.get("_path") or "",
                        "chart_index": chart_index,
                        "reader": reader,
                        "read_on": read_on,
                    }
                )
            source_rows.extend(
                _pair_rows(_a_rows(charts), b_items, source, fixture, reader, read_on)
            )
        rows.extend(source_rows)
        counts = Counter(row["class"] for row in source_rows)
        paired = counts.get("agree", 0) + counts.get("disagree", 0) + counts.get("unparsed", 0)
        by_source[source] = {
            "a_items": sum(counts.get(name, 0) for name in ("agree", "disagree", "unparsed", "only_a")),
            "b_items": len(b_items),
            "paired": paired,
            "agree": counts.get("agree", 0),
            "disagree": counts.get("disagree", 0),
            "only_a": counts.get("only_a", 0),
            "only_b": counts.get("only_b", 0),
            "unparsed": counts.get("unparsed", 0),
            "unpaired_source": 0,
        }
    counts = Counter(row["class"] for row in rows)
    return {"pairs": rows, "by_class": dict(counts), "by_source": by_source, "touched": touched}


def render_reconcile_markdown(report: dict[str, Any]) -> str:
    lines = ["# Chart reconcile", "", "## Counts", ""]
    for status in ("agree", "disagree", "only_a", "only_b", "unparsed", "unpaired_source"):
        lines.append(f"- {status}: {report['by_class'].get(status, 0)}")
    lines.extend(["", "## Pairs", ""])
    if not report["pairs"]:
        lines.append("None.")
    for row in report["pairs"]:
        if row["class"] == "unpaired_source":
            lines.append(f"- unpaired_source {row.get('source')}: {row.get('reason')}")
            continue
        a_score = "—" if not row.get("a") else _fmt(row["a"].get("score"))
        b_score = "—" if not row.get("b") else _fmt(row["b"].get("score"))
        lines.append(
            f"- {row['class']}: {row.get('source')} / {row.get('chart')} / "
            f"{row.get('model')} / {row.get('benchmark')} / {row.get('metric') or 'headline'} "
            f"A {a_score} B {b_score}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def write_reconcile(report: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "reconcile.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out / "reconcile.md").write_text(render_reconcile_markdown(report), encoding="utf-8")


def _chart_spans(text: str) -> list[tuple[int, int]]:
    starts = [match.start() for match in re.finditer(r"(?m)^  - title:", text)]
    spans = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        spans.append((start, end))
    return spans


def apply_second_reading(
    path: Path,
    chart_index: int,
    reader: str,
    read_on: str,
    disputes: list[dict[str, Any]],
) -> None:
    """Add the second reader, and mark disagreeing bars with both values."""
    text = path.read_text(encoding="utf-8")
    spans = _chart_spans(text)
    if chart_index < 0 or chart_index >= len(spans):
        raise ValueError(f"{path.name}: chart index {chart_index} is outside the file")
    start, end = spans[chart_index]
    chart = text[start:end]
    reading = f'      - reader: {reader}\n        date: "{read_on}"\n'
    if f"reader: {reader}\n" not in chart or f'date: "{read_on}"' not in chart:
        marker = "    bars:"
        at = chart.find(marker)
        if at < 0:
            raise ValueError(f"{path.name}: chart {chart_index} has no bars key")
        chart = chart[:at] + reading + chart[at:]
    bar_starts = [match.start() for match in re.finditer(r"(?m)^      - model_as_labelled:", chart)]
    for dispute in sorted(disputes, key=lambda item: item["bar_index"], reverse=True):
        bar_index = int(dispute["bar_index"])
        if bar_index < 0 or bar_index >= len(bar_starts):
            raise ValueError(f"{path.name}: bar index {bar_index} is outside the chart")
        bar_end = bar_starts[bar_index + 1] if bar_index + 1 < len(bar_starts) else len(chart)
        block = chart[bar_starts[bar_index] : bar_end]
        if "\n        disputed:" in block:
            continue
        insert = (
            "        disputed:\n"
            f"          - reader: {dispute['a_reader']}\n"
            f"            value: {_yaml_value(dispute['a_value'])}\n"
            f"          - reader: {dispute['b_reader']}\n"
            f"            value: {_yaml_value(dispute['b_value'])}\n"
        )
        chart = chart[:bar_end] + insert + chart[bar_end:]
    path.write_text(text[:start] + chart + text[end:], encoding="utf-8")


def _yaml_value(value: Any) -> str:
    text = str(value).strip()
    if re.fullmatch(r"-?(?:\d+(?:\.\d+)?|\.\d+)", text):
        return text
    return json.dumps(text)


def _load_reader_dir(directory: Path) -> list[dict[str, Any]]:
    docs = []
    for path in sorted(directory.glob("*.yaml")):
        source = path.read_text(encoding="utf-8")
        data = yaml.safe_load(source)
        if not isinstance(data, dict):
            raise ValueError(f"{path.name}: reader file is not a mapping")
        raw = _SCORE_LINE.findall(source)
        items = [
            item
            for chart in data.get("charts") or []
            if isinstance(chart, dict)
            for item in (chart.get("items") or [])
            if isinstance(item, dict)
        ]
        if len(raw) == len(items):
            for item, score_text in zip(items, raw, strict=True):
                item["score_text"] = score_text
        else:
            for item in items:
                if item.get("score_text"):
                    continue
                score = item.get("score")
                if isinstance(score, str) or score is None:
                    item["score_text"] = "" if score is None else score.strip()
        docs.append(data)
    return docs


def _check_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Classify release-chart fixtures against the cards.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    fixtures = load_fixtures(args.root / "benchmarks" / "_charts")
    models = load_models(args.root)
    problems = fixture_errors(fixtures, models)
    report = classify_fixtures(fixtures, models)
    report["fixture_errors"] = problems
    report["mismatch_errors"] = mismatch_errors(report)
    write_report(report, args.out)
    print(
        f"pages {report['pages']} charts {report['charts']} "
        f"bars {report['bars']} classes {report['by_class']}"
    )
    if problems or report["mismatch_errors"]:
        for line in problems + report["mismatch_errors"]:
            print(line, file=sys.stderr)
        return 1
    return 0


def _reconcile_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compare a second chart reading with the fixtures.")
    parser.add_argument("--reader-b", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--write-fixtures",
        action="store_true",
        help="Record the second reader on each compared chart and mark disagreements disputed.",
    )
    args = parser.parse_args(argv)
    fixtures = load_fixtures(args.root / "benchmarks" / "_charts")
    readings = _load_reader_dir(args.reader_b)
    report = reconcile_readings(fixtures, readings, load_manifest(args.manifest))
    write_reconcile(report, args.out)
    if args.write_fixtures:
        grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
        for row in report["pairs"]:
            if row["class"] != "disagree" or row.get("bar_index") is None:
                continue
            key = (row["fixture"], int(row["chart_index"]))
            a_reader = "fixture"
            fixture = next((item for item in fixtures if item.get("_path") == row["fixture"]), None)
            if fixture is not None:
                chart = (fixture.get("charts") or [])[int(row["chart_index"])]
                first = (chart.get("readings") or [{}])[0]
                a_reader = str(first.get("reader") or a_reader)
            grouped[key].append(
                {
                    "bar_index": row["bar_index"],
                    "a_reader": a_reader,
                    "a_value": row["a"]["score_text"],
                    "b_reader": row["reader"],
                    "b_value": row["b"]["score_text"],
                }
            )
        seen: set[tuple[str, int]] = set()
        for touch in report.get("touched") or []:
            key = (touch["fixture"], int(touch["chart_index"]))
            if key in seen or not key[0]:
                continue
            seen.add(key)
            apply_second_reading(
                Path(key[0]),
                key[1],
                touch["reader"],
                touch["read_on"],
                grouped.get(key, []),
            )
    counts = report["by_class"]
    print(
        "reconcile "
        + " ".join(
            f"{name} {counts.get(name, 0)}"
            for name in ("agree", "disagree", "only_a", "only_b", "unparsed", "unpaired_source")
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "reconcile":
        return _reconcile_main(argv[1:])
    return _check_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
