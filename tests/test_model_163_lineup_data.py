"""MODEL-163's rule inputs are sourced and independently verified."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from decision.model import value_hash
from scripts.model_163_local import SourceRowMismatchError, parse_memory_configuration

ROOT = Path(__file__).resolve().parents[1]
LOCAL_MODELS = {
    "google/gemma-4-26b-a4b-it",
    "google/gemma-4-31b-it",
    "google/gemma-4-e2b-it",
    "google/gemma-4-e4b-it",
    "microsoft/phi-4",
}


@pytest.fixture(scope="module")
def slice_2() -> dict:
    return yaml.safe_load((ROOT / "premier" / "inputs" / "slice-2.yaml").read_text())


@pytest.fixture(scope="module")
def latest_verifications() -> dict[tuple[str, str], dict]:
    latest = {}
    for line in (ROOT / "verification" / "log.jsonl").read_text().splitlines():
        row = json.loads(line)
        target = row["target"]
        latest[(target["kind"], target["id"])] = row
    return latest


def test_local_rule_uses_sourced_parameter_artifact_and_runtime_memory(slice_2) -> None:
    rows = slice_2["local"]["candidates"]
    assert {row["model_id"] for row in rows} == LOCAL_MODELS

    for row in rows:
        assert row["parameter_count"] > 0
        assert row["published_size_bytes"] > 0
        assert row["published_size_gb"] == pytest.approx(
            row["published_size_bytes"] / 1_000_000_000
        )
        assert row["runtime_memory_gb"] > row["published_size_gb"]
        assert row["context_tokens"] > 0
        assert row["parameter_source_url"].startswith("https://huggingface.co/api/models/")
        assert row["size_source_url"].startswith("https://huggingface.co/api/models/")
        assert row["memory_source_url"].startswith("https://")
        assert row["memory_method"]
        assert row["read_date"] == "2026-09-27"


@pytest.mark.parametrize(
    "source",
    [
        """
        <html><head><title>Other Model hardware requirements</title></head><body>
          <h1>Other Model</h1><p>Gemma 4 E2B is also available.</p>
          <table><thead><tr><th>Quant</th><th>Total @ 8K</th></tr></thead>
            <tbody><tr><td>Q4_K_M</td><td>3.5 GB</td></tr></tbody>
          </table>
        </body></html>
        """,
        """
        <html><head><title>Gemma 4 E2B hardware requirements</title></head><body>
          <h1>Gemma 4 E2B</h1>
          <table><thead><tr><th>Quant</th><th>Total @ 8K</th></tr></thead>
            <tbody>
              <tr><td>Q4_K_M</td><td>4.1 GB</td></tr>
              <tr><td>Q8_0</td><td>3.5 GB</td></tr>
            </tbody>
          </table>
        </body></html>
        """,
    ],
    ids=("cross-model", "cross-row"),
)
def test_memory_reader_rejects_cross_model_and_cross_row_matches(source: str) -> None:
    with pytest.raises(SourceRowMismatchError):
        parse_memory_configuration(
            source,
            model_names=("Gemma 4 E2B",),
            quantisation="Q4_K_M",
            context_tokens=8192,
            runtime_memory_gb=3.5,
        )


def test_memory_reader_retains_the_exact_model_configuration_row() -> None:
    source = """
    <html><head><title>Gemma 4 E2B hardware requirements</title></head><body>
      <h1>Gemma 4 E2B</h1><p>Figures are calculated at 8K context.</p>
      <table><thead><tr><th>Quant</th><th>Weights</th><th>Total VRAM</th></tr></thead>
        <tbody><tr><td>Q4_K_M</td><td>2.9 GB</td><td>3.5 GB</td></tr></tbody>
      </table>
    </body></html>
    """

    parsed = parse_memory_configuration(
        source,
        model_names=("Gemma 4 E2B",),
        quantisation="Q4_K_M",
        context_tokens=8192,
        runtime_memory_gb=3.5,
    )

    assert parsed["model"] == "Gemma 4 E2B hardware requirements"
    assert parsed["cited_region"] == {
        "context": [
            "Gemma 4 E2B hardware requirements",
            "Gemma 4 E2B",
            "Figures are calculated at 8K context.",
        ],
        "headers": ["Quant", "Weights", "Total VRAM"],
        "row": ["Q4_K_M", "2.9 GB", "3.5 GB"],
    }


def test_local_rule_inputs_have_counting_two_key_verifications(
    slice_2, latest_verifications
) -> None:
    for row in slice_2["local"]["candidates"]:
        for suffix in (
            "model.parameters_total",
            "local.quantised_size_bytes",
            "local.runtime_memory_gb",
        ):
            verification = latest_verifications[("fact", f"{row['model_id']}#{suffix}")]
            assert verification["outcome"] == "verified"
            assert verification["collector"]["agent"] == "openai-codex-model-163"
            assert verification["verifier"]["model_family"] == "deterministic"
            assert (
                verification["collector"]["model_family"]
                != verification["verifier"]["model_family"]
            )
            expected_value = {
                "model.parameters_total": row["parameter_count"],
                "local.quantised_size_bytes": row["published_size_bytes"],
                "local.runtime_memory_gb": row["runtime_memory_gb"],
            }[suffix]
            assert verification["target"]["value_hash"] == value_hash(expected_value)


def test_local_candidates_publish_the_verified_hardware_fit_facet(
    slice_2, latest_verifications
) -> None:
    for row in slice_2["local"]["candidates"]:
        card_path = ROOT / "models" / f"{row['model_id']}.md"
        card = yaml.safe_load(card_path.read_text(encoding="utf-8").split("---", 2)[1])
        facts = [fact for fact in card["facts"] if fact["facet"] == "model.fits_hardware"]
        assert len(facts) == 1
        assert facts[0]["state"] == "known"
        assert facts[0]["value"] == ["nvidia_rtx_4090"]
        assert facts[0]["sources"][0]["source_id"].endswith("-memory")

        verification = latest_verifications[("fact", f"{row['model_id']}#model.fits_hardware")]
        assert verification["outcome"] == "verified"
        assert verification["target"]["value_hash"] == value_hash(["nvidia_rtx_4090"])


def test_budget_input_contains_a_quota_not_a_named_candidate_list(slice_2) -> None:
    assert slice_2["budget"] == {"quota_per_class": 3}


def test_approved_lineup_status_is_recorded() -> None:
    lineup = yaml.safe_load((ROOT / "premier" / "slice-1.yaml").read_text())
    assert lineup["status"] == "approved"
    assert lineup["approved_date"] == "2026-09-26"
