"""Dated prices resolve once at build time and expire before the next rate."""

from copy import deepcopy
from datetime import date

import pytest
from pydantic import ValidationError

from decision import model as records
from decision.contract import parse_spec
from decision.engine import decide
from decision.model import Fact, Offering, value_hash
from decision.registry import default as default_registry
from decision.snapshot import (
    SnapshotBuildError,
    SnapshotError,
    SnapshotInputs,
    build_snapshot,
    load_snapshot_bytes,
)
from tests.snapshot_records import SOURCES, fact, model, offering, verification

MODEL = "lab/argon"
OFFERING = f"sambanova/{MODEL}/global/standard"
FACET = "offering.price.input"
REGISTRY = default_registry()


def dated_price(value, start=None, until=None, *, suffix="", model_id=MODEL):
    owner = f"sambanova/{model_id}/global/standard"
    row = fact("offering", owner, FACET, value, source="src-pricing")
    row["id"] += suffix
    if start is not None:
        row["effective_from"] = start
    if until is not None:
        row["effective_until"] = until
    expected = {"value": value, "effective_from": start, "effective_until": until}
    row["verification"] = verification("fact", row["id"], value=expected)
    return row


def schedule(*, model_id=MODEL):
    return [
        dated_price(2.0, "2026-10-14", "2026-11-30", suffix="@2026-10", model_id=model_id),
        dated_price(4.0, "2026-12-01", suffix="@2026-12", model_id=model_id),
    ]


def build(rows=None, *, as_of=date(2026, 11, 30), **overrides):
    inputs = {
        "models": [model(MODEL)],
        "offerings": [offering(MODEL, facts=schedule() if rows is None else rows)],
        "sources": SOURCES,
        **overrides,
    }
    return build_snapshot(SnapshotInputs(**inputs), registry=REGISTRY, as_of=as_of)


def load(built, *, include_archive=False):
    return load_snapshot_bytes(
        built.to_bytes(key=None, ed25519_signer=None),
        key=None,
        public_keys={},
        include_archive=include_archive,
    )


@pytest.mark.parametrize("day,expected,suffix", [
    (date(2026, 10, 14), 2.0, "@2026-10"),
    (date(2026, 11, 29), 2.0, "@2026-10"),
    (date(2026, 11, 30), 2.0, "@2026-10"),
    (date(2026, 12, 1), 4.0, "@2026-12"),
    (date(2027, 1, 1), 4.0, "@2026-12"),
])
def test_snapshot_resolves_exactly_one_price_on_its_as_of(day, expected, suffix):
    index = load(build(as_of=day))
    price = index.fact(OFFERING, FACET)
    assert price.value == expected
    assert price.record_id == f"{OFFERING}#{FACET}{suffix}"
    assert index.record(price.record_id)["verification"]["target"]["value_hash"] == value_hash({
        "value": expected,
        "effective_from": "2026-10-14" if expected == 2.0 else "2026-12-01",
        "effective_until": "2026-11-30" if expected == 2.0 else None,
    })


def test_offering_schema_accepts_a_contiguous_price_schedule():
    parsed = Offering.model_validate(offering(MODEL, facts=schedule()))
    assert [row.effective_from for row in parsed.facts] == [
        date(2026, 10, 14), date(2026, 12, 1),
    ]
    assert parsed.facts[0].effective_until == date(2026, 11, 30)


def test_snapshot_requires_as_of_for_scheduled_prices():
    with pytest.raises(SnapshotBuildError, match="as_of"):
        build(as_of=None)


@pytest.mark.parametrize("rows,reason", [
    ([dated_price(2, "2026-10-14", "2026-12-01", suffix="a"),
      dated_price(4, "2026-12-01", suffix="b")], "overlap"),
    ([dated_price(2, "2026-10-14", "2026-11-29", suffix="a"),
      dated_price(4, "2026-12-01", suffix="b")], "gap"),
    ([dated_price(2, "2026-10-14", suffix="a"),
      dated_price(4, "2026-12-01", suffix="b")], "overlap"),
    ([fact("offering", OFFERING, FACET, 2, source="src-pricing"),
      dated_price(4, "2026-12-01", suffix="b")], "mixed"),
    ([dated_price(2, "2026-12-01", "2026-11-30")], "before"),
    ([dated_price(2, "2026-11-31")], "date"),
    ([dated_price(2, "20261201")], "date"),
    ([dated_price(2, "2026-12-01T00:00:00")], "date"),
])
@pytest.mark.parametrize("boundary", ["schema", "builder"])
def test_invalid_schedules_are_rejected_at_both_input_boundaries(rows, reason, boundary):
    error = ValidationError if boundary == "schema" else SnapshotBuildError
    with pytest.raises(error, match=reason):
        if boundary == "schema":
            Offering.model_validate(offering(MODEL, facts=rows))
        else:
            build(rows)


@pytest.mark.parametrize("changes", [
    {"value": -1},
    {"value": "not_offered"},
    {"value": True},
    {"state": "unknown", "value": None},
    {"facet": "offering.api_model_id", "value": "argon"},
    {"subject": {"kind": "model", "id": MODEL}, "facet": "model.context_window", "value": 2},
])
def test_dates_are_only_valid_for_known_numeric_nonnegative_offering_prices(changes):
    row = dated_price(2, "2026-12-01")
    row.update(changes)
    row.pop("verification", None)
    with pytest.raises(ValidationError, match="dated|scheduled|price"):
        Fact.model_validate(row)
    with pytest.raises(SnapshotBuildError, match="dated|scheduled|price"):
        build([row], as_of=date(2026, 12, 1))


def test_date_changes_invalidate_the_schema_verification_target():
    row = dated_price(2, "2026-10-14", "2026-11-30")
    row["effective_until"] = "2026-12-01"
    with pytest.raises(ValidationError, match="value_hash"):
        Fact.model_validate(row)


def test_date_changes_cannot_admit_a_price_using_an_old_verification():
    row = dated_price(2, "2026-10-14", "2026-11-30")
    row["effective_until"] = "2026-12-01"
    index = load(build([row]))
    assert index.fact(OFFERING, FACET).state == "unknown"
    assert index.excluded["quarantined"] == 1


def test_fact_verification_value_keeps_legacy_hashes_and_binds_dates():
    legacy = fact("offering", OFFERING, FACET, 2, source="src-pricing")
    assert records.fact_verification_value(legacy) == 2
    scheduled = dated_price(2, "2026-10-14", "2026-11-30")
    expected = {"value": 2, "effective_from": "2026-10-14", "effective_until": "2026-11-30"}
    assert records.fact_verification_value(scheduled) == expected
    assert records.fact_verification_value(Fact.model_validate(scheduled)) == expected


def test_snapshot_refuses_to_cross_the_price_boundary_while_stale():
    built = build()
    assert built.content["valid_from"] == "2026-10-14"
    assert built.content["valid_until"] == "2026-12-01"
    index = load(built)
    index.require_current(date(2026, 11, 30))
    with pytest.raises(SnapshotError, match="expired|valid_until|2026-12-01"):
        index.require_current(date(2026, 12, 1))
    # Historical loads retain the price selected when the snapshot was built.
    assert index.fact(OFFERING, FACET).value == 2


def test_future_snapshot_refuses_to_serve_before_its_price_takes_effect():
    index = load(build(as_of=date(2026, 12, 1)))
    assert index.valid_from == date(2026, 12, 1)
    assert index.valid_until is None
    with pytest.raises(SnapshotError, match="not yet|before|valid_from"):
        index.require_current(date(2026, 11, 30))
    index.require_current(date(2026, 12, 1))


def test_a_missing_next_price_row_cannot_extend_the_old_price():
    rows = schedule()[:1]
    index = load(build(rows))
    with pytest.raises(SnapshotError, match="expired|valid_until|2026-12-01"):
        index.require_current(date(2026, 12, 1))
    with pytest.raises(SnapshotBuildError, match="no.*price|no.*entry|does not cover"):
        build(rows, as_of=date(2026, 12, 1))


def test_a_quarantined_future_price_cannot_extend_the_old_price():
    rows = schedule()
    rows[1]["verification"]["outcome"] = "mismatch"
    rows[1]["verification"]["diff"] = "the future row did not match"
    index = load(build(rows))
    assert index.fact(OFFERING, FACET).value == 2
    with pytest.raises(SnapshotError, match="expired|2026-12-01"):
        index.require_current(date(2026, 12, 1))
    next_index = load(build(rows, as_of=date(2026, 12, 1)))
    assert next_index.fact(OFFERING, FACET).state == "unknown"


def test_snapshot_validity_intersects_all_selected_price_periods():
    rows = schedule()
    output = dated_price(10, "2026-11-01", "2026-11-30", suffix="output")
    output["facet"] = "offering.price.output"
    rows.append(output)
    index = load(build(rows))
    assert index.valid_from == date(2026, 11, 1)
    assert index.valid_until == date(2026, 12, 1)


def test_out_of_lineup_prices_do_not_expire_the_live_snapshot():
    outside = "lab/outside"
    outside_rows = [dated_price(1, "2026-10-14", "2026-11-30", model_id=outside)]
    models = [model(MODEL), model(outside)]
    offerings = [
        offering(MODEL),
        offering(outside, facts=outside_rows),
    ]
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, sources=SOURCES),
        registry=REGISTRY, premier=[MODEL], gate=False, as_of=date(2026, 11, 30),
    )
    assert "valid_from" not in built.content
    assert "valid_until" not in built.content
    load(built).require_current(date(2026, 12, 1))


def test_an_expired_archived_price_cannot_answer_a_current_retired_model_request():
    retired = "lab/retired"
    owner = f"sambanova/{retired}/global/standard"
    rows = [
        dated_price(1, until="2000-01-01", suffix="before", model_id=retired),
        dated_price(9, "2000-01-02", suffix="after", model_id=retired),
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[model(MODEL), model(retired, lifecycle="retired", facts=[
                fact("model", retired, "model.lifecycle", "retired"),
            ])],
            offerings=[offering(retired, facts=rows)],
            sources=SOURCES,
        ),
        registry=REGISTRY, as_of=date(2000, 1, 1),
    )
    index = load(built, include_archive=True)
    spec = parse_spec({
        "spec_version": 1,
        "where": ["model.lifecycle = retired"],
        "optimize": {"min": FACET},
        "explain": "full",
    }, facets=REGISTRY.facet)
    with pytest.raises(SnapshotError, match="expired"):
        decide(spec, index, facets=REGISTRY.facet)
    assert built.content["valid_until"] == "2000-01-02"
    historical = decide(spec, index, facets=REGISTRY.facet, _validate_current=False)
    assert [row.offering.model for row in historical.results] == [retired]
    assert index.fact(owner, FACET).value == 1


@pytest.mark.parametrize("owner", ["model", "another_offering"])
def test_dated_price_facts_must_belong_to_their_actual_snapshot_owner(owner):
    row = dated_price(2, "2026-10-14", "2026-11-30")
    if owner == "model":
        inputs = SnapshotInputs(models=[model(MODEL, facts=[row])], sources=SOURCES)
    else:
        row["subject"]["id"] = "sambanova/lab/another/global/standard"
        inputs = SnapshotInputs(
            models=[model(MODEL)], offerings=[offering(MODEL, facts=[row])], sources=SOURCES,
        )
    with pytest.raises(SnapshotBuildError, match="owner|subject|metered offering"):
        build_snapshot(inputs, registry=REGISTRY, as_of=date(2026, 11, 30))


def test_undated_snapshots_have_no_new_validity_keys_and_do_not_expire():
    built = build([fact("offering", OFFERING, FACET, 2, source="src-pricing")])
    assert "valid_from" not in built.content
    assert "valid_until" not in built.content
    index = load(built)
    index.require_current(date(2099, 1, 1))
    assert index.fact(OFFERING, FACET).value == 2


def test_schedule_entry_order_does_not_change_snapshot_bytes():
    rows = schedule()
    assert build(rows).to_bytes(key=None, ed25519_signer=None) == build(
        list(reversed(deepcopy(rows)))
    ).to_bytes(key=None, ed25519_signer=None)


def test_native_yaml_dates_build_the_same_snapshot_as_iso_strings():
    rows = schedule()
    for row in rows:
        for key in ("effective_from", "effective_until"):
            if key in row:
                row[key] = date.fromisoformat(row[key])
    original = deepcopy(rows)
    records.validate_price_schedules(rows)
    assert build(rows).to_bytes(key=None, ed25519_signer=None) == build().to_bytes(
        key=None, ed25519_signer=None,
    )
    assert rows == original
