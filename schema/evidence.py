"""Benchmark evidence shared by model cards and decision records."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class BenchmarkEvidence(BaseModel):
    """One score, with everything needed to check it.

    The flat `scores` dict below carries one collection date for a whole card
    and a comma-joined source list, so no individual number can be attributed,
    dated or rechecked. This record is the shape the benchmark catalogue's
    evidence contract requires, and it mirrors the census evidence ledger so the
    two can be reconciled rather than diverging.

    Every field here is required. A record that cannot say where a number came
    from or when is not evidence, and admitting a partial one would quietly
    reintroduce exactly the problem this replaces.
    """

    benchmark_id: str
    model_id_as_evaluated: str
    score: float
    unit: str
    source_url: str
    #: benchmark author, independent evaluator, or the provider's own claim.
    #: Provider self-report is legitimate and must be visibly distinguishable.
    source_kind: Literal["benchmark_author", "independent_evaluator", "provider_self_report"]
    evidence_date: str
    #: `evaluated` when the run date is disclosed; `published` when only the
    #: publication date is. Never infer a run date from a retrieval timestamp.
    date_type: Literal["evaluated", "published"]
    verified_at: str
    benchmark_version: str = ""
    configuration: str = ""
    limitations: str = ""
    #: A published uncertainty interval on the same scale as ``score``.
    interval: tuple[float, float] | None = None
    #: The published observation count behind the measurement, when disclosed.
    n: int | None = Field(default=None, ge=1)
    #: Structured reasons this measurement is not a clean direct answer.
    quality_flags: list[Literal["deprecated", "contamination_warning"]] = Field(
        default_factory=list
    )

    @field_validator("source_url")
    @classmethod
    def _url_must_be_real(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("source_url must be a URL; a score without one is not evidence")
        return value

    @field_validator("evidence_date", "verified_at")
    @classmethod
    def _dates_must_be_iso(cls, value: str) -> str:
        from datetime import date as _date
        try:
            _date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"must be an exact ISO date YYYY-MM-DD, got {value!r}") from exc
        return value

    @model_validator(mode="after")
    def _valid_uncertainty_and_quality(self) -> BenchmarkEvidence:
        if self.interval is not None:
            low, high = self.interval
            if not all(float("-inf") < value < float("inf") for value in (low, high)):
                raise ValueError("interval bounds must be finite")
            if low > high:
                raise ValueError("interval lower bound must not exceed the upper bound")
            if not low <= self.score <= high:
                raise ValueError("evidence score must fall within its interval")
        if len(self.quality_flags) != len(set(self.quality_flags)):
            raise ValueError("quality_flags must not contain duplicates")
        return self


