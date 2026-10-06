"""Residency filters follow the countries a provider region name guarantees."""

from __future__ import annotations

import copy

import pytest

from decision.contract import parse_spec
from decision.engine import decide
from decision.explain import render_html
from decision.filter import apply as filter_apply
from decision.registry import facet as facets
from decision.resolve import resolve
from decision.snapshot import (
    FactValue,
    LoadedSnapshot,
    SnapshotError,
    SnapshotInputs,
    build_snapshot,
    load_built_snapshot,
)
from decision.why_not import why_not
from tests.snapshot_records import SOURCES, fact, model

GLOBAL_REASON = "provider region 'global' does not guarantee where inference runs"
EU_MEMBERS = (
    "offering.region in {AT, BE, BG, CY, CZ, DE, DK, EE, ES, FI, FR, GR, HR, "
    "HU, IE, IT, LT, LU, LV, MT, NL, PL, PT, RO, SE, SI, SK}"
)


def _offering(mid: str, region: str) -> dict:
    oid = f"lab-api/{mid}/{region}/standard"
    return {
        "model": mid,
        "provider": "lab-api",
        "region": region,
        "tier": "standard",
        "facts": [fact("offering", oid, "offering.price.input", 3.0, source="src-pricing")],
    }


def index_of(regions: list[tuple[str, str]]):
    """One model and one offering per ``(slug, region)``."""
    models, offerings = [], []
    for slug, region in regions:
        mid = f"lab/{slug}"
        models.append(model(mid))
        offerings.append(_offering(mid, region))
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, sources=SOURCES),
        gate=False,
    )
    return load_built_snapshot(built, include_archive=True, source="region test")


def _spec(where: str):
    return parse_spec(
        {
            "spec_version": 1,
            "where": [where],
            "optimize": {"max": "model.context_window"},
            "explain": "full",
        },
        facets=facets,
    )


def _filter(index, where: str):
    return filter_apply(resolve(_spec(where), facets=facets), index)


def test_a_region_filter_matches_a_documented_country_and_its_iso_code() -> None:
    index = index_of([
        ("sg-name", "singapore"),
        ("sg-code", "SG"),
        ("de", "DE"),
        ("global", "global"),
    ])
    decision = decide(_spec("offering.region in {SG}"), index, facets=facets)

    ranked = {row.offering.model: row.offering.region for row in decision.results}
    assert ranked == {"lab/sg-name": "singapore", "lab/sg-code": "SG"}

    eliminated = {row.model: row for row in decision.eliminated.models}
    assert eliminated["lab/de"].value == "DE"
    assert eliminated["lab/de"].condition == "offering.region in {SG}"
    assert "unverified" not in eliminated["lab/de"].condition
    assert "lab/de" not in {row.model for row in decision.may_qualify}

    (maybe,) = [row for row in decision.may_qualify if row.model == "lab/global"]
    assert maybe.unknown == ["offering.region"]
    assert "lab/global" not in ranked
    assert "lab/global" not in eliminated

    by_model = next(row for row in decision.by_model if row.model == "lab/global")
    assert by_model.status == "may_qualify"
    assert by_model.offerings[0].reason == GLOBAL_REASON
    assert by_model.offerings[0].unknown == ["offering.region"]

    answer = why_not(decision, "lab/global")
    assert answer.verdict == "may_qualify"
    assert answer.failed == []
    assert answer.unknown == ["offering.region"]
    assert answer.summary == (
        "lab/global may qualify but is not ranked: "
        "provider region 'global' does not guarantee where inference runs. "
        "Unknown is never ranked last and never dropped."
    )
    html = render_html(decision, index)
    assert (
        "lab/global may qualify; unknown: offering.region. "
        "provider region &#x27;global&#x27; does not guarantee where inference runs"
    ) in html


def test_filter_lists_a_global_offering_as_may_qualify() -> None:
    index = index_of([("global", "global")])
    oid = "lab-api/lab/global/global/standard"
    result = _filter(index, "offering.region in {SG}")
    assert result.feasible == ()
    assert [row.candidate for row in result.may_qualify] == [oid]
    assert result.may_qualify[0].unknown == ("offering.region",)
    assert oid not in [row.candidate for row in result.eliminated]

    known = _filter(index, "known(offering.region)")
    assert known.feasible == (oid,)
    assert known.may_qualify == ()


def test_singapore_outside_the_requested_set_fails() -> None:
    index = index_of([("sg-name", "singapore"), ("de", "DE")])
    result = _filter(index, "offering.region in {DE}")
    eliminated = {row.candidate: row for row in result.eliminated}
    singapore = eliminated["lab-api/lab/sg-name/singapore/standard"]
    assert singapore.value == "singapore"
    assert singapore.unverified is False
    assert singapore.condition == "offering.region in {DE}"
    assert result.may_qualify == ()
    assert result.feasible == ("lab-api/lab/de/DE/standard",)


def test_not_in_on_a_global_offering_stays_unknown() -> None:
    index = index_of([("global", "global")])
    oid = "lab-api/lab/global/global/standard"
    result = _filter(index, "offering.region not in {DE}")
    assert result.feasible == ()
    assert [row.candidate for row in result.may_qualify] == [oid]
    assert result.may_qualify[0].unknown == ("offering.region",)
    assert oid not in [row.candidate for row in result.eliminated]


def test_the_eu_member_set_matches_de_and_fails_singapore() -> None:
    index = index_of([("de", "DE"), ("sg-name", "singapore")])
    result = _filter(index, EU_MEMBERS)
    assert result.feasible == ("lab-api/lab/de/DE/standard",)
    assert result.may_qualify == ()
    (singapore,) = result.eliminated
    assert singapore.candidate == "lab-api/lab/sg-name/singapore/standard"
    assert singapore.value == "singapore"
    assert singapore.unverified is False
    assert singapore.condition == EU_MEMBERS


def test_contains_all_of_de_and_fr_fails_a_single_country_de_offering() -> None:
    index = index_of([("de", "DE")])
    bits = index.ids_where("offering.region", "contains_all", ["DE", "FR"])
    assert index.ids(bits.passing) == ()
    assert index.ids(bits.failing) == ("lab-api/lab/de/DE/standard",)
    assert index.ids(bits.unknown) == ("lab/de",)


def test_a_missing_region_fact_is_an_unverified_governance_fail() -> None:
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/row")],
            offerings=[_offering("lab/row", "DE")],
            sources=SOURCES,
        ),
        gate=False,
    )
    envelope = copy.deepcopy(built.envelope(None))
    for section_name in ("lineup", "archive"):
        column = envelope["content"][section_name]["facets"].get("offering.region")
        if column is None:
            continue
        column["state"] = ["unknown"] * len(column["state"])
        column["value"] = [None] * len(column["value"])
    index = LoadedSnapshot(envelope, include_archive=True, signature_verified=False)
    oid = "lab-api/lab/row/DE/standard"
    assert index.fact(oid, "offering.region") == FactValue("unknown")

    result = _filter(index, "offering.region in {SG}")
    assert result.feasible == ()
    assert result.may_qualify == ()
    (row,) = result.eliminated
    assert row.candidate == oid
    assert row.unverified is True
    assert row.value is None
    assert row.surface == "unverified: may qualify"
    assert row.condition == "offering.region in {SG}"


def test_a_region_gap_inside_all_stays_may_qualify_beside_another_unknown() -> None:
    index = index_of([("global", "global")])
    oid = "lab-api/lab/global/global/standard"
    result = _filter(
        index, "all(offering.region in {SG}; offering.price.output >= 0)",
    )
    assert result.feasible == ()
    assert result.eliminated == ()
    assert [(row.candidate, row.unknown) for row in result.may_qualify] == [
        (oid, ("offering.region", "offering.price.output")),
    ]


def test_a_region_gap_inside_all_still_fails_on_another_governance_unknown() -> None:
    index = index_of([("global", "global")])
    oid = "lab-api/lab/global/global/standard"
    where = "all(offering.region in {SG}; offering.data.trains_on_customer_data = false)"
    result = _filter(index, where)
    assert result.feasible == ()
    assert result.may_qualify == ()
    (row,) = result.eliminated
    assert row.candidate == oid
    assert row.unverified is True
    assert row.value is None
    assert row.surface == "unverified: may qualify"
    assert row.condition == where


@pytest.mark.parametrize("region", [
    "global", "global-short-context", "global-cross-region",
])
def test_a_global_variant_does_not_pass_or_fail_a_region_filter(region: str) -> None:
    index = index_of([("row", region)])
    oid = f"lab-api/lab/row/{region}/standard"
    result = _filter(index, "offering.region in {SG}")
    assert result.feasible == ()
    assert [row.candidate for row in result.may_qualify] == [oid]
    assert oid not in [row.candidate for row in result.eliminated]

    decision = decide(_spec("offering.region in {SG}"), index, facets=facets)
    (maybe,) = decision.may_qualify
    assert maybe.model == "lab/row"
    assert maybe.unknown == ["offering.region"]
    assert decision.results == []
    answer = why_not(decision, "lab/row")
    assert answer.verdict == "may_qualify"
    assert answer.failed == []
    assert answer.summary == (
        "lab/row may qualify but is not ranked: "
        f"provider region {region!r} does not guarantee where inference runs. "
        "Unknown is never ranked last and never dropped."
    )


def test_the_snapshot_refuses_an_unknown_region_name() -> None:
    inputs = SnapshotInputs(
        models=[model("lab/world")],
        offerings=[_offering("lab/world", "atlantis")],
        sources=SOURCES,
    )
    with pytest.raises(SnapshotError, match="atlantis"):
        build_snapshot(inputs, gate=False)

    with pytest.raises(SnapshotError, match="globalfoo"):
        build_snapshot(
            SnapshotInputs(
                models=[model("lab/world")],
                offerings=[_offering("lab/world", "globalfoo")],
                sources=SOURCES,
            ),
            gate=False,
        )

    with pytest.raises(SnapshotError, match="global-eu"):
        build_snapshot(
            SnapshotInputs(
                models=[model("lab/world")],
                offerings=[_offering("lab/world", "global-eu")],
                sources=SOURCES,
            ),
            gate=False,
        )


def test_a_loaded_snapshot_refuses_an_unknown_region_name() -> None:
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/world")],
            offerings=[_offering("lab/world", "global")],
            sources=SOURCES,
        ),
        gate=False,
    )
    envelope = built.envelope(None)

    renamed = copy.deepcopy(envelope)
    offering = next(
        cand for cand in renamed["content"]["lineup"]["candidates"] if cand["kind"] == "offering"
    )
    offering["id"] = offering["id"].replace("/global/", "/atlantis/")
    with pytest.raises(SnapshotError, match="atlantis"):
        LoadedSnapshot(renamed, include_archive=True, signature_verified=False)

    rewritten = copy.deepcopy(envelope)
    column = rewritten["content"]["lineup"]["facets"]["offering.region"]
    column["value"] = ["atlantis" if value == "global" else value for value in column["value"]]
    with pytest.raises(SnapshotError, match="atlantis"):
        LoadedSnapshot(rewritten, include_archive=True, signature_verified=False)
