"""The snapshot: verified facts and evidence, compiled, hashed and signed (MODEL-138).

A decision reads one snapshot and nothing else (design §4.2, §6). This module
builds it, gates it and loads it:

* ``build_snapshot`` compiles models, offerings and evidence into a columnar
  snapshot. Only values whose latest verification is ``verified`` enter, and
  only when every source they name resolves to a registered URL that is not an
  excluded source. A ``verified`` from the collector's own model family is not
  a second key (MODEL-159): it is skipped as if never logged, while a
  same-family mismatch still counts. Retired models and their offerings go to
  a separate ``archive`` section. With a premier list, the ``lineup`` holds only the
  premier models and their offerings; other active models are counted in
  ``out_of_lineup`` and left out (MODEL-157). The legacy flat
  ``benchmarks.scores`` block is never read.
* The **completeness gate** fails the build when a guaranteed facet is unknown
  or unverified for a premier model or one of its offerings, naming the
  subject, the facet and the source. Computed facets (``computed_by`` in the
  registry, such as ``estimate.capability``) are skipped: slice 1 does not
  compute them.
* ``Snapshot.write`` serialises canonical JSON, gzips it with a fixed header,
  and signs the content hash with HMAC-SHA256 when ``MODELSPEC_SNAPSHOT_KEY`` is
  set. The same inputs give the same bytes.
* ``load_snapshot`` checks the hash and, when a key is available, the
  signature, then builds the in-memory index: three-valued bitsets over the
  candidates, per facet value.

Inputs are MODEL-134's records (``decision.model``) or their serialised dicts;
the builder reads them by field name, so either works.
"""

from __future__ import annotations

import gzip
import hashlib
import hmac
import io
import json
import math
import os
from bisect import bisect_left, bisect_right
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal, Protocol, runtime_checkable

import yaml

from decision.excluded import ExcludedSources, excluded_sources
from decision.model import value_hash, verification_counts

FORMAT = "modelspec.decision-snapshot"
FORMAT_VERSION = 1
KEY_ENV = "MODELSPEC_SNAPSHOT_KEY"
SIGNATURE_ALG = "hmac-sha256"

FactState = Literal["known", "unknown", "not_disclosed", "requires_contract"]
Lifecycle = Literal["active", "deprecated", "retired"]
Directness = Literal["direct", "proxy"]
FACT_STATES = ("known", "unknown", "not_disclosed", "requires_contract")
LIFECYCLES = ("active", "deprecated", "retired")

#: A number facet may hold these literals instead of a number (MODEL-133).
UNBOUNDED = "unbounded"
NOT_OFFERED = "not_offered"


# ── errors ─────────────────────────────────────────────────────────────────


class SnapshotError(ValueError):
    """A snapshot could not be built or read."""


class SnapshotBuildError(SnapshotError):
    """The inputs cannot make a snapshot."""


class SnapshotIntegrityError(SnapshotError):
    """A snapshot file failed its format, hash or signature check."""


@dataclass(frozen=True)
class Gap:
    """One guaranteed facet a premier subject lacks."""

    model: str
    subject: str
    facet: str
    reason: str
    sources: tuple[str, ...] = ()

    def __str__(self) -> str:
        where = ", ".join(self.sources) if self.sources else "no source recorded"
        return f"{self.subject}: {self.facet} is {self.reason}; source: {where}"


class CompletenessError(SnapshotBuildError):
    """The premier-set completeness gate failed (design §5)."""

    def __init__(self, gaps: Sequence[Gap]):
        self.gaps = tuple(gaps)
        lines = "\n  ".join(str(g) for g in self.gaps)
        super().__init__(f"completeness gate: {len(self.gaps)} guaranteed fact(s) missing "
                         f"for the premier set:\n  {lines}")


# ── the values an index returns ────────────────────────────────────────────


@dataclass(frozen=True)
class FactValue:
    state: FactState
    value: Any = None
    sources: tuple[str, ...] = ()
    record_id: str | None = field(default=None, compare=False)


UNKNOWN = FactValue("unknown")


@dataclass(frozen=True)
class EvidenceValue:
    benchmark_id: str
    version: str | None
    subcategory: str | None
    value: float
    unit: str | None
    measured_by: str | None
    effort: str | None
    harness: str | None
    #: The evidence date; ``None`` when the source gave less than a full date.
    date: date | None
    source_ids: tuple[str, ...]
    verified: bool = True
    #: Set by ``evidence_for_domain`` only: how directly the benchmark measures
    #: the domain asked about. An addition to the agreed field list.
    directness: Directness | None = None
    record_id: str | None = field(default=None, compare=False)
    date_type: str | None = None
    source_snapshot: str | None = None


@dataclass(frozen=True)
class Bitset3:
    """Three disjoint bitsets over ``candidates()``: bit ``i`` is candidate ``i``."""

    passing: int
    failing: int
    unknown: int

    def __post_init__(self) -> None:
        if self.passing & self.failing or self.passing & self.unknown or self.failing & self.unknown:
            raise ValueError("a Bitset3's three sets must be disjoint")


@runtime_checkable
class SnapshotIndex(Protocol):
    snapshot_id: str

    def candidates(self) -> Sequence[str]: ...

    def lifecycle(self, cid: str) -> Lifecycle: ...

    def fact(self, cid: str, facet_id: str) -> FactValue: ...

    def ids_where(self, facet_id: str, op: str, arg: Any) -> Bitset3: ...

    def evidence(self, cid: str, benchmark_id: str, *, measured_by: set[str] | None = None,
                 effort: str | None = None, harness: str | None = None,
                 after: date | None = None) -> Sequence[EvidenceValue]: ...

    def evidence_where(
        self,
        benchmark_id: str,
        op: str,
        arg: Any,
        *,
        measured_by: set[str] | None = None,
        effort: str | None = None,
        harness: str | None = None,
        after: date | None = None,
        direct: bool = False,
        domains: Iterable[str] = (),
    ) -> Bitset3: ...

    def direct_for(self, benchmark_id: str, domains: Iterable[str] = ()) -> bool: ...

    def evidence_for_domain(self, cid: str, domain_id: str) -> Sequence[EvidenceValue]: ...


@runtime_checkable
class ExplanationIndex(SnapshotIndex, Protocol):
    """Snapshot metadata and retained records needed to transport a decision."""

    def require_explanation_records(self) -> None: ...
    def kind(self, cid: str) -> Literal["model", "offering"]: ...
    def model_of(self, cid: str) -> str: ...
    def source_url(self, source_id: str) -> str: ...
    def record(self, record_id: str) -> Mapping[str, Any]: ...
    def facet_ids(self) -> tuple[str, ...]: ...
    def domain_ids(self) -> tuple[str, ...]: ...
    def benchmark_ids(self) -> tuple[str, ...]: ...


# ── inputs ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SnapshotInputs:
    """What a snapshot is compiled from. Records may be MODEL-134 objects or dicts."""

    models: Sequence[Any] = ()
    offerings: Sequence[Any] = ()
    evidence: Sequence[Any] = ()
    #: Registered source ID -> URL.
    sources: Mapping[str, str] = field(default_factory=dict)
    #: Benchmark ID -> ((domain ID, directness), ...), from the benchmark pages.
    benchmark_domains: Mapping[str, Sequence[Sequence[str]]] = field(default_factory=dict)
    #: The verification log. The latest verification of a target wins, over an
    #: inline one too.
    verifications: Sequence[Any] = ()


def _as_dict(record: Any) -> dict[str, Any]:
    if isinstance(record, Mapping):
        return dict(record)
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json", by_alias=True)
    raise SnapshotBuildError(f"not a record: {record!r}")


def _counts(v: Mapping[str, Any]) -> bool:
    """A same-family ``verified`` is not a second key: it neither admits nor displaces."""
    return verification_counts(str(v["outcome"]), str(v["collector"]["model_family"]),
                               str(v["verifier"]["model_family"]))


def _offering_id(o: Mapping[str, Any]) -> str:
    return f"{o['provider']}/{o['model']}/{o['region']}/{o['tier']}"


# ── canonical form, hash and signature ─────────────────────────────────────


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def content_hash(content: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(content)).hexdigest()


def snapshot_id_for(digest: str) -> str:
    return "snap_" + digest.removeprefix("sha256:")[:16]


def _key_bytes(key: bytes | str | None) -> bytes | None:
    if key is None or key == "" or key == b"":
        return None
    return key.encode("utf-8") if isinstance(key, str) else key


def _sign(digest: str, key: bytes) -> str:
    return hmac.new(key, digest.encode("ascii"), hashlib.sha256).hexdigest()


_FROM_ENV: Any = object()


def env_key() -> bytes | None:
    """The signing key from ``MODELSPEC_SNAPSHOT_KEY``, or ``None``."""
    return _key_bytes(os.environ.get(KEY_ENV))


def _record_fields(
    record: Mapping[str, Any], prefix: tuple[str, ...] = (),
) -> Iterable[tuple[tuple[str, ...], Any]]:
    for key, value in record.items():
        path = (*prefix, key)
        if isinstance(value, dict) and value:
            yield from _record_fields(value, path)
        else:
            yield path, value


def _pack_records(records: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Intern repeated provenance values, including verification and source data.

    Nested dictionary paths preserve absent fields, explicit nulls and empty
    dictionaries distinctly. Values stay JSON until a record is requested.
    """
    flattened = {rid: dict(_record_fields(record)) for rid, record in records.items()}
    fields = sorted({path for record in flattened.values() for path in record})
    values: list[str] = []
    positions: dict[bytes, int] = {}
    rows = {}
    for rid, record in sorted(flattened.items()):
        row = []
        for path in fields:
            if path not in record:
                row.append(None)
                continue
            encoded = canonical_json(record[path])
            if encoded not in positions:
                positions[encoded] = len(values)
                values.append(encoded.decode("utf-8"))
            row.append(positions[encoded])
        rows[rid] = row
    return {"fields": fields, "values": values, "rows": rows}


def _unpack_record(table: Mapping[str, Any], rid: str) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for path, position in zip(table["fields"], table["rows"][rid]):
        if position is None:
            continue
        target = record
        for key in path[:-1]:
            target = target.setdefault(key, {})
        target[path[-1]] = json.loads(table["values"][position])
    return record


# ── the built snapshot ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class Snapshot:
    content: Mapping[str, Any]
    content_hash: str
    snapshot_id: str

    def envelope(self, key: bytes | str | None = _FROM_ENV) -> dict[str, Any]:
        key = env_key() if key is _FROM_ENV else _key_bytes(key)
        signature = None if key is None else {"alg": SIGNATURE_ALG,
                                              "value": _sign(self.content_hash, key)}
        return {"format": FORMAT, "format_version": FORMAT_VERSION,
                "snapshot_id": self.snapshot_id, "content_hash": self.content_hash,
                "signature": signature, "content": self.content}

    def to_bytes(self, key: bytes | str | None = _FROM_ENV) -> bytes:
        buf = io.BytesIO()
        # A fixed mtime and no file name keep the gzip header deterministic.
        with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as gz:
            gz.write(canonical_json(self.envelope(key)))
        return buf.getvalue()

    def write(self, path: str | Path, *, key: bytes | str | None = _FROM_ENV) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.to_bytes(key))
        return path


# ── building ───────────────────────────────────────────────────────────────


class _Compiler:
    def __init__(self, inputs: SnapshotInputs, registry: Any, guard: ExcludedSources | None):
        self.inputs = inputs
        self.registry = registry
        self.guard = guard
        self.sources = {str(k): str(v) for k, v in inputs.sources.items()}
        #: subject id (``None`` when a record names none) -> why its records stayed out.
        self.excluded: dict[str | None, Counter[str]] = {}
        #: (subject, facet) -> (reason, source URLs), for the gate's messages.
        self.rejected: dict[tuple[str, str], tuple[str, tuple[str, ...]]] = {}
        self.log = self._verification_log(inputs.verifications)
        #: subject id -> {"kind", "model", "lifecycle"}
        self.subjects: dict[str, dict[str, Any]] = {}
        #: subject id -> facet -> [state, value, source ids]
        self.facts: dict[str, dict[str, list[Any]]] = {}
        self.facet_subject: dict[str, str] = {}
        self.evidence: dict[str, list[list[Any]]] = {}
        self.records: dict[str, dict[str, Any]] = {}
        self.fact_records: dict[str, dict[str, str]] = {}

    # verification ------------------------------------------------------------

    @staticmethod
    def _verification_log(
        rows: Iterable[Any],
    ) -> dict[tuple[str, str, str], tuple[str, int, dict]]:
        latest: dict[tuple[str, str, str], tuple[str, int, dict]] = {}
        for i, raw in enumerate(rows):
            v = _as_dict(raw)
            if not _counts(v):
                continue
            target = v["target"]
            key = (target["kind"], target["id"], str(target.get("value_hash") or ""))
            entry = (str(v["date"]), i + 1, v)
            if key not in latest or entry[:2] >= latest[key][:2]:
                latest[key] = entry
        return latest

    def _verification(self, kind: str, rid: Any, inline: Any, value: Any) -> dict | None:
        """The winning verification record, or ``None``."""
        expected = value_hash(value)
        inline_record = None if inline is None else _as_dict(inline)
        best = (
            None
            if inline_record is None
            or not _counts(inline_record)
            or inline_record.get("target", {}).get("value_hash") != expected
            else (str(inline_record["date"]), 0, inline_record)
        )
        logged = self.log.get((kind, str(rid), expected)) if rid is not None else None
        if logged is not None and (best is None or logged[:2] >= best[:2]):
            best = logged
        return None if best is None else best[2]

    def _outcome(self, kind: str, rid: Any, inline: Any, value: Any) -> str:
        record = self._verification(kind, rid, inline, value)
        return "unverified" if record is None else str(record["outcome"])

    def _retain(self, kind: str, record: dict) -> str:
        rid = str(record.get("id") or content_hash(record))
        value = record.get("value") if kind == "fact" else record.get("score")
        retained = {**record, "verification": self._verification(
            kind, record.get("id"), record.get("verification"), value)}
        if rid in self.records and self.records[rid] != retained:
            raise SnapshotBuildError(f"duplicate record ID {rid}")
        self.records[rid] = retained
        return rid

    # admission ---------------------------------------------------------------

    def _source_ids(self, refs: Iterable[Any]) -> list[str]:
        return sorted({str(_as_dict(r)["source_id"]) for r in refs or ()})

    def _admit(self, kind: str, rid: Any, inline: Any, value: Any, source_ids: list[str],
               extra_urls: Iterable[Any] = (), benchmark: Any = None) -> str | None:
        """Why a record stays out, or ``None`` when it enters."""
        urls = [self.sources[s] for s in source_ids if s in self.sources]
        if self.guard is not None and (any(self.guard.url(u) for u in [*urls, *extra_urls])
                                       or (benchmark is not None
                                           and self.guard.benchmark(benchmark))):
            return "excluded_source"
        outcome = self._outcome(kind, rid, inline, value)
        if outcome != "verified":
            return f"quarantined ({outcome})"
        if not source_ids:
            return "unsourced"
        if len(urls) != len(source_ids):
            return "unresolved_source"
        return None

    def _exclude(self, sid: str | None, reason: str) -> None:
        kind = "quarantined" if reason.startswith("quarantined") else reason
        self.excluded.setdefault(sid, Counter())[kind] += 1

    def _reject(self, key: tuple[str, str], reason: str, source_ids: list[str]) -> None:
        self._exclude(key[0], reason)
        urls = tuple(self.sources.get(s, s) for s in source_ids)
        self.rejected[key] = (reason, urls)

    # subjects ----------------------------------------------------------------

    def _check_facet(self, facet_id: str, kind: str) -> None:
        if self.registry is not None:
            try:
                self.registry.facet(facet_id)
            except KeyError as exc:
                raise SnapshotBuildError(f"facet {facet_id!r} is not registered") from exc
        seen = self.facet_subject.setdefault(facet_id, kind)
        if seen != kind:
            raise SnapshotBuildError(f"facet {facet_id!r} is used on both a {seen} and a {kind}")

    def _add_facts(self, sid: str, kind: str, facts: Iterable[Any]) -> None:
        row = self.facts.setdefault(sid, {})
        for raw in facts or ():
            f = _as_dict(raw)
            facet_id, state = str(f["facet"]), str(f["state"])
            self._check_facet(facet_id, kind)
            if state not in FACT_STATES:
                raise SnapshotBuildError(f"{sid}: {facet_id} has an unknown state {state!r}")
            if facet_id in row or (sid, facet_id) in self.rejected:
                raise SnapshotBuildError(f"{sid}: {facet_id} is stated twice")
            source_ids = self._source_ids(f.get("sources"))
            if state == "unknown":
                self.rejected[(sid, facet_id)] = ("unknown", tuple(
                    self.sources.get(s, s) for s in source_ids))
                continue
            reason = self._admit(
                "fact", f.get("id"), f.get("verification"), f.get("value"), source_ids
            )
            if reason is not None:
                self._reject((sid, facet_id), reason, source_ids)
                continue
            self.fact_records.setdefault(sid, {})[facet_id] = self._retain("fact", f)
            row[facet_id] = [state, f.get("value") if state == "known" else None, source_ids]

    def add_model(self, raw: Any) -> None:
        m = _as_dict(raw)
        mid, lifecycle = str(m["id"]), str(m.get("lifecycle"))
        if lifecycle not in LIFECYCLES:
            raise SnapshotBuildError(f"{mid}: lifecycle {lifecycle!r} is not one of {LIFECYCLES}")
        if mid in self.subjects:
            raise SnapshotBuildError(f"model {mid} appears twice")
        self.subjects[mid] = {"kind": "model", "model": mid, "lifecycle": lifecycle}
        self._add_facts(mid, "model", m.get("facts"))

    def add_offering(self, raw: Any) -> None:
        o = _as_dict(raw)
        oid, mid = _offering_id(o), str(o["model"])
        if mid not in self.subjects:
            raise SnapshotBuildError(f"offering {oid} names model {mid}, which is not in the catalogue")
        if oid in self.subjects:
            raise SnapshotBuildError(f"offering {oid} appears twice")
        self.subjects[oid] = {"kind": "offering", "model": mid,
                              "lifecycle": self.subjects[mid]["lifecycle"]}
        self._add_facts(oid, "offering", o.get("facts"))
        # An offering's identity is its provider, region and tier: structural,
        # not a sourced claim, so they carry no source.
        row = self.facts[oid]
        for part in ("provider", "region", "tier"):
            facet_id = f"offering.{part}"
            if facet_id not in row:
                self._check_facet(facet_id, "offering")
                row[facet_id] = ["known", str(o[part]), []]

    def add_evidence(self, raw: Any) -> None:
        e = _as_dict(raw)
        subject = e.get("subject") or {}
        sid = subject.get("id")
        if sid is None:
            self._exclude(None, "quarantined")  # no subject: cannot be v2-verified
            return
        if sid not in self.subjects:
            raise SnapshotBuildError(f"evidence {e.get('id')!r} names {sid}, which is not in the catalogue")
        source_ids = self._source_ids(e.get("sources"))
        reason = self._admit("evidence", e.get("id"), e.get("verification"), e.get("score"), source_ids,
                             extra_urls=[e.get("source_url")], benchmark=e.get("benchmark_id"))
        if reason is not None:
            self._exclude(sid, reason)
            return
        self.evidence.setdefault(sid, []).append([
            str(e["benchmark_id"]), e.get("benchmark_version") or None, e.get("subcategory"),
            float(e["score"]), e.get("unit"), e.get("measured_by"), e.get("effort"),
            e.get("harness"), str(e.get("evidence_date") or "") or None, source_ids,
            self._retain("evidence", e), e.get("date_type"),
            next((r.get("snapshot_ref") for r in e.get("sources", [])
                  if r["source_id"] == source_ids[0]), None),
        ])

    # output ------------------------------------------------------------------

    def _section(self, ids: list[str]) -> dict[str, Any]:
        index = {sid: i for i, sid in enumerate(ids)}
        columns: dict[str, dict[str, list[Any]]] = {}
        for sid in ids:
            for facet_id, (state, value, sources) in self.facts.get(sid, {}).items():
                col = columns.setdefault(facet_id, {"row": [], "state": [], "value": [],
                                                    "sources": []})
                col["row"].append(index[sid])
                col["state"].append(state)
                col["value"].append(value)
                col["sources"].append(sources)
        return {
            "candidates": [{"id": sid, **self.subjects[sid]} for sid in ids],
            "facets": columns,
            "evidence": {sid: sorted(self.evidence[sid], key=lambda r: (
                r[0], r[8] or "", r[3], canonical_json(r))) for sid in ids if sid in self.evidence},
        }

    def content(self, as_of: date | None, premier: Iterable[str] | None = None) -> dict[str, Any]:
        """The snapshot content. With ``premier``, the lineup is the premier set.

        Retired models always go to the archive. Active and deprecated models
        outside the premier set leave the snapshot, with their offerings,
        evidence and records; only their number is kept, as ``out_of_lineup``.
        """
        wanted = None if premier is None else set(premier)
        archive = sorted(s for s, v in self.subjects.items() if v["lifecycle"] == "retired")
        lineup = sorted(s for s, v in self.subjects.items() if v["lifecycle"] != "retired"
                        and (wanted is None or v["model"] in wanted))
        kept = {*lineup, *archive}
        out_of_lineup = sum(1 for s, v in self.subjects.items()
                            if v["kind"] == "model" and s not in kept)
        sources: set[str] = set()
        record_ids: set[str] = set()
        for sid in kept:
            for _state, _value, source_ids in self.facts.get(sid, {}).values():
                sources.update(source_ids)
            record_ids.update(self.fact_records.get(sid, {}).values())
            for row in self.evidence.get(sid, ()):
                sources.update(row[9])
                record_ids.add(row[10])
        excluded: Counter[str] = Counter()
        for sid, counts in self.excluded.items():
            if sid is None or sid in kept:
                excluded.update(counts)
        domains = {}
        for bench, tags in sorted(self.inputs.benchmark_domains.items()):
            if self.guard is not None and self.guard.benchmark(bench):
                continue
            domains[str(bench)] = sorted([str(d), str(k)] for d, k in tags)
        return {
            "format_version": FORMAT_VERSION,
            "as_of": as_of.isoformat() if as_of else None,
            "facet_subjects": dict(sorted(self.facet_subject.items())),
            "lineup": self._section(lineup),
            "archive": self._section(archive),
            "out_of_lineup": out_of_lineup,
            "benchmark_domains": domains,
            "sources": {s: self.sources[s] for s in sorted(sources)},
            "excluded": dict(sorted(excluded.items())),
            "record_table": _pack_records({r: self.records[r] for r in record_ids}),
            "fact_records": {sid: rows for sid, rows in self.fact_records.items() if sid in kept},
        }

    # the gate ----------------------------------------------------------------

    def gaps(self, premier: Iterable[str]) -> list[Gap]:
        if self.registry is None:
            raise SnapshotBuildError("the completeness gate needs the facet registry")
        guaranteed = [f for f in self.registry.facets()
                      if f.tier == "guaranteed" and not getattr(f, "computed_by", None)
                      and f.subject in ("model", "offering")]
        out: list[Gap] = []
        for mid in sorted(set(premier)):
            subject = self.subjects.get(mid)
            if subject is None:
                out.append(Gap(mid, mid, "(model)", "not in the catalogue"))
                continue
            if subject["lifecycle"] == "retired":
                continue  # retired models leave the premier set (design §5)
            offerings = sorted(s for s, v in self.subjects.items()
                               if v["kind"] == "offering" and v["model"] == mid)
            for f in sorted(guaranteed, key=lambda f: f.id):
                for sid in ([mid] if f.subject == "model" else offerings):
                    if f.id in self.facts.get(sid, {}):
                        continue
                    reason, urls = self.rejected.get((sid, f.id), ("unknown (no fact)", ()))
                    if reason == "unknown":
                        reason = "unknown (stated as unknown)"
                    out.append(Gap(mid, sid, f.id, reason, urls))
        return out


def default_registry() -> Any:
    try:
        from decision import registry
    except ImportError as exc:  # MODEL-133 not present
        raise SnapshotBuildError(f"the facet registry is not available: {exc}") from exc
    return registry.default()


def build_snapshot(inputs: SnapshotInputs, *, registry: Any = None,
                   premier: Iterable[str] | None = None, as_of: date | None = None,
                   guard: ExcludedSources | None = None, gate: bool = True) -> Snapshot:
    """Compile ``inputs``. With ``premier``, the lineup is the premier set.

    With ``premier`` and ``gate`` (the default), the completeness gate runs
    first. ``gate=False`` keeps the premier lineup but skips the gate, for an
    audit that must run while facts are still missing (MODEL-146).
    ``registry`` validates facet IDs and names the guaranteed facets; the gate
    requires it. ``guard`` drops excluded sources and scans the output;
    ``build_from_repo`` always passes it.
    """
    c = _Compiler(inputs, registry, guard)
    for m in inputs.models:
        c.add_model(m)
    for o in inputs.offerings:
        c.add_offering(o)
    for e in inputs.evidence:
        c.add_evidence(e)
    premier = None if premier is None else tuple(premier)
    if premier is not None and gate:
        gaps = c.gaps(premier)
        if gaps:
            raise CompletenessError(gaps)
    content = c.content(as_of, premier)
    if guard is not None:
        text = canonical_json(content).decode("utf-8")
        hit = guard.text.search(text)
        bad = [u for u in content["sources"].values() if guard.url(u)]
        if hit or bad:
            raise SnapshotBuildError(
                f"excluded source in the snapshot output: {hit.group(0) if hit else bad[0]!r}")
    digest = content_hash(content)
    return Snapshot(content=content, content_hash=digest, snapshot_id=snapshot_id_for(digest))


# ── reading the repository ─────────────────────────────────────────────────


_LIFECYCLE_FROM_STATUS = {"deprecated": "deprecated", "sunset": "deprecated"}


def collect_repo(root: Path) -> SnapshotInputs:
    """Read the snapshot's inputs from a repository checkout.

    * Cards (``models/``): ``lifecycle`` (else the v1 ``status``: deprecated and
      sunset map to ``deprecated``, everything else to ``active``), v2 ``facts``,
      and ``benchmarks.evidence`` rows. ``benchmarks.scores`` is never read.
    * Offerings: ``offerings/<provider>/<lab>/<model>.yaml``, each a list.
    * Sources: canonical ``registry/sources.yaml``; see ``verification/README.md``.
    * Domains: each benchmark page's ``domains`` tags.
    * The verification log: ``verification/log.jsonl``.
    """
    from pipeline.load import load_benchmarks, load_models

    root = Path(root)
    models, evidence = [], []
    for card in load_models(root):
        mid = card.model_id
        front = card.front
        lifecycle = front.get("lifecycle") or _LIFECYCLE_FROM_STATUS.get(
            str(front.get("status") or ""), "active")
        facts = []
        for f in front.get("facts") or []:
            facts.append({"subject": {"kind": "model", "id": mid},
                          "id": f"{mid}#{f.get('facet')}", **f})
        models.append({"id": mid, "lifecycle": lifecycle, "facts": facts})
        for row in card.evidence:
            evidence.append({"subject": {"kind": "model", "id": mid}, **row})
    offerings = []
    for path in sorted((root / "offerings").glob("*/*/*.yaml")):
        rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if not isinstance(rows, list):
            raise SnapshotBuildError(f"{path}: an offering file is a list")
        for o in rows:
            oid = _offering_id(o)
            o = dict(o)
            o["facts"] = [{"subject": {"kind": "offering", "id": oid},
                           "id": f"{oid}#{f.get('facet')}", **f} for f in o.get("facts") or []]
            offerings.append(o)
    from decision.sources import load_sources

    sources = {
        source_id: str(source.url)
        for source_id, source in load_sources(root / "registry" / "sources.yaml").items()
    }
    domains = {}
    for b in load_benchmarks(root):
        tags = b.front.get("domains") or []
        if tags:
            domains[b.benchmark_id] = tuple((str(t["id"]), str(t["directness"])) for t in tags)
    verifications = []
    verification_log = root / "verification" / "log.jsonl"
    if verification_log.is_file():
        for line in verification_log.read_text(encoding="utf-8").splitlines():
            if line.strip():
                verifications.append(json.loads(line))
    return SnapshotInputs(models=models, offerings=offerings, evidence=evidence, sources=sources,
                          benchmark_domains=domains, verifications=verifications)


def load_premier(path: str | Path) -> tuple[str, ...]:
    """The premier model IDs from a YAML file: a list, or ``models:`` a list.

    Each item is an ID or a mapping with ``id`` or ``model_id``.
    """
    path = Path(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SnapshotBuildError(f"cannot read the premier list {path}: {exc}") from exc
    items = data.get("models") if isinstance(data, Mapping) else data
    ids = set()
    for item in items or []:
        mid = item.get("id") or item.get("model_id") if isinstance(item, Mapping) else item
        if not isinstance(mid, str) or not mid:
            raise SnapshotBuildError(f"{path}: premier entry {item!r} has no model id")
        ids.add(mid)
    if not ids:
        raise SnapshotBuildError(f"{path}: no premier models listed")
    return tuple(sorted(ids))


def build_from_repo(root: Path, *, premier: str | Path | None, as_of: date | None,
                    registry: Any = None, gate: bool = True) -> Snapshot:
    """The production build: collect, guard, gate and compile."""
    root = Path(root)
    return build_snapshot(
        collect_repo(root),
        registry=registry if registry is not None else default_registry(),
        premier=load_premier(premier) if premier is not None else None,
        as_of=as_of,
        guard=excluded_sources(),
        gate=gate,
    )


# ── loading ────────────────────────────────────────────────────────────────


def _date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _key(value: Any) -> tuple[str, Any]:
    if isinstance(value, str):
        return "str", value
    if isinstance(value, bool):
        return "bool", value
    if isinstance(value, int | float):
        return "number", value
    return "json", json.dumps(value, sort_keys=True)


def _ordered(value: Any) -> Any:
    if value == UNBOUNDED:
        return math.inf
    if isinstance(value, date):
        return value.isoformat()
    return value


def _holds(value: Any, op: str, arg: Any) -> bool:
    """Whether a known value satisfies ``op arg``."""
    if op in ("=", "=="):
        if isinstance(value, list):
            return isinstance(arg, (list, tuple, set, frozenset)) and sorted(value) == sorted(arg)
        return _ordered(value) == _ordered(arg)
    if op == "!=":
        return not _holds(value, "=", arg)
    if op in ("in", "not_in"):
        members = {_key(_ordered(a)) for a in arg}
        found = (any(_key(v) in members for v in value) if isinstance(value, list)
                 else _key(_ordered(value)) in members)
        return found if op == "in" else not found
    if op == "contains":
        return isinstance(value, list) and arg in value
    if op == "contains_all":
        return isinstance(value, list) and set(arg) <= set(value)
    if op == "contains_any":
        return isinstance(value, list) and bool(set(arg) & set(value))
    if op in ("<", "<=", ">", ">=", "between"):
        if value == NOT_OFFERED or isinstance(value, (list, bool)):
            return False
        v = _ordered(value)
        try:
            if op == "between":
                low, high = arg
                return _ordered(low) <= v <= _ordered(high)
            a = _ordered(arg)
            return {"<": v < a, "<=": v <= a, ">": v > a, ">=": v >= a}[op]
        except TypeError as exc:
            raise SnapshotError(f"cannot compare {value!r} {op} {arg!r}") from exc
    raise SnapshotError(f"unknown operator {op!r}")


def _equality_key(value: Any) -> tuple[str, Any]:
    ordered = _ordered(value)
    if isinstance(ordered, list):
        return "list", tuple(sorted(_key(_ordered(member)) for member in ordered))
    return "scalar", _key(ordered)


class _FacetBitsets:
    """Bitsets for one facet, built once from its known values."""

    def __init__(self, rows: Iterable[tuple[int, Any]], *, alternatives: bool = False):
        self.alternatives = alternatives
        self.known = 0
        self.collections = 0
        self.exact: dict[tuple[str, Any], int] = {}
        self.members: dict[tuple[str, Any], int] = {}
        self.contains: dict[tuple[str, Any], int] = {}
        ordered: dict[Any, int] = {}
        self._ordered_usable = True
        for row, raw in rows:
            bit = 1 << row
            self.known |= bit
            values = raw if alternatives else (raw,)
            for value in values:
                key = _equality_key(value)
                self.exact[key] = self.exact.get(key, 0) | bit
                members = value if isinstance(value, list) and not alternatives else (value,)
                if isinstance(value, list) and not alternatives:
                    self.collections |= bit
                for member in members:
                    member_key = _key(_ordered(member))
                    self.members[member_key] = self.members.get(member_key, 0) | bit
                    if isinstance(value, list) and not alternatives:
                        self.contains[member_key] = self.contains.get(member_key, 0) | bit
                if value == NOT_OFFERED or isinstance(value, (list, bool)):
                    continue
                try:
                    ordered_value = _ordered(value)
                    ordered[ordered_value] = ordered.get(ordered_value, 0) | bit
                except (TypeError, ValueError):
                    self._ordered_usable = False
        try:
            self.ordered_values = tuple(sorted(ordered))
        except TypeError:
            self._ordered_usable = False
            self.ordered_values = ()
        prefixes = [0]
        for value in self.ordered_values:
            prefixes.append(prefixes[-1] | ordered[value])
        self.prefixes = tuple(prefixes)

    def _ordered(self, op: str, arg: Any) -> int | None:
        if not self._ordered_usable:
            return None
        try:
            if op == "between":
                low, high = (_ordered(value) for value in arg)
                left = bisect_left(self.ordered_values, low)
                right = bisect_right(self.ordered_values, high)
                return 0 if left > right else self.prefixes[right] & ~self.prefixes[left]
            value = _ordered(arg)
            if op == "<":
                return self.prefixes[bisect_left(self.ordered_values, value)]
            if op == "<=":
                return self.prefixes[bisect_right(self.ordered_values, value)]
            if op == ">":
                return self.prefixes[-1] & ~self.prefixes[bisect_right(self.ordered_values, value)]
            if op == ">=":
                return self.prefixes[-1] & ~self.prefixes[bisect_left(self.ordered_values, value)]
        except (TypeError, ValueError):
            return None
        return None

    def passing(self, op: str, arg: Any) -> int | None:
        if op in ("=", "=="):
            return self.exact.get(_equality_key(arg), 0)
        if op == "!=":
            key = _equality_key(arg)
            if self.alternatives:
                passing = 0
                for value_key, bits in self.exact.items():
                    if value_key != key:
                        passing |= bits
                return passing
            return self.known & ~self.exact.get(key, 0)
        if op in ("in", "not_in"):
            hit = 0
            for value in arg:
                hit |= self.members.get(_key(_ordered(value)), 0)
            return self.known & (hit if op == "in" else ~hit)
        if op == "contains":
            return self.contains.get(_key(_ordered(arg)), 0)
        if op in ("contains_all", "contains_any"):
            values = tuple(arg)
            if op == "contains_all":
                if not values:
                    return self.collections
                passing = self.known
                for value in values:
                    passing &= self.contains.get(_key(_ordered(value)), 0)
                return passing
            passing = 0
            for value in values:
                passing |= self.contains.get(_key(_ordered(value)), 0)
            return passing
        if op in ("<", "<=", ">", ">=", "between"):
            return self._ordered(op, arg)
        return None


class _Evidence(dict[str, tuple[EvidenceValue, ...]]):
    """Materialise one candidate's evidence on first access.

    An offering answers its model's evidence: capability belongs to the model,
    and an offering is that model as one provider sells it. The offering's own
    measurements of a benchmark, when it has any, replace its model's for that
    benchmark. The stored snapshot keeps evidence under its subject only.
    """

    def __init__(self, rows: Mapping[str, Sequence[Sequence[Any]]],
                 model_of: Mapping[str, str]):
        super().__init__()
        self.rows = rows
        self.model_of = model_of

    def _rows(self, cid: str) -> list[Sequence[Any]]:
        own = list(self.rows.get(cid, ()))
        model = self.model_of.get(cid, cid)
        if model == cid:
            return own
        measured = {r[0] for r in own}
        inherited = [r for r in self.rows.get(model, ()) if r[0] not in measured]
        return sorted(own + inherited, key=lambda r: (r[0], r[8] or "", r[3], canonical_json(r)))

    def __missing__(self, cid: str) -> tuple[EvidenceValue, ...]:
        self[cid] = tuple(
            EvidenceValue(benchmark_id=r[0], version=r[1], subcategory=r[2], value=r[3],
                          unit=r[4], measured_by=r[5], effort=r[6], harness=r[7],
                          date=_date(r[8]), source_ids=tuple(r[9]),
                          record_id=r[10] if len(r) > 10 else None,
                          date_type=r[11] if len(r) > 11 else None,
                          source_snapshot=r[12] if len(r) > 12 else None)
            for r in self._rows(cid))
        return self[cid]


class LoadedSnapshot:
    """The in-memory index over one snapshot. Implements ``SnapshotIndex``."""

    def __init__(self, envelope: Mapping[str, Any], *, include_archive: bool,
                 signature_verified: bool):
        content = envelope["content"]
        self.snapshot_id: str = envelope["snapshot_id"]
        self.content_hash: str = envelope["content_hash"]
        self.signature_verified = signature_verified
        self.as_of = _date(content.get("as_of"))
        self.excluded: dict[str, int] = dict(content.get("excluded") or {})
        #: Active models the build left out because they are not in the premier set.
        self.out_of_lineup: int = int(content.get("out_of_lineup") or 0)
        self._sources: dict[str, str] = dict(content["sources"])
        self._records = content.get("records", {})
        self._record_table = content.get("record_table")
        self.explanation_rebuild_required = (
            None
            if "fact_records" in content and ("record_table" in content or "records" in content)
            else "snapshot predates retained verification records; rebuild it before explaining"
        )
        sections = [content["lineup"]] + ([content["archive"]] if include_archive else [])

        rows: list[tuple[dict[str, Any], dict[str, Any], int]] = []
        for section in sections:
            for i, cand in enumerate(section["candidates"]):
                rows.append((cand, section, i))
        rows.sort(key=lambda r: r[0]["id"])
        self._ids: tuple[str, ...] = tuple(r[0]["id"] for r in rows)
        self._row = {cid: i for i, cid in enumerate(self._ids)}
        self._meta = {r[0]["id"]: r[0] for r in rows}
        self._all = (1 << len(self._ids)) - 1

        facts: dict[str, dict[int, FactValue]] = {}
        for section in sections:
            local = [c["id"] for c in section["candidates"]]
            for facet_id, col in section["facets"].items():
                target = facts.setdefault(facet_id, {})
                for r, state, value, srcs in zip(col["row"], col["state"], col["value"],
                                                 col["sources"]):
                    target[self._row[local[r]]] = FactValue(
                        state, value, tuple(srcs),
                        content.get("fact_records", {}).get(local[r], {}).get(facet_id))
        # An offering is its model as sold: it answers its model's facets.
        subjects = content.get("facet_subjects") or {}
        for facet_id, by_row in facts.items():
            if subjects.get(facet_id) != "model":
                continue
            for cid, meta in self._meta.items():
                if meta["kind"] == "offering":
                    row, model_row = self._row[cid], self._row.get(meta["model"])
                    if row not in by_row and model_row in by_row:
                        by_row[row] = by_row[model_row]
        self._facts = facts

        self._facet_bits = {
            facet_id: _FacetBitsets(
                (row, fv.value) for row, fv in by_row.items() if fv.state == "known"
            )
            for facet_id, by_row in facts.items()
        }

        self._evidence = _Evidence({cid: rows for section in sections
                                    for cid, rows in section["evidence"].items()},
                                   {cid: meta["model"] for cid, meta in self._meta.items()})
        self._evidence_bits: dict[tuple[Any, ...], _FacetBitsets] = {}
        self._benchmarks = tuple(sorted(content["benchmark_domains"]))
        self._domains: dict[str, list[tuple[str, str]]] = {}
        for bench, tags in content["benchmark_domains"].items():
            for domain_id, directness in tags:
                self._domains.setdefault(domain_id, []).append((bench, directness))

    # SnapshotIndex -----------------------------------------------------------

    def candidates(self) -> Sequence[str]:
        return self._ids

    def _check(self, cid: str) -> int:
        try:
            return self._row[cid]
        except KeyError:
            raise KeyError(f"{cid!r} is not a candidate in snapshot {self.snapshot_id}") from None

    def lifecycle(self, cid: str) -> Lifecycle:
        self._check(cid)
        return self._meta[cid]["lifecycle"]

    def fact(self, cid: str, facet_id: str) -> FactValue:
        return self._facts.get(facet_id, {}).get(self._check(cid), UNKNOWN)

    def ids_where(self, facet_id: str, op: str, arg: Any) -> Bitset3:
        """Candidates passing, failing, or unknown on ``facet op arg``.

        Operators: ``=`` (or ``==``), ``!=``, ``<``, ``<=``, ``>``, ``>=``,
        ``between`` (a (low, high) pair, inclusive), ``in``, ``not_in``,
        ``contains``, ``contains_all``, ``contains_any`` (on set facets) and
        ``known``. Any state but ``known`` is unknown; ``known`` itself is
        never unknown. ``unbounded`` exceeds every number; ``not_offered``
        fails every ordered comparison.
        """
        column = self._facet_bits.get(facet_id)
        known = 0 if column is None else column.known
        if op == "known":
            return Bitset3(known, self._all & ~known, 0)
        passing = None if column is None else column.passing(op, arg)
        if passing is None:
            passing = 0
            by_row = self._facts.get(facet_id, {})
            for row in self._rows(known):
                if _holds(by_row[row].value, op, arg):
                    passing |= 1 << row
        return Bitset3(passing, known & ~passing, self._all & ~known)

    def evidence_where(
        self,
        benchmark_id: str,
        op: str,
        arg: Any,
        *,
        measured_by: set[str] | None = None,
        effort: str | None = None,
        harness: str | None = None,
        after: date | None = None,
        direct: bool = False,
        domains: Iterable[str] = (),
    ) -> Bitset3:
        """Three-valued evidence condition, indexed lazily per qualifier set.

        ``direct`` admits the benchmark only when it is direct for one of
        ``domains``, the capabilities asked about (see ``direct_for``).
        """
        admits = not direct or self.direct_for(benchmark_id, domains)
        key = (
            benchmark_id,
            None if measured_by is None else frozenset(measured_by),
            effort,
            harness,
            after,
            admits,
        )
        column = self._evidence_bits.get(key)
        if column is None:
            admitted = []
            for row, cid in enumerate(self._ids if admits else ()):
                values = tuple(
                    evidence.value
                    for evidence in self.evidence(
                        cid,
                        benchmark_id,
                        measured_by=measured_by,
                        effort=effort,
                        harness=harness,
                        after=after,
                    )
                )
                if values:
                    admitted.append((row, values))
            column = _FacetBitsets(admitted, alternatives=True)
            self._evidence_bits[key] = column
        passing = column.passing(op, arg)
        if passing is None:
            passing = 0
            for row, cid in enumerate(self._ids if admits else ()):
                values = self.evidence(
                    cid,
                    benchmark_id,
                    measured_by=measured_by,
                    effort=effort,
                    harness=harness,
                    after=after,
                )
                if any(_holds(value.value, op, arg) for value in values):
                    passing |= 1 << row
        return Bitset3(passing, column.known & ~passing, self._all & ~column.known)

    def evidence(self, cid: str, benchmark_id: str, *, measured_by: set[str] | None = None,
                 effort: str | None = None, harness: str | None = None,
                 after: date | None = None) -> Sequence[EvidenceValue]:
        """Evidence for one benchmark; ``after`` is exclusive. Unknown dates never pass it."""
        self._check(cid)
        return tuple(
            e for e in self._evidence[cid]
            if e.benchmark_id == benchmark_id
            and (measured_by is None or e.measured_by in measured_by)
            and (effort is None or e.effort == effort)
            and (harness is None or e.harness == harness)
            and (after is None or (e.date is not None and e.date > after)))

    def direct_for(self, benchmark_id: str, domains: Iterable[str] = ()) -> bool:
        """Whether ``benchmark_id`` directly measures a capability asked about.

        Directness is relative to the request (design §4.1): the benchmark must
        be tagged ``direct`` for one of ``domains``. With no domain asked
        about, a ``direct`` tag for any domain is enough.
        """
        return any((benchmark_id, "direct") in self._domains.get(domain_id, ())
                   for domain_id in (set(domains) or self._domains))

    def evidence_for_domain(self, cid: str, domain_id: str) -> Sequence[EvidenceValue]:
        self._check(cid)
        directness = dict(self._domains.get(domain_id, ()))
        return tuple(
            EvidenceValue(**{**e.__dict__, "directness": directness[e.benchmark_id]})
            for e in self._evidence[cid] if e.benchmark_id in directness)

    # beyond the protocol -----------------------------------------------------

    def require_explanation_records(self) -> None:
        """Refuse explanations from a snapshot built before provenance retention."""
        if self.explanation_rebuild_required is not None:
            raise SnapshotError(self.explanation_rebuild_required)

    def kind(self, cid: str) -> Literal["model", "offering"]:
        self._check(cid)
        return self._meta[cid]["kind"]

    def model_of(self, cid: str) -> str:
        self._check(cid)
        return self._meta[cid]["model"]

    def record(self, record_id: str) -> Mapping[str, Any]:
        """The admitted record with its winning verification, retained verbatim."""
        if record_id not in self._records and self._record_table is not None:
            self._records[record_id] = _unpack_record(self._record_table, record_id)
        return self._records[record_id]

    def facet_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._facts))

    def domain_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._domains))

    def benchmark_ids(self) -> tuple[str, ...]:
        return self._benchmarks

    def source_url(self, source_id: str) -> str:
        return self._sources[source_id]

    def ids(self, bits: int) -> tuple[str, ...]:
        """The candidate IDs a bitset names."""
        return tuple(self._ids[r] for r in self._rows(bits))

    @staticmethod
    def _rows(bits: int) -> Iterable[int]:
        row = 0
        while bits:
            if bits & 1:
                yield row
            bits >>= 1
            row += 1


def load_snapshot_bytes(
    data: bytes,
    *,
    key: bytes | str | None = _FROM_ENV,
    include_archive: bool = False,
    source: str = "snapshot bytes",
) -> LoadedSnapshot:
    """Check and index a gzipped snapshot already held in memory."""
    try:
        text = gzip.decompress(data).decode("utf-8")
        stored_digest = None
        if text.startswith('{"content":{'):
            # raw_decode finds the JSON boundary, including escaped quotes and
            # nested objects. Never search for a delimiter inside content.
            content, end = json.JSONDecoder().raw_decode(text, len('{"content":'))
            suffix = text[end:].lstrip()
            envelope = json.loads("{" + suffix[1:]) if suffix.startswith(",") else {}
            if "content" in envelope:
                raise SnapshotIntegrityError(f"{source}: duplicate content member")
            envelope["content"] = content
            stored_digest = "sha256:" + hashlib.sha256(
                text[len('{"content":'):end].encode("utf-8")).hexdigest()
        else:
            envelope = json.loads(text)
    except (OSError, EOFError, ValueError) as exc:
        raise SnapshotIntegrityError(f"{source}: not a gzipped JSON snapshot: {exc}") from exc
    if not isinstance(envelope, dict) or envelope.get("format") != FORMAT:
        raise SnapshotIntegrityError(f"{source}: not a {FORMAT} file")
    if envelope.get("format_version") != FORMAT_VERSION:
        raise SnapshotIntegrityError(
            f"{source}: format version {envelope.get('format_version')!r}, "
            f"expected {FORMAT_VERSION}"
        )
    # Canonical writer output can be checked directly. Other JSON encodings
    # retain the original semantic hash check, including the signature check.
    digest = stored_digest
    if digest != envelope.get("content_hash") or digest is None:
        digest = content_hash(envelope["content"])
    if digest != envelope.get("content_hash"):
        raise SnapshotIntegrityError(f"{source}: content hash mismatch: the snapshot was altered")
    if envelope.get("snapshot_id") != snapshot_id_for(digest):
        raise SnapshotIntegrityError(f"{source}: snapshot ID does not match its content hash")
    key = env_key() if key is _FROM_ENV else _key_bytes(key)
    verified = False
    if key is not None:
        signature = envelope.get("signature")
        if not signature:
            raise SnapshotIntegrityError(f"{source}: unsigned snapshot, but a key was given")
        if (signature.get("alg") != SIGNATURE_ALG
                or not hmac.compare_digest(str(signature.get("value")), _sign(digest, key))):
            raise SnapshotIntegrityError(f"{source}: signature does not verify with this key")
        verified = True
    return LoadedSnapshot(envelope, include_archive=include_archive, signature_verified=verified)


def load_snapshot(path: str | Path, *, key: bytes | str | None = _FROM_ENV,
                  include_archive: bool = False) -> LoadedSnapshot:
    """Read, check and index a snapshot.

    The content hash is always checked. The key defaults to
    ``MODELSPEC_SNAPSHOT_KEY``; with a key, the snapshot must be signed with it.
    Without one, the signature cannot be checked and ``signature_verified`` is
    false. Retired models are left out unless ``include_archive``.
    """
    path = Path(path)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SnapshotIntegrityError(f"{path}: not a gzipped JSON snapshot: {exc}") from exc
    return load_snapshot_bytes(data, key=key, include_archive=include_archive, source=str(path))
