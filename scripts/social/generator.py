"""Generate social drafts and image cards from decision snapshots.

The module reads local files only. It has no posting or network interface.
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import textwrap
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from api.ranking.engine import neutrality_commitment
from decision.computed import COST_PER_TASK, with_computed
from decision.contract import DEFAULT_TASK_TOKENS, Compare, Objective, Spec
from decision.engine import decide
from decision.registry import Domain
from decision.registry import default as default_registry
from decision.snapshot import LoadedSnapshot, load_snapshot
from decision.vocabulary import build_vocabulary
from schema.suppliers import supplier_for

ROOT = Path(__file__).resolve().parents[2]
BRAND_MARK = ROOT / "brand" / "2a" / "modelspec-mark-transparent.svg"
SNAPSHOT_URL = "https://modelspec.dev/api/decision/snapshot.json.gz"

PLATFORM_SIZES: dict[str, tuple[int, int]] = {
    "x": (1200, 675),
    "linkedin": (1200, 627),
    "instagram_square": (1080, 1080),
    "instagram_story": (1080, 1920),
    "tiktok_cover": (1080, 1920),
}

PR_ACCURACY_LAYERS = frozenset(
    {"deterministic_correctness", "freshness", "golden_answers", "output_parity"}
)


@dataclass(frozen=True)
class Standing:
    snapshot: LoadedSnapshot
    domain: Domain
    benchmark: str
    higher_is_better: bool
    ordered_models: tuple[str, ...]
    results: Mapping[str, Any]
    decision: Any

    def rank(self, model_id: str) -> int | None:
        try:
            return self.ordered_models.index(model_id) + 1
        except ValueError:
            return None


def _accuracy(path: Path, snapshot_id: str) -> dict[str, Any]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"could not read accuracy report {path}: {exc}") from exc
    if not isinstance(report, dict):
        raise ValueError(f"accuracy report {path} is not a JSON object")
    if report.get("status") != "pass":
        raise ValueError("accuracy report did not pass")
    if report.get("snapshot") != snapshot_id:
        raise ValueError(f"accuracy report covers {report.get('snapshot')!r}, not {snapshot_id!r}")
    if report.get("profile") != "pr":
        raise ValueError("accuracy report must use the pr profile")
    layers = report.get("layers")
    if not isinstance(layers, list) or any(not isinstance(row, Mapping) for row in layers):
        raise ValueError("accuracy report must contain the exact pr layers")
    names = [str(row.get("name", "")) for row in layers]
    if len(names) != len(PR_ACCURACY_LAYERS) or set(names) != PR_ACCURACY_LAYERS:
        raise ValueError("accuracy report must contain the exact pr layers")
    failed = [row.get("name", "unnamed") for row in layers if row.get("status") != "pass"]
    if failed:
        raise ValueError("accuracy report did not pass layers: " + ", ".join(failed))
    return dict(report)


def _load_signed(path: Path, key: bytes | str | None) -> LoadedSnapshot:
    if not key:
        raise ValueError("a snapshot verification key is required")
    snapshot = load_snapshot(path, key=key)
    if not snapshot.signature_verified:
        raise ValueError(f"snapshot signature was not verified: {path}")
    return snapshot


def _target_class(snapshot: LoadedSnapshot, model_id: str) -> str:
    candidates = set(snapshot.candidates())
    if model_id not in candidates and not any(
        snapshot.model_of(cid) == model_id for cid in candidates
    ):
        raise ValueError(f"{model_id!r} is not in snapshot {snapshot.snapshot_id}")
    found = snapshot.fact(model_id, "model.class")
    if found.state != "known" or not isinstance(found.value, str):
        raise ValueError(f"{model_id}: model.class is unknown")
    return found.value


def _standings(snapshot: LoadedSnapshot, model_class: str) -> list[Standing]:
    registry = default_registry()
    vocabulary = build_vocabulary(snapshot, registry=registry)
    domain_rows = {row["id"]: row for row in vocabulary["domains"]}
    benchmark_rows = {row["id"]: row for row in vocabulary["benchmarks"]}
    rows: list[Standing] = []
    for domain in registry.domains():
        published = domain_rows.get(domain.id)
        if published is None or not published["benchmarks"]:
            continue
        benchmark = published["default_benchmark"] or published["benchmarks"][0]
        higher_is_better = bool(benchmark_rows[benchmark]["higher_is_better"])
        spec = Spec(
            spec_version=1,
            capabilities={domain.id: "required"},
            where=[Compare(facet="model.class", op="=", value=model_class)],
            optimize=Objective(**({"max": benchmark} if higher_is_better else {"min": benchmark})),
            explain="full",
            limit=500,
        )
        answer = decide(spec, snapshot, facets=registry.facet)
        ordered: list[str] = []
        results: dict[str, Any] = {}
        for result in answer.results:
            model_id = result.offering.model
            if model_id not in results:
                ordered.append(model_id)
                results[model_id] = result
        rows.append(
            Standing(
                snapshot,
                domain,
                benchmark,
                higher_is_better,
                tuple(ordered),
                results,
                answer,
            )
        )
    return rows


def _record_date(snapshot: LoadedSnapshot, record_id: str | None) -> str | None:
    if not record_id:
        return None
    try:
        record = snapshot.record(record_id)
    except (KeyError, TypeError):
        return None
    verification = record.get("verification") if isinstance(record, Mapping) else None
    if isinstance(verification, Mapping) and verification.get("date"):
        return str(verification["date"])
    return None


def _claim(
    text: str, number: str, source: str, day: str, *, citation: str | None = None
) -> dict[str, str]:
    citation = citation or f"Source: {source} (read {day})"
    return {
        "text": text,
        "number": number,
        "source": source,
        "date": day,
        "citation": citation,
    }


def _validate_draft(draft: Mapping[str, Any]) -> None:
    """Refuse a numeric claim unless its source URL and read date travel with it."""
    for claim in draft.get("claims", []):
        number = str(claim.get("number") or "")
        source = str(claim.get("source") or "")
        read = str(claim.get("date") or "")
        citation = str(claim.get("citation") or "")
        if not number:
            raise ValueError(f"{draft.get('angle')}: numeric claim has no number")
        if not source.startswith("https://"):
            raise ValueError(f"{draft.get('angle')}: {number} has no HTTPS source")
        try:
            date.fromisoformat(read)
        except ValueError as exc:
            raise ValueError(f"{draft.get('angle')}: {number} has no ISO read date") from exc
        if source not in citation or read not in citation:
            raise ValueError(f"{draft.get('angle')}: {number} drops its source or read date")


def _snapshot_claim(snapshot: LoadedSnapshot, text: str, number: str) -> dict[str, str]:
    if snapshot.as_of is None:
        raise ValueError(f"snapshot {snapshot.snapshot_id} has no as_of date")
    return _claim(text, number, SNAPSHOT_URL, snapshot.as_of.isoformat())


def _evidence_item(standing: Standing, model_id: str) -> Any:
    result = standing.results[model_id]
    items = [
        item
        for group in result.evidence
        for item in group.items
        if item.benchmark == standing.benchmark
    ]
    if not items:
        raise ValueError(f"{model_id}: decision returned no {standing.benchmark} evidence")
    order = max if standing.higher_is_better else min
    return order(items, key=lambda item: item.value)


def _evidence_claim(standing: Standing, model_id: str) -> dict[str, str]:
    item = _evidence_item(standing, model_id)
    value = f"{item.value:g}"
    unit = (item.unit or "points").replace("_", " ")
    verified = next(
        (
            source.date
            for source in standing.decision.sources
            if str(source.url) == str(item.source) and source.date is not None
        ),
        None,
    )
    if verified is None:
        raise ValueError(f"{model_id}: {item.benchmark} source has no verification date")
    return _claim(
        f"Verified {item.benchmark} evidence: {value} {unit}.",
        value,
        str(item.source),
        verified.isoformat(),
    )


def _display_class(raw: str) -> str:
    return raw.replace("-", " ")


def _new_entrant(
    model_id: str,
    current: Sequence[Standing],
    previous: Mapping[str, Standing],
    snapshot: LoadedSnapshot,
    model_class: str,
) -> dict[str, Any] | None:
    eligible = []
    for standing in current:
        rank = standing.rank(model_id)
        if rank is None or rank > 5:
            continue
        prior = previous.get(standing.domain.id)
        prior_rank = None if prior is None else prior.rank(model_id)
        entered = prior_rank is not None and prior_rank > 5
        if rank == 1 or entered:
            eligible.append((rank, standing.domain.id, standing, entered))
    if not eligible:
        return None
    rank, _, standing, entered = min(eligible, key=lambda row: (row[0], row[1]))
    verb = "enters" if entered and rank != 1 else "ranks"
    rank_claim = _snapshot_claim(
        snapshot,
        f"{model_id} {verb} #{rank} for {standing.domain.name} within the "
        f"{_display_class(model_class)} class.",
        str(rank),
    )
    prior = previous.get(standing.domain.id)
    if entered and prior is not None and prior.snapshot.as_of is not None:
        rank_claim["citation"] += (
            f"; prior snapshot: {SNAPSHOT_URL} (read {prior.snapshot.as_of.isoformat()})"
        )
    claims = [
        rank_claim,
        _evidence_claim(standing, model_id),
    ]
    return {"angle": "new_entrant", "title": "New entrant", "claims": claims}


def _price_claim(snapshot: LoadedSnapshot, cid: str, value: float) -> dict[str, str]:
    inputs = snapshot.fact(cid, "offering.price.input")
    outputs = snapshot.fact(cid, "offering.price.output")
    provenance: list[tuple[str, str, str]] = []
    for label, fact in (("input", inputs), ("output", outputs)):
        if not fact.sources:
            raise ValueError(f"{cid}: {label} price fact has no source")
        day = _record_date(snapshot, fact.record_id)
        if day is None:
            raise ValueError(f"{cid}: {label} price fact has no verification date")
        provenance.extend(
            (label, snapshot.source_url(source_id), day) for source_id in fact.sources
        )
    amount = f"{value:.4f}".rstrip("0").rstrip(".")
    citation = "; ".join(
        f"{label.capitalize()} price source: {source} (read {day})"
        for label, source, day in provenance
    )
    return _claim(
        f"Default task cost at list price: ${amount}.",
        amount,
        provenance[0][1],
        provenance[0][2],
        citation=citation,
    )


def _value_angle(
    model_id: str,
    standing: Standing,
    snapshot: LoadedSnapshot,
    model_class: str,
) -> dict[str, Any] | None:
    if not standing.higher_is_better:
        return None
    priced = with_computed(snapshot, DEFAULT_TASK_TOKENS)
    candidates: list[tuple[float, str, float]] = []
    for cid in snapshot.candidates():
        if snapshot.kind(cid) != "offering":
            continue
        model = snapshot.model_of(cid)
        if snapshot.fact(model, "model.class").value != model_class:
            continue
        values = snapshot.evidence(cid, standing.benchmark)
        computed = priced.computed(cid, COST_PER_TASK)
        if not values or computed is None or computed.value <= 0:
            continue
        score = max(row.value for row in values)
        candidates.append((score / computed.value, cid, score))
    if not candidates:
        return None
    _, winner, _ = max(candidates, key=lambda row: (row[0], row[2], row[1]))
    if snapshot.model_of(winner) != model_id:
        return None
    computed = priced.computed(winner, COST_PER_TASK)
    assert computed is not None
    claims = [
        _snapshot_claim(
            snapshot,
            f"{model_id} has the best verified {standing.benchmark} evidence per dollar "
            f"within the {_display_class(model_class)} class.",
            "1",
        ),
        _evidence_claim(standing, model_id),
        _price_claim(snapshot, winner, computed.value),
    ]
    return {"angle": "value", "title": "Value angle", "claims": claims}


def _local_angle(
    model_id: str,
    standing: Standing,
    snapshot: LoadedSnapshot,
    device: str | None,
    model_class: str,
) -> dict[str, Any] | None:
    if not device:
        return None
    fitting = [
        candidate
        for candidate in standing.ordered_models
        if device in (snapshot.fact(candidate, "model.fits_hardware").value or [])
    ]
    if not fitting or fitting[0] != model_id:
        return None
    fact = snapshot.fact(model_id, "model.fits_hardware")
    if not fact.sources:
        raise ValueError(f"{model_id}: model.fits_hardware has no source")
    day = _record_date(snapshot, fact.record_id)
    if day is None:
        raise ValueError(f"{model_id}: model.fits_hardware has no verification date")
    claims = [
        _claim(
            f"{model_id} is estimated to fit {device}.",
            device,
            snapshot.source_url(fact.sources[0]),
            day,
        ),
        _snapshot_claim(
            snapshot,
            f"{model_id} ranks #1 for {standing.domain.name} within the "
            f"{_display_class(model_class)} class.",
            "1",
        ),
        _evidence_claim(standing, model_id),
    ]
    return {"angle": "local", "title": "Local angle", "claims": claims}


def _honest_gaps(standings: Sequence[Standing], snapshot: LoadedSnapshot) -> dict[str, Any] | None:
    gaps: dict[str, set[str]] = {}
    for standing in standings:
        for row in standing.decision.may_qualify:
            gaps.setdefault(row.model, set()).update(row.unknown)
    if not gaps:
        return None
    models = len(gaps)
    outstanding = sum(len(values) for values in gaps.values())
    claim = _snapshot_claim(
        snapshot,
        f"Not yet ranked: {models} model{'s' if models != 1 else ''}, with "
        f"{outstanding} outstanding fact{'s' if outstanding != 1 else ''} or benchmark "
        f"reading{'s' if outstanding != 1 else ''}.",
        f"{models},{outstanding}",
    )
    return {"angle": "honest_gaps", "title": "Honest gaps", "claims": [claim]}


def _weekly_movers(
    model_id: str,
    current: Sequence[Standing],
    previous: Mapping[str, Standing],
    snapshot: LoadedSnapshot,
) -> dict[str, Any] | None:
    moves = []
    for standing in current:
        prior = previous.get(standing.domain.id)
        if prior is None:
            continue
        for candidate in standing.ordered_models:
            now, before = standing.rank(candidate), prior.rank(candidate)
            if now is not None and before is not None and now != before:
                moves.append(
                    (abs(before - now), standing.domain.id, candidate, before, now, standing)
                )
    if not moves:
        return None
    largest = max(row[0] for row in moves)
    target_moves = [row for row in moves if row[0] == largest and row[2] == model_id]
    if not target_moves:
        return None
    change, _, _, before, now, standing = max(target_moves, key=lambda row: (row[0], row[1]))
    direction = "up" if now < before else "down"
    claim = _snapshot_claim(
        snapshot,
        f"Weekly mover: {model_id} moved {direction} {change} place"
        f"{'s' if change != 1 else ''}, from #{before} to #{now}, for {standing.domain.name}.",
        f"{change},{before},{now}",
    )
    prior = previous[standing.domain.id]
    if prior.snapshot.as_of is not None:
        claim["citation"] += (
            f"; prior snapshot: {SNAPSHOT_URL} (read {prior.snapshot.as_of.isoformat()})"
        )
    return {"angle": "weekly_movers", "title": "Weekly movers", "claims": [claim]}


def _disclosure(model_id: str) -> str:
    pledge = neutrality_commitment()["pledge"]
    supplier = supplier_for(model_id.split("/", 1)[0])
    if supplier is None:
        return f"Disclosure: {pledge}"
    return (
        f"Disclosure: {supplier.relationship} {supplier.rule} {pledge} "
        "Source: https://modelspec.dev/legal/neutrality/ (read 2026-09-23)"
    )


def _post_text(draft: Mapping[str, Any], disclosure: str, platform: str) -> str:
    if platform == "x":
        text = (
            f"ModelSpec {draft['title'].lower()}. The attached card has every figure's "
            f"source and read date.\n\n{disclosure}"
        )
        if len(text) > 280:
            text = (
                f"ModelSpec {draft['title'].lower()}. Sourced, dated figures are on the card.\n\n"
                f"{neutrality_commitment()['pledge']}"
            )
        if len(text) > 280:
            raise ValueError("X draft exceeds 280 characters")
        return text + "\n"
    lines = [draft["title"], ""]
    for claim in draft["claims"]:
        lines.extend((claim["text"], claim["citation"], ""))
    lines.append(disclosure)
    lines.append(
        "Generated from a signed ModelSpec decision snapshot. Nothing was posted automatically."
    )
    return "\n".join(lines).rstrip() + "\n"


def _brand_data_uri() -> str:
    encoded = base64.b64encode(BRAND_MARK.read_bytes()).decode("ascii")
    return "data:image/svg+xml;base64," + encoded


def _svg(draft: Mapping[str, Any], disclosure: str, width: int, height: int) -> str:
    landscape = width / height > 1.5
    if landscape:
        margin, mark_size = 48, 64
        title_size, body_size, foot_size = 50, 22, 14
        y = margin + 100
    else:
        margin = max(56, round(width * 0.065))
        mark_size = 72
        title_size = max(42, round(width * 0.055))
        body_size = max(24, round(width * 0.026))
        foot_size = max(16, round(width * 0.014))
        y = margin + 115
    pieces = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#0B1426"/>',
        f'<image href="{_brand_data_uri()}" x="{margin}" y="{margin}" '
        f'width="{mark_size}" height="{mark_size}"/>',
        f'<text x="{margin + mark_size + 20}" y="{margin + round(mark_size * 0.7)}" '
        'fill="#FFFFFF" font-family="Segoe UI,Arial,sans-serif" font-size="34" '
        'font-weight="600">ModelSpec</text>',
        f'<text x="{margin}" y="{y}" fill="#F2C94C" font-family="Segoe UI,Arial,sans-serif" '
        f'font-size="{title_size}" font-weight="600">{escape(draft["title"])}</text>',
    ]
    y += title_size + 34
    wrap = max(24, round((width - 2 * margin) / (body_size * 0.55)))
    for claim in draft["claims"]:
        for line in textwrap.wrap(claim["text"], width=wrap):
            pieces.append(
                f'<text x="{margin}" y="{y}" fill="#FFFFFF" '
                f'font-family="Segoe UI,Arial,sans-serif" font-size="{body_size}">'
                f"{escape(line)}</text>"
            )
            y += round(body_size * 1.3)
        for line in textwrap.wrap(claim["citation"], width=max(wrap, 50)):
            pieces.append(
                f'<text x="{margin}" y="{y}" fill="#5AA9EC" '
                f'font-family="Segoe UI,Arial,sans-serif" font-size="{foot_size}">'
                f"{escape(line)}</text>"
            )
            y += round(foot_size * 1.25)
        y += round(body_size * 0.55)
    disclosure_lines = textwrap.wrap(disclosure, width=max(45, round(wrap * 1.25)))
    line_height = round(foot_size * 1.25)
    footer_y = max(
        y + line_height,
        height - margin - (len(disclosure_lines) - 1) * line_height,
    )
    if footer_y + (len(disclosure_lines) - 1) * line_height > height - 12:
        raise ValueError(f"{draft['angle']} card content does not fit {width}x{height}")
    for line in disclosure_lines:
        pieces.append(
            f'<text x="{margin}" y="{footer_y}" fill="#3FB68B" '
            f'font-family="Segoe UI,Arial,sans-serif" font-size="{foot_size}">{escape(line)}</text>'
        )
        footer_y += round(foot_size * 1.25)
    pieces.append("</svg>")
    return "\n".join(pieces) + "\n"


def _png(svg: Path, png: Path) -> bool:
    converter = shutil.which("rsvg-convert")
    if converter is None:
        return False
    subprocess.run(
        [converter, "--format", "png", "--output", str(png), str(svg)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return True


def _write_draft(root: Path, draft: dict[str, Any], disclosure: str) -> None:
    platforms: dict[str, dict[str, str | None]] = {}
    for platform, (width, height) in PLATFORM_SIZES.items():
        directory = root / draft["angle"]
        directory.mkdir(parents=True, exist_ok=True)
        text_path = directory / f"{platform}.txt"
        svg_path = directory / f"{platform}.svg"
        png_path = directory / f"{platform}.png"
        text_path.write_text(_post_text(draft, disclosure, platform), encoding="utf-8")
        svg_path.write_text(_svg(draft, disclosure, width, height), encoding="utf-8")
        has_png = _png(svg_path, png_path)
        platforms[platform] = {
            "text": text_path.relative_to(root).as_posix(),
            "svg": svg_path.relative_to(root).as_posix(),
            "png": png_path.relative_to(root).as_posix() if has_png else None,
        }
    draft["platforms"] = platforms


def generate(
    *,
    model_id: str,
    snapshot_path: str | Path,
    accuracy_report_path: str | Path,
    output_dir: str | Path,
    previous_snapshot_path: str | Path | None = None,
    device: str | None = None,
    snapshot_key: bytes | str | None = None,
) -> dict[str, Any]:
    """Write every supported draft and return its deterministic manifest."""
    current = _load_signed(Path(snapshot_path), snapshot_key)
    _accuracy(Path(accuracy_report_path), current.snapshot_id)
    previous = (
        None
        if previous_snapshot_path is None
        else _load_signed(Path(previous_snapshot_path), snapshot_key)
    )
    model_class = _target_class(current, model_id)
    current_rows = _standings(current, model_class)
    if not current_rows:
        raise ValueError(f"no registered domain default has evidence for {model_class}")
    previous_rows = {
        row.domain.id: row for row in (_standings(previous, model_class) if previous else [])
    }
    primary = next((row for row in current_rows if row.rank(model_id) is not None), current_rows[0])
    drafts = [
        _new_entrant(model_id, current_rows, previous_rows, current, model_class),
        _value_angle(model_id, primary, current, model_class),
        _local_angle(model_id, primary, current, device, model_class),
        _honest_gaps(current_rows, current),
        _weekly_movers(model_id, current_rows, previous_rows, current),
    ]
    kept = [draft for draft in drafts if draft is not None]
    if not kept:
        raise ValueError(f"the snapshot supports no social angle for {model_id}")
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    disclosure = _disclosure(model_id)
    for draft in kept:
        _validate_draft(draft)
        _write_draft(root, draft, disclosure)
    manifest = {
        "schema_version": 1,
        "model": model_id,
        "snapshot": current.snapshot_id,
        "previous_snapshot": previous.snapshot_id if previous else None,
        "accuracy_report": Path(accuracy_report_path).name,
        "automatic_posting": False,
        "drafts": kept,
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest
