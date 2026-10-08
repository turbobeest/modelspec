"""Two-key verification and quarantine (MODEL-140; design §5, "Two keys").

The agent that collects a value never verifies it. A verifier re-reads the
value from the cited region of the retained source copy, with its own
extractor, and compares:

- the **model identity** in the region is the subject, not a sibling variant
  ("GPT-6 Sol" is not "GPT-6 Astra"; "Nimbus 3 (max effort)" is Nimbus 3 at
  max effort, never at default);
- the **value** agrees after unit normalisation, within ``TOLERANCE_RULE``;
- the **unit** is the one the collector filed;
- the **conditions** (effort, harness, date) are the ones the source states.

Extractors are pluggable. The deterministic ones (``TableExtractor``,
``KeyValueExtractor``) always run before any other; ``LLMExtractor`` reads
prose through an injected completion function, so nothing here calls a model
or the network on its own: ``claude_extractor`` (Claude Sonnet, via the Claude
CLI) and ``mistral_extractor`` (Mistral Large, via ollama) are the two wired
readers. ``LicenceExtractor`` reads a ``licence.*`` claim through that same
completion function, and only from a source kind the facet permits. Other
cited regions are binding pages, not readings. Deterministic extractors
still read a ``licence_text`` source for every other claim. An absence
verifies only from a source kind the facet permits; a ``licence.*`` absence
needs that kind explicitly. Each extractor's actor (agent, model family,
method) is the verifier the log records. Two keys means another model family
(MODEL-159): a reader from the collector's family is never asked, and a
same-family ``verified`` already in the log does not count
(``Verification.counts``).

Outcomes are ``verified``, ``mismatch`` (with a structured diff) and
``unreachable`` (the copy, source or region is missing). A claim no
independent extractor could read is ``skipped``: nothing is logged and it
stays queued. Anything whose latest logged outcome is not ``verified``, and
anything never verified, is **quarantined**.

Files, under ``verification/`` at the repository root:

- ``log.jsonl``: the verification log, append-only, one
  ``decision.model.Verification`` per line. The latest counting outcome per
  target and checked value wins: latest ``date``, and on a tie the later line
  (the rule ``decision.snapshot`` applies when it reads
  ``verification/log.jsonl``).
- ``queue/events.jsonl``: append-only work queue. A collector files a claim
  (``collected``), change detection re-queues one (``changed``), a run records
  what it checked (``checked``). Mismatched and unreachable targets stay listed
  by ``Queue.recrawl_requests`` until a collector files them again.

Refs from ``decision.sources`` (``Citation.ref``, ``RecheckReport.requeue``)
are ``"fact:<id>"`` or ``"evidence:<id>"``.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import subprocess
import urllib.request
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from decimal import Decimal
from functools import cache
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import JsonValue, ValidationError

from decision.licence_rules import licence_reading_rule
from decision.model import (
    DETERMINISTIC,
    SourceRef,
    TargetRef,
    Verification,
    VerificationActor,
    VerificationTarget,
    evidence_verification_value,
    value_hash,
)
from decision.normalise import (
    NORMALISERS,
    Locator,
    UnsupportedContentError,
    normalise_document,
    select_region,
)
from decision.registry import UNREGISTERED
from decision.registry import default as default_registry
from decision.sources import CopyStore, RecheckReport, Source, load_sources
from decision.units import UNITS, _MAGNITUDE, unit_id
from schema import private_errors

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIRECTORY = REPO_ROOT / "verification"

Outcome = Literal["verified", "mismatch", "unreachable", "skipped"]
CONDITION_KEYS = ("effort", "harness", "date")

# --- claims --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Claim:
    """One value as a collector filed it, with what the verifier needs to re-read it.

    ``names`` are the names the subject is published under, taken from the
    catalogue, never from the collector's own label for the row: that label is
    what a copied-score error gets wrong. ``label`` is the column or key the value
    sits under in the source (default: ``field`` with underscores as spaces).
    ``unit`` is a unit ID (``UNITS``); ``None`` means the base unit of whatever
    dimension the source states. ``conditions`` holds ``effort``, ``harness`` and
    ``date`` as the collector filed them.
    """

    target: TargetRef
    subject: str
    names: tuple[str, ...]
    field: str
    value: JsonValue
    collector: VerificationActor
    sources: tuple[SourceRef, ...]
    unit: str | None = None
    label: str | None = None
    conditions: Mapping[str, str | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.names:
            raise ValueError(f"{self.target.id}: a claim needs the subject's published names")
        if not self.sources:
            raise ValueError(f"{self.target.id}: a claim needs at least one source")
        unknown = set(self.conditions) - set(CONDITION_KEYS)
        if unknown:
            raise ValueError(f"{self.target.id}: unknown conditions {sorted(unknown)}")

    @classmethod
    def from_evidence(cls, evidence: Any, *, names: Sequence[str],
                      collector: VerificationActor, label: str | None = None) -> Claim:
        """A claim for a ``decision.model.Evidence`` row with an ID, subject and sources."""
        if evidence.id is None or evidence.subject is None:
            raise ValueError("evidence needs an ID and a subject to be verified")
        return cls(
            target=TargetRef(kind="evidence", id=evidence.id),
            subject=evidence.subject.id,
            names=tuple(names),
            field=evidence.benchmark_id,
            label=label,
            value=evidence_verification_value(evidence),
            unit=evidence.unit,
            conditions={"effort": evidence.effort, "harness": evidence.harness,
                        "date": evidence.evidence_date},
            collector=collector,
            sources=tuple(evidence.sources),
        )

    @classmethod
    def from_fact(cls, fact: Any, *, names: Sequence[str], collector: VerificationActor,
                  unit: str | None = None, label: str | None = None) -> Claim:
        """A claim for a filed ``Fact``; ``unit`` is its facet's unit.

        A scoped source region can also confirm ``not_disclosed`` or
        ``requires_contract`` by naming the subject while omitting the facet.
        ``unknown`` is not a filed value and cannot be verified.
        """
        if fact.state == "unknown":
            raise ValueError(f"{fact.id}: an unknown fact has no value to verify")
        return cls(
            target=TargetRef(kind="fact", id=fact.id),
            subject=fact.subject.id,
            names=tuple(names),
            field=fact.facet,
            label=label,
            value=fact.value,
            unit=unit,
            collector=collector,
            sources=tuple(fact.sources),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target.model_dump(),
            "subject": self.subject,
            "names": list(self.names),
            "field": self.field,
            "label": self.label,
            "value": self.value,
            "unit": self.unit,
            "conditions": dict(self.conditions),
            "collector": self.collector.model_dump(),
            "sources": [s.model_dump() for s in self.sources],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Claim:
        return cls(
            target=TargetRef.model_validate(data["target"]),
            subject=data["subject"],
            names=tuple(data["names"]),
            field=data["field"],
            label=data.get("label"),
            value=data["value"],
            unit=data.get("unit"),
            conditions=data.get("conditions") or {},
            collector=VerificationActor.model_validate(data["collector"]),
            sources=tuple(SourceRef.model_validate(s) for s in data["sources"]),
        )


def target_ref(ref: str | TargetRef) -> TargetRef:
    """``"fact:<id>"`` or ``"evidence:<id>"`` as a ``TargetRef``."""
    if isinstance(ref, TargetRef):
        return ref
    kind, sep, id_ = ref.partition(":")
    if not sep or kind not in ("fact", "evidence") or not id_:
        raise ValueError(f"not a verification ref (fact:<id> or evidence:<id>): {ref!r}")
    return TargetRef(kind=kind, id=id_)


def _key(target: TargetRef) -> tuple[str, str]:
    return (target.kind, target.id)


# --- units and numbers ---------------------------------------------------------------------------



@dataclass(frozen=True)
class Quantity:
    number: int | float
    unit: str | None
    #: Decimal places as written: the precision the rounding tolerance uses.
    decimals: int
    #: The number as the source wrote it.
    text: str

    def show(self) -> str:
        return f"{self.text} {self.unit}" if self.unit else self.text


_NUMBER = re.compile(
    r"^\s*(?P<cur>\$|usd\s)?\s*(?P<num>[-+]?\d[\d,]*(?:\.\d+)?)\s*(?P<rest>.*?)\s*$",
    re.IGNORECASE,
)


def parse_quantity(text: str | None, hint: str | None = None) -> Quantity | None:
    """A number and its unit from a cell ("71.2%", "400K tokens", "$2.50 / 1M tokens").

    ``hint`` is the unit a column header states; a bare magnitude ("400K") scales it.
    """
    if text is None:
        return None
    text = text.replace(r"\$", "$")
    text = re.sub(r"(?i)^\s*(?:up to|about|approximately)\s+", "", text)
    m = _NUMBER.match(text)
    if not m:
        return None
    raw = m.group("num").replace(",", "")
    number: int | float = float(raw) if "." in raw else int(raw)
    decimals = len(raw.partition(".")[2])
    rest = m.group("rest")
    if m.group("cur"):
        hinted = unit_id(hint)
        if not rest and hinted and hinted.startswith("usd_per_"):
            spelled = hinted
        elif not rest and hinted in {"k_tokens", "m_tokens"}:
            magnitude = "1k" if hinted == "k_tokens" else "1m"
            spelled = f"usd/{magnitude} tokens"
        else:
            spelled = "usd" + rest
    elif not rest:
        spelled = hint
    elif rest.casefold() in _MAGNITUDE and hint:
        spelled = f"{rest} {hint}"
    else:
        spelled = rest
    return Quantity(number, unit_id(spelled), decimals, m.group("num"))


def _decimals(value: int | float) -> int:
    if isinstance(value, int):
        return 0
    exponent = Decimal(repr(value)).as_tuple().exponent
    return max(0, -exponent) if isinstance(exponent, int) else 0


TOLERANCE_RULE = (
    "Both values are converted to the base unit of their dimension. They agree when "
    "|claimed - found| <= 0.5 * max(ulp_claimed, ulp_found) + 1e-9 * max(|claimed|, |found|), "
    "where a value's ulp is one unit in its last written decimal place, in the base unit: "
    "a value rounded to the other's precision agrees, and nothing else does."
)


def numbers_agree(claimed: int | float, claimed_unit: str | None, found: Quantity) -> bool:
    """Whether ``claimed`` (in ``claimed_unit``) agrees with ``found``; see ``TOLERANCE_RULE``."""
    found_dim, found_factor = UNITS.get(found.unit or "", (found.unit, 1.0))
    claimed_unit = unit_id(claimed_unit)
    if claimed_unit is None:
        claimed_dim, claimed_factor = found_dim, 1.0
    else:
        claimed_dim, claimed_factor = UNITS.get(claimed_unit, (claimed_unit, 1.0))
    if claimed_dim != found_dim:
        return False
    a, b = claimed * claimed_factor, found.number * found_factor
    ulp = max(10.0 ** -_decimals(claimed) * claimed_factor, 10.0 ** -found.decimals * found_factor)
    return abs(a - b) <= 0.5 * ulp + 1e-9 * max(abs(a), abs(b))


# --- identity and conditions ---------------------------------------------------------------------

EFFORT_LEVELS = frozenset(
    {"minimal", "low", "medium", "high", "xhigh", "max", "maximum", "default"})
_EFFORT_ALIASES = {"maximum": "max", "standard": "default"}
_QUALIFIER = re.compile(r"[\(\[]([^\)\]]*)[\)\]]")
_EFFORT_QUALIFIER = re.compile(
    r"^(?:(?:(?:reasoning|thinking)\s+)?effort\s*[:=]?\s*)?(\w+)"
    r"(?:\s+(?:(?:reasoning|thinking)\s+)?effort)?$")
#: A level named inside a longer phrase: "adaptive thinking at max effort".
_EFFORT_IN_PHRASE = re.compile(r"\b(\w+)\s+(?:(?:reasoning|thinking)\s+)?effort\b")
#: A phrase with a negation in it ("without adaptive thinking at max effort")
#: names no level: which words it negates is not decided here.
_NEGATION = re.compile(
    r"\b(no|not|without|non|never|except|excluding|unlike|rather than|instead of|other than)\b")


def normalise_name(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", " ", name.casefold()).strip()


def split_model_cell(cell: str) -> tuple[str, str | None]:
    """A model cell as (normalised identity, effort named in it, or ``None``).

    Only an effort qualifier is split off: "GPT-6 Sol (max effort)" is GPT-6 Sol at
    max effort, but "GPT-6 Sol (thinking)" stays a different identity.
    """
    effort = None

    def take(m: re.Match[str]) -> str:
        nonlocal effort
        q = _EFFORT_QUALIFIER.match(m.group(1).strip().casefold())
        if q and q.group(1) in EFFORT_LEVELS:
            effort = _EFFORT_ALIASES.get(q.group(1), q.group(1))
            return " "
        return m.group(0)

    return normalise_name(_QUALIFIER.sub(take, cell)), effort


def _effort_levels_in(text: str) -> set[str]:
    """The effort levels ``text`` names as an effort: "max effort", "high reasoning effort"."""
    text = text.casefold()
    if _NEGATION.search(text):
        return set()
    return {_EFFORT_ALIASES.get(level, level)
            for level in _EFFORT_IN_PHRASE.findall(text) if level in EFFORT_LEVELS}


def _condition(key: str, value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    s = str(value).strip().casefold()
    if key == "effort":
        # "max effort", "maximum thinking effort": the level, as a table cell would give it.
        q = _EFFORT_QUALIFIER.match(s)
        if q and q.group(1) in EFFORT_LEVELS:
            s = q.group(1)
        else:
            # A caption's phrase names one level; a phrase naming two stays as written.
            named = _effort_levels_in(s)
            if len(named) == 1:
                s = named.pop()
        return _EFFORT_ALIASES.get(s, s)
    if key == "date":
        parsed = _parse_date(str(value).strip())
        return parsed.isoformat() if parsed else s
    return s


_DATE_FORMATS = ("%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%Y/%m/%d")


def _parse_date(text: str) -> date | None:
    try:
        return date.fromisoformat(text)
    except ValueError:
        pass
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


# --- extractors ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class Reading:
    """One value an extractor found in a region, as written there."""

    subject: str | None
    value: JsonValue
    unit: str | None = None
    conditions: Mapping[str, str | None] = field(default_factory=dict)


class ExtractorError(Exception):
    """The extractor could not read the region: not evidence that a value is absent."""


class Extractor(Protocol):
    """Reads values from a cited region. ``actor`` is the verifier the log records."""

    actor: VerificationActor

    def accepts(self, text: str) -> bool: ...

    def extract(self, claim: Claim, text: str) -> list[Reading]: ...


VERIFY_AGENT = "modelspec-verify"


def _label(claim: Claim) -> str:
    return normalise_name(claim.label or claim.field.replace("_", " "))


_SUBJECT_HEADER = re.compile(r"^(model|model name|name|system|submission)$")
_EFFORT_HEADER = re.compile(r"\b(effort|reasoning|setting|mode)\b")
_HARNESS_HEADER = re.compile(r"\b(harness|scaffold|agent)\b")
_DATE_HEADER = re.compile(r"^(date|as of|evaluated|submitted|updated|last updated)")
_VALUE_HEADER = re.compile(r"score|accuracy|result|value|pass 1|resolved")
_HEADER_UNIT = re.compile(r"^(.*?)\s*\(([^)]*)\)\s*$")


class TableExtractor:
    """Tables as ``decision.normalise`` renders them: one row per line, cells joined by
    ``" | "``. The header must name a model column; the value column is the one whose
    header is the claim's label, else the only generic score column."""

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="table-header-match@1")

    @staticmethod
    def _rows(text: str) -> tuple[list[str], list[list[str]]] | None:
        lines = [[c.strip() for c in re.split(r" ?\| ?", line)] for line in text.splitlines()]
        for i, cells in enumerate(lines):
            headers = [normalise_name(_HEADER_UNIT.sub(r"\1", c)) for c in cells]
            if len(cells) >= 2 and any(_SUBJECT_HEADER.match(h) for h in headers):
                rows = [row for row in lines[i + 1:] if len(row) == len(cells)]
                return cells, rows
        return None

    def accepts(self, text: str) -> bool:
        return self._rows(text) is not None

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        parsed = self._rows(text)
        if parsed is None:
            raise ExtractorError("no table with a model column")
        header, rows = parsed
        bases, units = [], []
        for cell in header:
            m = _HEADER_UNIT.match(cell)
            bases.append(normalise_name(m.group(1) if m else cell))
            units.append(m.group(2) if m else None)

        def column(pattern: re.Pattern[str]) -> int | None:
            return next((i for i, h in enumerate(bases) if pattern.search(h)), None)

        subject = column(_SUBJECT_HEADER)
        conditions = {"effort": column(_EFFORT_HEADER), "harness": column(_HARNESS_HEADER),
                      "date": column(_DATE_HEADER)}
        label = _label(claim)
        value = next((i for i, h in enumerate(bases) if h == label), None)
        if value is None:
            generic = [i for i, h in enumerate(bases) if _VALUE_HEADER.search(h)]
            if len(generic) != 1:
                raise ExtractorError(f"no single value column for {label!r} in {header}")
            value = generic[0]
        return [
            Reading(
                subject=row[subject] or None,
                value=row[value] or None,
                unit=units[value],
                conditions={k: (row[i] or None) if i is not None else None
                            for k, i in conditions.items()},
            )
            for row in rows
        ]


class TransposedTableExtractor:
    """Read benchmark rows under exact model-name column headers."""

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="transposed-table-label-match@1")

    def accepts(self, text: str) -> bool:
        return any(line.startswith("| ") for line in text.splitlines())

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        rows = [[cell.strip() for cell in re.split(r" ?\| ?", line)]
                for line in text.splitlines()]
        names = {normalise_name(name): name for name in claim.names}
        readings = []
        for i, header in enumerate(rows):
            if len(header) < 2 or header[0]:
                continue
            columns = [(j, names[normalise_name(cell)]) for j, cell in enumerate(header)
                       if j and normalise_name(cell) in names]
            for row in rows[i + 1:]:
                if len(row) != len(header):
                    break
                if normalise_name(row[0]) != _label(claim):
                    continue
                readings.extend(Reading(subject=name, value=row[j] or None)
                                for j, name in columns)
        return readings


class OfferingPriceExtractor:
    """Read provider pricing tables whose rows or cells carry price labels."""

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="offering-price-table@1")

    def accepts(self, text: str) -> bool:
        return " | " in text and bool(re.search(r"(?i)\b(price|pricing|input|output)\b", text))

    @staticmethod
    def _wanted(field: str) -> str:
        return field.removeprefix("offering.price.")

    @staticmethod
    def _cell_value(cell: str, wanted: str) -> str | None:
        labels = {
            "input": "Input",
            "output": "Output",
            "cached_input": "Cached Input",
            "batch_input": "Input",
            "batch_output": "Output",
        }
        pattern = re.compile(
            rf"(?i)(?<!cached )\b{re.escape(labels[wanted])}\s*:\s*"
            r"(\\?\$\s*[0-9]+(?:\.[0-9]+)?)"
        )
        if wanted == "cached_input":
            pattern = re.compile(r"(?i)\bCached Input\s*:\s*(\\?\$\s*[0-9]+(?:\.[0-9]+)?)")
        match = pattern.search(cell)
        return match.group(1) if match else None

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        wanted = self._wanted(claim.field)
        if wanted == claim.field:
            raise ExtractorError("not an offering price")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        scoped_subject = next((name for name in claim.names
                               if normalise_name(name) in normalise_name(text)), None)
        simple_label = {"input": "input", "output": "output",
                        "cached_input": "cached input"}.get(wanted)
        if scoped_subject and simple_label:
            markdown = False
            for i, line in enumerate(lines):
                if "|" in line and (i == 0 or "|" not in lines[i - 1]):
                    markdown = line.startswith("|")  # the table's header row
                # In an HTML table a leading pipe is an empty first cell: the row
                # continues the model named above it (Vertex), so it is not this
                # page's own price (MODEL-235). Markdown rows all start with one.
                if line.startswith("|") and not markdown:
                    continue
                cells = [cell.strip() for cell in line.strip("| ").split("|")]
                if len(cells) >= 2 and normalise_name(cells[0]) == simple_label:
                    if match := re.search(r"\\?\$\s*[0-9]+(?:\.[0-9]+)?", cells[1]):
                        return [Reading(scoped_subject, match.group(0), claim.unit)]
        if scoped_subject and "price per btok per mtok" in normalise_name(text):
            if wanted == "input":
                match = re.search(r"(?im)^\|?\s*Price \(per Btok / per Mtok\).*?"
                                  r"\\?\$[0-9.]+\s*/\s*(\\?\$[0-9.]+)", text)
                if match:
                    return [Reading(scoped_subject, match.group(1), claim.unit)]
            if wanted == "output" and "output tokens are free" in text.casefold():
                return [Reading(scoped_subject, "0", claim.unit)]
        if scoped_subject and wanted == "cached_input":
            name = re.escape(scoped_subject)
            # The name must end there: "Claude Opus 5" is not "Claude Opus 5.5".
            pattern = (rf"(?is){name}(?![\w.]).{{0,160}}?"
                       r"\((\\?\$[0-9.]+)\s+USD per million tokens\)")
            match = re.search(pattern, text)
            if match:
                return [Reading(scoped_subject, match.group(1), claim.unit)]
        named_readings: list[Reading] = []
        label = {
            "input": "input price", "output": "output price",
            "cached_input": "context caching price",
            "batch_input": "input price", "batch_output": "output price",
        }[wanted]
        desired_mode = "batch" if wanted.startswith("batch_") else "standard"
        for published in claim.names:
            start = next((i for i, line in enumerate(lines)
                          if normalise_name(line) == normalise_name(published)), None)
            if start is None:
                continue
            mode = None
            for line in lines[start + 1:]:
                normal = normalise_name(line)
                if normal.startswith("gemini ") and "-" not in line \
                        and normal != normalise_name(published):
                    break
                if normal in {"standard", "batch", "flex", "priority"}:
                    mode = normal
                    continue
                if mode == desired_mode and normal.startswith(label):
                    if match := re.search(r"\\?\$\s*[0-9]+(?:\.[0-9]+)?", line):
                        named_readings.append(Reading(published, match.group(0), claim.unit))
                        break
        if named_readings:
            return named_readings
        rows = [[part.strip() for part in re.split(r" ?\| ?", line)]
                for line in text.splitlines() if "|" in line]
        if len(rows) < 2:
            raise ExtractorError("no pricing table")
        headers = [normalise_name(cell) for cell in rows[0]]
        names = [normalise_name(name) for name in claim.names]
        # A band-tiered table lists the token range beside the amount. The range
        # header contains "input tokens", so the column-header scan below would
        # read the range. The price column is the amount. The model's first row
        # is the lowest band, which is the base price (registry/facets.yaml).
        band_table = any(_TOKEN_BAND.search(cell) for row in rows for cell in row)
        price_col = _band_price_column(headers, wanted) if band_table else None
        current_subject: str | None = None
        readings: list[Reading] = []

        for row in rows[1:]:
            if len(row) != len(headers):
                continue
            if row[0]:
                current_subject = row[0]
            subject = current_subject
            matched_name = next((claim.names[i] for i, name in enumerate(names)
                                 if subject and name in normalise_name(subject)), None)
            if matched_name is None:
                continue
            subject = matched_name

            # Azure-style cells contain several labelled prices. Batch prices
            # live in the column whose header names the Batch API.
            columns = range(len(row))
            if wanted.startswith("batch_"):
                columns = [i for i, header in enumerate(headers) if "batch" in header]
            else:
                columns = [i for i, header in enumerate(headers) if "batch" not in header]
            for i in columns:
                if value := self._cell_value(row[i], wanted):
                    readings.append(Reading(subject, value, claim.unit))

            # Vertex-style continuation rows put the price kind in Type and
            # the value in the first price column.
            type_i = next((i for i, header in enumerate(headers) if header == "type"), None)
            if type_i is not None:
                kind = normalise_name(row[type_i])
                batch_table = any("batch" in header or "flex" in header for header in headers)
                has_cache_hit = any(
                    len(other) == len(headers) and normalise_name(other[type_i]) == "cache hit"
                    for other in rows[1:]
                )
                expected = {
                    "input": "input", "output": "output",
                    "cached_input": "cache hit" if has_cache_hit else "input",
                    "batch_input": "input" if batch_table else "batch input",
                    "batch_output": "output" if batch_table else "batch output",
                }[wanted]
                matches = (
                    kind.startswith(expected)
                    or (wanted.endswith("output") and "output" in kind)
                )
                if matches:
                    price_columns = [i for i, header in enumerate(headers)
                                     if "price" in header and i != type_i]
                    if wanted == "cached_input":
                        cached = [i for i in price_columns if "cached" in headers[i]]
                        price_columns = cached or price_columns
                    elif price_columns:
                        uncached = [i for i in price_columns if "cached" not in headers[i]]
                        price_columns = uncached or price_columns
                    value = next(
                        (row[i] for i in price_columns if row[i] and row[i] != "N/A"),
                        None,
                    )
                    if value:
                        readings.append(Reading(subject, value, claim.unit))

            # AWS-style tables encode each price kind in its column header.
            # On a band-tiered table that scan hits the range column first.
            if type_i is None and price_col is not None:
                value = row[price_col]
                if value and _PRICE_CELL.search(value):
                    readings.append(Reading(subject, value, claim.unit))
            elif type_i is None:
                terms = {
                    "input": ("input tokens",),
                    "output": ("output tokens",),
                    "cached_input": ("cache read",),
                    "batch_input": ("input tokens batch", "input tokens (batch"),
                    "batch_output": ("output tokens batch", "output tokens (batch"),
                }[wanted]
                for i, header in enumerate(headers):
                    flat = header.replace("price per 1m ", "")
                    if any(term.replace(" ", "") in flat.replace(" ", "") for term in terms):
                        if wanted in {"input", "output"} and "batch" in header:
                            continue
                        readings.append(Reading(subject, row[i], claim.unit))
                        break
        return readings or _grouped_header_tables(claim, text, wanted)


#: A price cell: a dollar amount, however the unit after it is written.
_PRICE_CELL = re.compile(r"\\?\$\s*[0-9]+(?:\.[0-9]+)?")
#: A token-range cell on a band-tiered price table, such as "0<Token≤1M".
_TOKEN_BAND = re.compile(r"(?i)<\s*tokens?\s*[≤<]")


def _band_price_column(headers: list[str], wanted: str) -> int | None:
    """The price column of a band-tiered table, or None when this table has none.

    The amount header names the kind and the word "price" ("Input price (per 1
    million tokens)"). The range header ("Input tokens per request") does not.
    """
    if wanted.endswith("output"):
        kind = "output"
    elif wanted.endswith("input"):
        kind = "input"
    else:
        return None
    batch = wanted.startswith("batch_")
    cached = "cached" in wanted
    for index, header in enumerate(headers):
        if "price" not in header or kind not in header:
            continue
        if ("batch" in header) != batch:
            continue
        if cached != ("cache" in header):
            continue
        if kind == "input" and "output" in header:
            continue
        return index
    return None


def _grouped_header_tables(claim: Claim, text: str, wanted: str) -> list[Reading]:
    """Prices from tables with a grouped two-row header (MODEL-235).

    Anthropic's pricing tables put column groups ("Model | Base tokens | Prompt
    caching", "Model | Batch tokens") above the column names ("Name | Input |
    Output | … | Hits and refreshes"), and each row's first cell is the model's
    name, sometimes followed by a description. Each table is read on its own: a
    group row naming batch makes it the batch table. A row is the subject's only
    when its first cell starts with one of the subject's names and the name is
    not followed by a digit or a dot, so "Claude Sonnet 5" never reads the
    "Claude Sonnet 5.5" row.
    """
    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    lines = text.splitlines()
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for i, line in enumerate(lines):
        if "|" in line:
            current.append(cells(line))
            continue
        # A one-cell row ("Additional models") labels a section of the same table:
        # the rows after it are as wide as the rows before it.
        after = lines[i + 1] if i + 1 < len(lines) else ""
        if len(current) > 2 and line.strip() and "|" in after \
                and len(cells(after)) == len(current[-1]):
            continue
        if current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)

    column = {"input": "input", "output": "output", "cached_input": "hits",
              "batch_input": "input", "batch_output": "output"}[wanted]
    readings: list[Reading] = []
    for rows in tables:
        if len(rows) < 3 or len(rows[1]) <= len(rows[0]) \
                or normalise_name(rows[1][0]) not in {"name", "model"}:
            continue
        batch = any("batch" in normalise_name(cell) for cell in rows[0])
        if batch != wanted.startswith("batch_"):
            continue
        headers = [normalise_name(cell) for cell in rows[1]]
        if column == "hits":
            index = next((i for i, h in enumerate(headers)
                          if any(word in {"hit", "hits"} for word in h.split())), None)
        else:
            index = next((i for i, h in enumerate(headers) if h == column), None)
        if index is None:
            continue
        for row in rows[2:]:
            if len(row) != len(headers):
                continue
            name = next((n for n in claim.names
                         if re.match(rf"(?i){re.escape(n)}(?![\w.])", row[0])), None)
            if name and (match := _PRICE_CELL.search(row[index])):
                readings.append(Reading(name, match.group(0), claim.unit))
    return readings


_KEY_VALUE = re.compile(r"^([^:|]{1,60}?)\s*:\s+(.+)$")
_SUBJECT_KEYS = frozenset({"model", "model name", "name"})
_DATE_KEYS = frozenset({"date", "as of", "evaluated", "updated", "last updated"})


class KeyValueExtractor:
    """``Key: value`` lists about one subject, which the region names under a ``Model``
    (or ``Name``) key. Returns one reading; its value is ``None`` when the key is absent."""

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="key-value-match@1")

    @staticmethod
    def _pairs(text: str) -> dict[str, str]:
        pairs: dict[str, str] = {}
        for line in text.splitlines():
            if m := _KEY_VALUE.match(line.strip()):
                pairs.setdefault(normalise_name(m.group(1)), m.group(2).strip())
        return pairs

    def accepts(self, text: str) -> bool:
        return len(self._pairs(text)) >= 2

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        pairs = self._pairs(text)
        subject = next((v for k, v in pairs.items() if k in _SUBJECT_KEYS), None)
        if subject is None:
            subject = next((
                name
                for name in claim.names
                if normalise_name(name) in normalise_name(text)
            ), None)
        date_ = next((v for k, v in pairs.items() if k in _DATE_KEYS), None)
        return [Reading(subject=subject, value=pairs.get(_label(claim)),
                        conditions={"effort": pairs.get("effort"),
                                    "harness": pairs.get("harness"), "date": date_})]


class GovernanceProseExtractor:
    """Read explicit provider-wide governance statements with fixed phrase rules."""

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="governance-prose@1")

    def accepts(self, text: str) -> bool:
        corpus = text.casefold()
        return any(term in corpus for term in ("train", "retention", "retained", "stored",
                                                "soc 2", "business associate agreement", "baa"))

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        corpus = text.casefold()
        subject = claim.names[0]
        if claim.field == "offering.data.trains_on_customer_data":
            phrases = ("does not use your prompts", "never trains on your api",
                       "not used to train", "not fine-tuned or lora-adapted with customer data")
            if any(phrase in corpus for phrase in phrases):
                return [Reading(subject, "false")]
        elif claim.field == "offering.data.zero_retention":
            if "guaranteed zero data retention" in corpus and "use vertex ai" in corpus:
                return [Reading(subject, "false")]
            if "never persisted to disk" in corpus or "no storage of prompts" in corpus:
                return [Reading(subject, "true")]
        elif claim.field == "offering.data.retention":
            match = re.search(r"(?is)(?:retained|stored).{0,100}?\b(\d+)\s*days?", text)
            if match:
                return [Reading(subject, match.group(1), "days")]
        elif claim.field == "offering.attestation.soc2":
            if re.search(r"(?i)SOC\s*2\s*Type\s*(?:2|II)", text):
                return [Reading(subject, "SOC 2 Type 2")]
        elif claim.field == "offering.attestation.baa":
            if "business associate agreement" in corpus and any(
                phrase in corpus
                for phrase in ("review and accept", "enter into an agreement")
            ):
                return [Reading(subject, "BAA available")]
        return []


class SubscriptionPageExtractor:
    """Read consumer-plan facts from plan cards and comparison tables."""

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="subscription-page@1")

    def accepts(self, text: str) -> bool:
        return bool(re.search(
            r"(?im)(?:\$[0-9.]+/(?:month|year)|billing cycle\s*\||plan\s*\|\s*limit|"
            r"everything in .+?, plus|\bcodex\b|claude code|more usage than pro|"
            r"google ai studio|\$\s?[0-9.]+\s*(?:/\s*(?:user/)?mo|per (?:member|user|seat))|"
            r"^\$[0-9.]+$|^all plans support |^supported models \||^#+ models$|"
            # MODEL-201's plan-fact layouts: a plans table with no price in it, a
            # yuan price, a plan's help article, a per-plan statement, a tier page.
            r"^(?:features|plan)\s*\||¥\s?[0-9]|^what is the .+ plan\?$|"
            r"\beach plan is\b|^quota windows\s*\||\bsupergrok\b)",
            text,
        ))

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        if not claim.field.startswith("offering.subscription."):
            raise ExtractorError("not a subscription claim")
        text = _content_block(text)
        readings = self._page_layouts(claim, text)
        for more in (_plan_cards(claim, text), _plan_facts(claim, text),
                     _vendor_layouts(claim, text)):
            readings += [r for r in more if r not in readings]
        return readings

    def _page_layouts(self, claim: Claim, text: str) -> list[Reading]:
        """The layouts MODEL-173's pages use (plan cards keyed by a price line)."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        aliases = {normalise_name(name) for name in claim.names}

        def matches(value: str) -> bool:
            candidate = normalise_name(value)
            return any(
                alias == candidate
                or (len(alias.split()) >= 2 and alias in candidate)
                for alias in aliases
            )

        products = (
            ("google ai studio", "Google AI Studio"),
            ("google antigravity", "Google Antigravity"),
            ("jules", "Jules"),
        )
        matrix_header = next(
            ([cell.strip() for cell in line.split("|")] for line in lines
             if normalise_name(line.split("|", 1)[0]) == "features"),
            None,
        )
        if claim.field == "offering.subscription.programmatic_or_agent_use" \
                and matrix_header is not None:
            columns = [i for i, heading in enumerate(matrix_header) if matches(heading)]
            found: list[tuple[str, set[str]]] = []
            for token, label in products:
                section = next(
                    (i for i, line in enumerate(lines) if token in normalise_name(line)),
                    None,
                )
                if section is None:
                    continue
                for line in lines[section + 1:]:
                    if "|" not in line:
                        break
                    row = [cell.strip() for cell in line.split("|")]
                    values = {
                        row[i].casefold() for i in columns if i < len(row) and row[i]
                    }
                    if values:
                        found.append((label, values))
                        break
            if found and len({tuple(sorted(values)) for _, values in found}) == 1:
                levels = set().union(*(values for _, values in found))
                level = " or ".join(sorted(levels))
                product_names = ", ".join(label for label, _ in found[:-1])
                product_names += f", and {found[-1][0]}" if len(found) > 1 else found[0][0]
                suffix = ", depending on subscription" if len(levels) > 1 else ""
                return [Reading(
                    subject=claim.names[0],
                    value=f"{level.capitalize()} {product_names} limits{suffix}",
                )]

        tables: list[list[list[str]]] = []
        current: list[list[str]] = []
        for line in [*lines, ""]:
            if "|" in line:
                current.append([cell.strip().rstrip("*") for cell in line.split("|")])
            elif current:
                tables.append(current)
                current = []

        for table in tables:
            if len(table[0]) == 2 and normalise_name(table[0][0]) == "plan":
                if claim.field == "offering.subscription.usage_allowance":
                    for row in table[1:]:
                        if len(row) == 2 and matches(row[0]):
                            return [Reading(subject=row[0], value=row[1])]
                continue

            columns = [i for i, heading in enumerate(table[0]) if matches(heading)]
            if not columns:
                continue
            if claim.field == "offering.subscription.billing_period":
                for row in table[1:]:
                    if normalise_name(row[0]) == "billing cycle":
                        values = [row[i] for i in columns if i < len(row)]
                        if values and all("monthly" in value.casefold() for value in values):
                            return [Reading(subject=claim.names[0], value="monthly")]
                if all("mo" in normalise_name(table[0][i]).split() for i in columns):
                    return [Reading(subject=claim.names[0], value="monthly")]
        price = re.compile(r"^\$[0-9.]+/(?:month|year)$", re.IGNORECASE)
        starts = [i - 1 for i, line in enumerate(lines) if i and price.match(line)]
        sections = {
            normalise_name(lines[start]): (lines[start + 1], lines[start + 2:next_start])
            for start, next_start in zip(starts, [*starts[1:], len(lines)])
        }
        wanted = next(
            (name for name in claim.names if normalise_name(name) in sections),
            None,
        )

        def features(plan: str, seen: set[str]) -> list[str]:
            key = normalise_name(plan)
            if key in seen or key not in sections:
                return []
            seen.add(key)
            _, body = sections[key]
            values = list(body)
            for line in body:
                inherited = re.match(r"Everything in (.+?), plus:?$", line, re.IGNORECASE)
                if inherited:
                    values.extend(features(inherited.group(1), seen))
            return values

        if claim.field == "offering.subscription.price":
            if wanted is not None:
                amount = re.match(r"^\$([0-9.]+)", sections[normalise_name(wanted)][0])
                if amount:
                    return [Reading(subject=wanted, value=amount.group(1))]
            if any("max 5x" in alias for alias in aliases):
                amount = re.search(r"(?is)\bmax\b.{0,100}?from \$([0-9.]+)", text)
                if amount:
                    return [Reading(subject=claim.names[0], value=amount.group(1))]
            if any(alias in {"claude pro", "pro"} for alias in aliases):
                amount = re.search(r"(?i)\$([0-9.]+) if billed monthly", text)
                if amount:
                    return [Reading(subject=claim.names[0], value=amount.group(1))]
            multiplier = next((m.group(1) for name in claim.names
                               if (m := re.search(r"\b(5x|20x)\b", name, re.IGNORECASE))), None)
            if multiplier:
                amount = re.search(
                    rf"(?i)Pro \$([0-9.]+) unlocks {re.escape(multiplier)}\b", text
                )
                if amount:
                    return [Reading(subject=claim.names[0], value=amount.group(1))]
            for line in lines:
                # One amount, after the plan's name: a line quoting several prices,
                # or naming the plan after the amount ("... vs. AI Pro"), is not
                # the plan's price line.
                amounts = list(re.finditer(r"\$([0-9.]+)", line))
                if len(amounts) == 1 and matches(line[:amounts[0].start()]):
                    return [Reading(subject=claim.names[0], value=amounts[0].group(1))]
            return []

        if claim.field == "offering.subscription.billing_period":
            if wanted is not None and price.match(sections[normalise_name(wanted)][0]):
                period = price.match(sections[normalise_name(wanted)][0]).group(0).rsplit("/", 1)[1]
                return [Reading(subject=wanted, value={"month": "monthly", "year": "annual"}[period])]
            for line in lines:
                if any(alias in normalise_name(line) for alias in aliases) and re.search(
                    r"(?i)(?:\$[0-9.]+/month|billed monthly)", line
                ):
                    return [Reading(subject=claim.names[0], value="monthly")]
            return []

        if claim.field == "offering.subscription.usage_allowance":
            if wanted is not None:
                body = features(wanted, set())
                allowance = next((line for line in body if re.match(
                    r"(?i)(?:more usage|higher rate limits|significantly higher usage)", line
                )), None)
                if allowance is not None:
                    return [Reading(subject=wanted, value=allowance.rstrip("*"))]
            multiplier = next((m.group(1) for name in claim.names
                               if (m := re.search(r"\b(5x|20x)\b", name, re.IGNORECASE))), None)
            if multiplier and re.search(r"(?i)choose 5x or 20x more usage than pro", text):
                return [Reading(subject=claim.names[0], value=f"{multiplier} more usage than Pro")]
            if multiplier:
                allowance = re.search(
                    rf"(?i)\b{re.escape(multiplier)}\b (?:higher )?usage than Plus", text
                )
                if allowance:
                    return [Reading(subject=claim.names[0], value=allowance.group(0))]
            if any(alias in {"claude pro", "pro"} for alias in aliases) and re.search(
                r"(?im)^More usage\*?$", text
            ):
                return [Reading(subject=claim.names[0], value="More usage")]
            return []

        if claim.field == "offering.subscription.programmatic_or_agent_use":
            if wanted is not None:
                body = features(wanted, set())
                access = next((line for line in body if re.search(
                    r"(?i)(?:bot access|claude code|ai studio|antigravity|jules)", line
                )), None)
                if access is not None:
                    return [Reading(subject=wanted, value=access)]
            codex_lines = [
                line for line in lines
                if "codex" in line.casefold()
                and any(alias in normalise_name(line) for alias in aliases)
            ]
            restriction = next((line for line in codex_lines if re.search(
                r"(?i)(?:\b(?:do|does|did|will) not include\b.{0,80}\bcodex\b|"
                r"\b(?:don't|doesn't|didn't|won't) include\b.{0,80}\bcodex\b|"
                r"\b(?:never|no longer) include\b.{0,80}\bcodex\b|"
                r"\binclude no\b.{0,80}\bcodex\b|"
                r"\bcodex\b.{0,80}\bnot included\b|"
                r"\bexclude(?:s|d)?\b.{0,80}\bcodex\b|"
                r"\bwithout\b.{0,80}\bcodex\b|"
                r"\bcodex\b.{0,80}\bunavailable\b)",
                line,
            )), None)
            if restriction is not None:
                return [Reading(subject=claim.names[0], value=restriction)]
            if any(re.search(
                r"(?i)(?:\binclude(?:s|d)?\b.{0,80}\bcodex\b|"
                r"\bcodex\b.{0,80}\bincluded\b|"
                r"\baccess to\b.{0,80}\bcodex\b)",
                line,
            ) for line in codex_lines):
                return [Reading(subject=claim.names[0], value="Codex")]
            claude = re.search(
                r"(?i)access to both Claude on the web, desktop, and mobile apps and Claude Code "
                r"in your terminal",
                text,
            )
            if claude and re.search(r"(?i)pro (?:and|or) max plan", text):
                return [Reading(subject=claim.names[0], value=claude.group(0))]
            return []

        if claim.field == "offering.subscription.models_covered":
            # ChatGPT's comparison rows: "Plan: Plus, Feature: GPT-6 Astra, Yes". Any
            # cell but "No" lists the model for that plan ("Limited access in ...").
            row = re.compile(r"^Plan: (.+?), Feature: (GPT-\d.*?), (.+)$")
            listed = [
                m.group(2) for line in lines
                if (m := row.match(line)) and matches(m.group(1))
                and normalise_name(m.group(3)) != "no"
            ]
            if listed:
                return [Reading(subject=claim.names[0],
                                value=", ".join(dict.fromkeys(listed)))]

        if claim.field != "offering.subscription.models_covered" or wanted is None:
            return []

        models = [
            match.group(1).strip() + " model"
            for line in features(wanted, set())
            if (match := re.fullmatch(r"(.+?\d(?:[\w .-]*))\s+model", line, re.IGNORECASE))
        ]
        models = list(dict.fromkeys(models))
        return [Reading(subject=wanted, value=", ".join(models))] if models else []


#: An amount in a currency symbol; ``$ 50``, ``$117.6`` and ``¥99`` included.
_AMOUNTS = {symbol: re.compile(re.escape(symbol) + r"\s?([0-9][0-9,]*(?:\.[0-9]+)?)")
            for symbol in ("$", "¥")}
_PLAN_LABEL = re.compile(r"(?i)(?:monthly|annual) plan:?\s*$")


def _priced(text: str, symbol: str = "$") -> list[tuple[str, str | None]]:
    """Each amount in ``symbol`` in ``text`` with the billing period its own words give.

    An amount's words run to the next amount; a "Monthly plan:" or "Annual plan:"
    label just before it belongs to it. "per month, billed annually" is annual.
    """
    found = list(_AMOUNTS[symbol].finditer(text))
    out = []
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        words = _PLAN_LABEL.sub("", text[m.end():end].split("|", 1)[0])
        label = _PLAN_LABEL.search(text[:m.start()])
        words = (label.group(0) if label else "") + words
        period = ("annual" if re.search(r"(?i)annual|/\s*y(?:ea)?r\b|per year", words)
                  else "monthly" if re.search(r"(?i)month|/\s*(?:user/)?mo\b", words)
                  else None)
        out.append((m.group(1).replace(",", ""), period))
    return out


def _price_readings(subject: str, field: str, text: str) -> list[Reading]:
    """Prices and periods for one plan from ``text``. When the plan publishes a
    monthly price, its annual rate is not read as the plan's price. A dollar price
    is read only from dollars and a yuan price only from yuan."""
    if field == "offering.subscription.billing_period":
        # As for the price: a plan that publishes a monthly price is billed monthly;
        # its annual option does not make "annual" a reading for it.
        periods = {p for symbol in _AMOUNTS for _, p in _priced(text, symbol) if p}
        period = "monthly" if "monthly" in periods else next(iter(periods), None)
        return [Reading(subject=subject, value=period)] if period else []
    symbol = {"offering.subscription.price": "$", "offering.subscription.price_cny": "¥"}.get(field)
    if symbol is None:
        return []
    priced = _priced(text, symbol)
    monthly = [a for a, p in priced if p == "monthly"]
    return [Reading(subject=subject, value=a)
            for a in (monthly or [a for a, _ in priced])]


def _model_list(cell: str) -> str:
    """A supported-models cell as a comma list: labels and qualifiers dropped."""
    cell = re.sub(r"(?i)only the following exact model versions are supported:|"
                  r"recommended models:|more models:|models not listed above are not "
                  r"supported\.?|\(vision\)", ",", cell)
    items = [i.strip() for i in re.split(r",|\band\b", cell) if i.strip()]
    return ", ".join(items)


#: A line that is page chrome, not plan content: a help centre's skip link, search
#: box and "Updated" stamp (MODEL-240).
_CHROME_LINE = re.compile(
    r"(?i)^(?:skip to (?:main )?content|search|updated (?:this|last) \w+|updated .+ ago)$")
#: A help centre's footer: nothing after it belongs to the article.
_FOOTER_LINE = re.compile(r"(?i)^(?:did this answer your question\??|related articles)$")


def _content_block(text: str) -> str:
    """The region without page chrome, so no reader offers a skip link or footer as
    a plan's value. A reader that finds nothing then says so, instead of reporting
    the page's first line as the value it found (MODEL-240)."""
    kept = []
    for line in text.splitlines():
        if _FOOTER_LINE.match(line.strip()):
            break
        if not _CHROME_LINE.match(line.strip()):
            kept.append(line)
    return "\n".join(kept)


#: "Premium seats: Team plan Premium seats include 6.25x the Pro plan's per-session
#: usage allowance and have a weekly usage limit…": what a labelled plan includes.
_INCLUDES = re.compile(r"\binclude[sd]?\s+(.+?)(?:\s+and\s+|[.;]?$)", re.IGNORECASE)


def _plan_cards(claim: Claim, text: str) -> list[Reading]:
    """Plan facts from generic plan-page layouts (MODEL-201).

    * a card: a line that is exactly the plan's name (markdown heading marks
      allowed), then within six lines its price line(s);
    * a tier line: "$199.99 / month: 20x higher usage limits vs. AI Pro", the tier
      named by its multiplier;
    * a table whose header names the plan as a column, or whose row starts with it;
    * a help article titled "What is the <plan>?", whose sentences are the plan's;
    * "All plans support A, B." and a "### Models" list, which apply to every plan
      on the page.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    aliases = {normalise_name(name) for name in claim.names}
    subject, field = claim.names[0], claim.field
    readings: list[Reading] = []

    def heading(line: str) -> bool:
        return _card_heading(line, aliases)

    for i, line in enumerate(lines):
        if not heading(line):
            continue
        window: list[str] = [line] if _PRICED_HEADING.match(line) else []
        for later in lines[i + 1:i + 7]:
            priced = "$" in later or "¥" in later
            if window and not (priced or later.startswith("/")):
                break
            if priced or (window and later.startswith("/")):
                window.append(later)
        readings += _price_readings(subject, field, " ".join(window))

    multiplier = next((m.group(1) for name in claim.names
                       if (m := re.search(r"\b(\d+x)\b", name, re.IGNORECASE))), None)
    if multiplier:
        for line in lines:
            m = re.match(r"^\$\s?([0-9.]+)\s*/\s*month:\s*(\d+x)\b\s*(.*)$", line,
                         re.IGNORECASE)
            if m and m.group(2).casefold() == multiplier.casefold():
                readings += _price_readings(subject, field, f"${m.group(1)}/month")
                if field == "offering.subscription.usage_allowance":
                    readings.append(Reading(subject=subject,
                                            value=f"{m.group(2)} {m.group(3)}".strip()))

    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in [*lines, ""]:
        if "|" in line:
            current.append([cell.strip() for cell in line.split("|")])
        elif current:
            tables.append(current)
            current = []
    for table in tables:
        columns = [j for j, cell in enumerate(table[0]) if normalise_name(cell) in aliases]
        for row in table[1:]:
            label = normalise_name(row[0])
            cells = [row[j] for j in columns if j < len(row)]
            if label == "price":
                for cell in cells:
                    readings += _price_readings(subject, field, cell)
            elif label == "supported models" and field == "offering.subscription.models_covered":
                readings += [Reading(subject=subject, value=_model_list(c)) for c in cells]
            elif label in {"quota", "quota windows"} \
                    and field == "offering.subscription.usage_allowance":
                readings += [Reading(subject=subject, value=c) for c in cells]
            if label in aliases:
                readings += _price_readings(subject, field, " | ".join(row[1:]))
                if field in {"offering.subscription.programmatic_or_agent_use",
                             "offering.subscription.usage_allowance"}:
                    readings += [Reading(subject=subject, value=c) for c in row[1:] if c]

    # A help article about one plan ("What is the Enterprise plan?"): its sentences
    # are that plan's wording.
    title = next((m.group(1) for line in lines[:3]
                  if (m := re.match(r"^What is the (.+?)\?$", line))), None)
    if title and normalise_name(title) in aliases:
        if field in {"offering.subscription.programmatic_or_agent_use",
                     "offering.subscription.usage_allowance"}:
            readings += [Reading(subject=subject, value=sentence) for line in lines
                         for sentence in re.split(r"(?<=[.!?])\s+", line) if sentence]
        if field == "offering.subscription.usage_allowance":
            # A line labelled with this plan ("Premium seats: …") states its allowance.
            for line in lines:
                label, sep, statement = line.partition(":")
                if sep and normalise_name(label) in aliases \
                        and (m := _INCLUDES.search(statement)):
                    readings.append(Reading(subject=subject, value=m.group(1)))
        if field == "offering.subscription.billing_period":
            # Only what the plan itself is billed by: a sentence about its seat,
            # plan or subscription ("Billed monthly in arrears" for usage is not).
            for line in lines:
                for sentence in re.split(r"(?<=[.!?])\s+|\s*\|\s*", line):
                    text_ = sentence.casefold()
                    if not re.search(r"\b(?:seats?|plans?|subscriptions?|priced)\b", text_):
                        continue
                    for word, period in (("billed annually", "annual"),
                                         ("billed monthly", "monthly")):
                        if word in text_:
                            readings.append(Reading(subject=subject, value=period))

    if field == "offering.subscription.models_covered":
        for i, line in enumerate(lines):
            if m := re.match(r"^All plans support (.+?)\.?$", line):
                readings.append(Reading(subject=subject, value=m.group(1)))
            if re.match(r"^#+\s*Models$", line):
                listed = []
                for later in lines[i + 1:]:
                    if later.startswith("#"):
                        break
                    listed.append(later)
                readings.append(Reading(subject=subject, value=", ".join(listed)))
    return readings


#: A card heading that carries its own price: "Moderato — ¥99/month".
_PRICED_HEADING = re.compile(r"^\S.*?\s[—–-]\s*[$¥]\s?[0-9]")


def _card_heading(line: str, aliases: set[str]) -> bool:
    """A plan card's heading: the plan's name alone (markdown marks allowed), or its
    name followed by a dash and a price."""
    if normalise_name(line.lstrip("#")) in aliases:
        return True
    if _PRICED_HEADING.match(line):
        name = re.split(r"\s[—–-]\s", line, maxsplit=1)[0]
        return normalise_name(name) in aliases
    return False


def _card_lines(lines: list[str], aliases: set[str]) -> list[str]:
    """The lines of the plan's card after its price, up to the next card.

    The next card starts at a markdown heading, a priced heading, or a short line
    (three words or fewer, no amount) that a price follows within four lines.
    """
    out: list[str] = []
    for i, line in enumerate(lines):
        if not _card_heading(line, aliases):
            continue
        priced = bool(_PRICED_HEADING.match(line))
        taken = 0
        for j in range(i + 1, min(len(lines), i + 40)):
            later = lines[j]
            has_amount = bool(re.search(r"[$¥]\s?[0-9]", later))
            if not priced:
                priced = has_amount  # the card's price, a heading line included
                continue
            if (later.startswith("#") or _PRICED_HEADING.match(later)
                    or re.match(r"(?i)compare\b", later) or taken >= 15):
                break
            taken += 1
            short = len(later.split()) <= 3 and not has_amount and not re.search(r"[0-9]", later)
            # A short line with a bare price close after it is the next card's name;
            # a priced heading ("Allegretto — ¥199/month") ends the card itself.
            upcoming = next((n for n in lines[j + 1:j + 5] if re.search(r"[$¥]\s?[0-9]", n)), None)
            if short and upcoming is not None and not _PRICED_HEADING.match(upcoming):
                break
            out.append(re.sub(r"^[-*•]\s+", "", later))
    return out


def _sentences(line: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", line.strip()) if s]


def _plan_scope(claim: Claim, lines: list[str], *, articles: bool = True,
                tiers_only: bool = False) -> list[str]:
    """Sentences and clauses that speak for the claim's plan.

    * every sentence of a help article titled "What is the <plan>?", unless
      ``articles`` is false (an article about a plan family also speaks for each
      of its tiers, so a tier's own number must come from a clause naming it);
    * a clause naming a distinctive alias (two words or more, such as "Max 5x" or
      "Pro $100"; a clause is split at ", while" and ";");
    * a sentence naming a one-word alias followed by "plan" or "plans" ("With Pro
      and Max plans, ...");
    * a sentence about "each plan", "every plan" or "all plans".

    ``tiers_only`` keeps only clauses naming a tier: a distinctive alias that is
    not a family name ("Team plan", "Max plan"), which sibling tiers share. It is
    what a tier's own number (a multiplier) is read from.
    """
    aliases = {normalise_name(name) for name in claim.names}
    distinctive = {a for a in aliases if len(a.split()) >= 2}
    single = aliases - distinctive
    if tiers_only:
        articles, single = False, set()
        distinctive = {a for a in distinctive if not re.search(r" plans?$", a)}
    title = next((m.group(1) for line in lines[:3]
                  if (m := re.match(r"^What is the (.+?)\?$", line))), None)
    if articles and title and normalise_name(title) in aliases:
        return [s for line in lines for s in _sentences(line)]
    scoped: list[str] = []
    for line in lines:
        for sentence in _sentences(line):
            normal = normalise_name(sentence)
            if not tiers_only and re.search(r"\b(?:each|every|all) (?:\w+ )?plans?\b", normal) or any(
                re.search(rf"\b{re.escape(a)}\b.*\bplans?\b", normal) for a in single
            ):
                scoped.append(sentence)
                continue
            for clause in re.split(r",\s*while\s+|;\s+", sentence):
                if any(re.search(rf"(?<![0-9a-z]){re.escape(a)}s?(?![0-9a-z])",
                                 normalise_name(clause)) for a in distinctive):
                    scoped.append(clause)
    return scoped


def _without_aliases(clause: str, names: Sequence[str]) -> str:
    for name in sorted(names, key=len, reverse=True):
        clause = re.sub(re.escape(name), " ", clause, flags=re.IGNORECASE)
    return clause


_TIMES = {"two": 2, "four": 4, "five": 5, "six": 6, "ten": 10, "fourteen": 14, "twenty": 20}
_MULTIPLE = re.compile(
    r"(?<![\w.])(\d+(?:\.\d+)?)\s*(?:[x×](?![a-z0-9])|times\b)|\b(two|four|five|six|ten|"
    r"fourteen|twenty)\s+times\b", re.IGNORECASE)
_BASE = re.compile(
    r"(?:\bthan\b|\bvs\.?|^\s*(?=the\b))\s*(?:the\s+)?([A-Z][A-Za-z0-9$ ]*?)"
    r"(?:'s\b|\s+plan\b|\s+limits?\b|\s*[.,;:*]|\s*$)")


def _multiples(provider: str, clause: str) -> list[tuple[float, str | None]]:
    """(multiplier, base plan id) for each "5x ... than Plus" or "five times the Pro
    plan's" in ``clause``. The base plan id is the provider's plan whose ID is the
    base's name: "AI Pro" is ``<provider>/subscription/ai-pro``."""
    out = []
    for m in _MULTIPLE.finditer(clause):
        number = float(m.group(1)) if m.group(1) else float(_TIMES[m.group(2).casefold()])
        tail = clause[m.end():]
        tail = re.sub(r"^\s*(?:(?:more|higher)\s+)?(?:usage\s+)?(?:limits\s+)?", " ", tail,
                      flags=re.IGNORECASE)
        base = _BASE.search(tail)
        plan = (f"{provider}/subscription/{normalise_name(base.group(1)).replace(' ', '-')}"
                if base else None)
        out.append((number, plan))
    return out


#: A five-hour allowance window, as providers write it.
_FIVE_HOURS = re.compile(r"\b(?:five|5)[- ]hours?\b", re.IGNORECASE)
_NOT_A_WINDOW = re.compile(r"\bno (?:five|5)[- ]hour|\bhours? per week\b", re.IGNORECASE)

#: Words that name where a plan can be used (MODEL-200's surfaces).
_SURFACE_WORDS = (
    (re.compile(r"\bweb\b", re.IGNORECASE), "chat_app"),
    (re.compile(r"\bdesktop\b", re.IGNORECASE), "desktop_app"),
    (re.compile(r"\b(?:mobile|iOS|Android)\b", re.IGNORECASE), "mobile_app"),
    (re.compile(r"\bClaude Code\b"), "coding_tool:claude-code"),
    (re.compile(r"\bCodex\b.*\bCLI\b|\bCLI\b.*\bCodex\b"), "coding_tool:codex-cli"),
    (re.compile(r"\bCopilot CLI\b"), "coding_tool:copilot-cli"),  # MODEL-205
)
#: Read only in a paragraph that opens with the plan's own list sentence
#: (``_vendor_layouts``): other providers' pages name Cursor as a place their own
#: tool runs ("VS Code, Cursor and other VS Code forks"), which is not a surface.
#: "Cursor Models" and the like are not the editor.
_VENDOR_SURFACE_WORDS = (
    *_SURFACE_WORDS,
    (re.compile(r"\bCursor\b(?!\s+(?:Models|Token|Router|SDK|CLI|for\s+iOS))"),
     "coding_tool:cursor"),
)


#: A sentence that opens with a list of plans and "include(s)": "Pro, Pro Plus, and
#: Ultra include unlimited tab completions", "Pro includes GPT-5.6 Terra, ...".
_LISTED_PLANS = re.compile(
    r"^(?P<plans>[A-Z][^.:;]{0,80}?)\s+(?:also\s+)?includes?\s+(?P<rest>.+?)\.?$")


def _listed_plan_sentences(claim: Claim, lines: list[str]) -> list[tuple[str, str, str]]:
    """(paragraph, sentence, what the plans include) for each sentence whose opening
    list of plans names the claim's plan exactly ("Pro" is not "Pro+")."""
    names = {name.casefold() for name in claim.names}
    out = []
    for line in lines:
        for sentence in _sentences(line):
            m = _LISTED_PLANS.match(sentence)
            if not m:
                continue
            plans = [p.strip() for p in re.split(r",\s*(?:and\s+)?|\s+and\s+", m.group("plans"))
                     if p.strip()]
            if all(len(p.split()) <= 3 for p in plans) and any(p.casefold() in names for p in plans):
                out.append((line, sentence, m.group("rest")))
    return out


def _pool_models(pool: str, lines: list[str]) -> list[str]:
    """The models a usage pool covers: those "The <pool> pool includes ..." names, and
    the rows of the first table after a heading that is the pool's name."""
    out: list[str] = []
    named = re.compile(rf"^The {re.escape(pool)} pool includes (.+?)\.?$", re.IGNORECASE)
    for line in lines:
        for sentence in _sentences(line):
            if m := named.match(sentence):
                out += [s.strip() for s in re.split(r",|\band\b", m.group(1)) if s.strip()]
    for i, line in enumerate(lines):
        if line.casefold() != pool.casefold():
            continue
        rows: list[str] = []
        for later in lines[i + 1:]:
            if "|" in later:
                rows.append(later.split("|", 1)[0].strip())
            elif rows:
                break
        out += [row for row in rows if normalise_name(row) not in {"", "name"}]
        break
    return out


def _vendor_layouts(claim: Claim, text: str) -> list[Reading]:
    """The layouts of the subscription-only vendors' plan pages (MODEL-205).

    * a sentence opening with a list of plans and "include(s)": what follows is what
      those plans include (models, allowance, agent use), and the surfaces its
      paragraph names are where they work;
    * a plan-column table whose cells are "Included" or "Not included" (GitHub
      Docs, read with the ``html-icon-labels`` normaliser): the rows the plan's
      column includes are the models it covers;
    * a plan's row in a table: each cell is read with its column heading
      ("Total monthly AI credits: 1,500"), and a price "per month" is monthly;
    * a plan table whose pool columns say "Included" (Cursor's "Cursor Models",
      "Other Models"): the plan covers each included pool's models;
    * a plan card ending in "Get <plan>": the lines after its price are its features.

    Plan names are matched exactly, case aside, so a sibling ("Copilot Pro+" beside
    "Copilot Pro") never confirms the claim's plan.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    names = {name.casefold() for name in claim.names}
    subject, field = claim.names[0], claim.field
    models = field == "offering.subscription.models_covered"
    wording = field in {"offering.subscription.usage_allowance",
                        "offering.subscription.programmatic_or_agent_use"}
    readings: list[Reading] = []

    for paragraph, sentence, rest in _listed_plan_sentences(claim, lines):
        if models:
            readings.append(Reading(subject=subject, value=rest))
        if wording:
            readings.append(Reading(subject=subject, value=sentence))
        if field == "offering.subscription.surfaces":
            found = sorted({s for word, s in _VENDOR_SURFACE_WORDS if word.search(paragraph)})
            if found:
                readings.append(Reading(subject=subject, value=", ".join(found)))
    if field == "offering.subscription.programmatic_or_agent_use":
        readings += [Reading(subject=subject, value=s) for line in lines
                     for s in _sentences(line) if re.match(r"(?i)^all plans include\b", s)]

    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in [*lines, ""]:
        if "|" in line:
            current.append([cell.strip() for cell in line.split("|")])
        elif current:
            tables.append(current)
            current = []
    for table in tables:
        header, rows = table[0], table[1:]
        if models:
            for j in (j for j, cell in enumerate(header) if cell.casefold() in names):
                cells = [normalise_name(row[j]) for row in rows if j < len(row)]
                if cells and set(cells) <= {"included", "not included"}:
                    included = [row[0] for row in rows
                                if j < len(row) and normalise_name(row[j]) == "included"]
                    readings.append(Reading(subject=subject, value=", ".join(included)))
        for row in rows:
            if not row or row[0].casefold() not in names:
                continue
            pairs = [(h, c) for h, c in zip(header[1:], row[1:]) if h and c]
            if field == "offering.subscription.usage_allowance":
                readings += [Reading(subject=subject, value=f"{h}: {c}") for h, c in pairs]
            if field == "offering.subscription.billing_period" and any(
                    re.search(r"[$¥]\s?[0-9]", c)
                    and re.search(r"(?i)\bper (?:\w+ ){0,3}month\b|/\s*mo\b", f"{h} {c}")
                    for h, c in pairs):
                readings.append(Reading(subject=subject, value="monthly"))
            if normalise_name(header[0]) == "plan":
                pools = [h for h, c in pairs if normalise_name(c) == "included"]
                covered = [m for pool in pools for m in _pool_models(pool, lines)]
                if models and covered:
                    readings.append(Reading(subject=subject,
                                            value=", ".join(dict.fromkeys(covered))))
                if field == "offering.subscription.usage_allowance" and pools:
                    readings += [Reading(subject=subject, value=s) for line in lines
                                 for s in _sentences(line) if "usage pools" in s.casefold()]

    if wording:
        for i, line in enumerate(lines):
            if line.casefold() not in {f"get {name}" for name in names}:
                continue
            # The card's own price: walking back past another card's "Get ..." line
            # would borrow that card's price and features, so a card with no price of
            # its own gives no reading.
            price = None
            for j in range(i - 1, max(-1, i - 25), -1):
                if re.search(r"[$¥]\s?[0-9]", lines[j]):
                    price = j
                    break
                if re.match(r"(?i)^get \S", lines[j]):
                    break
            if price is not None:
                readings += [Reading(subject=subject, value=later)
                             for later in lines[price + 1:i]]
    return readings


def _plan_facts(claim: Claim, text: str) -> list[Reading]:
    """MODEL-200's plan facts, read from text scoped to the plan (MODEL-201)."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    aliases = {normalise_name(name) for name in claim.names}
    subject, field = claim.names[0], claim.field
    provider = claim.subject.split("/", 1)[0]
    readings: list[Reading] = []

    if field == "offering.subscription.coverage_quote":
        # The facet is the page's own wording, so any line, sentence, table cell or
        # run of consecutive lines of the region is a candidate.
        bare = [line.lstrip("#").strip() for line in lines]
        candidates = [*bare, *(s for line in bare for s in _sentences(line)),
                      *(c.strip() for line in bare if "|" in line for c in line.split("|"))]
        candidates += ["\n".join(bare[i:i + n]) for n in range(2, 9)
                       for i in range(len(bare) - n + 1)]
        return [Reading(subject=subject, value=c) for c in dict.fromkeys(candidates) if c]

    if field in {"offering.subscription.usage_allowance",
                 "offering.subscription.programmatic_or_agent_use"}:
        readings += [Reading(subject=subject, value=line) for line in _card_lines(lines, aliases)]

    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in [*lines, ""]:
        if "|" in line:
            current.append([cell.strip().rstrip("*") for cell in line.split("|")])
        elif current:
            tables.append(current)
            current = []
    columns_of = [
        (table, [j for j, cell in enumerate(table[0]) if normalise_name(cell) in aliases])
        for table in tables
    ]

    if field == "offering.subscription.families_covered":
        families = default_registry().families()
        for table, columns in columns_of:
            for column in columns:
                covered = []
                for row in table[1:]:
                    label = normalise_name(row[0])
                    matched = [f.id for f in families
                               if normalise_name(f.name) == label
                               or normalise_name(f.name).endswith(" " + label)]
                    cell = normalise_name(row[column]) if column < len(row) else ""
                    if len(matched) == 1 and cell not in {"", "no", "usage credits", "n a"}:
                        covered.append(matched[0])
                if covered:
                    readings.append(Reading(subject=subject, value=", ".join(covered)))
        return readings

    scope = _plan_scope(claim, lines)
    if field == "offering.subscription.allowance.window":
        quota = [row[j] for table, columns in columns_of for row in table[1:]
                 if normalise_name(row[0]) in {"quota", "quota windows"}
                 for j in columns if j < len(row)]
        for piece in [*scope, *quota]:
            if _FIVE_HOURS.search(piece) and not _NOT_A_WINDOW.search(piece):
                readings.append(Reading(subject=subject, value="five hours"))
                break
    if field in {"offering.subscription.allowance.multiplier",
                 "offering.subscription.allowance.relative_to"}:
        tier = [f"{m.group(1)} {m.group(2)}" for line in lines
                if (m := re.match(r"^\$\s?[0-9.]+\s*/\s*month:\s*(\d+x)\s*(.*)$", line,
                                  re.IGNORECASE))
                and any(m.group(1).casefold() in a.split() for a in aliases)]
        own = _plan_scope(claim, lines, tiers_only=True)
        for clause in [*(_without_aliases(c, claim.names) for c in own), *tier]:
            for number, plan in _multiples(provider, clause):
                if plan is None:
                    continue  # a multiple of nothing named ("Max 5x and 20x plans")
                value = plan if field.endswith("relative_to") else f"{number:g}"
                readings.append(Reading(subject=subject, value=value))
    if field == "offering.subscription.surfaces":
        # Every surface the plan's text names: a surface it does not name is absent,
        # so a claim missing one the page names is wrong, not partial.
        found = sorted({surface for sentence in scope
                        for word, surface in _SURFACE_WORDS if word.search(sentence)})
        if found:
            readings.append(Reading(subject=subject, value=", ".join(found)))
    return readings


class ModelPageExtractor:
    """Read the label/value layouts used by first-party model-spec pages.

    These pages commonly render a label followed by its value on the next
    line (``Function calling`` / ``Supported``), or a value followed by its
    label on one line (``1,050,000 context window``).  The page must also name
    the model exactly; that keeps an individual page from confirming a sibling.
    """

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="model-page-label-match@1")

    def accepts(self, text: str) -> bool:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return len(lines) >= 3

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        names = {normalise_name(name): name for name in claim.names}

        def published_name(line: str) -> str | None:
            normal = normalise_name(line)
            return next((original for name, original in names.items() if name in normal), None)

        subject = next((name for line in lines if (name := published_name(line))), None)
        label = _label(claim)
        readings: list[Reading] = []

        aliases = {
            "context window": {"context window", "context"},
            "max output tokens": {"max output tokens", "max output"},
            "structured outputs": {"structured outputs", "structured output"},
            "reasoning effort": {"reasoning effort", "effort", "default effort", "thinking"},
        }.get(label, {label})

        for i, line in enumerate(lines):
            raw_header = line.strip("| ").split(" | ")
            header = [normalise_name(cell) for cell in raw_header]
            model_header = next((name for name in ("model", "model id") if name in header), None)
            if model_header is None:
                continue
            model_col = header.index(model_header)
            value_col = next((n for n, name in enumerate(header) if name in aliases), None)
            if value_col is None:
                continue
            for row_line in lines[i + 1:]:
                row = row_line.strip("| ").split(" | ")
                if len(row) != len(header):
                    break
                if row_name := published_name(row[model_col]):
                    readings.append(Reading(
                        subject=row_name, value=row[value_col], unit=claim.unit
                    ))

        for i, line in enumerate(lines):
            normal = normalise_name(line)
            if normal in aliases:
                value = lines[i + 1] if i + 1 < len(lines) else None
                unit = claim.unit if claim.field.startswith("offering.price.") else None
                if unit is not None:
                    # Model price pages can place a category label before the amount.
                    if normalise_name(value or "") == "tokens":
                        value = lines[i + 2] if i + 2 < len(lines) else None
                    if value is None or parse_quantity(value, unit) is None:
                        continue
                readings.append(Reading(subject=subject, value=value, unit=unit))
                continue
            suffix = next((alias for alias in aliases if normal.endswith(" " + alias)), None)
            if suffix:
                # Use the original line so punctuation in the numeric value is
                # retained; strip only the trailing label.
                words = len(suffix.split())
                value = " ".join(line.split()[:-words])
                readings.append(Reading(subject=subject, value=value, unit=claim.unit))

        if claim.field in {"offering.price.batch_input", "offering.price.batch_output"} \
                and re.search(r"(?i)batch(?: and flex)? (?:are )?priced at 50%", text):
            base_label = "input" if claim.field.endswith("batch_input") else "output"
            for i, line in enumerate(lines[:-1]):
                if normalise_name(line) != base_label:
                    continue
                quantity = parse_quantity(lines[i + 1], claim.unit)
                if quantity is not None:
                    readings.append(Reading(subject, str(quantity.number / 2), claim.unit))
        if claim.field in {"offering.price.batch_input", "offering.price.batch_output"} \
                and "Batch API price" in lines:
            start = lines.index("Batch API price")
            base_label = "input" if claim.field.endswith("batch_input") else "output"
            for i in range(start + 1, len(lines) - 1):
                if normalise_name(lines[i]) == base_label:
                    quantity = parse_quantity(lines[i + 1], claim.unit)
                    if quantity is not None:
                        readings.append(Reading(subject, str(quantity.number), claim.unit))
                        break
        if claim.field == "offering.price.cached_input" and "Cached tokens" in lines:
            i = lines.index("Cached tokens")
            if i + 1 < len(lines):
                readings.append(Reading(subject, lines[i + 1], claim.unit))
        if claim.field in {"offering.price.batch_input", "offering.price.batch_output"} \
                and "Batch API" in lines:
            i = lines.index("Batch API")
            if i + 1 < len(lines):
                readings.append(Reading(subject, lines[i + 1]))

        if claim.field == "model.class" and subject is not None:
            identity = normalise_name(f"{claim.subject} {' '.join(claim.names)}")
            derived = (
                "vectoriser"
                if any(
                    term in identity
                    for term in ("embedding", "ingot", "harrier", "qzhou", "kalm")
                )
                else "orderer" if any(term in identity for term in ("rerank", "querit"))
                else "decider" if any(term in identity for term in ("decision", "typesafe", "jev"))
                else "text-generator"
            )
            readings.append(Reading(subject=subject, value=derived))
        elif claim.field == "model.lifecycle" and subject is not None:
            readings.append(Reading(subject=subject, value="active"))
        elif claim.field == "model.weights_openness" and subject is not None:
            if re.search(r"(?im)^license\s*:", text) or "download the model" in text.casefold():
                readings.append(Reading(subject=subject, value="open_weights"))
        elif claim.field.startswith("feature.") and subject is not None:
            phrases = {
                "feature.tool_calling": ("function calling", "tool calling"),
                "feature.structured_output": ("structured output", "json mode", "json schema"),
                "feature.effort_controls": ("reasoning effort", "default effort", "thinking"),
                "feature.batch": ("v1/batch", "batch api", "batch inference"),
                "feature.streaming": ("streaming", "stream response"),
            }[claim.field]
            corpus = text.casefold()
            if any(phrase in corpus for phrase in phrases):
                readings.append(Reading(subject=subject, value="supported"))
        return readings or [Reading(subject=subject, value=None)]


class StructuredDataExtractor:
    """Read retained JSON or CSV board snapshots with one row per model."""

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="structured-row-match@1")
    _SUBJECTS = ("model", "model name", "model version", "model display", "name")
    _UNITS = {
        "rating": "Arena score (Elo scale)",
        "mean score": "fraction",
        "mean task": "fraction",
        "retrieval": "fraction",
        "reranking": "fraction",
        "accuracy": "percent",
        "pass at 1": "percent",
        "resolve rate": "percent",
    }

    @staticmethod
    def _rows(text: str) -> list[Mapping[str, Any]] | None:
        try:
            data = json.loads(text)
        except ValueError:
            first = text.splitlines()[0] if text.splitlines() else ""
            headers = {normalise_name(cell) for cell in first.split(",")}
            if not headers.intersection(StructuredDataExtractor._SUBJECTS):
                return None
            try:
                rows = list(csv.DictReader(io.StringIO(text)))
            except (csv.Error, UnicodeError):
                return None
            return rows or None
        if isinstance(data, Mapping) and isinstance(data.get("rows"), list):
            read_date = data.get("read_date")
            return [
                {**row, "_snapshot_read_date": read_date}
                for row in data["rows"]
                if isinstance(row, Mapping)
            ]
        if isinstance(data, list):
            return [row for row in data if isinstance(row, Mapping)]
        return None

    def accepts(self, text: str) -> bool:
        return self._rows(text) is not None

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        rows = self._rows(text) or []
        label = claim.label or claim.field
        out = []
        for row in rows:
            normal = {normalise_name(str(key)): value for key, value in row.items()}
            subject = next((normal.get(key) for key in self._SUBJECTS if normal.get(key)), None)
            value = normal.get(normalise_name(label))
            composite = isinstance(claim.value, dict) and "score" in claim.value
            flags = []
            if normal.get("deprecated") is True:
                flags.append("deprecated")
            if normal.get("release warning") is True:
                flags.append("contamination_warning")
            if subject is None or (value is None and not (composite and flags)):
                continue
            effort = normal.get("reasoning effort") or normal.get("effort")
            if effort is None:
                match = re.search(r"(?:[_\s\(\[])(minimal|low|medium|high|xhigh|max)(?:\)|\]|$)",
                                  str(subject), re.IGNORECASE)
                effort = match.group(1) if match else None
            date_ = next((normal.get(key) for key in (
                "date", "leaderboard publish date", "started at", "snapshot read date",
                "release date",
            ) if normal.get(key)), None)
            if date_ is not None:
                date_ = str(date_).split("T", 1)[0]
            harness = "unregistered" if normal.get("agent") or normal.get("harness") else None
            reading_value: JsonValue = str(value) if value is not None else None
            if composite:
                lower = normal.get("rating lower")
                upper = normal.get("rating upper")
                interval = [lower, upper] if lower is not None and upper is not None else None
                count = normal.get("vote count", normal.get("n"))
                reading_value = {
                    **({"score": str(value)} if value is not None else {}),
                    **({"interval": interval} if interval is not None else {}),
                    **({"n": count} if count is not None else {}),
                    **({"quality_flags": flags} if flags else {}),
                }
            out.append(Reading(
                subject=str(subject),
                value=reading_value,
                unit=self._UNITS.get(normalise_name(label)),
                conditions={"effort": _text(effort),
                            "harness": harness, "date": _text(date_)},
            ))
        return out


LLM_PROMPT = """\
You are checking a catalogue against a source. Read the source region below and
report every value it gives for "{label}", for any model.

Return only a JSON array. One object per value, with these string fields (null
when the region does not say): "subject" (the model name exactly as written),
"value" (the number or text exactly as written), "unit", "effort", "harness",
"date", "quoted_sentence" (the exact sentence containing the value) and
"condition_sentence" (the exact heading, caption or sentence that states the
effort or harness, when the quoted sentence does not).
Return [] if the region gives no such value. Do not infer, convert, combine
sentences, or use knowledge outside the source region. A quoted sentence must
appear verbatim in the source region.

A region can state a condition once for many values: in a heading such as
"Results (max reasoning effort)", or in a caption or note such as "all X results
use high effort". Give each value every condition the region states for it, unless
the region states a different condition for that value or that model.

The model being checked is published as: {names}.

Source region:
<<<
{text}
>>>
"""


class LLMCallBudgetExceededError(RuntimeError):
    """The configured live-reader call budget has been exhausted."""


class ClaudeCLICompletion:
    """Call the authenticated Claude CLI and return its assistant text."""

    def __init__(self, *, max_calls: int = 400) -> None:
        self.max_calls = max_calls
        self.calls = 0

    def __call__(self, prompt: str) -> str:
        if self.calls >= self.max_calls:
            raise LLMCallBudgetExceededError(
                f"stopped before exceeding the {self.max_calls}-call budget"
            )
        self.calls += 1
        command = [
            "claude", "-p", prompt, "--model", "claude-sonnet-5", "--effort", "low",
            "--output-format", "json",
        ]
        try:
            completed = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            raise ExtractorError(f"Claude CLI could not start: {exc}") from exc
        if completed.returncode != 0:
            detail = completed.stderr.strip() or f"exit {completed.returncode}"
            raise ExtractorError(f"Claude CLI failed: {detail}")
        try:
            envelope = json.loads(completed.stdout)
            result = envelope["result"]
            if not isinstance(result, str):
                raise TypeError("result is not text")
        except (KeyError, TypeError, ValueError) as exc:
            raise ExtractorError(f"Claude CLI returned an invalid JSON envelope: {exc}") from exc
        return result


class LLMCache:
    """Persistent reader replies keyed by source copy, cited region, facet and the
    names the prompt asks about.

    The names are in the key because the prompt carries them: a reader answers
    mostly for the named subject, and reads a row with no subject as that one, so
    a reply for one plan or model must not answer for a sibling on the same page
    (MODEL-201). ``strict-reader-v3`` keys therefore miss every v2 reply.

    ``namespace`` keeps one reader's replies from answering for another's.
    """

    def __init__(self, root: str | Path | None = None, *, namespace: str | None = None) -> None:
        configured = os.environ.get("MODELSPEC_LLM_CACHE")
        self.root = Path(root or configured or Path.home() / ".cache/modelspec/llm-reader")
        self.namespace = namespace

    def _path(self, key: tuple[str, ...]) -> Path:
        scope = () if self.namespace is None else (self.namespace,)
        digest = hashlib.sha256(
            json.dumps(("strict-reader-v3", *scope, *key), ensure_ascii=False,
                       separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return self.root / digest[:2] / f"{digest}.json"

    def get(self, key: tuple[str, ...]) -> str | None:
        path = self._path(key)
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def put(self, key: tuple[str, ...], reply: str) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(reply, encoding="utf-8")


def _check_effort_is_stated(claim: Claim, row: Mapping[str, Any], text: str,
                            subjects: Sequence[str] = ()) -> None:
    """Refuse a reader's effort the region does not plainly state for the value (MODEL-233).

    The prompt asks the reader to carry a heading's or caption's condition to the
    values it covers. Which values a caption covers is the reader's reading, and the
    collector's is the other key; this only refuses the plain inventions. The level
    counts when the row gives it (the model cell's qualifier, a cell that is the
    level, or an effort phrase); when the region's first line, not a table row and
    naming no other of ``subjects`` (the reply's models), names it as an effort; or when
    a verbatim ``condition_sentence`` does, and names the row's model, or names the
    benchmark and none of the other models.

    Not refused, and left to the two keys: a model the reader leaves out of its
    reply (its caption can then pass as unowned), a cell equal to a level in a
    column that is not an effort column, and a sentence stitched from fragments
    that each occur in the region (the ``quoted_sentence`` check shares this).
    """
    stated = row.get("condition_sentence")
    if isinstance(stated, str) and normalise_name(stated) not in normalise_name(text):
        raise ValueError("condition_sentence is not verbatim source text")
    level = _condition("effort", _text(row.get("effort")))
    if level not in EFFORT_LEVELS:
        return  # no level, or none this module can name: it can only mismatch a claim
    subject = _text(row.get("subject")) or claim.names[0]
    own_name, own_effort = split_model_cell(subject)
    if own_effort is not None and normalise_name(subject) not in normalise_name(text):
        own_effort = None  # the qualifier is the reader's, not the source's
    quote = str(row.get("quoted_sentence") or "")
    value = str(row.get("value") or "")
    lines = [line for line in quote.splitlines() if value and value in line] or [quote]
    cells = [normalise_name(c) for line in lines for c in line.split("|")]
    if own_effort == level or any(level in _effort_levels_in(line) for line in lines) or any(
            _EFFORT_ALIASES.get(c, c) == level for c in cells
            if c in EFFORT_LEVELS or c in _EFFORT_ALIASES):
        return
    others = [o for o in subjects if o != own_name]

    def names(sentence: str, name: str) -> bool:
        said = f" {normalise_name(sentence)} "
        for other in sorted(others, key=len, reverse=True):
            if other != name and f" {name} " in f" {other} ":
                said = said.replace(f" {other} ", " ")  # "Claude Opus 5.5" is not "Claude Opus 5"
        return bool(name) and re.search(rf" {re.escape(name)} (?!\d)", said) is not None

    first = text.strip().splitlines()[0] if text.strip() else ""
    scoped = []
    if " | " not in first and not any(names(first, o) for o in others):
        scoped.append(first)
    if isinstance(stated, str) and (names(stated, own_name) or (
            names(stated, _label(claim)) and not any(names(stated, o) for o in others))):
        scoped.append(stated)
    if not any(level in _effort_levels_in(line) for line in scoped):
        raise ValueError(f"effort {level!r} is not stated for this value in the source region")


class LLMExtractor:
    """Reads prose through ``complete(prompt) -> str``, an injected model call.

    The prompt never shows the collector's value: the verifier reads independently.
    A reply that is not the requested JSON raises ``ExtractorError``.
    """

    def __init__(self, complete: Callable[[str], str], *, agent: str, model: str,
                 model_family: str, cache: LLMCache | None = None) -> None:
        self.complete = complete
        self.cache = cache
        self.actor = VerificationActor(agent=agent, model_family=model_family,
                                       method=f"llm-extract:{model}")

    def accepts(self, text: str) -> bool:
        return bool(text.strip())

    def extract(self, claim: Claim, text: str, *,
                cache_key: tuple[str, ...] | None = None) -> list[Reading]:
        prompt = LLM_PROMPT.format(label=claim.label or claim.field.replace("_", " "),
                                   names=", ".join(claim.names), text=text)
        reply, store_key = _load_reply(self.complete, self.cache, LLM_PROMPT, prompt, cache_key)
        try:
            cleaned = reply.strip()
            if cleaned.startswith("```json") and cleaned.endswith("```"):
                cleaned = cleaned[7:-3].strip()
            rows = json.loads(cleaned)
            if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
                raise ValueError("not a list of objects")
            subjects = [split_model_cell(str(r["subject"]))[0] for r in rows if r.get("subject")]
            for row in rows:
                quote = row.get("quoted_sentence")
                if not isinstance(quote, str) or not quote.strip() or \
                        normalise_name(quote) not in normalise_name(text):
                    raise ValueError("quoted_sentence is missing or is not verbatim source text")
                _check_effort_is_stated(claim, row, text, subjects)
            readings = [
                Reading(subject=_text(r.get("subject")) or claim.names[0],
                        value=_text(r.get("value")),
                        unit=_text(r.get("unit")),
                        conditions={k: _text(r.get(k)) for k in CONDITION_KEYS})
                for r in rows
            ]
            if not readings and claim.value is None:
                readings = [Reading(subject=claim.names[0], value=None)]
            if self.cache is not None and store_key:
                self.cache.put(store_key, reply)
            return readings
        except ValueError as exc:
            raise ExtractorError(f"unparseable reply from {self.actor.method}: {exc}") from exc


def _load_reply(complete: Callable[[str], str], cache: LLMCache | None, template: str,
                prompt: str, cache_key: tuple[str, ...] | None, *,
                bound: str = "") -> tuple[str, tuple[str, ...] | None]:
    """A cached reply, or a fresh ``complete(prompt)``.

    The stored key includes a hash of ``template``. The licence reader also
    passes ``bound``, the reading rule, the facet definition and the allowed
    values that were filled into the prompt. A change to any of them asks
    again. The caller stores the reply only after it parses.
    """
    store_key = None
    if cache_key:
        material = template if not bound else f"{template}\n{bound}"
        digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
        store_key = (f"prompt:{digest}", *cache_key)
    reply = cache.get(store_key) if cache is not None and store_key else None
    if reply is None:
        reply = complete(prompt)
    return reply, store_key


#: Source kinds whose text is a licence or terms document.
LICENCE_SOURCE_KINDS = frozenset({"licence_text", "provider_terms"})

LICENCE_PROMPT = """\
You are reading a licence or terms of use. The document does not name a model.
Answer one question from the source region only. Follow the reading rule.
When the reading rule and another instruction disagree, follow the reading rule.

Facet: {facet_id}
Definition: {definition}
Reading rule: {reading_rule}
Allowed values: {allowed}

Return only a JSON object with:
- "value": the value the reading rule gives. It must be one allowed value.
- "clauses": one or more verbatim quotations from the source region that support the value

Do not infer from the licence's name or from knowledge outside the region.
Every quotation must appear verbatim in the source region.
When the reading rule says the text does not address the facet, set "value" to "not_disclosed" and still quote one verbatim clause from the region.

Source region:
<<<
{text}
>>>
"""

_LICENSE_SPDX = re.compile(
    r"(?im)^[ \t]*license:\s*[\"']?([A-Za-z0-9][A-Za-z0-9_.+-]*)"
)
_LICENSE_LINK = re.compile(
    r"(?im)^[ \t]*license_link:\s*[\"']?(https?://\S+?)[\"']?\s*$"
)
#: SPDX ids for the shared generic texts. ``license: other`` is not here, so
#: it binds only when the page carries the licence URL or a ``license_link``.
SPDX_LICENCE_URLS: dict[str, tuple[str, ...]] = {
    "apache-2.0": (
        "https://www.apache.org/licenses/LICENSE-2.0",
        "https://www.apache.org/licenses/LICENSE-2.0.txt",
    ),
    "mit": ("https://opensource.org/license/mit",),
}


def _licence_allowed(facet) -> list[str]:
    """The values the registry admits for a licence facet, including ``unbounded``."""
    value_type = facet.value_type
    allowed: list[str] = list(value_type.values or ())
    if value_type.kind == "number":
        unit = f" in {facet.unit}" if facet.unit else ""
        allowed.append(f"a number{unit}")
        if value_type.unbounded:
            allowed.append("unbounded")
    return allowed


def _licence_inputs(claim: Claim) -> tuple[str, str, str, str]:
    """Facet id, definition, reading rule and allowed values filled into the prompt."""
    facet = default_registry().facet(claim.field)
    rule = licence_reading_rule(facet.id)
    allowed = ", ".join(_licence_allowed(facet))
    return facet.id, facet.definition, rule, allowed


def _licence_prompt(claim: Claim, text: str) -> tuple[str, str]:
    """The prompt, and the filled inputs the cache key hashes."""
    facet_id, definition, rule, allowed = _licence_inputs(claim)
    prompt = LICENCE_PROMPT.format(
        facet_id=facet_id,
        definition=definition,
        reading_rule=rule,
        allowed=allowed,
        text=text,
    )
    return prompt, f"{rule}\n{definition}\n{allowed}"


def _strip_fence(reply: str) -> str:
    cleaned = reply.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _as_licence_value(raw: Any) -> JsonValue:
    if raw is None or (isinstance(raw, str) and normalise_name(raw) == "not disclosed"):
        return None
    if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
        raise ValueError("value is not a licence value")
    return raw


def _licence_url_key(url: str) -> str:
    """Scheme, host case, a leading ``www.`` and a trailing ``.txt`` do not differ."""
    text = url.strip().strip("\"'")
    text = re.sub(r"^https?://", "", text, flags=re.I)
    text = re.sub(r"^www\.", "", text, flags=re.I)
    text = text.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    if text.casefold().endswith(".txt"):
        text = text[:-4]
    return text.casefold()


@cache
def _catalogue_ids() -> frozenset[str]:
    ids: set[str] = set()
    for group in _catalogue_model_aliases().values():
        ids.update(group)
    return frozenset(ids)


def _binding_name_tokens(names: Sequence[str], subject: str | None) -> list[str]:
    """Phrases that name this model: its display name or its repository id.

    A family name such as Gemma, Qwen or DeepSeek does not count. When the
    subject is a catalogue card, only that card's display name and repository
    id count, each as a whole phrase. A subject the catalogue does not hold
    uses the claim's names, still as whole phrases.
    """
    if subject and subject in _catalogue_ids():
        repo = normalise_name(subject.rsplit("/", 1)[-1])
        tokens = [repo] if repo else []
        for label, ids in _catalogue_display_names().items():
            if subject in ids and label:
                tokens.append(label)
        return list(dict.fromkeys(token for token in tokens if token))
    return [token for name in names if (token := normalise_name(name))]


def _page_names_subject(page: str, names: Sequence[str], subject: str | None = None) -> bool:
    """The page contains the display name or the repository id as a whole phrase."""
    haystack = f" {normalise_name(page)} "
    return any(
        f" {token} " in haystack for token in _binding_name_tokens(names, subject)
    )


def _page_names_licence(page: str, licence_url: str | None) -> bool:
    """The page names this licence source, not merely some ``license:`` field."""
    if not licence_url:
        return False
    if licence_url in page:
        return True
    bare = re.sub(r"^https?://", "", licence_url).rstrip("/")
    if bare and bare in page:
        return True
    source_key = _licence_url_key(licence_url)
    for match in _LICENSE_LINK.finditer(page):
        if _licence_url_key(match.group(1)) == source_key:
            return True
    for match in _LICENSE_SPDX.finditer(page):
        canonical = SPDX_LICENCE_URLS.get(match.group(1).casefold(), ())
        if any(_licence_url_key(url) == source_key for url in canonical):
            return True
    return False


def licence_is_bound(names: Sequence[str], pages: Sequence[str], licence_url: str | None, *,
                     subject: str | None = None) -> bool:
    """A licence is about the subject when another cited page names both.

    The page names the subject by its display name or repository id, as a
    whole phrase. It names this licence when it contains the licence URL, a
    ``license_link`` to that URL, or a ``license:`` SPDX id in
    :data:`SPDX_LICENCE_URLS` that maps to that URL.
    """
    return any(
        _page_names_subject(page, names, subject) and _page_names_licence(page, licence_url)
        for page in pages
    )


class LicenceExtractor:
    """Reads one ``licence.*`` value from a licence or terms document.

    It uses the same injected ``complete(prompt)``, cache and call budget as
    ``LLMExtractor``. The prompt gives the facet's definition, the reading
    rule for that facet, and the allowed values. It never shows the collector's
    value. A missing or non-verbatim
    clause is unparseable, so it is not evidence. A licence does not name the
    model: the reading's subject is the claim's name only when a binding page
    passes :func:`licence_is_bound`: the page names this model's display name
    or repository id, and names this licence source.
    """

    def __init__(self, complete: Callable[[str], str], *, agent: str, model: str,
                 model_family: str, cache: LLMCache | None = None) -> None:
        self.complete = complete
        self.cache = cache
        self.actor = VerificationActor(
            agent=agent, model_family=model_family, method=f"licence-extract:{model}",
        )

    def accepts(self, text: str) -> bool:
        # Selected only for a licence claim cited to a licence or terms source.
        return False

    def extract(self, claim: Claim, text: str, *,
                cache_key: tuple[str, ...] | None = None,
                bindings: Sequence[str] = (),
                licence_url: str | None = None) -> list[Reading]:
        prompt, bound = _licence_prompt(claim, text)
        reply, store_key = _load_reply(
            self.complete, self.cache, LICENCE_PROMPT, prompt, cache_key, bound=bound,
        )
        try:
            data = json.loads(_strip_fence(reply))
            if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
                data = data[0]
            if not isinstance(data, dict):
                raise ValueError("not an object")
            clauses = data.get("clauses")
            if not isinstance(clauses, list) or not clauses:
                raise ValueError("clauses are missing")
            normal_text = normalise_name(text)
            for clause in clauses:
                if not isinstance(clause, str) or not clause.strip() \
                        or normalise_name(clause) not in normal_text:
                    raise ValueError("quoted clause is missing or is not verbatim source text")
            value = _as_licence_value(data.get("value"))
        except (ValueError, TypeError) as exc:
            raise ExtractorError(f"unparseable reply from {self.actor.method}: {exc}") from exc
        if self.cache is not None and store_key:
            self.cache.put(store_key, reply)
        subject = claim.names[0] if licence_is_bound(
            claim.names, bindings, licence_url, subject=claim.subject,
        ) else None
        shown: JsonValue = None if value is None else str(value)
        unit = None
        if shown is not None and parse_quantity(shown) is not None:
            unit = default_registry().facet(claim.field).unit
        return [Reading(subject=subject, value=shown, unit=unit)]


def claude_extractor(*, cache: LLMCache | None = None,
                     complete: Callable[[str], str] | None = None,
                     max_calls: int = 400) -> LLMExtractor:
    """The independent Claude Sonnet reader used by ``modelspec verify``."""
    return LLMExtractor(
        complete or ClaudeCLICompletion(max_calls=max_calls),
        agent="claude-cli",
        model="claude-sonnet-5",
        model_family="anthropic",
        cache=cache or LLMCache(),
    )


OLLAMA_URL = "http://100.127.37.30:11434/api/chat"
MISTRAL_MODEL = "mistral-large:123b-instruct-2411-q4_K_M"
#: Ollama's ``format: json`` constrains a reply to one JSON object, so a bare
#: array cannot be returned: Mistral then reports only the first value in a
#: region. This system turn asks for the array inside an object; ``LLM_PROMPT``
#: itself is sent unchanged.
OLLAMA_JSON_MODE = (
    'Your reply must be one JSON object of the form {"values": [...]}, where the '
    "array is exactly the JSON array the user asks for, with one element per value."
)


def _as_array(content: str) -> str:
    """A JSON-mode reply as the array ``LLM_PROMPT`` asks for.

    Ollama's ``format: json`` tends to wrap the array in an object, or to return
    one row bare. ``{"rows": [...]}`` (any single key) gives its array, one row
    gives a one-row array, ``{}`` gives ``[]``. Anything else is returned as is,
    for ``LLMExtractor`` to accept or refuse.
    """
    try:
        data = json.loads(content)
    except ValueError:
        return content
    if isinstance(data, dict):
        lists = [v for v in data.values() if isinstance(v, list)]
        if not data:
            data = []
        elif len(data) == 1 and len(lists) == 1:
            data = lists[0]
        elif "quoted_sentence" in data:
            data = [data]
    return json.dumps(data, ensure_ascii=False) if isinstance(data, list) else content


class OllamaChatCompletion:
    """Call a model served by ollama's ``/api/chat`` at temperature 0, in JSON mode."""

    def __init__(self, *, url: str | None = None, model: str = MISTRAL_MODEL,
                 max_calls: int = 400, timeout: float = 900) -> None:
        self.url = url or os.environ.get("MODELSPEC_OLLAMA_URL") or OLLAMA_URL
        self.model = model
        self.max_calls = max_calls
        self.timeout = timeout
        self.calls = 0

    def __call__(self, prompt: str) -> str:
        if self.calls >= self.max_calls:
            raise LLMCallBudgetExceededError(
                f"stopped before exceeding the {self.max_calls}-call budget"
            )
        self.calls += 1
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": OLLAMA_JSON_MODE},
                         {"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }
        request = urllib.request.Request(
            self.url, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310
                envelope = json.loads(response.read())
        except (OSError, ValueError) as exc:
            raise ExtractorError(f"ollama at {self.url} failed: {exc}") from exc
        try:
            content = envelope["message"]["content"]
            if not isinstance(content, str):
                raise TypeError("content is not text")
        except (KeyError, TypeError) as exc:
            raise ExtractorError(f"ollama returned an invalid chat envelope: {exc}") from exc
        return _as_array(content)


def mistral_extractor(*, cache: LLMCache | None = None,
                      complete: Callable[[str], str] | None = None,
                      max_calls: int = 400) -> LLMExtractor:
    """The local Mistral Large reader: a third model family, for Claude-collected values."""
    return LLMExtractor(
        complete or OllamaChatCompletion(max_calls=max_calls),
        agent="ollama",
        model=MISTRAL_MODEL,
        model_family="mistral",
        # The namespace names the request shape too: a reply cached before the
        # JSON-mode system turn read only one value per region.
        cache=cache or LLMCache(namespace=f"ollama:{MISTRAL_MODEL}:values-object"),
    )


def claude_licence_extractor(*, cache: LLMCache | None = None,
                             complete: Callable[[str], str] | None = None,
                             max_calls: int = 400) -> LicenceExtractor:
    """Licence reader on the same Claude CLI completion as ``claude_extractor``."""
    return LicenceExtractor(
        complete or ClaudeCLICompletion(max_calls=max_calls),
        agent="claude-cli",
        model="claude-sonnet-5",
        model_family="anthropic",
        cache=cache if cache is not None else LLMCache(namespace="licence"),
    )


def mistral_licence_extractor(*, cache: LLMCache | None = None,
                              complete: Callable[[str], str] | None = None,
                              max_calls: int = 400) -> LicenceExtractor:
    """Licence reader on the same local Mistral completion as ``mistral_extractor``."""
    return LicenceExtractor(
        complete or OllamaChatCompletion(max_calls=max_calls),
        agent="ollama",
        model=MISTRAL_MODEL,
        model_family="mistral",
        cache=cache if cache is not None else LLMCache(
            namespace=f"ollama:{MISTRAL_MODEL}:licence"),
    )


def _text(value: Any) -> str | None:
    return None if value is None else str(value)


def deterministic_extractors() -> list[Extractor]:
    return [StructuredDataExtractor(), OfferingPriceExtractor(), SubscriptionPageExtractor(),
            TableExtractor(), TransposedTableExtractor(),
            GovernanceProseExtractor(), KeyValueExtractor(), ModelPageExtractor()]


# --- regions -------------------------------------------------------------------------------------


class Regions(Protocol):
    def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
        """The cited region's text in that retained copy, or ``None`` when unreachable."""


class StoredRegions:
    """Regions read from retained copies in a ``CopyStore``.

    The copy is normalised with its source's rules but with volatile text (dates,
    times) kept: a date the verifier must compare is not boilerplate here.
    """

    def __init__(self, store: CopyStore, sources: Mapping[str, Source]) -> None:
        self.store = store
        self.sources = sources

    def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
        source = self.sources.get(source_id)
        region = next((r for r in source.cited_regions if r.id == region_id), None) \
            if source else None
        if source is None or region is None or not self.store.has(copy_ref):
            return None
        rules = replace(NORMALISERS[source.normaliser], strip_volatile=False)
        try:
            doc = normalise_document(self.store.get(copy_ref), rules)
            kind = "heading" if region.locator.kind == "heading_anchor" else region.locator.kind
            return select_region(doc, Locator(kind, region.locator.value))
        except (UnsupportedContentError, ValueError):
            return None

    def source_kind(self, source_id: str) -> str | None:
        source = self.sources.get(source_id)
        return None if source is None else source.kind

    def source_url(self, source_id: str) -> str | None:
        source = self.sources.get(source_id)
        return None if source is None else str(source.url)


# --- comparison ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class Diff:
    field: str
    expected: JsonValue
    found: JsonValue

    def to_dict(self) -> dict[str, JsonValue]:
        return {"field": self.field, "expected": self.expected, "found": self.found}


_TRUE = frozenset({"yes", "true", "supported", "available", "y", "✓", "✔"})
_FALSE = frozenset({
    "no", "none", "false", "not supported", "unsupported", "unavailable", "n", "✗", "✘",
})


def _show(claim: Claim) -> JsonValue:
    if isinstance(claim.value, (int, float)) and not isinstance(claim.value, bool):
        return f"{claim.value} {claim.unit}" if claim.unit else str(claim.value)
    return claim.value


@cache
def _catalogue_model_aliases() -> Mapping[str, frozenset[str]]:
    """Canonical model IDs indexed by names published on their cards."""
    return _catalogue_model_index()[0]


@cache
def _catalogue_display_names() -> Mapping[str, frozenset[str]]:
    """Canonical model IDs indexed by their cards' display names only."""
    return _catalogue_model_index()[1]


@cache
def _catalogue_model_index() -> tuple[Mapping[str, frozenset[str]], Mapping[str, frozenset[str]]]:
    aliases: dict[str, set[str]] = {}
    display: dict[str, set[str]] = {}
    for path in (REPO_ROOT / "models").rglob("*.md"):
        model_id = display_name = None
        with path.open(encoding="utf-8", errors="replace") as card:
            for line in card:
                if line.startswith("model_id:"):
                    model_id = line.split(":", 1)[1].strip().strip("'\"")
                elif line.startswith("display_name:"):
                    display_name = line.split(":", 1)[1].strip().strip("'\"")
                elif line.strip() == "---" and model_id is not None:
                    break
        if not model_id:
            continue
        for alias in (model_id, model_id.rsplit("/", 1)[-1], display_name):
            if alias:
                aliases.setdefault(normalise_name(alias), set()).add(model_id)
        if display_name:
            display.setdefault(normalise_name(display_name), set()).add(model_id)
    return ({alias: frozenset(ids) for alias, ids in aliases.items()},
            {name: frozenset(ids) for name, ids in display.items()})


def _catalogue_model_matches(published: str) -> frozenset[str]:
    """The cards a published name can mean. When it matches several, a card whose
    display name is exactly that name is the one (MODEL-205: "Claude Haiku 4.5" is
    the dated card so named, not the alias card whose ID stem reads the same)."""
    raw = re.sub(r"(?i)\s+model$", "", published.strip())
    label = normalise_name(raw)
    matches = _catalogue_model_aliases().get(label, frozenset())
    if len(matches) > 1:
        # A literal ID ("claude-haiku-4-5") is that card; a name is the card so named.
        literal = frozenset(m for m in matches
                            if raw.casefold() in {m.casefold(), m.rsplit("/", 1)[-1].casefold()})
        named = _catalogue_display_names().get(label, frozenset()) & matches
        for narrowed in (literal, named):
            if len(narrowed) == 1:
                return narrowed
    return matches


def _catalogue_model_id(published: str) -> str | None:
    matches = _catalogue_model_matches(published)
    return next(iter(matches)) if len(matches) == 1 else None


def _value_diff(claim: Claim, reading: Reading) -> Diff | None:
    expected, value = _show(claim), claim.value
    if reading.value is None:
        return None if value is None else Diff("value", expected, None)
    if isinstance(value, bool):
        s = reading.value.strip().casefold()
        explicit_no_training = (
            "train" in s
            and any(phrase in s for phrase in (
                "do not use", "does not use", "will not use", "won't use", "not used",
                "never use",
            ))
        )
        explicit_available = (
            (
                "zero data retention" in s
                and not any(x in s for x in ("not available", "unavailable"))
            )
            or ("baa" in s and any(x in s for x in ("available", "eligible")))
        )
        found = (True if s in _TRUE or explicit_available
                 else False if s in _FALSE or explicit_no_training else None)
        return None if found is value else Diff("value", expected, reading.value)
    if isinstance(value, (int, float)):
        if value == 0 and claim.unit == "days" and normalise_name(reading.value) in {
            "none", "no retention", "zero data retention",
        }:
            return None
        q = parse_quantity(reading.value, reading.unit)
        if q is None:
            return Diff("value", expected, reading.value)
        if claim.field in {"offering.subscription.price", "offering.subscription.price_cny"} \
                or (claim.field.startswith("offering.price.")
                    and unit_id(q.unit) == unit_id(claim.unit)):
            # A list price is exact: $19.99 is not $20, and $0.25 is not 0.2
            # (MODEL-235; a rounding tolerance would hide a price change).
            return None if Decimal(str(q.number)) == Decimal(str(value)) \
                else Diff("value", expected, q.show())
        if numbers_agree(value, claim.unit, q):
            return None
        unit_differs = claim.unit is not None and claim.unit != q.unit
        return Diff("unit" if unit_differs else "value", expected, q.show())
    if isinstance(value, list):
        if not value and normalise_name(reading.value) in _FALSE:
            return None
        published_items = {
            s.strip() for s in re.split(r",|;|\band\b", reading.value) if s.strip()
        }
        found_items = {item.casefold() for item in published_items}
        claimed_items = {str(v).strip().casefold() for v in value}
        if claimed_items and all("/" in item for item in claimed_items) \
                and claim.field != "offering.subscription.families_covered":
            # models_covered holds catalogue IDs, so a published model the
            # catalogue lacks cannot be claimed there; it is dropped. Anywhere
            # else, and for an ambiguous label, the name is kept and must match.
            found_items = set()
            for item in published_items:
                matches = _catalogue_model_matches(item)
                if len(matches) == 1:
                    found_items.add(next(iter(matches)).casefold())
                elif matches or claim.field != "offering.subscription.models_covered":
                    found_items.add(normalise_name(re.sub(r"(?i)\s+model$", "", item)))
        return None if found_items == claimed_items else Diff("value", expected, reading.value)
    expected_name = normalise_name(str(value))
    found_name = normalise_name(reading.value)
    if expected_name == "not offered" and found_name in {
        "n a", "na", "not available", "not supported",
    }:
        return None
    if expected_name == found_name:
        return None
    if expected_name == "type 2" and (
        "type 2" in found_name or "type ii" in found_name
    ):
        return None
    return Diff("value", expected, reading.value)


def _diffs(claim: Claim, reading: Reading) -> list[Diff]:
    diffs = [d for d in [_value_diff(claim, reading)] if d is not None]
    name_effort = split_model_cell(reading.subject)[1] if reading.subject else None
    for key in CONDITION_KEYS:
        claimed = _condition(key, claim.conditions.get(key))
        found = _condition(key, reading.conditions.get(key))
        if key == "effort" and found is None:
            found = name_effort
        if key == "date" and claimed is None:
            continue  # a date the claim does not carry is not checked
        if key == "harness" and claimed == UNREGISTERED and found is not None \
                and default_registry().resolve_harness(found) == UNREGISTERED:
            continue  # the registry reports a named, unregistered harness as `unregistered`
        if claimed != found:
            diffs.append(Diff(key, claim.conditions.get(key), found))
    return diffs


def compare(claim: Claim, readings: Sequence[Reading]) -> list[Diff]:
    """The diffs between a claim and what a region says; empty when it agrees."""
    if not readings:
        return [Diff("value", _show(claim), None)]
    names = {
        identity
        for name in claim.names
        for identity in (normalise_name(name), split_model_cell(name)[0])
    }
    own = [r for r in readings if r.subject and split_model_cell(r.subject)[0] in names]
    others = [r for r in readings if r not in own and r.subject]
    sibling = next((r for r in others if not _diffs(claim, r)), None)
    expected_name = claim.names[0]
    if not own:
        return [Diff("model", expected_name, sibling.subject if sibling else None)]
    candidates = [_diffs(claim, r) for r in own]
    if any(not c for c in candidates):
        return []
    best = min(candidates, key=lambda c: (any(d.field in ("value", "unit") for d in c), len(c)))
    if sibling and any(d.field in ("value", "unit") for d in best):
        best = [*best, Diff("model", expected_name, sibling.subject)]
    return best


# --- verification --------------------------------------------------------------------------------

#: The verifier recorded for an unreachable outcome: no extractor ran, a lookup did.
REGION_LOOKUP = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                                  method="region-lookup@1")


@dataclass(frozen=True)
class Result:
    target: TargetRef
    outcome: Outcome
    verification: Verification | None = None
    diffs: tuple[Diff, ...] = ()
    #: Why a claim was skipped, or which region was unreachable.
    reason: str | None = None


def _verification(claim: Claim, actor: VerificationActor, outcome: str, today: date,
                  diffs: Sequence[Diff] = ()) -> Verification:
    """Raises ``ValidationError`` when ``actor`` is not independent of the collector."""
    return Verification(
        target=VerificationTarget(
            kind=claim.target.kind,
            id=claim.target.id,
            value_hash=value_hash(claim.value),
        ),
        collector=claim.collector,
        verifier=actor,
        method=actor.method,
        outcome=outcome,
        date=today,
        diff=json.dumps([d.to_dict() for d in diffs], ensure_ascii=False) if diffs else None,
    )


def _independent(claim: Claim, actor: VerificationActor, today: date) -> bool:
    """A second key: another agent or family (parse rule), and another family unless
    deterministic (``Verification.independent``)."""
    try:
        return _verification(claim, actor, "verified", today).independent
    except ValidationError:
        return False


def _number_agrees(expected: int | float, found: object, unit: str | None = None) -> bool:
    quantity = parse_quantity(str(found), unit)
    return quantity is not None and numbers_agree(expected, unit, quantity)


def _verify_evidence_reading(
    claim: Claim,
    regions: Regions,
    extractors: Sequence[Extractor],
    *,
    today: date,
) -> Result:
    """Verify a score and its decision-affecting metadata across cited regions."""
    expected = claim.value
    assert isinstance(expected, dict)
    ordered = sorted(extractors, key=lambda e: e.actor.model_family != DETERMINISTIC)
    own_names = {
        identity
        for name in claim.names
        for identity in (normalise_name(name), split_model_cell(name)[0])
    }
    benchmark_names = {normalise_name(claim.field), normalise_name(claim.label or "")}
    confirmed: set[str] = set()
    found_flags: set[str] = set()
    actor: VerificationActor | None = None
    reachable = False
    reasons: list[str] = []
    diffs: list[Diff] = []

    for source in claim.sources:
        for region_id in source.cited_regions:
            where = f"{source.source_id}#{region_id}"
            text = regions.text(source.source_id, source.snapshot_ref, region_id)
            if text is None:
                reasons.append(f"unreachable:{where}")
                continue
            reachable = True
            for extractor in [
                item
                for item in ordered
                if item.accepts(text) and _independent(claim, item.actor, today)
            ]:
                try:
                    readings = extractor.extract(claim, text)
                except ExtractorError as exc:
                    reasons.append(f"extractor_error:{where}: {exc}")
                    continue
                for reading in readings:
                    if not isinstance(reading.value, dict) or not reading.subject:
                        continue
                    subject = split_model_cell(reading.subject)[0]
                    own = subject in own_names
                    benchmark = normalise_name(reading.subject) in benchmark_names
                    if not own and not benchmark:
                        continue
                    actor = actor or extractor.actor
                    found = reading.value
                    if own and "score" in found:
                        scalar_claim = replace(claim, value=expected["score"])
                        scalar_reading = replace(reading, value=found["score"])
                        score_diffs = _diffs(scalar_claim, scalar_reading)
                        if score_diffs:
                            diffs.extend(score_diffs)
                        else:
                            confirmed.add("score")
                    if own and expected.get("interval") is not None and "interval" in found:
                        wanted = expected["interval"]
                        actual = found["interval"]
                        if (
                            isinstance(wanted, list)
                            and isinstance(actual, list)
                            and len(wanted) == len(actual) == 2
                            and all(
                                _number_agrees(want, got, claim.unit)
                                for want, got in zip(wanted, actual, strict=True)
                            )
                        ):
                            confirmed.add("interval")
                        else:
                            diffs.append(Diff("interval", wanted, actual))
                    if own and expected.get("n") is not None and "n" in found:
                        if _number_agrees(expected["n"], found["n"]):
                            confirmed.add("n")
                        else:
                            diffs.append(Diff("n", expected["n"], found["n"]))
                    found_flags.update(str(flag) for flag in found.get("quality_flags", []))

    expected_flags = set(expected.get("quality_flags") or [])
    if found_flags == expected_flags:
        confirmed.add("quality_flags")
    elif found_flags or expected_flags:
        diffs.append(Diff("quality_flags", sorted(expected_flags), sorted(found_flags)))
    required = {"score", "quality_flags"}
    required.update(key for key in ("interval", "n") if expected.get(key) is not None)
    if required <= confirmed and actor is not None:
        return Result(claim.target, "verified", _verification(claim, actor, "verified", today))
    for key in sorted(required - confirmed):
        if not any(diff.field == key for diff in diffs):
            diffs.append(Diff(key, expected.get(key), None))
    if actor is not None:
        return Result(
            claim.target,
            "mismatch",
            _verification(claim, actor, "mismatch", today, diffs),
            tuple(diffs),
        )
    if not reachable:
        return Result(
            claim.target,
            "unreachable",
            _verification(claim, REGION_LOOKUP, "unreachable", today),
            reason="; ".join(reasons),
        )
    return Result(claim.target, "skipped", reason="; ".join(reasons))


def _source_kind(regions: Regions, source_id: str) -> tuple[bool, str | None]:
    """``(tracked, kind)``. Untracked regions predate source kinds."""
    method = getattr(regions, "source_kind", None)
    if not callable(method):
        return False, None
    return True, method(source_id)


def _facet_or_none(field: str):
    try:
        return default_registry().facet(field)
    except KeyError:
        return None


def _absence_block(claim: Claim, regions: Regions, source_id: str) -> list[Diff] | None:
    """Mismatch when an absence is cited to a source kind the facet does not permit.

    A source whose kind is unknown still supports a non-licence absence, so
    registries written before ``kind`` keep verifying. A ``licence.*`` absence
    needs an explicit permitted kind: a README that never states the term is
    not evidence that the licence is silent.
    """
    if claim.value is not None:
        return None
    facet = _facet_or_none(claim.field)
    if facet is None:
        return None
    permitted = list(facet.permitted_source_kinds)
    tracked, kind = _source_kind(regions, source_id)
    if kind in permitted:
        return None
    if not claim.field.startswith("licence.") and (not tracked or kind is None):
        return None
    return [Diff("source_kind", permitted, kind if kind is not None else "unknown")]


def _readers_for(extractors: Sequence[Extractor], claim: Claim, text: str,
                 kind: str | None) -> list[Extractor]:
    """Who may read this region.

    A ``licence.*`` claim is read only from a source kind in that facet's
    ``permitted_source_kinds``, and only by ``LicenceExtractor``. Any other
    cited region is a binding page. It is not a reading, for a known value or
    an absence. Deterministic extractors still read a ``licence_text`` source
    for every other claim, including ``model.weights_openness`` and ``origin.*``.
    """
    if claim.field.startswith("licence."):
        facet = _facet_or_none(claim.field)
        permitted = set(facet.permitted_source_kinds) if facet is not None else set()
        if kind not in permitted:
            return []
        return [extractor for extractor in extractors if isinstance(extractor, LicenceExtractor)]
    chosen = []
    for extractor in extractors:
        if isinstance(extractor, LicenceExtractor):
            continue
        if extractor.accepts(text):
            chosen.append(extractor)
    return chosen


def _binding_pages(claim: Claim, regions: Regions, source_id: str, region_id: str) -> list[str]:
    """Text of the claim's other cited regions: the pages that can bind a licence."""
    pages = []
    for source in claim.sources:
        for cited in source.cited_regions:
            if source.source_id == source_id and cited == region_id:
                continue
            text = regions.text(source.source_id, source.snapshot_ref, cited)
            if text:
                pages.append(text)
    return pages


def verify(claim: Claim, regions: Regions, extractors: Sequence[Extractor], *,
           today: date) -> Result:
    """Re-read ``claim`` from each cited region of its sources and compare.

    Deterministic extractors are tried before the rest, whatever the order given;
    the first that accepts a region and is independent of the collector reads it.
    A ``licence.*`` claim is the exception: only ``LicenceExtractor`` reads it,
    and only a source kind in that facet's ``permitted_source_kinds`` is a
    reading. Its other cited regions are binding pages. Verified if any
    reading confirms the value; otherwise the first mismatch.
    """
    if isinstance(claim.value, dict) and "score" in claim.value:
        return _verify_evidence_reading(claim, regions, extractors, today=today)

    ordered = sorted(extractors, key=lambda e: e.actor.model_family != DETERMINISTIC)
    reachable = False
    mismatch: tuple[VerificationActor, list[Diff]] | None = None
    reasons: list[str] = []
    for source in claim.sources:
        _, kind = _source_kind(regions, source.source_id)
        for region_id in source.cited_regions:
            where = f"{source.source_id}#{region_id}"
            text = regions.text(source.source_id, source.snapshot_ref, region_id)
            if text is None:
                reasons.append(f"unreachable:{where}")
                continue
            reachable = True
            accepting = _readers_for(ordered, claim, text, kind)
            independent = [e for e in accepting if _independent(claim, e.actor, today)]
            if not independent:
                if claim.value is None and claim.field.startswith("licence."):
                    blocked = _absence_block(claim, regions, source.source_id)
                    if blocked:
                        found = blocked[0].found
                        reasons.append(
                            f"absence_source_kind:{where}: {found} is not a permitted source kind"
                        )
                        mismatch = mismatch or (REGION_LOOKUP, blocked)
                        continue
                reasons.append("no_independent_extractor" if accepting else f"no_extractor:{where}")
                continue
            for extractor in independent:
                try:
                    if isinstance(extractor, LicenceExtractor):
                        url_of = getattr(regions, "source_url", None)
                        readings = extractor.extract(
                            claim,
                            text,
                            cache_key=(source.snapshot_ref, region_id, claim.field),
                            bindings=_binding_pages(claim, regions, source.source_id, region_id),
                            licence_url=url_of(source.source_id) if callable(url_of) else None,
                        )
                    elif isinstance(extractor, LLMExtractor):
                        readings = extractor.extract(
                            claim,
                            text,
                            cache_key=(source.snapshot_ref, region_id, claim.field,
                                       *claim.names),
                        )
                    else:
                        readings = extractor.extract(claim, text)
                except ExtractorError as exc:
                    reasons.append(f"extractor_error:{where}: {exc}")
                    continue
                diffs = compare(claim, readings)
                if not diffs:
                    blocked = _absence_block(claim, regions, source.source_id)
                    if blocked:
                        found = blocked[0].found
                        reasons.append(
                            f"absence_source_kind:{where}: {found} is not a permitted source kind"
                        )
                        mismatch = mismatch or (extractor.actor, blocked)
                        continue
                    return Result(claim.target, "verified",
                                  _verification(claim, extractor.actor, "verified", today))
                mismatch = mismatch or (extractor.actor, diffs)

    if mismatch is not None:
        actor, diffs = mismatch
        return Result(claim.target, "mismatch",
                      _verification(claim, actor, "mismatch", today, diffs), tuple(diffs))
    reason = "; ".join(reasons)
    if not reachable:
        if not _independent(claim, REGION_LOOKUP, today):
            return Result(claim.target, "skipped", reason="no_independent_extractor")
        return Result(claim.target, "unreachable",
                      _verification(claim, REGION_LOOKUP, "unreachable", today), reason=reason)
    return Result(claim.target, "skipped", reason=reason)


# --- the log -------------------------------------------------------------------------------------


class VerificationLog:
    """``verification/*.jsonl``: append-only; the latest outcome per target wins."""

    def __init__(self, directory: str | Path = DEFAULT_DIRECTORY) -> None:
        self.directory = Path(directory)
        self.path = self.directory / "log.jsonl"

    def append(self, verification: Verification) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(verification.model_dump_json() + "\n")

    def records(self) -> list[Verification]:
        records = []
        for path in sorted(self.directory.glob("*.jsonl")):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip():
                    with private_errors(path, line=number):
                        records.append(Verification.model_validate_json(line))
        return records

    def latest(self) -> dict[tuple[str, str], Verification]:
        """Latest ``date`` wins; on a tie, the later line (as ``decision.snapshot`` reads it).

        A record that does not count (a same-family ``verified``) is skipped.
        """
        latest: dict[tuple[str, str], Verification] = {}
        for record in self.records():
            if not record.counts:
                continue
            key = _key(record.target)
            if key not in latest or record.date >= latest[key].date:
                latest[key] = record
        return latest

    def requarantined(self) -> list[VerificationTarget]:
        """Values a same-family ``verified`` vouches for that no counting record admits.

        Keyed by target and checked value, as ``decision.snapshot`` admits them:
        what MODEL-159's family rule keeps out until another family verifies it.
        """
        vouched: dict[tuple[str, str, str], VerificationTarget] = {}
        counting: dict[tuple[str, str, str], Verification] = {}
        for record in self.records():
            key = (record.target.kind, record.target.id, record.target.value_hash)
            if not record.counts:
                vouched[key] = record.target
            elif key not in counting or record.date >= counting[key].date:
                counting[key] = record
        return [target for key, target in sorted(vouched.items())
                if key not in counting or counting[key].outcome != "verified"]

    def is_quarantined(self, target: TargetRef | str) -> bool:
        record = self.latest().get(_key(target_ref(target)))
        return record is None or record.quarantined

    def quarantined_values(self, targets: Iterable[TargetRef | str] | None = None
                           ) -> list[TargetRef | VerificationTarget]:
        """Quarantined targets: of ``targets`` (never-verified ones included), else of the log."""
        latest = self.latest()
        if targets is None:
            return [r.target for key, r in sorted(latest.items()) if r.quarantined]
        refs = [target_ref(t) for t in targets]
        return [t for t in refs if _key(t) not in latest or latest[_key(t)].quarantined]


def is_quarantined(target: TargetRef | str, *, directory: str | Path = DEFAULT_DIRECTORY) -> bool:
    return VerificationLog(directory).is_quarantined(target)


def quarantined_values(targets: Iterable[TargetRef | str] | None = None, *,
                       directory: str | Path = DEFAULT_DIRECTORY
                       ) -> list[TargetRef | VerificationTarget]:
    return VerificationLog(directory).quarantined_values(targets)


# --- the queue -----------------------------------------------------------------------------------


@dataclass
class _Pending:
    claim: Claim | None = None
    trigger: Literal["new", "changed"] | None = None
    copies: dict[str, str] = field(default_factory=dict)
    last: dict[str, Any] | None = None


class Queue:
    """``verification/queue/events.jsonl``: what to verify, and what to re-crawl."""

    def __init__(self, directory: str | Path = DEFAULT_DIRECTORY) -> None:
        self.directory = Path(directory)
        self.path = self.directory / "queue" / "events.jsonl"

    def _append(self, events: Iterable[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            for event in events:
                fh.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")

    def file(self, claim: Claim, *, at: datetime) -> None:
        """A collector files a new or re-collected value: verify it before first use."""
        self._append([{"event": "collected", "at": at.isoformat(), "claim": claim.to_dict()}])

    def requeue(self, changed: RecheckReport | Iterable[str | TargetRef], *, at: datetime) -> None:
        """Re-verify what change detection re-queued, against each source's new copy."""
        copies: dict[str, str] = {}
        if isinstance(changed, RecheckReport):
            copies = {sid: st.snapshot.copy_ref for sid, st in changed.states.items()
                      if st.snapshot is not None}
            changed = changed.requeue
        self._append({"event": "changed", "at": at.isoformat(),
                      "target": target_ref(ref).model_dump(), "copies": copies}
                     for ref in changed)

    def checked(self, result: Result, *, at: datetime) -> None:
        self._append([{"event": "checked", "at": at.isoformat(),
                       "target": result.target.model_dump(), "outcome": result.outcome,
                       "diff": [d.to_dict() for d in result.diffs]}])

    def _state(self) -> dict[tuple[str, str], _Pending]:
        state: dict[tuple[str, str], _Pending] = {}
        if not self.path.is_file():
            return state
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event["event"] == "collected":
                claim = Claim.from_dict(event["claim"])
                state[_key(claim.target)] = _Pending(claim, "new", {}, event)
                continue
            entry = state.setdefault(_key(TargetRef.model_validate(event["target"])), _Pending())
            entry.last = event
            if event["event"] == "changed":
                entry.trigger = entry.trigger or "changed"
                entry.copies.update(event.get("copies") or {})
            elif event["event"] == "checked":
                entry.trigger, entry.copies = None, {}
        return state

    def pending(self, *, changed_only: bool = False) -> tuple[list[Claim], list[TargetRef]]:
        """Claims to verify (each source pinned to its newest copy), and re-queued refs
        no collector has filed a claim for."""
        claims, unknown = [], []
        for key, entry in self._state().items():
            if entry.trigger is None or (changed_only and entry.trigger != "changed"):
                continue
            if entry.claim is None:
                unknown.append(TargetRef(kind=key[0], id=key[1]))
                continue
            sources = tuple(
                s.model_copy(update={"snapshot_ref": entry.copies[s.source_id]})
                if s.source_id in entry.copies else s
                for s in entry.claim.sources
            )
            claims.append(replace(entry.claim, sources=sources))
        return claims, unknown

    def filed(self) -> dict[tuple[str, str], Claim]:
        """The latest claim a collector filed for each target, keyed ``(kind, id)``."""
        return {key: entry.claim for key, entry in self._state().items()
                if entry.claim is not None}

    def recrawl_requests(self) -> list[tuple[TargetRef, str]]:
        """Targets whose last check failed and that no collector has filed again."""
        return [
            (TargetRef(kind=key[0], id=key[1]), entry.last["outcome"])
            for key, entry in self._state().items()
            if entry.last and entry.last["event"] == "checked"
            and entry.last["outcome"] != "verified"
        ]


# --- a run ---------------------------------------------------------------------------------------


@dataclass
class RunReport:
    changed_only: bool
    results: list[Result] = field(default_factory=list)
    #: Re-queued refs with no filed claim: nothing to verify them against.
    unknown: list[TargetRef] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        counts = dict.fromkeys(("verified", "mismatch", "unreachable", "skipped"), 0)
        for r in self.results:
            counts[r.outcome] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "changed_only": self.changed_only,
            "counts": self.counts,
            "results": [
                {"target": ref_str(r.target), "outcome": r.outcome,
                 "diff": [d.to_dict() for d in r.diffs], "reason": r.reason,
                 "verifier": r.verification.verifier.model_dump() if r.verification else None}
                for r in self.results
            ],
            "unknown": [ref_str(t) for t in self.unknown],
        }


def ref_str(target: TargetRef) -> str:
    return f"{target.kind}:{target.id}"


def run(queue: Queue, log: VerificationLog, regions: Regions, extractors: Sequence[Extractor],
        *, today: date, changed_only: bool = False, at: datetime | None = None) -> RunReport:
    """Verify what is queued; log every outcome and mark it checked. Skipped claims stay
    queued, unlogged and so quarantined."""
    at = at or datetime.now(UTC)
    claims, unknown = queue.pending(changed_only=changed_only)
    report = RunReport(changed_only, unknown=unknown)
    for claim in claims:
        result = verify(claim, regions, extractors, today=today)
        report.results.append(result)
        if result.verification is not None:
            log.append(result.verification)
            queue.checked(result, at=at)
    return report


__all__ = [
    "Claim", "ClaudeCLICompletion", "CONDITION_KEYS", "Diff", "Extractor", "ExtractorError",
    "GovernanceProseExtractor", "KeyValueExtractor", "LLMCache", "LLMCallBudgetExceededError",
    "LLMExtractor", "MISTRAL_MODEL", "ModelPageExtractor", "OLLAMA_URL", "OfferingPriceExtractor",
    "OLLAMA_JSON_MODE", "OllamaChatCompletion", "Quantity", "Queue", "Reading",
    "Regions", "Result",
    "RunReport", "StoredRegions", "StructuredDataExtractor", "SubscriptionPageExtractor",
    "TableExtractor", "TOLERANCE_RULE",
    "UNITS", "VerificationLog", "compare",
    "claude_extractor", "deterministic_extractors", "is_quarantined", "load_sources",
    "mistral_extractor",
    "numbers_agree",
    "parse_quantity", "quarantined_values", "run", "split_model_cell", "target_ref", "unit_id",
    "verify",
]
