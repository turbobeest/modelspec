#!/usr/bin/env python3
"""Build a Firecrawl work queue from what the cards actually lack.

The corpus is ~1,225 cards at ~13% complete. A dump of nulls is not a queue:
Firecrawl fetches pages, not fields, and a missing `co2_source` does not
unblock the same product path as a card with no benchmark scores.

This script reads every card, emits only fields that are empty on that card,
ranks the gaps by what they unblock, and groups the work by fetch URL.

    python scripts/build_manifest.py
    python scripts/build_manifest.py --output benchmarks/_census/fetch_manifest.json

Re-running is the progress measure: cards drop off a target once the field is
filled, and the per-tier counts shrink.

Geometry from Hugging Face `config.json` is owned by `scripts/fetch_geometry.py`.
Those URLs are referenced here so a Firecrawl run does not duplicate them.

Any scraped benchmark value that cannot be written as `schema.card.BenchmarkEvidence`
(source URL, ISO evidence date, source kind, date type) must not be written.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import ModelCard  # noqa: E402

DEFAULT_OUTPUT = PROJECT_ROOT / "benchmarks" / "_census" / "fetch_manifest.json"

#: A scraped score without these cannot be written. See schema/card.py
#: BenchmarkEvidence: source_url must be http(s), evidence_date and verified_at
#: must be YYYY-MM-DD, date_type is evaluated|published (never a crawl timestamp).
BENCHMARK_WRITE_RULE = (
    "Any scraped benchmark value MUST be written as schema.card.BenchmarkEvidence "
    "with source_url (http/https), source_kind (benchmark_author | "
    "independent_evaluator | provider_self_report), evidence_date (YYYY-MM-DD), "
    "date_type (evaluated | published), and verified_at (YYYY-MM-DD). "
    "Do not infer evidence_date from the retrieval timestamp. "
    "Do not write a bare number into benchmarks.scores without a matching "
    "evidence record — that reintroduces unverified-legacy scores."
)

# ─── What a gap unblocks ────────────────────────────────────────
#
# Weights are relative impact, not field counts. Justified against the
# live ranking and downselect paths, not against how often a field is empty.
#
# unrankable 100 — pipeline/ranking.py can only add a benchmark contribution
#   when a score exists (flat scores or evidence). docs/incomplete-evidence-ranking.md
#   is explicit: a model with no scores cannot be ordered on performance.
#   Highest because every other filter still leaves the catalogue unable to rank.
# price_filter 40 — web3d/downselect.v2.html drops a card when a cost cap is
#   set and `cost_input` is null (`!(c.cost_input !== null && c.cost_input <= N)`).
#   Silent exclusion, not a visible "unknown price".
# context_filter 30 — same file: `!(c.context_window >= N)` is false for null.
#   Same silent-exclusion shape; slightly below price because a context floor is
#   optional and a cost cap is the usual "don't bankrupt me" control.
# geometry 20 — pipeline/hardware.py cannot size the KV cache without
#   num_layers, hidden_size and num_kv_heads, so it uses a 25% working
#   allowance. FITS_ON is only computed for open-weights models.
# low 1 — extra fields a page would also yield. Not queued as their own crawl.

TIER_WEIGHT = {
    "unrankable": 100,
    "price_filter": 40,
    "context_filter": 30,
    "geometry": 20,
    "low": 1,
}

TIER_WHY = {
    "unrankable": (
        "No benchmark scores (flat or evidence). Ranking cannot order the model "
        "on performance; it is the blocker for any leaderboard or profile rank."
    ),
    "price_filter": (
        "cost.input is empty. web3d/downselect.v2.html silently drops the card "
        "when a max-cost filter is set."
    ),
    "context_filter": (
        "context_window is empty. web3d/downselect.v2.html silently drops the "
        "card when a min-context filter is set."
    ),
    "geometry": (
        "Open-weights card lacks num_layers, hidden_size or num_kv_heads. "
        "Hardware fit cannot size the KV cache and falls back to a flat working "
        "allowance. Fetched by scripts/fetch_geometry.py from config.json, "
        "not by Firecrawl."
    ),
    "low": (
        "Useful fields that do not unblock ranking, price filters, context "
        "filters or hardware fit. Ride along on pages already in the queue."
    ),
}

TEXT_TOKEN_TYPES = {
    "llm-chat", "llm-reasoning", "llm-code", "llm-base", "vlm", "agent-model",
}
CONTEXT_TYPES = TEXT_TOKEN_TYPES | {
    "embedding-text", "embedding-multimodal", "embedding-code", "reranker",
}
EMBED_TYPES = {
    "embedding-text", "embedding-multimodal", "embedding-code", "reranker",
}
IMAGE_TYPES = {"image-generation", "image-editing"}
VIDEO_TYPES = {"video-generation"}

# KV-cache geometry. hardware.py names these as the missing inputs.
GEOMETRY_REQUIRED = (
    "architecture.num_layers",
    "architecture.hidden_size",
    "architecture.num_kv_heads",
)
GEOMETRY_ALSO = (
    "architecture.num_attention_heads",
    "architecture.intermediate_size",
    "architecture.vocab_size",
    "architecture.rope_theta",
    "architecture.active_parameters",
    "architecture.num_experts",
    "architecture.experts_per_token",
    "architecture.type",
    "architecture.attention_type",
    "modalities.text.context_window",
)

HF_CONFIG_TEMPLATE = "https://huggingface.co/{huggingface_model_id}/raw/main/config.json"


# ─── Fetch catalogue: pages, not fields ─────────────────────────
#
# One provider pricing page answers cost (and often context) for a whole
# catalogue. Official docs over aggregators. URLs we cannot name are omitted
# rather than invented — those cards land in `unaddressed`.

PROVIDER_PRICING: dict[str, str] = {
    "openai": "https://developers.openai.com/api/docs/pricing",
    "anthropic": "https://docs.anthropic.com/en/docs/about-claude/pricing",
    "google": "https://ai.google.dev/gemini-api/docs/pricing",
    "xai": "https://docs.x.ai/docs/models",
    "mistral": "https://mistral.ai/pricing/api/",
    "deepseek": "https://api-docs.deepseek.com/quick_start/pricing",
    "cohere": "https://cohere.com/pricing",
    "moonshot": "https://platform.moonshot.ai/docs/pricing/chat",
    "zhipu": "https://docs.z.ai/guides/overview/pricing",
    "minimax": "https://platform.minimax.io/docs/pricing/overview",
    "voyage": "https://docs.voyageai.com/docs/pricing",
    "perplexity": "https://docs.perplexity.ai/getting-started/pricing",
    "together": "https://www.together.ai/pricing",
    "upstage": "https://console.upstage.ai/docs/pricing",
    "ai21": "https://www.ai21.com/pricing",
    "qwen": "https://www.alibabacloud.com/help/en/model-studio/models",
    "jina": "https://jina.ai/pricing",
    "ibm": "https://www.ibm.com/products/watsonx-ai/pricing",
    "nvidia": "https://build.nvidia.com/pricing",
    "microsoft": "https://azure.microsoft.com/pricing/details/azure-openai-service/",
    "stepfun": "https://platform.stepfun.com/docs/pricing",
    "cerebras": "https://inference.cerebras.ai/pricing",
    "liquid": "https://www.liquid.ai/pricing",
    "black-forest-labs": "https://bfl.ai/pricing",
    "stability": "https://platform.stability.ai/docs/getting-started/credits-and-pricing",
    "inception": "https://platform.inceptionlabs.ai/docs/pricing",
}

PROVIDER_DOCS: dict[str, str] = {
    "openai": "https://platform.openai.com/docs/models",
    "anthropic": "https://docs.anthropic.com/en/docs/about-claude/models/overview",
    "google": "https://ai.google.dev/gemini-api/docs/models",
    "xai": "https://docs.x.ai/docs/models",
    "mistral": "https://docs.mistral.ai/getting-started/models",
    "deepseek": "https://api-docs.deepseek.com/quick_start/pricing",
    "cohere": "https://docs.cohere.com/docs/models",
    "moonshot": "https://platform.moonshot.ai/docs/overview",
    "zhipu": "https://docs.z.ai/guides/overview/pricing",
    "minimax": "https://platform.minimax.io/docs/guides/models-intro",
    "voyage": "https://docs.voyageai.com/docs/embeddings",
    "perplexity": "https://docs.perplexity.ai/getting-started/models",
    "together": "https://docs.together.ai/docs/serverless-models",
    "upstage": "https://console.upstage.ai/docs/models",
    "ai21": "https://docs.ai21.com/docs/jamba-models",
    "qwen": "https://www.alibabacloud.com/help/en/model-studio/models",
    "jina": "https://jina.ai/models",
    "ibm": "https://www.ibm.com/granite",
    "nvidia": "https://build.nvidia.com/models",
    "microsoft": "https://learn.microsoft.com/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure",
    "meta": "https://www.llama.com/docs/overview/",
    "baai": "https://huggingface.co/BAAI",
    "nomic": "https://www.nomic.ai/blog",
    "intfloat": "https://huggingface.co/intfloat",
    "sentence-transformers": "https://sbert.net/",
    "snowflake": "https://www.snowflake.com/en/data-cloud/arctic/",
    "tencent": "https://hunyuan.tencent.com/",
    "tii": "https://falconllm.tii.ae/",
    "allen-ai": "https://allenai.org/olmo",
    "salesforce": "https://www.salesforce.com/blog/",
}

# Hosted-inference catalogues that list many open-weight models on one page.
# Used only when the card's provider has no first-party pricing URL.
MARKETPLACE_PRICING = (
    "https://www.together.ai/pricing",
    "https://fireworks.ai/pricing",
)

# Provider announcement / technical-report landings. Family-specific URLs
# override the provider default when both match.
PROVIDER_ANNOUNCEMENTS: dict[str, str] = {
    "openai": "https://openai.com/news/",
    "anthropic": "https://www.anthropic.com/news",
    "google": "https://blog.google/technology/google-deepmind/",
    "meta": "https://ai.meta.com/blog/",
    "mistral": "https://mistral.ai/news",
    "deepseek": "https://github.com/deepseek-ai",
    "xai": "https://x.ai/news",
    "qwen": "https://qwenlm.github.io/",
    "zhipu": "https://z.ai/blog",
    "ibm": "https://www.ibm.com/granite",
    "microsoft": "https://azure.microsoft.com/blog/tag/phi/",
    "nvidia": "https://developer.nvidia.com/blog/tag/nemotron/",
    "tii": "https://falconllm.tii.ae/",
    "allen-ai": "https://allenai.org/olmo",
    "01-ai": "https://github.com/01-ai",
    "cohere": "https://cohere.com/blog",
    "moonshot": "https://www.moonshot.ai/",
    "black-forest-labs": "https://bfl.ai/blog",
    "stability": "https://stability.ai/news",
    "baichuan": "https://www.baichuan-ai.com/",
    "liquid": "https://www.liquid.ai/blog",
    "ai21": "https://www.ai21.com/blog",
    "tencent": "https://hunyuan.tencent.com/",
    "openbmb": "https://www.openbmb.cn/",
    "rwkv": "https://wiki.rwkv.com/",
    "salesforce": "https://www.salesforce.com/blog/",
    "jina": "https://jina.ai/news/",
    "stepfun": "https://www.stepfun.com/",
    "minimax": "https://www.minimax.io/",
    "inception": "https://www.inceptionlabs.ai/",
    "upstage": "https://www.upstage.ai/blog",
    "perplexity": "https://www.perplexity.ai/hub/blog",
    "skywork": "https://www.skywork.ai/",
    "voyage": "https://blog.voyageai.com/",
    "nomic": "https://www.nomic.ai/blog",
    "intfloat": "https://huggingface.co/intfloat",
    "baai": "https://huggingface.co/BAAI",
    "sentence-transformers": "https://huggingface.co/sentence-transformers",
    "nous-research": "https://nousresearch.com/blog/",
    "together": "https://www.together.ai/blog",
    "cerebras": "https://www.cerebras.ai/blog",
    "moondream": "https://moondream.ai/blog",
    "teknium": "https://huggingface.co/teknium",
    "unsloth": "https://unsloth.ai/blog",
    "snowflake": "https://www.snowflake.com/en/blog/",
    "samsung": "https://research.samsung.com/",
}

FAMILY_ANNOUNCEMENTS: dict[tuple[str, str], str] = {
    ("google", "gemma"): "https://ai.google.dev/gemma",
    ("google", "gemini"): "https://deepmind.google/models/gemini/",
    ("google", "gemini-flash"): "https://deepmind.google/models/gemini/",
    ("google", "gemini-pro"): "https://deepmind.google/models/gemini/",
    ("google", "gemini-flash-lite"): "https://deepmind.google/models/gemini/",
    ("google", "veo"): "https://deepmind.google/models/veo/",
    ("qwen", "qwen"): "https://qwenlm.github.io/blog/qwen3/",
    ("meta", "llama"): "https://ai.meta.com/blog/llama-4-multimodal-intelligence/",
    ("microsoft", "phi"): "https://azure.microsoft.com/blog/tag/phi/",
    ("nvidia", "nemotron"): "https://developer.nvidia.com/blog/tag/nemotron/",
    ("allen-ai", "olmo"): "https://allenai.org/olmo",
    ("black-forest-labs", "flux"): "https://bfl.ai/announcements",
    ("tii", "falcon"): "https://falconllm.tii.ae/",
    ("ibm", "granite"): "https://www.ibm.com/granite",
    ("zhipu", "glm"): "https://z.ai/blog",
    ("deepseek", "deepseek"): "https://github.com/deepseek-ai/DeepSeek-V3",
    ("mistral", "mistral"): "https://mistral.ai/news",
    ("moonshot", "kimi"): "https://www.moonshot.ai/",
    ("01-ai", "yi"): "https://github.com/01-ai/Yi",
}

# Independent boards: one URL, many cards. source_kind = independent_evaluator.
LEADERBOARDS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "https://artificialanalysis.ai/leaderboards/models",
        "independent_leaderboard",
        tuple(sorted(TEXT_TOKEN_TYPES)),
    ),
    (
        "https://lmarena.ai/leaderboard",
        "independent_leaderboard",
        tuple(sorted(TEXT_TOKEN_TYPES)),
    ),
    (
        "https://huggingface.co/spaces/mteb/leaderboard",
        "independent_leaderboard",
        tuple(sorted(EMBED_TYPES)),
    ),
    (
        "https://artificialanalysis.ai/text-to-image",
        "independent_leaderboard",
        tuple(sorted(IMAGE_TYPES)),
    ),
)


# ─── Card inspection ────────────────────────────────────────────


def _type_name(card: ModelCard) -> str:
    mtype = card.identity.model_type
    return mtype.value if mtype else ""


def _all_types(card: ModelCard) -> set[str]:
    names = {_type_name(card)}
    names.update(s.value for s in card.identity.model_subtypes)
    names.discard("")
    return names


def _hf_id(card: ModelCard) -> str:
    return (card.availability.huggingface.model_id or "").strip()


def _has_scores(card: ModelCard) -> bool:
    if card.benchmarks.scores:
        return True
    if card.benchmarks.evidence:
        return True
    return False


def _missing_geometry(card: ModelCard) -> list[str]:
    arch = card.architecture
    missing = []
    if arch.num_layers is None:
        missing.append("architecture.num_layers")
    if arch.hidden_size is None:
        missing.append("architecture.hidden_size")
    if arch.num_kv_heads is None:
        missing.append("architecture.num_kv_heads")
    return missing


@dataclass(frozen=True)
class Gap:
    field: str
    tier: str


@dataclass
class CardRecord:
    path: str
    card: ModelCard
    model_id: str
    provider: str
    family: str
    types: set[str]
    open_weights: bool
    hf_id: str
    completeness: float
    gaps: list[Gap]

    @property
    def highest_tier(self) -> str | None:
        if not self.gaps:
            return None
        return min(self.gaps, key=lambda g: -TIER_WEIGHT[g.tier]).tier

    def missing_fields(self) -> set[str]:
        return {g.field for g in self.gaps}

    def fields_in(self, names: set[str] | tuple[str, ...]) -> set[str]:
        want = set(names)
        return {g.field for g in self.gaps if g.field in want}

    def tiers_for(self, names: set[str]) -> set[str]:
        return {g.tier for g in self.gaps if g.field in names}


def inspect(path: Path, card: ModelCard) -> CardRecord:
    """Return gaps that are empty on this card and that unblock a product path.

    Does not emit the rest of the 750-field null set. `co2_source` and friends
    stay off the queue until the four unblocking tiers are clear.
    """
    types = _all_types(card)
    gaps: list[Gap] = []

    if not _has_scores(card):
        gaps.append(Gap("benchmarks", "unrankable"))

    if card.cost.input is None:
        if types & EMBED_TYPES:
            if card.cost.embedding_per_million is None:
                gaps.append(Gap("cost.embedding_per_million", "price_filter"))
            # The live filter still reads cost.input, so the silent exclusion
            # is not fixed by filling only embedding_per_million.
            gaps.append(Gap("cost.input", "price_filter"))
        elif types & IMAGE_TYPES:
            if card.cost.output_image is None:
                gaps.append(Gap("cost.output_image", "price_filter"))
            gaps.append(Gap("cost.input", "price_filter"))
        elif types & VIDEO_TYPES:
            if card.cost.output_video_per_sec is None:
                gaps.append(Gap("cost.output_video_per_sec", "price_filter"))
            gaps.append(Gap("cost.input", "price_filter"))
        else:
            gaps.append(Gap("cost.input", "price_filter"))
            if card.cost.output is None:
                gaps.append(Gap("cost.output", "price_filter"))

    ctx = card.modalities.text.context_window
    if types & CONTEXT_TYPES:
        if ctx is None or ctx == 0:
            gaps.append(Gap("modalities.text.context_window", "context_filter"))
        if types & EMBED_TYPES and card.modalities.embeddings.max_input_tokens is None:
            gaps.append(Gap("modalities.embeddings.max_input_tokens", "context_filter"))

    if card.licensing.open_weights:
        for name in _missing_geometry(card):
            gaps.append(Gap(name, "geometry"))

    return CardRecord(
        path=str(path.relative_to(PROJECT_ROOT)),
        card=card,
        model_id=card.identity.model_id,
        provider=card.identity.provider,
        family=card.identity.family or "",
        types=types,
        open_weights=bool(card.licensing.open_weights),
        hf_id=_hf_id(card),
        completeness=float(card.card_completeness),
        gaps=gaps,
    )


# ─── Target assembly ────────────────────────────────────────────


@dataclass
class TargetAcc:
    url: str | None
    target_id: str
    kind: str
    fetcher: str
    firecrawl: bool
    note: str = ""
    url_template: str | None = None
    kinds: set[str] = field(default_factory=set)
    fills: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    def add(self, model_id: str, fields: set[str], kind: str | None = None) -> None:
        if kind:
            self.kinds.add(kind)
        if fields:
            self.fills[model_id].update(fields)


def _announcement_url(provider: str, family: str) -> str | None:
    return FAMILY_ANNOUNCEMENTS.get((provider, family)) or PROVIDER_ANNOUNCEMENTS.get(provider)


def assign_targets(records: list[CardRecord]) -> tuple[list[TargetAcc], list[dict[str, Any]]]:
    buckets: dict[str, TargetAcc] = {}
    unaddressed: list[dict[str, Any]] = []

    def bucket(
        key: str,
        *,
        url: str | None,
        kind: str,
        fetcher: str,
        firecrawl: bool,
        note: str = "",
        url_template: str | None = None,
    ) -> TargetAcc:
        acc = buckets.get(key)
        if acc is None:
            acc = TargetAcc(
                url=url,
                target_id=key,
                kind=kind,
                fetcher=fetcher,
                firecrawl=firecrawl,
                note=note,
                url_template=url_template,
                kinds={kind},
            )
            buckets[key] = acc
        else:
            acc.kinds.add(kind)
        return acc

    geom = bucket(
        "hf-config-geometry",
        url=None,
        kind="hf_config",
        fetcher="scripts/fetch_geometry.py",
        firecrawl=False,
        url_template=HF_CONFIG_TEMPLATE,
        note=(
            "Open-weight geometry is read from each card's "
            "availability.huggingface.model_id config.json. "
            "Already handled by scripts/fetch_geometry.py — do not Firecrawl "
            "these URLs and do not duplicate that script."
        ),
    )
    geom_blocked = bucket(
        "hf-config-geometry-unresolved",
        url=None,
        kind="hf_config_unresolved",
        fetcher="scripts/resolve_huggingface.py then scripts/fetch_geometry.py",
        firecrawl=False,
        note=(
            "Open-weight cards that still lack availability.huggingface.model_id. "
            "Geometry cannot be fetched until resolve_huggingface.py attaches a repo. "
            "Not a Firecrawl target."
        ),
    )

    for rec in records:
        missing = rec.missing_fields()
        leftover = set(missing)

        geom_fields = {f for f in missing if f.startswith("architecture.")}
        # Open-weight context and embedding length live in config.json
        # (max_position_embeddings). Do not Firecrawl those.
        if rec.open_weights and rec.hf_id:
            if "modalities.text.context_window" in missing:
                geom_fields.add("modalities.text.context_window")
            if "modalities.embeddings.max_input_tokens" in missing:
                geom_fields.add("modalities.embeddings.max_input_tokens")
        if rec.open_weights and geom_fields:
            dest = geom if rec.hf_id else geom_blocked
            dest.add(rec.model_id, geom_fields)
            leftover -= geom_fields

        price_fields = {
            f for f in leftover
            if f.startswith("cost.")
        }
        context_fields = {
            f for f in leftover
            if f in {
                "modalities.text.context_window",
                "modalities.embeddings.max_input_tokens",
            }
        }
        bench_fields = {f for f in leftover if f == "benchmarks"}

        if price_fields:
            pricing_url = PROVIDER_PRICING.get(rec.provider)
            if pricing_url:
                bucket(
                    pricing_url,
                    url=pricing_url,
                    kind="provider_pricing",
                    fetcher="firecrawl",
                    firecrawl=True,
                    note="Official provider pricing. One page covers the provider's catalogue.",
                ).add(rec.model_id, price_fields)
                leftover -= price_fields
            elif rec.open_weights:
                for url in MARKETPLACE_PRICING:
                    bucket(
                        url,
                        url=url,
                        kind="marketplace_pricing",
                        fetcher="firecrawl",
                        firecrawl=True,
                        note=(
                            "Hosted-inference pricing for open-weight models whose "
                            "publisher does not sell an API. Prefer this over inventing "
                            "a first-party price page."
                        ),
                    ).add(rec.model_id, price_fields)
                leftover -= price_fields

        if context_fields:
            docs_url = PROVIDER_DOCS.get(rec.provider) or PROVIDER_PRICING.get(rec.provider)
            if docs_url:
                bucket(
                    docs_url,
                    url=docs_url,
                    kind="provider_docs",
                    fetcher="firecrawl",
                    firecrawl=True,
                    note="Provider model docs: context window and related limits.",
                ).add(rec.model_id, context_fields)
                leftover -= context_fields

        if bench_fields:
            ann = _announcement_url(rec.provider, rec.family)
            if ann:
                bucket(
                    ann,
                    url=ann,
                    kind="provider_announcement",
                    fetcher="firecrawl",
                    firecrawl=True,
                    note=(
                        "Provider announcement / technical report. "
                        + BENCHMARK_WRITE_RULE
                    ),
                ).add(rec.model_id, bench_fields)
            for url, kind, allowed_types in LEADERBOARDS:
                if rec.types & set(allowed_types):
                    bucket(
                        url,
                        url=url,
                        kind=kind,
                        fetcher="firecrawl",
                        firecrawl=True,
                        note=(
                            "Independent evaluator board covering many models. "
                            "source_kind must be independent_evaluator. "
                            + BENCHMARK_WRITE_RULE
                        ),
                    ).add(rec.model_id, bench_fields)
            if ann or any(rec.types & set(t[2]) for t in LEADERBOARDS):
                leftover -= bench_fields

        if leftover:
            unaddressed.append({
                "model_id": rec.model_id,
                "fields": sorted(leftover),
                "reason": (
                    f"no fetch URL mapped for provider {rec.provider!r} "
                    f"family {rec.family!r}"
                ),
            })

    return list(buckets.values()), unaddressed


def _tier_for_field(field_name: str) -> str:
    if field_name == "benchmarks":
        return "unrankable"
    if field_name.startswith("cost."):
        return "price_filter"
    if "context_window" in field_name or field_name.endswith("max_input_tokens"):
        return "context_filter"
    if field_name.startswith("architecture."):
        return "geometry"
    return "low"


def serialize_target(acc: TargetAcc, rec_by_id: dict[str, CardRecord]) -> dict[str, Any]:
    cards_payload = []
    unblocks: dict[str, int] = defaultdict(int)
    weighted = 0
    expected: set[str] = set()
    for model_id, fields in sorted(acc.fills.items()):
        rec = rec_by_id.get(model_id)
        expected.update(fields)
        tiers = rec.tiers_for(fields) if rec else {_tier_for_field(f) for f in fields}
        for t in tiers:
            unblocks[t] += 1
        if tiers:
            weighted += max(TIER_WEIGHT[t] for t in tiers)
        cards_payload.append({
            "model_id": model_id,
            "fields": sorted(fields),
            "tiers": sorted(tiers, key=lambda t: -TIER_WEIGHT[t]),
        })

    expected_fields = set(expected)
    if acc.target_id == "hf-config-geometry":
        expected_fields.update(GEOMETRY_REQUIRED)
        expected_fields.update(GEOMETRY_ALSO)
    kinds = sorted(acc.kinds or {acc.kind})
    if len(kinds) == 1:
        display_kind = kinds[0]
    elif set(kinds) <= {"provider_pricing", "marketplace_pricing"}:
        display_kind = "provider_pricing" if "provider_pricing" in kinds else "marketplace_pricing"
    elif "independent_leaderboard" in kinds:
        display_kind = "independent_leaderboard"
    else:
        display_kind = "provider_page"
    out: dict[str, Any] = {
        "url": acc.url,
        "id": acc.target_id,
        "kind": display_kind,
        "kinds": kinds,
        "fetcher": acc.fetcher,
        "firecrawl": acc.firecrawl,
        "expected_fields": sorted(expected_fields),
        "cards_it_would_fill": [row["model_id"] for row in cards_payload],
        "fills": cards_payload,
        "cards_unblocked": len(cards_payload),
        "unblocks_by_tier": dict(
            sorted(unblocks.items(), key=lambda kv: -TIER_WEIGHT.get(kv[0], 0))
        ),
        "weighted_unblocks": weighted,
    }
    if acc.url_template:
        out["url_template"] = acc.url_template
    if acc.note:
        out["note"] = acc.note
    if "benchmarks" in expected:
        out["write_rule"] = BENCHMARK_WRITE_RULE
    return out


def load_cards() -> list[tuple[Path, ModelCard]]:
    models = PROJECT_ROOT / "models"
    out: list[tuple[Path, ModelCard]] = []
    for path in sorted(models.rglob("*.md")):
        if path.name == "LICENSE.md":
            continue
        out.append((path, ModelCard.from_yaml_file(path)))
    return out


def build(limit: int = 0) -> dict[str, Any]:
    loaded = load_cards()
    if limit:
        loaded = loaded[:limit]
    records = [inspect(path, card) for path, card in loaded]
    rec_by_id = {r.model_id: r for r in records}

    targets_acc, unaddressed = assign_targets(records)
    targets = [serialize_target(acc, rec_by_id) for acc in targets_acc]
    targets.sort(
        key=lambda t: (-t["cards_unblocked"], -t["weighted_unblocks"], t["id"]),
    )

    overlapping: dict[str, set[str]] = {t: set() for t in TIER_WEIGHT}
    exclusive: dict[str, int] = {t: 0 for t in TIER_WEIGHT}
    for rec in records:
        if not rec.gaps:
            continue
        seen = {g.tier for g in rec.gaps}
        for t in seen:
            overlapping[t].add(rec.model_id)
        exclusive[rec.highest_tier or "low"] += 1

    completeness = [r.completeness for r in records]
    mean_c = round(sum(completeness) / len(completeness), 2) if completeness else 0.0

    card_targets: dict[str, list[str]] = defaultdict(list)
    for t in targets:
        loc = t["url"] or t["id"]
        for model_id in t["cards_it_would_fill"]:
            card_targets[model_id].append(loc)

    cards_out = []
    for rec in records:
        if not rec.gaps:
            continue
        cards_out.append({
            "model_id": rec.model_id,
            "path": rec.path,
            "provider": rec.provider,
            "family": rec.family,
            "completeness": rec.completeness,
            "open_weights": rec.open_weights,
            "huggingface_model_id": rec.hf_id or None,
            "highest_tier": rec.highest_tier,
            "gaps": [
                {"field": g.field, "tier": g.tier} for g in rec.gaps
            ],
            "fetch_from": card_targets.get(rec.model_id, []),
        })

    firecrawl_targets = [t for t in targets if t["firecrawl"] and t["cards_unblocked"]]
    other_targets = [t for t in targets if not t["firecrawl"] and t["cards_unblocked"]]

    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "script": "scripts/build_manifest.py",
        "corpus": {
            "cards": len(records),
            "mean_completeness": mean_c,
            "min_completeness": min(completeness) if completeness else 0,
            "max_completeness": max(completeness) if completeness else 0,
            "open_weights": sum(1 for r in records if r.open_weights),
            "huggingface_model_id": sum(1 for r in records if r.hf_id),
        },
        "weighting": {
            name: {"weight": TIER_WEIGHT[name], "why": TIER_WHY[name]}
            for name in TIER_WEIGHT
        },
        "benchmark_write_rule": BENCHMARK_WRITE_RULE,
        "progress": {
            "cards_with_queued_gaps": sum(1 for r in records if r.gaps),
            "cards_clear_of_unblocking_gaps": sum(1 for r in records if not r.gaps),
            "tiers": {
                name: {
                    "cards": len(overlapping[name]),
                    "exclusive_highest": exclusive[name],
                    "weight": TIER_WEIGHT[name],
                }
                for name in TIER_WEIGHT
            },
            "firecrawl_targets": len(firecrawl_targets),
            "non_firecrawl_targets": len(other_targets),
            "unaddressed_cards": len({row["model_id"] for row in unaddressed}),
        },
        "targets": [t for t in targets if t["cards_unblocked"]],
        "unaddressed": unaddressed,
        "cards": cards_out,
    }


def print_report(manifest: dict[str, Any]) -> None:
    progress = manifest["progress"]
    print("corpus")
    corpus = manifest["corpus"]
    print(
        f"  cards {corpus['cards']}  mean completeness {corpus['mean_completeness']}%  "
        f"hf model_id {corpus['huggingface_model_id']}"
    )
    print("priority tiers (overlapping coverage / exclusive highest)")
    for name, row in progress["tiers"].items():
        print(
            f"  {name:16} cards={row['cards']:<5} "
            f"exclusive={row['exclusive_highest']:<5} weight={row['weight']}"
        )
    print(
        f"queued gaps {progress['cards_with_queued_gaps']}  "
        f"clear {progress['cards_clear_of_unblocking_gaps']}  "
        f"unaddressed {progress['unaddressed_cards']}"
    )

    firecrawl = [t for t in manifest["targets"] if t["firecrawl"]]
    print(f"\ntop Firecrawl targets by cards-unblocked ({len(firecrawl)} total)")
    for i, t in enumerate(firecrawl[:20], 1):
        tiers = ",".join(f"{k}={v}" for k, v in t["unblocks_by_tier"].items())
        print(
            f"  {i:2}. {t['cards_unblocked']:>4} cards  {t['kind']:24}  "
            f"{t['url']}"
        )
        print(f"      fields={t['expected_fields']}  {tiers}")

    other = [t for t in manifest["targets"] if not t["firecrawl"]]
    if other:
        print("\nnon-Firecrawl targets (geometry / unresolved HF)")
        for t in other:
            print(
                f"  {t['cards_unblocked']:>4} cards  {t['id']}  "
                f"fetcher={t['fetcher']}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="manifest JSON path (re-run overwrites; that is the progress measure)",
    )
    parser.add_argument("--limit", type=int, default=0, help="first N cards, for debugging")
    args = parser.parse_args()

    manifest = build(limit=args.limit)
    out = Path(args.output)
    if not out.is_absolute():
        out = PROJECT_ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print_report(manifest)
    print(f"\nmanifest: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
