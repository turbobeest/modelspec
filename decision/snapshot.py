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
  and signs the content hash with HMAC-SHA256 for the Worker and Ed25519 for
  public clients when their respective keys are set. The same inputs and keys
  give the same bytes.
* ``load_snapshot`` checks the hash and verifies either the Worker's HMAC or a
  pinned Ed25519 signature, then builds the in-memory index: three-valued
  bitsets over the candidates, per facet value.

Inputs are MODEL-134's records (``decision.model``) or their serialised dicts;
the builder reads them by field name, so either works.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import hmac
import io
import json
import logging
import math
import os
import warnings
from bisect import bisect_left, bisect_right
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal, Protocol, runtime_checkable

import yaml

from decision.excluded import ExcludedSources, excluded_sources
from decision.model import (
    Measurement,
    evidence_verification_value,
    value_hash,
    verification_counts,
)

logger = logging.getLogger(__name__)

FORMAT = "modelspec.decision-snapshot"
FORMAT_VERSION = 1
KEY_ENV = "MODELSPEC_SNAPSHOT_KEY"
SIGNATURE_ALG = "hmac-sha256"
ED25519_KEY_ENV = "MODELSPEC_SNAPSHOT_ED25519_KEY"
ED25519_SIGNATURE_ALG = "ed25519"
PUBLIC_KEY_SET_PATH = Path(__file__).with_name("snapshot_keys.json")
UNPROVISIONED_SIGNATURE_STATUS = "unsigned (ed25519 key not yet provisioned)"

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


@dataclass(frozen=True)
class JurisdictionCoverage:
    """Premier models with a known lab set, an explicit null, or neither."""

    known: int
    explicit_null: int
    gap: int
    gap_models: tuple[str, ...] = ()
    gap_labs: tuple[str, ...] = ()

    def __str__(self) -> str:
        premier_gap_labs = {model.split("/", 1)[0] for model in self.gap_models}
        outside = [lab for lab in self.gap_labs if lab not in premier_gap_labs]
        listed = ", ".join(outside)
        tail = f": {listed}" if listed else ":"
        return (f"premier models: known {self.known}, "
                f"explicit null {self.explicit_null}, gap {self.gap}; "
                f"gap labs outside premier{tail}")


class CompletenessError(SnapshotBuildError):
    """The premier-set completeness gate failed (design §5)."""

    def __init__(self, gaps: Sequence[Gap], *,
                 coverage: JurisdictionCoverage | None = None):
        self.gaps = tuple(gaps)
        self.coverage = coverage
        lines = "\n  ".join(str(g) for g in self.gaps)
        extra = f"\n{coverage}" if coverage is not None else ""
        super().__init__(f"completeness gate: {len(self.gaps)} guaranteed fact(s) missing "
                         f"for the premier set:\n  {lines}{extra}")


# ── the values an index returns ────────────────────────────────────────────


@dataclass(frozen=True)
class FactValue:
    state: FactState
    value: Any = None
    sources: tuple[str, ...] = ()
    record_id: str | None = field(default=None, compare=False)
    #: The fact's ``measurement`` block when ModelSpec measured it (MODEL-212).
    measurement: Mapping[str, Any] | None = field(default=None, compare=False)

    @property
    def interval(self) -> tuple[float, float] | None:
        """The 95% interval of a measured median, or ``None``."""
        if self.measurement is None:
            return None
        low, high = self.measurement["interval"]
        return float(low), float(high)


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
    interval: tuple[float, float] | None = None
    n: int | None = None
    quality_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class CapabilityEstimateValue:
    value: float
    low: float
    high: float
    sd: float


@dataclass(frozen=True)
class CapabilityDriverValue:
    record_id: str
    benchmark_id: str
    version: str | None
    loading: float
    weight: float
    recency_weight: float


@dataclass(frozen=True)
class RefinementEstimateValue:
    """A nested refinement estimate and how many tagged measurements moved it."""

    estimate: CapabilityEstimateValue
    #: 0 means no refinement evidence: the parent estimate, widened.
    evidence_count: int


def refinement_fallback_value(base: Any, prior_sd: float) -> RefinementEstimateValue:
    from decision.capability import refinement_fallback

    fallback = refinement_fallback(base, prior_sd)
    return RefinementEstimateValue(
        CapabilityEstimateValue(fallback.value, fallback.low, fallback.high, fallback.sd), 0
    )


class _Drivers(dict[tuple[str, str], tuple[CapabilityDriverValue, ...]]):
    """Materialise provenance only for a model/dimension being explained."""

    def __init__(self, raw: Mapping[str, Mapping[str, Any]] | None):
        super().__init__()
        self._raw = raw or {}

    def __missing__(self, pair):
        model_id, key = pair
        value = tuple(
            CapabilityDriverValue(
                record_id=row[0], benchmark_id=row[1], version=row[2],
                loading=float(row[3]), weight=float(row[4]),
                recency_weight=float(row[5]),
            )
            for row in self._raw.get(model_id, {}).get(key, ())
        )
        self[pair] = value
        return value


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

    def capability_estimate(
        self, cid: str, domain_id: str
    ) -> CapabilityEstimateValue | None: ...

    def capability_drivers(
        self, cid: str, domain_id: str
    ) -> Sequence[CapabilityDriverValue]: ...

    def evidence_record(self, cid: str, record_id: str) -> EvidenceValue | None: ...

    def kind(self, cid: str) -> Literal["model", "offering"]: ...

    def model_of(self, cid: str) -> str: ...

    def subscription_offerings(self) -> Sequence[Mapping[str, Any]]: ...


@runtime_checkable
class ExplanationIndex(SnapshotIndex, Protocol):
    """Snapshot metadata and retained records needed to transport a decision."""

    def require_explanation_records(self) -> None: ...
    def source_url(self, source_id: str) -> str: ...
    def record(self, record_id: str) -> Mapping[str, Any]: ...
    def facet_ids(self) -> tuple[str, ...]: ...
    def domain_ids(self) -> tuple[str, ...]: ...
    def benchmark_ids(self) -> tuple[str, ...]: ...
    def corpus_evidence(self) -> Iterator[tuple[str, EvidenceValue]]: ...
    def benchmark_domain_tags(self) -> dict[str, tuple[tuple[str, str], ...]]: ...


# ── inputs ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SnapshotInputs:
    """What a snapshot is compiled from. Records may be MODEL-134 objects or dicts."""

    models: Sequence[Any] = ()
    offerings: Sequence[Any] = ()
    subscriptions: Sequence[Any] = ()
    evidence: Sequence[Any] = ()
    #: Registered source ID -> URL.
    sources: Mapping[str, str] = field(default_factory=dict)
    #: Benchmark ID -> ((domain ID, directness), ...), from the benchmark pages.
    benchmark_domains: Mapping[str, Sequence[Sequence[str]]] = field(default_factory=dict)
    #: Benchmark measurement metadata used by the build-time capability fit.
    benchmark_metadata: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    #: Benchmark ID -> ((refinement ID, directness), ...), from the benchmark
    #: pages (MODEL-189). IDs are registered in ``registry/refinements.yaml``.
    benchmark_refinements: Mapping[str, Sequence[Sequence[str]]] = field(default_factory=dict)
    #: The verification log. The latest verification of a target wins, over an
    #: inline one too.
    verifications: Sequence[Any] = ()
    #: Lab id -> ``decision.labs.Lab``. Empty when the checkout has no lab registry.
    labs: Mapping[str, Any] = field(default_factory=dict)


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


def check_identity_region(region: str) -> None:
    """Refuse an offering region that is neither registered nor an ISO alpha-2 code."""
    from decision.regions import require_identity_region

    try:
        require_identity_region(region)
    except ValueError as exc:
        raise SnapshotError(str(exc)) from exc


def check_snapshot_offering_regions(content: Mapping[str, Any]) -> None:
    """Refuse a snapshot whose offering identity region is not registered.

    Lineup and archive are both checked, so a load that skips the archive
    still refuses a bad region stored there. A known string fact is checked
    too: the identity name and a sourced region name must each be registered.
    A list of alpha-2 codes is a country set, not an identity name.
    """
    from decision.regions import identity_region

    for section_name in ("lineup", "archive"):
        section = content.get(section_name) or {}
        candidates = section.get("candidates") or ()
        column = (section.get("facets") or {}).get("offering.region") or {}
        by_local = {
            row: (state, value)
            for row, state, value in zip(
                column.get("row") or (), column.get("state") or (), column.get("value") or (),
            )
        }
        for local, cand in enumerate(candidates):
            if cand.get("kind") != "offering":
                continue
            check_identity_region(identity_region(str(cand.get("id") or "")))
            stored = by_local.get(local)
            if stored is not None and stored[0] == "known" and isinstance(stored[1], str):
                check_identity_region(stored[1])


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


@dataclass(frozen=True)
class Ed25519Signer:
    """One build-time signing key and the public key ID written beside it."""

    key_id: str
    private_key: bytes | str

    def sign(self, digest: str) -> str:
        key = _load_ed25519_private_key(self.private_key)
        signature = key.sign(digest.encode("ascii"))
        return base64.b64encode(signature).decode("ascii")


def _load_ed25519_private_key(value: bytes | str):
    """Parse an Ed25519 private key from PEM, raw bytes, or raw base64."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    encoded = value.encode("ascii") if isinstance(value, str) else value
    if encoded.lstrip().startswith(b"-----BEGIN"):
        key = serialization.load_pem_private_key(encoded, password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise SnapshotBuildError("the snapshot signing key is not an Ed25519 private key")
        return key
    if len(encoded) != 32:
        try:
            encoded = base64.b64decode(encoded, validate=True)
        except (ValueError, TypeError) as exc:
            raise SnapshotBuildError(
                "the Ed25519 private key must be PEM or raw base64"
            ) from exc
    if len(encoded) != 32:
        raise SnapshotBuildError("the raw Ed25519 private key must contain 32 bytes")
    return Ed25519PrivateKey.from_private_bytes(encoded)


def load_public_keys(path: str | Path | None = None) -> dict[str, bytes]:
    """Read the pinned Ed25519 key set shipped by the CLI and public site."""
    path = PUBLIC_KEY_SET_PATH if path is None else path
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise SnapshotIntegrityError(f"could not read the pinned snapshot keys: {exc}") from exc
    if (not isinstance(raw, dict) or raw.get("format") != "modelspec.snapshot-keys"
            or raw.get("version") != 1 or not isinstance(raw.get("keys"), list)):
        raise SnapshotIntegrityError("the pinned snapshot key set has an invalid format")
    keys: dict[str, bytes] = {}
    for row in raw["keys"]:
        try:
            if row["alg"] != ED25519_SIGNATURE_ALG:
                raise ValueError("unsupported algorithm")
            key_id = str(row["key_id"])
            public = base64.b64decode(row["public_key"], validate=True)
            if not key_id or len(public) != 32 or key_id in keys:
                raise ValueError("invalid key")
        except (KeyError, TypeError, ValueError) as exc:
            raise SnapshotIntegrityError(
                "the pinned snapshot key set contains an invalid key"
            ) from exc
        keys[key_id] = public
    return keys


def env_ed25519_signer() -> Ed25519Signer | None:
    """Match the CI private key to its ID in the pinned public key set."""
    value = os.environ.get(ED25519_KEY_ENV)
    if not value:
        return None
    key = _load_ed25519_private_key(value)
    from cryptography.hazmat.primitives import serialization

    public = key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    public_keys = load_public_keys()
    if not public_keys:
        warnings.warn(
            f"{ED25519_KEY_ENV} is set but {PUBLIC_KEY_SET_PATH.name} contains no keys; "
            "skipping Ed25519 signing",
            RuntimeWarning,
            stacklevel=2,
        )
        return None
    for key_id, candidate in public_keys.items():
        if hmac.compare_digest(public, candidate):
            return Ed25519Signer(key_id, value)
    raise SnapshotBuildError(
        f"the {ED25519_KEY_ENV} public key is not in {PUBLIC_KEY_SET_PATH.name}"
    )


VOCABULARY_SIGNATURES_FIELD = "signatures"
_VOCABULARY_DOMAIN = "modelspec.vocabulary\n"


def vocabulary_digest(vocabulary: Mapping[str, Any]) -> str:
    """SHA-256 of the vocabulary with its own ``signatures`` block left out."""
    body = {k: v for k, v in vocabulary.items() if k != VOCABULARY_SIGNATURES_FIELD}
    return "sha256:" + hashlib.sha256(canonical_json(body)).hexdigest()


def _vocabulary_message(vocabulary: Mapping[str, Any]) -> bytes:
    return (_VOCABULARY_DOMAIN + vocabulary_digest(vocabulary)).encode("ascii")


def sign_vocabulary(vocabulary: Mapping[str, Any], signer: Ed25519Signer) -> dict[str, Any]:
    """Return the vocabulary with an Ed25519 signature made by the snapshot's key (MODEL-227).

    The signed message is domain-separated from the snapshot's, so a snapshot
    signature can never be replayed as a vocabulary signature. The vocabulary's
    own ``snapshot`` field is inside the digest, which ties it to one snapshot.
    """
    key = _load_ed25519_private_key(signer.private_key)
    value = base64.b64encode(key.sign(_vocabulary_message(vocabulary))).decode("ascii")
    signed = {k: v for k, v in vocabulary.items() if k != VOCABULARY_SIGNATURES_FIELD}
    signed[VOCABULARY_SIGNATURES_FIELD] = [
        {"alg": ED25519_SIGNATURE_ALG, "key_id": signer.key_id, "value": value}
    ]
    return signed


def verify_vocabulary(vocabulary: Mapping[str, Any]) -> str:
    """Check a vocabulary against the pinned Ed25519 key set.

    Returns ``"verified"``, ``"unsigned"`` (no signature block: a vocabulary
    published before MODEL-227) or ``"unpinned"`` (the pinned set is empty, the
    same hash-only mode the snapshot loader allows). Raises
    ``SnapshotIntegrityError`` when a signature block is present and none of its
    signatures verifies.
    """
    signatures = vocabulary.get(VOCABULARY_SIGNATURES_FIELD)
    if signatures is None:
        return "unsigned"
    public_keys = load_public_keys()
    if not public_keys:
        return "unpinned"
    if not isinstance(signatures, list) or not signatures:
        raise SnapshotIntegrityError("the vocabulary signature block is malformed")
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    message = _vocabulary_message(vocabulary)
    for row in signatures:
        try:
            if row["alg"] != ED25519_SIGNATURE_ALG:
                continue
            public = public_keys.get(str(row["key_id"]))
            if public is None:
                continue
            Ed25519PublicKey.from_public_bytes(public).verify(
                base64.b64decode(row["value"], validate=True), message
            )
        except (KeyError, TypeError, ValueError, InvalidSignature):
            continue
        return "verified"
    raise SnapshotIntegrityError(
        "the vocabulary has no valid Ed25519 signature from a pinned key"
    )


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

    def envelope(self, key: bytes | str | None = _FROM_ENV,
                 ed25519_signer: Ed25519Signer | None | Any = _FROM_ENV) -> dict[str, Any]:
        key = env_key() if key is _FROM_ENV else _key_bytes(key)
        signature = None if key is None else {"alg": SIGNATURE_ALG,
                                              "value": _sign(self.content_hash, key)}
        signer = env_ed25519_signer() if ed25519_signer is _FROM_ENV else ed25519_signer
        signatures = [] if signer is None else [{
            "alg": ED25519_SIGNATURE_ALG,
            "key_id": signer.key_id,
            "value": signer.sign(self.content_hash),
        }]
        return {"format": FORMAT, "format_version": FORMAT_VERSION,
                "snapshot_id": self.snapshot_id, "content_hash": self.content_hash,
                "signature": signature, "signatures": signatures, "content": self.content}

    def to_bytes(self, key: bytes | str | None = _FROM_ENV,
                 ed25519_signer: Ed25519Signer | None | Any = _FROM_ENV) -> bytes:
        buf = io.BytesIO()
        # A fixed mtime and no file name keep the gzip header deterministic.
        with gzip.GzipFile(filename="", mode="wb", fileobj=buf, compresslevel=9, mtime=0) as gz:
            gz.write(canonical_json(self.envelope(key, ed25519_signer)))
        return buf.getvalue()

    def write(self, path: str | Path, *, key: bytes | str | None = _FROM_ENV,
              ed25519_signer: Ed25519Signer | None | Any = _FROM_ENV) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.to_bytes(key, ed25519_signer))
        return path


# ── building ───────────────────────────────────────────────────────────────


class _Compiler:
    def __init__(self, inputs: SnapshotInputs, registry: Any, guard: ExcludedSources | None,
                 as_of: date | None = None, allow_fixture_measurements: bool = False):
        self.inputs = inputs
        self.as_of = as_of
        self.allow_fixture_measurements = allow_fixture_measurements
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
        #: subject id -> facet -> the admitted fact's measurement block.
        self.measurements: dict[str, dict[str, dict[str, Any]]] = {}
        self.facet_subject: dict[str, str] = {}
        self.evidence: dict[str, list[list[Any]]] = {}
        self.records: dict[str, dict[str, Any]] = {}
        self.fact_records: dict[str, dict[str, str]] = {}
        self.labs: Mapping[str, Any] = inputs.labs
        #: Premier models whose lab recorded a sourced null jurisdiction.
        self.jurisdiction_null_ok: set[str] = set()

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
        value = (
            record.get("value")
            if kind == "fact"
            else evidence_verification_value(record)
        )
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
                registered = self.registry.facet(facet_id)
            except KeyError as exc:
                raise SnapshotBuildError(f"facet {facet_id!r} is not registered") from exc
            if getattr(registered, "computed_by", None):
                raise SnapshotBuildError(
                    f"facet {facet_id!r} is computed ({registered.computed_by}), never authored")
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
            measurement = self._measurement(sid, facet_id, f.get("measurement"))
            reason = (
                "stale_measurement"
                if measurement is not None and self.as_of is not None
                and measurement.stale(self.as_of)
                else self._admit(
                    "fact", f.get("id"), f.get("verification"), f.get("value"), source_ids)
            )
            if reason is not None:
                self._reject((sid, facet_id), reason, source_ids)
                continue
            self.fact_records.setdefault(sid, {})[facet_id] = self._retain("fact", f)
            if measurement is not None:
                self.measurements.setdefault(sid, {})[facet_id] = measurement.model_dump(
                    mode="json")
            row[facet_id] = [state, f.get("value") if state == "known" else None, source_ids]

    def _measurement(self, sid: str, facet_id: str, raw: Any) -> Measurement | None:
        """A fact's measurement, checked before anything else: a fixture number is a bug."""
        if raw is None:
            return None
        measurement = Measurement.model_validate(_as_dict(raw))
        if measurement.provenance == "fixture" and not self.allow_fixture_measurements:
            raise SnapshotBuildError(
                f"{sid}: {facet_id} is a fixture measurement ({measurement.run_id}); "
                "fixture numbers never enter a published snapshot")
        return measurement

    def add_model(self, raw: Any) -> None:
        m = _as_dict(raw)
        mid, lifecycle = str(m["id"]), str(m.get("lifecycle"))
        if lifecycle not in LIFECYCLES:
            raise SnapshotBuildError(f"{mid}: lifecycle {lifecycle!r} is not one of {LIFECYCLES}")
        if mid in self.subjects:
            raise SnapshotBuildError(f"model {mid} appears twice")
        self.subjects[mid] = {"kind": "model", "model": mid, "lifecycle": lifecycle}
        facts = self._inherit_jurisdiction(mid, list(m.get("facts") or []))
        self._add_facts(mid, "model", facts)

    def _inherit_jurisdiction(self, mid: str, facts: list[Any]) -> list[Any]:
        """Copy the lab's jurisdiction onto this model, or fail if they disagree.

        A known model value that is not the lab's set raises. The same set, or
        no known set, is replaced by the lab fact when that fact verifies.
        When the lab fact does not verify, an agreeing model fact is left in
        place. An explicit sourced null is not copied; the model is exempt.
        """
        from decision.labs import FACET, lab_id_of, stated_codes

        lab = self.labs.get(lab_id_of(mid))
        if lab is None:
            return facts
        existing = [
            _as_dict(fact) for fact in facts if str(_as_dict(fact).get("facet")) == FACET
        ]
        model_codes = stated_codes(existing[0]) if existing else None
        lab_codes = lab.codes
        if model_codes is not None and model_codes != (lab_codes or frozenset()):
            raise SnapshotBuildError(
                f"{mid}: {FACET} {sorted(model_codes)} disagrees with lab "
                f"{lab.id} {None if lab_codes is None else sorted(lab_codes)}"
            )
        if lab_codes is None:
            if lab.explicit_null:
                self.jurisdiction_null_ok.add(mid)
            return facts
        shared = lab.fact()
        source_ids = self._source_ids(shared.get("sources"))
        reason = self._admit(
            "fact", shared.get("id"), shared.get("verification"), shared.get("value"), source_ids,
        )
        if reason is not None:
            return facts
        kept = [fact for fact in facts if str(_as_dict(fact).get("facet")) != FACET]
        kept.append(shared)
        return kept

    def add_offering(self, raw: Any) -> None:
        o = _as_dict(raw)
        check_identity_region(str(o["region"]))
        oid, mid = _offering_id(o), str(o["model"])
        if mid not in self.subjects:
            raise SnapshotBuildError(f"offering {oid} names model {mid}, which is not in the catalogue")
        if oid in self.subjects:
            raise SnapshotBuildError(f"offering {oid} appears twice")
        self.subjects[oid] = {"kind": "offering", "model": mid,
                              "lifecycle": self.subjects[mid]["lifecycle"]}
        self._add_facts(oid, "offering", o.get("facts"))
        # An offering's identity is its provider, region and tier: structural,
        # not a sourced claim, so they carry no source. They still name
        # registered values (MODEL-324). The stored region stays the
        # provider's region name; residency reads the country map from it
        # (MODEL-326).
        row = self.facts[oid]
        for part in ("provider", "region", "tier"):
            facet_id, value = f"offering.{part}", str(o[part])
            self._check_facet(facet_id, "offering")
            self._check_identity(oid, facet_id, value)
            row.setdefault(facet_id, ["known", value, []])
        stored = row.get("offering.region")
        if stored is not None and stored[0] == "known" and isinstance(stored[1], str):
            check_identity_region(stored[1])

    def _check_identity(self, oid: str, facet_id: str, value: str) -> None:
        if self.registry is None:
            return
        allowed = self.registry.allowed_values(self.registry.facet(facet_id))
        if allowed is not None and value not in allowed:
            raise SnapshotBuildError(
                f"offering {oid}: {facet_id} {value!r} is not registered; "
                f"use one of {sorted(allowed)}")

    def add_subscription(self, raw: Any) -> None:
        subscription = _as_dict(raw)
        sid = f"{subscription['provider']}/subscription/{subscription['plan']}"
        if sid in self.subjects:
            raise SnapshotBuildError(f"subscription offering {sid} appears twice")
        if self.registry is not None:
            try:
                self.registry.plan_owner(str(subscription["provider"]))
            except KeyError as exc:
                raise SnapshotBuildError(f"subscription offering {sid}: {exc}") from exc
        self.subjects[sid] = {
            "kind": "subscription",
            "provider": str(subscription["provider"]),
            "plan": str(subscription["plan"]),
            "name": str(subscription["name"]),
        }
        self._add_facts(sid, "offering", subscription.get("facts"))

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
        reason = self._admit(
            "evidence",
            e.get("id"),
            e.get("verification"),
            evidence_verification_value(e),
            source_ids,
                             extra_urls=[e.get("source_url")], benchmark=e.get("benchmark_id"))
        if reason is None:
            from schema.benchmark_values import validate_value

            metric = self.inputs.benchmark_metadata.get(str(e["benchmark_id"]), {})
            try:
                validate_value(e.get("score"), e.get("unit"), metric)
            except ValueError:
                reason = "invalid_benchmark_value"
        if reason is None and not e.get("measured_by"):
            # Who measured a row is never inferred (MODEL-239): the decision
            # contract requires it, so a row without it would fail every
            # decision that cites it.
            reason = "unclassified"
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
            e.get("interval"), e.get("n"), sorted(e.get("quality_flags") or []),
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
        # A measured facet adds a parallel column; an unmeasured one keeps its bytes.
        for facet_id, col in columns.items():
            measured = [self.measurements.get(ids[r], {}).get(facet_id) for r in col["row"]]
            if any(m is not None for m in measured):
                col["measurement"] = measured
        return {
            "candidates": [{"id": sid, **self.subjects[sid]} for sid in ids],
            "facets": columns,
            "evidence": {sid: sorted(self.evidence[sid], key=lambda r: (
                r[0], r[8] or "", r[3], canonical_json(r))) for sid in ids if sid in self.evidence},
        }

    def refinements(self) -> dict[str, dict[str, Any]]:
        """Each registered refinement's classes and benchmark tags, by weight key.

        Empty without tags, so a snapshot built without refinement data keeps
        its content. With tags, every registered refinement is listed, so the
        engine can tell a refinement nothing measures from an unknown key.
        """
        if not self.inputs.benchmark_refinements:
            return {}
        registry = self.registry if self.registry is not None else default_registry()
        by_id: dict[str, list[Any]] = {}
        out: dict[str, dict[str, Any]] = {}
        for refinement in sorted(registry.refinements(), key=lambda r: r.weight_key):
            by_id.setdefault(refinement.id, []).append(refinement)
            out[refinement.weight_key] = {
                "eligible_classes": sorted(refinement.eligible_classes),
                "benchmarks": [],
            }
        for bench, tags in sorted(self.inputs.benchmark_refinements.items()):
            if self.guard is not None and self.guard.benchmark(bench):
                continue
            for refinement_id, directness in tags:
                if str(directness) not in ("direct", "proxy"):
                    raise SnapshotBuildError(
                        f"{bench}: invalid refinement directness {directness!r}"
                    )
                if refinement_id not in by_id:
                    raise SnapshotBuildError(f"{bench}: unregistered refinement {refinement_id!r}")
                for refinement in by_id[refinement_id]:
                    out[refinement.weight_key]["benchmarks"].append([str(bench), str(directness)])
        for row in out.values():
            row["benchmarks"].sort()
        return out

    def content(self, as_of: date | None, premier: Iterable[str] | None = None) -> dict[str, Any]:
        """The snapshot content. With ``premier``, the lineup is the premier set.

        Retired models always go to the archive. Active and deprecated models
        outside the premier set leave the snapshot, with their offerings,
        evidence and records; only their number is kept, as ``out_of_lineup``.
        """
        wanted = None if premier is None else set(premier)
        candidate_subjects = {
            s: v for s, v in self.subjects.items() if v["kind"] != "subscription"
        }
        subscription_ids = sorted(
            s for s, v in self.subjects.items() if v["kind"] == "subscription"
        )
        archive = sorted(s for s, v in candidate_subjects.items() if v["lifecycle"] == "retired")
        lineup = sorted(s for s, v in candidate_subjects.items() if v["lifecycle"] != "retired"
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
        for sid in subscription_ids:
            for _state, _value, source_ids in self.facts.get(sid, {}).values():
                sources.update(source_ids)
            record_ids.update(self.fact_records.get(sid, {}).values())
        excluded: Counter[str] = Counter()
        for sid, counts in self.excluded.items():
            if sid is None or sid in kept or sid in subscription_ids:
                excluded.update(counts)
        # The same counts per kept subject (MODEL-224), so one model's
        # held-back readings can be told apart from the snapshot-wide total.
        held_back = {
            sid: dict(sorted(counts.items()))
            for sid, counts in sorted(self.excluded.items())
            if sid is not None and sid in kept
        }
        domains = {}
        for bench, tags in sorted(self.inputs.benchmark_domains.items()):
            if self.guard is not None and self.guard.benchmark(bench):
                continue
            domains[str(bench)] = sorted([str(d), str(k)] for d, k in tags)
        refinements = self.refinements()
        refinement_tags: dict[str, list[tuple[str, str]]] = {}
        for key, row in refinements.items():
            for bench, directness in row["benchmarks"]:
                refinement_tags.setdefault(bench, []).append((key, directness))
        capability: dict[str, Any] = {}
        if self.inputs.benchmark_metadata and as_of is not None:
            from decision.capability import (
                BenchmarkSpec,
                CapabilityObservation,
                fit_capabilities,
            )

            observations = []
            fitted_models = {self.subjects[sid]["model"] for sid in kept}
            for subject, evidence_rows in sorted(self.evidence.items()):
                model_id = self.subjects[subject]["model"]
                if model_id not in fitted_models:
                    continue
                for row in evidence_rows:
                    evidence_date = _date(row[8])
                    tag_rows: list[tuple[str, Directness]] = []
                    for domain_id, raw_directness in self.inputs.benchmark_domains.get(row[0], ()):
                        directness = str(raw_directness)
                        if directness not in ("direct", "proxy"):
                            raise SnapshotBuildError(
                                f"{row[0]}: invalid capability directness {directness!r}"
                            )
                        tag_rows.append((str(domain_id), directness))
                    tags = tuple(tag_rows)
                    if evidence_date is None or not (tags or row[0] in refinement_tags):
                        continue
                    observations.append(CapabilityObservation(
                        model_id=model_id,
                        benchmark_id=row[0],
                        value=float(row[3]),
                        unit=row[4],
                        measured_by=str(row[5] or ""),
                        date=evidence_date,
                        record_id=row[10],
                        version=row[1],
                        domains=tags,
                        refinements=tuple(refinement_tags.get(row[0], ())),
                    ))
            specs = {
                benchmark: BenchmarkSpec(
                    random_baseline=metadata.get("random_baseline"),
                    sample_size=metadata.get("sample_size"),
                    direction=metadata.get("direction", "higher_is_better"),
                )
                for benchmark, metadata in self.inputs.benchmark_metadata.items()
            }
            fit = fit_capabilities(observations, specs, as_of=as_of)
            capability = fit.to_payload(
                self.subjects[sid]["model"] for sid in kept
                if self.subjects[sid]["kind"] == "model"
            )
        content = {
            "format_version": FORMAT_VERSION,
            "as_of": as_of.isoformat() if as_of else None,
            "facet_subjects": dict(sorted(self.facet_subject.items())),
            "lineup": self._section(lineup),
            "archive": self._section(archive),
            "out_of_lineup": out_of_lineup,
            "benchmark_domains": domains,
            "capability": capability,
            **({"refinements": refinements} if refinements else {}),
            "sources": {s: self.sources[s] for s in sorted(sources)},
            "excluded": dict(sorted(excluded.items())),
            # Present whenever anything was held back, even when none of it
            # belongs to a kept subject, so a reader can tell "none of this
            # model's" from a snapshot that predates the key.
            **({"held_back": held_back} if excluded else {}),
            "record_table": _pack_records({r: self.records[r] for r in record_ids}),
            "fact_records": {
                sid: rows
                for sid, rows in self.fact_records.items()
                if sid in kept or sid in subscription_ids
            },
        }
        if subscription_ids:
            content["subscriptions"] = [
                {
                    "id": sid,
                    "provider": self.subjects[sid]["provider"],
                    "plan": self.subjects[sid]["plan"],
                    "name": self.subjects[sid]["name"],
                    "facts": {
                        facet_id: [state, value, source_ids]
                        for facet_id, (state, value, source_ids) in sorted(
                            self.facts.get(sid, {}).items()
                        )
                    },
                }
                for sid in subscription_ids
            ]
        return content

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
                    if self._jurisdiction_satisfied(sid, f.id):
                        continue
                    if f.id in self.facts.get(sid, {}) and not self._jurisdiction_required(sid, f.id):
                        continue
                    reason, urls = self.rejected.get((sid, f.id), ("unknown (no fact)", ()))
                    if reason == "unknown":
                        reason = "unknown (stated as unknown)"
                    out.append(Gap(mid, sid, f.id, reason, urls))
        return out

    def _jurisdiction_required(self, sid: str, facet_id: str) -> bool:
        """True when this subject's lab registry makes a null jurisdiction a gap."""
        from decision.labs import FACET, lab_id_of

        if facet_id != FACET or sid not in self.subjects:
            return False
        if self.subjects[sid]["kind"] != "model":
            return False
        return lab_id_of(sid) in self.labs

    def _jurisdiction_satisfied(self, sid: str, facet_id: str) -> bool:
        """A known set, or an explicit sourced null, satisfies the lab gate."""
        if not self._jurisdiction_required(sid, facet_id):
            return False
        if sid in self.jurisdiction_null_ok:
            return True
        stored = self.facts.get(sid, {}).get(facet_id)
        return bool(stored and stored[0] == "known" and stored[1])

    def jurisdiction_coverage(self, premier: Iterable[str]) -> JurisdictionCoverage:
        """Count premier models whose lab jurisdiction is known, an explicit null, or a gap.

        A gap lab with no premier model is still named. The gate is unchanged:
        a gap model is still a missing guaranteed fact.
        """
        from decision.labs import FACET

        known = explicit = gap = 0
        gap_models: list[str] = []
        for mid in sorted(set(premier)):
            if not self._jurisdiction_required(mid, FACET):
                continue
            if mid in self.jurisdiction_null_ok:
                explicit += 1
                continue
            stored = self.facts.get(mid, {}).get(FACET)
            if stored and stored[0] == "known" and stored[1]:
                known += 1
                continue
            gap += 1
            gap_models.append(mid)
        gap_labs = tuple(sorted(
            lab.id for lab in self.labs.values()
            if lab.codes is None and not lab.explicit_null
        ))
        return JurisdictionCoverage(known, explicit, gap, tuple(gap_models), gap_labs)


def default_registry() -> Any:
    try:
        from decision import registry
    except ImportError as exc:  # MODEL-133 not present
        raise SnapshotBuildError(f"the facet registry is not available: {exc}") from exc
    return registry.default()


def build_snapshot(inputs: SnapshotInputs, *, registry: Any = None,
                   premier: Iterable[str] | None = None, as_of: date | None = None,
                   guard: ExcludedSources | None = None, gate: bool = True,
                   allow_fixture_measurements: bool = False) -> Snapshot:
    """Compile ``inputs``. With ``premier``, the lineup is the premier set.

    With ``premier`` and ``gate`` (the default), the completeness gate runs
    first. ``gate=False`` keeps the premier lineup but skips the gate, for an
    audit that must run while facts are still missing (MODEL-146).
    ``registry`` validates facet IDs and names the guaranteed facets; the gate
    requires it. ``guard`` drops excluded sources and scans the output;
    ``build_from_repo`` always passes it. ``allow_fixture_measurements`` lets a
    test compile fixture speed numbers; ``build_from_repo`` never passes it.
    A measurement older than its staleness limit at ``as_of`` stays out.
    """
    c = _compile(inputs, registry, guard, as_of, allow_fixture_measurements)
    premier = None if premier is None else tuple(premier)
    if premier is not None and gate:
        coverage = c.jurisdiction_coverage(premier)
        gaps = c.gaps(premier)
        if gaps:
            raise CompletenessError(gaps, coverage=coverage)
        logger.info("%s", coverage)
    return _finish(c, as_of, premier, guard)


@dataclass(frozen=True)
class BuildAudit:
    """What a premier build admitted, and what it kept out and why (MODEL-215).

    ``rejected`` maps (subject, facet) to the reason a fact stayed out: the
    same reasons the completeness gate prints, for every facet, not only the
    guaranteed ones. ``excluded`` counts every record kept out, by subject.
    """

    snapshot: Snapshot
    gaps: tuple[Gap, ...]
    rejected: Mapping[tuple[str, str], str]
    excluded: Mapping[str | None, Mapping[str, int]]


def audit_build(inputs: SnapshotInputs, *, registry: Any, premier: Iterable[str],
                as_of: date | None, guard: ExcludedSources | None) -> BuildAudit:
    """Compile a premier build without the gate and keep the compiler's reasons."""
    c = _compile(inputs, registry, guard, as_of, False)
    premier = tuple(premier)
    gaps = tuple(c.gaps(premier))
    return BuildAudit(
        snapshot=_finish(c, as_of, premier, guard),
        gaps=gaps,
        rejected={key: reason for key, (reason, _urls) in c.rejected.items()},
        excluded={sid: dict(counts) for sid, counts in c.excluded.items()},
    )


def _compile(inputs: SnapshotInputs, registry: Any, guard: ExcludedSources | None,
             as_of: date | None, allow_fixture_measurements: bool) -> _Compiler:
    c = _Compiler(inputs, registry, guard, as_of, allow_fixture_measurements)
    for m in inputs.models:
        c.add_model(m)
    for o in inputs.offerings:
        c.add_offering(o)
    for subscription in inputs.subscriptions:
        c.add_subscription(subscription)
    for e in inputs.evidence:
        c.add_evidence(e)
    return c


def _finish(c: _Compiler, as_of: date | None, premier: tuple[str, ...] | None,
            guard: ExcludedSources | None) -> Snapshot:
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
    * Metered offerings: ``offerings/<provider>/<lab>/<model>.yaml``, each a list.
    * Subscription offerings: ``offerings/subscriptions/<provider>.yaml``, each a list.
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
    subscriptions = []
    for path in sorted((root / "offerings" / "subscriptions").glob("*.yaml")):
        rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if not isinstance(rows, list):
            raise SnapshotBuildError(f"{path}: a subscription offering file is a list")
        for subscription in rows:
            subscription = dict(subscription)
            sid = f"{subscription['provider']}/subscription/{subscription['plan']}"
            subscription["facts"] = [
                {
                    "subject": {"kind": "offering", "id": sid},
                    "id": f"{sid}#{fact.get('facet')}",
                    **fact,
                }
                for fact in subscription.get("facts") or []
            ]
            subscriptions.append(subscription)
    from decision.sources import load_sources

    sources = {
        source_id: str(source.url)
        for source_id, source in load_sources(root / "registry" / "sources.yaml").items()
    }
    domains = {}
    refinements = {}
    metadata = {}
    for b in load_benchmarks(root):
        tags = b.front.get("domains") or []
        if tags:
            domains[b.benchmark_id] = tuple((str(t["id"]), str(t["directness"])) for t in tags)
        refinement_tags = b.front.get("refinements") or []
        if refinement_tags:
            refinements[b.benchmark_id] = tuple(
                (str(t["id"]), str(t["directness"])) for t in refinement_tags
            )
        metric = b.front.get("metric") or {}
        dataset = b.front.get("dataset") or {}
        metadata[b.benchmark_id] = {
            "min_score": metric.get("min_score", 0),
            "max_score": metric.get("max_score"),
            "unit": metric.get("unit"),
            "random_baseline": metric.get("random_baseline"),
            "sample_size": dataset.get("size"),
            "direction": metric.get("direction", "higher_is_better"),
        }
    verifications = []
    verification_log = root / "verification" / "log.jsonl"
    if verification_log.is_file():
        for line in verification_log.read_text(encoding="utf-8").splitlines():
            if line.strip():
                verifications.append(json.loads(line))
    from decision.labs import load_labs

    return SnapshotInputs(models=models, offerings=offerings, subscriptions=subscriptions,
                          evidence=evidence, sources=sources,
                          benchmark_domains=domains, benchmark_metadata=metadata,
                          benchmark_refinements=refinements,
                          verifications=verifications,
                          labs=load_labs(root))


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


def _or_all(masks: Iterable[int]) -> int:
    combined = 0
    for mask in masks:
        combined |= mask
    return combined


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
        self._parsed_records: dict[tuple[str, str], EvidenceValue] = {}
        self.records = {
            (model_of.get(cid, cid), row[10]): row
            for cid, candidate_rows in rows.items()
            for row in candidate_rows
            if len(row) > 10 and row[10] is not None
        }

    @staticmethod
    def _value(row: Sequence[Any]) -> EvidenceValue:
        return EvidenceValue(
            benchmark_id=row[0], version=row[1], subcategory=row[2], value=row[3],
            unit=row[4], measured_by=row[5], effort=row[6], harness=row[7],
            date=_date(row[8]), source_ids=tuple(row[9]),
            record_id=row[10] if len(row) > 10 else None,
            date_type=row[11] if len(row) > 11 else None,
            source_snapshot=row[12] if len(row) > 12 else None,
            interval=tuple(row[13]) if len(row) > 13 and row[13] is not None else None,
            n=row[14] if len(row) > 14 else None,
            quality_flags=tuple(row[15]) if len(row) > 15 else (),
        )

    def record(self, cid: str, record_id: str) -> EvidenceValue | None:
        key = self.model_of.get(cid, cid), record_id
        row = self.records.get(key)
        if row is None:
            return None
        if key not in self._parsed_records:
            self._parsed_records[key] = self._value(row)
        return self._parsed_records[key]

    def _rows(self, cid: str) -> list[Sequence[Any]]:
        own = list(self.rows.get(cid, ()))
        model = self.model_of.get(cid, cid)
        if model == cid:
            return own
        measured = {r[0] for r in own}
        inherited = [r for r in self.rows.get(model, ()) if r[0] not in measured]
        return sorted(own + inherited, key=lambda r: (r[0], r[8] or "", r[3], canonical_json(r)))

    def __missing__(self, cid: str) -> tuple[EvidenceValue, ...]:
        self[cid] = tuple(self._value(row) for row in self._rows(cid))
        return self[cid]


class LoadedSnapshot:
    """The in-memory index over one snapshot. Implements ``SnapshotIndex``."""

    def __init__(self, envelope: Mapping[str, Any], *, include_archive: bool,
                 signature_verified: bool, signature_status: str | None = None,
                 signature_key_id: str | None = None):
        content = envelope["content"]
        check_snapshot_offering_regions(content)
        self.snapshot_id: str = envelope["snapshot_id"]
        self.content_hash: str = envelope["content_hash"]
        self.signature_verified = signature_verified
        self.signature_status = signature_status or (
            "verified" if signature_verified else UNPROVISIONED_SIGNATURE_STATUS
        )
        self.signature_key_id = signature_key_id
        self.publisher_signature = envelope.get("signature")
        self.as_of = _date(content.get("as_of"))
        self.excluded: dict[str, int] = dict(content.get("excluded") or {})
        #: Per kept subject, the ``excluded`` counts (MODEL-224); ``None`` when
        #: the snapshot predates the key and held anything back.
        self._held_back: dict[str, dict[str, int]] | None = (
            content["held_back"] if "held_back" in content
            else None if self.excluded else {}
        )
        #: Active models the build left out because they are not in the premier set.
        self.out_of_lineup: int = int(content.get("out_of_lineup") or 0)
        self._subscription_offerings = tuple(
            {
                "id": row["id"],
                "provider": row["provider"],
                "plan": row["plan"],
                "name": row["name"],
                "facts": {
                    facet_id: FactValue(
                        state, value, tuple(sources),
                        content.get("fact_records", {}).get(row["id"], {}).get(facet_id),
                    )
                    for facet_id, (state, value, sources) in row.get("facts", {}).items()
                },
            }
            for row in content.get("subscriptions", ())
        )
        self._sources: dict[str, str] = dict(content["sources"])
        self._records = content.get("records", {})
        self._record_table = content.get("record_table")
        self.explanation_rebuild_required = (
            None
            if "fact_records" in content and ("record_table" in content or "records" in content)
            else "snapshot predates retained verification records; rebuild it before explaining"
        )
        self._corpus_sections = (content["lineup"], content["archive"])
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
                measured = col.get("measurement") or [None] * len(col["row"])
                for r, state, value, srcs, measurement in zip(
                        col["row"], col["state"], col["value"], col["sources"], measured):
                    target[self._row[local[r]]] = FactValue(
                        state, value, tuple(srcs),
                        content.get("fact_records", {}).get(local[r], {}).get(facet_id),
                        measurement)
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
        capability = content.get("capability") or {}
        # Parse the learned lookup once.  Domain objectives are the page's
        # default, so reconstructing these values throughout filtering,
        # optimisation and explanation made the first Worker request pay the
        # same JSON-to-object cost repeatedly.
        self._capability_estimates = {
            (model_id, domain_id): CapabilityEstimateValue(*map(float, row))
            for model_id, domains in (capability.get("estimates") or {}).items()
            for domain_id, row in domains.items()
        }
        self._capability_drivers = _Drivers(capability.get("drivers"))
        # Refinements (MODEL-190): stored estimates exist only where a model
        # has refinement evidence; everyone else falls back at read time.
        self._refinements: Mapping[str, Mapping[str, Any]] = content.get("refinements") or {}
        self._refinement_prior_sd = {
            key: float(value)
            for key, value in (capability.get("refinement_prior_sd") or {}).items()
        }
        self._refinement_estimates = {
            (model_id, key): (CapabilityEstimateValue(*map(float, row[:4])), int(row[4]))
            for model_id, keys in (capability.get("refinement_estimates") or {}).items()
            for key, row in keys.items()
        }
        self._refinement_drivers = _Drivers(capability.get("refinement_drivers"))
        self._fitted_models = frozenset(model for model, _ in self._capability_estimates)
        self.capability_method = capability.get("method")
        self.capability_items = capability.get("items") or {}
        self.capability_source_offsets = capability.get("source_offsets") or {}
        self._domains: dict[str, list[tuple[str, str]]] = {}
        for bench, tags in content["benchmark_domains"].items():
            for domain_id, directness in tags:
                self._domains.setdefault(domain_id, []).append((bench, directness))
        self._benchmark_domain_tags = {
            benchmark: tuple(sorted(tuple(tag) for tag in content["benchmark_domains"][benchmark]))
            for benchmark in self._benchmarks
        }

    # SnapshotIndex -----------------------------------------------------------

    def candidates(self) -> Sequence[str]:
        return self._ids

    def subscription_offerings(self) -> Sequence[Mapping[str, Any]]:
        return self._subscription_offerings

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

        Membership on ``offering.region`` uses the countries the stored name
        guarantees. A name that guarantees none is unknown, not a fail.
        ``known``, ``=`` and ``!=`` still compare the identity name.
        """
        if facet_id == "offering.region":
            from decision.regions import is_membership_op

            if is_membership_op(op):
                return self._region_membership(op, arg)
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
        failing = known & ~passing
        unknown = self._all & ~known
        if facet_id == "model.fits_hardware" and op in {
            "contains", "contains_all", "contains_any",
        }:
            indeterminate = self._hardware_indeterminate(column, op, arg) & ~passing
            unknown |= indeterminate
            failing &= ~indeterminate
        return Bitset3(passing, failing, unknown)

    def _region_membership(self, op: str, arg: Any) -> Bitset3:
        """Pass, fail, or unknown for a residency test on ``offering.region``.

        A missing fact stays unknown. A known name with no country guarantee
        is unknown too, so a global offering is not eliminated. A known country
        set that misses the request fails.
        """
        from decision.regions import countries_of, region_matches

        column = self._facet_bits.get("offering.region")
        known = 0 if column is None else column.known
        by_row = self._facts.get("offering.region", {})
        passing = failing = unguaranteed = 0
        for row in self._rows(known):
            bit = 1 << row
            countries = countries_of(by_row[row].value)
            if countries is None:
                unguaranteed |= bit
                continue
            if region_matches(countries, op, arg):
                passing |= bit
            else:
                failing |= bit
        unknown = (self._all & ~known) | unguaranteed
        return Bitset3(passing, failing, unknown)

    def _hardware_indeterminate(self, fits: _FacetBitsets | None, op: str, arg: Any) -> int:
        """Rows whose fit on a named device is unknown and could still satisfy ``op``.

        A device a row fits counts as passing, one it is indeterminate on as
        unknown, so ``contains_all`` stays may-qualify when every named device
        is one or the other and at least one is unknown.
        """
        values = [arg] if op == "contains" else list(arg)
        refused = self._facet_bits.get("model.hardware_fit_indeterminate")

        def bits(column: _FacetBitsets | None, value: Any) -> int:
            return 0 if column is None else column.passing("contains", value) or 0

        if op != "contains_all":
            return _or_all(bits(refused, value) for value in values)
        if not values:
            return 0
        reachable = self._all
        for value in values:
            reachable &= bits(fits, value) | bits(refused, value)
        return reachable

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

    def capability_estimate(
        self, cid: str, domain_id: str
    ) -> CapabilityEstimateValue | None:
        self._check(cid)
        model_id = self._meta[cid]["model"]
        return self._capability_estimates.get((model_id, domain_id))

    def capability_drivers(
        self, cid: str, domain_id: str
    ) -> Sequence[CapabilityDriverValue]:
        self._check(cid)
        model_id = self._meta[cid]["model"]
        return self._capability_drivers[model_id, domain_id]

    def refinement_keys(self) -> tuple[str, ...]:
        """Every registered refinement's weight key, when the snapshot carries them."""
        return tuple(self._refinements)

    def refinement_benchmarks(self, key: str) -> tuple[tuple[str, str], ...]:
        """The (benchmark, directness) tags of one refinement."""
        return tuple((b, d) for b, d in self._refinements[key]["benchmarks"])

    def refinement_eligible_classes(self, key: str) -> tuple[str, ...]:
        return tuple(self._refinements[key]["eligible_classes"])

    def refinement_eligible(self, cid: str, key: str) -> bool:
        classes = self.refinement_eligible_classes(key)
        return self.fact(self.model_of(cid), "model.class").value in classes

    def refinement_estimate(self, cid: str, key: str) -> RefinementEstimateValue | None:
        """The nested estimate, or the parent estimate widened when unmeasured."""
        from decision.capability import ANY_PARENT, population_prior, refinement_parent

        if key not in self._refinements or not self.refinement_eligible(cid, key):
            return None
        stored = self._refinement_estimates.get((self.model_of(cid), key))
        if stored is not None:
            return RefinementEstimateValue(stored[0], stored[1])
        prior_sd = self._refinement_prior_sd.get(key)
        if prior_sd is None:
            return None
        parent = refinement_parent(key)
        if parent == ANY_PARENT:
            base = population_prior() if self.model_of(cid) in self._fitted_models else None
        else:
            base = self.capability_estimate(cid, parent)
        return None if base is None else refinement_fallback_value(base, prior_sd)

    def refinement_drivers(self, cid: str, key: str) -> Sequence[CapabilityDriverValue]:
        self._check(cid)
        return self._refinement_drivers[self.model_of(cid), key]

    def evidence_record(self, cid: str, record_id: str) -> EvidenceValue | None:
        """Return retained model evidence by record ID in constant time."""
        self._check(cid)
        return self._evidence.record(self._meta[cid]["model"], record_id)

    # beyond the protocol -----------------------------------------------------

    def require_explanation_records(self) -> None:
        """Refuse explanations from a snapshot built before provenance retention."""
        if self.explanation_rebuild_required is not None:
            raise SnapshotError(self.explanation_rebuild_required)

    def held_back(self, cid: str) -> dict[str, int] | None:
        """Why ``cid``'s own records stayed out, by reason, or ``None`` when unknown.

        ``None`` means the snapshot predates ``content.held_back`` and held
        something back, so a subject's share cannot be recovered. A subject
        with nothing held back gets ``{}``.
        """
        if self._held_back is None:
            return None
        return dict(self._held_back.get(cid, {}))

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

    def corpus_evidence(self) -> Iterator[tuple[str, EvidenceValue]]:
        """Every stored evidence row of the snapshot, lineup and archive, as (model, row).

        The fit that built the snapshot read this whole corpus, so a refit must
        too: it must not change with ``include_archive``.
        """
        for section in self._corpus_sections:
            model_of = {c["id"]: c["model"] for c in section["candidates"]}
            for subject in sorted(section["evidence"]):
                for row in section["evidence"][subject]:
                    yield model_of[subject], _Evidence._value(row)

    def benchmark_domain_tags(self) -> dict[str, tuple[tuple[str, str], ...]]:
        """Each benchmark's (domain, directness) tags, sorted by domain."""
        return dict(self._benchmark_domain_tags)

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


def verify_hmac_signature(digest: str, signature: Mapping[str, Any] | None,
                          key: bytes | str | None, *, source: str) -> None:
    """Authenticate an already checked content hash with the publisher's key."""
    key = _key_bytes(key)
    if not signature:
        raise SnapshotIntegrityError(f"{source}: unsigned snapshot, but a key was given")
    if (key is None or signature.get("alg") != SIGNATURE_ALG
            or not hmac.compare_digest(str(signature.get("value")), _sign(digest, key))):
        raise SnapshotIntegrityError(f"{source}: signature does not verify with this key")


def load_snapshot_bytes(
    data: bytes,
    *,
    key: bytes | str | None = _FROM_ENV,
    public_keys: Mapping[str, bytes] | None | Any = _FROM_ENV,
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
            # Hash the canonical content without copying the full JSON string
            # and then allocating a second full UTF-8 buffer in the isolate.
            digest = hashlib.sha256()
            for offset in range(len('{"content":'), end, 4096):
                digest.update(text[offset:min(offset + 4096, end)].encode("utf-8"))
            stored_digest = "sha256:" + digest.hexdigest()
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
    signature_status = UNPROVISIONED_SIGNATURE_STATUS
    signature_key_id = None
    if key is not None:
        verify_hmac_signature(digest, envelope.get("signature"), key, source=source)
        verified = True
        signature_status = "verified (hmac-sha256)"
    else:
        pinned = load_public_keys() if public_keys is _FROM_ENV else dict(public_keys or {})
        if pinned:
            from cryptography.exceptions import InvalidSignature
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

            signatures = envelope.get("signatures")
            if not isinstance(signatures, list):
                raise SnapshotIntegrityError(f"{source}: Ed25519 signature is missing")
            known_signature = False
            for signature in signatures:
                if not isinstance(signature, Mapping):
                    continue
                key_id = str(signature.get("key_id") or "")
                if signature.get("alg") != ED25519_SIGNATURE_ALG or key_id not in pinned:
                    continue
                known_signature = True
                try:
                    value = base64.b64decode(str(signature.get("value") or ""), validate=True)
                    Ed25519PublicKey.from_public_bytes(pinned[key_id]).verify(
                        value, digest.encode("ascii")
                    )
                except (ValueError, TypeError, InvalidSignature):
                    continue
                verified = True
                signature_key_id = key_id
                signature_status = f"verified (ed25519 key {key_id})"
                break
            if not verified:
                reason = "does not verify" if known_signature else "uses no pinned key"
                raise SnapshotIntegrityError(f"{source}: Ed25519 signature {reason}")
    return LoadedSnapshot(
        envelope,
        include_archive=include_archive,
        signature_verified=verified,
        signature_status=signature_status,
        signature_key_id=signature_key_id,
    )


def load_built_snapshot(
    snapshot: Snapshot,
    *,
    include_archive: bool = False,
    source: str = "repository build",
) -> LoadedSnapshot:
    """Load a trusted in-process build without publisher credentials.

    The loader still checks the content hash and snapshot ID. Public snapshot
    readers must use ``load_snapshot`` or ``load_snapshot_bytes`` so they verify
    the configured HMAC or a pinned Ed25519 signature.
    """
    return load_snapshot_bytes(
        snapshot.to_bytes(key=None, ed25519_signer=None),
        key=None,
        public_keys={},
        include_archive=include_archive,
        source=source,
    )


def load_snapshot(path: str | Path, *, key: bytes | str | None = _FROM_ENV,
                  public_keys: Mapping[str, bytes] | None | Any = _FROM_ENV,
                  include_archive: bool = False) -> LoadedSnapshot:
    """Read, check and index a snapshot.

    The content hash is always checked. The HMAC key defaults to
    ``MODELSPEC_SNAPSHOT_KEY``. Without an HMAC key, the loader uses the pinned
    Ed25519 public key set. Retired models are left out unless
    ``include_archive``.
    """
    path = Path(path)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SnapshotIntegrityError(f"{path}: not a gzipped JSON snapshot: {exc}") from exc
    return load_snapshot_bytes(
        data,
        key=key,
        public_keys=public_keys,
        include_archive=include_archive,
        source=str(path),
    )
