"""MODEL-348: literal readings from retained HF configs and model cards."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from pathlib import Path

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
    assert reader.extract(
        c, config, page_url=CONFIG_URL, bindings=[(api, API_URL), ("# Alpha\nA model.", README_URL)]
    ) == [
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
        assert (
            reader.extract(
                c,
                other,
                page_url=CONFIG_URL,
                bindings=[(api, API_URL), ("# Alpha\nA model.", README_URL)],
            )
            == []
        )
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
            ("readme", README_URL, "# Alpha\nA model."),
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
            (
                "api",
                API_URL,
                '{"id":"lab/Alpha","config":{"architectures":["MysteryModel"]},"safetensors":{"parameters":{"BF16":671000000000}}}',
            ),
            ("config", CONFIG_URL, '{"model_type":"mixtral","num_local_experts":8}'),
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


def test_gemma_null_expert_placeholders_allow_dense_but_populated_settings_block():
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
        Reading("Alpha", "dense-transformer")
    ]
    config["expert_custom"] = 1
    assert reader.extract(claim(), json.dumps(config), page_url=CONFIG_URL) == []


@pytest.mark.parametrize(
    "name,total,active,heads,ple_hidden",
    [
        ("gemma-4-31b-it", 31_273_088_876, None, 32, 0),
        ("gemma-4-e2b-it", 5_123_178_051, 2_300_000_000, 8, 256),
        ("gemma-4-e4b-it", 7_996_156_490, 4_500_000_000, 8, 256),
    ],
)
def test_retained_gemma_configs_have_dense_backbones_and_dimension_gated_ple(
    tmp_path, name, total, active, heads, ple_hidden
):
    config = (Path(__file__).parent / "fixtures" / "hf-gemma-4" / f"{name}.json").read_text()
    text_config = json.loads(config)["text_config"]
    assert text_config["enable_moe_block"] is False
    assert text_config["num_experts"] is None
    assert text_config["top_k_experts"] is None
    assert text_config["expert_intermediate_size"] is None
    assert text_config["num_attention_heads"] == heads
    assert text_config["hidden_size_per_layer_input"] == ple_hidden
    assert text_config["vocab_size_per_layer_input"] == 262144
    repo = f"google/{name}"
    url = f"https://huggingface.co/{repo}/resolve/main/config.json"
    c = replace(claim(), subject=repo, names=(name, repo))
    assert HFConfigExtractor().extract(c, config, page_url=url) == [
        Reading(name, "dense-transformer")
    ]
    for facet in ("model.experts_total", "model.experts_per_token"):
        assert HFConfigExtractor().extract(replace(c, field=facet), config, page_url=url) == []
    card = (
        "### Dense Models\n"
        "| Property | E2B | E4B | 31B Dense |\n"
        "| --- | --- | --- | --- |\n"
        "| Total Parameters | 2.3B effective (5.1B with embeddings) | "
        "4.5B effective (8B with embeddings) | 30.7B |\n"
        '\nThe "E" in E2B and E4B stands for "effective" parameters.\n'
        "### Mixture-of-Experts (MoE) Model\n"
        "| Property | 26B A4B MoE |\n"
        "| --- | --- |\n"
        "| Active Parameters | 3.8B |\n"
    )
    api = json.dumps({"id": repo, "safetensors": {"parameters": {"BF16": total}}})
    api_url = f"https://huggingface.co/api/models/{repo}"
    readme_url = f"https://huggingface.co/{repo}/raw/main/README.md"
    c = replace(c, field="model.parameters_active", unit="parameters")
    assert ModelCardParamsExtractor().extract(c, card, page_url=readme_url) == (
        [] if active is None else [Reading(name, active, "parameters")]
    )
    assert (
        DenseActiveEqualsTotalExtractor().extract(
            c, config, page_url=url, bindings=[(api, api_url), (card, readme_url)]
        )
        == []
    )
    if name == "gemma-4-31b-it":
        regions, refs = retained(
            tmp_path,
            [("config", url, config), ("api", api_url, api), ("readme", readme_url, card)],
        )
        for sid in ("config", "api"):
            regions.sources[sid] = regions.sources[sid].model_copy(
                update={"normaliser": "json-default"}
            )
        result = verify(
            replace(c, value=31_273_088_876, sources=tuple(refs)),
            regions,
            deterministic_extractors(),
            today=date(2026, 10, 10),
        )
        assert result.outcome == "skipped", result
        assert result.reason == "no_hf_reading"


@pytest.mark.parametrize(
    "extra,expected",
    [
        ({"num_experts": None}, "dense-transformer"),
        ({"num_experts": 0}, "dense-transformer"),
        ({"num_experts": False}, "dense-transformer"),
        ({"num_experts": 1}, "dense-transformer"),
        ({"vision_config": {"num_experts": None}}, "dense-transformer"),
        ({"vision_config": {"expert_intermediate_size": 128}}, None),
        ({"enable_moe_block": False, "num_experts": 1}, None),
        ({"enable_moe_block": False, "num_experts": 0}, None),
        ({"enable_moe_block": False, "num_experts": 8}, "MoE"),
        ({"enable_moe_block": True, "num_experts": None}, None),
        ({"use_moe": False, "num_experts": None}, "dense-transformer"),
        ({"moe_enabled": False, "other": {"top_k_experts": 1}}, None),
        ({"enable_moe": False, "layers": [{"num_experts": 8}]}, "MoE"),
        ({"expert_custom": False}, None),
        ({"expert_custom": 0}, None),
        ({"expert_custom": 1}, None),
    ],
)
def test_populated_expert_settings_and_explicit_disable_conflicts(extra, expected):
    config = {"model_type": "llama", "num_attention_heads": 8, **extra}
    assert hf_config_architecture(config) == expected
    text = json.dumps(config)
    api = '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":703}}}'
    assert DenseActiveEqualsTotalExtractor().extract(
        claim("model.parameters_active"),
        text,
        page_url=CONFIG_URL,
        bindings=[(api, API_URL), ("# Alpha\nA model.", README_URL)],
    ) == (
        [Reading("Alpha", 703, "parameters")]
        if expected == "dense-transformer" and "vision_config" not in extra
        else []
    )


@pytest.mark.parametrize("ple", [None, 0])
@pytest.mark.parametrize("key", ["hidden_size_per_layer_input", "vocab_size_per_layer_input"])
@pytest.mark.parametrize(
    "card,expected",
    [
        ("# Alpha\nAlpha is released.", [Reading("Alpha", 703, "parameters")]),
        ("# Beta\n| Effective Parameters | 2.3B |", [Reading("Alpha", 703, "parameters")]),
        ("# Alpha\nBeta uses 2.3B effective parameters.", [Reading("Alpha", 703, "parameters")]),
        ("# Alpha\nAlpha uses 2-3B effective parameters.", []),
        ("# Alpha\n| Effective Parameters | unknown |", []),
        (
            "# Alpha\n| Model | Total Parameters |\n| --- | --- |\n"
            "| Alpha | 2.3B effective |\n| Beta | 3.5B |",
            [],
        ),
        (
            "# Alpha\n| Model | Total Parameters |\n| --- | --- |\n"
            "| Alpha | 0.000000703B |\n| Beta | 2.3B effective |",
            [Reading("Alpha", 703, "parameters")],
        ),
    ],
)
def test_dense_equality_ignores_empty_ple_and_other_variants(ple, key, card, expected):
    text = json.dumps({"model_type": "llama", "num_attention_heads": 8, key: ple})
    api = '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":703}}}'
    assert (
        DenseActiveEqualsTotalExtractor().extract(
            claim("model.parameters_active"),
            text,
            page_url=CONFIG_URL,
            bindings=[(api, API_URL), (card, README_URL)],
        )
        == expected
    )


@pytest.mark.parametrize(
    "ple_settings",
    [
        {"vocab_size_per_layer_input": 262144},
        {"hidden_size_per_layer_input": 0, "vocab_size_per_layer_input": 262144},
        {"hidden_size_per_layer_input": None, "vocab_size_per_layer_input": 262144},
        {"hidden_size_per_layer_input": -1, "vocab_size_per_layer_input": 262144},
    ],
)
@pytest.mark.parametrize("nested", [False, True])
def test_dense_equality_requires_positive_ple_dimension_to_block(ple_settings, nested):
    config = {"model_type": "llama", "num_attention_heads": 8}
    config = {"text_config": {**config, **ple_settings}} if nested else {**config, **ple_settings}
    api = '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":703}}}'
    assert DenseActiveEqualsTotalExtractor().extract(
        claim("model.parameters_active"),
        json.dumps(config),
        page_url=CONFIG_URL,
        bindings=[(api, API_URL), ("# Alpha\nA model.", README_URL)],
    ) == [Reading("Alpha", 703, "parameters")]


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
            "dense-transformer",
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
            bindings=[(api, API_URL), ("# Alpha\nA model.", README_URL)],
        )
    ] == expected


@pytest.mark.parametrize(
    "extra,card",
    [
        ({"hidden_size_per_layer_input": 256}, "# Alpha\nAlpha is released."),
        ({"text_config": {"hidden_size_per_layer_input": 256}}, "# Alpha\nAlpha is released."),
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
    assert reader.extract(
        c, text, page_url=README_URL, bindings=[(api, API_URL), ("# Alpha\nA model.", README_URL)]
    ) == [Reading("Alpha", 430_000_000, "parameters")]
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
        reader.extract(
            c,
            "# Alpha-4.92B-A0.43B",
            page_url=README_URL,
            bindings=[(api, API_URL), ("# Alpha\nA model.", README_URL)],
        )
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


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "Alpha has 3B active parameters, compared with the 22B active parameters of Beta.",
            [3_000_000_000],
        ),
        (
            "Alpha uses 3B active parameters; the previous release used 22B active parameters.",
            [3_000_000_000],
        ),
        (
            "Alpha is 30B total. For reference, 22B active parameters is typical of larger models.",
            [],
        ),
        ("Alpha matches models with 22B active parameters.", []),
        ("Alpha outperforms 22B active parameter models.", []),
        ("Alpha (3B active parameters) beats Qwen3-235B (22B active parameters).", [3_000_000_000]),
        ("Alpha-Base has 3B active parameters.", []),
        ("Alpha Lite has 1B active parameters.", []),
        ("Alpha Lite has 1B active parameters and Alpha Pro has 9B active parameters.", []),
        ("Alpha matches the 22B active parameters of Beta.", []),
        ("Alpha matches 22B active parameters compared with Beta.", []),
        ("Alpha matches 22B active parameters unlike Beta.", []),
        ("Alpha has 22B active parameters belonging to Beta.", []),
        (
            "Alpha has 3B active parameters. Alpha has 4B active parameters.",
            [3_000_000_000, 4_000_000_000],
        ),
        (
            "| Property | Alpha | Alpha Lite |\n|---|---|---|\n| Active Parameters | 3B | 1B |",
            [3_000_000_000],
        ),
        (
            "| Property | Alpha Lite | Alpha |\n|---|---|---|\n| Active Parameters | 1B | 3B |",
            [3_000_000_000],
        ),
    ],
)
def test_round4_prose_and_column_probes(text, expected):
    assert [
        r.value
        for r in ModelCardParamsExtractor().extract(
            claim("model.parameters_active"),
            "# Alpha\n" + text,
            page_url=README_URL,
        )
    ] == expected


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"model_type": "mamba", "hidden_size": 768, "state_size": 16}, "SSM"),
        ({"model_type": "mamba2", "num_heads": 24}, "SSM"),
        ({"model_type": "rwkv7"}, "SSM"),
        ({"model_type": "mamba2", "num_attention_heads": 8}, "hybrid-SSM-transformer"),
        (
            {
                "model_type": "qwen3_next",
                "num_attention_heads": 16,
                "layer_types": ["linear_attention", "full_attention"],
                "num_experts": 512,
            },
            "MoE",
        ),
        (
            {"model_type": "llama", "num_attention_heads": 8, "cache_implementation": "hybrid"},
            "dense-transformer",
        ),
        (
            {"model_type": "gemma2", "num_attention_heads": 8, "final_logit_softcapping": 30.0},
            "dense-transformer",
        ),
        (
            {
                "model_type": "gemma3",
                "text_config": {
                    "model_type": "gemma3_text",
                    "num_attention_heads": 8,
                    "cache_implementation": "hybrid",
                },
            },
            "dense-transformer",
        ),
    ],
)
def test_round4_architecture_probes(config, expected):
    assert hf_config_architecture(config) == expected


@pytest.mark.parametrize(
    "facet,value,config,api,readme,outcome,reason",
    [
        (
            "model.parameters_active",
            8_030_000_000,
            {"model_type": "llama", "num_attention_heads": 32},
            8_030_000_000,
            None,
            "skipped",
            "no_hf_reading",
        ),
        (
            "model.parameters_active",
            8_030_000_000,
            {"model_type": "llama", "num_attention_heads": 32},
            8_030_000_000,
            "Alpha has 2B effective parameters (8B with embeddings).",
            "mismatch",
            None,
        ),
        ("model.parameters_total", None, None, None, "A model.", "skipped", "no_hf_reading"),
        (
            "model.parameters_total",
            None,
            {"model_type": "llama", "num_attention_heads": 32},
            None,
            None,
            "skipped",
            "no_hf_reading",
        ),
        (
            "model.parameters_active",
            None,
            None,
            None,
            "A model.",
            "skipped",
            "retained_census_required",
        ),
        (
            "model.parameters_active",
            22_000_000_000,
            None,
            None,
            "Alpha has 3B active parameters, compared with the 22B active parameters of Beta.",
            "mismatch",
            None,
        ),
        (
            "model.parameters_active",
            430_000_000,
            None,
            4_919_641_986,
            "- Number of Parameters: 4.92B-A0.43B",
            "verified",
            None,
        ),
        (
            "model.parameters_total",
            8_030_000_000,
            {"model_type": "llama", "num_attention_heads": 32},
            8_030_000_000,
            None,
            "verified",
            None,
        ),
        (
            "model.experts_total",
            1,
            {"model_type": "llama", "num_attention_heads": 32},
            None,
            None,
            "skipped",
            "no_hf_reading",
        ),
        ("model.architecture", "MoE", None, None, "Alpha is an MoE.", "skipped", "no_hf_reading"),
        (
            "model.architecture",
            None,
            {"model_type": "qwen4", "num_attention_heads": 32},
            None,
            None,
            "skipped",
            "no_hf_reading",
        ),
        (
            "model.experts_total",
            None,
            {"model_type": "qwen4", "num_attention_heads": 32},
            None,
            None,
            "skipped",
            "no_hf_reading",
        ),
        (
            "model.experts_total",
            None,
            {"model_type": "x_moe", "num_experts": [64, 128], "num_experts_per_tok": 8},
            None,
            None,
            "skipped",
            "no_hf_reading",
        ),
        (
            "model.architecture",
            None,
            {"model_type": "llama", "num_attention_heads": 32, "moe_intermediate_size": 1408},
            None,
            None,
            "skipped",
            "no_hf_reading",
        ),
        (
            "model.experts_total",
            None,
            {"model_type": "llama", "num_attention_heads": 32},
            None,
            None,
            "skipped",
            "no_hf_reading",
        ),
        (
            "model.parameters_active",
            3_000_000_000,
            None,
            None,
            "Alpha has 3B active parameters. Alpha has 4B active parameters.",
            "skipped",
            "ambiguous_hf_reading",
        ),
        (
            "model.parameters_active",
            None,
            {"model_type": "llama", "num_attention_heads": 32},
            8_030_000_000,
            "A model.",
            "mismatch",
            None,
        ),
        (
            "model.parameters_active",
            None,
            {"model_type": "mixtral", "num_experts": 8},
            8_030_000_000,
            "A model.",
            "verified",
            None,
        ),
    ],
)
def test_round4_verifier_probes(tmp_path, facet, value, config, api, readme, outcome, reason):
    docs = []
    if config is not None:
        docs.append(("config", CONFIG_URL, json.dumps(config)))
    if api is not None:
        docs.append(
            (
                "api",
                API_URL,
                json.dumps({"id": "lab/Alpha", "safetensors": {"parameters": {"BF16": api}}}),
            )
        )
    if readme is not None:
        docs.append(("readme", README_URL, "# Alpha\n" + readme))
    regions, refs = retained(tmp_path, docs)
    result = verify(
        claim(facet, value, refs), regions, deterministic_extractors(), today=date(2026, 10, 10)
    )
    assert (result.outcome, result.reason) == (outcome, reason)


@pytest.mark.parametrize(
    "tower", ["vision_config", "audio_config", "image_encoder", "audio_encoder_config"]
)
@pytest.mark.parametrize("value", [None, {}, {"model_type": "encoder"}])
def test_round4_nontext_tower_blocks_equality(tower, value):
    config = json.dumps({"model_type": "llama", "num_attention_heads": 32, tower: value})
    api = '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":8030000000}}}'
    assert DenseActiveEqualsTotalExtractor().extract(
        claim("model.parameters_active"),
        config,
        page_url=CONFIG_URL,
        bindings=[(api, API_URL), ("# Alpha\nA model.", README_URL)],
    ) == ([Reading("Alpha", 8_030_000_000, "parameters")] if value is None else [])


@pytest.mark.parametrize(
    "total,expected", [("8.0B", [Reading("Alpha", 8_030_000_000, "parameters")]), ("7.0B", [])]
)
def test_round4_card_total_must_agree_with_census(total, expected):
    assert (
        DenseActiveEqualsTotalExtractor().extract(
            claim("model.parameters_active"),
            '{"model_type":"llama","num_attention_heads":32}',
            page_url=CONFIG_URL,
            bindings=[
                ('{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":8030000000}}}', API_URL),
                (f"# Alpha\n| Property | Alpha |\n| Total Parameters | {total} |", README_URL),
            ],
        )
        == expected
    )


@pytest.mark.parametrize(
    "name,repo,card,expected",
    [
        (
            "glm-4-5",
            "zai-org/GLM-4.5",
            (
                "# GLM-4.5\n| Model | Total Parameters | Active Parameters |\n|---|---|---|\n| "
                "GLM-4.5 | 355B | 32B |\n| GLM-4.5-Air | 106B | 12B |"
            ),
            [32_000_000_000],
        ),
        (
            "glm-4-5-air",
            "zai-org/GLM-4.5-Air",
            (
                "# GLM-4.5-Air\n| Model | Total Parameters | Active Parameters "
                "|\n|---|---|---|\n| GLM-4.5 | 355B | 32B |\n| GLM-4.5-Air | 106B | 12B |"
            ),
            [12_000_000_000],
        ),
        (
            "deepseek-v3-1",
            "deepseek-ai/DeepSeek-V3.1",
            (
                "# DeepSeek-V3.1\n| Model | #Total Params | #Activated Params "
                "|\n|---|---|---|\n| DeepSeek-V3.1-Base | 671B | 37B |\n| DeepSeek-V3.1 | 671B "
                "| 37B |"
            ),
            [37_000_000_000],
        ),
        (
            "qwen3-30b-a3b",
            "Qwen/Qwen3-30B-A3B",
            (
                "# Qwen3-30B-A3B\nQwen3-30B-A3B has 3.3B activated parameters. "
                "Qwen3-235B-A22B has 22B activated parameters."
            ),
            [3_300_000_000],
        ),
        (
            "qwen3-30b-a3b",
            "Qwen/Qwen3-30B-A3B",
            (
                "# Qwen3-30B-A3B\n- Number of Parameters: 30.5B in total and 3.3B "
                "activated\n- Number of Activated Experts: 8"
            ),
            [],
        ),
        (
            "gemma-4-e2b-it",
            "google/gemma-4-e2b-it",
            (
                "# Gemma 4\n| Property | E2B | E4B | 31B Dense |\n|---|---|---|---|\n| Total "
                "Parameters | 2.3B effective <br> (5.1B with embeddings) | 4.5B effective "
                "<br> (8B with embeddings) | 30.7B |"
            ),
            [2_300_000_000],
        ),
        (
            "gemma-4-e4b-it",
            "google/gemma-4-e4b-it",
            (
                "# Gemma 4\n| Property | E2B | E4B | 31B Dense |\n|---|---|---|---|\n| Total "
                "Parameters | 2.3B effective <br> (5.1B with embeddings) | 4.5B effective "
                "<br> (8B with embeddings) | 30.7B |"
            ),
            [4_500_000_000],
        ),
        (
            "gemma-4-31b-it",
            "google/gemma-4-31b-it",
            (
                "# Gemma 4\n| Property | E2B | E4B | 31B Dense |\n|---|---|---|---|\n| Total "
                "Parameters | 2.3B effective <br> (5.1B with embeddings) | 4.5B effective "
                "<br> (8B with embeddings) | 30.7B |"
            ),
            [],
        ),
    ],
)
def test_round4_named_variant_probes(name, repo, card, expected):
    c = replace(claim("model.parameters_active"), names=(name, repo))
    assert [
        r.value
        for r in ModelCardParamsExtractor().extract(
            c,
            card,
            page_url=f"https://huggingface.co/{repo}/raw/main/README.md",
        )
    ] == expected


def test_round4_retained_gemma31_wording_and_readings():
    card = (Path(__file__).parent / "fixtures/hf-gemma-4/README.md").read_text()
    c = replace(claim("model.parameters_active"), names=("gemma-4-31b-it", "google/gemma-4-31B-it"))
    assert ModelCardParamsExtractor().wording(c, card) == ()
    assert (
        ModelCardParamsExtractor().extract(
            c,
            card,
            page_url="https://huggingface.co/google/gemma-4-31B-it/raw/main/README.md",
        )
        == []
    )


@pytest.mark.parametrize("tower", [True, False])
def test_round4_gemma_like_verification_cannot_use_dense_equality(tmp_path, tower):
    config = {
        "model_type": "gemma4",
        "text_config": {
            "model_type": "gemma4_text",
            "num_attention_heads": 32,
            "hidden_size_per_layer_input": 0,
            "vocab_size_per_layer_input": 262144,
        },
        "enable_moe_block": False,
        "num_experts": None,
    }
    if tower:
        config["vision_config"] = {"model_type": "gemma4_vision", "num_attention_heads": 16}
    regions, refs = retained(
        tmp_path,
        [
            ("config", CONFIG_URL, json.dumps(config)),
            (
                "api",
                API_URL,
                '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":31273088876}}}',
            ),
            (
                "readme",
                README_URL,
                (
                    "# Alpha\n| Property | Alpha |\n| Total Parameters | 30.7B |\n| Vision Encoder "
                    "Parameters | ~550M |"
                ),
            ),
        ],
    )
    result = verify(
        claim("model.parameters_active", 31_273_088_876, refs),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert (result.outcome, result.reason) == ("skipped", "no_hf_reading")


@pytest.mark.parametrize(
    "config,expected",
    [
        (
            {"model_type": "mamba2", "num_heads": 24, "layer_types": ["mamba", "attention"]},
            "hybrid-SSM-transformer",
        ),
        ({"model_type": "mamba", "layer_types": None}, "SSM"),
    ],
)
def test_round4_recurrent_layer_readings(config, expected):
    assert hf_config_architecture(config) == expected


@pytest.mark.parametrize(
    "card,expected",
    [
        ("Alpha has 7.0B total parameters.", []),
        ("Alpha has 8.0B parameters.", [Reading("Alpha", 8_030_000_000, "parameters")]),
        ("Total Parameters: 7.0B", []),
        (
            "| Property | Alpha | Alpha Lite |\n| Total Parameters | 8.0B | 7.0B |",
            [Reading("Alpha", 8_030_000_000, "parameters")],
        ),
    ],
)
def test_round4_card_total_binding_and_precision(card, expected):
    assert (
        DenseActiveEqualsTotalExtractor().extract(
            claim("model.parameters_active"),
            '{"model_type":"llama","num_attention_heads":32}',
            page_url=CONFIG_URL,
            bindings=[
                ('{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":8030000000}}}', API_URL),
                ("# Alpha\n" + card, README_URL),
            ],
        )
        == expected
    )


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"model_type": "falcon_mamba", "state_size": 16, "conv_kernel": 4}, "SSM"),
        ({"model_type": "x", "text_config": {"model_type": "mamba"}}, "SSM"),
        ({"model_type": "rwkv7", "attention_hidden_size": 2048}, "SSM"),
        ({"model_type": "mamba2", "num_heads": 24, "n_groups": 1}, "SSM"),
        ({"model_type": "jamba", "num_attention_heads": 32, "num_experts": 1}, None),
        ({"model_type": "zamba2", "num_attention_heads": 32}, None),
        ({"model_type": "custom", "ssm_state_size": 16}, "SSM"),
        ({"model_type": "falcon_mamba", "num_attention_heads": 32}, "hybrid-SSM-transformer"),
        ({"model_type": "falcon_mamba", "layer_types": ["attention"]}, "hybrid-SSM-transformer"),
        ({"model_type": "hybrid"}, None),
        ({"model_type": "custom", "hybrid_override_pattern": "unknown"}, None),
    ],
)
def test_round5_recurrent_probes(config, expected):
    assert hf_config_architecture(config) == expected


@pytest.mark.parametrize(
    "config,outcome,reason",
    [
        (None, "skipped", "retained_config_required"),
        (
            {"model_type": "granite", "num_attention_heads": 32},
            "skipped",
            "non_dense_config_required",
        ),
        (
            {"model_type": "exaone4", "num_attention_heads": 32},
            "skipped",
            "non_dense_config_required",
        ),
        (
            {"model_type": "cohere2", "num_attention_heads": 32},
            "skipped",
            "non_dense_config_required",
        ),
        (
            {"model_type": "smollm3", "num_attention_heads": 32},
            "skipped",
            "non_dense_config_required",
        ),
        (
            {"model_type": "internlm3", "num_attention_heads": 32},
            "skipped",
            "non_dense_config_required",
        ),
        ({"model_type": "falcon_mamba", "num_attention_heads": 32}, "verified", None),
        ({"model_type": "falcon_mamba", "state_size": 16}, "verified", None),
        ({"model_type": "mixtral", "num_experts": 8}, "verified", None),
        (
            {
                "model_type": "gemma3",
                "text_config": {"model_type": "gemma3_text", "num_attention_heads": 16},
                "vision_config": {"model_type": "siglip"},
            },
            "skipped",
            "non_dense_config_required",
        ),
        ({"model_type": "llama", "num_attention_heads": 32}, "mismatch", None),
        ({"model_type": "hybrid"}, "skipped", "non_dense_config_required"),
    ],
)
def test_round5_active_absence_needs_a_cited_non_dense_config(tmp_path, config, outcome, reason):
    docs = [
        ("readme", README_URL, "# Alpha\nA model.\n"),
        ("api", API_URL, '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":8030000000}}}'),
    ]
    if config is not None:
        docs.append(("config", CONFIG_URL, json.dumps(config)))
    regions, refs = retained(tmp_path, docs)
    result = verify(
        claim("model.parameters_active", None, refs),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert (result.outcome, result.reason) == (outcome, reason)
    if outcome == "verified":
        assert result.verification.method == "hf-architecture-absence@1"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Alpha is a MoE model with 3B active parameters.", [3_000_000_000]),
        ("Alpha has 3B active parameters out of 30B total.", []),
        ("3B active parameters out of 30B total", []),
        (
            "Alpha is a language model with 671B total parameters with 37B activated.",
            [37_000_000_000],
        ),
        ("Alpha activates 3B active parameters of its 30B.", []),
        ("Alpha: 30B total, 3B active parameters.", [3_000_000_000]),
        ("Alpha, unlike Beta, has 3B active parameters.", []),
        ("Alpha uses 3B active parameters (Beta uses 9B active parameters).", []),
        ("Alpha uses 3B active parameters while Beta uses 9B active parameters.", [3_000_000_000]),
        ("Alpha uses 3B active parameters, and Beta uses 9B active parameters.", [3_000_000_000]),
        ("Beta uses 9B active parameters, and Alpha uses 3B active parameters.", [3_000_000_000]),
        ("Alpha and Beta use 3B and 9B active parameters respectively.", []),
        ("Alpha uses 3B active parameters versus 9B active parameters in Beta.", []),
        (
            "Alpha has 3B active parameters, vs. 9B active parameters for Beta-Large.",
            [3_000_000_000],
        ),
        ("Alpha has 3B active parameters, Beta 9B active parameters.", [3_000_000_000]),
        ("Alpha matches a model with 22B active parameters.", []),
        ("Alpha matches a language model with 671B total parameters with 37B activated.", []),
        ("Alpha matches 3B active parameters out of Beta's 30B total.", []),
    ],
)
def test_round5_subject_prose_probes(text, expected):
    assert [
        reading.value
        for reading in ModelCardParamsExtractor().extract(
            claim("model.parameters_active"),
            "# Alpha\n" + text,
            page_url=README_URL,
        )
    ] == expected


@pytest.mark.parametrize(
    "tower,value,expected",
    [
        ("mm_vision_tower", "openai/clip", []),
        ("img_processor", {"name": "clip"}, []),
        ("audio_processor", {"name": "conformer"}, []),
        ("visual", {"depth": 32}, []),
        ("vision_config", None, [Reading("Alpha", 8_030_000_000, "parameters")]),
        ("use_vision_tower", False, []),
        ("img_processor", None, [Reading("Alpha", 8_030_000_000, "parameters")]),
        ("audio_processor", None, [Reading("Alpha", 8_030_000_000, "parameters")]),
        ("visual", None, [Reading("Alpha", 8_030_000_000, "parameters")]),
    ],
)
def test_round5_nontext_tower_probes(tower, value, expected):
    assert (
        DenseActiveEqualsTotalExtractor().extract(
            claim("model.parameters_active"),
            json.dumps({"model_type": "llama", "num_attention_heads": 32, tower: value}),
            page_url=CONFIG_URL,
            bindings=[
                ('{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":8030000000}}}', API_URL),
                ("# Alpha\nA model.\n", README_URL),
            ],
        )
        == expected
    )


@pytest.mark.parametrize(
    "card,expected",
    [
        ("Alpha has 8B parameters.", [Reading("Alpha", 8_030_000_000, "parameters")]),
        ("Alpha has 7B parameters.", []),
        ("| Model | Parameters |\n|---|---|\n| Alpha | 9B |", []),
        ("- Number of Parameters: 7.0B", []),
        ("- Total Parameters: 6.2B", []),
        ("Alpha is a 6B parameter model.", []),
        ("Alpha is an 8B parameter model.", [Reading("Alpha", 8_030_000_000, "parameters")]),
        ("| Model | Params |\n|---|---|\n| **Alpha** | 6B |", []),
        (
            "The model has 6.0B parameters in total.",
            [Reading("Alpha", 8_030_000_000, "parameters")],
        ),
    ],
)
def test_round5_card_total_probes(card, expected):
    assert (
        DenseActiveEqualsTotalExtractor().extract(
            claim("model.parameters_active"),
            '{"model_type":"llama","num_attention_heads":32}',
            page_url=CONFIG_URL,
            bindings=[
                ('{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":8030000000}}}', API_URL),
                ("# Alpha\n" + card, README_URL),
            ],
        )
        == expected
    )


@pytest.mark.parametrize(
    "card,value",
    [
        ("Alpha is a MoE model with 3B active parameters.", 3_000_000_000),
        (
            "Alpha is a language model with 671B total parameters with 37B activated.",
            37_000_000_000,
        ),
    ],
)
def test_round5_own_prose_verifies_from_retained_readme(tmp_path, card, value):
    regions, refs = retained(tmp_path, [("readme", README_URL, "# Alpha\n" + card)])
    result = verify(
        claim("model.parameters_active", value, refs),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert (result.outcome, result.reason) == ("verified", None)
    assert result.verification.method == "model-card-params@1"


def test_round5_uncited_config_cannot_support_active_absence(tmp_path):
    regions, refs = retained(
        tmp_path,
        [
            ("config", CONFIG_URL, '{"model_type":"mixtral","num_experts":8}'),
            ("readme", README_URL, "# Alpha\nA model."),
            ("api", API_URL, '{"id":"lab/Alpha","safetensors":{"parameters":{"BF16":8030000000}}}'),
        ],
    )
    result = verify(
        claim("model.parameters_active", None, refs[1:]),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert (result.outcome, result.reason) == ("skipped", "retained_config_required")


@pytest.mark.parametrize(
    "table,expected",
    [
        (
            "| Property | **Alpha** | Alpha Lite |\n|---|---|---|\n| Active Parameters | 3B | 1B |",
            [Reading("Alpha", 3_000_000_000, "parameters")],
        ),
        (
            "| Property | `Alpha` |\n|---|---|\n| Active Parameters | 3B |",
            [Reading("Alpha", 3_000_000_000, "parameters")],
        ),
        ("| Property | lab/Alpha |\n|---|---|\n| Active Parameters | 3B |", []),
        (
            "| Property | Alpha-Lite | Alpha |\n|---|---|---|\n| Active Parameters | 1B | 3B |",
            [Reading("Alpha", 3_000_000_000, "parameters")],
        ),
        (
            "| Model | Active Parameters |\n|---|---|\n| Alpha | 3B |\n| Alpha-Lite | 1B |",
            [Reading("Alpha", 3_000_000_000, "parameters")],
        ),
        ("| Model | Active Parameters |\n|---|---|\n| [Alpha](https://hf.co/lab/Alpha) | 3B |", []),
    ],
)
def test_round5_probe_table_bindings(table, expected):
    assert (
        ModelCardParamsExtractor().extract(
            claim("model.parameters_active"),
            "# Alpha\n\n" + table,
            page_url=README_URL,
        )
        == expected
    )


@pytest.mark.parametrize(
    "card,outcome,reason",
    [
        (
            "Alpha has 3B active parameters.\n\n| Model | Active Parameters |\n"
            "|---|---|\n| Alpha | 3.0B |",
            "verified",
            None,
        ),
        (
            "Alpha has 3B active parameters.\n\nAlpha has 3.2B active parameters.",
            "skipped",
            "ambiguous_hf_reading",
        ),
    ],
)
def test_round5_probe_multiple_own_readings(tmp_path, card, outcome, reason):
    regions, refs = retained(tmp_path, [("readme", README_URL, "# Alpha\n" + card)])
    result = verify(
        claim("model.parameters_active", 3_000_000_000, refs),
        regions,
        deterministic_extractors(),
        today=date(2026, 10, 10),
    )
    assert (result.outcome, result.reason) == (outcome, reason)


@pytest.mark.parametrize("heading", ["Beta", "Alpha Lite", "Alpha-Base"])
def test_round5_standalone_count_requires_the_subject_heading(heading):
    assert (
        ModelCardParamsExtractor().extract(
            claim("model.parameters_active"),
            f"# {heading}\n3B active parameters out of 30B total",
            page_url=README_URL,
        )
        == []
    )


@pytest.mark.parametrize(
    "text",
    [
        "Alpha is fast, unlike Beta (22B active).",
        "Alpha beats models with 22B active parameters.",
        "Alpha is competitive compared with Beta's 22B active parameters.",
        "Alpha Lite has 1B active parameters.",
        "Alpha Lite is a MoE model with 1B active parameters.",
        "Alpha is a MoE model with 30B total parameters.",
        "Alpha is a model with 30B parameters.",
        "Alpha, unlike Beta, is a MoE model with 22B active parameters.",
        "Unlike Beta, Alpha is a MoE model with 3B active parameters.",
        "Alpha is a MoE model with 3B active parameters compared with Beta.",
        "Alpha is a MoE model with 3B active parameters out of 30B total compared with Beta.",
        "Beta has 22B active parameters out of 200B total.",
        "22B active parameters out of 200B total, unlike Alpha.",
        "22B active parameters out of 200B total, as in Beta.",
        "- 22B active parameters out of 200B total, the Beta configuration.",
        (
            "Alpha is a MoE model with 3B active parameters unlike Beta "
            "which has 22B active parameters."
        ),
        "Alpha is a MoE model with 22B active parameters of Beta.",
        "Alpha is a model with 30B total parameters with 3B activated per token.",
        "Alpha is a MoE model with 3B activated experts.",
        "Alpha is a MoE model with 30B total parameters with 3B activated experts.",
        "Alpha is a MoE model with 3B activated.",
        "Alpha is a model with 3B activated layers.",
        "Alpha is a model with 3B activated tokens per step.",
        "Alpha uses 3B activated parameters and Beta uses 22B activated parameters.",
        "Alpha is a MoE model with up to 3B active parameters.",
        "Alpha is a MoE model with 3B active parameters out of 30B total parameters.",
        "Alpha is a MoE model with 30B total parameters with 3B activated, Beta has 9B activated.",
        "It has 3B active parameters out of 30B total.",
        "Beta is a MoE model with 22B active parameters.",
        "Alpha is a MoE model with 22B active parameters, unlike Beta.",
        "Compared with Beta, Alpha is a MoE model with 3B active parameters.",
        "Alpha is a MoE model with 30B total parameters with 22B activated in Beta.",
        "Alpha is a MoE model with 30B total parameters with 3B activated compared with Beta.",
        "Alpha is a MoE model with 3B active parameters, like other models.",
        "Alpha is a MoE model with 3B active parameters versus 9B active parameters.",
        "Alpha is a MoE model with 3B active parameters (unlike Beta).",
        "Alpha is a MoE model with 3B active parameters while Beta uses 22B active parameters.",
        "Alpha is a MoE model with 3B active parameters; Beta uses 22B active parameters.",
        "Alpha is a MoE model with 3B active parameters,\nunlike Beta.",
        "Unlike Beta,\nAlpha is a MoE model with 3B active parameters.",
        "Alpha is a MoE model with 30B total parameters with 3B activated,\nBeta has 9B activated.",
        "Alpha is a MoE model with 30B total parameters with 3B activated.layers.",
        "Alpha has 3B effective layers.",
        "Alpha has 3B effective tokens per step.",
        "Alpha has 3B effective experts.",
        "Alpha has 3B effective.",
        "Alpha has 3B activated.",
    ],
)
def test_round6_false_active_prose_reads_nothing(text):
    assert ModelCardParamsExtractor().extract(
        claim("model.parameters_active"), "# Alpha\n" + text, page_url=README_URL
    ) == []


@pytest.mark.parametrize("heading", ["Alpha", "Beta", "Comparison", ""])
@pytest.mark.parametrize(
    "text",
    ["3B active parameters out of 30B total.", "Alpha has 3B active parameters out of 30B total."],
)
def test_round6_out_of_total_stays_unreadable(heading, text):
    assert ModelCardParamsExtractor().extract(
        claim("model.parameters_active"), f"# {heading}\n{text}", page_url=README_URL
    ) == []


@pytest.mark.parametrize(
    "text,amount",
    [
        ("Alpha is a MoE model with 3B active parameters.", 3_000_000_000),
        ("Alpha is a model with 30B effective parameters.", 30_000_000_000),
        ("Alpha is a MoE model with 30B total parameters with 3B activated.", 3_000_000_000),
        (
            "Alpha is a language model with 671B total parameters with 37B activated.",
            37_000_000_000,
        ),
        ("Alpha has 3B activated params.", 3_000_000_000),
        ("Alpha has 3B effective params.", 3_000_000_000),
        ("Alpha is a MoE model with 3B active parameters. Beta has 22B active parameters.",
         3_000_000_000),
    ],
)
def test_round6_parameter_prose_with_safe_binding(text, amount):
    assert ModelCardParamsExtractor().extract(
        claim("model.parameters_active"), "# Alpha\n" + text, page_url=README_URL
    ) == [Reading("Alpha", amount, "parameters")]


@pytest.mark.parametrize("word", ["activated", "effective"])
@pytest.mark.parametrize("label", ["Parameters", "Active Parameters", "Total Parameters"])
@pytest.mark.parametrize("orientation", ["row", "column"])
def test_round6_bare_active_table_value_needs_a_parameter_label(word, label, orientation):
    if orientation == "row":
        card = f"| Property | Alpha | Beta |\n| {label} | 3B {word} | 22B {word} |"
    else:
        card = f"| Model | {label} |\n| Alpha | 3B {word} |\n| Beta | 22B {word} |"
    assert ModelCardParamsExtractor().extract(
        claim("model.parameters_active"), "# Alpha\n" + card, page_url=README_URL
    ) == [Reading("Alpha", 3_000_000_000, "parameters")]


@pytest.mark.parametrize("word", ["activated", "effective"])
@pytest.mark.parametrize("label", ["Layers", "Tokens per step", "Experts"])
def test_round6_bare_active_table_value_rejects_nonparameter_labels(word, label):
    card = f"| Property | Alpha | Beta |\n| {label} | 3B {word} | 22B {word} |"
    assert ModelCardParamsExtractor().extract(
        claim("model.parameters_active"), "# Alpha\n" + card, page_url=README_URL
    ) == []


@pytest.mark.parametrize("name,amount", [("gemma-4-e2b-it", 2_300_000_000),
                                        ("gemma-4-e4b-it", 4_500_000_000)])
def test_round6_retained_gemma_readme_effective_counts(name, amount):
    card = (Path(__file__).parent / "fixtures/hf-gemma-4/README.md").read_text()
    c = replace(claim("model.parameters_active"), names=(name, "google/" + name))
    assert ModelCardParamsExtractor().extract(
        c, card, page_url=f"https://huggingface.co/google/{name}/raw/main/README.md"
    ) == [Reading(name, amount, "parameters")]


@pytest.mark.parametrize(
    "text",
    [
        "Alpha distils a 70B parameter model.",
        "Alpha is smaller than a 70B parameter model.",
        "Alpha was trained from a 70B parameter model.",
        "Alpha is a 6B parameter model like Beta.",
        "Alpha beats a 70B parameter model.",
        "Alpha is a 6B-parameter model, unlike Beta.",
        "Alpha is a 6B parameter language model compared with Beta.",
    ],
)
def test_round6_foreign_total_prose_reads_nothing(text):
    assert ModelCardParamsExtractor()._scan(
        claim("model.parameters_active"), "# Alpha\n" + text, (), total_only=True
    )[0] == []


@pytest.mark.parametrize(
    "text,amount",
    [
        ("Alpha is a 6B parameter model.", "6B"),
        ("Alpha is a 6B parameter model trained on 2T tokens.", "6B"),
        ("Alpha is a 6B-parameter model.", "6B"),
        ("Alpha is a 6 billion parameter model.", "6 billion"),
        ("Alpha is a 6B parameter language model.", "6B"),
        ("Alpha is a 6B parameter model, trained on 2T tokens.", "6B"),
        ("Alpha is a 6B parameter model.  Beta is a 70B parameter model.", "6B"),
        ("Alpha has 6B parameters.", "6B"),
    ],
)
def test_round6_total_parameter_prose(text, amount):
    assert ModelCardParamsExtractor()._scan(
        claim("model.parameters_active"), "# Alpha\n" + text, (), total_only=True
    )[0] == [Reading("Alpha", amount, "parameters")]


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"model_type": "cobra", "ssm_cfg": {},
          "vision_config": {"num_attention_heads": 16}}, "SSM"),
        ({"model_type": "cobra", "ssm_cfg": {},
          "vision_config": {"layer_types": ["attention"]}}, "SSM"),
        ({"model_type": "mamba", "visual": {"num_attention_heads": 16}}, "SSM"),
        ({"model_type": "mamba", "audio_config": {"num_attention_heads": 16}}, "SSM"),
        ({"model_type": "mamba", "decoder": {"num_attention_heads": 16}},
         "hybrid-SSM-transformer"),
        ({"model_type": "wrapper", "text_config": {"model_type": "mamba"},
          "vision_config": {"num_attention_heads": 16}}, "SSM"),
        ({"model_type": "wrapper", "text_config": {"model_type": "mamba",
          "vision_config": {"num_attention_heads": 16}}}, "SSM"),
        ({"model_type": "zamba", "layers_block_type": ["mamba", "hybrid"]}, "SSM"),
        ({"model_type": "custom", "layers_block_type": ["hybrid"]}, None),
        ({"model_type": "mamba", "layers_block_type": ["mamba", "hybrid_attention"]},
         "hybrid-SSM-transformer"),
        ({"model_type": "mamba", "layer_types": ["mamba", "hybrid-attention"]},
         "hybrid-SSM-transformer"),
    ],
)
def test_round6_attention_evidence_belongs_to_the_text_backbone(config, expected):
    assert hf_config_architecture(config) == expected
