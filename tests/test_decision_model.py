"""Domain records, using MODEL-133's registry interface until it lands."""

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from decision.model import Fact, Verification, value_hash


class RegistryStub:
    def facet(self, id):
        types = {
            "context": "integer",
            "price.input": "number",
            "price.output": "number",
            "price.cached": "number",
            "price.batch": "number",
            "speed.ttft_ms": "number",
            "speed.tokens_per_second": "number",
            "speed.method": "string",
            "limits.requests_per_minute": "integer",
            "limits.sla": "string",
            "data.retention_days": "integer",
            "fine_tuning": "boolean",
            "private_deployment": "string_set",
            "harness_compatibility": "string_set",
            "training": "boolean",
            "region": "string",
            "attestations": "string_set",
            "release": "date",
        }
        return SimpleNamespace(id=id, value_type=types[id], tier="guaranteed", risk="capability")

    def provider(self, id):
        if id != "fake-provider":
            raise KeyError(id)
        return SimpleNamespace(id=id)

    def harness(self, id):
        if id != "fake-harness@1.0":
            raise KeyError(id)
        return SimpleNamespace(id=id)


@pytest.fixture
def context():
    return {"registry": RegistryStub()}


def citation():
    return {
        "source_id": "fake-doc",
        "snapshot_ref": "sha256:" + "a" * 64,
        "cited_regions": ["specs"],
    }


def fact_data(**changes):
    return {
        "id": "fake-context",
        "subject": {"kind": "model", "id": "fake-lab/fake-model"},
        "facet": "context",
        "state": "known",
        "value": 128000,
        "sources": [citation()],
        **changes,
    }


def verification_data(**changes):
    return {
        "target": {
            "kind": "fact",
            "id": "fake-context",
            "value_hash": value_hash(128000),
        },
        "collector": {"agent": "collector", "model_family": "family-a", "method": "extract"},
        "verifier": {"agent": "verifier", "model_family": "family-b", "method": "re-read"},
        "method": "compare",
        "outcome": "verified",
        "date": "2026-09-24",
        **changes,
    }


def test_fact_round_trip(context):
    fact = Fact.model_validate(fact_data(), context=context)
    assert fact.value == 128000
    assert fact.quarantined
    assert Fact.model_validate_json(fact.model_dump_json(), context=context) == fact


def test_facts_validate_against_the_real_facet_registry() -> None:
    context = Fact.model_validate(
        fact_data(facet="model.context_window", value=128000)
    )
    assert context.value == 128000

    modalities = Fact.model_validate(
        fact_data(facet="model.input_modalities", value=["text", "image"])
    )
    assert modalities.value == ["text", "image"]

    with pytest.raises(ValidationError, match="registered values"):
        Fact.model_validate(
            fact_data(facet="model.input_modalities", value=["text", "telepathy"])
        )


@pytest.mark.parametrize("state", ["unknown", "not_disclosed", "requires_contract"])
def test_non_known_facts_have_no_value(context, state):
    with pytest.raises(ValidationError, match="value"):
        Fact.model_validate(fact_data(state=state), context=context)
    fact = Fact.model_validate(fact_data(state=state, value=None), context=context)
    assert fact.value is None


@pytest.mark.parametrize(
    "facet,value",
    [
        ("context", True),
        ("context", 1.2),
        ("context", "100"),
        ("price.input", "1.2"),
        ("training", 1),
        ("region", 4),
        ("attestations", [1]),
        ("release", "yesterday"),
        ("price.input", float("nan")),
    ],
)
def test_facet_value_types_are_not_coerced(context, facet, value):
    with pytest.raises(ValidationError):
        Fact.model_validate(fact_data(facet=facet, value=value), context=context)


@pytest.mark.parametrize(
    "facet,value",
    [
        ("context", 0),
        ("price.input", 1.2),
        ("training", False),
        ("region", "test"),
        ("attestations", ["fake-attestation"]),
        ("release", "2026-09-24"),
    ],
)
def test_registry_value_types_round_trip(context, facet, value):
    fact = Fact.model_validate(fact_data(facet=facet, value=value), context=context)
    assert Fact.model_validate_json(fact.model_dump_json(), context=context) == fact


def test_known_fact_needs_value_and_source(context):
    for changes in ({"value": None}, {"sources": []}, {"facet": "not-registered"}):
        with pytest.raises(ValidationError):
            Fact.model_validate(fact_data(**changes), context=context)


def test_collector_cannot_verify_own_work():
    data = verification_data()
    data["verifier"] = {**data["collector"], "method": "another-method"}
    with pytest.raises(ValidationError, match="independent"):
        Verification.model_validate(data)


@pytest.mark.parametrize("change", [{"agent": "another-agent"}, {"model_family": "other-family"}])
def test_different_agent_or_family_is_independent(change):
    data = verification_data()
    data["verifier"] = {**data["collector"], **change}
    assert not Verification.model_validate(data).quarantined


@pytest.mark.parametrize("outcome", ["verified", "mismatch", "unreachable"])
def test_verification_round_trip_and_quarantine(outcome):
    record = Verification.model_validate(
        verification_data(
            outcome=outcome, diff="128000 became 64000" if outcome == "mismatch" else None
        )
    )
    assert record.quarantined == (outcome != "verified")
    assert record.date == date(2026, 9, 24)
    assert Verification.model_validate_json(record.model_dump_json()) == record


def test_mismatch_requires_diff():
    with pytest.raises(ValidationError, match="diff"):
        Verification.model_validate(verification_data(outcome="mismatch"))


def test_verification_must_name_its_fact(context):
    data = fact_data(verification=verification_data())
    assert not Fact.model_validate(data, context=context).quarantined
    data["verification"]["target"]["id"] = "another-fact"
    with pytest.raises(ValidationError, match="target"):
        Fact.model_validate(data, context=context)


def test_verification_record_names_the_value_it_checked() -> None:
    data = verification_data()
    del data["target"]["value_hash"]
    with pytest.raises(ValidationError, match="value_hash"):
        Verification.model_validate(data)


def test_source_and_snapshot_round_trip():
    from decision.model import Source, SourceSnapshot

    source = Source.model_validate(
        {
            "id": "fake-doc",
            "url": "https://example.invalid/spec",
            "fetch": "conditional_http",
            "normaliser": "html-default",
            "cited_regions": [{"id": "specs", "locator": {"kind": "css", "value": "#specs"}}],
        }
    )
    snapshot = SourceSnapshot.model_validate(
        {
            "source_id": source.id,
            "retrieved_at": "2026-09-24T12:00:00Z",
            "page_fingerprint": "sha256:" + "a" * 64,
            "region_fingerprints": {"specs": "sha256:" + "b" * 64},
            "copy_ref": "sha256:" + "c" * 64,
            "etag": '"fixture-v1"',
            "last_modified": "Wed, 24 Sep 2026 12:00:00 GMT",
        }
    )
    assert Source.model_validate_json(source.model_dump_json()) == source
    assert SourceSnapshot.model_validate_json(snapshot.model_dump_json()) == snapshot
    assert str(source.url) == "https://example.invalid/spec"


def test_source_rejects_duplicate_regions():
    from decision.model import Source

    region = {"id": "specs", "locator": {"kind": "heading_anchor", "value": "specs"}}
    with pytest.raises(ValidationError, match="unique"):
        Source.model_validate(
            {
                "id": "fake-doc",
                "url": "https://example.invalid/spec",
                "fetch": "http",
                "normaliser": "fake-v1",
                "cited_regions": [region, region],
            }
        )


@pytest.mark.parametrize(
    "change",
    [
        {"copy_ref": "local/file.html"},
        {"retrieved_at": "2026-09-24T12:00:00"},
        {"page_fingerprint": "not-a-hash"},
    ],
)
def test_snapshot_requires_content_addresses_and_aware_time(change):
    from decision.model import SourceSnapshot

    with pytest.raises(ValidationError):
        SourceSnapshot.model_validate(
            {
                "source_id": "fake-doc",
                "retrieved_at": "2026-09-24T12:00:00Z",
                "page_fingerprint": "sha256:" + "a" * 64,
                "region_fingerprints": {"specs": "sha256:" + "b" * 64},
                "copy_ref": "sha256:" + "c" * 64,
                **change,
            }
        )


def legacy_evidence():
    return {
        "benchmark_id": "fake-benchmark",
        "model_id_as_evaluated": "Fake Model",
        "score": 42.0,
        "unit": "%",
        "source_url": "https://example.invalid/result",
        "source_kind": "benchmark_author",
        "evidence_date": "2026-09-23",
        "date_type": "published",
        "verified_at": "2026-09-24",
    }


def test_evidence_extends_card_record_without_inventing_qualifiers(context):
    from decision.model import Evidence
    from schema.card import BenchmarkEvidence

    row = Evidence.model_validate(legacy_evidence(), context=context)
    assert isinstance(row, BenchmarkEvidence)
    assert row.harness is None
    assert row.measured_by is None
    assert row.sources == []
    assert row.verification is None and row.quarantined
    assert Evidence.model_validate_json(row.model_dump_json(), context=context) == row


def test_qualified_evidence_round_trip(context):
    from decision.model import Evidence

    row = Evidence.model_validate(
        {
            **legacy_evidence(),
            "id": "fake-evidence",
            "subject": {"kind": "model", "id": "fake-lab/fake-model"},
            "harness": "fake-harness@1.0",
            "effort": "high",
            "tools": ["shell"],
            "measured_by": "outcome_protocol",
            "benchmark_version": "2.0",
            "subcategory": "fake-task",
            "sources": [citation()],
            "verification": verification_data(
                target={
                    "kind": "evidence",
                    "id": "fake-evidence",
                    "value_hash": value_hash(42.0),
                }
            ),
        },
        context=context,
    )
    assert not row.quarantined
    assert row.measured_by == "outcome_protocol"
    assert Evidence.model_validate_json(row.model_dump_json(), context=context) == row


def test_evidence_checks_registry_and_verification_binding(context):
    from decision.model import Evidence

    assert (
        Evidence.model_validate(
            {**legacy_evidence(), "harness": "unregistered"}, context=context
        ).harness
        == "unregistered"
    )
    for changes in (
        {"harness": "free-text"},
        {"verification": verification_data()},
        {"subject": {"kind": "provider", "id": "fake-provider"}},
    ):
        with pytest.raises(ValidationError):
            Evidence.model_validate({**legacy_evidence(), **changes}, context=context)


@pytest.mark.parametrize(
    "lifecycle,lineup,archive",
    [("active", True, False), ("deprecated", True, False), ("retired", False, True)],
)
def test_model_lifecycle_round_trip(lifecycle, lineup, archive):
    from decision.model import Model

    model = Model(id="fake-lab/fake-model", lifecycle=lifecycle)
    assert model.in_lineup is lineup
    assert model.in_live_archive is archive
    assert Model.model_validate_json(model.model_dump_json()) == model


def test_every_existing_card_and_evidence_row_still_loads(context):
    from decision.model import Evidence
    from schema.card import ModelCard

    paths = sorted((Path(__file__).resolve().parents[1] / "models").rglob("*.md"))
    cards = [ModelCard.from_yaml_file(p) for p in paths if p.name != "LICENSE.md"]
    assert len(cards) > 1000
    count = 0
    for card in cards:
        for row in card.benchmarks.evidence:
            loaded = Evidence.model_validate(row.model_dump(), context=context)
            assert loaded.score == row.score
            assert loaded.quarantined
            count += 1
    assert count > 0


def test_offering_fixture_loads_and_round_trips(context):
    from decision.model import Offering, load_offerings

    path = Path(__file__).parent / "fixtures/offerings/fake-provider/fake-lab/fake-model.yaml"
    offerings = load_offerings(path, registry=context["registry"])
    assert len(offerings) == 2
    assert offerings[0].id == "fake-provider/fake-lab/fake-model/test-region/standard"
    assert offerings[0].facts[0].value == 1.25
    assert offerings[1].tier == "enterprise"
    assert offerings[1].facts[0].state == "requires_contract"
    for offering in offerings:
        assert Offering.model_validate_json(offering.model_dump_json(), context=context) == offering


def test_offering_rejects_wrong_subject_unknown_provider_and_duplicate_facets(context):
    from decision.model import Offering

    data = {
        "model": "fake-lab/fake-model",
        "provider": "fake-provider",
        "region": "test-region",
        "tier": "standard",
        "facts": [fact_data()],
    }
    with pytest.raises(ValidationError, match="subject"):
        Offering.model_validate(data, context=context)
    data["facts"] = []
    data["provider"] = "missing-provider"
    with pytest.raises(ValidationError, match="provider"):
        Offering.model_validate(data, context=context)
    data["provider"] = "fake-provider"
    fact = fact_data(
        subject={"kind": "offering", "id": "fake-provider/fake-lab/fake-model/test-region/standard"}
    )
    data["facts"] = [fact, fact]
    with pytest.raises(ValidationError, match="unique"):
        Offering.model_validate(data, context=context)


def test_offering_loader_checks_file_identity_and_duplicate_offerings(context, tmp_path):
    import yaml

    from decision.model import load_offerings

    directory = tmp_path / "fake-provider/fake-lab"
    directory.mkdir(parents=True)
    path = directory / "fake-model.yaml"
    row = {
        "model": "fake-lab/fake-model",
        "provider": "fake-provider",
        "region": "test-region",
        "tier": "standard",
        "facts": [],
    }
    path.write_text(yaml.safe_dump([row, row]))
    with pytest.raises(ValueError, match="duplicate"):
        load_offerings(path, registry=context["registry"])
    row["model"] = "fake-lab/wrong-model"
    path.write_text(yaml.safe_dump([row]))
    with pytest.raises(ValueError, match="path"):
        load_offerings(path, registry=context["registry"])
    path.write_text("offerings: []")
    with pytest.raises(ValidationError):
        load_offerings(path, registry=context["registry"])


def test_fake_offering_covers_provider_dependent_facts(context):
    from decision.model import load_offerings

    path = Path(__file__).parent / "fixtures/offerings/fake-provider/fake-lab/fake-model.yaml"
    standard = load_offerings(path, registry=context["registry"])[0]
    values = {fact.facet: fact.value for fact in standard.facts}
    assert values == {
        "price.input": 1.25,
        "price.output": 5.0,
        "price.cached": 0.25,
        "price.batch": 0.625,
        "speed.ttft_ms": 200.0,
        "speed.tokens_per_second": 50.0,
        "speed.method": "FAKE fixed 100-token prompt, 100-token output, one request",
        "limits.requests_per_minute": 60,
        "limits.sla": "FAKE test SLA",
        "data.retention_days": 0,
        "training": False,
        "attestations": ["FAKE test attestation"],
        "fine_tuning": False,
        "private_deployment": ["FAKE private option"],
        "harness_compatibility": ["fake-harness@1.0"],
    }
    assert all(fact.sources for fact in standard.facts)


def test_default_registry_uses_the_agreed_module_interface(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "decision.registry", RegistryStub())
    assert Fact.model_validate(fact_data()).value == 128000
    assert (
        Fact.model_validate(
            fact_data(subject={"kind": "provider", "id": "fake-provider"})
        ).subject.kind
        == "provider"
    )
    with pytest.raises(ValidationError, match="provider"):
        Fact.model_validate(fact_data(subject={"kind": "provider", "id": "absent"}))


def test_model_owns_its_facts(context):
    from decision.model import Model

    model = Model.model_validate(
        {"id": "fake-lab/fake-model", "lifecycle": "active", "facts": [fact_data()]},
        context=context,
    )
    assert Model.model_validate_json(model.model_dump_json(), context=context) == model
    with pytest.raises(ValidationError, match="subject"):
        Model.model_validate(
            {"id": "fake-lab/other-model", "lifecycle": "active", "facts": [fact_data()]},
            context=context,
        )


def test_blank_verification_identity_is_rejected():
    data = verification_data()
    data["verifier"]["agent"] = "   "
    with pytest.raises(ValidationError):
        Verification.model_validate(data)
