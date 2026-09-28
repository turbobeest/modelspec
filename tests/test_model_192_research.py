"""MODEL-192 research coverage and collection guards."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import pytest
import yaml

from decision.excluded import excluded_sources
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore
from decision.verify import Claim, StructuredDataExtractor, compare
from scripts import model_192_evidence

ROOT = Path(__file__).parents[1]
REPORT = ROOT / "docs" / "research" / "refinements" / "model-192-coverage.yaml"
VERIFICATION_LOG = ROOT / "verification" / "log.jsonl"
FINANCE_BENCHMARK_ID = "finance_benchmark_v2"
FINANCE_SOURCE_ID = "model-192-finance-benchmark-v2"
FINANCE_SOURCE_URL = "https://finbenchmark.ai/"

EXPECTED_FINANCE_EVIDENCE = (
    ("models/anthropic/claude-fable-5.md", 90.411),
    ("models/anthropic/claude-opus-4-6.md", 86.3014),
    ("models/anthropic/claude-opus-4-7.md", 93.1507),
    ("models/deepseek/deepseek-v4-pro.md", 89.0411),
    ("models/google/gemini-3-5-flash.md", 83.5616),
    ("models/moonshot/kimi-k3.md", 89.0411),
    ("models/openai/gpt-5-4.md", 63.0137),
    ("models/openai/gpt-5-6-sol.md", 91.7808),
)
EXPECTED_CODING_LANGUAGES = frozenset(
    {
        "C",
        "C++",
        "Go",
        "Java",
        "JavaScript",
        "TypeScript",
        "PHP",
        "Ruby",
        "Rust",
        "Python",
    }
)
SWE_BENCH_MULTILINGUAL_LANGUAGES = EXPECTED_CODING_LANGUAGES - {"Python"}


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_front_matter(path: Path) -> dict:
    _, front_matter, _ = path.read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(front_matter)


def _finance_rows(path: Path) -> list[dict]:
    card = _load_front_matter(path)
    return [
        row
        for row in card.get("benchmarks", {}).get("evidence", [])
        if row["benchmark_id"] == FINANCE_BENCHMARK_ID
    ]


def _latest_verifications() -> dict[str, dict]:
    latest = {}
    for line in VERIFICATION_LOG.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        latest[entry["target"]["id"]] = entry
    return latest


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


def test_coverage_records_every_language_for_every_lineup_model() -> None:
    report = _load(REPORT)
    candidate_ids = {row["id"] for row in report["candidate_sources"]}
    registered_ids = {
        row.get("registry_source_id", row["id"])
        for row in report["candidate_sources"]
    }
    for model in report["coverage"]:
        languages = model["coding_languages"]
        assert set(languages) == EXPECTED_CODING_LANGUAGES
        for language, item in languages.items():
            expected_sources = (
                ["swe-bench-multilingual"]
                if model["model_id"] == "anthropic/claude-opus-4-6"
                and language in SWE_BENCH_MULTILINGUAL_LANGUAGES
                else []
            )
            assert item == {
                "state": "not_disclosed",
                "sources": expected_sources,
            }

        for domain in ("finance", "legal"):
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


@pytest.mark.parametrize(("card_path", "expected_score"), EXPECTED_FINANCE_EVIDENCE)
def test_collected_finance_evidence_is_filed_and_verified(
    card_path: str,
    expected_score: float,
) -> None:
    rows = _finance_rows(ROOT / card_path)
    assert len(rows) == 1
    row = rows[0]

    assert row["benchmark_id"] == FINANCE_BENCHMARK_ID
    assert row["score"] == expected_score
    assert row["unit"] == "percent"
    assert row["source_url"] == FINANCE_SOURCE_URL
    assert row["source_kind"] == "independent_evaluator"
    assert row["measured_by"] == "independent_evaluator"
    assert row["sources"] == [{
        "source_id": FINANCE_SOURCE_ID,
        "snapshot_ref": "sha256:a8d3d8dec4605e37bf43a29ef09b35b6e47a78e4bc9e64b701d620d9dfb668d7",
        "cited_regions": ["rows"],
    }]

    verification = _latest_verifications()[row["id"]]
    assert verification["outcome"] == "verified"
    assert verification["diff"] is None
    assert verification["collector"]["agent"] != verification["verifier"]["agent"]
    assert verification["collector"]["method"] != verification["verifier"]["method"]


def test_report_and_cards_contain_exactly_the_expected_finance_evidence() -> None:
    report = _load(REPORT)
    expected = dict(EXPECTED_FINANCE_EVIDENCE)
    collected = {
        row["card"]: row["score"]
        for row in report["collected_evidence"]
        if row["domain"] == "finance"
    }
    card_changes = {
        row["card"]: row["score"]
        for row in report["card_changes"]
        if row["domain"] == "finance"
    }
    actual = {}
    for path in (ROOT / "models").glob("*/*.md"):
        if f"benchmark_id: {FINANCE_BENCHMARK_ID}" not in path.read_text(encoding="utf-8"):
            continue
        rows = _finance_rows(path)
        if rows:
            assert len(rows) == 1
            actual[str(path.relative_to(ROOT))] = rows[0]["score"]

    assert collected == expected
    assert card_changes == expected
    assert actual == expected


def test_finance_projection_replays_unit_and_harness() -> None:
    body = yaml.safe_dump({
        "rows": [{"model": "lab/model", "pass_at_1": 91.2, "unit": "percent",
                  "harness": "unregistered", "date": "2026-09-28"}],
    })
    # JSON and YAML mappings normalize to the same structured row shape.
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


def test_finance_projection_links_to_its_retained_source_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = (
        b'<script>\\"model_name\\":\\"model\\",'
        b'\\"provider\\":\\"lab\\",'
        b'\\"harness_version\\":\\"0.2.0\\",'
        b'\\"task_set_version\\":\\"v2\\",'
        b'\\"pass_at_1\\":0.912,'
        b'\\"completed_at\\":\\"2026-09-28T00:00:00Z\\"</script>'
    )

    class Response:
        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return raw

    monkeypatch.setattr(
        model_192_evidence.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: Response(),
    )
    store = CopyStore(tmp_path / "copies")

    rows, projection_ref = model_192_evidence.fetch_rows(store)

    projection = json.loads(store.get(projection_ref))
    fetched_copy = projection["provenance"]["fetched_copy"]
    assert store.get(fetched_copy) == raw
    assert projection["rows"] == rows
