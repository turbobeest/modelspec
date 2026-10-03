"""Agent lookup budgets and the unchanged page/data-split boundary (MODEL-280)."""
from __future__ import annotations

import asyncio
import copy
import json
import math
import sys
from types import SimpleNamespace

import pytest

from api.worker.src.display_vocabulary import PAGE_SIZE, SECTIONS, lookup, starter_ids, trim
from decision.registry import default
from tests.test_decision_vocabulary import snapshot, vocabulary  # noqa: F401


def tokens(value):
    text = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    try:
        import tiktoken
    except ImportError:
        return math.ceil(len(text) / 4)
    return len(tiktoken.get_encoding("cl100k_base").encode(text))


@pytest.fixture(scope="module")
def display(vocabulary):
    registry = default()
    values = {f.id: ([True, False] if f.value_type.kind == "boolean" else sorted(registry.allowed_values(f) or ()))
              for f in registry.facets() if f.value_type.kind in {"enum", "boolean"}}
    return trim(vocabulary, model_ids=set(vocabulary["models"]), facet_values=values)


@pytest.mark.parametrize("section", SECTIONS)
def test_every_compact_section_page_has_a_token_budget(section, vocabulary, display):
    for source in (vocabulary, display):
        offset = 0
        while True:
            result = lookup(source, section=section, offset=offset)
            envelope = {"origin": "https://api.modelspec.dev/v1/vocabulary?section=" + section,
                        "status": 200, "body": result[section]}
            assert tokens(envelope) <= 4000, (section, offset)
            if len(result[section]) < PAGE_SIZE:
                break
            offset += PAGE_SIZE


def test_starter_is_derived_from_all_40_template_specs(vocabulary):
    assert len(vocabulary["templates"]) == 40
    assert starter_ids(vocabulary) == [
        "model.class", "offering.cost_per_task", "model.lifecycle", "model.context_window",
        "offering.speed.throughput", "licence.commercial_use", "model.weights_openness",
        "offering.data.trains_on_customer_data", "offering.attestation.baa",
        "offering.data.zero_retention", "offering.region",
    ]
    assert 10 <= len(lookup(vocabulary)["starter"]) <= 15
    altered = copy.deepcopy(vocabulary)
    altered["templates"] = [{"spec": {"where": ["model.context_window >= 4000"]}}]
    assert starter_ids(altered) == ["model.context_window"]


def test_compact_facets_have_finite_allowed_values_even_without_observations(vocabulary):
    facet = next(f for f in vocabulary["facets"] if f["id"] == "model.weights_openness")
    assert "closed_weights" in facet["allowed_values"]
    empty = copy.deepcopy(vocabulary)
    empty["facets"] = [facet | {"known": 0, "values": []}]
    row = lookup(empty, section="facets")["facets"][0]
    assert row["allowed_values"] == facet["allowed_values"]
    assert set(row) == {"id", "label", "definition", "value_type", "allowed_values"}
    assert "\n" not in row["definition"]


def test_search_ids_intersection_full_detail_and_pages(display):
    source = {"facets": [
        {"id": "x", "label": "Long Context", "definition": "First sentence. More details.", "value_type": "number", "operators": [">="]},
        {"id": "model.context", "label": "Window", "value_type": "number"},
        {"id": "cost", "label": "Price", "value_type": "number"},
    ]}
    assert [row["id"] for row in lookup(source, section="facets", search="CONTEXT")["facets"]] == ["x", "model.context"]
    assert lookup(source, section="facets", search="CONTEXT", ids=["x", "cost"])["facets"] == [source["facets"][0]]
    assert lookup(source, section="facets", ids=["missing"])["facets"] == []
    assert lookup(source, section="facets", detail="full", limit=1)["facets"] == source["facets"]
    assert lookup(source, section="facets", limit=1, offset=1)["facets"] == [source["facets"][1]]
    assert lookup(source, section="facets", offset=3)["facets"] == []
    assert lookup(source, section="facets")["facets"][0]["definition"] == "First sentence."
    assert lookup({"models": {"lab/id": {"display_name": "Friendly Model", "lab": "lab"}}}, section="models", search="FRIENDLY") == {"models": {"lab/id": {"display_name": "Friendly Model"}}}
    assert lookup({"models": {"lab/id": {"display_name": None}}}, section="models", search="NONE") == {"models": {}}
    assert lookup({"providers": {"id": "Provider Name"}}, section="providers", search="NAME") == {"providers": {"id": "Provider Name"}}


@pytest.mark.parametrize("scored", [1, 2, 3])
def test_full_and_compact_cannot_escape_trim_allowances(scored):
    source = {"facets": [{"id": "number", "value_type": "number", "known": 9, "range": {"min": 123.456, "max": 123.456}}],
              "models": {"lab/private": {"display_name": "Private", "price": 123.456, "score": 98.765}},
              "benchmarks": [{"id": "b", "models": scored, "range": {"min": 98.765, "max": 99.765}}]}
    public = trim(source, model_ids={"lab/private"}, facet_values={})
    for args in ({}, {"detail": "full"}, {"ids": ["b", "number", "lab/private"]}):
        for section in ("facets", "models", "benchmarks"):
            result = lookup(public, section=section, **args)[section]
            encoded = json.dumps(result)
            assert "123.456" not in encoded
            for forbidden in ('"known"', '"count"', '"models"', '"price"', '"score"'):
                assert forbidden not in encoded
            if section != "benchmarks" or scored < 3 or not args:
                assert "98.765" not in encoded
    assert lookup(public, section="benchmarks", detail="full")["benchmarks"] == public["benchmarks"]


def test_http_keeps_the_page_bytes_and_handles_optional_queries(monkeypatch, display):
    from tests.test_feedback import entry as entry_fixture, Request
    # Whitespace deliberately differs from the lookup serializer.
    raw = (json.dumps(display, indent=3) + "\n").encode()
    monkeypatch.setitem(sys.modules, "bundled_data", SimpleNamespace(read=lambda path: raw
                        if path == "/api/decision/vocabulary.json" else None))
    context = entry_fixture.__wrapped__()
    entry = next(context)
    worker = entry.Default()
    worker.env = SimpleNamespace()

    def fetch(query="", method="GET"):
        request = Request(method, headers={"Origin": "https://modelspec.dev"})
        request.url = "https://api.modelspec.dev/v1/vocabulary" + query
        return asyncio.run(worker.fetch(request))

    try:
        assert fetch().body == raw.decode()
        assert fetch("?detail=full&section=facets").json()["facets"] == display["facets"]
        assert fetch("?section=facets&search=CONTEXT").json()["facets"] == lookup(display, section="facets", search="CONTEXT")["facets"]
        selected = fetch("?section=facets&id=model.context_window&ids=model.class,missing&ids=model.class").json()["facets"]
        assert {row["id"] for row in selected} == {"model.context_window", "model.class"}
        assert fetch("?section=starter", "HEAD").body is None
        assert set(fetch("?section=starter").json()) == {"starter", "facets", "domains", "templates", "models", "estate"}
        for query in ("?section=bad", "?detail=bad", "?limit=0", "?limit=21", "?offset=-1", "?offset=1.5"):
            response = fetch(query)
            assert response.status == 400
            assert response.json()["error"]["code"] == "invalid_request"
    finally:
        context.close()


def test_openapi_documents_query_lookup_without_changing_legacy_schema(monkeypatch):
    import yaml
    from api.worker import openapi
    monkeypatch.setenv("DATA_SPLIT_ENABLED", "true")
    operation = yaml.safe_load(openapi.render())["paths"]["/v1/vocabulary"]["get"]
    assert {p["name"] for p in operation["parameters"]} == {"section", "search", "id", "ids", "detail", "offset", "limit"}
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["required"] == ["facets", "domains", "templates", "models", "estate"]


def test_lookup_caps_ids_and_tolerates_a_template_without_a_spec():
    vocabulary = {"facets": [{"id": "a", "label": "A"}], "templates": [{"id": "t"}]}
    assert starter_ids(vocabulary) == []
    with pytest.raises(ValueError):
        lookup(vocabulary, section="facets", ids=[str(i) for i in range(101)])
    assert lookup(vocabulary, section="facets", ids=["a", "a"])["facets"]
