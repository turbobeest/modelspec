"""Every spec the decide page can build is a valid contract spec (MODEL-153).

`web/src/decide/__tests__/vocabulary.test.ts` generates every spec the page
can send from the vocabulary fixture (the default task, each template, every
"+ add condition" option, every next question, every facet-editor operator,
and every next-question probe on the default task and each template)
and pins them in `web/src/decide/__fixtures__/ui-specs.json`. This test parses
each one with the Python contract and the facet registry, which the TypeScript
side cannot reach. Regenerate the golden file with
`UPDATE_GOLDEN=1 npx vitest run src/decide/__tests__/vocabulary.test.ts`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from decision.contract import parse_spec
from decision.registry import facet as registry_facet

WEB = Path(__file__).resolve().parents[1] / "web" / "src" / "decide" / "__fixtures__"
GOLDEN = json.loads((WEB / "ui-specs.json").read_text(encoding="utf-8"))
VOCABULARY = json.loads((WEB / "vocabulary.json").read_text(encoding="utf-8"))


def test_the_golden_file_covers_the_default_task_and_every_template():
    names = {row["name"] for row in GOLDEN}
    assert "default task" in names
    assert {n for n in names if n.startswith("template ")} >= {
        "template budget-agent", "template private"}
    assert len(GOLDEN) > 60
    assert any(n.startswith("probe default task ") for n in names)


@pytest.mark.parametrize("row", GOLDEN, ids=[row["name"] for row in GOLDEN])
def test_the_page_spec_parses_with_the_registry(row):
    spec = parse_spec(row["spec"], facets=registry_facet)
    assert spec.task_tokens is not None


def test_the_web_fixture_has_the_shape_the_builder_writes():
    """The fixture is a vocabulary.json; a field the builder renames breaks here."""
    from datetime import date

    from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
    from decision.vocabulary import build_vocabulary
    from tests.snapshot_records import SOURCES, evidence, model

    built = build_snapshot(SnapshotInputs(
        models=[model("lab/a")], offerings=[],
        evidence=[evidence("lab/a", "swe_bench_verified", 70.0)],
        sources=SOURCES,
        benchmark_domains={"swe_bench_verified": [("software_engineering", "direct")]},
    ), gate=False, as_of=date(2026, 9, 24))
    fresh = build_vocabulary(load_snapshot_bytes(built.to_bytes(key=None), key=None))
    assert set(VOCABULARY) == set(fresh)
    assert set(VOCABULARY["benchmarks"][0]) == set(fresh["benchmarks"][0])
    assert set(VOCABULARY["domains"][0]) == set(fresh["domains"][0])
    fixture_facets = {row["id"]: set(row) for row in VOCABULARY["facets"]}
    for row in fresh["facets"]:
        assert fixture_facets[row["id"]] <= set(row) | {"range", "values", "literals"}, row["id"]
        assert set(row) <= fixture_facets[row["id"]] | {"range", "values", "literals"}, row["id"]
