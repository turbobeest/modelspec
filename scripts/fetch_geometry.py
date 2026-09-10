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
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import httpx  # noqa: E402
import yaml  # noqa: E402

from schema.card import ModelCard  # noqa: E402

CONFIG_URL = "https://huggingface.co/{repo_id}/resolve/main/config.json"

#: Nested objects that hold the language-model fields on multimodal cards.
#: vision_config is deliberately not consulted — its hidden_size is the
#: vision tower, not the model the architecture block describes.
NEST_KEYS = ("text_config", "llm_config")

#: Card field -> config.json keys, in preference order. Only ints that are
#: actually present are written. `num_experts` is included because Qwen-MoE
#: names the field that, Mixtral uses num_local_experts, DeepSeek uses
#: n_routed_experts.
FIELD_MAP: dict[str, tuple[str, ...]] = {
    "num_layers": ("num_hidden_layers",),
    "num_attention_heads": ("num_attention_heads",),
    "num_kv_heads": ("num_key_value_heads",),
    "hidden_size": ("hidden_size",),
    "intermediate_size": ("intermediate_size",),
    "vocab_size": ("vocab_size",),
    "num_experts": ("num_local_experts", "n_routed_experts", "num_experts"),
    "experts_per_token": ("num_experts_per_tok",),
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
GATED_ACT = {"silu", "swish", "gelu_pytorch_tanh"}

#: Presence of any of these means the stack is not a uniform transformer-MoE
#: and the Mixtral-style active-parameter formula would be a fabrication.
NON_UNIFORM_KEYS = (
    "qk_nope_head_dim",
    "q_lora_rank",
    "kv_lora_rank",
    "mamba_d_state",
    "mamba_expand",
    "expert_layer_period",
    "attn_layer_period",
    "attn_layer_offset",
)


def _as_int(value: object) -> int | None:
    """JSON bool is a subclass of int — reject it. Accept only real ints."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


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
    fetched: dict[str, int] = {}
    for field, keys in FIELD_MAP.items():
        value = _as_int(lookup(config, *keys))
        if value is not None:
            fetched[field] = value

    if "num_experts" in fetched:
        explicit = _as_int(lookup(config, *EXPLICIT_ACTIVE_KEYS))
        if explicit is not None:
            fetched["active_parameters"] = explicit
        else:
            active = _active_parameters_from_config(config, fetched)
            if active is not None:
                fetched["active_parameters"] = active
    return fetched


def _active_parameters_from_config(
    config: dict[str, Any], fetched: dict[str, int]
) -> int | None:
    """Exact active params for a uniform gated-MLP transformer-MoE, else None.

    The config has to *state* every term. Hybrid stacks (Jamba, Mamba), MLA
    (DeepSeek), sparse layer schedules and missing tie_word_embeddings are
    left null rather than approximated from total × k/N.
    """
    if any(lookup(config, key) is not None for key in NON_UNIFORM_KEYS):
        return None

    mlp_only = lookup(config, "mlp_only_layers")
    if mlp_only not in (None, [], ()):
        return None
    first_dense = lookup(config, "first_k_dense_replace")
    if first_dense not in (None, 0):
        return None
    sparse_step = lookup(config, "decoder_sparse_step")
    if sparse_step not in (None, 1):
        return None
    moe_freq = lookup(config, "moe_layer_freq")
    if moe_freq not in (None, 1):
        return None
    nextn = lookup(config, "num_nextn_predict_layers")
    if nextn not in (None, 0):
        return None

    hidden = fetched.get("hidden_size")
    n_layers = fetched.get("num_layers")
    n_heads = fetched.get("num_attention_heads")
    n_kv = fetched.get("num_kv_heads")
    vocab = fetched.get("vocab_size")
    n_experts = fetched.get("num_experts")
    k_active = fetched.get("experts_per_token")
    if None in (hidden, n_layers, n_heads, n_kv, vocab, n_experts, k_active):
        return None
    assert hidden is not None and n_layers is not None and n_heads is not None
    assert n_kv is not None and vocab is not None
    assert n_experts is not None and k_active is not None
    if n_heads <= 0 or n_experts <= 0 or k_active <= 0 or k_active > n_experts:
        return None

    tied = lookup(config, "tie_word_embeddings")
    if not isinstance(tied, bool):
        return None
    act = lookup(config, "hidden_act")
    if act not in GATED_ACT:
        return None

    head_dim = _as_int(lookup(config, "head_dim"))
    if head_dim is None:
        if hidden % n_heads != 0:
            return None
        head_dim = hidden // n_heads
    if head_dim <= 0:
        return None

    expert_width = _as_int(lookup(config, "moe_intermediate_size"))
    if expert_width is None:
        expert_width = fetched.get("intermediate_size")
    if expert_width is None or expert_width <= 0:
        return None

    n_shared = _as_int(lookup(config, "n_shared_experts", "num_shared_experts"))
    shared_width = _as_int(lookup(config, "shared_expert_intermediate_size"))
    if n_shared is not None and n_shared > 0:
        if shared_width is None:
            return None
        shared_ffn = n_shared * 3 * hidden * shared_width
    elif shared_width is not None:
        shared_ffn = 3 * hidden * shared_width
    else:
        shared_ffn = 0

    q = hidden * (n_heads * head_dim)
    k_proj = hidden * (n_kv * head_dim)
    v_proj = hidden * (n_kv * head_dim)
    o_proj = (n_heads * head_dim) * hidden
    attn = q + k_proj + v_proj + o_proj
    expert = 3 * hidden * expert_width
    router = hidden * n_experts
    layer = attn + k_active * expert + router + shared_ffn
    embed = vocab * hidden
    lm_head = 0 if tied else embed
    return embed + lm_head + n_layers * layer


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


def fetch_config(
    client: httpx.Client, repo_id: str
) -> tuple[str, dict[str, Any] | None, str]:
    """GET config.json. Returns (status, payload, detail).

    status is one of: ok, not_found, gated, error. Never raises for 401/404.
    """
    url = CONFIG_URL.format(repo_id=repo_id)
    for attempt in range(8):
        try:
            response = client.get(url)
        except httpx.HTTPError as exc:
            if attempt == 7:
                return "error", None, f"network: {exc.__class__.__name__}"
            time.sleep(min(2 ** attempt, 30))
            continue

        if response.status_code == 429:
            wait = _rate_limit_wait(response)
            print(f"  Hugging Face rate-limited, waiting {wait:.0f}s")
            time.sleep(wait)
            continue
        if response.status_code == 404:
            return "not_found", None, "404"
        if response.status_code in (401, 403):
            return "gated", None, str(response.status_code)

        if response.status_code != 200:
            if attempt == 7:
                return "error", None, f"http {response.status_code}"
            time.sleep(min(2 ** attempt, 30))
            continue

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

    return "error", None, "retries exhausted"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--limit", type=int, default=0, help="only the first N resolved cards"
    )
    parser.add_argument(
        "--report", default="benchmarks/_census/hf_geometry.json"
    )
    args = parser.parse_args()

    targets: list[tuple[Path, ModelCard, str]] = []
    for path in _card_paths():
        try:
            card = ModelCard.from_yaml_file(path)
        except Exception as exc:
            print(f"  SKIP unreadable {path.relative_to(PROJECT_ROOT)}: {exc}")
            continue
        repo_id = repo_id_of(card)
        if not repo_id:
            continue
        targets.append((path, card, repo_id))
        if args.limit and len(targets) >= args.limit:
            break

    cards_report: dict[str, dict[str, Any]] = {}
    not_found: list[str] = []
    gated: list[str] = []
    errors: list[dict[str, str]] = []
    conflict_cards: list[str] = []
    would_gain = 0
    moe_with_experts = 0
    written = 0

    with httpx.Client(
        timeout=30, follow_redirects=True, headers=_hf_headers()
    ) as client:
        for index, (path, card, repo_id) in enumerate(targets, 1):
            model_id = card.identity.model_id
            status, payload, detail = fetch_config(client, repo_id)
            entry: dict[str, Any] = {
                "repo_id": repo_id,
                "status": status,
                "detail": detail,
                "gained": {},
                "already": [],
                "conflicts": [],
                "moe": False,
            }

            if status == "not_found":
                not_found.append(model_id)
            elif status == "gated":
                gated.append(model_id)
            elif status != "ok" or payload is None:
                errors.append({"model_id": model_id, "detail": detail})
            else:
                fetched = geometry_from_config(payload)
                existing = existing_architecture(card)
                gained, conflicts, already = apply_geometry(existing, fetched)
                moe = "num_experts" in fetched
                entry.update(
                    {
                        "gained": gained,
                        "already": already,
                        "conflicts": conflicts,
                        "moe": moe,
                        "fetched_fields": sorted(fetched),
                    }
                )
                if moe:
                    moe_with_experts += 1
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
            time.sleep(0.12)

    report = {
        "dry_run": args.dry_run,
        "considered": len(targets),
        "would_gain_geometry": would_gain,
        "written": written,
        "moe_with_expert_counts": moe_with_experts,
        "not_found": not_found,
        "gated": gated,
        "errors": errors,
        "conflict_cards": conflict_cards,
        "not_found_count": len(not_found),
        "gated_count": len(gated),
        "error_count": len(errors),
        "conflict_count": len(conflict_cards),
        "cards": cards_report,
    }
    out = PROJECT_ROOT / args.report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")

    print(
        f"\nconsidered {len(targets)}  would gain geometry {would_gain}  "
        f"MoE with experts {moe_with_experts}"
    )
    print(
        f"404={len(not_found)}  gated={len(gated)}  "
        f"errors={len(errors)}  conflicts={len(conflict_cards)}"
        + ("" if args.dry_run else f"  written={written}")
    )
    print(f"report: {out.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
