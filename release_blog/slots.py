"""Fact slots for platform drafts (MODEL-226).

A slot is one formatted fact. Prose and chart text may contain a digit only
when a slot placed it there. ``Piece.lit`` rejects a digit in a template.
``audit`` rejects a digit in rendered claim text that is not one of the
slots for that surface.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser

from release_blog.model import Breakdown, Cited
from release_blog.render import SNAPSHOT_FILE, _number

_DIGIT = re.compile(r"\d")
# Optional minus so a formatted ``-0.30`` matches the character sequence in the chart.
_TOKEN = re.compile(r"(?<![\w.^])-?[$]?\d[\d,]*(?:\.\d+)?%?")
_TEXT = re.compile(r"<text\b[^>]*>(.*?)</text>", re.DOTALL)
_TITLE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.DOTALL)
_LABEL = re.compile(r'aria-label="([^"]*)"')
_BARE_UNITS = {None, "percent", "USD", "USD per month", "usd_per_1m_tokens", "probability"}


@dataclass(frozen=True)
class Fact:
    fact_id: str
    formatted: str
    source_url: str
    read_date: str


@dataclass(frozen=True)
class FilledSlot:
    fact_id: str
    source_url: str
    read_date: str
    formatted: str
    chart: str


def _pure(text: str) -> bool:
    return _TOKEN.fullmatch(text.strip()) is not None


def _cover(text: str) -> bool:
    """A string that may hide a digit without being a measurement token."""
    return bool(text) and bool(_DIGIT.search(text)) and not _pure(text)


@dataclass
class Piece:
    """One chart's sentence. Digits enter through ``put`` or ``data``."""

    chart: str
    parts: list[str] = field(default_factory=list)
    slots: list[FilledSlot] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)
    identity: list[str] = field(default_factory=list)

    def lit(self, text: str) -> None:
        if _DIGIT.search(text):
            raise ValueError(f"template literal contains a digit: {text!r}")
        self.parts.append(text)

    def data(self, text: str) -> None:
        if _cover(text):
            self.identity.append(text)
        self.parts.append(text)

    def put(self, fact: Fact) -> None:
        self.parts.append(fact.formatted)
        self.tokens.append(fact.formatted)
        self.slots.append(
            FilledSlot(
                fact.fact_id,
                fact.source_url,
                fact.read_date,
                fact.formatted,
                self.chart,
            )
        )

    @property
    def text(self) -> str:
        return "".join(self.parts)


def _locate(breakdown: Breakdown, cited: Cited) -> tuple[str, str]:
    for source_id in cited.source_ids:
        url = breakdown.sources.get(source_id) or ""
        if url.startswith("https://"):
            return url, cited.read_date.isoformat()
    snap = breakdown.generated_from.after.snapshot_id
    return SNAPSHOT_FILE.format(id=snap), cited.read_date.isoformat()


def _add(book: dict[str, Fact], fact_id: str, formatted: str, url: str, read: str) -> Fact:
    if fact_id in book:
        raise ValueError(f"duplicate fact id {fact_id}")
    fact = Fact(fact_id, formatted, url, read)
    book[fact_id] = fact
    return fact


def _add_cited(
    book: dict[str, Fact],
    fact_id: str,
    formatted: str,
    breakdown: Breakdown,
    cited: Cited,
) -> Fact:
    url, read = _locate(breakdown, cited)
    return _add(book, fact_id, formatted, url, read)


def displayed_estimates(breakdown: Breakdown) -> list[tuple[str, Cited]]:
    """Rows the standing chart labels, skipping a leader who is the subject."""
    rows: list[tuple[str, Cited]] = []
    for index, standing in enumerate(breakdown.standing):
        seen = {breakdown.model.id}
        rows.append((f"standing[{index}].estimate", standing.estimate))
        for leader_index, leader in enumerate(standing.leaders):
            if leader.model in seen or leader.estimate is None:
                continue
            seen.add(leader.model)
            rows.append((f"standing[{index}].leaders[{leader_index}].estimate", leader.estimate))
    return rows


def _ticks(rows: Sequence[tuple[str, Cited]]) -> list[int]:
    if not rows:
        return []
    lo = min(cited.low or cited.value for _, cited in rows)
    hi = max(cited.high or cited.value for _, cited in rows)
    pad = (hi - lo) * 0.05 or 1.0
    lo, hi = lo - pad, hi + pad
    return list(range(math.ceil(lo), math.floor(hi) + 1))


def catalogue(breakdown: Breakdown) -> dict[str, Fact]:
    """Every fact a draft can print, keyed by id. Rendering chooses which."""
    book: dict[str, Fact] = {}
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
    rows = displayed_estimates(breakdown)
    for base, cited in rows:
        _add_cited(book, f"{base}.value", f"{cited.value:.2f}", breakdown, cited)
        if cited.low is None or cited.high is None:
            continue
        _add_cited(book, f"{base}.low", f"{cited.low:.2f}", breakdown, cited)
        _add_cited(book, f"{base}.high", f"{cited.high:.2f}", breakdown, cited)
    if rows:
        url, read = _locate(breakdown, rows[0][1])
        for tick in _ticks(rows):
            _add(book, f"standing.scale.{tick}", str(tick), url, read)
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
    return book


def fill(fact: Fact, chart: str) -> FilledSlot:
    return FilledSlot(fact.fact_id, fact.source_url, fact.read_date, fact.formatted, chart)


def claims_chart_slots(breakdown: Breakdown, book: dict[str, Fact]) -> list[FilledSlot]:
    slots: list[FilledSlot] = []
    for row in breakdown.claims_vs_evidence.claims:
        slots.append(fill(book[f"claims.{row.benchmark}.claim"], "claims"))
        for index, _reading in enumerate(row.readings):
            slots.append(fill(book[f"claims.{row.benchmark}.readings[{index}].value"], "claims"))
    return slots


def claims_chart_tokens(breakdown: Breakdown, book: dict[str, Fact]) -> list[str]:
    """Each claims-chart number is a bar title and a text label."""
    tokens: list[str] = []
    for slot in claims_chart_slots(breakdown, book):
        tokens.extend((slot.formatted, slot.formatted))
    return tokens


def standing_chart_slots(breakdown: Breakdown, book: dict[str, Fact]) -> list[FilledSlot]:
    slots: list[FilledSlot] = []
    for base, cited in displayed_estimates(breakdown):
        slots.append(fill(book[f"{base}.value"], "standing.chart"))
        if cited.low is None or cited.high is None:
            continue
        slots.append(fill(book[f"{base}.low"], "standing.chart"))
        slots.append(fill(book[f"{base}.high"], "standing.chart"))
    for tick in _ticks(displayed_estimates(breakdown)):
        slots.append(fill(book[f"standing.scale.{tick}"], "standing.chart"))
    return slots


def standing_chart_tokens(breakdown: Breakdown, book: dict[str, Fact]) -> list[str]:
    """Interval tips are drawn twice. Axis ticks are drawn once."""
    tokens: list[str] = []
    for base, cited in displayed_estimates(breakdown):
        shown = [book[f"{base}.value"].formatted]
        if cited.low is not None and cited.high is not None:
            shown.extend((book[f"{base}.low"].formatted, book[f"{base}.high"].formatted))
        tokens.extend(shown)
        tokens.extend(shown)
    for tick in _ticks(displayed_estimates(breakdown)):
        tokens.append(book[f"standing.scale.{tick}"].formatted)
    return tokens


def cost_chart_slots(breakdown: Breakdown, book: dict[str, Fact]) -> list[FilledSlot]:
    slots: list[FilledSlot] = []
    for index, offering in enumerate(breakdown.cost.offerings):
        if offering.task.basis != "contract_default" or offering.cost_per_task is None:
            continue
        slots.append(fill(book[f"cost.offerings[{index}].cost_per_task"], "cost.chart"))
    return slots


def cost_chart_tokens(breakdown: Breakdown, book: dict[str, Fact]) -> list[str]:
    tokens: list[str] = []
    for slot in cost_chart_slots(breakdown, book):
        tokens.extend((slot.formatted, slot.formatted))
    return tokens


def needs_unit_suffix(unit: str | None) -> bool:
    return unit not in _BARE_UNITS


def identity_strings(breakdown: Breakdown, post_url: str) -> list[str]:
    """Names, links, and dates. Not measurement tokens."""
    found: list[str] = []

    def add(text: str | None) -> None:
        if text and _cover(text) and text not in found:
            found.append(text)

    add(breakdown.model.name)
    add(breakdown.model.id)
    add(breakdown.headline.text)
    add(post_url)
    add(breakdown.disclosures.neutrality)
    add(breakdown.disclosures.supplier)
    add(breakdown.disclosures.early_access)
    add(SNAPSHOT_FILE.format(id=breakdown.generated_from.after.snapshot_id))
    for url in breakdown.sources.values():
        add(url)
    for name in breakdown.names.values():
        add(name)
    for row in breakdown.claims_vs_evidence.claims:
        add(row.benchmark)
        add(row.claim.read_date.isoformat())
        for reading in row.readings:
            add(reading.value.read_date.isoformat())
            if reading.difference is not None:
                add(reading.difference.read_date.isoformat())
    for item in breakdown.claims_vs_evidence.unreported:
        add(item.benchmark)
        add(item.reading.read_date.isoformat())
    for standing in breakdown.standing:
        add(standing.domain.name)
        lowered = standing.domain.name[:1].lower() + standing.domain.name[1:]
        add(lowered)
        add(standing.estimate.read_date.isoformat())
        for leader in standing.leaders:
            add(leader.model)
            add(breakdown.names.get(leader.model, leader.model))
            if leader.estimate is not None:
                add(leader.estimate.read_date.isoformat())
    for offering in breakdown.cost.offerings:
        add(offering.offering)
        add(offering.provider)
        add(offering.region)
        add(offering.tier)
        add(f"{offering.provider} · {offering.region} · {offering.tier}")
        if offering.cost_per_task is not None:
            add(offering.cost_per_task.read_date.isoformat())
    for cited in (breakdown.not_yet_measured.held_back or {}).values():
        add(cited.read_date.isoformat())
    return found


def audit(text: str, expected: Iterable[str], identity: Iterable[str], label: str) -> None:
    """Raise when claim text's numeric tokens are not ``expected``."""
    stripped = unescape(text)
    covers = sorted({item for item in identity if _cover(item)}, key=len, reverse=True)
    for item in covers:
        stripped = stripped.replace(item, " ")
    found = _TOKEN.findall(stripped)
    want = list(expected)
    if Counter(found) != Counter(want):
        extra = list((Counter(found) - Counter(want)).elements())[:8]
        missing = list((Counter(want) - Counter(found)).elements())[:8]
        raise ValueError(f"{label} digits are not the fact slots: extra {extra} missing {missing}")


def svg_claim_text(svg: str) -> str:
    """Text, titles, and aria-labels. Geometry and CSS are not claim text."""
    parts = _TEXT.findall(svg) + _TITLE.findall(svg) + _LABEL.findall(svg)
    return " ".join(unescape(part) for part in parts)


class _VisibleHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"style", "script", "metadata"}:
            self._skip += 1
        if self._skip:
            return
        for key, value in attrs:
            if key in {"alt", "aria-label", "title"} and value:
                self.parts.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"style", "script", "metadata"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip and data.strip():
            self.parts.append(data)

    def handle_comment(self, data: str) -> None:
        return


def html_claim_text(document: str) -> str:
    parser = _VisibleHTML()
    parser.feed(document)
    return " ".join(parser.parts)
