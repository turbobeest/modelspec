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
from typer.testing import CliRunner

from cli.modelspec import cli as cli_mod
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


PAGE_SNAPSHOT_KEY = b"model-111-page-parity"


@pytest.fixture(scope="module")
def page_snapshot_bytes():
    """A signed snapshot that knows every benchmark the fixture vocabulary names."""
    from datetime import date

    from decision.snapshot import SnapshotInputs, build_snapshot
    from tests.snapshot_records import SOURCES, evidence, model

    benchmarks = [row["id"] for row in VOCABULARY["benchmarks"]]
    built = build_snapshot(SnapshotInputs(
        models=[model("lab/a"), model("lab/b")],
        offerings=[],
        evidence=[evidence(m, b, score) for b in benchmarks
                  for m, score in (("lab/a", 70.0), ("lab/b", 60.0))],
        sources=SOURCES,
        benchmark_domains={row["id"]: [(d["id"], d["directness"]) for d in row["domains"]]
                           for row in VOCABULARY["benchmarks"]},
    ), gate=False, as_of=date(2026, 9, 25))
    return built.to_bytes(key=PAGE_SNAPSHOT_KEY)


@pytest.fixture(scope="module")
def worker_snapshot(page_snapshot_bytes):
    from decision.snapshot import load_snapshot_bytes

    return load_snapshot_bytes(
        page_snapshot_bytes, key=PAGE_SNAPSHOT_KEY, source="page specs"
    )


@pytest.fixture(scope="module")
def decide_service():
    import importlib.util
    import sys

    src = Path(__file__).resolve().parents[1] / "api" / "worker" / "src"
    spec = importlib.util.spec_from_file_location("page_specs_decide_service",
                                                  src / "decide_service.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("page_specs_decide_service", module)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("row", GOLDEN, ids=[row["name"] for row in GOLDEN])
def test_the_worker_answers_the_page_spec(row, worker_snapshot, decide_service):
    """What the Worker does with it, not only what the registry parses: no 400.

    On 2026-09-25 two next-question probes came back HTTP 400 from the live
    Worker. The registry parse above could not have caught a refusal that
    depends on the Worker's own facet lookup, which resolves benchmarks
    against the loaded snapshot; this runs each spec through that path.
    """
    status, body = decide_service.decide(row["spec"], worker_snapshot)
    assert status == 200, body.get("error")


@pytest.mark.parametrize("row", GOLDEN, ids=[row["name"] for row in GOLDEN])
def test_the_page_spec_has_byte_identical_cli_and_worker_output(
    row, page_snapshot_bytes, worker_snapshot, decide_service, tmp_path
):
    """The page mapping, CLI, and Worker meet at one byte-identical decision."""
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(page_snapshot_bytes)
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(row["spec"]), encoding="utf-8")

    cli = CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), "--json"],
        env={"MODELSPEC_SNAPSHOT_KEY": PAGE_SNAPSHOT_KEY.decode()},
    )
    assert cli.exit_code == 0, cli.output
    status, body = decide_service.decide(row["spec"], worker_snapshot)
    assert status == 200, body.get("error")
    assert decide_service.serialise(body) == cli.stdout.encode("utf-8")
