"""MODEL-380 evidence and price reader regressions, using synthetic source text."""

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor
from scripts.accuracy import verify_fidelity_sample


TODAY = date(2026, 1, 3)
COLLECTOR = VerificationActor(
    agent="synthetic-collector", model_family="synthetic", method="synthetic@1"
)
SOURCE = SourceRef(
    source_id="synthetic-source",
    snapshot_ref="sha256:" + "0" * 64,
    cited_regions=["rows"],
)


class _Regions:
    def __init__(self, text: str) -> None:
        self._text = text

    def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
        return self._text


def _evidence_claim(*, value: float = 42.13) -> verify.Claim:
    return verify.Claim(
        target=TargetRef(kind="evidence", id="synthetic-model#synthetic-benchmark"),
        subject="synthetic/aurora",
        names=("Aurora",),
        field="synthetic_benchmark",
        label="pass_1",
        value=value,
        unit="percent",
        conditions={"effort": "max", "date": "2026-01-02"},
        collector=COLLECTOR,
        sources=(SOURCE,),
    )


def _read(claim: verify.Claim, text: str) -> verify.Result:
    return verify.verify(
        claim, _Regions(text), verify.deterministic_extractors(), today=TODAY
    )


def _fidelity(
    claim: verify.Claim, text: str, tmp_path: Path, unread_outcome: str | None = None,
):
    directory = tmp_path / "verification"
    return verify_fidelity_sample(
        [claim],
        regions=_Regions(text),
        extractors=verify.deterministic_extractors(),
        queue=verify.Queue(directory),
        log=verify.VerificationLog(directory),
        today=TODAY,
        source_urls={"synthetic-source": "https://source.example.test/rows"},
        unread={(claim.target.kind, claim.target.id): unread_outcome} if unread_outcome else None,
    )


def test_benchmark_raw_number_agrees_at_stored_precision() -> None:
    result = _read(
        _evidence_claim(),
        "Model: Aurora\npass_1: 42.13456789%\nEffort: max\nDate: 2026-01-02\n",
    )

    assert result.outcome == "verified"


def test_benchmark_key_value_reader_uses_explicit_source_unit() -> None:
    result = _read(
        _evidence_claim(),
        "Model: Aurora\npass_1: 42.13456789\nUnit: percent\n"
        "Effort: max\nDate: 2026-01-02\n",
    )

    assert result.outcome == "verified", result


@pytest.mark.parametrize("unread_outcome", [None, "mismatch"], ids=["changed", "unchanged"])
@pytest.mark.parametrize(
    "conditions",
    ["Date: 2026-01-02\n", "Effort: max\n", ""],
    ids=["missing-effort", "missing-date", "missing-both"],
)
def test_benchmark_missing_optional_conditions_has_no_determination(
    conditions: str, tmp_path: Path, unread_outcome: str | None,
) -> None:
    result = _fidelity(
        _evidence_claim(), "Model: Aurora\npass_1: 42.13456789%\n" + conditions,
        tmp_path, unread_outcome,
    )

    assert result.counts["undetermined"] == 1, result
    assert result.counts["mismatch"] == result.counts["verified"] == 0


@pytest.mark.parametrize("unread_outcome", [None, "mismatch"], ids=["changed", "unchanged"])
def test_benchmark_without_source_unit_has_no_determination(
    tmp_path: Path, unread_outcome: str | None,
) -> None:
    result = _fidelity(
        _evidence_claim(),
        "Model: Aurora\npass_1: 42.13456789\nEffort: max\nDate: 2026-01-02\n",
        tmp_path, unread_outcome,
    )

    assert result.counts["undetermined"] == 1, result
    assert result.counts["mismatch"] == result.counts["verified"] == 0


@pytest.mark.parametrize(
    "score,effort,date_,diff_field",
    [
        ("42.14%", "max", "2026-01-02", "value"),
        ("42.13456789%", "high", "2026-01-02", "effort"),
        ("42.13456789%", "max", "2026-01-01", "date"),
    ],
    ids=["changed-score", "changed-effort", "changed-date"],
)
def test_benchmark_stated_disagreement_remains_a_mismatch(
    score: str, effort: str, date_: str, diff_field: str
) -> None:
    result = _read(
        _evidence_claim(),
        f"Model: Aurora\npass_1: {score}\nEffort: {effort}\nDate: {date_}\n",
    )

    assert result.outcome == "mismatch"
    assert any(diff.field == diff_field for diff in result.diffs)


@pytest.mark.parametrize(
    "source_text,diff_field",
    [
        ("Model: Aurora\npass_1: 42.14%\n", "value"),
        ("Model: Aurora\npass_1: 42.13456789%\nEffort: high\n", "effort"),
        ("Model: Aurora\npass_1: 42.13456789%\nDate: 2026-01-01\n", "date"),
    ],
    ids=["changed-score", "changed-effort-missing-date", "changed-date-missing-effort"],
)
def test_benchmark_stated_disagreement_with_missing_metadata_is_a_mismatch(
    source_text: str, diff_field: str, tmp_path: Path,
) -> None:
    result = _fidelity(_evidence_claim(), source_text, tmp_path)

    assert result.counts["mismatch"] == 1, result
    assert result.counts["undetermined"] == result.counts["verified"] == 0
    assert any(diff["field"] == diff_field for diff in result.details[0]["diff"])


@pytest.mark.parametrize("unread_outcome", [None, "mismatch"], ids=["changed", "unchanged"])
@pytest.mark.parametrize("metadata", [{"interval": [41.9, 42.4]}, {"n": 120}])
def test_composite_benchmark_missing_optional_metadata_has_no_determination(
    metadata: dict, tmp_path: Path, unread_outcome: str | None,
) -> None:
    claim = replace(
        _evidence_claim(),
        label="accuracy",
        value={"score": 42.13, "interval": None, "n": None, "quality_flags": [], **metadata},
    )
    result = _fidelity(
        claim,
        '[{"model": "Aurora", "accuracy": 42.13456789, '
        '"effort": "max", "date": "2026-01-02"}]',
        tmp_path, unread_outcome,
    )

    assert result.counts["undetermined"] == 1, result
    assert result.counts["mismatch"] == result.counts["verified"] == 0


def _price_claim(field: str, value: float) -> verify.Claim:
    return verify.Claim(
        target=TargetRef(kind="fact", id=f"synthetic-offering#{field}"),
        subject="synthetic/aurora/api/standard",
        names=("Aurora",),
        field=f"offering.price.{field}",
        value=value,
        unit="usd_per_1m_tokens",
        collector=COLLECTOR,
        sources=(SOURCE,),
    )


SIBLING_PRICE_TABLE = """\
Borealis
Usage | Price per 1M tokens
Input | $7.50
Output | $12.00
Cached Input | $0.75
"""
OWN_PRICE_TABLE = """\
Aurora
Usage | Price per 1M tokens
Input | $2.50
Output | $6.00
Cached Input | $0.25
"""


@pytest.mark.parametrize(
    "field,value", [("input", 2.50), ("output", 6.00), ("cached_input", 0.25)]
)
def test_price_reader_selects_the_models_own_table(field: str, value: float) -> None:
    result = _read(_price_claim(field, value), SIBLING_PRICE_TABLE + "\n" + OWN_PRICE_TABLE)

    assert result.outcome == "verified", result


@pytest.mark.parametrize(
    "field,value", [("input", 7.50), ("output", 12.00), ("cached_input", 0.75)]
)
def test_price_reader_never_verifies_the_table_above_the_model(
    field: str, value: float,
) -> None:
    result = _read(_price_claim(field, value), SIBLING_PRICE_TABLE + "\n" + OWN_PRICE_TABLE)

    assert result.outcome == "mismatch", result
    assert any(diff.field == "value" for diff in result.diffs)


def test_price_reader_keeps_a_real_price_change_as_a_mismatch() -> None:
    result = _read(_price_claim("input", 2.49), SIBLING_PRICE_TABLE + "\n" + OWN_PRICE_TABLE)

    assert result.outcome == "mismatch"
    assert [diff.found for diff in result.diffs if diff.field == "value"] == [
        "2.50 usd_per_1m_tokens"
    ]


def test_price_reader_does_not_borrow_when_the_models_row_is_absent(tmp_path: Path) -> None:
    result = _fidelity(
        _price_claim("input", 7.50),
        SIBLING_PRICE_TABLE + "\nAurora\nUsage | Price per 1M tokens\nOutput | $6.00\n",
        tmp_path,
    )

    assert result.counts["undetermined"] == 1, result
    assert result.counts["mismatch"] == result.counts["verified"] == 0


@pytest.mark.parametrize(
    "text",
    [
        "Aurora\n" + SIBLING_PRICE_TABLE,
        "Models: Aurora 2\nUsage | Price per 1M tokens\nInput | $7.50\n",
    ],
    ids=["sibling-heading-before-first-table", "longer-sibling-in-model-list"],
)
def test_price_reader_requires_the_table_owners_exact_model(
    text: str, tmp_path: Path,
) -> None:
    result = _fidelity(_price_claim("input", 7.50), text, tmp_path)

    assert result.counts["undetermined"] == 1, result
    assert result.counts["mismatch"] == result.counts["verified"] == 0


@pytest.mark.parametrize(
    "source_text",
    [
        "Model: Aurora\npass_1: 42.13456789 ,\n",
        "Model: Aurora\npass_1: 42.13456789\nUnit: synthetic units\n",
    ],
    ids=["trailing-comma", "unknown-explicit-unit"],
)
def test_benchmark_unrecognized_source_unit_has_no_determination(
    source_text: str, tmp_path: Path,
) -> None:
    result = _fidelity(_evidence_claim(), source_text, tmp_path)

    assert result.counts["undetermined"] == 1, result
    assert result.counts["mismatch"] == result.counts["verified"] == 0


@pytest.mark.parametrize("source_unit", ["fraction", "tokens"])
def test_benchmark_stated_known_unit_disagreement_remains_a_mismatch(
    source_unit: str, tmp_path: Path,
) -> None:
    result = _fidelity(
        _evidence_claim(),
        f"Model: Aurora\npass_1: 42.13456789\nUnit: {source_unit}\n",
        tmp_path,
    )

    assert result.counts["mismatch"] == 1, result
    assert result.counts["undetermined"] == result.counts["verified"] == 0
    assert any(diff["field"] == "unit" for diff in result.details[0]["diff"])


def test_benchmark_unknown_unit_does_not_hide_a_stated_condition_disagreement(
    tmp_path: Path,
) -> None:
    result = _fidelity(
        _evidence_claim(), "Model: Aurora\npass_1: 42.13456789 ,\nEffort: high\n", tmp_path
    )

    assert result.counts["mismatch"] == 1, result
    assert result.counts["undetermined"] == result.counts["verified"] == 0
    assert any(diff["field"] == "effort" for diff in result.details[0]["diff"])
