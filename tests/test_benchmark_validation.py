"""Synthetic benchmark pages exercise validation and all-file audit boundaries."""

from datetime import date

import pytest

from decision.registry import load as load_registry
from pipeline.load import split_front_matter
from schema.benchmark import REQUIRED_SECTIONS
from scripts.benchmarks.validate import check
from scripts.data_trust.catalogue import calibrate, load
from scripts.data_trust.invariants import run


@pytest.fixture
def page(tmp_path):
    path = tmp_path / "benchmarks" / "example.md"
    path.parent.mkdir()
    body = "\n".join(f"## {heading}\n" + "A measured task. " * 20
                     for heading in REQUIRED_SECTIONS["benchmark"])
    text = """---
id: example
name: Example benchmark
category: coding
summary: A synthetic benchmark for validation.
measures: A synthetic collection of tasks used to verify benchmark validation.
sources: [{url: 'https://example.test/paper', accessed: '2026-11-09'}]
freshness: {researched: '2026-11-09', researched_by: tester}
---
""" + body
    path.write_text(text)
    assert check(path) == []
    return path


def insert_mapping(page, mapping):
    text = page.read_text()
    if mapping.startswith("freshness:"):
        text = text.replace("freshness: {researched: '2026-11-09', researched_by: tester}", mapping)
    else:
        text = text.replace("\n---\n", f"\n{mapping}\n---\n", 1)
    page.write_text(text)


MAPPINGS = [
    ("dataset", "dataset: {splits: train, private prose, test}"),
    ("contamination", "contamination: {note: measured, private prose}"),
    ("saturation", "saturation: {note: measured, private prose}"),
    ("freshness", "freshness: {researched: '2026-11-09', researched_by: tester, private prose}"),
]


@pytest.mark.parametrize("field,mapping", MAPPINGS)
def test_benchmark_validator_rejects_unknown_nested_key(page, field, mapping):
    insert_mapping(page, mapping)
    assert check(page) == [f"unknown_benchmark_key: {field}"]


@pytest.mark.parametrize("field,mapping", MAPPINGS)
def test_trust_inventory_reports_unknown_benchmark_key(page, field, mapping, monkeypatch):
    from decision import snapshot

    insert_mapping(page, mapping)
    root = page.parent.parent
    (root / "models").mkdir()
    (root / "models/example.md").write_text("---\nmodel_id: test/model\n---\n")
    c = load(root)
    registry = load_registry()
    inputs = snapshot.SnapshotInputs(models=[{"id": "test/model", "lifecycle": "active", "facts": []}])
    monkeypatch.setattr(snapshot, "collect_repo", lambda root: inputs)
    calibrate(c, root, registry, date(2026, 11, 9))
    findings = [f for f in run(c, registry, date(2026, 11, 9))["findings"]
                if f["rule"] == "unknown_benchmark_key"]
    assert findings == [{"id": "benchmarks/example.md", "field": field,
                         "rule": "unknown_benchmark_key", "severity": "error"}]
    assert "private prose" not in str(findings)


def test_quoted_comma_string_loads_intact(page):
    insert_mapping(page, 'dataset: {splits: "train, validation, test"}')
    assert check(page) == []
    front, _ = split_front_matter(page.read_text())
    assert front["dataset"]["splits"] == "train, validation, test"
    assert load(page.parent.parent).boards["example"]["dataset"]["splits"] == "train, validation, test"


def test_model_fields_owned_by_other_loaders_are_not_benchmark_keys(tmp_path):
    (tmp_path / "models").mkdir()
    (tmp_path / "models/example.md").write_text("""---
model_id: test/model
facts: [{id: fact-id, facet: model.context_window, value: 10, observation: {custom: value}}]
benchmarks:
  evidence: [{id: evidence-id, benchmark_id: example, score: 1, effort: high, observation: {custom: value}}]
sources: [{id: source-id, url: 'https://example.test'}]
---
""")
    assert load(tmp_path).findings == []


def test_benchmark_validator_reports_duplicate_aliases(page):
    insert_mapping(page, "aliases: [first]\naliases: [second]")
    assert check(page) == ["duplicate_yaml_key: line 10, column 1"]


@pytest.mark.parametrize("relative,content", [
    ("models/example.md", "---\nmodel_id: test/model\naliases: [first]\naliases: [second]\n---\n"),
    ("benchmarks/example.md", "---\nid: example\naliases: [first]\naliases: [second]\n---\n"),
    ("registry/sources.yaml", "sources: []\nsources: []\n"),
    ("registry/harnesses.yaml", "harnesses: []\nharnesses: []\n"),
    ("offerings/example.yaml", "- provider: test\n  facts: []\n  facts: []\n"),
    ("premier/example.yaml", "models: []\nmodels: []\n"),
])
def test_trust_duplicate_diagnostic_survives_calibration(tmp_path, monkeypatch, relative, content):
    from decision import snapshot

    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text(content)
    c = load(tmp_path)
    inputs = snapshot.SnapshotInputs()
    monkeypatch.setattr(snapshot, "collect_repo", lambda root: inputs)
    registry = load_registry()
    calibrate(c, tmp_path, registry, date(2026, 11, 9))
    findings = [f for f in run(c, registry, date(2026, 11, 9))["findings"]
                if f["rule"] == "duplicate_yaml_key"]
    assert len(findings) == 1
    assert findings[0]["id"].startswith(relative + ":")
    assert findings[0]["field"] == "document"
    assert "first" not in str(findings)


def test_calibration_keeps_the_duplicate_diagnostic_when_the_page_loads(tmp_path):
    (tmp_path / "models").mkdir()
    (tmp_path / "models/example.md").write_text("---\nmodel_id: test/model\n---\n")
    (tmp_path / "benchmarks").mkdir()
    (tmp_path / "benchmarks/example.md").write_text("---\nid: example\naliases: []\naliases: []\n---\n")
    c = load(tmp_path)
    assert c.boards["example"]["aliases"] == []
    registry = load_registry()
    calibrate(c, tmp_path, registry, date(2026, 11, 9))
    rules = {f["rule"] for f in run(c, registry, date(2026, 11, 9))["findings"]}
    assert "duplicate_yaml_key" in rules
    assert "snapshot_build" not in rules
