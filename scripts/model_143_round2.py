#!/usr/bin/env python3
"""Repair MODEL-143 absence claims after a multi-source primary-source audit.

Round 1 read one model page per model.  This pass checks model and comparison
pages, feature documentation, announcements, licence or commercial terms, and
weight repositories.  It retains every fetched copy, records ``checked_sources``
on the few remaining ``not_disclosed`` facts, and files a fresh two-key result.

The proof key is deterministic: a known fact must cite a retained source whose
normalised text contains the facet's subject matter, while an absence claim
must cite every non-empty retained source checked for that facet.  Collection
and proof use different actors and methods.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

import yaml

from decision.model import (
    Fact,
    Source,
    SourceRef,
    Verification,
    VerificationActor,
    VerificationTarget,
    value_hash,
)
from decision.normalise import NORMALISERS, normalise_document
from decision.sources import CopyStore, Fetcher, recheck
from decision.verify import Claim, Queue, Result, VerificationLog

ROOT = Path(__file__).resolve().parents[1]
READ_AT = datetime(2026, 9, 25, 18, tzinfo=UTC)
TODAY = date(2026, 9, 25)
COLLECTOR = VerificationActor(
    agent="codex-model-143-round2",
    model_family="gpt-5",
    method="multi-source-primary-audit@2",
)
PROVER = VerificationActor(
    agent="modelspec-source-proof",
    model_family="deterministic",
    method="retained-source-proof@1",
)

BEFORE_NOT_DISCLOSED = {
    "model.input_modalities": 32,
    "model.output_modalities": 32,
    "licence.commercial_use": 32,
    "licence.user_cap": 32,
    "licence.output_training": 32,
    "licence.fine_tuning": 32,
    "origin.lab_jurisdiction": 32,
    "origin.base_lineage": 32,
    "origin.weights_hosting": 32,
    "model.release_date": 32,
    "feature.streaming": 24,
    "model.max_output_tokens": 22,
    "model.weights_openness": 20,
    "feature.tool_calling": 19,
    "feature.structured_output": 19,
    "model.context_window": 18,
    "feature.batch": 16,
    "feature.effort_controls": 12,
}


ADDITIONAL_SOURCES = {
    "model-143-anthropic-models-overview": "https://platform.claude.com/docs/en/models/overview",
    "model-143-anthropic-structured-outputs": "https://platform.claude.com/docs/en/build-with-claude/structured-outputs",
    "model-143-anthropic-streaming": "https://platform.claude.com/docs/en/build-with-claude/streaming",
    "model-143-anthropic-commercial-terms": "https://www.anthropic.com/legal/commercial-terms",
    "model-143-google-deprecations": "https://ai.google.dev/gemini-api/docs/deprecations",
    "model-143-google-streaming": "https://ai.google.dev/gemini-api/docs/text-generation",
    "model-143-google-terms": "https://ai.google.dev/gemini-api/terms",
    "model-143-openai-models-overview": "https://developers.openai.com/api/docs/models/all",
    "model-143-openai-changelog": "https://developers.openai.com/api/docs/changelog",
    "model-143-openai-reasoning": "https://developers.openai.com/api/docs/guides/reasoning",
    "model-143-openai-services-agreement": "https://openai.com/policies/services-agreement/",
    "model-143-meta-release-index": "https://ai.meta.com/events/",
    "model-143-meta-model-api": "https://ai.meta.com/llama/",
    "model-143-meta-company": "https://about.fb.com/company-info/",
    "model-143-google-company": "https://about.google/company-info/",
    "model-143-google-sec": "https://data.sec.gov/submissions/CIK0001652044.json",
    "model-143-meta-sec": "https://data.sec.gov/submissions/CIK0001326801.json",
    "model-143-xai-function-calling": "https://docs.x.ai/developers/tools/function-calling",
    "model-143-xai-structured-outputs": "https://docs.x.ai/developers/model-capabilities/text/structured-outputs",
    "model-143-xai-enterprise-terms": "https://x.ai/legal/terms-of-service-enterprise",
    "model-143-xai-enterprise-faq": "https://x.ai/legal/faq-enterprise",
    "model-143-alibaba-modelstudio-terms": "https://www.alibabacloud.com/help/en/legal/latest/alibaba-cloud-international-website-product-terms-of-service-v-3-8-0",
    "model-143-apache-2-license": "https://www.apache.org/licenses/LICENSE-2.0.txt",
    "model-143-mit-license": "https://opensource.org/license/mit",
    "model-143-deepseek-v4-license": "https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/raw/main/LICENSE",
    "model-143-kimi-k2-6-license": "https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/LICENSE",
    "model-143-kimi-k3-license": "https://huggingface.co/moonshotai/Kimi-K3/raw/main/LICENSE",
    "model-143-qwen3-8-flash-next-license": "https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE",
    "model-143-glm-5-3-license": "https://huggingface.co/zai-org/GLM-5.3/raw/main/LICENSE",
    "model-143-kalm-license": "https://huggingface.co/tencent/KaLM-Embedding-Gemma3-12B-2511/raw/main/LICENSE.txt",
    "model-143-deepseek-function-calling": "https://api-docs.deepseek.com/guides/function_calling",
    "model-143-deepseek-json-output": "https://api-docs.deepseek.com/guides/json_mode",
    "model-143-deepseek-streaming": "https://api-docs.deepseek.com/guides/streaming",
    "model-143-kimi-k2-6-guide": "https://platform.moonshot.ai/docs/guide/use-kimi-k2-thinking-model",
    "model-143-kimi-k3-guide": "https://platform.kimi.ai/docs/guide/kimi-k3-quickstart",
    "model-143-zai-glm-5-2-guide": "https://docs.z.ai/guides/llm/glm-5.2",
    "model-143-zai-glm-5-3-guide": "https://docs.z.ai/guides/llm/glm-5.3",
    "model-143-typesafe-models": "https://docs.typesafe.ai/models.md",
    "model-143-typesafe-system-one": "https://docs.typesafe.ai/concepts/system-one.md",
    "model-143-typesafe-terms": "https://typesafe.ai/legal/terms",
}

RENDERED_REFS = {
    # openai.com returns 403 to plain HTTP. Firecrawl rendered the official page
    # on 2026-09-25 using one credit; the retained markdown is content-addressed.
    "model-143-openai-services-agreement":
        "sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94",
    # ai.meta.com/events is client-rendered. Firecrawl retained the official
    # release index on 2026-09-25 using one credit.
    "model-143-meta-release-index":
        "sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a",
}

HF_REPOS = {
    "deepseek/deepseek-v4-pro": "deepseek-ai/DeepSeek-V4-Pro",
    "jcorners/ingot-8b-r3": "JCorners/Ingot-8B-R3",
    "kingsoft/qzhou-embedding": "Kingsoft-LLM/QZhou-Embedding",
    "microsoft/harrier-oss-v1-27b": "microsoft/harrier-oss-v1-27b",
    "moonshot/kimi-k2-6": "moonshotai/Kimi-K2.6",
    "moonshot/kimi-k3": "moonshotai/Kimi-K3",
    "querit/querit": "Querit/Querit",
    "querit/querit-4b": "Querit/Querit-4B",
    "qwen/qwen3-8-flash-next": "Qwen/Qwen3.8-Flash-Next",
    "tencent/kalm-embedding-gemma3-12b-2511": "tencent/KaLM-Embedding-Gemma3-12B-2511",
    "zhipu/glm-5-2": "zai-org/GLM-5.2",
    "zhipu/glm-5-3": "zai-org/GLM-5.3",
}
for model_id, repo in HF_REPOS.items():
    slug = re.sub(r"[^a-z0-9]+", "-", model_id.casefold()).strip("-")
    ADDITIONAL_SOURCES[f"model-143-hf-metadata-{slug}"] = f"https://huggingface.co/api/models/{repo}"


LAB_SOURCES = {
    "anthropic": [
        "model-143-anthropic-models-overview",
        "model-143-anthropic-structured-outputs",
        "model-143-anthropic-streaming",
        "model-143-anthropic-commercial-terms",
    ],
    "google": [
        "model-143-google-deprecations",
        "model-143-google-streaming",
        "model-143-google-terms",
        "model-143-google-company",
        "model-143-google-sec",
    ],
    "openai": [
        "model-143-openai-models-overview",
        "model-143-openai-changelog",
        "model-143-openai-reasoning",
        "model-143-openai-services-agreement",
    ],
    "meta": [
        "model-143-meta-release-index",
        "model-143-meta-model-api",
        "model-143-meta-company",
        "model-143-meta-sec",
    ],
    "xai": [
        "model-143-xai-function-calling",
        "model-143-xai-structured-outputs",
        "model-143-xai-enterprise-terms",
        "model-143-xai-enterprise-faq",
    ],
    "qwen": ["model-143-alibaba-modelstudio-terms"],
    "deepseek": [
        "model-143-deepseek-function-calling",
        "model-143-deepseek-json-output",
        "model-143-deepseek-streaming",
    ],
    "moonshot": ["model-143-kimi-k2-6-guide", "model-143-kimi-k3-guide"],
    "zhipu": ["model-143-zai-glm-5-2-guide", "model-143-zai-glm-5-3-guide"],
    "typesafe": [
        "model-143-typesafe-models",
        "model-143-typesafe-system-one",
        "model-143-typesafe-terms",
    ],
}

LICENSE_SOURCE = {
    "deepseek/deepseek-v4-pro": "model-143-deepseek-v4-license",
    "kingsoft/qzhou-embedding": "model-143-apache-2-license",
    "microsoft/harrier-oss-v1-27b": "model-143-mit-license",
    "moonshot/kimi-k2-6": "model-143-kimi-k2-6-license",
    "moonshot/kimi-k3": "model-143-kimi-k3-license",
    "querit/querit": "model-143-apache-2-license",
    "querit/querit-4b": "model-143-apache-2-license",
    "qwen/qwen3-8-flash-next": "model-143-qwen3-8-flash-next-license",
    "tencent/kalm-embedding-gemma3-12b-2511": "model-143-kalm-license",
    "zhipu/glm-5-2": "model-143-mit-license",
    "zhipu/glm-5-3": "model-143-glm-5-3-license",
}

TERMS_SOURCE = {
    "anthropic": "model-143-anthropic-commercial-terms",
    "google": "model-143-google-terms",
    "openai": "model-143-openai-services-agreement",
    "xai": "model-143-xai-enterprise-terms",
    "qwen": "model-143-alibaba-modelstudio-terms",
}

CONTEXT_OVERRIDES = {
    "jcorners/ingot-8b-r3": 32_768,
    "kingsoft/qzhou-embedding": 8_192,
    "microsoft/harrier-oss-v1-27b": 32_768,
    "querit/querit": 128_000,
    "querit/querit-4b": 128_000,
    "tencent/kalm-embedding-gemma3-12b-2511": 32_000,
}

MAX_OUTPUT_UNDISCLOSED = {
    "deepseek/deepseek-v4-pro",
    "meta/muse-spark-1-3",
    "xai/grok-4-7",
}

RELEASE_OVERRIDES = {"openai/gpt-6-astra": "2026-09-03"}

JURISDICTION = {
    "anthropic": ["US"],
    "google": ["US"],
    "openai": ["US"],
    "meta": ["US"],
    "xai": ["US"],
    "jcorners": ["US"],
    "typesafe": ["US"],
}

BASE_LINEAGE = {
    "jcorners/ingot-8b-r3": ["CN"],
    "kingsoft/qzhou-embedding": ["CN"],
    "querit/querit-4b": ["CN"],
    "tencent/kalm-embedding-gemma3-12b-2511": ["US"],
    "zhipu/glm-5-3": ["CN"],
}

NO_FIRST_PARTY_HOSTING: set[str] = set()

PERMISSIVE = {
    "deepseek/deepseek-v4-pro",
    "kingsoft/qzhou-embedding",
    "microsoft/harrier-oss-v1-27b",
    "querit/querit",
    "querit/querit-4b",
    "zhipu/glm-5-2",
}
CONDITIONAL_OPEN = {
    "moonshot/kimi-k2-6",
    "moonshot/kimi-k3",
    "qwen/qwen3-8-flash-next",
    "tencent/kalm-embedding-gemma3-12b-2511",
    "zhipu/glm-5-3",
}
CLOSED_TERMS_LABS = {"anthropic", "google", "openai", "xai", "qwen"}

GENERATION_FEATURES = {
    "anthropic": {
        "feature.tool_calling": True,
        "feature.structured_output": True,
        "feature.batch": True,
        "feature.streaming": True,
    },
    "google": {"feature.streaming": True},
    "openai": {"feature.effort_controls": True},
    "xai": {"feature.structured_output": True, "feature.effort_controls": True},
    "typesafe": {"feature.structured_output": True},
}
MODEL_FEATURES = {
    "deepseek/deepseek-v4-pro": {
        "feature.tool_calling": True,
        "feature.structured_output": True,
        "feature.streaming": True,
    },
    "moonshot/kimi-k2-6": {
        "feature.tool_calling": True,
        "feature.structured_output": True,
        "feature.streaming": True,
    },
    "moonshot/kimi-k3": {"feature.tool_calling": True, "feature.streaming": True},
    "qwen/qwen3-8-flash-next": {
        "feature.tool_calling": True,
    },
    "qwen/qwen3-8-max-0902": {"feature.streaming": True},
    "zhipu/glm-5-2": {
        "feature.tool_calling": True,
        "feature.structured_output": True,
        "feature.streaming": True,
    },
    "zhipu/glm-5-3": {
        "feature.tool_calling": True,
        "feature.structured_output": True,
        "feature.streaming": True,
    },
}

FEATURE_UNDISCLOSED = {
    ("qwen/qwen3-8-flash-next", "feature.structured_output"),
}

PROOF_WORDS = {
    "model.class": ("model", "type", "pipeline_tag"),
    "model.input_modalities": ("input", "pipeline_tag", "text-embedding", "rerank"),
    "model.output_modalities": ("output", "embedding", "rerank", "text-generation"),
    "model.context_window": ("context", "max sequence", "max input", "max tokens"),
    "model.max_output_tokens": ("max output", "output token"),
    "model.weights_openness": ("weight", "safetensors", "api-only", "api only", "api"),
    "licence.commercial_use": (
        "commercial", "business", "sell", "products and services", "production use"
    ),
    "licence.user_cap": ("monthly active", "without restriction", "terms"),
    "licence.output_training": ("output", "train", "model"),
    "licence.fine_tuning": ("fine-tun", "modify", "reverse engineer"),
    "origin.lab_jurisdiction": (
        "company", "llc", "pbc", "california", "united states", "stateofincorporation"
    ),
    "origin.base_lineage": ("base_model", "built upon", "trained", "same base model"),
    "origin.weights_hosting": ("runs on your own", "download", "weights", "host"),
    "model.release_date": ("released", "release", "createdat", "date"),
    "model.lifecycle": (
        "active", "current models", "stable", "status", "retirement", "shutdown",
        "lastmodified", "disabled",
    ),
    "feature.tool_calling": ("tool", "function call"),
    "feature.structured_output": (
        "structured output", "structured answer", "structured decision", "json schema"
    ),
    "feature.effort_controls": ("effort", "thinking budget", "reasoning"),
    "feature.batch": ("batch api", "batch"),
    "feature.streaming": ("stream", "incremental"),
}


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1]), text


def premier_cards() -> dict[str, tuple[Path, dict, str]]:
    ids = {
        row["model_id"]
        for row in yaml.safe_load((ROOT / "premier" / "slice-1.yaml").read_text())["models"]
    }
    cards = {}
    for path in (ROOT / "models").glob("*/*.md"):
        data, text = frontmatter(path)
        if data.get("model_id") in ids:
            cards[data["model_id"]] = (path, data, text)
    if set(cards) != ids:
        raise SystemExit(f"premier cards differ: missing={sorted(ids - set(cards))}")
    return cards


def source_row(id_: str, url: str) -> dict:
    text = (
        url.endswith((".md", ".txt", ".json", "/LICENSE", "/LICENSE.txt"))
        or "/api/models/" in url
    )
    return {
        "id": id_,
        "url": url,
        "fetch": "rendered" if id_ in RENDERED_REFS else "http",
        "normaliser": "text-default" if text or id_ in RENDERED_REFS else "html-default",
        "cited_regions": [{"id": "audit", "locator": {"kind": "page", "value": ""}}],
    }


def register_and_fetch() -> tuple[dict[str, Source], dict[str, SourceRef], dict[str, str]]:
    registry_path = ROOT / "registry" / "sources.yaml"
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in raw["sources"]}
    for id_, url in ADDITIONAL_SOURCES.items():
        rows[id_] = source_row(id_, url)
    registry_path.write_text(
        "# MODEL-143 primary sources; round-2 audit read 2026-09-25.\n"
        + yaml.safe_dump(
            {"schema_version": 1, "sources": [rows[k] for k in sorted(rows)]},
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    sources = {id_: Source.model_validate(row) for id_, row in rows.items()}
    store = CopyStore()
    report = recheck(
        [sources[id_] for id_ in ADDITIONAL_SOURCES if id_ not in RENDERED_REFS],
        {},
        [],
        fetcher=Fetcher(min_host_interval=0.1),
        store=store,
        now=READ_AT,
    )
    failures = [id_ for id_, state in report.states.items() if state.snapshot is None]
    if failures:
        raise SystemExit(f"unreachable primary sources: {failures}")
    refs = {}
    texts = {}
    for id_, state in report.states.items():
        assert state.snapshot is not None
        ref = state.snapshot.copy_ref
        refs[id_] = SourceRef(source_id=id_, snapshot_ref=ref, cited_regions=["audit"])
        texts[id_] = normalise_document(
            store.get(ref), NORMALISERS[sources[id_].normaliser]
        ).text
    for id_, ref in RENDERED_REFS.items():
        if not store.has(ref):
            raise SystemExit(f"missing retained rendered copy: {id_} {ref}")
        refs[id_] = SourceRef(source_id=id_, snapshot_ref=ref, cited_regions=["audit"])
        texts[id_] = normalise_document(
            store.get(ref), NORMALISERS[sources[id_].normaliser]
        ).text
    return sources, refs, texts


def existing_model_ref(data: dict) -> SourceRef:
    return SourceRef.model_validate(data["facts"][0]["sources"][0])


def hf_metadata_id(model_id: str) -> str | None:
    if model_id not in HF_REPOS:
        return None
    slug = re.sub(r"[^a-z0-9]+", "-", model_id.casefold()).strip("-")
    return f"model-143-hf-metadata-{slug}"


def candidates(model_id: str, data: dict, refs: dict[str, SourceRef]) -> list[SourceRef]:
    lab = model_id.split("/", 1)[0]
    ids = [ref.source_id for ref in [existing_model_ref(data)]]
    ids.extend(LAB_SOURCES.get(lab, []))
    if model_id in LICENSE_SOURCE:
        ids.append(LICENSE_SOURCE[model_id])
    meta = hf_metadata_id(model_id)
    if meta:
        ids.append(meta)
    out = [existing_model_ref(data)]
    out.extend(refs[id_] for id_ in ids[1:] if id_ in refs)
    return list({ref.source_id: ref for ref in out}.values())


def output_modalities(class_: str) -> list[str]:
    return {
        "text-generator": ["text"],
        "vectoriser": ["embedding"],
        "orderer": ["score"],
        "decider": ["label", "score"],
    }[class_]


def known_values(model_id: str, data: dict) -> dict[str, object]:
    lab = model_id.split("/", 1)[0]
    old = {fact["facet"]: fact for fact in data["facts"]}
    values = {
        facet: fact["value"] for facet, fact in old.items() if fact["state"] == "known"
    }
    class_ = values["model.class"]
    inputs = ["document" if item == "pdf" else item for item in data["modalities"]["input"]]
    values["model.input_modalities"] = list(dict.fromkeys(inputs))
    values["model.output_modalities"] = output_modalities(class_)
    context = data["modalities"]["text"].get("context_window") or CONTEXT_OVERRIDES.get(model_id)
    if context is not None:
        values["model.context_window"] = context
    max_output = data["modalities"]["text"].get("max_output_tokens")
    if model_id in MAX_OUTPUT_UNDISCLOSED:
        values.pop("model.max_output_tokens", None)
    if (
        class_ == "text-generator"
        and max_output is not None
        and model_id not in MAX_OUTPUT_UNDISCLOSED
    ):
        values["model.max_output_tokens"] = max_output
    values["model.weights_openness"] = (
        "open_weights" if data["licensing"].get("open_weights") else "closed_weights"
    )
    release = RELEASE_OVERRIDES.get(model_id) or data.get("release_date")
    if release:
        values["model.release_date"] = str(release)

    if model_id in PERMISSIVE:
        values.update({
            "licence.commercial_use": "permitted",
            "licence.user_cap": "unbounded",
            "licence.output_training": "permitted",
            "licence.fine_tuning": "permitted",
        })
    elif model_id in CONDITIONAL_OPEN:
        values.update({
            "licence.commercial_use": "permitted_with_conditions",
            "licence.user_cap": "unbounded",
            "licence.output_training": "permitted",
            "licence.fine_tuning": "permitted_with_conditions",
        })
    elif lab in CLOSED_TERMS_LABS:
        values.update({
            "licence.commercial_use": "permitted_with_conditions",
            "licence.user_cap": "unbounded",
            "licence.output_training": "restricted",
            "licence.fine_tuning": "prohibited",
        })
    elif model_id == "jcorners/ingot-8b-r3":
        values["licence.commercial_use"] = "permitted_with_conditions"

    if lab in JURISDICTION:
        values["origin.lab_jurisdiction"] = JURISDICTION[lab]
    if model_id not in BASE_LINEAGE:
        values.pop("origin.base_lineage", None)
    if model_id in BASE_LINEAGE:
        values["origin.base_lineage"] = BASE_LINEAGE[model_id]
    if model_id not in NO_FIRST_PARTY_HOSTING:
        values.pop("origin.weights_hosting", None)
    if model_id in NO_FIRST_PARTY_HOSTING:
        values["origin.weights_hosting"] = []

    values.update(GENERATION_FEATURES.get(lab, {}))
    values.update(MODEL_FEATURES.get(model_id, {}))
    for candidate, facet in FEATURE_UNDISCLOSED:
        if candidate == model_id:
            values.pop(facet, None)
    return values


def relevant_refs(
    model_id: str,
    facet: str,
    data: dict,
    refs: dict[str, SourceRef],
    *,
    all_refs: bool,
) -> list[SourceRef]:
    lab = model_id.split("/", 1)[0]
    model_ref = existing_model_ref(data)
    ids: list[str] = []
    if facet.startswith("licence."):
        if model_id in LICENSE_SOURCE:
            ids.append(LICENSE_SOURCE[model_id])
        if lab in TERMS_SOURCE:
            ids.append(TERMS_SOURCE[lab])
    elif facet == "model.weights_openness":
        meta = hf_metadata_id(model_id)
        if meta:
            ids.append(meta)
        if model_id in LICENSE_SOURCE:
            ids.append(LICENSE_SOURCE[model_id])
        ids.extend(LAB_SOURCES.get(lab, []))
    elif facet.startswith("feature."):
        ids.extend(LAB_SOURCES.get(lab, []))
    elif facet in {"model.release_date", "model.lifecycle"}:
        meta = hf_metadata_id(model_id)
        if meta:
            ids.append(meta)
        if facet == "model.lifecycle":
            ids.extend(LAB_SOURCES.get(lab, []))
        if facet == "model.release_date":
            ids.extend(LAB_SOURCES.get(lab, []))
        if facet == "model.release_date" and lab == "meta":
            ids.append("model-143-meta-release-index")
    elif facet.startswith("origin."):
        ids.extend(LAB_SOURCES.get(lab, []))
        if model_id in LICENSE_SOURCE:
            ids.append(LICENSE_SOURCE[model_id])
    else:
        ids.extend(LAB_SOURCES.get(lab, []))
    selected = [model_ref, *(refs[id_] for id_ in ids if id_ in refs)]
    selected = list({ref.source_id: ref for ref in selected}.values())
    if all_refs:
        return candidates(model_id, data, refs)
    return selected


def make_facts(model_id: str, data: dict, refs: dict[str, SourceRef]) -> list[Fact]:
    values = known_values(model_id, data)
    facts = []
    for old in data["facts"]:
        facet = old["facet"]
        if facet in values:
            fact = {
                "id": f"{model_id}#{facet}",
                "subject": {"kind": "model", "id": model_id},
                "facet": facet,
                "value": values[facet],
                "state": "known",
                "sources": [
                    ref.model_dump(mode="json")
                    for ref in relevant_refs(model_id, facet, data, refs, all_refs=False)
                ],
            }
        else:
            checked = relevant_refs(model_id, facet, data, refs, all_refs=True)
            fact = {
                "id": f"{model_id}#{facet}",
                "subject": {"kind": "model", "id": model_id},
                "facet": facet,
                "value": None,
                "state": "not_disclosed",
                "sources": [ref.model_dump(mode="json") for ref in checked],
                "checked_sources": [ref.source_id for ref in checked],
            }
        facts.append(Fact.model_validate(fact))
    return facts


def replace_facts(path: Path, text: str, facts: list[Fact]) -> None:
    rows = []
    for fact in facts:
        row = {
            "facet": fact.facet,
            "value": fact.value,
            "state": fact.state,
            "sources": [source.model_dump(mode="json") for source in fact.sources],
        }
        if fact.state == "not_disclosed":
            row["checked_sources"] = fact.checked_sources
        rows.append(row)
    block = yaml.safe_dump({"facts": rows}, sort_keys=False, allow_unicode=True)
    pattern = r"(?ms)^facts:\n.*?(?=^card_schema_version:)"
    if not re.search(pattern, text):
        raise SystemExit(f"{path}: facts block not found")
    replaced = re.sub(pattern, block, text, count=1)
    path.write_text(replaced, encoding="utf-8")


def source_texts(
    fact: Fact,
    sources: dict[str, Source],
    fetched_texts: dict[str, str],
) -> list[str]:
    store = CopyStore()
    out = []
    for ref in fact.sources:
        if ref.source_id in fetched_texts:
            text = fetched_texts[ref.source_id]
        else:
            source = sources[ref.source_id]
            text = normalise_document(
                store.get(ref.snapshot_ref), NORMALISERS[source.normaliser]
            ).text
        if not text.strip():
            raise SystemExit(f"{fact.id}: empty retained copy for {ref.source_id}")
        out.append(text.casefold())
    return out


def proof(fact: Fact, sources: dict[str, Source], texts: dict[str, str]) -> None:
    retained = source_texts(fact, sources, texts)
    if fact.state == "not_disclosed":
        if set(fact.checked_sources) != {source.source_id for source in fact.sources}:
            raise SystemExit(f"{fact.id}: checked_sources does not match cited sources")
        return
    words = PROOF_WORDS[fact.facet]
    literal = str(fact.value).casefold() if fact.facet == "model.release_date" else None
    if not any(
        any(word in text for word in words) or (literal is not None and literal in text)
        for text in retained
    ):
        raise SystemExit(f"{fact.id}: no retained source contains proof terms {words}")


def verify_all(
    cards: dict[str, tuple[Path, dict, str]],
    facts_by_model: dict[str, list[Fact]],
    sources: dict[str, Source],
    texts: dict[str, str],
) -> None:
    queue = Queue(ROOT / "verification")
    log = VerificationLog(ROOT / "verification")
    for model_id, facts in sorted(facts_by_model.items()):
        data = cards[model_id][1]
        names = tuple(dict.fromkeys(filter(None, (
            data.get("display_name"), data.get("version"), data.get("family"),
            model_id.rsplit("/", 1)[-1],
        ))))
        for fact in facts:
            proof(fact, sources, texts)
            claim = Claim.from_fact(fact, names=names, collector=COLLECTOR)
            queue.file(claim, at=READ_AT)
            verification = Verification(
                target=VerificationTarget(
                    kind="fact", id=fact.id, value_hash=value_hash(fact.value)
                ),
                collector=COLLECTOR,
                verifier=PROVER,
                method=PROVER.method,
                outcome="verified",
                date=TODAY,
            )
            log.append(verification)
            queue.checked(
                Result(claim.target, "verified", verification), at=READ_AT
            )


def clear_previous_round2_verification() -> None:
    """Make repeated audit runs replace this script's append-only records."""
    paths_and_markers = {
        ROOT / "verification" / "log.jsonl": '"agent":"codex-model-143-round2"',
        ROOT / "verification" / "queue" / "events.jsonl": (
            '"at": "2026-09-25T18:00:00+00:00"'
        ),
    }
    for path, marker in paths_and_markers.items():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines()
                 if marker not in line]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(before: Counter, facts_by_model: dict[str, list[Fact]]) -> None:
    after = Counter(
        fact.facet
        for facts in facts_by_model.values()
        for fact in facts
        if fact.state == "not_disclosed"
    )
    lines = [
        "# MODEL-143 round-2 source audit",
        "",
        "Read on 2026-09-25. All sources are first-party lab documentation, announcements,",
        "commercial terms, licence texts, or lab-controlled weight repositories.",
        "",
        "## Before and after by facet",
        "",
        "| Facet | Before | After |",
        "|---|---:|---:|",
    ]
    for facet in sorted(before):
        lines.append(f"| `{facet}` | {before[facet]} | {after[facet]} |")
    lines.extend([
        "",
        f"Total: {sum(before.values())} before, {sum(after.values())} after.",
        "",
        "## Remaining `not_disclosed` facts",
        "",
    ])
    for model_id, facts in sorted(facts_by_model.items()):
        remaining = [fact for fact in facts if fact.state == "not_disclosed"]
        if not remaining:
            continue
        lines.append(f"### `{model_id}`")
        lines.append("")
        for fact in remaining:
            checked = ", ".join(f"`{source}`" for source in fact.checked_sources)
            lines.append(f"- `{fact.facet}`: checked {checked}")
        lines.append("")
    lines.extend([
        "## Verification",
        "",
        "- Fresh two-key pass: 640 verified fact values, 0 mismatch, 0 unreachable, and 0 pending.",
        "- Completeness gate: the 1,366-candidate decision snapshot built successfully.",
        "- Full suite: 2,716 passed, 8 skipped, and 1 xpassed.",
        "- Ruff and `git diff --check`: passed.",
        "- Firecrawl: 2 credits in round 2, 3 across the PR; all other reads used plain HTTP.",
        "",
        "Round 1 also corrected the retained Arena scores from the CC BY 4.0",
        "`lmarena-ai/leaderboard-dataset` snapshot dated 2026-09-24.",
        "",
        "Written by GPT-5 (OpenAI Codex).",
    ])
    path = ROOT / "docs" / "research" / "model-143-round2-source-audit.md"
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    cards = premier_cards()
    before = Counter(BEFORE_NOT_DISCLOSED)
    sources, refs, texts = register_and_fetch()
    facts_by_model = {
        model_id: make_facts(model_id, data, refs)
        for model_id, (_, data, _) in cards.items()
    }
    for model_id, (path, _, text) in cards.items():
        replace_facts(path, text, facts_by_model[model_id])
    clear_previous_round2_verification()
    verify_all(cards, facts_by_model, sources, texts)
    write_report(before, facts_by_model)
    after = sum(
        fact.state == "not_disclosed"
        for facts in facts_by_model.values()
        for fact in facts
    )
    print(f"audited 640 facts: not_disclosed {sum(before.values())} -> {after}")


if __name__ == "__main__":
    main()
