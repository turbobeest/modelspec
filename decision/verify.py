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
``KeyValueExtractor``, ``CanonicalLicenceExtractor``) always run before any
other; ``LLMExtractor`` reads
prose through an injected completion function, so nothing here calls a model
or the network on its own: ``claude_extractor`` (Claude Sonnet, via the Claude
CLI) and ``mistral_extractor`` (Mistral Large, via ollama) are the two wired
readers. ``LicenceExtractor`` reads a ``licence.*`` claim through that same
completion function, and only from a source kind the facet permits.
``CanonicalLicenceExtractor`` reads a canonical MIT or Apache-2.0
``licence_text`` first, and the licence reader is not asked about a text it
accepts. Other
cited regions are binding pages, not readings. Deterministic extractors
still read a ``licence_text`` source for every other claim. An absence
verifies only from a source kind the facet permits; a ``licence.*`` absence
needs that kind explicitly. A region of another kind is a ``source_kind``
mismatch only when the claim cites no permitted kind. When every permitted
region has no extractor, or every one raises ``ExtractorError``, the claim
is skipped. Each extractor's actor (agent, model family,
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
import html
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
from typing import Any, Literal, NamedTuple, Protocol
from urllib.parse import urljoin

import yaml
from pydantic import JsonValue, ValidationError

from decision.licence_rules import (
    LICENCE_CONDITION_RULE,
    LICENCE_READING_RULES,
    licence_reading_rule,
)
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
    ``date`` as the collector filed them. ``base_model`` is the card's
    ``lineage.base_model`` when the subject is a fine-tune. It is empty when
    the card names no base.
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
    base_model: str | None = None

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
                  unit: str | None = None, label: str | None = None,
                  base_model: str | None = None) -> Claim:
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
            base_model=base_model or None,
        )

    def to_dict(self) -> dict[str, Any]:
        data = {
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
        if self.base_model:
            data["base_model"] = self.base_model
        return data

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
            base_model=data.get("base_model") or None,
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
        return (readings or _peak_price_tables(claim, rows, wanted)
                or _grouped_header_tables(claim, text, wanted))


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


def _peak_price_tables(claim: Claim, rows: list[list[str]], wanted: str) -> list[Reading]:
    """DeepSeek's transposed table: exact model columns and PEAK list prices.

    HTML rowspans leave the price kind on the first band row only. The model
    cells and each band's prices occupy the same rightmost columns. Filed
    standard prices have no time-band condition; OFF-PEAK is a discount.
    """
    kinds = {"1m input tokens cache hit": "cached_input",
             "1m input tokens cache miss": "input", "1m output tokens": "output"}
    if wanted not in kinds.values():
        return []
    names = {normalise_name(name): name for name in claim.names}
    columns: list[tuple[int, str]] = []
    width = 0
    kind = None
    readings: list[Reading] = []
    for row in rows:
        if normalise_name(row[0]) in {"model", "model version"}:
            width = len(row) - 1
            columns = [(i, names[normalise_name(cell)]) for i, cell in enumerate(row[1:])
                       if normalise_name(cell) in names]
            kind = None
            continue
        if not columns or len(row) <= width:
            kind = None
            continue
        labels = [normalise_name(cell) for cell in row[:-width]]
        stated_kind = next((kinds[label] for label in labels if label in kinds), None)
        if stated_kind:
            kind = stated_kind
        elif len(labels) != 1:
            kind = None
        band = labels[-1]
        if band not in {"peak", "off peak"}:
            kind = None
            continue
        if band == "peak" and kind == wanted:
            prices = row[-width:]
            for i, name in columns:
                if match := _PRICE_CELL.search(prices[i]):
                    readings.append(Reading(name, match.group(0), claim.unit))
    return readings


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
        # its model rows match the column header, even after a narrower continuation.
        # A column-header row after it ("Name | Input | Output") starts a new table.
        after = lines[i + 1] if i + 1 < len(lines) else ""
        if len(current) > 2 and line.strip() and "|" in after \
                and len(cells(after)) == len(current[1]) \
                and normalise_name(cells(after)[0]) not in {"name", "model"}:
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


#: Gap stops at a sentence or block break, so a heading cannot take the next block's count.
_RETENTION_DAYS = re.compile(
    r"(?is)(?:retained|stored)(?:(?![.!?](?:\s+|$)|\n).){0,100}?\b(\d+)\s*days?"
)
#: A clause conditioned on a model set or a mode head, not a later mention of "mode".
_RETENTION_SCOPE_BEGIN = re.compile(
    r"(?is)^for models requiring\b|^for the\b[^:.]+?\bmode\b\s*:"
)
#: A dot between digits is a version (5.1), not the end of the model list.
_RETENTION_CURRENTLY = re.compile(
    r"\b(?i:currently)\s+[A-Z](?:[^.:;)]|\.(?=\d))*"
)
#: Block-level tags whose edges are clause breaks. Other tags drop; their text stays.
_HTML_BLOCK = re.compile(
    r"(?i)</?p(?:\s[^>]*)?>|</?li(?:\s[^>]*)?>|<br(?:\s[^>]*)?/?>"
    r"|</?h[1-6](?:\s[^>]*)?>|</div(?:\s[^>]*)?>|</?t[dh](?:\s[^>]*)?>"
)
_HTML_TAG = re.compile(r"<[^>]+>")
_CLAUSE_BREAK = re.compile(r"[.!?](?:\s+|$)|\n+")


def _region_prose(text: str) -> str:
    """HTML region text as prose. Plain text, with no tag and no entity, is unchanged."""
    if "<" not in text and "&" not in text:
        return text
    broken = _HTML_BLOCK.sub("\n", text)
    return html.unescape(_HTML_TAG.sub("", broken))


def _clause_around(text: str, start: int, end: int) -> str:
    """The sentence or block containing ``text[start:end]``. Newlines are breaks too."""
    begin = 0
    for mark in _CLAUSE_BREAK.finditer(text[:start]):
        begin = mark.end()
    tail = _CLAUSE_BREAK.search(text[end:])
    stop = len(text) if tail is None else end + tail.end()
    return text[begin:stop]


def _retention_scope(clause: str) -> str | None:
    """The conditioning phrase, or ``None`` when the clause states a period outright."""
    body = clause.strip()
    parts: list[str] = []
    if _RETENTION_SCOPE_BEGIN.match(body):
        head, sep, _rest = body.partition(":")
        parts.append(head if sep else body)
    currently = _RETENTION_CURRENTLY.search(body)
    if currently:
        parts.append(currently.group(0))
    return " ".join(parts) or None


def _scope_names_subject(scope: str, names: tuple[str, ...]) -> bool:
    normal = normalise_name(scope)
    aliases = [alias for name in names if (alias := normalise_name(name))]
    return any(
        re.search(rf"(?<![0-9a-z]){re.escape(alias)}(?![0-9a-z]| \d)", normal)
        for alias in aliases
    )


def _retention_days(claim: Claim, text: str) -> str | None:
    """The first day count whose own clause is unscoped or names this subject.

    A count after "For models requiring …", "For the … mode:", or "currently
    <models>" applies only when that condition names one of ``claim.names``.
    The clause is the one around the count, not the one around an earlier
    "retained" or "stored".
    """
    text = _region_prose(text)
    for match in _RETENTION_DAYS.finditer(text):
        scope = _retention_scope(_clause_around(text, match.start(1), match.end(1)))
        if scope is None or _scope_names_subject(scope, claim.names):
            return match.group(1)
    return None


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
            days = _retention_days(claim, text)
            if days is not None:
                return [Reading(subject, days, "days")]
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
    r"(?im)^[ \t]*license_link:\s*[\"']?(\S+?)[\"']?\s*$"
)
_PAGE_URL = re.compile(r"https?://[^\s\"'<>)\]]+", re.IGNORECASE)
_HF_FILE_VERBS = frozenset({"raw", "resolve", "blob"})
_NAME_JOIN = re.compile(r"\s*[-_.][-_.\s]*(?=[0-9A-Za-z])")
#: SPDX ids for the shared generic texts. ``license: other`` is not one of them.
#: A shared text binds only through this table.
SPDX_LICENCE_URLS: dict[str, tuple[str, ...]] = {
    "apache-2.0": (
        "https://www.apache.org/licenses/LICENSE-2.0",
        "https://www.apache.org/licenses/LICENSE-2.0.txt",
    ),
    "mit": ("https://opensource.org/license/mit",),
}
#: Phrases a retained root file must contain before an id in
#: :data:`SPDX_LICENCE_URLS` binds that file. Every phrase has to appear.
#: An id outside the table is not checked.
SPDX_SIGNATURES: dict[str, tuple[str, ...]] = {
    "apache-2.0": ("Apache License", "Version 2.0"),
    "mit": ("Permission is hereby granted, free of charge",),
}
_ROOT_LICENCE_NAME = re.compile(r"(?i)^(license|licence|copying)")


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


def _url_parts(url: str) -> list[str] | None:
    """Host and path segments, without a scheme, ``www.``, query or fragment."""
    text = url.strip().strip("\"'")
    if not text:
        return None
    text = re.sub(r"^https?://", "", text, flags=re.I)
    text = re.sub(r"^www\.", "", text, flags=re.I)
    text = text.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    parts = [part for part in text.split("/") if part]
    return parts or None


def _licence_url_key(url: str) -> str:
    """Scheme, host case, a leading ``www.`` and a trailing ``.txt`` do not differ.

    On huggingface.co, ``/raw/<rev>/<path>``, ``/resolve/<rev>/<path>`` and
    ``/blob/<rev>/<path>`` name the same file.
    """
    text = url.strip().strip("\"'")
    text = re.sub(r"^https?://", "", text, flags=re.I)
    text = re.sub(r"^www\.", "", text, flags=re.I)
    text = text.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    if text.casefold().endswith(".txt"):
        text = text[:-4]
    parts = [part for part in text.split("/") if part]
    if (len(parts) >= 4 and parts[0].casefold() == "huggingface.co"
            and parts[3].casefold() in _HF_FILE_VERBS):
        del parts[3]
    return "/".join(parts).casefold()


def _hf_repo(url: str) -> tuple[str, str, str] | None:
    """``(host, org, repo)`` casefolded, when ``url`` is on huggingface.co."""
    parts = _url_parts(url)
    if parts is None or len(parts) < 3 or parts[0].casefold() != "huggingface.co":
        return None
    return parts[0].casefold(), parts[1].casefold(), parts[2].casefold()


def _hf_repo_name(url: str) -> str | None:
    """The repository segment of a huggingface.co URL, as published."""
    parts = _url_parts(url)
    if parts is None or len(parts) < 3 or parts[0].casefold() != "huggingface.co":
        return None
    return parts[2]


def _hf_file(url: str) -> bool:
    """A root licence file on huggingface.co.

    ``huggingface.co/<org>/<repo>/(raw|resolve|blob)/<rev>/<name>``. ``name``
    is one path segment and starts with ``LICENSE``, ``LICENCE`` or
    ``COPYING``, in any case. ``README.md``, ``config.json`` and a file in a
    subdirectory are not.
    """
    parts = _url_parts(url)
    if parts is None or len(parts) != 6 or parts[0].casefold() != "huggingface.co":
        return False
    if parts[3].casefold() not in _HF_FILE_VERBS:
        return False
    return _ROOT_LICENCE_NAME.match(parts[5]) is not None


def _front_matter(page: str) -> str:
    """YAML front matter when the page opens with fences. Otherwise the page.

    A Hugging Face README keeps ``license:`` and ``license_link:`` between
    the fences. A region that is only those fields has no fences.
    """
    if not page.startswith("---"):
        return page
    parts = page.split("---", 2)
    if len(parts) < 3 or parts[0].strip():
        return page
    return parts[1]


def _text_is_spdx(spdx_id: str, text: str | None) -> bool:
    """The retained text carries every signature phrase for this SPDX id."""
    phrases = SPDX_SIGNATURES.get(spdx_id)
    if not phrases or not text:
        return False
    return all(phrase in text for phrase in phrases)


def _resolve_license_link(link: str, page_url: str | None) -> str:
    """An absolute link unchanged. A relative link resolved in the page's repository."""
    link = link.strip().strip("\"'")
    if re.match(r"(?i)^[a-z][a-z0-9+.-]*://", link) or not page_url:
        return link
    base = page_url if page_url.endswith("/") else page_url.rsplit("/", 1)[0] + "/"
    return urljoin(base, link)


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


def _page_words(page: str) -> list[tuple[str, bool]]:
    """``(word, joined to the next word)``. ``-``, ``_`` and ``.`` join one name."""
    words: list[tuple[str, bool]] = []
    for match in re.finditer(r"[0-9A-Za-z]+", page):
        words.append((match.group(0).casefold(),
                      _NAME_JOIN.match(page[match.end():]) is not None))
    return words


def _name_segments(name: str) -> tuple[str, ...]:
    """Case-folded pieces of one name. ``-``, ``_``, ``.`` and spaces split it."""
    return tuple(part for part in re.split(r"[-_.\s]+", name.casefold()) if part)


def _same_whole_name(left: str, right: str) -> bool:
    """The two names are the same whole name, not a prefix of a longer one."""
    segments = _name_segments(left)
    return bool(segments) and segments == _name_segments(right)


def _whole_name_in_words(token: str, words: list[tuple[str, bool]]) -> bool:
    """``token`` is a maximal name in ``words``. A hyphen-joined prefix does not count.

    ``Querit`` does not match ``Querit-4B``. ``Querit-4B`` does not match
    ``Querit-4B-Pro``. A space-separated phrase still matches as that phrase.
    """
    parts = token.split()
    if not parts:
        return False
    width = len(parts)
    for start in range(len(words) - width + 1):
        if [words[start + offset][0] for offset in range(width)] != parts:
            continue
        if words[start + width - 1][1]:
            continue
        if start > 0 and words[start - 1][1]:
            continue
        return True
    return False


def _page_names_subject(page: str, names: Sequence[str], subject: str | None = None,
                        page_url: str | None = None) -> bool:
    """The page names the subject by a whole name, or its repository name equals one.

    ``-``, ``_``, ``.`` and spaces separate segments of one name. The published
    name or the repository name must be that whole name, not a prefix of a
    longer hyphen-joined name. A family name still does not count: the tokens
    are the display name and the model id's last segment.
    """
    tokens = _binding_name_tokens(names, subject)
    words = _page_words(page)
    if any(_whole_name_in_words(token, words) for token in tokens):
        return True
    repo = _hf_repo_name(page_url) if page_url else None
    if not repo:
        return False
    candidates = list(tokens)
    if subject:
        candidates.append(subject.rsplit("/", 1)[-1])
    return any(_same_whole_name(repo, candidate) for candidate in candidates)


def _license_link_matches(page: str, licence_url: str, page_url: str | None) -> bool:
    source_key = _licence_url_key(licence_url)
    for match in _LICENSE_LINK.finditer(page):
        resolved = _resolve_license_link(match.group(1), page_url)
        if _licence_url_key(resolved) == source_key:
            return True
    return False


def _page_contains_licence_url(page: str, licence_url: str) -> bool:
    if licence_url in page:
        return True
    bare = re.sub(r"^https?://", "", licence_url).rstrip("/")
    if bare and bare in page:
        return True
    source_key = _licence_url_key(licence_url)
    return any(_licence_url_key(match.group(0)) == source_key for match in _PAGE_URL.finditer(page))


def _repo_location_binds(page: str, page_url: str | None, licence_url: str,
                         licence_text: str | None = None) -> bool:
    """A root licence file in the page's own repository, named by ``license:``.

    An id in :data:`SPDX_LICENCE_URLS` binds that file only when
    ``licence_text`` carries the signature in :data:`SPDX_SIGNATURES`.
    ``license: other``, and any id outside the table, binds the file by
    location alone.
    """
    match = _LICENSE_SPDX.search(_front_matter(page))
    if not page_url or match is None or not _hf_file(licence_url):
        return False
    page_repo = _hf_repo(page_url)
    if page_repo is None or page_repo != _hf_repo(licence_url):
        return False
    spdx_id = match.group(1).casefold()
    if spdx_id in SPDX_LICENCE_URLS:
        return _text_is_spdx(spdx_id, licence_text)
    return True


def _spdx_binds(page: str, licence_url: str) -> bool:
    source_key = _licence_url_key(licence_url)
    for match in _LICENSE_SPDX.finditer(page):
        canonical = SPDX_LICENCE_URLS.get(match.group(1).casefold(), ())
        if any(_licence_url_key(url) == source_key for url in canonical):
            return True
    return False


def _licence_rule(page: str, page_url: str | None, licence_url: str | None,
                  licence_text: str | None = None) -> str | None:
    """Which rule names this licence on this page: link, url, repo, or SPDX.

    A ``license_link`` in front matter is exclusive. A source that does not
    match it does not bind by URL, repository location, or SPDX.
    """
    if not licence_url:
        return None
    matter = _front_matter(page)
    if _LICENSE_LINK.search(matter):
        if _license_link_matches(matter, licence_url, page_url):
            return "license_link"
        return None
    if _page_contains_licence_url(page, licence_url):
        return "url"
    if _repo_location_binds(page, page_url, licence_url, licence_text):
        return "repo-location"
    if _spdx_binds(matter, licence_url):
        return "SPDX"
    return None


def _bound_on_pages(names: Sequence[str], pages: Sequence[str], licence_url: str | None, *,
                    subject: str | None = None,
                    page_urls: Sequence[str | None] | None = None,
                    licence_text: str | None = None) -> str | None:
    """The link, url, repo-location or SPDX rule that binds this licence, or ``None``."""
    urls = tuple(page_urls or ())
    for index, page in enumerate(pages):
        page_url = urls[index] if index < len(urls) else None
        if _page_names_subject(page, names, subject, page_url):
            rule = _licence_rule(page, page_url, licence_url, licence_text)
            if rule:
                return rule
    return None


#: One sentence. The subject is the derivatives. They are or remain subject to,
#: or must or shall be distributed under, these or this terms, licence, or
#: agreement. ``derivatives`` opens the sentence or follows whitespace, so a
#: hyphen in ``non-derivatives`` does not count. ``not``, ``no``, ``none`` and
#: ``need not`` anywhere in the match reject the sentence. A grant preamble
#: and a notice-retention sentence do not match.
_DERIVATIVE_TERMS = re.compile(
    r"(?:^|(?<=\s))(?:model\s+)?derivatives?\b"
    r"[^.;!?]{0,220}?"
    r"(?:"
    r"(?:(?:must|shall)\s+)?(?:are|remain)\s+subject\s+to"
    r"|"
    r"(?:must|shall)\s+be\s+distributed\s+under"
    r")"
    r"[^.;!?]{0,80}?"
    r"\b(?:these|this)\b"
    r"[^.;!?]{0,40}?"
    r"\b(?:terms|licen[cs]es?|licences?|agreements?)\b",
    re.IGNORECASE,
)
_NEGATED_DUTY = re.compile(r"\b(?:not|no|none|need\s+not)\b", re.IGNORECASE)
#: The retained Gemma terms split this duty across the next sentence. Either
#: sentence alone is a Llama "copy of this Agreement" or an OpenRAIL
#: use-restriction carry-over, and neither of those matches on its own.
_GEMMA_DERIVATIVE_TERMS = re.compile(
    r"(?:^|(?<=\s))(?:model\s+)?derivatives?\s+are\s+subject\s+to\s+the\s+use\s+restrictions\b"
    r".{0,240}?"
    r"\ba\s+copy\s+of\s+this\s+agreement\b",
    re.IGNORECASE | re.DOTALL,
)


def licence_requires_derivative_terms(text: str | None) -> bool:
    """The licence says a derivative must be distributed under it, or stay subject to it.

    The sentence's subject is the derivatives. It says they are or remain
    subject to, or must or shall be distributed under, these or this terms,
    licence, or agreement. ``derivatives`` opens the sentence or follows
    whitespace. ``Non-derivatives`` does not count. ``not``, ``no``, ``none``
    and ``need not`` anywhere in the match reject it. A grant to prepare
    derivative works is not enough, and neither is a grant preamble that only
    says the grant is subject to the licence.

    The retained Gemma terms match by saying Model Derivatives are subject to
    the use restrictions and, in the next sentence, that recipients of those
    derivatives get a copy of this Agreement. A Llama sentence that only says
    to provide a copy of this Agreement, and an OpenRAIL sentence that only
    carries use restrictions onto derivatives, do not match. MIT and
    Apache-2.0 do not say this. Keeping their notices is not this duty.
    """
    if not text:
        return False
    flat = re.sub(r"\s+", " ", text)
    for match in _DERIVATIVE_TERMS.finditer(flat):
        if _NEGATED_DUTY.search(match.group(0)):
            continue
        return True
    gemma = _GEMMA_DERIVATIVE_TERMS.search(flat)
    return gemma is not None and _NEGATED_DUTY.search(gemma.group(0)) is None


def licence_is_bound(names: Sequence[str], pages: Sequence[str], licence_url: str | None, *,
                     subject: str | None = None,
                     page_urls: Sequence[str | None] | None = None,
                     licence_text: str | None = None,
                     base_model: str | None = None) -> str | None:
    """The rule that binds this licence to the subject, or ``None``.

    A page names the subject by its display name or repository id, as a whole
    name, or when the page URL's repository name is that same whole name.
    ``-``, ``_``, ``.`` and spaces separate segments. A prefix of a longer
    hyphen-joined name does not count: ``Querit`` is not ``Querit-4B``.
    A family name does not count.

    ``license:`` and ``license_link:`` are read from YAML front matter when
    the page has it, and from the whole page otherwise.

    The licence rule is the first that holds. A ``license_link`` is exclusive:
    when the front matter has one, only a source that matches it binds.
    A relative link resolves against the page URL's directory. On
    huggingface.co, ``raw``, ``resolve`` and ``blob`` name the same file.

    With no ``license_link``: ``url`` (that file's URL is in the page),
    ``repo-location`` (a root file named ``LICENSE*``, ``LICENCE*`` or
    ``COPYING*`` in the page's own repository, and the page has a
    ``license:`` field), or ``SPDX`` (the field names a shared text in
    :data:`SPDX_LICENCE_URLS`). A ``license:`` of ``mit`` or ``apache-2.0``
    binds that root file only when ``licence_text`` contains the signature
    in :data:`SPDX_SIGNATURES`. ``license: other``, and any id outside that
    table, binds the root file by location. ``README.md``, ``config.json``
    and a subdirectory do not. ``license: other`` does not bind a shared
    text. A file in a different repository binds only by ``license_link``
    or ``url``.

    When none of those rules name the subject, a licence bound to
    ``base_model`` binds the subject too. The card field is ``base_model``.
    The binding page declares that base in ``base_model`` (a string or a list
    of repository ids, compared case-insensitively). Fenced YAML counts. So
    do the leading ``key: value`` lines of a normalised page, whose fences
    the text normaliser has already dropped, including a list written as
    ``base_model:`` and then ``- id``. A heading, a blank line, or any other
    line ends that block. A prose mention of the base does not count. The
    same link, url, repo-location and SPDX rules have to hold on that page,
    and :func:`licence_requires_derivative_terms` has to be true of the
    licence text. The returned rule is ``base-model``. No ``base_model``, a
    base the front matter does not list, or a licence that only grants
    modification, does not bind. MIT and Apache-2.0 do not require
    derivative terms, so they do not bind by this path. A direct rule still
    wins when the page names the subject itself.
    """
    direct = _bound_on_pages(
        names, pages, licence_url, subject=subject, page_urls=page_urls,
        licence_text=licence_text,
    )
    if direct:
        return direct
    base = (base_model or "").strip()
    if not base or (subject and base.casefold() == subject.casefold()):
        return None
    if not licence_requires_derivative_terms(licence_text):
        return None
    urls = tuple(page_urls or ())
    for index, page in enumerate(pages):
        if not _page_declares_base(page, base):
            continue
        page_url = urls[index] if index < len(urls) else None
        if _licence_rule(page, page_url, licence_url, licence_text):
            return "base-model"
    return None


# A normalised page has no fences: ``---`` is only punctuation, so text-default
# drops it. The front matter is then the leading ``key: value`` lines. A colon
# has to be followed by a space, so a URL (``https://``) is not a key.
_KEY_LINE = re.compile(
    r"^[A-Za-z_][\w-]*[ \t]*:(?:[ \t]+(?P<value>\S(?:.*\S)?)|[ \t]*)$"
)
_LIST_ITEM = re.compile(r"^[ \t]*-[ \t]+\S")
_HEADING_LINE = re.compile(r"^[ \t]*#[ \t]*\S")


def _load_mapping(text: str) -> Mapping[str, Any] | None:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def _fenced_front_matter(page: str) -> str | None:
    """The text between opening fences, or ``None`` when the page has none."""
    if not page.startswith("---"):
        return None
    parts = page.split("---", 2)
    if len(parts) < 3 or parts[0].strip():
        return None
    return parts[1]


def _leading_mapping_block(page: str) -> str:
    """Leading ``key: value`` lines, including ``base_model:`` then ``- id``.

    A heading, a blank line, or any other line ends the block. That is the
    front matter left after the text normaliser drops the fences.
    """
    taken: list[str] = []
    in_list = False
    for line in page.splitlines():
        if not line.strip():
            if taken:
                break
            continue
        if _HEADING_LINE.match(line):
            break
        key = _KEY_LINE.match(line)
        if key:
            taken.append(line)
            in_list = key.group("value") is None
            continue
        if in_list and _LIST_ITEM.match(line):
            taken.append(line)
            continue
        break
    return "\n".join(taken)


def _front_matter_mapping(page: str) -> Mapping[str, Any] | None:
    """The page's YAML mapping, fenced or the normalised leading keys."""
    text = page.lstrip("\ufeff")
    fenced = _fenced_front_matter(text)
    if fenced is not None:
        return _load_mapping(fenced)
    block = _leading_mapping_block(text)
    if not block:
        return None
    return _load_mapping(block)


def _declared_base_models(page: str) -> tuple[str, ...]:
    """Repository ids in the front matter ``base_model`` string or list."""
    data = _front_matter_mapping(page)
    if not data or "base_model" not in data:
        return ()
    raw = data["base_model"]
    if isinstance(raw, str):
        items: tuple[Any, ...] = (raw,)
    elif isinstance(raw, list):
        items = tuple(raw)
    else:
        return ()
    return tuple(item.strip() for item in items if isinstance(item, str) and item.strip())


def _page_declares_base(page: str, base: str) -> bool:
    """The front matter ``base_model`` entry lists this repository id."""
    wanted = base.strip().casefold()
    if not wanted:
        return False
    return any(item.casefold() == wanted for item in _declared_base_models(page))


class LicenceExtractor:
    """Reads one ``licence.*`` value from a licence or terms document.

    It uses the same injected ``complete(prompt)``, cache and call budget as
    ``LLMExtractor``. The prompt gives the facet's definition, the reading
    rule for that facet, and the allowed values. It never shows the collector's
    value. A missing or non-verbatim
    clause is unparseable, so it is not evidence. A licence does not name the
    model: the reading's subject is the claim's name only when a binding page
    passes :func:`licence_is_bound`. A licence bound to ``claim.base_model``
    also names the subject when the page's YAML front matter lists that base
    and the licence requires derivatives to carry its terms.
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
                binding_urls: Sequence[str | None] | None = None,
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
            claim.names, bindings, licence_url, subject=claim.subject, page_urls=binding_urls,
            licence_text=text, base_model=claim.base_model,
        ) else None
        shown: JsonValue = None if value is None else str(value)
        unit = None
        if shown is not None and parse_quantity(shown) is not None:
            unit = default_registry().facet(claim.field).unit
        return [Reading(subject=subject, value=shown, unit=unit)]


class CanonicalClause(NamedTuple):
    """A canonical licence facet: the value, a verbatim clause, and the rule key."""

    value: JsonValue
    clause: str
    rule: str


_LICENCE_QUOTE_CHARS = str.maketrans({
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
    "\u00a0": " ",
})


def _canonical_form(text: str) -> str:
    """The licence collapsed to one spacing, and one way of writing the warranty.

    Retained MIT files write the warranty as ``"AS IS"``, with curly quotes, or
    as ``*AS IS*`` (Phi-4). Signatures and the canonical body are compared
    after those three are the same sentence.
    """
    straight = text.translate(_LICENCE_QUOTE_CHARS).replace("*AS IS*", '"AS IS"')
    return re.sub(r"\s+", " ", straight).strip()


#: Verbatim operative sentences. Every phrase has to appear. The MIT warranty
#: is matched on :func:`_canonical_form`, so curly quotes and ``*AS IS*`` count.
CANONICAL_LICENCE_SIGNATURES: dict[str, tuple[str, ...]] = {
    "mit": (
        "Permission is hereby granted, free of charge",
        'THE SOFTWARE IS PROVIDED "AS IS"',
    ),
    "apache-2.0": (
        "Apache License",
        "Version 2.0, January 2004",
        "2. Grant of Copyright License. Subject to the terms and conditions of "
        "this License, each Contributor hereby grants to You a perpetual, "
        "worldwide, non-exclusive, no-charge, royalty-free, irrevocable "
        "copyright license to reproduce, prepare Derivative Works of",
    ),
}

#: A phrase that means the text adds terms the canonical licence does not have.
#: Extra guard beside :data:`CANONICAL_LICENCE_RESIDUALS`. A short restriction
#: can avoid every phrase here and still miss the residual list.
CANONICAL_LICENCE_RED_FLAGS: tuple[str, ...] = (
    "separate agreement",
    "monthly active users",
    "not intended for use",
    "prohibited use",
    "acceptable use",
)

#: Collapsed characters allowed outside the canonical body. The longest retained
#: residual is 1,092 characters on apache.org ``LICENSE-2.0.txt`` (the space
#: after the terms, then the appendix). 1,200 leaves a margin.
CANONICAL_LICENCE_OUTSIDE_LIMIT = 1200

_MIT_CANONICAL_TEXT = """\
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

_APACHE_CANONICAL_TEXT = """\
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS
"""

#: The Apache how-to appendix, through the end of the boilerplate notice.
#: Verbatim apart from the copyright line, which the notice tells the holder
#: to fill in (Qwen writes ``Copyright 2024 Alibaba Cloud``).
_APACHE_APPENDIX_TEXT = """\
   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

_APACHE_APPENDIX_COPYRIGHT = "Copyright [yyyy] [name of copyright owner]"

CANONICAL_LICENCE_BODIES: dict[str, str] = {
    "mit": _canonical_form(_MIT_CANONICAL_TEXT),
    "apache-2.0": _canonical_form(_APACHE_CANONICAL_TEXT),
}

_APACHE_APPENDIX = _canonical_form(_APACHE_APPENDIX_TEXT)
if _APACHE_APPENDIX.count(_APACHE_APPENDIX_COPYRIGHT) != 1:
    raise RuntimeError("apache appendix copyright line is not verbatim once")
_APPENDIX_HEAD, _APPENDIX_TAIL = _APACHE_APPENDIX.split(_APACHE_APPENDIX_COPYRIGHT, 1)
if not _APPENDIX_HEAD.startswith("APPENDIX: How to apply the Apache License to your work."):
    raise RuntimeError("apache appendix does not start at the how-to heading")
if not _APPENDIX_TAIL.endswith("limitations under the License."):
    raise RuntimeError("apache appendix does not end at the boilerplate notice")
if _APPENDIX_HEAD in CANONICAL_LICENCE_BODIES["apache-2.0"]:
    raise RuntimeError("apache appendix heading is inside the canonical body")


#: Exact ``(before, after)`` text around a canonical body, after
#: :func:`_canonical_form` and whitespace stripping. For Apache-2.0, ``after``
#: is what remains once the canonical appendix is removed, so it is the
#: copyright line between the how-to and the boilerplate.
#:
#: DeepSeek-V4-Pro, DeepSeek-V4.1-Flash, and ``model-143-deepseek-v4-license``
#: are the same retained bytes as DeepSeek-V3.1, so they share that pair.
#: A copyright line that is not listed here is not read by this extractor
#: until the residual is reviewed and added in code.
CANONICAL_LICENCE_RESIDUALS: dict[str, frozenset[tuple[str, str]]] = {
    "mit": frozenset({
        (
            "Popular / Strong Community The MIT License Version N/A "
            "SPDX short identifier: MIT Copyright <YEAR> <COPYRIGHT HOLDER>",
            "",
        ),
        ("Microsoft. Copyright (c) Microsoft Corporation. MIT License", ""),
        ("MIT License Copyright (c) 2023 DeepSeek", ""),
        ("MIT License Copyright (c) 2026 Zhipu AI", ""),
    }),
    "apache-2.0": frozenset({
        ("", "Copyright [yyyy] [name of copyright owner]"),
        ("", "Copyright 2024 Alibaba Cloud"),
    }),
}
if set(CANONICAL_LICENCE_RESIDUALS) != set(CANONICAL_LICENCE_BODIES):
    raise RuntimeError("residual table does not match the canonical bodies")


def _canonical_clause(value: JsonValue, clause: str, rule: str) -> CanonicalClause:
    if rule not in LICENCE_READING_RULES:
        raise RuntimeError(f"no licence reading rule for {rule}")
    return CanonicalClause(value, clause, rule)


#: Facet values for a canonical text. ``rule`` is the ``LICENCE_READING_RULES``
#: key. ``None`` is ``not_disclosed``. Notice retention is not a condition
#: (``LICENCE_CONDITION_RULE``), so commercial use and fine-tuning are
#: ``permitted``.
CANONICAL_LICENCE_READINGS: dict[str, dict[str, CanonicalClause]] = {
    "mit": {
        "licence.commercial_use": _canonical_clause(
            "permitted", "sell copies of the Software", "licence.commercial_use",
        ),
        "licence.user_cap": _canonical_clause(
            "unbounded",
            "The above copyright notice and this permission notice shall be included "
            "in all copies or substantial portions of the Software.",
            "licence.user_cap",
        ),
        "licence.output_training": _canonical_clause(
            None,
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or "
            "sell copies of the Software",
            "licence.output_training",
        ),
        "licence.fine_tuning": _canonical_clause(
            "permitted",
            "modify, merge, publish, distribute, sublicense, and/or sell copies "
            "of the Software",
            "licence.fine_tuning",
        ),
    },
    "apache-2.0": {
        "licence.commercial_use": _canonical_clause(
            "permitted",
            "make, have made, use, offer to sell, sell",
            "licence.commercial_use",
        ),
        "licence.user_cap": _canonical_clause(
            "unbounded",
            "copyright license to reproduce, prepare Derivative Works of",
            "licence.user_cap",
        ),
        "licence.output_training": _canonical_clause(
            None, "prepare Derivative Works", "licence.output_training",
        ),
        "licence.fine_tuning": _canonical_clause(
            "permitted", "prepare Derivative Works", "licence.fine_tuning",
        ),
    },
}

for _spdx, _phrases in CANONICAL_LICENCE_SIGNATURES.items():
    _body = CANONICAL_LICENCE_BODIES[_spdx]
    for _phrase in _phrases:
        if _phrase not in _body:
            raise RuntimeError(f"{_spdx} signature is not in the canonical body: {_phrase}")
for _spdx, _rows in CANONICAL_LICENCE_READINGS.items():
    _body = CANONICAL_LICENCE_BODIES[_spdx]
    for _facet, _row in _rows.items():
        if _row.rule != _facet or _row.clause not in _body:
            raise RuntimeError(f"{_spdx} {_facet} clause is not in the canonical body")


def _strip_apache_appendix(residual: str) -> str | None:
    """Remove one verbatim Apache how-to and boilerplate notice.

    The copyright line between them stays, so :data:`CANONICAL_LICENCE_RESIDUALS`
    can require that line exactly. ``None`` when an ``APPENDIX:`` is present
    and the how-to or the boilerplate is not the canonical text.
    """
    start = residual.find(_APPENDIX_HEAD)
    if start < 0:
        if "APPENDIX:" in residual:
            return None
        return residual
    holder_at = start + len(_APPENDIX_HEAD)
    tail_at = residual.find(_APPENDIX_TAIL, holder_at)
    if tail_at < 0 or "APPENDIX:" in residual[tail_at + len(_APPENDIX_TAIL):]:
        return None
    holder = residual[holder_at:tail_at].strip()
    end = tail_at + len(_APPENDIX_TAIL)
    left = residual[:start].strip()
    right = residual[end:].strip()
    return " ".join(part for part in (left, holder, right) if part)


def _canonical_licence_id(text: str) -> str | None:
    """``mit`` or ``apache-2.0`` when the signature, body, and residual all match.

    The signature has to match and the canonical body has to be present. The
    text before and after that body, after :func:`_canonical_form` and
    whitespace stripping, has to be a pair in :data:`CANONICAL_LICENCE_RESIDUALS`.
    For Apache-2.0 the appendix how-to and boilerplate are removed first, and
    the copyright line that was between them is the ``after`` value.

    Returns ``None`` when the notice-retention rule is no longer the one this
    table applies, when a red-flag phrase is present, when the text outside
    the canonical body is longer than :data:`CANONICAL_LICENCE_OUTSIDE_LIMIT`,
    or when the residual pair is not one this code records. A new canonical
    file with a different copyright line is not read here until that residual
    is reviewed and added in code. The licence reader then reads the text.
    """
    if (
        "Keeping a copyright, licence, NOTICE or change notice is not attribution "
        "and not a condition."
        not in LICENCE_CONDITION_RULE
    ):
        return None
    form = _canonical_form(text)
    if any(flag in form.casefold() for flag in CANONICAL_LICENCE_RED_FLAGS):
        return None
    matched = [
        spdx for spdx, phrases in CANONICAL_LICENCE_SIGNATURES.items()
        if all(phrase in form for phrase in phrases)
    ]
    if len(matched) != 1:
        return None
    spdx = matched[0]
    body = CANONICAL_LICENCE_BODIES[spdx]
    start = form.find(body)
    if start < 0:
        return None
    if len(form) - len(body) > CANONICAL_LICENCE_OUTSIDE_LIMIT:
        return None
    before = form[:start].strip()
    after = form[start + len(body):].strip()
    if spdx == "apache-2.0":
        stripped = _strip_apache_appendix(after)
        if stripped is None:
            return None
        after = stripped.strip()
    if (before, after) not in CANONICAL_LICENCE_RESIDUALS[spdx]:
        return None
    return spdx


def _text_around_body(spdx: str, before: str, after: str, *, appendix: bool) -> str:
    body = CANONICAL_LICENCE_BODIES[spdx]
    if appendix:
        after = f"{_APPENDIX_HEAD}{after}{_APPENDIX_TAIL}"
    return " ".join(part for part in (before, body, after) if part)


for _spdx, _pairs in CANONICAL_LICENCE_RESIDUALS.items():
    for _before, _after in _pairs:
        _plain = _text_around_body(_spdx, _before, _after, appendix=False)
        if _canonical_licence_id(_plain) != _spdx:
            raise RuntimeError(f"{_spdx} residual is not recognised around the body")
        if _spdx == "apache-2.0" and _canonical_licence_id(
            _text_around_body(_spdx, _before, _after, appendix=True)
        ) != _spdx:
            raise RuntimeError(f"{_spdx} residual is not recognised with the appendix")


class CanonicalLicenceExtractor:
    """Reads the four ``licence.*`` facets from a canonical MIT or Apache-2.0 text.

    A deterministic extractor, so it counts as an independent second key.
    It accepts a ``licence_text`` region only. The text has to carry that
    licence's signature and its canonical body. The text before and after the
    body, after :func:`_canonical_form` and whitespace stripping, has to be a
    pair in :data:`CANONICAL_LICENCE_RESIDUALS`. For Apache-2.0 the how-to
    appendix and the boilerplate notice are removed first. The copyright line
    that was between them is the ``after`` residual, and it has to match
    exactly. A new canonical file with a different copyright line is not read
    here until that residual is reviewed and added in code. The licence reader
    then reads the region. The red-flag list is a second guard.

    The value for each facet is the one ``LICENCE_READING_RULES`` gives, with
    ``LICENCE_CONDITION_RULE`` applied: a duty to keep a notice is not a
    condition. The table quotes the operative clause and records the rule key.
    The reading's subject is the claim's name only when :func:`licence_is_bound`
    passes. A licence bound to ``claim.base_model`` also names the subject
    when that licence requires derivatives to carry its terms.
    """

    actor = VerificationActor(
        agent=VERIFY_AGENT, model_family=DETERMINISTIC, method="canonical-licence@1",
    )

    def accepts(self, text: str) -> bool:
        return _canonical_licence_id(text) is not None

    def extract(
        self,
        claim: Claim,
        text: str,
        *,
        bindings: Sequence[str] = (),
        binding_urls: Sequence[str | None] | None = None,
        licence_url: str | None = None,
        **_extra: object,
    ) -> list[Reading]:
        spdx = _canonical_licence_id(text)
        if spdx is None:
            raise ExtractorError("not a canonical MIT or Apache-2.0 licence")
        row = CANONICAL_LICENCE_READINGS[spdx].get(claim.field)
        if row is None or row.rule != claim.field or claim.field not in LICENCE_READING_RULES:
            raise ExtractorError(f"no canonical reading for {claim.field}")
        if row.clause not in _canonical_form(text):
            raise ExtractorError("operative clause is not in the licence text")
        subject = claim.names[0] if licence_is_bound(
            claim.names, bindings, licence_url, subject=claim.subject, page_urls=binding_urls,
            licence_text=text, base_model=claim.base_model,
        ) else None
        shown: JsonValue = None if row.value is None else str(row.value)
        return [Reading(subject=subject, value=shown)]


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


# USPS abbreviations as the SEC writes stateOfIncorporation for a US state.
# Kentucky is "KY" here. That is not the Cayman Islands (country KY).
_USPS_STATE = frozenset({
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC",
})
_SEC_STATE = re.compile(r'"stateOfIncorporation"\s*:\s*"([A-Z]{2})"')
_SEC_DESC = re.compile(r'"stateOfIncorporationDescription"\s*:\s*"([^"]+)"')
_JURISDICTION_CUE = re.compile(
    r"incorporat|organi[sz]ed under|laws of the state of|"
    r"jurisdiction of incorporation|company limited by shares|\bamtsgericht\b",
    re.IGNORECASE,
)
_US_STATE_NAME = (
    r"delaware|california|nevada|washington|new york|texas|massachusetts|florida|"
    r"illinois|colorado|virginia|maryland|georgia|pennsylvania|new jersey|ohio|"
    r"north carolina|arizona|oregon|utah|michigan|minnesota|wisconsin|connecticut|"
    r"district of columbia"
)
_FORMED = r"(?:incorporated|registered|formed|organi[sz]ed)"
# A country counts only from a phrase that states incorporation, not a headquarters
# or a governing-law mention. "laws of the state of Delaware" alone is governing law.
# The same words followed by Law, Act, or Code name a statute.
# Order does not matter; the reading is sorted.
_INCORPORATION_PHRASES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(
        r"(?i)\b(?:" + _US_STATE_NAME + r") (?:public benefit corporation|"
        r"(?:(?:non-?profit|not-for-profit|nonstock) )?corporation|"
        r"limited liability company|llc|company)\b(?! (?:law|act|code)\b)"
    ), "US"),
    (re.compile(r"(?i)\b" + _FORMED + r" (?:in|under the laws of)(?: the)?(?: state of)? (?:" + _US_STATE_NAME + r")\b"), "US"),
    (re.compile(r"(?i)\b(?:" + _FORMED + r" )(?:in|under the laws of) the cayman islands\b"), "KY"),
    (re.compile(r"(?i)\bcayman islands (?:exempted )?company\b"), "KY"),
    (re.compile(r"(?i)\b" + _FORMED + r" (?:in|under the laws of) (?:the )?(?:people's republic of china|prc)\b"), "CN"),
    (re.compile(r"(?i)\bincorporated in (?:mainland )?china\b"), "CN"),
    (re.compile(r"(?i)\b" + _FORMED + r" (?:in|under the laws of) hong kong\b"), "HK"),
    (re.compile(r"(?i)\b(?:incorporated|registered) in england and wales\b"), "GB"),
    (re.compile(r"(?i)\borgani[sz]ed under the laws of england and wales\b"), "GB"),
    (re.compile(r"(?i)\b" + _FORMED + r" in (?:the )?united kingdom\b"), "GB"),
    (re.compile(r"(?i)\b" + _FORMED + r" in (?:the federal republic of )?germany\b"), "DE"),
    (re.compile(r"(?i)\bgesellschaft mit beschr[aä]nkter haftung\b"), "DE"),
    (re.compile(r"(?i)\bamtsgericht\b(?:\s+\S+){0,6}\s+hrb\b"), "DE"),
    (re.compile(r"(?i)\b" + _FORMED + r" (?:in|under the laws of) (?:the republic of )?singapore\b"), "SG"),
    # An Exhibit 21 row is a whole legal suffix, a pipe, then the state, and the
    # state ends the cell. "Zinc" is not "Inc". A pipe before a state name in
    # any other table is not incorporation.
    (re.compile(
        r"(?i)\b(?:llc|l\.l\.c\.|inc\.?|corp\.?|corporation|ltd\.?|limited|l\.p\.)\s*\|\s*(?:"
        + _US_STATE_NAME + r")\s*(?:\||$)"
    ), "US"),
    (re.compile(r"(?i)\b" + _FORMED + r" in japan\b"), "JP"),
    (re.compile(r"(?i)\b" + _FORMED + r" in (?:the republic of korea|south korea)\b"), "KR"),
    (re.compile(r"(?i)\b" + _FORMED + r" in ireland\b"), "IE"),
    (re.compile(r"(?i)\b" + _FORMED + r" in the republic of ireland\b"), "IE"),
    (re.compile(r"(?i)\(cayman(?: islands)?\)"), "KY"),
    (re.compile(r"(?i)\b" + _FORMED + r" in (?:the )?netherlands\b"), "NL"),
    (re.compile(r"(?i)\b" + _FORMED + r" (?:in|under the laws of) (?:the )?british virgin islands\b"), "VG"),
    (re.compile(r"(?i)\b" + _FORMED + r" in bermuda\b"), "BM"),
    (re.compile(r"(?i)\bincorporated in (?:the )?cayman islands\b"), "KY"),
)
# SEC submissions name the country in stateOfIncorporationDescription. A US
# filer repeats the postal code there ("DE"). A foreign filer names the country
# ("Cayman Islands"). Map only that field, not a prose mention of the same words.
_SEC_DESC_COUNTRY = {
    "cayman islands": "KY",
    "hong kong": "HK",
    "china": "CN",
    "people's republic of china": "CN",
    "singapore": "SG",
    "ireland": "IE",
    "united kingdom": "GB",
    "netherlands": "NL",
    "bermuda": "BM",
    "british virgin islands": "VG",
    "japan": "JP",
    "korea": "KR",
    "republic of korea": "KR",
    "germany": "DE",
    "taiwan": "TW",
    "israel": "IL",
    "canada": "CA",
    "australia": "AU",
    "france": "FR",
    "switzerland": "CH",
    "luxembourg": "LU",
    "united states": "US",
}
# A cited region whose whole text is the incorporation jurisdiction, as on an
# SEC cover element. A longer page that merely mentions the name does not match.
_BARE_JURISDICTION = {
    "cayman islands": "KY",
    "hong kong": "HK",
    "delaware": "US",
    "singapore": "SG",
    "ireland": "IE",
    "bermuda": "BM",
    "british virgin islands": "VG",
    "people's republic of china": "CN",
    "china": "CN",
    "japan": "JP",
    "netherlands": "NL",
    "germany": "DE",
    "united kingdom": "GB",
    "england and wales": "GB",
    "united states": "US",
    # "Georgia" alone is the country as often as the US state. A state name
    # still counts when the phrase says "Georgia corporation".
    **{name: "US" for name in _US_STATE_NAME.split("|") if name != "georgia"},
}


def jurisdiction_codes(text: str) -> frozenset[str]:
    """ISO codes a legal page or registry filing states as incorporation."""
    found: set[str] = set()
    for match in _SEC_STATE.finditer(text):
        if match.group(1) in _USPS_STATE:
            found.add("US")
    for match in _SEC_DESC.finditer(text):
        label = match.group(1).strip()
        if label in _USPS_STATE:
            found.add("US")
            continue
        code = _SEC_DESC_COUNTRY.get(label.casefold())
        if code:
            found.add(code)
    for pattern, code in _INCORPORATION_PHRASES:
        if pattern.search(text):
            found.add(code)
    bare = re.sub(r"\s+", " ", text).strip().casefold()
    code = _BARE_JURISDICTION.get(bare)
    if code:
        found.add(code)
    return frozenset(found)


class LabJurisdictionExtractor:
    """Read country of incorporation with fixed phrases (``lab-jurisdiction@1``).

    The reading's subject is the claim's published name, so a lab page verifies
    a lab fact without the model's name appearing on it. No reading means the
    page did not state incorporation. That does not confirm a null.
    """

    actor = VerificationActor(agent=VERIFY_AGENT, model_family=DETERMINISTIC,
                              method="lab-jurisdiction@1")

    def accepts(self, text: str) -> bool:
        if jurisdiction_codes(text):
            return True
        return _JURISDICTION_CUE.search(text) is not None

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        if claim.field != "origin.lab_jurisdiction":
            return []
        codes = jurisdiction_codes(text)
        if not codes:
            return []
        return [Reading(claim.names[0], ", ".join(sorted(codes)))]


def deterministic_extractors() -> list[Extractor]:
    return [CanonicalLicenceExtractor(), StructuredDataExtractor(), OfferingPriceExtractor(),
            SubscriptionPageExtractor(), TableExtractor(), TransposedTableExtractor(),
            GovernanceProseExtractor(), KeyValueExtractor(), ModelPageExtractor(),
            LabJurisdictionExtractor()]


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


def _verify_jurisdiction_set(claim: Claim, regions: Regions, extractors: Sequence[Extractor], *,
                            today: date) -> Result:
    """A lab-jurisdiction set is the union of its cited regions, not any one of them.

    Every cited region has to be reachable and contribute a non-empty set of
    codes. ``lab-jurisdiction@1`` reads the region when it returns a reading.
    An earlier extractor that accepts the page for another facet and returns
    nothing does not decide the claim. Each region's codes are a subset of the
    claim. The union equals the claim. One region that states only part of the
    set does not verify it, and a region that adds a code the claim does not
    name is a mismatch.
    """
    claimed = {str(code).strip().upper() for code in claim.value}
    union: set[str] = set()
    actor: VerificationActor | None = None
    reasons: list[str] = []
    diffs: list[Diff] = []
    unreachable = False
    ordered = sorted(extractors, key=lambda e: e.actor.model_family != DETERMINISTIC)
    for source in claim.sources:
        _, kind = _source_kind(regions, source.source_id)
        for region_id in source.cited_regions:
            where = f"{source.source_id}#{region_id}"
            text = regions.text(source.source_id, source.snapshot_ref, region_id)
            if text is None:
                unreachable = True
                reasons.append(f"unreachable:{where}")
                continue
            accepting = _readers_for(ordered, claim, text, kind)
            independent = [item for item in accepting if _independent(claim, item.actor, today)]
            prefer = [item for item in independent if item.actor.method == "lab-jurisdiction@1"]
            readers = prefer + [item for item in independent if item not in prefer]
            extractor = None
            for item in readers:
                try:
                    got = item.extract(claim, text)
                except ExtractorError as exc:
                    reasons.append(f"extractor_error:{where}: {exc}")
                    continue
                if got:
                    extractor = item
                    break
            if extractor is None:
                reasons.append("no_independent_extractor" if accepting else f"no_extractor:{where}")
                diffs.append(Diff("value", sorted(claimed), None))
                continue
            actor = extractor.actor
            codes = jurisdiction_codes(text)
            if not codes:
                reasons.append(f"no_codes:{where}")
                diffs.append(Diff("value", sorted(claimed), None))
                continue
            if not codes <= claimed:
                diffs.append(Diff("value", sorted(claimed), ", ".join(sorted(codes))))
                continue
            union |= set(codes)
    if unreachable:
        if not _independent(claim, REGION_LOOKUP, today):
            return Result(claim.target, "skipped", reason="no_independent_extractor")
        return Result(claim.target, "unreachable",
                      _verification(claim, REGION_LOOKUP, "unreachable", today),
                      reason="; ".join(reasons))
    if union == claimed and not diffs and actor is not None:
        return Result(claim.target, "verified",
                      _verification(claim, actor, "verified", today))
    if actor is not None or diffs:
        if union != claimed and not any(d.field == "value" and d.found is not None for d in diffs):
            diffs.append(Diff("value", sorted(claimed), ", ".join(sorted(union)) or None))
        who = actor or REGION_LOOKUP
        return Result(claim.target, "mismatch",
                      _verification(claim, who, "mismatch", today, diffs), tuple(diffs))
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


def _binding_page(claim: Claim, regions: Regions, kind: str | None) -> bool:
    """A licence region whose kind the facet does not permit, beside a permitted one.

    The region can name the licence. It is not a reading, and it gives no
    outcome. A ``source_kind`` mismatch is only for a claim that cites no
    permitted kind at all.
    """
    if claim.value is not None or not claim.field.startswith("licence."):
        return False
    facet = _facet_or_none(claim.field)
    if facet is None:
        return False
    permitted = set(facet.permitted_source_kinds)
    if kind in permitted:
        return False
    for source in claim.sources:
        if not source.cited_regions:
            continue
        _, cited = _source_kind(regions, source.source_id)
        if cited in permitted:
            return True
    return False


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
    ``permitted_source_kinds``. ``CanonicalLicenceExtractor`` takes a
    ``licence_text`` region whose text is the canonical MIT licence or the
    Apache License 2.0 terms, and the licence reader is not asked about that
    text. ``LicenceExtractor`` reads every other permitted region. Any other
    cited region is a binding page. It is not a reading, for a known value or
    an absence. Deterministic extractors still read a ``licence_text`` source
    for every other claim, including ``model.weights_openness`` and ``origin.*``.
    """
    if claim.field.startswith("licence."):
        facet = _facet_or_none(claim.field)
        permitted = set(facet.permitted_source_kinds) if facet is not None else set()
        if kind not in permitted:
            return []
        if kind == "licence_text":
            canonical = [
                extractor for extractor in extractors
                if isinstance(extractor, CanonicalLicenceExtractor) and extractor.accepts(text)
            ]
            if canonical:
                return canonical
        return [extractor for extractor in extractors if isinstance(extractor, LicenceExtractor)]
    chosen = []
    for extractor in extractors:
        if isinstance(extractor, (LicenceExtractor, CanonicalLicenceExtractor)):
            continue
        if extractor.accepts(text):
            chosen.append(extractor)
    return chosen


def _binding_pages(claim: Claim, regions: Regions, source_id: str,
                   region_id: str) -> tuple[list[str], list[str | None]]:
    """Text and source URL of the claim's other cited regions."""
    pages: list[str] = []
    urls: list[str | None] = []
    url_of = getattr(regions, "source_url", None)
    for source in claim.sources:
        for cited in source.cited_regions:
            if source.source_id == source_id and cited == region_id:
                continue
            text = regions.text(source.source_id, source.snapshot_ref, cited)
            if text:
                pages.append(text)
                urls.append(url_of(source.source_id) if callable(url_of) else None)
    return pages, urls


def verify(claim: Claim, regions: Regions, extractors: Sequence[Extractor], *,
           today: date) -> Result:
    """Re-read ``claim`` from each cited region of its sources and compare.

    Deterministic extractors are tried before the rest, whatever the order given;
    the first that accepts a region and is independent of the collector reads it.
    A ``licence.*`` claim is read from a source kind in that facet's
    ``permitted_source_kinds``. ``CanonicalLicenceExtractor`` reads a
    ``licence_text`` region when the text is the canonical MIT licence or the
    Apache License 2.0 terms, and ``LicenceExtractor`` is not asked about that
    text. ``LicenceExtractor`` reads the other permitted regions. Other cited
    regions are binding pages. A binding page gives
    no outcome while the claim also cites a permitted kind. It is a
    ``source_kind`` mismatch only when the claim cites no permitted kind.
    Verified if any reading confirms the value; otherwise the first mismatch.
    A claim whose permitted regions all have no extractor, or all raised
    ``ExtractorError``, is skipped.
    ``origin.lab_jurisdiction`` is the exception: the cited regions are unioned,
    and every one of them has to contribute.
    """
    if isinstance(claim.value, dict) and "score" in claim.value:
        return _verify_evidence_reading(claim, regions, extractors, today=today)
    if claim.field == "origin.lab_jurisdiction" and isinstance(claim.value, list):
        return _verify_jurisdiction_set(claim, regions, extractors, today=today)

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
                if _binding_page(claim, regions, kind):
                    continue
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
                    if isinstance(extractor, (LicenceExtractor, CanonicalLicenceExtractor)):
                        url_of = getattr(regions, "source_url", None)
                        pages, page_urls = _binding_pages(
                            claim, regions, source.source_id, region_id,
                        )
                        readings = extractor.extract(
                            claim,
                            text,
                            cache_key=(source.snapshot_ref, region_id, claim.field),
                            bindings=pages,
                            binding_urls=page_urls,
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
        *, today: date, changed_only: bool = False, at: datetime | None = None,
        only: str | None = None) -> RunReport:
    """Verify what is queued; log every outcome and mark it checked. Skipped claims stay
    queued, unlogged and so quarantined.

    ``only`` keeps claims whose target id starts with that prefix. Other pending
    claims are not checked and not logged.
    """
    at = at or datetime.now(UTC)
    claims, unknown = queue.pending(changed_only=changed_only)
    if only:
        claims = [claim for claim in claims if claim.target.id.startswith(only)]
        unknown = [target for target in unknown if target.id.startswith(only)]
    report = RunReport(changed_only, unknown=unknown)
    for claim in claims:
        result = verify(claim, regions, extractors, today=today)
        report.results.append(result)
        if result.verification is not None:
            log.append(result.verification)
            queue.checked(result, at=at)
    return report


__all__ = [
    "Claim", "CanonicalLicenceExtractor", "ClaudeCLICompletion", "CONDITION_KEYS", "Diff",
    "Extractor", "ExtractorError",
    "GovernanceProseExtractor", "KeyValueExtractor", "LLMCache", "LLMCallBudgetExceededError",
    "LabJurisdictionExtractor",
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
