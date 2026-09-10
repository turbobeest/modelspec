#!/usr/bin/env python3
"""Fill architecture geometry from each resolved Hugging Face config.json.

Layer counts, head counts, hidden sizes and expert routing live in the repo's
config.json — not in the Hub search result that attached the repo. Fetching
them is the step that turns a resolved address into structured architecture.
The same fetch closes both the geometry ticket and the MoE-routing ticket.

A number that is not in the config is left null. Guessing a layer count from
the model name, or an active-parameter figure from total × k/N, would arrive
as a correctly-typed, confident value that nothing downstream would question.
That is worse than the empty field it replaces.

    python scripts/fetch_geometry.py --dry-run --limit 40
    python scripts/fetch_geometry.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import httpx  # noqa: E402
import yaml  # noqa: E402

from schema.card import ModelCard  # noqa: E402

CONFIG_URL = "https://huggingface.co/{repo_id}/resolve/main/config.json"
README_URL = "https://huggingface.co/{repo_id}/raw/main/README.md"

#: Nested objects that hold the language-model fields on multimodal cards.
#: vision_config is deliberately not consulted — its hidden_size is the
#: vision tower, not the model the architecture block describes.
NEST_KEYS = ("text_config", "llm_config", "language_config")

#: Card field -> config.json keys, in preference order. Only ints that are
#: actually present are written. `num_experts` is included because Qwen-MoE
#: names the field that, Mixtral uses num_local_experts, DeepSeek uses
#: n_routed_experts.
#:
#: `num_kv_heads` aliases include ChatGLM's `multi_query_group_num`. That
#: key is GQA/MQA, not MHA — treating its absence-of-`num_key_value_heads`
#: as MHA overstates GLM-4-9B's cache sixteenfold.
FIELD_MAP: dict[str, tuple[str, ...]] = {
    "num_layers": ("num_hidden_layers", "n_layer"),
    "num_attention_heads": (
        "num_attention_heads",
        "n_head",
        "n_heads",
        "encoder_attention_heads",
    ),
    "num_kv_heads": (
        "num_key_value_heads",
        "num_kv_heads",
        "multi_query_group_num",
        "n_head_kv",
        "n_kv_heads",
    ),
    "hidden_size": ("hidden_size", "n_embd", "d_model"),
    "intermediate_size": ("intermediate_size", "n_inner"),
    "vocab_size": ("vocab_size",),
    "num_experts": ("num_local_experts", "n_routed_experts", "num_experts"),
    "experts_per_token": ("num_experts_per_tok", "moe_topk", "moe_top_k"),
}

#: Direct names some configs use instead of a computable breakdown.
EXPLICIT_ACTIVE_KEYS = (
    "active_parameters",
    "num_active_parameters",
    "n_active_params",
    "activated_parameters",
)

#: Gated-MLP activations. Anything else (or missing) means we do not know
#: how many FFN matrices there are, so active_parameters stays null.
GATED_ACT = {"silu", "swish", "gelu_pytorch_tanh", "swigluoai"}

#: Presence of any of these means the stack is not a uniform transformer-MoE
#: and the Mixtral-style active-parameter formula would be a fabrication.
NON_UNIFORM_KEYS = (
    "qk_nope_head_dim",
    "q_lora_rank",
    "kv_lora_rank",
    "mamba_d_state",
    "mamba_expand",
    "mamba_d_conv",
    "mamba_head_dim",
    "expert_layer_period",
    "attn_layer_period",
    "attn_layer_offset",
    "hybrid_override_pattern",
)

#: Attention-only layer_types do not change the parameter count. Anything
#: else (conv, mamba) is a hybrid stack we will not invent a figure for.
ATTENTION_LAYER_TYPES = {"full_attention", "sliding_attention", "attention"}

KV_HEAD_KEYS = FIELD_MAP["num_kv_heads"]


@dataclass
class GeometryExtraction:
    """Mapped architecture ints plus how each one was obtained."""

    fields: dict[str, int] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    refusal: str | None = None


def _as_int(value: object) -> int | None:
    """JSON bool is a subclass of int — reject it. Accept only real ints."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _as_uniform_int(value: object) -> int | None:
    """A scalar int, or a list of identical ints (Hunyuan per-layer widths)."""
    direct = _as_int(value)
    if direct is not None:
        return direct
    if isinstance(value, list) and value:
        ints = [_as_int(item) for item in value]
        if all(item is not None for item in ints) and len(set(ints)) == 1:
            return ints[0]
    return None


def _sources(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Nested language-model configs first, then the top-level object."""
    sources: list[dict[str, Any]] = []
    for key in NEST_KEYS:
        nested = config.get(key)
        if isinstance(nested, dict):
            sources.append(nested)
    sources.append(config)
    return sources


def lookup(config: dict[str, Any], *keys: str) -> Any:
    """Return the first non-null value among keys, nested then top-level."""
    for src in _sources(config):
        for key in keys:
            if key in src and src[key] is not None:
                return src[key]
    return None


def geometry_from_config(config: dict[str, Any]) -> dict[str, int]:
    """Map config.json onto architecture fields. Missing keys are omitted."""
    return extract_geometry(config).fields


def extract_geometry(config: dict[str, Any]) -> GeometryExtraction:
    """Map config.json onto architecture fields, recording how each was obtained.

    `num_kv_heads` is copied from a real KV key when one exists. When the
    config is present and every KV key is absent, Hugging Face (and the
    architecture) treat the model as MHA, so kv heads equal attention heads.
    That equality is not applied when the config could not be fetched — this
    function is only called on a real config object.
    """
    out = GeometryExtraction()
    for field_name, keys in FIELD_MAP.items():
        raw = lookup(config, *keys)
        value = _as_uniform_int(raw) if field_name in {
            "experts_per_token", "intermediate_size"
        } else _as_int(raw)
        if value is None:
            continue
        if field_name == "num_experts" and value <= 0:
            continue
        if field_name == "experts_per_token" and value <= 0:
            continue
        out.fields[field_name] = value
        hit = _which_key(config, *keys)
        out.sources[field_name] = hit or keys[0]

    if "num_kv_heads" not in out.fields and "num_attention_heads" in out.fields:
        if not _config_has_any_key(config, *KV_HEAD_KEYS):
            out.fields["num_kv_heads"] = out.fields["num_attention_heads"]
            out.sources["num_kv_heads"] = "mha_equals_num_attention_heads"

    if out.fields.get("num_experts"):
        explicit = _as_int(lookup(config, *EXPLICIT_ACTIVE_KEYS))
        if explicit is not None and explicit > 0:
            out.fields["active_parameters"] = explicit
            out.sources["active_parameters"] = "config_explicit"
        else:
            active, reason = _active_parameters_from_config(config, out.fields)
            if active is not None:
                out.fields["active_parameters"] = active
                out.sources["active_parameters"] = reason
            else:
                out.refusal = reason
    return out


def _which_key(config: dict[str, Any], *keys: str) -> str | None:
    for src in _sources(config):
        for key in keys:
            if key in src and src[key] is not None:
                return key
    return None


def _config_has_any_key(config: dict[str, Any], *keys: str) -> bool:
    """True if the key exists and is not null — used to distinguish MHA."""
    for src in _sources(config):
        for key in keys:
            if key in src and src[key] is not None:
                return True
    return False


def _active_parameters_from_config(
    config: dict[str, Any], fetched: dict[str, int]
) -> tuple[int | None, str]:
    """Exact active params for a gated-MLP transformer-MoE, else (None, reason).

    The config has to *state* every term. Hybrid stacks (Jamba, Mamba), MLA
    (DeepSeek) and missing tie_word_embeddings are left null rather than
    approximated from total × k/N. A sparse schedule is accepted only when
    the config names which layers are dense (`first_k_dense_replace` or a
    0/1 `moe_layer_freq` list).
    """
    if any(lookup(config, key) is not None for key in NON_UNIFORM_KEYS):
        return None, "mla_or_hybrid"

    layer_types = lookup(config, "layer_types")
    if isinstance(layer_types, list) and layer_types:
        kinds = {str(item).lower() for item in layer_types}
        if kinds - ATTENTION_LAYER_TYPES:
            return None, "hybrid_layer_types"

    mlp_only = lookup(config, "mlp_only_layers")
    if mlp_only not in (None, [], ()):
        return None, "sparse_schedule_unknown"

    nextn = lookup(config, "num_nextn_predict_layers")
    if nextn not in (None, 0):
        return None, "nextn_predict_layers"

    hidden = fetched.get("hidden_size")
    n_layers = fetched.get("num_layers")
    n_heads = fetched.get("num_attention_heads")
    n_kv = fetched.get("num_kv_heads")
    vocab = fetched.get("vocab_size")
    n_experts = fetched.get("num_experts")
    k_active = fetched.get("experts_per_token")
    if None in (hidden, n_layers, n_heads, n_kv, vocab, n_experts, k_active):
        return None, "missing_geometry_term"
    assert hidden is not None and n_layers is not None and n_heads is not None
    assert n_kv is not None and vocab is not None
    assert n_experts is not None and k_active is not None
    if n_heads <= 0 or n_experts <= 0 or k_active <= 0 or k_active > n_experts:
        return None, "missing_geometry_term"

    tied = lookup(config, "tie_word_embeddings")
    if not isinstance(tied, bool):
        return None, "missing_tie_word_embeddings"
    act = lookup(config, "hidden_act", "hidden_activation", "mlp_hidden_act")
    if act not in GATED_ACT:
        return None, "unknown_activation"

    head_dim = _as_int(lookup(config, "head_dim"))
    if head_dim is None:
        if hidden % n_heads != 0:
            return None, "missing_geometry_term"
        head_dim = hidden // n_heads
    if head_dim <= 0:
        return None, "missing_geometry_term"

    expert_width = _as_uniform_int(lookup(config, "moe_intermediate_size"))
    if expert_width is None:
        expert_width = fetched.get("intermediate_size")
    if expert_width is None or expert_width <= 0:
        return None, "missing_geometry_term"

    n_shared = _as_int(lookup(config, "n_shared_experts", "num_shared_experts")) or 0
    shared_width = _as_int(
        lookup(
            config,
            "shared_expert_intermediate_size",
            "shared_intermediate_size",
            "moe_shared_expert_intermediate_size",
        )
    )
    if n_shared > 0:
        if shared_width is None:
            shared_width = expert_width
        shared_ffn = n_shared * 3 * hidden * shared_width
    elif shared_width is not None:
        shared_ffn = 3 * hidden * shared_width
    else:
        shared_ffn = 0

    moe_layers, dense_layers, schedule_reason = _moe_layer_counts(config, n_layers)
    if moe_layers is None or dense_layers is None:
        return None, schedule_reason or "sparse_schedule_unknown"

    dense_width = _as_int(
        lookup(config, "prefix_dense_intermediate_size")
    ) or fetched.get("intermediate_size")
    if dense_layers and (dense_width is None or dense_width <= 0):
        return None, "missing_geometry_term"

    q = hidden * (n_heads * head_dim)
    k_proj = hidden * (n_kv * head_dim)
    v_proj = hidden * (n_kv * head_dim)
    o_proj = (n_heads * head_dim) * hidden
    attn = q + k_proj + v_proj + o_proj
    expert = 3 * hidden * expert_width
    router = hidden * n_experts
    moe_layer = attn + k_active * expert + router + shared_ffn
    dense_ffn = 3 * hidden * dense_width if dense_layers else 0
    dense_layer = attn + dense_ffn
    embed = vocab * hidden
    lm_head = 0 if tied else embed
    total = embed + lm_head + moe_layers * moe_layer + dense_layers * dense_layer
    source = (
        "derived_uniform_gated_moe"
        if dense_layers == 0
        else "derived_sparse_gated_moe"
    )
    return total, source


def _moe_layer_counts(
    config: dict[str, Any], n_layers: int
) -> tuple[int | None, int | None, str | None]:
    """How many layers are MoE vs dense. None if the schedule is unnamed."""
    first_dense = lookup(config, "first_k_dense_replace")
    sparse_step = lookup(config, "decoder_sparse_step")
    moe_freq = lookup(config, "moe_layer_freq")

    if isinstance(moe_freq, list):
        flags = [_as_int(item) for item in moe_freq]
        if len(flags) != n_layers or any(f not in (0, 1) for f in flags):
            return None, None, "sparse_schedule_unknown"
        # MiniMax and DeepSeek lists use 1 = MoE, 0 = dense.
        moe_layers = sum(1 for f in flags if f == 1)
        return moe_layers, n_layers - moe_layers, None

    if moe_freq not in (None, 1):
        return None, None, "sparse_schedule_unknown"
    if sparse_step not in (None, 1):
        return None, None, "sparse_schedule_unknown"

    k_dense = _as_int(first_dense)
    if k_dense is None:
        k_dense = 0
    if k_dense < 0 or k_dense > n_layers:
        return None, None, "sparse_schedule_unknown"
    return n_layers - k_dense, k_dense, None


_UNIT = r"(?:billion|million|trillion|[bmt])s?"
_NUM = r"(\d+(?:\.\d+)?)"


def _params_from_num_unit(number: str, unit: str) -> int | None:
    try:
        amount = float(number)
    except ValueError:
        return None
    letter = unit.lower().rstrip("s")[:1]
    scale = {"t": 1_000_000_000_000, "b": 1_000_000_000, "m": 1_000_000}.get(letter)
    if scale is None or amount <= 0:
        return None
    return int(round(amount * scale))


def published_active_from_readme(
    text: str, repo_id: str = ""
) -> tuple[int, str] | None:
    """A figure the model card states, or None if absent or ambiguous.

    Comparison tables that list several models' activated counts are refused
    unless a more specific extractor (highlighted cell, two-column property
    table, a row named for this model, or unique prose) already decided.
    """
    if not text:
        return None
    slug = repo_id.rsplit("/", 1)[-1].strip()
    plain = re.sub(r"\*\*", "", text)

    for row in re.findall(r"<tr>(.*?)</tr>", plain, flags=re.I | re.S):
        if not re.search(r"activ(?:e|ated)\s+parameters", row, re.I):
            continue
        highlighted = re.findall(
            r"background-color:\s*#DAE8FF[^>]*>(.*?)</td>", row, flags=re.I | re.S
        )
        if len(highlighted) == 1:
            parsed = _parse_size_token(re.sub(r"<[^>]+>", "", highlighted[0]))
            if parsed:
                return parsed, "html_highlighted_active_cell"
        cells = [
            re.sub(r"<[^>]+>", "", cell).strip()
            for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.I | re.S)
        ]
        if len(cells) == 2 and re.search(r"activ(?:e|ated)\s+parameters", cells[0], re.I):
            parsed = _parse_size_token(cells[1])
            if parsed:
                return parsed, "html_two_cell_active"

    table_hits: list[int] = []
    for match in re.finditer(
        r"^\|\s*(?:#\s*)?(?:activated|active)\s+parameters"
        r"(?:\s+during\s+inference)?\s*\|\s*"
        r"~?" + _NUM + r"\s*(" + _UNIT + r")\s*\|?\s*$",
        plain,
        flags=re.I | re.M,
    ):
        parsed = _params_from_num_unit(match.group(1), match.group(2))
        if parsed:
            table_hits.append(parsed)
    if len(set(table_hits)) == 1:
        return table_hits[0], "property_table"

    named = _active_from_named_markdown_row(plain, slug)
    if named:
        return named, "named_markdown_row"

    from_to = re.search(
        r"from\s+" + _NUM + r"\s*(" + _UNIT + r")\s+parameters?\s*"
        r"\(\s*" + _NUM + r"\s*(" + _UNIT + r")\s+active\s*\)\s+to\s+"
        + _NUM + r"\s*(" + _UNIT + r")\s+parameters?\s*"
        r"\(\s*" + _NUM + r"\s*(" + _UNIT + r")\s+active\s*\)",
        plain,
        flags=re.I,
    )
    if from_to:
        parsed = _params_from_num_unit(from_to.group(7), from_to.group(8))
        if parsed:
            return parsed, "prose_from_to_destination"

    bound = _active_bound_to_name(plain, slug)
    if bound:
        return bound, "prose_name_bound"

    votes: dict[int, str] = {}
    prose_patterns = (
        r"with\s+" + _NUM + r"\s*(" + _UNIT + r")\s+activated\s+for\s+each\s+token",
        r"of which\s+" + _NUM + r"\s*(" + _UNIT + r")\s+are\s+activated",
        r"(?:with\s+|and\s+|,\s*)~?" + _NUM + r"\s*(" + _UNIT + r")\s+"
        r"activ(?:e|ated)\s+parameters?",
        r"~?" + _NUM + r"\s*(" + _UNIT + r")\s+activ(?:e|ated)\s+"
        r"(?:parameters?|params?|per\s+token)",
        r"(\d+(?:\.\d+)?)\s+(billion|million)\s+activ(?:e|ated)\s+parameters?",
        r"total parameters and\s+" + _NUM + r"\s*(" + _UNIT + r")\s+"
        r"active parameters?",
        r"total;\s*" + _NUM + r"\s*(" + _UNIT + r")\s+active",
        r"only\s+" + _NUM + r"\s*(" + _UNIT + r")\s+activ(?:e|ated)\s+parameters?",
        r"with only\s+" + _NUM + r"\s*(" + _UNIT + r")\s+active\s+parameters?",
        r"parameters,\s+" + _NUM + r"\s*(" + _UNIT + r")\s+active",
        r"parameters \(" + _NUM + r"\s*(" + _UNIT + r")\s+activ(?:e|ated)\)",
        r"Active Parameters During Inference\s*:\s*" + _NUM
        + r"\s*(" + _UNIT + r")",
        r"\(\s*" + _NUM + r"\s*(" + _UNIT + r")\s*activ(?:e|ated)\s*\)",
    )
    for pattern in prose_patterns:
        for match in re.finditer(pattern, plain, flags=re.I):
            parsed = _params_from_num_unit(match.group(1), match.group(2))
            if parsed:
                votes[parsed] = "prose"
    if len(votes) == 1:
        value, why = next(iter(votes.items()))
        return value, why

    # `30B-A3B` is a published self-size. Never take it from another model's
    # name in a bake-off table (`Qwen3-235B-A22B` is not this card's figure).
    a_self = _self_a_token(plain, slug)
    if not votes and a_self:
        return a_self, "size_token_A"
    return None


def _base_models_from_readme(text: str) -> list[str]:
    """Hub card YAML `base_model:` — a quant of X publishes X's active count."""
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    try:
        front = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return []
    raw = front.get("base_model")
    if isinstance(raw, str) and "/" in raw:
        return [raw.strip()]
    if isinstance(raw, list):
        return [item.strip() for item in raw if isinstance(item, str) and "/" in item]
    return []


def _self_a_token(text: str, slug: str) -> int | None:
    """`30B-A3B` only when it names this model, not a neighbour in a table."""
    pattern = re.compile(
        r"(\d+(?:\.\d+)?)B-A" + _NUM + r"(" + _UNIT + r")\b", flags=re.I
    )
    slug_hit = pattern.search(slug)
    if slug_hit:
        return _params_from_num_unit(slug_hit.group(2), slug_hit.group(3))
    heading = re.search(r"^#\s+(.+)$", text, flags=re.M)
    if heading:
        hit = pattern.search(heading.group(1))
        if hit:
            return _params_from_num_unit(hit.group(2), hit.group(3))
    intro = re.search(
        r"is a\s+\d+(?:\.\d+)?B-A" + _NUM + r"(" + _UNIT + r")\b",
        text,
        flags=re.I,
    )
    if intro:
        return _params_from_num_unit(intro.group(1), intro.group(2))
    return None


def _parse_size_token(token: str) -> int | None:
    match = re.search(r"~?" + _NUM + r"\s*(" + _UNIT + r")\b", token, flags=re.I)
    if not match:
        return None
    return _params_from_num_unit(match.group(1), match.group(2))


_SLUG_SUFFIXES = (
    "-nvfp4",
    "-fp8",
    "-bf16",
    "-fp16",
    "-gguf",
    "-base",
    "-instruct",
    "-chat",
    "-it",
    "-exp",
)


def _slug_stems(slug: str) -> list[str]:
    """Repo name plus the same model without quant/date suffixes.

    `DeepSeek-V3-0324` is DeepSeek-V3; `Kimi-K2.5-NVFP4` is Kimi-K2.5.
    Date suffixes (`-0324`, `-0528`) and weight-format suffixes are stripped
    one at a time so a named table row for the base model still binds.
    """
    stems = [slug]
    current = slug
    changed = True
    while changed:
        changed = False
        lower = current.lower()
        for suffix in _SLUG_SUFFIXES:
            if lower.endswith(suffix) and len(current) > len(suffix) + 2:
                current = current[: -len(suffix)]
                stems.append(current)
                changed = True
                break
        dated = re.sub(r"-\d{4}$", "", current)
        if dated != current:
            current = dated
            stems.append(current)
            changed = True
    return stems


def _name_patterns(slug: str) -> list[str]:
    if not slug:
        return []
    variants: list[str] = []
    for stem in _slug_stems(slug):
        variants.extend((stem, stem.replace("-", " "), stem.replace("_", "-")))
    # Longest first so GLM-4.5-Air wins over GLM-4.5.
    return sorted({v for v in variants if v}, key=len, reverse=True)


def _active_from_named_markdown_row(text: str, slug: str) -> int | None:
    """Active params from a row that starts with this model's name.

    `355B-A32B` is total-A-active; the A figure is the one we want. A
    DeepSeek-style `| name | 671B | 37B |` row puts activated second.
    """
    if not slug:
        return None
    for name in _name_patterns(slug):
        row_re = re.compile(
            r"^\|\s*" + re.escape(name) + r"\s*\|(.*)$",
            flags=re.I | re.M,
        )
        for row in row_re.finditer(text):
            rest = row.group(1)
            a_token = re.search(
                r"\b\d+(?:\.\d+)?B-A" + _NUM + r"(" + _UNIT + r")\b",
                rest,
                flags=re.I,
            )
            if a_token:
                parsed = _params_from_num_unit(a_token.group(1), a_token.group(2))
                if parsed:
                    return parsed
            sizes = [
                _params_from_num_unit(num, unit)
                for num, unit in re.findall(
                    r"~?" + _NUM + r"\s*(" + _UNIT + r")\b", rest, flags=re.I
                )
            ]
            sizes = [value for value in sizes if value]
            if len(sizes) >= 2:
                return sizes[1]
    return None


def _active_bound_to_name(text: str, slug: str) -> int | None:
    """The active figure that sits nearest after this model's name."""
    if not slug:
        return None
    figure = (
        r"~?" + _NUM + r"\s*(" + _UNIT + r")\s+"
        r"activ(?:e|ated)(?:\s+parameters?|\s+params?|\s+for\s+each\s+token)?"
        r"|\(\s*" + _NUM + r"\s*(" + _UNIT + r")\s*activ(?:e|ated)\s*\)"
    )
    best: tuple[int, int] | None = None  # (distance, value)
    for name in _name_patterns(slug):
        name_re = re.compile(
            r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9.-])",
            flags=re.I,
        )
        for found in name_re.finditer(text):
            window = text[found.end(): found.end() + 220]
            hit = re.search(figure, window, flags=re.I)
            if not hit:
                continue
            if hit.group(1) is not None:
                parsed = _params_from_num_unit(hit.group(1), hit.group(2))
            else:
                parsed = _params_from_num_unit(hit.group(3), hit.group(4))
            if not parsed:
                continue
            distance = hit.start()
            if best is None or distance < best[0]:
                best = (distance, parsed)
    return None if best is None else best[1]


def apply_geometry(
    existing: dict[str, int | None], fetched: dict[str, int]
) -> tuple[dict[str, int], list[dict[str, int | str]], list[str]]:
    """Split fetched values into gained / conflicts / already-matching.

    A non-null existing value is never overwritten. A mismatch is a conflict
    and is reported; the card keeps what it had.
    """
    gained: dict[str, int] = {}
    conflicts: list[dict[str, int | str]] = []
    already: list[str] = []
    for field, value in fetched.items():
        current = existing.get(field)
        if current is None:
            gained[field] = value
        elif current == value:
            already.append(field)
        else:
            conflicts.append(
                {"field": field, "existing": current, "fetched": value}
            )
    return gained, conflicts, already


def existing_architecture(card: ModelCard) -> dict[str, int | None]:
    arch = card.architecture
    fields = (*FIELD_MAP.keys(), "active_parameters")
    return {name: getattr(arch, name) for name in fields}


def repo_id_of(card: ModelCard) -> str:
    raw = (card.availability.huggingface.model_id or "").strip()
    for prefix in ("https://huggingface.co/", "http://huggingface.co/"):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
    return raw.strip("/")


def _rate_limit_wait(response: httpx.Response) -> float:
    retry_after = response.headers.get("Retry-After") or response.headers.get(
        "retry-after"
    )
    if retry_after:
        try:
            return min(max(float(retry_after), 1.0), 180.0)
        except ValueError:
            pass
    ratelimit = (
        response.headers.get("RateLimit")
        or response.headers.get("ratelimit")
        or ""
    )
    match = re.search(r"[;,]t=(\d+)", ratelimit)
    if match:
        return min(int(match.group(1)) + 1, 180.0)
    return 20.0


def _is_gated_body(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "gated",
            "restricted",
            "must have access",
            "please log in",
            "authorize",
            "access to model",
        )
    )


def _get_with_retry(
    client: httpx.Client, url: str
) -> tuple[str, httpx.Response | None, str]:
    """GET a Hub URL. 429 is retried; it is never returned as not_found."""
    rate_limits = 0
    errors = 0
    while rate_limits < 20 and errors < 8:
        try:
            response = client.get(url)
        except httpx.HTTPError as exc:
            errors += 1
            if errors >= 8:
                return "error", None, f"network: {exc.__class__.__name__}"
            time.sleep(min(2 ** (errors - 1), 30))
            continue

        if response.status_code == 429:
            rate_limits += 1
            wait = _rate_limit_wait(response)
            print(f"  Hugging Face rate-limited, waiting {wait:.0f}s")
            time.sleep(wait)
            continue
        if response.status_code == 404:
            return "not_found", response, "404"
        if response.status_code in (401, 403):
            return "gated", response, str(response.status_code)
        if response.status_code != 200:
            errors += 1
            if errors >= 8:
                return "error", response, f"http {response.status_code}"
            time.sleep(min(2 ** (errors - 1), 30))
            continue
        return "ok", response, "ok"

    if rate_limits >= 20:
        return "error", None, "rate-limited retries exhausted"
    return "error", None, "retries exhausted"


def fetch_config(
    client: httpx.Client, repo_id: str
) -> tuple[str, dict[str, Any] | None, str]:
    """GET config.json. Returns (status, payload, detail).

    status is one of: ok, not_found, gated, error. Never raises for 401/404.
    A 429 is retried until the window opens; it is never an absent field.
    """
    url = CONFIG_URL.format(repo_id=repo_id)
    status, response, detail = _get_with_retry(client, url)
    if status != "ok" or response is None:
        return status, None, detail
    try:
        payload = response.json()
    except ValueError:
        text = response.text[:2000]
        if _is_gated_body(text):
            return "gated", None, "gated-body"
        return "error", None, "non-json config.json"
    if not isinstance(payload, dict):
        return "error", None, "config.json is not an object"
    return "ok", payload, "ok"


def fetch_readme(client: httpx.Client, repo_id: str) -> tuple[str, str]:
    """GET README.md. Returns (status, text). 404 is empty text, not an error."""
    url = README_URL.format(repo_id=repo_id)
    status, response, _detail = _get_with_retry(client, url)
    if status == "not_found":
        return "not_found", ""
    if status != "ok" or response is None:
        return status, ""
    return "ok", response.text


def _write_architecture(path: Path, gained: dict[str, int]) -> None:
    """Patch architecture fields in place, then refuse to leave a broken card."""
    original = path.read_text(encoding="utf-8")
    front_raw, body = original.split("---", 2)[1], original.split("---", 2)[2]
    front = yaml.safe_load(front_raw) or {}
    architecture = front.setdefault("architecture", {}) or {}
    architecture.update(gained)
    front["architecture"] = architecture
    path.write_text(
        "---\n"
        + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
        + "---"
        + body,
        encoding="utf-8",
    )
    try:
        ModelCard.from_yaml_file(path)
    except Exception:
        path.write_text(original, encoding="utf-8")
        raise


def _hf_headers() -> dict[str, str]:
    headers = {"User-Agent": "ModelSpec-Geometry/1.0"}
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _card_paths() -> list[Path]:
    return [
        p
        for p in sorted((PROJECT_ROOT / "models").rglob("*.md"))
        if p.name != "LICENSE.md"
    ]


def _needs_fetch(card: ModelCard) -> bool:
    arch = card.architecture
    kv_gap = arch.num_layers is not None and arch.num_kv_heads is None
    moe_gap = bool(arch.num_experts) and arch.active_parameters is None
    return kv_gap or moe_gap


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--limit", type=int, default=0, help="only the first N resolved cards"
    )
    parser.add_argument(
        "--report", default="benchmarks/_census/hf_geometry.json"
    )
    parser.add_argument(
        "--all-resolved",
        action="store_true",
        help="re-fetch every resolved card, not only kv/active gaps",
    )
    args = parser.parse_args()

    targets: list[tuple[Path, ModelCard, str]] = []
    skipped_complete = 0
    for path in _card_paths():
        try:
            card = ModelCard.from_yaml_file(path)
        except Exception as exc:
            print(f"  SKIP unreadable {path.relative_to(PROJECT_ROOT)}: {exc}")
            continue
        repo_id = repo_id_of(card)
        if not repo_id:
            continue
        if not args.all_resolved and not _needs_fetch(card):
            skipped_complete += 1
            continue
        targets.append((path, card, repo_id))
        if args.limit and len(targets) >= args.limit:
            break

    cards_report: dict[str, dict[str, Any]] = {}
    not_found: list[str] = []
    gated: list[str] = []
    errors: list[dict[str, str]] = []
    conflict_cards: list[str] = []
    refusals: list[dict[str, str]] = []
    would_gain = 0
    moe_with_experts = 0
    written = 0
    kv_mha = 0
    active_published = 0
    active_derived = 0

    with httpx.Client(
        timeout=30, follow_redirects=True, headers=_hf_headers()
    ) as client:
        for index, (path, card, repo_id) in enumerate(targets, 1):
            model_id = card.identity.model_id
            status, payload, detail = fetch_config(client, repo_id)
            time.sleep(0.65)
            entry: dict[str, Any] = {
                "repo_id": repo_id,
                "status": status,
                "detail": detail,
                "gained": {},
                "already": [],
                "conflicts": [],
                "sources": {},
                "moe": False,
                "refusal": None,
            }

            if status == "not_found":
                not_found.append(model_id)
                if card.architecture.num_experts:
                    refusals.append(
                        {"model_id": model_id, "reason": "config_not_found"}
                    )
            elif status == "gated":
                gated.append(model_id)
                if card.architecture.num_experts:
                    refusals.append(
                        {"model_id": model_id, "reason": "config_gated"}
                    )
            elif status != "ok" or payload is None:
                errors.append({"model_id": model_id, "detail": detail})
                if card.architecture.num_experts:
                    refusals.append(
                        {"model_id": model_id, "reason": f"config_error:{detail}"}
                    )
            else:
                extracted = extract_geometry(payload)
                fetched = dict(extracted.fields)
                sources = dict(extracted.sources)
                refusal = extracted.refusal
                moe = bool(fetched.get("num_experts"))
                existing = existing_architecture(card)

                if moe and existing.get("active_parameters") is None:
                    if "active_parameters" not in fetched or sources.get(
                        "active_parameters", ""
                    ).startswith("derived_"):
                        readme_status, readme = fetch_readme(client, repo_id)
                        time.sleep(0.65)
                        if readme_status == "ok" and readme:
                            published = published_active_from_readme(
                                readme, repo_id
                            )
                            if published is None:
                                for parent in _base_models_from_readme(readme)[:1]:
                                    pst, parent_text = fetch_readme(client, parent)
                                    time.sleep(0.65)
                                    if pst == "ok" and parent_text:
                                        published = published_active_from_readme(
                                            parent_text, parent
                                        )
                                        if published:
                                            value, why = published
                                            published = (
                                                value,
                                                f"base_model:{parent}:{why}",
                                            )
                                            break
                            if published:
                                value, why = published
                                fetched["active_parameters"] = value
                                sources["active_parameters"] = (
                                    f"model_card_published:{why}"
                                )
                                refusal = None
                        elif (
                            "active_parameters" not in fetched
                            and readme_status not in ("ok", "not_found")
                        ):
                            refusal = f"readme_{readme_status}"

                if moe and "active_parameters" not in fetched:
                    k_active = fetched.get("experts_per_token") or existing.get(
                        "experts_per_token"
                    )
                    n_exp = fetched.get("num_experts") or existing.get(
                        "num_experts"
                    )
                    total = card.architecture.total_parameters
                    if (
                        k_active
                        and n_exp
                        and k_active == n_exp
                        and total
                    ):
                        # k == N: every expert fires, so every parameter is
                        # active. This is identity, not total × k/N.
                        fetched["active_parameters"] = int(total)
                        sources["active_parameters"] = (
                            "all_experts_active_equals_total"
                        )
                        refusal = None
                    elif not refusal:
                        refusal = "no_published_figure_or_derivable_schedule"

                gained, conflicts, already = apply_geometry(existing, fetched)
                entry.update(
                    {
                        "gained": gained,
                        "already": already,
                        "conflicts": conflicts,
                        "moe": moe,
                        "fetched_fields": sorted(fetched),
                        "sources": {
                            k: sources[k] for k in gained if k in sources
                        },
                        "refusal": refusal,
                    }
                )
                if moe:
                    moe_with_experts += 1
                    if "active_parameters" not in gained and existing.get(
                        "active_parameters"
                    ) is None:
                        refusals.append(
                            {
                                "model_id": model_id,
                                "reason": refusal or "unresolved",
                            }
                        )
                if sources.get("num_kv_heads") == "mha_equals_num_attention_heads":
                    kv_mha += 1
                src_active = sources.get("active_parameters", "")
                if src_active.startswith("model_card_published"):
                    active_published += 1
                elif src_active.startswith("derived_"):
                    active_derived += 1
                if gained:
                    would_gain += 1
                if conflicts:
                    conflict_cards.append(model_id)
                if gained and not args.dry_run:
                    _write_architecture(path, gained)
                    written += 1

            cards_report[model_id] = entry
            if index % 25 == 0:
                print(
                    f"  {index}/{len(targets)}  "
                    f"gain={would_gain} moe={moe_with_experts} "
                    f"404={len(not_found)} gated={len(gated)}"
                )

    refusal_counts: dict[str, int] = {}
    for item in refusals:
        refusal_counts[item["reason"]] = refusal_counts.get(item["reason"], 0) + 1

    report = {
        "dry_run": args.dry_run,
        "considered": len(targets),
        "skipped_already_complete": skipped_complete,
        "would_gain_geometry": would_gain,
        "written": written,
        "moe_with_expert_counts": moe_with_experts,
        "kv_mha_fallback": kv_mha,
        "active_from_model_card": active_published,
        "active_from_derivation": active_derived,
        "not_found": not_found,
        "gated": gated,
        "errors": errors,
        "conflict_cards": conflict_cards,
        "refusals": refusals,
        "refusals_by_reason": refusal_counts,
        "not_found_count": len(not_found),
        "gated_count": len(gated),
        "error_count": len(errors),
        "conflict_count": len(conflict_cards),
        "refusal_count": len(refusals),
        "cards": cards_report,
    }
    out = PROJECT_ROOT / args.report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")

    print(
        f"\nconsidered {len(targets)}  skipped complete {skipped_complete}  "
        f"would gain {would_gain}  MoE with experts {moe_with_experts}"
    )
    print(
        f"kv MHA fallback={kv_mha}  active published={active_published}  "
        f"active derived={active_derived}"
    )
    print(
        f"404={len(not_found)}  gated={len(gated)}  "
        f"errors={len(errors)}  conflicts={len(conflict_cards)}  "
        f"refusals={len(refusals)}"
        + ("" if args.dry_run else f"  written={written}")
    )
    if refusal_counts:
        print("refusals by reason:")
        for reason, count in sorted(
            refusal_counts.items(), key=lambda kv: (-kv[1], kv[0])
        ):
            print(f"  {count:4d}  {reason}")
    print(f"report: {out.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
