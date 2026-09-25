"""The recall specs and reporting runner form one non-gating smoke test."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from decision.contract import parse_spec
from decision.registry import default as default_registry
from decision.snapshot import SnapshotInputs, build_snapshot
from scripts.recall_run import run
from tests.snapshot_records import SOURCES, evidence, model, offering

HERE = Path(__file__).resolve().parent
IDS = [f"Q{number:02d}" for number in range(1, 21)]


def test_all_twenty_contract_specs_parse() -> None:
    registry = default_registry()
    paths = sorted((HERE / "specs").glob("Q*.yaml"))

    assert [path.stem for path in paths] == IDS
    for path in paths:
        spec = parse_spec(path.read_text(encoding="utf-8"), facets=registry.facet)
        assert spec.explain == "full"


def test_runner_reports_against_a_fixture_snapshot(tmp_path: Path) -> None:
    snapshot = build_snapshot(
        SnapshotInputs(
            models=[model("lab/alpha")],
            offerings=[offering("lab/alpha")],
            evidence=[evidence("lab/alpha", "swe_bench_pro", 55.0)],
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        registry=default_registry(),
        as_of=date(2026, 9, 24),
    )
    snapshot_file = tmp_path / "fixture-snapshot.json.gz"
    snapshot.write(snapshot_file)

    result = run(
        root=Path(__file__).resolve().parents[2],
        snapshot_file=snapshot_file,
        output_dir=tmp_path / "reports",
        report_date=date(2026, 9, 25),
    )

    assert result.markdown_path.exists()
    assert result.json_path.exists()
    assert len(result.questions) == 20
    assert {row.verdict for row in result.questions} <= {"pass", "partial", "fail"}
    assert "This report does not gate CI" in result.markdown_path.read_text(encoding="utf-8")


def test_the_ungated_fallback_keeps_the_premier_lineup(monkeypatch, tmp_path: Path) -> None:
    import scripts.recall_run as recall
    from decision.snapshot import CompletenessError, Gap

    calls = []
    fixture = build_snapshot(
        SnapshotInputs(models=[model("lab/alpha")], sources=SOURCES), as_of=date(2026, 9, 24)
    )

    def fake_build(root, *, premier, as_of, registry, gate=True):
        calls.append((premier, gate))
        if gate:
            raise CompletenessError([Gap("lab/alpha", "lab/alpha", "model.class", "unknown")])
        return fixture

    monkeypatch.setattr(recall, "build_from_repo", fake_build)
    _, gaps = recall._snapshot(
        root=tmp_path, snapshot_file=None, report_date=date(2026, 9, 25),
        registry=default_registry(),
    )
    premier = tmp_path / "premier" / "slice-1.yaml"
    assert calls == [(premier, True), (premier, False)]
    assert len(gaps) == 1


def test_the_direct_detector_reads_directness_against_the_request() -> None:
    from decision.snapshot import load_snapshot_bytes
    from scripts.recall_run import _direct_objective_has_a_value

    registry = default_registry()
    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/alpha")],
            evidence=[evidence("lab/alpha", "terminal_bench_v4_0", 60.0)],
            sources=SOURCES,
            benchmark_domains={"terminal_bench_v4_0": [
                ("agentic_tool_use", "direct"), ("software_engineering", "proxy")]},
        ),
        as_of=date(2026, 9, 24),
    )
    index = load_snapshot_bytes(built.to_bytes(key=None), key=None)

    def asks(capability: str):
        return parse_spec({
            "spec_version": 1,
            "capabilities": {capability: "required"},
            "optimize": {"max": "terminal_bench_v4_0 @direct"},
        }, facets=registry.facet)

    assert _direct_objective_has_a_value(asks("agentic_tool_use"), index, {"lab/alpha"}, registry)
    assert not _direct_objective_has_a_value(
        asks("software_engineering"), index, {"lab/alpha"}, registry)
