"""Claude Sonnet 5.5 catalogue coverage."""

from __future__ import annotations

from pathlib import Path

import yaml

from schema.card import ModelCard

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "anthropic/claude-sonnet-5-5"
READ_DATE = "2026-09-28"


def test_card_records_only_published_identity_specs_and_evidence() -> None:
    card = ModelCard.from_yaml_file(ROOT / "models/anthropic/claude-sonnet-5-5.md")

    assert card.identity.model_id == MODEL_ID
    assert card.identity.release_date == READ_DATE
    assert card.modalities.input == ["text", "image"]
    assert card.modalities.output == ["text"]
    assert card.modalities.text.context_window == 1_000_000
    assert card.modalities.text.max_output_tokens == 128_000
    assert card.cost.input == 2.0
    assert card.cost.output == 10.0
    assert card.cost.cache_read == 0.2
    assert card.cost.cache_write == 2.5

    evidence = {row.benchmark_id: row for row in card.benchmarks.evidence}
    assert {key: evidence[key].score for key in evidence} == {
        "terminal_bench_v4_0": 70.6,
        "frontiercode_v1_1": 46.2,
        "cursorbench_4": 55.5,
        "humanitys_last_exam": 64.5,
        "osworld_2_1": 80.1,
        "chartography": 61.6,
    }
    assert all(row.source_kind == "provider_self_report" for row in evidence.values())
    assert all(row.evidence_date == READ_DATE for row in evidence.values())
    assert all(row.verified_at == READ_DATE for row in evidence.values())
    assert all(row.source_url.startswith("https://www.anthropic.com/") for row in evidence.values())


def test_announced_api_bedrock_and_vertex_offerings_have_verified_prices() -> None:
    expected = {
        "anthropic": ("global", 2.0, 10.0, 0.2, 1.0, 5.0),
        "aws-bedrock": ("global-cross-region", 2.0, 10.0, 0.2, "not_offered", "not_offered"),
        "google-vertex-ai": ("global", 2.0, 10.0, 0.2, 1.0, 5.0),
    }

    for provider, values in expected.items():
        region, input_price, output_price, cache_price, batch_input, batch_output = values
        path = ROOT / "offerings" / provider / "anthropic" / "claude-sonnet-5-5.yaml"
        rows = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert len(rows) == 1
        row = rows[0]
        assert row["model"] == MODEL_ID
        assert row["provider"] == provider
        assert row["region"] == region
        facts = {fact["facet"]: fact for fact in row["facts"]}
        assert facts["offering.price.input"]["value"] == input_price
        assert facts["offering.price.output"]["value"] == output_price
        assert facts["offering.price.cached_input"]["value"] == cache_price
        assert facts["offering.price.batch_input"]["value"] == batch_input
        assert facts["offering.price.batch_output"]["value"] == batch_output
        for facet in (
            "offering.price.input",
            "offering.price.output",
            "offering.price.cached_input",
            "offering.price.batch_input",
            "offering.price.batch_output",
        ):
            assert facts[facet]["sources"]
