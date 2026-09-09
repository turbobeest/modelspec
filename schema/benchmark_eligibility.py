"""Strict records and the mechanical eligibility gate for benchmark evidence.

This validates the shape, dates, and coverage of submitted evidence.  It does
not establish that a source is truthful; that remains the reviewer's job.
"""

from __future__ import annotations

from datetime import date, datetime
from math import isfinite
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


def _text(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("must be a nonblank string")
    return value.strip()


def _date_value(value: object) -> object:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("must be an ISO date YYYY-MM-DD") from exc
        if parsed.isoformat() != value:
            raise ValueError("must be an exact ISO date YYYY-MM-DD")
        return parsed
    raise ValueError("must be an ISO date YYYY-MM-DD")


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Identity(StrictRecord):
    url: HttpUrl
    rationale: str = ""


class Usefulness(StrictRecord):
    verdict: Literal["useful", "saturated", "unknown"]
    rationale: str
    source_url: HttpUrl

    _rationale = field_validator("rationale")(_text)


class Result(StrictRecord):
    model_id: str
    benchmark_version: str
    configuration: str
    score: float
    unit: str
    source_url: HttpUrl
    evidence_date: date
    date_type: Literal["evaluated", "published"]
    verified_at: date
    source_kind: Literal["benchmark_author", "independent_evaluator", "model_provider"]

    _text_fields = field_validator("model_id", "benchmark_version", "configuration", "unit")(_text)
    _dates = field_validator("evidence_date", "verified_at", mode="before")(_date_value)

    @field_validator("score", mode="before")
    @classmethod
    def finite_score(cls, value: object) -> float:
        if isinstance(value, (bool, str)) or not isinstance(value, (int, float)):
            raise ValueError("score must be numeric")
        value = float(value)
        if not isfinite(value):
            raise ValueError("score must be finite")
        return value


class Review(StrictRecord):
    reviewer: str
    reviewed_at: date
    verdict: Literal["approved", "needs_work"]
    rationale: str

    _text_fields = field_validator("reviewer", "rationale")(_text)
    _date = field_validator("reviewed_at", mode="before")(_date_value)


class BenchmarkEvidence(StrictRecord):
    candidate_id: str
    canonical_id: str
    domain: str
    identity: Identity
    researcher: str
    task: str = ""
    metric: str = ""
    protocol: str = ""
    usefulness: Usefulness
    results: list[Result] = Field(default_factory=list)
    review: Review | None = None

    _text_fields = field_validator("candidate_id", "canonical_id", "domain", "researcher")(_text)


class ReferenceModel(StrictRecord):
    model_id: str
    organization: str
    domain: str
    cohort: Literal["frontier", "open"]
    openness: Literal["closed", "open_weight", "open_source"]
    source_url: HttpUrl
    rationale: str

    _text_fields = field_validator("model_id", "organization", "domain", "rationale")(_text)


class ModelReferenceSet(StrictRecord):
    as_of: date
    models: list[ReferenceModel] = Field(min_length=1)

    _date = field_validator("as_of", mode="before")(_date_value)

    @field_validator("models")
    @classmethod
    def unique_model_domains(cls, value: list[ReferenceModel]) -> list[ReferenceModel]:
        keys = [(model.model_id, model.domain) for model in value]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate reference model_id/domain")
        return value


class EligibilityRow(StrictRecord):
    candidate_id: str
    canonical_id: str
    status: Literal["active", "historical", "unverified", "alias"]
    reasons: list[str]
    accepted_results: list[dict[str, object]]
    source_evidence: list[str]


class EligibilityReport(StrictRecord):
    as_of: date
    active_ids: list[str]
    rows: list[EligibilityRow]
    mechanical_validation_note: str = (
        "Mechanical validation does not prove source truth; reviewer approval is required."
    )


def _age_days(as_of: date, evidence_date: date) -> int:
    return (as_of - evidence_date).days


def evaluate(
    evidence: BenchmarkEvidence, references: ModelReferenceSet, as_of: date
) -> EligibilityRow:
    """Evaluate one already parsed candidate against the reference set."""
    review_ok = evidence.review is not None and evidence.review.verdict == "approved"
    identity_known = bool(evidence.identity.rationale.strip())
    reasons: list[str] = []
    if not review_ok:
        reasons.append("review is not approved")
    if evidence.review is not None and evidence.review.reviewer == evidence.researcher:
        reasons.append("reviewer must be different from researcher")
    if not identity_known:
        reasons.append("identity is unknown")
    if not all((evidence.task.strip(), evidence.metric.strip(), evidence.protocol.strip())):
        reasons.append("task, metric, and protocol are incomplete")
    if evidence.usefulness.verdict == "unknown":
        reasons.append("usefulness is unknown")
    if evidence.usefulness.verdict == "saturated":
        reasons.append("benchmark is saturated")
    if evidence.usefulness.verdict != "useful" or not evidence.usefulness.rationale.strip():
        reasons.append("usefulness is not established")

    reference_fresh = references.as_of <= as_of and _age_days(as_of, references.as_of) <= 30
    if not reference_fresh:
        reasons.append("reference set is older than 30 days or future-dated")

    reference_by_id = {(model.model_id, model.domain): model for model in references.models}
    valid: list[tuple[Result, ReferenceModel]] = []
    stale: list[tuple[Result, ReferenceModel]] = []
    invalid: list[str] = []
    for result in evidence.results:
        model = reference_by_id.get((result.model_id, evidence.domain))
        if model is None:
            invalid.append(
                f"model {result.model_id} is absent from reference set for domain {evidence.domain}"
            )
            continue
        if result.evidence_date > as_of:
            invalid.append(f"result {result.model_id} has future evidence_date")
            continue
        if result.verified_at < result.evidence_date or result.verified_at > as_of:
            invalid.append(f"result {result.model_id} has invalid verified_at")
            continue
        if (
            evidence.review is None
            or evidence.review.reviewed_at < result.verified_at
            or evidence.review.reviewed_at > as_of
        ):
            invalid.append(f"result {result.model_id} predates review or has future review")
            continue
        if model.cohort == "open" and model.openness not in ("open_weight", "open_source"):
            invalid.append(f"open reference model {result.model_id} is not open")
            continue
        (stale if _age_days(as_of, result.evidence_date) > 60 else valid).append((result, model))

    reasons.extend(invalid)

    def groups(
        items: list[tuple[Result, ReferenceModel]],
    ) -> dict[tuple[str, str, str], list[tuple[Result, ReferenceModel]]]:
        grouped: dict[tuple[str, str, str], list[tuple[Result, ReferenceModel]]] = {}
        for result, model in items:
            key = (result.benchmark_version, result.configuration, result.unit)
            grouped.setdefault(key, []).append((result, model))
        return grouped

    def qualifying(
        items: list[tuple[Result, ReferenceModel]],
    ) -> list[tuple[Result, ReferenceModel]]:
        for group in groups(items).values():
            cohorts = {model.cohort for _, model in group}
            orgs = {model.organization for _, model in group}
            if {"frontier", "open"} <= cohorts and len(orgs) >= 2:
                return group
        return []

    accepted = qualifying(valid)
    all_coverage = qualifying(valid + stale)
    historical = all_coverage if not accepted or evidence.usefulness.verdict == "saturated" else []
    substantive = all(
        value.strip() for value in (evidence.task, evidence.metric, evidence.protocol)
    )
    review_dates_ok = evidence.review is not None and evidence.review.reviewed_at <= as_of
    full_identity_review = (
        review_ok
        and review_dates_ok
        and identity_known
        and (evidence.review is not None and evidence.review.reviewer != evidence.researcher)
    )
    if evidence.candidate_id != evidence.canonical_id:
        status = "alias" if full_identity_review and reference_fresh else "unverified"
    elif (
        accepted
        and full_identity_review
        and substantive
        and evidence.usefulness.verdict == "useful"
        and reference_fresh
    ):
        status = "active"
    elif (
        historical
        and full_identity_review
        and substantive
        and evidence.usefulness.verdict in ("useful", "saturated")
        and reference_fresh
    ):
        status = "historical"
    else:
        status = "unverified"
    if not accepted and status == "unverified":
        reasons.append("no qualifying current frontier/open coverage from different organizations")
    if historical and not accepted:
        reasons.append("qualifying coverage requires evidence older than 60 days")
    if status == "alias":
        reasons = [
            "independently reviewed alias; retain canonical benchmark and protocol distinctions"
        ]
    if status == "active":
        reasons.append("qualifying current coverage")
    accepted_for_report = accepted or historical
    if status == "unverified" or status == "alias":
        accepted_for_report = []
    attempted_sources = {
        str(evidence.identity.url),
        str(evidence.usefulness.source_url),
        *(str(r.source_url) for r in evidence.results),
    }
    return EligibilityRow(
        candidate_id=evidence.candidate_id,
        canonical_id=evidence.canonical_id,
        status=status,
        reasons=sorted(set(reasons)),
        accepted_results=[
            {
                "model_id": r.model_id,
                "benchmark_version": r.benchmark_version,
                "configuration": r.configuration,
                "unit": r.unit,
                "score": r.score,
                "evidence_date": r.evidence_date.isoformat(),
                "date_type": r.date_type,
                "verified_at": r.verified_at.isoformat(),
                "source_kind": r.source_kind,
                "source_url": str(r.source_url),
            }
            for r, _ in accepted_for_report
        ],
        source_evidence=sorted(attempted_sources),
    )
