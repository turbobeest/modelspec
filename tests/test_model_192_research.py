"""MODEL-192 research coverage and collection guards."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import yaml

from decision.excluded import excluded_sources
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import Claim, StructuredDataExtractor, compare

ROOT = Path(__file__).parents[1]
REPORT = ROOT / "docs" / "research" / "refinements" / "model-192-coverage.yaml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_research_reports_every_premier_model_and_candidate_source() -> None:
    report = _load(REPORT)
    premier = _load(ROOT / "premier" / "slice-1.yaml")
    expected = {row["model_id"] for row in premier["models"]}

    assert report["ticket"] == "MODEL-192"
    assert report["read_date"] == "2026-09-28"
    assert {row["model_id"] for row in report["coverage"]} == expected

    candidates = {row["id"]: row for row in report["candidate_sources"]}
    assert {
        "swe-bench-multilingual",
        "multi-swe-bench",
        "aider-polyglot",
        "multipl-e",
        "finance-benchmark-v2",
        "legalbench",
        "tw-legalbench",
    } <= candidates.keys()
    assert {row["domain"] for row in candidates.values()} >= {
        "software_engineering",
        "finance",
        "legal",
    }

    for source in candidates.values():
        assert source["url"].startswith("https://")
        assert source["terms_url"].startswith("https://")
        assert source["read_date"] == "2026-09-28"
        assert source["reuse"] in {"permitted", "not_permitted", "unclear"}
        assert source["lineup_matches"] >= 0
        assert not excluded_sources().url(source["url"]), source["id"]

    assert candidates["swe-bench-multilingual"]["reuse"] == "not_permitted"
    assert candidates["finance-benchmark-v2"]["reuse"] == "permitted"
    assert candidates["finance-benchmark-v2"]["lineup_matches"] == 8


def test_coverage_uses_exact_lineup_identities_and_language_rows_have_subcategories() -> None:
    report = _load(REPORT)
    candidate_ids = {row["id"] for row in report["candidate_sources"]}
    registered_ids = {
        row.get("registry_source_id", row["id"])
        for row in report["candidate_sources"]
    }
    for model in report["coverage"]:
        for domain in ("coding_languages", "finance", "legal"):
            item = model[domain]
            assert item["state"] in {"known", "not_disclosed"}
            assert set(item["sources"]) <= candidate_ids

    for change in report["collected_evidence"]:
        if change["domain"] == "software_engineering":
            assert change["sub_category"]
        assert change["source_id"] in registered_ids
        assert urlparse(change["source_url"]).hostname

    finance = [row for row in report["collected_evidence"] if row["domain"] == "finance"]
    assert len(finance) == 8
    assert {row["source_id"] for row in finance} == {"model-192-finance-benchmark-v2"}


def test_report_lists_every_model_card_change() -> None:
    report = _load(REPORT)
    assert isinstance(report["card_changes"], list)
    changed_cards = {row["card"] for row in report["collected_evidence"]}
    assert changed_cards == {row["card"] for row in report["card_changes"]}


def test_finance_projection_replays_unit_and_harness() -> None:
    body = yaml.safe_dump({
        "rows": [{"model": "lab/model", "pass_at_1": 91.2, "unit": "percent",
                  "harness": "unregistered", "date": "2026-09-28"}],
    })
    # JSON and YAML mappings normalize to the same structured row shape.
    import json
    claim = Claim(
        target=TargetRef(kind="evidence", id="x"), subject="lab/model",
        names=("lab/model",), field="finance_benchmark_v2", label="pass_at_1",
        value=91.2, unit="percent",
        conditions={"effort": None, "harness": "unregistered", "date": "2026-09-28"},
        collector=VerificationActor(agent="collector", model_family="openai", method="test"),
        sources=(SourceRef(source_id="s", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["rows"]),),
    )
    readings = StructuredDataExtractor().extract(
        claim, json.dumps(yaml.safe_load(body))
    )
    assert compare(claim, readings) == []
