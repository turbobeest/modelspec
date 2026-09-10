"""total_parameters comes from Hub safetensors, never the model name."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest
from pydantic import ValidationError

from scripts.fetch_total_parameters import (  # noqa: E402
    already_decided,
    decide_total,
    extract_safetensors_total,
    is_name_parsed_total,
    published_total_from_readme,
)
from scripts.seed_huggingface import extract_params  # noqa: E402
from schema.card import Architecture  # noqa: E402

MIXTRAL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
MIXTRAL_SAFETENSORS = {
    "parameters": {"BF16": 46_702_792_704},
    "total": 46_702_792_704,
}


def test_safetensors_total_is_the_hub_aggregate() -> None:
    assert extract_safetensors_total({"safetensors": MIXTRAL_SAFETENSORS}) == (
        46_702_792_704
    )


def test_safetensors_total_absent_is_none_not_zero() -> None:
    assert extract_safetensors_total({}) is None
    assert extract_safetensors_total({"safetensors": {}}) is None
    assert extract_safetensors_total({"safetensors": {"total": 0}}) is None
    assert extract_safetensors_total(None) is None


def test_extract_params_uses_safetensors_not_the_name() -> None:
    assert extract_params({"id": MIXTRAL_ID, "safetensors": MIXTRAL_SAFETENSORS}) == (
        46_702_792_704
    )


def test_extract_params_does_not_parse_the_filename() -> None:
    assert extract_params({"id": MIXTRAL_ID}) is None
    assert extract_params({"id": "allenai/OLMoE-1B-7B-0924"}) is None
    assert extract_params({"id": "tencent/Hunyuan-A13B-Instruct"}) is None
    assert extract_params({"id": "zai-org/GLM-4.5"}) is None


def test_mixtral_8x7b_name_parses_as_7b_historically() -> None:
    """The bug: first `Nb` in the name is the expert width, not the total."""
    assert is_name_parsed_total(7_000_000_000, "mistral/mixtral-8x7b-instruct-v0-1")
    assert is_name_parsed_total(7_000_000_000, MIXTRAL_ID)
    assert not is_name_parsed_total(46_702_792_704, MIXTRAL_ID)


def test_olmoe_name_parses_as_the_active_1b() -> None:
    assert is_name_parsed_total(1_000_000_000, "allen-ai/olmoe-1b-7b-0924")


def test_decide_overwrites_a_name_parsed_guess() -> None:
    decision = decide_total(
        7_000_000_000, 46_702_792_704, "safetensors", True, 12_879_659_008
    )
    assert decision.action == "write"
    assert decision.value == 46_702_792_704
    assert decision.source == "safetensors"


def test_decide_nulls_unverified_name_parsed() -> None:
    decision = decide_total(7_000_000_000, None, "", True, None)
    assert decision.action == "null"
    assert decision.value is None


def test_decide_nulls_when_active_exceeds_unverified_total() -> None:
    decision = decide_total(9_000_000_000, None, "", False, 32_000_000_000)
    assert decision.action == "null"


def test_decide_keeps_unverified_non_name_parsed() -> None:
    decision = decide_total(52_000_000_000, None, "", False, None)
    assert decision.action == "keep"
    assert decision.value == 52_000_000_000


def test_decide_keeps_null_when_there_is_no_source() -> None:
    decision = decide_total(None, None, "", False, None)
    assert decision.action == "keep"
    assert decision.value is None


def test_already_decided_skips_a_previous_hub_source() -> None:
    """Re-running the fetcher must not hit the Hub for a settled card."""
    assert already_decided("safetensors")
    assert already_decided("safetensors:base_model:ibm-granite/granite-4.0-micro")
    assert already_decided("model_card_published:prose")
    assert already_decided("model_card_published:named_markdown_row")


def test_already_decided_does_not_skip_an_empty_source() -> None:
    """Empty source is unfinished work: a name-parsed guess, a legacy fill, or null."""
    assert not already_decided("")
    assert not already_decided("   ")


def test_published_total_from_property_table() -> None:
    text = (
        "| Property | 26B A4B MoE |\n"
        "| :---- | :---- |\n"
        "| **Total Parameters** | 25.2B |\n"
        "| **Active Parameters** | 3.8B |\n"
        "| **Layers** | 30 |\n"
    )
    value, why = published_total_from_readme(text, "google/gemma-4-26B-A4B-it")
    assert value == 25_200_000_000
    assert why == "property_table"


def test_published_total_not_the_active_figure() -> None:
    text = (
        "We present DeepSeek-V3, a strong Mixture-of-Experts (MoE) language "
        "model with 671B total parameters with 37B activated for each token.\n"
    )
    value, why = published_total_from_readme(text, "deepseek-ai/DeepSeek-V3")
    assert value == 671_000_000_000
    assert why == "prose"


def test_published_total_glm45_named_row_is_355b_not_32b() -> None:
    text = (
        "| GLM-4.5          | [link](https://huggingface.co/zai-org/GLM-4.5) "
        "| 355B-A32B  | BF16      |\n"
        "| GLM-4.5-Air      | [link](https://huggingface.co/zai-org/GLM-4.5-Air) "
        "| 106B-A12B  | BF16      |\n"
    )
    full, why = published_total_from_readme(text, "zai-org/GLM-4.5")
    air, _ = published_total_from_readme(text, "zai-org/GLM-4.5-Air")
    assert full == 355_000_000_000
    assert air == 106_000_000_000
    assert why == "named_markdown_row"


def test_architecture_rejects_active_exceeding_total() -> None:
    with pytest.raises(
        ValidationError,
        match=r"active_parameters \(32000000000\) exceeds total_parameters \(9000000000\)",
    ):
        Architecture(total_parameters=9_000_000_000, active_parameters=32_000_000_000)


def test_architecture_allows_null_total_with_active() -> None:
    arch = Architecture(total_parameters=None, active_parameters=32_000_000_000)
    assert arch.active_parameters == 32_000_000_000
    assert arch.total_parameters is None


def test_architecture_allows_null_active_with_total() -> None:
    arch = Architecture(total_parameters=46_702_792_704, active_parameters=None)
    assert arch.total_parameters == 46_702_792_704


def test_architecture_allows_active_equal_or_below_total() -> None:
    Architecture(total_parameters=7_000_000_000, active_parameters=7_000_000_000)
    Architecture(
        total_parameters=46_702_792_704, active_parameters=12_879_659_008
    )


def test_published_total_refuses_a_comparison_table() -> None:
    text = (
        "| | # Activated Params | - | 21B | 72B | 405B | 37B |\n"
        "| | # Total Params | - | 236B | 540B | 405B | 671B |\n"
    )
    assert published_total_from_readme(text, "deepseek-ai/DeepSeek-V3") is None
