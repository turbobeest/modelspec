"""``breakdown.json``: the release breakdown as data (MODEL-224, design §3.2).

Every number is a ``Cited``: a value with the snapshot record behind it, or
the name of the computation that produced it from the snapshot. A number
with neither fails validation, which is the machine form of "nothing is
typed". ``schemas/release-breakdown-v1.schema.json`` is generated from
``Breakdown`` (``write_schema``) and a test keeps the two equal.
"""

from __future__ import annotations

import datetime as _dt
import json
from datetime import date
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "release-breakdown/1"
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "release-breakdown-v1.schema.json"
SCHEMA_ID = "https://modelspec.dev/schemas/release-breakdown-v1.schema.json"

Comparability = Literal["same_setup", "different_setup", "not_comparable"]
Band = Literal["best", "rest", "thin"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Cited(_Strict):
    """One number and where it came from."""

    value: float
    unit: str | None = None
    #: The 80% interval, for an estimate.
    low: float | None = None
    high: float | None = None
    #: The snapshot record behind a stored value.
    record_id: str | None = None
    #: The records a computed value was computed from.
    records: list[str] = Field(default_factory=list)
    #: The decision a decision-engine value came from, a key into ``decisions``.
    decision_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    #: The record's verification date; for a computed value, the snapshot's ``as_of``.
    read_date: date
    #: The computation, e.g. ``offering.cost_per_task``, when derived.
    computed: str | None = None

    @model_validator(mode="after")
    def _traceable(self) -> Cited:
        if self.record_id is None and self.computed is None:
            raise ValueError("a cited number needs a record_id or a computed origin")
        if (self.low is None) != (self.high is None):
            raise ValueError("an interval needs both ends")
        return self


class ModelRef(_Strict):
    id: str
    name: str
    provider: str
    class_: str = Field(alias="class")

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class SnapshotRef(_Strict):
    snapshot_id: str
    content_hash: str
    as_of: date | None
    key_id: str


class AccuracyRef(_Strict):
    snapshot: str
    profile: Literal["pr"]
    status: Literal["pass"]


class GeneratorRef(_Strict):
    package: Literal["release_blog"] = "release_blog"
    version: str


class VocabularyRef(_Strict):
    """The published decision vocabulary display names came from."""

    snapshot: str
    sha256: str


class GeneratedFrom(_Strict):
    after: SnapshotRef
    before: SnapshotRef | None
    accuracy: AccuracyRef
    generator: GeneratorRef
    vocabulary: VocabularyRef | None = None


class DecisionRef(_Strict):
    """One ``decide()`` call the post relies on. Re-running ``spec`` against
    ``snapshot_id`` reproduces ``decision_id``."""

    purpose: str
    spec: dict[str, Any]
    spec_hash: str
    decision_id: str
    snapshot_id: str


# ── claims vs evidence (§3.3) ───────────────────────────────────────────────


class Setup(_Strict):
    version: str | None = None
    subcategory: str | None = None
    harness: str | None = None
    effort: str | None = None
    date: _dt.date | None = None


class Reading(_Strict):
    value: Cited
    measured_by: str
    setup: Setup
    #: The reading's sample size, from its record.
    n: Cited | None = None
    quality_flags: list[str] = Field(default_factory=list)
    #: The retained record's own ``limitations``, verbatim, when it has them.
    limitations: str | None = None
    comparability: Comparability
    differs_in: list[str] = Field(default_factory=list)
    #: reading − claim, for ``same_setup`` only.
    difference: Cited | None = None
    #: Whether the claim lies inside the reading's own interval, when it has one.
    claim_within_interval: bool | None = None


class ClaimRow(_Strict):
    benchmark: str
    claim: Cited
    setup: Setup
    limitations: str | None = None
    readings: list[Reading] = Field(default_factory=list)
    status: Literal["read", "no_independent_reading_yet"]


class Unreported(_Strict):
    benchmark: str
    reading: Cited
    measured_by: str
    setup: Setup


class ClaimsVsEvidence(_Strict):
    claims: list[ClaimRow] = Field(default_factory=list)
    #: Independent readings in the model's estimated domains with no lab figure.
    unreported: list[Unreported] = Field(default_factory=list)


# ── standing (§3.4) ─────────────────────────────────────────────────────────


class Named(_Strict):
    id: str
    name: str


class Leader(_Strict):
    model: str
    estimate: Cited | None
    p_best: Cited | None


class Driver(_Strict):
    """A record the estimate was fitted from (``capability.drivers``)."""

    record_id: str
    benchmark: str
    version: str | None


class Spread(_Strict):
    """The estimates of every model of the same class in the domain, for scale."""

    models: Cited
    low: Cited
    median: Cited
    high: Cited


class DomainStanding(_Strict):
    domain: Named
    estimate: Cited
    #: Where the class's estimates sit, so a reader can place ``estimate``.
    spread: Spread
    decision: str
    #: The model's place among ranked models (``Result.model_rank``); null when unranked.
    rank: Cited | None
    band: Band | None
    #: Models in the ``best`` band.
    band_size: Cited
    #: Distinct models the decision ranked.
    ranked_models: Cited
    p_best: Cited | None
    top3_stability: Cited | None
    #: The ``best`` band, ordered by P(best), at most ``LEADERS_MAX`` of it.
    leaders: list[Leader] = Field(default_factory=list)
    drivers: list[Driver] = Field(default_factory=list)


# ── template changes (§3.5) ─────────────────────────────────────────────────


class TemplateRef(_Strict):
    id: str
    category: str
    tier: str
    name: str


class TemplateChange(_Strict):
    template: TemplateRef
    decisions: dict[Literal["before", "after"], str]
    band_before: Band | None
    band_after: Band | None
    model_in_best: dict[Literal["before", "after"], bool]
    top_before: list[str]
    top_after: list[str]
    displaced: list[str]
    #: ``decision.compare.compare(before, after)["counts"]``.
    compare_counts: dict[str, Cited]


class TemplateChanges(_Strict):
    #: Why the section is empty, when it is.
    unavailable: str | None = None
    changes: list[TemplateChange] = Field(default_factory=list)


# ── cost (§3.6) and hardware (§3.7) ─────────────────────────────────────────


class TaskSize(_Strict):
    """The task a cost is for: a spec input, not a finding."""

    input: int
    output: int
    #: ``contract_default`` or the template that sets it.
    basis: str


class OfferingCost(_Strict):
    offering: str
    provider: str
    region: str
    tier: str
    task: TaskSize
    cost_per_task: Cited | None
    price_input: Cited | None
    price_output: Cited | None


class PlanCoverage(_Strict):
    plan: dict[Literal["id", "provider", "name"], str]
    covers: bool | Literal["unknown"]
    rule: str | None = None
    quote: str | None = None
    quote_record: str | None = None
    monthly: Cited | None
    break_even: Cited | None
    surface: str | None = None


class Cost(_Strict):
    offerings: list[OfferingCost] = Field(default_factory=list)
    plans: list[PlanCoverage] = Field(default_factory=list)


class HardwareFit(_Strict):
    weights_openness: str
    fits: list[str] | None
    fits_record: str | None
    indeterminate: list[str] | None
    indeterminate_record: str | None


# ── gaps (§3.8) ─────────────────────────────────────────────────────────────


class UnknownFacet(_Strict):
    facet: str
    subjects: list[str]


class DomainGap(_Strict):
    domain: str
    reason: str
    #: The verified fact the reason rests on, for ``not_offered``.
    record_id: str | None = None


class Speed(_Strict):
    offering: str
    time_to_first_token: Cited | Literal["unknown"]
    throughput: Cited | Literal["unknown"]


class NotYetMeasured(_Strict):
    unknown_facets: list[UnknownFacet] = Field(default_factory=list)
    #: Reason -> count of this model's rows the snapshot refused; null when the
    #: snapshot predates ``content.held_back``.
    held_back: dict[str, Cited] | None
    #: Domains the class can be measured on, not measured yet: unknown.
    domains_without_estimate: list[str] = Field(default_factory=list)
    #: Domains the class cannot be measured on (MODEL-97): not a gap.
    domains_inapplicable: list[DomainGap] = Field(default_factory=list)
    #: Domains a verified fact about this model rules out.
    domains_not_offered: list[DomainGap] = Field(default_factory=list)
    claims_without_reading: list[str] = Field(default_factory=list)
    speed: list[Speed] = Field(default_factory=list)


class Recheck(_Strict):
    first_published: date
    schedule: list[dict[str, Any]]


class Disclosures(_Strict):
    supplier: str | None
    early_access: str | None
    neutrality: str


class Headline(_Strict):
    text: str = Field(max_length=110)
    #: The rule that chose it, so a reader can see why this sentence.
    rule: str


class Breakdown(_Strict):
    schema_version: Literal["release-breakdown/1"] = SCHEMA_VERSION
    model: ModelRef
    revision: int = Field(ge=1)
    headline: Headline
    generated_from: GeneratedFrom
    decisions: list[DecisionRef]
    claims_vs_evidence: ClaimsVsEvidence
    standing: list[DomainStanding]
    template_changes: TemplateChanges
    cost: Cost
    hardware: HardwareFit | None
    not_yet_measured: NotYetMeasured
    recheck: Recheck
    disclosures: Disclosures
    sources: dict[str, str]
    #: Display names by model ID, from the vocabulary; empty without one.
    names: dict[str, str] = Field(default_factory=dict)
    changes_since_r1: list[dict[str, Any]] | None = None


def schema() -> dict[str, Any]:
    body = Breakdown.model_json_schema(by_alias=True)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "title": "ModelSpec release breakdown",
        **body,
    }


def write_schema(path: Path = SCHEMA_PATH) -> Path:
    path.write_text(json.dumps(schema(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
