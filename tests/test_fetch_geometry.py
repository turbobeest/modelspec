"""Geometry mapping from Hugging Face config.json.

The fetcher must copy only fields the config actually contains, prefer the
language-model nest over a vision tower, and refuse to overwrite or invent.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.fetch_geometry import (  # noqa: E402
    _base_models_from_readme,
    apply_geometry,
    extract_geometry,
    fetch_config,
    geometry_from_config,
    published_active_from_readme,
)

MIXTRAL = {
    "architectures": ["MixtralForCausalLM"],
    "hidden_act": "silu",
    "hidden_size": 4096,
    "intermediate_size": 14336,
    "num_attention_heads": 32,
    "num_experts_per_tok": 2,
    "num_hidden_layers": 32,
    "num_key_value_heads": 8,
    "num_local_experts": 8,
    "tie_word_embeddings": False,
    "vocab_size": 32000,
}

QWEN3_MOE = {
    "architectures": ["Qwen3MoeForCausalLM"],
    "head_dim": 128,
    "hidden_act": "silu",
    "hidden_size": 2048,
    "intermediate_size": 6144,
    "moe_intermediate_size": 768,
    "mlp_only_layers": [],
    "decoder_sparse_step": 1,
    "num_attention_heads": 32,
    "num_experts": 128,
    "num_experts_per_tok": 8,
    "num_hidden_layers": 48,
    "num_key_value_heads": 4,
    "tie_word_embeddings": False,
    "vocab_size": 151936,
}

JAMBA = {
    "architectures": ["JambaForCausalLM"],
    "attn_layer_offset": 4,
    "attn_layer_period": 8,
    "expert_layer_offset": 1,
    "expert_layer_period": 2,
    "hidden_act": "silu",
    "hidden_size": 4096,
    "intermediate_size": 14336,
    "mamba_d_state": 16,
    "mamba_expand": 2,
    "num_attention_heads": 32,
    "num_experts": 16,
    "num_experts_per_tok": 2,
    "num_hidden_layers": 32,
    "num_key_value_heads": 8,
    "tie_word_embeddings": False,
    "vocab_size": 65536,
}

DEEPSEEK_V3 = {
    "first_k_dense_replace": 3,
    "hidden_act": "silu",
    "hidden_size": 7168,
    "intermediate_size": 18432,
    "kv_lora_rank": 512,
    "moe_intermediate_size": 2048,
    "n_routed_experts": 256,
    "n_shared_experts": 1,
    "num_attention_heads": 128,
    "num_experts_per_tok": 8,
    "num_hidden_layers": 61,
    "num_key_value_heads": 128,
    "num_nextn_predict_layers": 1,
    "q_lora_rank": 1536,
    "qk_nope_head_dim": 128,
    "tie_word_embeddings": False,
    "v_head_dim": 128,
    "vocab_size": 129280,
}

INTERNVL = {
    "llm_config": {
        "hidden_act": "silu",
        "hidden_size": 4096,
        "intermediate_size": 14336,
        "num_attention_heads": 32,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "tie_word_embeddings": False,
        "vocab_size": 92553,
    },
    "vision_config": {
        "hidden_size": 1024,
        "intermediate_size": 4096,
        "num_attention_heads": 16,
        "num_hidden_layers": 24,
    },
}


def test_mixtral_maps_local_experts_and_geometry() -> None:
    fetched = geometry_from_config(MIXTRAL)
    assert fetched["num_layers"] == 32
    assert fetched["num_attention_heads"] == 32
    assert fetched["num_kv_heads"] == 8
    assert fetched["hidden_size"] == 4096
    assert fetched["intermediate_size"] == 14336
    assert fetched["vocab_size"] == 32000
    assert fetched["num_experts"] == 8
    assert fetched["experts_per_token"] == 2
    # Mixtral 8x7B is ~12.9B active. Using all 8 experts would look like ~47B.
    assert 12_000_000_000 < fetched["active_parameters"] < 13_500_000_000


def test_qwen3_moe_uses_num_experts_and_moe_ffn_width() -> None:
    fetched = geometry_from_config(QWEN3_MOE)
    assert fetched["num_experts"] == 128
    assert fetched["experts_per_token"] == 8
    assert fetched["num_layers"] == 48
    assert fetched["intermediate_size"] == 6144  # dense width, not moe width
    assert 3_000_000_000 < fetched["active_parameters"] < 4_000_000_000


def test_jamba_records_experts_but_does_not_invent_active_params() -> None:
    fetched = geometry_from_config(JAMBA)
    assert fetched["num_experts"] == 16
    assert fetched["experts_per_token"] == 2
    assert "active_parameters" not in fetched


def test_deepseek_mla_does_not_invent_active_params() -> None:
    fetched = geometry_from_config(DEEPSEEK_V3)
    assert fetched["num_experts"] == 256
    assert fetched["experts_per_token"] == 8
    assert "active_parameters" not in fetched


def test_multimodal_llm_config_wins_over_vision_tower() -> None:
    fetched = geometry_from_config(INTERNVL)
    assert fetched["hidden_size"] == 4096
    assert fetched["num_layers"] == 32
    assert fetched["num_attention_heads"] == 32
    assert fetched["intermediate_size"] == 14336


def test_text_config_nest_is_used() -> None:
    fetched = geometry_from_config({
        "text_config": {
            "hidden_size": 2560,
            "num_hidden_layers": 34,
            "num_attention_heads": 8,
            "num_key_value_heads": 4,
            "intermediate_size": 10240,
            "vocab_size": 262144,
        },
        "vision_config": {"hidden_size": 1152, "num_hidden_layers": 27},
    })
    assert fetched["hidden_size"] == 2560
    assert fetched["num_layers"] == 34
    assert fetched["vocab_size"] == 262144


def test_missing_fields_are_omitted_not_defaulted() -> None:
    fetched = geometry_from_config({"hidden_size": 4096})
    assert fetched == {"hidden_size": 4096}
    assert "num_kv_heads" not in fetched
    assert "num_experts" not in fetched
    assert "active_parameters" not in fetched


def test_bool_is_not_an_int() -> None:
    fetched = geometry_from_config({"num_hidden_layers": True, "hidden_size": 4})
    assert "num_layers" not in fetched
    assert fetched["hidden_size"] == 4


def test_explicit_active_parameters_are_copied() -> None:
    cfg = dict(MIXTRAL)
    cfg["active_parameters"] = 12_900_000_000
    fetched = geometry_from_config(cfg)
    assert fetched["active_parameters"] == 12_900_000_000


def test_conflicts_are_flagged_and_not_overwritten() -> None:
    existing = {"num_layers": 99, "hidden_size": None, "num_experts": 8}
    fetched = {"num_layers": 32, "hidden_size": 4096, "num_experts": 8}
    gained, conflicts, already = apply_geometry(existing, fetched)
    assert gained == {"hidden_size": 4096}
    assert already == ["num_experts"]
    assert conflicts == [
        {"field": "num_layers", "existing": 99, "fetched": 32}
    ]


def test_write_round_trips_through_model_card(tmp_path: Path) -> None:
    from schema.card import ModelCard
    from scripts.fetch_geometry import _write_architecture

    path = tmp_path / "tiny.md"
    path.write_text(
        "---\n"
        "model_id: test/tiny\n"
        "display_name: Tiny\n"
        "provider: test\n"
        "architecture:\n"
        "  num_layers: null\n"
        "  hidden_size: 99\n"
        "  num_experts: null\n"
        "---\n\nprose\n",
        encoding="utf-8",
    )
    existing = existing_from_file(path)
    fetched = {"num_layers": 12, "hidden_size": 128, "num_experts": 4}
    gained, conflicts, _already = apply_geometry(existing, fetched)
    assert gained == {"num_layers": 12, "num_experts": 4}
    assert conflicts[0]["field"] == "hidden_size"
    _write_architecture(path, gained)
    card = ModelCard.from_yaml_file(path)
    assert card.architecture.num_layers == 12
    assert card.architecture.num_experts == 4
    assert card.architecture.hidden_size == 99
    assert card.prose_body == "prose"


def existing_from_file(path: Path) -> dict[str, int | None]:
    from schema.card import ModelCard
    from scripts.fetch_geometry import existing_architecture

    return existing_architecture(ModelCard.from_yaml_file(path))


def test_absent_kv_key_is_mha_when_config_is_present() -> None:
    """BERT-style configs omit num_key_value_heads because they are MHA."""
    fetched = geometry_from_config({
        "hidden_size": 768,
        "num_attention_heads": 12,
        "num_hidden_layers": 12,
        "vocab_size": 30522,
    })
    assert fetched["num_kv_heads"] == 12
    assert extract_geometry({
        "hidden_size": 768,
        "num_attention_heads": 12,
        "num_hidden_layers": 12,
    }).sources["num_kv_heads"] == "mha_equals_num_attention_heads"


def test_mha_fallback_needs_attention_heads_in_the_config() -> None:
    fetched = geometry_from_config({"num_hidden_layers": 6, "hidden_size": 768})
    assert "num_kv_heads" not in fetched


def test_chatglm_multi_query_group_num_is_not_mha() -> None:
    fetched = geometry_from_config({
        "hidden_size": 4096,
        "num_attention_heads": 32,
        "num_hidden_layers": 40,
        "multi_query_group_num": 2,
        "multi_query_attention": True,
    })
    assert fetched["num_kv_heads"] == 2
    assert extract_geometry({
        "num_attention_heads": 32,
        "multi_query_group_num": 2,
    }).sources["num_kv_heads"] == "multi_query_group_num"


def test_zero_experts_are_not_moe() -> None:
    fetched = geometry_from_config({
        "num_local_experts": 0,
        "num_experts_per_tok": 0,
        "hidden_size": 2048,
        "num_hidden_layers": 40,
    })
    assert "num_experts" not in fetched
    assert "active_parameters" not in fetched


COMMAND_A_PLUS = {
    "text_config": {
        "hidden_act": "silu",
        "hidden_size": 4096,
        "intermediate_size": 4096,
        "num_attention_heads": 128,
        "num_experts": 128,
        "num_experts_per_tok": 8,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "num_shared_experts": 4,
        "first_k_dense_replace": 0,
        "head_dim": 128,
        "tie_word_embeddings": True,
        "vocab_size": 262144,
        "layer_types": ["sliding_attention", "full_attention"] * 16,
    },
    "tie_word_embeddings": True,
}


def test_command_a_plus_derives_active_params_matching_published_25b() -> None:
    """Worked derivation 1. Shared experts use the one stated FFN width."""
    fetched = geometry_from_config(COMMAND_A_PLUS)
    # attn 142_606_336 + 8*50_331_648 + 524_288 + 4*50_331_648 = 747_110_400
    # embed 1_073_741_824 + 32 * 747_110_400 = 24_981_274_624
    assert fetched["active_parameters"] == 24_981_274_624
    assert 24_900_000_000 < fetched["active_parameters"] < 25_100_000_000
    assert extract_geometry(COMMAND_A_PLUS).sources[
        "active_parameters"
    ] == "derived_uniform_gated_moe"


def test_hunyuan_uniform_moe_topk_list_maps_experts_per_token() -> None:
    """Worked derivation 3 ingredients: moe_topk is a per-layer list of 8s."""
    fetched = geometry_from_config({
        "hidden_act": "silu",
        "hidden_size": 4096,
        "intermediate_size": 3072,
        "moe_intermediate_size": [3072] * 32,
        "moe_topk": [8] * 32,
        "num_attention_heads": 32,
        "num_experts": 64,
        "num_hidden_layers": 32,
        "num_key_value_heads": 8,
        "tie_word_embeddings": True,
        "vocab_size": 128167,
        "head_dim": 128,
    })
    assert fetched["experts_per_token"] == 8
    # 11.54B derived; published 13B is preferred later from the README.
    assert 11_000_000_000 < fetched["active_parameters"] < 12_000_000_000


def test_glm45_air_sparse_schedule_is_derived_not_total_times_k_over_n() -> None:
    """Worked derivation 2. first_k_dense_replace=1, one shared expert.

    The published card figure is 12B; the exact sum is ~13.4B because the
    card rounds. Derivation still must not use total × 8/128.
    """
    cfg = {
        "hidden_act": "silu",
        "hidden_size": 4096,
        "intermediate_size": 10944,
        "moe_intermediate_size": 1408,
        "n_routed_experts": 128,
        "n_shared_experts": 1,
        "num_attention_heads": 96,
        "num_experts_per_tok": 8,
        "num_hidden_layers": 46,
        "num_key_value_heads": 8,
        "first_k_dense_replace": 1,
        "head_dim": 128,
        "tie_word_embeddings": False,
        "vocab_size": 151552,
    }
    fetched = geometry_from_config(cfg)
    naive = 106_000_000_000 * 8 // 128
    assert fetched["active_parameters"] != naive
    assert 13_000_000_000 < fetched["active_parameters"] < 14_000_000_000
    assert extract_geometry(cfg).sources[
        "active_parameters"
    ] == "derived_sparse_gated_moe"


def test_glm45_air_nextn_layer_refuses_derivation() -> None:
    cfg = {
        "hidden_act": "silu",
        "hidden_size": 4096,
        "intermediate_size": 10944,
        "moe_intermediate_size": 1408,
        "n_routed_experts": 128,
        "n_shared_experts": 1,
        "num_attention_heads": 96,
        "num_experts_per_tok": 8,
        "num_hidden_layers": 46,
        "num_key_value_heads": 8,
        "first_k_dense_replace": 1,
        "num_nextn_predict_layers": 1,
        "head_dim": 128,
        "tie_word_embeddings": False,
        "vocab_size": 151552,
    }
    fetched = geometry_from_config(cfg)
    assert "active_parameters" not in fetched
    assert extract_geometry(cfg).refusal == "nextn_predict_layers"


def test_published_readme_prefers_property_table() -> None:
    text = (
        "| Property | 26B A4B MoE |\n"
        "| :---- | :---- |\n"
        "| **Total Parameters** | 25.2B |\n"
        "| **Active Parameters** | 3.8B |\n"
        "| **Layers** | 30 |\n"
    )
    value, why = published_active_from_readme(text, "google/gemma-4-26B-A4B-it")
    assert value == 3_800_000_000
    assert why == "property_table"


def test_published_readme_deepseek_v3_unique_prose() -> None:
    text = (
        "We present DeepSeek-V3, a strong Mixture-of-Experts (MoE) language "
        "model with 671B total parameters with 37B activated for each token.\n"
    )
    value, why = published_active_from_readme(text, "deepseek-ai/DeepSeek-V3")
    assert value == 37_000_000_000
    assert why in {"prose", "prose_name_bound"}


def test_published_readme_refuses_comparison_table_with_many_activated() -> None:
    text = (
        "| | # Activated Params | - | 21B | 72B | 405B | 37B |\n"
        "| | # Total Params | - | 236B | 540B | 405B | 671B |\n"
    )
    assert published_active_from_readme(text, "deepseek-ai/DeepSeek-V3") is None


def test_published_readme_granite_highlighted_cell() -> None:
    text = (
        "<tr>"
        '<td style="text-align:left; background-color: #FFFFFF; color: black;">'
        "# Active parameters</td>"
        '<td style="text-align:center; background-color: #FFFFFF; color: black;">3B</td>'
        '<td style="text-align:center; background-color: #FFFFFF; color: black;">3B</td>'
        '<td style="text-align:center; background-color: #FFFFFF; color: black;">1B</td>'
        '<td style="text-align:center; background-color: #DAE8FF; color: black;">9B</td>'
        "</tr>"
    )
    value, why = published_active_from_readme(
        text, "ibm-granite/granite-4.0-h-small"
    )
    assert value == 9_000_000_000
    assert why == "html_highlighted_active_cell"


def test_published_readme_from_to_takes_destination() -> None:
    text = (
        "Compared to GLM-4.5, GLM-5 scales from 355B parameters (32B active) "
        "to 744B parameters (40B active), and increases pre-training data.\n"
    )
    value, why = published_active_from_readme(text, "zai-org/GLM-5")
    assert value == 40_000_000_000
    assert why == "prose_from_to_destination"


def test_published_readme_kimi_property_row() -> None:
    text = (
        "| **Architecture** | Mixture-of-Experts (MoE) |\n"
        "| **Total Parameters** | 1T |\n"
        "| **Activated Parameters** | 32B |\n"
        "| **Number of Layers** | 61 |\n"
    )
    value, why = published_active_from_readme(text, "moonshotai/Kimi-K2-Thinking")
    assert value == 32_000_000_000
    assert why == "property_table"


def test_published_readme_jamba_active_not_activate() -> None:
    text = (
        "It's a pretrained, mixture-of-experts (MoE) generative text model, "
        "with 12B active parameters and a total of 52B parameters across all experts."
    )
    value, why = published_active_from_readme(text, "ai21labs/Jamba-v0.1")
    assert value == 12_000_000_000
    assert why == "prose"


def test_published_readme_lfm2_prefers_1_5b_over_a1b_name() -> None:
    text = (
        "We're releasing the weights of our first MoE based on LFM2, "
        "with 8.3B total parameters and 1.5B active parameters.\n"
        "Find more information about LFM2-8B-A1B in our blog post.\n"
        "| **Active parameters** | 1.5B                          | 2.3B |\n"
    )
    value, why = published_active_from_readme(text, "LiquidAI/LFM2-8B-A1B")
    assert value == 1_500_000_000
    assert why == "prose"


def test_base_model_yaml_is_read_from_card_front_matter() -> None:
    text = (
        "---\n"
        "base_model:\n"
        "- moonshotai/Kimi-K2.5\n"
        "license: other\n"
        "---\n"
        "# Quant of Kimi K2.5\n"
    )
    assert _base_models_from_readme(text) == ["moonshotai/Kimi-K2.5"]


def test_published_readme_quant_suffix_still_binds_base_row() -> None:
    text = (
        "| **Model** | **#Total Params** | **#Activated Params** | **Context Length** |\n"
        "| DeepSeek-V3 | 671B | 37B | 128K |\n"
    )
    value, why = published_active_from_readme(
        text, "deepseek-ai/DeepSeek-V3-0324"
    )
    assert value == 37_000_000_000
    assert why == "named_markdown_row"


def test_published_readme_glm45_size_token_is_active_not_total() -> None:
    text = (
        "| GLM-4.5          | [link](https://huggingface.co/zai-org/GLM-4.5) "
        "| 355B-A32B  | BF16      |\n"
        "| GLM-4.5-Air      | [link](https://huggingface.co/zai-org/GLM-4.5-Air) "
        "| 106B-A12B  | BF16      |\n"
    )
    full, why = published_active_from_readme(text, "zai-org/GLM-4.5")
    air, _ = published_active_from_readme(text, "zai-org/GLM-4.5-Air")
    assert full == 32_000_000_000
    assert air == 12_000_000_000
    assert why == "named_markdown_row"


def test_published_readme_glm45_air_not_the_355b_sibling() -> None:
    text = (
        "GLM-4.5 has 355 billion total parameters with 32 billion active "
        "parameters, while GLM-4.5-Air adopts a more compact design with "
        "106 billion total parameters and 12 billion active parameters."
    )
    air, _ = published_active_from_readme(text, "zai-org/GLM-4.5-Air")
    full, _ = published_active_from_readme(text, "zai-org/GLM-4.5")
    assert air == 12_000_000_000
    assert full == 32_000_000_000


def test_published_readme_kimi_k3_html_two_cell() -> None:
    text = (
        "<tr>\n"
        '<td align="center"><strong>Activated Parameters</strong></td>\n'
        '<td align="center">104B</td>\n'
        "</tr>"
    )
    value, why = published_active_from_readme(text, "moonshotai/Kimi-K3")
    assert value == 104_000_000_000
    assert why == "html_two_cell_active"


def test_published_readme_does_not_take_a22b_from_a_neighbour() -> None:
    text = (
        "| Qwen3-235B-A22B                | 85.7    | 81.5    |\n"
        "| DeepSeek-R1-0528 | 671B | 37B | 128K |\n"
    )
    value, why = published_active_from_readme(
        text, "deepseek-ai/DeepSeek-R1-0528"
    )
    assert value == 37_000_000_000
    assert why == "named_markdown_row"


def test_published_readme_a3b_self_size() -> None:
    text = (
        "GLM-4.7-Flash is a 30B-A3B MoE model. As the strongest model "
        "in the 30B class, GLM-4.7-Flash offers a new option.\n"
    )
    value, why = published_active_from_readme(text, "zai-org/GLM-4.7-Flash")
    assert value == 3_000_000_000
    assert why == "size_token_A"


def test_published_readme_a3b_from_heading_not_from_slug() -> None:
    text = "# Some Model\n\nIt is a 30B-A3B MoE model.\n"
    value, why = published_active_from_readme(text, "zai-org/GLM-4.7-Flash")
    assert value == 3_000_000_000
    assert why == "size_token_A"


def test_429_is_retried_not_treated_as_missing(monkeypatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(
        "scripts.fetch_geometry.time.sleep", lambda seconds: sleeps.append(seconds)
    )

    class Response:
        def __init__(self, status: int, payload=None, headers=None):
            self.status_code = status
            self.headers = headers or {}
            self._payload = payload
            self.text = ""

        def json(self):
            return self._payload

    class Client:
        def __init__(self) -> None:
            self.calls = 0

        def get(self, url: str):
            self.calls += 1
            if self.calls == 1:
                return Response(429, headers={"Retry-After": "1"})
            return Response(200, payload={"hidden_size": 4})

    client = Client()
    status, payload, detail = fetch_config(client, "org/model")
    assert status == "ok"
    assert payload == {"hidden_size": 4}
    assert detail == "ok"
    assert client.calls == 2
    assert sleeps == [1.0]


def test_429_exhaustion_is_error_not_not_found(monkeypatch) -> None:
    monkeypatch.setattr("scripts.fetch_geometry.time.sleep", lambda _seconds: None)

    class Response:
        status_code = 429
        headers = {"Retry-After": "1"}
        text = ""

        def json(self):
            raise ValueError("no body")

    class Client:
        def get(self, url: str):
            return Response()

    status, payload, detail = fetch_config(Client(), "org/model")
    assert status == "error"
    assert payload is None
    assert "rate-limited" in detail
    assert status != "not_found"
