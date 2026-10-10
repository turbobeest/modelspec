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
    hf_config_architecture,
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
            "config": {
                "architectures": ["Gemma4ForConditionalGeneration"],
                "model_type": "gemma4",
                "tokenizer_config": {"bos_token": "<bos>"},
            },
        }
    )
    reader = HFConfigExtractor()
    assert reader.extract(claim(), text, page_url=API_URL) == []
    assert reader.extract(claim("model.experts_total"), text, page_url=API_URL) == []
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


def test_gemma_null_or_unknown_expert_settings_block_dense():
    reader = HFConfigExtractor()
    config = {
        "model_type": "gemma4_text",
        "num_attention_heads": 32,
        "enable_moe_block": False,
        "num_experts": None,
        "top_k_experts": None,
        "expert_intermediate_size": None,
    }
    assert reader.extract(claim(), json.dumps(config), page_url=CONFIG_URL) == []
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


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "# Alpha\n\n## Compared with Beta\n\n| Spec | Beta-235B |\n"
            "|---|---|\n| Active Parameters | 22B |\n",
            [],
        ),
        (
            "# Alpha\n\n| Attribute | Value |\n|---|---|\n| Activated Params | 22B |\n",
            [22_000_000_000],
        ),
        (
            "Alpha uses 3B active parameters, while Beta uses 22B active parameters.\n",
            [3_000_000_000],
        ),
        ("Unlike Beta (22B active parameters), Alpha is dense.\n", []),
        ("Alpha: 30B total parameters, 3B active parameters\n", [3_000_000_000]),
        ("Alpha has 30B parameters of which 3 B active params\n", [3_000_000_000]),
        ("Alpha has 3B non-embedding active parameters\n", []),
        ("Alpha has 3-4B active parameters\n", []),
        ("Alpha has 3 to 4B active parameters\n", []),
        ("Alpha has between 3 and 4B active parameters\n", []),
        ("Alpha has 3 or 4B active parameters\n", []),
        ("Alpha has 3B active parameters to 4B\n", []),
        ("Alpha has 8B active parameters during prefill and 16B during decode\n", []),
        ("Alpha has 8B active parameters for prefill and 16B for decode\n", []),
        ("Alpha has up to 17B active parameters per expert\n", []),
        (
            "Beta uses 22B active parameters, while Alpha uses 3B active parameters.\n",
            [3_000_000_000],
        ),
        ("Alpha is dense. Beta uses 22B active parameters.\n", []),
        ("Alpha is dense; 22B active parameters belong to Beta.\n", []),
        ("# Alpha\n\n## Beta\n\n| Property | Value |\n| Active parameters | 22B |", []),
        ("# Alpha\n\n## Beta-235B\n\n| Attribute | Value |\n| Active parameters | 22B |", []),
        ("# Alpha\n\n## Beta\n\n| Active parameters | 22B |", []),
        (
            "# Alpha\n\n## Alpha\n\n| Property | Value |\n| Active parameters | 3B |",
            [3_000_000_000],
        ),
        ("# Alpha\n\n| Spec | Alpha |\n| Active parameters | 3B |", [3_000_000_000]),
        ("# Alpha\n\n| Spec | Beta |\n| Active parameters | 22B |", []),
        ("# Alpha\n\n| Model | Value |\n| Beta | 22B |\n| Active parameters | 22B |", []),
        ("Alpha uses 3B active parameters, beta uses 22B active parameters.", [3_000_000_000]),
        ("# Alpha\n\n## beta\n\n| Attribute | Value |\n| Active parameters | 22B |", []),
        (
            "# Alpha\n\n## 2. Model Summary\n| | |\n| Architecture | Mixture-of-Experts (MoE) |\n"
            "| Total Parameters | 30B |\n| Activated Parameters | 3B |\n"
            "| Selected Experts per Token | 8 |\n| Vision Encoder | MoonViT |",
            [3_000_000_000],
        ),
        ("# Alpha\n| Attribute | Value |\n| Model | beta |\n| Activated Parameters | 22B |", []),
    ],
)
def test_review_card_scope_and_scalar_probes(text, expected):
    assert [
        r.value
        for r in ModelCardParamsExtractor().extract(
            claim("model.parameters_active"), text, page_url=README_URL
        )
    ] == expected


@pytest.mark.parametrize(
    "text,outcome,reason",
    [
        (
            "# Alpha\n- Number of Parameters: 30B with 3B activated\n",
            "skipped",
            "active_wording_unparsed",
        ),
        (
            "# Alpha\nAlpha activates 3B parameters per token.\n",
            "skipped",
            "active_wording_unparsed",
        ),
        ("# Alpha\nActive parameters: 3B\n", "mismatch", None),
        (
            "# Alpha\n| Property | Alpha |\n| Activated Params | 8B / 16B |\n",
            "skipped",
            "active_wording_unparsed",
        ),
        ("# Alpha\nAlpha has 3-4B active parameters.\n", "skipped", "active_wording_unparsed"),
        ("# Alpha\nAlpha has 2.3B effective parameters.\n", "mismatch", None),
        (
            "# Alpha\nAlpha has 8B active parameters during prefill and 16B during decode\n",
            "skipped",
            "active_wording_unparsed",
        ),
    ],
)
def test_review_active_wording_cannot_verify_an_absence(tmp_path, text, outcome, reason):
    regions, refs = retained(tmp_path, [("readme", README_URL, text)])
    result = verify(
        claim("model.parameters_active", None, refs),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert result.outcome == outcome
    assert result.reason == reason


@pytest.mark.parametrize(
    "facet", ["model.architecture", "model.experts_total", "model.experts_per_token"]
)
@pytest.mark.parametrize(
    "docs",
    [
        [("readme", README_URL, "# Alpha\nAlpha is an MoE with 128 experts, 8 active.\n")],
        [
            (
                "api",
                API_URL,
                '{"id":"lab/Alpha","config":{"architectures":["AlphaMoeForCausalLM"],"model_type":"alpha_moe"}}',
            )
        ],
    ],
)
def test_review_config_absence_requires_a_retained_config(tmp_path, facet, docs):
    regions, refs = retained(tmp_path, docs)
    result = verify(
        claim(facet, None, refs), regions, deterministic_extractors(), today=date(2026, 10, 10)
    )
    assert result.outcome == "skipped"
    assert result.reason == "retained_config_required"


@pytest.mark.parametrize(
    "config,expected",
    [
        (
            {
                "model_type": "nemotron_h",
                "num_attention_heads": 32,
                "hybrid_override_pattern": "M-M-M*-M-",
                "mamba_num_heads": 128,
            },
            "hybrid-SSM-transformer",
        ),
        (
            {"model_type": "falcon_h1", "num_attention_heads": 8, "mamba_d_ssm": 1024},
            "hybrid-SSM-transformer",
        ),
        (
            {
                "model_type": "zamba2",
                "num_attention_heads": 32,
                "layers_block_type": ["mamba", "hybrid"],
            },
            "hybrid-SSM-transformer",
        ),
        ({"model_type": "rwkv7", "num_attention_heads": 32}, "hybrid-SSM-transformer"),
        (
            {"num_local_experts": 16, "text_config": {"model_type": "x", "num_attention_heads": 8}},
            "MoE",
        ),
        ({"num_experts": 1, "num_attention_heads": 8}, None),
        (
            {
                "model_type": "dbrx",
                "n_heads": 48,
                "ffn_config": {"moe_num_experts": 16, "moe_top_k": 4},
            },
            "MoE",
        ),
        (
            {
                "model_type": "dbrx",
                "num_heads": 48,
                "ffn_config": {"moe_num_experts": 16, "moe_top_k": 4},
            },
            "MoE",
        ),
        ({"num_experts": [0, 64, 64], "num_attention_heads": 8}, "MoE"),
        ({"model_type": "jetmoe", "num_attention_heads": 8, "num_local_experts": 8}, "MoE"),
        ({"model_type": "switch_transformers", "num_heads": 12, "num_experts": 8}, "MoE"),
        (
            {
                "num_attention_heads": 8,
                "enable_moe_block": False,
                "num_experts": None,
                "top_k_experts": None,
            },
            None,
        ),
        ({"num_attention_heads": 8, "enable_moe_block": False, "num_experts": 128}, "MoE"),
        ({"num_attention_heads": 8, "num_experts": True}, None),
        ({"model_type": "unrecognised_decoder", "num_attention_heads": 8}, None),
        (
            {"model_type": "llama", "num_attention_heads": 8, "vision_config": {"num_experts": 1}},
            None,
        ),
        (
            {
                "model_type": "llama",
                "num_attention_heads": 8,
                "other_config": {"model_type": "rwkv7"},
            },
            "hybrid-SSM-transformer",
        ),
        (
            {
                "model_type": "llama",
                "num_attention_heads": 8,
                "other_config": {"ssm_state_size": 16},
            },
            "hybrid-SSM-transformer",
        ),
        (
            {
                "model_type": "llama",
                "num_attention_heads": 8,
                "vision_config": {"model_type": "bert", "num_attention_heads": 12},
            },
            "dense-transformer",
        ),
    ],
)
def test_review_config_classification_probes(config, expected):
    assert hf_config_architecture(config) == expected
    assert [
        r.value
        for r in HFConfigExtractor().extract(claim(), json.dumps(config), page_url=CONFIG_URL)
    ] == ([] if expected is None else [expected])


def test_review_expert_list_excludes_layers_without_experts():
    text = '{"num_experts":[0,64,64],"num_experts_per_tok":8,"num_attention_heads":8}'
    assert HFConfigExtractor().extract(claim("model.experts_total"), text, page_url=CONFIG_URL) == [
        Reading("Alpha", 64, "experts"),
    ]


def test_review_top_level_experts_block_the_dense_rule():
    text = (
        '{"num_local_experts":16,"num_experts_per_tok":1,'
        '"text_config":{"model_type":"x","num_attention_heads":8}}'
    )
    assert HFConfigExtractor().extract(claim(), text, page_url=CONFIG_URL) == [
        Reading("Alpha", "MoE")
    ]
    assert not DenseActiveEqualsTotalExtractor().accepts(text)
    assert HFConfigExtractor().extract(claim("model.experts_total"), text, page_url=CONFIG_URL) == [
        Reading("Alpha", 16, "experts")
    ]
    assert HFConfigExtractor().extract(
        claim("model.experts_per_token"), text, page_url=CONFIG_URL
    ) == [Reading("Alpha", 1, "experts")]


def test_review_nemotron_h_cannot_use_dense_equality():
    text = (
        '{"model_type":"nemotron_h","num_attention_heads":32,"hybrid_override_pattern":"M-M-M*-M-"}'
    )
    api = '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":9000000000}}}'
    assert (
        DenseActiveEqualsTotalExtractor().extract(
            claim("model.parameters_active"),
            text,
            page_url=CONFIG_URL,
            bindings=[(text, CONFIG_URL), (api, API_URL)],
        )
        == []
    )


@pytest.mark.parametrize(
    "census,expected",
    [
        ({"parameters": {"BF16": 700, "F16": 2, "F32": 1}}, [703]),
        ({"parameters": {"BF16": 700, "F8_E4M3": 2, "F32": 1}}, []),
        ({"parameters": {"BF16": 700, "I32": 2, "U8": 1}}, []),
        ({"parameters": {"F8_E4M3": 700, "F32": 3}}, []),
        ({"total": 703}, []),
    ],
)
def test_dense_rule_requires_an_unpacked_float_census(census, expected):
    text = '{"model_type":"llama","num_attention_heads":32}'
    api = json.dumps({"id": "lab/Alpha", "safetensors": census})
    assert [
        r.value
        for r in DenseActiveEqualsTotalExtractor().extract(
            claim("model.parameters_active"),
            text,
            page_url=CONFIG_URL,
            bindings=[(api, API_URL)],
        )
    ] == expected


@pytest.mark.parametrize(
    "extra,card",
    [
        ({"hidden_size_per_layer_input": 256}, "# Alpha\nAlpha is released."),
        ({"text_config": {"vocab_size_per_layer_input": 256}}, "# Alpha\nAlpha is released."),
        ({}, "# Alpha\nAlpha uses 2.3B active parameters."),
        ({}, "# Alpha\nAlpha uses 2.3B effective parameters."),
        ({}, "# Alpha\n| Effective parameters | 2.3B |"),
        ({}, "# Alpha\nAlpha activates 2.3B parameters per token."),
    ],
)
def test_dense_rule_defers_to_active_or_effective_wording_and_ple(extra, card):
    config = json.dumps({"model_type": "gemma4_text", "num_attention_heads": 8, **extra})
    api = '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":5123178051}}}'
    assert (
        DenseActiveEqualsTotalExtractor().extract(
            claim("model.parameters_active"),
            config,
            page_url=CONFIG_URL,
            bindings=[(api, API_URL), (card, README_URL)],
        )
        == []
    )


@pytest.mark.parametrize(
    "name,amount", [("gemma-4-e2b-it", 2_300_000_000), ("gemma-4-e4b-it", 4_500_000_000)]
)
def test_effective_parameter_table_binds_to_the_gemma_variant(name, amount):
    c = replace(
        claim("model.parameters_active"), subject="google/" + name, names=(name, "google/" + name)
    )
    text = (
        "# Gemma 4\n| Property | E2B | E4B |\n"
        "| Total Parameters | 2.3B effective <br> (5.1B with embeddings) | "
        "4.5B effective <br> (8B with embeddings) |\n"
    )
    url = "https://huggingface.co/google/" + name + "/raw/main/README.md"
    assert ModelCardParamsExtractor().extract(c, text, page_url=url) == [
        Reading(name, amount, "parameters")
    ]


@pytest.mark.parametrize(
    "label", ["Number of Total Parameters", "Total Parameters", "Number of Parameters"]
)
@pytest.mark.parametrize("value", ["4.92B-A0.43B", "4.92B A0.43B"])
def test_parameter_field_shorthand_requires_a_matching_tensor_total(label, value):
    text = f"# Alpha\n- {label}: {value}\n"
    reader = ModelCardParamsExtractor()
    c = claim("model.parameters_active")
    api = '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":4919641986}}}'
    assert reader.extract(c, text, page_url=README_URL, bindings=[(api, API_URL)]) == [
        Reading("Alpha", 430_000_000, "parameters")
    ]
    assert reader.extract(c, text, page_url=README_URL) == []
    wrong = api.replace("4919641986", "4021782018")
    assert reader.extract(c, text, page_url=README_URL, bindings=[(wrong, API_URL)]) == []
    assert (
        reader.extract(
            c, text, page_url=README_URL, bindings=[(api.replace("Alpha", "Beta"), API_URL)]
        )
        == []
    )
    assert (
        reader.extract(c, "# Alpha-4.92B-A0.43B", page_url=README_URL, bindings=[(api, API_URL)])
        == []
    )


def test_json_normalizer_rejects_deeply_nested_json(monkeypatch):
    from json.scanner import py_make_scanner

    from decision.normalise import NORMALISERS, UnsupportedContentError, normalise_document

    body = b'{"nested":' + b"[" * 10_000 + b"0" + b"]" * 10_000 + b"}"
    decoder = json.JSONDecoder()
    decoder.scan_once = py_make_scanner(decoder)
    monkeypatch.setattr(json, "loads", decoder.decode)
    with pytest.raises(UnsupportedContentError, match="invalid_json"):
        normalise_document(body, NORMALISERS["json-default"])


def test_hardware_claim_with_an_hf_and_non_hf_citation_remains_skipped(tmp_path):
    regions, refs = retained(
        tmp_path,
        [
            ("config", CONFIG_URL, '{"num_experts":8}'),
            ("lab", "https://lab.example/Alpha", "Alpha is an MoE."),
        ],
    )
    result = verify(
        claim("model.architecture", "MoE", refs),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert result.outcome == "skipped"
    assert result.reason == "unbound_hf_copy"


def test_html_specs_with_quantization_and_modality_keep_the_repository_subject():
    text = """# Alpha
## 2. Model Summary
<table>
<tr><td>Architecture</td><td>Mixture-of-Experts (MoE)</td></tr>
<tr><td>Activated Parameters</td><td>104B</td></tr>
<tr><td>Vision Encoder</td><td>MoonViT-V2</td></tr>
<tr><td>Quantization</td><td>MXFP4 weights / MXFP8 activations</td></tr>
<tr><td>Modality</td><td>Text, Image</td></tr>
</table>"""
    assert ModelCardParamsExtractor().extract(
        claim("model.parameters_active"),
        text,
        page_url=README_URL,
    ) == [Reading("Alpha", 104_000_000_000, "parameters")]
