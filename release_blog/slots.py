"""Fact slots for platform drafts (MODEL-226).

A draft is a list of pieces. A piece is a reviewed literal with no digit, or
a slot that names a fact and a formatter. ``bind`` rebuilds the draft from
those pieces and the breakdown, requires the same bytes, and rejects any
digit that the slot did not place. There is no second channel for text.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from release_blog.model import Breakdown, Cited
from release_blog.render import SNAPSHOT_FILE, _number
from release_blog.wording import difference, plan_line

_DIGIT = re.compile(r"\d")
_DIGITS = re.compile(r"\d+")
_FORMATTERS = frozenset({"value", "source_url", "read_date"})
_BARE_UNITS = {None, "percent", "USD", "USD per month", "usd_per_1m_tokens", "probability"}


@dataclass(frozen=True)
class Fact:
    fact_id: str
    formatted: str
    source_url: str
    read_date: str


@dataclass(frozen=True)
class Literal:
    text: str

    def __post_init__(self) -> None:
        if _DIGIT.search(self.text):
            raise ValueError(f"template literal contains a digit: {self.text!r}")


@dataclass(frozen=True)
class Slot:
    fact_id: str
    formatter: str = "value"

    def __post_init__(self) -> None:
        if self.formatter not in _FORMATTERS:
            raise ValueError(f"unknown formatter {self.formatter}")


Piece = Literal | Slot


def needs_unit_suffix(unit: str | None) -> bool:
    return unit not in _BARE_UNITS


def _locate(breakdown: Breakdown, cited: Cited) -> tuple[str, str]:
    for source_id in cited.source_ids:
        url = breakdown.sources.get(source_id) or ""
        if url.startswith("https://"):
            return url, cited.read_date.isoformat()
    snap = breakdown.generated_from.after.snapshot_id
    return SNAPSHOT_FILE.format(id=snap), cited.read_date.isoformat()


def _label(book: dict[str, Fact], fact_id: str, text: str) -> None:
    """An identifier copied from the breakdown. It is not a measured reading."""
    current = book.get(fact_id)
    if current is not None:
        if current.formatted != text:
            raise ValueError(f"label {fact_id} already has a different value")
        return
    _add(book, fact_id, text, "", "")


def _add(book: dict[str, Fact], fact_id: str, formatted: str, url: str, read: str) -> None:
    if fact_id in book:
        raise ValueError(f"duplicate fact id {fact_id}")
    book[fact_id] = Fact(fact_id, formatted, url, read)


def _add_cited(
    book: dict[str, Fact],
    fact_id: str,
    formatted: str,
    breakdown: Breakdown,
    cited: Cited,
) -> None:
    url, read = _locate(breakdown, cited)
    _add(book, fact_id, formatted, url, read)


def catalogue(breakdown: Breakdown, post_url: str) -> dict[str, Fact]:
    """Every fact a draft can print, keyed by id."""
    book: dict[str, Fact] = {}
    as_of = breakdown.generated_from.after.as_of
    if as_of is None:
        raise ValueError("generated_from.after.as_of is missing")
    snapshot = SNAPSHOT_FILE.format(id=breakdown.generated_from.after.snapshot_id)
    _add(book, "model.name", breakdown.model.name, snapshot, as_of.isoformat())
    _add(book, "post.url", post_url, "", "")
    for row in breakdown.claims_vs_evidence.claims:
        claim_id = f"claims.{row.benchmark}.claim"
        _add_cited(book, claim_id, _number(row.claim.value, row.claim.unit), breakdown, row.claim)
        for index, reading in enumerate(row.readings):
            base = f"claims.{row.benchmark}.readings[{index}]"
            value = reading.value
            _add_cited(book, f"{base}.value", _number(value.value, value.unit), breakdown, value)
            change = reading.difference
            if change is None:
                continue
            shown = _number(abs(change.value), change.unit).rstrip("%")
            _add_cited(book, f"{base}.difference", shown, breakdown, change)
    for item in breakdown.claims_vs_evidence.unreported:
        fact_id = f"claims.unreported.{item.benchmark}.reading"
        shown = _number(item.reading.value, item.reading.unit)
        _add_cited(book, fact_id, shown, breakdown, item.reading)
    for index, standing in enumerate(breakdown.standing):
        for name, cited in (
            ("band_size", standing.band_size),
            ("rank", standing.rank),
            ("ranked_models", standing.ranked_models),
        ):
            if cited is None:
                continue
            _add_cited(
                book,
                f"standing[{index}].{name}",
                _number(cited.value, cited.unit),
                breakdown,
                cited,
            )
    for index, offering in enumerate(breakdown.cost.offerings):
        cost = offering.cost_per_task
        if cost is None:
            continue
        url, read = _locate(breakdown, cost)
        _add(book, f"cost.offerings[{index}].task.input", f"{offering.task.input:,}", url, read)
        _add(book, f"cost.offerings[{index}].task.output", f"{offering.task.output:,}", url, read)
        _add(
            book,
            f"cost.offerings[{index}].cost_per_task",
            _number(cost.value, cost.unit),
            url,
            read,
        )
    held = breakdown.not_yet_measured.held_back or {}
    for reason, cited in held.items():
        _add_cited(book, f"held_back.{reason}", _number(cited.value, cited.unit), breakdown, cited)
        _label(book, f"label.held.{reason}", reason.replace("_", " "))
    _label(book, "label.class", breakdown.model.class_.replace("-", " "))
    gaps = breakdown.not_yet_measured
    for name in gaps.claims_without_reading:
        _label(book, f"label.benchmark.{name}", name)
    for row in breakdown.claims_vs_evidence.claims:
        _label(book, f"label.benchmark.{row.benchmark}", row.benchmark)
        for index, reading in enumerate(row.readings):
            if reading.comparability == "same_setup":
                continue
            sentence = difference(reading.comparability, differs_in=reading.differs_in)
            sentence = sentence[:1].lower() + sentence[1:]
            _label(book, f"label.relation.{row.benchmark}[{index}]", sentence)
            if needs_unit_suffix(reading.value.unit):
                unit = " " + (reading.value.unit or "").replace("_", " ")
                _label(book, f"label.unit.{row.benchmark}[{index}]", unit)
    for item in breakdown.claims_vs_evidence.unreported:
        _label(book, f"label.benchmark.{item.benchmark}", item.benchmark)
    for index, standing in enumerate(breakdown.standing):
        name = standing.domain.name
        _label(book, f"label.standing[{index}].domain", name[:1].lower() + name[1:])
    for index, name in enumerate(gaps.domains_without_estimate):
        _label(book, f"label.domain[{index}]", name)
    for index, row in enumerate(gaps.unknown_facets):
        _label(book, f"label.facet[{index}]", row.facet)
    for index, row in enumerate(gaps.domains_inapplicable):
        _label(book, f"label.inapplicable[{index}].domain", row.domain)
        _label(book, f"label.inapplicable[{index}].reason", row.reason)
    for index, plan in enumerate(breakdown.cost.plans):
        _label(book, f"label.plan[{index}]", plan_line(plan.covers, plan.plan["name"]))
    return book


def piece_text(piece: Piece, book: dict[str, Fact]) -> str:
    if isinstance(piece, Literal):
        return piece.text
    try:
        fact = book[piece.fact_id]
    except KeyError as exc:
        raise ValueError(f"unknown fact id {piece.fact_id}") from exc
    if piece.formatter == "value":
        return fact.formatted
    if piece.formatter == "source_url":
        return fact.source_url
    return fact.read_date


def assemble(pieces: Sequence[Piece], breakdown: Breakdown, post_url: str) -> str:
    book = catalogue(breakdown, post_url)
    return "".join(piece_text(piece, book) for piece in pieces)


def bind(output: str, pieces: Sequence[Piece], breakdown: Breakdown, post_url: str) -> None:
    """Rebuild ``output`` from the manifest and reject a digit the slot did not place."""
    book = catalogue(breakdown, post_url)
    spans: list[tuple[int, int]] = []
    parts: list[str] = []
    cursor = 0
    for piece in pieces:
        if isinstance(piece, Literal):
            if _DIGIT.search(piece.text):
                raise ValueError(f"template literal contains a digit: {piece.text!r}")
            text = piece.text
        elif isinstance(piece, Slot):
            text = piece_text(piece, book)
            spans.append((cursor, cursor + len(text)))
        else:
            raise ValueError("manifest piece is not a literal or a slot")
        parts.append(text)
        cursor += len(text)
    expected = "".join(parts)
    if output != expected:
        if output.startswith(expected):
            match = _DIGITS.search(output[len(expected) :])
            if match:
                raise ValueError(f"digit sequence {match.group()!r} is not from a fact slot")
        raise ValueError("draft bytes do not match the manifest")
    for match in _DIGITS.finditer(output):
        if not any(start <= match.start() and match.end() <= end for start, end in spans):
            raise ValueError(f"digit sequence {match.group()!r} is not from a fact slot")
