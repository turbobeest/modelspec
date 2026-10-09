"""MODEL-359: the MCP decide schema drops annotations and shares one condition union."""
import copy
import json
import re
from collections import Counter
from pathlib import Path

import pytest

from qa.contracts import compact_decide_schema

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/decision-contract.schema.json"
FIXTURE = ROOT / "qa/fixtures/mcp-tools.json"
BUDGET = ROOT / "mcp/test/fixtures/decide-budget.json"
CONDITION_UNION = [
    {"type": "string"},
    {"$ref": "#/$defs/Compare"},
    {"$ref": "#/$defs/Window"},
    {"$ref": "#/$defs/InSet"},
    {"$ref": "#/$defs/Known"},
    {"$ref": "#/$defs/AnyOf"},
    {"$ref": "#/$defs/AllOf"},
    {"$ref": "#/$defs/NotOf"},
]
_MAPS = ("properties", "patternProperties", "$defs")


def _decide_fixture():
    tools = json.loads(FIXTURE.read_text())["tools"]
    return next(tool for tool in tools if tool["name"] == "decide")["input_schema"]


def _reachable():
    document = json.loads(CONTRACT.read_text())
    definitions = {}
    pending = ["DecideRequest"]
    while pending:
        name = pending.pop()
        if name in definitions:
            continue
        definition = document["$defs"][name]
        definitions[name] = copy.deepcopy(definition)
        pending.extend(re.findall(r'#/\$defs/([^" ]+)', json.dumps(definition)))
    schema = {
        "$schema": document["$schema"],
        "$defs": definitions,
        "$ref": "#/$defs/DecideRequest",
    }
    defaults = json.loads(BUDGET.read_text())["request"]
    for name in ("explain", "limit", "fields"):
        schema["$defs"]["DecideRequest"]["properties"][name]["default"] = defaults[name]
    return schema


def _walk_maps(node, visit):
    if isinstance(node, list):
        for item in node:
            _walk_maps(item, visit)
        return
    if not isinstance(node, dict):
        return
    visit(node)
    for key, value in node.items():
        if key in _MAPS and isinstance(value, dict):
            for child in value.values():
                _walk_maps(child, visit)
        else:
            _walk_maps(value, visit)


def _descriptions(node):
    found = []

    def visit(schema):
        if isinstance(schema.get("description"), str):
            found.append(schema["description"])

    _walk_maps(node, visit)
    return found


def _strip(node):
    if isinstance(node, list):
        return [_strip(item) for item in node]
    if not isinstance(node, dict):
        return node
    out = {}
    for key, value in node.items():
        if key == "title" or (key == "default" and value is None):
            continue
        if key in _MAPS and isinstance(value, dict):
            out[key] = {name: _strip(child) for name, child in value.items()}
        else:
            out[key] = _strip(value)
    return out


def _expand(schema):
    union = schema["$defs"]["Condition"]["anyOf"]

    def walk(node):
        if isinstance(node, list):
            return [walk(item) for item in node]
        if not isinstance(node, dict):
            return node
        if node.get("$ref") == "#/$defs/Condition":
            siblings = {key: walk(value) for key, value in node.items() if key != "$ref"}
            return {"anyOf": copy.deepcopy(union), **siblings}
        return {key: walk(value) for key, value in node.items()}

    expanded = walk(copy.deepcopy(schema))
    del expanded["$defs"]["Condition"]
    return expanded


def _count(node, target):
    found = 0

    def walk(value):
        nonlocal found
        if isinstance(value, list):
            if value == target:
                found += 1
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            for child in value.values():
                walk(child)

    walk(node)
    return found


def test_decide_fixture_drops_annotations_and_hoists_one_condition_union():
    schema = _decide_fixture()
    titles = []
    null_defaults = []

    def visit(node):
        if "title" in node:
            titles.append(node["title"])
        if "default" in node and node["default"] is None:
            null_defaults.append(True)

    _walk_maps(schema, visit)
    assert titles == []
    assert null_defaults == []
    assert schema["$defs"]["Condition"] == {"anyOf": CONDITION_UNION}
    assert _count(schema, CONDITION_UNION) == 1
    props = schema["$defs"]["DecideRequest"]["properties"]
    assert props["explain"]["default"] == "none"
    assert props["limit"]["default"] == 10
    assert props["fields"]["default"] == ["model_rank", "cost_per_task", "estimates", "p_best"]
    assert props["snapshot"]["default"] == "latest"
    assert props["unknowns"]["default"] == "default"
    assert schema["$defs"]["EvidenceQualifiers"]["properties"]["direct"]["default"] is False
    assert schema["$defs"]["Hardware"]["properties"]["count"]["default"] == 1
    assert schema == compact_decide_schema(_reachable())


def test_decide_descriptions_stay_byte_identical_to_the_contract():
    schema = _decide_fixture()
    contract = json.loads(CONTRACT.read_text())
    compacted = _descriptions(schema)
    reachable = _descriptions(_reachable())
    published = set(_descriptions(contract))
    assert Counter(compacted) == Counter(reachable)
    assert set(compacted) <= published
    assert set(reachable) <= set(compacted)


def test_resolving_condition_reproduces_the_stripped_reachable_schema():
    assert _expand(_decide_fixture()) == _strip(_reachable())


def test_property_named_title_is_kept_and_an_absent_union_adds_nothing():
    schema = {
        "type": "object",
        "title": "Wrapper",
        "properties": {
            "title": {"type": "string", "title": "Title", "default": None},
            "count": {"type": "integer", "default": 1, "title": "Count"},
        },
        "patternProperties": {"^title$": {"title": "Pattern", "type": "string"}},
    }
    original = copy.deepcopy(schema)
    assert compact_decide_schema(schema) == {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "count": {"type": "integer", "default": 1},
        },
        "patternProperties": {"^title$": {"type": "string"}},
    }
    assert schema == original
    assert "Condition" not in compact_decide_schema({"type": "object"})


def test_changed_condition_union_is_refused():
    schema = {
        "$defs": {
            "DecideRequest": {
                "properties": {
                    "where": {
                        "items": {"anyOf": [{"type": "string"}, {"$ref": "#/$defs/Compare"}]},
                    }
                }
            }
        }
    }
    with pytest.raises(ValueError, match="condition union changed"):
        compact_decide_schema(schema)
