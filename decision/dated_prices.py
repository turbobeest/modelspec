"""Exact dated rows in the reviewed Gemini API and Vertex pricing layouts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from decision.normalise import Document, Locator, Node, select_region_tables

_DATE = r"([A-Z][a-z]+ [0-9]{1,2}, [0-9]{4})"
_PERIOD = re.compile(rf"(through|starting) {_DATE}", re.IGNORECASE)
_AMOUNT = r"\$([0-9]+(?:\.[0-9]+)?)"


@dataclass(frozen=True)
class DatedPrice:
    subject: str
    value: str
    effective_from: str | None = None
    effective_until: str | None = None

    @property
    def conditions(self) -> dict[str, str | None]:
        return {"effective_from": self.effective_from, "effective_until": self.effective_until}


def _text(node: Node) -> str:
    return " ".join(
        " ".join(
            child if isinstance(child, str) else _text(child) for child in node.children
        ).split()
    )


def _period(phrase: str) -> dict[str, str | None] | None:
    match = _PERIOD.fullmatch(phrase)
    if match is None:
        return None
    try:
        day = datetime.strptime(match[2], "%B %d, %Y").date().isoformat()
    except ValueError:
        return None
    return {
        "effective_from": day if match[1].casefold() == "starting" else None,
        "effective_until": day if match[1].casefold() == "through" else None,
    }


def _rows(table: Node) -> list[list[str]]:
    if any(node.tag == "table" for node in table.elements()):
        return []
    rows = []
    for row in table.elements():
        if row.tag != "tr":
            continue
        cells = [c for c in row.children if isinstance(c, Node) and c.tag in {"td", "th"}]
        if any(
            c.attrs.get("rowspan", "1") != "1" or c.attrs.get("colspan", "1") != "1" for c in cells
        ):
            return []
        rows.append([_text(c) for c in cells])
    return rows


def _gemini(
    doc: Document, tables: list[Node], names: tuple[str, ...], subject: str, facet: str
) -> list[DatedPrice]:
    parts = subject.split("/")
    if len(parts) != 5 or parts[0] != "google-gemini-api" or parts[3:] != ["global", "standard"]:
        return []
    kind = facet.removeprefix("offering.price.")
    tier = "Batch" if kind.startswith("batch_") else "Standard"
    label = {
        "input": "Input price",
        "output": "Output price (including thinking tokens)",
        "cached_input": "Context caching price",
        "batch_input": "Input price",
        "batch_output": "Output price (including thinking tokens)",
    }.get(kind)
    if label is None or doc.root is None:
        return []
    owned = []
    table_ids = {id(table) for table in tables}
    for wrapper in doc.root.elements():
        if wrapper.tag != "div" or "models-section" not in wrapper.classes:
            continue
        headings = [n for n in wrapper.elements() if n.tag == "h2"]
        if len(headings) != 1 or _text(headings[0]) not in names:
            continue
        # This template declares the model in a sibling models-section and its
        # tiers in the next devsite-selector. A new model declaration ends it.
        parent = wrapper.parent
        if parent is None:
            continue
        siblings = [n for n in parent.children if isinstance(n, Node)]
        for sibling in siblings[siblings.index(wrapper) + 1 :]:
            if any(n.tag == "h2" for n in [sibling, *sibling.elements()]):
                break
            selectors = [n for n in [sibling, *sibling.elements()] if n.tag == "devsite-selector"]
            tier_nodes = {id(n) for selector in selectors for n in selector.elements()}
            if any(
                n.tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and id(n) not in tier_nodes
                for n in [sibling, *sibling.elements()]
            ):
                break
            for selector in selectors:
                for section in selector.children:
                    if not isinstance(section, Node) or section.tag != "section":
                        continue
                    hs = [n for n in section.children if isinstance(n, Node) and n.tag == "h3"]
                    ts = [n for n in section.children if isinstance(n, Node) and n.tag == "table"]
                    if (
                        len(hs) == 1
                        and _text(hs[0]) == tier
                        and len(ts) == 1
                        and id(ts[0]) in table_ids
                    ):
                        owned.append((_text(headings[0]), ts[0]))
    if len(owned) != 1:
        return []
    name, table = owned[0]
    rows = _rows(table)
    if not rows or rows[0] != ["", "Free Tier", "Paid Tier, per 1M tokens in USD"]:
        return []
    matches = [row for row in rows[1:] if len(row) == 3 and row[0] == label]
    if len(matches) != 1:
        return []
    cell = matches[0][2]
    if kind == "cached_input":
        cell = cell.removesuffix(" Implicit caching only (explicit caching is not supported).")
    # Every amount in this cell must carry its own exact date phrase. Storage
    # fees and other units are deliberately unsupported, never guessed.
    entry = rf"{_AMOUNT} ((?:through|starting) {_DATE})\."
    matches = list(re.finditer(entry, cell))
    if not matches or " ".join(m.group(0) for m in matches) != cell:
        return []
    readings = []
    for match in matches:
        period = _period(match[2])
        if period is None:
            return []
        readings.append(DatedPrice(name, match[1], **period))
    return readings


def _vertex(
    tables: list[Node], names: tuple[str, ...], subject: str, facet: str
) -> list[DatedPrice]:
    parts = subject.split("/")
    if len(parts) != 5 or parts[0] != "google-vertex-ai" or parts[3:] != ["global", "standard"]:
        return []
    kind = facet.removeprefix("offering.price.")
    batch = kind.startswith("batch_")
    suffix = " with Flex/Batch" if batch else ""
    headers = [
        "Model",
        "Type",
        "Region",
        *[
            "Price (/1M tokens) " + band + suffix
            for band in (
                "<= 200K input tokens",
                "> 200K input tokens",
                "<= 200K cached input tokens",
                "> 200K cached input tokens",
            )
        ],
    ]
    eligible = [rows for table in tables if (rows := _rows(table)) and rows[0] == headers]
    if len(eligible) != 1:
        return []
    readings = []
    owner = None
    period = None
    for row in eligible[0][1:]:
        if len(row) != len(headers):
            owner, period = None, None
            continue
        if row[0]:
            owner, period = None, None
            match = re.fullmatch(
                rf"(.+?)\s*\*?\s+((?:through|starting) {_DATE})", row[0], re.IGNORECASE
            )
            if match and match[1].rstrip(" *") in names:
                owner, period = match[1].rstrip(" *"), _period(match[2])
        if owner is None or period is None or row[2] != "Global":
            continue
        wanted = (
            "Text output (response and reasoning)"
            if kind.endswith("output")
            else "Input (text, image, video, audio)"
        )
        if row[1] != wanted:
            continue
        column = 5 if kind == "cached_input" else 3
        amount = re.fullmatch(_AMOUNT, row[column])
        if amount:
            readings.append(DatedPrice(owner, amount[1], **period))
    return readings


def read_dated_prices(
    doc: Document, locator: Locator, *, names: tuple[str, ...], subject: str, facet: str, url: str
) -> list[DatedPrice]:
    """Read supported primary tables contained in the exact cited region."""
    if doc.root is None:
        return []
    tables = select_region_tables(doc, locator)
    if url == "https://ai.google.dev/gemini-api/docs/pricing":
        return _gemini(doc, tables, names, subject, facet)
    if url in {
        "https://cloud.google.com/vertex-ai/generative-ai/pricing",
        "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing",
    }:
        return _vertex(tables, names, subject, facet)
    return []
