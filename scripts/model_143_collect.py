#!/usr/bin/env python3
"""Collect MODEL-143's premier-model facts from first-party model pages.

This is an auditable one-shot collector, not a second catalogue format.  It
adds v2 ``facts`` to the existing cards, registers the pages in the canonical
source registry, retains their fetched copies, and files verification claims.
``modelspec verify`` remains the only writer of verification outcomes.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.model import Fact, SourceRef, VerificationActor
from decision.normalise import NORMALISERS, normalise_document
from decision.sources import CopyStore, Fetcher, recheck
from decision.verify import Claim, ModelPageExtractor, Queue, parse_quantity

ROOT = Path(__file__).resolve().parents[1]
READ_AT = datetime(2026, 9, 25, 12, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="codex-model-143",
    model_family="gpt-5",
    method="primary-source-model-page@1",
)


SOURCE_URLS = {
    "anthropic/claude-fable-5": "https://platform.claude.com/docs/en/models/fable-5/overview",
    "anthropic/claude-fable-5-1": "https://platform.claude.com/docs/en/models/fable-5-1/overview",
    "anthropic/claude-opus-4-6": "https://platform.claude.com/docs/en/models/opus-4-6/overview",
    "anthropic/claude-opus-4-7": "https://platform.claude.com/docs/en/models/opus-4-7/overview",
    "anthropic/claude-opus-5": "https://platform.claude.com/docs/en/models/opus-5/overview",
    "anthropic/claude-opus-5-5": "https://platform.claude.com/docs/en/models/opus-5-5/overview",
    "deepseek/deepseek-v4-pro": "https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/README.md",
    "google/gemini-3-1-pro-preview": "https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview",
    "google/gemini-3-5-flash": "https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash",
    "google/gemini-3-7-flash": "https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash",
    "google/gemini-3-8-flash": "https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash",
    "jcorners/ingot-8b-r3": "https://huggingface.co/JCorners/Ingot-8B-R3/resolve/main/README.md",
    "kingsoft/qzhou-embedding": "https://huggingface.co/Kingsoft-LLM/QZhou-Embedding/raw/main/README.md",
    "meta/muse-spark": "https://ai.developer.meta.com/docs/models.md",
    "meta/muse-spark-1-1": "https://ai.developer.meta.com/docs/models.md",
    "meta/muse-spark-1-3": "https://ai.developer.meta.com/docs/models.md",
    "microsoft/harrier-oss-v1-27b": "https://huggingface.co/microsoft/harrier-oss-v1-27b/raw/main/README.md",
    "moonshot/kimi-k2-6": "https://huggingface.co/moonshotai/Kimi-K2.6/resolve/main/README.md",
    "moonshot/kimi-k3": "https://huggingface.co/moonshotai/Kimi-K3/resolve/main/README.md",
    "openai/gpt-5-4": "https://developers.openai.com/api/docs/models/gpt-5.4",
    "openai/gpt-5-6-sol": "https://developers.openai.com/api/docs/models/gpt-5.6-sol",
    "openai/gpt-6-astra": "https://developers.openai.com/api/docs/models/gpt-6-astra",
    "openai/gpt-6-sol": "https://developers.openai.com/api/docs/models/gpt-6-sol",
    "querit/querit": "https://huggingface.co/Querit/Querit/resolve/main/README.md",
    "querit/querit-4b": "https://huggingface.co/Querit/Querit-4B/resolve/main/README.md",
    "qwen/qwen3-8-flash-next": "https://huggingface.co/Qwen/Qwen3.8-Flash-Next/resolve/main/README.md",
    "qwen/qwen3-8-max-0902": "https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen3-8-max",
    "tencent/kalm-embedding-gemma3-12b-2511": "https://huggingface.co/tencent/KaLM-Embedding-Gemma3-12B-2511/raw/main/README.md",
    "typesafe/jev-1-13": "https://docs.typesafe.ai/",
    "xai/grok-4-7": "https://docs.x.ai/docs/models/grok-4-7",
    "zhipu/glm-5-2": "https://huggingface.co/zai-org/GLM-5.2/resolve/main/README.md",
    "zhipu/glm-5-3": "https://huggingface.co/zai-org/GLM-5.3/resolve/main/README.md",
}

BASE_JURISDICTION = {
    "google": "US",
    "qwen": "CN",
    "zai-org": "CN",
}

LABELS = {
    "model.class": "model class",
    "model.input_modalities": "input modalities",
    "model.output_modalities": "output modalities",
    "model.context_window": "context window",
    "model.max_output_tokens": "max output tokens",
    "model.weights_openness": "weights openness",
    "licence.commercial_use": "commercial use",
    "licence.user_cap": "monthly active user cap",
    "licence.output_training": "output training",
    "licence.fine_tuning": "licence fine tuning",
    "origin.lab_jurisdiction": "lab jurisdiction",
    "origin.base_lineage": "base lineage",
    "origin.weights_hosting": "weights hosting",
    "model.release_date": "model release date",
    "model.lifecycle": "lifecycle",
    "feature.tool_calling": "function calling",
    "feature.structured_output": "structured outputs",
    "feature.effort_controls": "reasoning effort",
    "feature.batch": "batch",
    "feature.streaming": "streaming",
}


def source_id(model_id: str) -> str:
    return "model-143-" + re.sub(r"[^a-z0-9]+", "-", model_id.casefold()).strip("-")


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


def known(facet: str, value, ref: SourceRef) -> Fact:
    return Fact(
        id="placeholder",
        subject={"kind": "model", "id": "lab/model"},
        facet=facet,
        state="known",
        value=value,
        sources=[ref],
    )


def undisclosed(facet: str, ref: SourceRef) -> Fact:
    return Fact(
        id="placeholder",
        subject={"kind": "model", "id": "lab/model"},
        facet=facet,
        state="not_disclosed",
        sources=[ref],
    )


def source_values(
    data: dict, ref: SourceRef, source_text: str, names: tuple[str, ...]
) -> dict[str, object]:
    values: dict[str, object] = {}
    extractor = ModelPageExtractor()
    for facet in LABELS:
        unit = "tokens" if facet in {"model.context_window", "model.max_output_tokens"} else None
        probe = Claim(
            target={"kind": "fact", "id": f"probe#{facet}"},
            subject=data["model_id"],
            names=names,
            field=facet,
            label=LABELS[facet],
            value=None,
            unit=unit,
            collector=COLLECTOR,
            sources=(ref,),
        )
        readings = [reading for reading in extractor.extract(probe, source_text)
                    if reading.subject is not None and reading.value is not None]
        if not readings:
            continue
        if facet in {"model.context_window", "model.max_output_tokens"}:
            for reading in readings:
                quantity = parse_quantity(reading.value, unit)
                if quantity is None:
                    continue
                factor = {"tokens": 1, "k_tokens": 1_000, "m_tokens": 1_000_000}.get(
                    quantity.unit or unit
                )
                if factor is not None:
                    values[facet] = int(quantity.number * factor)
                    break
        elif facet.startswith("feature."):
            lowered = readings[-1].value.casefold()
            if lowered in {"supported", "true", "yes", "available"}:
                values[facet] = True
            elif lowered in {"not supported", "false", "no", "unavailable"}:
                values[facet] = False
        elif facet in {"model.class", "model.lifecycle", "model.weights_openness"}:
            values[facet] = readings[-1].value
    return values


def make_facts(
    data: dict, ref: SourceRef, source_text: str, names: tuple[str, ...]
) -> list[Fact]:
    mid = data["model_id"]
    values: dict[str, object | None] = {
        "model.class": None,
        "model.input_modalities": None,
        "model.output_modalities": None,
        "model.context_window": None,
        "model.max_output_tokens": None,
        "model.weights_openness": None,
        "model.release_date": None,
        "model.lifecycle": None,
        "feature.tool_calling": None,
        "feature.structured_output": None,
        "feature.effort_controls": None,
        "feature.batch": None,
        "feature.streaming": None,
    }

    values["origin.lab_jurisdiction"] = None
    values["origin.base_lineage"] = None
    values["origin.weights_hosting"] = None

    values.update({
        "licence.commercial_use": None,
        "licence.user_cap": None,
        "licence.output_training": None,
        "licence.fine_tuning": None,
    })
    values.update(source_values(data, ref, source_text, names))

    facts = []
    for facet in LABELS:
        value = values.get(facet)
        fact = known(facet, value, ref) if value is not None else undisclosed(facet, ref)
        facts.append(Fact.model_validate({
            **fact.model_dump(mode="json"),
            "id": f"{mid}#{facet}",
            "subject": {"kind": "model", "id": mid},
        }))
    return facts


def insert_facts(path: Path, text: str, facts: list[Fact]) -> None:
    rows = [
        fact.model_dump(mode="json", exclude={"id", "subject", "verification"})
        for fact in facts
    ]
    block = yaml.safe_dump({"facts": rows}, sort_keys=False, allow_unicode=True)
    marker = "card_schema_version:"
    if marker not in text:
        raise SystemExit(f"{path}: no card_schema_version marker")
    if re.search(r"(?m)^facts:\s*$", text):
        text = re.sub(r"(?ms)^facts:\n.*?(?=^card_schema_version:)", block, text, count=1)
    else:
        text = text.replace(marker, block + marker, 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    cards = premier_cards()
    rows = []
    for mid, url in sorted(SOURCE_URLS.items()):
        rows.append({
            "id": source_id(mid),
            "url": url,
            "fetch": "http",
            "normaliser": "text-default" if url.endswith(".md") else "html-default",
            "cited_regions": [{"id": "model-spec", "locator": {"kind": "page", "value": ""}}],
        })
    registry_path = ROOT / "registry" / "sources.yaml"
    registry_path.write_text(
        "# MODEL-143 primary model pages; read 2026-09-25.\n"
        + yaml.safe_dump({"schema_version": 1, "sources": rows}, sort_keys=False),
        encoding="utf-8",
    )

    from decision.sources import load_sources

    registered = load_sources(registry_path)
    store = CopyStore()
    report = recheck(
        registered.values(),
        {},
        [],
        fetcher=Fetcher(min_host_interval=0.1),
        store=store,
        now=READ_AT,
    )
    failures = [sid for sid, state in report.states.items() if state.snapshot is None]
    if failures:
        raise SystemExit(f"unreachable primary sources: {failures}")

    queue = Queue(ROOT / "verification")
    for mid, (path, data, card_text) in sorted(cards.items()):
        snapshot = report.states[source_id(mid)].snapshot
        assert snapshot is not None
        ref = SourceRef(
            source_id=source_id(mid),
            snapshot_ref=snapshot.copy_ref,
            cited_regions=["model-spec"],
        )
        names = tuple(dict.fromkeys(filter(None, (
            data.get("display_name"), data.get("version"), data.get("family"),
            mid.rsplit("/", 1)[-1],
            "DeepSeek V4" if mid == "deepseek/deepseek-v4-pro" else None,
            "Querit-Reranker-4B" if mid == "querit/querit-4b" else None,
            "Qwen3.8 Flash Next" if mid == "qwen/qwen3-8-flash-next" else None,
        ))))
        source = registered[source_id(mid)]
        document = normalise_document(
            store.get(snapshot.copy_ref), NORMALISERS[source.normaliser]
        )
        facts = make_facts(data, ref, document.text, names)
        insert_facts(path, card_text, facts)
        for fact in facts:
            facet = fact.facet
            unit = (
                "tokens"
                if facet in {"model.context_window", "model.max_output_tokens"}
                else None
            )
            queue.file(
                Claim.from_fact(
                    fact,
                    names=names,
                    collector=COLLECTOR,
                    unit=unit,
                    label=LABELS[facet],
                ),
                at=READ_AT,
            )
    print(f"filed {len(cards) * len(LABELS)} facts from {len(registered)} primary sources")


if __name__ == "__main__":
    main()
