"""Lab jurisdiction is recorded once per lab and inherited (MODEL-344)."""

from __future__ import annotations

import logging
import os
from datetime import date
from pathlib import Path

import pytest
import yaml

from decision.compare import _condition_facet
from decision.contract import parse_spec
from decision.engine import decide
from decision.filter import strip_unverified_condition
from decision.labs import FACET, Lab, LabRegistryError, check_lab_copies, load_labs
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.registry import facet as facets
from decision.model import value_hash
from decision.snapshot import (
    CompletenessError,
    SnapshotBuildError,
    SnapshotInputs,
    build_from_repo,
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
    assert jurisdiction_codes("governed by the New York Not-for-Profit Corporation Law") == frozenset()
    assert jurisdiction_codes("California Nonprofit Corporation Law") == frozenset()
    assert jurisdiction_codes("Delaware Limited Liability Company Act") == frozenset()
    assert jurisdiction_codes("SpaceXAI LLC is a Nevada company.") == frozenset({"US"})
    assert jurisdiction_codes(
        "Anthropic is a Delaware public benefit corporation."
    ) == frozenset({"US"})
    assert jurisdiction_codes(
        "OpenAI, Inc. was incorporated as a Delaware nonprofit corporation in 2015."
    ) == frozenset({"US"})
    assert jurisdiction_codes("a Delaware non-profit corporation") == frozenset({"US"})
    assert jurisdiction_codes("a nonprofit corporation") == frozenset()
    assert jurisdiction_codes("Jina AI GmbH") == frozenset()
    assert jurisdiction_codes("Moonshot AI PTE. LTD.") == frozenset()
    assert jurisdiction_codes(
        "Register: Amtsgericht Berlin Register Number: HRB 218021"
    ) == frozenset({"DE"})
    assert jurisdiction_codes("Google LLC | Delaware") == frozenset({"US"})
    assert jurisdiction_codes(
        '"stateOfIncorporationDescription": "Cayman Islands"'
    ) == frozenset({"KY"})
    assert jurisdiction_codes('"stateOfIncorporationDescription": "DE"') == frozenset({"US"})
    assert jurisdiction_codes("Cayman Islands") == frozenset({"KY"})
    assert jurisdiction_codes(
        "OpenAI Ireland Ltd, a company incorporated in the Republic of Ireland"
    ) == frozenset({"IE"})


def test_an_exhibit_21_cell_is_a_whole_suffix_then_a_state() -> None:
    assert jurisdiction_codes("Zinc | Texas") == frozenset()
    assert jurisdiction_codes("Limited | Washington state office") == frozenset()
    assert jurisdiction_codes("Google LLC | Delaware") == frozenset({"US"})


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
    assert jurisdiction_codes(whole or "") == frozenset({"KY"})


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
    assert exc.value.coverage is not None
    assert exc.value.coverage.known == 0
    assert exc.value.coverage.explicit_null == 0
    assert exc.value.coverage.gap == 1
    assert "explicit null 0" in str(exc.value)


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


@pytest.mark.parametrize("text", [
    "Example GmbH (Switzerland)",
    "Handelsregister Basel",
    "Wien GmbH",
    "Our reseller Foo Pte Ltd",
    "Georgia",
    "| Washington | Seattle office |",
    "| New York | 10 employees",
    "Office | Texas",
])
def test_a_suffix_or_a_bare_state_name_is_not_incorporation(text: str) -> None:
    assert jurisdiction_codes(text) == frozenset()


def test_an_excerpt_cites_one_sentence_and_drops_the_other_country() -> None:
    from decision.normalise import NORMALISERS, Locator, normalise_document, select_region

    html = (
        "<p>OpenAI OpCo, LLC, a Delaware company, and OpenAI Ireland Ltd, "
        "a company incorporated in the Republic of Ireland.</p>"
    )
    doc = normalise_document(html.encode(), NORMALISERS["html-default"])
    region = select_region(
        doc, Locator("css", "p::excerpt=OpenAI OpCo, LLC, a Delaware company")
    )
    assert region == "OpenAI OpCo, LLC, a Delaware company"
    assert jurisdiction_codes(region or "") == frozenset({"US"})
    assert select_region(doc, Locator("css", "p::excerpt=not on the page")) is None


def test_a_parent_without_its_own_code_is_refused(tmp_path) -> None:
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "labs.yaml").write_text(
        "schema_version: 1\n"
        "labs:\n"
        "  - id: qwen\n"
        "    entity: Alibaba Cloud\n"
        "    entity_code: KY\n"
        "    parent_entity: Alibaba Group Holding Limited\n"
        "    note: The parent country is not on the page.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: known\n"
        "      value: [KY]\n"
        "      sources:\n"
        "        - source_id: lab-jurisdiction-qwen\n"
        f"          snapshot_ref: '{SOURCE['snapshot_ref']}'\n"
        "          cited_regions: [incorporation]\n"
        "          party: entity\n",
        encoding="utf-8",
    )
    with pytest.raises(LabRegistryError, match="parent"):
        load_labs(tmp_path)


def test_a_parent_named_as_the_same_entity_is_refused(tmp_path) -> None:
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "labs.yaml").write_text(
        "schema_version: 1\n"
        "labs:\n"
        "  - id: google\n"
        "    entity: Alphabet Inc.\n"
        "    entity_code: US\n"
        "    parent_entity: Alphabet Inc.\n"
        "    parent_code: US\n"
        "    note: The filing names one company.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: known\n"
        "      value: [US]\n"
        "      sources:\n"
        "        - source_id: lab-jurisdiction-google\n"
        f"          snapshot_ref: '{SOURCE['snapshot_ref']}'\n"
        "          cited_regions: [incorporation]\n"
        "          party: entity\n"
        "        - source_id: lab-jurisdiction-google-parent\n"
        f"          snapshot_ref: '{SOURCE['snapshot_ref']}'\n"
        "          cited_regions: [incorporation]\n"
        "          party: parent\n",
        encoding="utf-8",
    )
    with pytest.raises(LabRegistryError, match="differ"):
        load_labs(tmp_path)


def _registry(tmp_path, labs_yaml: str, sources_yaml: str) -> None:
    (tmp_path / "registry").mkdir(exist_ok=True)
    (tmp_path / "registry" / "labs.yaml").write_text(labs_yaml, encoding="utf-8")
    (tmp_path / "registry" / "sources.yaml").write_text(sources_yaml, encoding="utf-8")


def _source_row(source_id: str, url: str, region: str = "incorporation",
                kind: str | None = "provider_terms") -> str:
    kind_line = "" if kind is None else f"  kind: {kind}\n"
    return (
        f"- id: {source_id}\n"
        f"  url: {url}\n"
        "  volatility: static\n"
        "  fetch: http\n"
        "  normaliser: html-default\n"
        f"{kind_line}"
        "  cited_regions:\n"
        f"  - id: {region}\n"
        "    locator: {kind: page, value: ''}\n"
    )


def _widget_null_registry(source_yaml: str) -> tuple[str, str]:
    absent = "sha256:" + "cd" * 32
    labs = (
        "schema_version: 1\n"
        "labs:\n"
        "  - id: widget\n"
        "    note: The terms do not state incorporation.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: not_disclosed\n"
        "      value: null\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-widget, "
        f"snapshot_ref: '{absent}', cited_regions: [incorporation]}}\n"
    )
    return labs, "schema_version: 1\nsources:\n" + source_yaml


def test_a_source_without_a_kind_is_refused(tmp_path) -> None:
    labs, sources = _widget_null_registry(_source_row(
        "lab-jurisdiction-widget", "https://example.com/legal/terms", kind=None,
    ))
    _registry(tmp_path, labs, sources)
    with pytest.raises(LabRegistryError, match="kind") as exc:
        load_labs(tmp_path)
    message = str(exc.value)
    assert "widget" in message
    assert "lab-jurisdiction-widget" in message
    assert "None" in message
    for kind in facets(FACET).permitted_source_kinds:
        assert kind in message


def test_a_source_kind_outside_the_facet_is_refused(tmp_path) -> None:
    assert "lab_announcement" not in facets(FACET).permitted_source_kinds
    labs, sources = _widget_null_registry(_source_row(
        "lab-jurisdiction-widget", "https://example.com/legal/terms", kind="lab_announcement",
    ))
    _registry(tmp_path, labs, sources)
    with pytest.raises(LabRegistryError, match="lab_announcement") as exc:
        load_labs(tmp_path)
    message = str(exc.value)
    assert "widget" in message
    assert "lab-jurisdiction-widget" in message
    for kind in facets(FACET).permitted_source_kinds:
        assert kind in message


def test_a_permitted_source_kind_loads(tmp_path) -> None:
    permitted = facets(FACET).permitted_source_kinds[0]
    labs, sources = _widget_null_registry(_source_row(
        "lab-jurisdiction-widget", "https://example.com/legal/terms", kind=permitted,
    ))
    _registry(tmp_path, labs, sources)
    loaded = load_labs(tmp_path)
    assert loaded["widget"].explicit_null


def test_an_explicit_null_rejects_a_readme_and_a_homepage(tmp_path) -> None:
    absent = "sha256:" + "cd" * 32
    _registry(
        tmp_path,
        "schema_version: 1\n"
        "labs:\n"
        "  - id: infgrad\n"
        "    note: The model card is not a legal page.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: not_disclosed\n"
        "      value: null\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-infgrad, "
        f"snapshot_ref: '{absent}', cited_regions: [incorporation]}}\n",
        "schema_version: 1\nsources:\n"
        + _source_row(
            "lab-jurisdiction-infgrad",
            "https://huggingface.co/infgrad/Jasper/raw/main/README.md",
        ),
    )
    with pytest.raises(LabRegistryError, match="Hugging Face"):
        load_labs(tmp_path)

    _registry(
        tmp_path,
        "schema_version: 1\n"
        "labs:\n"
        "  - id: annamodels\n"
        "    note: The homepage is marketing.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: not_disclosed\n"
        "      value: null\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-annamodels, "
        f"snapshot_ref: '{absent}', cited_regions: [incorporation]}}\n",
        "schema_version: 1\nsources:\n"
        + _source_row("lab-jurisdiction-annamodels", "https://www.lgresearch.ai/"),
    )
    with pytest.raises(LabRegistryError, match="homepage"):
        load_labs(tmp_path)


def test_an_empty_retained_page_fails_the_copy_check_not_the_loader(tmp_path) -> None:
    from decision.sources import CopyStore

    store = CopyStore(tmp_path / "copies")
    empty = store.put(b"<html><body></body></html>")
    _registry(
        tmp_path,
        "schema_version: 1\n"
        "labs:\n"
        "  - id: codefuse\n"
        "    note: The page normalises to nothing.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: not_disclosed\n"
        "      value: null\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-codefuse, "
        f"snapshot_ref: '{empty}', cited_regions: [incorporation]}}\n",
        "schema_version: 1\nsources:\n"
        + _source_row("lab-jurisdiction-codefuse", "https://codefuse.ai/legal/terms"),
    )
    labs = load_labs(tmp_path)
    assert labs["codefuse"].explicit_null
    with pytest.raises(LabRegistryError, match="no retained text"):
        check_lab_copies(tmp_path, labs, store)


def test_an_explicit_null_accepts_a_legal_page_with_text(tmp_path) -> None:
    from decision.sources import CopyStore

    store = CopyStore(tmp_path / "copies")
    ref = store.put(b"<html><body><p>Terms of service. The operator is named and no country of incorporation is stated.</p></body></html>")
    _registry(
        tmp_path,
        "schema_version: 1\n"
        "labs:\n"
        "  - id: deepseek\n"
        "    note: The terms do not state incorporation.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: not_disclosed\n"
        "      value: null\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-deepseek, "
        f"snapshot_ref: '{ref}', cited_regions: [incorporation]}}\n",
        "schema_version: 1\nsources:\n"
        + _source_row(
            "lab-jurisdiction-deepseek",
            "https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html",
        ),
    )
    labs = load_labs(tmp_path)
    check_lab_copies(tmp_path, labs, store)
    assert labs["deepseek"].explicit_null


def test_jurisdiction_codes_from_two_regions_verify_only_as_a_union() -> None:
    from decision.verify import deterministic_extractors, verify

    imprint = SourceRef.model_validate({
        "source_id": "imprint", "snapshot_ref": SOURCE["snapshot_ref"], "cited_regions": ["incorporation"],
    })
    cover = SourceRef.model_validate({
        "source_id": "cover", "snapshot_ref": SOURCE["snapshot_ref"], "cited_regions": ["incorporation"],
    })
    claim = Claim(
        target=TargetRef(kind="fact", id="lab:jina#origin.lab_jurisdiction"),
        subject="lab:jina",
        names=("Jina AI GmbH",),
        field=FACET,
        value=["DE", "NL"],
        collector=VerificationActor(agent="grok", model_family="grok", method="lab-registry@1"),
        sources=(imprint, cover),
    )

    class Regions:
        def __init__(self, mapping: dict[tuple[str, str], str | None]) -> None:
            self.mapping = mapping

        def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
            return self.mapping.get((source_id, region_id))

    both = Regions({
        ("imprint", "incorporation"): "Amtsgericht Berlin HRB 218021",
        ("cover", "incorporation"): "Netherlands",
    })
    assert verify(claim, both, deterministic_extractors(), today=date(2026, 10, 8)).outcome == "verified"
    partial = Regions({
        ("imprint", "incorporation"): "Amtsgericht Berlin HRB 218021",
        ("cover", "incorporation"): "Amtsgericht Munich HRB 1",
    })
    assert verify(claim, partial, deterministic_extractors(), today=date(2026, 10, 8)).outcome == "mismatch"
    extra = Regions({
        ("imprint", "incorporation"): "Amtsgericht Berlin HRB 218021",
        ("cover", "incorporation"): "Cayman Islands",
    })
    assert verify(claim, extra, deterministic_extractors(), today=date(2026, 10, 8)).outcome == "mismatch"
    missing = Regions({
        ("imprint", "incorporation"): "Amtsgericht Berlin HRB 218021",
        ("cover", "incorporation"): None,
    })
    assert verify(claim, missing, deterministic_extractors(), today=date(2026, 10, 8)).outcome == "unreachable"


def test_a_training_mention_does_not_block_the_jurisdiction_extractor() -> None:
    """Governance prose accepts pages that say "train" and returns nothing for this facet."""
    from decision.verify import deterministic_extractors, verify

    text = (
        "Anthropic does not train on customer content. "
        "Anthropic is a Delaware public benefit corporation."
    )
    claim = _claim(["US"], "Anthropic")

    class Regions:
        def text(self, source_id: str, copy_ref: str, region_id: str) -> str:
            return text

    result = verify(claim, Regions(), deterministic_extractors(), today=date(2026, 10, 8))
    assert result.outcome == "verified"
    assert result.verification is not None
    assert result.verification.verifier.method == "lab-jurisdiction@1"


def test_only_prefix_leaves_other_claims_pending(tmp_path) -> None:
    from datetime import UTC, datetime

    from decision.sources import CopyStore
    from decision.verify import Queue, VerificationLog, deterministic_extractors, run

    store = CopyStore(tmp_path / "copies")
    body = b"<p>Google LLC is a Delaware limited liability company.</p>"
    ref = store.put(body)
    _registry(
        tmp_path,
        "schema_version: 1\nlabs: []\n",
        "schema_version: 1\nsources:\n"
        + _source_row("src-lab-docs", "https://www.sec.gov/Archives/example.htm", region="r1"),
    )
    # The claim's snapshot ref has to be the retained copy the region reader opens.
    source = dict(SOURCE)
    source["snapshot_ref"] = ref
    lab_claim = Claim(
        target=TargetRef(kind="fact", id="lab:google#origin.lab_jurisdiction"),
        subject="lab:google",
        names=("Google LLC",),
        field=FACET,
        value=["US"],
        collector=VerificationActor(agent="grok", model_family="grok", method="lab-registry@1"),
        sources=(SourceRef.model_validate(source),),
    )
    other = Claim(
        target=TargetRef(kind="fact", id="azure-ai-foundry/gpt-5-4#offering.attestation.soc2"),
        subject="azure-ai-foundry/gpt-5-4",
        names=("GPT-5.4",),
        field="offering.attestation.soc2",
        value=True,
        collector=VerificationActor(agent="grok", model_family="grok", method="primary-source@1"),
        sources=(SourceRef.model_validate(source),),
    )
    queue = Queue(tmp_path / "verification")
    queue.file(lab_claim, at=datetime(2026, 10, 8, tzinfo=UTC))
    queue.file(other, at=datetime(2026, 10, 8, tzinfo=UTC))
    from decision.sources import load_sources
    from decision.verify import StoredRegions

    report = run(
        queue,
        VerificationLog(tmp_path / "verification"),
        StoredRegions(store, load_sources(tmp_path / "registry" / "sources.yaml")),
        deterministic_extractors(),
        today=date(2026, 10, 8),
        only="lab:",
    )
    assert [result.target.id for result in report.results] == ["lab:google#origin.lab_jurisdiction"]
    assert report.results[0].outcome == "verified"
    log = (tmp_path / "verification" / "log.jsonl").read_text(encoding="utf-8")
    assert "lab:google#origin.lab_jurisdiction" in log
    assert "offering.attestation.soc2" not in log
    pending, _unknown = queue.pending()
    assert [claim.target.id for claim in pending] == [
        "azure-ai-foundry/gpt-5-4#offering.attestation.soc2"
    ]


def test_cli_only_checks_lab_claims(tmp_path, monkeypatch) -> None:
    from datetime import UTC, datetime

    from typer.testing import CliRunner

    from cli.modelspec import legacy as cli_mod
    from decision.sources import CopyStore
    from decision.verify import Queue

    store = CopyStore(tmp_path / "copies")
    ref = store.put(b"<p>Anthropic is a Delaware public benefit corporation.</p>")
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(store.root))
    _registry(
        tmp_path,
        "schema_version: 1\nlabs: []\n",
        "schema_version: 1\nsources:\n"
        + _source_row(
            "src-lab-docs",
            "https://www.anthropic.com/news/the-long-term-benefit-trust",
            region="r1",
        ),
    )
    source = dict(SOURCE)
    source["snapshot_ref"] = ref
    queue = Queue(tmp_path / "verification")
    queue.file(Claim(
        target=TargetRef(kind="fact", id="lab:anthropic#origin.lab_jurisdiction"),
        subject="lab:anthropic",
        names=("Anthropic",),
        field=FACET,
        value=["US"],
        collector=VerificationActor(agent="grok", model_family="grok", method="lab-registry@1"),
        sources=(SourceRef.model_validate(source),),
    ), at=datetime(2026, 10, 8, tzinfo=UTC))
    queue.file(Claim(
        target=TargetRef(kind="fact", id="google/gemma-4#deepmind_mrcr_v2"),
        subject="google/gemma-4",
        names=("Gemma 4",),
        field="deepmind_mrcr_v2",
        value=1,
        collector=VerificationActor(agent="grok", model_family="grok", method="primary-source@1"),
        sources=(SourceRef.model_validate(source),),
    ), at=datetime(2026, 10, 8, tzinfo=UTC))
    result = CliRunner().invoke(
        cli_mod.app, ["verify", "--root", str(tmp_path), "--only", "lab:", "--json"]
    )
    assert result.exit_code == 0, result.output
    payload = __import__("json").loads(result.output)
    assert payload["counts"]["verified"] == 1
    assert payload["results"][0]["target"] == "fact:lab:anthropic#origin.lab_jurisdiction"
    log = (tmp_path / "verification" / "log.jsonl").read_text(encoding="utf-8")
    assert "deepmind_mrcr_v2" not in log


def test_coverage_counts_known_null_and_gap_apart() -> None:
    present = _lab("google", ["US"])
    absent = _lab("deepseek", None, state="not_disclosed", note="The terms state no country.")
    missing = _lab("infgrad", None, state="gap", note="No legal page was found.")
    with pytest.raises(CompletenessError) as exc:
        build_snapshot(
            SnapshotInputs(
                models=[model("google/gemma"), model("deepseek/v4"), model("infgrad/stella")],
                sources=SOURCES,
                verifications=[verification("fact", present.fact()["id"], value=["US"])],
                labs={"google": present, "deepseek": absent, "infgrad": missing},
            ),
            premier=["google/gemma", "deepseek/v4", "infgrad/stella"],
            registry=__import__("decision.registry", fromlist=["default"]).default(),
        )
    coverage = exc.value.coverage
    assert coverage is not None
    assert (coverage.known, coverage.explicit_null, coverage.gap) == (1, 1, 1)
    assert coverage.gap_models == ("infgrad/stella",)
    assert "infgrad" in coverage.gap_labs


def _verified_absence(mid: str, facet_id: str) -> dict:
    fid = f"{mid}#{facet_id}"
    return {
        "id": fid,
        "facet": facet_id,
        "state": "not_disclosed",
        "value": None,
        "sources": [{
            "source_id": "src-fixture",
            "snapshot_ref": "sha256:" + "11" * 32,
            "cited_regions": ["r1"],
        }],
        "verification": {
            "target": {"kind": "fact", "id": fid, "value_hash": value_hash(None)},
            "collector": {"agent": "collector-a", "model_family": "family-a", "method": "read"},
            "verifier": {"agent": "verifier-b", "model_family": "family-b", "method": "re-read"},
            "method": "re-read the cited region",
            "outcome": "verified",
            "date": "2026-10-08",
        },
    }


def test_a_snapshot_builds_from_labs_yaml_when_the_source_cache_is_empty(
    tmp_path, monkeypatch, caplog,
) -> None:
    """``vendor.py`` builds through ``build_from_repo``. That path does not open the cache."""
    cache = tmp_path / "empty-cache"
    cache.mkdir()
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(cache))
    root = tmp_path / "repo"
    (root / "models" / "fixturelab").mkdir(parents=True)
    (root / "benchmarks").mkdir()
    (root / "offerings").mkdir()
    (root / "premier").mkdir()
    (root / "registry").mkdir()
    absent = "sha256:" + "ab" * 32
    _registry(
        root,
        "schema_version: 1\n"
        "labs:\n"
        "  - id: fixturelab\n"
        "    note: The terms do not state incorporation.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: not_disclosed\n"
        "      value: null\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-fixturelab, "
        f"snapshot_ref: '{absent}', cited_regions: [incorporation]}}\n"
        "  - id: widget\n"
        "    entity: Widget LLC\n"
        "    entity_code: US\n"
        "    note: The filing names Delaware.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: known\n"
        "      value: [US]\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-widget, "
        f"snapshot_ref: '{absent}', cited_regions: [incorporation], party: entity}}\n"
        "  - id: gaplab\n"
        "    note: No legal page was found.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction: {state: gap, value: null}\n",
        "schema_version: 1\nsources:\n"
        + _source_row("src-fixture", "https://fixturelab.example/legal/terms", region="r1")
        + _source_row(
            "lab-jurisdiction-fixturelab",
            "https://fixturelab.example/legal/terms",
        )
        + _source_row(
            "lab-jurisdiction-widget",
            "https://www.sec.gov/Archives/example.htm",
        ),
    )
    from decision.registry import default

    registry = default()
    mid = "fixturelab/one"
    facts = [
        _verified_absence(mid, facet.id)
        for facet in registry.facets()
        if facet.tier == "guaranteed"
        and not getattr(facet, "computed_by", None)
        and facet.subject == "model"
        and facet.id != FACET
    ]
    card = {"model_id": mid, "lifecycle": "active", "facts": facts}
    (root / "models" / "fixturelab" / "one.md").write_text(
        "---\n" + yaml.safe_dump(card, sort_keys=False) + "---\n\nFixture.\n",
        encoding="utf-8",
    )
    (root / "premier" / "slice.yaml").write_text(
        "models:\n- fixturelab/one\n",
        encoding="utf-8",
    )
    with caplog.at_level(logging.INFO, logger="decision.snapshot"):
        built = build_from_repo(
            root,
            premier=root / "premier" / "slice.yaml",
            as_of=date(2026, 10, 8),
            registry=registry,
        )
    assert built.snapshot_id.startswith("snap_")
    assert (
        "premier models: known 0, explicit null 1, gap 0; "
        "gap labs outside premier: gaplab"
    ) in caplog.text
    assert not any(path.is_file() for path in cache.rglob("*"))


def test_check_lab_copies_requires_the_recorded_code(tmp_path) -> None:
    from decision.sources import CopyStore

    store = CopyStore(tmp_path / "copies")
    wrong = store.put(b"<p>Widget LLC was incorporated in the Cayman Islands.</p>")
    _registry(
        tmp_path,
        "schema_version: 1\n"
        "labs:\n"
        "  - id: widget\n"
        "    entity: Widget LLC\n"
        "    entity_code: US\n"
        "    note: The filing names Delaware.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: known\n"
        "      value: [US]\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-widget, "
        f"snapshot_ref: '{wrong}', cited_regions: [incorporation], party: entity}}\n",
        "schema_version: 1\nsources:\n"
        + _source_row("lab-jurisdiction-widget", "https://www.sec.gov/Archives/example.htm"),
    )
    labs = load_labs(tmp_path)
    with pytest.raises(LabRegistryError, match="does not state US"):
        check_lab_copies(tmp_path, labs, store)

    both = store.put(
        b"<p>Widget LLC is a Delaware limited liability company. "
        b"A subsidiary was incorporated in the Cayman Islands.</p>"
    )
    _registry(
        tmp_path,
        "schema_version: 1\n"
        "labs:\n"
        "  - id: widget\n"
        "    entity: Widget LLC\n"
        "    entity_code: US\n"
        "    note: The filing names Delaware.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: known\n"
        "      value: [US]\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-widget, "
        f"snapshot_ref: '{both}', cited_regions: [incorporation], party: entity}}\n",
        "schema_version: 1\nsources:\n"
        + _source_row("lab-jurisdiction-widget", "https://www.sec.gov/Archives/example.htm"),
    )
    labs = load_labs(tmp_path)
    with pytest.raises(LabRegistryError, match="outside the recorded set"):
        check_lab_copies(tmp_path, labs, store)

    stated = store.put(b"<p>Widget LLC is a Delaware limited liability company.</p>")
    _registry(
        tmp_path,
        "schema_version: 1\n"
        "labs:\n"
        "  - id: widget\n"
        "    entity: Widget LLC\n"
        "    entity_code: US\n"
        "    note: The filing names Delaware.\n"
        "    read_date: '2026-10-08'\n"
        "    jurisdiction:\n"
        "      state: known\n"
        "      value: [US]\n"
        "      sources:\n"
        "        - {source_id: lab-jurisdiction-widget, "
        f"snapshot_ref: '{stated}', cited_regions: [incorporation], party: entity}}\n",
        "schema_version: 1\nsources:\n"
        + _source_row("lab-jurisdiction-widget", "https://www.sec.gov/Archives/example.htm"),
    )
    labs = load_labs(tmp_path)
    check_lab_copies(tmp_path, labs, store)


def test_check_lab_copies_reads_the_cache_when_it_is_present() -> None:
    from decision.sources import CopyStore

    configured = os.environ.get("MODELSPEC_SOURCE_CACHE")
    cache = Path(configured) if configured else Path.home() / ".cache" / "modelspec" / "sources"
    if not cache.is_dir() or not any(cache.iterdir()):
        pytest.skip("source cache absent")
    candidates = []
    raw = os.environ.get("MODELSPEC_DATA_DIR", "").strip()
    if raw:
        candidates.append(Path(raw))
    candidates.append(Path(__file__).resolve().parents[1].parent / "model-344-data")
    data = next((path for path in candidates if (path / "registry" / "labs.yaml").is_file()), None)
    if data is None:
        pytest.skip("source cache absent")
    labs = load_labs(data)
    store = CopyStore()
    cited = [source["snapshot_ref"] for lab in labs.values() for source in lab.sources]
    if not cited or any(not store.has(ref) for ref in cited):
        pytest.skip("source cache absent")
    check_lab_copies(data, labs, store)
