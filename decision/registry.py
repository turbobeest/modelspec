"""Load and validate the registries in `registry/*.yaml` (MODEL-133).

Facets, units, source kinds, providers, harnesses and domains are open sets
(design §3.4, ADR 0002). This module holds no list of any of them: it reads the
YAML, checks every entry, and answers typed lookups. Adding a facet, provider,
harness or domain is a registry entry, never an edit here.

Two rules the engine depends on:

* **Unknown IDs fail loudly.** Every accessor raises `UnknownIdError` naming
  the kind, the ID and the nearest registered IDs. Nothing is silently ignored
  (design §6.1).
* **An unknown harness is `unregistered`.** `Registry.resolve_harness` maps any
  string to a registered `name@major.minor` or to the literal `unregistered`,
  never to free text (design §4.1).
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterable, Literal, Mapping

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO_ROOT / "registry"

#: What a harness that is not registered is reported as.
UNREGISTERED = "unregistered"

Subject = Literal["model", "offering", "evidence"]
Tier = Literal["guaranteed", "best_effort"]
Risk = Literal["capability", "governance"]
UnknownPolicy = Literal["may_qualify", "not_satisfied"]

SUBJECTS = ("model", "offering", "evidence")
TIERS = ("guaranteed", "best_effort")
RISKS = ("capability", "governance")
KINDS = ("number", "enum", "boolean", "date", "set", "range")
PROVIDER_KINDS = ("lab_api", "cloud", "inference", "aggregator")
SHOWN_BY = ("address", "incorporation", "governing_law")
BASES = ("service_terms", "website_terms")

#: A facet definition shorter than this is a label, not a definition.
MIN_DEFINITION_WORDS = 12

FACET_ID = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")
SNAKE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
KEBAB_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
COUNTRY = re.compile(r"^[A-Z]{2}$")
HARNESS_REF = re.compile(r"^([a-z0-9][a-z0-9-]*)@(\d+)\.(\d+)(?:[.+-][0-9A-Za-z.+-]*)?$")


class RegistryError(ValueError):
    """A registry file is missing, malformed, or has an invalid entry."""


class UnknownIdError(RegistryError, KeyError):
    """A lookup named an ID no registry holds."""

    def __init__(self, kind: str, id_: str, known: Iterable[str]):
        self.kind, self.id = kind, id_
        close = difflib.get_close_matches(id_, list(known), n=3, cutoff=0.6)
        hint = f"; did you mean {', '.join(repr(c) for c in close)}?" if close else ""
        super().__init__(f"unknown {kind} {id_!r}: not in registry/{_FILE_FOR.get(kind, kind)}{hint}")

    def __str__(self) -> str:  # KeyError would repr() the message
        return str(self.args[0])


_FILE_FOR = {
    "facet": "facets.yaml", "unit": "facets.yaml", "source_kind": "facets.yaml",
    "provider": "providers.yaml", "harness": "harnesses.yaml", "domain": "domains.yaml",
}


# ── entries ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Unit:
    id: str
    definition: str


@dataclass(frozen=True)
class SourceKind:
    id: str
    definition: str


@dataclass(frozen=True)
class ValueType:
    kind: str
    values: tuple[str, ...] | None = None
    values_from: str | None = None
    #: A known value may be the literal `unbounded` (no limit).
    unbounded: bool = False
    #: A known value may be the literal `not_offered`.
    not_offered: bool = False


@dataclass(frozen=True)
class Parameter:
    """A facet that is a family: one value per member of a named list."""
    name: str
    values_from: str


@dataclass(frozen=True)
class Facet:
    id: str
    subject: Subject
    value_type: ValueType
    definition: str
    tier: Tier
    risk: Risk
    permitted_source_kinds: tuple[str, ...]
    unit: str | None = None
    parameter: Parameter | None = None
    required_qualifiers: tuple[str, ...] = ()
    computed_by: str | None = None

    @property
    def unknown_policy(self) -> UnknownPolicy:
        """Capability unknowns may qualify; governance unknowns are not satisfied."""
        return "may_qualify" if self.risk == "capability" else "not_satisfied"


@dataclass(frozen=True)
class Sourced:
    """A value read from a URL on a date, or unknown (`value is None`)."""
    value: str | None = None
    source: str | None = None
    read: str | None = None
    note: str = ""

    @property
    def known(self) -> bool:
        return self.value is not None


@dataclass(frozen=True)
class Jurisdiction(Sourced):
    entity: str = ""
    shown_by: str = ""
    basis: str = ""


@dataclass(frozen=True)
class Provider:
    id: str
    name: str
    url: str
    kind: str
    jurisdiction: Jurisdiction
    attestations: Mapping[str, Sourced]
    v1_availability_field: str | None = None


@dataclass(frozen=True)
class HarnessVersion:
    id: str
    source: str | None
    read: str
    note: str = ""


@dataclass(frozen=True)
class Harness:
    id: str
    name: str
    url: str | None
    version_records: tuple[HarnessVersion, ...]
    url_note: str = ""

    @property
    def versions(self) -> tuple[str, ...]:
        return tuple(v.id for v in self.version_records)


@dataclass(frozen=True)
class Domain:
    id: str
    name: str
    definition: str
    proxy_only: bool = False


# ── the registry ───────────────────────────────────────────────────────────


class Registry:
    """Typed, validated lookups over every registry file."""

    def __init__(self, *, units, source_kinds, facets, providers, harnesses, domains,
                 named_lists: Mapping[str, Callable[[], frozenset[str]] | None]):
        self._units: Mapping[str, Unit] = MappingProxyType(units)
        self._source_kinds: Mapping[str, SourceKind] = MappingProxyType(source_kinds)
        self._facets: Mapping[str, Facet] = MappingProxyType(facets)
        self._providers: Mapping[str, Provider] = MappingProxyType(providers)
        self._harnesses: Mapping[str, Harness] = MappingProxyType(harnesses)
        self._domains: Mapping[str, Domain] = MappingProxyType(domains)
        self._named_lists = named_lists
        self._harness_versions = frozenset(v for h in harnesses.values() for v in h.versions)

    @staticmethod
    def _get(kind: str, table: Mapping[str, Any], id_: str):
        try:
            return table[id_]
        except (KeyError, TypeError):
            raise UnknownIdError(kind, str(id_), table) from None

    def facet(self, id_: str) -> Facet:
        return self._get("facet", self._facets, id_)

    def unit(self, id_: str) -> Unit:
        return self._get("unit", self._units, id_)

    def source_kind(self, id_: str) -> SourceKind:
        return self._get("source_kind", self._source_kinds, id_)

    def provider(self, id_: str) -> Provider:
        return self._get("provider", self._providers, id_)

    def harness(self, id_: str) -> Harness:
        """A harness by name (`claude-code`), not by version."""
        return self._get("harness", self._harnesses, id_)

    def domain(self, id_: str) -> Domain:
        return self._get("domain", self._domains, id_)

    def facets(self) -> tuple[Facet, ...]:
        return tuple(self._facets.values())

    def units(self) -> tuple[Unit, ...]:
        return tuple(self._units.values())

    def source_kinds(self) -> tuple[SourceKind, ...]:
        return tuple(self._source_kinds.values())

    def providers(self) -> tuple[Provider, ...]:
        return tuple(self._providers.values())

    def harnesses(self) -> tuple[Harness, ...]:
        return tuple(self._harnesses.values())

    def domains(self) -> tuple[Domain, ...]:
        return tuple(self._domains.values())

    def resolve_harness(self, raw: str | None) -> str:
        """The registered `name@major.minor` for `raw`, else `unregistered`."""
        m = HARNESS_REF.match((raw or "").strip())
        if not m:
            return UNREGISTERED
        canonical = f"{m.group(1)}@{int(m.group(2))}.{int(m.group(3))}"
        return canonical if canonical in self._harness_versions else UNREGISTERED

    def allowed_values(self, facet: Facet) -> frozenset[str] | None:
        """The values an enum or set facet admits; `None` for an open list
        (a code standard such as ISO 3166, or a list validated elsewhere)."""
        vt = facet.value_type
        if vt.values is not None:
            return frozenset(vt.values)
        if vt.values_from is None:
            return None
        producer = self._named_lists[vt.values_from]
        return producer() if producer else None


# ── loading and validation ─────────────────────────────────────────────────


def _named_lists(repo_root: Path, raw: Mapping[str, list[dict]]) -> dict[str, Callable[[], frozenset[str]] | None]:
    """Every name a `values_from` may use. `None` marks an open list whose
    members are validated where the values are written, not here."""

    def ids(name: str, key: str = "id") -> Callable[[], frozenset[str]]:
        return lambda: frozenset(str(e.get(key)) for e in raw.get(name, []))

    def harness_versions() -> frozenset[str]:
        return frozenset(str(v.get("id")) for h in raw.get("harnesses", []) for v in h.get("versions") or [])

    def model_classes() -> frozenset[str]:
        from api.classes import CLASS_BY_ID
        return frozenset(CLASS_BY_ID)

    def architecture_types() -> frozenset[str]:
        from schema.enums import ArchitectureType
        return frozenset(a.value for a in ArchitectureType)

    def stems(directory: str, pattern: str) -> Callable[[], frozenset[str]]:
        return lambda: frozenset(
            p.stem for p in (repo_root / directory).glob(pattern)
            if not p.name.startswith("_") and p.name not in {"README.md", "LICENSE.md", "AUTHORING.md"})

    return {
        "registry:providers": ids("providers"),
        "registry:harnesses": harness_versions,
        "registry:domains": ids("domains"),
        "model_classes": model_classes,
        "architecture_types": architecture_types,
        "benchmarks": stems("benchmarks", "*.md"),
        "hardware": stems("hardware", "*.yaml"),
        "iso_3166_1_alpha_2": None,
        "bcp_47": None,
        "model_ids": None,
        "outcome_task_types": None,
    }


class _Errors:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, where: str, message: str) -> None:
        self.items.append(f"{where}: {message}")

    def raise_if_any(self) -> None:
        if self.items:
            raise RegistryError("invalid registry:\n  " + "\n  ".join(self.items))


def _read(root: Path, name: str, key: str) -> list[dict]:
    path = root / f"{name}.yaml"
    if not path.is_file():
        raise RegistryError(f"missing registry file {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise RegistryError(f"{path}: not valid YAML: {exc}") from exc
    if data.get("schema_version") != 1:
        raise RegistryError(f"{path}: schema_version must be 1")
    entries = data.get(key)
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise RegistryError(f"{path}: `{key}` must be a list of mappings")
    return entries


def _keys(err: _Errors, where: str, entry: dict, required: set[str], optional: set[str]) -> None:
    for k in sorted(required - entry.keys()):
        err.add(where, f"missing required field {k!r}")
    for k in sorted(entry.keys() - required - optional):
        err.add(where, f"unknown field {k!r}")


def _iso_date(value: Any) -> bool:
    try:
        date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


def _https(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("https://")


def _unique(err: _Errors, file: str, entries: list[dict], pattern: re.Pattern, label: str) -> None:
    seen: set[str] = set()
    for e in entries:
        id_ = e.get("id")
        if not isinstance(id_, str) or not pattern.match(id_):
            err.add(f"{file} {id_!r}", f"id must be {label}")
        elif id_ in seen:
            err.add(f"{file} {id_!r}", "duplicate id")
        seen.add(str(id_))


def _described(err: _Errors, where: str, entry: dict, min_words: int = 1) -> None:
    text = entry.get("definition")
    if not isinstance(text, str) or len(text.split()) < min_words:
        err.add(where, f"definition must be at least {min_words} words")


def _load_units_and_kinds(err: _Errors, root: Path) -> tuple[dict, dict]:
    tables = []
    for key in ("units", "source_kinds"):
        entries = _read(root, "facets", key)
        _unique(err, f"facets.yaml {key}", entries, SNAKE_ID, "snake_case")
        for e in entries:
            where = f"facets.yaml {key} {e.get('id')!r}"
            _keys(err, where, e, {"id", "definition"}, set())
            _described(err, where, e)
        tables.append(entries)
    units = {e["id"]: Unit(e["id"], str(e.get("definition", ""))) for e in tables[0] if "id" in e}
    kinds = {e["id"]: SourceKind(e["id"], str(e.get("definition", ""))) for e in tables[1] if "id" in e}
    return units, kinds


def _value_type(err: _Errors, where: str, raw: Any, unit: Any, units: Mapping, lists: Mapping) -> ValueType | None:
    if not isinstance(raw, dict):
        err.add(where, "value_type must be a mapping with a `kind`")
        return None
    kind = raw.get("kind")
    if kind not in KINDS:
        err.add(where, f"value_type.kind {kind!r} must be one of {', '.join(KINDS)}")
        return None
    optional = {"unbounded", "not_offered"} if kind == "number" else set()
    if kind in ("enum", "set"):
        optional = {"values", "values_from"}
    _keys(err, where, raw, {"kind"}, optional)
    if kind in ("number", "range"):
        if unit is None:
            err.add(where, f"a {kind} facet needs a unit")
        elif unit not in units:
            err.add(where, f"unit {unit!r} is not registered in facets.yaml units")
    elif unit is not None:
        err.add(where, f"a {kind} facet takes no unit")
    values, values_from = raw.get("values"), raw.get("values_from")
    if kind in ("enum", "set"):
        if (values is None) == (values_from is None):
            err.add(where, f"a {kind} facet needs exactly one of values or values_from")
        if values is not None and (not isinstance(values, list) or not values
                                   or len(set(map(str, values))) != len(values)):
            err.add(where, "values must be a non-empty list without duplicates")
        if values_from is not None and values_from not in lists:
            err.add(where, f"values_from {values_from!r} is not a known list ({', '.join(sorted(lists))})")
    return ValueType(
        kind=kind,
        values=tuple(map(str, values)) if isinstance(values, list) else None,
        values_from=values_from,
        unbounded=bool(raw.get("unbounded", False)),
        not_offered=bool(raw.get("not_offered", False)),
    )


def _load_facets(err: _Errors, root: Path, units: Mapping, kinds: Mapping, lists: Mapping) -> dict[str, Facet]:
    entries = _read(root, "facets", "facets")
    _unique(err, "facets.yaml", entries, FACET_ID, "dotted snake_case, such as model.context_window")
    required = {"id", "subject", "value_type", "definition", "tier", "risk", "permitted_source_kinds"}
    optional = {"unit", "parameter", "required_qualifiers", "computed_by"}
    out: dict[str, Facet] = {}
    for e in entries:
        where = f"facets.yaml {e.get('id')!r}"
        _keys(err, where, e, required, optional)
        _described(err, where, e, MIN_DEFINITION_WORDS)
        for field_, allowed in (("subject", SUBJECTS), ("tier", TIERS), ("risk", RISKS)):
            if e.get(field_) not in allowed:
                err.add(where, f"{field_} {e.get(field_)!r} must be one of {', '.join(allowed)}")
        vt = _value_type(err, where, e.get("value_type"), e.get("unit"), units, lists)
        psk = e.get("permitted_source_kinds")
        if not isinstance(psk, list) or not psk:
            err.add(where, "permitted_source_kinds must be a non-empty list")
            psk = []
        for k in psk:
            if k not in kinds:
                err.add(where, f"permitted source kind {k!r} is not registered in facets.yaml source_kinds")
        param = e.get("parameter")
        parameter = None
        if param is not None:
            if not isinstance(param, dict) or set(param) != {"name", "values_from"}:
                err.add(where, "parameter must be {name, values_from}")
            elif param["values_from"] not in lists:
                err.add(where, f"parameter values_from {param['values_from']!r} is not a known list")
            else:
                parameter = Parameter(str(param["name"]), str(param["values_from"]))
        rq = e.get("required_qualifiers", [])
        if not isinstance(rq, list) or not all(isinstance(q, str) for q in rq):
            err.add(where, "required_qualifiers must be a list of names")
            rq = []
        if vt is None or not isinstance(e.get("id"), str):
            continue
        out.setdefault(e["id"], Facet(
            id=e["id"], subject=e.get("subject"), value_type=vt,
            definition=" ".join(str(e.get("definition", "")).split()),
            tier=e.get("tier"), risk=e.get("risk"), permitted_source_kinds=tuple(psk),
            unit=e.get("unit"), parameter=parameter, required_qualifiers=tuple(rq),
            computed_by=e.get("computed_by"),
        ))
    return out


def _sourced(err: _Errors, where: str, raw: Any, extra: set[str] = frozenset()) -> dict | None:
    """`unknown`, or a mapping with a value, an https source and a read date."""
    if raw == "unknown":
        return None
    if not isinstance(raw, dict):
        err.add(where, "must be `unknown` or a mapping with value, source and read")
        return None
    _keys(err, where, raw, {"value", "source", "read"}, {"note"} | set(extra))
    if "source" in raw and not _https(raw["source"]):
        err.add(where, "source must be an https URL")
    if "read" in raw and not _iso_date(raw["read"]):
        err.add(where, "read must be a date YYYY-MM-DD")
    return raw


def _load_providers(err: _Errors, root: Path) -> dict[str, Provider]:
    entries = _read(root, "providers", "providers")
    _unique(err, "providers.yaml", entries, KEBAB_ID, "kebab-case")
    required = {"id", "name", "url", "kind", "jurisdiction", "attestations"}
    availability: set[str] | None = None
    out: dict[str, Provider] = {}
    for e in entries:
        where = f"providers.yaml {e.get('id')!r}"
        _keys(err, where, e, required, {"v1_availability_field"})
        if not _https(e.get("url")):
            err.add(where, "url must be an https URL")
        if e.get("kind") not in PROVIDER_KINDS:
            err.add(where, f"kind {e.get('kind')!r} must be one of {', '.join(PROVIDER_KINDS)}")
        field_ = e.get("v1_availability_field")
        if field_ is not None:
            if availability is None:
                from schema.card import Availability, PlatformEntry
                availability = {n for n, f in Availability.model_fields.items() if f.annotation is PlatformEntry}
            if field_ not in availability:
                err.add(where, f"v1_availability_field {field_!r} is not a platform field on Availability")
        j = _sourced(err, f"{where} jurisdiction", e.get("jurisdiction"), {"entity", "shown_by", "basis"})
        jurisdiction = Jurisdiction()
        if j is not None:
            if not COUNTRY.match(str(j.get("value", ""))):
                err.add(f"{where} jurisdiction", "value must be an ISO 3166-1 alpha-2 code")
            if j.get("shown_by") not in SHOWN_BY:
                err.add(f"{where} jurisdiction", f"shown_by must be one of {', '.join(SHOWN_BY)}")
            if j.get("basis") not in BASES:
                err.add(f"{where} jurisdiction", f"basis must be one of {', '.join(BASES)}")
            if not j.get("entity"):
                err.add(f"{where} jurisdiction", "entity must name the contracting entity")
            jurisdiction = Jurisdiction(
                value=str(j.get("value")), source=j.get("source"), read=str(j.get("read")),
                note=str(j.get("note", "")), entity=str(j.get("entity", "")),
                shown_by=str(j.get("shown_by", "")), basis=str(j.get("basis", "")))
        attestations: dict[str, Sourced] = {}
        raw_att = e.get("attestations")
        if not isinstance(raw_att, dict):
            err.add(where, "attestations must be a mapping of name to `unknown` or a sourced value")
            raw_att = {}
        for name, raw in raw_att.items():
            a = _sourced(err, f"{where} attestation {name!r}", raw)
            attestations[str(name)] = Sourced() if a is None else Sourced(
                value=str(a.get("value")), source=a.get("source"), read=str(a.get("read")),
                note=str(a.get("note", "")))
        if isinstance(e.get("id"), str):
            out.setdefault(e["id"], Provider(
                id=e["id"], name=str(e.get("name", "")), url=str(e.get("url", "")),
                kind=str(e.get("kind", "")), jurisdiction=jurisdiction,
                attestations=MappingProxyType(attestations), v1_availability_field=field_))
    return out


def _load_harnesses(err: _Errors, root: Path) -> dict[str, Harness]:
    entries = _read(root, "harnesses", "harnesses")
    _unique(err, "harnesses.yaml", entries, KEBAB_ID, "kebab-case")
    out: dict[str, Harness] = {}
    for e in entries:
        where = f"harnesses.yaml {e.get('id')!r}"
        _keys(err, where, e, {"id", "name", "url", "versions"}, {"url_note"})
        url = e.get("url")
        if url is None and not e.get("url_note"):
            err.add(where, "a harness with no public url needs a url_note saying why")
        elif url is not None and not _https(url):
            err.add(where, "url must be an https URL or null")
        records: list[HarnessVersion] = []
        versions = e.get("versions")
        if not isinstance(versions, list) or not versions:
            err.add(where, "versions must be a non-empty list")
            versions = []
        for v in versions:
            if not isinstance(v, dict):
                err.add(where, "each version must be a mapping")
                continue
            vid = v.get("id")
            vwhere = f"{where} version {vid!r}"
            _keys(err, vwhere, v, {"id", "source", "read"}, {"note"})
            if not re.fullmatch(rf"{re.escape(str(e.get('id')))}@\d+\.\d+", str(vid)):
                err.add(vwhere, "version id must be canonical name@major.minor")
            if v.get("source") is not None and not _https(v.get("source")):
                err.add(vwhere, "source must be an https URL or null")
            if v.get("source") is None and url is not None:
                err.add(vwhere, "a version of a public harness needs a source")
            if not _iso_date(v.get("read")):
                err.add(vwhere, "read must be a date YYYY-MM-DD")
            records.append(HarnessVersion(str(vid), v.get("source"), str(v.get("read")), str(v.get("note", ""))))
        if len({r.id for r in records}) != len(records):
            err.add(where, "duplicate version id")
        if isinstance(e.get("id"), str):
            out.setdefault(e["id"], Harness(
                id=e["id"], name=str(e.get("name", "")), url=url,
                version_records=tuple(records), url_note=str(e.get("url_note", ""))))
    return out


def _load_domains(err: _Errors, root: Path) -> dict[str, Domain]:
    entries = _read(root, "domains", "domains")
    _unique(err, "domains.yaml", entries, SNAKE_ID, "snake_case")
    out: dict[str, Domain] = {}
    for e in entries:
        where = f"domains.yaml {e.get('id')!r}"
        _keys(err, where, e, {"id", "name", "definition"}, {"proxy_only"})
        _described(err, where, e, MIN_DEFINITION_WORDS)
        if not isinstance(e.get("proxy_only", False), bool):
            err.add(where, "proxy_only must be true or false")
        if isinstance(e.get("id"), str):
            out.setdefault(e["id"], Domain(
                id=e["id"], name=str(e.get("name", "")),
                definition=" ".join(str(e.get("definition", "")).split()),
                proxy_only=e.get("proxy_only", False) is True))
    return out


def load(root: Path | None = None, *, repo_root: Path | None = None) -> Registry:
    """Read and validate every registry file under `root` (default `registry/`).

    Raises `RegistryError` listing every problem found, not just the first.
    `repo_root` is where file-backed lists (benchmark pages, hardware SKUs) are
    read from; it defaults to this repository.
    """
    root = Path(root) if root is not None else REGISTRY_DIR
    repo_root = Path(repo_root) if repo_root is not None else REPO_ROOT
    err = _Errors()
    raw = {
        "providers": _read(root, "providers", "providers"),
        "harnesses": _read(root, "harnesses", "harnesses"),
        "domains": _read(root, "domains", "domains"),
    }
    lists = _named_lists(repo_root, raw)
    units, kinds = _load_units_and_kinds(err, root)
    facets = _load_facets(err, root, units, kinds, lists)
    providers = _load_providers(err, root)
    harnesses = _load_harnesses(err, root)
    domains = _load_domains(err, root)
    err.raise_if_any()
    return Registry(units=units, source_kinds=kinds, facets=facets, providers=providers,
                    harnesses=harnesses, domains=domains, named_lists=lists)


@cache
def default() -> Registry:
    """The repository's own registries, loaded once."""
    return load()


# Module-level shortcuts over the default registry. Other `decision` modules
# (the contract, the engine) call these rather than holding a Registry.
def facet(id_: str) -> Facet:
    return default().facet(id_)


def provider(id_: str) -> Provider:
    return default().provider(id_)


def harness(id_: str) -> Harness:
    return default().harness(id_)


def domain(id_: str) -> Domain:
    return default().domain(id_)
