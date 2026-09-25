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
or the network on its own. Each extractor's actor (agent, model family,
method) is the verifier the log records, and ``decision.model.Verification``
refuses one that matches the collector in both agent and model family.

Outcomes are ``verified``, ``mismatch`` (with a structured diff) and
``unreachable`` (the copy, source or region is missing). A claim no
independent extractor could read is ``skipped``: nothing is logged and it
stays queued. Anything whose latest logged outcome is not ``verified``, and
anything never verified, is **quarantined**.

Files, under ``verification/`` at the repository root:

- ``log.jsonl``: the verification log, append-only, one
  ``decision.model.Verification`` per line. The latest outcome per target and
  checked value wins: latest ``date``, and on a tie the later line (the rule
  ``decision.snapshot`` applies when it reads ``verification/log.jsonl``).
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
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import JsonValue, ValidationError

from decision.model import (
    SourceRef,
    TargetRef,
    Verification,
    VerificationActor,
    VerificationTarget,
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
            value=evidence.score,
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

#: Unit ID -> (dimension, factor to the dimension's base unit). IDs follow the
#: facet registry's ``units`` where one exists.
UNITS: Mapping[str, tuple[str, float]] = {
    "percent": ("ratio", 0.01),
    "fraction": ("ratio", 1.0),
    "tokens": ("tokens", 1.0),
    "k_tokens": ("tokens", 1e3),
    "m_tokens": ("tokens", 1e6),
    "usd_per_1m_tokens": ("usd_per_token", 1e-6),
    "usd_per_1k_tokens": ("usd_per_token", 1e-3),
    "usd_per_token": ("usd_per_token", 1.0),
    "milliseconds": ("seconds", 1e-3),
    "seconds": ("seconds", 1.0),
    "tokens_per_second": ("tokens_per_second", 1.0),
    "tokens_per_minute": ("tokens_per_minute", 1.0),
    "requests_per_minute": ("requests_per_minute", 1.0),
    "parameters": ("parameters", 1.0),
    "m_parameters": ("parameters", 1e6),
    "b_parameters": ("parameters", 1e9),
    "days": ("days", 1.0),
}

_UNIT_SPELLINGS = {
    "%": "percent", "percent": "percent", "pct": "percent", "per cent": "percent",
    "fraction": "fraction", "ratio": "fraction",
    "token": "tokens", "tokens": "tokens", "tok": "tokens",
    "ktok": "k_tokens", "mtok": "m_tokens",
    "ms": "milliseconds", "millisecond": "milliseconds", "milliseconds": "milliseconds",
    "s": "seconds", "sec": "seconds", "second": "seconds", "seconds": "seconds",
    "tokens/s": "tokens_per_second", "tok/s": "tokens_per_second",
    "tokens/sec": "tokens_per_second", "tokens/second": "tokens_per_second",
    "tokens/min": "tokens_per_minute", "tpm": "tokens_per_minute",
    "requests/min": "requests_per_minute", "rpm": "requests_per_minute",
    "parameter": "parameters", "parameters": "parameters", "params": "parameters",
    "day": "days", "days": "days",
    "usd/token": "usd_per_token",
}
_MAGNITUDE = {"k": "k", "thousand": "k", "m": "m", "million": "m", "b": "b", "billion": "b"}
_SCALED = re.compile(r"^(k|m|b|thousand|million|billion)\s*(tokens?|parameters?|params)$")
_PRICE = re.compile(r"^usd\s*/\s*(1\s*)?(k|m|thousand|million)\s*(tokens?|tok)?$")


def unit_id(text: str | None) -> str | None:
    """A unit spelling ("%", "K tokens", "$/1M tokens") as a unit ID, or ``None``.

    An unrecognised spelling is returned cleaned, so it still compares exactly.
    """
    if text is None:
        return None
    s = text.strip().casefold().replace("$", "usd ").replace(" per ", "/")
    s = re.sub(r"\s*/\s*", "/", re.sub(r"\s+", " ", s)).strip()
    if not s:
        return None
    if s in {"/1m tokens", "per 1m tokens", "per million tokens"}:
        return "usd_per_1m_tokens"
    if s in UNITS:
        return s
    if s in _UNIT_SPELLINGS:
        return _UNIT_SPELLINGS[s]
    if m := _SCALED.match(s):
        base = "tokens" if m.group(2).startswith("tok") else "parameters"
        return f"{_MAGNITUDE[m.group(1)]}_{base}"
    if m := _PRICE.match(s):
        return f"usd_per_1{_MAGNITUDE[m.group(2)]}_tokens"
    return s


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
    r"^(?:(?:reasoning\s+)?effort\s*[:=]?\s*)?(\w+)(?:\s+(?:reasoning\s+)?effort)?$")


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


def _condition(key: str, value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    s = str(value).strip().casefold()
    if key == "effort":
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
    value: str | None
    unit: str | None = None
    conditions: Mapping[str, str | None] = field(default_factory=dict)


class ExtractorError(Exception):
    """The extractor could not read the region: not evidence that a value is absent."""


class Extractor(Protocol):
    """Reads values from a cited region. ``actor`` is the verifier the log records."""

    actor: VerificationActor

    def accepts(self, text: str) -> bool: ...

    def extract(self, claim: Claim, text: str) -> list[Reading]: ...


DETERMINISTIC = "deterministic"
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
            for line in lines:
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
            pattern = rf"(?is){name}.{{0,160}}?\((\\?\$[0-9.]+)\s+USD per million tokens\)"
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
            if type_i is None:
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
            if subject is None or value is None:
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
            harness = "unregistered" if normal.get("agent") else None
            out.append(Reading(
                subject=str(subject),
                value=str(value),
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
"date", and "quoted_sentence" (the exact sentence containing the value).
Return [] if the region gives no such value. Do not infer, convert, combine
sentences, or use knowledge outside the source region. A quoted sentence must
appear verbatim in the source region.

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
    """Persistent reader replies keyed by source copy, cited region and facet."""

    def __init__(self, root: str | Path | None = None) -> None:
        configured = os.environ.get("MODELSPEC_LLM_CACHE")
        self.root = Path(root or configured or Path.home() / ".cache/modelspec/llm-reader")

    def _path(self, key: tuple[str, str, str]) -> Path:
        digest = hashlib.sha256(
            json.dumps(("strict-reader-v2", *key), ensure_ascii=False,
                       separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return self.root / digest[:2] / f"{digest}.json"

    def get(self, key: tuple[str, str, str]) -> str | None:
        path = self._path(key)
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def put(self, key: tuple[str, str, str], reply: str) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(reply, encoding="utf-8")


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
                cache_key: tuple[str, str, str] | None = None) -> list[Reading]:
        prompt = LLM_PROMPT.format(label=claim.label or claim.field.replace("_", " "),
                                   names=", ".join(claim.names), text=text)
        reply = self.cache.get(cache_key) if self.cache is not None and cache_key else None
        if reply is None:
            reply = self.complete(prompt)
        try:
            cleaned = reply.strip()
            if cleaned.startswith("```json") and cleaned.endswith("```"):
                cleaned = cleaned[7:-3].strip()
            rows = json.loads(cleaned)
            if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
                raise ValueError("not a list of objects")
            for row in rows:
                quote = row.get("quoted_sentence")
                if not isinstance(quote, str) or not quote.strip() or \
                        normalise_name(quote) not in normalise_name(text):
                    raise ValueError("quoted_sentence is missing or is not verbatim source text")
            readings = [
                Reading(subject=_text(r.get("subject")) or claim.names[0],
                        value=_text(r.get("value")),
                        unit=_text(r.get("unit")),
                        conditions={k: _text(r.get(k)) for k in CONDITION_KEYS})
                for r in rows
            ]
            if not readings and claim.value is None:
                readings = [Reading(subject=claim.names[0], value=None)]
            if self.cache is not None and cache_key:
                self.cache.put(cache_key, reply)
            return readings
        except ValueError as exc:
            raise ExtractorError(f"unparseable reply from {self.actor.method}: {exc}") from exc


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


def _text(value: Any) -> str | None:
    return None if value is None else str(value)


def deterministic_extractors() -> list[Extractor]:
    return [StructuredDataExtractor(), OfferingPriceExtractor(), TableExtractor(),
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
        if numbers_agree(value, claim.unit, q):
            return None
        unit_differs = claim.unit is not None and claim.unit != q.unit
        return Diff("unit" if unit_differs else "value", expected, q.show())
    if isinstance(value, list):
        found_items = {s.strip().casefold()
                       for s in re.split(r",|;|\band\b", reading.value) if s.strip()}
        claimed_items = {str(v).strip().casefold() for v in value}
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
    try:
        _verification(claim, actor, "verified", today)
    except ValidationError:
        return False
    return True


def verify(claim: Claim, regions: Regions, extractors: Sequence[Extractor], *,
           today: date) -> Result:
    """Re-read ``claim`` from each cited region of its sources and compare.

    Deterministic extractors are tried before the rest, whatever the order given;
    the first that accepts a region and is independent of the collector reads it.
    Verified if any region confirms the value; otherwise the first mismatch.
    """
    ordered = sorted(extractors, key=lambda e: e.actor.model_family != DETERMINISTIC)
    reachable = False
    mismatch: tuple[VerificationActor, list[Diff]] | None = None
    reasons: list[str] = []
    for source in claim.sources:
        for region_id in source.cited_regions:
            where = f"{source.source_id}#{region_id}"
            text = regions.text(source.source_id, source.snapshot_ref, region_id)
            if text is None:
                reasons.append(f"unreachable:{where}")
                continue
            reachable = True
            accepting = [e for e in ordered if e.accepts(text)]
            independent = [e for e in accepting if _independent(claim, e.actor, today)]
            if not independent:
                reasons.append("no_independent_extractor" if accepting else f"no_extractor:{where}")
                continue
            for extractor in independent:
                try:
                    if isinstance(extractor, LLMExtractor):
                        readings = extractor.extract(
                            claim,
                            text,
                            cache_key=(source.snapshot_ref, region_id, claim.field),
                        )
                    else:
                        readings = extractor.extract(claim, text)
                except ExtractorError as exc:
                    reasons.append(f"extractor_error:{where}: {exc}")
                    continue
                diffs = compare(claim, readings)
                if not diffs:
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
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(Verification.model_validate_json(line))
        return records

    def latest(self) -> dict[tuple[str, str], Verification]:
        """Latest ``date`` wins; on a tie, the later line (as ``decision.snapshot`` reads it)."""
        latest: dict[tuple[str, str], Verification] = {}
        for record in self.records():
            key = _key(record.target)
            if key not in latest or record.date >= latest[key].date:
                latest[key] = record
        return latest

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
    "LLMExtractor", "ModelPageExtractor", "OfferingPriceExtractor", "Quantity", "Queue", "Reading",
    "Regions", "Result",
    "RunReport", "StoredRegions", "StructuredDataExtractor", "TableExtractor", "TOLERANCE_RULE",
    "UNITS", "VerificationLog", "compare",
    "claude_extractor", "deterministic_extractors", "is_quarantined", "load_sources",
    "numbers_agree",
    "parse_quantity", "quarantined_values", "run", "split_model_cell", "target_ref", "unit_id",
    "verify",
]
