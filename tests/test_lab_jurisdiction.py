"""Lab jurisdiction is recorded once per lab and inherited (MODEL-344)."""

from __future__ import annotations

from datetime import date

import pytest

from decision.compare import _condition_facet
from decision.contract import parse_spec
from decision.engine import decide
from decision.filter import strip_unverified_condition
from decision.labs import FACET, Lab, LabRegistryError, load_labs
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.registry import facet as facets
from decision.snapshot import (
    CompletenessError,
    SnapshotBuildError,
    SnapshotInputs,
    build_snapshot,
    load_built_snapshot,
)
from decision.verify import Claim, LabJurisdictionExtractor, compare, jurisdiction_codes
from tests.snapshot_records import SOURCES, fact, model, offering, verification

READ = "2026-10-08"
SOURCE = {
    "source_id": "src-lab-docs",
    "snapshot_ref": "sha256:" + "ab" * 32,
    "cited_regions": ["r1"],
}


def _lab(lab_id: str, codes: list[str] | None, *, state: str = "known", note: str = "Read the filing.") -> Lab:
    return Lab(
        id=lab_id,
        entity="Lab Inc." if state == "known" else None,
        parent_entity=None,
        note=note,
        read_date=READ,
        state=state,
        value=tuple(codes) if codes else None,
        sources=(dict(SOURCE),),
    )


def _claim(value: list[str], text_name: str = "Lab Inc.") -> Claim:
    return Claim(
        target=TargetRef(kind="fact", id="lab:google#origin.lab_jurisdiction"),
        subject="lab:google",
        names=(text_name,),
        field=FACET,
        value=value,
        collector=VerificationActor(agent="grok", model_family="grok", method="lab-registry@1"),
        sources=(SourceRef.model_validate(SOURCE),),
    )


def test_delaware_and_the_sec_state_field_read_as_us() -> None:
    page = "Google LLC is a Delaware limited liability company."
    filing = '{"stateOfIncorporation": "DE", "name": "Alphabet Inc."}'
    assert jurisdiction_codes(page) == frozenset({"US"})
    assert jurisdiction_codes(filing) == frozenset({"US"})
    readings = LabJurisdictionExtractor().extract(_claim(["US"]), page)
    assert compare(_claim(["US"]), readings) == []


def test_cayman_and_china_are_both_read_when_the_page_states_both() -> None:
    text = (
        "Alibaba Group Holding Limited was incorporated in the Cayman Islands. "
        "A subsidiary was incorporated in the People's Republic of China."
    )
    assert jurisdiction_codes(text) == frozenset({"CN", "KY"})
    assert compare(_claim(["KY", "CN"]), LabJurisdictionExtractor().extract(_claim(["KY", "CN"]), text)) == []


def test_a_headquarters_mention_is_not_incorporation() -> None:
    text = "The company is headquartered in China and has an office in the United States."
    assert jurisdiction_codes(text) == frozenset()
    assert LabJurisdictionExtractor().extract(_claim(["CN"]), text) == []


def test_governing_law_and_entity_form_are_not_the_same_thing() -> None:
    assert jurisdiction_codes(
        "This agreement is governed by the laws of the State of Delaware."
    ) == frozenset()
    assert jurisdiction_codes("governed by the laws of the state of California") == frozenset()
    assert jurisdiction_codes("SpaceXAI LLC is a Nevada company.") == frozenset({"US"})
    assert jurisdiction_codes(
        "Anthropic is a Delaware public benefit corporation."
    ) == frozenset({"US"})
    assert jurisdiction_codes("Jina AI GmbH") == frozenset({"DE"})
    assert jurisdiction_codes("Moonshot AI PTE. LTD.") == frozenset({"SG"})
    assert jurisdiction_codes(
        '"stateOfIncorporationDescription": "Cayman Islands"'
    ) == frozenset({"KY"})
    assert jurisdiction_codes('"stateOfIncorporationDescription": "DE"') == frozenset({"US"})
    assert jurisdiction_codes("Cayman Islands") == frozenset({"KY"})
    assert jurisdiction_codes(
        "OpenAI Ireland Ltd, a company incorporated in the Republic of Ireland"
    ) == frozenset({"IE"})


def test_a_parent_label_is_read_without_its_subsidiaries() -> None:
    from decision.normalise import NORMALISERS, Locator, normalise_document, select_region

    html = (
        '<ul class="structure-list"><li>Bytedance Ltd. (Cayman)'
        "<ul><li>Nuverse Pte. Ltd.</li></ul></li></ul>"
    )
    doc = normalise_document(html.encode(), NORMALISERS["html-default"])
    region = select_region(doc, Locator("css", "ul.structure-list > li::own"))
    assert region == "Bytedance Ltd. (Cayman)"
    assert jurisdiction_codes(region or "") == frozenset({"KY"})
    whole = select_region(doc, Locator("css", "ul.structure-list"))
    assert jurisdiction_codes(whole or "") == frozenset({"KY", "SG"})


def test_a_missing_registry_loads_as_empty(tmp_path) -> None:
    assert load_labs(tmp_path) == {}


def test_an_explicit_null_without_a_source_is_refused(tmp_path) -> None:
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "labs.yaml").write_text(
        "schema_version: 1\n"
        "labs:\n"
        "  - id: infgrad\n"
        "    note: no page states it\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction: {state: not_disclosed, value: null, sources: []}\n",
        encoding="utf-8",
    )
    with pytest.raises(LabRegistryError):
        load_labs(tmp_path)


def test_a_model_inherits_its_labs_verified_jurisdiction() -> None:
    lab = _lab("google", ["US"])
    built = build_snapshot(
        SnapshotInputs(
            models=[model("google/gemma", facts=[
                fact("model", "google/gemma", "model.weights_openness", "open_weights"),
                fact("model", "google/gemma", FACET, None, state="not_disclosed", outcome=None),
            ])],
            sources=SOURCES,
            verifications=[verification("fact", lab.fact()["id"], value=["US"])],
            labs={"google": lab},
        ),
        gate=False,
    )
    index = load_built_snapshot(built, source="inherit")
    fact_value = index.fact("google/gemma", FACET)
    assert fact_value.state == "known"
    assert fact_value.value == ["US"]
    assert fact_value.record_id == "lab:google#origin.lab_jurisdiction"


def test_a_disagreeing_model_value_fails_the_build() -> None:
    lab = _lab("qwen", ["KY"])
    with pytest.raises(SnapshotBuildError, match="disagrees"):
        build_snapshot(
            SnapshotInputs(
                models=[model("qwen/qwen", facts=[
                    fact("model", "qwen/qwen", "model.weights_openness", "open_weights"),
                    fact("model", "qwen/qwen", FACET, ["US"]),
                ])],
                sources=SOURCES,
                verifications=[verification("fact", lab.fact()["id"], value=["KY"])],
                labs={"qwen": lab},
            ),
            gate=False,
        )


def test_an_explicit_sourced_null_is_not_a_jurisdiction_gap() -> None:
    present = _lab("google", ["US"])
    absent = _lab("infgrad", None, state="not_disclosed", note="The imprint does not state incorporation.")
    try:
        build_snapshot(
            SnapshotInputs(
                models=[
                    model("google/gemma"),
                    model("infgrad/stella"),
                ],
                sources=SOURCES,
                verifications=[verification("fact", present.fact()["id"], value=["US"])],
                labs={"google": present, "infgrad": absent},
            ),
            premier=["google/gemma", "infgrad/stella"],
            registry=__import__("decision.registry", fromlist=["default"]).default(),
        )
    except CompletenessError as exc:
        gaps = [gap for gap in exc.gaps if gap.facet == FACET]
    else:
        gaps = []
    assert gaps == []


def test_a_registered_lab_without_a_known_value_is_a_gap() -> None:
    lab = _lab("qwen", ["KY"])
    with pytest.raises(CompletenessError) as exc:
        build_snapshot(
            SnapshotInputs(
                models=[model("qwen/qwen")],
                sources=SOURCES,
                labs={"qwen": lab},
            ),
            premier=["qwen/qwen"],
            registry=__import__("decision.registry", fromlist=["default"]).default(),
        )
    assert any(gap.facet == FACET and gap.model == "qwen/qwen" for gap in exc.value.gaps)


def test_an_eliminated_governance_row_names_the_facet_and_unknown_list() -> None:
    built = build_snapshot(
        SnapshotInputs(
            models=[model("qwen/qwen")],
            offerings=[offering("qwen/qwen", "deepinfra")],
            sources=SOURCES,
        ),
        gate=False,
        as_of=date(2026, 10, 8),
    )
    index = load_built_snapshot(built, source="reason")
    spec = parse_spec(
        {
            "spec_version": 1,
            "access": {"kind": "own_hardware"},
            "where": ["origin.lab_jurisdiction in {US}"],
            "optimize": {"max": "model.context_window"},
            "explain": "full",
        },
        facets=facets,
    )
    decision = decide(spec, index, facets=facets)
    rows = [row for row in decision.eliminated.models if row.model == "qwen/qwen"]
    note = ": eliminated: Lab jurisdiction not verified; unknown(list)"
    assert rows
    assert all(row.condition.endswith(note) for row in rows)
    assert _condition_facet(rows[0].condition) == FACET
    group = next(g for g in decision.eliminated.model_groups if g.model == "qwen/qwen")
    assert group.model_elimination is not None
    assert group.model_elimination.condition.endswith(note)


def test_a_capability_unknown_keeps_the_may_qualify_note() -> None:
    closed = model("lab/closed", facts=[
        fact("model", "lab/closed", "model.weights_openness", "open_weights"),
        fact("model", "lab/closed", "model.context_window", None, state="not_disclosed", outcome=None),
        fact("model", "lab/closed", "model.input_modalities", ["text"]),
        fact("model", "lab/closed", "licence.user_cap", "unbounded"),
    ])
    built = build_snapshot(
        SnapshotInputs(models=[closed], sources=SOURCES),
        gate=False,
        as_of=date(2026, 10, 8),
    )
    index = load_built_snapshot(built, source="capability")
    spec = parse_spec(
        {
            "spec_version": 1,
            "where": ["model.context_window >= 1 unknown(fail)"],
            "optimize": {"max": "model.context_window"},
            "explain": "full",
        },
        facets=facets,
    )
    decision = decide(spec, index, facets=facets)
    rows = [row.condition for row in decision.eliminated.models if row.model == "lab/closed"]
    matched = next(row for row in rows if row.endswith(": unverified: may qualify"))
    assert _condition_facet(matched) == "model.context_window"


def test_strip_unverified_condition_removes_both_notes() -> None:
    governance = "origin.lab_jurisdiction in {US}: eliminated: Lab jurisdiction not verified; unknown(list)"
    capability = "model.weights_openness = open_weights: unverified: may qualify"
    assert strip_unverified_condition(governance) == "origin.lab_jurisdiction in {US}"
    assert strip_unverified_condition(capability) == "model.weights_openness = open_weights"


def test_display_has_data_follows_lineup_counts() -> None:
    from api.worker.src.display_vocabulary import trim

    vocabulary = {
        "vocabulary_version": 1,
        "facets": [{
            "id": FACET,
            "label": "Lab jurisdiction",
            "definition": "where",
            "subject": "model",
            "value_type": "set",
            "unit": None,
            "unit_definition": None,
            "operators": ["in"],
            "objective": False,
            "preference": None,
            "risk": "governance",
            "computed_by": None,
            "known": 2,
            "of": 4,
            "values": [
                {"value": "US", "count": 2},
                {"value": "KY", "count": 0},
            ],
        }],
    }
    row = trim(vocabulary, model_ids=set(), facet_values={})["facets"][0]
    assert row["has_data"] is True
    by_value = {item["value"]: item["has_data"] for item in row["values"]}
    assert by_value == {"US": True, "KY": False}

    vocabulary["facets"][0]["known"] = 0
    vocabulary["facets"][0]["values"] = []
    empty = trim(vocabulary, model_ids=set(), facet_values={})["facets"][0]
    assert empty["has_data"] is False
    assert "values" not in empty
