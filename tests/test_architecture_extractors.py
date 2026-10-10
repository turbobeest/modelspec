"""MODEL-348: literal readings from retained HF configs and model cards."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date

import pytest

from decision.model import Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore
from decision.verify import (
    Claim,
    DenseActiveEqualsTotalExtractor,
    HFConfigExtractor,
    HFParametersExtractor,
    ModelCardParamsExtractor,
    Reading,
    StoredRegions,
    deterministic_extractors,
    verify,
)

CONFIG_URL = "https://huggingface.co/lab/Alpha/resolve/main/config.json"
API_URL = "https://huggingface.co/api/models/lab/Alpha"
README_URL = "https://huggingface.co/lab/Alpha/raw/main/README.md"
ME = VerificationActor(agent="collector", model_family="openai", method="test")


def claim(facet="model.architecture", value=None, refs=None):
    return Claim(
        TargetRef(kind="fact", id=f"lab/alpha#{facet}"),
        "lab/alpha",
        ("Alpha", "lab/Alpha"),
        facet,
        value,
        ME,
        tuple(
            refs
            or [
                SourceRef(
                    source_id="config", snapshot_ref="sha256:" + "a" * 64, cited_regions=["page"]
                ),
            ]
        ),
        unit=None
        if facet == "model.architecture"
        else "experts"
        if "experts" in facet
        else "parameters",
    )


@pytest.mark.parametrize(
    "config,architecture,experts,topk",
    [
        (
            {
                "model_type": "deepseek_v3",
                "n_routed_experts": 256,
                "n_shared_experts": 1,
                "num_experts_per_tok": 8,
            },
            "MoE",
            256,
            8,
        ),
        ({"model_type": "mixtral", "num_local_experts": 8, "num_experts_per_tok": 2}, "MoE", 8, 2),
        ({"model_type": "qwen3_moe", "num_experts": 128, "num_experts_per_tok": 8}, "MoE", 128, 8),
        (
            {
                "model_type": "gemma4",
                "text_config": {"model_type": "gemma4_text", "num_attention_heads": 32},
            },
            "dense-transformer",
            None,
            None,
        ),
        ({"model_type": "phi3", "num_attention_heads": 40}, "dense-transformer", None, None),
        ({"model_type": "llama", "num_attention_heads": 32}, "dense-transformer", None, None),
        ({"model_type": "bert", "num_attention_heads": 12}, "encoder-only", None, None),
        ({"architectures": ["CustomForMaskedLM"]}, "encoder-only", None, None),
        (
            {
                "model_type": "qwen3",
                "architectures": ["Qwen3ForCausalLM"],
                "num_attention_heads": 32,
            },
            "dense-transformer",
            None,
            None,
        ),
        (
            {
                "model_type": "hybrid",
                "num_attention_heads": 32,
                "layer_types": ["full_attention", "linear_attention"],
            },
            "hybrid-SSM-transformer",
            None,
            None,
        ),
        (
            {
                "model_type": "hybrid",
                "num_attention_heads": 32,
                "layers_block_type": ["attention", "mamba"],
                "num_experts": 8,
                "moe_topk": 2,
            },
            "MoE",
            8,
            2,
        ),
    ],
)
def test_config_literal_readings(config, architecture, experts, topk):
    reader = HFConfigExtractor()
    text = json.dumps(config)
    assert reader.accepts(text)
    assert reader.extract(claim(), text, page_url=CONFIG_URL) == [Reading("Alpha", architecture)]
    for facet, expected in (("model.experts_total", experts), ("model.experts_per_token", topk)):
        found = reader.extract(claim(facet), text, page_url=CONFIG_URL)
        assert found == ([] if expected is None else [Reading("Alpha", expected, "experts")])


@pytest.mark.parametrize(
    "text", ["Not a config", "[]", '{"rows": []}', '{"text_config": "bad"}', '{"config": {}}']
)
def test_config_does_not_accept_other_formats(text):
    reader = HFConfigExtractor()
    assert not reader.accepts(text)
    assert reader.extract(claim(), text, page_url=CONFIG_URL) == []


@pytest.mark.parametrize(
    "config",
    [
        {"model_type": "mystery"},
        {"num_attention_heads": 32, "num_experts": "128"},
        {"num_attention_heads": 32, "num_experts": 1},
        {"num_attention_heads": 32, "n_shared_experts": 1},
        {"num_attention_heads": True},
    ],
)
def test_config_never_guesses_a_dense_backbone(config):
    assert HFConfigExtractor().extract(claim(), json.dumps(config), page_url=CONFIG_URL) == []


def test_variable_layer_counts_do_not_become_one_uniform_expert_fact():
    text = json.dumps(
        {"model_type": "custom_moe", "num_experts": [8, 16], "num_experts_per_tok": [2, 4]}
    )
    reader = HFConfigExtractor()
    assert reader.extract(claim(), text, page_url=CONFIG_URL) == [Reading("Alpha", "MoE")]
    assert reader.extract(claim("model.experts_total"), text, page_url=CONFIG_URL) == []
    assert reader.extract(claim("model.experts_per_token"), text, page_url=CONFIG_URL) == []


def test_public_api_config_is_a_gated_repo_fallback():
    text = json.dumps(
        {
            "id": "lab/Alpha",
            "config": {"model_type": "gemma4", "text_config": {"num_experts": 128, "moe_topk": 8}},
        }
    )
    reader = HFConfigExtractor()
    assert reader.extract(claim(), text, page_url=API_URL) == [Reading("Alpha", "MoE")]
    assert reader.extract(claim("model.experts_total"), text, page_url=API_URL) == [
        Reading("Alpha", 128, "experts"),
    ]
    assert reader.extract(claim(), text.replace("lab/Alpha", "lab/Beta"), page_url=API_URL) == []
    assert reader.extract(claim(), text, page_url=CONFIG_URL.replace("Alpha", "Beta")) == []
    assert reader.extract(claim("model.context_window"), text, page_url=API_URL) == []


@pytest.mark.parametrize(
    "text,expected",
    [
        ("# Alpha\nAlpha has 37B activated parameters and 671B total parameters.", 37_000_000_000),
        ("Alpha uses 3.8B active parameters.", 3_800_000_000),
        ("# Alpha\n| Activated Params | 32B |", 32_000_000_000),
        ("# Alpha\n| Model | Active parameters |\n| Beta | 49B |\n| Alpha | 4B |", 4_000_000_000),
        ("# Alpha\nAlpha has 671B total parameters.", None),
        ("# Alpha-A4B\nAlpha-A4B is available.", None),
        ("# Alpha\nBeta has 37B activated parameters.", None),
        ("# Alpha\n| Total Params | 32B |", None),
        ("# Alpha\n| Activated Params | about 32B |", None),
    ],
)
def test_readme_active_parameters_are_explicit_and_model_scoped(text, expected):
    reader = ModelCardParamsExtractor()
    readings = reader.extract(claim("model.parameters_active"), text, page_url=README_URL)
    assert readings == ([] if expected is None else [Reading("Alpha", expected, "parameters")])
    assert reader.extract(claim("model.parameters_total"), text, page_url=README_URL) == []


def test_dense_equality_uses_both_retained_primary_inputs():
    config = '{"model_type":"llama","num_attention_heads":32}'
    api = '{"id":"lab/Alpha","safetensors":{"total":2,"parameters":{"BF16":700,"F32":3}}}'
    reader = DenseActiveEqualsTotalExtractor()
    c = claim("model.parameters_active", 703)
    assert reader.extract(c, config, page_url=CONFIG_URL, bindings=[(api, API_URL)]) == [
        Reading("Alpha", 703, "parameters"),
    ]
    assert reader.extract(c, config, page_url=CONFIG_URL) == []
    assert (
        reader.extract(
            c,
            config,
            page_url=CONFIG_URL,
            bindings=[(api.replace("lab/Alpha", "lab/Beta"), API_URL)],
        )
        == []
    )
    for other in ('{"num_experts":8}', '{"model_type":"mystery"}', "not JSON"):
        assert not reader.accepts(other)
        assert reader.extract(c, other, page_url=CONFIG_URL, bindings=[(api, API_URL)]) == []
    assert HFParametersExtractor().extract(
        claim("model.parameters_total"), api, page_url=API_URL
    ) == [
        Reading("Alpha", 703, "parameters"),
    ]


def retained(tmp_path, docs):
    store, sources, refs = CopyStore(tmp_path), {}, []
    for sid, url, text in docs:
        sources[sid] = Source(
            id=sid,
            url=url,
            kind="weights_repository",
            normaliser="text-default",
            cited_regions=[{"id": "page", "locator": {"kind": "page"}}],
        )
        refs.append(
            SourceRef(source_id=sid, snapshot_ref=store.put(text.encode()), cited_regions=["page"])
        )
    return StoredRegions(store, sources), refs


def test_registered_dispatch_repeats_dense_equality_and_rejects_a_changed_total(tmp_path):
    regions, refs = retained(
        tmp_path,
        [
            ("config", CONFIG_URL, '{"model_type":"phi3","num_attention_heads":40}'),
            ("api", API_URL, '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":703}}}'),
        ],
    )
    c = claim("model.parameters_active", 703, refs)
    result = verify(c, regions, deterministic_extractors(), today=date(2026, 10, 10))
    assert result.outcome == "verified"
    assert result.verification.method == "dense-active-equals-total@1"
    assert (
        verify(
            replace(c, value=704), regions, deterministic_extractors(), today=date(2026, 10, 10)
        ).outcome
        == "mismatch"
    )
    regions.store.path(refs[0].snapshot_ref).unlink()
    assert (
        verify(c, regions, deterministic_extractors(), today=date(2026, 10, 10)).outcome
        == "unreachable"
    )


def test_absence_checks_all_copies_and_never_calls_an_llm(tmp_path):
    class NoLLM:
        actor = VerificationActor(agent="llm", model_family="anthropic", method="llm")

        def accepts(self, text):
            raise AssertionError("hardware facts never reach an LLM")

    regions, refs = retained(
        tmp_path,
        [
            ("api", API_URL, '{"id":"lab/Alpha","config":{"architectures":["MysteryModel"]}}'),
            ("readme", README_URL, "# Alpha\nAlpha has 671B total parameters."),
        ],
    )
    readers = [NoLLM(), *deterministic_extractors()]
    c = claim("model.parameters_active", None, refs)
    result = verify(c, regions, readers, today=date(2026, 10, 10))
    assert result.outcome == "verified"
    assert result.verification.method == "hf-architecture-absence@1"
    regions, refs = retained(
        tmp_path,
        [
            ("readme", README_URL, "# Alpha\nAlpha has 37B activated parameters."),
        ],
    )
    assert (
        verify(replace(c, sources=tuple(refs)), regions, readers, today=date(2026, 10, 10)).outcome
        == "mismatch"
    )


def test_unrecognised_copy_cannot_confirm_an_absence(tmp_path):
    regions, refs = retained(tmp_path, [("config", CONFIG_URL, "not a config")])
    result = verify(
        claim("model.architecture", None, refs),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert result.outcome == "skipped"


def test_gemma_disabled_null_expert_settings_verify_dense_but_unknown_settings_do_not():
    reader = HFConfigExtractor()
    config = {
        "model_type": "gemma4_text",
        "num_attention_heads": 32,
        "enable_moe_block": False,
        "num_experts": None,
        "top_k_experts": None,
        "expert_intermediate_size": None,
    }
    assert reader.extract(claim(), json.dumps(config), page_url=CONFIG_URL) == [
        Reading("Alpha", "dense-transformer"),
    ]
    config["expert_custom"] = 1
    assert reader.extract(claim(), json.dumps(config), page_url=CONFIG_URL) == []


def test_gemma_shared_readme_scopes_the_moe_table_to_its_variant():
    text = """## Models overview
| Property | 26B A4B MoE |
| :---- | :---- |
| **Total Parameters** | 25.2B |
| **Active Parameters** | 3.8B |
"""
    reader = ModelCardParamsExtractor()
    for name, expected in (
        ("gemma-4-26b-a4b-it", 3_800_000_000),
        ("gemma-4-31b-it", None),
        ("gemma-4-e2b-it", None),
    ):
        c = replace(
            claim("model.parameters_active"),
            names=(name, "google/" + name),
            subject="google/" + name,
        )
        url = "https://huggingface.co/google/" + name + "/raw/main/README.md"
        assert reader.extract(c, text, page_url=url) == (
            [] if expected is None else [Reading(name, expected, "parameters")]
        )


def test_readme_html_and_markdown_model_tables_keep_variant_identity():
    reader = ModelCardParamsExtractor()
    c = claim("model.parameters_active")
    markdown = """| Model | #Total Params | #Activated Params | Download |
| Alpha-Base | 700B | 37B | [HF](https://huggingface.co/lab/Alpha-Base) \\| mirror |
| Alpha | 703B | 32B | [HF](https://huggingface.co/lab/Alpha) \\| mirror |
"""
    assert reader.extract(c, markdown, page_url=README_URL) == [
        Reading("Alpha", 32_000_000_000, "parameters")
    ]
    html = "<h1>Alpha</h1><table><tr><td>Activated Parameters</td><td>104B</td></tr></table>"
    assert reader.extract(c, html, page_url=README_URL) == [
        Reading("Alpha", 104_000_000_000, "parameters")
    ]
    variable = "| Property | Alpha | Beta |\n| Activated Params | 8B / 16B | 49B |"
    assert reader.extract(c, variable, page_url=README_URL) == []


def test_conflicting_cited_readings_do_not_verify_by_taking_the_first_match(tmp_path):
    regions, refs = retained(
        tmp_path,
        [
            ("config", CONFIG_URL, '{"num_experts":8}'),
            ("api", API_URL, '{"id":"lab/Alpha","config":{"num_experts":16}}'),
        ],
    )
    result = verify(
        claim("model.experts_total", 8, refs),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert result.outcome == "mismatch"


def test_generation_top_k_is_not_an_expert_router_setting():
    text = json.dumps(
        {"model_type": "kimi_k2", "n_routed_experts": 384, "num_experts_per_tok": 8, "top_k": 50}
    )
    assert HFConfigExtractor().extract(
        claim("model.experts_per_token"), text, page_url=CONFIG_URL
    ) == [Reading("Alpha", 8, "experts")]


def test_json_normalizer_preserves_formatted_configs_and_stable_fingerprints(tmp_path):
    from decision.normalise import NORMALISERS, UnsupportedContentError, normalise_document

    config = {"model_type": "llama", "num_attention_heads": 32, "layer_types": ["full_attention"]}
    pretty = json.dumps(config, indent=2).encode()
    compact = json.dumps(config).encode()
    rules = NORMALISERS["json-default"]
    assert normalise_document(pretty, rules).text == normalise_document(compact, rules).text
    assert json.loads(normalise_document(pretty, rules).text) == config
    with pytest.raises(UnsupportedContentError, match="invalid_json"):
        normalise_document(b"not JSON", rules)
    with pytest.raises(ValueError, match="page locators"):
        Source(
            id="json",
            url=CONFIG_URL,
            normaliser="json-default",
            cited_regions=[
                {"id": "table", "locator": {"kind": "table", "value": "0"}},
            ],
        )


def test_html_table_normalization_preserves_surrounding_markdown_parameter_rows():
    text = """# Alpha
| Total Parameters | 703B |
| Activated Parameters | 32B |
<table><tr><td>Benchmark</td><td>Score</td></tr></table>
"""
    assert ModelCardParamsExtractor().extract(
        claim("model.parameters_active"), text, page_url=README_URL
    ) == [
        Reading("Alpha", 32_000_000_000, "parameters"),
    ]


def test_html_comparison_tables_preserve_the_empty_corner_cell():
    html = """<table>
<tr><th></th><th>Alpha</th><th>Beta</th></tr>
<tr><td># Params</td><td>703B</td><td>800B</td></tr>
<tr><td># Activated params</td><td>6B</td><td>13B</td></tr>
</table>"""
    assert ModelCardParamsExtractor().extract(
        claim("model.parameters_active"), html, page_url=README_URL
    ) == [
        Reading("Alpha", 6_000_000_000, "parameters"),
    ]
