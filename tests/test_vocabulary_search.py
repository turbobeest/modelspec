"""Vocabulary discovery through Python and HTTP (MODEL-319)."""
from __future__ import annotations

import asyncio
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode

import pytest

from api.worker.src.display_vocabulary import lookup, trim
from decision.registry import default
from tests.test_compact_vocabulary import tokens
from tests.test_decision_vocabulary import snapshot, vocabulary  # noqa: F401

SEARCHED = ["facets", "domains", "refinements", "benchmarks", "templates", "task_types",
            "estate", "providers", "vendors", "models", "template_categories", "template_tiers"]
SHARED = Path(__file__).resolve().parents[1] / "web/src/decide/__fixtures__/vocabulary.json"


def display_of(source):
    registry = default()
    values = {facet.id: ([True, False] if facet.value_type.kind == "boolean"
                         else sorted(registry.allowed_values(facet) or ()))
              for facet in registry.facets()}
    return trim(source, model_ids=set(source["models"]), facet_values=values)


@pytest.fixture(scope="module", params=["built", "shared"])
def display(request, vocabulary):
    shared = json.loads(SHARED.read_text())
    source = vocabulary if request.param == "built" else shared
    if request.param == "built":
        source = {**source, "domains": [*source["domains"],
                  next(row for row in shared["domains"] if row["id"] == "chat_preference")]}
    return display_of(source)


@pytest.fixture
def http(monkeypatch, display):
    from tests.test_feedback import Request, entry as entry_fixture

    raw = (json.dumps(display, indent=3) + "\n").encode()
    monkeypatch.setitem(sys.modules, "bundled_data", SimpleNamespace(
        read=lambda path: raw if path == "/api/decision/vocabulary.json" else None))
    context = entry_fixture.__wrapped__()
    entry = next(context)
    worker = entry.Default()
    worker.env = SimpleNamespace()

    def fetch(query=""):
        request = Request("GET", headers={"Origin": "https://modelspec.dev"})
        request.url = "https://api.modelspec.dev/v1/vocabulary" + query
        response = asyncio.run(worker.fetch(request))
        assert response.status == 200
        return response

    try:
        yield fetch, raw.decode()
    finally:
        context.close()


def assert_query(result, query):
    assert result.get("matches") is not None, result
    matches = result["matches"]
    if query == "price":
        assert {"section": "facets", "id": "offering.price.input", "label": "Input price",
                "matched": "id"} in matches
        assert "offering.price.input" in [row["id"] for row in result["facets"]]
    elif query == "4090":
        assert {"section": "facets", "id": "model.fits_hardware", "label": "Fits hardware",
                "matched": "value", "value": "nvidia_rtx_4090"} in matches
        assert {"section": "estate", "id": "nvidia_rtx_4090", "matched": "id"} in matches
        assert result["estate"]["devices"] == ["nvidia_rtx_4090"]
        hardware = next(row for row in result["facets"] if row["id"] == "model.fits_hardware")
        assert "nvidia_rtx_3090" in hardware["allowed_values"]
    elif query == "chat":
        assert {"section": "domains", "id": "chat_preference", "label": "Chat and preference",
                "matched": "id"} in matches
        assert "chat_preference" in [row["id"] for row in result["domains"]]
        assert not any(row["section"] == "benchmarks" for row in matches)
    else:
        assert matches == [{"section": "facets", "id": "offering.price.input",
                            "label": "Input price", "matched": "id"}]
        assert result["facets"][0]["operators"] == ["=", "!=", "<", "<=", ">", ">=", "between", "known"]


@pytest.mark.parametrize("query", ["price", "4090", "chat", "offering.price.input"])
@pytest.mark.parametrize("section", [None, "starter"])
@pytest.mark.parametrize("interface", ["lookup", "http"])
def test_default_and_explicit_starter_find_terms_across_sections(display, http, query, section, interface):
    args = {} if section is None else {"section": section}
    params = {} if section is None else {"section": section}
    if query == "offering.price.input":
        args["ids"] = [query]
        params["id"] = query
    else:
        args["search"] = query
        params["search"] = query
    fetch, _ = http
    result = lookup(display, **args) if interface == "lookup" else fetch("?" + urlencode(params)).json()
    assert_query(result, query)


@pytest.mark.parametrize("interface", ["lookup", "facets", "http"])
def test_every_registered_display_facet_resolves_exactly_in_lookup_and_http(display, http, interface):
    fetch, _ = http
    by_id = {row["id"]: row for row in display["facets"]}
    facet_ids = {facet.id for facet in default().facets()} & by_id.keys()
    assert {"offering.price.input", "model.fits_hardware"} <= facet_ids
    for fid in sorted(facet_ids):
        if interface == "http":
            result = fetch("?" + urlencode({"id": fid})).json()
        else:
            result = lookup(display, ids=[fid], **({"section": "facets"} if interface == "facets" else {}))
        assert result.get("facets") == [by_id[fid]], fid
        assert result.get("matches") == [{"section": "facets", "id": fid,
                                          "label": by_id[fid]["label"], "matched": "id"}], fid


def test_misses_explain_the_search_and_suggest_price_ids(display, http):
    fetch, _ = http
    for result in (lookup(display, search="zzzqqq"), fetch("?search=zzzqqq").json()):
        assert result.get("matches") == []
        assert result["total"] == 0
        assert result["searched"] == SEARCHED
        assert result["starter"] == []
        assert result["spec"] == {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}}
        assert "suggestions" in result
        assert "retry" in result["next"]
        assert "id, label, definition or values" in result["message"]
        assert all(section in result["message"] for section in SEARCHED)
    for result in (lookup(display, search="pirce"), fetch("?search=pirce").json()):
        assert any(item["section"] == "facets" and item["id"].startswith("offering.price.")
                   for item in result.get("suggestions", [])), result
        assert len(result["suggestions"]) <= 5
    for result in (lookup(display, ids=["offering.price.inptu"]),
                   fetch("?id=offering.price.inptu").json()):
        assert {"section": "facets", "id": "offering.price.input"} in result.get("suggestions", []), result


@pytest.mark.parametrize("search", ["RTX 4090", "rtx_4090", "Offering.Price.Input"])
def test_search_normalizes_case_and_separators(display, http, search):
    fetch, _ = http
    for result in (lookup(display, search=search), fetch("?" + urlencode({"search": search})).json()):
        ids = {row["id"] for row in result.get("matches", [])}
        assert ("offering.price.input" if "Offering" in search else "model.fits_hardware") in ids
        if "Offering" not in search:
            assert "nvidia_rtx_4090" in ids


def test_scoped_search_retains_rows_and_suggests_other_sections(display):
    context = lookup(display, section="facets", search="CONTEXT")
    expected = next(row for row in display["facets"] if row["id"] == "model.context_window")
    assert expected["id"] in [row["id"] for row in context["facets"]]
    miss = lookup(display, section="domains", search="price")
    assert miss["domains"] == []
    assert miss.get("searched") == ["domains"]
    assert miss.get("matches") == []
    assert {"section": "facets", "id": "offering.price.input"} in miss.get("suggestions", [])
    assert "domains" in miss["message"]


def test_plain_requests_keep_the_original_bytes_and_starter_body(display, http):
    fetch, raw = http
    assert fetch().body == raw
    expected = {"facets": [], "domains": [], "templates": [], "models": {}, "estate": {},
                "starter": lookup(display)["starter"],
                "next": "next: call decide with this; refine from reading",
                "spec": {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}}}
    assert fetch("?section=starter").body == json.dumps(expected, ensure_ascii=False)
    assert not ({"matches", "total", "searched", "suggestions", "message"} & lookup(display).keys())
    source = {"facets": [{"id": "x", "label": "Long Context"}, {"id": "model.context", "label": "Window"}]}
    assert lookup(source, section="facets", search="CONTEXT")["facets"] == source["facets"]


def test_cross_section_pages_stay_within_the_envelope_budget(display, http):
    fetch, _ = http
    first = lookup(display, search="a")
    assert first.get("total", 0) > 20
    seen = []
    for offset in range(0, first["total"], 20):
        result = lookup(display, search="a", offset=offset)
        envelope = {"origin": "https://api.modelspec.dev/v1/vocabulary?search=a", "status": 200, "body": result}
        assert tokens(envelope) <= 4000, (offset, tokens(envelope))
        response = fetch(f"?search=a&offset={offset}").json()
        assert tokens({**envelope, "body": response}) <= 4000, (offset, tokens(response))
        assert len(result["matches"]) <= 20
        assert result["total"] == first["total"]
        for match in result["matches"]:
            section = match["section"]
            rows = result[section]
            if section == "estate":
                assert any(match["id"] in [row.get("id") if isinstance(row, dict) else row for row in group]
                           for group in rows.values())
            elif isinstance(rows, dict):
                assert match["id"] in rows
            else:
                assert match["id"] in [row.get("id") if isinstance(row, dict) else row for row in rows]
        seen.extend((row["section"], row["id"]) for row in result["matches"])
    assert len(seen) == len(set(seen)) == first["total"]


def test_search_fields_ranking_intersection_and_exact_ids():
    source = {
        "facets": [
            {"id": "value_hit", "label": "Device", "values": [{"value": "rtx", "label": "RTX 4090"}]},
            {"id": "definition_hit", "definition": "Uses rtx"},
            {"id": "label_hit", "label": "RTX"},
            {"id": "id.rtx", "label": "Other"},
            {"id": "rtx", "label": "Exact"},
        ],
        "domains": [{"id": "domain_rtx", "name": "Other"}],
        "benchmarks": [{"id": "arena", "name": "Arena", "domains": [{"id": "rtx"}]}],
        "templates": [{"id": "template", "name": "Example", "purpose": "rtx"}],
        "estate": {"providers": [], "devices": [], "plans": [{"id": "plus", "provider": "openai", "name": "ChatGPT Plus"}]},
    }
    result = lookup(source, search="rtx")
    assert [row["id"] for row in result.get("matches", [])] == [
        "rtx", "id.rtx", "domain_rtx", "label_hit", "definition_hit", "template", "value_hit"]
    assert [row["matched"] for row in result["matches"]] == ["id", "id", "id", "label", "definition", "definition", "value"]
    assert result["matches"][-1]["value"] == "rtx"
    assert "suggestions" not in result and "message" not in result
    page = lookup(source, search="rtx", offset=1, limit=2, detail="full")
    assert [row["id"] for row in page["matches"]] == ["id.rtx", "domain_rtx"]
    assert page["facets"] == [source["facets"][3]]
    assert page["domains"] == source["domains"]
    intersect = lookup(source, search="rtx", ids=["label_hit", "plus"])
    assert [row["id"] for row in intersect["matches"]] == ["label_hit"]
    assert lookup(source, ids=["RTX"]).get("matches") == []
    assert lookup(source, search="plus openai")["estate"]["plans"] == [{"id": "plus", "name": "ChatGPT Plus"}]
    assert lookup(source, section="estate", search="chat")["estate"]["plans"] == [{"id": "plus", "name": "ChatGPT Plus"}]
    assert {"section": "facets", "id": "rtx"} in lookup(source, search="rtxx")["suggestions"]
    assert {"section": "facets", "id": "value_hit", "value": "rtx"} in lookup(source, search="rtxx")["suggestions"]


def test_field_coverage_and_suggestions_are_deterministic():
    source = {
        "facets": [{"id": "facet", "allowed_values": ["violet"], "definition": "Useful on lilac"}],
        "domains": [{"id": "domain", "name": "Lilac"}],
        "refinements": [{"id": "refinement", "definition": "Lilac"}],
        "benchmarks": [{"id": "benchmark", "name": "Lilac"}],
        "templates": [{"id": "template", "category": "Lilac", "tier": "small"}],
        "task_types": ["lilac_task"],
        "estate": {"providers": ["lilac_provider"], "devices": ["lilac_device"], "plans": []},
        "providers": {"p": "Lilac"}, "vendors": {"v": "Lilac"},
        "models": {"lab/m": {"display_name": "Lilac"}},
        "template_categories": [{"id": "category", "name": "Lilac"}],
        "template_tiers": [{"id": "tier", "name": "Lilac"}],
        "coverage": {"lilac": 42},
    }
    untouched = copy.deepcopy(source)
    result = lookup(source, search="lilac")
    assert result.get("total") == 13
    assert "coverage" not in result
    assert lookup(source, search="violet")["matches"] == [
        {"section": "facets", "id": "facet", "matched": "value", "value": "violet"}]
    miss = lookup(source, section="domains", search="violett")
    # A value suggestion names its facet, so retrying with that id resolves.
    assert miss["suggestions"][0] == {"section": "facets", "id": "facet", "value": "violet"}
    assert "facet (value violet)" in miss["message"]
    assert [row["id"] for row in lookup(source, ids=[miss["suggestions"][0]["id"]])["facets"]] == ["facet"]
    ids = ["lilac_task", "lilac_device", "lilac_provider", "p", "v", "lab/m", "category", "tier"]
    assert lookup(source, ids=ids)["total"] == len(ids)
    assert lookup(source, ids=ids, limit=2)["matches"] == lookup(source, ids=ids)["matches"][:2]
    assert source == untouched


def test_openapi_adds_optional_lookup_metadata(monkeypatch):
    import yaml
    from api.worker import openapi

    monkeypatch.setenv("DATA_SPLIT_ENABLED", "true")
    operation = yaml.safe_load(openapi.render())["paths"]["/v1/vocabulary"]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert {"matches", "total", "searched", "suggestions", "message"} <= schema["properties"].keys()
    assert schema["required"] == ["facets", "domains", "templates", "models", "estate"]
    assert "every section" in next(p["description"] for p in operation["parameters"] if p["name"] == "search")


def test_oversized_terms_are_refused_and_separator_only_search_matches_nothing(display):
    with pytest.raises(ValueError):
        lookup(display, search="x" * 129)
    with pytest.raises(ValueError):
        lookup(display, ids=["x" * 129])
    assert lookup(display, search="x" * 128)["total"] == 0
    for blank in (".", "-", " ", "_./"):
        result = lookup(display, search=blank)
        assert result["total"] == 0 and result["matches"] == [], blank
        assert "message" in result


def catalogue(size=1500):
    """A catalogue-sized vocabulary whose ids and names pass the suggestion length filter."""
    return {
        "facets": [{"id": f"offering.synthetic.metric_{i:04d}", "label": f"Synthetic metric number {i:04d}",
                    "allowed_values": [f"value_{i:04d}_{j}" for j in range(3)]} for i in range(60)],
        "models": {f"lab{i % 40:02d}/model-family-{i:04d}-instruct": {"display_name": f"Model Family {i:04d} Instruct"}
                   for i in range(size)},
        "estate": {"providers": [], "devices": [f"vendor_accelerator_{i:04d}_96gb" for i in range(200)], "plans": []},
    }


def test_suggestion_work_is_bounded_by_a_cell_budget(monkeypatch):
    from api.worker.src import display_vocabulary
    cells, similarity = [0], display_vocabulary.similarity

    def counted(left, right):
        cells[0] += len(left) * len(right)
        return similarity(left, right)

    monkeypatch.setattr(display_vocabulary, "similarity", counted)
    source = catalogue()
    needles = [f"zz{i}-model-family-instruct-xyzw" for i in range(100)]  # ~30 characters each
    for args in ({"search": needles[0]}, {"ids": needles}, {"search": "q" * 128}):
        cells[0] = 0
        first = lookup(source, **args)
        assert first["total"] == 0 and len(first["suggestions"]) <= 5
        assert 0 < cells[0] <= display_vocabulary.SUGGESTION_CELLS, (args, cells[0])
        assert lookup(source, **args)["suggestions"] == first["suggestions"]
    # Short typos still reach every section within the budget.
    cells[0] = 0
    assert lookup(source, search="instrct")["suggestions"]
    assert cells[0] <= display_vocabulary.SUGGESTION_CELLS


def test_boolean_value_suggestions_render_like_json():
    miss = lookup({"facets": [{"id": "flag", "allowed_values": [True, False]}]}, search="ture")
    assert miss["suggestions"][0] == {"section": "facets", "id": "flag", "value": True}
    assert "flag (value true)" in miss["message"]
