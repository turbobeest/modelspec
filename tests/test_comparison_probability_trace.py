"""Rounded comparison probabilities retain the exact decision values."""

from collections import Counter
from copy import deepcopy
from datetime import date
from html.parser import HTMLParser
import json

import pytest

from pipeline.comparison_pages import comparison_page
from pipeline.surface_lint import Page

DAY = date(2026, 9, 23)
LEADER = "lab/z-leader"
CHALLENGER = "lab/a-challenger"


@pytest.fixture
def comparison():
    template = {
        "id": "coding-fixture", "category": "coding", "name": "Coding fixture",
        "purpose": "Compare coding evidence.", "tradeoff": "Coding capability first.",
        "where": [], "weights": {}, "spec": {}, "teaches": "Read the intervals.",
    }
    entries = [
        {"model": model,
         "offering": {"model": model, "provider": "lab", "region": "global", "tier": "standard"},
         "score": score, "score_interval": [0.1112131415, 0.9192939495],
         "p_best": probability, "p_beats_leader": against, "cost_per_task": 0.0412,
         "estimates": [{"dimension": "software_engineering", "value": 1.234,
                        "interval": [0.123, 2.345], "benchmarks": 3, "direct_benchmarks": 2}]}
        for model, score, probability, against in (
            (LEADER, 0.8111, 0.56789123456789, None),
            (CHALLENGER, 0.7222, 0.12345678912345, 0.321987654),
        )
    ]
    decision = {
        "decision_id": "dec_probability_fixture", "snapshot": "snap_probability_fixture",
        "status": "answered", "answer": {"kind": "tied", "members": [LEADER, CHALLENGER]},
        "results": [{"offering": row["offering"], "warnings": []} for row in entries],
        "bands": {"leader": LEADER, "best": entries, "rest": [], "thin": [],
                  "basis": "Fixture probability rule."},
    }
    facts = {
        "models": [{"model": model, "facts": [], "offerings": [], "evidence": []}
                   for model in (LEADER, CHALLENGER)],
        "sources": [],
    }
    return template, decision, facts


class ProbabilitySpans(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.spans = []
        self.current = None
        self.model_row = False
        self.feed(raw)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr" and attrs.get("class") == "comparison-model":
            self.model_row = True
        if tag == "span" and "data-probability" in attrs:
            self.current = {"attrs": attrs, "text": "", "table": self.model_row}
            self.spans.append(self.current)

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag):
        if tag == "span":
            self.current = None
        if tag == "tr":
            self.model_row = False


def dataset(raw):
    nodes = [node for block in Page(raw).ld for node in json.loads(block)["@graph"]]
    datasets = [node for node in nodes if node["@type"] == "Dataset"]
    assert len(datasets) == 1
    return datasets[0]


def property_values(raw):
    rows = dataset(raw)["variableMeasured"]
    assert all(row["@type"] == "PropertyValue" for row in rows)
    assert len({row["propertyID"] for row in rows}) == len(rows)
    return {row["propertyID"]: row for row in rows}


def separate(decision):
    decision["bands"]["rest"] = [decision["bands"]["best"].pop()]
    decision["answer"] = {"kind": "separated", "members": [LEADER], "leader": LEADER}


@pytest.mark.parametrize("probability,display", [
    (None, "Unavailable"),
    (0.0, "under 1%"),
    (0.000001, "under 1%"),
    (0.009999999, "under 1%"),
    (0.01, "1%"),
    (0.014999999, "1%"),
    (0.015, "2%"),
    (0.024999999, "2%"),
    (0.025, "3%"),
    (0.994999999, "99%"),
    (0.995, "100%"),
    (1.0, "100%"),
])
def test_probability_percent_boundaries_keep_exact_trace(comparison, probability, display):
    _, decision, _ = comparison
    for row in decision["bands"]["best"]:
        row["p_best"] = probability
    decision["bands"]["best"][1]["p_beats_leader"] = probability
    raw = comparison_page(*comparison, DAY)
    spans = ProbabilitySpans(raw).spans
    assert len(spans) == 3
    assert all(span["text"] == display for span in spans)
    assert all(span["attrs"]["data-probability"] == json.dumps(probability) for span in spans)
    rows = property_values(raw)
    for property_id in (LEADER + ":p_best", CHALLENGER + ":p_best", CHALLENGER + ":p_beats_leader"):
        assert rows[property_id]["value"] == probability
        assert rows[property_id]["unitText"] == "probability"


@pytest.mark.parametrize("separated", [False, True])
def test_every_visible_probability_identifies_its_model_and_engine_field(comparison, separated):
    if separated:
        separate(comparison[1])
    spans = ProbabilitySpans(comparison_page(*comparison, DAY)).spans
    observed = Counter((span["attrs"]["data-model"], span["attrs"]["data-field"],
                        span["attrs"]["data-probability"], span["text"], span["table"])
                       for span in spans)
    expected = Counter({
        (LEADER, "p_best", "0.56789123456789", "57%", True): 1,
        (CHALLENGER, "p_best", "0.12345678912345", "12%", True): 1,
        (CHALLENGER, "p_beats_leader", "0.321987654", "32%", False): 1,
    })
    if separated:
        expected[(LEADER, "p_best", "0.56789123456789", "57%", False)] = 1
    assert observed == expected


@pytest.mark.parametrize("names", [None, {LEADER: "Zebra Pro", CHALLENGER: "Alpha <Fast> & Co"}])
def test_probability_dataset_associates_exact_values_with_model_identity(comparison, names):
    kwargs = {} if names is None else {"model_names": names}
    raw = comparison_page(*comparison, DAY, **kwargs)
    rows = property_values(raw)
    expected = {LEADER + ":p_best": 0.56789123456789,
                CHALLENGER + ":p_best": 0.12345678912345,
                CHALLENGER + ":p_beats_leader": 0.321987654}
    for property_id, probability in expected.items():
        assert rows[property_id]["value"] == probability
        assert rows[property_id]["unitText"] == "probability"
    references = []
    for node in (dataset(raw), *rows.values()):
        about = node.get("about", [])
        references.extend(about if isinstance(about, list) else [about])
    models = {item["identifier"]: item["name"] for item in references if item.get("@type") == "Thing"}
    assert {model: models[model] for model in (LEADER, CHALLENGER)} == (
        names if names is not None else {LEADER: LEADER, CHALLENGER: CHALLENGER})


@pytest.mark.parametrize("model,field,original,count", [
    (LEADER, "p_best", 0.56789123456789, 2),
    (CHALLENGER, "p_best", 0.12345678912345, 1),
    (CHALLENGER, "p_beats_leader", 0.321987654, 1),
])
def test_probability_mutation_changes_every_visible_copy_and_exact_trace(comparison, model, field, original, count):
    separate(comparison[1])
    before = comparison_page(*comparison, DAY)
    modified = deepcopy(comparison)
    decision = modified[1]
    row = next(row for band in ("best", "rest") for row in decision["bands"][band] if row["model"] == model)
    row[field] = 0.0102030405
    unchanged_input = deepcopy(modified)
    after = comparison_page(*modified, DAY)
    assert modified == unchanged_input
    assert json.dumps(original) in before
    assert json.dumps(original) not in after
    spans = [span for span in ProbabilitySpans(after).spans
             if span["attrs"]["data-model"] == model and span["attrs"]["data-field"] == field]
    assert len(spans) == count
    assert all(span["text"] == "1%" for span in spans)
    assert all(span["attrs"]["data-probability"] == "0.0102030405" for span in spans)
    property_id = model + ":" + field
    previous = property_values(before)
    updated = property_values(after)
    assert previous[property_id]["value"] == original
    assert updated[property_id]["value"] == 0.0102030405
    assert updated[property_id]["unitText"] == "probability"
    assert {key: row["value"] for key, row in updated.items() if key != property_id} == {
        key: row["value"] for key, row in previous.items() if key != property_id}


def test_probability_mutation_with_same_rounded_percent_updates_exact_trace(comparison):
    separate(comparison[1])
    before = comparison_page(*comparison, DAY)
    modified = deepcopy(comparison)
    modified[1]["bands"]["best"][0]["p_best"] = 0.57123456789123
    after = comparison_page(*modified, DAY)
    for raw, exact in ((before, "0.56789123456789"), (after, "0.57123456789123")):
        spans = [span for span in ProbabilitySpans(raw).spans
                 if span["attrs"]["data-model"] == LEADER and span["attrs"]["data-field"] == "p_best"]
        assert len(spans) == 2
        assert all(span["text"] == "57%" for span in spans)
        assert all(span["attrs"]["data-probability"] == exact for span in spans)
    assert "0.56789123456789" not in after
    previous = property_values(before)
    updated = property_values(after)
    assert previous[LEADER + ":p_best"]["value"] == 0.56789123456789
    assert updated[LEADER + ":p_best"]["value"] == 0.57123456789123
    assert {key: row["value"] for key, row in updated.items() if key != LEADER + ":p_best"} == {
        key: row["value"] for key, row in previous.items() if key != LEADER + ":p_best"}
