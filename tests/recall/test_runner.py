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
