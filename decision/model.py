"""Sourced domain records for the decision engine (MODEL-134).

Registry lookups use decision.registry, or context={"registry": registry} for
an explicitly supplied registry with the same interface. No legacy flat scores
are read here. See docs/decision-model.md for the card evidence mapping.
"""

from __future__ import annotations

import datetime
import hashlib
import itertools
import json
import math
import re
from collections.abc import Iterable, Mapping
from importlib import import_module
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal, Self

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
    field_validator,
    model_validator,
)

from schema.evidence import BenchmarkEvidence

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
    retrieved_at: AwareDatetime | None = Field(default=None, exclude_if=lambda value: value is None)
    resolved_urls: list[HttpUrl] = Field(default_factory=list, exclude_if=lambda value: not value)


class TargetRef(Record):
    kind: Literal["fact", "evidence"]
    id: Text


class VerificationTarget(TargetRef):
    value_hash: ContentRef


class VerificationActor(Record):
    agent: Text
    model_family: Text
    method: Text


#: The ``model_family`` of a reader that runs no model: always independent.
DETERMINISTIC = "deterministic"

#: A family name's first word -> the lab whose lineage it is.
_LINEAGES = {
    "anthropic": "anthropic", "claude": "anthropic",
    "openai": "openai", "gpt": "openai",
    "google": "google", "gemini": "google", "gemma": "google",
    "alibaba": "alibaba", "qwen": "alibaba",
    "meta": "meta", "llama": "meta",
    "xai": "xai", "grok": "xai",
    "mistral": "mistral", "mixtral": "mistral", "codestral": "mistral",
    "deepseek": "deepseek",
}


def model_family(name: str) -> str:
    """The lineage a recorded ``model_family`` names: "claude" and "anthropic" are one.

    Case and a trailing version are dropped ("gpt-5", "gemma4", "qwen3"); a
    first word that names a known lineage ("claude-sonnet-5", "mistral-large")
    maps to its lab. Gemma and Gemini are one family: a second key must not
    share the first key's lineage. An unknown name is its own family.
    """
    base = re.sub(r"[-_ .]?v?\d[\w.\-]*$", "", name.strip().casefold()) or name.casefold()
    return _LINEAGES.get(re.split(r"[-_ ]", base)[0], base)


def independent_families(collector: str, verifier: str) -> bool:
    """Two keys: the verifier is deterministic, or of another model family (MODEL-140)."""
    return verifier == DETERMINISTIC or model_family(collector) != model_family(verifier)


def verification_counts(outcome: str, collector: str, verifier: str) -> bool:
    """Whether a logged verification decides its value's state.

    A same-family ``verified`` is not a second key and does not count; any other
    outcome counts, so a same-family mismatch still keeps a value out.
    """
    return outcome != "verified" or independent_families(collector, verifier)


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
    def independent(self) -> bool:
        return independent_families(self.collector.model_family, self.verifier.model_family)

    @property
    def counts(self) -> bool:
        """See ``verification_counts``: a same-family ``verified`` is ignored."""
        return verification_counts(
            self.outcome, self.collector.model_family, self.verifier.model_family)

    @property
    def quarantined(self) -> bool:
        return self.outcome != "verified" or not self.independent


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


#: The most members a set value may have for a verification of it written in
#: another order to be found (MODEL-416). Before MODEL-416 a verification bound
#: the order the card filed, so reordering the same members gave a new hash and
#: stepped out from under a mismatch. Those rows are fixed: every verification
#: written since binds the canonical form. Matching tries every ordering of the
#: members, 9! = 362,880 hashes at most (about 0.2 s), and only for a fact that
#: has a row on a hash nothing else explains. Past the bound the snapshot fails
#: closed (``exceeds_legacy_orderings``), and a census test over the data
#: (``tests/test_set_value_hashes.py``) fails if any fact would be held so.
LEGACY_ORDERINGS_MAX_MEMBERS = 9


def unordered_facet(facet: Any) -> bool:
    """Whether a registered facet's value is a set whose order means nothing.

    Read from the registry's explicit ``value_type.unordered``, never inferred
    from the value's shape: a range is a list whose order does mean something.
    """
    return getattr(getattr(facet, "value_type", None), "unordered", False) is True


def _members(value: JsonValue) -> list[str] | None:
    if isinstance(value, list) and all(isinstance(member, str) for member in value):
        return value
    return None


def canonical_value(value: JsonValue, *, unordered: bool) -> JsonValue:
    """The form a verification binds: an unordered value's members, sorted.

    A repeated member is kept, never folded: a set's members are unique, so a
    list with a repeat is a different, invalid value, not the same set.
    """
    members = _members(value) if unordered else None
    return value if members is None else sorted(members)


def exceeds_legacy_orderings(value: JsonValue, *, unordered: bool) -> bool:
    """Whether a legacy hash of another order of ``value`` can no longer be found.

    Such a row cannot be told apart from a row on other members, so a caller
    that meets one it cannot bind must hold the value back (fail closed).
    """
    members = _members(value) if unordered else None
    return members is not None and len(members) > LEGACY_ORDERINGS_MAX_MEMBERS


def verification_value_hash(value: JsonValue, *, unordered: bool) -> str:
    """The ``value_hash`` a new verification records: the same for any member order."""
    return value_hash(canonical_value(value, unordered=unordered))


def matching_value_hashes(
    value: JsonValue, recorded: Iterable[str], *, unordered: bool
) -> set[str]:
    """Which of the ``recorded`` hashes bind ``value``.

    For an ordered facet, only ``value_hash(value)``. For an unordered facet, a
    hash binds the member set, not an order: the canonical hash, the legacy hash
    of the order filed, and the legacy hash of any other order of the same
    members (up to ``LEGACY_ORDERINGS_MAX_MEMBERS``). So, up to that bound, a
    reorder never changes which verifications apply: it cannot clear a mismatch,
    nor drop a verified. Past it a legacy hash of another order stays unbound;
    see ``exceeds_legacy_orderings``.
    """
    recorded = set(recorded)
    found = recorded & {value_hash(value)}
    members = _members(value) if unordered else None
    if members is None:
        return found
    found |= recorded & {verification_value_hash(value, unordered=True)}
    rest = recorded - found
    if not rest or len(members) > LEGACY_ORDERINGS_MAX_MEMBERS:
        return found
    # ``value_hash`` of a list of strings, without re-encoding each member per order.
    encoded = [json.dumps(member, ensure_ascii=False) for member in members]
    for ordering in itertools.permutations(encoded):
        candidate = "sha256:" + hashlib.sha256(
            ("[" + ",".join(ordering) + "]").encode("utf-8")).hexdigest()
        if candidate in rest:
            found.add(candidate)
            rest.discard(candidate)
            if not rest:
                break
    return found


def _fact_field(fact: Any, key: str, default: Any = None) -> Any:
    return fact.get(key, default) if isinstance(fact, Mapping) else getattr(fact, key, default)


def _price_date(value: Any) -> datetime.date | None:
    if value is None or type(value) is datetime.date:
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.date.fromisoformat(value)
        except ValueError:
            pass
        else:
            if parsed.isoformat() == value:
                return parsed
    raise ValueError("a scheduled price date must be an exact YYYY-MM-DD date")


def fact_verification_value(fact: Any) -> JsonValue:
    """Bind a dated price to its dates while preserving undated fact hashes."""
    start = _price_date(_fact_field(fact, "effective_from"))
    until = _price_date(_fact_field(fact, "effective_until"))
    value = _fact_field(fact, "value")
    if start is None and until is None:
        return value
    return {
        "value": value,
        "effective_from": start.isoformat() if start is not None else None,
        "effective_until": until.isoformat() if until is not None else None,
    }


def validate_price_schedules(facts: Iterable[Any]) -> None:
    """Validate inclusive price periods on either records or raw input mappings."""
    groups: dict[str, list[tuple[datetime.date | None, datetime.date | None]]] = {}
    dated: set[str] = set()
    ids: set[str] = set()
    for fact in facts:
        facet = str(_fact_field(fact, "facet"))
        start = _price_date(_fact_field(fact, "effective_from"))
        until = _price_date(_fact_field(fact, "effective_until"))
        groups.setdefault(facet, []).append((start, until))
        if start is None and until is None:
            continue
        subject = _fact_field(fact, "subject")
        value = _fact_field(fact, "value")
        if (_fact_field(subject, "kind") != "offering"
                or not facet.startswith("offering.price.")
                or _fact_field(fact, "state") != "known"
                or type(value) not in (int, float) or not math.isfinite(value) or value < 0):
            raise ValueError(
                "a dated price must be a known nonnegative numeric offering.price fact")
        rid = _fact_field(fact, "id")
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError("scheduled price fact IDs must be present and unique for a subject")
        ids.add(rid)
        if start is not None and until is not None and until < start:
            raise ValueError(f"{facet}: a scheduled price ends before it starts")
        dated.add(facet)
    for facet, periods in groups.items():
        if facet not in dated:
            if len(periods) > 1:
                raise ValueError("fact IDs and facets must be unique for a subject")
            continue
        if any(start is None and until is None for start, until in periods):
            raise ValueError(f"{facet}: mixed dated and undated price facts")
        ordered = sorted(periods, key=lambda period: period[0] or datetime.date.min)
        for (_start, until), (start, _until) in zip(ordered, ordered[1:]):
            if until is None or start is None or until >= start:
                raise ValueError(f"{facet}: scheduled price periods overlap")
            if until + datetime.timedelta(days=1) != start:
                raise ValueError(f"{facet}: scheduled price periods have a gap")


def evidence_verification_value(evidence: object) -> JsonValue:
    """The evidence reading bound to a verification.

    Evidence without structured uncertainty or quality metadata keeps the v1
    score-only identity. Once any decision-affecting metadata is present, the
    verification binds all of it, including the absence of the other fields.
    """
    get = evidence.get if isinstance(evidence, dict) else lambda key, default=None: getattr(
        evidence, key, default
    )
    score = get("score")
    interval = get("interval")
    n = get("n")
    quality_flags = sorted(get("quality_flags") or [])
    if interval is None and n is None and not quality_flags:
        return score
    return {
        "score": score,
        "interval": list(interval) if interval is not None else None,
        "n": n,
        "quality_flags": quality_flags,
    }


def _check_target(verification: Verification | None, kind: str, id: str, value: JsonValue,
                  *, unordered: bool = False) -> None:
    if verification is not None and (
        verification.target.kind != kind
        or verification.target.id != id
        or not matching_value_hashes(
            value, [verification.target.value_hash], unordered=unordered)
    ):
        raise ValueError("verification target or value_hash does not match this record")


#: A first-party measurement stops deciding anything this many days after its
#: sampling window closes (docs/method/speed-measurement.md, "Staleness").
MEASUREMENT_STALE_AFTER_DAYS = 30


class MeasurementWindow(Record):
    start: AwareDatetime
    end: AwareDatetime


class Measurement(Record):
    """How ModelSpec measured a fact's value (ADR 0004, MODEL-212).

    ``value`` is the median. ``iqr`` is the spread one request sees;
    ``interval`` is the 95% distribution-free interval of the median, the
    uncertainty a ranking must respect. ``provenance: fixture`` marks a number
    replayed from recorded test streams: the published snapshot refuses it.
    """

    measured_by: Literal["ModelSpec"]
    method: Text
    method_url: HttpUrl
    workload: Text
    #: The reasoning effort the offering was pinned at, and the median
    #: reasoning tokens its counted requests reported.
    effort: Text
    reasoning_tokens: float = Field(ge=0)
    provenance: Literal["live", "fixture"]
    run_id: Text
    vantage: Text
    n: int = Field(ge=1, strict=True)
    time_slots: int = Field(ge=1, strict=True)
    days: int = Field(ge=1, strict=True)
    failure_rate: float = Field(ge=0, le=1)
    median: float
    iqr: tuple[float, float]
    interval: tuple[float, float]
    window: MeasurementWindow

    @model_validator(mode="after")
    def ordered(self) -> Self:
        numbers = (self.median, *self.iqr, *self.interval)
        if not all(math.isfinite(x) for x in numbers):
            raise ValueError("measurement numbers must be finite")
        if not (self.iqr[0] <= self.median <= self.iqr[1]):
            raise ValueError("the median must lie inside its IQR")
        if not (self.interval[0] <= self.median <= self.interval[1]):
            raise ValueError("the median must lie inside its interval")
        if self.window.start > self.window.end:
            raise ValueError("the measurement window ends before it starts")
        return self

    def stale(self, as_of: datetime.date) -> bool:
        age = as_of - self.window.end.date()
        return age > datetime.timedelta(days=MEASUREMENT_STALE_AFTER_DAYS)


class Fact(Record):
    id: Text
    subject: SubjectRef
    facet: Text
    value: JsonValue = None
    state: Literal["known", "unknown", "not_disclosed", "requires_contract"]
    sources: list[SourceRef] = Field(default_factory=list)
    checked_sources: list[Text] = Field(default_factory=list)
    derivation: dict[str, JsonValue] | None = None
    measurement: Measurement | None = None
    verification: Verification | None = None
    effective_from: datetime.date | None = None
    effective_until: datetime.date | None = None

    @field_validator("effective_from", "effective_until", mode="before")
    @classmethod
    def exact_price_date(cls, value: Any) -> datetime.date | None:
        return _price_date(value)

    @model_validator(mode="after")
    def valid_fact(self, info: ValidationInfo) -> Self:
        validate_price_schedules([self])
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
        if self.measurement is not None:
            if self.state != "known" or self.value != self.measurement.median:
                raise ValueError("a measured fact is known and its value is the median")
            if "modelspec_measurement" not in facet.permitted_source_kinds:
                raise ValueError(f"facet {self.facet} does not admit a ModelSpec measurement")
        _check_target(self.verification, "fact", self.id, fact_verification_value(self),
                      unordered=unordered_facet(facet))
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


class RenderedControl(Record):
    selector: Annotated[Text, Field(max_length=1024)]

    @field_validator("selector")
    @classmethod
    def css_selector(cls, value: str) -> str:
        from decision.normalise import Locator

        Locator("css", value)
        return value


class RenderedClick(RenderedControl):
    action: Literal["click", "reject_consent", "scroll"]


class RenderedSelect(RenderedControl):
    action: Literal["select_option"]
    value: Annotated[Text, Field(max_length=256)]


class RenderedWait(RenderedControl):
    action: Literal["wait_text"]
    text: Annotated[Text, Field(max_length=256)]


RenderedInteraction = Annotated[
    RenderedClick | RenderedSelect | RenderedWait, Field(discriminator="action")
]


class Source(Record):
    id: Text
    url: HttpUrl
    #: Whether values read from this source age from the day it was observed.
    #: Static is the safe default for papers, system cards, and launch posts.
    volatility: Literal["static", "live"] = "static"
    fetch: Literal["http", "conditional_http", "rendered"] = "conditional_http"
    normaliser: Text = "html-default"
    #: A ``source_kinds`` id from ``registry/facets.yaml``. Absent means the kind
    #: is unknown; existing registries still load.
    kind: str | None = None
    cited_regions: list[CitedRegion] = Field(default_factory=list)
    rendered_interactions: list[RenderedInteraction] = Field(
        default_factory=list, max_length=16, exclude_if=lambda value: not value)

    @model_validator(mode="after")
    def unique_regions(self) -> Self:
        from decision.normalise import NORMALISERS, Locator

        ids = [region.id for region in self.cited_regions]
        if len(ids) != len(set(ids)):
            raise ValueError("cited region IDs must be unique within a source")
        if self.normaliser not in NORMALISERS:
            raise ValueError(f"unknown normaliser {self.normaliser!r}")
        if self.rendered_interactions:
            if self.fetch != "rendered" or NORMALISERS[self.normaliser].content != "html":
                raise ValueError("rendered interactions require a rendered HTML source")
            if self.rendered_interactions[-1].action != "wait_text":
                raise ValueError("rendered interactions must end by waiting for cited text")
        for region in self.cited_regions:
            locator = region.locator
            if locator.kind == "xpath":
                raise ValueError(
                    "xpath cited-region locators are not supported; register a css, "
                    "heading_anchor, table, or page locator"
                )
            kind = "heading" if locator.kind == "heading_anchor" else locator.kind
            Locator(kind, locator.value)
            if NORMALISERS[self.normaliser].content in {"text", "json"} and kind != "page":
                raise ValueError("text sources support only page locators")
        if self.kind is not None:
            from decision.registry import default as default_registry

            try:
                default_registry().source_kind(self.kind)
            except KeyError as exc:
                raise ValueError(f"unknown source kind {self.kind!r}") from exc
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
            _check_target(
                self.verification, "evidence", self.id, evidence_verification_value(self)
            )
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
    if len(ids) != len(set(ids)):
        raise ValueError("fact IDs and facets must be unique for a subject")
    validate_price_schedules(facts)
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


class SubscriptionOffering(Record):
    """A fixed-period plan that covers one or more models.

    Subscription facts stay separate from metered inference offerings because
    a plan can cover several models and its allowance is not a token price.
    """

    kind: Literal["subscription"]
    provider: PathPart
    plan: PathPart
    name: Text
    facts: list[Fact] = Field(default_factory=list)

    REQUIRED_FACETS: ClassVar[frozenset[str]] = frozenset({
        "offering.subscription.price",
        "offering.subscription.billing_period",
        "offering.subscription.models_covered",
        "offering.subscription.usage_allowance",
        "offering.subscription.programmatic_or_agent_use",
    })
    #: MODEL-200's plan facts. Each may be stated once; an absent one is unknown.
    #: ``unknown`` means not yet researched, so it needs no checked sources.
    PLAN_FACETS: ClassVar[frozenset[str]] = frozenset({
        "offering.subscription.availability",
        "offering.subscription.surfaces",
        "offering.subscription.coding_tools_quote",
        "offering.subscription.families_covered",
        "offering.subscription.coverage_quote",
        "offering.subscription.allowance.relative_to",
        "offering.subscription.allowance.multiplier",
        "offering.subscription.allowance.window",
        "offering.subscription.allowance.tokens",
        "offering.subscription.price_cny",
    })

    @property
    def id(self) -> str:
        return f"{self.provider}/subscription/{self.plan}"

    @model_validator(mode="after")
    def valid_subscription(self, info: ValidationInfo) -> Self:
        # A provider or a subscription-only vendor (MODEL-205) may sell a plan.
        _registered(info, "plan_owner", self.provider)
        _check_facts(self.facts, "offering", self.id)
        facets = {fact.facet for fact in self.facts}
        if not self.REQUIRED_FACETS <= facets <= self.REQUIRED_FACETS | self.PLAN_FACETS:
            missing = sorted(self.REQUIRED_FACETS - facets)
            extra = sorted(facets - self.REQUIRED_FACETS - self.PLAN_FACETS)
            raise ValueError(
                "a subscription requires exactly one fact for every subscription facet; "
                f"missing={missing}, extra={extra}"
            )
        for fact in self.facts:
            if fact.state == "unknown" and fact.facet in self.PLAN_FACETS:
                continue
            if fact.state != "known" and not fact.checked_sources:
                raise ValueError(
                    f"{fact.id}: a non-known subscription fact requires checked_sources"
                )
        return self


def load_subscription_offerings(
    path: str | Path, *, registry=None
) -> list[SubscriptionOffering]:
    """Read ``offerings/subscriptions/<provider>.yaml``."""

    path = Path(path)
    rows = TypeAdapter(list[SubscriptionOffering]).validate_python(
        yaml.safe_load(path.read_text(encoding="utf-8")),
        context={"registry": registry},
    )
    ids: set[str] = set()
    for row in rows:
        if path.stem != row.provider:
            raise ValueError(
                f"subscription offering {row.id} does not match path {row.provider}.yaml"
            )
        if row.id in ids:
            raise ValueError(f"duplicate subscription offering: {row.id}")
        ids.add(row.id)
    return rows
