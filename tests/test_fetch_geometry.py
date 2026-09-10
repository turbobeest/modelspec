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
    apply_geometry,
    geometry_from_config,
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
