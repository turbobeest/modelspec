"""Sourced domain records for the decision engine (MODEL-134).

Registry lookups use decision.registry, or context={"registry": registry} for
an explicitly supplied registry with the same interface. No legacy flat scores
are read here. See docs/decision-model.md for the card evidence mapping.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import math
from importlib import import_module
from pathlib import Path
from typing import Annotated, Literal, Self

import yaml
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    JsonValue,
    TypeAdapter,
    ValidationInfo,
    model_validator,
)

from schema.card import BenchmarkEvidence

Text = Annotated[str, Field(min_length=1, pattern=r"\S", strict=True)]
ContentRef = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SubjectRef(Record):
    kind: Literal["model", "offering", "provider"]
    id: Text


class SourceRef(Record):
    source_id: Text
    snapshot_ref: ContentRef
    cited_regions: list[Text] = Field(min_length=1)


class TargetRef(Record):
    kind: Literal["fact", "evidence"]
    id: Text


class VerificationTarget(TargetRef):
    value_hash: ContentRef


class VerificationActor(Record):
    agent: Text
    model_family: Text
    method: Text


class Verification(Record):
    target: VerificationTarget
    collector: VerificationActor
    verifier: VerificationActor
    method: Text
    outcome: Literal["verified", "mismatch", "unreachable"]
    date: datetime.date
    diff: Text | None = None

    @model_validator(mode="after")
    def independent_check(self) -> Self:
        if (
            self.collector.agent == self.verifier.agent
            and self.collector.model_family == self.verifier.model_family
        ):
            raise ValueError("verification must be independent in agent or model family")
        if self.outcome == "mismatch" and self.diff is None:
            raise ValueError("a mismatch requires a diff")
        if self.outcome != "mismatch" and self.diff is not None:
            raise ValueError("diff belongs only to a mismatch")
        return self

    @property
    def quarantined(self) -> bool:
        return self.outcome != "verified"


def _registry(info: ValidationInfo):
    registry = (info.context or {}).get("registry")
    if registry is None:
        registry = import_module("decision.registry")
    return registry


def _registered(info: ValidationInfo, collection: str, id: str):
    registry = _registry(info)
    try:
        return getattr(registry, collection)(id)
    except KeyError as exc:
        raise ValueError(f"unknown {collection} ID: {id}") from exc


def _allowed_values(registry, facet) -> frozenset[str] | None:
    if isinstance(facet.value_type, str):
        return None
    owner = registry.default() if hasattr(registry, "default") else registry
    return owner.allowed_values(facet) if hasattr(owner, "allowed_values") else None


def _check_value(value: JsonValue, facet, registry) -> None:
    value_type = facet.value_type
    kind = value_type if isinstance(value_type, str) else value_type.kind
    if not isinstance(value_type, str):
        if value == "unbounded" and value_type.unbounded:
            return
        if value == "not_offered" and value_type.not_offered:
            return
    if kind == "date":
        if not isinstance(value, str):
            raise ValueError("date value must be an ISO date string")
        parsed = datetime.date.fromisoformat(value)
        valid = parsed.isoformat() == value
    else:
        checks = {
            "integer": lambda: type(value) is int,
            "number": lambda: type(value) in (int, float) and math.isfinite(value),
            "bool": lambda: type(value) is bool,
            "boolean": lambda: type(value) is bool,
            "string": lambda: isinstance(value, str),
            "string_set": lambda: (
                isinstance(value, list)
                and all(isinstance(item, str) for item in value)
                and len(value) == len(set(value))
            ),
            "enum": lambda: isinstance(value, str),
            "set": lambda: (
                isinstance(value, list)
                and all(isinstance(item, str) for item in value)
                and len(value) == len(set(value))
            ),
            "range": lambda: (
                isinstance(value, list)
                and len(value) == 2
                and all(type(item) in (int, float) and math.isfinite(item) for item in value)
                and value[0] <= value[1]
            ),
        }
        if kind not in checks:
            raise ValueError(f"unsupported facet value_type: {kind}")
        valid = checks[kind]()
    if not valid:
        raise ValueError(f"value must match facet value_type {kind}")
    allowed = _allowed_values(registry, facet)
    members = value if kind in ("set", "string_set") else [value]
    if allowed is not None and any(member not in allowed for member in members):
        raise ValueError(f"value must use the facet's registered values: {sorted(allowed)}")


def value_hash(value: JsonValue) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _check_target(verification: Verification | None, kind: str, id: str, value: JsonValue) -> None:
    if verification is not None and (
        verification.target.kind != kind
        or verification.target.id != id
        or verification.target.value_hash != value_hash(value)
    ):
        raise ValueError("verification target or value_hash does not match this record")


class Fact(Record):
    id: Text
    subject: SubjectRef
    facet: Text
    value: JsonValue = None
    state: Literal["known", "unknown", "not_disclosed", "requires_contract"]
    sources: list[SourceRef] = Field(default_factory=list)
    checked_sources: list[Text] = Field(default_factory=list)
    verification: Verification | None = None

    @model_validator(mode="after")
    def valid_fact(self, info: ValidationInfo) -> Self:
        facet = _registered(info, "facet", self.facet)
        facet_subject = getattr(facet, "subject", None)
        if facet_subject is not None and facet_subject != self.subject.kind:
            raise ValueError(
                f"facet {self.facet} belongs to {facet_subject}, not {self.subject.kind}"
            )
        if self.subject.kind == "provider":
            _registered(info, "provider", self.subject.id)
        if self.state == "known":
            if self.value is None or not self.sources:
                raise ValueError("a known fact requires a value and sources")
            _check_value(self.value, facet, _registry(info))
        elif self.value is not None:
            raise ValueError("only a known fact may have a value")
        _check_target(self.verification, "fact", self.id, self.value)
        return self

    @property
    def quarantined(self) -> bool:
        return self.verification is None or self.verification.quarantined


class RegionLocator(Record):
    kind: Literal["page", "css", "xpath", "heading", "heading_anchor", "table"]
    value: str = ""


class CitedRegion(Record):
    id: Text
    locator: RegionLocator


class Source(Record):
    id: Text
    url: HttpUrl
    fetch: Literal["http", "conditional_http", "rendered"] = "conditional_http"
    normaliser: Text = "html-default"
    cited_regions: list[CitedRegion] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_regions(self) -> Self:
        from decision.normalise import NORMALISERS, Locator

        ids = [region.id for region in self.cited_regions]
        if len(ids) != len(set(ids)):
            raise ValueError("cited region IDs must be unique within a source")
        if self.normaliser not in NORMALISERS:
            raise ValueError(f"unknown normaliser {self.normaliser!r}")
        for region in self.cited_regions:
            locator = region.locator
            if locator.kind == "xpath":
                raise ValueError(
                    "xpath cited-region locators are not supported; register a css, "
                    "heading_anchor, table, or page locator"
                )
            kind = "heading" if locator.kind == "heading_anchor" else locator.kind
            Locator(kind, locator.value)
            if NORMALISERS[self.normaliser].content == "text" and kind != "page":
                raise ValueError("text sources support only page locators")
        return self


class SourceSnapshot(Record):
    source_id: Text
    retrieved_at: AwareDatetime
    page_fingerprint: ContentRef
    region_fingerprints: dict[Text, ContentRef | None]
    copy_ref: ContentRef
    etag: Text | None = None
    last_modified: Text | None = None


class EvidenceSubjectRef(Record):
    kind: Literal["model", "offering"]
    id: Text


class Evidence(BenchmarkEvidence):
    """Additive v2 evidence; legacy verified_at does not grant v2 verification."""

    model_config = ConfigDict(extra="forbid")
    id: Text | None = None
    subject: EvidenceSubjectRef | None = None
    harness: Text | None = None
    effort: Text | None = None
    tools: list[Text] | None = None
    measured_by: (
        Literal[
            "benchmark_author",
            "independent_evaluator",
            "provider_self_report",
            "modelspec",
            "outcome_protocol",
        ]
        | None
    ) = None
    subcategory: Text | None = None
    sources: list[SourceRef] = Field(default_factory=list)
    verification: Verification | None = None

    @model_validator(mode="after")
    def qualified_evidence(self, info: ValidationInfo) -> Self:
        if not math.isfinite(self.score):
            raise ValueError("evidence score must be finite")
        if self.harness is not None and self.harness != "unregistered":
            _registered(info, "harness", self.harness)
        if self.verification is not None:
            if self.id is None or self.subject is None or not self.sources:
                raise ValueError("verification requires an ID, subject and source snapshots")
            _check_target(self.verification, "evidence", self.id, self.score)
        return self

    @property
    def quarantined(self) -> bool:
        return self.verification is None or self.verification.quarantined


Lifecycle = Literal["active", "deprecated", "retired"]
ModelId = Annotated[str, Field(pattern=r"^[^/\s]+/[^/\s]+$")]


class Model(Record):
    id: ModelId
    lifecycle: Lifecycle
    facts: list[Fact] = Field(default_factory=list)

    @model_validator(mode="after")
    def own_facts(self) -> Self:
        _check_facts(self.facts, "model", self.id)
        return self

    @property
    def in_lineup(self) -> bool:
        return self.lifecycle != "retired"

    @property
    def in_live_archive(self) -> bool:
        return self.lifecycle == "retired"


def _check_facts(facts: list[Fact], kind: str, id: str) -> None:
    ids = [fact.id for fact in facts]
    facets = [fact.facet for fact in facts]
    if len(ids) != len(set(ids)) or len(facets) != len(set(facets)):
        raise ValueError("fact IDs and facets must be unique for a subject")
    if any(fact.subject.kind != kind or fact.subject.id != id for fact in facts):
        raise ValueError("fact subject does not match its owner")


PathPart = Annotated[str, Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")]


class Offering(Record):
    model: ModelId
    provider: PathPart
    region: PathPart
    tier: PathPart
    facts: list[Fact] = Field(default_factory=list)

    @property
    def id(self) -> str:
        return f"{self.provider}/{self.model}/{self.region}/{self.tier}"

    @model_validator(mode="after")
    def valid_offering(self, info: ValidationInfo) -> Self:
        _registered(info, "provider", self.provider)
        _check_facts(self.facts, "offering", self.id)
        return self


def load_offerings(path: str | Path, *, registry=None) -> list[Offering]:
    """Read a list from offerings/<provider>/<lab>/<model>.yaml.

    The last three path components must agree with every row's identity.
    Source storage and cross-record source resolution belong to MODEL-137/138.
    """
    path = Path(path)
    rows = TypeAdapter(list[Offering]).validate_python(
        yaml.safe_load(path.read_text(encoding="utf-8")),
        context={"registry": registry},
    )
    ids: set[str] = set()
    for row in rows:
        expected = Path(row.provider) / f"{row.model}.yaml"
        if tuple(path.parts[-3:]) != expected.parts:
            raise ValueError(f"offering {row.id} does not match path {expected}")
        if row.id in ids:
            raise ValueError(f"duplicate offering: {row.id}")
        ids.add(row.id)
    return rows
